"""
Typed RAG data contracts used across ingestion, scraping, vector storage,
retrieval, memory, and API endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


SupportedLanguage = Literal["en", "hi", "mr", "unknown"]


class DocumentMetadata(BaseModel):
    source_url: str = ""
    source_path: str = ""
    source_hash: str = ""
    department: str = ""
    document_type: str = "unknown"
    language: SupportedLanguage = "unknown"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    scraped_at: str | None = None
    title: str = ""
    domain: str = ""
    file_name: str = ""
    mime_type: str = ""
    page_number: int | None = None
    
    # Phase B++: Document Versioning & Soft Lineage
    document_id: str = ""
    version: int = 1
    is_latest: bool = True
    effective_date: str = ""
    superseded_by: str | None = None
    supersedes: str | None = None
    last_modified: str | None = None
    version_hash: str = ""
    lineage_id: str = ""
    version_reason: str = ""
    change_summary: str = ""
    content_delta_hash: str = ""
    
    extra: dict[str, Any] = Field(default_factory=dict)


class LoadedDocument(BaseModel):
    text: str
    metadata: DocumentMetadata


class DocumentChunk(BaseModel):
    text: str
    metadata: DocumentMetadata
    chunk_id: str
    chunk_index: int
    content_hash: str
    
    # Phase B++: Historical Preservation & Hierarchy
    is_active: bool = True
    department_id: str = ""
    document_id: str = ""
    section_id: str = ""
    section_title: str = ""
    parent_chunk: str | None = None


class ScrapeTarget(BaseModel):
    name: str
    base_url: HttpUrl
    department: str = ""
    allowed_domains: list[str] = Field(default_factory=list)
    start_paths: list[str] = Field(default_factory=lambda: ["/"])
    document_types: list[str] = Field(default_factory=list)
    max_depth: int = 1
    rate_limit_per_second: float = 0.5
    enabled: bool = True


class ScrapeResult(BaseModel):
    target: str
    pages_seen: int = 0
    pages_saved: int = 0
    pdfs_saved: int = 0
    duplicates: int = 0
    failures: list[str] = Field(default_factory=list)
    documents: list[LoadedDocument] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    text: str
    score: float
    metadata: DocumentMetadata
    source: str = "faiss"
    citation: str = ""


class IngestionReport(BaseModel):
    documents_loaded: int = 0
    chunks_created: int = 0
    chunks_indexed: int = 0
    duplicates_skipped: int = 0
    failed_files: list[str] = Field(default_factory=list)
    vector_store_path: str = "data/vector_store"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

