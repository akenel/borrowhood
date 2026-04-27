"""Type-first /list splash regression guards (BL-175, April 28, 2026).

Angel's TTT call: ask 'what are you posting?' first, before name/photos/etc.
Cuts confusing fields-for-the-wrong-type and gives raffles their own door.

Contract:
- /list with NO ?type= -> renders list_picker.html (the splash)
- /list?type=X (one of valid PRESET_TYPES) -> renders list_item.html (the form)
- /list?duplicate_from=UUID -> bypasses splash (type comes from source)
- Splash has 6 cards, each linking to a flow
- 5 cards link to /list?type=X, 1 (raffle) links to /raffles/create
"""
from pathlib import Path

import pytest
from httpx import AsyncClient


REPO_ROOT = Path(__file__).resolve().parent.parent
PICKER_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "list_picker.html").read_text()
ITEM_PY = (REPO_ROOT / "src" / "routers" / "pages" / "item.py").read_text()


class TestPickerTemplate:
    """The splash page itself: 6 cards, right hrefs, right copy."""

    def test_template_has_six_cards(self):
        # Each card is an <a href="..."> with a min-h-[160px] in its class
        card_count = PICKER_HTML.count("min-h-[160px]")
        assert card_count == 6, (
            f"Expected exactly 6 picker cards (Lend/Service/Teach/Event/"
            f"Raffle/Giveaway), got {card_count}"
        )

    def test_lend_card_links_to_rent(self):
        assert 'href="/list?type=rent"' in PICKER_HTML, (
            "Lend or Sell card must default to ?type=rent (user can change to "
            "sell on Step 3)"
        )

    def test_service_card_links_to_service(self):
        assert 'href="/list?type=service"' in PICKER_HTML

    def test_teach_card_links_to_training(self):
        assert 'href="/list?type=training"' in PICKER_HTML

    def test_event_card_links_to_event(self):
        assert 'href="/list?type=event"' in PICKER_HTML

    def test_raffle_card_redirects_to_raffles_create(self):
        # Raffles get their own dedicated flow, not the listing form
        assert 'href="/raffles/create"' in PICKER_HTML, (
            "Raffle card must link to /raffles/create -- raffles use a "
            "dedicated flow with ticket prices, draw config, etc."
        )

    def test_giveaway_card_links_to_giveaway(self):
        assert 'href="/list?type=giveaway"' in PICKER_HTML

    def test_template_has_help_link_for_unsure_users(self):
        assert "Not sure?" in PICKER_HTML or "Non sei sicuro?" in PICKER_HTML, (
            "Splash must have a 'not sure?' fallback link for users who "
            "don't know which to pick"
        )


class TestRouteWiring:
    """The /list route must serve the splash when no type is set, and the
    form when type is set."""

    def test_route_renders_picker_when_no_type(self):
        # The route must call _render('pages/list_picker.html', ...) when
        # preset_type is None and not duplicating
        assert 'pages/list_picker.html' in ITEM_PY, (
            "/list route must render the picker template when no ?type= is set"
        )

    def test_route_skips_splash_for_duplicate_from(self):
        # Duplicating an existing item carries its type with it -- splash
        # would be redundant and break the one-tap relist UX
        assert "has_dup" in ITEM_PY and "duplicate_from" in ITEM_PY, (
            "Duplicate flow must bypass the splash so the source type "
            "carries through to the form"
        )


@pytest.mark.asyncio
class TestRouteEndToEnd:
    """End-to-end behavior of the route. Anonymous users get redirected to
    /login. We can't test logged-in flow easily without auth fixtures."""

    async def test_anon_visit_to_list_redirects_to_login(self, client):
        r = await client.get("/list", follow_redirects=False)
        # Either redirect to login OR direct serve depending on auth
        # Anon should redirect
        assert r.status_code in (302, 303, 307), (
            f"Anon /list must redirect to /login, got {r.status_code}"
        )

    async def test_anon_visit_to_list_with_type_redirects_too(self, client):
        # Same gate -- ?type= doesn't bypass auth
        r = await client.get("/list?type=event", follow_redirects=False)
        assert r.status_code in (302, 303, 307)
