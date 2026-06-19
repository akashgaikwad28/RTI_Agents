"""Tool feedback model and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ToolFeedback:
    async def record(self, db: Any, tool_name: str, score: float, reason: str, request_id: str | None = None) -> dict[str, Any]:
        doc = {"tool_name": tool_name, "score": score, "reason": reason, "request_id": request_id, "created_at": datetime.now(timezone.utc)}
        if db is not None:
            await db["tool_feedback"].insert_one(doc)
        return doc
