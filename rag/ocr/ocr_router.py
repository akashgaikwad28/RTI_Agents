"""Routes low-quality PDF pages to the best available OCR engine."""

from __future__ import annotations

from typing import Any

from rag.ocr.image_preprocessor import get_image_from_pdf_page
from rag.ocr.pytesseract_engine import OCRResult, run_ocr as run_pytesseract
from rag.ocr.text_quality_detector import TextQualityDetector
from observability.structured_logger import get_logger

logger = get_logger(__name__)

class OCRRouter:
    @staticmethod
    def process_page(page: Any, raw_text: str) -> OCRResult | None:
        """
        Checks if a PyMuPDF page needs OCR and runs it if necessary.
        Returns OCRResult if OCR was run, else None.
        """
        if not TextQualityDetector.needs_ocr(raw_text):
            return None
            
        logger.info(f"Page quality too low (chars: {len(raw_text)}). Triggering OCR fallback.")
        
        try:
            image_bytes = get_image_from_pdf_page(page)
            result = run_pytesseract(image_bytes)
            return result
        except Exception as exc:
            logger.error(f"OCR Router failed to process page: {exc}")
            return None
