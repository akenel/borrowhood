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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import BadgeTier, BHUser, BHUserPoints


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

    await db.flush()
    return user_points
