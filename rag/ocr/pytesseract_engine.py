"""PyTesseract engine fallback for OCR."""

from __future__ import annotations

import io
from typing import TypedDict

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

from observability.structured_logger import get_logger

logger = get_logger(__name__)

class OCRResult(TypedDict):
    text: str
    confidence: float
    engine: str

def run_ocr(image_bytes: bytes, language: str = "eng+hin+mar") -> OCRResult:
    """Runs PyTesseract OCR on an image byte stream."""
    if Image is None or pytesseract is None:
        logger.warning("PyTesseract or Pillow not installed. Skipping OCR.")
        return {"text": "", "confidence": 0.0, "engine": "none"}
        
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang=language)
        return {
            "text": text.strip(),
            "confidence": 0.85 if text.strip() else 0.0,
            "engine": "pytesseract"
        }
    except Exception as exc:
        logger.error(f"PyTesseract OCR failed: {exc}")
        return {"text": "", "confidence": 0.0, "engine": "pytesseract_failed"}
