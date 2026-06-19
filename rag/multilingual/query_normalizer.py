"""Query transliteration and normalization."""

from __future__ import annotations

from observability.structured_logger import get_logger

logger = get_logger(__name__)

class QueryNormalizer:
    @staticmethod
    def transliterate_to_native(query: str, target_lang: str) -> str:
        """
        Transliterates English script (Hinglish/Marathi) to native Devanagari.
        Placeholder for an actual transliteration engine (e.g. Indic-Transliteration).
        """
        return query
        
    @staticmethod
    def expand_bilingual(query: str, source_lang: str) -> list[str]:
        """
        Expands a query into a bilingual search space.
        Example: "pune road budget" -> ["pune road budget", "पुणे रस्ता अर्थसंकल्प"]
        """
        return [query]
