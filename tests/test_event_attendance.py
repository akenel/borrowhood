"""Tests for the auto-attendance background service."""

from datetime import datetime, timedelta, timezone

import pytest


def test_cutoff_uses_event_end_plus_grace():
    """When event_end is set, cutoff = event_end + GRACE_HOURS."""
    from src.services.event_attendance import _event_cutoff, GRACE_HOURS

    class L:
        event_start = datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc)
        event_end = datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc)

    cutoff = _event_cutoff(L())
    assert cutoff == L.event_end + timedelta(hours=GRACE_HOURS)


def test_cutoff_falls_back_to_start_plus_24h():
    """Without event_end, cutoff = event_start + fallback + grace."""
    from src.services.event_attendance import (
        _event_cutoff, GRACE_HOURS, FALLBACK_EVENT_DURATION_HOURS,
    )

    class L:
        event_start = datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc)
        event_end = None

    cutoff = _event_cutoff(L())
    expected = L.event_start + timedelta(
        hours=FALLBACK_EVENT_DURATION_HOURS + GRACE_HOURS
    )
    assert cutoff == expected


def test_cutoff_none_without_event_start():
    """Events with no start time can't be auto-attended."""
    from src.services.event_attendance import _event_cutoff

    class L:
        event_start = None
        event_end = None

    assert _event_cutoff(L()) is None


@pytest.mark.asyncio
async def test_auto_attend_skips_future_events(db_client):
    """A function-level smoke test: the service function is importable
    and doesn't blow up on an empty/live DB."""
    from src.database import async_session
    from src.services.event_attendance import auto_attend_past_events

    async with async_session() as db:
        events_closed, rsvps = await auto_attend_past_events(db)
        # No assertion on counts -- just that it ran without crashing.
        assert events_closed >= 0
        assert rsvps >= 0
