"""Location privacy: blur coordinates for public display.

Adds a deterministic random offset (~500m radius) to lat/lng so that
exact home/workshop locations are never revealed on public pages.
The offset is seeded by entity ID so it stays consistent across page loads.
"""

import hashlib
import math
import struct


def blur_coordinates(
    lat: float | None,
    lng: float | None,
    entity_id: str = "",
    radius_m: float = 500.0,
) -> tuple[float | None, float | None]:
    """Return lat/lng with a deterministic offset within radius_m.

    Uses entity_id (UUID string) as seed so the same entity always
    gets the same offset -- no jumping markers on page refresh.
    Returns (None, None) if inputs are None.
    """
    if lat is None or lng is None:
        return (None, None)

    # Deterministic seed from entity ID
    seed = hashlib.sha256(entity_id.encode()).digest()
    # Extract two floats (0.0-1.0) from the hash
    angle = struct.unpack("!d", seed[:8])[0] % (2 * math.pi)
    distance_frac = (struct.unpack("!I", seed[8:12])[0] / 0xFFFFFFFF)

    # Random distance within radius (sqrt for uniform distribution)
    distance_m = radius_m * math.sqrt(distance_frac)

    # Convert meters to degree offsets
    # 1 degree latitude = ~111,320m
    # 1 degree longitude = ~111,320m * cos(lat)
    d_lat = (distance_m * math.cos(angle)) / 111_320.0
    d_lng = (distance_m * math.sin(angle)) / (111_320.0 * max(math.cos(math.radians(lat)), 0.01))

    return (round(lat + d_lat, 5), round(lng + d_lng, 5))
