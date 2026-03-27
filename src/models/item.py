"""Item and ItemMedia models.

Items are the things people list: tools, kitchen gear, equipment,
digital goods, services, spaces, and made-to-order products.
"""

import enum
import uuid
from typing import List, Optional

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
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
    # Wave 2 extras (already in DB via seed)
    EXPERIENCES = "experiences"
    FASHION = "fashion"
    SERVICES = "services"
    TECHNOLOGY = "technology"
    TRAINING = "training"
    TRANSPORT = "transport"
    # Property & Rentals
    APARTMENT = "apartment"
    ROOM = "room"
    HOUSE = "house"
    VACATION_RENTAL = "vacation_rental"
    COMMERCIAL_SPACE = "commercial_space"
    LAND = "land"
    # Jobs & Gigs
    JOB_FULL_TIME = "job_full_time"
    JOB_PART_TIME = "job_part_time"
    JOB_CONTRACT = "job_contract"
    JOB_SEASONAL = "job_seasonal"
    JOB_FREELANCE = "job_freelance"
    JOB_INTERNSHIP = "job_internship"


CATEGORY_GROUPS = {
    "property": ["apartment", "room", "house", "vacation_rental", "commercial_space", "land"],
    "vehicles": ["vehicles", "automotive"],
    "jobs": ["job_full_time", "job_part_time", "job_contract", "job_seasonal", "job_freelance", "job_internship"],
    "community": ["skill_exchange", "neighborhood_help", "local_food", "rides"],
    "tools_workshop": ["power_tools", "hand_tools", "welding", "woodworking", "3d_printing", "tool_library"],
    "home_living": ["kitchen", "cleaning", "garden", "furniture", "home_improvement"],
    "sports_outdoors": ["sports", "camping", "water_sports", "cycling"],
    "creative": ["art", "music", "photography", "sewing"],
    "tech": ["electronics", "computers", "drones"],
    "spaces_transport": ["spaces", "transport"],
    "services": ["repairs", "training_service", "custom_orders", "education"],
    "other": ["other", "crafts", "food", "outdoor", "tools", "science", "engineering"],
}

# Attribute schemas per category group -- defines which fields are valid for each group
ATTRIBUTE_SCHEMAS = {
    "vehicles": {
        "year": {"type": "int", "label": "Year", "label_it": "Anno"},
        "mileage_km": {"type": "int", "label": "Mileage (km)", "label_it": "Chilometraggio (km)"},
        "fuel_type": {"type": "select", "label": "Fuel Type", "label_it": "Carburante",
                      "options": ["gasoline", "diesel", "electric", "hybrid", "lpg", "cng", "hydrogen"]},
        "transmission": {"type": "select", "label": "Transmission", "label_it": "Cambio",
                         "options": ["manual", "automatic"]},
        "engine_cc": {"type": "int", "label": "Engine (cc)", "label_it": "Cilindrata (cc)"},
        "power_kw": {"type": "int", "label": "Power (kW)", "label_it": "Potenza (kW)"},
        "body_type": {"type": "select", "label": "Body Type", "label_it": "Carrozzeria",
                      "options": ["sedan", "suv", "hatchback", "wagon", "coupe", "convertible", "van", "truck", "minivan", "motorcycle", "scooter", "camper"]},
        "doors": {"type": "int", "label": "Doors", "label_it": "Porte"},
        "seats": {"type": "int", "label": "Seats", "label_it": "Posti"},
        "color": {"type": "text", "label": "Color", "label_it": "Colore"},
        "euro_class": {"type": "select", "label": "Euro Class", "label_it": "Classe Euro",
                       "options": ["euro_1", "euro_2", "euro_3", "euro_4", "euro_5", "euro_6", "euro_6d"]},
        "plate_province": {"type": "text", "label": "Plate Province", "label_it": "Provincia Targa"},
        "owners_count": {"type": "int", "label": "Previous Owners", "label_it": "Proprietari Precedenti"},
        "accident_free": {"type": "bool", "label": "Accident Free", "label_it": "Senza Sinistri"},
        "mot_expiry": {"type": "text", "label": "MOT Expiry", "label_it": "Scadenza Revisione"},
    },
    "property": {
        "bedrooms": {"type": "int", "label": "Bedrooms", "label_it": "Locali"},
        "bathrooms": {"type": "int", "label": "Bathrooms", "label_it": "Bagni"},
        "floor_area_sqm": {"type": "int", "label": "Floor Area (m\u00b2)", "label_it": "Superficie (m\u00b2)"},
        "floor_number": {"type": "int", "label": "Floor", "label_it": "Piano"},
        "total_floors": {"type": "int", "label": "Total Floors", "label_it": "Piani Totali"},
        "elevator": {"type": "bool", "label": "Elevator", "label_it": "Ascensore"},
        "energy_class": {"type": "select", "label": "Energy Class", "label_it": "Classe Energetica",
                         "options": ["A4", "A3", "A2", "A1", "B", "C", "D", "E", "F", "G"]},
        "heating_type": {"type": "select", "label": "Heating", "label_it": "Riscaldamento",
                         "options": ["autonomous", "centralized", "floor", "heat_pump", "none"]},
        "furnished": {"type": "select", "label": "Furnished", "label_it": "Arredato",
                      "options": ["furnished", "partially", "unfurnished"]},
        "year_built": {"type": "int", "label": "Year Built", "label_it": "Anno Costruzione"},
        "parking": {"type": "bool", "label": "Parking / Garage", "label_it": "Parcheggio / Garage"},
        "balcony": {"type": "bool", "label": "Balcony / Terrace", "label_it": "Balcone / Terrazzo"},
        "garden": {"type": "bool", "label": "Garden", "label_it": "Giardino"},
        "air_conditioning": {"type": "bool", "label": "Air Conditioning", "label_it": "Aria Condizionata"},
        "monthly_expenses": {"type": "int", "label": "Monthly Expenses (\u20ac)", "label_it": "Spese Condominiali (\u20ac)"},
        "contract_type": {"type": "select", "label": "Contract Type", "label_it": "Tipo Contratto",
                          "options": ["4+4", "3+2", "transitorio", "cedolare_secca", "commercial", "seasonal"]},
    },
    "jobs": {
        "job_type": {"type": "select", "label": "Job Type", "label_it": "Tipo Lavoro",
                     "options": ["full_time", "part_time", "contract", "seasonal", "freelance", "internship"]},
        "salary_min": {"type": "int", "label": "Salary Min (\u20ac)", "label_it": "Stipendio Min (\u20ac)"},
        "salary_max": {"type": "int", "label": "Salary Max (\u20ac)", "label_it": "Stipendio Max (\u20ac)"},
        "salary_period": {"type": "select", "label": "Salary Period", "label_it": "Periodo Stipendio",
                          "options": ["hourly", "monthly", "yearly"]},
        "experience_level": {"type": "select", "label": "Experience", "label_it": "Esperienza",
                             "options": ["entry", "junior", "mid", "senior", "lead"]},
        "remote_option": {"type": "select", "label": "Remote", "label_it": "Remoto",
                          "options": ["on_site", "remote", "hybrid"]},
        "industry": {"type": "text", "label": "Industry", "label_it": "Settore"},
        "application_deadline": {"type": "text", "label": "Application Deadline", "label_it": "Scadenza Candidatura"},
    },
}


def get_attribute_schema(category: str) -> dict:
    """Return the attribute schema for a given category, or empty dict if none."""
    for group_name, cats in CATEGORY_GROUPS.items():
        if category in cats and group_name in ATTRIBUTE_SCHEMAS:
            return ATTRIBUTE_SCHEMAS[group_name]
    return {}


class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"                 # Uploaded video file (MP4, WebM)
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

    # Category-specific attributes (vehicle specs, property details, job fields)
    # Stored as JSONB -- schema defined in ATTRIBUTE_SCHEMAS per category group
    attributes: Mapped[Optional[dict]] = mapped_column(JSON, default=None)

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


class BHItemVote(BHBase, Base):
    """Upvote on an item. One per user per item. Toggle on/off."""

    __tablename__ = "bh_item_vote"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_item_vote"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_item.id"), nullable=False, index=True
    )
