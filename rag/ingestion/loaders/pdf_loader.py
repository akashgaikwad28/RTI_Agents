"""Async PDF loader backed by PyMuPDF."""

from __future__ import annotations

import asyncio
from pathlib import Path

import fitz

# Fix P1: move OCR import to module level with try/except so ImportError surfaces clearly
try:
    from rag.ocr.ocr_router import OCRRouter
    _ocr_available = True
except ImportError:
    OCRRouter = None  # type: ignore[assignment]
    _ocr_available = False

from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.ingestion.cleaners.text_cleaner import clean_text
from rag.types import LoadedDocument


def _extract_pdf_pages(path: Path) -> list[tuple[int, str, dict]]:
    pages: list[tuple[int, str, dict]] = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            raw_text = page.get_text("text")
            page_meta: dict = {}
            final_text = raw_text

            if _ocr_available and OCRRouter is not None:
                ocr_result = OCRRouter.process_page(page, raw_text)
                if ocr_result is not None:
                    # Fix P3: map OCRResult TypedDict keys correctly
                    final_text = ocr_result.get("text", raw_text) or raw_text
                    page_meta = {
                        "ocr_confidence": ocr_result.get("confidence", 0.0),
                        "ocr_engine_used": ocr_result.get("engine", "unknown"),
                        "ocr_page_count": 1,
                        "raw_text_chars": len(raw_text),
                    }

            pages.append((index, final_text, page_meta))
    return pages


async def load_pdf(
    path: str | Path,
    *,
    source_url: str = "",
    department: str = "",
    title: str = "",
) -> list[LoadedDocument]:
    pdf_path = Path(path)

    # Fix P4: validate file existence before entering the thread
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Fix P5: run in thread (already done), exceptions propagate cleanly to caller
    pages = await asyncio.to_thread(_extract_pdf_pages, pdf_path)

    documents: list[LoadedDocument] = []
    for page_number, raw_text, page_meta in pages:
        text = clean_text(raw_text)
        if not text:
            continue
        metadata = build_metadata(
            text=text,
            source_url=source_url,
            source_path=str(pdf_path),
            department=department,
            document_type="pdf",
            title=title or pdf_path.stem,
            mime_type="application/pdf",
            page_number=page_number,
            extra=page_meta,
        )
        documents.append(LoadedDocument(text=text, metadata=metadata))
    return documents
