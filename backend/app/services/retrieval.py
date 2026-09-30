from __future__ import annotations

from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

from app.schemas.retrieval import RetrievalHit
from app.services.chunking import Chunk


class Retriever(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        raise NotImplementedError


class NumpyRetriever(Retriever):
    """File-backed cosine retriever. Injection filtering is not performed here."""

    def __init__(self, embed_fn, matrix: np.ndarray, records: list[dict[str, Any]]) -> None:
        self._embed_fn = embed_fn
        self._matrix = matrix
        self._records = records

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        if self._matrix.size == 0 or not self._records:
            return []
        query_vec = self._embed_fn(query)
        if sparse.issparse(self._matrix):
            query_vec = normalize(query_vec, norm="l2")
            scores = (self._matrix @ query_vec.T).toarray().ravel()
        else:
            query_vec = np.asarray(query_vec, dtype=np.float32)
            denom = float(np.linalg.norm(query_vec))
            if denom:
                query_vec = query_vec / denom
            scores = self._matrix @ query_vec
        k = min(top_k, len(self._records))
        order = np.argsort(-scores)[:k]
        hits: list[RetrievalHit] = []
        for idx in order:
            rec = self._records[int(idx)]
            hits.append(
                RetrievalHit(
                    chunk_id=rec["chunk_id"],
                    email_id=rec["email_id"],
                    score=float(scores[int(idx)]),
                    text=rec["text"],
                    metadata={
                        "parent_id": rec.get("parent_id"),
                        "section": rec.get("section"),
                        "boundary_reason": rec.get("boundary_reason"),
                        "char_count": rec.get("char_count"),
                        "token_estimate": rec.get("token_estimate"),
                        "source_metadata": rec.get("source_metadata") or {},
                    },
                )
            )
        return hits


def persist_index(index_dir: Path, chunks: list[Chunk], embeddings, source_meta: dict[str, dict]) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    if sparse.issparse(embeddings):
        matrix = normalize(embeddings.tocsr(), norm="l2")
        sparse.save_npz(index_dir / "embeddings.npz", matrix)
    else:
        matrix = np.asarray(embeddings, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        matrix = matrix / norms
        np.save(index_dir / "embeddings.npy", matrix)
    records = []
    for chunk in chunks:
        records.append(
            {
                "chunk_id": chunk.chunk_id,
                "email_id": chunk.email_id,
                "parent_id": chunk.parent_id,
                "section": chunk.section,
                "text": chunk.text,
                "boundary_reason": chunk.boundary_reason,
                "char_count": chunk.char_count,
                "token_estimate": chunk.token_estimate,
                "source_metadata": source_meta.get(chunk.email_id, {}),
            }
        )
    (index_dir / "chunks.jsonl").write_text(
        "\n".join(json.dumps(item) for item in records) + ("\n" if records else ""),
        encoding="utf-8",
    )
    status = {
        "status": "ready" if records else "waiting",
        "chunks": len(records),
        "emails": len({chunk.email_id for chunk in chunks}),
    }
    (index_dir / "index_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


def load_index_status(index_dir: Path) -> dict:
    path = index_dir / "index_status.json"
    if not path.exists():
        return {"status": "waiting", "chunks": 0, "emails": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def load_retriever(index_dir: Path, embed_fn) -> NumpyRetriever | None:
    sparse_path = index_dir / "embeddings.npz"
    matrix_path = index_dir / "embeddings.npy"
    records_path = index_dir / "chunks.jsonl"
    if not (sparse_path.exists() or matrix_path.exists()) or not records_path.exists():
        return None
    matrix = sparse.load_npz(sparse_path) if sparse_path.exists() else np.load(matrix_path)
    records = []
    for line in records_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    if matrix.shape[0] != len(records):
        return None
    return NumpyRetriever(embed_fn, matrix, records)


def load_chunk_record(index_dir: Path, chunk_id: str) -> dict[str, Any] | None:
    path = index_dir / "chunks.jsonl"
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("chunk_id") == chunk_id:
            return rec
    return None
