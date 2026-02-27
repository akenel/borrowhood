"""Lock box access code service.

Generates unique, human-readable one-time codes for contactless exchanges.
Codes exclude confusing characters (0/O, 1/I/L) for readability.
"""

import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lockbox import BHLockBoxAccess

# Alphabet: uppercase + digits, minus confusing chars
_ALPHABET = "".join(
    c for c in string.ascii_uppercase + string.digits
    if c not in "0O1IL"
)  # 31 chars: A-Z minus O,I,L + 2-9


def _generate_code(length: int = 8) -> str:
    """Generate a random code from the safe alphabet."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


async def generate_unique_codes(db: AsyncSession) -> tuple[str, str]:
    """Generate two unique 8-char codes (pickup + return).

    Checks DB for collisions (astronomically unlikely but we're thorough).
    """
    for _ in range(10):  # Max retries
        pickup = _generate_code()
        return_code = _generate_code()

        # Ensure both are unique in DB
        existing = await db.execute(
            select(BHLockBoxAccess).where(
                (BHLockBoxAccess.pickup_code == pickup)
                | (BHLockBoxAccess.return_code == pickup)
                | (BHLockBoxAccess.pickup_code == return_code)
                | (BHLockBoxAccess.return_code == return_code)
            )
        )
        if not existing.scalars().first():
            return pickup, return_code

    # Should never reach here (31^8 = 852 billion combinations)
    raise RuntimeError("Failed to generate unique lock box codes")
