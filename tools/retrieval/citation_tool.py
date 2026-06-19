from __future__ import annotations

from pydantic import BaseModel

from tools.base.base_tool import BaseTool


class CitationInput(BaseModel):
    results: list[dict]


class CitationTool(BaseTool):
    name = "citation_builder"
    description = "Build normalized citations from retrieval metadata."
    category = "retrieval"
    permissions = ["read:rag"]
    capabilities = ["citation"]
    input_schema = CitationInput

    async def execute(self, results: list[dict]):
        citations = []
        for item in results:
            metadata = item.get("metadata", {})
            source = metadata.get("source_url") or metadata.get("source_path") or item.get("citation") or "unknown"
            page = f", page {metadata.get('page_number')}" if metadata.get("page_number") else ""
            citations.append({"citation": f"{metadata.get('title') or metadata.get('document_type') or 'Source'}: {source}{page}", "score": item.get("score", 0)})
        return {"citations": citations}

