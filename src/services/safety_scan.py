"""Listing content safety scan -- catch off-platform FUNNELS and scam phrasing before a listing
reaches neighbours. Content heuristics only; it reads the listing text, never the user. Returns a
list of human-readable flags ([] = clean). Never raises -- a guard that breaks create is worse
than no guard, so callers wrap it and creation always proceeds.
"""
import re

# Off-platform chat/funnel destinations (the classic "leave the platform" scam vector).
_LINKS = re.compile(
    r"(t\.me/|telegram\.me/|telegram\.dog/|wa\.me/|chat\.whatsapp\.com/|"
    r"discord\.(?:gg|com)/|signal\.(?:me|group)/|m\.me/|join\.skype\.com/)",
    re.I,
)
# Funnel phrasing -- "come talk to me somewhere I control".
_PHRASES = [
    r"join\s+(here|us|first|my|the)\s+(telegram|whatsapp|group|channel|chat)",
    r"join\s+here\s+first",
    r"(dm|pm|message|contact|text|write|reach)\s+me\s+(on|at|off|directly|first|via)",
    r"contact\s+(me\s+)?off[\s-]?platform",
    r"add\s+me\s+on\s+(telegram|whatsapp|signal|discord)",
    r"(telegram|whatsapp)\s*[:@]",
    r"@[A-Za-z0-9_]{4,}\s*(>>>|>>|→|first|join)",
]
_PHRASE_RE = [re.compile(p, re.I) for p in _PHRASES]


def scan_listing(name: str = "", description: str = "", story: str = "") -> list[str]:
    """Return human-readable safety flags for a listing's text. [] means clean."""
    try:
        text = " ".join([name or "", description or "", story or ""])
        flags: list[str] = []
        links = sorted({m.group(0).rstrip("/").lower() for m in _LINKS.finditer(text)})
        if links:
            flags.append("off-platform funnel link(s): " + ", ".join(links)[:180])
        for rx in _PHRASE_RE:
            if rx.search(text):
                flags.append("funnel phrasing detected (e.g. 'join my telegram / dm me off-platform')")
                break
        return flags
    except Exception:  # noqa: BLE001 -- a scan must never break listing creation
        return []
