"""Phonetic mappings for romanized Hindi and Marathi governance queries."""

from __future__ import annotations


PHONETIC_TERMS = {
    "sadak": ["road", "सड़क"],
    "rasta": ["road", "रस्ता"],
    "vikas": ["development", "विकास"],
    "budget": ["budget", "बजट", "अर्थसंकल्प"],
    "mahiti": ["information", "माहिती"],
    "jaankari": ["information", "जानकारी"],
    "jankari": ["information", "जानकारी"],
    "pahije": ["required", "चाहिए", "पाहिजे"],
    "mala": ["I need", "मला"],
    "mujhe": ["I need", "मुझे"],
    "yojana": ["scheme", "योजना"],
    "kharcha": ["expenditure", "खर्च"],
    "anudan": ["grant", "अनुदान"],
    "pani": ["water", "पानी"],
    "nagar": ["municipal", "नगर"],
}


class PhoneticMapper:
    def expand_token(self, token: str) -> list[str]:
        return PHONETIC_TERMS.get(token.lower(), [])
