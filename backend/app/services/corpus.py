from __future__ import annotations

import json
from pathlib import Path

from app.core.config import Settings
from app.services.dataset_adapter import EmailRecord
from app.services.dataset_inspector import inspect_dataset_root
from app.services.ingestion import EnronDatasetAdapter


CORPUS_NAME = "corpus.jsonl"
STATUS_NAME = "corpus_status.json"


def corpus_status_path(settings: Settings) -> Path:
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    return settings.processed_dir / STATUS_NAME


def corpus_path(settings: Settings) -> Path:
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    return settings.processed_dir / CORPUS_NAME


def load_corpus_status(settings: Settings) -> dict:
    path = corpus_status_path(settings)
    if not path.exists():
        inspection = inspect_dataset_root(settings.dataset_root_path)
        return {
            "status": "waiting",
            "emails": 0,
            "reason": "corpus not built",
            "dataset": inspection["status"],
            "complete_files": inspection["complete_files"],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_records(settings: Settings, records: list[EmailRecord], source: str, source_emails: int) -> dict:
    path = corpus_path(settings)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(
                    {
                        "email_id": record.email_id,
                        "text": record.text,
                        "metadata": record.metadata,
                        "source_path": record.source_path,
                        "source_row": record.source_row,
                    }
                )
                + "\n"
            )
    status = {
        "status": "ready" if records else "waiting",
        "emails": len(records),
        "source_emails": source_emails,
        "path": str(path),
        "source": source,
        "fixtures": False,
    }
    corpus_status_path(settings).write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


def build_corpus(settings: Settings, min_emails: int = 10000, limit: int | None = None) -> dict:
    inspection = inspect_dataset_root(settings.dataset_root_path)
    if inspection["source_files"] == 0:
        status = {
            "status": "waiting",
            "emails": 0,
            "reason": "no usable Enron CSV or Parquet source",
            "dataset": inspection,
        }
        corpus_status_path(settings).write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    adapter = EnronDatasetAdapter(settings.dataset_root_path, limit=limit)
    adapter.load()
    records = list(adapter.iter_records())
    if len(records) < min_emails:
        status = {
            "status": "waiting",
            "emails": len(records),
            "reason": f"only {len(records)} complete records; need {min_emails}",
            "dataset": inspection,
        }
        corpus_status_path(settings).write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    source_emails = sum(
        int(item.get("row_count") or 0)
        for item in inspection.get("csv_files", [])
        if item.get("complete")
    ) or len(records)
    saved = save_records(
        settings,
        records,
        source="enron-csv-or-parquet",
        source_emails=source_emails,
    )
    saved["dataset"] = inspection
    return saved
