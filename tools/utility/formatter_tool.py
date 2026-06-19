from __future__ import annotations

from tools.base.base_tool import BaseTool
from tools.utility.validator_tool import ValidatorInput


class FormatterUtilityTool(BaseTool):
    name = "rti_formatter"
    description = "Deterministic fallback formatter for RTI clauses."
    category = "utility"
    permissions = ["read:public"]
    capabilities = ["formatting"]
    input_schema = ValidatorInput

    async def execute(self, query: str):
        return {
            "formatted": (
                "I request certified information under the Right to Information Act, 2005 regarding: "
                f"{query.strip()}"
            )
        }

