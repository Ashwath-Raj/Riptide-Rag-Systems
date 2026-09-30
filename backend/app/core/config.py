from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    embedding_model: str = "tfidf-embedding-v1"
    embedding_vectorizer_path: str = "data/index/embedding_vectorizer.joblib"
    injection_model_path: str = "data/models/injection_classifier.joblib"
    injection_vectorizer_path: str = "data/models/injection_vectorizer.joblib"
    whisper_api_key: str = ""
    whisper_model: str = "whisper-1"
    whisper_base_url: str = "https://api.openai.com/v1"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    model: str = ""

    injection_allow_threshold: float = 0.30
    injection_block_threshold: float = 0.70

    dataset_root: str = str(PROJECT_ROOT / "datasets")
    data_dir: str = str(PROJECT_ROOT / "data")
    top_k: int = 5

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir).resolve()

    @property
    def processed_dir(self) -> Path:
        return self.data_path / "processed"

    @property
    def index_dir(self) -> Path:
        return self.data_path / "index"

    @property
    def fixtures_dir(self) -> Path:
        return self.data_path / "fixtures"

    @property
    def injection_model_file(self) -> Path:
        return (PROJECT_ROOT / self.injection_model_path).resolve()

    @property
    def injection_vectorizer_file(self) -> Path:
        return (PROJECT_ROOT / self.injection_vectorizer_path).resolve()

    @property
    def embedding_vectorizer_file(self) -> Path:
        return (PROJECT_ROOT / self.embedding_vectorizer_path).resolve()

    @property
    def whisper_ready(self) -> bool:
        return bool(self.whisper_api_key.strip())

    @property
    def dataset_root_path(self) -> Path:
        return Path(self.dataset_root).resolve()

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
