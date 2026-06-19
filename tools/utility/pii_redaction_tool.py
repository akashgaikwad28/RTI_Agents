from __future__ import annotations

from tools.base.base_tool import BaseTool
from tools.utility.language_detector_tool import TextInput
from security.pii_masker import mask_pii


class PIIRedactionTool(BaseTool):
    name = "pii_redaction"
    description = "Redact sensitive PII before tool/agent processing."
    category = "utility"
    permissions = ["privacy:redact"]
    capabilities = ["pii_redaction", "safety"]
    input_schema = TextInput

    async def execute(self, text: str):
        return {"text": mask_pii(text)}

