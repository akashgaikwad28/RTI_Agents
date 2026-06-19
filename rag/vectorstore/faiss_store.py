"""Persistent FAISS vector store with metadata manifest and duplicate control."""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from config.settings import settings
from observability.metrics import faiss_search_duration
from observability.structured_logger import get_logger
from rag.embeddings.embedding_router import get_embedder
from rag.types import DocumentChunk, DocumentMetadata, RetrievalResult
from rag.vectorstore.base import BaseVectorStore

logger = get_logger(__name__)

_store: "RealFaissStore | None" = None


class RealFaissStore(BaseVectorStore):
    def __init__(self, index_path: str | Path | None = None):
        self.index_path = Path(index_path or settings.FAISS_INDEX_PATH)
        self.manifest_path = self.index_path / "manifest.json"
        self.embedder = get_embedder().get_langchain_embedder()
        self.store: FAISS | None = None
        self.manifest: dict[str, dict[str, Any]] = {}
        self.index_path.mkdir(parents=True, exist_ok=True)
        self._load_manifest()
        self._load_index()

    @property
    def is_loaded(self) -> bool:
        return self.store is not None

    def _load_manifest(self) -> None:
        if self.manifest_path.exists():
            try:
                self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning(f"[FAISSStore] Failed to load manifest: {exc}")
                self.manifest = {}

    def _save_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_index(self) -> None:
        if not (self.index_path / "index.faiss").exists():
            logger.warning(f"[FAISSStore] No FAISS index found at {self.index_path}")
            return
        try:
            trusted_local_index = self._is_trusted_local_index()
            self.store = FAISS.load_local(
                str(self.index_path),
                self.embedder,
                allow_dangerous_deserialization=(
                    getattr(settings, "FAISS_ALLOW_DANGEROUS_DESERIALIZATION", False)
                    or trusted_local_index
                ),
            )
            logger.info(f"[FAISSStore] Loaded index from {self.index_path}")
        except ValueError as exc:
            logger.error(
                "[FAISSStore] Refused unsafe FAISS docstore deserialization. "
                "Set FAISS_ALLOW_DANGEROUS_DESERIALIZATION=true only for trusted local indexes."
            )
            logger.debug(str(exc))
            self.store = None
        except Exception as exc:
            logger.error(f"[FAISSStore] Failed to load index: {exc}")
            self.store = None

    def _is_trusted_local_index(self) -> bool:
        """Only auto-load LangChain's pickle docstore for indexes created inside this workspace."""
        try:
            root = Path.cwd().resolve()
            resolved = self.index_path.resolve()
            return self.manifest_path.exists() and resolved.is_relative_to(root)
        except Exception:
            return False

    def rebuild(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        docs, ids = self._chunks_to_documents(chunks, skip_existing=False)
        if not docs:
            self.store = None
            self.manifest = {}
            self._save_manifest()
            return {"indexed": 0, "duplicates": 0}
        self.store = FAISS.from_documents(docs, self.embedder, ids=ids)
        self.store.save_local(str(self.index_path))
        self.manifest = {doc.metadata["chunk_id"]: doc.metadata for doc in docs}
        self._save_manifest()
        logger.info(f"[FAISSStore] Rebuilt index with {len(docs)} chunks")
        return {"indexed": len(docs), "duplicates": len(chunks) - len(docs)}

    def add_chunks(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        docs, ids = self._chunks_to_documents(chunks, skip_existing=True)
        duplicates = len(chunks) - len(docs)
        if not docs:
            return {"indexed": 0, "duplicates": duplicates}
        if self.store is None:
            self.store = FAISS.from_documents(docs, self.embedder, ids=ids)
        else:
            self.store.add_documents(docs, ids=ids)
        self.store.save_local(str(self.index_path))
        for doc in docs:
            self.manifest[doc.metadata["chunk_id"]] = doc.metadata
        self._save_manifest()
        logger.info(f"[FAISSStore] Added {len(docs)} chunks, skipped {duplicates} duplicates")
        return {"indexed": len(docs), "duplicates": duplicates}

    async def aadd_chunks(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        return await asyncio.to_thread(self.add_chunks, chunks)

    async def arebuild(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        return await asyncio.to_thread(self.rebuild, chunks)

    def similarity_search(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        return [result for result, _distance in self.similarity_search_with_score(query, k=k, filters=filters)]

    def similarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[RetrievalResult, float]]:
        if self.store is None:
            return []
        started = time.perf_counter()
        fetch_k = max(k * 5, k)
        raw_results = self.store.similarity_search_with_score(query, k=fetch_k)
        faiss_search_duration.observe(time.perf_counter() - started)
        filtered: list[tuple[RetrievalResult, float]] = []
        for doc, distance in raw_results:
            if doc.metadata.get("is_active") is False:
                continue
            if filters and not _matches_filter(doc.metadata, filters):
                continue
            score = _distance_to_similarity(float(distance))
            metadata = DocumentMetadata.model_validate(_metadata_for_model(doc.metadata))
            filtered.append(
                (
                    RetrievalResult(
                        text=doc.page_content,
                        score=score,
                        metadata=metadata,
                        source="faiss",
                        citation=_citation(metadata),
                    ),
                    float(distance),
                )
            )
            if len(filtered) >= k:
                break
        return filtered

    async def asimilarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[RetrievalResult, float]]:
        return await asyncio.to_thread(self.similarity_search_with_score, query, k=k, filters=filters)

    def stats(self) -> dict[str, Any]:
        return {
            "index_path": str(self.index_path),
            "loaded": self.store is not None,
            "chunks": len(self.manifest),
            "departments": sorted({item.get("department", "") for item in self.manifest.values() if item.get("department")}),
            "languages": sorted({item.get("language", "") for item in self.manifest.values() if item.get("language")}),
        }

    def _chunks_to_documents(self, chunks: list[DocumentChunk], *, skip_existing: bool) -> tuple[list[Document], list[str]]:
        docs: list[Document] = []
        ids: list[str] = []
        seen_hashes = {item.get("content_hash") for item in self.manifest.values() if item.get("content_hash")}
        for chunk in chunks:
            if skip_existing and (chunk.chunk_id in self.manifest or chunk.content_hash in seen_hashes):
                continue
            metadata = chunk.metadata.model_dump()
            metadata.update(
                {
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "content_hash": chunk.content_hash,
                    "is_active": True,
                    "source": chunk.metadata.source_url or chunk.metadata.source_path,
                }
            )
            docs.append(Document(page_content=chunk.text, metadata=metadata))
            ids.append(chunk.chunk_id)
            seen_hashes.add(chunk.content_hash)
        return docs, ids


def _metadata_for_model(metadata: dict[str, Any]) -> dict[str, Any]:
    allowed = set(DocumentMetadata.model_fields)
    return {key: value for key, value in metadata.items() if key in allowed}


def _matches_filter(metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
    for key, expected in filters.items():
        if expected in (None, "", []):
            continue
        actual = metadata.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif str(actual).lower() != str(expected).lower():
            return False
    return True


def _distance_to_similarity(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 / (1.0 + max(distance, 0.0))))


def _citation(metadata: DocumentMetadata) -> str:
    source = metadata.source_url or metadata.source_path or metadata.title or "unknown source"
    page = f", page {metadata.page_number}" if metadata.page_number else ""
    return f"{metadata.title or metadata.document_type}: {source}{page}"


def get_faiss_store() -> RealFaissStore:
    global _store
    if _store is None:
        _store = RealFaissStore()
    return _store


def build_and_save_faiss_store(chunks: list[DocumentChunk]) -> RealFaissStore:
    store = get_faiss_store()
    store.rebuild(chunks)
    return store

def deactivate_document_chunks(document_id: str) -> int:
    """Marks chunks of a document as inactive due to supersession."""
    store = get_faiss_store()
    count = 0
    for chunk_id, metadata in store.manifest.items():
        if metadata.get("document_id") == document_id and metadata.get("is_latest") is True:
            metadata["is_latest"] = False
            metadata["is_active"] = False
            count += 1
    if count > 0:
        store._save_manifest()
    return count


def add_documents_to_store(chunks: list[DocumentChunk]) -> dict[str, int]:
    return get_faiss_store().add_chunks(chunks)
