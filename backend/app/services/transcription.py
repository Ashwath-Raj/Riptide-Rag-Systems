from __future__ import annotations

import json
import time
import urllib.request
import uuid

from app.core.config import Settings
from app.core.errors import TranscriptionUnavailable


def transcribe_audio(settings: Settings, filename: str, content_type: str, audio: bytes) -> tuple[str, int]:
    if not settings.whisper_ready:
        raise TranscriptionUnavailable("WHISPER_API_KEY is not configured")
    started = time.perf_counter()
    boundary = f"----riptide-{uuid.uuid4().hex}"
    fields = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{settings.whisper_model}\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename or 'recording.webm'}\"\r\n"
        f"Content-Type: {content_type or 'audio/webm'}\r\n\r\n"
    ).encode("utf-8")
    body = fields + audio + f"\r\n--{boundary}--\r\n".encode("utf-8")
    request = urllib.request.Request(
        f"{settings.whisper_base_url.rstrip('/')}/audio/transcriptions",
        data=body,
        headers={
            "Authorization": f"Bearer {settings.whisper_api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
        transcript = str(payload.get("text") or "").strip()
        if not transcript:
            raise TranscriptionUnavailable("Whisper returned an empty transcript")
    except TranscriptionUnavailable:
        raise
    except Exception as exc:
        raise TranscriptionUnavailable("Whisper request failed") from exc
    return transcript, int((time.perf_counter() - started) * 1000)