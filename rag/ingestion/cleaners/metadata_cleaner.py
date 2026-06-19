"""Metadata normalization for government RAG sources."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from rag.ingestion.cleaners.text_cleaner import detect_language
from rag.types import DocumentMetadata

DEPARTMENT_ALIASES = {
    "agriculture": "Ministry of Agriculture & Farmers Welfare",
    "pm kisan": "Ministry of Agriculture & Farmers Welfare",
    "education": "Ministry of Education",
    "health": "Ministry of Health and Family Welfare",
    "mohfw": "Ministry of Health and Family Welfare",
    "road": "Ministry of Road Transport and Highways",
    "transport": "Ministry of Road Transport and Highways",
    "morth": "Ministry of Road Transport and Highways",
    "municipal": "Municipal Corporation",
    "pune": "Municipal Corporation",
}


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def normalize_department(value: str, fallback: str = "") -> str:
    raw = (value or fallback or "").strip()
    lowered = raw.lower()
    for key, canonical in DEPARTMENT_ALIASES.items():
        if key in lowered:
            return canonical
    return raw or "General"


def infer_document_type(title: str = "", url: str = "", path: str = "") -> str:
    haystack = " ".join([title, url, path]).lower()
    keywords = {
        "rti_act": ["rti act", "right to information"],
        "tender": ["tender", "bid", "eoi"],
        "circular": ["circular", "office memorandum", "notification"],
        "scheme": ["scheme", "yojana", "pm-kisan", "subsidy"],
        "budget_report": ["budget", "annual report", "report"],
        "faq": ["faq", "frequently asked"],
    }
    for doc_type, markers in keywords.items():
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
    return DocumentMetadata(
        source_url=source_url,
        source_path=source_path,
        source_hash=content_hash("|".join([source_url, source_path, text[:5000]])),
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

