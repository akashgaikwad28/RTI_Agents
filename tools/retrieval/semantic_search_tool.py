from __future__ import annotations

from tools.retrieval.hybrid_search_tool import HybridSearchInput, HybridSearchTool


class SemanticSearchTool(HybridSearchTool):
    name = "semantic_search"
    description = "Semantic FAISS retrieval over government document chunks."
    capabilities = ["semantic_search"]
    input_schema = HybridSearchInput

