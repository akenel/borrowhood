"""Feedback reward engine.

Awards points + badges to the user who reported a backlog item once
it transitions to DONE. Idempotent via BHBacklogItem.reporter_rewarded_at.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.backlog import BHBacklogItem, BacklogItemType, BacklogStatus
from src.models.badge import BadgeCode
from src.models.notification import NotificationType
from src.services.badges import _award_badge
from src.services.notify import create_notification
from src.services.reputation import award_points

logger = logging.getLogger(__name__)

# Points per feedback type
_POINTS_BY_TYPE = {
    BacklogItemType.BUG_FIX: 10,
    BacklogItemType.FEATURE: 25,
    BacklogItemType.IMPROVEMENT: 15,
}

# Badge thresholds by confirmed-fix count
_BADGE_MILESTONES = [
    (1, BadgeCode.BUG_SPOTTER),
    (10, BadgeCode.QUALITY_GUARDIAN),
    (25, BadgeCode.CODE_WHISPERER),
]


async def reward_reporter_on_done(db: AsyncSession, item: BHBacklogItem) -> None:
    """Award points + notify + check badges for the item's reporter.

    Safe to call multiple times -- reporter_rewarded_at gates re-award.
    Silently no-ops if no reporter_user_id.
    """
    if not item.reporter_user_id:
        return
    if item.reporter_rewarded_at is not None:
        return
    if item.status != BacklogStatus.DONE:
        return

    user_id: UUID = item.reporter_user_id
    points = _POINTS_BY_TYPE.get(item.item_type, 10)

    try:
        await award_points(db, user_id, points, reason="feedback_fixed")
    except Exception as exc:
        logger.exception("award_points failed for user %s: %s", user_id, exc)
        return

    item.reporter_rewarded_at = datetime.now(timezone.utc)

    # Count lifetime confirmed fixes for this user to check badge tiers.
    confirmed = await db.scalar(
        select(func.count(BHBacklogItem.id))
        .where(BHBacklogItem.reporter_user_id == user_id)
        .where(BHBacklogItem.reporter_rewarded_at.isnot(None))
    ) or 0

    for threshold, code in _BADGE_MILESTONES:
        if confirmed >= threshold:
            await _award_badge(
                db, user_id, code,
                reason=f"{confirmed} confirmed feedback fixes",
            )

    # Neighbour-facing notification: thanks + points
    # Framed as a shipped contribution, not a fixed complaint.
    body = f"BL-{item.item_number:03d} '{item.title[:60]}' is live."
    if item.resolution_sha:
        body += f" Shipped in commit {item.resolution_sha[:7]}."
    body += " Neighbors like you keep La Piazza sharp. Grazie."

    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.BADGE_EARNED,
        title=f"Your contribution shipped: +{points} points",
        body=body,
        link=f"/backlog#BL-{item.item_number}",
        entity_type="backlog_item",
        entity_id=item.id,
    )

    logger.info(
        "Feedback reward: user=%s +%d points (BL-%d) confirmed_total=%d",
        user_id, points, item.item_number, confirmed,
    )
