"""Tag staging items with edition attributes so the Locandina ribbon (#138) has
something real to render — the visual companion to tests/test_locandina_edition_ribbon.py.

The unit test proves the caption logic and the template render in isolation. This
script gives a human eye three live cards to compare on staging:

  ORIGINAL   item.attributes["edition"] = {"type": "original", "catalog_no": "003"}
                -> caption "ORIGINAL · 1 of 1 · № 003"
  EDITION    item.attributes["edition"] = {"type": "edition", "number": 1, "total": 200}
                -> caption "EDITION · 1 of 200"
  CONTROL    edition tag cleared
                -> NO caption (proves it collapses for non-art items)

It picks the first 3 ACTIVE listings that map to DISTINCT items. The edition data
lives on the ITEM (a JSON column), so two listings of the same item would collide
— hence the de-dupe. Reversible: clears attributes["edition"] on the control and
can be re-pointed by re-running.

Companion human test card (click-ready staging URLs baked in):
  docs/testing/test-scripts/EDITION-RIBBON-TEST-SCRIPT.html  (helixnet repo)

Usage on staging (via docker exec, NO rebuild needed):
  docker exec -i borrowhood_staging python scripts/seed_edition_test_cases.py

Output: prints listing IDs + Locandina PDF URLs ready to open.
"""

import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import async_session
from src.models.listing import BHListing, ListingStatus


async def main() -> int:
    async with async_session() as db:
        all_rows = (await db.execute(
            select(BHListing).options(selectinload(BHListing.item))
            .where(BHListing.status == ListingStatus.ACTIVE)
            .where(BHListing.deleted_at.is_(None))
            .limit(60)
        )).scalars().all()

        # DISTINCT items only — attributes live on the item, so same-item
        # listings would overwrite each other.
        rows, seen = [], set()
        for r in all_rows:
            if r.item and r.item.deleted_at is None and r.item.id not in seen:
                seen.add(r.item.id)
                rows.append(r)
            if len(rows) == 3:
                break
        if len(rows) < 3:
            print(f"only {len(rows)} active listings with DISTINCT items — need 3")
            return 1

        tags = [
            {"type": "original", "catalog_no": "003"},
            {"type": "edition", "number": 1, "total": 200},
            None,  # control — left untagged
        ]
        out = []
        for r, tag in zip(rows, tags):
            it = r.item
            attrs = dict(it.attributes or {})
            if tag is None:
                attrs.pop("edition", None)
                role = "CONTROL (no edition tag — caption must collapse)"
            else:
                attrs["edition"] = tag
                role = "ORIGINAL · № 003" if tag["type"] == "original" else "EDITION · 1 of 200"
            it.attributes = attrs
            out.append((role, str(r.id), it.slug, it.name))
        await db.commit()

    print("\n==== TAGGED STAGING ITEMS (for the edition-ribbon human check) ====")
    for role, lid, slug, name in out:
        print(f"\n[{role}]  {name}")
        print(f"  listing_id: {lid}")
        print(f"  item slug : {slug}")
        print(f"  locandina : https://staging.lapiazza.app/api/v1/listings/{lid}/locandina.pdf")
        print(f"  item page : https://staging.lapiazza.app/items/{slug}")
    print("\n(to revert: clear attributes['edition'] on these items)")
    return 0


sys.exit(asyncio.run(main()))
