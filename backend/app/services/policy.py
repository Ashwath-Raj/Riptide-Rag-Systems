from __future__ import annotations

from app.core.config import Settings
from app.schemas.security import PolicyDecision


class SecurityPolicy:
    def __init__(self, settings: Settings) -> None:
        self.allow_threshold = settings.injection_allow_threshold
        self.block_threshold = settings.injection_block_threshold

    def evaluate_query(self, score: float) -> PolicyDecision:
        if score >= self.block_threshold:
            return "BLOCK"
        if score > self.allow_threshold:
            return "REVIEW"
        return "ALLOW"

    def evaluate_chunk(self, score: float) -> PolicyDecision:
        if score >= self.block_threshold:
            return "QUARANTINE"
        if score > self.allow_threshold:
            return "REVIEW"
        return "ALLOW"

    def query_blocks(self, decision: PolicyDecision) -> bool:
        return decision == "BLOCK"

    def chunk_quarantines(self, decision: PolicyDecision) -> bool:
        return decision in {"REVIEW", "QUARANTINE", "BLOCK"}
