"""Communication bus event schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class WorkflowEvent(BaseModel):
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None
    node: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

