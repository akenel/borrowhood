"""Attribute schema endpoints (must register before /{item_id} to avoid UUID conflict)."""

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

# ── Attribute schemas (must be BEFORE /{item_id} to avoid UUID conflict) ──


@router.get("/attribute-schema/{category}")
async def get_category_attributes(category: str):
    """Return the attribute field definitions for a category.
    Frontend uses this to render dynamic form fields."""
    schema = get_attribute_schema(category)
    return {"category": category, "fields": schema}


@router.get("/attribute-schemas")
async def get_all_attribute_schemas():
    """Return all attribute schemas and category groups."""
    return {
        "schemas": ATTRIBUTE_SCHEMAS,
        "groups": CATEGORY_GROUPS,
    }



