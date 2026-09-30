from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

from app.api import chunks, health, query, session, transcribe
from app.core.config import get_settings
from app.core.errors import RiptideError
from app.core.logging import configure_logging
from app.services.runtime import create_runtime
from app.services.privacy_guard import PrivacyGuard


class PiiReleaseMiddleware:
    """Sanitize every JSON response string before bytes leave the backend."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_start = None
        body_parts = []
        json_response = False

        async def guarded_send(message):
            nonlocal response_start, json_response
            if message["type"] == "http.response.start":
                response_start = message
                headers = {key.lower(): value for key, value in message.get("headers", [])}
                json_response = b"application/json" in headers.get(b"content-type", b"").lower()
                if not json_response:
                    await send(message)
                return

            if message["type"] != "http.response.body" or not json_response:
                await send(message)
                return

            body_parts.append(message.get("body", b""))
            if message.get("more_body", False):
                return

            try:
                payload = json.loads(b"".join(body_parts))
                privacy = PrivacyGuard()

                def sanitize(value):
                    if isinstance(value, str):
                        return privacy.redact(value).sanitized_text
                    if isinstance(value, list):
                        return [sanitize(item) for item in value]
                    if isinstance(value, dict):
                        return {key: sanitize(item) for key, item in value.items()}
                    return value

                body = json.dumps(sanitize(payload), ensure_ascii=False).encode("utf-8")
                status = response_start["status"]
                headers = [
                    (key, value)
                    for key, value in response_start.get("headers", [])
                    if key.lower() not in {b"content-length", b"content-encoding"}
                ]
            except Exception:
                body = b'{"status":"refused","reason":"privacy_gate_unavailable"}'
                status = 503
                headers = [(b"content-type", b"application/json")]

            headers.append((b"content-length", str(len(body)).encode("ascii")))
            await send({"type": "http.response.start", "status": status, "headers": headers})
            await send({"type": "http.response.body", "body": body, "more_body": False})

        await self.app(scope, receive, guarded_send)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    application = FastAPI(title="RIPTIDE", version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(PiiReleaseMiddleware)
    application.state.settings = settings
    application.state.runtime = create_runtime(settings)

    @application.exception_handler(RiptideError)
    async def riptide_error(_, exc: RiptideError) -> JSONResponse:
        return JSONResponse(
            status_code=503 if "unavailable" in exc.code else 400,
            content={"status": "refused", "reason": exc.code, "message": exc.message},
        )

    application.include_router(health.router, prefix="/api")
    application.include_router(query.router, prefix="/api")
    application.include_router(chunks.router, prefix="/api")
    application.include_router(session.router, prefix="/api")
    application.include_router(transcribe.router, prefix="/api")
    return application


app = create_app()
