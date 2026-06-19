"""Tool metrics helpers."""

from __future__ import annotations

from observability.metrics import tool_execution_duration, tool_executions_total


def record_tool_metric(tool_name: str, status: str, latency_ms: float) -> None:
    tool_executions_total.labels(tool=tool_name, status=status).inc()
    tool_execution_duration.labels(tool=tool_name).observe(latency_ms / 1000)
