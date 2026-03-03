"""
BorrowHood Review tools for ADK agents.
"""

from .common import bh_get


# Review weight multipliers by badge tier (from BorrowHood reputation system)
REVIEW_WEIGHTS = {
    "NEWCOMER": 1.0,
    "ACTIVE": 2.0,
    "TRUSTED": 5.0,
    "PILLAR": 8.0,
    "LEGEND": 10.0,
}


def get_user_reviews(user_id: str) -> dict:
    """Get all reviews written about a specific user.

    Args:
        user_id: The UUID of the user to get reviews for.

    Returns:
        Dictionary with 'reviews' list containing rating, title, body,
        skill_name, skill_rating, reviewer tier, and weight for each review.
    """
    data = bh_get("/api/v1/reviews", params={"reviewee_id": user_id})
    if "error" in data:
        return data

    reviews = data if isinstance(data, list) else data.get("reviews", data.get("items", data.get("results", [])))
    results = []
    for review in reviews:
        results.append({
            "rating": review.get("rating"),
            "title": review.get("title", ""),
            "body": review.get("body", ""),
            "skill_name": review.get("skill_name"),
            "skill_rating": review.get("skill_rating"),
            "reviewer_tier": review.get("reviewer_tier", "NEWCOMER"),
            "weight": review.get("weight", 1.0),
            "created_at": review.get("created_at", ""),
        })
    return {"reviews": results, "total": len(results), "weight_scale": REVIEW_WEIGHTS}


def get_review_summary(user_id: str) -> dict:
    """Get review summary statistics for a user.

    Args:
        user_id: The UUID of the user.

    Returns:
        Dictionary with review count, average rating, and weighted average.
    """
    return bh_get(f"/api/v1/reviews/summary/{user_id}")
