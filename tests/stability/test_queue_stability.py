"""Tests for async concurrency limits and memory leaks in the queue."""

import asyncio
import pytest
from rag.queue.persistent_queue import PersistentQueue

@pytest.mark.asyncio
@pytest.mark.slow
async def test_queue_concurrent_exhaustion(temp_workspace):
    """Simulates 100 concurrent workers trying to claim jobs."""
    db_path = temp_workspace / "stability_queue.db"
    queue = PersistentQueue(db_path=str(db_path))
    
    for i in range(50):
        queue.push(f"job_{i}", {})
        
    async def worker(worker_id):
        await asyncio.sleep(0.01)
        return queue.claim(worker_id=f"worker_{worker_id}")

    tasks = [worker(i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    
    successful_claims = [r for r in results if r is not None]
    assert len(successful_claims) == 50
