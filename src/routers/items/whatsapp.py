"""WhatsApp connect: authenticated wa.me link + audit log."""

import uuid as uuid_mod
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth, require_badge_tier, user_throttle
from src.models.item import ATTRIBUTE_SCHEMAS, CATEGORY_GROUPS, BHItem, BHItemFavorite, BHItemMedia, MediaType, get_attribute_schema
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser
from src.schemas.item import ItemCreate, ItemOut, ItemUpdate

from ._shared import (
    UPLOAD_DIR,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
    ALLOWED_TYPES,
    MAX_IMAGE_SIZE,
    MAX_VIDEO_SIZE,
    _unique_slug,
)

router = APIRouter()

import logging
import re

_wa_log = logging.getLogger("borrowhood.whatsapp")


@router.post("/by-slug/{slug}/whatsapp-connect")
async def whatsapp_connect(
    slug: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return a wa.me link for the item's owner. Authenticated only.

    The seller's phone number is never in the page HTML -- only revealed
    via this authenticated API call, with an audit log entry.
    """
    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.owner))
        .where(BHItem.slug == slug)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.owner or not item.owner.whatsapp_number:
        raise HTTPException(status_code=404, detail="Seller has no WhatsApp number")

    if item.owner.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot contact yourself")

    # Sanitize number: digits only (strip +, spaces, dashes)
    digits = re.sub(r"[^\d]", "", item.owner.whatsapp_number)
    # Pre-filled message with item context
    msg = f"Hi, I'm interested in your listing: {item.name}"
    from urllib.parse import quote
    url = f"https://wa.me/{digits}?text={quote(msg)}"

    # Audit log
    _wa_log.info(
        "WhatsApp connect: buyer=%s requested seller=%s number for item=%s (%s)",
        user.id, item.owner.id, item.id, item.slug,
    )

    return {"url": url, "item": item.name}



