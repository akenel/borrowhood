"""AI-powered listing and profile generation API.

Multi-provider cascade: Gemini -> Ollama Turbo -> Pollinations -> template.
Smart listing, review analysis, and concierge endpoints.
These endpoints power the "grandma test" -- list an item in 60 seconds.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import require_auth
from src.services.ai import (
    generate_listing_description, generate_skill_bio,
    generate_image_url, build_image_prompt, generate_image,
)
from src.services.gemini import smart_listing, review_analysis, concierge_search

logger = logging.getLogger(__name__)

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
    category: str = Field(default="", max_length=50)
    description: str = Field(default="", max_length=500)
    brand: str = Field(default="", max_length=100)
    prompt: Optional[str] = Field(None, max_length=500)


class ImageGenerateResponse(BaseModel):
    image_url: str
    prompt: str
    ai_generated: bool


@router.post("/generate-image", response_model=ImageGenerateResponse)
async def ai_generate_image(
    data: ImageGenerateRequest,
    token: dict = Depends(require_auth),
):
    """Generate a product preview image.

    If prompt is provided, uses it directly (user edited it).
    Otherwise builds a smart prompt from name + description + brand + category.
    Returns the prompt used so the user can see and edit it.
    """
    prompt = data.prompt or build_image_prompt(
        name=data.name,
        description=data.description,
        category=data.category,
        brand=data.brand,
    )
    result = await generate_image(prompt)
    return {
        "image_url": result["image_url"],
        "prompt": prompt,
        "ai_generated": result["ai_generated"],
    }


# ── Gemini-powered endpoints ──────────────────────────────────────────


class SmartListingRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(default="", max_length=50)
    item_type: str = Field(default="physical", max_length=30)
    language: str = Field(default="en", max_length=5)


class SmartListingResponse(BaseModel):
    title: str
    description: str
    category: str = ""
    subcategory: str = ""
    condition: str = ""
    item_type: str = "physical"
    suggested_price: float = 0.0
    price_unit: str = "per_day"
    deposit_suggestion: float = 0.0
    suggested_listing_type: str = "rent"
    tags: List[str] = []
    story_suggestion: str = ""
    ai_provider: str = "gemini"


@router.post("/smart-listing", response_model=SmartListingResponse)
async def ai_smart_listing(
    data: SmartListingRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate a complete listing with Gemini intelligence.

    Returns price, deposit, story, subcategory -- everything needed to list.
    Falls back to Pollinations.ai if Gemini is unavailable.
    """
    from src.models.item import BHItem

    # Fetch similar items for price calibration
    similar = []
    stmt = select(BHItem).where(
        BHItem.name.ilike(f"%{data.name.split()[0]}%")
    ).limit(5)
    result = await db.execute(stmt)
    for item in result.scalars():
        similar.append({
            "name": item.name,
            "category": item.category,
            "condition": str(item.condition.value) if item.condition else "",
        })

    # Try AI provider cascade (gemini -> ollama -> pollinations)
    ai_result, provider = await smart_listing(
        name=data.name,
        category=data.category,
        item_type=data.item_type,
        language=data.language,
        similar_items=similar,
    )

    if ai_result:
        return SmartListingResponse(
            title=ai_result.get("title", data.name),
            description=ai_result.get("description", ""),
            category=ai_result.get("category", data.category),
            subcategory=ai_result.get("subcategory", ""),
            condition=ai_result.get("condition", "good"),
            item_type=ai_result.get("item_type", data.item_type),
            suggested_price=float(ai_result.get("suggested_price", 0)),
            price_unit=ai_result.get("price_unit", "per_day"),
            deposit_suggestion=float(ai_result.get("deposit_suggestion", 0)),
            suggested_listing_type=ai_result.get("suggested_listing_type", "rent"),
            tags=ai_result.get("tags", [])[:5],
            story_suggestion=ai_result.get("story_suggestion", ""),
            ai_provider=provider,
        )

    # All AI providers failed -- use basic template fallback
    logger.info("All AI providers unavailable, using template fallback for smart-listing")
    fallback = await generate_listing_description(
        name=data.name,
        category=data.category or "hand_tools",
        item_type=data.item_type,
        language=data.language,
    )
    return SmartListingResponse(
        title=fallback.get("title", data.name),
        description=fallback.get("description", ""),
        tags=fallback.get("tags", []),
        category=data.category,
        ai_provider="template",
    )


class ReviewAnalysisRequest(BaseModel):
    user_id: UUID


class ReviewAnalysisResponse(BaseModel):
    user_name: str = ""
    badge_tier: str = ""
    total_reviews: int = 0
    sentiment: dict = {}
    average_rating: float = 0.0
    weighted_average: float = 0.0
    fake_review_flags: List[str] = []
    skill_insights: List[dict] = []
    top_keywords: dict = {}
    summary: str = ""
    ai_provider: str = ""


@router.post("/review-analysis", response_model=ReviewAnalysisResponse)
async def ai_review_analysis(
    data: ReviewAnalysisRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Analyze reviews for a user using Gemini AI.

    Returns sentiment breakdown, fake review flags, skill insights,
    and a human-readable summary.
    """
    from src.models.user import BHUser
    from src.models.review import BHReview

    # Get user
    user = await db.get(BHUser, data.user_id)
    if not user:
        return ReviewAnalysisResponse(summary="User not found.")

    # Get reviews
    stmt = select(BHReview).where(BHReview.reviewee_id == data.user_id)
    result = await db.execute(stmt)
    db_reviews = result.scalars().all()

    reviews = []
    total_rating = 0.0
    for r in db_reviews:
        reviews.append({
            "rating": r.rating,
            "title": r.title or "",
            "body": r.body or "",
            "reviewer_tier": r.reviewer_tier,
            "weight": r.weight,
            "skill_name": r.skill_name,
            "skill_rating": r.skill_rating,
        })
        total_rating += r.rating

    avg_rating = total_rating / len(reviews) if reviews else 0.0

    ai_result, provider = await review_analysis(
        user_name=user.display_name,
        badge_tier=str(user.badge_tier.value) if user.badge_tier else "NEWCOMER",
        reviews=reviews,
        review_count=len(reviews),
        average_rating=avg_rating,
    )

    if ai_result:
        ai_result["ai_provider"] = provider
        return ReviewAnalysisResponse(**ai_result)

    # All AI providers failed -- basic stats fallback
    positive = sum(1 for r in reviews if r["rating"] >= 4)
    neutral = sum(1 for r in reviews if r["rating"] == 3)
    negative = sum(1 for r in reviews if r["rating"] <= 2)
    return ReviewAnalysisResponse(
        user_name=user.display_name,
        badge_tier=str(user.badge_tier.value) if user.badge_tier else "NEWCOMER",
        total_reviews=len(reviews),
        sentiment={"positive": positive, "neutral": neutral, "negative": negative},
        average_rating=round(avg_rating, 1),
        summary=f"{user.display_name} has {len(reviews)} review(s) with an average rating of {avg_rating:.1f}/5.",
        ai_provider="template",
    )


class ConciergeRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    language: str = Field(default="en", max_length=5)


class ConciergeResponse(BaseModel):
    interpretation: str = ""
    response: str = ""
    suggestions: List[str] = []
    items: List[dict] = []
    members: List[dict] = []
    ai_provider: str = ""


@router.post("/concierge", response_model=ConciergeResponse)
async def ai_concierge(
    data: ConciergeRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Natural language search powered by Gemini.

    User asks in plain language, we search the DB, Gemini formats
    a friendly response with match reasons and suggestions.
    """
    from src.models.item import BHItem
    from src.models.user import BHUser, BHUserLanguage
    from sqlalchemy.orm import selectinload

    # Search items
    words = data.query.lower().split()
    item_stmt = select(BHItem).options(selectinload(BHItem.owner)).limit(10)
    for word in words[:3]:  # Use first 3 words for search
        if len(word) > 2:
            item_stmt = item_stmt.where(
                BHItem.name.ilike(f"%{word}%") | BHItem.description.ilike(f"%{word}%")
            )
    result = await db.execute(item_stmt)
    db_items = result.scalars().all()

    items_for_gemini = []
    items_for_response = []
    for item in db_items:
        item_dict = {
            "id": str(item.id),
            "name": item.name,
            "category": item.category,
            "condition": str(item.condition.value) if item.condition else "",
            "owner_name": item.owner.display_name if item.owner else "",
            "owner_badge": str(item.owner.badge_tier.value) if item.owner and item.owner.badge_tier else "",
        }
        items_for_gemini.append(item_dict)
        items_for_response.append(item_dict)

    # Search members (if query seems people-related)
    people_words = {"who", "speak", "speaks", "language", "member", "person", "someone"}
    search_members = any(w in words for w in people_words)

    members_for_gemini = []
    members_for_response = []
    if search_members:
        member_stmt = (
            select(BHUser)
            .options(selectinload(BHUser.languages))
            .limit(5)
        )
        for word in words[:3]:
            if len(word) > 2 and word not in people_words:
                member_stmt = member_stmt.where(
                    BHUser.display_name.ilike(f"%{word}%")
                    | BHUser.workshop_name.ilike(f"%{word}%")
                )
        result = await db.execute(member_stmt)
        db_members = result.scalars().all()
        for m in db_members:
            langs = [
                f"{l.language_code} ({l.proficiency})"
                for l in (m.languages or [])
            ]
            member_dict = {
                "id": str(m.id),
                "display_name": m.display_name,
                "badge_tier": str(m.badge_tier.value) if m.badge_tier else "NEWCOMER",
                "languages": langs,
                "workshop_name": m.workshop_name or "",
            }
            members_for_gemini.append(member_dict)
            members_for_response.append(member_dict)

    # Get AI interpretation (cascade: gemini -> ollama -> pollinations)
    ai_result, provider = await concierge_search(
        query=data.query,
        language=data.language,
        items=items_for_gemini,
        members=members_for_gemini,
    )

    if ai_result:
        return ConciergeResponse(
            interpretation=ai_result.get("interpretation", data.query),
            response=ai_result.get("response", ""),
            suggestions=ai_result.get("suggestions", []),
            items=items_for_response,
            members=members_for_response,
            ai_provider=provider,
        )

    # All AI providers failed -- basic fallback
    if items_for_response:
        names = ", ".join(i["name"] for i in items_for_response[:3])
        return ConciergeResponse(
            interpretation=data.query,
            response=f"I found some items that might match: {names}",
            suggestions=["Try a different category", "Search by brand name"],
            items=items_for_response,
            members=members_for_response,
            ai_provider="template",
        )

    return ConciergeResponse(
        interpretation=data.query,
        response="I couldn't find anything matching your search. Try different keywords or browse by category.",
        suggestions=["Browse all items", "Check the helpboard"],
        items=[],
        members=[],
        ai_provider="template",
    )
