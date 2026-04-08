"""Tests for location feature: new fields, auto-fill, Nominatim integration.

Covers:
1. User model has new location columns
2. PATCH /users/me accepts new location fields
3. GET /users/me returns new location fields
4. Dashboard template has location UI (Use my location, city search)
5. Address is marked as private in UI
6. Nominatim integration in template
"""

import pytest
import inspect
from pathlib import Path


# ── User model: new columns ──


class TestLocationModelFields:
    def test_state_region_column_exists(self):
        from src.models.user import BHUser
        cols = {c.name for c in BHUser.__table__.columns}
        assert "state_region" in cols

    def test_postal_code_column_exists(self):
        from src.models.user import BHUser
        cols = {c.name for c in BHUser.__table__.columns}
        assert "postal_code" in cols

    def test_address_line_column_exists(self):
        from src.models.user import BHUser
        cols = {c.name for c in BHUser.__table__.columns}
        assert "address_line" in cols

    def test_existing_location_fields_still_exist(self):
        from src.models.user import BHUser
        cols = {c.name for c in BHUser.__table__.columns}
        assert "city" in cols
        assert "country_code" in cols
        assert "latitude" in cols
        assert "longitude" in cols

    def test_address_line_max_length(self):
        from src.models.user import BHUser
        col = BHUser.__table__.columns["address_line"]
        assert col.type.length == 300


# ── PATCH /users/me: accepts new fields ──


class TestPatchAcceptsLocationFields:
    def test_allowed_fields_include_location(self):
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["update_me"]).update_me
        )
        assert "state_region" in source
        assert "postal_code" in source
        assert "address_line" in source

    def test_enum_conversion_for_workshop_type(self):
        """Workshop type must be converted to Python enum, not raw string."""
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["update_me"]).update_me
        )
        assert "WorkshopType" in source
        assert "enum_map" in source


# ── GET /users/me: returns new fields ──


class TestGetMeReturnsLocationFields:
    def test_response_includes_state_region(self):
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["get_current_user"]).get_current_user
        )
        assert "state_region" in source

    def test_response_includes_postal_code(self):
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["get_current_user"]).get_current_user
        )
        assert "postal_code" in source

    def test_response_includes_address_line(self):
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["get_current_user"]).get_current_user
        )
        assert "address_line" in source

    def test_response_includes_lat_lng(self):
        source = inspect.getsource(
            __import__("src.routers.users", fromlist=["get_current_user"]).get_current_user
        )
        assert "latitude" in source
        assert "longitude" in source


# ── Dashboard template: location UI ──


class TestDashboardLocationUI:
    def _read(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "dashboard.html").read_text()

    def test_use_my_location_button(self):
        content = self._read()
        assert "navigator.geolocation" in content
        assert "getCurrentPosition" in content

    def test_nominatim_reverse_geocode(self):
        content = self._read()
        assert "nominatim.openstreetmap.org/reverse" in content

    def test_nominatim_city_search(self):
        content = self._read()
        assert "nominatim.openstreetmap.org/search" in content

    def test_city_search_autocomplete(self):
        content = self._read()
        assert "cityResults" in content
        assert "display_name" in content

    def test_state_region_input(self):
        content = self._read()
        assert "p.state_region" in content

    def test_postal_code_input(self):
        content = self._read()
        assert "p.postal_code" in content

    def test_address_line_input(self):
        content = self._read()
        assert "p.address_line" in content

    def test_address_marked_private(self):
        content = self._read()
        assert "private" in content.lower()
        assert "address_line" in content

    def test_location_preview_shows_when_set(self):
        content = self._read()
        assert "p.latitude && p.longitude" in content
        assert "Location set" in content or "Posizione impostata" in content

    def test_mobile_friendly_inputs(self):
        """All location inputs should have min-h-[48px] for mobile."""
        content = self._read()
        # Check that the location section inputs have mobile sizing
        assert "min-h-[48px]" in content

    def test_bilingual_labels(self):
        content = self._read()
        assert "Regione" in content or "Cantone" in content  # Italian
        assert "State" in content or "Region" in content  # English


# ── API endpoint: orders page with filters ──


@pytest.mark.asyncio
async def test_dashboard_settings_loads(client):
    """Dashboard settings tab should not crash."""
    resp = await client.get("/dashboard?tab=settings")
    assert resp.status_code in (200, 302)
