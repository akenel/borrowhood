"""Printable A6 share card ("Locandina" IT / "Flyer" EN) -- universal mode.

Block 2: skeleton -- ONE good PDF downloads at A4-landscape 4-up geometry. DONE.
Block 3: design pass -- bg wash, real photo, avatar inline with byline, real QR,
         description block (verbatim <=250 / truncated stub). DONE.
Block 5b (this commit): universal mode -- the locandina is no longer
         events-only. It's THE share artifact for any ListingType (event,
         raffle, giveaway, rental, sale, service, training, auction,
         commission, offer). See lp-locandina-universal-share-artifact
         memory for the why.

         Two new regions: a TYPE BADGE in the top-right corner (color + label
         matching nav-bar taxonomy) and a DATA RIBBON between the description
         and QR row carrying type-appropriate fields (price, deposit, dates,
         participants, etc.). Schedule line collapses for non-event types.

Later blocks wire:
- Block 4: Ollama-Turbo AI summary cached on bh_listing.locandina_summary
- Block 5c: real cover image fallback (placeholder is fine for now)
- Block 6: pdftoppm PNG preview for mobile-friendly in-page rendering
- Block 7: language picker, print-instructions panel, slug-named filename
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
from src.models.listing import BHListing, ListingType
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


# Type badge taxonomy (top-right corner of card). Colors are print-safe
# hexes matching the nav-bar palette so the printed card carries the brand
# language. Label is uppercase + bilingual fallback.
TYPE_BADGE_EN: dict[ListingType, tuple[str, str]] = {
    ListingType.EVENT:      ("EVENT",      "#2563eb"),  # blue
    ListingType.RAFFLE:     ("RAFFLE",     "#7c3aed"),  # purple
    ListingType.GIVEAWAY:   ("FREE",       "#16a34a"),  # green
    ListingType.RENT:       ("FOR RENT",   "#ea580c"),  # orange
    ListingType.SELL:       ("FOR SALE",   "#dc2626"),  # red
    ListingType.SERVICE:    ("SERVICE",    "#0d9488"),  # teal
    ListingType.TRAINING:   ("TRAINING",   "#4f46e5"),  # indigo
    ListingType.AUCTION:    ("AUCTION",    "#d97706"),  # amber
    ListingType.COMMISSION: ("COMMISSION", "#475569"),  # slate
    ListingType.OFFER:      ("MAKE OFFER", "#64748b"),  # gray
}

TYPE_BADGE_IT: dict[ListingType, str] = {
    ListingType.EVENT:      "EVENTO",
    ListingType.RAFFLE:     "RAFFLE",
    ListingType.GIVEAWAY:   "GRATIS",
    ListingType.RENT:       "IN AFFITTO",
    ListingType.SELL:       "IN VENDITA",
    ListingType.SERVICE:    "SERVIZIO",
    ListingType.TRAINING:   "FORMAZIONE",
    ListingType.AUCTION:    "ASTA",
    ListingType.COMMISSION: "SU COMMISSIONE",
    ListingType.OFFER:      "FAI UN'OFFERTA",
}


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


def _type_badge(listing: BHListing, lang: str) -> dict:
    """Return {label, color} for the top-right type indicator.

    EVENT + price=0 is rendered as "EVENT (FREE)" with a free-marker in the
    ribbon -- we keep the type as EVENT in the badge itself because that's
    still the more useful identifier. GIVEAWAY badges as "FREE" / "GRATIS"
    since by definition that's the type's whole point.
    """
    label_en, color = TYPE_BADGE_EN.get(listing.listing_type, ("LISTING", "#475569"))
    if lang == "it":
        label = TYPE_BADGE_IT.get(listing.listing_type, "ANNUNCIO")
    else:
        label = label_en
    return {"label": label, "color": color}


def _euro(amount) -> str:
    """Format a euro amount without decimals when whole, with decimals when not.
    €15 (whole) -- €12.50 (fractional)."""
    if amount is None:
        return ""
    val = float(amount)
    if val == int(val):
        return f"€{int(val)}"
    return f"€{val:.2f}"


def _is_free(listing: BHListing) -> bool:
    """True if listing should display a FREE marker (giveaway, or 0-priced event/training)."""
    if listing.listing_type == ListingType.GIVEAWAY:
        return True
    if listing.listing_type in (ListingType.EVENT, ListingType.TRAINING, ListingType.SERVICE):
        if listing.price is None or float(listing.price) == 0.0:
            return True
    return False


def _data_ribbon(listing: BHListing, lang: str) -> str:
    """Build the 1-line data ribbon (between description and QR).

    Type-aware: shows price/deposit/dates/participants appropriate to the
    ListingType. Returns "" if nothing meaningful to display -- the
    template collapses the ribbon strip when empty.
    """
    lt = listing.listing_type
    parts: list[str] = []

    # Translations -- keep small + hand-rolled (no full i18n yet for ribbon).
    is_it = lang == "it"
    t = {
        "free": "GRATIS" if is_it else "FREE",
        "free_fc": "GRATIS — primo arrivato" if is_it else "FREE — first come",
        "deposit": "cauzione" if is_it else "deposit",
        "min": "min" if is_it else "min",
        "max": "max" if is_it else "max",
        "day": "giorno" if is_it else "day",
        "days": "giorni" if is_it else "days",
        "hour": "ora" if is_it else "hour",
        "person": "persona" if is_it else "person",
        "people": "persone" if is_it else "people",
        "draw": "Estrazione" if is_it else "Draw",
        "ends": "Termina" if is_it else "Ends",
        "starting": "Partenza" if is_it else "Starting",
        "from": "Da" if is_it else "From",
        "mto": "Su commissione" if is_it else "Made to order",
        "make_offer": "Fai un'offerta" if is_it else "Make an offer",
        "venue": None,  # rendered without prefix
    }

    if lt == ListingType.EVENT:
        # Prefer real event_start over schedule_summary in the ribbon -- the
        # schedule line in the header already has the human text.
        if listing.event_start:
            fmt = "%d %b %H:%M"
            parts.append(listing.event_start.strftime(fmt))
        if listing.event_venue:
            parts.append(listing.event_venue)
        if listing.max_participants:
            label = t["person"] if listing.max_participants == 1 else t["people"]
            parts.append(f"{t['max']} {listing.max_participants} {label}")
        if _is_free(listing):
            parts.append(t["free"])
        elif listing.price:
            parts.append(_euro(listing.price))

    elif lt == ListingType.RAFFLE:
        if listing.price:
            parts.append(f"{_euro(listing.price)}/ticket")
        if listing.auction_end:
            parts.append(f"{t['draw']} {listing.auction_end.strftime('%d %b')}")

    elif lt == ListingType.GIVEAWAY:
        parts.append(t["free_fc"])

    elif lt == ListingType.RENT:
        if listing.price:
            unit = (listing.price_unit or "per_day").lower()
            unit_label = {
                "per_day": f"/{t['day']}",
                "per_hour": f"/{t['hour']}",
                "flat": "",
                "negotiable": "",
            }.get(unit, "")
            parts.append(f"{_euro(listing.price)}{unit_label}")
        if listing.deposit:
            parts.append(f"{_euro(listing.deposit)} {t['deposit']}")
        if listing.min_rental_days:
            day_label = t["day"] if listing.min_rental_days == 1 else t["days"]
            parts.append(f"{t['min']} {listing.min_rental_days} {day_label}")

    elif lt == ListingType.SELL:
        if listing.price:
            parts.append(_euro(listing.price))

    elif lt == ListingType.SERVICE:
        if _is_free(listing):
            parts.append(t["free"])
        elif listing.price:
            unit = (listing.price_unit or "per_hour").lower()
            unit_label = {
                "per_hour": f"/{t['hour']}",
                "per_day": f"/{t['day']}",
                "flat": "",
            }.get(unit, "")
            parts.append(f"{_euro(listing.price)}{unit_label}")
        if listing.minimum_charge:
            parts.append(f"{t['min']} {_euro(listing.minimum_charge)}")

    elif lt == ListingType.TRAINING:
        if _is_free(listing):
            parts.append(t["free"])
        elif listing.per_person_rate:
            parts.append(f"{_euro(listing.per_person_rate)}/{t['person']}")
        elif listing.price:
            parts.append(_euro(listing.price))
        if listing.max_participants:
            label = t["person"] if listing.max_participants == 1 else t["people"]
            parts.append(f"{t['max']} {listing.max_participants} {label}")

    elif lt == ListingType.AUCTION:
        if listing.starting_bid:
            parts.append(f"{t['starting']} {_euro(listing.starting_bid)}")
        if listing.auction_end:
            parts.append(f"{t['ends']} {listing.auction_end.strftime('%d %b %H:%M')}")

    elif lt == ListingType.COMMISSION:
        if listing.price:
            parts.append(f"{t['from']} {_euro(listing.price)}")
        else:
            parts.append(t["mto"])

    elif lt == ListingType.OFFER:
        parts.append(t["make_offer"])

    return " · ".join(parts)


def _schedule_text(listing: BHListing, lang: str) -> str | None:
    """The header schedule line. Only meaningful for events; None hides the line.

    Priority:
      1. owner-typed schedule_summary (verbatim, what they want on the card)
      2. derived from event_start (formatted)
      3. None -- hide the line entirely for non-events / no data
    """
    if listing.listing_type != ListingType.EVENT:
        return None
    if listing.schedule_summary:
        return listing.schedule_summary
    if listing.event_start:
        # "Sab 14 Jun, 15:00" -- short weekday + day + month + time
        return listing.event_start.strftime("%a %d %b, %H:%M")
    return "Programma da definire" if lang == "it" else "Schedule TBD"


@router.get("/{listing_id}/locandina.pdf")
async def generate_locandina(
    listing_id: UUID,
    lang: str = Query("en", pattern="^(en|it)$"),
    db: AsyncSession = Depends(get_db),
):
    """Render an A6-ish share card (4-up on A4 landscape) as a downloadable PDF.

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
        "schedule_text": _schedule_text(listing, lang),
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
        "type_badge": _type_badge(listing, lang),
        "data_ribbon": _data_ribbon(listing, lang),
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
