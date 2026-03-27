"""i18n engine tests."""

import pytest

from src.i18n import (
    SUPPORTED_LANGUAGES,
    detect_language,
    get_translator,
    load_locale,
    resolve_key,
)


def test_supported_languages():
    """Should support English and Italian."""
    assert "en" in SUPPORTED_LANGUAGES
    assert "it" in SUPPORTED_LANGUAGES


def test_load_locale_en():
    """Should load English locale file."""
    data = load_locale("en")
    assert "app" in data
    assert data["app"]["name"] == "La Piazza"


def test_load_locale_it():
    """Should load Italian locale file."""
    data = load_locale("it")
    assert "app" in data
    assert data["app"]["name"] == "La Piazza"


def test_load_locale_fallback():
    """Unknown locale should fall back to English."""
    data = load_locale("xx")
    assert data["app"]["name"] == "La Piazza"


def test_resolve_key_simple():
    """Should resolve simple dot-notation keys."""
    data = load_locale("en")
    assert resolve_key(data, "app.name") == "La Piazza"


def test_resolve_key_nested():
    """Should resolve nested keys."""
    data = load_locale("en")
    result = resolve_key(data, "nav.home")
    assert result == "Home"


def test_resolve_key_missing_falls_back_to_en():
    """Missing key in IT should fall back to English."""
    data = {"app": {"name": "Test"}}
    # Will fall back to en.json for missing key
    result = resolve_key(data, "nav.home")
    assert result == "Home"


def test_resolve_key_completely_missing():
    """Completely missing key should return the key itself."""
    data = load_locale("en")
    result = resolve_key(data, "totally.nonexistent.key")
    assert result == "totally.nonexistent.key"


def test_get_translator_returns_callable():
    """get_translator should return a function."""
    t = get_translator("en")
    assert callable(t)


def test_translator_en():
    """English translator should return English strings."""
    t = get_translator("en")
    assert t("nav.home") == "Home"
    assert t("nav.browse") == "Browse"


def test_translator_it():
    """Italian translator should return Italian strings."""
    t = get_translator("it")
    assert t("nav.home") == "Home"  # Same in both
    assert t("nav.browse") == "Esplora"


def test_translator_unsupported_lang():
    """Unsupported language should fall back to English."""
    t = get_translator("xx")
    assert t("nav.home") == "Home"


# --- Language Detection ---

def test_detect_query_param():
    """Query param should be highest priority."""
    assert detect_language("it", "en", "en") == "it"


def test_detect_cookie():
    """Cookie should override Accept-Language."""
    assert detect_language(None, "it", "en") == "it"


def test_detect_accept_language():
    """Accept-Language header should be parsed."""
    assert detect_language(None, None, "it-IT,it;q=0.9,en;q=0.8") == "it"


def test_detect_accept_language_en():
    """English Accept-Language should work."""
    assert detect_language(None, None, "en-US,en;q=0.9") == "en"


def test_detect_default():
    """No signals should default to English."""
    assert detect_language(None, None, None) == "en"


def test_detect_invalid_query_param():
    """Invalid query param should fall through to next priority."""
    assert detect_language("xx", "it", None) == "it"


def test_detect_invalid_cookie():
    """Invalid cookie should fall through to Accept-Language."""
    assert detect_language(None, "xx", "it") == "it"


# --- Locale file completeness ---

def test_all_en_keys_exist_in_it():
    """Every key in English should also exist in Italian."""
    en = load_locale("en")
    it = load_locale("it")

    def check_keys(en_dict, it_dict, prefix=""):
        for key, value in en_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key
            assert key in it_dict, f"Missing IT key: {full_key}"
            if isinstance(value, dict):
                assert isinstance(it_dict[key], dict), f"Type mismatch: {full_key}"
                check_keys(value, it_dict[key], full_key)

    check_keys(en, it)
