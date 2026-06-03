"""Seed test events that stress-test every edge case of the Locandina template.

The first round of Locandina design (Block 3) was tested against one event with a
~250-char description, a cover photo, and an owner without an avatar. That's a
sample of one and tells us nothing about how the template behaves on the spectrum
of real content owners will throw at it.

This script creates 4 EVENT listings on the same test owner, each engineered to
hit a specific failure mode of the design:

  T1  empty-soul-walk       desc=NULL              no cover     short title
                            -> tests:  empty description slot, gradient placeholder,
                                       title-doesn't-wrap, owner avatar visibility

  T2  brief-coffee-meetup   desc=~60 chars         has cover    short title
                            -> tests:  max white-space (small desc + huge slot),
                                       single-line title, wash-over-empty-space

  T3  acquerello-workshop   desc=~220 chars        has cover    medium title
                            -> tests:  "verbatim Goldilocks" -- fills the slot
                                       without truncation; the design's sweet spot

  T4  masterclass-imprenditoria  desc=~900 chars   has cover    long title
                            -> tests:  Block-3 truncation stub at 250 chars
                            -> later:  Block-4 Ollama compression target

Owner = the seeded user "Nico" (Nic's Dojo / Trapani). If Nico doesn't have an
avatar_url, this script sets one to a tiny generated placeholder so we can also
visually verify the avatar-inline-with-byline rendering.

Idempotent: re-running updates existing rows by slug rather than duplicating.

Usage on staging (via docker exec):
  docker exec -i borrowhood_staging python scripts/seed_locandina_test_cases.py

Output: prints listing IDs + PDF URLs ready to curl.
"""

import asyncio
import sys
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session
from src.models.item import BHItem, BHItemMedia, ItemCategory, ItemType, MediaType
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.user import BHUser


# Image sources for stress-test cards.
# Pollinations (used in earlier draft) is now monetized via USDC-on-Base
# payments and returns HTTP 402 + JSON error to anonymous callers, which
# WeasyPrint silently swallows -- the cards rendered with blank gradient
# placeholders. Switched to Unsplash (stable photo IDs, instant CDN, real
# JPEGs) for cover photos, plus picsum.photos for the avatar (any real
# JPEG proves the avatar slot wires correctly).
def unsplash(photo_id: str, w: int = 800, h: int = 600) -> str:
    return f"https://images.unsplash.com/photo-{photo_id}?w={w}&h={h}&fit=crop&q=80"


def picsum(seed: str, size: int = 256) -> str:
    return f"https://picsum.photos/seed/{seed}/{size}/{size}"


TEST_CASES = [
    {
        "slug": "loc-test-1-empty-soul-walk",
        "name": "Camminata in Silenzio",
        "description": None,  # NULL on purpose -- empty-slot stress test
        "schedule_summary": None,  # Schedule TBD will fall through
        "cover_url": None,  # No photo -- gradient placeholder stress test
        "label": "T1 -- empty desc + no cover + short title",
    },
    {
        "slug": "loc-test-2-brief-coffee-meetup",
        "name": "Caffè al Tramonto",
        "description": "Un caffè al tramonto al porto. Vieni a parlare. Tutti benvenuti.",
        "schedule_summary": "Ogni giovedì 19:00",
        # Unsplash: espresso cup at golden hour
        "cover_url": unsplash("1495474472287-4d71bcdd2085"),
        "label": "T2 -- short desc (white space) + has cover",
    },
    {
        "slug": "loc-test-3-acquerello-workshop",
        "name": "Acquerello in Piazza -- Pomeriggio Creativo",
        "description": (
            "Porta un foglio di carta e impara le basi dell'acquerello con noi. "
            "Tre ore di pittura all'aperto in Piazza Mercato. Tutti i livelli "
            "benvenuti, materiali forniti per chi non li ha. Pochi posti -- "
            "prenota in anticipo per assicurarti un cavalletto."
        ),
        "schedule_summary": "Sabato 14 giugno, 15:00–18:00",
        # Unsplash: watercolor paint palette
        "cover_url": unsplash("1547826039-bfc35e0f1ea8"),
        "label": "T3 -- ~220 char desc (Goldilocks)",
    },
    {
        "slug": "loc-test-4-masterclass-imprenditoria",
        "name": "Masterclass Imprenditoria Locale -- Dai Mercati Online al Negozio di Quartiere",
        "description": (
            "Una giornata completa per chi vuole aprire un'attività locale a "
            "Trapani o trasformare un hobby in un piccolo business. Mattina: "
            "fondamenti del business plan, scelta della forma giuridica (ditta "
            "individuale vs SRL semplificata), regime fiscale forfettario e "
            "flat tax, come aprire la P.IVA passo passo. Pausa pranzo offerta. "
            "Pomeriggio: marketing locale a costo zero, presenza online "
            "minima ma efficace (Google Maps, Instagram, La Piazza), come "
            "ottenere le prime recensioni, gestione del cliente difficile, "
            "errori da evitare nei primi sei mesi. Sessione di Q&A finale con "
            "due imprenditori locali che hanno aperto la loro attività negli "
            "ultimi 18 mesi. Riservato ai residenti della provincia di Trapani. "
            "Posti limitati a 25. Iscrizione obbligatoria via WhatsApp."
        ),
        "schedule_summary": "Sabato 28 giugno, 09:30–17:30",
        # Unsplash: business meeting / small-shop owner
        "cover_url": unsplash("1556761175-5973dc0f32e7"),
        "label": "T4 -- 900+ char desc (truncation/Ollama stress)",
    },
]


async def find_owner(db: AsyncSession) -> Optional[BHUser]:
    """Find any user we can attach test events to. Prefer Nico if available."""
    result = await db.execute(
        select(BHUser)
        .where(BHUser.display_name.ilike("%nico%"))
        .limit(1)
    )
    user = result.scalar_one_or_none()
    if user:
        return user
    # Fallback -- any user
    result = await db.execute(select(BHUser).limit(1))
    return result.scalar_one_or_none()


async def ensure_avatar(db: AsyncSession, user: BHUser) -> bool:
    """Make sure the test owner has an avatar so we can verify avatar rendering.
    Returns True if we set one, False if it was already present.
    Force-replace if the existing URL is Pollinations (HTTP 402 since June 2026)."""
    existing = user.avatar_url or ""
    if existing and "pollinations" not in existing.lower():
        return False
    # picsum.photos -- deterministic by seed, real JPEG, no rate limit.
    # Slug the display_name so re-runs return the same image.
    seed = (user.display_name or "owner").lower().replace(" ", "-").replace("ò", "o")
    user.avatar_url = picsum(seed, 256)
    return True


async def upsert_event(
    db: AsyncSession,
    owner: BHUser,
    case: dict,
) -> tuple[BHListing, str]:
    """Find-or-create an EVENT listing for a test case. Returns (listing, action)."""
    # Look for existing item by slug
    result = await db.execute(select(BHItem).where(BHItem.slug == case["slug"]))
    item = result.scalar_one_or_none()

    action = "updated" if item else "created"

    if not item:
        item = BHItem(
            id=uuid.uuid4(),
            owner_id=owner.id,
            name=case["name"],
            slug=case["slug"],
            description=case["description"],
            content_language="it",
            item_type=ItemType.SERVICE,
            category=ItemCategory.WORKSHOP_EVENT.value,
        )
        db.add(item)
        await db.flush()
    else:
        item.name = case["name"]
        item.description = case["description"]

    # Replace media so re-runs don't pile up duplicates
    existing_media = (await db.execute(
        select(BHItemMedia).where(BHItemMedia.item_id == item.id)
    )).scalars().all()
    for m in existing_media:
        await db.delete(m)
    await db.flush()

    if case["cover_url"]:
        media = BHItemMedia(
            id=uuid.uuid4(),
            item_id=item.id,
            media_type=MediaType.PHOTO,
            url=case["cover_url"],
            alt_text=f"Cover for {case['name']}",
            sort_order=0,
        )
        db.add(media)

    # Find or create the EVENT listing
    result = await db.execute(
        select(BHListing).where(BHListing.item_id == item.id, BHListing.listing_type == ListingType.EVENT)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        listing = BHListing(
            id=uuid.uuid4(),
            item_id=item.id,
            listing_type=ListingType.EVENT,
            status=ListingStatus.ACTIVE,
            schedule_summary=case["schedule_summary"],
        )
        db.add(listing)
    else:
        listing.schedule_summary = case["schedule_summary"]
        listing.status = ListingStatus.ACTIVE

    await db.flush()
    return listing, action


async def main() -> int:
    async with async_session() as db:
        owner = await find_owner(db)
        if not owner:
            print("ERROR: No users in DB. Run the main seed first.", file=sys.stderr)
            return 1

        print(f"Test owner: {owner.display_name} (id={owner.id})")
        if await ensure_avatar(db, owner):
            print(f"  -> Set avatar_url for {owner.display_name} (was empty)")
        else:
            print(f"  -> avatar_url already set")

        results = []
        for case in TEST_CASES:
            listing, action = await upsert_event(db, owner, case)
            results.append((case["label"], listing.id, case["slug"]))
            print(f"  [{action}] {case['label']}  -> listing {listing.id}")

        await db.commit()

        print("\nPDF URLs (staging):")
        for label, lid, slug in results:
            print(f"  # {label}")
            print(f"  https://staging.lapiazza.app/api/v1/listings/{lid}/locandina.pdf?lang=it")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
