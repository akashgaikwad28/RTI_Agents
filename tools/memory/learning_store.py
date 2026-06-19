"""Long-term tool learning store backed by MongoDB when available."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class LearningStore:
    async def learn(self, db: Any, request_id: str | None, plan: dict, results: list[dict], consensus: dict) -> dict[str, Any]:
        rankings = {}
        for result in results:
            name = result.get("tool_name", "unknown")
            reward = (1.0 if result.get("status") == "success" else 0.0) + result.get("confidence", 0.0)
            rankings[name] = round(reward / 2, 4)
        doc = {
            "request_id": request_id,
            "plan": plan,
            "tool_rankings": rankings,
            "failure_reasons": [r.get("error") for r in results if r.get("error")],
            "consensus": consensus,
            "created_at": datetime.now(timezone.utc),
        }
        if db is not None:
            await db["tool_learning_memory"].insert_one(doc)
        return {"stored": db is not None, "tool_rankings": rankings, "failures": len(doc["failure_reasons"])}
