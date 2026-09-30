from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterator

from app.services.dataset_adapter import DatasetAdapter, EmailRecord, SchemaInspection
from app.services.dataset_inspector import (
    find_parquet_files,
    infer_id_column,
    infer_metadata_columns,
    infer_text_column,
    inspect_parquet_file,
    is_complete_parquet,
    find_enron_csv_files,
    inspect_csv_file,
)


class EnronDatasetAdapter(DatasetAdapter):
    def __init__(self, root: Path, limit: int | None = None) -> None:
        self.root = Path(root)
        self.limit = limit
        self._files: list[Path] = []
        self._csv_files: list[Path] = []
        self._inspections: list[dict] = []

    def load(self) -> None:
        all_files = find_parquet_files(self.root)
        enronish = [
            path
            for path in all_files
            if "enron" in str(path).lower() or "pile" in str(path).lower()
        ]
        candidates = enronish or all_files
        self._files = [path for path in candidates if is_complete_parquet(path)]
        self._inspections = [inspect_parquet_file(path) for path in candidates]
        self._csv_files = [path for path in find_enron_csv_files(self.root) if inspect_csv_file(path)["complete"]]

    def inspect_schema(self) -> list[SchemaInspection]:
        if not self._inspections:
            self.load()
        out: list[SchemaInspection] = []
        for item in self._inspections:
            out.append(
                SchemaInspection(
                    path=item["path"],
                    row_count=item["row_count"],
                    columns=item["columns"],
                    inferred_text_column=item["inferred_text_column"],
                    inferred_metadata_columns=item["inferred_metadata_columns"],
                    complete=item["complete"],
                    notes=item["notes"],
                )
            )
        return out

    def iter_records(self) -> Iterator[EmailRecord]:
        if not self._files:
            self.load()
        emitted = 0
        for path in self._csv_files:
            csv.field_size_limit(2**31 - 1)
            with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
                reader = csv.DictReader(handle)
                for row_index, raw in enumerate(reader):
                    yield EmailRecord(
                        email_id=str(raw.get("file") or f"row-{row_index}"),
                        text=str(raw.get("message") or ""),
                        metadata={
                            "source": "enron-csv",
                            "file": raw.get("file"),
                            "source_path": str(path),
                            "source_row": row_index,
                        },
                        source_path=str(path),
                        source_row=row_index,
                    )
                    emitted += 1
                    if self.limit is not None and emitted >= self.limit:
                        return
        for path in self._files:
            inspection = inspect_parquet_file(path)
            text_col = inspection["inferred_text_column"]
            id_col = infer_id_column(inspection["columns"])
            if not text_col:
                continue
            try:
                import pyarrow.parquet as pq
            except ImportError as exc:
                raise RuntimeError("pyarrow is required to read parquet corpora") from exc
            parquet = pq.ParquetFile(path)
            row_index = 0
            for group_index in range(parquet.num_row_groups):
                table = parquet.read_row_group(group_index)
                columns = table.to_pydict()
                n = table.num_rows
                for i in range(n):
                    raw = {name: columns[name][i] for name in columns}
                    record = self.normalize_record(raw, str(path), row_index, text_col, id_col)
                    yield record
                    emitted += 1
                    row_index += 1
                    if self.limit is not None and emitted >= self.limit:
                        return

    def normalize_record(
        self,
        raw: dict[str, Any],
        source_path: str,
        source_row: int,
        text_column: str | None = None,
        id_column: str | None = None,
    ) -> EmailRecord:
        columns = list(raw.keys())
        text_column = text_column or infer_text_column(columns)
        id_column = id_column or infer_id_column(columns)
        text_value = raw.get(text_column) if text_column else None
        if isinstance(text_value, dict):
            text = str(text_value.get("text") or text_value.get("content") or text_value)
        else:
            text = "" if text_value is None else str(text_value)
        email_id = str(raw.get(id_column) or f"row-{source_row}")
        meta_cols = infer_metadata_columns(columns, text_column)
        metadata = {key: _jsonable(raw.get(key)) for key in meta_cols}
        metadata["source"] = "enron"
        return EmailRecord(
            email_id=email_id,
            text=text,
            metadata=metadata,
            source_path=source_path,
            source_row=source_row,
        )


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return str(value)
