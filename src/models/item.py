"""Item and ItemMedia models.

Items are the things people list: tools, kitchen gear, equipment,
digital goods, services, spaces, and made-to-order products.
"""

import enum
import uuid
from typing import List, Optional

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class ItemType(str, enum.Enum):
    PHYSICAL = "physical"           # Tools, equipment, kitchen gear
    DIGITAL = "digital"             # PDFs, templates, recipes
    SERVICE = "service"             # "I'll deliver it", "I'll teach you"
    SPACE = "space"                 # Workshop, kitchen, garage rental
    MADE_TO_ORDER = "made_to_order" # Custom items (Sally's cookies)


class ItemCondition(str, enum.Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    WORN = "worn"


class ItemCategory(str, enum.Enum):
    """Fixed set of item categories for the marketplace."""
    # Tools & Workshop
    POWER_TOOLS = "power_tools"
    HAND_TOOLS = "hand_tools"
    AUTOMOTIVE = "automotive"
    WELDING = "welding"
    WOODWORKING = "woodworking"
    THREE_D_PRINTING = "3d_printing"
    # Home & Living
    KITCHEN = "kitchen"
    CLEANING = "cleaning"
    GARDEN = "garden"
    FURNITURE = "furniture"
    HOME_IMPROVEMENT = "home_improvement"
    # Sports & Outdoors
    SPORTS = "sports"
    CAMPING = "camping"
    WATER_SPORTS = "water_sports"
    CYCLING = "cycling"
    # Creative
    ART = "art"
    MUSIC = "music"
    PHOTOGRAPHY = "photography"
    SEWING = "sewing"
    # Tech
    ELECTRONICS = "electronics"
    COMPUTERS = "computers"
    DRONES = "drones"
    # Spaces & Transport
    SPACES = "spaces"
    VEHICLES = "vehicles"
    # Services
    REPAIRS = "repairs"
    TRAINING_SERVICE = "training_service"
    CUSTOM_ORDERS = "custom_orders"
    # Other
    OTHER = "other"
    # Wave 2 legend categories
    CRAFTS = "crafts"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    FOOD = "food"
    OUTDOOR = "outdoor"
    SCIENCE = "science"
    TOOLS = "tools"


CATEGORY_GROUPS = {
    "tools_workshop": ["power_tools", "hand_tools", "automotive", "welding", "woodworking", "3d_printing"],
    "home_living": ["kitchen", "cleaning", "garden", "furniture", "home_improvement"],
    "sports_outdoors": ["sports", "camping", "water_sports", "cycling"],
    "creative": ["art", "music", "photography", "sewing"],
    "tech": ["electronics", "computers", "drones"],
    "spaces_transport": ["spaces", "vehicles"],
    "services": ["repairs", "training_service", "custom_orders", "education"],
    "science_engineering": ["science", "engineering"],
    "other": ["other", "crafts", "food", "outdoor", "tools"],
}


class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO_EMBED = "video_embed"     # YouTube URL
    DIGITAL_DOWNLOAD = "digital_download"


class BHItem(BHBase, Base):
    """An item that can be listed for rent, sale, or service."""

    __tablename__ = "bh_item"

    # Owner
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Identity
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    content_language: Mapped[str] = mapped_column(String(5), default="en")  # Language of the description

    # Classification
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "tools", "kitchen", "garden"
    subcategory: Mapped[Optional[str]] = mapped_column(String(50))

    # Physical item attributes
    condition: Mapped[Optional[ItemCondition]] = mapped_column(Enum(ItemCondition))
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))

    # Location (inherits from owner if not set)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    altitude: Mapped[Optional[float]] = mapped_column(Float, default=None)  # meters ASL

    # Community (multi-community federation)
    community_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_community.id"), nullable=True, index=True
    )

    # Story -- the human narrative behind this item
    story: Mapped[Optional[str]] = mapped_column(Text)  # "My father's drill from 1978..."

    # Tags for search and discovery
    tags: Mapped[Optional[str]] = mapped_column(Text)  # Comma-separated: "wool, felt, handmade, Swiss"

    # Safety & age
    age_restricted: Mapped[bool] = mapped_column(default=False)  # 18+ only (power tools, vehicles)
    safety_notes: Mapped[Optional[str]] = mapped_column(Text)  # Custom safety instructions from seller

    # Relationships & compatibility
    needs_equipment: Mapped[Optional[str]] = mapped_column(Text)  # "Requires safety goggles, hearing protection"
    compatible_with: Mapped[Optional[str]] = mapped_column(Text)  # "Works with Bosch 18V batteries"

    # Relationships
    owner: Mapped["BHUser"] = relationship(back_populates="items")
    media: Mapped[List["BHItemMedia"]] = relationship(back_populates="item", cascade="all, delete-orphan")
    listings: Mapped[List["BHListing"]] = relationship(back_populates="item")


class BHItemMedia(BHBase, Base):
    """Photos, video embeds, and digital downloads for items."""

    __tablename__ = "bh_item_media"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_item.id"), nullable=False, index=True
    )
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    alt_text: Mapped[str] = mapped_column(String(200), nullable=False)  # Required -- accessibility rule
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    item: Mapped["BHItem"] = relationship(back_populates="media")


class BHItemFavorite(BHBase, Base):
    """User-to-item favorites (wishlist / bookmarks)."""

    __tablename__ = "bh_item_favorite"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_item_favorite"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_item.id"), nullable=False, index=True
    )

    user: Mapped["BHUser"] = relationship()
    item: Mapped["BHItem"] = relationship()
