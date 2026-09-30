from typing import Any, Literal

from pydantic import BaseModel


PolicyDecision = Literal["ALLOW", "REVIEW", "BLOCK", "QUARANTINE"]


class InjectionScore(BaseModel):
    score: float
    label: str
    model: str
    latency_ms: int


class PrivacyEntity(BaseModel):
    kind: str
    start: int
    end: int


class PrivacyResult(BaseModel):
    pii_detected: bool
    entities: list[PrivacyEntity]
    redaction_count: int
    sanitized_text: str
    pii_redacted: bool | None = None


class EvidenceItem(BaseModel):
    email_id: str
    chunk_id: str
    parent_id: str | None = None
    section: str | None = None
    title: str | None = None
    preview: str
    decision: str
    injection_score: float | None = None
    boundary_reason: str | None = None
    char_count: int | None = None
    token_estimate: int | None = None
    quarantined: bool = False


class Citation(BaseModel):
    email_id: str
    chunk_id: str


class PipelineStage(BaseModel):
    id: str
    label: str
    state: str
    duration_ms: int | None = None
    risk: float | None = None
    count_label: str | None = None
