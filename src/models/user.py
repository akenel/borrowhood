"""User models: profile, languages, skills, points, social links.

Every user IS a workshop. Their profile is their storefront.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class WorkshopType(str, enum.Enum):
    KITCHEN = "kitchen"
    GARAGE = "garage"
    GARDEN = "garden"
    WORKSHOP = "workshop"
    STUDIO = "studio"
    OFFICE = "office"
    OTHER = "other"
    # Wave 2 legend workshop types
    ARENA = "arena"
    CAMP = "camp"
    DOCK = "dock"
    DOJO = "dojo"
    FORGE = "forge"
    FORTRESS = "fortress"
    LABORATORY = "laboratory"
    LODGE = "lodge"
    OBSERVATORY = "observatory"
    PALACE = "palace"
    PAVILION = "pavilion"
    STUDY = "study"


class AccountStatus(str, enum.Enum):
    REGISTERED = "registered"
    VERIFIED = "verified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    BANNED = "banned"


class CEFRLevel(str, enum.Enum):
    """Common European Framework of Reference for Languages."""
    A1 = "A1"  # Beginner
    A2 = "A2"  # Elementary
    B1 = "B1"  # Intermediate
    B2 = "B2"  # Upper Intermediate
    C1 = "C1"  # Advanced
    C2 = "C2"  # Proficient
    NATIVE = "native"


class BadgeTier(str, enum.Enum):
    NEWCOMER = "newcomer"      # 0-49 pts
    ACTIVE = "active"          # 50-199 pts
    TRUSTED = "trusted"        # 200-499 pts
    PILLAR = "pillar"          # 500-999 pts
    LEGEND = "legend"          # 1000+ pts


class BHUser(BHBase, Base):
    """Core user model. Every user is a workshop."""

    __tablename__ = "bh_user"

    # Identity (synced from Keycloak)
    keycloak_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)  # Keycloak preferred_username
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    mother_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    father_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Workshop profile
    workshop_name: Mapped[Optional[str]] = mapped_column(String(100))
    workshop_type: Mapped[Optional[WorkshopType]] = mapped_column(Enum(WorkshopType))
    tagline: Mapped[Optional[str]] = mapped_column(String(200))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(2000))
    banner_url: Mapped[Optional[str]] = mapped_column(String(500))
    # Featured video -- YouTube / Vimeo / TikTok URL, embedded on workshop page
    featured_video_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Contact
    telegram_username: Mapped[Optional[str]] = mapped_column(String(100))
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50))  # Numeric Telegram chat ID for Bot API
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(30))  # International format e.g. +39328123456

    # Location (fuzzy -- 3 decimal places max)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    altitude: Mapped[Optional[float]] = mapped_column(Float, default=None)  # meters ASL
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state_region: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    address_line: Mapped[Optional[str]] = mapped_column(String(300))  # private -- only shared in active orders
    country_code: Mapped[Optional[str]] = mapped_column(String(2))

    # Status
    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus), default=AccountStatus.REGISTERED, nullable=False
    )
    badge_tier: Mapped[BadgeTier] = mapped_column(
        Enum(BadgeTier), default=BadgeTier.NEWCOMER, nullable=False
    )

    # Composite trust score (0.0 to 1.0)
    trust_score: Mapped[Optional[float]] = mapped_column(Float, default=None)

    # Raffle vouching privilege — only admin-granted, NOT from badge tier
    can_vouch_raffles: Mapped[bool] = mapped_column(default=False)

    # Service declarations ("I offer...")
    offers_delivery: Mapped[bool] = mapped_column(default=False)
    offers_pickup: Mapped[bool] = mapped_column(default=False)
    offers_training: Mapped[bool] = mapped_column(default=False)
    offers_custom_orders: Mapped[bool] = mapped_column(default=False)
    offers_repair: Mapped[bool] = mapped_column(default=False)

    # Accepted payment methods (comma-separated: cash,satispay,iban,paypal,twint,revolut,card)
    accepted_payments: Mapped[Optional[str]] = mapped_column(Text, default="")

    # Seller type (BL-069: tax/VAT compliance)
    seller_type: Mapped[Optional[str]] = mapped_column(String(20), default="personal")  # personal | business | organization
    business_name: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    vat_number: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    organization_description: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # Stripe Connect (marketplace payouts)
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(200), default=None)

    # Multi-community federation
    default_community_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_community.id"), nullable=True
    )

    # Event reliability tracking
    no_show_count: Mapped[int] = mapped_column(Integer, default=0)

    # Activity tracking
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    # Terms of Service acceptance
    tos_accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    # Notification preferences
    notify_telegram: Mapped[bool] = mapped_column(default=True)
    notify_email: Mapped[bool] = mapped_column(default=True)

    # Referral tracking
    referred_by: Mapped[Optional[str]] = mapped_column(String(80))  # slug of the referrer

    # Relationships
    languages: Mapped[List["BHUserLanguage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    skills: Mapped[List["BHUserSkill"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    points: Mapped[Optional["BHUserPoints"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    social_links: Mapped[List["BHUserSocialLink"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    items: Mapped[List["BHItem"]] = relationship(back_populates="owner")
    favorites: Mapped[List["BHUserFavorite"]] = relationship(
        back_populates="user", foreign_keys="BHUserFavorite.user_id", cascade="all, delete-orphan"
    )


class BHUserLanguage(BHBase, Base):
    """CEFR language proficiency per user."""

    __tablename__ = "bh_user_language"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)  # "en", "it", "de", "fr"
    proficiency: Mapped[CEFRLevel] = mapped_column(Enum(CEFRLevel), nullable=False)

    user: Mapped["BHUser"] = relationship(back_populates="languages")


class BHUserSkill(BHBase, Base):
    """Self-declared skills with optional community verification."""

    __tablename__ = "bh_user_skill"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # "woodworking", "baking", "gardening"
    self_rating: Mapped[int] = mapped_column(Integer, default=3)  # 1-5
    verified_by_count: Mapped[int] = mapped_column(Integer, default=0)
    years_experience: Mapped[Optional[int]] = mapped_column(Integer)

    user: Mapped["BHUser"] = relationship(back_populates="skills")


class BHUserPoints(BHBase, Base):
    """Reputation points tracking."""

    __tablename__ = "bh_user_points"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), unique=True, nullable=False
    )
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rentals_completed: Mapped[int] = mapped_column(Integer, default=0)
    reviews_given: Mapped[int] = mapped_column(Integer, default=0)
    reviews_received: Mapped[int] = mapped_column(Integer, default=0)
    items_listed: Mapped[int] = mapped_column(Integer, default=0)
    helpful_flags: Mapped[int] = mapped_column(Integer, default=0)
    giveaways_completed: Mapped[int] = mapped_column(Integer, default=0)

    # Event gamification
    events_attended: Mapped[int] = mapped_column(Integer, default=0)
    events_hosted: Mapped[int] = mapped_column(Integer, default=0)
    event_streak: Mapped[int] = mapped_column(Integer, default=0)     # Current consecutive streak
    best_streak: Mapped[int] = mapped_column(Integer, default=0)      # All-time best streak
    challenges_completed: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["BHUser"] = relationship(back_populates="points")


class BHUserSocialLink(BHBase, Base):
    """Social media and external profile links."""

    __tablename__ = "bh_user_social_link"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(30), nullable=False)  # "youtube", "instagram", "linkedin"
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(100))  # "My Woodworking Channel"

    user: Mapped["BHUser"] = relationship(back_populates="social_links")


class BHUserFavorite(BHBase, Base):
    """User-to-user favorites (bookmarks)."""

    __tablename__ = "bh_user_favorite"
    __table_args__ = (
        UniqueConstraint("user_id", "favorite_user_id", name="uq_user_favorite"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    favorite_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    note: Mapped[Optional[str]] = mapped_column(String(200))

    user: Mapped["BHUser"] = relationship(back_populates="favorites", foreign_keys=[user_id])
    favorite_user: Mapped["BHUser"] = relationship(foreign_keys=[favorite_user_id])
