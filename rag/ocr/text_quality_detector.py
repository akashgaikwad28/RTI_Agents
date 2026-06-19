"""Heuristics to determine if a PDF page requires OCR fallback."""

from __future__ import annotations

class TextQualityDetector:
    @staticmethod
    def needs_ocr(raw_text: str, threshold_chars: int = 50) -> bool:
        """Determines if the extracted text from a page is too sparse or low quality."""
        if not raw_text or len(raw_text.strip()) < threshold_chars:
            return True
            
        # Check if the text is mostly non-alphanumeric noise (garbled extraction)
        alnum_count = sum(c.isalnum() for c in raw_text)
        if alnum_count / max(len(raw_text), 1) < 0.4:
            return True
            
        return False
