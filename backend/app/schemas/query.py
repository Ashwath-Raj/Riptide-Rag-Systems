from typing import Any, Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    source: Literal["voice", "typed"] = "typed"


class QueryScoreRequest(BaseModel):
    query: str = Field(min_length=1)


class QuerySecurity(BaseModel):
    risk_score: float
    decision: str
    label: str | None = None
    model: str | None = None
    latency_ms: int | None = None


class QueryScoreResponse(BaseModel):
    risk_score: float
    decision: str
    label: str | None = None
    model: str | None = None
