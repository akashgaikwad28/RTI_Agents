"""Timeout, retry, cache, permission, and tracing wrapper for tool calls."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
from typing import Any

from cachetools import TTLCache
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from communication.event_bus import get_event_bus
from observability.metrics import tool_execution_duration, tool_executions_total
from observability.structured_logger import get_logger
from tools.base.base_tool import BaseTool
from tools.base.tool_context import ToolContext
from tools.base.tool_permission import ToolPermissionChecker
from tools.base.tool_schemas import ToolExecutionResult, ToolInvocation
from tools.execution.execution_trace import ExecutionTraceStore
from tools.execution.retry_handler import CircuitBreaker
from tools.validation.result_validator import ResultValidator

logger = get_logger(__name__)


class ToolExecutor:
    def __init__(self):
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=2048, ttl=300)
        self._permissions = ToolPermissionChecker()
        self._validator = ResultValidator()
        self._traces = ExecutionTraceStore()
        self._breakers: dict[str, CircuitBreaker] = {}

    async def execute(self, tool: BaseTool, invocation: ToolInvocation) -> ToolExecutionResult:
        trace_id = str(uuid.uuid4())
        started = time.perf_counter()
        decision = self._permissions.check(tool.permissions, invocation.permissions)
        if not decision.allowed:
            result = self._result(tool.name, "permission_denied", trace_id, started, error=decision.reason, permission_scope=invocation.permissions)
            self._traces.record(result, invocation.payload)
            return result

        breaker = self._breakers.setdefault(tool.name, CircuitBreaker())
        if not breaker.can_execute():
            result = self._result(tool.name, "circuit_open", trace_id, started, error="Circuit breaker is open", permission_scope=invocation.permissions)
            self._traces.record(result, invocation.payload)
            return result

        try:
            payload = await tool.validate_input(invocation.payload)
        except Exception as exc:
            return self._result(tool.name, "error", trace_id, started, error=f"Invalid input: {exc}")

        cache_key = self._cache_key(tool.name, payload)
        if tool.cache_ttl_seconds and cache_key in self._cache:
            cached = self._result(tool.name, "success", trace_id, started, output=self._cache[cache_key], cached=True, permission_scope=invocation.permissions)
            self._traces.record(cached, payload)
            return cached

        bus = get_event_bus()
        await bus.publish("tool.started", {"tool": tool.name, "trace_id": trace_id, "request_id": invocation.request_id})
        retry_count = 0
        try:
            attempts = max(1, tool.max_retries + 1)
            async for attempt in AsyncRetrying(stop=stop_after_attempt(attempts), wait=wait_exponential(min=0.2, max=3), reraise=True):
                with attempt:
                    retry_count = attempt.retry_state.attempt_number - 1
                    context = ToolContext(
                        request_id=invocation.request_id,
                        trace_id=trace_id,
                        department=invocation.department,
                        actor=invocation.actor,
                        permissions=invocation.permissions,
                    )
                    if "context" in getattr(tool.execute, "__annotations__", {}):
                        output = await asyncio.wait_for(tool.execute(context=context, **payload), timeout=invocation.timeout_seconds or tool.timeout_seconds)
                    else:
                        output = await asyncio.wait_for(tool.execute(**payload), timeout=invocation.timeout_seconds or tool.timeout_seconds)
            validation = await self._validator.validate(tool, output)
            confidence = await tool.confidence_score(output, context)
            if not validation["valid"]:
                result = self._result(tool.name, "validation_failed", trace_id, started, output=output, validation=validation, confidence=confidence, retry_count=retry_count, permission_scope=invocation.permissions)
                breaker.record_failure()
                self._traces.record(result, payload)
                return result
            if tool.cache_ttl_seconds:
                self._cache[cache_key] = output
            breaker.record_success()
            result = self._result(tool.name, "success", trace_id, started, output=output, validation=validation, confidence=confidence, retry_count=retry_count, permission_scope=invocation.permissions)
        except asyncio.TimeoutError:
            breaker.record_failure()
            result = self._result(tool.name, "timeout", trace_id, started, error="Tool execution timed out", retry_count=retry_count, permission_scope=invocation.permissions)
        except Exception as exc:
            logger.warning(f"[ToolExecutor] {tool.name} failed: {exc}")
            breaker.record_failure()
            result = self._result(tool.name, "error", trace_id, started, error=str(exc), retry_count=retry_count, permission_scope=invocation.permissions)

        await bus.publish("tool.finished", result.model_dump())
        tool_executions_total.labels(tool=tool.name, status=result.status).inc()
        tool_execution_duration.labels(tool=tool.name).observe(result.latency_ms / 1000)
        self._traces.record(result, payload)
        return result

    def traces(self, trace_id: str | None = None) -> list[dict[str, Any]]:
        return self._traces.list(trace_id=trace_id)

    def _result(self, tool_name: str, status: str, trace_id: str, started: float, **kwargs: Any) -> ToolExecutionResult:
        return ToolExecutionResult(
            tool_name=tool_name,
            status=status,  # type: ignore[arg-type]
            trace_id=trace_id,
            latency_ms=(time.perf_counter() - started) * 1000,
            **kwargs,
        )

    def _cache_key(self, tool_name: str, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, default=str)
        return f"{tool_name}:{hashlib.sha256(encoded.encode()).hexdigest()}"
