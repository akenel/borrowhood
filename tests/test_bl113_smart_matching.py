"""Tests for BL-113: Smart Matching on Help Board.

Covers:
1. Matching service exists and is callable
2. Category synonyms are defined
3. API endpoint exists
4. Help Board template shows suggested helpers
"""

import pytest
import inspect
from pathlib import Path


# ── Matching service ──


class TestMatchingService:
    def test_function_exists(self):
        from src.services.helpboard_matching import find_suggested_helpers
        assert inspect.iscoroutinefunction(find_suggested_helpers)

    def test_category_synonyms_defined(self):
        from src.services.helpboard_matching import CATEGORY_SYNONYMS
        assert isinstance(CATEGORY_SYNONYMS, dict)
        assert "repairs" in CATEGORY_SYNONYMS
        assert "welding" in CATEGORY_SYNONYMS
        assert "woodworking" in CATEGORY_SYNONYMS

    def test_synonyms_are_lists(self):
        from src.services.helpboard_matching import CATEGORY_SYNONYMS
        for cat, syns in CATEGORY_SYNONYMS.items():
            assert isinstance(syns, list), f"Synonyms for '{cat}' must be a list"
            assert len(syns) > 0, f"'{cat}' must have at least one synonym"

    def test_matching_function_signature(self):
        from src.services.helpboard_matching import find_suggested_helpers
        sig = inspect.signature(find_suggested_helpers)
        params = list(sig.parameters.keys())
        assert "db" in params
        assert "post_category" in params
        assert "post_author_id" in params
        assert "limit" in params


# ── API endpoint ──


class TestSuggestedHelpersEndpoint:
    def test_endpoint_exists(self):
        from src.routers.helpboard import suggested_helpers
        assert inspect.iscoroutinefunction(suggested_helpers)

    def test_endpoint_signature(self):
        from src.routers.helpboard import suggested_helpers
        sig = inspect.signature(suggested_helpers)
        params = list(sig.parameters.keys())
        assert "post_id" in params
        assert "limit" in params

    def test_endpoint_is_get(self):
        """Suggested helpers should be a GET endpoint (public, no auth)."""
        from src.routers.helpboard import router
        routes = [r for r in router.routes if hasattr(r, 'path') and 'suggested-helpers' in r.path]
        assert len(routes) == 1
        assert "GET" in routes[0].methods


# ── Help Board template ──


class TestHelpBoardTemplate:
    def _read(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "helpboard.html").read_text()

    def test_suggested_helpers_section_exists(self):
        content = self._read()
        assert "suggested-helpers" in content

    def test_fetches_from_api(self):
        content = self._read()
        assert "/api/v1/helpboard/posts/" in content
        assert "/suggested-helpers" in content

    def test_shows_helper_cards(self):
        content = self._read()
        assert "h.display_name" in content
        assert "h.skill_name" in content

    def test_shows_verification_badge(self):
        content = self._read()
        assert "h.verified_by_count" in content
        assert "verified" in content

    def test_only_shows_for_open_need_posts(self):
        """Suggested helpers should only appear for open 'need' posts."""
        content = self._read()
        assert "activePost.status === 'open'" in content
        assert "activePost.help_type === 'need'" in content

    def test_links_to_workshop(self):
        content = self._read()
        assert "'/workshop/' + h.slug" in content


# ── User skills model (matching depends on this) ──


class TestUserSkillsModel:
    def test_skill_model_exists(self):
        from src.models.user import BHUserSkill
        cols = {c.name for c in BHUserSkill.__table__.columns}
        assert "skill_name" in cols
        assert "category" in cols
        assert "self_rating" in cols
        assert "verified_by_count" in cols
        assert "years_experience" in cols

    def test_skill_has_user_foreign_key(self):
        from src.models.user import BHUserSkill
        cols = {c.name for c in BHUserSkill.__table__.columns}
        assert "user_id" in cols
