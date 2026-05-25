"""BorrowHood database models.

All models use the BHBase mixin for UUID primary keys,
timestamps (created_at, updated_at), and soft delete (deleted_at).
"""

from src.models.user import BHUser, BHUserLanguage, BHUserSkill, BHUserPoints, BHUserSocialLink
from src.models.item import BHItem, BHItemMedia
from src.models.listing import BHListing
from src.models.rental import BHRental
from src.models.review import BHReview
from src.models.workshop import BHWorkshopMember
from src.models.audit import BHAuditLog
from src.models.report import BHReport
from src.models.bid import BHBid
from src.models.deposit import BHDeposit
from src.models.dispute import BHDispute
from src.models.payment import BHPayment
from src.models.notification import BHNotification
from src.models.notification_pref import BHNotificationPref
from src.models.badge import BHBadge
from src.models.qa import BHTestResult, BHBugReport, BHBugActivity, BHBugCommit
from src.models.backlog import BHBacklogItem, BHBacklogActivity
from src.models.translation import BHContentTranslation
from src.models.helpboard import BHHelpPost, BHHelpReply, BHHelpMedia, BHHelpUpvote
from src.models.lockbox import BHLockBoxAccess
from src.models.skill_verification import BHSkillVerification
from src.models.telegram import BHTelegramLink
from src.models.mentorship import BHMentorship
from src.models.message import BHMessage
from src.models.listing_qa import BHListingQA
from src.models.event_rsvp import BHEventRSVP
from src.models.achievement import BHAchievement
# Newer models that weren't registered with Base.metadata via this __init__
# -- without these imports, create_all() can't see the tables they own,
# and FKs from older tables (e.g. bh_user.default_community_id -> bh_community)
# fail with NoReferencedTableError. Caught when CI's seed step finally
# surfaced the real traceback (was silently exit-1 for 9+ days).
from src.models.analytics import BHItemView
from src.models.community import BHCommunity, BHCommunityMembership
from src.models.delivery import BHDeliveryTracking, BHDeliveryEvent
from src.models.insurance import BHInsurancePolicy, BHInsuranceClaim
from src.models.invoice import BHInvoice
from src.models.quote import BHServiceQuote
from src.models.raffle import BHRaffle, BHRaffleTicket, BHRaffleVerification, BHRaffleVouch
from src.models.saved_search import BHSavedSearch

__all__ = [
    "BHUser",
    "BHUserLanguage",
    "BHUserSkill",
    "BHUserPoints",
    "BHUserSocialLink",
    "BHItem",
    "BHItemMedia",
    "BHListing",
    "BHRental",
    "BHReview",
    "BHWorkshopMember",
    "BHAuditLog",
    "BHReport",
    "BHBid",
    "BHDeposit",
    "BHDispute",
    "BHPayment",
    "BHNotification",
    "BHNotificationPref",
    "BHBadge",
    "BHTestResult",
    "BHBugReport",
    "BHBugActivity",
    "BHBugCommit",
    "BHBacklogItem",
    "BHBacklogActivity",
    "BHContentTranslation",
    "BHHelpPost",
    "BHHelpReply",
    "BHHelpMedia",
    "BHHelpUpvote",
    "BHLockBoxAccess",
    "BHSkillVerification",
    "BHTelegramLink",
    "BHMentorship",
    "BHMessage",
    "BHListingQA",
    "BHEventRSVP",
    "BHAchievement",
]
