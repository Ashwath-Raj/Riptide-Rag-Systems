#!/usr/bin/env python3
"""Explicitly download optional local models. Never invoked by backend startup."""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download optional embedding/injection models. Backend startup never does this."
    )
    parser.add_argument("--embedding-model", default="", help="sentence-transformers model name")
    parser.add_argument("--injection-model", default="", help="local transformers classifier path or hub id")
    parser.add_argument("--allow-download", action="store_true", help="permit network downloads")
    args = parser.parse_args()
    if not args.allow_download:
        print("Refusing to download. Re-run with --allow-download if you intend to fetch models.")
        print("The runtime uses a corpus-trained TF-IDF index; train the local injection classifier separately.")
        return 0
    if args.embedding_model:
        from sentence_transformers import SentenceTransformer

        SentenceTransformer(args.embedding_model)
        print(f"Downloaded embedding model: {args.embedding_model}")
    if args.injection_model:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        AutoTokenizer.from_pretrained(args.injection_model)
        AutoModelForSequenceClassification.from_pretrained(args.injection_model)
        print(f"Downloaded injection model: {args.injection_model}")
    if not args.embedding_model and not args.injection_model:
        print("Nothing to download. Pass --embedding-model and/or --injection-model.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
