from __future__ import annotations

import json
from pathlib import Path

from app.core.config import Settings
from app.services.chunking import Chunk, DynamicEmailChunker
from app.services.corpus import corpus_path, load_corpus_status
from app.services.embeddings import build_embedding_provider
from app.services.retrieval import persist_index


def load_processed_emails(settings: Settings) -> list[dict]:
    path = corpus_path(settings)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_chunks_from_corpus(settings: Settings) -> tuple[list[Chunk], dict[str, dict]]:
    chunker = DynamicEmailChunker()
    emails = load_processed_emails(settings)
    chunks: list[Chunk] = []
    meta: dict[str, dict] = {}
    for email in emails:
        email_id = str(email["email_id"])
        meta[email_id] = email.get("metadata") or {}
        chunks.extend(chunker.chunk_email(email_id, email.get("text") or ""))
    return chunks, meta


def build_index(settings: Settings) -> dict:
    status = load_corpus_status(settings)
    if status.get("status") != "ready":
        return {
            "status": "waiting",
            "reason": status.get("reason") or "corpus not ready",
            "chunks": 0,
        }
    embeddings, embedding_status, embedding_model = build_embedding_provider(settings)
    if embeddings is None:
        return {
            "status": "unavailable",
            "reason": "EMBEDDING UNAVAILABLE",
            "chunks": 0,
        }
    chunks, meta = build_chunks_from_corpus(settings)
    if not chunks:
        return {"status": "waiting", "reason": "CORPUS HAS NO CHUNKS", "chunks": 0}
    if hasattr(embeddings, "fit"):
        embeddings.fit([chunk.text for chunk in chunks])
    vectors = embeddings.embed_many([chunk.text for chunk in chunks])
    persist_index(settings.index_dir, chunks, vectors, meta)
    return {
        "status": "ready",
        "chunks": len(chunks),
        "emails": len(meta),
        "embedding_model": embedding_model,
    }
