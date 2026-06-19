"""Typed schemas for MCP-style tool execution.

These contracts intentionally mirror the parts of MCP/OpenAI-style tool
calling that matter to RTI-Agent: discoverable schemas, auditable invocation,
structured results, confidence, and validation metadata.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ToolStatus = Literal["success", "error", "timeout", "permission_denied", "validation_failed", "circuit_open"]


class ToolMetadata(BaseModel):
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    permissions: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    departments: list[str] = Field(default_factory=list)
    supported_departments: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 20
    cache_ttl_seconds: int | None = None
    risk_level: Literal["low", "medium", "high"] = "low"


class ToolInvocation(BaseModel):
    tool_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    permissions: list[str] = Field(default_factory=list)
    request_id: str | None = None
    department: str | None = None
    actor: str = "agent"
    timeout_seconds: int | None = None


class ToolExecutionResult(BaseModel):
    tool_name: str
    status: ToolStatus
    output: Any = None
    error: str | None = None
    latency_ms: float = 0.0
    trace_id: str
    cached: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    validation: dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    permission_scope: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ToolCallPlan(BaseModel):
    tool_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    depends_on: list[str] = Field(default_factory=list)
    expected_output: str = ""


class ToolQueryRequest(BaseModel):
    query: str | None = Field(None, min_length=2)
    queries: list[str] | None = None
    department: str | None = None
    language: str = "en"
    permissions: list[str] = Field(default_factory=lambda: ["read:public", "read:rag", "network:gov", "privacy:redact"])
    max_tools: int = Field(default=6, ge=1, le=12)
    iterations: int = Field(default=1, ge=1, le=20)

    @model_validator(mode="after")
    def normalize_benchmark_queries(self) -> "ToolQueryRequest":
        if self.query is None and self.queries:
            self.query = " | ".join(self.queries)
        if self.query is None:
            raise ValueError("query is required")
        return self


class ToolQueryResponse(BaseModel):
    execution_plan: dict[str, Any]
    selected_tools: list[str]
    tool_results: list[ToolExecutionResult]
    debate: dict[str, Any]
    validation: dict[str, Any]
    consensus: dict[str, Any]
    reasoning_trace: list[dict[str, Any]]
