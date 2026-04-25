"""Mobile overflow regression guards (BL-155 + BL-156, April 25, 2026).

These tests lock in CSS utility classes that defend against horizontal
overflow on narrow viewports. The classes themselves are tiny strings in
template files -- trivially removed by an unrelated refactor without any
runtime failure to warn anyone. These tests catch that.

Background: April 25 we hit two related bugs on Sylvie's Android:
  1. Q&A "Ask" button pushed off-screen because flex-row didn't wrap (BL-155)
  2. Bottom nav appeared shifted because some user-content element was
     wider than viewport, page got horizontal scroll, fixed nav rode along
     visually (BL-156)

Defenses we shipped:
  - html + body get `overflow-x-hidden` so nothing can ever push the page
    wider than viewport
  - Q&A / form-style input+button rows use `flex-col sm:flex-row` so the
    button drops below the input on mobile
  - Chat-style send rows (icon button) keep `flex` horizontal but add
    `min-w-0` to the input so it can shrink
  - User-content prose blocks get `break-words` so long URLs wrap inside
    their card instead of being clipped
"""

from pathlib import Path

import pytest


TEMPLATES = Path(__file__).resolve().parent.parent / "src" / "templates"


def _read(rel_path: str) -> str:
    return (TEMPLATES / rel_path).read_text()


# ── Body-level overflow clamp (BL-156) ──

class TestBodyOverflowClamp:
    """html + body must clamp horizontal overflow so fixed nav stays anchored."""

    def test_html_has_overflow_x_hidden(self):
        base = _read("base.html")
        assert "<html" in base
        # Find the html tag and confirm overflow-x-hidden is on it
        html_tag = base[base.find("<html"):base.find(">", base.find("<html")) + 1]
        assert "overflow-x-hidden" in html_tag, (
            "html element must have overflow-x-hidden so wide children "
            "cannot create page-level horizontal scroll (would shift fixed nav)"
        )

    def test_body_has_overflow_x_hidden(self):
        base = _read("base.html")
        body_open = base.find("<body")
        body_tag = base[body_open:base.find(">", body_open) + 1]
        assert "overflow-x-hidden" in body_tag, (
            "body element must have overflow-x-hidden as a second-layer "
            "defense against page-level horizontal scroll on mobile"
        )


# ── Form-style input + button rows wrap on mobile (BL-155) ──

class TestQAFormWraps:
    """Q&A 'Ask' form on item/event detail must stack vertically on mobile."""

    def test_ask_question_row_uses_flex_col(self):
        item = _read("pages/item_detail.html")
        # The form row containing the input and ASK button
        ask_block_start = item.find('@submit.prevent="askQuestion()"')
        assert ask_block_start > 0, "Q&A askQuestion form not found"
        # Look at the next ~200 chars for the wrapping div
        snippet = item[ask_block_start:ask_block_start + 600]
        assert "flex-col sm:flex-row" in snippet, (
            "Q&A 'Ask' input+button row must be flex-col on mobile so the "
            "ASK button drops below the input instead of off-screen"
        )

    def test_qa_owner_reply_row_uses_flex_col(self):
        item = _read("pages/item_detail.html")
        # The owner-reply inline row inside the Q&A list
        marker = 'x-model="qa._draft"'
        idx = item.find(marker)
        assert idx > 0, "Q&A owner reply input not found"
        # Walk back ~200 chars to find the wrapping div
        before = item[max(0, idx - 200):idx]
        assert "flex-col sm:flex-row" in before, (
            "Q&A owner reply row must wrap to column on mobile"
        )


class TestHelpboardAIDraftWraps:
    """Help Board AI draft input+button row must stack on mobile."""

    def test_ai_draft_row_uses_flex_col(self):
        hb = _read("pages/helpboard.html")
        marker = 'x-model="aiDraftInput"'
        idx = hb.find(marker)
        assert idx > 0, "AI draft input not found"
        before = hb[max(0, idx - 200):idx]
        assert "flex-col sm:flex-row" in before, (
            "Help Board AI draft input+button must wrap to column on mobile"
        )


class TestDashboardWhatsAppWraps:
    """Dashboard WhatsApp number setting input+button must stack on mobile."""

    def test_whatsapp_row_uses_flex_col(self):
        dash = _read("pages/dashboard.html")
        marker = 'x-model="waNumber"'
        idx = dash.find(marker)
        assert idx > 0, "WhatsApp number input not found"
        before = dash[max(0, idx - 200):idx]
        assert "flex-col sm:flex-row" in before, (
            "WhatsApp number input+Save button must wrap to column on mobile"
        )


# ── Chat-style send rows keep flex but with min-w-0 input ──

class TestChatStyleSendRows:
    """Messages + AI chat keep horizontal send (icon button) but input must
    have min-w-0 so flexbox can actually shrink it past intrinsic width."""

    def test_messages_compose_input_has_min_w_0(self):
        msg = _read("pages/messages.html")
        marker = 'x-model="newMessage"'
        idx = msg.find(marker)
        assert idx > 0
        # The input attribute block usually fits in the next 400 chars
        snippet = msg[idx:idx + 400]
        assert "min-w-0" in snippet, (
            "Messages compose input needs min-w-0 so flex can shrink it; "
            "without it the send icon gets pushed off-screen"
        )

    def test_ai_chat_input_has_min_w_0(self):
        chat = _read("pages/chat.html")
        marker = 'x-model="query"'
        idx = chat.find(marker)
        assert idx > 0
        snippet = chat[idx:idx + 400]
        assert "min-w-0" in snippet, (
            "AI chat input needs min-w-0 so flex can shrink it past "
            "its intrinsic min-width"
        )


# ── User-content prose blocks must break long words/URLs ──

class TestUserContentBreaksWords:
    """Markdown-rendered user content (bios, descriptions, posts, messages)
    must use break-words so a pasted long URL wraps inside its card instead
    of getting clipped at the right edge by the body overflow clamp."""

    @pytest.mark.parametrize("template,marker", [
        ("pages/workshop.html", 'id="workshop-bio"'),
        ("pages/profile.html", 'id="bio-text"'),
        ("pages/item_detail.html", 'id="desc-text"'),
        ("pages/messages.html", 'marked.parse(msg.body'),
        ("pages/helpboard.html", 'marked.parse(activePost.body'),
    ])
    def test_prose_block_has_break_words(self, template, marker):
        content = _read(template)
        idx = content.find(marker)
        assert idx > 0, f"marker {marker!r} not found in {template}"
        # The class attribute is usually within 300 chars of the marker
        # (could be before or after depending on tag structure)
        window = content[max(0, idx - 300):idx + 300]
        assert "break-words" in window, (
            f"{template}: user-content prose block near {marker!r} "
            f"must include break-words so long URLs wrap inside the card"
        )
