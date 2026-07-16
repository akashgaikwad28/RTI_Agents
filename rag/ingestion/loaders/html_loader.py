"""HTML extraction and cleanup loader."""

from __future__ import annotations

import asyncio

from bs4 import BeautifulSoup, NavigableString

try:
    import trafilatura
except ImportError:  # Fix H1: catch ImportError only, not all exceptions
    trafilatura = None

from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.ingestion.cleaners.text_cleaner import clean_text
from rag.types import LoadedDocument


REMOVE_SELECTORS = ["script", "style", "noscript", "nav", "header", "footer", "form", "aside"]


def extract_title(soup: BeautifulSoup) -> str:
    """Extract page title from a pre-parsed BeautifulSoup object."""
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    return h1.get_text(" ", strip=True) if h1 else ""


def _html_table_to_markdown(table) -> str:
    """Convert a BeautifulSoup <table> element into a Markdown table string."""
    markdown_rows: list[str] = []
    separator_inserted = False
    first_row_cols = 0

    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        row_data = [c.get_text(" ", strip=True).replace("|", "\\|") for c in cells]
        markdown_rows.append("| " + " | ".join(row_data) + " |")

        # Insert separator after the first row (whether th or td)
        if not separator_inserted:
            first_row_cols = len(row_data)
            markdown_rows.append("|" + "|".join(["---"] * first_row_cols) + "|")
            separator_inserted = True

    return "\n".join(markdown_rows)


def extract_text_from_html(html: str) -> str:
    # Fix H5: parse once and reuse the soup object for both title and body extraction
    soup = BeautifulSoup(html, "html.parser")

    if trafilatura is not None:
        extracted = trafilatura.extract(html, include_tables=True, favor_recall=True)
        if extracted:
            return clean_text(extracted)

    for selector in REMOVE_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()

    main = soup.find("main") or soup.find("article") or soup.body or soup
    if not main:
        return ""

    # Fix H4: Replace headers using replace_with() instead of clear()+append()
    for i in range(1, 7):
        for header in main.find_all(f"h{i}"):
            text = header.get_text(" ", strip=True)
            header.replace_with(NavigableString(f"\n\n{'#' * i} {text}\n\n"))

    # Fix H3: Replace tables using replace_with() so get_text() picks up the content
    for table in main.find_all("table"):
        md = _html_table_to_markdown(table)
        if md:
            table.replace_with(NavigableString(f"\n\n{md}\n\n"))

    return clean_text(main.get_text("\n", strip=True))


def _parse_and_extract(html: str) -> tuple[str, str]:
    """CPU-bound parse: returns (title, body_text). Runs in a thread."""
    soup = BeautifulSoup(html, "html.parser")
    title = extract_title(soup)
    body = extract_text_from_html(html)
    return title, body


async def load_html(html: str, *, source_url: str = "", department: str = "", document_type: str = "html") -> LoadedDocument:
    # Fix H2: wrap CPU-bound BeautifulSoup/trafilatura work in asyncio.to_thread
    title, text = await asyncio.to_thread(_parse_and_extract, html)
    metadata = build_metadata(
        text=text,
        source_url=source_url,
        department=department,
        document_type=document_type,
        title=title,
        mime_type="text/html",
    )
    return LoadedDocument(text=text, metadata=metadata)
