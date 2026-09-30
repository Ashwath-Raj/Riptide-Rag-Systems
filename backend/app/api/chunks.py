from fastapi import APIRouter, HTTPException, Request

from app.schemas.response import ChunkInspectorResponse
from app.services.privacy_guard import PrivacyGuard
from app.services.retrieval import load_chunk_record
from app.services.runtime import Runtime

router = APIRouter()


@router.get("/chunks/{chunk_id}", response_model=ChunkInspectorResponse)
def get_chunk(chunk_id: str, request: Request) -> ChunkInspectorResponse:
    runtime: Runtime = request.app.state.runtime
    rec = load_chunk_record(runtime.settings.index_dir, chunk_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="chunk_not_found")
    preview = PrivacyGuard().redact_preview(rec.get("text") or "", limit=400)
    return ChunkInspectorResponse(
        chunk_id=rec["chunk_id"],
        email_id=rec["email_id"],
        parent_id=rec.get("parent_id"),
        section=rec.get("section"),
        boundary_reason=rec.get("boundary_reason"),
        char_count=rec.get("char_count"),
        token_estimate=rec.get("token_estimate"),
        preview=preview,
        metadata=rec.get("source_metadata") or {},
    )
