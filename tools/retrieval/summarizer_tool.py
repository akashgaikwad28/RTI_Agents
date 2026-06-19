from __future__ import annotations

from pydantic import BaseModel

from tools.base.base_tool import BaseTool


class SummarizerInput(BaseModel):
    texts: list[str]
    max_chars: int = 1200


class SummarizerTool(BaseTool):
    name = "context_summarizer"
    description = "Extract concise grounded summary snippets from retrieved context."
    category = "retrieval"
    permissions = ["read:rag"]
    capabilities = ["summarization"]
    input_schema = SummarizerInput

    async def execute(self, texts: list[str], max_chars: int = 1200):
        joined = "\n\n".join(text.strip() for text in texts if text.strip())
        return {"summary": joined[:max_chars], "source_count": len(texts)}

