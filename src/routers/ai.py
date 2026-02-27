"""AI-powered listing and profile generation API.

Uses Pollinations.ai (free, no key) with Ollama fallback.
These endpoints power the "grandma test" -- list an item in 60 seconds.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.dependencies import require_auth
from src.services.ai import generate_listing_description, generate_skill_bio, generate_image_url

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class ListingGenerateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(..., max_length=50)
    item_type: str = Field(default="physical", max_length=30)
    language: str = Field(default="en", max_length=5)


class ListingGenerateResponse(BaseModel):
    title: str
    description: str
    tags: List[str]


class SkillBioRequest(BaseModel):
    skill_input: str = Field(..., min_length=2, max_length=200)
    language: str = Field(default="en", max_length=5)


class SkillBioResponse(BaseModel):
    bio: str


@router.post("/generate-listing", response_model=ListingGenerateResponse)
async def ai_generate_listing(
    data: ListingGenerateRequest,
    token: dict = Depends(require_auth),
):
    """Generate a listing title, description, and tags using AI.

    The grandma test: she types "embroidery machine" and gets a
    ready-to-publish listing in seconds.
    """
    result = await generate_listing_description(
        name=data.name,
        category=data.category,
        item_type=data.item_type,
        language=data.language,
    )
    return result


@router.post("/generate-skill-bio", response_model=SkillBioResponse)
async def ai_generate_skill_bio(
    data: SkillBioRequest,
    token: dict = Depends(require_auth),
):
    """Expand a short skill description into a professional bio.

    User types "I know carpentry" -> gets a full paragraph.
    """
    bio = await generate_skill_bio(
        skill_input=data.skill_input,
        language=data.language,
    )
    return {"bio": bio}


class ImageGenerateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(..., max_length=50)


class ImageGenerateResponse(BaseModel):
    image_url: str


@router.post("/generate-image", response_model=ImageGenerateResponse)
async def ai_generate_image(
    data: ImageGenerateRequest,
    token: dict = Depends(require_auth),
):
    """Generate a product preview image using Pollinations.ai.

    Returns a URL that generates the image on-demand (no storage needed).
    The grandma moment: type a name, get a professional product photo.
    """
    url = generate_image_url(name=data.name, category=data.category)
    return {"image_url": url}
