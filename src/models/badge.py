"""Badge model: achievement badges awarded for milestones.

Badges are permanent, non-revocable achievements that build reputation.
"""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BadgeCode(str, enum.Enum):
    """Achievement badge codes. Each user can earn each badge once."""
    FIRST_LISTING = "first_listing"           # Listed your first item
    FIRST_RENTAL = "first_rental"             # Completed your first rental
    FIRST_REVIEW = "first_review"             # Left your first review
    FIVE_STAR = "five_star"                   # Received a 5-star review
    SUPER_LENDER = "super_lender"             # 10+ items listed
    TRUSTED_RENTER = "trusted_renter"         # 5+ rentals completed
    COMMUNITY_VOICE = "community_voice"       # 10+ reviews given
    MULTILINGUAL = "multilingual"             # Speaks 3+ languages
    SKILL_MASTER = "skill_master"             # 5+ verified skills
    AUCTION_WINNER = "auction_winner"         # Won an auction
    EARLY_ADOPTER = "early_adopter"           # Joined during beta
    PERFECT_RECORD = "perfect_record"         # 10+ rentals, all 5-star
    NEIGHBORHOOD_HERO = "neighborhood_hero"   # 50+ transactions
    WORKSHOP_PRO = "workshop_pro"             # Complete profile + banner + bio
    GENEROUS_NEIGHBOR = "generous_neighbor"   # Gave away 3+ items


# Badge metadata (display info)
BADGE_INFO = {
    BadgeCode.FIRST_LISTING: {
        "name": "First Listing",
        "description": "Listed your first item on BorrowHood",
        "icon": "package",
        "color": "emerald",
    },
    BadgeCode.FIRST_RENTAL: {
        "name": "First Rental",
        "description": "Completed your first rental transaction",
        "icon": "handshake",
        "color": "blue",
    },
    BadgeCode.FIRST_REVIEW: {
        "name": "First Review",
        "description": "Left your first review for a neighbor",
        "icon": "star",
        "color": "amber",
    },
    BadgeCode.FIVE_STAR: {
        "name": "Five Star",
        "description": "Received a perfect 5-star review",
        "icon": "sparkles",
        "color": "yellow",
    },
    BadgeCode.SUPER_LENDER: {
        "name": "Super Lender",
        "description": "Listed 10 or more items for the community",
        "icon": "gift",
        "color": "purple",
    },
    BadgeCode.TRUSTED_RENTER: {
        "name": "Trusted Renter",
        "description": "Completed 5 or more rentals successfully",
        "icon": "shield-check",
        "color": "green",
    },
    BadgeCode.COMMUNITY_VOICE: {
        "name": "Community Voice",
        "description": "Left 10 or more reviews helping others decide",
        "icon": "megaphone",
        "color": "indigo",
    },
    BadgeCode.MULTILINGUAL: {
        "name": "Multilingual",
        "description": "Speaks 3 or more languages",
        "icon": "globe",
        "color": "cyan",
    },
    BadgeCode.SKILL_MASTER: {
        "name": "Skill Master",
        "description": "Has 5 or more verified skills",
        "icon": "wrench",
        "color": "orange",
    },
    BadgeCode.AUCTION_WINNER: {
        "name": "Auction Winner",
        "description": "Won an auction bid",
        "icon": "trophy",
        "color": "yellow",
    },
    BadgeCode.EARLY_ADOPTER: {
        "name": "Early Adopter",
        "description": "Joined BorrowHood during the beta period",
        "icon": "rocket",
        "color": "rose",
    },
    BadgeCode.PERFECT_RECORD: {
        "name": "Perfect Record",
        "description": "10+ rentals with all 5-star reviews",
        "icon": "crown",
        "color": "amber",
    },
    BadgeCode.NEIGHBORHOOD_HERO: {
        "name": "Neighborhood Hero",
        "description": "50+ transactions helping the community",
        "icon": "heart",
        "color": "red",
    },
    BadgeCode.WORKSHOP_PRO: {
        "name": "Workshop Pro",
        "description": "Complete workshop profile with bio and banner",
        "icon": "building-storefront",
        "color": "violet",
    },
    BadgeCode.GENEROUS_NEIGHBOR: {
        "name": "Generous Neighbor",
        "description": "Gave away 3 or more items to the community",
        "icon": "gift",
        "color": "rose",
    },
}


class BHBadge(BHBase, Base):
    """Earned badge instance. One per user per badge_code."""

    __tablename__ = "bh_badge"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    badge_code: Mapped[BadgeCode] = mapped_column(Enum(BadgeCode), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=True)

    user: Mapped["BHUser"] = relationship(backref="badges")
