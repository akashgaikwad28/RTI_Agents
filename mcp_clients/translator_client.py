# mcp_clients/translator_client.py

"""
translator_client.py
--------------------
Handles multilingual translation using LibreTranslate API.
Auto-detects input language and translates between English
and regional Indian languages for the RTI workflow.
"""

import json
import requests
from config.settings import settings
from utils.logger import logger
from utils.exception_handler import exception_handler


class TranslatorClient:
    def __init__(self):
        """
        Initialize LibreTranslate client with fallback to public endpoint.
        """
        self.endpoint = settings.TRANSLATOR_API_ENDPOINT or "https://libretranslate.de"
        self.detect_url = f"{self.endpoint}/detect"
        self.translate_url = f"{self.endpoint}/translate"

        # Verify the endpoint is reachable
        try:
            response = requests.get(self.endpoint, timeout=15)
            if response.status_code == 200:
                logger.info(f"✅ LibreTranslate client initialized: {self.endpoint}")
            else:
                logger.warning(f"⚠️ LibreTranslate endpoint reachable but returned status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Failed to reach LibreTranslate endpoint: {e}")
            raise

    @exception_handler
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        Returns language code (e.g., 'en', 'hi', 'mr', etc.).
        """
        payload = {"q": text}
        try:
            response = requests.post(self.detect_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                raise ValueError("Empty response from detect API.")

            lang = data[0].get("language", "en")
            logger.info(f"🌐 Detected language: {lang}")
            return lang

        except requests.RequestException as e:
            logger.error(f"❌ Network error during language detection: {e}")
            return "en"
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to decode detection response: {e}")
            return "en"

    @exception_handler
    def translate(self, text: str, target_lang: str = "en") -> str:
        """
        Automatically detects the source language and translates to the target language.
        """
        source_lang = self.detect_language(text)

        if source_lang == target_lang:
            logger.info("⚠️ Source and target language are the same. Returning original text.")
            return text

        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }

        try:
            response = requests.post(self.translate_url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()

            translated_text = data.get("translatedText", "").strip()
            if not translated_text:
                raise ValueError("Empty translation result received.")

            logger.info(f"✅ Translated from {source_lang} → {target_lang}")
            return translated_text

        except requests.RequestException as e:
            logger.error(f"❌ Translation request failed: {e}")
            return text
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"❌ Error parsing translation response: {e}")
            return text


# Singleton instance
translator_client = TranslatorClient()
