"""Base abstraction for async, observable MCP-style tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from tools.base.tool_schemas import ToolMetadata
from tools.base.tool_context import ToolContext
from tools.base.tool_result import ToolResult


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    category: str = "utility"
    permissions: list[str] = []
    capabilities: list[str] = []
    departments: list[str] = []
    timeout_seconds: int = 20
    cache_ttl_seconds: int | None = None
    input_schema: type[BaseModel] | None = None
    output_schema: type[BaseModel] | None = None
    version: str = "1.0.0"
    risk_level: str = "low"
    max_retries: int = 2
    supported_departments: list[str] = []

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            category=self.category,
            version=self.version,
            permissions=self.permissions,
            capabilities=self.capabilities,
            departments=self.departments,
            supported_departments=self.supported_departments or self.departments,
            input_schema=self.input_schema.model_json_schema() if self.input_schema else {},
            output_schema=self.output_schema.model_json_schema() if self.output_schema else {},
            timeout_seconds=self.timeout_seconds,
            cache_ttl_seconds=self.cache_ttl_seconds,
            risk_level=self.risk_level,  # type: ignore[arg-type]
        )

    async def validate_input(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.input_schema is None:
            return payload
        return self.input_schema.model_validate(payload).model_dump()

    async def health_check(self) -> dict[str, Any]:
        return {"healthy": True, "tool": self.name}

    async def confidence_score(self, output: Any, context: ToolContext | None = None) -> float:
        if isinstance(output, dict):
            if "confidence" in output:
                return float(output["confidence"])
            if output.get("citations") or output.get("sources") or output.get("source_url"):
                return 0.82
            if output.get("results"):
                return 0.72
        return 0.6 if output else 0.0

    async def validate_output(self, output: Any) -> ToolResult:
        if self.output_schema is None:
            return ToolResult(success=True, output=output, confidence=0.6)
        validated = self.output_schema.model_validate(output).model_dump()
        return ToolResult(success=True, output=validated, confidence=0.75)

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        raise NotImplementedError
