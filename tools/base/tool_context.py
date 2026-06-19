"""Execution context passed through tool calls."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ToolContext(BaseModel):
    request_id: str | None = None
    trace_id: str | None = None
    department: str | None = None
    actor: str = "agent"
    permissions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
