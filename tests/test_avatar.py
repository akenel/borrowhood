"""Generative avatar (services/avatar.py) -- pure-logic, runs every pass (no DB).

Guards the dummy-avatar contract: deterministic per user, visibly distinct
between users, valid self-contained SVG, and -- the whole point -- NO letters.
"""
import re

from src.services.avatar import PALETTES, generate_avatar_svg

_ALL_COLOURS = {c for p in PALETTES for c in p}


def test_deterministic_same_seed_same_svg():
    assert generate_avatar_svg("marco") == generate_avatar_svg("marco")


def test_seed_normalised_case_and_whitespace():
    assert generate_avatar_svg("  Marco ") == generate_avatar_svg("marco")


def test_different_seeds_differ():
    assert generate_avatar_svg("marco") != generate_avatar_svg("sofia")
    assert generate_avatar_svg("nino") != generate_avatar_svg("angel")


def test_is_a_valid_self_contained_svg():
    svg = generate_avatar_svg("angel")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert 'viewBox="0 0 80 80"' in svg
    assert "http://" not in svg.replace('xmlns="http://www.w3.org/2000/svg"', "")  # no external refs


def test_no_letters_it_is_geometric_not_initials():
    svg = generate_avatar_svg("marco")
    assert "<text" not in svg  # the whole point: better than letters


def test_uses_palette_colours():
    svg = generate_avatar_svg("sofia")
    assert any(c in svg for c in _ALL_COLOURS)


def test_empty_or_none_seed_still_valid():
    for bad in ("", "   ", None):
        svg = generate_avatar_svg(bad)  # type: ignore[arg-type]
        assert svg.startswith("<svg") and "</svg>" in svg


def test_clip_id_is_seed_derived_unique():
    # distinct clip ids so two inlined avatars don't collide in one DOM
    id_a = re.search(r'id="(av[0-9a-f]+)"', generate_avatar_svg("marco")).group(1)
    id_b = re.search(r'id="(av[0-9a-f]+)"', generate_avatar_svg("sofia")).group(1)
    assert id_a != id_b
