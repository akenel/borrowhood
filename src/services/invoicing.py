"""Invoice generation service.

Builds a fully populated BHInvoice from a completed BHRental, with
sequential numbering per provider per year. Snapshots all relevant
fields so historical invoices stay correct even when profiles change.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.invoice import BHInvoice, InvoiceStatus, InvoiceType
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.rental import BHRental
from src.models.user import BHUser


# Italian small-business legal notices
LEGAL_NOTICE_RICEVUTA_REGIME_FORFETTARIO = (
    "Operazione effettuata in regime forfettario ex art. 1, commi 54-89, "
    "Legge 190/2014 -- non soggetta a IVA né ritenuta d'acconto."
)
LEGAL_NOTICE_RICEVUTA_OCCASIONAL = (
    "Ricevuta non fiscale. Prestazione di natura occasionale ai sensi "
    "dell'art. 67, comma 1, lett. l) del DPR 917/86."
)
LEGAL_NOTICE_FATTURA_VAT = (
    "Fattura emessa ai sensi del DPR 633/72."
)


async def next_invoice_number(
    db: AsyncSession, provider_id, year: Optional[int] = None
) -> tuple[int, str]:
    """Return (sequence_number, formatted_invoice_number) atomically.

    Counter is per provider per year. Uses MAX+1 in a transaction; the
    UNIQUE constraint on (provider_id, year, sequence_number) is the
    safety net against races (the second writer gets IntegrityError and
    can retry).
    """
    if year is None:
        year = datetime.now(timezone.utc).year

    max_seq = await db.scalar(
        select(func.max(BHInvoice.sequence_number))
        .where(BHInvoice.provider_id == provider_id)
        .where(BHInvoice.year == year)
    )
    seq = (max_seq or 0) + 1
    formatted = f"FT-{year}-{seq:04d}"
    return seq, formatted


def _build_provider_snapshot(provider: BHUser) -> dict:
    """Freeze provider details at issue time."""
    return {
        "display_name": provider.display_name or "",
        "business_name": provider.business_name or None,
        "vat_number": provider.vat_number or None,
        "seller_type": (provider.seller_type or "personal"),
        "city": provider.city or None,
        "country_code": provider.country_code or None,
        "email": provider.email or None,
        "telegram_username": provider.telegram_username or None,
        "slug": provider.slug or "",
    }


def _build_customer_snapshot(customer: BHUser) -> dict:
    """Freeze customer details at issue time."""
    return {
        "display_name": customer.display_name or "",
        "business_name": customer.business_name or None,
        "vat_number": customer.vat_number or None,
        "city": customer.city or None,
        "country_code": customer.country_code or None,
        "slug": customer.slug or "",
    }


def _build_line_items(rental: BHRental, listing: BHListing, item: BHItem) -> list:
    """Build invoice line items from the rental + listing + item."""
    description = item.name or "Service"
    listing_type = listing.listing_type.value if listing.listing_type else "service"
    description_with_type = f"{description} ({listing_type})"

    # Quantity logic: rentals charge per period, services charge once
    qty = 1.0
    unit_price = float(listing.price or 0)

    if listing_type == "rent" and listing.price_unit == "per_day":
        if rental.requested_start and rental.requested_end:
            days = max(1, (rental.requested_end - rental.requested_start).days)
            qty = float(days)
    elif listing_type == "rent" and listing.price_unit == "per_hour":
        if rental.requested_start and rental.requested_end:
            hours = max(1, int((rental.requested_end - rental.requested_start).total_seconds() / 3600))
            qty = float(hours)

    return [{
        "description": description_with_type,
        "quantity": qty,
        "unit_price": unit_price,
        "total": round(qty * unit_price, 2),
    }]


async def create_invoice_from_rental(
    db: AsyncSession,
    rental_id,
    issuer_user: BHUser,
    payment_method: Optional[str] = None,
    payment_reference: Optional[str] = None,
    notes: Optional[str] = None,
) -> BHInvoice:
    """Generate an invoice from a rental. Issuer must be the provider (item owner).

    Returns the created BHInvoice. Raises ValueError if the rental cannot
    be invoiced (wrong owner, missing data, already invoiced).
    """
    # Load rental with item + listing + customer
    result = await db.execute(
        select(BHRental)
        .options(
            selectinload(BHRental.listing).selectinload(BHListing.item).selectinload(BHItem.owner),
            selectinload(BHRental.renter),
        )
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise ValueError("rental_not_found")

    listing = rental.listing
    item = listing.item if listing else None
    if not item:
        raise ValueError("rental_missing_item")

    provider = item.owner
    customer = rental.renter
    if not provider or not customer:
        raise ValueError("rental_missing_parties")

    # Authorization: only the provider can issue an invoice
    if issuer_user.id != provider.id:
        raise ValueError("not_provider")

    # Idempotency: one invoice per rental (use existing if present)
    existing = await db.scalar(
        select(BHInvoice).where(BHInvoice.rental_id == rental_id)
    )
    if existing:
        return existing

    # Build snapshots
    provider_snap = _build_provider_snapshot(provider)
    customer_snap = _build_customer_snapshot(customer)
    line_items = _build_line_items(rental, listing, item)

    # Money math
    subtotal = sum(li["total"] for li in line_items)
    is_business = provider_snap["seller_type"] == "business"
    vat_rate = 22.0 if is_business else 0.0
    vat_amount = round(subtotal * vat_rate / 100, 2)
    total = round(subtotal + vat_amount, 2)

    # Choose invoice type + legal notice
    if is_business:
        invoice_type = InvoiceType.FATTURA
        legal_notice = LEGAL_NOTICE_FATTURA_VAT
    else:
        invoice_type = InvoiceType.RICEVUTA
        legal_notice = LEGAL_NOTICE_RICEVUTA_OCCASIONAL

    # Sequential number
    year = datetime.now(timezone.utc).year
    seq, number = await next_invoice_number(db, provider.id, year)

    invoice = BHInvoice(
        invoice_number=number,
        invoice_type=invoice_type,
        status=InvoiceStatus.ISSUED,
        year=year,
        sequence_number=seq,
        rental_id=rental.id,
        provider_id=provider.id,
        customer_id=customer.id,
        provider_snapshot=provider_snap,
        customer_snapshot=customer_snap,
        line_items=line_items,
        subtotal_eur=subtotal,
        vat_rate=vat_rate,
        vat_amount_eur=vat_amount,
        total_eur=total,
        payment_method=payment_method,
        payment_reference=payment_reference,
        notes=notes,
        legal_notice=legal_notice,
    )
    db.add(invoice)
    await db.flush()
    await db.refresh(invoice)
    return invoice
