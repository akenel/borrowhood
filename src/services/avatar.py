"""Deterministic generative avatars for users with no photo.

Why: avatar fallback used to be inconsistent across the app -- a bare letter in
messages, a grey silhouette SVG in leaderboard, nothing in browse. A bare letter
looks unfinished. This gives every photo-less user ONE consistent, designed-looking
placeholder: a geometric/gradient mark derived deterministically from their name,
so the same person always gets the same avatar (recognisable across the app) and
two different people get visibly different ones.

No external service (privacy is a feature; external image services have burned us
before -- see lesson-weasyprint-silent-image-fail), no dependency: pure SVG math
off a sha256 of the seed. Served by routers/avatar.py and cached immutable.
"""
from __future__ import annotations

import hashlib

# Curated harmonious palettes -- warm La Piazza / Sicilian-town-square vibe.
# Index 0 = background, 1 & 2 = the two shape colours. One palette per user.
PALETTES = [
    ["#F2D6A2", "#E08D55", "#C0392B"],  # terracotta / Sicilian sun
    ["#A7C5BD", "#5E8B7E", "#2F5D62"],  # sea green
    ["#F6E0B5", "#AA6373", "#6C5B7B"],  # plum dusk
    ["#FCE38A", "#F38181", "#95E1D3"],  # citrus
    ["#C9D6DF", "#52616B", "#2C3E50"],  # slate
    ["#FFD3B6", "#FFAAA5", "#C0392B"],  # coral
    ["#B5EAD7", "#C7CEEA", "#6C5B7B"],  # pastel
    ["#E6B89C", "#9CAFB7", "#4281A4"],  # adriatic
]


def _bytes(seed: str, n: int = 12) -> list[int]:
    """n deterministic 0-255 values from the seed (sha256 -> byte pairs)."""
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return [int(h[i * 2:i * 2 + 2], 16) for i in range(n)]


def generate_avatar_svg(seed: str, size: int = 80) -> str:
    """A deterministic geometric avatar for `seed` (username/name). Same seed ->
    byte-identical SVG every time; different seeds -> visibly different.

    The mark: a coloured field with two overlapping circles and one rotated
    rounded square, all clipped to a circle. No letters, no external refs.
    """
    seed = (seed or "anon").strip().lower() or "anon"
    v = _bytes(seed)
    bg, c1, c2 = PALETTES[v[0] % len(PALETTES)]
    cid = "av" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8]
    mid = size / 2

    def coord(i: int) -> int:
        return 6 + (v[i] % (size - 12))

    def radius(i: int) -> int:
        return int(size * 0.22) + (v[i] % int(size * 0.32))

    rot = v[8] % 360

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" aria-label="avatar">'
        f'<defs><clipPath id="{cid}"><circle cx="{mid}" cy="{mid}" r="{mid}"/>'
        f'</clipPath></defs>'
        f'<g clip-path="url(#{cid})">'
        f'<rect width="{size}" height="{size}" fill="{bg}"/>'
        f'<circle cx="{coord(1)}" cy="{coord(2)}" r="{radius(3)}" fill="{c1}" opacity="0.85"/>'
        f'<circle cx="{coord(4)}" cy="{coord(5)}" r="{radius(6)}" fill="{c2}" opacity="0.80"/>'
        f'<rect x="{coord(7)}" y="{coord(9)}" width="{radius(10)}" height="{radius(11)}" '
        f'rx="{int(size * 0.12)}" fill="{c1}" opacity="0.55" '
        f'transform="rotate({rot} {mid} {mid})"/>'
        f'</g></svg>'
    )
