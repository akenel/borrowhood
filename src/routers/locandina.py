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
import logging
import os
from io import BytesIO
from uuid import UUID

import qrcode

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.item import BHItem, BHItemMedia, MediaType
from src.models.listing import BHListing, ListingType
from src.models.user import BadgeTier, BHUser
from src.routers.pages._helpers import templates

router = APIRouter(prefix="/api/v1/listings", tags=["locandina"])

# Hard fallback only -- DO NOT hardcode this for the URL itself. The card
# must point at the env that rendered it so testers can verify their own
# locandinas (staging cards -> staging.lapiazza.app, prod cards ->
# lapiazza.app). See _public_base() below.
PUBLIC_BASE_DEFAULT = "https://lapiazza.app"


async def _preflight_validate(
    cover_url: str | None,
    avatar_url: str | None,
    qr_target: str,
    strict: bool,
) -> list[str]:
    """Chuck Norris validator -- run BEFORE WeasyPrint to catch silent fails.

    Returns a list of human-readable failure strings. Empty list = OK to render.

    Checks (all parallel via asyncio.gather to stay fast):
      1. cover_url (if set) returns HTTP 200 + image/* content-type
      2. avatar_url (if set) returns HTTP 200 + image/* content-type
      3. qr_target resolves (HEAD or GET 200 / redirect)

    Codifies the second-arrow lesson at the API layer. The Pollinations 402,
    the env-URL 404, the staging stamp clipped text -- all silent fails that
    a pre-flight check would have caught before serving a broken PDF.

    Honors the "lean hard but don't fail closed silently" rule
    ([[feedback-lean-hard-on-ollama-summarization]]): in strict=False mode
    (default for prod), failures are warnings -- the PDF still renders with
    fallback placeholders. In strict=True (override via ?strict=1), failures
    return 503 with the list. Use strict in CI / pre-deploy smoke tests.
    """
    import asyncio
    import httpx
    failures: list[str] = []

    async def check_image(label: str, url: str | None) -> None:
        if not url:
            return
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                # HEAD first (cheap); some CDNs reject HEAD so fall back to GET range.
                try:
                    resp = await client.head(url)
                except httpx.HTTPError:
                    resp = await client.get(url, headers={"Range": "bytes=0-1"})
                if resp.status_code >= 400:
                    failures.append(f"{label}: HTTP {resp.status_code} from {url[:80]}")
                    return
                ctype = (resp.headers.get("content-type") or "").lower()
                if not ctype.startswith("image/"):
                    failures.append(
                        f"{label}: content-type '{ctype[:40]}' is not image/* "
                        f"(silent-fail trap; URL: {url[:60]})"
                    )
        except Exception as e:
            failures.append(f"{label}: fetch failed -- {type(e).__name__}: {str(e)[:80]}")

    async def check_qr_target() -> None:
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=False, verify=False) as client:
                resp = await client.head(qr_target)
                if resp.status_code >= 500:
                    failures.append(f"qr_target: HTTP {resp.status_code} -- public item page broken")
                # 404 on the QR target IS a real problem (printed cards lead to dead pages)
                elif resp.status_code == 404:
                    failures.append(f"qr_target: 404 -- printed QR will land on a dead page")
        except Exception as e:
            failures.append(f"qr_target: fetch failed -- {type(e).__name__}: {str(e)[:80]}")

    await asyncio.gather(
        check_image("cover_url", cover_url),
        check_image("avatar_url", avatar_url),
        check_qr_target(),
    )
    return failures


def _public_base(request: Request) -> str:
    """Origin the locandina's QR + URL line point to.

    Priority order:
      1. BH_PUBLIC_BASE env var if explicitly set (e.g. "https://lapiazza.app"
         on staging if you intentionally want staging cards to point at prod).
      2. Derive from the request: scheme + host. Auto-correct per env.
         Staging-rendered cards -> staging.lapiazza.app; prod -> lapiazza.app;
         local dev -> https://helix.local. Each card is verifiable in the env
         that rendered it without ever hardcoding a host in the codebase.
      3. Hard fallback to PUBLIC_BASE_DEFAULT if request had no host header
         (shouldn't happen behind Caddy, but a safety net).

    Previously this was hardcoded to "https://lapiazza.app" which made every
    staging-rendered card link to prod -- where the seeded test items don't
    exist -- so anyone testing the printed URL got a 404. (Angel hit this
    on 2026-06-03 testing the Jiu-Jitsu workshop card.)
    """
    explicit = os.environ.get("BH_PUBLIC_BASE", "").strip()
    if explicit:
        return explicit.rstrip("/")
    # Trust forwarded headers from Caddy/Traefik (see Public Access memory).
    scheme = request.url.scheme
    netloc = request.url.netloc
    if netloc:
        return f"{scheme}://{netloc}"
    return PUBLIC_BASE_DEFAULT


# Bruce Lee Easter egg quotes (bonus #11 from the spec). Each listing
# deterministically picks one based on its id hash so the same card always
# carries the same quote -- reproducible, collectable, brand-coherent.
# Curated for printability: short (<= 65 chars), Eastern philosophy, applicable
# to the kind of work La Piazza members do (skill, patience, water, fire).
BRUCE_LEE_QUOTES: tuple[str, ...] = (
    "Be water, my friend.",
    "Empty your cup so that it may be filled.",
    "Do not pray for an easy life; pray for the strength to endure.",
    "Knowing is not enough, we must apply.",
    "If you spend too much time thinking, you'll never get it done.",
    "Mistakes are always forgivable, if one has the courage to admit them.",
    "Absorb what is useful, discard what is useless.",
    "Take no thought of who is right or wrong. Produce greater results.",
    "A goal is not always meant to be reached, often it serves as something to aim at.",
    "The successful warrior is the average man, with laser-like focus.",
    "Showing off is the fool's idea of glory.",
    "I fear not the man who has practiced 10,000 kicks once.",
    "Real living is living for others.",
    "Notice that the stiffest tree is most easily cracked, while the bamboo bends with the wind.",
)


def _pick_bruce_quote(listing: BHListing) -> str:
    """Deterministic Bruce Lee quote pick based on listing id hash.
    Same listing -> same quote across renders, so collectors can chase variants."""
    import hashlib
    seed = hashlib.sha1(str(listing.id).encode("utf-8")).digest()
    idx = seed[0] % len(BRUCE_LEE_QUOTES)
    return BRUCE_LEE_QUOTES[idx]


def _render_watermark(listing: BHListing, public_base: str) -> str:
    """Render the cryptic sheet-level watermark Angel calls the Banksy mark.

    Format:  LP . YYYY-MM-DD . <hash4>

    The hash4 is the first 4 hex chars of SHA1(public_base + listing.id +
    listing.updated_at). Three properties matter:
      - Reproducible: same card re-rendered same day = same hash. Print twice,
        you can prove they're the same print run.
      - Cheap to verify: a future /verify/<hash> endpoint can answer "yes,
        this is a real La Piazza card rendered on date X by listing Y."
      - Cryptic but not secret: anyone CAN reverse it given inputs; the
        point is anti-fraud authentication ("is this card a real LP card
        or a phishing knock-off?"), not protecting the inputs.

    Uses listing.updated_at (NOT NOW()) so re-renders of an unchanged card
    are stable. Falls back to the listing.id if updated_at is missing.
    """
    import hashlib
    seed = f"{public_base}|{listing.id}|{listing.updated_at or listing.id}"
    h4 = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:4]
    # Date stable per-listing: use updated_at if present, else "----".
    date_str = listing.updated_at.strftime("%Y-%m-%d") if listing.updated_at else "----"
    return f"LP · {date_str} · {h4}"


def _is_staging(request: Request) -> bool:
    """True if this card is being rendered from the staging env.

    Used to stamp a big diagonal "STAGING -- DO NOT DISTRIBUTE" watermark
    across the card so a tester can never accidentally hand a staging-rendered
    card to a real customer. Even if they did, the stamp screams "test."

    Detection follows the same source-of-truth as _public_base:
      1. If BH_PUBLIC_BASE explicitly contains 'staging', it's staging.
      2. Otherwise check the request hostname for 'staging.'.
    """
    base = _public_base(request).lower()
    return "staging" in base

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


async def _description_short(
    item: BHItem,
    listing: BHListing,
    lang: str,
    db: AsyncSession,
) -> str:
    """Return the description block contents.

    Rules (from feedback-locandina-description-block memory + Block 4):
      1. listing.locandina_summary set (cache hit): use it verbatim.
      2. description <= DESC_LIMIT chars: verbatim (no AI needed).
      3. description > DESC_LIMIT chars: call Ollama Turbo to compress to
         200-250 chars, cache on listing.locandina_summary, return.
      4. Ollama unreachable / fails: fall back to truncation stub.
      5. description NULL: empty string (the slot collapses gracefully).
    """
    # Cache hit -- owner already has an AI summary or hand-edited version.
    if listing.locandina_summary and listing.locandina_summary.strip():
        return listing.locandina_summary.strip()

    desc = (item.description or "").strip()
    if not desc:
        return ""
    if len(desc) <= DESC_LIMIT:
        return desc

    # Cache miss + over the limit: call Ollama Turbo.
    from src.services.llm.locandina_summary import generate_locandina_summary
    summary = await generate_locandina_summary(
        description=desc,
        story=(item.story or None),
        lang=lang,
        target_min=200,
        target_max=DESC_LIMIT,
    )
    if summary:
        # Cache for future renders. Commit immediately so concurrent re-renders
        # don't re-spend Ollama calls. Owner-edit path will clear/overwrite.
        listing.locandina_summary = summary
        try:
            await db.commit()
            await db.refresh(listing)
        except Exception as e:
            # Cache write failed -- still serve the summary for this render.
            logger.warning("locandina_summary cache write failed: %s", e)
        return summary

    # Ollama unreachable / failed -- last-resort truncation stub.
    return desc[: DESC_LIMIT - 3].rstrip() + "..."


def _cover_url(item: BHItem) -> str | None:
    """First PHOTO media URL, or None if the item has no photo."""
    for m in (item.media or []):
        if m.media_type == MediaType.PHOTO and m.url:
            return m.url
    return None


def _tag_chips(item: BHItem, max_chips: int = 5) -> list[str]:
    """Split item.tags (comma-separated text) into a clean list of chip labels.

    The card has room for 4-5 chips at the top; clip to that to avoid wrapping
    into the description slot. Trim, dedupe, drop empties.
    """
    raw = (item.tags or "").strip()
    if not raw:
        return []
    seen: set[str] = set()
    chips: list[str] = []
    # Split on comma OR semicolon (some old seeds used ; -- be tolerant).
    for part in raw.replace(";", ",").split(","):
        chip = part.strip()
        if not chip:
            continue
        key = chip.lower()
        if key in seen:
            continue
        seen.add(key)
        chips.append(chip)
        if len(chips) >= max_chips:
            break
    return chips


# Attribute keys we surface on the card as Grandma-context hints. Keyed by
# category group; falls back to nothing if the category isn't in the map.
# Display labels are bilingual; the VALUE comes from item.attributes as-is.
ATTRIBUTE_HINTS: dict[str, list[tuple[str, str, str]]] = {
    # group -> list of (json_key, EN label, IT label)
    "events": [
        ("skill_level",      "level",       "livello"),
        ("age_requirement",  "ages",        "età"),
        ("what_to_bring",    "bring",       "porta"),
    ],
    "vehicles": [
        ("year",             "year",        "anno"),
        ("fuel_type",        "fuel",        "carburante"),
        ("transmission",     "trans",       "cambio"),
    ],
    "property": [
        ("bedrooms",         "br",          "loc"),
        ("bathrooms",        "ba",          "bagni"),
        ("floor_area_sqm",   "m²",     "m²"),
    ],
}


def _grandma_hints(item: BHItem, lang: str) -> list[str]:
    """Pull a few item.attributes into short display strings so a viewer who
    doesn't know La Piazza can still parse what kind of thing this is.

    Examples produced:
        events:    "level Beginner", "bring brushes", "ages 18+"
        vehicles:  "year 2020", "fuel diesel"
        property:  "br 3", "ba 2", "m² 95"

    Falls back to empty list when the item has no attributes or the category
    has no hint mapping. Pure formatting -- no API calls, no DB writes.
    """
    attrs = item.attributes or {}
    if not isinstance(attrs, dict) or not attrs:
        return []
    category = (item.category or "").lower()
    # Resolve which group this category belongs to.
    from src.models.item import CATEGORY_GROUPS
    group = None
    for grp_name, cats in CATEGORY_GROUPS.items():
        if category in cats:
            group = grp_name
            break
    hints_def = ATTRIBUTE_HINTS.get(group or "", [])
    out: list[str] = []
    for key, en_label, it_label in hints_def:
        val = attrs.get(key)
        if val is None or val == "" or val is False:
            continue
        label = it_label if lang == "it" else en_label
        # Truncate long string values so they don't break the ribbon.
        sval = str(val).strip()
        if len(sval) > 18:
            sval = sval[:15].rstrip() + "..."
        out.append(f"{label} {sval}")
        if len(out) >= 3:
            break
    return out


def _byline(owner: BHUser | None) -> str:
    """Storefront/display name + city -- 'Nic's Dojo · Trapani'."""
    if not owner:
        return ""
    name = owner.workshop_name or owner.display_name or ""
    city = (owner.city or "").strip()
    if name and city:
        return f"{name} · {city}"
    return name or city


# Tier-light identity palette (Block 5d, Angel's "Leonardo card vs newcomer
# card should LOOK different" rule). Each tier carries:
#   - a `slug` for the CSS class (.tier-newcomer, .tier-legend, ...)
#   - an `accent` color for the avatar ring
#   - a `chip` label (None = don't show a chip)
#
# NEWCOMER intentionally has no chip -- not bragging about being new is part
# of the welcome. ACTIVE gets a humble chip; TRUSTED+ get progressively
# more presence; LEGEND gets the apex gold + a star.
TIER_PALETTE: dict[BadgeTier, dict] = {
    BadgeTier.NEWCOMER: {"slug": "newcomer", "accent": "#64748b", "chip": None,             "chip_label_it": None},
    BadgeTier.ACTIVE:   {"slug": "active",   "accent": "#0d9488", "chip": "ACTIVE",         "chip_label_it": "ATTIVO"},
    BadgeTier.TRUSTED:  {"slug": "trusted",  "accent": "#4338ca", "chip": "TRUSTED",        "chip_label_it": "FIDATO"},
    BadgeTier.PILLAR:   {"slug": "pillar",   "accent": "#7c3aed", "chip": "◆ PILLAR",       "chip_label_it": "◆ PILASTRO"},
    BadgeTier.LEGEND:   {"slug": "legend",   "accent": "#b45309", "chip": "✦ LEGEND",       "chip_label_it": "✦ LEGGENDA"},
}


def _tier_marker(owner: BHUser | None, lang: str) -> dict:
    """Return {slug, accent, chip} for the owner's tier-light identity.

    Used to:
      - colour the avatar ring (always rendered, even for Newcomers, so the
        tier signal is subtle but ever-present)
      - render a small chip beside the byline (ACTIVE+ only -- Newcomers
        don't brag about being new)

    Falls back to the Newcomer palette if the owner has no tier (shouldn't
    happen with the schema default, but safety).
    """
    tier = (owner.badge_tier if owner else None) or BadgeTier.NEWCOMER
    pal = TIER_PALETTE.get(tier, TIER_PALETTE[BadgeTier.NEWCOMER])
    chip = pal["chip_label_it"] if lang == "it" else pal["chip"]
    return {
        "slug": pal["slug"],
        "accent": pal["accent"],
        "chip": chip,
    }


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
        "session": "sessione" if is_it else "session",
        "person": "persona" if is_it else "person",
        "people": "persone" if is_it else "people",
        "draw": "Estrazione" if is_it else "Draw",
        "ends": "Termina" if is_it else "Ends",
        "starting": "Partenza" if is_it else "Starting",
        "from": "Da" if is_it else "From",
        "mto": "Su commissione" if is_it else "Made to order",
        "make_offer": "Fai un'offerta" if is_it else "Make an offer",
        "group_off": "sconto gruppo" if is_it else "group off",
        "venue": None,  # rendered without prefix
    }

    # Helper -- format a price + price_unit cleanly. "€18/session", "€15/day",
    # "€20/hour", "€50/person", or just "€120" for flat/sale.
    def _price_with_unit(price, unit_raw: str | None, default_unit: str = "session") -> str:
        if price is None:
            return ""
        unit = (unit_raw or "").lower()
        unit_map = {
            "per_hour":    f"/{t['hour']}",
            "per_day":     f"/{t['day']}",
            "per_session": f"/{t['session']}",
            "per_person":  f"/{t['person']}",
            "flat":        "",
            "negotiable":  "",
        }
        suffix = unit_map.get(unit, f"/{t[default_unit]}" if default_unit in t else "")
        return f"{_euro(price)}{suffix}"

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
        elif listing.per_person_rate:
            parts.append(f"{_euro(listing.per_person_rate)}/{t['person']}")
        elif listing.price:
            parts.append(_price_with_unit(listing.price, listing.price_unit, "person"))

    elif lt == ListingType.RAFFLE:
        if listing.price:
            parts.append(f"{_euro(listing.price)}/ticket")
        if listing.auction_end:
            parts.append(f"{t['draw']} {listing.auction_end.strftime('%d %b')}")

    elif lt == ListingType.GIVEAWAY:
        parts.append(t["free_fc"])

    elif lt == ListingType.RENT:
        if listing.price:
            parts.append(_price_with_unit(listing.price, listing.price_unit, "day"))
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
            parts.append(_price_with_unit(listing.price, listing.price_unit, "hour"))
        if listing.minimum_charge:
            parts.append(f"{t['min']} {_euro(listing.minimum_charge)}")
        if listing.group_discount_pct:
            parts.append(f"-{int(listing.group_discount_pct)}% {t['group_off']}")

    elif lt == ListingType.TRAINING:
        if _is_free(listing):
            parts.append(t["free"])
        elif listing.per_person_rate:
            parts.append(f"{_euro(listing.per_person_rate)}/{t['person']}")
        elif listing.price:
            parts.append(_price_with_unit(listing.price, listing.price_unit, "session"))
        if listing.max_participants:
            label = t["person"] if listing.max_participants == 1 else t["people"]
            parts.append(f"{t['max']} {listing.max_participants} {label}")
        if listing.group_discount_pct:
            parts.append(f"-{int(listing.group_discount_pct)}% {t['group_off']}")

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
    request: Request,
    lang: str = Query("en", pattern="^(en|it)$"),
    style: str = Query("classic", pattern="^(classic|museum)$"),
    strict: int = Query(0, ge=0, le=1),
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
    public_base = _public_base(request)
    qr_target = f"{public_base}/items/{item.slug}"

    # Chuck Norris pre-flight gate (Block 5e, 2026-06-04). Validates external
    # URLs return real images and the QR target isn't a 404 BEFORE we burn
    # WeasyPrint cycles + serve a half-rendered PDF. In strict=1 mode (CI /
    # pre-deploy smoke), failures return 503 with the list. In default mode,
    # failures log warnings and the PDF renders with whatever fell through
    # (Block 3's placeholder gradient + monogram fallback are designed for
    # exactly this case).
    avatar_url = owner.avatar_url if owner else None
    preflight_failures = await _preflight_validate(
        cover_url=cover_url,
        avatar_url=avatar_url,
        qr_target=qr_target,
        strict=bool(strict),
    )
    if preflight_failures:
        if strict:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Locandina pre-flight failed",
                    "failures": preflight_failures,
                    "listing_id": str(listing.id),
                    "item_slug": item.slug,
                },
            )
        for f in preflight_failures:
            logger.warning("locandina pre-flight (non-strict): %s", f)

    # The displayed URL line below the QR drops the scheme for visual
    # cleanliness: "staging.lapiazza.app/items/<slug>" or "lapiazza.app/...".
    display_host = public_base.removeprefix("https://").removeprefix("http://")

    ctx = {
        "title": item.name,
        "schedule_text": _schedule_text(listing, lang),
        "byline": _byline(owner),
        "avatar_url": (owner.avatar_url if owner else None),
        "cover_url": cover_url,
        "description": await _description_short(item, listing, lang, db),
        "qr_data_uri": _qr_data_uri(qr_target),
        "url_display": f"{display_host}/items/{item.slug}",
        "scan_me": (
            "Scansiona per i dettagli — apre su La Piazza"
            if lang == "it"
            else "Scan for full details — opens on La Piazza"
        ),
        "type_badge": _type_badge(listing, lang),
        # Phase 1.5 Grandma context (2026-06-04): item.tags become a chip row
        # above the description; item.attributes (skill_level, what_to_bring,
        # condition, etc.) get appended to the data ribbon as small hints so
        # a viewer who doesn't know La Piazza can parse the listing at first
        # glance. Both sourced from existing DB columns -- no new schema.
        "data_ribbon": " · ".join(filter(None, [
            _data_ribbon(listing, lang),
            *_grandma_hints(item, lang),
        ])),
        "tag_chips": _tag_chips(item),
        "tier_marker": _tier_marker(owner, lang),
        "is_staging": _is_staging(request),
        "watermark": _render_watermark(listing, public_base),
        # Bonus #11 -- Bruce Lee quote, deterministic per-listing, always rendered
        # but in micro-type along the gutter edge. Fans find them on closer look.
        "bruce_quote": _pick_bruce_quote(listing),
        # Bonus #12 -- ?style=museum strips chrome (badge / ribbon / scan-me text)
        # for owners who want the gallery-print look. is_museum=True hides those.
        "is_museum": (style == "museum"),
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
