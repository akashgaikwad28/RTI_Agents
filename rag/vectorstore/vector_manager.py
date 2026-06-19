"""High-level FAISS lifecycle operations."""

from __future__ import annotations

from pathlib import Path

from config.settings import settings
from observability.metrics import documents_ingested_total
from rag.ingestion.chunking.chunker import SmartChunker
from rag.types import IngestionReport, LoadedDocument
from rag.vectorstore import get_vector_store


class VectorManager:
    def __init__(self):
        self.store = get_vector_store()
        self.chunker = SmartChunker()

    async def ingest_documents(self, documents: list[LoadedDocument], *, rebuild: bool = False) -> IngestionReport:
        chunks = self.chunker.chunk_documents(documents)
        if rebuild:
            result = await self.store.arebuild(chunks)
        else:
            result = await self.store.aadd_chunks(chunks)
        documents_ingested_total.labels(source="rag_pipeline").inc(result["indexed"])
        
        vector_path = str(getattr(self.store, "index_path", "mongodb_cloud"))
        return IngestionReport(
            documents_loaded=len(documents),
            chunks_created=len(chunks),
            chunks_indexed=result["indexed"],
            duplicates_skipped=result["duplicates"],
            vector_store_path=vector_path,
        )

    def stats(self) -> dict:
        return self.store.stats()

    async def astats(self) -> dict:
        astats = getattr(self.store, "astats", None)
        if astats is not None:
            return await astats()
        return self.store.stats()

    def exists(self) -> bool:
        index_path = getattr(self.store, "index_path", None)
        if index_path is not None:
            return Path(index_path, "index.faiss").exists()
        return True
