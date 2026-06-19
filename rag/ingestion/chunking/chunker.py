"""Semantic-preserving chunking for RTI/government documents."""

from __future__ import annotations

import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import settings
from rag.types import DocumentChunk, LoadedDocument


class SmartChunker:
    def __init__(self, chunk_size: int | None = None, overlap: int | None = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap if overlap is not None else getattr(settings, "CHUNK_OVERLAP", 80)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        )

    def chunk_documents(self, documents: list[LoadedDocument]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for document in documents:
            chunks.extend(self.chunk_document(document))
        return chunks

    def chunk_document(self, document: LoadedDocument) -> list[DocumentChunk]:
        raw_chunks = self.splitter.split_text(document.text)
        output: list[DocumentChunk] = []
        base = document.metadata.source_hash or _hash(document.text[:5000])
        for index, text in enumerate(raw_chunks):
            clean_chunk = text.strip()
            if len(clean_chunk) < 40:
                continue
            content_hash = _hash(clean_chunk)
            chunk_id = f"{base[:16]}:{index}:{content_hash[:12]}"
            metadata = document.metadata.model_copy(deep=True)
            metadata.extra = {
                **metadata.extra,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.overlap,
                "chunk_index": index,
            }
            output.append(
                DocumentChunk(
                    text=clean_chunk,
                    metadata=metadata,
                    chunk_id=chunk_id,
                    chunk_index=index,
                    content_hash=content_hash,
                )
            )
        return output


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

