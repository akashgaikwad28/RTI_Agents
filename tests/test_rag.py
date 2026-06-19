import pytest
import sys
import os
import shutil
import tempfile
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.types import DocumentChunk, DocumentMetadata

@pytest.fixture
def temp_faiss_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_faiss_store_initialization(temp_faiss_dir):
    """Verify FAISS vector store initializes cleanly."""
    from rag.vectorstore.faiss_store import RealFaissStore
    
    store = RealFaissStore(index_path=temp_faiss_dir)
    assert store.is_loaded is False
    assert store.manifest == {}

def test_faiss_add_and_search_chunks(temp_faiss_dir):
    """Verify chunks are indexed, duplicated control works, and similarity searches return correct citations."""
    from rag.vectorstore.faiss_store import RealFaissStore
    
    store = RealFaissStore(index_path=temp_faiss_dir)
    
    metadata = DocumentMetadata(
        title="Puducherry RTI Guide",
        document_type="government_circular",
        department="Revenue",
        language="en",
        scraped_at="2026-05-18T00:00:00Z"
    )
    
    chunks = [
        DocumentChunk(
            chunk_id="chunk_001",
            chunk_index=0,
            text="Section 4 of RTI Act requires proactive disclosure of government budgets.",
            content_hash="hash_abc123",
            metadata=metadata
        )
    ]
    
    # Rebuild index
    result = store.rebuild(chunks)
    assert result["indexed"] == 1
    assert result["duplicates"] == 0
    assert store.is_loaded is True
    
    # Test duplicate control when adding same chunk
    add_result = store.add_chunks(chunks)
    assert add_result["indexed"] == 0
    assert add_result["duplicates"] == 1
    
    # Verify similarity search
    search_results = store.similarity_search("proactive disclosure", k=1)
    assert len(search_results) == 1
    assert "Section 4" in search_results[0].text
    assert search_results[0].metadata.department == "Revenue"
    assert "Puducherry RTI Guide" in search_results[0].citation

@pytest.mark.asyncio
async def test_semantic_cache_initialization():
    """Verify semantic cache singleton initialization."""
    from rag.vectorstore.semantic_cache import get_semantic_cache
    
    cache = await get_semantic_cache()
    assert cache is not None
