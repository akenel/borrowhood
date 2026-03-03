"""Translation API.

On-demand translation of user-generated content (items, reviews, help posts).
Backed by LibreTranslate (self-hosted) with DB caching.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.item import BHItem
from src.models.review import BHReview
from src.models.helpboard import BHHelpPost
from src.services.translation import translate_content, get_languages

router = APIRouter(prefix="/api/v1/translate", tags=["translation"])


# --- Schemas ---

class TranslateRequest(BaseModel):
    content_type: str  # "item_description", "item_story", "review", "helppost"
    content_id: UUID
    target_language: str  # e.g. "en", "it"


class TranslateResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    cached: bool


# --- Helpers ---

CONTENT_LOADERS = {
    "item_description": ("description", BHItem),
    "item_story": ("story", BHItem),
    "review": ("body", BHReview),
    "helppost": ("body", BHHelpPost),
}


async def _load_content(
    db: AsyncSession, content_type: str, content_id: UUID
) -> tuple[str, str]:
    """Load original text and source language for a content type.

    Returns (text, source_language) or raises 404.
    """
    if content_type not in CONTENT_LOADERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown content_type: {content_type}. "
                   f"Valid: {', '.join(CONTENT_LOADERS.keys())}",
        )

    field_name, model_cls = CONTENT_LOADERS[content_type]
    result = await db.execute(
        select(model_cls).where(model_cls.id == content_id)
    )
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{content_type} not found")

    text = getattr(obj, field_name, None)
    if not text:
        raise HTTPException(status_code=400, detail="Content is empty")

    source_lang = getattr(obj, "content_language", "en") or "en"
    return text, source_lang


# --- Endpoints ---

@router.post("", response_model=TranslateResponse)
async def translate(
    req: TranslateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Translate user-generated content. Cached after first translation."""
    if not settings.libretranslate_enabled:
        raise HTTPException(status_code=503, detail="Translation service not enabled")

    text, source_lang = await _load_content(db, req.content_type, req.content_id)

    if source_lang == req.target_language:
        return TranslateResponse(
            translated_text=text,
            source_language=source_lang,
            target_language=req.target_language,
            cached=False,
        )

    # Check cache
    from src.models.translation import BHContentTranslation
    cache_result = await db.execute(
        select(BHContentTranslation).where(
            BHContentTranslation.content_type == req.content_type,
            BHContentTranslation.content_id == req.content_id,
            BHContentTranslation.target_language == req.target_language,
        )
    )
    cached = cache_result.scalars().first()
    if cached:
        return TranslateResponse(
            translated_text=cached.translated_text,
            source_language=source_lang,
            target_language=req.target_language,
            cached=True,
        )

    # Translate via LibreTranslate
    translated = await translate_content(
        db, req.content_type, req.content_id,
        text, source_lang, req.target_language,
    )
    if not translated:
        raise HTTPException(status_code=502, detail="Translation service unavailable")

    await db.commit()

    return TranslateResponse(
        translated_text=translated,
        source_language=source_lang,
        target_language=req.target_language,
        cached=False,
    )


@router.get("/languages")
async def list_languages():
    """List languages supported by the translation service."""
    if not settings.libretranslate_enabled:
        return {"languages": [], "enabled": False}

    langs = await get_languages()
    return {"languages": langs, "enabled": True}
