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
        assert "og_title=f\"{raffle.title} - La Piazza Raffle\"" in COMMUNITY_PY, (
            "Raffle detail route must pass og_title built from the raffle's "
            "own title (was inheriting the generic site title)"
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
