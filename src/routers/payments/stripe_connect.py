"""Stripe Connect endpoints: onboard, status, payout."""

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

from ._schemas import (
    PaymentOut,
    CreateOrderRequest,
    CreateOrderResponse,
    CaptureRequest,
    RefundRequest,
    ConnectOnboardResponse,
    ConnectStatusResponse,
    PayoutRequest,
    StripeCreateRequest,
    StripeCreateResponse,
    StripeConfirmRequest,
)

router = APIRouter()

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


