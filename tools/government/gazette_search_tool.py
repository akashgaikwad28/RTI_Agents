from __future__ import annotations

from urllib.parse import quote_plus

from pydantic import BaseModel, Field

from tools.base.base_tool import BaseTool


class GazetteSearchInput(BaseModel):
    query: str = Field(..., min_length=2)
    year: int | None = Field(default=None, ge=1950, le=2100)
    department: str = ""


class GazetteSearchTool(BaseTool):
    name = "gazette_search"
    description = "Searches official gazette and notification discovery endpoints and returns citation targets."
    category = "government"
    permissions = ["read:public", "network:gov"]
    capabilities = ["gazette_search", "policy_search", "citation_discovery"]
    input_schema = GazetteSearchInput

    async def execute(self, query: str, year: int | None = None, department: str = ""):
        q = quote_plus(" ".join(part for part in [query, department, str(year or "")] if part))
        return {
            "query": query,
            "results": [
                {"title": "eGazette of India", "url": f"https://egazette.nic.in/SearchGazette.aspx?keyword={q}", "citation": "eGazette of India, NIC"},
                {"title": "India Code notifications", "url": f"https://www.indiacode.nic.in/search?q={q}", "citation": "India Code, Legislative Department"},
            ],
            "confidence": 0.74,
        }
