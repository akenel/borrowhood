"""Translation service -- LibreTranslate integration with DB caching.

Translates user-generated content on-demand. The original text is sacred;
translations are cached in bh_content_translation and served from cache
on subsequent requests.

Usage:
    translated = await translate_content(db, content_type, content_id,
                                         source_text, source_lang, target_lang)
"""

import logging
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.translation import BHContentTranslation, TranslationSource

logger = logging.getLogger(__name__)


async def translate_text(text: str, source: str, target: str) -> Optional[str]:
    """Call LibreTranslate API to translate text.

    Returns translated string, or None on failure.
    """
    if not settings.libretranslate_url:
        logger.warning("LibreTranslate URL not configured")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.libretranslate_url}/translate",
                json={
                    "q": text,
                    "source": source,
                    "target": target,
                    "format": "text",
                },
            )
        if resp.status_code == 200:
            return resp.json().get("translatedText")
        logger.error("LibreTranslate error: %s %s", resp.status_code, resp.text)
        return None
    except httpx.RequestError as e:
        logger.error("LibreTranslate connection error: %s", e)
        return None


async def translate_content(
    db: AsyncSession,
    content_type: str,
    content_id: UUID,
    source_text: str,
    source_lang: str,
    target_lang: str,
) -> Optional[str]:
    """Translate content with DB caching. Returns cached or fresh translation."""
    if source_lang == target_lang:
        return source_text

    # Check cache first
    result = await db.execute(
        select(BHContentTranslation).where(
            BHContentTranslation.content_type == content_type,
            BHContentTranslation.content_id == content_id,
            BHContentTranslation.target_language == target_lang,
        )
    )
    cached = result.scalars().first()
    if cached:
        return cached.translated_text

    # Call LibreTranslate
    translated = await translate_text(source_text, source_lang, target_lang)
    if not translated:
        return None

    # Cache the result
    entry = BHContentTranslation(
        content_type=content_type,
        content_id=content_id,
        source_language=source_lang,
        target_language=target_lang,
        translated_text=translated,
        translated_by=TranslationSource.API,
    )
    db.add(entry)
    await db.flush()

    return translated


async def get_languages() -> list[dict]:
    """Get list of languages supported by LibreTranslate."""
    if not settings.libretranslate_url:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{settings.libretranslate_url}/languages")
        if resp.status_code == 200:
            return resp.json()
        return []
    except httpx.RequestError:
        return []
