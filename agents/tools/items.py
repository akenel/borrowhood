"""
BorrowHood Item & Listing tools for ADK agents.
"""

from .common import bh_get


# All 31 valid BorrowHood item categories
CATEGORIES = [
    "power_tools", "hand_tools", "automotive", "welding", "woodworking",
    "3d_printing", "kitchen", "cleaning", "garden", "furniture",
    "home_improvement", "sports", "camping", "water_sports", "cycling",
    "art", "music", "photography", "sewing", "electronics", "computers",
    "drones", "spaces", "vehicles", "repairs", "training_service",
    "custom_orders", "fashion", "books", "kids", "pets",
]

ITEM_TYPES = ["physical", "digital", "service", "space", "made_to_order"]

CONDITIONS = ["new", "like_new", "good", "fair", "worn"]

LISTING_TYPES = [
    {"type": "rent", "description": "Rent out an item for a daily/hourly fee with optional deposit"},
    {"type": "sell", "description": "Sell an item outright for a fixed price"},
    {"type": "auction", "description": "Auction an item with starting bid, reserve price, and countdown timer"},
    {"type": "giveaway", "description": "Give away an item for free to a neighbor"},
    {"type": "commission", "description": "Accept custom orders or made-to-order work"},
    {"type": "training", "description": "Offer training or lessons (per hour)"},
    {"type": "service", "description": "Offer a service like repairs, delivery, or consulting"},
]


def search_items(query: str, category: str = "", limit: int = 10) -> dict:
    """Search BorrowHood items by keyword and optional category.

    Args:
        query: Search text (matches item name and description).
        category: Optional category filter (e.g. 'power_tools', 'kitchen').
        limit: Maximum number of results (default 10).

    Returns:
        Dictionary with 'items' list containing name, description, category,
        condition, price info, and owner details for each match.
    """
    params = {"q": query, "limit": limit}
    if category:
        params["category"] = category
    data = bh_get("/api/v1/items", params=params)
    if "error" in data:
        return data

    # Simplify the response for the agent
    items = data if isinstance(data, list) else data.get("items", data.get("results", data.get("members", [])))
    results = []
    for item in items[:limit]:
        results.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "description": (item.get("description") or "")[:200],
            "category": item.get("category"),
            "subcategory": item.get("subcategory"),
            "condition": item.get("condition"),
            "item_type": item.get("item_type"),
            "brand": item.get("brand"),
            "owner_id": item.get("owner_id"),
            "needs_equipment": item.get("needs_equipment"),
            "compatible_with": item.get("compatible_with"),
        })
    return {"items": results, "total": len(results)}


def get_item_detail(item_id: str) -> dict:
    """Get full details for a specific item including listings and owner info.

    Args:
        item_id: The UUID of the item.

    Returns:
        Dictionary with complete item details, active listings with prices,
        and owner profile information.
    """
    return bh_get(f"/api/v1/items/{item_id}")


def get_item_listings(item_id: str) -> dict:
    """Get all active listings for a specific item.

    Args:
        item_id: The UUID of the item.

    Returns:
        Dictionary with 'listings' list containing type, price, and terms.
    """
    return bh_get("/api/v1/listings", params={"item_id": item_id, "status": "active"})


def get_categories() -> dict:
    """Return all valid BorrowHood item categories with their groups.

    Returns:
        Dictionary with 'categories' list and 'item_types' list.
    """
    return {
        "categories": CATEGORIES,
        "item_types": ITEM_TYPES,
        "conditions": CONDITIONS,
        "listing_types": LISTING_TYPES,
    }
