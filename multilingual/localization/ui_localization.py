"""Backend UI localization catalog."""

from __future__ import annotations


UI_MESSAGES = {
    "en": {"dashboard": "Dashboard", "approval": "Approval", "tools": "Tools", "confidence": "Confidence", "language": "Language"},
    "hi": {"dashboard": "डैशबोर्ड", "approval": "अनुमोदन", "tools": "उपकरण", "confidence": "विश्वास", "language": "भाषा"},
    "mr": {"dashboard": "डॅशबोर्ड", "approval": "मंजुरी", "tools": "साधने", "confidence": "विश्वास", "language": "भाषा"},
}


class UILocalization:
    def messages(self, language: str = "en") -> dict:
        return UI_MESSAGES.get(language, UI_MESSAGES["en"])
