"""Semantic memory for successful RTI requests.

Stores historical RTI applications in a separate FAISS index so future routing
and drafting can retrieve similar prior requests without mixing them into the
government document corpus.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rag.ingestion.chunking.chunker import _hash
from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.types import DocumentChunk, LoadedDocument, RetrievalResult
from rag.vectorstore.faiss_store import RealFaissStore


class SemanticMemory:
    def __init__(self, index_path: str | Path = "data/vector_store/semantic_memory"):
        self.store = RealFaissStore(index_path=index_path)

    async def remember_successful_request(self, *, query: str, formal_query: str, department: str, metadata: dict[str, Any] | None = None) -> dict:
        text = "\n\n".join(part for part in [query, formal_query] if part)
        doc_metadata = build_metadata(
            text=text,
            department=department,
            document_type="historical_rti",
            title=f"Historical RTI {datetime.now(timezone.utc).date().isoformat()}",
            extra=metadata or {},
        )
        document = LoadedDocument(text=text, metadata=doc_metadata)
        content_hash = _hash(text)
        chunk = DocumentChunk(
            text=text,
            metadata=document.metadata,
            chunk_id=f"memory:{content_hash[:24]}",
            chunk_index=0,
            content_hash=content_hash,
        )
        return await self.store.aadd_chunks([chunk])

    async def retrieve_similar(self, query: str, *, department: str = "", k: int = 5) -> list[RetrievalResult]:
        filters = {"department": department} if department else None
        results = await self.store.asimilarity_search_with_score(query, k=k, filters=filters)
        return [result for result, _distance in results]

