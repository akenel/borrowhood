"""
BorrowHood User & Member tools for ADK agents.
"""

from .common import bh_get


def search_members(
    query: str = "",
    language: str = "",
    badge_tier: str = "",
    city: str = "",
    limit: int = 10,
) -> dict:
    """Search BorrowHood member directory with filters.

    Args:
        query: Search text (matches display name, workshop name, tagline).
        language: Filter by language code (e.g. 'it', 'en', 'de').
        badge_tier: Filter by minimum badge tier ('NEWCOMER', 'ACTIVE', 'TRUSTED', 'PILLAR', 'LEGEND').
        city: Filter by city name.
        limit: Maximum results (default 10).

    Returns:
        Dictionary with 'members' list containing profile info, languages,
        skills, and badge tier for each match.
    """
    params = {"limit": limit}
    if query:
        params["q"] = query
    if language:
        params["language"] = language
    if badge_tier:
        params["badge_tier"] = badge_tier
    if city:
        params["city"] = city

    data = bh_get("/api/v1/users", params=params)
    if "error" in data:
        return data

    members = data if isinstance(data, list) else data.get("items", data.get("members", data.get("results", [])))
    results = []
    for member in members[:limit]:
        langs = member.get("languages", [])
        lang_list = [
            f"{l.get('language_code', '?')} ({l.get('proficiency', '?')})"
            for l in langs
        ]
        results.append({
            "id": member.get("id"),
            "display_name": member.get("display_name"),
            "workshop_name": member.get("workshop_name"),
            "workshop_type": member.get("workshop_type"),
            "city": member.get("city"),
            "badge_tier": member.get("badge_tier"),
            "tagline": member.get("tagline", ""),
            "languages": lang_list,
        })
    return {"members": results, "total": len(results)}


def get_user_profile(user_id: str) -> dict:
    """Get full profile for a specific user including languages, skills, and badge info.

    Args:
        user_id: The UUID of the user.

    Returns:
        Dictionary with complete user profile including workshop details,
        language proficiencies (CEFR levels), skills, badge tier, and social links.
    """
    return bh_get(f"/api/v1/users/{user_id}")
