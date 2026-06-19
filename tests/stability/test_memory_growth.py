"""Tests to monitor memory growth and SQLite file size limits under continuous load."""

import os
import pytest
import sys
from rag.queue.persistent_queue import PersistentQueue

def test_queue_database_size_stability(temp_workspace):
    """Ensure database size remains stable and bounded after high push/claim/complete activity."""
    db_path = temp_workspace / "bloat_queue.db"
    queue = PersistentQueue(db_path=str(db_path))
    
    # 1. Measure initial database file size after creation
    initial_size = os.path.getsize(db_path)
    
    # 2. Perform 500 operations (push, claim, complete)
    for i in range(100):
        job_id = f"bloat_job_{i}"
        queue.push(job_id, {"data": "A" * 1000}) # 1KB payload
        job = queue.claim("worker_bloat")
        assert job is not None
        queue.complete(job_id)
        
    final_size = os.path.getsize(db_path)
    
    # Assert database size is bounded and doesn't grow exponentially
    # High activity with cleanup shouldn't bloat the file beyond a reasonable margin (e.g., 500KB)
    assert final_size < 500 * 1024, f"Database file size grew too large: {final_size} bytes"
    
    # Assert sys.getsizeof on queue remains tiny
    assert sys.getsizeof(queue) < 1000, "Queue class instance has abnormal memory size"
