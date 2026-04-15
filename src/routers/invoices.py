"""Invoices API + printable view.

Endpoints:
    POST /api/v1/invoices/from-rental/{rental_id}  -- generate invoice
    GET  /api/v1/invoices                          -- list mine (provider OR customer)
    GET  /api/v1/invoices/{id}                     -- get single
    PATCH /api/v1/invoices/{id}/status             -- mark paid / cancel
    GET  /invoices/{id}/print                      -- printable HTML view
    GET  /invoices/{id}.csv                        -- CSV row (for accountant export)
"""

import csv
import io
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth
from src.i18n import get_translator, detect_language
from src.models.invoice import BHInvoice, InvoiceStatus, InvoiceType
from src.services.invoicing import create_invoice_from_rental
from src.routers.pages import templates


router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])
view_router = APIRouter()  # public view routes (HTML + CSV) at /invoices/...


# ── Schemas ────────────────────────────────────────────────────────────


class InvoiceCreateRequest(BaseModel):
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class InvoiceStatusUpdate(BaseModel):
    status: str  # "paid" | "cancelled"


class InvoiceOut(BaseModel):
    id: UUID
    invoice_number: str
    invoice_type: str
    status: str
    issue_date: str
    rental_id: UUID
    provider_id: UUID
    customer_id: UUID
    provider_snapshot: dict
    customer_snapshot: dict
    line_items: list
    currency: str
    subtotal_eur: float
    vat_rate: float
    vat_amount_eur: float
    total_eur: float
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    paid_at: Optional[str] = None
    notes: Optional[str] = None
    legal_notice: Optional[str] = None

    class Config:
        from_attributes = True


def _to_out(inv: BHInvoice) -> InvoiceOut:
    return InvoiceOut(
        id=inv.id,
        invoice_number=inv.invoice_number,
        invoice_type=inv.invoice_type.value if inv.invoice_type else "ricevuta",
        status=inv.status.value if inv.status else "issued",
        issue_date=inv.issue_date.isoformat() if inv.issue_date else "",
        rental_id=inv.rental_id,
        provider_id=inv.provider_id,
        customer_id=inv.customer_id,
        provider_snapshot=inv.provider_snapshot or {},
        customer_snapshot=inv.customer_snapshot or {},
        line_items=inv.line_items or [],
        currency=inv.currency or "EUR",
        subtotal_eur=inv.subtotal_eur or 0,
        vat_rate=inv.vat_rate or 0,
        vat_amount_eur=inv.vat_amount_eur or 0,
        total_eur=inv.total_eur or 0,
        payment_method=inv.payment_method,
        payment_reference=inv.payment_reference,
        paid_at=inv.paid_at.isoformat() if inv.paid_at else None,
        notes=inv.notes,
        legal_notice=inv.legal_notice,
    )


# ── API endpoints ──────────────────────────────────────────────────────


@router.post("/from-rental/{rental_id}", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    rental_id: UUID,
    body: InvoiceCreateRequest = InvoiceCreateRequest(),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate an invoice from a completed rental. Provider only.

    Idempotent: returns existing invoice if one already exists for this rental.
    """
    user = await get_user(db, token)
    try:
        invoice = await create_invoice_from_rental(
            db, rental_id, user,
            payment_method=body.payment_method,
            payment_reference=body.payment_reference,
            notes=body.notes,
        )
    except ValueError as e:
        msg = str(e)
        if msg == "rental_not_found":
            raise HTTPException(status_code=404, detail="Rental not found")
        if msg == "not_provider":
            raise HTTPException(status_code=403, detail="Only the provider can issue invoices")
        if msg in ("rental_missing_item", "rental_missing_parties"):
            raise HTTPException(status_code=400, detail=f"Rental data incomplete: {msg}")
        raise HTTPException(status_code=400, detail=msg)
    await db.commit()
    return _to_out(invoice)


@router.get("", response_model=List[InvoiceOut])
async def list_my_invoices(
    role: str = Query("provider", pattern="^(provider|customer|all)$"),
    year: Optional[int] = None,
    month: Optional[int] = Query(None, ge=1, le=12),
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List invoices where current user is provider, customer, or both."""
    user = await get_user(db, token)
    q = select(BHInvoice).where(BHInvoice.deleted_at.is_(None))
    if role == "provider":
        q = q.where(BHInvoice.provider_id == user.id)
    elif role == "customer":
        q = q.where(BHInvoice.customer_id == user.id)
    else:
        q = q.where(or_(BHInvoice.provider_id == user.id, BHInvoice.customer_id == user.id))
    if year:
        q = q.where(BHInvoice.year == year)
    if status:
        try:
            q = q.where(BHInvoice.status == InvoiceStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if month:
        # Filter by month of issue_date
        from sqlalchemy import extract
        q = q.where(extract("month", BHInvoice.issue_date) == month)
    q = q.order_by(BHInvoice.issue_date.desc()).limit(limit)
    result = await db.execute(q)
    return [_to_out(inv) for inv in result.scalars().all()]


@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get an invoice. Only provider or customer can view."""
    user = await get_user(db, token)
    inv = await db.scalar(
        select(BHInvoice).where(BHInvoice.id == invoice_id).where(BHInvoice.deleted_at.is_(None))
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if user.id not in (inv.provider_id, inv.customer_id):
        raise HTTPException(status_code=403, detail="Not your invoice")
    return _to_out(inv)


@router.patch("/{invoice_id}/status", response_model=InvoiceOut)
async def update_invoice_status(
    invoice_id: UUID,
    body: InvoiceStatusUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Mark invoice as paid or cancelled. Provider only."""
    user = await get_user(db, token)
    inv = await db.scalar(
        select(BHInvoice).where(BHInvoice.id == invoice_id).where(BHInvoice.deleted_at.is_(None))
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if user.id != inv.provider_id:
        raise HTTPException(status_code=403, detail="Only provider can change status")
    try:
        new_status = InvoiceStatus(body.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
    inv.status = new_status
    if new_status == InvoiceStatus.PAID and not inv.paid_at:
        inv.paid_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inv)
    return _to_out(inv)


# ── Public view routes ────────────────────────────────────────────────


@view_router.get("/invoices/{invoice_id}/print", response_class=HTMLResponse)
async def print_invoice(
    invoice_id: UUID,
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
):
    """Printable invoice page. Only provider or customer can view.

    The CSS is print-optimized -- A4 page, no nav, no footer, full bleed.
    Browser File > Print -> Save as PDF gives a clean PDF.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = await get_user(db, token)
    inv = await db.scalar(
        select(BHInvoice).where(BHInvoice.id == invoice_id).where(BHInvoice.deleted_at.is_(None))
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if user.id not in (inv.provider_id, inv.customer_id):
        raise HTTPException(status_code=403, detail="Not your invoice")

    lang = detect_language(
        query_param=request.query_params.get("lang"),
        cookie=request.cookies.get("bh_lang"),
        accept_header=request.headers.get("accept-language"),
    )
    t = get_translator(lang)
    return templates.TemplateResponse(
        request,
        "pages/invoice_print.html",
        {
            "request": request,
            "invoice": inv,
            "lang": lang,
            "t": t,
        },
    )


@view_router.get("/invoices/{invoice_id}.csv")
async def invoice_csv(
    invoice_id: UUID,
    token: Optional[dict] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
):
    """CSV row of the invoice for accountant export. Provider only."""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = await get_user(db, token)
    inv = await db.scalar(
        select(BHInvoice).where(BHInvoice.id == invoice_id).where(BHInvoice.deleted_at.is_(None))
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if user.id != inv.provider_id:
        raise HTTPException(status_code=403, detail="Provider only")

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["invoice_number", "issue_date", "type", "status",
                "provider_name", "provider_vat",
                "customer_name", "customer_city",
                "subtotal_eur", "vat_rate", "vat_amount_eur", "total_eur",
                "payment_method", "payment_reference"])
    p = inv.provider_snapshot or {}
    c = inv.customer_snapshot or {}
    w.writerow([
        inv.invoice_number,
        inv.issue_date.isoformat() if inv.issue_date else "",
        inv.invoice_type.value if inv.invoice_type else "",
        inv.status.value if inv.status else "",
        p.get("business_name") or p.get("display_name", ""),
        p.get("vat_number") or "",
        c.get("business_name") or c.get("display_name", ""),
        c.get("city") or "",
        f"{inv.subtotal_eur:.2f}",
        f"{inv.vat_rate:.2f}",
        f"{inv.vat_amount_eur:.2f}",
        f"{inv.total_eur:.2f}",
        inv.payment_method or "",
        inv.payment_reference or "",
    ])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{inv.invoice_number}.csv"'},
    )


# ── Day Summary aggregate endpoint ────────────────────────────────────


@router.get("/day-summary/{day}")
async def day_summary(
    day: str,  # YYYY-MM-DD
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Summary of provider's activity for a given day.

    Returns: rentals completed, total earnings, hours worked, invoices issued,
    list of transactions (rentals) for that day.
    """
    user = await get_user(db, token)
    try:
        target = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(status_code=400, detail="day must be YYYY-MM-DD")

    from datetime import timedelta
    day_start = target.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    from src.models.item import BHItem
    from src.models.listing import BHListing
    from src.models.rental import BHRental, RentalStatus

    # All rentals on user's items completed today
    q = (
        select(BHRental)
        .options(
            selectinload(BHRental.listing).selectinload(BHListing.item),
            selectinload(BHRental.renter),
        )
        .join(BHListing, BHRental.listing_id == BHListing.id)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user.id)
        .where(BHRental.updated_at >= day_start)
        .where(BHRental.updated_at < day_end)
        .where(BHRental.status.in_([
            RentalStatus.COMPLETED, RentalStatus.PAYMENT_CONFIRMED,
            RentalStatus.RETURNED, RentalStatus.PICKED_UP,
        ]))
        .order_by(BHRental.updated_at.desc())
    )
    rentals = (await db.execute(q)).scalars().unique().all()

    # Invoiced rentals
    invoiced_ids = set()
    if rentals:
        invs = await db.execute(
            select(BHInvoice.rental_id).where(BHInvoice.rental_id.in_([r.id for r in rentals]))
        )
        invoiced_ids = {row[0] for row in invs.all()}

    # Aggregates
    earnings = 0.0
    hours = 0.0
    transactions = []
    for r in rentals:
        listing = r.listing
        item = listing.item if listing else None
        price = float(listing.price or 0) if listing else 0
        # Estimate qty (for per_day/per_hour rentals)
        qty = 1.0
        if listing and r.requested_start and r.requested_end:
            if listing.price_unit == "per_day":
                qty = max(1, (r.requested_end - r.requested_start).days)
            elif listing.price_unit == "per_hour":
                qty = max(1, (r.requested_end - r.requested_start).total_seconds() / 3600)
                hours += qty
        earnings += price * qty
        transactions.append({
            "rental_id": str(r.id),
            "item_name": item.name if item else "(deleted)",
            "item_slug": item.slug if item else None,
            "customer_name": r.renter.display_name if r.renter else "Unknown",
            "status": r.status.value,
            "listing_type": listing.listing_type.value if listing else None,
            "price_eur": price,
            "qty": qty,
            "total_eur": round(price * qty, 2),
            "completed_at": r.updated_at.isoformat() if r.updated_at else None,
            "invoiced": r.id in invoiced_ids,
        })

    return {
        "day": day,
        "rentals_count": len(rentals),
        "earnings_eur": round(earnings, 2),
        "hours_worked": round(hours, 2),
        "invoices_issued": len(invoiced_ids),
        "transactions": transactions,
    }
