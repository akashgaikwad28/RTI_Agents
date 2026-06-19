"""Retrieval trace logger for reproducible debugging and evaluation."""

from __future__ import annotations

import json
import sqlite3
import contextlib
import time
from pathlib import Path
from typing import Any

from observability.structured_logger import get_logger

logger = get_logger(__name__)

class RetrievalTraceLogger:
    def __init__(self, db_path: str = "data/retrieval_traces.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self) -> None:
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS traces (
                        request_id TEXT PRIMARY KEY,
                        query TEXT NOT NULL,
                        embedding_vector_hash TEXT,
                        configuration TEXT,
                        top_k_results TEXT,
                        reranked_results TEXT,
                        filters_applied TEXT,
                        final_context TEXT,
                        timeline TEXT,
                        latency_ms REAL,
                        created_at REAL
                    )
                """)
            
    def log_trace(self, request_id: str, trace_data: dict[str, Any]) -> None:
        """Logs a complete retrieval trace for debugging and replay."""
        # Always log to local SQLite first (acts as local audit trail, cache, and zero-latency failsafe)
        self._log_to_sqlite_fallback(request_id, trace_data)
        
        # Log to Cloud MongoDB Atlas central aggregate tracking concurrently
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                loop.create_task(self._log_to_mongo(request_id, trace_data))
            else:
                asyncio.run(self._log_to_mongo(request_id, trace_data))
        except Exception as exc:
            logger.error(f"Failed to log retrieval trace to MongoDB Atlas: {exc}")

    async def _log_to_mongo(self, request_id: str, trace_data: dict[str, Any]) -> None:
        from mcp_clients.mongo_client import get_mongo_client
        mongo = await get_mongo_client()
        await mongo.db["retrieval_traces"].update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "request_id": request_id,
                    "query": trace_data.get("query", ""),
                    "embedding_vector_hash": trace_data.get("embedding_vector_hash", ""),
                    "configuration": trace_data.get("configuration", {}),
                    "top_k_results": trace_data.get("top_k_results", []),
                    "reranked_results": trace_data.get("reranked_results", []),
                    "filters_applied": trace_data.get("filters_applied", {}),
                    "final_context": trace_data.get("final_context", []),
                    "timeline": trace_data.get("timeline", []),
                    "latency_ms": trace_data.get("latency_ms", 0.0),
                    "created_at": time.time()
                }
            },
            upsert=True
        )
        logger.info(f"[RetrievalTraceLogger] Logged retrieval trace to MongoDB Atlas for request {request_id}")

    def _log_to_sqlite_fallback(self, request_id: str, trace_data: dict[str, Any]) -> None:
        try:
            with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
                with conn:
                    conn.execute(
                        """INSERT OR REPLACE INTO traces 
                           (request_id, query, embedding_vector_hash, configuration, top_k_results, reranked_results, filters_applied, final_context, timeline, latency_ms, created_at) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            request_id,
                            trace_data.get("query", ""),
                            trace_data.get("embedding_vector_hash", ""),
                            json.dumps(trace_data.get("configuration", {})),
                            json.dumps(trace_data.get("top_k_results", [])),
                            json.dumps(trace_data.get("reranked_results", [])),
                            json.dumps(trace_data.get("filters_applied", {})),
                            json.dumps(trace_data.get("final_context", [])),
                            json.dumps(trace_data.get("timeline", [])),
                            trace_data.get("latency_ms", 0.0),
                            time.time()
                        )
                    )
            logger.info(f"[RetrievalTraceLogger] Logged retrieval trace to local SQLite fallback for request {request_id}")
        except Exception as exc:
            logger.error(f"[RetrievalTraceLogger] Failed to log retrieval trace to SQLite fallback: {exc}")
