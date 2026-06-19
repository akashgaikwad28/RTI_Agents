import pytest
import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def test_unicode_normalizer():
    """Verify Unicode normalizer normalizes NFC and strips zero-width non-joiners."""
    from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
    
    normalizer = UnicodeNormalizer()
    
    # zero width characters should be stripped
    dirty_text = "हिन्दी\u200c"
    normalized = normalizer.normalize(dirty_text)
    assert "\u200c" not in normalized
    assert normalized == "हिन्दी"
    
    # check valid encoding
    res = normalizer.validate_encoding("मराठी")
    assert res["valid"] is True

def test_hindi_normalizer():
    """Verify Hindi normalizer cleans Devanagari text correctly."""
    from multilingual.normalization.hindi_normalizer import HindiNormalizer
    
    normalizer = HindiNormalizer()
    # Should collapse whitespace and format Devanagari danda characters properly
    res = normalizer.normalize("यह   एक  परीक्षण   है।")
    assert res == "यह एक परीक्षण है।"

def test_marathi_normalizer():
    """Verify Marathi normalizer cleans Marathi text."""
    from multilingual.normalization.marathi_normalizer import MarathiNormalizer
    
    normalizer = MarathiNormalizer()
    res = normalizer.normalize("माहितीचा   अधिकार   ॥")
    assert "माहितीचा अधिकार ॥" in res
