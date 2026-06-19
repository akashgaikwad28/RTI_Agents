from __future__ import annotations

from pydantic import BaseModel

from rag.ingestion.cleaners.text_cleaner import detect_language
from tools.base.base_tool import BaseTool


class TextInput(BaseModel):
    text: str


class LanguageDetectorTool(BaseTool):
    name = "language_detector"
    description = "Detect English, Hindi, Marathi, or unknown text."
    category = "utility"
    permissions = ["read:public"]
    capabilities = ["language_detection"]
    input_schema = TextInput

    async def execute(self, text: str):
        return {"language": detect_language(text)}

