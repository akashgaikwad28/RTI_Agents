"""Tests for the OCR fallback pipeline."""

import os
import pytest
from rag.ocr.text_quality_detector import TextQualityDetector
from rag.ocr.ocr_router import OCRRouter
from rag.ocr.pytesseract_engine import run_ocr as run_pytesseract

@pytest.mark.unit
@pytest.mark.ocr
def test_text_quality_detector_needs_ocr():
    assert TextQualityDetector.needs_ocr("This is a clean paragraph with sufficient alphanumeric characters.", threshold_chars=40) is False
    assert TextQualityDetector.needs_ocr("short", threshold_chars=40) is True
    assert TextQualityDetector.needs_ocr("!@#$%^&*()_+-=[]{}|;':,./<>?    ", threshold_chars=10) is True

@pytest.mark.unit
@pytest.mark.ocr
def test_ocr_router_skips_clean_text():
    class DummyPage:
        pass
    result = OCRRouter.process_page(DummyPage(), "This is a completely clean paragraph that does not need OCR.")
    assert result is None

@pytest.mark.integration
@pytest.mark.ocr
@pytest.mark.skipif(os.environ.get("ENABLE_REAL_OCR_TESTS") != "true", reason="Real OCR tests disabled")
def test_real_pytesseract_execution():
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 30), color = (73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    
    result = run_pytesseract(img_byte_arr.getvalue(), language="eng")
    assert result is not None
    assert "engine" in result
