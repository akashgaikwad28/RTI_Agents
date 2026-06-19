"""Dashboard label localization."""

from __future__ import annotations

from multilingual.localization.ui_localization import UILocalization


class DashboardTranslation:
    def translate_labels(self, language: str = "en") -> dict:
        return UILocalization().messages(language)
