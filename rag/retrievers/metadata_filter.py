"""Metadata filtering and query-intent helpers for RAG retrieval."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from rag.ingestion.cleaners.metadata_cleaner import normalize_department
from rag.types import RetrievalResult

RTI_KEYWORDS = {
    "rti",
    "information",
    "pio",
    "public information officer",
    "appeal",
    "beneficiary",
    "budget",
    "tender",
    "circular",
    "scheme",
    "subsidy",
}

# Devanagari keyword mappings for Marathi and Hindi queries (fixes cross-language department inference)
_DEVANAGARI_DEPT_MAP: list[tuple[list[str], str]] = [
    (["शेतकरी", "कृषि", "पीएम किसान", "पिक"], "Ministry of Agriculture & Farmers Welfare"),
    (["शिक्षण", "शाळा", "महाविद्यालय", "विद्यार्थी"], "Ministry of Education"),
    (["आरोग्य", "रुग्णालय", "औषध", "डॉक्टर"], "Ministry of Health and Family Welfare"),
    (["रस्ते", "महामार्ग", "वाहतूक", "वाहन"], "Ministry of Road Transport and Highways"),
    (["महानगरपालिका", "पुणे", "पाणी", "कचरा", "मालमत्ता कर"], "Municipal Corporation"),
    # Hindi
    (["किसान", "कृषि", "फसल", "खेती"], "Ministry of Agriculture & Farmers Welfare"),
    (["स्वास्थ्य", "अस्पताल", "दवाई"], "Ministry of Health and Family Welfare"),
    (["शिक्षा", "विद्यालय", "छात्र"], "Ministry of Education"),
    (["सड़क", "राजमार्ग", "वाहन"], "Ministry of Road Transport and Highways"),
    (["नगरपालिका", "पानी", "कचरा"], "Municipal Corporation"),
]


def build_filters(department: str = "", language: str = "", document_type: str = "") -> dict[str, Any]:
    filters: dict[str, Any] = {}
    if department:
        filters["department"] = normalize_department(department)
    if language:
        filters["language"] = language
    if document_type:
        filters["document_type"] = document_type
    return filters


def infer_department(query: str, department: str = "") -> str:
    if department:
        return normalize_department(department)
    lowered = query.lower()

    # First check Devanagari keywords (Marathi/Hindi queries)
    for keywords, dept in _DEVANAGARI_DEPT_MAP:
        if any(kw in query for kw in keywords):
            return dept

    # English keyword matching
    if any(word in lowered for word in ["farmer", "agriculture", "pm kisan", "subsidy", "crop", "kisan"]):
        return "Ministry of Agriculture & Farmers Welfare"
    if any(word in lowered for word in ["road", "transport", "highway", "vehicle"]):
        return "Ministry of Road Transport and Highways"
    if any(word in lowered for word in ["school", "college", "education", "teacher", "student"]):
        return "Ministry of Education"
    if any(word in lowered for word in ["hospital", "health", "medicine", "doctor"]):
        return "Ministry of Health and Family Welfare"
    if any(word in lowered for word in ["municipal", "pune", "corporation", "water supply", "garbage", "property tax"]):
        return "Municipal Corporation"
    return ""


def intent_keywords(query: str) -> set[str]:
    # Latin-script tokens only — used for English keyword overlap scoring
    tokens = {token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", query)}
    return tokens | {keyword for keyword in RTI_KEYWORDS if keyword in query.lower()}


def apply_recency_boost(result: RetrievalResult, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    stamp = result.metadata.scraped_at or result.metadata.created_at
    if not stamp:
        return 0.0
    try:
        created = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except Exception:
        return 0.0
    age_days = max((now - created).days, 0)
    if age_days <= 90:
        return 0.08
    if age_days <= 365:
        return 0.04
    return 0.0


def keyword_overlap_score(query: str, text: str) -> float:
    query_terms = intent_keywords(query)
    if not query_terms:
        return 0.0
    lowered = text.lower()
    hits = sum(1 for term in query_terms if term in lowered)
    return min(0.12, hits / max(len(query_terms), 1) * 0.12)
