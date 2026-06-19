from __future__ import annotations

from tools.retrieval.hybrid_search_tool import HybridSearchInput, HybridSearchTool


class RTIGuidelineTool(HybridSearchTool):
    name = "rti_guideline"
    description = "Retrieve RTI Act, PIO, fee, appeal, and compliance guidelines."
    category = "government"
    permissions = ["read:rag"]
    capabilities = ["rti_guidelines", "compliance"]
    input_schema = HybridSearchInput

    async def execute(self, query: str, department: str = "", language: str = "", k: int = 5):
        return await super().execute(f"RTI Act 2005 PIO appeal fee guideline {query}", department=department, language=language, k=k)

