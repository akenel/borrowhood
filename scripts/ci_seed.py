"""CI seed helper.

The inline `python -c` in .github/workflows/ci.yml swallowed tracebacks
for 9+ days while seed_database silently exit-1'd. This script does the
same work but with explicit error surfacing so the GitHub Actions log
shows the actual exception + line number when seeding breaks.

Usage:
    python scripts/ci_seed.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
import traceback


async def main() -> None:
    # Log everything at DEBUG so the CI log captures what step blew up.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )
    log = logging.getLogger("ci_seed")

    log.info("=== ci_seed: importing ===")
    from src.database import create_tables, async_session
    from src.services.seeding import seed_database

    log.info("=== ci_seed: creating tables ===")
    await create_tables()

    log.info("=== ci_seed: opening session ===")
    async with async_session() as db:
        log.info("=== ci_seed: calling seed_database() ===")
        result = await seed_database(db)
        log.info("=== ci_seed: result = %s ===", result)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except BaseException:
        # Print the full traceback to stderr so the GitHub Actions
        # job log actually shows it. Previously the inline `python -c`
        # would print nothing visible and just exit 1.
        sys.stderr.write("\n!!! ci_seed FAILED -- traceback follows !!!\n")
        traceback.print_exc()
        sys.exit(1)
