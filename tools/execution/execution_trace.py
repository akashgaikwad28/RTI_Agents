"""In-memory execution trace store with Mongo-friendly documents."""

from __future__ import annotations

from collections import deque
from typing import Any

from tools.base.tool_schemas import ToolExecutionResult


class ExecutionTraceStore:
    def __init__(self, maxlen: int = 5000):
        self._events: deque[dict[str, Any]] = deque(maxlen=maxlen)

    def record(self, result: ToolExecutionResult, payload: dict[str, Any]) -> None:
        self._events.append({"trace_id": result.trace_id, "tool_name": result.tool_name, "payload": payload, "result": result.model_dump()})

    def list(self, trace_id: str | None = None) -> list[dict[str, Any]]:
        events = list(self._events)
        if trace_id:
            events = [event for event in events if event["trace_id"] == trace_id]
        return events
