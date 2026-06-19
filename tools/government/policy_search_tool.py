from __future__ import annotations

from tools.retrieval.hybrid_search_tool import HybridSearchInput, HybridSearchTool


class PolicySearchTool(HybridSearchTool):
    name = "policy_search"
    description = "Search policy, circular, budget, and RTI corpus documents."
    category = "government"
    permissions = ["read:rag"]
    capabilities = ["policy_search", "government_search"]
    input_schema = HybridSearchInput

