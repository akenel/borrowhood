"""Turn a user-pasted video URL into a safe embed URL.

Supports YouTube, Vimeo, TikTok. Returns (embed_url, provider) or
(None, None) if the URL isn't recognized. Never returns an arbitrary
domain -- this is the security boundary that prevents embedding
malicious iframes from random hosts.
"""
import re
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}
TIKTOK_HOSTS = {"tiktok.com", "www.tiktok.com", "m.tiktok.com"}

_TIKTOK_ID = re.compile(r"/video/(\d+)")
_VIMEO_ID = re.compile(r"/(\d+)")


def parse_video_url(url: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return (embed_url, provider) for supported providers, else (None, None)."""
    if not url or not isinstance(url, str):
        return None, None
    url = url.strip()
    if not url:
        return None, None

    try:
        parsed = urlparse(url if "://" in url else "https://" + url)
    except Exception:
        return None, None

    host = (parsed.hostname or "").lower()
    if not host:
        return None, None

    # YouTube
    if host in YOUTUBE_HOSTS:
        video_id = None
        if host == "youtu.be":
            video_id = parsed.path.strip("/").split("/")[0] or None
        elif parsed.path == "/watch":
            video_id = (parse_qs(parsed.query).get("v") or [None])[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/", 1)[1].split("/")[0] or None
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/", 1)[1].split("/")[0] or None
        if video_id and re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id):
            # Privacy-enhanced mode -- no tracking cookies, GDPR-friendlier
            return f"https://www.youtube-nocookie.com/embed/{video_id}", "youtube"

    # Vimeo
    if host in VIMEO_HOSTS:
        m = _VIMEO_ID.search(parsed.path)
        if m:
            return f"https://player.vimeo.com/video/{m.group(1)}", "vimeo"

    # TikTok
    if host in TIKTOK_HOSTS:
        m = _TIKTOK_ID.search(parsed.path)
        if m:
            return f"https://www.tiktok.com/embed/v2/{m.group(1)}", "tiktok"

    return None, None


def is_supported_video_url(url: Optional[str]) -> bool:
    """Quick check -- does this URL parse to a known provider?"""
    embed, _ = parse_video_url(url)
    return embed is not None
