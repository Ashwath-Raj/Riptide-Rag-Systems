#!/usr/bin/env python3
"""Normalize the Enron parquet corpus when a complete dataset is present."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.services.corpus import build_corpus  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the processed Enron corpus from parquet.")
    parser.add_argument("--min-emails", type=int, default=10000)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    settings = get_settings()
    result = build_corpus(settings, min_emails=args.min_emails, limit=args.limit)
    print(json.dumps(result, indent=2, default=str))
    if result.get("status") != "ready":
        print("\nCorpus: WAITING")
        return 0
    print(f"\nCorpus emails: {result.get('emails')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
