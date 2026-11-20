"""One configuration shared by the API and ingestion commands."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    groq_api_key: SecretStr = SecretStr("")
    groq_model: str = "openai/gpt-oss-20b"
    groq_timeout_seconds: float = Field(default=30, gt=0, le=120)
    groq_max_tokens: int = Field(default=1024, ge=128, le=4096)
    chroma_path: Path = BACKEND_DIR / "chroma_db"
    chroma_collection: str = "university_knowledge"
    data_path: Path = BACKEND_DIR / "data"
    rag_top_k: int = Field(default=4, ge=1, le=20)
    rag_max_distance: float = Field(default=0.5, ge=0, le=2)
    rag_context_chars: int = Field(default=8000, ge=1000, le=24000)
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("chroma_path", "data_path")
    @classmethod
    def resolve_paths(cls, value: Path) -> Path:
        return value if value.is_absolute() else (BACKEND_DIR / value).resolve()

    @field_validator("cors_origins")
    @classmethod
    def explicit_origins(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("Configure explicit CORS origins")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
