"""Tests for preventing unicode poisoning and zero-width character exploitation."""

import pytest
from multilingual.normalization.unicode_normalizer import UnicodeNormalizer

def test_unicode_normalization_strips_zero_width():
    """Verify that zero-width non-joiner and joiner characters are stripped out."""
    normalizer = UnicodeNormalizer()
    poisoned_text = "road\u200cbud\u200dget" # poisoned with \u200c and \u200d
    normalized = normalizer.normalize(poisoned_text)
    
    assert normalized == "roadbudget"
    assert "\u200c" not in normalized
    assert "\u200d" not in normalized

def test_unicode_normalization_strips_control_characters():
    """Verify that control characters are neutralized/replaced by space."""
    normalizer = UnicodeNormalizer()
    text_with_control = "road\u0001budget\u0007details"
    normalized = normalizer.normalize(text_with_control)
    
    assert normalized == "road budget details"
    assert "\u0001" not in normalized
    assert "\u0007" not in normalized

def test_unicode_encoding_validation():
    """Verify unicode encoding validation behaves correctly."""
    normalizer = UnicodeNormalizer()
    res = normalizer.validate_encoding("road budget 2024")
    assert res["valid"] is True
    assert res["encoding"] == "utf-8"
