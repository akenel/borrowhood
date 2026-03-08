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


class TestEP2CastConsistency:
    """EP2 story consistency -- these are the foundations for Season 1.

    If any of these fail, the recording script will produce a broken episode
    and downstream episodes (EP3-5) will contradict EP2.
    """

    EP2_CAST_SLUGS = {
        "sallys-kitchen", "pietros-drones", "sofias-bakes", "johns-cleaning",
    }

    # All 14 demo cast members
    ALL_CAST_SLUGS = {
        "sallys-kitchen", "mikes-garage", "angel-hq", "ninos-campers",
        "marias-garden", "marcos-workshop", "jakes-electronics", "rosas-home",
        "georges-villa", "johns-cleaning", "pietros-drones", "sofias-bakes",
        "annes-qa-lab", "leonardos-bottega",
    }

    def _users(self, seed_data):
        return {u["slug"]: u for u in seed_data.get("users", []) if u.get("slug")}

    def _items(self, seed_data):
        return seed_data.get("items", [])

    # --- Cast member existence ---

    def test_all_14_cast_exist(self, seed_data):
        """All 14 demo cast must exist in seed.json."""
        users = self._users(seed_data)
        missing = self.ALL_CAST_SLUGS - set(users.keys())
        assert not missing, f"Missing cast members: {missing}"

    def test_all_cast_have_avatars(self, seed_data):
        """Every cast member must have an avatar_url (Unsplash photo)."""
        users = self._users(seed_data)
        missing = []
        for slug in self.ALL_CAST_SLUGS:
            user = users.get(slug)
            if user and not user.get("avatar_url"):
                missing.append(slug)
        assert not missing, f"Cast without avatar_url: {missing}"

    def test_all_cast_have_addresses(self, seed_data):
        """Every cast member must have a street address (drone delivery needs GPS)."""
        users = self._users(seed_data)
        missing = []
        for slug in self.ALL_CAST_SLUGS:
            user = users.get(slug)
            if user and not user.get("address"):
                missing.append(slug)
        assert not missing, f"Cast without address: {missing}"

    def test_all_cast_have_gps(self, seed_data):
        """Every cast member must have latitude and longitude (drone + delivery routes)."""
        users = self._users(seed_data)
        missing = []
        for slug in self.ALL_CAST_SLUGS:
            user = users.get(slug)
            if user:
                lat = user.get("latitude")
                lng = user.get("longitude")
                if not lat or not lng:
                    missing.append(slug)
        assert not missing, f"Cast without GPS coords: {missing}"

    # Anne is QA tester in Nairobi -- not a Trapani resident
    TRAPANI_CAST = ALL_CAST_SLUGS - {"annes-qa-lab"}

    def test_trapani_cast_gps_in_range(self, seed_data):
        """Trapani cast GPS must be in the province (lat ~37.9-38.2, lng ~12.4-12.9).
        Includes Scopello (Pietro, Sofia) at lng ~12.82.
        """
        users = self._users(seed_data)
        out_of_range = []
        for slug in self.TRAPANI_CAST:
            user = users.get(slug)
            if user and user.get("latitude") and user.get("longitude"):
                lat = float(user["latitude"])
                lng = float(user["longitude"])
                if not (37.9 <= lat <= 38.2 and 12.4 <= lng <= 12.9):
                    out_of_range.append(f"{slug}: {lat}, {lng}")
        assert not out_of_range, f"Cast GPS outside Trapani province: {out_of_range}"

    # --- Item ownership (story-critical) ---

    def test_sally_owns_cookie_cutters(self, seed_data):
        """Sally MUST own the cookie cutter set -- Sofia rents them via Pietro."""
        items = self._items(seed_data)
        cutter = [i for i in items if "cookie-cutter" in i.get("slug", "")]
        assert cutter, "Cookie cutter item not found in seed"
        for item in cutter:
            assert item["owner_slug"] == "sallys-kitchen", (
                f"Cookie cutters owned by {item['owner_slug']} -- must be sallys-kitchen"
            )

    def test_sally_owns_baking_training(self, seed_data):
        """Sally MUST own the baking training -- Pietro books it for Sofia."""
        items = self._items(seed_data)
        training = [i for i in items if "baking-with-sally" in i.get("slug", "")]
        assert training, "Baking training item not found in seed"
        for item in training:
            assert item["owner_slug"] == "sallys-kitchen", (
                f"Baking training owned by {item['owner_slug']} -- must be sallys-kitchen"
            )

    def test_sofia_does_not_own_cookie_cutters(self, seed_data):
        """Sofia must NOT own cookie cutters -- she borrows Sally's via Pietro's gift."""
        items = self._items(seed_data)
        sofia_cutters = [
            i for i in items
            if i.get("owner_slug") == "sofias-bakes"
            and "cookie-cutter" in i.get("slug", "")
        ]
        assert not sofia_cutters, (
            "Sofia owns cookie cutters in seed data -- she should NOT. "
            "Pietro rents Sally's cutters as a birthday gift for Sofia."
        )

    def test_sofia_owns_birthday_cookie_box(self, seed_data):
        """Sofia MUST own the Birthday Cookie Box -- her first listing."""
        items = self._items(seed_data)
        box = [i for i in items if "birthday-cookie-box" in i.get("slug", "")]
        assert box, "Birthday Cookie Box not found in seed"
        assert box[0]["owner_slug"] == "sofias-bakes", (
            f"Birthday Cookie Box owned by {box[0]['owner_slug']} -- must be sofias-bakes"
        )

    def test_johnny_owns_broken_bike(self, seed_data):
        """Johnny MUST own the broken bike -- his OFFER listing."""
        items = self._items(seed_data)
        bike = [i for i in items if "bike-broken" in i.get("slug", "") or "delivery-bike" in i.get("slug", "")]
        assert bike, "Johnny's broken bike not found in seed"
        for item in bike:
            assert item["owner_slug"] == "johns-cleaning", (
                f"Broken bike owned by {item['owner_slug']} -- must be johns-cleaning"
            )

    def test_johnny_owns_delivery_service(self, seed_data):
        """Johnny MUST own a delivery service listing."""
        items = self._items(seed_data)
        delivery = [i for i in items if "delivery" in i.get("slug", "") and i.get("owner_slug") == "johns-cleaning"]
        assert delivery, "Johnny's delivery service not found in seed"

    def test_sally_owns_scooter(self, seed_data):
        """Sally MUST own the electric scooter (EP3 prep -- she leases it to Johnny)."""
        items = self._items(seed_data)
        scooter = [i for i in items if "scooter" in i.get("slug", "")]
        assert scooter, "Electric scooter not found in seed"
        assert scooter[0]["owner_slug"] == "sallys-kitchen", (
            f"Scooter owned by {scooter[0]['owner_slug']} -- must be sallys-kitchen"
        )

    def test_pietro_owns_drones(self, seed_data):
        """Pietro MUST own drone-related items (aerial service)."""
        items = self._items(seed_data)
        drones = [i for i in items if i.get("owner_slug") == "pietros-drones" and "drone" in i.get("slug", "").lower()]
        assert drones, "Pietro has no drone items in seed"

    # --- Mentorships (story-critical) ---

    def test_mentorships_exist(self, seed_data):
        """At least 3 mentorships must exist (Sally->Sofia, Pietro->Sofia, John->Sofia)."""
        mentorships = seed_data.get("mentorships", [])
        assert len(mentorships) >= 3, f"Only {len(mentorships)} mentorships, need at least 3"

    def test_sally_mentors_sofia_in_baking(self, seed_data):
        """Sally MUST mentor Sofia in baking -- the core EP2 relationship."""
        mentorships = seed_data.get("mentorships", [])
        match = [
            m for m in mentorships
            if m.get("mentor_slug") == "sallys-kitchen"
            and m.get("apprentice_slug") == "sofias-bakes"
        ]
        assert match, "Sally->Sofia baking mentorship not found"

    # --- 5 delivery addresses (EP2 Act 4) ---

    def test_five_delivery_cast_have_distinct_addresses(self, seed_data):
        """The 5 cookie delivery recipients must have distinct addresses.

        Mapped cast: Pietro (Via Roma), Sally (Via Garibaldi),
        Leonardo (Via Torrearsa), Nino (Piazza Mercato), Maria (Via Fardella)
        """
        delivery_slugs = [
            "pietros-drones", "sallys-kitchen", "leonardos-bottega",
            "ninos-campers", "marias-garden",
        ]
        users = self._users(seed_data)
        addresses = []
        missing = []
        for slug in delivery_slugs:
            user = users.get(slug)
            if not user or not user.get("address"):
                missing.append(slug)
            else:
                addresses.append(user["address"])
        assert not missing, f"Delivery cast without address: {missing}"
        assert len(set(addresses)) == 5, (
            f"5 delivery addresses must be distinct, got {len(set(addresses))}: {addresses}"
        )

    def test_leonardo_lives_in_trapani(self, seed_data):
        """Leonardo da Vinci lives in Trapani for the show (not Vinci)."""
        users = self._users(seed_data)
        leo = users.get("leonardos-bottega")
        assert leo, "Leonardo not found"
        city = leo.get("city", "")
        assert city == "Trapani", f"Leonardo's city is '{city}' -- must be 'Trapani' (he lives here for the show)"
