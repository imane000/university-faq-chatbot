import pytest
from app.config import BACKEND_DIR, Settings
from pydantic import ValidationError


def test_paths_are_anchored_to_backend(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=None, chroma_path="chroma_db", data_path="data")
    assert settings.chroma_path == BACKEND_DIR / "chroma_db"
    assert settings.data_path == BACKEND_DIR / "data"
    assert Settings(_env_file=None, chroma_path=tmp_path).chroma_path == tmp_path


def test_secrets_are_redacted_and_cors_validated():
    settings = Settings(_env_file=None, groq_api_key="test-only-secret")
    assert "test-only-secret" not in repr(settings)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=["*"])
    with pytest.raises(ValidationError):
        Settings(_env_file=None, rag_top_k=0)
