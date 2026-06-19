from __future__ import annotations

from urllib.parse import quote_plus

from pydantic import BaseModel, Field

from tools.base.base_tool import BaseTool


class MunicipalDataInput(BaseModel):
    query: str = Field(..., min_length=2)
    city: str = ""
    topic: str = ""
    language: str = "en"


class MunicipalDataTool(BaseTool):
    name = "municipal_data"
    description = "Discovers local body data for civic works, budgets, health, roads, and municipal records."
    category = "government"
    permissions = ["read:public", "network:gov"]
    capabilities = ["municipal_data", "civic_records", "budget_search"]
    input_schema = MunicipalDataInput

    async def execute(self, query: str, city: str = "", topic: str = "", language: str = "en"):
        from multilingual.transliteration.query_expansion import QueryExpansion

        expanded = " ".join(QueryExpansion().expand(query, language)[:2])
        q = quote_plus(" ".join(part for part in [city, topic, expanded] if part))
        return {
            "query": query,
            "language": language,
            "expanded_query": expanded,
            "city": city,
            "results": [
                {"title": "Municipal official-domain search", "url": f"https://www.google.com/search?q={q}+site%3A.gov.in+municipal", "citation": "Official municipal .gov.in search target"},
                {"title": "Open Government civic datasets", "url": f"https://data.gov.in/search?title={q}", "citation": "data.gov.in civic datasets"},
            ],
            "confidence": 0.66,
        }
