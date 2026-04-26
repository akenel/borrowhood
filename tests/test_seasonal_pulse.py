"""Seasonal pulse regression guards (BL-115, April 26, 2026).

The seasonal map drives a real home-page section, so its shape needs
guarding. Each month must have every key the template reads. New accent
colors added to the map must also exist in the template's accent styles
dict, otherwise the section falls back to indigo silently.
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.services.seasonal import SEASONAL_MAP, get_current_seasonal_hint


REPO_ROOT = Path(__file__).resolve().parent.parent
HOME_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "home.html").read_text()
DISCOVER_PY = (REPO_ROOT / "src" / "routers" / "pages" / "discover.py").read_text()


REQUIRED_KEYS = {"theme_en", "theme_it", "subtitle_en", "subtitle_it", "categories", "accent"}


class TestSeasonalMapShape:
    """The seasonal map must cover all 12 months and every entry must have
    every key the template depends on."""

    def test_all_twelve_months_present(self):
        assert set(SEASONAL_MAP.keys()) == set(range(1, 13)), (
            "SEASONAL_MAP must have an entry for each month 1-12"
        )

    @pytest.mark.parametrize("month", range(1, 13))
    def test_each_month_has_required_keys(self, month):
        entry = SEASONAL_MAP[month]
        missing = REQUIRED_KEYS - set(entry.keys())
        assert not missing, f"Month {month} is missing keys: {missing}"

    @pytest.mark.parametrize("month", range(1, 13))
    def test_each_month_has_at_least_one_category(self, month):
        cats = SEASONAL_MAP[month]["categories"]
        assert isinstance(cats, list) and len(cats) >= 1, (
            f"Month {month} must list at least one category for the query "
            "to return anything"
        )

    @pytest.mark.parametrize("month", range(1, 13))
    def test_each_month_has_non_empty_strings(self, month):
        entry = SEASONAL_MAP[month]
        for key in ("theme_en", "theme_it", "subtitle_en", "subtitle_it", "accent"):
            value = entry[key]
            assert isinstance(value, str) and value.strip(), (
                f"Month {month} key '{key}' must be a non-empty string"
            )


class TestAccentColorsCoveredByTemplate:
    """Every accent used by the seasonal map must have a matching entry
    in the home.html _accent_styles dict, else the section silently falls
    back to indigo styling."""

    def test_all_accents_have_template_styles(self):
        accents_used = {entry["accent"] for entry in SEASONAL_MAP.values()}
        # Pull the set of accent keys defined in the template
        # _accent_styles is a Jinja set with keys like 'indigo':, 'rose':, etc.
        styles_block_start = HOME_HTML.find("{% set _accent_styles = {")
        assert styles_block_start > 0, (
            "home.html must define _accent_styles dict for the seasonal section"
        )
        styles_block_end = HOME_HTML.find("} %}", styles_block_start)
        styles_block = HOME_HTML[styles_block_start:styles_block_end]

        missing = []
        for accent in accents_used:
            if f"'{accent}':" not in styles_block:
                missing.append(accent)
        assert not missing, (
            f"Seasonal accents missing from home.html _accent_styles: {missing}. "
            "Either add them to the template dict or pick an accent that exists."
        )


class TestGetCurrentSeasonalHint:
    """The accessor must return the right month and tolerate missing input."""

    def test_returns_january_for_january_date(self):
        hint = get_current_seasonal_hint(datetime(2026, 1, 15, tzinfo=timezone.utc))
        assert hint["theme_en"] == SEASONAL_MAP[1]["theme_en"]

    def test_returns_august_for_ferragosto_date(self):
        # Ferragosto = Aug 15
        hint = get_current_seasonal_hint(datetime(2026, 8, 15, tzinfo=timezone.utc))
        assert hint["theme_en"] == SEASONAL_MAP[8]["theme_en"]
        # August must mention Ferragosto explicitly somewhere -- the whole
        # point of having a Trapani-flavored map
        assert "Ferragosto" in hint["theme_en"] or "Ferragosto" in hint["subtitle_en"]

    def test_returns_october_with_olive_theme(self):
        # October is olive harvest in Trapani -- the map should reflect that
        hint = get_current_seasonal_hint(datetime(2026, 10, 10, tzinfo=timezone.utc))
        theme = hint["theme_en"].lower() + " " + hint["subtitle_en"].lower()
        assert "olive" in theme, (
            "October is olive harvest in Sicily -- the seasonal hint should "
            "mention it"
        )

    def test_no_arg_uses_current_time(self):
        # Smoke check: calling with no args returns one of the 12 entries
        hint = get_current_seasonal_hint()
        assert hint in SEASONAL_MAP.values()


class TestHomePageSeasonalSection:
    """The home page must render the section under an {% if seasonal_items
    and seasonal_hint %} guard so it hides cleanly when there are no
    matches (no empty-state pollution)."""

    def test_section_guarded_by_seasonal_items_and_hint(self):
        assert "{% if seasonal_items and seasonal_hint %}" in HOME_HTML, (
            "Seasonal section must be guarded so it disappears entirely "
            "when there are no in-season listings"
        )

    def test_section_renders_theme(self):
        assert "seasonal_hint.theme_en" in HOME_HTML
        assert "seasonal_hint.theme_it" in HOME_HTML

    def test_section_renders_subtitle(self):
        assert "seasonal_hint.subtitle_en" in HOME_HTML
        assert "seasonal_hint.subtitle_it" in HOME_HTML


class TestDiscoverRouteWiring:
    """The home() route must import the seasonal service and pass both
    seasonal_items and seasonal_hint into the template context."""

    def test_route_imports_seasonal_service(self):
        assert "from src.services.seasonal import get_current_seasonal_hint" in DISCOVER_PY

    def test_route_passes_seasonal_items_and_hint_to_template(self):
        assert "seasonal_items=seasonal_items" in DISCOVER_PY
        assert "seasonal_hint=seasonal_hint" in DISCOVER_PY

    def test_route_uses_random_order_for_freshness(self):
        # Random ordering ensures the strip surfaces a different mix on
        # each visit -- otherwise the same 6 items dominate forever
        # (look in the seasonal block, not the rest of the file)
        seasonal_block_start = DISCOVER_PY.find("BL-115")
        seasonal_block = DISCOVER_PY[seasonal_block_start:seasonal_block_start + 1000]
        assert "func.random()" in seasonal_block, (
            "Seasonal query must order_by(func.random()) so the surfaced "
            "set rotates between visits"
        )
