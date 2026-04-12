"""Team pricing calculator for service/training listings."""

from typing import Optional


def calculate_service_price(
    per_person_rate: Optional[float],
    participant_count: int,
    minimum_charge: Optional[float] = None,
    group_discount_pct: Optional[float] = None,
    max_participants: Optional[int] = None,
    base_price: Optional[float] = None,
) -> dict:
    """Calculate total price for a group booking.

    Returns dict with breakdown: base, discount, total, per_person_final.
    Raises ValueError if participant_count exceeds max_participants.
    """
    if max_participants and participant_count > max_participants:
        raise ValueError(f"Exceeds maximum of {max_participants} participants")
    if participant_count < 1:
        raise ValueError("At least 1 participant required")

    if per_person_rate and per_person_rate > 0:
        subtotal = per_person_rate * participant_count
    elif base_price and base_price > 0:
        subtotal = base_price
    else:
        return {"subtotal": 0, "discount": 0, "total": 0, "per_person": 0}

    discount = 0
    if participant_count >= 3 and group_discount_pct and group_discount_pct > 0:
        discount = subtotal * (group_discount_pct / 100)

    total = subtotal - discount
    if minimum_charge and minimum_charge > 0:
        total = max(total, minimum_charge)

    per_person = total / participant_count if participant_count > 0 else total

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "total": round(total, 2),
        "per_person": round(per_person, 2),
    }
