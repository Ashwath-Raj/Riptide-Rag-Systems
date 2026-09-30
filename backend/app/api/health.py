from fastapi import APIRouter, Request

from app.schemas.response import HealthResponse
from app.services.runtime import Runtime

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    runtime: Runtime = request.app.state.runtime
    runtime.refresh_retriever()
    return HealthResponse.model_validate(runtime.health())
