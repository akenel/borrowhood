"""Internationalization engine.

Loads locale JSON files and provides a translation function
for use in Jinja2 templates via {{ t('key.path') }}.

Language selection priority:
1. ?lang= query parameter (sets cookie)
2. bh_lang cookie
3. Accept-Language header
4. Default: English
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LANGUAGES = ["en", "it"]
DEFAULT_LANGUAGE = "en"


@lru_cache(maxsize=None)
def load_locale(lang: str) -> dict:
    """Load and cache a locale file."""
    locale_file = LOCALES_DIR / f"{lang}.json"
    if not locale_file.exists():
        logger.warning("Locale file not found: %s, falling back to en", locale_file)
        locale_file = LOCALES_DIR / "en.json"

    with open(locale_file, encoding="utf-8") as f:
        return json.load(f)


def resolve_key(data: dict, key: str) -> str:
    """Resolve a dot-notation key like 'nav.home' from nested dict.

    Returns the key itself if not found (never show raw key to user,
    but also never crash -- log a warning instead).
    """
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            logger.warning("Missing i18n key: %s", key)
            # Fall back to English
            en_data = load_locale("en")
            en_current = en_data
            for en_part in parts:
                if isinstance(en_current, dict) and en_part in en_current:
                    en_current = en_current[en_part]
                else:
                    return key  # Last resort: return the key
            return en_current if isinstance(en_current, str) else key

    return current if isinstance(current, str) else key


def get_translator(lang: str):
    """Return a translation function for the given language.

    Usage in Jinja2: {{ t('nav.home') }}
    """
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE

    locale_data = load_locale(lang)

    def t(key: str) -> str:
        return resolve_key(locale_data, key)

    return t


def detect_language(
    query_param: Optional[str] = None,
    cookie_value: Optional[str] = None,
    accept_language: Optional[str] = None,
) -> str:
    """Detect user's preferred language.

    Priority: query param > cookie > Accept-Language header > default.
    """
    # 1. Query parameter
    if query_param and query_param in SUPPORTED_LANGUAGES:
        return query_param

    # 2. Cookie
    if cookie_value and cookie_value in SUPPORTED_LANGUAGES:
        return cookie_value

    # 3. Accept-Language header (simplified parsing)
    if accept_language:
        for part in accept_language.split(","):
            lang_code = part.strip().split(";")[0].split("-")[0].lower()
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code

    # 4. Default
    return DEFAULT_LANGUAGE
