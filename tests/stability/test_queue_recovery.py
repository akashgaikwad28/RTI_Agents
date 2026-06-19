"""Tests for recovery of failed/stuck queue jobs post-failure."""

import pytest
import sqlite3
import contextlib
from rag.queue.persistent_queue import PersistentQueue

def recover_failed_jobs(queue: PersistentQueue) -> int:
    """Simulates a system recovery daemon resetting failed jobs back to PENDING."""
    with contextlib.closing(sqlite3.connect(queue.db_path)) as conn:
        with conn:
            cursor = conn.execute(
                "UPDATE jobs SET status = 'PENDING', worker_id = NULL, failure_reason = NULL WHERE status = 'FAILED'"
            )
            return cursor.rowcount

def test_queue_recovery_and_resume(temp_workspace):
    """Verify that failed jobs can be recovered and safely claimed again by workers."""
    db_path = temp_workspace / "recovery_queue.db"
    queue = PersistentQueue(db_path=str(db_path))
    
    # 1. Push and claim job
    job_id = "recoverable_job"
    queue.push(job_id, {"action": "parse"})
    job = queue.claim("worker_1")
    assert job is not None
    
    # 2. Simulate worker crash / failure
    queue.fail(job_id, "OutOfMemoryError during document parsing")
    
    # 3. Verify it is marked failed and cannot be claimed by others
    assert queue.claim("worker_2") is None
    
    # 4. Trigger recovery
    recovered_count = recover_failed_jobs(queue)
    assert recovered_count == 1
    
    # 5. Verify the job is successfully resumed and can be claimed again
    job_retry = queue.claim("worker_3")
    assert job_retry is not None
    assert job_retry["job_id"] == job_id
    assert job_retry["status"] == "PROCESSING"
    assert job_retry["worker_id"] == "worker_3"
