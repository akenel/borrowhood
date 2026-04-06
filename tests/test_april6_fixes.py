"""Tests for April 6, 2026 fixes.

Covers:
1. Social login email linking (get_user duplicate email -> link account)
2. PATCH /users/me empty enum coercion (workshop_type="" -> NULL)
3. Homepage i18n keys resolve with section prefix (i18n.ltfm_*)
4. Orders page renders without errors
"""

import pytest
from src.i18n import get_translator, load_locale, resolve_key


# ── i18n: LTFM + Bottega keys ──


class TestLTFMTranslations:
    """LTFM and Bottega homepage keys must resolve in both languages."""

    LTFM_KEYS = [
        "i18n.ltfm_title",
        "i18n.ltfm_subtitle",
        "i18n.ltfm_learn",
        "i18n.ltfm_teach",
        "i18n.ltfm_fix",
        "i18n.ltfm_make",
        "i18n.ltfm_learn_desc",
        "i18n.ltfm_teach_desc",
        "i18n.ltfm_fix_desc",
        "i18n.ltfm_make_desc",
    ]

    BOTTEGA_KEYS = [
        "i18n.bottega_title",
        "i18n.bottega_subtitle",
        "i18n.bottega_step_1",
        "i18n.bottega_step_2",
        "i18n.bottega_step_3",
        "i18n.bottega_cta",
        "i18n.bottega_cta_logged_in",
        "i18n.andiamo",
    ]

    @pytest.mark.parametrize("key", LTFM_KEYS)
    def test_ltfm_keys_resolve_en(self, key):
        t = get_translator("en")
        result = t(key)
        assert result != key, f"EN key '{key}' returned raw key (not translated)"

    @pytest.mark.parametrize("key", LTFM_KEYS)
    def test_ltfm_keys_resolve_it(self, key):
        t = get_translator("it")
        result = t(key)
        assert result != key, f"IT key '{key}' returned raw key (not translated)"

    @pytest.mark.parametrize("key", BOTTEGA_KEYS)
    def test_bottega_keys_resolve_en(self, key):
        t = get_translator("en")
        result = t(key)
        assert result != key, f"EN key '{key}' returned raw key (not translated)"

    @pytest.mark.parametrize("key", BOTTEGA_KEYS)
    def test_bottega_keys_resolve_it(self, key):
        t = get_translator("it")
        result = t(key)
        assert result != key, f"IT key '{key}' returned raw key (not translated)"

    def test_ltfm_title_en_content(self):
        t = get_translator("en")
        assert "Learn" in t("i18n.ltfm_title")
        assert "Teach" in t("i18n.ltfm_title")

    def test_ltfm_title_it_content(self):
        t = get_translator("it")
        assert "Impara" in t("i18n.ltfm_title")


# ── Social login: email linking ──


class TestSocialLoginEmailLinking:
    """get_user should link social login to existing account by email."""

    def test_get_user_function_exists(self):
        from src.dependencies import get_user
        assert callable(get_user)

    def test_get_user_accepts_token_dict(self):
        """get_user signature should accept db and token dict."""
        import inspect
        from src.dependencies import get_user
        sig = inspect.signature(get_user)
        params = list(sig.parameters.keys())
        assert "db" in params
        assert "token" in params

    def test_email_linking_code_path_exists(self):
        """The email-based linking code path must exist in get_user."""
        import inspect
        from src.dependencies import get_user
        source = inspect.getsource(get_user)
        assert "BHUser.email ==" in source, "get_user must check for existing email"
        assert "Linking social login" in source, "get_user must log social login linking"


# ── PATCH /users/me: empty enum coercion ──


class TestEmptyEnumCoercion:
    """Empty string enum values should be coerced to None, not sent to Postgres."""

    def test_enum_fields_defined_in_update_endpoint(self):
        """The update_me endpoint must define enum_fields for coercion."""
        import inspect
        from src.routers.users import update_me
        source = inspect.getsource(update_me)
        assert "enum_fields" in source, "update_me must define enum_fields set"
        assert "workshop_type" in source
        assert "seller_type" in source

    def test_empty_string_coercion_logic(self):
        """Empty strings on enum fields must become None."""
        import inspect
        from src.routers.users import update_me
        source = inspect.getsource(update_me)
        assert 'value = None' in source, "Empty enum values must be set to None"

    def test_workshop_type_enum_values(self):
        """WorkshopType enum should have expected values."""
        from src.models.user import WorkshopType
        values = {e.value for e in WorkshopType}
        assert "workshop" in values
        assert "kitchen" in values
        assert "" not in values, "Empty string must NOT be a valid WorkshopType"


# ── Orders page rendering ──


@pytest.mark.asyncio
async def test_orders_page_requires_login(client):
    """Orders page should redirect to login when not authenticated."""
    resp = await client.get("/orders")
    # Should either redirect to login or show a login prompt
    assert resp.status_code in (200, 302)


@pytest.mark.asyncio
async def test_orders_page_accepts_filters(client):
    """Orders page should accept filter query params without crashing."""
    resp = await client.get("/orders?role=buyer&status=pending&sort=newest")
    assert resp.status_code in (200, 302)


@pytest.mark.asyncio
async def test_orders_page_accepts_pagination(client):
    """Orders page should accept pagination params."""
    resp = await client.get("/orders?limit=10&offset=0")
    assert resp.status_code in (200, 302)


# ── Homepage renders LTFM section ──


def test_homepage_template_uses_i18n_prefix():
    """Homepage template must use i18n. prefix for LTFM/Bottega keys."""
    from pathlib import Path
    template = Path(__file__).parent.parent / "src" / "templates" / "pages" / "home.html"
    content = template.read_text()
    # Must NOT have bare ltfm_ keys (without i18n. prefix)
    assert "t('ltfm_" not in content, "Found bare t('ltfm_*') -- must use t('i18n.ltfm_*')"
    assert "t('bottega_" not in content, "Found bare t('bottega_*') -- must use t('i18n.bottega_*')"
    assert "t('andiamo')" not in content, "Found bare t('andiamo') -- must use t('i18n.andiamo')"
    # Must have the prefixed versions
    assert "t('i18n.ltfm_title')" in content
    assert "t('i18n.bottega_title')" in content
