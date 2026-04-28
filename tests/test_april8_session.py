"""Tests for April 8, 2026 session fixes.

Covers:
1. OG meta tag helpers (_abs_url, _og_item_desc, _og_workshop_desc)
2. Item slug regeneration on title edit
3. Workshop page: no Alpine.js var in x-text, has OpenStreetMap embed
4. Profile save: enum conversion (workshop_type string -> Python enum)
5. Item detail: no duplicate OG tags
6. Corrado account migration verification
"""

import pytest
import inspect
from pathlib import Path


# ── OG tag helpers ──


class TestOGHelpers:
    def test_abs_url_converts_relative(self):
        from src.routers.pages import _abs_url
        result = _abs_url("/static/uploads/photo.jpg")
        assert result.startswith("http")
        assert "/static/uploads/photo.jpg" in result

    def test_abs_url_preserves_absolute(self):
        from src.routers.pages import _abs_url
        result = _abs_url("https://images.unsplash.com/photo.jpg")
        assert result == "https://images.unsplash.com/photo.jpg"

    def test_abs_url_returns_none_for_none(self):
        from src.routers.pages import _abs_url
        assert _abs_url(None) is None

    def test_abs_url_returns_none_for_empty(self):
        from src.routers.pages import _abs_url
        assert _abs_url("") is None

    def test_og_workshop_desc_exists(self):
        from src.routers.pages import _og_workshop_desc
        assert callable(_og_workshop_desc)

    def test_og_item_desc_exists(self):
        from src.routers.pages import _og_item_desc
        assert callable(_og_item_desc)

    def test_og_item_desc_with_no_listing(self):
        """Should return something even without a listing."""
        from src.routers.pages import _og_item_desc

        class FakeItem:
            description = "A nice thing"
            owner = None
        result = _og_item_desc(FakeItem(), None)
        assert "nice thing" in result

    def test_og_item_desc_with_listing(self):
        """Should include price and listing type."""
        from src.routers.pages import _og_item_desc

        class FakeListing:
            price = 120.0
            currency = "EUR"
            class listing_type:
                value = "training"
        class FakeItem:
            description = "Learn to sail"
            class owner:
                display_name = "Corrado"
                city = "Trapani"
        result = _og_item_desc(FakeItem(), FakeListing())
        assert "120.00" in result
        assert "Training" in result
        assert "Corrado" in result
        assert "Trapani" in result


# ── Item slug regeneration ──


class TestSlugRegeneration:
    def test_update_item_regenerates_slug(self):
        """update_item must regenerate slug when name changes."""
        source = inspect.getsource(
            __import__("src.routers.items", fromlist=["update_item"]).update_item
        )
        assert "_unique_slug" in source
        assert '"name"' in source or "'name'" in source

    def test_unique_slug_function_exists(self):
        from src.routers.items import _unique_slug
        assert inspect.iscoroutinefunction(_unique_slug)


# ── Workshop template: no Alpine var crash, has map ──


class TestWorkshopTemplate:
    def _read(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "workshop.html").read_text()

    def test_no_var_in_x_text(self):
        """Workshop template must not use 'var' inside Alpine x-text expressions."""
        content = self._read()
        # The old code had: x-text="(() => { var city = ...
        assert "x-text=\"(() =>" not in content, "Alpine x-text must not contain IIFE with var"

    def test_openstreetmap_embed(self):
        content = self._read()
        assert "openstreetmap.org/export/embed" in content

    def test_map_uses_lat_lng(self):
        content = self._read()
        assert "workshop.latitude" in content
        assert "workshop.longitude" in content

    def test_shows_state_region(self):
        content = self._read()
        assert "workshop.state_region" in content


# ── Item detail: no duplicate OG tags ──


class TestItemDetailOGTags:
    def _read(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "item_detail.html").read_text()

    def test_no_hardcoded_og_description(self):
        """item_detail must NOT have its own og:description -- base.html handles it."""
        content = self._read()
        # Should not contain og:description in the block head
        assert 'og:description" content="{{ (item.description' not in content

    def test_no_hardcoded_og_title(self):
        """item_detail must NOT have its own og:title -- base.html handles it."""
        content = self._read()
        assert 'og:title" content="{{ item.name' not in content

    def test_has_product_price_tags(self):
        """Item-specific product:price tags should exist."""
        content = self._read()
        assert "product:price:amount" in content
        assert "product:price:currency" in content

    def test_no_hardcoded_og_image_size_hints(self):
        """BL-177: item_detail.html no longer hardcodes 1200x630 on top of
        base.html's. Hardcoded dims were wrong for user uploads (typically
        1000x750) and broke WhatsApp/Facebook previews."""
        content = self._read()
        assert "og:image:width" not in content, (
            "item_detail.html must not declare og:image:width -- base.html "
            "handles dimensions only when actually known (no lying)"
        )


# ── Profile enum conversion ──


class TestProfileEnumConversion:
    def test_workshop_type_enum_conversion(self):
        """PATCH /users/me must convert workshop_type string to Python enum."""
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["update_me"]).update_me
        )
        assert "WorkshopType" in source
        assert "enum_map" in source
        # Must try both lowercase and uppercase
        assert ".upper()" in source

    def test_profile_cache_invalidated_on_save(self):
        """Dashboard must clear _profileCache after save."""
        content = (Path(__file__).parent.parent / "src" / "templates" / "pages" / "dashboard.html").read_text()
        assert "_profileCache = null" in content
        assert "_profilePromise = null" in content

    def test_save_shows_error_toast(self):
        """Dashboard must show error toast on failed save."""
        content = (Path(__file__).parent.parent / "src" / "templates" / "pages" / "dashboard.html").read_text()
        assert "Failed to save profile" in content or "Network error" in content


# ── Page render smoke tests ──


def test_og_item_desc_no_crash_on_empty():
    """Should not crash with completely empty item."""
    from src.routers.pages import _og_item_desc
    class EmptyItem:
        description = None
        owner = None
    result = _og_item_desc(EmptyItem(), None)
    assert result == "Available on La Piazza"
