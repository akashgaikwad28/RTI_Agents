"""Semantic-preserving chunking for RTI/government documents."""

from __future__ import annotations

import hashlib

from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter

from config.settings import settings
from rag.types import DocumentChunk, LoadedDocument


class SmartChunker:
    def __init__(self, chunk_size: int | None = None, overlap: int | None = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap if overlap is not None else getattr(settings, "CHUNK_OVERLAP", 80)

        # Fix C2/C5: use MarkdownTextSplitter for HTML, RecursiveCharacterTextSplitter for PDFs/plain-text
        self._markdown_splitter = MarkdownTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
        )
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        )

    def _get_splitter(self, document_type: str):
        if document_type == "html":
            return self._markdown_splitter
        return self._text_splitter

    def chunk_documents(self, documents: list[LoadedDocument]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for document in documents:
            chunks.extend(self.chunk_document(document))
        return chunks

    def chunk_document(self, document: LoadedDocument) -> list[DocumentChunk]:
        splitter = self._get_splitter(document.metadata.document_type)
        raw_chunks = splitter.split_text(document.text)
        output: list[DocumentChunk] = []

        # Fix C1: hash full text (not truncated) — metadata_cleaner.py already hashes full text now
        base = document.metadata.source_hash or _hash(document.text)

        output_index = 0  # Fix C2: use dense sequential output index, not raw splitter index
        for raw_index, text in enumerate(raw_chunks):
            clean_chunk = text.strip()
            if len(clean_chunk) < 40:
                continue
            content_hash = _hash(clean_chunk)
            # Use output_index for chunk_id so IDs are always dense and collision-free
            chunk_id = f"{base[:16]}:{output_index}:{content_hash[:12]}"
            metadata = document.metadata.model_copy(deep=True)
            metadata.extra = {
                **metadata.extra,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.overlap,
                "chunk_index": output_index,
                "raw_splitter_index": raw_index,
            }
            output.append(
                DocumentChunk(
                    text=clean_chunk,
                    metadata=metadata,
                    chunk_id=chunk_id,
                    chunk_index=output_index,
                    content_hash=content_hash,
                )
            )
            output_index += 1
        return output


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
