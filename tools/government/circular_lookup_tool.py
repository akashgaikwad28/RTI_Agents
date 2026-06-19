from __future__ import annotations

from tools.retrieval.hybrid_search_tool import HybridSearchInput, HybridSearchTool


class CircularLookupTool(HybridSearchTool):
    name = "circular_lookup"
    description = "Lookup government circulars and notifications from the RAG corpus."
    category = "government"
    permissions = ["read:rag"]
    capabilities = ["circular_lookup", "notification_lookup"]
    input_schema = HybridSearchInput

    async def execute(self, query: str, department: str = "", language: str = "", k: int = 5):
        return await super().execute(f"circular notification order {query}", department=department, language=language, k=k)

