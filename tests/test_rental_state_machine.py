"""Tests for rental state machine transitions.

Tests the core business logic without needing auth.
"""

import pytest
from src.models.rental import RentalStatus, validate_rental_transition, VALID_RENTAL_TRANSITIONS


class TestRentalStateMachine:
    """Test all valid and invalid state transitions."""

    # --- Valid transitions ---

    def test_pending_to_approved(self):
        assert validate_rental_transition(RentalStatus.PENDING, RentalStatus.APPROVED)

    def test_pending_to_declined(self):
        assert validate_rental_transition(RentalStatus.PENDING, RentalStatus.DECLINED)

    def test_pending_to_cancelled(self):
        assert validate_rental_transition(RentalStatus.PENDING, RentalStatus.CANCELLED)

    def test_approved_to_picked_up(self):
        assert validate_rental_transition(RentalStatus.APPROVED, RentalStatus.PICKED_UP)

    def test_approved_to_cancelled(self):
        assert validate_rental_transition(RentalStatus.APPROVED, RentalStatus.CANCELLED)

    def test_approved_to_disputed(self):
        assert validate_rental_transition(RentalStatus.APPROVED, RentalStatus.DISPUTED)

    def test_picked_up_to_returned(self):
        assert validate_rental_transition(RentalStatus.PICKED_UP, RentalStatus.RETURNED)

    def test_picked_up_to_disputed(self):
        assert validate_rental_transition(RentalStatus.PICKED_UP, RentalStatus.DISPUTED)

    def test_returned_to_completed(self):
        assert validate_rental_transition(RentalStatus.RETURNED, RentalStatus.COMPLETED)

    def test_returned_to_disputed(self):
        assert validate_rental_transition(RentalStatus.RETURNED, RentalStatus.DISPUTED)

    def test_disputed_to_completed(self):
        assert validate_rental_transition(RentalStatus.DISPUTED, RentalStatus.COMPLETED)

    def test_disputed_to_cancelled(self):
        assert validate_rental_transition(RentalStatus.DISPUTED, RentalStatus.CANCELLED)

    # --- Invalid transitions (terminal states cannot go anywhere) ---

    def test_completed_is_terminal(self):
        for status in RentalStatus:
            assert not validate_rental_transition(RentalStatus.COMPLETED, status)

    def test_declined_is_terminal(self):
        for status in RentalStatus:
            assert not validate_rental_transition(RentalStatus.DECLINED, status)

    def test_cancelled_is_terminal(self):
        for status in RentalStatus:
            assert not validate_rental_transition(RentalStatus.CANCELLED, status)

    # --- Invalid backwards transitions ---

    def test_cannot_go_backwards_approved_to_pending(self):
        assert not validate_rental_transition(RentalStatus.APPROVED, RentalStatus.PENDING)

    def test_cannot_go_backwards_picked_up_to_approved(self):
        assert not validate_rental_transition(RentalStatus.PICKED_UP, RentalStatus.APPROVED)

    def test_cannot_go_backwards_returned_to_picked_up(self):
        assert not validate_rental_transition(RentalStatus.RETURNED, RentalStatus.PICKED_UP)

    def test_cannot_skip_pending_to_picked_up(self):
        assert not validate_rental_transition(RentalStatus.PENDING, RentalStatus.PICKED_UP)

    def test_cannot_skip_pending_to_returned(self):
        assert not validate_rental_transition(RentalStatus.PENDING, RentalStatus.RETURNED)

    def test_cannot_skip_pending_to_completed(self):
        assert not validate_rental_transition(RentalStatus.PENDING, RentalStatus.COMPLETED)

    def test_cannot_skip_approved_to_returned(self):
        assert not validate_rental_transition(RentalStatus.APPROVED, RentalStatus.RETURNED)

    def test_cannot_skip_approved_to_completed(self):
        assert not validate_rental_transition(RentalStatus.APPROVED, RentalStatus.COMPLETED)

    # --- Completeness check ---

    def test_all_states_have_transition_rules(self):
        """Every status must have an entry in the transition map."""
        for status in RentalStatus:
            assert status in VALID_RENTAL_TRANSITIONS

    def test_happy_path_full_flow(self):
        """Verify the full happy path: PENDING -> APPROVED -> PICKED_UP -> RETURNED -> COMPLETED"""
        flow = [
            RentalStatus.PENDING,
            RentalStatus.APPROVED,
            RentalStatus.PICKED_UP,
            RentalStatus.RETURNED,
            RentalStatus.COMPLETED,
        ]
        for i in range(len(flow) - 1):
            assert validate_rental_transition(flow[i], flow[i + 1]), \
                f"Transition {flow[i].value} -> {flow[i+1].value} should be valid"

    def test_dispute_flow(self):
        """Verify dispute can happen from active states and resolve."""
        disputable = [RentalStatus.APPROVED, RentalStatus.PICKED_UP, RentalStatus.RETURNED]
        for status in disputable:
            assert validate_rental_transition(status, RentalStatus.DISPUTED), \
                f"Should be able to dispute from {status.value}"

        # Dispute can resolve to completed or cancelled
        assert validate_rental_transition(RentalStatus.DISPUTED, RentalStatus.COMPLETED)
        assert validate_rental_transition(RentalStatus.DISPUTED, RentalStatus.CANCELLED)
