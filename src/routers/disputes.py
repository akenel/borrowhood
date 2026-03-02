"""Dispute resolution API.

3-step process:
1. File a dispute (either party on a rental)
2. Other party responds
3. Resolution applied (by owner or admin)
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.dispute import BHDispute, DisputeReason, DisputeResolution, DisputeStatus
from src.models.notification import NotificationType
from src.models.rental import BHRental, RentalStatus
from src.models.user import BHUser
from src.services.notify import create_notification

router = APIRouter(prefix="/api/v1/disputes", tags=["disputes"])


# --- Schemas ---

class DisputeOut(BaseModel):
    id: UUID
    rental_id: UUID
    filed_by_id: UUID
    status: DisputeStatus
    reason: DisputeReason
    description: str
    evidence_urls: Optional[str] = None
    response: Optional[str] = None
    response_by_id: Optional[UUID] = None
    resolution: Optional[DisputeResolution] = None
    resolution_notes: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class DisputeCreate(BaseModel):
    rental_id: UUID
    reason: DisputeReason
    description: str = Field(..., min_length=10, max_length=2000)
    evidence_urls: Optional[str] = None


class DisputeRespond(BaseModel):
    response: str = Field(..., min_length=10, max_length=2000)


class DisputeResolve(BaseModel):
    resolution: DisputeResolution
    resolution_notes: Optional[str] = Field(None, max_length=2000)


class DisputeSummary(BaseModel):
    total: int
    filed: int
    under_review: int
    resolved: int


# --- Endpoints ---

@router.post("", response_model=DisputeOut, status_code=201)
async def file_dispute(
    dispute_in: DisputeCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """File a dispute on a rental. Either the renter or item owner can file."""
    user = await get_user(db, token)

    # Get rental with listing + item
    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing))
        .where(BHRental.id == dispute_in.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # Get item owner
    from src.models.item import BHItem
    item_result = await db.execute(
        select(BHItem).where(BHItem.id == rental.listing.item_id)
    )
    item = item_result.scalars().first()

    # Must be renter or owner
    is_renter = rental.renter_id == user.id
    is_owner = item and item.owner_id == user.id
    if not is_renter and not is_owner:
        raise HTTPException(status_code=403, detail="Only rental parties can file disputes")

    # Check rental is in a disputable state
    disputable = [RentalStatus.APPROVED, RentalStatus.PICKED_UP, RentalStatus.RETURNED, RentalStatus.DISPUTED]
    if rental.status not in disputable:
        raise HTTPException(status_code=400, detail=f"Cannot dispute a rental in {rental.status.value} status")

    # Check for existing active dispute
    existing = await db.scalar(
        select(func.count(BHDispute.id))
        .where(BHDispute.rental_id == rental.id)
        .where(BHDispute.status.in_([DisputeStatus.FILED, DisputeStatus.UNDER_REVIEW]))
    )
    if existing:
        raise HTTPException(status_code=409, detail="An active dispute already exists for this rental")

    # Update rental status
    rental.status = RentalStatus.DISPUTED

    # Create dispute
    dispute = BHDispute(
        rental_id=rental.id,
        filed_by_id=user.id,
        reason=dispute_in.reason,
        description=dispute_in.description,
        evidence_urls=dispute_in.evidence_urls,
    )
    db.add(dispute)

    # Notify the other party
    other_party_id = item.owner_id if is_renter else rental.renter_id
    await create_notification(
        db=db,
        user_id=other_party_id,
        notification_type=NotificationType.DISPUTE_FILED,
        title=f"A dispute has been filed on rental of {item.name}",
        body=f"Reason: {dispute_in.reason.value.replace('_', ' ').title()}",
        link="/dashboard",
        entity_type="dispute",
        entity_id=rental.id,
    )

    await db.flush()
    await db.commit()

    return DisputeOut(
        id=dispute.id,
        rental_id=dispute.rental_id,
        filed_by_id=dispute.filed_by_id,
        status=dispute.status,
        reason=dispute.reason,
        description=dispute.description,
        evidence_urls=dispute.evidence_urls,
        created_at=dispute.created_at.isoformat(),
    )


@router.get("", response_model=List[DisputeOut])
async def list_disputes(
    status: Optional[DisputeStatus] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List disputes involving the authenticated user."""
    user = await get_user(db, token)

    # Get rental IDs where user is renter
    renter_rentals = select(BHRental.id).where(BHRental.renter_id == user.id)

    # Get rental IDs where user is owner (through item)
    from src.models.item import BHItem
    from src.models.listing import BHListing
    owner_rentals = (
        select(BHRental.id)
        .join(BHListing, BHRental.listing_id == BHListing.id)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user.id)
    )

    query = (
        select(BHDispute)
        .where(
            (BHDispute.rental_id.in_(renter_rentals)) |
            (BHDispute.rental_id.in_(owner_rentals))
        )
    )

    if status:
        query = query.where(BHDispute.status == status)

    query = query.order_by(BHDispute.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    disputes = result.scalars().all()

    return [
        DisputeOut(
            id=d.id,
            rental_id=d.rental_id,
            filed_by_id=d.filed_by_id,
            status=d.status,
            reason=d.reason,
            description=d.description,
            evidence_urls=d.evidence_urls,
            response=d.response,
            response_by_id=d.response_by_id,
            resolution=d.resolution,
            resolution_notes=d.resolution_notes,
            created_at=d.created_at.isoformat(),
        )
        for d in disputes
    ]


@router.get("/summary", response_model=DisputeSummary)
async def dispute_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get dispute counts for the current user."""
    user = await get_user(db, token)

    # All disputes filed by user
    filed_by_user = select(BHDispute.id).where(BHDispute.filed_by_id == user.id)
    total = await db.scalar(select(func.count()).select_from(filed_by_user.subquery())) or 0

    filed = await db.scalar(
        select(func.count(BHDispute.id))
        .where(BHDispute.filed_by_id == user.id)
        .where(BHDispute.status == DisputeStatus.FILED)
    ) or 0

    under_review = await db.scalar(
        select(func.count(BHDispute.id))
        .where(BHDispute.filed_by_id == user.id)
        .where(BHDispute.status == DisputeStatus.UNDER_REVIEW)
    ) or 0

    resolved = await db.scalar(
        select(func.count(BHDispute.id))
        .where(BHDispute.filed_by_id == user.id)
        .where(BHDispute.status == DisputeStatus.RESOLVED)
    ) or 0

    return DisputeSummary(total=total, filed=filed, under_review=under_review, resolved=resolved)


@router.patch("/{dispute_id}/respond")
async def respond_to_dispute(
    dispute_id: UUID,
    body: DisputeRespond,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """The other party responds to a dispute (step 2)."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHDispute)
        .options(selectinload(BHDispute.rental))
        .where(BHDispute.id == dispute_id)
    )
    dispute = result.scalars().first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    if dispute.status != DisputeStatus.FILED:
        raise HTTPException(status_code=400, detail="Dispute is not in FILED status")

    # Must not be the filer
    if dispute.filed_by_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot respond to your own dispute")

    dispute.response = body.response
    dispute.response_by_id = user.id
    dispute.status = DisputeStatus.UNDER_REVIEW

    # Notify the filer
    await create_notification(
        db=db,
        user_id=dispute.filed_by_id,
        notification_type=NotificationType.DISPUTE_FILED,
        title="The other party has responded to your dispute",
        link="/dashboard",
        entity_type="dispute",
        entity_id=dispute.rental_id,
    )

    await db.commit()
    return {"status": "ok", "dispute_status": "under_review"}


@router.patch("/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: UUID,
    body: DisputeResolve,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Resolve a dispute (step 3). Owner or admin applies resolution."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHDispute)
        .options(selectinload(BHDispute.rental))
        .where(BHDispute.id == dispute_id)
    )
    dispute = result.scalars().first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    if dispute.status not in (DisputeStatus.FILED, DisputeStatus.UNDER_REVIEW):
        raise HTTPException(status_code=400, detail="Dispute is already resolved")

    # Apply resolution
    dispute.resolution = body.resolution
    dispute.resolution_notes = body.resolution_notes
    dispute.resolved_by_id = user.id
    dispute.status = DisputeStatus.RESOLVED

    # Update rental status based on resolution
    rental = dispute.rental
    if body.resolution in (DisputeResolution.FULL_REFUND, DisputeResolution.NO_ACTION):
        rental.status = RentalStatus.CANCELLED
    else:
        rental.status = RentalStatus.COMPLETED

    # Apply deposit action based on resolution
    from src.models.deposit import BHDeposit, DepositStatus
    dep_result = await db.execute(
        select(BHDeposit)
        .where(BHDeposit.rental_id == rental.id)
        .where(BHDeposit.status == DepositStatus.HELD)
    )
    deposit = dep_result.scalars().first()
    if deposit:
        if body.resolution in (DisputeResolution.DEPOSIT_FORFEITED,):
            deposit.status = DepositStatus.FORFEITED
            deposit.forfeited_amount = deposit.amount
            deposit.reason = body.resolution_notes or "Forfeited via dispute resolution"
        elif body.resolution in (
            DisputeResolution.DEPOSIT_RETURNED,
            DisputeResolution.FULL_REFUND,
        ):
            deposit.status = DepositStatus.RELEASED
            deposit.released_amount = deposit.amount
            deposit.reason = body.resolution_notes or "Released via dispute resolution"
        elif body.resolution == DisputeResolution.PARTIAL_REFUND:
            # Partial refund: release deposit back to renter (benefit of doubt)
            deposit.status = DepositStatus.RELEASED
            deposit.released_amount = deposit.amount
            deposit.reason = body.resolution_notes or "Released via partial refund resolution"

    # Notify both parties
    renter_id = rental.renter_id
    filer_id = dispute.filed_by_id

    for notify_user_id in {renter_id, filer_id}:
        await create_notification(
            db=db,
            user_id=notify_user_id,
            notification_type=NotificationType.DISPUTE_RESOLVED,
            title=f"Dispute resolved: {body.resolution.value.replace('_', ' ').title()}",
            body=body.resolution_notes,
            link="/dashboard",
            entity_type="dispute",
            entity_id=rental.id,
        )

    await db.commit()
    return {"status": "resolved", "resolution": body.resolution.value}
