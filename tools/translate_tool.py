"""
tools/translate_tool.py
------------------------
Async translation tool using googletrans.
Translates non-English RTI queries to English.
"""

from observability.structured_logger import get_logger

logger = get_logger(__name__)


async def translate_to_english(text: str) -> str:
    """
    Translates text to English using googletrans.
    Falls back to original text on failure.
    """
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, dest="en")
        translated = result.text
        logger.info(f"[TranslateTool] Translated: {text[:40]} → {translated[:40]}")
        return translated
    except Exception as e:
        logger.warning(f"[TranslateTool] Translation failed: {e}. Using original text.")
        return text
