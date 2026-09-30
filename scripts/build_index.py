#!/usr/bin/env python3
"""Chunk the processed corpus and persist a file-backed vector index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.services.index_builder import build_index  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dynamic chunks and the retrieval index.")
    parser.parse_args()
    settings = get_settings()
    result = build_index(settings)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
