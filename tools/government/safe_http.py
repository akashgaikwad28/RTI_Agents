"""Safe HTTP utilities for official government retrieval tools."""

from __future__ import annotations

import asyncio
import ipaddress
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup


ALLOWED_SUFFIXES = (".gov.in", ".nic.in")
ALLOWED_HOSTS = {"data.gov.in", "egazette.nic.in", "indiacode.nic.in", "pib.gov.in"}


def is_allowed_government_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        return False
    host = parsed.hostname or ""
    try:
        ip = ipaddress.ip_address(host)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
    except ValueError:
        pass
    host = host.lower()
    return host in ALLOWED_HOSTS or any(host.endswith(suffix) for suffix in ALLOWED_SUFFIXES) or "municipal" in host


@dataclass
class SafePage:
    url: str
    title: str
    text: str
    links: list[str]
    status: int


class SafeGovernmentHttpClient:
    def __init__(self, timeout_seconds: int = 15):
        self.timeout_seconds = timeout_seconds
        self._robots_cache: dict[str, RobotFileParser] = {}
        self._lock = asyncio.Lock()

    async def fetch_text(self, url: str, *, max_chars: int = 5000, respect_robots: bool = True) -> SafePage:
        if not is_allowed_government_url(url):
            raise ValueError("URL is not an allowlisted government endpoint")
        if respect_robots and not await self._robots_allowed(url):
            raise ValueError("robots.txt disallows this fetch")
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        headers = {"User-Agent": "RTI-Agent-v2-Government-Research/1.0 (+read-only)"}
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as response:
                response.raise_for_status()
                body = await response.text(errors="ignore")
                final_url = str(response.url)
        soup = BeautifulSoup(body, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else final_url
        text = " ".join(soup.get_text(" ", strip=True).split())[:max_chars]
        links = []
        for link in soup.find_all("a", href=True):
            href = urljoin(final_url, link["href"])
            if is_allowed_government_url(href):
                links.append(href)
        return SafePage(url=final_url, title=title, text=text, links=links[:50], status=200)

    async def _robots_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        async with self._lock:
            parser = self._robots_cache.get(root)
            if parser is None:
                parser = RobotFileParser()
                parser.set_url(urljoin(root, "/robots.txt"))
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        async with session.get(parser.url) as response:
                            if response.status >= 400:
                                self._robots_cache[root] = parser
                                return True
                            parser.parse((await response.text()).splitlines())
                except Exception:
                    return True
                self._robots_cache[root] = parser
        return parser.can_fetch("RTI-Agent-v2-Government-Research/1.0", url)
