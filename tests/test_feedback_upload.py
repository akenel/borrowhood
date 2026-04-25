"""Feedback widget photo-upload regression guards (BL-148, April 25, 2026).

Sylvie's BL-148 incident: tried to attach a photo of Simon to her feedback,
file rejected silently. Three layered bugs, all fixed:

1. Server error message LIED -- said "max 10 MB" while the actual constant
   is 25 MB. Sylvie reasonably concluded 10 MB was the limit.

2. Client `uploadOne` returned just a boolean -- on failure, the queued
   photo silently disappeared. User saw 'feedback submitted' toast and
   no clue their attachment vanished.

3. iPhone HEIC photos fail canvas decode -> shrinkImage threw -> caught
   silently -> file goes through at original size -> server might reject
   with "Unsupported type: image/heic" (also silently dropped on client).

These tests guard each layer.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_HTML = (REPO_ROOT / "src" / "templates" / "base.html").read_text()
BACKLOG_PY = (REPO_ROOT / "src" / "routers" / "backlog.py").read_text()


class TestServerSizeErrorIsTruthful:
    """The error message must report the ACTUAL constant value, not a
    stale hardcoded number."""

    def test_no_hardcoded_10_mb_message(self):
        assert 'detail="File too large (max 10 MB)"' not in BACKLOG_PY, (
            "Old hardcoded 'max 10 MB' message detected -- it lies because "
            "the actual constant is 25 MB. Use the constant in the message."
        )

    def test_uses_constant_for_max_mb(self):
        assert "max_mb = MAX_FEEDBACK_FILE_SIZE //" in BACKLOG_PY, (
            "Error message must derive max_mb from MAX_FEEDBACK_FILE_SIZE "
            "constant so message stays in sync if limit changes"
        )

    def test_message_includes_actual_size(self):
        # The error should tell the user how big their file actually was
        # so they know how much to compress.
        assert "actual_mb = len(contents)" in BACKLOG_PY


class TestHeicDetection:
    """iPhone HEIC photos must be detected and surfaced clearly, both
    client-side (skip queue) and server-side (helpful error)."""

    def test_server_returns_helpful_heic_error(self):
        # When somehow a HEIC reaches the server, the error must guide
        # the user, not just say "Unsupported type: image/heic".
        assert 'image/heic' in BACKLOG_PY and 'image/heif' in BACKLOG_PY, (
            "Server must explicitly recognise HEIC/HEIF and return a "
            "helpful error (how to convert), not the generic mime error"
        )
        assert "Most Compatible" in BACKLOG_PY, (
            "Server HEIC error must mention 'Most Compatible' (the iPhone "
            "Camera setting that switches to JPEG)"
        )

    def test_client_rejects_heic_before_compression(self):
        # Catch HEIC client-side before shrinkImage chokes on it
        assert "image/heic" in BASE_HTML and "image/heif" in BASE_HTML, (
            "Client must check for HEIC/HEIF mime types in pickFiles "
            "before attempting canvas compression"
        )
        assert "/\\.(heic|heif)$/i.test" in BASE_HTML, (
            "Client must also check filename extension (Android camera "
            "uploads sometimes have empty mime type)"
        )


class TestIterativeCompression:
    """First-pass compression at 1920px @ 0.85 may still leave files over
    the server limit. Iterate down on size if needed."""

    def test_compression_passes_array_exists(self):
        # Three passes: aggressive enough to cover 30 MB phone photos
        assert "passes = [" in BASE_HTML
        assert "{ maxPx: 1920, quality: 0.85 }" in BASE_HTML
        assert "{ maxPx: 1600, quality: 0.78 }" in BASE_HTML
        assert "{ maxPx: 1280, quality: 0.70 }" in BASE_HTML, (
            "Compression must iterate through 3 size tiers; the smallest "
            "(1280px @ 0.70) reliably gets phone photos under 8 MB"
        )

    def test_target_threshold_is_8mb(self):
        # 8 MB target leaves headroom under 25 MB server limit
        assert "compressed.size <= 8 * 1024 * 1024" in BASE_HTML, (
            "Compression loop must target 8 MB (server limit 25 MB minus "
            "headroom for transfer overhead and base64 inflation)"
        )


class TestUploadErrorsSurfacedToUser:
    """Sylvie's silent-failure root cause: uploadOne returned bool only,
    losing the server's 'why it failed' message."""

    def test_uploadOne_returns_object_not_bool(self):
        # New contract: { ok: bool, error?: string }
        assert "return { ok: true }" in BASE_HTML
        assert "return { ok: false, error:" in BASE_HTML, (
            "uploadOne must return { ok, error } so failure reason can "
            "be surfaced to the user, not just a true/false"
        )

    def test_upload_loop_toasts_per_file_error(self):
        # The submit loop must show a toast for each failed file
        assert "if (res.ok)" in BASE_HTML
        assert "item.name + ': ' + res.error" in BASE_HTML, (
            "submitFeedback upload loop must toast item-name + error so "
            "user sees 'simon.jpg: HEIC not supported' instead of silence"
        )

    def test_old_silent_failure_pattern_removed(self):
        # The old `if (ok) this.uploadedCount += 1;` pattern dropped errors
        assert "var ok = await this.uploadOne(" not in BASE_HTML, (
            "Old silent-failure pattern detected -- replaced with the "
            "{ok, error} object that toasts on failure"
        )
