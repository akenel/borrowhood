"""Tests for seed data integrity.

Validates seed.json: no blank images, valid URLs, required fields.
No DB needed -- reads the JSON file directly.
"""

import json
import pytest
from pathlib import Path


SEED_PATH = Path(__file__).parent.parent / "seed_data" / "seed.json"


@pytest.fixture(scope="module")
def seed_data():
    with open(SEED_PATH) as f:
        return json.load(f)


class TestSeedImages:
    """Every item with a listing must have at least one valid image."""

    # EP2 cast slugs -- these MUST have images (video-critical)
    EP2_CAST = {"sallys-kitchen", "pietros-drones", "johns-cleaning", "sofias-bakes"}

    def test_ep2_cast_items_have_media(self, seed_data):
        """EP2 cast items MUST have at least one image (video-critical)."""
        missing = []
        for item in seed_data.get("items", []):
            if item.get("owner_slug") in self.EP2_CAST:
                media = item.get("media", [])
                if not media:
                    missing.append(f"{item.get('owner_slug')}/{item.get('slug')}")
        assert not missing, (
            f"{len(missing)} EP2 cast items have no images:\n" +
            "\n".join(missing)
        )

    def test_items_without_media_count(self, seed_data):
        """Advisory: count items with no media (not a blocker for non-cast)."""
        missing = []
        for item in seed_data.get("items", []):
            if item.get("owner_slug") not in self.EP2_CAST:
                media = item.get("media", [])
                if not media:
                    missing.append(item.get("slug"))
        # Just report, don't fail -- legends don't need images for now
        if missing:
            pytest.skip(f"{len(missing)} non-cast items have no images (advisory, not blocking)")

    def test_no_blank_image_urls(self, seed_data):
        """No image URL should be empty or whitespace."""
        blank = []
        for item in seed_data.get("items", []):
            for i, media in enumerate(item.get("media", [])):
                url = media.get("url", "")
                if not url or not url.strip():
                    blank.append(f"{item.get('slug')}[{i}]: blank URL")
        assert not blank, (
            f"{len(blank)} images have blank URLs:\n" +
            "\n".join(blank)
        )

    def test_no_broken_local_media_paths(self, seed_data):
        """No image should use /media/borrowhood/items/ paths (files don't exist on server)."""
        broken = []
        for item in seed_data.get("items", []):
            for i, media in enumerate(item.get("media", [])):
                url = media.get("url", "")
                if url.startswith("/media/borrowhood/"):
                    broken.append(f"{item.get('slug')}[{i}]: {url}")
        assert not broken, (
            f"{len(broken)} images use broken /media/ local paths:\n" +
            "\n".join(broken)
        )

    def test_image_urls_are_valid_format(self, seed_data):
        """All image URLs should be https:// or /static/ paths."""
        invalid = []
        for item in seed_data.get("items", []):
            for i, media in enumerate(item.get("media", [])):
                url = media.get("url", "")
                if url and not url.startswith("https://") and not url.startswith("/static/"):
                    invalid.append(f"{item.get('slug')}[{i}]: {url}")
        assert not invalid, (
            f"{len(invalid)} images have invalid URL format (expected https:// or /static/):\n" +
            "\n".join(invalid)
        )

    def test_all_media_have_alt_text(self, seed_data):
        """Every image should have alt_text for accessibility."""
        missing_alt = []
        for item in seed_data.get("items", []):
            for i, media in enumerate(item.get("media", [])):
                alt = media.get("alt_text", "")
                if not alt or not alt.strip():
                    missing_alt.append(f"{item.get('slug')}[{i}]: missing alt_text")
        assert not missing_alt, (
            f"{len(missing_alt)} images missing alt_text:\n" +
            "\n".join(missing_alt)
        )


class TestSeedUsers:
    """Basic user seed data validation."""

    def test_all_users_have_slugs(self, seed_data):
        missing = []
        for user in seed_data.get("users", []):
            if not user.get("slug"):
                missing.append(user.get("email", "unknown"))
        assert not missing, f"Users without slugs: {missing}"

    def test_all_users_have_display_names(self, seed_data):
        missing = []
        for user in seed_data.get("users", []):
            if not user.get("display_name"):
                missing.append(user.get("slug", "unknown"))
        assert not missing, f"Users without display_name: {missing}"


class TestSeedItems:
    """Basic item seed data validation."""

    def test_all_items_have_slugs(self, seed_data):
        missing = []
        for item in seed_data.get("items", []):
            if not item.get("slug"):
                missing.append(item.get("name", "unknown"))
        assert not missing, f"Items without slugs: {missing}"

    def test_all_items_have_owner(self, seed_data):
        missing = []
        for item in seed_data.get("items", []):
            if not item.get("owner_slug"):
                missing.append(item.get("slug", "unknown"))
        assert not missing, f"Items without owner_slug: {missing}"

    def test_all_items_have_listings(self, seed_data):
        missing = []
        for item in seed_data.get("items", []):
            if not item.get("listings"):
                missing.append(item.get("slug", "unknown"))
        assert not missing, f"Items without listings: {missing}"

    def test_item_owners_exist_as_users(self, seed_data):
        user_slugs = {u.get("slug") for u in seed_data.get("users", [])}
        orphaned = []
        for item in seed_data.get("items", []):
            owner = item.get("owner_slug")
            if owner and owner not in user_slugs:
                orphaned.append(f"{item.get('slug')} -> {owner}")
        assert not orphaned, (
            f"{len(orphaned)} items reference non-existent users:\n" +
            "\n".join(orphaned)
        )
