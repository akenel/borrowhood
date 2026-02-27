"""Workshop team membership.

Teams allow multiple people to manage a workshop:
grandmother owns the recipes, grandson manages the tech.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class TeamRole(str, enum.Enum):
    OWNER = "owner"             # Full control, can delete workshop
    MANAGER = "manager"         # Edit items, manage listings, handle rentals
    HELPER = "helper"           # Assist with pickups/returns, limited editing
    CONTRIBUTOR = "contributor"  # Can suggest items, no editing rights


class BHWorkshopMember(BHBase, Base):
    """A team member of a workshop."""

    __tablename__ = "bh_workshop_member"

    workshop_owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), nullable=False)
    invite_message: Mapped[Optional[str]] = mapped_column(String(500))
    accepted: Mapped[bool] = mapped_column(default=False)

    workshop_owner: Mapped["BHUser"] = relationship(foreign_keys=[workshop_owner_id])
    member: Mapped["BHUser"] = relationship(foreign_keys=[member_id])
