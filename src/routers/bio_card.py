"""Printable A6 bio postcard ("Biglietto" IT / "Bio Card" EN).

Block 5g of the share-artifact roadmap (2026-06-04). The Locandina was Block
1 of the universal pattern: a share artifact for a LISTING. The bio card is
Block 2: same skeleton, but for a MEMBER (`/u/<slug>`).

What changes vs Locandina:
  - cover photo = banner_url if set, else avatar_url, else placeholder
  - title = workshop_name OR display_name
  - byline = display_name + city (when workshop is the title) else just city
  - description = bio (verbatim <= 250 / Ollama-compressed to 300-500 else)
  - type badge = workshop_type (DOJO / STUDIO / GARDEN / LAB / etc.)
  - data ribbon = tagline OR languages OR member-since
  - QR target = /u/<slug> instead of /items/<slug>
  - avatar inline always rendered with tier ring (even when cover IS the avatar)
  - watermark hash + Bruce quote keyed on user.id

What stays:
  - 4-up A4 landscape geometry, 138.5x95mm cards, 5/10mm gutters
  - Per-card cutting ticks
  - Per-card watermark + Bruce quote inside the print area
  - STAGING stamp for staging-rendered cards
  - Pre-flight gate (image content-type + QR resolves)
  - museum mode (?style=museum)
  - Tier-light identity (avatar ring + chip)

Implementation note: helpers are imported from src.routers.locandina rather
than refactored into a shared module yet. The refactor into src/routers/share/
with Jinja inheritance is queued (see lp-share-artifact-extends-bios-and-htmls
memory) but tonight's goal is shipping the second variant cleanly. We'll
DRY it up in a follow-up once both variants are working in production.
"""

import logging
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.user import BadgeTier, BHUser, WorkshopType
from src.routers.pages._helpers import templates
# Reuse the rendering primitives from the locandina module -- single source of
# truth for QR generation, env detection, watermarking, Bruce-Lee picking,
# pre-flight validation, and the tier palette. The bio card is a different
# entity but the print discipline is identical.
from src.routers.locandina import (
    DESC_LIMIT,
    TIER_PALETTE,
    _is_staging,
    _pick_bruce_quote,
    _preflight_validate,
    _public_base,
    _qr_data_uri,
    _render_watermark,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["bio_card"])

# Wider description band for the bio card -- the bio is typically more
# personal/long than an item description and the layout (smaller photo,
# more text room) accommodates it.
BIO_DESC_LIMIT = 500


# Workshop type -> (label, accent color). Matches nav-bar palette where
# applicable; fills in sensible defaults for the legend-era types.
WORKSHOP_BADGE_EN: dict[WorkshopType, tuple[str, str]] = {
    WorkshopType.KITCHEN:     ("KITCHEN",     "#dc2626"),  # red
    WorkshopType.GARAGE:      ("GARAGE",      "#475569"),  # slate
    WorkshopType.GARDEN:      ("GARDEN",      "#16a34a"),  # green
    WorkshopType.WORKSHOP:    ("WORKSHOP",    "#2563eb"),  # blue
    WorkshopType.STUDIO:      ("STUDIO",      "#ea580c"),  # orange
    WorkshopType.OFFICE:      ("OFFICE",      "#1e3a8a"),  # navy
    WorkshopType.OTHER:       ("MEMBER",      "#64748b"),  # gray
    WorkshopType.ARENA:       ("ARENA",       "#dc2626"),  # red
    WorkshopType.CAMP:        ("CAMP",        "#16a34a"),  # green
    WorkshopType.DOCK:        ("DOCK",        "#0d9488"),  # teal
    WorkshopType.DOJO:        ("DOJO",        "#4f46e5"),  # indigo
    WorkshopType.FORGE:       ("FORGE",       "#b45309"),  # bronze
    WorkshopType.FORTRESS:    ("FORTRESS",    "#475569"),  # slate
    WorkshopType.LABORATORY:  ("LABORATORY",  "#0d9488"),  # teal
    WorkshopType.LODGE:       ("LODGE",       "#92400e"),  # brown
    WorkshopType.OBSERVATORY: ("OBSERVATORY", "#7c3aed"),  # purple
    WorkshopType.PALACE:      ("PALACE",      "#b45309"),  # gold
    WorkshopType.PAVILION:    ("PAVILION",    "#0891b2"),  # cyan
    WorkshopType.STUDY:       ("STUDY",       "#92400e"),  # brown
}

WORKSHOP_BADGE_IT: dict[WorkshopType, str] = {
    WorkshopType.KITCHEN:     "CUCINA",
    WorkshopType.GARAGE:      "GARAGE",
    WorkshopType.GARDEN:      "GIARDINO",
    WorkshopType.WORKSHOP:    "OFFICINA",
    WorkshopType.STUDIO:      "STUDIO",
    WorkshopType.OFFICE:      "UFFICIO",
    WorkshopType.OTHER:       "MEMBRO",
    WorkshopType.ARENA:       "ARENA",
    WorkshopType.CAMP:        "CAMPO",
    WorkshopType.DOCK:        "MOLO",
    WorkshopType.DOJO:        "DOJO",
    WorkshopType.FORGE:       "FORGIA",
    WorkshopType.FORTRESS:    "FORTEZZA",
    WorkshopType.LABORATORY:  "LABORATORIO",
    WorkshopType.LODGE:       "RIFUGIO",
    WorkshopType.OBSERVATORY: "OSSERVATORIO",
    WorkshopType.PALACE:      "PALAZZO",
    WorkshopType.PAVILION:    "PADIGLIONE",
    WorkshopType.STUDY:       "STUDIO",
}


def _workshop_badge(user: BHUser, lang: str) -> dict:
    """Type badge for the bio card. Falls back to MEMBER/MEMBRO if no workshop type."""
    if user.workshop_type and user.workshop_type in WORKSHOP_BADGE_EN:
        label_en, color = WORKSHOP_BADGE_EN[user.workshop_type]
        if lang == "it":
            label = WORKSHOP_BADGE_IT.get(user.workshop_type, label_en)
        else:
            label = label_en
        return {"label": label, "color": color}
    return {"label": "MEMBRO" if lang == "it" else "MEMBER", "color": "#64748b"}


def _bio_cover_url(user: BHUser) -> str | None:
    """Banner is preferred (more storefront-feel + bigger), avatar is fallback."""
    return user.banner_url or user.avatar_url or None


def _bio_title(user: BHUser) -> str:
    return user.workshop_name or user.display_name or "—"


def _bio_byline(user: BHUser) -> str:
    """When workshop_name is the title, show 'display_name . city'.
    When display_name IS the title (no workshop set), just show the city."""
    city = (user.city or "").strip()
    if user.workshop_name and user.display_name:
        if city:
            return f"{user.display_name} · {city}"
        return user.display_name
    return city or ""


def _bio_data_ribbon(user: BHUser, lang: str) -> str:
    """The bio card's type-aware data strip. Priority: tagline > languages > tier."""
    if user.tagline:
        # Tagline is the owner's chosen one-liner -- highest priority signal.
        return user.tagline.strip()
    # No tagline -- pull from member metadata.
    parts: list[str] = []
    if user.country_code:
        parts.append(f"📍 {user.country_code}")
    if user.created_at:
        year = user.created_at.year
        if lang == "it":
            parts.append(f"membro dal {year}")
        else:
            parts.append(f"member since {year}")
    return " · ".join(parts)


def _bio_tier_marker(user: BHUser | None, lang: str) -> dict:
    """Same tier-light identity logic as the Locandina (avatar ring + chip)."""
    tier = (user.badge_tier if user else None) or BadgeTier.NEWCOMER
    pal = TIER_PALETTE.get(tier, TIER_PALETTE[BadgeTier.NEWCOMER])
    chip = pal["chip_label_it"] if lang == "it" else pal["chip"]
    return {
        "slug": pal["slug"],
        "accent": pal["accent"],
        "chip": chip,
    }


async def _bio_description(
    user: BHUser,
    lang: str,
    db: AsyncSession,
) -> str:
    """Bio description block contents. Same caching + Ollama pattern as Locandina."""
    if user.bio_card_summary and user.bio_card_summary.strip():
        return user.bio_card_summary.strip()
    bio = (user.bio or "").strip()
    if not bio:
        return ""
    if len(bio) <= DESC_LIMIT:
        # Even on the bio card we keep the printable slot at DESC_LIMIT chars;
        # the BIO_DESC_LIMIT is for the Ollama target band, not the slot.
        return bio

    from src.services.llm.locandina_summary import generate_locandina_summary
    summary = await generate_locandina_summary(
        description=bio,
        story=None,
        lang=lang,
        target_min=300,
        target_max=BIO_DESC_LIMIT,
    )
    if summary:
        # Clamp to the printable slot (DESC_LIMIT) before caching so the slot
        # never overflows; the wider target_max gives Ollama latitude on word
        # boundaries.
        if len(summary) > DESC_LIMIT:
            cut = summary.rfind(" ", 0, DESC_LIMIT - 3)
            if cut > DESC_LIMIT // 2:
                summary = summary[:cut].rstrip() + "..."
            else:
                summary = summary[: DESC_LIMIT - 3].rstrip() + "..."
        user.bio_card_summary = summary
        try:
            await db.commit()
            await db.refresh(user)
        except Exception as e:
            logger.warning("bio_card_summary cache write failed: %s", e)
        return summary
    # Ollama failed -- truncation fallback.
    return bio[: DESC_LIMIT - 3].rstrip() + "..."


@router.get("/{user_id}/bio-card.pdf")
async def generate_bio_card(
    user_id: UUID,
    request: Request,
    lang: str = Query("en", pattern="^(en|it)$"),
    style: str = Query("classic", pattern="^(classic|museum)$"),
    strict: int = Query(0, ge=0, le=1),
    db: AsyncSession = Depends(get_db),
):
    """Render a member's bio card (4-up on A4 landscape) as a downloadable PDF."""
    result = await db.execute(
        select(BHUser).where(BHUser.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found")

    cover_url = _bio_cover_url(user)
    public_base = _public_base(request)
    qr_target = f"{public_base}/u/{user.slug}"

    # Pre-flight (Chuck Norris) -- validate image URLs and QR resolution
    # before WeasyPrint burns cycles + a half-rendered PDF goes out.
    avatar_url = user.avatar_url
    preflight_failures = await _preflight_validate(
        cover_url=cover_url,
        avatar_url=avatar_url,
        qr_target=qr_target,
        strict=bool(strict),
    )
    if preflight_failures:
        if strict:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Bio card pre-flight failed",
                    "failures": preflight_failures,
                    "user_id": str(user.id),
                    "user_slug": user.slug,
                },
            )
        for f in preflight_failures:
            logger.warning("bio_card pre-flight (non-strict): %s", f)

    # URL display strips scheme for visual cleanliness.
    display_host = public_base.removeprefix("https://").removeprefix("http://")

    ctx = {
        "title": _bio_title(user),
        "byline": _bio_byline(user),
        "tagline": user.tagline or "",
        "avatar_url": avatar_url,
        "cover_url": cover_url,
        "description": await _bio_description(user, lang, db),
        "qr_data_uri": _qr_data_uri(qr_target),
        "url_display": f"{display_host}/u/{user.slug}",
        "scan_me": (
            "Scansiona per il profilo — apre su La Piazza"
            if lang == "it"
            else "Scan for the full profile — opens on La Piazza"
        ),
        "type_badge": _workshop_badge(user, lang),
        "data_ribbon": _bio_data_ribbon(user, lang),
        "tier_marker": _bio_tier_marker(user, lang),
        "is_staging": _is_staging(request),
        # Watermark + Bruce-Lee both keyed on user identity (not listing) so the
        # bio card has its own unique fingerprint + collectable Bruce quote.
        # _render_watermark expects an object with .id and .updated_at -- both
        # present on BHUser, so we reuse it directly.
        "watermark": _render_watermark(user, public_base),
        "bruce_quote": _pick_bruce_quote(user),
        "is_museum": (style == "museum"),
        "lang": lang,
    }

    html = templates.get_template("bio_card/card.html").render(**ctx)

    from weasyprint import HTML  # noqa: WPS433
    pdf_bytes = HTML(string=html).write_pdf()

    filename = f"bio-card-{user.slug}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
