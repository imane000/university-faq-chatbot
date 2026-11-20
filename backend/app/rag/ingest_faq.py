"""Run from backend: python -m app.rag.ingest_faq."""

import json
from pathlib import Path

from app.config import get_settings
from app.rag.store import get_collection, sync_source
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class FAQItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


def ingest_faq(path: Path | None = None) -> int:
    path = path or get_settings().data_path / "faq.json"
    items = TypeAdapter(list[FAQItem]).validate_python(json.loads(path.read_text(encoding="utf-8")))
    source = path.name
    texts = [f"Question: {item.question}\nRéponse: {item.answer}" for item in items]
    metadata = [{"source": source, "source_type": "faq", "chunk": i} for i in range(len(texts))]
    return sync_source(get_collection(create=True), source, texts, metadata)


if __name__ == "__main__":
    print(f"Indexed {ingest_faq()} FAQ entries.")
