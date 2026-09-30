from __future__ import annotations

from abc import ABC, abstractmethod
import joblib
import time

from app.core.config import Settings
from app.core.errors import SecurityGateUnavailable
from app.schemas.security import InjectionScore

class InjectionClassifier(ABC):
    model_name: str
    available: bool

    @abstractmethod
    def score(self, text: str) -> InjectionScore:
        raise NotImplementedError


class LocalInjectionClassifier(InjectionClassifier):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.available = False
        self.model_name = "unavailable"
        self._classifier = None
        self._vectorizer = None
        self._load()

    def _load(self) -> None:
        try:
            self._classifier = joblib.load(self.settings.injection_model_file)
            self._vectorizer = joblib.load(self.settings.injection_vectorizer_file)
        except Exception:
            return False
        self.model_name = "tfidf-logistic-injection"
        self.available = True

    def score(self, text: str) -> InjectionScore:
        if not self.available:
            raise SecurityGateUnavailable("SECURITY MODEL UNAVAILABLE")
        started = time.perf_counter()
        vector = self._vectorizer.transform([text])
        probabilities = self._classifier.predict_proba(vector)[0]
        classes = list(self._classifier.classes_)
        malicious_index = next(
            (
                index
                for index, value in enumerate(classes)
                if str(value).strip().lower()
                in {"1", "true", "injection", "malicious", "unsafe"}
            ),
            None,
        )
        if malicious_index is None:
            raise SecurityGateUnavailable("CLASSIFIER HAS NO MALICIOUS CLASS")
        risk = float(probabilities[malicious_index])
        label = "malicious" if risk >= 0.5 else "benign"
        latency = int((time.perf_counter() - started) * 1000)
        return InjectionScore(score=round(float(risk), 4), label=label, model=self.model_name, latency_ms=latency)
