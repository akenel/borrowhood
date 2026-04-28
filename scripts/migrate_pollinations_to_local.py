"""Migrate Pollinations hot-links to locally-hosted images.

WhatsApp/Telegram share-preview bots time out (~5s) before
Pollinations finishes generating an on-demand image, so any link to
an item whose photo is a Pollinations URL gets a broken share card.

This script:
  1. Selects every BHItemMedia row whose url contains "pollinations".
  2. Downloads each URL (concurrent, sem=5) to:
       /app/src/static/uploads/seed-images/<media-uuid>.jpg
  3. Updates the row's url to "/static/uploads/seed-images/<media-uuid>.jpg".
  4. Leaves alt_text untouched.

Idempotent: rows whose url already starts with "/static/" are skipped.
Failed downloads keep the original URL so the next run can retry.

Run inside the borrowhood container:
    docker exec borrowhood python3 /app/scripts/migrate_pollinations_to_local.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "/app")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx


SEED_DIR = Path("/app/src/static/uploads/seed-images")
LOCAL_PREFIX = "/static/uploads/seed-images"

# Be polite to Pollinations and don't hammer the box's network either
CONCURRENCY = 5
PER_REQUEST_TIMEOUT = 60  # seconds; first-time generation can be slow


async def fetch_one(client: httpx.AsyncClient, sem: asyncio.Semaphore,
                     media_id, original_url: str):
    """Download one Pollinations URL. Returns (media_id, local_url or None)."""
    async with sem:
        try:
            resp = await client.get(original_url, follow_redirects=True)
            if resp.status_code != 200:
                print(f"  [{resp.status_code}] {media_id}: {original_url[:80]}")
                return media_id, None
            data = resp.content
            if len(data) < 1000:
                print(f"  [tiny:{len(data)}b] {media_id}: skipping")
                return media_id, None
            ext = "jpg"
            ctype = resp.headers.get("Content-Type", "")
            if "png" in ctype:
                ext = "png"
            elif "webp" in ctype:
                ext = "webp"
            fname = f"{media_id}.{ext}"
            fpath = SEED_DIR / fname
            fpath.write_bytes(data)
            local_url = f"{LOCAL_PREFIX}/{fname}"
            return media_id, local_url
        except httpx.TimeoutException:
            print(f"  [timeout] {media_id}")
            return media_id, None
        except Exception as e:
            print(f"  [err] {media_id}: {type(e).__name__}: {e}")
            return media_id, None


async def main():
    import importlib
    import pkgutil
    from sqlalchemy import select, update
    from src.database import async_session
    import src.models as _models_pkg
    for _, _modname, _ in pkgutil.iter_modules(_models_pkg.__path__):
        importlib.import_module(f"src.models.{_modname}")
    from src.models.item import BHItemMedia

    SEED_DIR.mkdir(parents=True, exist_ok=True)

    # Collect rows that need migration
    async with async_session() as db:
        result = await db.execute(
            select(BHItemMedia.id, BHItemMedia.url)
            .where(BHItemMedia.url.like("%pollinations%"))
        )
        rows = result.all()

    if not rows:
        print("Nothing to migrate -- no pollinations URLs in bh_item_media.")
        return

    print(f"Found {len(rows)} Pollinations URLs to migrate.")
    print(f"Saving to: {SEED_DIR}")
    print()

    # Concurrent fetch
    sem = asyncio.Semaphore(CONCURRENCY)
    timeout = httpx.Timeout(PER_REQUEST_TIMEOUT, connect=10)
    limits = httpx.Limits(max_connections=CONCURRENCY * 2)
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        tasks = [fetch_one(client, sem, mid, url) for mid, url in rows]
        results = await asyncio.gather(*tasks)

    # Build update map
    updates = [(mid, local_url) for mid, local_url in results if local_url]
    failed = [mid for mid, local_url in results if not local_url]

    print()
    print(f"Downloaded: {len(updates)}")
    print(f"Failed:     {len(failed)} (will retry on next run)")

    if not updates:
        return

    # Persist URL changes -- one bulk transaction
    async with async_session() as db:
        for mid, local_url in updates:
            await db.execute(
                update(BHItemMedia)
                .where(BHItemMedia.id == mid)
                .values(url=local_url)
            )
        await db.commit()
    print(f"DB updated: {len(updates)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
