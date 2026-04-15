"""Tests for the video URL → embed URL parser."""

from src.services.video_embed import parse_video_url, is_supported_video_url


# ── YouTube ────────────────────────────────────────────────────────────

def test_youtube_watch_url():
    embed, p = parse_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert embed == "https://www.youtube.com/embed/dQw4w9WgXcQ"
    assert p == "youtube"


def test_youtube_short_url():
    embed, p = parse_video_url("https://youtu.be/dQw4w9WgXcQ")
    assert embed == "https://www.youtube.com/embed/dQw4w9WgXcQ"
    assert p == "youtube"


def test_youtube_shorts():
    embed, p = parse_video_url("https://www.youtube.com/shorts/abc123DEF45")
    assert embed == "https://www.youtube.com/embed/abc123DEF45"
    assert p == "youtube"


def test_youtube_embed_already():
    embed, p = parse_video_url("https://www.youtube.com/embed/dQw4w9WgXcQ")
    assert embed == "https://www.youtube.com/embed/dQw4w9WgXcQ"


def test_youtube_with_extra_params():
    embed, p = parse_video_url("https://youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=RDx")
    assert embed == "https://www.youtube.com/embed/dQw4w9WgXcQ"


# ── Vimeo ──────────────────────────────────────────────────────────────

def test_vimeo_standard():
    embed, p = parse_video_url("https://vimeo.com/123456789")
    assert embed == "https://player.vimeo.com/video/123456789"
    assert p == "vimeo"


# ── TikTok ─────────────────────────────────────────────────────────────

def test_tiktok_video():
    embed, p = parse_video_url("https://www.tiktok.com/@leonardo/video/7123456789012345678")
    assert embed == "https://www.tiktok.com/embed/v2/7123456789012345678"
    assert p == "tiktok"


# ── Rejection cases ────────────────────────────────────────────────────

def test_rejects_random_domain():
    embed, p = parse_video_url("https://evil.example.com/steal.html")
    assert embed is None and p is None


def test_rejects_empty():
    assert parse_video_url(None) == (None, None)
    assert parse_video_url("") == (None, None)
    assert parse_video_url("   ") == (None, None)


def test_rejects_javascript_scheme():
    embed, p = parse_video_url("javascript:alert('xss')")
    assert embed is None and p is None


def test_rejects_youtube_without_video_id():
    embed, p = parse_video_url("https://www.youtube.com/")
    assert embed is None


def test_is_supported_helper():
    assert is_supported_video_url("https://youtu.be/dQw4w9WgXcQ") is True
    assert is_supported_video_url("https://evil.example.com/x") is False
    assert is_supported_video_url(None) is False
