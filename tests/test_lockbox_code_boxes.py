"""Lockbox code segmented-input regression guards (BL-157, April 25, 2026).

Background: Leo logged in as renter, tried to confirm pickup with a single
text input. The visual presentation made it unclear how many characters were
needed, the input also let you submit at 4 chars (front-end), and the API
silently returned 'Invalid' if the count was wrong.

Fix: replaced the single text input with 8 OTP-style boxes (pickup + return
modals) backed by `lockboxCodeBoxes()` Alpine factory:
- Each box accepts exactly one alphanumeric character
- Auto-advances on input, backspaces to previous on empty
- Paste anywhere fills all 8 boxes at once
- Verify button disabled until all 8 chars entered (no more 4-char submits)
- Visual gap after position 4 for scannability
- Active boxes color-change to match modal accent (blue=pickup, green=return)

These tests assert the wiring stays intact -- easy to break in a refactor.
"""

from pathlib import Path


ORDERS_HTML = (
    Path(__file__).resolve().parent.parent
    / "src" / "templates" / "pages" / "orders.html"
).read_text()


class TestLockboxCodeBoxes:
    """8-box segmented input replaces the old single text input."""

    def test_factory_function_exists(self):
        assert "function lockboxCodeBoxes(" in ORDERS_HTML, (
            "lockboxCodeBoxes Alpine factory missing -- both pickup and "
            "return modals depend on it"
        )

    def test_pickup_modal_uses_factory(self):
        # The pickup modal x-data binding wires up the factory with blue color
        assert "lockboxCodeBoxes('{{ order.id }}', 'blue', 'Confirm Pickup'" in ORDERS_HTML, (
            "Confirm Pickup modal must use lockboxCodeBoxes('blue', ...) "
            "instead of the old single text input"
        )

    def test_return_modal_uses_factory(self):
        assert "lockboxCodeBoxes('{{ order.id }}', 'emerald', 'Confirm Return'" in ORDERS_HTML, (
            "Confirm Return modal must use lockboxCodeBoxes('emerald', ...) "
            "instead of the old single text input"
        )

    def test_chars_array_is_8_boxes(self):
        # The factory initializes chars as 8 empty strings -- this is the
        # core guarantee that the input is exactly 8 boxes.
        assert "chars: ['', '', '', '', '', '', '', '']" in ORDERS_HTML, (
            "lockboxCodeBoxes.chars must be an 8-element array (one per box)"
        )

    def test_filled_check_requires_all_8(self):
        # `filled` returns true only when every box has exactly one char
        assert "this.chars.every(function(c){ return c.length === 1; })" in ORDERS_HTML, (
            "filled getter must require ALL 8 boxes to have a character -- "
            "this is what disables the Verify button until full code entered"
        )

    def test_submit_button_gated_on_filled(self):
        # Both Verify Code buttons should be `:disabled="verifying || !filled"`
        assert ORDERS_HTML.count(':disabled="verifying || !filled"') >= 2, (
            "Both pickup and return Verify buttons must be disabled until "
            "all 8 boxes are filled (no more lenient 4-char submits)"
        )

    def test_paste_handler_wired(self):
        # @paste on the boxes container so users can paste the full code
        assert '@paste="handlePaste($event)"' in ORDERS_HTML
        assert "handlePaste(evt)" in ORDERS_HTML, (
            "handlePaste must exist on the factory so users can paste the "
            "full 8-char code instead of typing one box at a time"
        )

    def test_paste_sanitizes_to_8_uppercase_alphanumeric(self):
        # The paste handler should slice to 8 chars, uppercase, A-Z0-9 only
        assert ".toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8)" in ORDERS_HTML, (
            "Paste handler must sanitize input to 8 uppercase alphanumerics "
            "(prevents whitespace, lowercase, or punctuation from breaking match)"
        )

    def test_data_code_box_attribute_for_dom_lookup(self):
        # All 8 inputs use data-code-box so the handler can find siblings
        # via parentElement.querySelectorAll without using brittle x-refs
        assert "data-code-box" in ORDERS_HTML, (
            "Each box needs data-code-box attribute so handlers can find "
            "siblings for auto-advance / backspace navigation"
        )

    def test_old_single_input_pattern_removed(self):
        # The old `placeholder="Enter 8-digit code"` string should be gone
        # -- if it comes back, someone reverted the segmented design.
        assert 'placeholder="Enter 8-digit code"' not in ORDERS_HTML, (
            "Old single text input pattern detected -- segmented 8-box "
            "input was reverted? Restore the lockboxCodeBoxes factory"
        )

    def test_old_lenient_4char_check_removed(self):
        # The old front-end check `code.length < 4` was too lenient.
        # Should not exist anywhere now.
        assert "code.length < 4" not in ORDERS_HTML, (
            "Old `code.length < 4` lenient gate detected -- the segmented "
            "input enforces 8 chars via `filled`. Don't reintroduce."
        )
