"""Lock box access code API.

Contactless item exchange: owner generates codes, renter uses them.
No need for both parties to be present at the same time.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.listing import BHListing
from src.models.lockbox import BHLockBoxAccess
from src.models.notification import NotificationType
from src.models.rental import BHRental, RentalStatus
from src.models.user import BHUser
from src.services.lockbox import generate_unique_codes
from src.services.notify import create_notification

router = APIRouter(prefix="/api/v1/lockbox", tags=["lockbox"])


async def _get_rental_with_auth(
    db: AsyncSession, rental_id: UUID, user: BHUser
) -> BHRental:
    """Load rental with listing+item, verify user is owner or renter."""
    result = await db.execute(
        select(BHRental)
        .options(
            selectinload(BHRental.listing).selectinload(BHListing.item),
            selectinload(BHRental.lockbox),
        )
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    is_renter = rental.renter_id == user.id
    is_owner = rental.listing and rental.listing.item and rental.listing.item.owner_id == user.id
    if not (is_renter or is_owner):
        raise HTTPException(status_code=403, detail="Not your rental")

    return rental


# --- Schemas ---

class GenerateCodesRequest(BaseModel):
    location_hint: Optional[str] = Field(None, max_length=500)
    instructions: Optional[str] = Field(None, max_length=2000)


class LockBoxOut(BaseModel):
    id: UUID
    rental_id: UUID
    pickup_code: str
    return_code: str
    pickup_used_at: Optional[str] = None
    return_used_at: Optional[str] = None
    location_hint: Optional[str] = None
    instructions: Optional[str] = None

    class Config:
        from_attributes = True


class CodeVerifyRequest(BaseModel):
    code: str = Field(..., min_length=8, max_length=8)


class CodeVerifyResponse(BaseModel):
    valid: bool
    action: str  # "pickup" or "return"
    message: str


# --- Endpoints ---

@router.post("/{rental_id}/generate", response_model=LockBoxOut, status_code=201)
async def generate_codes(
    rental_id: UUID,
    data: GenerateCodesRequest = GenerateCodesRequest(),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate lock box access codes. Owner only. Rental must be APPROVED."""
    user = await get_user(db, token)
    rental = await _get_rental_with_auth(db, rental_id, user)

    # Only owner can generate codes
    if rental.listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the item owner can generate codes")

    # Must be approved
    if rental.status != RentalStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Rental must be approved to generate codes")

    # Check if codes already exist
    if rental.lockbox:
        raise HTTPException(status_code=409, detail="Codes already generated for this rental")

    # Generate unique codes
    pickup_code, return_code = await generate_unique_codes(db)

    lockbox = BHLockBoxAccess(
        rental_id=rental.id,
        pickup_code=pickup_code,
        return_code=return_code,
        location_hint=data.location_hint,
        instructions=data.instructions,
    )
    db.add(lockbox)

    # Notify renter that codes are ready
    await create_notification(
        db=db,
        user_id=rental.renter_id,
        notification_type=NotificationType.LOCKBOX_CODES_READY,
        title=f"Pickup code ready for {rental.listing.item.name}",
        body=f"Code: {pickup_code}" + (f" | {data.location_hint}" if data.location_hint else ""),
        link="/orders",
        entity_type="rental",
        entity_id=rental.id,
    )

    await db.commit()
    await db.refresh(lockbox)
    return lockbox


@router.get("/{rental_id}")
async def get_codes(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get lock box codes for a rental. Owner or renter. Returns null if none exist."""
    user = await get_user(db, token)
    rental = await _get_rental_with_auth(db, rental_id, user)

    if not rental.lockbox:
        return None

    return rental.lockbox


@router.post("/{rental_id}/verify", response_model=CodeVerifyResponse)
async def verify_code(
    rental_id: UUID,
    data: CodeVerifyRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Verify and use a lock box code. Marks the corresponding action as done.

    - Pickup code: transitions rental to PICKED_UP
    - Return code: transitions rental to RETURNED
    """
    user = await get_user(db, token)
    rental = await _get_rental_with_auth(db, rental_id, user)

    if not rental.lockbox:
        raise HTTPException(status_code=404, detail="No lock box codes for this rental")

    lockbox = rental.lockbox
    code = data.code.upper().strip()

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    # Check pickup code
    if code == lockbox.pickup_code:
        if lockbox.pickup_used_at:
            raise HTTPException(status_code=400, detail="Pickup code already used")
        if rental.status != RentalStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Rental must be approved for pickup")

        lockbox.pickup_used_at = now
        rental.status = RentalStatus.PICKED_UP
        rental.actual_pickup = now

        # Notify owner
        await create_notification(
            db=db,
            user_id=rental.listing.item.owner_id,
            notification_type=NotificationType.LOCKBOX_PICKUP_CONFIRMED,
            title=f"{rental.listing.item.name} has been picked up",
            body="Renter confirmed pickup using lock box code.",
            link="/orders",
            entity_type="rental",
            entity_id=rental.id,
        )

        await db.commit()
        return CodeVerifyResponse(valid=True, action="pickup", message="Pickup confirmed! Enjoy the item.")

    # Check return code
    if code == lockbox.return_code:
        if lockbox.return_used_at:
            raise HTTPException(status_code=400, detail="Return code already used")
        if rental.status != RentalStatus.PICKED_UP:
            raise HTTPException(status_code=400, detail="Item must be picked up before returning")

        lockbox.return_used_at = now
        rental.status = RentalStatus.RETURNED
        rental.actual_return = now

        # Notify owner
        await create_notification(
            db=db,
            user_id=rental.listing.item.owner_id,
            notification_type=NotificationType.LOCKBOX_RETURN_CONFIRMED,
            title=f"{rental.listing.item.name} has been returned",
            body="Renter confirmed return using lock box code.",
            link="/orders",
            entity_type="rental",
            entity_id=rental.id,
        )

        await db.commit()
        return CodeVerifyResponse(valid=True, action="return", message="Return confirmed! Thanks for returning it.")

    # Invalid code
    raise HTTPException(status_code=400, detail="Invalid code")
