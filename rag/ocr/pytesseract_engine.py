"""PyTesseract engine fallback for OCR."""

from __future__ import annotations

import io
from typing import TypedDict

try:
    from PIL import Image
    import pytesseract
    _tesseract_available = True
except ImportError:
    Image = None
    pytesseract = None
    _tesseract_available = False

from observability.structured_logger import get_logger

logger = get_logger(__name__)


class OCRResult(TypedDict):
    text: str
    confidence: float
    engine: str


def run_ocr(image_bytes: bytes, language: str = "eng+hin+mar") -> OCRResult:
    """Runs PyTesseract OCR on an image byte stream with real confidence scores."""
    if not _tesseract_available or Image is None or pytesseract is None:
        logger.warning("PyTesseract or Pillow not installed. Skipping OCR.")
        return {"text": "", "confidence": 0.0, "engine": "none"}

    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang=language)

        # Fix: use real per-word confidence instead of hardcoded 0.85
        real_confidence = 0.0
        try:
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data.get("conf", []) if str(c).lstrip("-").isdigit() and int(c) >= 0]
            if confidences:
                real_confidence = round(sum(confidences) / len(confidences) / 100.0, 4)
        except Exception as conf_exc:
            logger.debug(f"Could not compute real OCR confidence: {conf_exc}")
            real_confidence = 0.7 if text.strip() else 0.0

        return {
            "text": text.strip(),
            "confidence": real_confidence,
            "engine": "pytesseract",
        }
    except Exception as exc:
        logger.error(f"PyTesseract OCR failed: {exc}")
        return {"text": "", "confidence": 0.0, "engine": "pytesseract_failed"}
