"""Deposit API.

Manage security deposits: hold on rental start, release on return, forfeit on dispute.
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
from src.models.deposit import BHDeposit, DepositStatus
from src.models.listing import BHListing
from src.models.item import BHItem
from src.models.notification import NotificationType
from src.models.rental import BHRental
from src.models.user import BHUser
from src.services.notify import create_notification

router = APIRouter(prefix="/api/v1/deposits", tags=["deposits"])


# --- Schemas ---

class DepositOut(BaseModel):
    id: UUID
    rental_id: UUID
    payer_id: UUID
    recipient_id: UUID
    amount: float
    currency: str
    status: DepositStatus
    released_amount: Optional[float] = None
    forfeited_amount: Optional[float] = None
    reason: Optional[str] = None
    payment_ref: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class DepositCreate(BaseModel):
    rental_id: UUID
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    payment_ref: Optional[str] = None


class DepositRelease(BaseModel):
    released_amount: Optional[float] = Field(None, ge=0)
    reason: Optional[str] = None


class DepositForfeit(BaseModel):
    forfeited_amount: Optional[float] = Field(None, ge=0)
    reason: str = Field(..., min_length=5, max_length=500)


# --- Endpoints ---

@router.post("", response_model=DepositOut, status_code=201)
async def hold_deposit(
    dep_in: DepositCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Hold a deposit for a rental (renter pays at pickup)."""
    user = await get_user(db, token)

    # Get rental
    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing))
        .where(BHRental.id == dep_in.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # Must be the renter
    if rental.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Only the renter can pay a deposit")

    # Check no existing deposit
    existing = await db.scalar(
        select(func.count(BHDeposit.id)).where(BHDeposit.rental_id == rental.id)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Deposit already exists for this rental")

    # Get item owner
    item_result = await db.execute(
        select(BHItem).where(BHItem.id == rental.listing.item_id)
    )
    item = item_result.scalars().first()

    deposit = BHDeposit(
        rental_id=rental.id,
        payer_id=user.id,
        recipient_id=item.owner_id,
        amount=dep_in.amount,
        currency=dep_in.currency,
        payment_ref=dep_in.payment_ref,
    )
    db.add(deposit)

    # Notify owner
    await create_notification(
        db=db,
        user_id=item.owner_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Deposit of {dep_in.amount:.2f} {dep_in.currency} received for {item.name}",
        link="/dashboard",
        entity_type="deposit",
        entity_id=rental.id,
    )

    await db.flush()
    await db.commit()

    return DepositOut(
        id=deposit.id,
        rental_id=deposit.rental_id,
        payer_id=deposit.payer_id,
        recipient_id=deposit.recipient_id,
        amount=deposit.amount,
        currency=deposit.currency,
        status=deposit.status,
        payment_ref=deposit.payment_ref,
        created_at=deposit.created_at.isoformat(),
    )


@router.get("", response_model=List[DepositOut])
async def list_deposits(
    status: Optional[DepositStatus] = None,
    limit: int = Query(20, ge=1, le=100),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List deposits for the current user (as payer or recipient)."""
    user = await get_user(db, token)

    query = select(BHDeposit).where(
        (BHDeposit.payer_id == user.id) | (BHDeposit.recipient_id == user.id)
    )
    if status:
        query = query.where(BHDeposit.status == status)
    query = query.order_by(BHDeposit.created_at.desc()).limit(limit)

    result = await db.execute(query)
    deposits = result.scalars().all()

    return [
        DepositOut(
            id=d.id,
            rental_id=d.rental_id,
            payer_id=d.payer_id,
            recipient_id=d.recipient_id,
            amount=d.amount,
            currency=d.currency,
            status=d.status,
            released_amount=d.released_amount,
            forfeited_amount=d.forfeited_amount,
            reason=d.reason,
            payment_ref=d.payment_ref,
            created_at=d.created_at.isoformat(),
        )
        for d in deposits
    ]


@router.patch("/{deposit_id}/release")
async def release_deposit(
    deposit_id: UUID,
    body: DepositRelease,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Release deposit back to renter (owner action after successful return)."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHDeposit).where(BHDeposit.id == deposit_id)
    )
    deposit = result.scalars().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    if deposit.status != DepositStatus.HELD:
        raise HTTPException(status_code=400, detail="Deposit is not in HELD status")
    if deposit.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can release a deposit")

    released = body.released_amount if body.released_amount is not None else deposit.amount

    if released > deposit.amount:
        raise HTTPException(status_code=400, detail="Cannot release more than the deposit amount")

    deposit.released_amount = released
    deposit.reason = body.reason

    if released == deposit.amount:
        deposit.status = DepositStatus.RELEASED
    else:
        deposit.status = DepositStatus.PARTIAL_RELEASE
        deposit.forfeited_amount = deposit.amount - released

    # Notify renter
    await create_notification(
        db=db,
        user_id=deposit.payer_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Your deposit of {released:.2f} {deposit.currency} has been released",
        link="/dashboard",
        entity_type="deposit",
        entity_id=deposit.rental_id,
    )

    await db.commit()
    return {"status": deposit.status.value, "released": released, "forfeited": deposit.forfeited_amount or 0}


@router.patch("/{deposit_id}/forfeit")
async def forfeit_deposit(
    deposit_id: UUID,
    body: DepositForfeit,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Forfeit deposit (owner keeps it due to damage/loss)."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHDeposit).where(BHDeposit.id == deposit_id)
    )
    deposit = result.scalars().first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    if deposit.status != DepositStatus.HELD:
        raise HTTPException(status_code=400, detail="Deposit is not in HELD status")
    if deposit.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can forfeit a deposit")

    forfeited = body.forfeited_amount if body.forfeited_amount is not None else deposit.amount

    if forfeited > deposit.amount:
        raise HTTPException(status_code=400, detail="Cannot forfeit more than the deposit amount")

    deposit.forfeited_amount = forfeited
    deposit.reason = body.reason
    deposit.status = DepositStatus.FORFEITED

    if forfeited < deposit.amount:
        deposit.released_amount = deposit.amount - forfeited
        deposit.status = DepositStatus.PARTIAL_RELEASE

    # Notify renter
    await create_notification(
        db=db,
        user_id=deposit.payer_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Your deposit of {forfeited:.2f} {deposit.currency} has been forfeited",
        body=body.reason,
        link="/dashboard",
        entity_type="deposit",
        entity_id=deposit.rental_id,
    )

    await db.commit()
    return {"status": deposit.status.value, "forfeited": forfeited, "released": deposit.released_amount or 0}
