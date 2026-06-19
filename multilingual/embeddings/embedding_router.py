"""Router for multilingual embedding providers."""

from __future__ import annotations

from multilingual.embeddings.multilingual_embedder import MultilingualEmbedder

_embedder: MultilingualEmbedder | None = None


def get_multilingual_embedder(provider: str = "gemini") -> MultilingualEmbedder:
    global _embedder
    if _embedder is None or _embedder.provider != provider:
        _embedder = MultilingualEmbedder(provider)
    return _embedder
