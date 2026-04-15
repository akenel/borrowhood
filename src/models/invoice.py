"""Invoice (Fattura/Ricevuta) model.

Generated from completed rentals/services. Snapshot-based: stores a frozen
copy of provider/customer/item info at issue time so future profile edits
don't change historical invoices.

Numbering: FT-YYYY-NNNN sequential per provider per year (resets Jan 1).
Format follows Italian small-business "ricevuta" (receipt) for personal
sellers, "fattura" with VAT for business sellers (seller_type=business).
"""

import enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class InvoiceType(str, enum.Enum):
    RICEVUTA = "ricevuta"          # Receipt (personal sellers, no VAT)
    FATTURA = "fattura"            # Invoice with VAT (business sellers)


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"                # Generated, not yet finalized
    ISSUED = "issued"              # Finalized, customer notified
    PAID = "paid"                  # Payment confirmed
    CANCELLED = "cancelled"        # Voided


class BHInvoice(BHBase, Base):
    """A formal invoice/receipt for a rental or service."""

    __tablename__ = "bh_invoice"
    __table_args__ = (
        UniqueConstraint("provider_id", "year", "sequence_number",
                         name="uq_invoice_provider_year_seq"),
    )

    # ── Identity ──
    invoice_number: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    invoice_type: Mapped[InvoiceType] = mapped_column(
        Enum(InvoiceType), default=InvoiceType.RICEVUTA, nullable=False
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.ISSUED, nullable=False, index=True
    )

    # Sequential numbering (per provider per year)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # ── Foreign keys (for joins/lookups) ──
    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=False, index=True
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # ── Snapshot fields (frozen at issue time) ──
    issue_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    provider_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    """Frozen provider details: name, business_name, vat_number, seller_type,
    address, city, country, email."""

    customer_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    """Frozen customer details: name, business_name (if any), city, country."""

    line_items: Mapped[list] = mapped_column(JSONB, nullable=False)
    """List of {description, quantity, unit_price, total} dicts."""

    # ── Money ──
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    subtotal_eur: Mapped[float] = mapped_column(Float, nullable=False)
    """Total before VAT."""

    vat_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    """VAT percentage (0 for ricevuta, 22 for fattura by default)."""

    vat_amount_eur: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_eur: Mapped[float] = mapped_column(Float, nullable=False)
    """Subtotal + VAT. The amount the customer pays."""

    # ── Payment ──
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    """e.g. 'cash', 'paypal', 'iban', 'satispay'."""
    payment_reference: Mapped[Optional[str]] = mapped_column(String(200))
    """Transaction ID, IBAN reference, etc."""
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ── Notes ──
    notes: Mapped[Optional[str]] = mapped_column(Text)
    """Free-form notes from provider (e.g. 'Thanks for your business!')."""

    # ── Compliance ──
    legal_notice: Mapped[Optional[str]] = mapped_column(Text)
    """e.g. 'Operazione effettuata ai sensi dell\\'art. 27 del DPR 600/1973'
    for ricevute under €77.47, or VAT exemption text for small businesses."""

    # ── Relationships ──
    rental: Mapped["BHRental"] = relationship(foreign_keys=[rental_id])
    provider: Mapped["BHUser"] = relationship(foreign_keys=[provider_id])
    customer: Mapped["BHUser"] = relationship(foreign_keys=[customer_id])
