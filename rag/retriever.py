"""Compatibility wrapper for LangGraph RetrievalNode."""

from __future__ import annotations

from langchain_core.documents import Document

from rag.retrievers.hybrid_retriever import HybridRetriever
from rag.types import RetrievalResult

_retriever: HybridRetriever | None = None


def get_hybrid_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


async def retrieve_documents(
    query: str,
    department: str = "",
    k: int | None = None,
    language: str = "",
) -> tuple[list[Document], list[float], bool]:
    results, cache_hit, _confidence = await get_hybrid_retriever().retrieve(
        query,
        department=department,
        language=language,
        k=k,
    )
    docs = [
        Document(
            page_content=result.text,
            metadata=result.metadata.model_dump() | {"citation": result.citation, "source": result.metadata.source_url or result.metadata.source_path},
        )
        for result in results
    ]
    return docs, [result.score for result in results], cache_hit


async def retrieve_rag_results(
    query: str,
    department: str = "",
    k: int | None = None,
    language: str = "",
) -> tuple[list[RetrievalResult], bool, float]:
    return await get_hybrid_retriever().retrieve(query, department=department, language=language, k=k)


async def retrieve_multilingual_results(
    query: str,
    department: str = "",
    k: int | None = None,
    response_language: str | None = None,
    db=None,
) -> dict:
    from multilingual.retrieval.multilingual_retriever import MultilingualRetriever

    return await MultilingualRetriever().retrieve(
        query,
        department=department,
        response_language=response_language,
        k=k or 5,
        db=db,
    )
