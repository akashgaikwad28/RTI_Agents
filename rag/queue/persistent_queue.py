"""SQLite-backed persistent queue for incremental embedding jobs."""

from __future__ import annotations

import sqlite3
import contextlib
import json
import time
from typing import Any
from pathlib import Path

from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)

class PersistentQueue:
    def __init__(self, db_path: str = "data/queue.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self) -> None:
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        payload TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        started_at REAL,
                        completed_at REAL,
                        failure_reason TEXT,
                        worker_id TEXT
                    )
                """)
            
    def push(self, job_id: str, payload: dict[str, Any]) -> None:
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO jobs (job_id, payload, status, created_at) VALUES (?, ?, ?, ?)",
                    (job_id, json.dumps(payload), "PENDING", time.time())
                )
            
    def claim(self, worker_id: str) -> dict[str, Any] | None:
        """Claims a pending job for a worker."""
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM jobs WHERE status = 'PENDING' ORDER BY created_at ASC LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    return None
                    
                job_id = row["job_id"]
                cursor.execute(
                    "UPDATE jobs SET status = 'PROCESSING', started_at = ?, worker_id = ? WHERE job_id = ?",
                    (time.time(), worker_id, job_id)
                )
            job_dict = dict(row)
            job_dict["status"] = "PROCESSING"
            job_dict["worker_id"] = worker_id
            return job_dict
            
    def complete(self, job_id: str) -> None:
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    "UPDATE jobs SET status = 'COMPLETED', completed_at = ? WHERE job_id = ?",
                    (time.time(), job_id)
                )
            
    def fail(self, job_id: str, reason: str) -> None:
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    "UPDATE jobs SET status = 'FAILED', completed_at = ?, failure_reason = ? WHERE job_id = ?",
                    (time.time(), reason, job_id)
                )
