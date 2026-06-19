"""Benchmarks for ingestion parsing throughput."""

import pytest
import time
from rag.types import LoadedDocument, DocumentMetadata
from rag.ingestion.chunking.chunker import SmartChunker

@pytest.mark.benchmark
def test_chunking_throughput():
    chunker = SmartChunker()
    text = "This is a sentence. " * 1000
    doc = LoadedDocument(text=text, metadata=DocumentMetadata())
    
    start = time.perf_counter()
    iterations = 50
    for _ in range(iterations):
        chunker.chunk_document(doc)
    duration = time.perf_counter() - start
    
    throughput = iterations / duration
    print(f"Chunking throughput: {throughput:.2f} docs/sec")
    assert throughput > 10.0
