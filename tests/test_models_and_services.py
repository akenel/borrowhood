"""Tests for models, badge service, review weights, and tier calculations.

No auth needed -- validates pure business logic and data integrity.
"""

import pytest
from slugify import slugify


# --- Review Weight System ---

class TestReviewWeights:
    """Verify review weight multipliers match tier design."""

    def test_weight_values(self):
        from src.models.review import REVIEW_WEIGHTS
        from src.models.user import BadgeTier

        assert REVIEW_WEIGHTS[BadgeTier.NEWCOMER] == 1.0
        assert REVIEW_WEIGHTS[BadgeTier.ACTIVE] == 2.0
        assert REVIEW_WEIGHTS[BadgeTier.TRUSTED] == 5.0
        assert REVIEW_WEIGHTS[BadgeTier.PILLAR] == 8.0
        assert REVIEW_WEIGHTS[BadgeTier.LEGEND] == 10.0

    def test_all_tiers_have_weights(self):
        from src.models.review import REVIEW_WEIGHTS
        from src.models.user import BadgeTier

        for tier in BadgeTier:
            assert tier in REVIEW_WEIGHTS, f"Missing weight for tier {tier.value}"

    def test_weights_are_monotonically_increasing(self):
        from src.models.review import REVIEW_WEIGHTS
        from src.models.user import BadgeTier

        tiers = [BadgeTier.NEWCOMER, BadgeTier.ACTIVE, BadgeTier.TRUSTED,
                 BadgeTier.PILLAR, BadgeTier.LEGEND]
        for i in range(len(tiers) - 1):
            assert REVIEW_WEIGHTS[tiers[i]] < REVIEW_WEIGHTS[tiers[i + 1]], \
                f"Weight for {tiers[i].value} should be less than {tiers[i+1].value}"

    def test_weighted_average_calculation(self):
        """Simulate a weighted average like review_summary endpoint does."""
        from src.models.review import REVIEW_WEIGHTS
        from src.models.user import BadgeTier

        # Simulate: 1 newcomer gives 3 stars, 1 legend gives 5 stars
        reviews = [
            (3, REVIEW_WEIGHTS[BadgeTier.NEWCOMER]),   # 3 * 1.0 = 3.0
            (5, REVIEW_WEIGHTS[BadgeTier.LEGEND]),      # 5 * 10.0 = 50.0
        ]

        total_weighted = sum(r * w for r, w in reviews)
        total_weight = sum(w for _, w in reviews)
        weighted_avg = round(total_weighted / total_weight, 2)

        # Legend's review dominates: (3+50)/(1+10) = 53/11 = 4.82
        assert weighted_avg == 4.82

        # Simple average would be (3+5)/2 = 4.0
        simple_avg = round(sum(r for r, _ in reviews) / len(reviews), 2)
        assert simple_avg == 4.0

        # Weighted should be higher because the legend gave 5 stars
        assert weighted_avg > simple_avg


# --- Badge Tier Thresholds ---

class TestBadgeTierThresholds:
    """Verify tier boundaries match the design."""

    def test_tier_values(self):
        from src.models.user import BadgeTier
        expected = {"newcomer", "active", "trusted", "pillar", "legend"}
        assert {t.value for t in BadgeTier} == expected

    def test_tier_boundary_newcomer(self):
        """0-49 points = newcomer."""
        assert _tier_for_points(0) == "newcomer"
        assert _tier_for_points(49) == "newcomer"

    def test_tier_boundary_active(self):
        """50-199 points = active."""
        assert _tier_for_points(50) == "active"
        assert _tier_for_points(199) == "active"

    def test_tier_boundary_trusted(self):
        """200-499 points = trusted."""
        assert _tier_for_points(200) == "trusted"
        assert _tier_for_points(499) == "trusted"

    def test_tier_boundary_pillar(self):
        """500-999 points = pillar."""
        assert _tier_for_points(500) == "pillar"
        assert _tier_for_points(999) == "pillar"

    def test_tier_boundary_legend(self):
        """1000+ points = legend."""
        assert _tier_for_points(1000) == "legend"
        assert _tier_for_points(9999) == "legend"

    def test_points_formula(self):
        """items*10 + rentals*20 + reviews*5 + five_stars*15."""
        # 10 items, 5 rentals, 10 reviews, 2 five-stars
        total = (10 * 10) + (5 * 20) + (10 * 5) + (2 * 15)
        assert total == 280  # = trusted tier
        assert _tier_for_points(total) == "trusted"


def _tier_for_points(total: int) -> str:
    """Mirror the tier calculation from badges.py."""
    if total >= 1000:
        return "legend"
    elif total >= 500:
        return "pillar"
    elif total >= 200:
        return "trusted"
    elif total >= 50:
        return "active"
    else:
        return "newcomer"


# --- Badge Catalog Completeness ---

class TestBadgeCatalog:
    """Verify badge definitions are complete and consistent."""

    def test_all_badge_codes_have_info(self):
        from src.models.badge import BadgeCode, BADGE_INFO
        for code in BadgeCode:
            assert code in BADGE_INFO, f"Badge {code.value} missing from BADGE_INFO"

    def test_badge_info_has_required_fields(self):
        from src.models.badge import BADGE_INFO
        required = {"name", "description", "icon", "color"}
        for code, info in BADGE_INFO.items():
            for field in required:
                assert field in info, f"Badge {code.value} missing field '{field}'"
                assert info[field], f"Badge {code.value} has empty '{field}'"

    def test_badge_code_count(self):
        from src.models.badge import BadgeCode
        # We should have at least 14 badge types
        assert len(BadgeCode) >= 14

    def test_no_duplicate_badge_names(self):
        from src.models.badge import BADGE_INFO
        names = [info["name"] for info in BADGE_INFO.values()]
        assert len(names) == len(set(names)), "Duplicate badge names found"


# --- Slug Generation ---

class TestSlugGeneration:
    """Test slug generation for items and users."""

    def test_basic_slug(self):
        assert slugify("Bosch Drill") == "bosch-drill"

    def test_unicode_slug(self):
        assert slugify("Trapano Bosch (Usato)") == "trapano-bosch-usato"

    def test_special_chars_removed(self):
        slug = slugify("My Item @ $50/day!!!")
        assert "@" not in slug
        assert "$" not in slug
        assert "!" not in slug

    def test_max_length(self):
        long_name = "A" * 300
        slug = slugify(long_name, max_length=200)
        assert len(slug) <= 200

    def test_empty_string(self):
        slug = slugify("")
        assert slug == ""

    def test_numeric_only(self):
        slug = slugify("12345")
        assert slug == "12345"

    def test_accented_chars(self):
        slug = slugify("Caffè Maltese Speciale")
        assert "caffe" in slug or "caff" in slug

    def test_german_umlauts(self):
        slug = slugify("Bohrmaschine fur Anfanger")
        assert "bohrmaschine" in slug


# --- Deposit Status Machine ---

class TestDepositStatuses:
    """Verify deposit status values."""

    def test_deposit_status_values(self):
        from src.models.deposit import DepositStatus
        expected = {"held", "released", "forfeited", "partial_release"}
        assert {s.value for s in DepositStatus} == expected


# --- Dispute Model ---

class TestDisputeModel:
    """Verify dispute enums are complete."""

    def test_dispute_status_values(self):
        from src.models.dispute import DisputeStatus
        expected = {"filed", "under_review", "resolved", "dismissed"}
        assert {s.value for s in DisputeStatus} == expected

    def test_dispute_reason_values(self):
        from src.models.dispute import DisputeReason
        expected = {
            "item_not_as_described", "item_damaged", "item_not_returned",
            "late_return", "no_show", "payment_issue", "safety_concern", "other"
        }
        assert {r.value for r in DisputeReason} == expected

    def test_dispute_resolution_values(self):
        from src.models.dispute import DisputeResolution
        expected = {
            "full_refund", "partial_refund", "deposit_forfeited",
            "deposit_returned", "no_action", "account_warning", "account_suspended"
        }
        assert {r.value for r in DisputeResolution} == expected


# --- Payment Model ---

class TestPaymentModel:
    """Verify payment enums."""

    def test_payment_provider_values(self):
        from src.models.payment import PaymentProvider
        expected = {"paypal", "stripe", "manual"}
        assert {p.value for p in PaymentProvider} == expected

    def test_payment_status_values(self):
        from src.models.payment import PaymentStatus
        expected = {"pending", "completed", "failed", "refunded", "partial_refund"}
        assert {s.value for s in PaymentStatus} == expected

    def test_payment_type_values(self):
        from src.models.payment import PaymentType
        expected = {"rental", "deposit", "purchase", "auction", "service"}
        assert {t.value for t in PaymentType} == expected


# --- Notification Model ---

class TestNotificationModel:
    """Verify all notification types are present."""

    def test_notification_count(self):
        from src.models.notification import NotificationType
        # Should have at least 18 notification types
        assert len(NotificationType) >= 18

    def test_rental_notifications_complete(self):
        from src.models.notification import NotificationType
        rental_types = {
            "rental_request", "rental_approved", "rental_declined",
            "rental_picked_up", "rental_returned", "rental_completed",
            "rental_cancelled"
        }
        actual = {t.value for t in NotificationType}
        assert rental_types.issubset(actual)

    def test_auction_notifications_complete(self):
        from src.models.notification import NotificationType
        auction_types = {"bid_placed", "bid_outbid", "auction_won", "auction_ended"}
        actual = {t.value for t in NotificationType}
        assert auction_types.issubset(actual)

    def test_dispute_notifications_complete(self):
        from src.models.notification import NotificationType
        dispute_types = {"dispute_filed", "dispute_resolved"}
        actual = {t.value for t in NotificationType}
        assert dispute_types.issubset(actual)

    def test_lockbox_notifications_complete(self):
        from src.models.notification import NotificationType
        lockbox_types = {
            "lockbox_codes_ready", "lockbox_pickup_confirmed",
            "lockbox_return_confirmed"
        }
        actual = {t.value for t in NotificationType}
        assert lockbox_types.issubset(actual)


# --- User Model Enums ---

class TestUserModelEnums:
    """Verify user-related enums."""

    def test_workshop_type_values(self):
        from src.models.user import WorkshopType
        expected = {
            "kitchen", "garage", "garden", "workshop", "studio", "office", "other",
            "arena", "camp", "dock", "dojo", "forge", "fortress",
            "laboratory", "lodge", "observatory", "palace", "pavilion", "study",
        }
        assert {t.value for t in WorkshopType} == expected

    def test_account_status_values(self):
        from src.models.user import AccountStatus
        expected = {"registered", "verified", "active", "suspended", "deactivated", "banned"}
        assert {s.value for s in AccountStatus} == expected

    def test_cefr_levels(self):
        from src.models.user import CEFRLevel
        expected = {"A1", "A2", "B1", "B2", "C1", "C2", "native"}
        assert {l.value for l in CEFRLevel} == expected

    def test_badge_tier_ordering(self):
        """Badge tiers should go newcomer -> active -> trusted -> pillar -> legend."""
        from src.models.user import BadgeTier
        tiers = list(BadgeTier)
        assert tiers[0] == BadgeTier.NEWCOMER
        assert tiers[-1] == BadgeTier.LEGEND


# --- Listing Model ---

class TestListingModel:
    """Verify listing fields cover all use cases."""

    def test_listing_type_includes_auction(self):
        from src.models.listing import ListingType
        values = {t.value for t in ListingType}
        assert "auction" in values
        assert "rent" in values
        assert "sell" in values
        assert "service" in values

    def test_listing_has_auction_fields(self):
        """BHListing should have auction-related columns."""
        from src.models.listing import BHListing
        columns = {c.name for c in BHListing.__table__.columns}
        assert "starting_bid" in columns
        assert "bid_increment" in columns
        assert "reserve_price" in columns
        assert "auction_end" in columns
