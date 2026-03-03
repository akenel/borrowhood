"""Badge awarding service.

Checks user milestones and awards badges. Idempotent -- safe to call repeatedly.
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.badge import BHBadge, BadgeCode, BADGE_INFO
from src.models.item import BHItem
from src.models.listing import BHListing, ListingType
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview
from src.models.bid import BHBid, BidStatus
from src.models.user import BHUser, BHUserLanguage, BHUserSkill, BHUserPoints, BadgeTier
from src.models.notification import NotificationType
from src.services.notify import create_notification

logger = logging.getLogger(__name__)


async def _has_badge(db: AsyncSession, user_id: UUID, code: BadgeCode) -> bool:
    """Check if user already has a specific badge."""
    result = await db.scalar(
        select(func.count(BHBadge.id))
        .where(BHBadge.user_id == user_id)
        .where(BHBadge.badge_code == code)
    )
    return (result or 0) > 0


async def _award_badge(
    db: AsyncSession, user_id: UUID, code: BadgeCode, reason: str = ""
) -> Optional[BHBadge]:
    """Award a badge if not already earned. Returns badge or None."""
    if await _has_badge(db, user_id, code):
        return None

    badge = BHBadge(user_id=user_id, badge_code=code, reason=reason)
    db.add(badge)

    info = BADGE_INFO.get(code, {})
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.BADGE_EARNED,
        title=f"Badge earned: {info.get('name', code.value)}",
        body=info.get("description", ""),
        link="/profile",
        entity_type="badge",
    )

    logger.info("Badge awarded: %s -> %s", code.value, user_id)
    return badge


async def _update_badge_tier(db: AsyncSession, user_id: UUID):
    """Recalculate badge tier from total points."""
    points_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user_id)
    )
    points = points_result.scalars().first()
    if not points:
        return

    total = points.total_points
    if total >= 1000:
        new_tier = BadgeTier.LEGEND
    elif total >= 500:
        new_tier = BadgeTier.PILLAR
    elif total >= 200:
        new_tier = BadgeTier.TRUSTED
    elif total >= 50:
        new_tier = BadgeTier.ACTIVE
    else:
        new_tier = BadgeTier.NEWCOMER

    user_result = await db.execute(select(BHUser).where(BHUser.id == user_id))
    user = user_result.scalars().first()
    if user and user.badge_tier != new_tier:
        user.badge_tier = new_tier


async def check_and_award_badges(db: AsyncSession, user_id: UUID) -> List[BHBadge]:
    """Run all badge checks for a user. Returns list of newly awarded badges."""
    awarded = []

    # First Listing
    item_count = await db.scalar(
        select(func.count(BHItem.id))
        .where(BHItem.owner_id == user_id)
        .where(BHItem.deleted_at.is_(None))
    ) or 0
    if item_count >= 1:
        b = await _award_badge(db, user_id, BadgeCode.FIRST_LISTING, f"{item_count} items")
        if b:
            awarded.append(b)

    # Super Lender (10+ items)
    if item_count >= 10:
        b = await _award_badge(db, user_id, BadgeCode.SUPER_LENDER, f"{item_count} items listed")
        if b:
            awarded.append(b)

    # First Rental (as renter)
    rentals_as_renter = await db.scalar(
        select(func.count(BHRental.id))
        .where(BHRental.renter_id == user_id)
        .where(BHRental.status == RentalStatus.COMPLETED)
    ) or 0
    if rentals_as_renter >= 1:
        b = await _award_badge(db, user_id, BadgeCode.FIRST_RENTAL)
        if b:
            awarded.append(b)

    # Trusted Renter (5+ completed)
    if rentals_as_renter >= 5:
        b = await _award_badge(db, user_id, BadgeCode.TRUSTED_RENTER, f"{rentals_as_renter} rentals")
        if b:
            awarded.append(b)

    # First Review given
    reviews_given = await db.scalar(
        select(func.count(BHReview.id)).where(BHReview.reviewer_id == user_id)
    ) or 0
    if reviews_given >= 1:
        b = await _award_badge(db, user_id, BadgeCode.FIRST_REVIEW)
        if b:
            awarded.append(b)

    # Community Voice (10+ reviews)
    if reviews_given >= 10:
        b = await _award_badge(db, user_id, BadgeCode.COMMUNITY_VOICE, f"{reviews_given} reviews")
        if b:
            awarded.append(b)

    # Five Star (received a 5-star review)
    five_star_count = await db.scalar(
        select(func.count(BHReview.id))
        .where(BHReview.reviewee_id == user_id)
        .where(BHReview.rating == 5)
    ) or 0
    if five_star_count >= 1:
        b = await _award_badge(db, user_id, BadgeCode.FIVE_STAR)
        if b:
            awarded.append(b)

    # Multilingual (3+ languages)
    lang_count = await db.scalar(
        select(func.count(BHUserLanguage.id)).where(BHUserLanguage.user_id == user_id)
    ) or 0
    if lang_count >= 3:
        b = await _award_badge(db, user_id, BadgeCode.MULTILINGUAL, f"{lang_count} languages")
        if b:
            awarded.append(b)

    # Skill Master (5+ skills)
    skill_count = await db.scalar(
        select(func.count(BHUserSkill.id)).where(BHUserSkill.user_id == user_id)
    ) or 0
    if skill_count >= 5:
        b = await _award_badge(db, user_id, BadgeCode.SKILL_MASTER, f"{skill_count} skills")
        if b:
            awarded.append(b)

    # Auction Winner
    auction_wins = await db.scalar(
        select(func.count(BHBid.id))
        .where(BHBid.bidder_id == user_id)
        .where(BHBid.status == BidStatus.WON)
    ) or 0
    if auction_wins >= 1:
        b = await _award_badge(db, user_id, BadgeCode.AUCTION_WINNER)
        if b:
            awarded.append(b)

    # Workshop Pro (complete profile)
    user_result = await db.execute(select(BHUser).where(BHUser.id == user_id))
    user = user_result.scalars().first()
    if user and user.bio and user.workshop_name and user.tagline:
        b = await _award_badge(db, user_id, BadgeCode.WORKSHOP_PRO)
        if b:
            awarded.append(b)

    # Neighborhood Hero (50+ total transactions)
    total_rentals = rentals_as_renter
    rentals_as_owner = await db.scalar(
        select(func.count(BHRental.id))
        .join(BHListing)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user_id)
        .where(BHRental.status == RentalStatus.COMPLETED)
    ) or 0
    if (total_rentals + rentals_as_owner) >= 50:
        b = await _award_badge(db, user_id, BadgeCode.NEIGHBORHOOD_HERO)
        if b:
            awarded.append(b)

    # Generous Neighbor (3+ giveaways completed as owner)
    giveaways_completed = await db.scalar(
        select(func.count(BHRental.id))
        .join(BHListing)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user_id)
        .where(BHRental.status == RentalStatus.COMPLETED)
        .where(BHListing.listing_type == ListingType.GIVEAWAY)
    ) or 0
    if giveaways_completed >= 3:
        b = await _award_badge(db, user_id, BadgeCode.GENEROUS_NEIGHBOR, f"{giveaways_completed} giveaways")
        if b:
            awarded.append(b)

    # Originator: first person to list an item in a category
    if not await _has_badge(db, user_id, BadgeCode.ORIGINATOR):
        # Get categories this user has items in
        user_items = await db.execute(
            select(BHItem.category)
            .where(BHItem.owner_id == user_id)
            .where(BHItem.deleted_at.is_(None))
            .distinct()
        )
        user_categories = [row[0] for row in user_items.all()]

        for cat in user_categories:
            # Find the earliest item in this category
            earliest = await db.execute(
                select(BHItem.owner_id)
                .where(BHItem.category == cat)
                .where(BHItem.deleted_at.is_(None))
                .order_by(BHItem.created_at.asc())
                .limit(1)
            )
            first_owner = earliest.scalar()
            if first_owner == user_id:
                b = await _award_badge(db, user_id, BadgeCode.ORIGINATOR, f"First in {cat}")
                if b:
                    awarded.append(b)
                break  # One originator badge per user

    # Update points and tier
    await _update_points(db, user_id, item_count, rentals_as_renter, reviews_given, five_star_count, giveaways_completed)
    await _update_badge_tier(db, user_id)

    return awarded


async def _update_points(
    db: AsyncSession, user_id: UUID,
    items: int, rentals: int, reviews_given: int, five_stars: int,
    giveaways: int = 0
):
    """Update user points based on current stats."""
    result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user_id)
    )
    points = result.scalars().first()
    if not points:
        points = BHUserPoints(user_id=user_id)
        db.add(points)

    points.items_listed = items
    points.rentals_completed = rentals
    points.reviews_given = reviews_given
    points.reviews_received = five_stars  # approximate
    points.giveaways_completed = giveaways

    # Point calculation: items*10 + rentals*20 + giveaways*25 + reviews*5 + five_stars*15
    points.total_points = (items * 10) + (rentals * 20) + (giveaways * 25) + (reviews_given * 5) + (five_stars * 15)
