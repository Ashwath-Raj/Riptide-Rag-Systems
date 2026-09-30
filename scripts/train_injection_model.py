#!/usr/bin/env python3
"""Train and persist the local prompt-injection classifier."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


TEXT_HINTS = ("text", "prompt", "content", "input", "instruction")
LABEL_HINTS = ("label", "target", "class", "category", "is_injection", "injection")


def _column(columns: list[str], hints: tuple[str, ...]) -> str | None:
    for hint in hints:
        for column in columns:
            if hint == column.lower() or hint in column.lower():
                return column
    return None


def _records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            return list(csv.DictReader(handle))
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if path.suffix.lower() == ".parquet":
        import pyarrow.parquet as parquet

        return parquet.read_table(path).to_pylist()
    raise ValueError(f"unsupported training file: {path}")


def _label(value: Any) -> int:
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "injection", "malicious", "prompt_injection", "unsafe"}:
        return 1
    if normalized in {"0", "false", "no", "benign", "safe", "normal"}:
        return 0
    raise ValueError(f"unrecognized injection label: {value!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Train a TF-IDF + LogisticRegression injection classifier.")
    parser.add_argument("--root", default=str(ROOT / "data" / "raw"))
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "models"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    root = Path(args.root)
    paths = sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".csv", ".jsonl", ".ndjson", ".parquet"})
    if not paths:
        raise SystemExit("No materialized prompt-injection dataset found.")
    rows: list[dict[str, Any]] = []
    for path in paths:
        try:
            rows.extend(_records(path))
        except Exception as exc:
            print(f"Skipping {path}: {exc}", file=sys.stderr)
    if not rows:
        raise SystemExit("Prompt-injection dataset contains no readable records.")
    columns = list(rows[0])
    text_column = _column(columns, TEXT_HINTS)
    label_column = _column(columns, LABEL_HINTS)
    if not text_column or not label_column:
        raise SystemExit(f"Could not infer text/label columns from {columns!r}")
    examples = [(str(row.get(text_column) or "").strip(), _label(row.get(label_column))) for row in rows]
    examples = [(text, label) for text, label in examples if text]
    if args.limit:
        examples = examples[: args.limit]
    if len({label for _, label in examples}) < 2:
        raise SystemExit("Training data must contain both benign and injection labels.")
    from joblib import dump
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    texts, labels = zip(*examples)
    config = json.loads((ROOT / "configs" / "injection_model.json").read_text(encoding="utf-8"))
    vectorizer_options = dict(config["vectorizer"])
    vectorizer_options["ngram_range"] = tuple(vectorizer_options["ngram_range"])
    vectorizer = TfidfVectorizer(**vectorizer_options)
    matrix = vectorizer.fit_transform(texts)
    classifier = LogisticRegression(**config["classifier"])
    classifier.fit(matrix, labels)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dump(classifier, output_dir / "injection_classifier.joblib")
    dump(vectorizer, output_dir / "injection_vectorizer.joblib")
    manifest = {
        "status": "ready",
        "model": "tfidf-logistic-injection",
        "records": len(texts),
        "source_files": [str(path.resolve()) for path in paths],
        "text_column": text_column,
        "label_column": label_column,
        "config": str((ROOT / "configs" / "injection_model.json").relative_to(ROOT)),
    }
    (output_dir / "injection_classifier_status.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({**manifest, "output_dir": str(output_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
