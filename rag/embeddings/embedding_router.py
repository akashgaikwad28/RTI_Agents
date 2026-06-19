"""Embedding provider router.

Supports:
- gemini: GoogleGenerativeAIEmbeddings (API key required)
- local_sentence_transformers: sentence-transformers (no external API keys)

The returned provider object must expose `get_langchain_embedder()`.
"""

from __future__ import annotations

from typing import Any

from rag.embeddings.gemini_embedder import GeminiEmbedder
from rag.embeddings.local_sentence_transformer_embedder import (
    LocalSentenceTransformerEmbedder,
)

_embedder: Any | None = None
_embedder_provider: str | None = None


def get_embedder(provider: str | None = None) -> Any:
    """Return a cached embedder instance for the chosen provider."""
    global _embedder, _embedder_provider

    if provider is None:
        try:
            from config.settings import settings

            provider = getattr(settings, "RAG_EMBEDDING_PROVIDER", "local_sentence_transformers")
        except Exception:
            provider = "local_sentence_transformers"

    chosen = provider

    if _embedder is None or _embedder_provider != chosen:
        if chosen == "gemini":
            _embedder = GeminiEmbedder()
        elif chosen == "local_sentence_transformers":
            _embedder = LocalSentenceTransformerEmbedder()
        else:
            raise ValueError(f"Unsupported embedding provider: {chosen}")

        _embedder_provider = chosen

    return _embedder


