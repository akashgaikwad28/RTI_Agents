"""HTML extraction and cleanup loader."""

from __future__ import annotations

from bs4 import BeautifulSoup

try:
    import trafilatura
except Exception:  # pragma: no cover - optional dependency
    trafilatura = None

from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.ingestion.cleaners.text_cleaner import clean_text
from rag.types import LoadedDocument


REMOVE_SELECTORS = ["script", "style", "noscript", "nav", "header", "footer", "form", "aside"]


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    return h1.get_text(" ", strip=True) if h1 else ""


def extract_text_from_html(html: str) -> str:
    if trafilatura is not None:
        extracted = trafilatura.extract(html, include_tables=True, favor_recall=True)
        if extracted:
            return clean_text(extracted)

    soup = BeautifulSoup(html, "html.parser")
    for selector in REMOVE_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return clean_text(main.get_text("\n", strip=True))


async def load_html(html: str, *, source_url: str = "", department: str = "", document_type: str = "html") -> LoadedDocument:
    title = extract_title(html)
    text = extract_text_from_html(html)
    metadata = build_metadata(
        text=text,
        source_url=source_url,
        department=department,
        document_type=document_type,
        title=title,
        mime_type="text/html",
    )
    return LoadedDocument(text=text, metadata=metadata)

