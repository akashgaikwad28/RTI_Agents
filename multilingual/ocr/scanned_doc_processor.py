"""Scanned document OCR processor."""

from __future__ import annotations

from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
from multilingual.ocr.document_parser import DocumentParser


class ScannedDocProcessor:
    async def process(self, path: str, languages: list[str] | None = None) -> dict:
        parsed = await DocumentParser().parse(path, languages)
        parsed["normalized_text"] = UnicodeNormalizer().normalize(parsed.get("text", ""))
        return parsed
