"""In-app notification model.

Every significant event creates a notification for the relevant user.
Notifications can also be forwarded to Telegram if the user has it enabled.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class NotificationType(str, enum.Enum):
    RENTAL_REQUEST = "rental_request"         # Someone wants to rent your item
    RENTAL_APPROVED = "rental_approved"       # Owner approved your request
    RENTAL_DECLINED = "rental_declined"       # Owner declined your request
    RENTAL_PICKED_UP = "rental_picked_up"     # Renter confirmed pickup
    RENTAL_RETURNED = "rental_returned"       # Item returned
    RENTAL_COMPLETED = "rental_completed"     # Transaction complete
    RENTAL_CANCELLED = "rental_cancelled"     # Rental cancelled
    REVIEW_RECEIVED = "review_received"       # Someone reviewed you
    DISPUTE_FILED = "dispute_filed"           # Dispute opened on your rental
    DISPUTE_RESPONDED = "dispute_responded"   # Other party responded to dispute
    DISPUTE_RESOLVED = "dispute_resolved"     # Dispute resolved
    DEPOSIT_FORFEITED = "deposit_forfeited"   # Your deposit was forfeited
    BID_PLACED = "bid_placed"                 # Someone bid on your auction
    BID_OUTBID = "bid_outbid"                 # You've been outbid
    AUCTION_WON = "auction_won"              # You won an auction
    AUCTION_ENDED = "auction_ended"           # Your auction ended
    LOCKBOX_CODES_READY = "lockbox_codes_ready"   # Pickup code is ready for renter
    LOCKBOX_PICKUP_CONFIRMED = "lockbox_pickup_confirmed"  # Renter confirmed pickup
    LOCKBOX_RETURN_CONFIRMED = "lockbox_return_confirmed"  # Return confirmed
    BADGE_EARNED = "badge_earned"               # You earned a badge
    MESSAGE_RECEIVED = "message_received"     # Someone sent you a message
    # Delivery tracking
    DELIVERY_PREPARING = "delivery_preparing"      # Owner is preparing your order
    DELIVERY_DISPATCHED = "delivery_dispatched"    # Your order is on its way
    DELIVERY_IN_TRANSIT = "delivery_in_transit"    # In transit to you
    DELIVERY_DELIVERED = "delivery_delivered"       # Delivered -- confirm receipt
    DELIVERY_READY_PICKUP = "delivery_ready_pickup" # Ready for pickup + location/code
    DELIVERY_CONFIRMED = "delivery_confirmed"      # Buyer confirmed receipt
    DELIVERY_FAILED = "delivery_failed"            # Delivery attempt failed
    DELIVERY_DAMAGED = "delivery_damaged"          # Buyer reports damage
    SAVED_SEARCH_MATCH = "SAVED_SEARCH_MATCH"   # A new listing matches your saved search
    SYSTEM = "system"                         # Platform announcement


class BHNotification(BHBase, Base):
    """A notification for a user."""

    __tablename__ = "bh_notification"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(String(500))  # URL to navigate to

    # Related entity (polymorphic reference)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))  # "rental", "review", "bid"
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # Status
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    telegram_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship
    user: Mapped["BHUser"] = relationship()
