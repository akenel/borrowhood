"""Service quoting API.

Workflow: customer requests quote on a service listing -> provider sends
pricing -> customer accepts/declines -> work proceeds -> completion.

Routes:
  POST   /api/v1/service-quotes              - Request a quote
  GET    /api/v1/service-quotes              - List quotes (as customer or provider)
  GET    /api/v1/service-quotes/{id}         - Get single quote
  PATCH  /api/v1/service-quotes/{id}/quote   - Provider submits pricing
  PATCH  /api/v1/service-quotes/{id}/status  - Transition status
  GET    /api/v1/service-quotes/summary      - Summary counts
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
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.notification import NotificationType
from src.models.quote import BHServiceQuote, QuoteStatus, VALID_QUOTE_TRANSITIONS
from src.models.user import BHUser
from src.services.notify import create_notification

router = APIRouter(prefix="/api/v1/service-quotes", tags=["service-quotes"])


# --- Schemas ---

class QuoteOut(BaseModel):
    id: UUID
    customer_id: UUID
    provider_id: UUID
    listing_id: UUID
    status: QuoteStatus
    request_description: str
    quote_description: Optional[str] = None
    labor_hours: Optional[float] = None
    labor_rate: Optional[float] = None
    materials_cost: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "EUR"
    deposit_required: Optional[float] = None
    estimated_days: Optional[int] = None
    quote_valid_days: int = 7
    customer_message: Optional[str] = None
    provider_message: Optional[str] = None
    decline_reason: Optional[str] = None
    cancel_reason: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class QuoteRequest(BaseModel):
    listing_id: UUID
    request_description: str = Field(..., min_length=10, max_length=2000)
    customer_message: Optional[str] = Field(None, max_length=1000)
    idempotency_key: Optional[str] = Field(None, max_length=100)


class QuoteSubmit(BaseModel):
    quote_description: str = Field(..., min_length=5, max_length=2000)
    labor_hours: Optional[float] = Field(None, ge=0)
    labor_rate: Optional[float] = Field(None, ge=0)
    materials_cost: Optional[float] = Field(None, ge=0)
    total_amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    deposit_required: Optional[float] = Field(None, ge=0)
    estimated_days: Optional[int] = Field(None, ge=1)
    quote_valid_days: int = Field(default=7, ge=1, le=90)
    provider_message: Optional[str] = Field(None, max_length=1000)


class StatusUpdate(BaseModel):
    status: QuoteStatus
    message: Optional[str] = Field(None, max_length=1000)
    decline_reason: Optional[str] = Field(None, max_length=500)
    cancel_reason: Optional[str] = Field(None, max_length=500)


# --- Endpoints ---

@router.post("", response_model=QuoteOut, status_code=201)
async def request_quote(
    req: QuoteRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Customer requests a quote on a service listing."""
    user = await get_user(db, token)

    # Idempotency check
    if req.idempotency_key:
        existing = await db.execute(
            select(BHServiceQuote).where(
                BHServiceQuote.idempotency_key == req.idempotency_key
            )
        )
        found = existing.scalars().first()
        if found:
            return _to_out(found)

    # Load listing + item
    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == req.listing_id)
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Must be a service or training listing
    if listing.listing_type not in ("service", "training"):
        raise HTTPException(
            status_code=400,
            detail="Quotes are only for service or training listings"
        )

    provider_id = listing.item.owner_id
    if provider_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot request a quote on your own listing")

    quote = BHServiceQuote(
        customer_id=user.id,
        provider_id=provider_id,
        listing_id=listing.id,
        status=QuoteStatus.REQUESTED,
        request_description=req.request_description,
        customer_message=req.customer_message,
        idempotency_key=req.idempotency_key,
    )
    db.add(quote)
    await db.flush()

    # Notify provider
    await create_notification(
        db=db,
        user_id=provider_id,
        notification_type=NotificationType.SYSTEM,
        title=f"New quote request for {listing.item.name}",
        body=req.request_description[:100],
        link="/orders?tab=quotes",
        entity_type="quote",
        entity_id=quote.id,
    )

    await db.commit()
    return _to_out(quote)


@router.get("", response_model=List[QuoteOut])
async def list_quotes(
    status: Optional[QuoteStatus] = None,
    role: Optional[str] = Query(None, regex="^(customer|provider)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List quotes where user is customer or provider."""
    user = await get_user(db, token)

    query = select(BHServiceQuote)

    if role == "customer":
        query = query.where(BHServiceQuote.customer_id == user.id)
    elif role == "provider":
        query = query.where(BHServiceQuote.provider_id == user.id)
    else:
        query = query.where(
            (BHServiceQuote.customer_id == user.id) |
            (BHServiceQuote.provider_id == user.id)
        )

    if status:
        query = query.where(BHServiceQuote.status == status)

    query = query.order_by(BHServiceQuote.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    quotes = result.scalars().all()

    return [_to_out(q) for q in quotes]


@router.get("/summary")
async def quote_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Summary of quote counts for the current user."""
    user = await get_user(db, token)

    result = await db.execute(
        select(
            BHServiceQuote.status,
            func.count(BHServiceQuote.id),
        )
        .where(
            (BHServiceQuote.customer_id == user.id) |
            (BHServiceQuote.provider_id == user.id)
        )
        .group_by(BHServiceQuote.status)
    )
    counts = {row[0].value: row[1] for row in result.all()}
    total = sum(counts.values())

    return {
        "total": total,
        "requested": counts.get("requested", 0),
        "quoted": counts.get("quoted", 0),
        "accepted": counts.get("accepted", 0),
        "in_progress": counts.get("in_progress", 0),
        "completed": counts.get("completed", 0),
        "declined": counts.get("declined", 0),
        "cancelled": counts.get("cancelled", 0),
    }


@router.get("/{quote_id}", response_model=QuoteOut)
async def get_quote(
    quote_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get a single quote. Must be customer or provider."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHServiceQuote).where(BHServiceQuote.id == quote_id)
    )
    quote = result.scalars().first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if quote.customer_id != user.id and quote.provider_id != user.id:
        raise HTTPException(status_code=403, detail="Not your quote")

    return _to_out(quote)


@router.patch("/{quote_id}/quote", response_model=QuoteOut)
async def submit_quote(
    quote_id: UUID,
    req: QuoteSubmit,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Provider submits pricing for a quote request."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHServiceQuote).where(BHServiceQuote.id == quote_id)
    )
    quote = result.scalars().first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if quote.provider_id != user.id:
        raise HTTPException(status_code=403, detail="Only the provider can submit a quote")
    if quote.status != QuoteStatus.REQUESTED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot submit quote when status is {quote.status.value}"
        )

    quote.quote_description = req.quote_description
    quote.labor_hours = req.labor_hours
    quote.labor_rate = req.labor_rate
    quote.materials_cost = req.materials_cost
    quote.total_amount = req.total_amount
    quote.currency = req.currency
    quote.deposit_required = req.deposit_required
    quote.estimated_days = req.estimated_days
    quote.quote_valid_days = req.quote_valid_days
    quote.provider_message = req.provider_message
    quote.status = QuoteStatus.QUOTED

    # Notify customer
    await create_notification(
        db=db,
        user_id=quote.customer_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Quote received: {req.total_amount:.2f} {req.currency}",
        body=req.quote_description[:100],
        link="/orders?tab=quotes",
        entity_type="quote",
        entity_id=quote.id,
    )

    await db.commit()
    return _to_out(quote)


@router.patch("/{quote_id}/status")
async def update_quote_status(
    quote_id: UUID,
    req: StatusUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Transition quote status. Validates state machine."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHServiceQuote).where(BHServiceQuote.id == quote_id)
    )
    quote = result.scalars().first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if quote.customer_id != user.id and quote.provider_id != user.id:
        raise HTTPException(status_code=403, detail="Not your quote")

    # Validate transition
    allowed = VALID_QUOTE_TRANSITIONS.get(quote.status, set())
    if req.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {quote.status.value} to {req.status.value}. "
                   f"Allowed: {', '.join(s.value for s in allowed)}"
        )

    # Authorization per transition
    is_customer = quote.customer_id == user.id
    is_provider = quote.provider_id == user.id

    if req.status == QuoteStatus.ACCEPTED and not is_customer:
        raise HTTPException(status_code=403, detail="Only customer can accept")
    if req.status == QuoteStatus.DECLINED and not is_customer:
        raise HTTPException(status_code=403, detail="Only customer can decline")
    if req.status == QuoteStatus.IN_PROGRESS and not is_provider:
        raise HTTPException(status_code=403, detail="Only provider can start work")
    if req.status == QuoteStatus.COMPLETED and not is_provider:
        raise HTTPException(status_code=403, detail="Only provider can mark complete")

    quote.status = req.status

    if req.decline_reason:
        quote.decline_reason = req.decline_reason
    if req.cancel_reason:
        quote.cancel_reason = req.cancel_reason

    # Notify other party
    other_id = quote.provider_id if is_customer else quote.customer_id
    status_labels = {
        QuoteStatus.ACCEPTED: "Quote accepted",
        QuoteStatus.DECLINED: "Quote declined",
        QuoteStatus.IN_PROGRESS: "Work has started",
        QuoteStatus.COMPLETED: "Work completed",
        QuoteStatus.CANCELLED: "Quote cancelled",
        QuoteStatus.DISPUTED: "Quote disputed",
    }
    title = status_labels.get(req.status, f"Quote status: {req.status.value}")

    await create_notification(
        db=db,
        user_id=other_id,
        notification_type=NotificationType.SYSTEM,
        title=title,
        body=req.message,
        link="/orders?tab=quotes",
        entity_type="quote",
        entity_id=quote.id,
    )

    await db.commit()
    return {"status": quote.status.value, "quote_id": str(quote.id)}


# --- Helpers ---

def _to_out(q: BHServiceQuote) -> QuoteOut:
    return QuoteOut(
        id=q.id,
        customer_id=q.customer_id,
        provider_id=q.provider_id,
        listing_id=q.listing_id,
        status=q.status,
        request_description=q.request_description,
        quote_description=q.quote_description,
        labor_hours=q.labor_hours,
        labor_rate=q.labor_rate,
        materials_cost=q.materials_cost,
        total_amount=q.total_amount,
        currency=q.currency,
        deposit_required=q.deposit_required,
        estimated_days=q.estimated_days,
        quote_valid_days=q.quote_valid_days,
        customer_message=q.customer_message,
        provider_message=q.provider_message,
        decline_reason=q.decline_reason,
        cancel_reason=q.cancel_reason,
        created_at=q.created_at.isoformat(),
    )
