from __future__ import annotations

from pydantic import BaseModel, Field

from rag.retriever import retrieve_rag_results
from tools.base.base_tool import BaseTool


class HybridSearchInput(BaseModel):
    query: str = Field(..., min_length=3)
    department: str = ""
    language: str = ""
    k: int = Field(5, ge=1, le=20)


class HybridSearchTool(BaseTool):
    name = "hybrid_search"
    description = "Hybrid FAISS + metadata retrieval over the Phase B RAG corpus."
    category = "retrieval"
    permissions = ["read:rag"]
    capabilities = ["semantic_search", "hybrid_retrieval", "citation_retrieval"]
    cache_ttl_seconds = 300
    input_schema = HybridSearchInput

    async def execute(self, query: str, department: str = "", language: str = "", k: int = 5):
        results, cache_hit, confidence = await retrieve_rag_results(query, department=department, language=language, k=k)
        return {
            "cache_hit": cache_hit,
            "confidence": confidence,
            "results": [
                {"text": r.text, "score": r.score, "citation": r.citation, "metadata": r.metadata.model_dump()}
                for r in results
            ],
        }

