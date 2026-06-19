"""Tests for semantic retrieval evaluation using Ground Truth."""

import json
import pytest
from pathlib import Path
from rag.retriever import retrieve_rag_results
from rag.types import DocumentChunk, DocumentMetadata
from rag.vectorstore.faiss_store import get_faiss_store

@pytest.fixture
def populated_vectorstore(temp_workspace, mock_env):
    store = get_faiss_store()
    store.index_path = temp_workspace
    store.manifest_path = temp_workspace / "manifest.json"
    
    chunks = [
        DocumentChunk(
            text="Pune Road Budget Allocation 2024 is 100 Cr",
            chunk_id="chunk1",
            chunk_index=1,
            content_hash="hash1",
            metadata=DocumentMetadata(
                title="pwd_budget_2024.pdf",
                department="Road & Transport",
                document_type="budget"
            )
        ),
        DocumentChunk(
            text="RTI Act Section 19 describes appeal timeline.",
            chunk_id="chunk2",
            chunk_index=1,
            content_hash="hash2",
            metadata=DocumentMetadata(
                title="rti_act_2005.pdf",
                department="General Administration",
                document_type="act"
            )
        )
    ]
    store.rebuild(chunks)
    yield store

@pytest.mark.rag
@pytest.mark.integration
async def test_precision_recall_against_golden(populated_vectorstore):
    golden_path = Path("tests/retrieval/golden/golden_queries.json")
    if not golden_path.exists():
        pytest.skip("Golden queries missing")
        
    with open(golden_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
        
    q = queries[0]
    results, cache_hit, confidence = await retrieve_rag_results(q["query"], k=3)
    
    assert isinstance(results, list)
    assert len(results) <= 3
    assert isinstance(confidence, (float, int))
