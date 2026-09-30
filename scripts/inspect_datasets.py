#!/usr/bin/env python3
"""Inspect parquet datasets under DATASET_ROOT without requiring a complete corpus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.services.dataset_inspector import format_inspection_report, inspect_dataset_root  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect parquet files under the dataset root.")
    parser.add_argument("--root", help="Dataset root (defaults to DATASET_ROOT)")
    args = parser.parse_args()
    settings = get_settings()
    root = Path(args.root).resolve() if args.root else settings.dataset_root_path
    payload = inspect_dataset_root(root)
    print(format_inspection_report(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
