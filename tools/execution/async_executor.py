"""Parallel async tool execution orchestration."""

from __future__ import annotations

import asyncio
from typing import Any

from tools.base.tool_registry import get_tool_registry
from tools.base.tool_schemas import ToolCallPlan, ToolExecutionResult


class AsyncToolExecutor:
    async def run_plan(
        self,
        calls: list[ToolCallPlan],
        *,
        permissions: list[str],
        request_id: str | None = None,
        department: str | None = None,
    ) -> list[ToolExecutionResult]:
        registry = get_tool_registry()
        tasks = [
            registry.execute_tool(call.tool_name, call.payload, permissions=permissions, request_id=request_id, department=department)
            for call in calls
        ]
        raw = await asyncio.gather(*tasks, return_exceptions=True)
        results: list[ToolExecutionResult] = []
        for idx, item in enumerate(raw):
            if isinstance(item, ToolExecutionResult):
                results.append(item)
            else:
                results.append(
                    ToolExecutionResult(
                        tool_name=calls[idx].tool_name,
                        status="error",
                        error=str(item),
                        trace_id=f"exception:{idx}",
                    )
                )
        return results
