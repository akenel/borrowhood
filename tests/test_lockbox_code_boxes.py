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


class TestLockboxSubmitBulletproofing:
    """Submit() must not let users get stuck on 'Verifying...' forever.

    April 25 incident: server returned 200 OK + DB recorded the return at
    19:11:50, but the client never received the response (lost in flight
    behind 179 parallel requests). User sat staring at 'Verifying...' for
    52 seconds with no recovery path. The action had already succeeded but
    the UI lied.
    """

    def test_abort_controller_used_for_fetch_timeout(self):
        assert "AbortController" in ORDERS_HTML, (
            "submit() must use AbortController so a hung fetch can be "
            "aborted instead of leaving the spinner running forever"
        )
        assert "signal: ctrl.signal" in ORDERS_HTML, (
            "fetch() must pass the AbortController signal -- without it "
            "ctrl.abort() does nothing"
        )

    def test_fetch_timeout_is_15_seconds(self):
        # The fetch abort timer fires after 15s
        assert "ctrl.abort();" in ORDERS_HTML and "15000" in ORDERS_HTML, (
            "Fetch must abort after 15s so a hung response surfaces an "
            "actionable error instead of an infinite spinner"
        )

    def test_watchdog_resets_verifying_at_20s(self):
        # The watchdog timer ensures `verifying = false` even if every
        # other safety net fails. 20s is a soft outer bound.
        assert "self.verifying = false;" in ORDERS_HTML
        assert "20000" in ORDERS_HTML, (
            "20s watchdog must force verifying back to false so the user "
            "can retry or refresh -- last line of defense against stuck UI"
        )

    def test_success_reloads_immediately(self):
        # The old setTimeout(reload, 1500) was the failure mode -- if the
        # 1500ms timeout fired during a slow render, the reload could be
        # missed. Hard-reload immediately on success.
        assert "setTimeout(function() { location.reload(); }, 1500)" not in ORDERS_HTML, (
            "Old delayed-reload pattern detected -- success must reload "
            "immediately. The new page state IS the success confirmation."
        )

    def test_abort_error_message_tells_user_to_refresh(self):
        # AbortError should produce a message guiding the user to refresh
        # because the action MAY have succeeded server-side.
        assert "AbortError" in ORDERS_HTML
        assert "Refresh" in ORDERS_HTML or "refresh" in ORDERS_HTML, (
            "On AbortError / timeout, message must tell user to refresh "
            "(action may have succeeded server-side -- don't claim it failed)"
        )
