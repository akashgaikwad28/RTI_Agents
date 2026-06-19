from __future__ import annotations

from urllib.parse import quote_plus

from pydantic import BaseModel, Field

from tools.base.base_tool import BaseTool


class BudgetSearchInput(BaseModel):
    query: str = Field(..., min_length=2)
    department: str = ""
    financial_year: str | None = None


class BudgetSearchTool(BaseTool):
    name = "budget_search"
    description = "Discovers official budget documents and data tables for departments."
    category = "government"
    permissions = ["read:public", "network:gov"]
    capabilities = ["budget_search", "financial_data", "government_search"]
    input_schema = BudgetSearchInput

    async def execute(self, query: str, department: str = "", financial_year: str | None = None):
        q = quote_plus(" ".join(part for part in [department, query, financial_year or "", "budget"] if part))
        return {
            "query": query,
            "department": department,
            "financial_year": financial_year,
            "results": [
                {"title": "Union Budget documents", "url": f"https://www.indiabudget.gov.in/search.php?q={q}", "citation": "India Budget, Ministry of Finance"},
                {"title": "Open Government Data budget datasets", "url": f"https://data.gov.in/search?title={q}", "citation": "data.gov.in"},
            ],
            "extractors": ["pdf_table_parser", "csv_dataset_reader"],
            "confidence": 0.7,
        }
