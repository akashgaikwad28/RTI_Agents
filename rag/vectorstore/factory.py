"""Factory for dynamic vector database loading based on active settings."""

from __future__ import annotations

from config.settings import settings
from rag.vectorstore.base import BaseVectorStore
from rag.vectorstore.faiss_store import get_faiss_store

_vector_store: BaseVectorStore | None = None


def get_vector_store() -> BaseVectorStore:
    """Gets the active vector store singleton configured in settings."""
    global _vector_store
    if _vector_store is None:
        if getattr(settings, "VECTORSTORE_TYPE", "faiss") == "mongodb":
            from rag.vectorstore.mongo_store import get_mongo_store
            _vector_store = get_mongo_store()
        else:
            _vector_store = get_faiss_store()
    return _vector_store
