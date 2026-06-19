"""Mock VectorStore for tests."""

from __future__ import annotations

from typing import Any

from rag.types import DocumentChunk, RetrievalResult
from rag.vectorstore.base import BaseVectorStore

class MockVectorStore(BaseVectorStore):
    def __init__(self):
        self.chunks: list[DocumentChunk] = []
        
    def add_chunks(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        self.chunks.extend(chunks)
        return {"indexed": len(chunks), "duplicates": 0}
        
    def rebuild(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        self.chunks = list(chunks)
        return {"indexed": len(chunks), "duplicates": 0}
        
    def similarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None
    ) -> list[tuple[RetrievalResult, float]]:
        results = []
        for i, chunk in enumerate(self.chunks[:k]):
            res = RetrievalResult(
                text=chunk.text,
                score=1.0 - (i * 0.1),
                metadata=chunk.metadata,
                citation=chunk.metadata.title or "mock citation"
            )
            results.append((res, float(i)))
        return results
        
    def stats(self) -> dict[str, Any]:
        return {"loaded": True, "chunks": len(self.chunks)}
