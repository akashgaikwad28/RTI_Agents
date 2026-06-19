"""Tests for Persistent SQLite Queue."""

import pytest
from rag.queue.persistent_queue import PersistentQueue

@pytest.mark.unit
@pytest.mark.queue
def test_persistent_queue_lifecycle(temp_workspace):
    db_path = temp_workspace / "test_queue.db"
    queue = PersistentQueue(db_path=str(db_path))
    
    queue.push("job1", {"file": "test.pdf"})
    
    job = queue.claim(worker_id="worker_1")
    assert job is not None
    assert job["job_id"] == "job1"
    assert job["status"] == "PROCESSING"
    assert job["worker_id"] == "worker_1"
    
    assert queue.claim("worker_2") is None
    
    queue.complete("job1")
    
    queue2 = PersistentQueue(db_path=str(db_path))
    assert queue2.claim("worker_3") is None

@pytest.mark.unit
@pytest.mark.queue
def test_persistent_queue_failure(temp_workspace):
    db_path = temp_workspace / "test_queue2.db"
    queue = PersistentQueue(db_path=str(db_path))
    
    queue.push("job2", {})
    queue.claim("worker_1")
    queue.fail("job2", "Some error")
    
    import sqlite3
    import contextlib
    with contextlib.closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM jobs WHERE job_id = 'job2'").fetchone()
            assert row["status"] == "FAILED"
            assert row["failure_reason"] == "Some error"
