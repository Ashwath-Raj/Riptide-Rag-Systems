from typing import Any

from pydantic import BaseModel


class RetrievalHit(BaseModel):
    chunk_id: str
    email_id: str
    score: float
    text: str
    metadata: dict[str, Any] = {}


class RetrievalStats(BaseModel):
    candidate_count: int
    quarantined_count: int
    safe_count: int
    latency_ms: int | None = None
