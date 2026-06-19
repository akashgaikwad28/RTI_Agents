"""Document parser combining digital PDF extraction and OCR fallback."""

from __future__ import annotations

from pathlib import Path

from rag.ingestion.loaders.pdf_loader import load_pdf
from multilingual.ocr.multilingual_ocr import MultilingualOCR
from multilingual.ocr.pdf_language_detector import PDFLanguageDetector


class DocumentParser:
    async def parse(self, path: str, languages: list[str] | None = None) -> dict:
        file_path = Path(path)
        if file_path.suffix.lower() == ".pdf":
            docs = await load_pdf(file_path)
            text = "\n".join(doc.text for doc in docs)
            if text.strip():
                return {"text": text, "pages": len(docs), "language": PDFLanguageDetector().detect_from_text(text), "engine": "pymupdf"}
        ocr = await MultilingualOCR().extract_text(str(file_path), languages=languages)
        return {**ocr, "language": PDFLanguageDetector().detect_from_text(ocr.get("text", ""))}
