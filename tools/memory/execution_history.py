"""Execution history persistence helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ExecutionHistory:
    async def record(self, db: Any, event: dict[str, Any]) -> dict[str, Any]:
        doc = {**event, "created_at": datetime.now(timezone.utc)}
        if db is not None:
            await db["tool_execution_history"].insert_one(doc)
        return {"stored": db is not None, "collection": "tool_execution_history"}
