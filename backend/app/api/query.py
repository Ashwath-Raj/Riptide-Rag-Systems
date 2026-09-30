from fastapi import APIRouter, Request

from app.core.errors import SecurityGateUnavailable
from app.schemas.query import QueryRequest, QueryScoreRequest, QueryScoreResponse, QuerySecurity
from app.schemas.response import QueryResponse
from app.services.runtime import Runtime

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, request: Request) -> QueryResponse:
    runtime: Runtime = request.app.state.runtime
    runtime.refresh_retriever()
    return runtime.run_query(payload.query.strip(), payload.source)


@router.post("/query/score", response_model=QueryScoreResponse)
def score_query(payload: QueryScoreRequest, request: Request) -> QueryScoreResponse:
    runtime: Runtime = request.app.state.runtime
    if not runtime.classifier.available:
        raise SecurityGateUnavailable()
    result = runtime.classifier.score(payload.query)
    decision = runtime.policy.evaluate_query(result.score)
    return QueryScoreResponse(
        risk_score=result.score,
        decision=decision.lower(),
        label=result.label,
        model=result.model,
    )
