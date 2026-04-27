"""Regression guards for the four feedback bugs Giulia Collaudo reported
on Android Chrome the morning of April 27, 2026.

  - BL-167: Notification badge doesn't clear after the user reads a notification
            (the PATCH /read got cancelled mid-flight when the anchor navigated)
  - BL-166: Leaderboard 'Streaks' and 'coaches' columns get cut off on mobile
  - BL-165: Raffle share preview has no image (item shares work fine)
  - BL-168: Service-item share preview has no image and no price (no fallback OG)

Each test pins a specific symptom so a future refactor can't silently
regress one of these.
"""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_HTML = (REPO_ROOT / "src" / "templates" / "base.html").read_text()
LEADERBOARD_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "leaderboard.html").read_text()
RAFFLE_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "raffle_detail.html").read_text()
ITEM_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "item_detail.html").read_text()
COMMUNITY_PY = (REPO_ROOT / "src" / "routers" / "pages" / "community.py").read_text()


# ---- BL-167: notification PATCH must complete after navigation ----

class TestNotifPatchKeepalive:
    """Both notification drawers (desktop + mobile) must use keepalive: true
    on the PATCH /read request, otherwise the browser cancels it when the
    anchor navigates and the badge stays stale until next reload."""

    def test_desktop_drawer_uses_keepalive(self):
        # The desktop drawer is the inline @click on the <a> in the dropdown
        marker = "/api/v1/notifications/' + n.id + '/read', { method: 'PATCH', keepalive: true }"
        assert marker in BASE_HTML, (
            "Desktop notification drawer's PATCH /read must include "
            "keepalive: true so the request survives the anchor navigation"
        )

    def test_mobile_drawer_uses_keepalive(self):
        # The mobile drawer's markRead() function -- look for the keepalive
        # comment + the actual fetch with keepalive
        assert "BL-167: keepalive" in BASE_HTML, (
            "Mobile drawer markRead() must reference BL-167 in the keepalive comment"
        )
        # Also assert the structural fix: the fetch in markRead has keepalive: true
        # Find markRead body and check it
        idx = BASE_HTML.find("async markRead(n) {")
        assert idx > 0, "Mobile markRead function not found"
        markread_block = BASE_HTML[idx:idx + 700]
        assert "keepalive: true" in markread_block, (
            "Mobile markRead must use keepalive: true on the PATCH so the "
            "badge counter stays consistent when the user taps a notification"
        )

    def test_no_remaining_unkeepalive_notification_patches(self):
        # Catch any future code that re-introduces a non-keepalive PATCH /read
        # by walking the file and looking for the bare pattern
        import re
        # Match: fetch('/api/v1/notifications/...read', {...}) WITHOUT keepalive
        pattern = re.compile(
            r"fetch\([^)]*?/api/v1/notifications/[^']*?/read[^)]*?\)",
            re.DOTALL,
        )
        offending = []
        for m in pattern.finditer(BASE_HTML):
            block = m.group(0)
            if "keepalive" not in block:
                offending.append(block[:120])
        assert not offending, (
            "Found PATCH /api/v1/notifications/.../read calls without "
            "keepalive: true. Add keepalive so the request survives anchor "
            "navigation. Offenders:\n" + "\n".join(offending)
        )


# ---- BL-171: mobile notification drawer needs Mark-all + poll + close-refresh ----

class TestMobileNotificationDrawerParity:
    """The mobile drawer was missing three things the desktop drawer had:
    a Mark-all-as-read button, a periodic poll, and a re-fetch-on-close.
    Without them, badge counts felt stale even after the user 'read' a
    notification (Angel's report April 27 morning shift).
    """

    def test_mobile_has_mark_all_read_function(self):
        # The Alpine x-data must declare a markAllRead() method
        idx = BASE_HTML.find("Mobile: notification + messages")
        assert idx > 0
        block = BASE_HTML[idx:idx + 3500]
        assert "async markAllRead()" in block, (
            "Mobile drawer must define markAllRead() so users can clear "
            "the badge without tapping each notification individually"
        )

    def test_mobile_has_mark_all_button_in_drawer_header(self):
        idx = BASE_HTML.find("Mobile notifications drawer")
        block = BASE_HTML[idx:idx + 2500]
        # Button must call markAllRead() and only show when there are unread
        assert '@click="markAllRead()"' in block, (
            "Mobile drawer header must include a Mark-all-as-read button"
        )
        assert 'x-show="nUnread > 0"' in block, (
            "Mark-all button must be hidden when nothing is unread"
        )

    def test_mobile_polls_for_summary_updates(self):
        idx = BASE_HTML.find("Mobile: notification + messages")
        block = BASE_HTML[idx:idx + 3500]
        # Must set up a 30-second poll like the desktop drawer
        assert "setInterval(() => loadSummary(), 30000)" in block, (
            "Mobile drawer must poll /summary every 30s so badge counts "
            "stay fresh without requiring a page refresh"
        )

    def test_mobile_closeNotifs_refetches_summary(self):
        idx = BASE_HTML.find("Mobile: notification + messages")
        block = BASE_HTML[idx:idx + 3500]
        assert "async closeNotifs()" in block, (
            "Mobile drawer must define closeNotifs() that re-fetches the "
            "summary -- otherwise the badge keeps a stale count after the "
            "user reads notifications and closes the drawer"
        )
        # And the close paths must use closeNotifs(), not bare notifOpen=false
        drawer_idx = BASE_HTML.find("Mobile notifications drawer")
        drawer_block = BASE_HTML[drawer_idx:drawer_idx + 2500]
        assert "closeNotifs()" in drawer_block, (
            "All close actions in the mobile drawer (X button, backdrop tap, "
            "notification tap) must call closeNotifs() to trigger the refresh"
        )


# ---- BL-166: leaderboard Streaks + Coaches must not cut off long names ----

class TestLeaderboardOverflowDefenses:
    """The Streaks and Coaches tabs must apply the same min-w-0 + truncate
    + flex-shrink-0 defenses the Rankings tab uses, otherwise long names
    push the right-side score column off-screen on mobile."""

    def _streaks_block(self) -> str:
        # Pull the Streaks template block
        start = LEADERBOARD_HTML.find("<!-- Streaks Tab -->")
        end = LEADERBOARD_HTML.find("<!-- Coaches Tab -->", start)
        assert start > 0 and end > start, "Streaks/Coaches markers not found"
        return LEADERBOARD_HTML[start:end]

    def _coaches_block(self) -> str:
        start = LEADERBOARD_HTML.find("<!-- Coaches Tab -->")
        # Read until the next major comment block or end of template
        # (Coaches is the last tab before footer)
        return LEADERBOARD_HTML[start:start + 3000]

    def test_streaks_name_div_has_min_w_0(self):
        block = self._streaks_block()
        assert "flex-1 min-w-0" in block, (
            "Streaks tab's name container must have `flex-1 min-w-0` so "
            "long display names truncate instead of pushing the streak "
            "number off-screen"
        )

    def test_streaks_name_span_truncates(self):
        block = self._streaks_block()
        assert 'class="font-semibold text-gray-900 truncate block"' in block, (
            "Streaks tab's display_name span must use `truncate block` "
            "(block needed because span is inline by default and truncate "
            "needs a block-level box)"
        )

    def test_streaks_score_block_does_not_shrink(self):
        block = self._streaks_block()
        assert 'class="text-right flex-shrink-0"' in block, (
            "Streaks tab's right-side score block must use flex-shrink-0 "
            "so it stays visible no matter how long the name is"
        )

    def test_coaches_name_div_has_min_w_0(self):
        block = self._coaches_block()
        assert "flex-1 min-w-0" in block, (
            "Coaches tab's name container must have flex-1 min-w-0"
        )

    def test_coaches_name_span_truncates(self):
        block = self._coaches_block()
        assert 'class="font-semibold text-gray-900 truncate block"' in block, (
            "Coaches tab's display_name span must use truncate block"
        )

    def test_coaches_score_block_does_not_shrink(self):
        block = self._coaches_block()
        assert 'class="text-right flex-shrink-0"' in block, (
            "Coaches tab's right-side score block must use flex-shrink-0"
        )


# ---- BL-165: raffle pages need rich OG tags so shares show image + price ----

class TestRaffleOgTags:
    """The raffle detail route must pass og_title + og_description +
    og_image so social platforms can build a rich preview card. Item
    shares already do this; raffles were the regression."""

    def test_raffle_route_passes_og_title(self):
        # raffle_title is derived from item.name (BHRaffle has no title col)
        assert "og_title=f\"{raffle_title} - La Piazza Raffle\"" in COMMUNITY_PY, (
            "Raffle detail route must pass og_title built from raffle_title "
            "(which the route derives from item.name, since BHRaffle has no "
            "title field of its own)"
        )

    def test_raffle_route_passes_og_description(self):
        assert "og_description=" in COMMUNITY_PY[COMMUNITY_PY.find("raffle_detail_page"):], (
            "Raffle detail route must pass og_description so the share "
            "preview shows ticket price + organizer + prize description"
        )

    def test_raffle_route_passes_og_image(self):
        assert "og_image=raffle_image" in COMMUNITY_PY, (
            "Raffle detail route must pass og_image (from the raffle's "
            "item media if available, otherwise None to fall back to "
            "og-default.png)"
        )

    def test_raffle_og_description_includes_price(self):
        # The description-builder must mention ticket price when > 0
        block_start = COMMUNITY_PY.find("# BL-165")
        block = COMMUNITY_PY[block_start:block_start + 800]
        assert "ticket_price" in block and "EUR" in block, (
            "Raffle og_description must include the ticket price -- that's "
            "the conversion hook for the share preview"
        )


# ---- BL-168: OG image fallback must be a 1200x630 PNG, not a 192x192 icon ----

class TestOgDefaultImageFallback:
    """When a page doesn't pass og_image (or the source item has no media),
    the fallback must be a real 1200x630 share card -- platforms reject
    or hide images smaller than ~600x300."""

    def test_base_html_og_image_falls_back_to_og_default_png(self):
        assert "/static/images/og-default.png" in BASE_HTML, (
            "base.html must reference /static/images/og-default.png as the "
            "OG image fallback (was icon-192.png which is too small for "
            "platform previews)"
        )
        assert "icon-192.png" not in BASE_HTML.split("<meta")[1].split("</head>")[0], (
            "OG image fallback must NOT use icon-192.png anymore -- 192x192 "
            "is too small for Facebook/LinkedIn/Twitter preview cards"
        )

    def test_og_image_dimensions_declared(self):
        assert 'property="og:image:width"' in BASE_HTML
        assert 'property="og:image:height"' in BASE_HTML, (
            "OG image must declare width + height so platforms cache and "
            "render the preview without a fetch round-trip"
        )

    def test_og_default_png_exists_at_expected_path(self):
        png_path = REPO_ROOT / "src" / "static" / "images" / "og-default.png"
        assert png_path.exists(), (
            f"og-default.png must exist at {png_path} -- it's the OG fallback "
            "for every page that doesn't provide its own image"
        )
        # Sanity: must be at least 50KB (so it's a real image, not a
        # transparent stub)
        assert png_path.stat().st_size > 50_000, (
            "og-default.png must be substantial (> 50KB) -- a tiny file "
            "suggests the SVG conversion didn't render properly"
        )


# ---- bhShare must accept and forward an optional text payload ----

class TestBhShareCarriesDescriptionText:
    """bhShare(title, url, text) -- the third arg becomes the body of
    the share message so users see price + 1-line description even if
    the receiving platform doesn't fetch our OG card."""

    def test_bhShare_accepts_three_args(self):
        assert "async function bhShare(title, url, text)" in BASE_HTML, (
            "bhShare must accept title + url + text (text is the share "
            "message body, distinct from the URL preview card)"
        )

    def test_bhShare_passes_text_to_navigator_share(self):
        # navigator.share's payload must include text when provided
        idx = BASE_HTML.find("async function bhShare(")
        block = BASE_HTML[idx:idx + 800]
        assert "if (text) payload.text = text" in block, (
            "bhShare must add `text` to the navigator.share payload when "
            "the caller passes one"
        )

    def test_item_detail_share_passes_og_description(self):
        # item_detail.html must wire the share button to pass the rich text
        assert "data-text=\"{{ og_description" in ITEM_HTML, (
            "item_detail.html share button must include og_description as "
            "the share text payload (otherwise LinkedIn/WhatsApp recipients "
            "see only title + URL with no price)"
        )

    def test_raffle_detail_share_passes_og_description(self):
        assert "bhShare(document.title, window.location.href, this.dataset.text)" in RAFFLE_HTML, (
            "raffle_detail.html share buttons must use bhShare with the "
            "dataset.text payload (was using a bare navigator.share that "
            "stripped the description)"
        )

    def test_item_route_hides_draft_from_non_owners(self):
        """BL-170: Giulia saved a listing as draft; the public /items/{slug}
        URL was still accessible and rendered with no price block, looking
        broken. Owners must still see + edit their drafts (with a banner);
        everyone else must get 404."""
        item_py = (REPO_ROOT / "src" / "routers" / "pages" / "item.py").read_text()
        # The route must check has_active_listing AND not is_owner before 404
        assert "has_active_listing" in item_py and "not is_owner" in item_py, (
            "item_detail route must 404 when no active listing AND viewer is "
            "not the owner -- otherwise DRAFT items leak to the public with "
            "a broken-looking page"
        )

    def test_item_detail_shows_draft_banner_for_owner(self):
        item_html = (REPO_ROOT / "src" / "templates" / "pages" / "item_detail.html").read_text()
        assert "BL-170" in item_html and "is_owner and not active_listing" in item_html, (
            "item_detail must show a 'Draft -- not yet published' banner for "
            "owners viewing their own non-published items"
        )

    def test_first_photo_url_skips_videos(self):
        """BL-168 lesson: Giulia's counselling listing's first media was an
        mp4. The OG image was a video URL, which platforms can't preview.
        _first_photo_url must skip videos and return the first photo (or
        None to fall back to og-default.png in the template)."""
        from src.routers.pages._helpers import _first_photo_url

        class _FakeMedia:
            def __init__(self, url, mt):
                self.url = url
                self.media_type = mt
        class _MT:
            def __init__(self, v): self.value = v
        # Video first, photo second -> must return the photo
        media = [
            _FakeMedia("/uploads/clip.mp4", _MT("video")),
            _FakeMedia("/uploads/photo.jpg", _MT("photo")),
        ]
        assert _first_photo_url(media) == "/uploads/photo.jpg"
        # Only video -> None (template falls back to og-default.png)
        assert _first_photo_url([_FakeMedia("/x.mp4", _MT("video"))]) is None
        # Empty / None
        assert _first_photo_url([]) is None
        assert _first_photo_url(None) is None
        # Plain string media_type also accepted (defensive)
        media2 = [_FakeMedia("/u/p.jpg", "photo")]
        assert _first_photo_url(media2) == "/u/p.jpg"

    def test_item_route_uses_first_photo_url(self):
        item_py = (REPO_ROOT / "src" / "routers" / "pages" / "item.py").read_text()
        assert "_first_photo_url(item.media)" in item_py, (
            "item route must use _first_photo_url helper for og_image so "
            "items whose first media is a video still get a photo OG"
        )

    def test_raffle_route_uses_first_photo_url(self):
        assert "_first_photo_url(item.media)" in COMMUNITY_PY, (
            "raffle route must use _first_photo_url helper for og_image"
        )

    def test_no_inline_navigator_share_in_user_facing_pages(self):
        """Every share call goes through bhShare so the description text
        and clipboard fallback stay consistent. Inline navigator.share
        bypasses both. Also caught a missed straggler in raffles list +
        a 2nd share button on item_detail and raffle_detail."""
        import re
        pages_dir = REPO_ROOT / "src" / "templates" / "pages"
        offenders = []
        # bhShare itself naturally calls navigator.share -- exempt base.html
        for path in pages_dir.glob("*.html"):
            text = path.read_text()
            # Match inline button onclicks/atclicks that call navigator.share directly
            for m in re.finditer(r"(?:onclick|@click)\s*=\s*\"[^\"]*navigator\.share", text):
                offenders.append(f"{path.name}: {m.group(0)[:120]}")
        assert not offenders, (
            "Found inline navigator.share calls in user-facing pages. "
            "Use bhShare(title, url, text) instead so all shares carry "
            "the description payload and use the same clipboard fallback. "
            "Offenders:\n" + "\n".join(offenders)
        )


# ---- April 27 incident lesson: /api/v1/* must always return JSON on 500 ----

class TestApiJsonErrorHandler:
    """When an unhandled exception escapes an API route, the response MUST
    be JSON -- not an HTML error page. Otherwise the frontend's
    `await r.json()` chokes with 'Unexpected token <' and users see a
    cryptic toast instead of a friendly 'try again' message.

    Triggered April 27 when Postgres went into recovery mode mid-request
    and the AI endpoint returned an HTML 500.
    """

    def test_handler_registered(self):
        # Implemented as a BaseHTTPMiddleware (not @app.exception_handler) --
        # the latter doesn't catch exceptions that escape downstream
        # BaseHTTPMiddleware in starlette's task group.
        from src.main import app as _app
        middleware_names = [m.cls.__name__ for m in _app.user_middleware if hasattr(m, "cls")]
        assert "JsonErrorMiddleware" in middleware_names, (
            "JsonErrorMiddleware must be registered on the app so /api/v1/* "
            "unhandled errors return JSON instead of HTML"
        )

    @pytest.mark.asyncio
    async def test_handler_returns_json_for_api_paths(self, client):
        # Reach into the global app and mount a test route that always raises.
        # We can leave it mounted for the rest of the session -- it's namespaced.
        from src.main import app as _app
        if not any(getattr(r, "path", None) == "/api/v1/_test_boom" for r in _app.routes):
            @_app.get("/api/v1/_test_boom")
            async def _b():
                raise RuntimeError("kaboom")
        r = await client.get("/api/v1/_test_boom")
        assert r.status_code == 500
        assert r.headers.get("content-type", "").startswith("application/json"), (
            f"Expected JSON 500 for /api/v1/* unhandled errors, got "
            f"content-type: {r.headers.get('content-type')}"
        )
        body = r.json()
        assert "detail" in body, "JSON 500 response must have a 'detail' field"
        assert isinstance(body["detail"], str) and body["detail"].strip(), (
            "detail must be a human-readable string the frontend can show in a toast"
        )

    @pytest.mark.asyncio
    async def test_handler_does_not_leak_stack_trace_in_response(self, client):
        """Stack traces must stay in the server log, never in the response body."""
        from src.main import app as _app
        if not any(getattr(r, "path", None) == "/api/v1/_test_secret_boom" for r in _app.routes):
            @_app.get("/api/v1/_test_secret_boom")
            async def _bs():
                raise RuntimeError("SECRET_INTERNAL_DETAIL_dont_leak_me")
        r = await client.get("/api/v1/_test_secret_boom")
        assert "SECRET_INTERNAL_DETAIL" not in r.text, (
            "Exception message must not be echoed back to the client -- "
            "could leak DB connection strings, query SQL, etc."
        )

    @pytest.mark.asyncio
    async def test_http_exceptions_still_pass_through_unchanged(self, client):
        """The Exception handler must NOT shadow HTTPException -- 404, 422,
        401, 403 etc. should still get their normal handling."""
        # /api/v1/items/<bad-uuid> typically returns 422 (pydantic) or 404 --
        # assert we don't accidentally convert those to a generic 500
        r = await client.get("/api/v1/items/not-a-uuid")
        assert r.status_code != 500, (
            f"HTTPException/422-based responses must not be converted to "
            f"generic 500 by the new Exception handler. Got: {r.status_code} {r.text[:200]}"
        )
