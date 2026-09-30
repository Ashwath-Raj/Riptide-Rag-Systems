from fastapi import APIRouter, Request

from app.schemas.response import TrustResponse, VerifyRequest, VerifyResponse
from app.services.runtime import Runtime

router = APIRouter()


@router.get("/session/trust", response_model=TrustResponse)
def session_trust(request: Request) -> TrustResponse:
    runtime: Runtime = request.app.state.runtime
    session = runtime.session
    return TrustResponse(
        trust_score=round(session.trust_score, 3),
        state=session.state,
        step_up_required=session.step_up_required,
        high_risk_queries=session.high_risk_queries,
    )


@router.post("/verify", response_model=VerifyResponse)
def verify(payload: VerifyRequest, request: Request) -> VerifyResponse:
    runtime: Runtime = request.app.state.runtime
    if payload.challenge.strip().upper() in {"CONFIRM", "VERIFY", "OK"}:
        runtime.session.verify()
        return VerifyResponse(verified=True, trust_score=runtime.session.trust_score, state=runtime.session.state)
    return VerifyResponse(verified=False, trust_score=runtime.session.trust_score, state=runtime.session.state)
