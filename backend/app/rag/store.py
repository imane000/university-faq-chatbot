"""Persistent Chroma storage using the same embedding function for all operations."""

from functools import lru_cache
from hashlib import sha256

import chromadb
from app.config import get_settings
from chromadb.config import Settings as ChromaSettings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


@lru_cache
def get_client():
    return chromadb.PersistentClient(
        path=str(get_settings().chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


@lru_cache
def get_embedding_function():
    # Local ONNX all-MiniLM-L6-v2; downloads model weights on first use.
    return DefaultEmbeddingFunction()


def get_collection(*, create: bool = False):
    client = get_client()
    kwargs = dict(
        name=get_settings().chroma_collection,
        embedding_function=get_embedding_function(),
    )
    if create:
        return client.get_or_create_collection(
            **kwargs, configuration={"hnsw": {"space": "cosine"}}
        )
    return client.get_collection(**kwargs)


def sync_source(collection, source: str, texts: list[str], metadata: list[dict]) -> int:
    """Upsert a source, then remove its obsolete chunks. Re-running is idempotent.

    Ingestion is an offline, single-writer operation. Deleting a source file requires
    rebuilding the index; it is never inferred from an incomplete input directory.
    """
    ids = [sha256(f"{source}:{i}:{text}".encode()).hexdigest() for i, text in enumerate(texts)]
    old_ids = set(collection.get(where={"source": source}, include=[])["ids"])
    batch_size = min(100, get_client().get_max_batch_size())
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.upsert(
            ids=ids[start:end], documents=texts[start:end], metadatas=metadata[start:end]
        )
    stale = sorted(old_ids - set(ids))
    for start in range(0, len(stale), batch_size):
        collection.delete(ids=stale[start : start + batch_size])
    return len(ids)
