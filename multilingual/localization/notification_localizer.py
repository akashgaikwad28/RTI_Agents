"""Localized notification messages."""

from __future__ import annotations


class NotificationLocalizer:
    def localize(self, key: str, language: str = "en", **values) -> str:
        templates = {
            "submitted": {"en": "RTI request submitted.", "hi": "आरटीआई अनुरोध जमा हो गया है।", "mr": "आरटीआय विनंती जमा झाली आहे."},
            "approval_pending": {"en": "Approval is pending.", "hi": "अनुमोदन लंबित है।", "mr": "मंजुरी प्रलंबित आहे."},
        }
        return templates.get(key, {}).get(language, templates.get(key, {}).get("en", key)).format(**values)
