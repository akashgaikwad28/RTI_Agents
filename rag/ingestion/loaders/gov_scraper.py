"""Config-driven async government website scraper."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config.settings import settings
from observability.metrics import scrape_failures_total
from observability.structured_logger import get_logger
from rag.ingestion.loaders.html_loader import load_html
from rag.ingestion.loaders.pdf_loader import load_pdf
from rag.types import LoadedDocument, ScrapeResult, ScrapeTarget

logger = get_logger(__name__)

DEFAULT_CONFIG = Path("config/gov_sources.json")
RAW_DIR = Path("rag/ingestion/corpus/raw")
FAILED_DIR = Path("rag/ingestion/corpus/failed")


@dataclass
class AsyncRateLimiter:
    rate_per_second: float
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _last_call: float = 0.0

    async def wait(self) -> None:
        if self.rate_per_second <= 0:
            return
        interval = 1.0 / self.rate_per_second
        async with self._lock:
            elapsed = time.monotonic() - self._last_call
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)
            self._last_call = time.monotonic()


class GovernmentScraper:
    def __init__(
        self,
        *,
        config_path: str | Path = DEFAULT_CONFIG,
        raw_dir: str | Path = RAW_DIR,
        user_agent: str = "RTI-Agent-RAG/2.0 (+https://github.com/akashgaikwad28)",
        session_factory: Callable[..., aiohttp.ClientSession] = aiohttp.ClientSession,
    ):
        self.config_path = Path(config_path)
        self.raw_dir = Path(raw_dir)
        self.failed_dir = FAILED_DIR
        self.user_agent = user_agent
        self.session_factory = session_factory
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)
        self._robots: dict[str, RobotFileParser] = {}
        self._seen_hashes: set[str] = set()

    def load_targets(self, names: list[str] | None = None) -> list[ScrapeTarget]:
        config = json.loads(self.config_path.read_text(encoding="utf-8"))
        targets = [ScrapeTarget.model_validate(item) for item in config.get("targets", [])]
        if names:
            wanted = {name.lower() for name in names}
            targets = [target for target in targets if target.name.lower() in wanted]
        return [target for target in targets if target.enabled]

    async def scrape_targets(
        self,
        targets: list[ScrapeTarget] | None = None,
        *,
        names: list[str] | None = None,
        max_depth: int | None = None,
    ) -> list[ScrapeResult]:
        selected = targets or self.load_targets(names)
        timeout = aiohttp.ClientTimeout(total=60)
        headers = {"User-Agent": self.user_agent}
        async with self.session_factory(timeout=timeout, headers=headers) as session:
            tasks = [self.scrape_target(session, target, max_depth=max_depth) for target in selected]
            return await asyncio.gather(*tasks)

    async def scrape_target(
        self,
        session: aiohttp.ClientSession,
        target: ScrapeTarget,
        *,
        max_depth: int | None = None,
    ) -> ScrapeResult:
        result = ScrapeResult(target=target.name)
        limiter = AsyncRateLimiter(target.rate_limit_per_second)
        depth_limit = min(max_depth if max_depth is not None else target.max_depth, getattr(settings, "MAX_SCRAPE_DEPTH", target.max_depth))
        queue: asyncio.Queue[tuple[str, int]] = asyncio.Queue()
        base = str(target.base_url).rstrip("/")
        for path in target.start_paths:
            await queue.put((urljoin(base + "/", path.lstrip("/")), 0))

        visited: set[str] = set()
        while not queue.empty():
            url, depth = await queue.get()
            normalized = _normalize_url(url)
            if normalized in visited or depth > depth_limit:
                continue
            visited.add(normalized)
            result.pages_seen += 1

            if not self._allowed_domain(normalized, target) or not await self._robots_allowed(session, normalized):
                continue

            try:
                await limiter.wait()
                content, content_type = await self._fetch(session, normalized)
                if _is_pdf_url(normalized, content_type):
                    docs = await self._save_and_load_pdf(content, normalized, target)
                    result.pdfs_saved += 1 if docs else 0
                    result.documents.extend(docs)
                    continue

                html = content.decode(_guess_encoding(content_type), errors="replace")
                page_hash = _hash(html)
                if page_hash in self._seen_hashes:
                    result.duplicates += 1
                    continue
                self._seen_hashes.add(page_hash)
                self._save_raw(normalized, html.encode("utf-8"), suffix=".html")
                document = await load_html(html, source_url=normalized, department=target.department)
                if document.text:
                    result.documents.append(document)
                    result.pages_saved += 1

                if depth < depth_limit:
                    for link in self._discover_links(html, normalized, target):
                        await queue.put((link, depth + 1))
            except Exception as exc:
                scrape_failures_total.labels(target=target.name).inc()
                failure = f"{normalized}: {exc}"
                result.failures.append(failure)
                self._save_failed(normalized, str(exc))
                logger.warning(f"[GovernmentScraper] {failure}")

        return result

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
    )
    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> tuple[bytes, str]:
        async with session.get(url, allow_redirects=True) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            max_pdf_bytes = getattr(settings, "MAX_PDF_SIZE_MB", 25) * 1024 * 1024
            content_length = int(response.headers.get("content-length") or 0)
            if _is_pdf_url(url, content_type) and content_length > max_pdf_bytes:
                raise ValueError(f"PDF exceeds MAX_PDF_SIZE_MB: {content_length}")
            data = await response.read()
            if _is_pdf_url(url, content_type) and len(data) > max_pdf_bytes:
                raise ValueError(f"PDF exceeds MAX_PDF_SIZE_MB after download: {len(data)}")
            return data, content_type

    async def _robots_allowed(self, session: aiohttp.ClientSession, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain not in self._robots:
            robots_url = f"{parsed.scheme}://{domain}/robots.txt"
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                content, _content_type = await self._fetch(session, robots_url)
                parser.parse(content.decode("utf-8", errors="ignore").splitlines())
            except Exception:
                parser.parse([])
            self._robots[domain] = parser
        return self._robots[domain].can_fetch(self.user_agent, url)

    def _discover_links(self, html: str, base_url: str, target: ScrapeTarget) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "").strip()
            if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            candidate = _normalize_url(urljoin(base_url, href))
            if self._allowed_domain(candidate, target):
                links.append(candidate)
        return list(dict.fromkeys(links))

    def _allowed_domain(self, url: str, target: ScrapeTarget) -> bool:
        domain = urlparse(url).netloc.lower()
        allowed = target.allowed_domains or [urlparse(str(target.base_url)).netloc.lower()]
        return any(domain == item.lower() or domain.endswith("." + item.lower()) for item in allowed)

    async def _save_and_load_pdf(self, content: bytes, url: str, target: ScrapeTarget) -> list[LoadedDocument]:
        pdf_hash = _hash_bytes(content)
        if pdf_hash in self._seen_hashes:
            return []
        self._seen_hashes.add(pdf_hash)
        path = self._save_raw(url, content, suffix=".pdf")
        return await load_pdf(path, source_url=url, department=target.department, title=Path(urlparse(url).path).stem)

    def _save_raw(self, url: str, content: bytes, *, suffix: str) -> Path:
        parsed = urlparse(url)
        safe_domain = parsed.netloc.replace(":", "_")
        digest = _hash(url)[:16]
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        directory = self.raw_dir / safe_domain / day
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{digest}{suffix}"
        path.write_bytes(content)
        meta = {
            "url": url,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "bytes": len(content),
            "content_hash": _hash_bytes(content),
        }
        path.with_suffix(path.suffix + ".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return path

    def _save_failed(self, url: str, reason: str) -> None:
        payload = {"url": url, "reason": reason, "failed_at": datetime.now(timezone.utc).isoformat()}
        path = self.failed_dir / f"{_hash(url)[:16]}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _is_pdf_url(url: str, content_type: str = "") -> bool:
    return urlparse(url).path.lower().endswith(".pdf") or "application/pdf" in content_type.lower()


def _guess_encoding(content_type: str) -> str:
    if "charset=" in content_type:
        return content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
    return "utf-8"

