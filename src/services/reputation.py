"""Reputation and points calculation service.

Points earned:
- Complete a rental (as renter): +10
- Complete a rental (as owner): +10
- Leave a review: +5
- Receive a positive review (4-5 stars): +15
- List an item: +3
- Get flagged as helpful: +5

Badge thresholds:
- Newcomer: 0-49
- Active: 50-199
- Trusted: 200-499
- Pillar: 500-999
- Legend: 1000+
"""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import BadgeTier, BHUser, BHUserPoints, BHUserSkill


# Points values
POINTS_RENTAL_COMPLETED = 10
POINTS_REVIEW_GIVEN = 5
POINTS_POSITIVE_REVIEW_RECEIVED = 15
POINTS_ITEM_LISTED = 3
POINTS_HELPFUL_FLAG = 5

# Badge thresholds
BADGE_THRESHOLDS = [
    (1000, BadgeTier.LEGEND),
    (500, BadgeTier.PILLAR),
    (200, BadgeTier.TRUSTED),
    (50, BadgeTier.ACTIVE),
    (0, BadgeTier.NEWCOMER),
]


def calculate_badge_tier(total_points: int) -> BadgeTier:
    """Determine badge tier from total points."""
    for threshold, tier in BADGE_THRESHOLDS:
        if total_points >= threshold:
            return tier
    return BadgeTier.NEWCOMER


async def award_points(
    db: AsyncSession,
    user_id: UUID,
    points: int,
    reason: str,
) -> BHUserPoints:
    """Award points to a user and update their badge tier."""
    result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user_id)
    )
    user_points = result.scalars().first()

    if not user_points:
        user_points = BHUserPoints(user_id=user_id, total_points=0)
        db.add(user_points)

    user_points.total_points += points

    # Update counter based on reason
    if reason == "rental_completed":
        user_points.rentals_completed += 1
    elif reason == "review_given":
        user_points.reviews_given += 1
    elif reason == "review_received":
        user_points.reviews_received += 1
    elif reason == "item_listed":
        user_points.items_listed += 1
    elif reason == "helpful_flag":
        user_points.helpful_flags += 1

    # Update badge tier on user
    new_tier = calculate_badge_tier(user_points.total_points)
    user_result = await db.execute(select(BHUser).where(BHUser.id == user_id))
    user = user_result.scalars().first()
    if user and user.badge_tier != new_tier:
        user.badge_tier = new_tier

    # Recalculate trust score
    await calculate_trust_score(db, user_id)

    await db.flush()
    return user_points


# Tier numeric values for trust score calculation
TIER_VALUES = {
    BadgeTier.NEWCOMER: 0.0,
    BadgeTier.ACTIVE: 0.25,
    BadgeTier.TRUSTED: 0.5,
    BadgeTier.PILLAR: 0.75,
    BadgeTier.LEGEND: 1.0,
}


async def calculate_trust_score(db: AsyncSession, user_id: UUID) -> float:
    """Calculate composite trust score (0.0 to 1.0).

    Formula:
    - 35% from points (capped at 1000)
    - 40% from weighted review average (1-5 scaled to 0-1)
    - 15% from badge tier (0.0 newcomer to 1.0 legend)
    - 10% from skill verifications (capped at 10)
    """
    # Points component
    points_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user_id)
    )
    points = points_result.scalars().first()
    total_points = points.total_points if points else 0
    points_score = min(total_points / 1000.0, 1.0)

    # Review component
    from src.models.review import BHReview
    review_result = await db.execute(
        select(
            func.sum(BHReview.rating * BHReview.weight),
            func.sum(BHReview.weight),
        )
        .where(BHReview.reviewee_id == user_id)
        .where(BHReview.visible == True)
    )
    row = review_result.one()
    if row[1] and row[1] > 0:
        weighted_avg = row[0] / row[1]  # 1.0 to 5.0
        review_score = (weighted_avg - 1.0) / 4.0  # Scale to 0.0-1.0
    else:
        review_score = 0.0

    # Tier component
    user_result = await db.execute(select(BHUser).where(BHUser.id == user_id))
    user = user_result.scalars().first()
    if not user:
        return 0.0
    tier_score = TIER_VALUES.get(user.badge_tier, 0.0)

    # Skill verifications component
    verified_skills = await db.scalar(
        select(func.coalesce(func.sum(BHUserSkill.verified_by_count), 0))
        .where(BHUserSkill.user_id == user_id)
    ) or 0
    skill_score = min(verified_skills / 10.0, 1.0)

    # Weighted composite
    trust = (
        0.35 * points_score
        + 0.40 * review_score
        + 0.15 * tier_score
        + 0.10 * skill_score
    )
    trust = round(trust, 3)

    # Update user record
    user.trust_score = trust
    return trust
