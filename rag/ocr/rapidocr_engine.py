"""RapidOCR engine fallback for OCR."""

from __future__ import annotations

import io
from typing import TypedDict

try:
    from PIL import Image
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    Image = None
    np = None
    RapidOCR = None

from observability.structured_logger import get_logger

logger = get_logger(__name__)

class OCRResult(TypedDict):
    text: str
    confidence: float
    engine: str

_engine = None

def get_engine():
    global _engine
    if RapidOCR and _engine is None:
        _engine = RapidOCR()
    return _engine

def run_ocr(image_bytes: bytes) -> OCRResult:
    """Runs RapidOCR on an image byte stream."""
    if Image is None or np is None or RapidOCR is None:
        logger.warning("RapidOCR dependencies not installed. Skipping OCR.")
        return {"text": "", "confidence": 0.0, "engine": "none"}
        
    try:
        engine = get_engine()
        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)
        
        result, elapse = engine(img_array)
        if not result:
            return {"text": "", "confidence": 0.0, "engine": "rapidocr"}
            
        texts = []
        confidences = []
        for line in result:
            texts.append(line[1])
            confidences.append(float(line[2]))
            
        final_text = "\n".join(texts)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "text": final_text.strip(),
            "confidence": avg_conf,
            "engine": "rapidocr"
        }
    except Exception as exc:
        logger.error(f"RapidOCR failed: {exc}")
        return {"text": "", "confidence": 0.0, "engine": "rapidocr_failed"}
