from __future__ import annotations

from tools.retrieval.hybrid_search_tool import HybridSearchInput, HybridSearchTool


class SchemeLookupTool(HybridSearchTool):
    name = "scheme_lookup"
    description = "Lookup scheme announcements, subsidy details, and beneficiary information."
    category = "government"
    permissions = ["read:rag"]
    capabilities = ["scheme_lookup", "beneficiary_lookup"]
    input_schema = HybridSearchInput

    async def execute(self, query: str, department: str = "", language: str = "", k: int = 5):
        return await super().execute(f"scheme yojana subsidy beneficiary {query}", department=department, language=language, k=k)

