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
        from observability.structured_logger import get_logger
        logger = get_logger(__name__)

        valid_documents: list[LoadedDocument] = []
        failed_files: list[str] = []
        for doc in documents:
            try:
                # Validate document has non-empty text before chunking
                if not doc.text or not doc.text.strip():
                    raise ValueError("Document has empty text body")
                valid_documents.append(doc)
            except Exception as exc:
                src = doc.metadata.source_url or doc.metadata.source_path or "unknown"
                logger.warning(f"[VectorManager] Skipping bad document '{src}': {exc}")
                failed_files.append(src)

        chunks = self.chunker.chunk_documents(valid_documents)
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
            failed_files=failed_files,
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
