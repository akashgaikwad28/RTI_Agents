"""Multilingual embedding facade for cross-lingual retrieval."""

from __future__ import annotations

from rag.embeddings.embedding_router import get_embedder


class MultilingualEmbedder:
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.embedder = get_embedder(provider)

    async def aembed_query(self, text: str, language: str = "en") -> list[float]:
        return await self.embedder.aembed_query(f"language:{language}\n{text}")

    async def aembed_documents(self, texts: list[str], language: str = "unknown") -> list[list[float]]:
        return await self.embedder.aembed_documents([f"language:{language}\n{text}" for text in texts])

    def get_langchain_embedder(self):
        return self.embedder.get_langchain_embedder()
