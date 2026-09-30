from __future__ import annotations

import json
from pathlib import Path

LFS_PREFIX = "version https://git-lfs.github.com/spec/v1"
TEXT_HINTS = ("text", "content", "body", "email", "message", "document")
ID_HINTS = ("id", "email_id", "doc_id", "uid")
META_HINTS = ("from", "to", "cc", "bcc", "date", "subject", "meta", "metadata", "header")


def is_lfs_pointer(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            first = handle.readline(120)
        return first.startswith("version https://git-lfs.github.com/spec/v1")
    except OSError:
        return False


def is_complete_parquet(path: Path) -> bool:
    if path.suffix == ".crdownload" or ".crdownload" in path.name:
        return False
    if path.stat().st_size < 1024:
        return False
    if is_lfs_pointer(path):
        return False
    try:
        with path.open("rb") as handle:
            magic = handle.read(4)
        return magic == b"PAR1"
    except OSError:
        return False


def find_parquet_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if ".crdownload" in path.name:
            continue
        if path.suffix.lower() == ".parquet":
            files.append(path)
    return files


def find_enron_csv_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*.csv")
        if path.is_file() and "email" in path.name.lower()
    )


def inspect_csv_file(path: Path) -> dict:
    import csv

    report = {"path": str(path), "columns": [], "row_count": 0, "complete": False, "notes": []}
    try:
        csv.field_size_limit(2**31 - 1)
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            report["columns"] = reader.fieldnames or []
            report["row_count"] = sum(1 for _ in reader)
        report["complete"] = {"file", "message"}.issubset(
            {column.lower() for column in report["columns"]}
        )
        if not report["complete"]:
            report["notes"].append("expected file and message columns")
    except (OSError, csv.Error) as exc:
        report["notes"].append(f"csv read failed: {exc}")
    return report


def infer_text_column(columns: list[str]) -> str | None:
    lowered = {col.lower(): col for col in columns}
    for hint in TEXT_HINTS:
        for key, original in lowered.items():
            if hint == key or hint in key:
                return original
    return columns[0] if len(columns) == 1 else None


def infer_id_column(columns: list[str]) -> str | None:
    lowered = {col.lower(): col for col in columns}
    for hint in ID_HINTS:
        if hint in lowered:
            return lowered[hint]
    return None


def infer_metadata_columns(columns: list[str], text_column: str | None) -> list[str]:
    meta: list[str] = []
    for col in columns:
        if col == text_column:
            continue
        key = col.lower()
        if any(hint in key for hint in META_HINTS + ID_HINTS):
            meta.append(col)
    return meta


def inspect_parquet_file(path: Path) -> dict:
    report = {
        "path": str(path),
        "row_count": None,
        "columns": [],
        "inferred_text_column": None,
        "inferred_metadata_columns": [],
        "complete": is_complete_parquet(path),
        "notes": [],
        "bytes": path.stat().st_size,
    }
    if ".crdownload" in path.name:
        report["notes"].append("ignored incomplete download")
        report["complete"] = False
        return report
    if is_lfs_pointer(path):
        report["notes"].append("git-lfs pointer; dataset not materialized")
        report["complete"] = False
        return report
    if not report["complete"]:
        report["notes"].append("file too small or not a parquet body")
        return report
    try:
        import pyarrow.parquet as pq
    except ImportError:
        report["notes"].append("pyarrow not installed; schema unread")
        return report
    try:
        parquet = pq.ParquetFile(path)
        columns = [field.name for field in parquet.schema_arrow]
        report["columns"] = columns
        report["row_count"] = parquet.metadata.num_rows
        report["inferred_text_column"] = infer_text_column(columns)
        report["inferred_metadata_columns"] = infer_metadata_columns(
            columns, report["inferred_text_column"]
        )
    except Exception as exc:  # pragma: no cover - defensive
        report["notes"].append(f"schema read failed: {exc}")
        report["complete"] = False
    return report


def inspect_dataset_root(root: Path) -> dict:
    files = find_parquet_files(root)
    inspections = [inspect_parquet_file(path) for path in files]
    complete = [item for item in inspections if item["complete"]]
    csv_files = find_enron_csv_files(root)
    csv_inspections = [inspect_csv_file(path) for path in csv_files]
    csv_complete = [item for item in csv_inspections if item["complete"]]
    return {
        "root": str(root),
        "parquet_files": len(files),
        "complete_files": len(complete),
        "files": inspections,
        "csv_files": csv_inspections,
        "source_files": len(complete) + len(csv_complete),
        "status": "ready" if complete or csv_complete else "waiting",
    }


def format_inspection_report(payload: dict) -> str:
    lines = [
        "RIPTIDE DATASET INSPECTION",
        "--------------------------",
        f"Root: {payload['root']}",
        f"Parquet files found: {payload['parquet_files']}",
        f"Complete parquet files: {payload['complete_files']}",
        f"Usable CSV files: {sum(1 for item in payload.get('csv_files', []) if item['complete'])}",
        f"Status: {payload['status'].upper()}",
        "",
    ]
    if not payload["files"]:
        lines.append("No parquet files discovered.")
        return "\n".join(lines)
    for item in payload["files"]:
        lines.extend(
            [
                f"PATH  {item['path']}",
                f"BYTES {item['bytes']}",
                f"ROWS  {item['row_count'] if item['row_count'] is not None else 'n/a'}",
                f"COLS  {', '.join(item['columns']) if item['columns'] else '(unread)'}",
                f"TEXT  {item['inferred_text_column'] or '(unknown)'}",
                f"META  {', '.join(item['inferred_metadata_columns']) or '(none inferred)'}",
                f"OK    {item['complete']}",
            ]
        )
        for note in item["notes"]:
            lines.append(f"NOTE  {note}")
        lines.append("")
    for item in payload.get("csv_files", []):
        lines.extend(
            [
                f"PATH  {item['path']}",
                f"ROWS  {item['row_count']}",
                f"COLS  {', '.join(item['columns']) or '(unread)'}",
                f"OK    {item['complete']}",
            ]
        )
        for note in item["notes"]:
            lines.append(f"NOTE  {note}")
        lines.append("")
    return "\n".join(lines)


def dump_inspection_json(payload: dict) -> str:
    return json.dumps(payload, indent=2)
