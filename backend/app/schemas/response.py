from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.query import QuerySecurity
from app.schemas.retrieval import RetrievalStats
from app.schemas.security import Citation, EvidenceItem, PipelineStage, PrivacyResult


class ComponentStatus(BaseModel):
    status: str
    detail: str | None = None
    emails: int | None = None
    model: str | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
    corpus_emails: int
    source_emails: int
    indexed_email_count: int
    chunk_count: int
    index_status: str
    index_ready: bool
    classifier_ready: bool
    llm_ready: bool
    embedding_ready: bool
    dataset: ComponentStatus
    embedding: ComponentStatus
    classifier: ComponentStatus
    llm: ComponentStatus
    retrieval: ComponentStatus
    voice: ComponentStatus
    privacy: ComponentStatus


class TranscriptionResponse(BaseModel):
    transcript: str
    duration_ms: int
    provider: str = "whisper"


class ChunkInspectorResponse(BaseModel):
    chunk_id: str
    email_id: str
    parent_id: str | None = None
    section: str | None = None
    boundary_reason: str | None = None
    char_count: int | None = None
    token_estimate: int | None = None
    injection_score: float | None = None
    decision: str | None = None
    preview: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrustResponse(BaseModel):
    trust_score: float
    state: str
    step_up_required: bool
    high_risk_queries: int = 0


class VerifyRequest(BaseModel):
    challenge: str = ""


class VerifyResponse(BaseModel):
    verified: bool
    trust_score: float
    state: str


class QueryResponse(BaseModel):
    request_id: str
    status: Literal["ok", "blocked", "refused", "error"]
    transcript: str | None = None
    query_security: QuerySecurity | None = None
    retrieval: RetrievalStats | None = None
    answer: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    privacy: PrivacyResult | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    pipeline: list[PipelineStage] = Field(default_factory=list)
    reason: str | None = None
    risk_score: float | None = None
    llm_called: bool = False
    grounded: bool | None = None
    source: str | None = None
    trace: dict[str, Any] = Field(default_factory=dict)
