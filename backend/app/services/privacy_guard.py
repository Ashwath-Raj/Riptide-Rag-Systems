from __future__ import annotations

import re

from app.core.errors import PrivacyGateUnavailable
from app.schemas.security import PrivacyEntity, PrivacyResult

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(
    r"(?:(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4})"
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class PrivacyGuard:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def scan(self, text: str) -> PrivacyResult:
        if not self.enabled:
            raise PrivacyGateUnavailable()
        entities: list[PrivacyEntity] = []
        for match in EMAIL_RE.finditer(text):
            entities.append(PrivacyEntity(kind="email", start=match.start(), end=match.end()))
        for match in PHONE_RE.finditer(text):
            if "@" in match.group(0):
                continue
            entities.append(PrivacyEntity(kind="phone", start=match.start(), end=match.end()))
        for match in SSN_RE.finditer(text):
            entities.append(PrivacyEntity(kind="identifier", start=match.start(), end=match.end()))
        entities = self._merge_entities(entities)
        sanitized = self._apply(text, entities)
        return PrivacyResult(
            pii_detected=bool(entities),
            entities=entities,
            redaction_count=len(entities),
            sanitized_text=sanitized,
            pii_redacted=bool(entities),
        )

    def redact(self, text: str) -> PrivacyResult:
        return self.scan(text)

    def _apply(self, text: str, entities: list[PrivacyEntity]) -> str:
        if not entities:
            return text
        chars = list(text)
        for entity in reversed(entities):
            labels = {"email": "[REDACTED_EMAIL]", "phone": "[REDACTED_PHONE]"}
            label = labels.get(entity.kind, "[REDACTED_IDENTIFIER]")
            chars[entity.start : entity.end] = list(label)
        return "".join(chars)

    def _merge_entities(self, entities: list[PrivacyEntity]) -> list[PrivacyEntity]:
        merged: list[PrivacyEntity] = []
        for entity in sorted(entities, key=lambda item: (item.start, -(item.end - item.start))):
            if merged and entity.start < merged[-1].end:
                if entity.end > merged[-1].end:
                    merged[-1] = PrivacyEntity(
                        kind=merged[-1].kind,
                        start=merged[-1].start,
                        end=entity.end,
                    )
                continue
            merged.append(entity)
        return merged

    def redact_preview(self, text: str, limit: int = 180) -> str:
        sanitized = self.scan(text).sanitized_text.replace("\n", " ")
        return sanitized[:limit].strip()
