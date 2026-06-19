"""Prepares PDF pages as images for optimal OCR."""

from __future__ import annotations

from typing import Any

def get_image_from_pdf_page(page: Any, dpi: int = 300) -> bytes:
    """Renders a PyMuPDF page as a high-res image byte stream."""
    pix = page.get_pixmap(dpi=dpi)
    return pix.tobytes("png")
