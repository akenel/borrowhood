"""Printable A6 event flyer ("Locandina" IT / "Flyer" EN).

Block 2: skeleton -- ONE good PDF downloads, with stub content laid out at the
correct A4-landscape 4-up geometry. DONE.

Block 3 (this commit): design pass.
- Real cover photo (first PHOTO media, fallback gradient placeholder)
- Cover image full-bleed at 12% opacity as background wash (Angel's idea)
- Owner avatar INLINE with byline (option B -- never overlaps photo content)
- Real QR via qrcode lib, embedded as data: URI
- Description block: verbatim if <=250 chars, stub-truncated otherwise
  (Block 4 will replace stub with Ollama Turbo compression)

Later blocks wire:
- Block 4: Ollama-Turbo AI summary cached on bh_listing.locandina_summary
- Block 5: pdftoppm PNG preview for mobile-friendly in-page rendering
- Block 6: language picker, print-instructions panel, slug-named filename
"""

import base64
from io import BytesIO
from uuid import UUID

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.item import BHItem, BHItemMedia, MediaType
from src.models.listing import BHListing
from src.models.user import BHUser
from src.routers.pages._helpers import templates

router = APIRouter(prefix="/api/v1/listings", tags=["locandina"])

# Public-facing canonical host. The QR scans to prod regardless of which
# env rendered the PDF: a flyer in someone's hand should land them on the
# real site, not a staging URL that may not exist tomorrow.
PUBLIC_BASE = "https://lapiazza.app"

# Description-block threshold. <= this many chars: print verbatim. Over:
# stub-truncate in Block 3, real Ollama Turbo compression in Block 4.
DESC_LIMIT = 250


def _qr_data_uri(target_url: str) -> str:
    """Generate a QR PNG and return it as a data: URI for inline embed."""
    img = qrcode.make(target_url, box_size=10, border=2)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _description_short(item: BHItem) -> str:
    """Return the description block contents.

    Block 3 rules (from feedback-locandina-description-block memory):
      - description <= DESC_LIMIT chars: verbatim.
      - description >  DESC_LIMIT chars: truncated stub (Block 4 swaps in
        Ollama Turbo compression).
      - description NULL: empty string (the slot collapses gracefully).
    """
    desc = (item.description or "").strip()
    if not desc:
        return ""
    if len(desc) <= DESC_LIMIT:
        return desc
    # Block-4 STUB. Replace with _ollama_generate(desc + story) once wired.
    return desc[: DESC_LIMIT - 3].rstrip() + "..."


def _cover_url(item: BHItem) -> str | None:
    """First PHOTO media URL, or None if the item has no photo."""
    for m in (item.media or []):
        if m.media_type == MediaType.PHOTO and m.url:
            return m.url
    return None


def _byline(owner: BHUser | None) -> str:
    """Storefront/display name + city -- 'Nic's Dojo · Trapani'."""
    if not owner:
        return ""
    name = owner.workshop_name or owner.display_name or ""
    city = (owner.city or "").strip()
    if name and city:
        return f"{name} · {city}"
    return name or city


@router.get("/{listing_id}/locandina.pdf")
async def generate_locandina(
    listing_id: UUID,
    lang: str = Query("en", pattern="^(en|it)$"),
    db: AsyncSession = Depends(get_db),
):
    """Render an A6-ish event card (4-up on A4 landscape) as a downloadable PDF.

    Pure GET, no auth required: anyone with the link can print -- the QR they
    scan will land them on the public item page, no login needed (same
    pattern as the existing per-item QR PNG).
    """
    result = await db.execute(
        select(BHListing)
        .options(
            selectinload(BHListing.item).selectinload(BHItem.owner),
            selectinload(BHListing.item).selectinload(BHItem.media),
        )
        .where(BHListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing or listing.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Listing not found")

    item: BHItem = listing.item
    if item is None or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Listing has no item")

    owner: BHUser | None = item.owner
    cover_url = _cover_url(item)
    qr_target = f"{PUBLIC_BASE}/items/{item.slug}"

    ctx = {
        "title": item.name,
        "schedule_summary": listing.schedule_summary or (
            "Programma da definire" if lang == "it" else "Schedule TBD"
        ),
        "byline": _byline(owner),
        "avatar_url": (owner.avatar_url if owner else None),
        "cover_url": cover_url,
        "description": _description_short(item),
        "qr_data_uri": _qr_data_uri(qr_target),
        "url_display": f"lapiazza.app/items/{item.slug}",
        "scan_me": (
            "Scansiona per i dettagli — apre su La Piazza"
            if lang == "it"
            else "Scan for full details — opens on La Piazza"
        ),
        "lang": lang,
    }

    html = templates.get_template("locandina/card.html").render(**ctx)

    # WeasyPrint imported at call-time so missing system libs surface a clear
    # error on the first request rather than at module import / app boot.
    from weasyprint import HTML  # noqa: WPS433
    pdf_bytes = HTML(string=html).write_pdf()

    filename = f"locandina-{item.slug}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{filename}\""},
    )
