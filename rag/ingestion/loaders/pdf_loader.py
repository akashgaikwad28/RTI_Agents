"""Async PDF loader backed by PyMuPDF."""

from __future__ import annotations

import asyncio
from pathlib import Path

import fitz

from rag.ingestion.cleaners.metadata_cleaner import build_metadata
from rag.ingestion.cleaners.text_cleaner import clean_text
from rag.types import LoadedDocument


def _extract_pdf_pages(path: Path) -> list[tuple[int, str, dict]]:
    from rag.ocr.ocr_router import OCRRouter
    pages: list[tuple[int, str, dict]] = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            raw_text = page.get_text("text")
            ocr_result = OCRRouter.process_page(page, raw_text)
            
            page_meta = {}
            final_text = raw_text
            if ocr_result:
                final_text = ocr_result["text"]
                page_meta = {
                    "ocr_confidence": ocr_result["confidence"],
                    "ocr_engine_used": ocr_result["engine"],
                    "ocr_page_count": 1,
                    "raw_text": raw_text,
                    "ocr_corrected_text": final_text
                }
            pages.append((index, final_text, page_meta))
    return pages


async def load_pdf(path: str | Path, *, source_url: str = "", department: str = "", title: str = "") -> list[LoadedDocument]:
    pdf_path = Path(path)
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

