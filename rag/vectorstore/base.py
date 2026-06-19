"""Base abstraction for vector database storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rag.types import DocumentChunk, RetrievalResult

class BaseVectorStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        """Adds semantic chunks to the vector store."""
        pass
        
    @abstractmethod
    def rebuild(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        """Rebuilds the vector store entirely from new chunks."""
        pass
        
    @abstractmethod
    def similarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None
    ) -> list[tuple[RetrievalResult, float]]:
        """Performs a similarity search returning results and scores."""
        pass
        
    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Returns the health and statistics of the vector store."""
        pass
