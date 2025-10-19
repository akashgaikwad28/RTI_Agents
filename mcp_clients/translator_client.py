# translator_client.py - auto-generated
"""
translator_client.py
--------------------
Handles multilingual translation using Googletrans (free API).
Auto-detects input language and translates between English
and regional Indian languages for the RTI workflow.
"""

from googletrans import Translator
from utils.logger import logger
from utils.exception_handler import exception_handler


class TranslatorClient:
    """
    A lightweight wrapper around googletrans Translator.
    """

    def __init__(self):
        try:
            self.translator = Translator()
            logger.info("✅ TranslatorClient initialized successfully.")
        except Exception as e:
            logger.error(f"❌ TranslatorClient initialization failed: {e}")
            raise

    @exception_handler
    def detect_language(self, text: str) -> str:
        """
        Detects the language of the given text.
        Returns ISO language code (e.g., 'en', 'hi', 'mr', 'ta').
        """
        try:
            result = self.translator.detect(text)
            lang = result.lang
            logger.info(f"🌐 Detected language: {lang}")
            return lang
        except Exception as e:
            logger.error(f"❌ Language detection failed: {e}")
            raise

    @exception_handler
    def translate_to_english(self, text: str) -> str:
        """
        Translates the given text to English.
        """
        try:
            result = self.translator.translate(text, dest="en")
            logger.info("✅ Successfully translated to English.")
            return result.text
        except Exception as e:
            logger.error(f"❌ Translation to English failed: {e}")
            raise

    @exception_handler
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translates the given text from English to a target language.
        """
        try:
            result = self.translator.translate(text, dest=target_lang)
            logger.info(f"✅ Successfully translated from English to {target_lang}.")
            return result.text
        except Exception as e:
            logger.error(f"❌ Translation from English failed: {e}")
            raise


# Singleton instance for shared usage
translator_client = TranslatorClient()
