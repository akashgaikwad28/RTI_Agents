"""Detect likely PDF language from extracted text samples."""

from __future__ import annotations

from multilingual.detection.language_detector import LanguageDetector


class PDFLanguageDetector:
    def detect_from_text(self, text: str) -> dict:
        return LanguageDetector().detect(text[:5000]).model_dump()
