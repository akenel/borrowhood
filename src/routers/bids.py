"""Auction bid API.

Place bids on AUCTION-type listings, view bid history, and get auction summaries.
Includes automatic outbid notifications and auction-end resolution.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import require_auth
from src.models.bid import BHBid, BidStatus
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.user import BHUser
from src.models.notification import NotificationType
from src.schemas.bid import AuctionSummary, BidCreate, BidOut
from src.services.notify import create_notification

router = APIRouter(prefix="/api/v1/bids", tags=["bids"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")
    return user


@router.post("", response_model=BidOut, status_code=201)
async def place_bid(
    bid_in: BidCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Place a bid on an auction listing.

    Validates:
    - Listing exists, is AUCTION type, and is ACTIVE
    - Auction hasn't ended
    - Bid meets minimum (starting_bid or current highest + increment)
    - Bidder is not the item owner
    """
    user = await _get_user(db, token["sub"])

    # Get listing with item for owner check
    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == bid_in.listing_id)
    )
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.listing_type != ListingType.AUCTION:
        raise HTTPException(status_code=400, detail="Listing is not an auction")
    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Auction is not active")

    # Check auction end time
    if listing.auction_end and datetime.now(timezone.utc) > listing.auction_end:
        raise HTTPException(status_code=400, detail="Auction has ended")

    # Can't bid on your own item
    if listing.item.owner_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot bid on your own item")

    # Get current highest bid
    current_highest = await db.scalar(
        select(func.max(BHBid.amount))
        .where(BHBid.listing_id == listing.id)
        .where(BHBid.status == BidStatus.ACTIVE)
    )

    # Calculate minimum bid
    if current_highest:
        min_bid = current_highest + (listing.bid_increment or 1.0)
    else:
        min_bid = listing.starting_bid or 0.01

    if bid_in.amount < min_bid:
        raise HTTPException(
            status_code=400,
            detail=f"Bid must be at least {min_bid:.2f} {listing.currency}"
        )

    # Mark previous winning bid as outbid
    prev_winner_result = await db.execute(
        select(BHBid)
        .where(BHBid.listing_id == listing.id)
        .where(BHBid.is_winning == True)
    )
    prev_winner = prev_winner_result.scalars().first()

    if prev_winner:
        prev_winner.is_winning = False
        prev_winner.status = BidStatus.OUTBID

        # Notify previous winning bidder they've been outbid
        await create_notification(
            db=db,
            user_id=prev_winner.bidder_id,
            notification_type=NotificationType.BID_OUTBID,
            title=f"You've been outbid on {listing.item.name}",
            body=f"New bid: {bid_in.amount:.2f} {listing.currency}",
            link=f"/items/{listing.item.slug}",
            entity_type="bid",
            entity_id=listing.id,
        )

    # Create the bid
    bid = BHBid(
        listing_id=listing.id,
        bidder_id=user.id,
        amount=bid_in.amount,
        currency=listing.currency,
        status=BidStatus.ACTIVE,
        is_winning=True,
    )
    db.add(bid)

    # Notify item owner of new bid
    await create_notification(
        db=db,
        user_id=listing.item.owner_id,
        notification_type=NotificationType.BID_PLACED,
        title=f"New bid on {listing.item.name}: {bid_in.amount:.2f} {listing.currency}",
        link=f"/items/{listing.item.slug}",
        entity_type="bid",
        entity_id=listing.id,
    )

    await db.flush()
    await db.commit()

    return BidOut(
        id=bid.id,
        listing_id=bid.listing_id,
        bidder_id=bid.bidder_id,
        amount=bid.amount,
        currency=bid.currency,
        status=bid.status,
        is_winning=bid.is_winning,
        created_at=bid.created_at.isoformat(),
    )


@router.get("", response_model=List[BidOut])
async def list_bids(
    listing_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List bids for an auction listing, newest first."""
    result = await db.execute(
        select(BHBid)
        .where(BHBid.listing_id == listing_id)
        .order_by(BHBid.amount.desc())
        .limit(limit)
    )
    bids = result.scalars().all()

    return [
        BidOut(
            id=b.id,
            listing_id=b.listing_id,
            bidder_id=b.bidder_id,
            amount=b.amount,
            currency=b.currency,
            status=b.status,
            is_winning=b.is_winning,
            created_at=b.created_at.isoformat(),
        )
        for b in bids
    ]


@router.get("/summary", response_model=AuctionSummary)
async def auction_summary(
    listing_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get auction summary: total bids, current price, winning bidder. Public endpoint."""
    result = await db.execute(
        select(BHListing).where(BHListing.id == listing_id)
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.listing_type != ListingType.AUCTION:
        raise HTTPException(status_code=400, detail="Listing is not an auction")

    total_bids = await db.scalar(
        select(func.count(BHBid.id)).where(BHBid.listing_id == listing_id)
    ) or 0

    # Get winning bid
    winner_result = await db.execute(
        select(BHBid)
        .where(BHBid.listing_id == listing_id)
        .where(BHBid.is_winning == True)
    )
    winner = winner_result.scalars().first()

    current_price = winner.amount if winner else listing.starting_bid
    reserve_met = True
    if listing.reserve_price and current_price:
        reserve_met = current_price >= listing.reserve_price

    return AuctionSummary(
        listing_id=listing_id,
        total_bids=total_bids,
        current_price=current_price,
        winning_bidder_id=winner.bidder_id if winner else None,
        auction_end=listing.auction_end.isoformat() if listing.auction_end else None,
        reserve_met=reserve_met,
    )


@router.post("/{listing_id}/end")
async def end_auction(
    listing_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """End an auction manually (owner only) or called by timer.

    - Marks listing as EXPIRED
    - If reserve met: winning bid status = WON, notifications sent
    - If reserve not met: all bids marked RESERVE_NOT_MET
    """
    user = await _get_user(db, token["sub"])

    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == listing_id)
    )
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.listing_type != ListingType.AUCTION:
        raise HTTPException(status_code=400, detail="Listing is not an auction")
    if listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the item owner can end the auction")
    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Auction is not active")

    # Mark listing as expired
    listing.status = ListingStatus.EXPIRED

    # Get winning bid
    winner_result = await db.execute(
        select(BHBid)
        .where(BHBid.listing_id == listing_id)
        .where(BHBid.is_winning == True)
    )
    winner = winner_result.scalars().first()

    if winner:
        reserve_met = True
        if listing.reserve_price:
            reserve_met = winner.amount >= listing.reserve_price

        if reserve_met:
            winner.status = BidStatus.WON

            # Notify winner
            await create_notification(
                db=db,
                user_id=winner.bidder_id,
                notification_type=NotificationType.AUCTION_WON,
                title=f"You won the auction for {listing.item.name}!",
                body=f"Winning bid: {winner.amount:.2f} {listing.currency}",
                link=f"/items/{listing.item.slug}",
                entity_type="bid",
                entity_id=listing.id,
            )
        else:
            # Reserve not met -- mark all bids
            await db.execute(
                update(BHBid)
                .where(BHBid.listing_id == listing_id)
                .values(status=BidStatus.RESERVE_NOT_MET, is_winning=False)
            )

    # Notify owner
    await create_notification(
        db=db,
        user_id=user.id,
        notification_type=NotificationType.AUCTION_ENDED,
        title=f"Your auction for {listing.item.name} has ended",
        body=f"Total bids: {await db.scalar(select(func.count(BHBid.id)).where(BHBid.listing_id == listing_id)) or 0}",
        link=f"/items/{listing.item.slug}",
        entity_type="bid",
        entity_id=listing.id,
    )

    await db.commit()

    return {
        "status": "ended",
        "winner_id": str(winner.bidder_id) if winner and winner.status == BidStatus.WON else None,
        "winning_amount": winner.amount if winner and winner.status == BidStatus.WON else None,
        "reserve_met": winner.status == BidStatus.WON if winner else False,
    }
