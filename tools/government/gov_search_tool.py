from __future__ import annotations

from urllib.parse import urlparse

import aiohttp
from pydantic import BaseModel, Field

from rag.ingestion.loaders.html_loader import extract_text_from_html
from tools.base.base_tool import BaseTool


class GovSearchInput(BaseModel):
    url: str = Field(..., min_length=8)
    max_chars: int = Field(2000, ge=200, le=10000)


class GovernmentSearchTool(BaseTool):
    name = "government_live_fetch"
    description = "Safe read-only fetch for allowlisted government URLs."
    category = "government"
    permissions = ["read:public", "network:gov"]
    capabilities = ["government_search", "live_fetch"]
    timeout_seconds = 15
    input_schema = GovSearchInput

    async def execute(self, url: str, max_chars: int = 2000):
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if not (domain.endswith(".gov.in") or domain.endswith(".nic.in") or "municipal" in domain):
            raise ValueError("Live fetch is restricted to official government/municipal domains")
        async with aiohttp.ClientSession(headers={"User-Agent": "RTI-Agent-Governance/3.0"}) as session:
            async with session.get(url, timeout=self.timeout_seconds) as response:
                response.raise_for_status()
                html = await response.text()
        text = extract_text_from_html(html)
        return {"url": url, "text": text[:max_chars], "freshness_score": 1.0}

