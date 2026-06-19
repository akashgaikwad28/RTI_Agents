"""Mock embedder for deterministic, zero-cost tests."""

from __future__ import annotations

import hashlib

from langchain_core.embeddings import Embeddings

class MockEmbedder(Embeddings):
    """Produces deterministic 768-dimensional vectors based on text hash."""
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        base_hash = hashlib.md5(text.encode("utf-8")).digest()
        vector = []
        for i in range(768):
            byte_val = base_hash[i % 16]
            vector.append(float(byte_val) / 255.0)
        return vector

class MockEmbeddingRouter:
    def get_langchain_embedder(self) -> Embeddings:
        return MockEmbedder()
