from __future__ import annotations

from pydantic import BaseModel

from tools.base.base_tool import BaseTool
from multilingual.translation.translator_router import TranslatorRouter


class TranslatorInput(BaseModel):
    text: str
    target_language: str = "en"
    source_language: str | None = None


class TranslatorUtilityTool(BaseTool):
    name = "translator"
    description = "Translate RTI text for multilingual workflows."
    category = "utility"
    permissions = ["read:public"]
    capabilities = ["translation"]
    input_schema = TranslatorInput

    async def execute(self, text: str, target_language: str = "en", source_language: str | None = None):
        return await TranslatorRouter().translate(text, target_language=target_language, source_language=source_language)
