"""Locandina edition ribbon (#138) — the gallery caption on the share card.

Promoted from a one-shot verifier (was /tmp/verify_edition_ribbon.py) into a
committed regression net, so the next person who touches `_edition_ribbon` or
card.html can't silently break the art-drop caption.

Two layers, both DB-free so they run in every default `pytest` pass:
  - the pure `_edition_ribbon` mapper (EN/IT, original/edition, the None cases)
  - a real card.html render (catches template syntax errors + proves the caption
    shows in classic AND museum styles, and COLLAPSES for a non-art item)

The edition data lives in `item.attributes["edition"]` (a JSON column, no
migration). Shape:
    original  ->  {"type": "original", "catalog_no": "003"}      (1/1 + catalog №)
    edition   ->  {"type": "edition",  "number": 1, "total": 200} (1 of N)
"""

from types import SimpleNamespace

import pytest

from src.routers.locandina import _edition_ribbon
from src.routers.pages._helpers import templates


def _item(edition):
    """A stand-in item carrying just the attributes the ribbon reads."""
    return SimpleNamespace(attributes={"edition": edition} if edition is not None else {})


# --------------------------------------------------------------------------
# 1. the pure mapper
# --------------------------------------------------------------------------

def test_original_en():
    item = _item({"type": "original", "catalog_no": "003"})
    assert _edition_ribbon(item, "en") == "ORIGINAL · 1 of 1 · № 003"


def test_original_it():
    item = _item({"type": "original", "catalog_no": "003"})
    assert _edition_ribbon(item, "it") == "ORIGINALE · 1 di 1 · № 003"


def test_original_without_catalog_no_drops_the_number():
    item = _item({"type": "original"})
    assert _edition_ribbon(item, "en") == "ORIGINAL · 1 of 1"


def test_edition_en():
    item = _item({"type": "edition", "number": 1, "total": 200})
    assert _edition_ribbon(item, "en") == "EDITION · 1 of 200"


def test_edition_it():
    item = _item({"type": "edition", "number": 1, "total": 200})
    assert _edition_ribbon(item, "it") == "EDIZIONE · 1 di 200"


def test_edition_total_only_assumes_piece_one():
    item = _item({"type": "edition", "total": 50})
    assert _edition_ribbon(item, "en") == "EDITION · 1 of 50"


def test_non_art_item_yields_no_ribbon():
    """A normal listing (no edition key) must produce no caption -> it collapses."""
    item = SimpleNamespace(attributes={"condition": "good"})
    assert _edition_ribbon(item, "en") is None


def test_missing_attributes_yields_no_ribbon():
    assert _edition_ribbon(SimpleNamespace(attributes=None), "en") is None


def test_unknown_edition_type_yields_no_ribbon():
    item = _item({"type": "poster"})
    assert _edition_ribbon(item, "en") is None


def test_garbage_numbers_dont_raise():
    """Bad total/number must degrade to the bare label, never 500 the PDF."""
    item = _item({"type": "edition", "number": "x", "total": "y"})
    assert _edition_ribbon(item, "en") == "EDITION"


# --------------------------------------------------------------------------
# 2. the real card.html render
# --------------------------------------------------------------------------

def _ctx(edition_ribbon, museum=False):
    """Minimal but complete render context for locandina/card.html."""
    return dict(
        title="Embroidered Vintage No.3", schedule_text=None, edition_ribbon=edition_ribbon,
        byline="Corrado · Roma", avatar_url=None, cover_url=None,
        description="A hand-embroidered framed piece.", qr_data_uri="data:image/png;base64,AAAA",
        url_display="lapiazza.app/items/x", scan_me="Scan for details",
        type_badge={"label": "FOR SALE", "color": "#dc2626"},
        data_ribbon="€200", tag_chips=["embroidery", "vintage"],
        tier_marker={"slug": "active", "accent": "#0d9488", "chip": None, "wash": 0.14},
        is_staging=False, watermark="LP · test", bruce_quote="Be water, my friend.",
        is_museum=museum, lang="en",
    )


def _render(edition_ribbon, museum=False):
    return templates.get_template("locandina/card.html").render(**_ctx(edition_ribbon, museum))


def test_classic_render_shows_the_caption():
    html = _render("EDITION · 1 of 200")
    assert "EDITION · 1 of 200" in html
    assert 'class="edition"' in html


def test_museum_style_still_shows_the_caption():
    """Museum mode strips most chrome — the edition caption must survive it."""
    html = _render("ORIGINAL · 1 of 1 · № 003", museum=True)
    assert "ORIGINAL · 1 of 1 · № 003" in html


def test_no_edition_omits_the_caption_div():
    html = _render(None)
    assert 'class="edition"' not in html


def test_qr_still_targets_the_item_url():
    """Guard the drop's actual mechanism: the QR/footer points at the item page."""
    assert "lapiazza.app/items/x" in _render("EDITION · 1 of 200")
