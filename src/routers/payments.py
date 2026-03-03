"""Payment API.

PayPal Checkout integration:
1. POST /api/v1/payments/create-order -> creates PayPal order, returns approval URL
2. POST /api/v1/payments/capture -> captures after buyer approves
3. POST /api/v1/payments/{id}/refund -> issues refund
4. GET /api/v1/payments -> list user's payments
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.notification import NotificationType
from src.models.payment import BHPayment, PaymentProvider, PaymentStatus, PaymentType
from src.models.rental import BHRental
from src.models.user import BHUser
from src.services.notify import create_notification
from src.services.paypal import capture_order, create_order, refund_capture
from src.services import stripe_service

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


# --- Schemas ---

class PaymentOut(BaseModel):
    id: UUID
    payer_id: UUID
    payee_id: UUID
    rental_id: Optional[UUID] = None
    payment_type: PaymentType
    amount: float
    currency: str
    provider: PaymentProvider
    status: PaymentStatus
    provider_order_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class CreateOrderRequest(BaseModel):
    rental_id: UUID
    payment_type: PaymentType
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)


class CreateOrderResponse(BaseModel):
    payment_id: UUID
    paypal_order_id: str
    approval_url: str


class CaptureRequest(BaseModel):
    payment_id: UUID
    paypal_order_id: str


class RefundRequest(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    reason: Optional[str] = None


class ConnectOnboardResponse(BaseModel):
    account_id: str
    onboarding_url: str


class ConnectStatusResponse(BaseModel):
    has_account: bool
    charges_enabled: bool = False
    payouts_enabled: bool = False
    details_submitted: bool = False


class PayoutRequest(BaseModel):
    payment_id: UUID


class StripeCreateRequest(BaseModel):
    rental_id: UUID
    payment_type: PaymentType
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)


class StripeCreateResponse(BaseModel):
    payment_id: UUID
    stripe_session_id: str
    checkout_url: str


class StripeConfirmRequest(BaseModel):
    payment_id: UUID
    stripe_session_id: str


# --- Endpoints ---

@router.post("/create-order", response_model=CreateOrderResponse)
async def create_payment_order(
    req: CreateOrderRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a PayPal order. Returns approval URL to redirect buyer."""
    user = await get_user(db, token)

    # Get rental and item owner
    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing))
        .where(BHRental.id == req.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    if rental.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Only the renter can make payments")

    # Get item owner as payee
    item_result = await db.execute(
        select(BHItem).where(BHItem.id == rental.listing.item_id)
    )
    item = item_result.scalars().first()

    # Create PayPal order
    description = f"BorrowHood {req.payment_type.value}: {item.name}"
    pp_order = await create_order(
        amount=req.amount,
        currency=req.currency,
        description=description,
    )

    if not pp_order:
        raise HTTPException(status_code=502, detail="PayPal order creation failed")

    # Record payment
    payment = BHPayment(
        payer_id=user.id,
        payee_id=item.owner_id,
        rental_id=rental.id,
        payment_type=req.payment_type,
        amount=req.amount,
        currency=req.currency,
        provider=PaymentProvider.PAYPAL,
        status=PaymentStatus.PENDING,
        provider_order_id=pp_order["id"],
    )
    db.add(payment)
    await db.flush()
    await db.commit()

    return CreateOrderResponse(
        payment_id=payment.id,
        paypal_order_id=pp_order["id"],
        approval_url=pp_order.get("approval_url", ""),
    )


@router.post("/capture")
async def capture_payment(
    req: CaptureRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Capture a PayPal payment after buyer approval."""
    user = await get_user(db, token)

    # Get payment record
    result = await db.execute(
        select(BHPayment).where(BHPayment.id == req.payment_id)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your payment")
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Payment is not pending")

    # Capture via PayPal
    capture = await capture_order(req.paypal_order_id)
    if not capture:
        payment.status = PaymentStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=502, detail="PayPal capture failed")

    payment.status = PaymentStatus.COMPLETED
    payment.provider_capture_id = capture.get("capture_id")

    # Notify payee
    await create_notification(
        db=db,
        user_id=payment.payee_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Payment of {payment.amount:.2f} {payment.currency} received",
        link="/dashboard",
        entity_type="payment",
        entity_id=payment.rental_id,
    )

    await db.commit()
    return {"status": "completed", "capture_id": capture.get("capture_id")}


@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: UUID,
    req: RefundRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Refund a payment (full or partial). Payee (item owner) initiates."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHPayment).where(BHPayment.id == payment_id)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payee_id != user.id:
        raise HTTPException(status_code=403, detail="Only the payee can issue refunds")
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only refund completed payments")
    if not payment.provider_capture_id:
        raise HTTPException(status_code=400, detail="No capture ID to refund")

    refund_amount = req.amount or payment.amount

    refund = await refund_capture(
        payment.provider_capture_id,
        amount=req.amount,
        currency=payment.currency,
    )

    if not refund:
        raise HTTPException(status_code=502, detail="PayPal refund failed")

    payment.provider_refund_id = refund.get("refund_id")
    payment.refund_amount = refund_amount
    payment.refund_reason = req.reason

    if refund_amount >= payment.amount:
        payment.status = PaymentStatus.REFUNDED
    else:
        payment.status = PaymentStatus.PARTIAL_REFUND

    # Notify payer
    await create_notification(
        db=db,
        user_id=payment.payer_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Refund of {refund_amount:.2f} {payment.currency} processed",
        link="/dashboard",
        entity_type="payment",
        entity_id=payment.rental_id,
    )

    await db.commit()
    return {"status": payment.status.value, "refund_id": refund.get("refund_id")}


@router.get("", response_model=List[PaymentOut])
async def list_payments(
    limit: int = Query(20, ge=1, le=100),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List payments for the current user (as payer or payee)."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHPayment)
        .where((BHPayment.payer_id == user.id) | (BHPayment.payee_id == user.id))
        .order_by(BHPayment.created_at.desc())
        .limit(limit)
    )
    payments = result.scalars().all()

    return [
        PaymentOut(
            id=p.id,
            payer_id=p.payer_id,
            payee_id=p.payee_id,
            rental_id=p.rental_id,
            payment_type=p.payment_type,
            amount=p.amount,
            currency=p.currency,
            provider=p.provider,
            status=p.status,
            provider_order_id=p.provider_order_id,
            created_at=p.created_at.isoformat(),
        )
        for p in payments
    ]


# --- Stripe Endpoints ---

@router.post("/stripe/create-session", response_model=StripeCreateResponse)
async def create_stripe_session(
    req: StripeCreateRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Checkout Session. Returns checkout URL to redirect buyer."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing))
        .where(BHRental.id == req.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Only the renter can make payments")

    item_result = await db.execute(
        select(BHItem).where(BHItem.id == rental.listing.item_id)
    )
    item = item_result.scalars().first()

    description = f"BorrowHood {req.payment_type.value}: {item.name}"
    session = await stripe_service.create_checkout_session(
        amount=req.amount,
        currency=req.currency,
        description=description,
    )

    if not session:
        raise HTTPException(status_code=502, detail="Stripe session creation failed")

    payment = BHPayment(
        payer_id=user.id,
        payee_id=item.owner_id,
        rental_id=rental.id,
        payment_type=req.payment_type,
        amount=req.amount,
        currency=req.currency,
        provider=PaymentProvider.STRIPE,
        status=PaymentStatus.PENDING,
        provider_order_id=session["id"],
    )
    db.add(payment)
    await db.flush()
    await db.commit()

    return StripeCreateResponse(
        payment_id=payment.id,
        stripe_session_id=session["id"],
        checkout_url=session["url"],
    )


@router.post("/stripe/confirm")
async def confirm_stripe_payment(
    req: StripeConfirmRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Confirm a Stripe payment after buyer completes checkout."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHPayment).where(BHPayment.id == req.payment_id)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your payment")
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Payment is not pending")

    session = await stripe_service.retrieve_session(req.stripe_session_id)
    if not session:
        payment.status = PaymentStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=502, detail="Stripe session retrieval failed")

    if session.get("payment_status") == "paid":
        payment.status = PaymentStatus.COMPLETED
        payment.provider_capture_id = session.get("payment_intent", "")

        await create_notification(
            db=db,
            user_id=payment.payee_id,
            notification_type=NotificationType.SYSTEM,
            title=f"Payment of {payment.amount:.2f} {payment.currency} received (Stripe)",
            link="/dashboard",
            entity_type="payment",
            entity_id=payment.rental_id,
        )
    else:
        payment.status = PaymentStatus.FAILED

    await db.commit()
    return {"status": payment.status.value, "payment_intent": session.get("payment_intent")}


@router.post("/stripe/{payment_id}/refund")
async def refund_stripe_payment(
    payment_id: UUID,
    req: RefundRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Refund a Stripe payment (full or partial). Payee initiates."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHPayment).where(BHPayment.id == payment_id)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payee_id != user.id:
        raise HTTPException(status_code=403, detail="Only the payee can issue refunds")
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only refund completed payments")
    if not payment.provider_capture_id:
        raise HTTPException(status_code=400, detail="No payment intent to refund")

    refund_amount = req.amount or payment.amount

    refund = await stripe_service.refund_payment(
        payment.provider_capture_id,
        amount=req.amount,
    )

    if not refund:
        raise HTTPException(status_code=502, detail="Stripe refund failed")

    payment.provider_refund_id = refund.get("refund_id")
    payment.refund_amount = refund_amount
    payment.refund_reason = req.reason

    if refund_amount >= payment.amount:
        payment.status = PaymentStatus.REFUNDED
    else:
        payment.status = PaymentStatus.PARTIAL_REFUND

    await create_notification(
        db=db,
        user_id=payment.payer_id,
        notification_type=NotificationType.SYSTEM,
        title=f"Refund of {refund_amount:.2f} {payment.currency} processed (Stripe)",
        link="/dashboard",
        entity_type="payment",
        entity_id=payment.rental_id,
    )

    await db.commit()
    return {"status": payment.status.value, "refund_id": refund.get("refund_id")}


# --- Stripe Connect (Marketplace Payouts) ---

@router.post("/stripe/connect/onboard", response_model=ConnectOnboardResponse)
async def stripe_connect_onboard(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Start Stripe Connect onboarding for the current user (seller).

    Creates an Express Connect account and returns the onboarding URL.
    If the user already has an account, returns a new onboarding link.
    """
    user = await get_user(db, token)

    if user.stripe_account_id:
        # Already has account -- generate fresh onboarding/dashboard link
        link = await stripe_service.create_account_link(user.stripe_account_id)
        if not link:
            raise HTTPException(status_code=502, detail="Failed to create account link")
        return ConnectOnboardResponse(
            account_id=user.stripe_account_id,
            onboarding_url=link["url"],
        )

    # Create new Connect account
    result = await stripe_service.create_connect_account(
        email=user.email,
        country=user.country_code or "IT",
    )
    if not result:
        raise HTTPException(status_code=502, detail="Failed to create Stripe Connect account")

    user.stripe_account_id = result["account_id"]
    await db.commit()

    return ConnectOnboardResponse(
        account_id=result["account_id"],
        onboarding_url=result["onboarding_url"],
    )


@router.get("/stripe/connect/status", response_model=ConnectStatusResponse)
async def stripe_connect_status(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Check the current user's Stripe Connect onboarding status."""
    user = await get_user(db, token)

    if not user.stripe_account_id:
        return ConnectStatusResponse(has_account=False)

    account = await stripe_service.retrieve_account(user.stripe_account_id)
    if not account:
        return ConnectStatusResponse(has_account=True)

    return ConnectStatusResponse(
        has_account=True,
        charges_enabled=account["charges_enabled"],
        payouts_enabled=account["payouts_enabled"],
        details_submitted=account["details_submitted"],
    )


@router.post("/stripe/connect/payout")
async def stripe_connect_payout(
    req: PayoutRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Transfer funds to a seller after rental completion.

    Calculates 5% platform fee. Only the payee can trigger payouts.
    """
    user = await get_user(db, token)

    result = await db.execute(
        select(BHPayment).where(BHPayment.id == req.payment_id)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payee_id != user.id:
        raise HTTPException(status_code=403, detail="Only the payee can request payouts")
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Payment must be completed first")
    if payment.seller_payout_amount is not None:
        raise HTTPException(status_code=400, detail="Payout already processed")

    # Get seller's Connect account
    seller = await db.get(BHUser, payment.payee_id)
    if not seller or not seller.stripe_account_id:
        raise HTTPException(status_code=400, detail="Seller has not completed Stripe Connect onboarding")

    # Calculate split: 5% platform, 95% seller
    platform_fee = round(payment.amount * 0.05, 2)
    seller_amount = round(payment.amount - platform_fee, 2)

    transfer = await stripe_service.create_transfer(
        amount=seller_amount,
        destination_account_id=seller.stripe_account_id,
        currency=payment.currency,
        description=f"BorrowHood payout for payment {payment.id}",
    )

    if not transfer:
        raise HTTPException(status_code=502, detail="Stripe transfer failed")

    payment.platform_fee = platform_fee
    payment.seller_payout_amount = seller_amount

    await create_notification(
        db=db,
        user_id=seller.id,
        notification_type=NotificationType.SYSTEM,
        title=f"Payout of {seller_amount:.2f} {payment.currency} sent to your account",
        link="/dashboard",
        entity_type="payment",
        entity_id=payment.rental_id,
    )

    await db.commit()
    return {
        "status": "transferred",
        "transfer_id": transfer["transfer_id"],
        "platform_fee": platform_fee,
        "seller_amount": seller_amount,
    }
