from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionTrust:
    trust_score: float = 1.0
    high_risk_queries: int = 0

    @property
    def state(self) -> str:
        if self.trust_score < 0.4:
            return "restricted"
        if self.trust_score < 0.7:
            return "elevated"
        return "normal"

    @property
    def step_up_required(self) -> bool:
        return self.state == "restricted"

    def register_high_risk(self) -> None:
        self.high_risk_queries += 1
        self.trust_score = max(0.0, self.trust_score - 0.25)

    def register_repeated_probe(self) -> None:
        self.trust_score = max(0.0, self.trust_score - 0.15)

    def verify(self) -> None:
        self.trust_score = min(1.0, self.trust_score + 0.4)
        if self.trust_score >= 0.7:
            self.high_risk_queries = 0
