"""Facade for long-term tool learning memory."""

from __future__ import annotations

from typing import Any

from tools.memory.execution_history import ExecutionHistory
from tools.memory.learning_store import LearningStore


class ToolMemory:
    def __init__(self):
        self.history = ExecutionHistory()
        self.learning = LearningStore()

    async def record_workflow(self, db: Any, request_id: str | None, plan: dict, results: list[dict], consensus: dict) -> dict:
        await self.history.record(db, {"request_id": request_id, "plan": plan, "results": results, "consensus": consensus})
        return await self.learning.learn(db, request_id, plan, results, consensus)
