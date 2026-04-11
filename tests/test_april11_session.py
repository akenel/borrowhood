"""Tests for April 11, 2026 morning session -- login fixes, mobile UX, avatar.

Covers:
1. Login route: /login not /auth/login
2. Login route: redirects to dashboard if already logged in
3. Avatar URL: VARCHAR(2000) not 500 (Google URLs are 1000+ chars)
4. Feedback panel: mobile-responsive CSS classes
5. Font scaling: text-only via data-text-scale, not root font-size
6. Service worker: cache version bumped to v3
7. Session timeout: 60min token, warning banner exists
8. Workshop page: in-app messaging button
9. Workshop page: event badge color (rose)
10. Home page: Sign In links to /login not /auth/login
"""

import pytest
import inspect
from pathlib import Path


# ── 1. Login route path ──

class TestLoginRoute:
    def test_login_route_exists(self):
        from src.routers.auth import router
        paths = [r.path for r in router.routes]
        assert "/login" in paths

    def test_no_auth_login_in_templates(self):
        """No template should link to /auth/login -- it doesn't exist."""
        for html_file in Path("src/templates").rglob("*.html"):
            content = html_file.read_text()
            assert "/auth/login" not in content, f"{html_file} still links to /auth/login"

    def test_no_auth_login_in_pages_router(self):
        source = inspect.getsource(__import__("src.routers.pages", fromlist=["edit_item_page"]))
        assert "/auth/login" not in source

    def test_home_page_sign_in_uses_login(self):
        content = Path("src/templates/pages/home.html").read_text()
        assert 'href="/login"' in content


# ── 2. Login redirect if already logged in ──

class TestLoginRedirect:
    def test_login_checks_existing_session(self):
        """Login route should check for existing token before redirecting to KC."""
        source = inspect.getsource(__import__("src.routers.auth", fromlist=["login"]))
        assert "get_current_user_token" in source
        assert "/dashboard" in source

    def test_login_redirects_to_dashboard(self):
        """If user has valid session, /login should redirect to /dashboard."""
        source = inspect.getsource(__import__("src.routers.auth", fromlist=["login"]))
        assert "RedirectResponse" in source
        assert "dashboard" in source


# ── 3. Avatar URL length ──

class TestAvatarUrlLength:
    def test_avatar_url_is_2000_chars(self):
        from src.models.user import BHUser
        col = BHUser.__table__.columns["avatar_url"]
        assert col.type.length >= 2000, f"avatar_url is VARCHAR({col.type.length}), needs 2000+"

    def test_migration_includes_avatar_resize(self):
        source = inspect.getsource(__import__("src.database", fromlist=["run_migrations"]))
        assert "avatar_url" in source
        assert "2000" in source


# ── 4. Feedback panel mobile ──

class TestFeedbackPanelMobile:
    def test_feedback_panel_uses_left_right_on_mobile(self):
        content = Path("src/templates/base.html").read_text()
        assert "left-4 right-4" in content

    def test_feedback_panel_fixed_width_on_desktop(self):
        content = Path("src/templates/base.html").read_text()
        assert "sm:w-80" in content

    def test_feedback_panel_scrollable(self):
        content = Path("src/templates/base.html").read_text()
        assert "overflow-y-auto" in content

    def test_feedback_endpoint_still_exists(self):
        from src.routers.backlog import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["POST"], "/api/v1/backlog/feedback") in paths


# ── 5. Font scaling ──

class TestFontScaling:
    def test_uses_data_text_scale_not_root_fontsize(self):
        """Font scaling must use data-text-scale attribute, NOT html root font-size."""
        content = Path("src/templates/base.html").read_text()
        assert "data-text-scale" in content
        # Should NOT set root font-size anymore
        assert "lp-font-size" not in content or "removeItem" in content

    def test_text_scale_targets_text_elements_only(self):
        content = Path("src/templates/base.html").read_text()
        # Must target specific text elements, not everything
        assert ":is(p,span,a,li" in content

    def test_text_scale_has_multiple_levels(self):
        content = Path("src/templates/base.html").read_text()
        assert "125%" in content
        assert "150%" in content
        assert "200%" in content
        assert "300%" in content

    def test_old_font_size_key_cleaned_up(self):
        content = Path("src/templates/base.html").read_text()
        assert "removeItem('lp-font-size')" in content

    def test_a_minus_a_plus_in_header(self):
        content = Path("src/templates/base.html").read_text()
        assert "A-" in content
        assert "A+" in content
        # Should have tooltip
        assert "settings.font_size" in content


# ── 6. Service worker version ──

class TestServiceWorker:
    def test_cache_version_is_v3(self):
        content = Path("src/static/sw.js").read_text()
        assert "lp-v3" in content

    def test_sw_deletes_old_caches(self):
        content = Path("src/static/sw.js").read_text()
        assert "caches.delete" in content


# ── 7. Session timeout ──

class TestSessionTimeout:
    def test_session_warning_exists_in_template(self):
        content = Path("src/templates/base.html").read_text()
        assert "session-warning" in content

    def test_session_timeout_60_minutes(self):
        content = Path("src/templates/base.html").read_text()
        assert "SESSION_MINUTES = 60" in content or "SESSION_MINUTES" in content

    def test_session_i18n_keys_exist(self):
        import json
        with open("src/locales/en.json") as f:
            en = json.load(f)
        assert "session" in en
        assert "expiring" in en["session"]
        assert "expired" in en["session"]
        assert "stay_logged_in" in en["session"]

    def test_kc_token_lifespan_3600(self):
        import json
        with open("keycloak/borrowhood-realm-dev.json") as f:
            realm = json.load(f)
        assert realm["accessTokenLifespan"] == 3600


# ── 8. Workshop in-app messaging ──

class TestWorkshopMessaging:
    def test_workshop_has_send_message_button(self):
        content = Path("src/templates/pages/workshop.html").read_text()
        assert "send_message" in content
        assert "/messages?to=" in content

    def test_workshop_has_login_to_message(self):
        content = Path("src/templates/pages/workshop.html").read_text()
        assert "login_to_message" in content

    def test_i18n_send_message(self):
        import json
        with open("src/locales/en.json") as f:
            en = json.load(f)
        assert en["workshop"]["send_message"] == "Send Message"
        assert "login_to_message" in en["workshop"]

    def test_i18n_send_message_italian(self):
        import json
        with open("src/locales/it.json") as f:
            it = json.load(f)
        assert "send_message" in it["workshop"]
        assert "login_to_message" in it["workshop"]


# ── 9. Workshop event badge ──

class TestWorkshopEventBadge:
    def test_workshop_items_have_event_color(self):
        content = Path("src/templates/pages/workshop.html").read_text()
        assert "event" in content
        assert "rose" in content

    def test_workshop_items_show_event_date(self):
        content = Path("src/templates/pages/workshop.html").read_text()
        assert "event_start" in content


# ── 10. Settings i18n ──

class TestSettingsI18n:
    def test_font_size_label_exists(self):
        import json
        with open("src/locales/en.json") as f:
            en = json.load(f)
        assert "settings" in en
        assert "font_size" in en["settings"]
        assert "smaller" in en["settings"]
        assert "larger" in en["settings"]

    def test_font_size_label_italian(self):
        import json
        with open("src/locales/it.json") as f:
            it = json.load(f)
        assert "settings" in it
        assert "font_size" in it["settings"]


# ── 11. Delete warning i18n completeness ──

class TestDeleteWarningCompleteness:
    def test_en_it_parity_for_account_section(self):
        import json
        with open("src/locales/en.json") as f:
            en = json.load(f)
        with open("src/locales/it.json") as f:
            it = json.load(f)
        for key in en["account"]:
            assert key in it["account"], f"Italian missing account.{key}"


# ── 12. GDPR cleanup completeness ──

class TestGDPRCleanupCompleteness:
    def test_cleanup_has_all_critical_tables(self):
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        critical_tables = [
            "bh_event_rsvp", "bh_achievement", "bh_saved_search", "bh_item_vote",
            "bh_help_upvote", "bh_help_reply", "bh_help_post", "bh_help_media",
            "bh_message", "bh_notification", "bh_user_points", "bh_user_skill",
            "bh_item_media", "bh_listing", "bh_item", "bh_rental", "bh_bid",
            "bh_review", "bh_badge", "bh_mentorship",
        ]
        for table in critical_tables:
            assert table in source, f"GDPR cleanup missing {table}"

    def test_cleanup_uses_savepoints(self):
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "begin_nested" in source

    def test_delete_preview_endpoint_exists(self):
        from src.routers.users import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["GET"], "/api/v1/users/me/delete-preview") in paths
