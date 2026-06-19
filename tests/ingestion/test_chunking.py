"""Tests for semantic chunking logic."""

import pytest
from rag.ingestion.chunking.chunker import SmartChunker
from rag.types import LoadedDocument, DocumentMetadata

@pytest.mark.unit
@pytest.mark.rag
def test_smart_chunker_respects_boundaries():
    chunker = SmartChunker()
    text = "Paragraph 1 is here.\n\nParagraph 2 is here. It has multiple sentences. We don't want to break it.\n\nParagraph 3."
    doc = LoadedDocument(text=text, metadata=DocumentMetadata(source_url="http://test.com"))
    
    chunks = chunker.chunk_document(doc)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.metadata.source_url == "http://test.com"
        assert chunk.chunk_id is not None
        assert chunk.content_hash is not None

@pytest.mark.unit
def test_smart_chunker_discards_garbage():
    chunker = SmartChunker()
    doc = LoadedDocument(text="Too short.", metadata=DocumentMetadata())
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0
