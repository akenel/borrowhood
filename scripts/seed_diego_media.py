"""Add Pollinations cover images to Diego's items + flip listings to ACTIVE.

Run after seed_diego_sim.py. Idempotent: if an item already has media,
it's skipped. Listings already ACTIVE stay ACTIVE.

    docker exec borrowhood python3 /app/scripts/seed_diego_media.py
"""
import asyncio
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, "/app")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# Pollinations URL builder
def pollinations(prompt: str, seed: int, w: int = 1200, h: int = 800) -> str:
    p = quote(prompt, safe="")
    return f"https://image.pollinations.ai/prompt/{p}?width={w}&height={h}&seed={seed}&nologo=true&model=flux"


# slug -> (alt_text, prompt, seed)
ITEM_IMAGES = {
    "diego-trapani-walking-tour": (
        "Trapani old town walking tour at golden hour",
        "Old town of Trapani Sicily, narrow cobblestone alleys, golden hour Mediterranean light, baroque limestone architecture, no people, photographic",
        4201,
    ),
    "diego-erice-day-trip": (
        "Medieval Erice Sicily perched on mountain",
        "Medieval hilltop town of Erice Sicily, ancient stone walls, panoramic view of the Mediterranean, blue sky, dramatic landscape, photographic",
        4202,
    ),
    "diego-marsala-wine-tour": (
        "Marsala wine cellar with oak barrels and tasting glasses",
        "Sicilian Marsala wine cellar, oak barrels, golden glass of Marsala wine on rustic wooden table, warm light, photographic",
        4203,
    ),
    "diego-saline-sunset-boat": (
        "Trapani salt flats at sunset with windmill",
        "Saline di Trapani salt flats at sunset, white salt mountains, traditional windmill silhouette, orange and pink sky reflecting on water, wooden boat, photographic",
        4204,
    ),
    "diego-airport-transfer-tps": (
        "Airport transfer at Trapani-Birgi",
        "Clean white minivan parked at small Sicilian airport TPS Trapani-Birgi terminal, palm trees, sunny Mediterranean afternoon, professional driver service, photographic",
        4205,
    ),
    "diego-may1-aperitivo-civico11": (
        "Aperitivo at Enoteca Civico 11 evening",
        "Cozy wine bar in Trapani Sicily at evening, glasses of red wine, charcuterie board, candles, vintage Italian interior, warm welcoming atmosphere, photographic",
        4206,
    ),
    "diego-raffle-erice-day-trip": (
        "Erice raffle prize -- day trip for two",
        "Two glasses raised in cheers in front of medieval Erice town, sunny day, Sicilian stone arch, romantic travel scene, photographic",
        4207,
    ),
}


async def main():
    import importlib
    import pkgutil
    from sqlalchemy import select, update

    from src.database import async_session
    import src.models as _models_pkg
    for _, _modname, _ in pkgutil.iter_modules(_models_pkg.__path__):
        importlib.import_module(f"src.models.{_modname}")

    from src.models.user import BHUser
    from src.models.item import BHItem, BHItemMedia, MediaType
    from src.models.listing import BHListing, ListingStatus

    async with async_session() as db:
        # Find Diego
        diego = await db.scalar(
            select(BHUser).where(BHUser.email == "diego-sim@lapiazza.app")
        )
        if not diego:
            print("Diego sim user not found -- run seed_diego_sim.py first")
            return

        # Find each item by slug
        added = 0
        skipped = 0
        for slug, (alt, prompt, seed) in ITEM_IMAGES.items():
            item = await db.scalar(
                select(BHItem).where(BHItem.owner_id == diego.id).where(BHItem.slug == slug)
            )
            if not item:
                print(f"  SKIP: item {slug} not found")
                continue

            # Skip if media already exists
            existing = await db.scalar(
                select(BHItemMedia).where(BHItemMedia.item_id == item.id).limit(1)
            )
            if existing:
                print(f"  SKIP: {slug} already has media")
                skipped += 1
                continue

            url = pollinations(prompt, seed)
            db.add(BHItemMedia(
                item_id=item.id,
                media_type=MediaType.PHOTO,
                url=url,
                alt_text=alt,
                sort_order=0,
            ))
            print(f"  Added image: {slug}")
            added += 1

        # Flip Diego's listings from DRAFT to ACTIVE so click-through works
        item_ids = (await db.execute(
            select(BHItem.id).where(BHItem.owner_id == diego.id)
        )).scalars().all()

        if item_ids:
            result = await db.execute(
                update(BHListing)
                .where(BHListing.item_id.in_(item_ids))
                .where(BHListing.status == ListingStatus.DRAFT)
                .values(status=ListingStatus.ACTIVE)
            )
            print(f"  Flipped {result.rowcount} listing(s) DRAFT -> ACTIVE")

        await db.commit()
        print()
        print(f"DONE: {added} image(s) added, {skipped} skipped (already had media)")


if __name__ == "__main__":
    asyncio.run(main())
