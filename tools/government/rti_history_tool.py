from __future__ import annotations

from pydantic import BaseModel, Field

from rag.retriever import retrieve_rag_results
from tools.base.base_tool import BaseTool


class RTIHistoryInput(BaseModel):
    query: str = Field(..., min_length=2)
    department: str = ""
    k: int = Field(default=5, ge=1, le=10)


class RTIHistoryTool(BaseTool):
    name = "rti_history"
    description = "Searches historical RTI corpus for similar applications and outcomes."
    category = "government"
    permissions = ["read:rag"]
    capabilities = ["rti_history", "similar_cases", "retrieval"]
    input_schema = RTIHistoryInput

    async def execute(self, query: str, department: str = "", k: int = 5):
        results, cache_hit, confidence = await retrieve_rag_results(query, department=department, k=k)
        return {
            "query": query,
            "cache_hit": cache_hit,
            "confidence": confidence,
            "results": [
                {
                    "text": result.text,
                    "score": result.score,
                    "citation": result.citation,
                    "source_url": result.metadata.source_url,
                    "department": result.metadata.department,
                }
                for result in results
            ],
        }
