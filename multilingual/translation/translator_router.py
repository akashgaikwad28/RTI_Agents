"""Enterprise translation router with cache, memory, and provider fallback."""

from __future__ import annotations

import time
from typing import Any

from multilingual.detection.language_detector import LanguageDetector
from multilingual.translation.gemini_translator import GeminiTranslator
from multilingual.translation.indictrans_adapter import IndicTransAdapter
from multilingual.translation.translation_cache import TranslationCache
from multilingual.translation.translation_memory import TranslationMemory


class TranslatorRouter:
    def __init__(self):
        self.detector = LanguageDetector()
        self.cache = TranslationCache()
        self.memory = TranslationMemory()
        self.providers = [IndicTransAdapter(), GeminiTranslator()]

    async def translate(self, text: str, target_language: str = "en", source_language: str | None = None, db: Any = None) -> dict:
        started = time.perf_counter()
        detection = self.detector.detect(text)
        source = source_language or detection.language
        if source == target_language:
            return {
                "source_language": source,
                "target_language": target_language,
                "translated_text": text,
                "provider": "identity",
                "cache_hit": False,
                "latency_ms": 0.0,
                "confidence": detection.confidence,
            }
        remembered = await self.memory.lookup(db, text, source, target_language)
        if remembered:
            return self._result(source, target_language, remembered, "translation_memory", True, started, detection.confidence)
        cached = await self.cache.get(text, source, target_language)
        if cached:
            return self._result(source, target_language, cached, "redis_cache", True, started, detection.confidence)
        translated = text
        provider_name = "fallback"
        for provider in self.providers:
            translated = await provider.translate(text, source, target_language)
            provider_name = provider.__class__.__name__
            if translated and translated != text:
                break
        await self.cache.set(text, source, target_language, translated)
        await self.memory.remember(db, text, translated, source, target_language, {"provider": provider_name})
        return self._result(source, target_language, translated, provider_name, False, started, detection.confidence)

    def _result(self, source: str, target: str, translated: str, provider: str, cache_hit: bool, started: float, confidence: float) -> dict:
        return {
            "source_language": source,
            "target_language": target,
            "translated_text": translated,
            "provider": provider,
            "cache_hit": cache_hit,
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "confidence": confidence,
        }
