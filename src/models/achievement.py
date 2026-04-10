"""Achievement model: unlockable milestones for event gamification.

Kids earn achievements by showing up, maintaining streaks, and being reliable.
Achievements are visible on profiles and the leaderboard.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class AchievementTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class BHAchievement(BHBase, Base):
    """A user's unlocked achievement."""

    __tablename__ = "bh_achievement"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    achievement_key: Mapped[str] = mapped_column(String(50), nullable=False)
    tier: Mapped[AchievementTier] = mapped_column(
        Enum(AchievementTier), default=AchievementTier.BRONZE, nullable=False
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["BHUser"] = relationship()


# Achievement definitions -- the rules of the game
# key: { name, name_it, description, description_it, icon, tiers }
ACHIEVEMENTS = {
    # -- Attendance milestones --
    "first_event": {
        "name": "First Step",
        "name_it": "Primo Passo",
        "desc": "Attended your first event",
        "desc_it": "Hai partecipato al tuo primo evento",
        "icon": "foot",
        "trigger": "events_attended",
        "threshold": 1,
        "tier": "bronze",
        "points": 5,
    },
    "regular": {
        "name": "Regular",
        "name_it": "Habitue",
        "desc": "Attended 5 events",
        "desc_it": "Hai partecipato a 5 eventi",
        "icon": "calendar-check",
        "trigger": "events_attended",
        "threshold": 5,
        "tier": "bronze",
        "points": 15,
    },
    "dedicated": {
        "name": "Dedicated",
        "name_it": "Dedicato",
        "desc": "Attended 10 events",
        "desc_it": "Hai partecipato a 10 eventi",
        "icon": "fire",
        "trigger": "events_attended",
        "threshold": 10,
        "tier": "silver",
        "points": 30,
    },
    "warrior": {
        "name": "Warrior",
        "name_it": "Guerriero",
        "desc": "Attended 25 events",
        "desc_it": "Hai partecipato a 25 eventi",
        "icon": "shield",
        "trigger": "events_attended",
        "threshold": 25,
        "tier": "gold",
        "points": 75,
    },
    "legend_100": {
        "name": "Centurion",
        "name_it": "Centurione",
        "desc": "Attended 100 events. You are the standard.",
        "desc_it": "100 eventi. Tu sei lo standard.",
        "icon": "crown",
        "trigger": "events_attended",
        "threshold": 100,
        "tier": "diamond",
        "points": 200,
    },

    # -- Streak milestones --
    "streak_3": {
        "name": "Hat Trick",
        "name_it": "Tripletta",
        "desc": "3 events in a row. You showed up when it mattered.",
        "desc_it": "3 eventi di fila. Ti sei fatto vivo quando contava.",
        "icon": "flame",
        "trigger": "event_streak",
        "threshold": 3,
        "tier": "bronze",
        "points": 10,
    },
    "streak_5": {
        "name": "Iron Will",
        "name_it": "Volonta di Ferro",
        "desc": "5 in a row. The couch lost.",
        "desc_it": "5 di fila. Il divano ha perso.",
        "icon": "flame",
        "trigger": "event_streak",
        "threshold": 5,
        "tier": "silver",
        "points": 25,
    },
    "streak_10": {
        "name": "Unbreakable",
        "name_it": "Indistruttibile",
        "desc": "10 in a row. Bruce Lee would be proud.",
        "desc_it": "10 di fila. Bruce Lee sarebbe orgoglioso.",
        "icon": "flame",
        "trigger": "event_streak",
        "threshold": 10,
        "tier": "gold",
        "points": 50,
    },
    "streak_20": {
        "name": "Way of the Dragon",
        "name_it": "La Via del Dragone",
        "desc": "20 in a row. You ARE the discipline.",
        "desc_it": "20 di fila. TU SEI la disciplina.",
        "icon": "dragon",
        "trigger": "event_streak",
        "threshold": 20,
        "tier": "diamond",
        "points": 100,
    },

    # -- Host milestones (for Nic) --
    "first_host": {
        "name": "Coach",
        "name_it": "Allenatore",
        "desc": "Hosted your first event",
        "desc_it": "Hai organizzato il tuo primo evento",
        "icon": "whistle",
        "trigger": "events_hosted",
        "threshold": 1,
        "tier": "bronze",
        "points": 15,
    },
    "host_10": {
        "name": "Sensei",
        "name_it": "Sensei",
        "desc": "Hosted 10 events. You're building something real.",
        "desc_it": "10 eventi organizzati. Stai costruendo qualcosa di vero.",
        "icon": "star",
        "trigger": "events_hosted",
        "threshold": 10,
        "tier": "silver",
        "points": 50,
    },
    "host_25": {
        "name": "Master",
        "name_it": "Maestro",
        "desc": "25 events hosted. The community knows your name.",
        "desc_it": "25 eventi organizzati. La comunita conosce il tuo nome.",
        "icon": "trophy",
        "trigger": "events_hosted",
        "threshold": 25,
        "tier": "gold",
        "points": 100,
    },
    "host_50": {
        "name": "Grandmaster",
        "name_it": "Gran Maestro",
        "desc": "50 events. You built a movement.",
        "desc_it": "50 eventi. Hai creato un movimento.",
        "icon": "mountain",
        "trigger": "events_hosted",
        "threshold": 50,
        "tier": "diamond",
        "points": 200,
    },

    # -- Reliability milestones --
    "reliable": {
        "name": "Man of My Word",
        "name_it": "Uomo di Parola",
        "desc": "10 events, zero no-shows. Your word means something.",
        "desc_it": "10 eventi, zero assenze. La tua parola vale.",
        "icon": "handshake",
        "trigger": "reliability",
        "threshold": 10,
        "tier": "silver",
        "points": 40,
    },
    "comeback": {
        "name": "Redemption",
        "name_it": "Redenzione",
        "desc": "Was a no-show, came back, attended 5 more. Respect.",
        "desc_it": "Eri assente, sei tornato, 5 eventi di fila. Rispetto.",
        "icon": "sunrise",
        "trigger": "comeback",
        "threshold": 5,
        "tier": "silver",
        "points": 30,
    },
}
