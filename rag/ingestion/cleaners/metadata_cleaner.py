"""Metadata normalization for government RAG sources."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from rag.ingestion.cleaners.text_cleaner import detect_language
from rag.types import DocumentMetadata

# Use word-boundary-aware matching to fix M2 (e.g. "road" matching "Broad Services")
DEPARTMENT_ALIASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bagriculture\b|\bpm\s*kisan\b|\bkisan\b", re.IGNORECASE), "Ministry of Agriculture & Farmers Welfare"),
    (re.compile(r"\beducation\b|\bschool\b|\buniversity\b", re.IGNORECASE), "Ministry of Education"),
    (re.compile(r"\bhealth\b|\bmohfw\b|\bhospital\b|\bmedicine\b", re.IGNORECASE), "Ministry of Health and Family Welfare"),
    (re.compile(r"\broads?\b|\bhighway\b|\btransport\b|\bmorth\b|\bvehicle\b", re.IGNORECASE), "Ministry of Road Transport and Highways"),
    (re.compile(r"\bmunicipal\b|\bpune\b|\bcorporation\b|\bpmc\b", re.IGNORECASE), "Municipal Corporation"),
]


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def normalize_department(value: str, fallback: str = "") -> str:
    raw = (value or fallback or "").strip()
    for pattern, canonical in DEPARTMENT_ALIASES:
        if pattern.search(raw):
            return canonical
    return raw or "General"


def infer_document_type(title: str = "", url: str = "", path: str = "") -> str:
    haystack = " ".join([title, url, path]).lower()
    # Ordered from most-specific to least-specific to prevent M4 mis-classification
    keywords: list[tuple[str, list[str]]] = [
        ("rti_act", ["rti act", "right to information"]),
        ("tender", ["tender", "bid", "eoi"]),
        ("faq", ["faq", "frequently asked"]),
        ("circular", ["circular", "office memorandum", "notification"]),
        ("scheme", ["scheme", "yojana", "pm-kisan", "subsidy"]),
        ("budget_report", ["annual budget", "budget report"]),  # Tightened: avoid matching plain "report"
    ]
    for doc_type, markers in keywords:
        if any(marker in haystack for marker in markers):
            return doc_type
    if url.lower().endswith(".pdf") or path.lower().endswith(".pdf"):
        return "pdf"
    return "html" if url else "document"


def build_metadata(
    *,
    text: str,
    source_url: str = "",
    source_path: str = "",
    department: str = "",
    document_type: str = "",
    title: str = "",
    mime_type: str = "",
    page_number: int | None = None,
    extra: dict | None = None,
) -> DocumentMetadata:
    parsed = urlparse(source_url)
    file_name = Path(source_path).name if source_path else Path(parsed.path).name
    detected_language = detect_language(text)
    doc_type = document_type or infer_document_type(title=title, url=source_url, path=source_path)

    # Hash the FULL text content, not truncated at 5000 chars (fixes M1/C1 false-positive dedup)
    source_hash = content_hash("|".join([source_url, source_path, text]))

    return DocumentMetadata(
        source_url=source_url,
        source_path=source_path,
        source_hash=source_hash,
        department=normalize_department(department),
        document_type=doc_type,
        language=detected_language,
        created_at=datetime.now(timezone.utc).isoformat(),
        scraped_at=datetime.now(timezone.utc).isoformat() if source_url else None,
        title=re.sub(r"\s+", " ", title).strip(),
        domain=parsed.netloc.lower(),
        file_name=file_name,
        mime_type=mime_type,
        page_number=page_number,
        extra=extra or {},
    )
