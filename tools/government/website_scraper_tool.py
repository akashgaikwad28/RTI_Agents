from __future__ import annotations

from pydantic import BaseModel, Field

from tools.base.base_tool import BaseTool
from tools.government.safe_http import SafeGovernmentHttpClient


class WebsiteScraperInput(BaseModel):
    url: str = Field(..., min_length=8)
    max_chars: int = Field(default=5000, ge=500, le=20000)
    respect_robots: bool = True


class WebsiteScraperTool(BaseTool):
    name = "website_scraper"
    description = "Read-only scraper for allowlisted official government pages with robots.txt support."
    category = "government"
    permissions = ["read:public", "network:gov"]
    capabilities = ["scraping", "government_search", "live_fetch"]
    input_schema = WebsiteScraperInput
    timeout_seconds = 20

    async def execute(self, url: str, max_chars: int = 5000, respect_robots: bool = True):
        page = await SafeGovernmentHttpClient(timeout_seconds=self.timeout_seconds).fetch_text(
            url,
            max_chars=max_chars,
            respect_robots=respect_robots,
        )
        return {"url": page.url, "title": page.title, "text": page.text, "links": page.links, "source_type": "official_website"}
