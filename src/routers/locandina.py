"""Printable A6 event flyer ("Locandina" IT / "Flyer" EN).

Block 2 (this commit): skeleton -- ONE good PDF downloads, with stub content
laid out at the correct A4-landscape 4-up geometry. Visit the URL, get a
real PDF, print on plain paper, confirm scissors-cuts work. That's the
milestone.

Later blocks wire:
- Block 3: real QR (qrcode lib), real cover photo, real fields, "Scan me" microcopy
- Block 4: Ollama-Turbo AI summary + editable textarea
- Block 5: pdftoppm PNG preview for mobile-friendly in-page rendering
- Block 6: language picker, print-instructions panel, slug-named filename
"""

from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.user import BHUser
from src.routers.pages._helpers import templates  # reuse the same Jinja env the page routers use

router = APIRouter(prefix="/api/v1/listings", tags=["locandina"])


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
            selectinload(BHListing.item)
            .selectinload(BHItem.owner)
        )
        .where(BHListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing or listing.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Listing not found")

    item: BHItem = listing.item
    if item is None or item.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Listing has no item")

    owner: BHUser = item.owner
    byline = (owner.workshop_name or owner.display_name) if owner else ""

    # Block-2 stub. Real fields wired in Block 3.
    ctx = {
        "title": item.name,
        "schedule_summary": listing.schedule_summary or ("Programma da definire" if lang == "it" else "Schedule TBD"),
        "byline": byline,
        "url_canonical": f"lapiazza.app/items/{item.slug}",
        "scan_me": "Scansiona per i dettagli — apre su La Piazza" if lang == "it" else "Scan for full details — opens on La Piazza",
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
