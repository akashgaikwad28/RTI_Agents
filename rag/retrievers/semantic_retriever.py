"""Async semantic retriever over the persistent FAISS store."""

from __future__ import annotations

from config.settings import settings
from rag.retrievers.metadata_filter import build_filters
from rag.types import RetrievalResult
from rag.vectorstore import get_vector_store


class SemanticRetriever:
    def __init__(self):
        self.store = get_vector_store()

    async def retrieve(
        self,
        query: str,
        *,
        department: str = "",
        language: str = "",
        document_type: str = "",
        k: int | None = None,
    ) -> list[RetrievalResult]:
        filters = build_filters(department=department, language=language, document_type=document_type)
        results = await self.store.asimilarity_search_with_score(
            query,
            k=k or getattr(settings, "FAISS_TOP_K", settings.RAG_TOP_K),
            filters=filters or None,
        )
        threshold = settings.RAG_SIMILARITY_THRESHOLD
        return [result for result, _distance in results if result.score >= threshold]

