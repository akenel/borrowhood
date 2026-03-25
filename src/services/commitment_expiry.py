"""Background task: auto-expire stale commitments.

Runs every 5 minutes. Finds COMMITTED rentals past their
commitment_expires_at and sets them to EXPIRED.
Notifies both buyer and seller. Logs reputation hit.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import async_session
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.notification import NotificationType
from src.models.rental import BHRental, RentalStatus
from src.services.notify import create_notification

logger = logging.getLogger("commitment_expiry")

INTERVAL_SECONDS = 300  # 5 minutes


async def expire_stale_commitments():
    """Find and expire all commitments past their deadline."""
    async with async_session() as db:
        now = datetime.now(timezone.utc)

        # Find committed rentals that have expired
        result = await db.execute(
            select(BHRental)
            .options(
                selectinload(BHRental.listing).selectinload(BHListing.item),
                selectinload(BHRental.renter),
            )
            .where(BHRental.status == RentalStatus.COMMITTED)
            .where(BHRental.commitment_expires_at < now)
        )
        expired_rentals = result.scalars().all()

        if not expired_rentals:
            return 0

        count = 0
        for rental in expired_rentals:
            rental.status = RentalStatus.EXPIRED
            item = rental.listing.item if rental.listing else None
            item_name = item.name if item else "Unknown item"
            owner_id = item.owner_id if item else None

            # Notify buyer
            await create_notification(
                db=db,
                user_id=rental.renter_id,
                notification_type=NotificationType.SYSTEM,
                title=f"Your commitment to {item_name} has expired",
                body="The payment window has closed. The listing is available again.",
                link="/orders",
                entity_type="rental",
                entity_id=rental.id,
            )

            # Notify seller
            if owner_id:
                await create_notification(
                    db=db,
                    user_id=owner_id,
                    notification_type=NotificationType.SYSTEM,
                    title=f"Commitment expired on {item_name}",
                    body=f"{rental.renter.display_name} did not complete payment. Listing is available again.",
                    link="/orders",
                    entity_type="rental",
                    entity_id=rental.id,
                )

            count += 1
            logger.info(
                "Expired commitment: rental=%s buyer=%s item=%s",
                rental.id, rental.renter_id, item_name,
            )

        await db.commit()
        if count:
            logger.info("Expired %d stale commitments", count)
        return count


async def run_expiry_loop():
    """Background loop that checks for expired commitments every 5 minutes."""
    logger.info("Commitment expiry loop started (interval=%ds)", INTERVAL_SECONDS)
    while True:
        try:
            await expire_stale_commitments()
        except Exception as e:
            logger.error("Commitment expiry error: %s", e, exc_info=True)
        await asyncio.sleep(INTERVAL_SECONDS)
