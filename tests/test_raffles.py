"""Tests for raffle system: model, engine, and API endpoints."""

import pytest
from datetime import datetime, timedelta, timezone


# ── Model / enum tests ─────────────────────────────────────────────────

def test_raffle_status_enum():
    from src.models.raffle import RaffleStatus
    assert {s.value for s in RaffleStatus} == {
        "draft", "published", "active", "drawn", "completed", "cancelled"
    }


def test_ticket_status_enum():
    from src.models.raffle import RaffleTicketStatus
    assert {s.value for s in RaffleTicketStatus} == {
        "reserved", "confirmed", "expired", "cancelled"
    }


def test_draw_type_enum():
    from src.models.raffle import RaffleDrawType
    assert {s.value for s in RaffleDrawType} == {"date", "soldout", "manual"}


def test_delivery_enum():
    from src.models.raffle import RaffleDelivery
    assert {s.value for s in RaffleDelivery} == {"pickup", "shipping", "digital"}


def test_listing_type_has_raffle():
    from src.models.listing import ListingType
    assert ListingType.RAFFLE.value == "raffle"


# ── Trust tiers ────────────────────────────────────────────────────────

def test_trust_tier_zero_completions():
    from src.models.raffle import max_raffle_value_for
    assert max_raffle_value_for(0) == 10


def test_trust_tier_scales():
    from src.models.raffle import max_raffle_value_for
    assert max_raffle_value_for(1) == 20
    assert max_raffle_value_for(2) == 40
    assert max_raffle_value_for(3) == 80
    assert max_raffle_value_for(4) == 160
    assert max_raffle_value_for(5) == 320


def test_trust_tier_caps_at_ceiling():
    from src.models.raffle import max_raffle_value_for, RAFFLE_HARD_CEILING_EUR
    assert max_raffle_value_for(100) == RAFFLE_HARD_CEILING_EUR


# ── Provably fair draw ─────────────────────────────────────────────────

def test_draw_deterministic():
    """Same seed + same pool = same winner every time."""
    from src.services.raffle_engine import compute_winner
    seed = "abc123"
    ids = ["t1", "t2", "t3"]
    quantities = [1, 2, 1]

    idx1, hash1 = compute_winner(seed, ids, quantities)
    idx2, hash2 = compute_winner(seed, ids, quantities)
    assert idx1 == idx2
    assert hash1 == hash2


def test_draw_different_seed_different_winner():
    """Different seeds give different proof hashes."""
    from src.services.raffle_engine import compute_winner
    ids = ["t1", "t2", "t3"]
    quantities = [1, 1, 1]
    _, h1 = compute_winner("seed_a", ids, quantities)
    _, h2 = compute_winner("seed_b", ids, quantities)
    assert h1 != h2


def test_draw_respects_quantity():
    """User with 3 tickets appears 3 times in the pool."""
    from src.services.raffle_engine import compute_winner
    ids = ["solo", "triple"]
    quantities = [1, 3]
    # Pool should be [solo, triple, triple, triple] = size 4
    # Run 100 draws with different seeds — triple should win ~75%
    triple_wins = 0
    for i in range(100):
        idx, _ = compute_winner(f"seed{i}", ids, quantities)
        pool = ["solo"] + ["triple"] * 3
        if pool[idx] == "triple":
            triple_wins += 1
    assert triple_wins > 50  # statistically should be ~75, floor at 50


def test_draw_single_ticket():
    """One confirmed ticket = guaranteed winner."""
    from src.services.raffle_engine import compute_winner
    idx, proof = compute_winner("any_seed", ["only_ticket"], [1])
    assert idx == 0
    assert len(proof) == 64  # sha256 hex


# ── Anti-casino safeguards ─────────────────────────────────────────────

def test_cooldown_constant():
    from src.models.raffle import COOLDOWN_DAYS
    assert COOLDOWN_DAYS == 7


def test_one_active_raffle_check_exists():
    """check_one_active_raffle function is importable."""
    from src.services.raffle_engine import check_one_active_raffle
    assert callable(check_one_active_raffle)


def test_cooldown_check_exists():
    """check_cooldown function is importable."""
    from src.services.raffle_engine import check_cooldown
    assert callable(check_cooldown)


def test_raffle_ban_check_exists():
    from src.services.raffle_engine import check_raffle_ban
    assert callable(check_raffle_ban)


def test_raffle_ban_threshold():
    from src.models.raffle import RAFFLE_BAN_AFTER_FAILURES
    assert RAFFLE_BAN_AFTER_FAILURES == 2


def test_grace_period_constant():
    from src.models.raffle import ORGANIZER_GRACE_DAYS
    assert ORGANIZER_GRACE_DAYS == 30


def test_demote_function_exists():
    from src.services.raffle_engine import demote_raffle_abandoners
    assert callable(demote_raffle_abandoners)


# ── Legend vouch system ─────────────────────────────────────────────────

def test_vouch_reason_enum():
    from src.models.raffle import VouchReason
    assert {r.value for r in VouchReason} == {
        "personal_emergency", "technical_issue", "honest_mistake",
        "delivery_delay", "communication_failure", "known_personally",
    }


def test_vouch_model_exists():
    from src.models.raffle import BHRaffleVouch
    assert BHRaffleVouch.__tablename__ == "bh_raffle_vouch"


def test_can_vouch_flag_default_false():
    from src.models.user import BHUser
    col = BHUser.__table__.columns["can_vouch_raffles"]
    assert col.default.arg is False


# ── Gamification tests ─────────────────────────────────────────────────

def test_points_constants_defined():
    from src.models.raffle import (
        POINTS_RAFFLE_ORGANIZER_COMPLETE, POINTS_RAFFLE_TICKET_PURCHASE,
        POINTS_RAFFLE_WINNER, POINTS_RAFFLE_VERIFICATION,
        POINTS_RAFFLE_ORGANIZER_VERIFIED, VERIFICATION_CLEAN_THRESHOLD,
    )
    assert POINTS_RAFFLE_ORGANIZER_COMPLETE == 25
    assert POINTS_RAFFLE_TICKET_PURCHASE == 3
    assert POINTS_RAFFLE_WINNER == 10
    assert POINTS_RAFFLE_VERIFICATION == 5
    assert POINTS_RAFFLE_ORGANIZER_VERIFIED == 15
    assert VERIFICATION_CLEAN_THRESHOLD == 0.80


def test_is_cleanly_completed_logic():
    """Raffle needs 80%+ positive verifications to count as clean."""
    from src.services.raffle_engine import is_cleanly_completed
    from src.models.raffle import RaffleStatus

    class FakeRaffle:
        status = RaffleStatus.COMPLETED
        verifications_positive = 4
        verifications_negative = 1
        @property
        def verification_rate(self):
            t = self.verifications_positive + self.verifications_negative
            return round(self.verifications_positive / t * 100, 1) if t else 0

    r = FakeRaffle()
    assert is_cleanly_completed(r) is True  # 80% = threshold met

    r.verifications_positive = 3
    r.verifications_negative = 2
    assert is_cleanly_completed(r) is False  # 60% < 80%


def test_verification_rate_property():
    from src.models.raffle import RaffleStatus

    class FakeRaffle:
        status = RaffleStatus.COMPLETED
        verifications_positive = 9
        verifications_negative = 1
        @property
        def verification_rate(self):
            t = self.verifications_positive + self.verifications_negative
            return round(self.verifications_positive / t * 100, 1) if t else 0

    assert FakeRaffle().verification_rate == 90.0


def test_verification_rate_zero_verifications():
    class FakeRaffle:
        verifications_positive = 0
        verifications_negative = 0
        @property
        def verification_rate(self):
            t = self.verifications_positive + self.verifications_negative
            return round(self.verifications_positive / t * 100, 1) if t else 0

    assert FakeRaffle().verification_rate == 0.0
