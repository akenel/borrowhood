"""Smart matching service for Help Board.

Matches help posts to users with relevant skills.
Ranking: verified skills > self-rating > trust score > experience.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import BHUser, BHUserSkill

logger = logging.getLogger(__name__)

# Category synonyms for fuzzy matching
CATEGORY_SYNONYMS = {
    "repairs": ["hand_tools", "power_tools", "automotive", "electronics"],
    "hand_tools": ["repairs", "woodworking"],
    "power_tools": ["repairs", "woodworking", "automotive"],
    "automotive": ["repairs", "power_tools"],
    "woodworking": ["hand_tools", "power_tools", "art"],
    "welding": ["automotive", "repairs", "power_tools"],
    "kitchen": ["food", "cleaning"],
    "food": ["kitchen"],
    "garden": ["camping", "cleaning"],
    "electronics": ["computers", "repairs"],
    "computers": ["electronics"],
    "sewing": ["art"],
    "art": ["sewing", "photography", "woodworking"],
    "music": ["education"],
    "education": ["music", "computers"],
}


async def find_suggested_helpers(
    db: AsyncSession,
    post_category: str,
    post_author_id: UUID,
    limit: int = 5,
) -> list[dict]:
    """Find users with skills matching a help post's category.

    Returns list of dicts with user info + matching skill details,
    ranked by skill verification count, self-rating, trust score.
    """
    # Build category list: exact + synonyms
    categories = [post_category]
    if post_category in CATEGORY_SYNONYMS:
        categories.extend(CATEGORY_SYNONYMS[post_category])
    categories = list(set(categories))

    # Query users with matching skills, excluding post author
    q = (
        select(
            BHUser.id,
            BHUser.display_name,
            BHUser.slug,
            BHUser.avatar_url,
            BHUser.trust_score,
            BHUser.badge_tier,
            BHUser.workshop_name,
            BHUserSkill.skill_name,
            BHUserSkill.category,
            BHUserSkill.self_rating,
            BHUserSkill.verified_by_count,
            BHUserSkill.years_experience,
        )
        .join(BHUserSkill, BHUser.id == BHUserSkill.user_id)
        .where(
            BHUserSkill.category.in_(categories),
            BHUser.id != post_author_id,
            BHUser.deleted_at.is_(None),
        )
        .order_by(
            # Exact category match first
            case(
                (BHUserSkill.category == post_category, 0),
                else_=1,
            ),
            BHUserSkill.verified_by_count.desc(),
            BHUserSkill.self_rating.desc(),
            BHUser.trust_score.desc(),
        )
        .limit(limit * 2)  # Fetch extra to dedupe users
    )

    result = await db.execute(q)
    rows = result.all()

    # Dedupe by user (keep best skill per user)
    seen_users = set()
    helpers = []
    for row in rows:
        if row.id in seen_users:
            continue
        seen_users.add(row.id)
        helpers.append({
            "id": str(row.id),
            "display_name": row.display_name,
            "slug": row.slug,
            "avatar_url": row.avatar_url,
            "trust_score": float(row.trust_score) if row.trust_score else 0,
            "badge_tier": row.badge_tier.value if row.badge_tier else "newcomer",
            "workshop_name": row.workshop_name,
            "skill_name": row.skill_name,
            "skill_category": row.category,
            "self_rating": row.self_rating,
            "verified_by_count": row.verified_by_count or 0,
            "years_experience": row.years_experience,
            "exact_match": row.category == post_category,
        })
        if len(helpers) >= limit:
            break

    return helpers
