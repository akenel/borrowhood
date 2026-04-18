"""Pydantic schemas for payments/ package."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.payment import PaymentProvider, PaymentStatus, PaymentType

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
