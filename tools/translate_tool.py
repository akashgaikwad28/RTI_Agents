"""
tools/translate_tool.py
------------------------
Async translation tool using enterprise TranslatorRouter.
Translates non-English RTI queries to English.
"""

from observability.structured_logger import get_logger

logger = get_logger(__name__)


async def translate_to_english(text: str) -> str:
    """
    Translates text to English using the enterprise TranslatorRouter.
    Falls back to original text on failure.
    """
    try:
        from multilingual.translation.translator_router import TranslatorRouter
        result = await TranslatorRouter().translate(text, target_language="en")
        translated = result.get("translated_text") or text
        logger.info(f"[TranslateTool] Translated: {text[:40]} → {translated[:40]}")
        return translated
    except Exception as e:
        logger.warning(f"[TranslateTool] Translation failed: {e}. Using original text.")
        return text
