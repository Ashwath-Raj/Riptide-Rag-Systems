from typing import Annotated

from fastapi import APIRouter, File, Request, UploadFile

from app.schemas.response import TranscriptionResponse
from app.services.transcription import transcribe_audio

router = APIRouter()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(request: Request, audio: Annotated[UploadFile, File()]) -> TranscriptionResponse:
    settings = request.app.state.settings
    transcript, duration_ms = transcribe_audio(
        settings,
        audio.filename or "recording.webm",
        audio.content_type or "audio/webm",
        await audio.read(),
    )
    return TranscriptionResponse(transcript=transcript, duration_ms=duration_ms)