"""MongoDB Atlas Vector Search backend with dynamic local calculation fallback."""

from __future__ import annotations

import asyncio
import math
import time
from typing import Any

from config.settings import settings
from mcp_clients.mongo_client import get_mongo_client
from observability.structured_logger import get_logger
from rag.embeddings.embedding_router import get_embedder
from rag.types import DocumentChunk, DocumentMetadata, RetrievalResult
from rag.vectorstore.base import BaseVectorStore

logger = get_logger(__name__)

_mongo_store_instance: "MongoDBVectorStore | None" = None


class MongoDBVectorStore(BaseVectorStore):
    def __init__(self):
        self.embedder = get_embedder().get_langchain_embedder()
        self.collection_name = "vector_chunks"

    async def _get_collection(self):
        mongo = await get_mongo_client()
        return mongo.db[self.collection_name]

    def add_chunks(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        """Sync wrapper for adding chunks."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError("MongoDBVectorStore.add_chunks cannot run inside an active event loop; use aadd_chunks instead.")
        else:
            return asyncio.run(self.aadd_chunks(chunks))

    async def aadd_chunks(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        """Async implementation of adding semantic chunks to MongoDB."""
        if not chunks:
            return {"indexed": 0, "duplicates": 0}

        collection = await self._get_collection()
        texts = [chunk.text for chunk in chunks]
        
        # Embed all texts concurrently
        embeddings = await asyncio.to_thread(self.embedder.embed_documents, texts)

        operations = []
        duplicates = 0
        indexed = 0

        for chunk, embedding in zip(chunks, embeddings):
            # Check for duplicates by chunk_id or content_hash
            existing = await collection.find_one({
                "$or": [
                    {"chunk_id": chunk.chunk_id},
                    {"content_hash": chunk.content_hash}
                ]
            })
            if existing:
                duplicates += 1
                continue

            metadata = chunk.metadata.model_dump()
            metadata.update({
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "content_hash": chunk.content_hash,
                "is_active": True,
                "source": chunk.metadata.source_url or chunk.metadata.source_path,
            })

            doc = {
                "_id": chunk.chunk_id,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "embedding": embedding,
                "metadata": metadata,
                "created_at": time.time(),
            }
            operations.append(collection.insert_one(doc))
            indexed += 1

        if operations:
            await asyncio.gather(*operations)

        logger.info(f"[MongoDBStore] Ingested {indexed} chunks, skipped {duplicates} duplicates.")
        return {"indexed": indexed, "duplicates": duplicates}

    def rebuild(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        """Sync wrapper for rebuilding index."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError("MongoDBVectorStore.rebuild cannot run inside an active event loop; use arebuild instead.")
        else:
            return asyncio.run(self.arebuild(chunks))

    async def arebuild(self, chunks: list[DocumentChunk]) -> dict[str, int]:
        """Completely rebuilds the MongoDB vector store collection."""
        collection = await self._get_collection()
        # Drop existing chunks for rebuilding
        await collection.delete_many({})
        logger.info("[MongoDBStore] Cleared vector collection for complete rebuild.")
        return await self.aadd_chunks(chunks)

    def similarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None
    ) -> list[tuple[RetrievalResult, float]]:
        """Sync wrapper for similarity search."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError(
                "MongoDBVectorStore.similarity_search_with_score cannot run inside an active event loop; "
                "use asimilarity_search_with_score instead."
            )
        else:
            return asyncio.run(self.asimilarity_search_with_score(query, k=k, filters=filters))

    async def asimilarity_search_with_score(
        self,
        query: str,
        *,
        k: int = 5,
        filters: dict[str, Any] | None = None
    ) -> list[tuple[RetrievalResult, float]]:
        """Async similarity search utilizing MongoDB `$vectorSearch` with high-performance python fallback."""
        collection = await self._get_collection()
        
        # Embed the search query
        query_embedding = await asyncio.to_thread(self.embedder.embed_query, query)

        # Standard MongoDB filter preparation
        mongo_filter: dict[str, Any] = {"metadata.is_active": True}
        if filters:
            for key, val in filters.items():
                if val not in (None, "", []):
                    if isinstance(val, list):
                        mongo_filter[f"metadata.{key}"] = {"$in": val}
                    else:
                        mongo_filter[f"metadata.{key}"] = val

        try:
            # 1. Primary path: Attempt Cloud MongoDB Atlas `$vectorSearch` aggregation
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": max(k * 10, 100),
                        "limit": k,
                        "filter": mongo_filter
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "chunk_id": 1,
                        "text": 1,
                        "metadata": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=k)
            
            # Map Atlas Search results
            filtered = []
            for doc in results:
                metadata = DocumentMetadata.model_validate(_metadata_for_model(doc.get("metadata", {})))
                score = float(doc.get("score", 0.0))
                # Map similarity score (cosine score returns 0 to 1 directly in Atlas)
                filtered.append(
                    (
                        RetrievalResult(
                            text=doc.get("text", ""),
                            score=score,
                            metadata=metadata,
                            source="mongodb_vector",
                            citation=_citation(metadata),
                        ),
                        1.0 - score  # Distance representation
                    )
                )
            logger.info(f"[MongoDBStore] Vector search query completed via Cloud Atlas Vector Search. Found: {len(filtered)}")
            return filtered

        except Exception as exc:
            # 2. Fallback path: local cosine similarity calculation if `$vectorSearch` index is not configured (e.g. offline testing)
            logger.warning(
                f"[MongoDBStore] Cloud search index missing or failed: {exc}. "
                "Executing local cosine similarity fallback calculations..."
            )
            
            # Retrieve active documents matching criteria
            cursor = collection.find(mongo_filter)
            documents = await cursor.to_list(length=1000) # Cap for performance
            
            # Offload CPU-heavy cosine calculation to separate thread to prevent event loop blocking
            scored_docs = await asyncio.to_thread(
                _calculate_similarities, query_embedding, documents
            )
                
            # Sort by descending score
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            top_k = scored_docs[:k]
            
            filtered = []
            for doc, score in top_k:
                metadata = DocumentMetadata.model_validate(_metadata_for_model(doc.get("metadata", {})))
                filtered.append(
                    (
                        RetrievalResult(
                            text=doc.get("text", ""),
                            score=score,
                            metadata=metadata,
                            source="mongodb_vector_fallback",
                            citation=_citation(metadata),
                        ),
                        1.0 - score
                    )
                )
            logger.info(f"[MongoDBStore] Vector search query completed via Python Cosine Fallback. Found: {len(filtered)}")
            return filtered

    def stats(self) -> dict[str, Any]:
        """Sync stats wrapper."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError("MongoDBVectorStore.stats cannot run inside an active event loop; use astats instead.")
        else:
            return asyncio.run(self.astats())

    async def astats(self) -> dict[str, Any]:
        """Returns statistics for the MongoDB vector collection."""
        collection = await self._get_collection()
        total_chunks = await collection.count_documents({})
        active_chunks = await collection.count_documents({"metadata.is_active": True})
        
        # Aggregate unique fields
        departments = await collection.distinct("metadata.department")
        languages = await collection.distinct("metadata.language")
        
        return {
            "type": "mongodb_vector",
            "loaded": True,
            "chunks": total_chunks,
            "total_chunks": total_chunks,
            "active_chunks": active_chunks,
            "departments": sorted([d for d in departments if d]),
            "languages": sorted([l for l in languages if l]),
        }

    async def document_history(self, document_id: str) -> list[dict[str, Any]]:
        """Return known metadata versions for a document from MongoDB chunks."""
        collection = await self._get_collection()
        cursor = collection.find(
            {
                "$or": [
                    {"metadata.document_id": document_id},
                    {"metadata.source_hash": {"$regex": f"^{document_id}"}},
                ]
            },
            {"_id": 0, "metadata": 1},
        )
        documents = await cursor.to_list(length=1000)

        versions: dict[int, dict[str, Any]] = {}
        for document in documents:
            metadata = dict(document.get("metadata") or {})
            version = int(metadata.get("version") or 1)
            versions.setdefault(version, metadata)
        return [versions[key] for key in sorted(versions, reverse=True)]

    async def document_version(self, document_id: str, version: int) -> dict[str, Any] | None:
        """Return representative content and metadata for a document version."""
        collection = await self._get_collection()
        cursor = collection.find(
            {
                "$and": [
                    {
                        "$or": [
                            {"metadata.document_id": document_id},
                            {"metadata.source_hash": {"$regex": f"^{document_id}"}},
                        ]
                    },
                    {"metadata.version": version},
                ]
            },
            {"_id": 0, "text": 1, "metadata": 1},
        ).sort("metadata.chunk_index", 1)
        chunks = await cursor.to_list(length=1000)
        if not chunks and version == 1:
            cursor = collection.find(
                {
                    "$or": [
                        {"metadata.document_id": document_id},
                        {"metadata.source_hash": {"$regex": f"^{document_id}"}},
                    ]
                },
                {"_id": 0, "text": 1, "metadata": 1},
            ).sort("metadata.chunk_index", 1)
            chunks = await cursor.to_list(length=1000)
        if not chunks:
            return None

        metadata = dict(chunks[0].get("metadata") or {})
        content = "\n\n".join(chunk.get("text", "") for chunk in chunks if chunk.get("text"))
        return {"metadata": metadata, "content": content}


def _metadata_for_model(metadata: dict[str, Any]) -> dict[str, Any]:
    allowed = set(DocumentMetadata.model_fields)
    return {key: value for key, value in metadata.items() if key in allowed}


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(b * b for b in v2))
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0.0
    return dot_product / (magnitude_v1 * magnitude_v2)


def _calculate_similarities(query_embedding: list[float], documents: list[dict[str, Any]]) -> list[tuple[dict[str, Any], float]]:
    scored_docs = []
    for doc in documents:
        doc_embedding = doc.get("embedding")
        if not doc_embedding:
            continue
        score = _cosine_similarity(query_embedding, doc_embedding)
        scored_docs.append((doc, score))
    return scored_docs


def _citation(metadata: DocumentMetadata) -> str:
    source = metadata.source_url or metadata.source_path or metadata.title or "unknown source"
    page = f", page {metadata.page_number}" if metadata.page_number else ""
    return f"{metadata.title or metadata.document_type}: {source}{page}"


def get_mongo_store() -> MongoDBVectorStore:
    """Returns the MongoDBVectorStore singleton instance."""
    global _mongo_store_instance
    if _mongo_store_instance is None:
        _mongo_store_instance = MongoDBVectorStore()
    return _mongo_store_instance
