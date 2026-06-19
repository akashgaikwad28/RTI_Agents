"""OCR adapter for Hindi, Marathi, and English documents."""

from __future__ import annotations

import asyncio
from pathlib import Path


class MultilingualOCR:
    async def extract_text(self, path: str, languages: list[str] | None = None) -> dict:
        langs = languages or ["eng", "hin", "mar"]
        return await asyncio.to_thread(self._extract, Path(path), langs)

    def _extract(self, path: Path, languages: list[str]) -> dict:
        try:
            import pytesseract
            from PIL import Image

            text = pytesseract.image_to_string(Image.open(path), lang="+".join(languages))
            return {"text": text, "engine": "tesseract", "languages": languages, "confidence": 0.7 if text.strip() else 0.0}
        except Exception as exc:
            return {"text": "", "engine": "unavailable", "languages": languages, "confidence": 0.0, "error": str(exc)}
