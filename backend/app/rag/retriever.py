"""Semantic top-k search over the shared FAQ/PDF Chroma collection."""

from dataclasses import dataclass

from app.config import get_settings
from app.rag.store import get_collection
from chromadb.errors import NotFoundError


@dataclass(frozen=True)
class Passage:
    id: str
    text: str
    source: str
    page: int | None
    distance: float


def retrieve_passages(question: str) -> list[Passage]:
    if not question.strip():
        return []
    try:
        collection = get_collection()
    except NotFoundError:
        return []
    count = collection.count()
    if not count:
        return []
    settings = get_settings()
    result = collection.query(
        query_texts=[question],
        n_results=min(settings.rag_top_k, count),
        include=["documents", "metadatas", "distances"],
    )
    passages = []
    remaining = settings.rag_context_chars
    for doc_id, text, metadata, distance in zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
        strict=True,
    ):
        if not text or distance > settings.rag_max_distance:
            continue
        if remaining <= 0:
            break
        metadata = metadata or {}
        excerpt = text[:remaining]
        passages.append(
            Passage(
                doc_id,
                excerpt,
                metadata.get("source", "unknown"),
                metadata.get("page"),
                float(distance),
            )
        )
        remaining -= len(excerpt)
    return passages


def format_context(passages: list[Passage]) -> str:
    return "\n\n".join(
        f"[{i}] Source: {p.source}" + (f", page {p.page}" if p.page else "") + f"\n{p.text}"
        for i, p in enumerate(passages, start=1)
    )


def retrieve_context(question: str) -> str:
    return format_context(retrieve_passages(question))
