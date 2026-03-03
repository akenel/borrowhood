"""Insurance API: purchase policies, file claims, manage claim lifecycle.

Flow: Purchase policy -> File claim -> UNDER_REVIEW -> APPROVED/DENIED -> PAID_OUT
Premium: 5% of item listing price. Coverage: up to item value.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.insurance import (
    BHInsuranceClaim, BHInsurancePolicy,
    ClaimStatus, InsuranceStatus, CLAIM_TRANSITIONS,
)
from src.models.listing import BHListing
from src.models.rental import BHRental

router = APIRouter(prefix="/api/v1/insurance", tags=["insurance"])


# --- Schemas ---

class PolicyOut(BaseModel):
    id: UUID
    rental_id: UUID
    holder_id: UUID
    provider: str
    policy_number: str
    coverage_amount: float
    premium: float
    status: InsuranceStatus
    created_at: str

    class Config:
        from_attributes = True


class ClaimOut(BaseModel):
    id: UUID
    policy_id: UUID
    claimant_id: UUID
    description: str
    evidence_url: Optional[str] = None
    claim_amount: float
    approved_amount: Optional[float] = None
    status: ClaimStatus
    resolution_notes: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    rental_id: UUID


class FileClaimRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=2000)
    evidence_url: Optional[str] = Field(None, max_length=500)
    claim_amount: float = Field(..., gt=0)


class UpdateClaimRequest(BaseModel):
    status: ClaimStatus
    approved_amount: Optional[float] = None
    resolution_notes: Optional[str] = None


# --- Endpoints ---

@router.post("/purchase", response_model=PolicyOut, status_code=201)
async def purchase_policy(
    req: PurchaseRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Purchase insurance for a rental. Premium = 5% of listing price."""
    user = await get_user(db, token)

    # Check rental exists and user is the renter
    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == req.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Only the renter can purchase insurance")

    # Check no existing active policy
    existing = await db.execute(
        select(BHInsurancePolicy)
        .where(BHInsurancePolicy.rental_id == rental.id)
        .where(BHInsurancePolicy.status == InsuranceStatus.ACTIVE)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Active policy already exists for this rental")

    # Calculate premium and coverage from listing price
    item_value = rental.listing.price_per_day or rental.listing.price_per_hour or 50.0
    coverage = item_value * 10  # Coverage = 10x daily rate
    premium = round(coverage * 0.05, 2)  # 5% of coverage

    policy_number = f"BH-INS-{uuid.uuid4().hex[:8].upper()}"

    policy = BHInsurancePolicy(
        rental_id=rental.id,
        holder_id=user.id,
        provider="BorrowHood Basic",
        policy_number=policy_number,
        coverage_amount=coverage,
        premium=premium,
        status=InsuranceStatus.ACTIVE,
    )
    db.add(policy)
    await db.flush()
    await db.commit()
    await db.refresh(policy)

    return PolicyOut(
        id=policy.id,
        rental_id=policy.rental_id,
        holder_id=policy.holder_id,
        provider=policy.provider,
        policy_number=policy.policy_number,
        coverage_amount=policy.coverage_amount,
        premium=policy.premium,
        status=policy.status,
        created_at=policy.created_at.isoformat(),
    )


@router.get("", response_model=List[PolicyOut])
async def list_policies(
    limit: int = Query(20, ge=1, le=100),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List insurance policies for the current user."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHInsurancePolicy)
        .where(BHInsurancePolicy.holder_id == user.id)
        .order_by(BHInsurancePolicy.created_at.desc())
        .limit(limit)
    )
    policies = result.scalars().all()
    return [
        PolicyOut(
            id=p.id, rental_id=p.rental_id, holder_id=p.holder_id,
            provider=p.provider, policy_number=p.policy_number,
            coverage_amount=p.coverage_amount, premium=p.premium,
            status=p.status, created_at=p.created_at.isoformat(),
        )
        for p in policies
    ]


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(
    policy_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get a single insurance policy."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHInsurancePolicy).where(BHInsurancePolicy.id == policy_id)
    )
    policy = result.scalars().first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.holder_id != user.id:
        raise HTTPException(status_code=403, detail="Not your policy")

    return PolicyOut(
        id=policy.id, rental_id=policy.rental_id, holder_id=policy.holder_id,
        provider=policy.provider, policy_number=policy.policy_number,
        coverage_amount=policy.coverage_amount, premium=policy.premium,
        status=policy.status, created_at=policy.created_at.isoformat(),
    )


@router.post("/{policy_id}/claim", response_model=ClaimOut, status_code=201)
async def file_claim(
    policy_id: UUID,
    req: FileClaimRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """File an insurance claim against a policy."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHInsurancePolicy).where(BHInsurancePolicy.id == policy_id)
    )
    policy = result.scalars().first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.holder_id != user.id:
        raise HTTPException(status_code=403, detail="Not your policy")
    if policy.status != InsuranceStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Policy is not active")
    if req.claim_amount > policy.coverage_amount:
        raise HTTPException(status_code=400, detail="Claim exceeds coverage amount")

    claim = BHInsuranceClaim(
        policy_id=policy.id,
        claimant_id=user.id,
        description=req.description,
        evidence_url=req.evidence_url,
        claim_amount=req.claim_amount,
        status=ClaimStatus.FILED,
    )
    policy.status = InsuranceStatus.CLAIMED
    db.add(claim)
    await db.flush()
    await db.commit()
    await db.refresh(claim)

    return ClaimOut(
        id=claim.id, policy_id=claim.policy_id, claimant_id=claim.claimant_id,
        description=claim.description, evidence_url=claim.evidence_url,
        claim_amount=claim.claim_amount, approved_amount=claim.approved_amount,
        status=claim.status, resolution_notes=claim.resolution_notes,
        created_at=claim.created_at.isoformat(),
    )


@router.patch("/claims/{claim_id}", response_model=ClaimOut)
async def update_claim(
    claim_id: UUID,
    req: UpdateClaimRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update claim status. State machine: FILED->UNDER_REVIEW->APPROVED/DENIED->PAID_OUT."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHInsuranceClaim)
        .options(selectinload(BHInsuranceClaim.policy))
        .where(BHInsuranceClaim.id == claim_id)
    )
    claim = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Validate state transition
    valid_next = CLAIM_TRANSITIONS.get(claim.status, set())
    if req.status not in valid_next:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {claim.status.value} to {req.status.value}",
        )

    claim.status = req.status
    if req.approved_amount is not None:
        claim.approved_amount = req.approved_amount
    if req.resolution_notes:
        claim.resolution_notes = req.resolution_notes

    await db.commit()
    await db.refresh(claim)

    return ClaimOut(
        id=claim.id, policy_id=claim.policy_id, claimant_id=claim.claimant_id,
        description=claim.description, evidence_url=claim.evidence_url,
        claim_amount=claim.claim_amount, approved_amount=claim.approved_amount,
        status=claim.status, resolution_notes=claim.resolution_notes,
        created_at=claim.created_at.isoformat(),
    )


@router.get("/claims", response_model=List[ClaimOut])
async def list_claims(
    limit: int = Query(20, ge=1, le=100),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List insurance claims for the current user."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHInsuranceClaim)
        .where(BHInsuranceClaim.claimant_id == user.id)
        .order_by(BHInsuranceClaim.created_at.desc())
        .limit(limit)
    )
    claims = result.scalars().all()
    return [
        ClaimOut(
            id=c.id, policy_id=c.policy_id, claimant_id=c.claimant_id,
            description=c.description, evidence_url=c.evidence_url,
            claim_amount=c.claim_amount, approved_amount=c.approved_amount,
            status=c.status, resolution_notes=c.resolution_notes,
            created_at=c.created_at.isoformat(),
        )
        for c in claims
    ]
