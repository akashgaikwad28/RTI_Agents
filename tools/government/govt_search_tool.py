from __future__ import annotations

from urllib.parse import quote_plus

from pydantic import BaseModel, Field

from tools.base.base_tool import BaseTool


class GovernmentWebsiteSearchInput(BaseModel):
    query: str = Field(..., min_length=2)
    department: str = ""
    language: str = "en"
    limit: int = Field(default=5, ge=1, le=10)


class GovernmentWebsiteSearchTool(BaseTool):
    name = "government_website_search"
    description = "Builds official-domain search targets for Indian government information retrieval."
    category = "government"
    permissions = ["read:public", "network:gov"]
    capabilities = ["government_search", "tool_discovery", "official_domain_search"]
    input_schema = GovernmentWebsiteSearchInput
    timeout_seconds = 10

    async def execute(self, query: str, department: str = "", language: str = "en", limit: int = 5):
        from multilingual.transliteration.query_expansion import QueryExpansion

        expanded = " ".join(QueryExpansion().expand(query, language)[:2])
        q = quote_plus(f"{expanded} {department}".strip())
        targets = [
            {"title": "India.gov.in search", "url": f"https://www.india.gov.in/search/site/{q}", "domain": "india.gov.in"},
            {"title": "Data.gov.in search", "url": f"https://data.gov.in/search?title={q}", "domain": "data.gov.in"},
            {"title": "PIB search", "url": f"https://pib.gov.in/SearchResult.aspx?Search={q}", "domain": "pib.gov.in"},
            {"title": "eGazette search", "url": f"https://egazette.nic.in/SearchGazette.aspx?keyword={q}", "domain": "egazette.nic.in"},
            {"title": "India Code search", "url": f"https://www.indiacode.nic.in/search?q={q}", "domain": "indiacode.nic.in"},
        ]
        return {"query": query, "department": department, "language": language, "expanded_query": expanded, "results": targets[:limit], "confidence": 0.72}
