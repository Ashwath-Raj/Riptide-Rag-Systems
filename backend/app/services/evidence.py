from __future__ import annotations

import re

from app.schemas.retrieval import RetrievalHit


CITATION_RE = re.compile(r"\[(\d+)\]")


class EvidenceValidator:
    """Sprint-scope validator: citation markers must point at admitted evidence."""

    def validate(self, answer: str, chunks: list[RetrievalHit]) -> str:
        if not chunks:
            return "INSUFFICIENT"
        if not answer.strip():
            return "INSUFFICIENT"
        markers = [int(item) for item in CITATION_RE.findall(answer)]
        if not markers:
            return "INSUFFICIENT"
        if any(marker < 1 or marker > len(chunks) for marker in markers):
            return "INSUFFICIENT"
        return "SUPPORTED"
