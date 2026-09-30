from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import Settings


class EmbeddingProvider(ABC):
    model_name: str

    @abstractmethod
    def embed_text(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def embed_many(self, texts: list[str]):
        raise NotImplementedError


class TfidfEmbeddingProvider(EmbeddingProvider):
    """Persisted corpus-trained sparse text embedding model."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.model_name = "tfidf-embedding-v1"
        self._vectorizer = joblib.load(path) if path.exists() else None

    def fit(self, texts: list[str]) -> None:
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self._vectorizer.fit(texts)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._vectorizer, self.path)

    def embed_text(self, text: str):
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]):
        if self._vectorizer is None:
            raise RuntimeError("embedding vectorizer is not trained")
        return self._vectorizer.transform(texts)

    def reload(self) -> None:
        self._vectorizer = joblib.load(self.path) if self.path.exists() else None


def build_embedding_provider(settings: Settings) -> tuple[EmbeddingProvider | None, str, str]:
    provider = TfidfEmbeddingProvider(settings.embedding_vectorizer_file)
    return provider, "ready" if provider._vectorizer is not None else "waiting", provider.model_name
