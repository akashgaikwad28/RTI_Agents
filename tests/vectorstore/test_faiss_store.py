"""Tests for FAISS vector store."""

import pytest
from rag.types import DocumentChunk, DocumentMetadata
from rag.vectorstore.faiss_store import RealFaissStore

@pytest.mark.unit
@pytest.mark.vectorstore
def test_faiss_store_initializes(temp_workspace, mock_env):
    store = RealFaissStore(index_path=temp_workspace)
    assert store is not None
    assert store.manifest == {}

@pytest.mark.unit
@pytest.mark.vectorstore
def test_faiss_store_duplicate_prevention(temp_workspace, mock_env):
    store = RealFaissStore(index_path=temp_workspace)
    chunk1 = DocumentChunk(text="Chunk 1", chunk_id="1", chunk_index=1, content_hash="hash1", metadata=DocumentMetadata())
    chunk2 = DocumentChunk(text="Chunk 2", chunk_id="2", chunk_index=2, content_hash="hash1", metadata=DocumentMetadata())
    
    res1 = store.add_chunks([chunk1])
    assert res1["indexed"] == 1
    
    store2 = RealFaissStore(index_path=temp_workspace)
    assert len(store2.manifest) == 1
    
    res2 = store2.add_chunks([chunk2])
    assert res2["indexed"] == 0
    assert res2["duplicates"] == 1

@pytest.mark.unit
@pytest.mark.vectorstore
def test_deactivate_document_chunks(temp_workspace, mock_env):
    from rag.vectorstore.faiss_store import deactivate_document_chunks
    
    store = RealFaissStore(index_path=temp_workspace)
    store.manifest = {
        "chunk1": {"document_id": "doc1", "is_latest": True, "is_active": True},
        "chunk2": {"document_id": "doc1", "is_latest": True, "is_active": True},
        "chunk3": {"document_id": "doc2", "is_latest": True, "is_active": True}
    }
    store._save_manifest()
    
    import rag.vectorstore.faiss_store
    rag.vectorstore.faiss_store._store = store
    
    count = deactivate_document_chunks("doc1")
    assert count == 2
    assert store.manifest["chunk1"]["is_active"] is False
    assert store.manifest["chunk1"]["is_latest"] is False
    assert store.manifest["chunk3"]["is_active"] is True
