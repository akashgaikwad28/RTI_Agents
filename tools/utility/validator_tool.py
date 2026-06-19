from __future__ import annotations

from pydantic import BaseModel

from security.sanitizer import sanitize_query
from tools.base.base_tool import BaseTool


class ValidatorInput(BaseModel):
    query: str


class ValidatorTool(BaseTool):
    name = "query_validator"
    description = "Validate and sanitize user or agent-generated RTI text."
    category = "utility"
    permissions = ["read:public"]
    capabilities = ["validation", "prompt_injection_defense"]
    input_schema = ValidatorInput

    async def execute(self, query: str):
        sanitized = sanitize_query(query)
        return {"valid": True, "sanitized_query": sanitized}

