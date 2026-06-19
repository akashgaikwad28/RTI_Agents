"""Citation localization for UI and responses."""

from __future__ import annotations

from rag.types import RetrievalResult


LABELS = {
    "en": {"source": "Source", "department": "Department", "page": "Page"},
    "hi": {"source": "स्रोत", "department": "विभाग", "page": "पृष्ठ"},
    "mr": {"source": "स्रोत", "department": "विभाग", "page": "पान"},
}


class CitationLocalizer:
    def localize(self, result: RetrievalResult, language: str = "en") -> str:
        labels = LABELS.get(language, LABELS["en"])
        base = result.citation or result.metadata.source_url or result.metadata.source_path or "Unknown source"
        department = result.metadata.department
        page = f", {labels['page']} {result.metadata.page_number}" if result.metadata.page_number else ""
        dept = f", {labels['department']}: {department}" if department else ""
        return f"{labels['source']}: {base}{dept}{page}"
