"""Offline tests: real persistent Chroma, deterministic test-only embeddings."""

import re

import pytest
from app.config import Settings
from app.rag import store
from app.services import llm_service
from chromadb import EmbeddingFunction


class TestEmbeddings(EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input):
        topics = [r"inscription|registration", r"biblioth|library", r"examen|exam"]
        return [
            [1.0 if re.search(topic, text.lower()) else 0.0 for topic in topics] + [0.01]
            for text in input
        ]

    @staticmethod
    def name():
        return "deterministic-test-embeddings"

    def get_config(self):
        return {}

    @staticmethod
    def build_from_config(config):
        return TestEmbeddings()


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    settings = Settings(
        _env_file=None,
        groq_api_key="",
        chroma_path=tmp_path / "chroma",
        data_path=tmp_path,
        rag_max_distance=0.2,
    )
    from app import config

    monkeypatch.setattr(config, "get_settings", lambda: settings)
    from app.rag import ingest_faq, ingest_pdf, retriever

    for module in [store, ingest_faq, ingest_pdf, retriever, llm_service]:
        monkeypatch.setattr(module, "get_settings", lambda: settings)
    monkeypatch.setattr(store, "get_embedding_function", TestEmbeddings)
    store.get_client.cache_clear()
    cached_groq_client = llm_service.get_groq_client
    cached_groq_client.cache_clear()
    yield settings
    store.get_client.cache_clear()
    cached_groq_client.cache_clear()
