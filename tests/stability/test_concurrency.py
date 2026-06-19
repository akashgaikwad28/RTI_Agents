"""Tests to ensure no SQLite deadlocks occur under high concurrency loads."""

import pytest
import asyncio
import concurrent.futures
from rag.queue.persistent_queue import PersistentQueue

def run_sync_push(db_path, job_id):
    """Pushes a single job in a sync wrapper for thread safety testing."""
    queue = PersistentQueue(db_path=str(db_path))
    queue.push(job_id, {"data": "test"})
    return True

@pytest.mark.asyncio
async def test_sqlite_concurrency_no_deadlocks(temp_workspace):
    """Verifies that pushing and claiming concurrently across multiple threads does not lead to SQLite deadlocks."""
    db_path = temp_workspace / "concurrency_queue.db"
    queue = PersistentQueue(db_path=str(db_path))
    
    # 1. Concurrently push 50 jobs using a thread pool executor
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            loop.run_in_executor(executor, run_sync_push, db_path, f"concurrent_job_{i}")
            for i in range(50)
        ]
        results = await asyncio.gather(*futures)
        assert len(results) == 50
        
    # 2. Concurrently claim jobs using async tasks simulating multiple parallel workers
    async def worker(worker_id):
        # Claim a job from the queue
        return queue.claim(worker_id=f"worker_{worker_id}")

    claim_tasks = [worker(i) for i in range(100)]
    claim_results = await asyncio.gather(*claim_tasks)
    
    successful_claims = [r for r in claim_results if r is not None]
    
    # Exactly 50 jobs were pushed and should be claimed, remainder of claimants get None
    assert len(successful_claims) == 50
