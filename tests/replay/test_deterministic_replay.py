"""Tests for replay traces."""

import pytest
from rag.debug.retrieval_trace_logger import RetrievalTraceLogger

@pytest.mark.unit
def test_retrieval_trace_logs_successfully(temp_workspace):
    logger = RetrievalTraceLogger(db_path=str(temp_workspace / "traces.db"))
    trace_data = {
        "query": "Test query",
        "embedding_vector_hash": "abc",
        "top_k_results": ["chunk1", "chunk2"],
        "latency_ms": 150.5
    }
    
    logger.log_trace("req1", trace_data)
    
    import sqlite3
    import contextlib
    with contextlib.closing(sqlite3.connect(temp_workspace / "traces.db")) as conn:
        with conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM traces WHERE request_id = 'req1'").fetchone()
            assert row["query"] == "Test query"
            assert row["latency_ms"] == 150.5
