"""Offer → seller notification → Telegram forward (the art-drop ping path).

Promoted from a one-shot verifier (was /tmp/verify_offer_notify.py) into a
committed regression net. The art drop relies on this: when a buyer makes an
offer, the seller (Corrado) must get pinged on Telegram with no human relay.

`make_offer` calling `create_notification(... MESSAGE_RECEIVED ...)` for the
item owner is a direct, code-confirmed call. What's runtime-subtle — and what
this guards — is the DELIVERY branch inside `create_notification`:
  - the per-type mute-pref gate (default = deliver)
  - the Telegram forward when the seller has notify_telegram + telegram_chat_id
  - the telegram_sent flag getting set from the sender's return

We monkeypatch the Telegram sender so nothing leaves the box (staging/prod have
TG delivery off anyway) but PROVE create_notification invokes it with the
seller's chat id + the offer text. The probe user is created and torn down
inside one transaction.

DB-dependent: self-skips when the database is unreachable (so it's a no-op on a
laptop with no DB, and a real check inside the container where `make test`
runs).
"""

import uuid

import pytest
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.models.notification import BHNotification, NotificationType
from src.models.user import BHUser

pytestmark = pytest.mark.db


@pytest.fixture
async def db_session():
    """A NullPool DB session that skips the test if the database is unreachable."""
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        await engine.dispose()
        pytest.skip("Database not reachable")
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        yield session
    await engine.dispose()


async def test_offer_pings_a_telegram_linked_seller(db_session, monkeypatch):
    calls = []

    async def fake_send(chat_id, text_):
        calls.append((chat_id, text_))
        return True

    # create_notification does `from ... import send_telegram_message`, so the
    # name it looks up lives in notify's namespace — patch it THERE.
    monkeypatch.setattr("src.services.notify.send_telegram_message", fake_send)
    from src.services.notify import create_notification

    tag = "offerprobe-" + uuid.uuid4().hex[:8]
    seller = BHUser(
        keycloak_id=tag + "-kc", email=tag + "@example.com",
        display_name="Offer Probe Seller", slug=tag,
        notify_telegram=True, telegram_chat_id="999000111", notify_email=False,
    )
    db_session.add(seller)
    await db_session.flush()

    try:
        notification = await create_notification(
            db_session, user_id=seller.id,
            notification_type=NotificationType.MESSAGE_RECEIVED,
            title="New offer from Probe Buyer",
            body="€180.00 on Probe Piece 1/1",
            link="/messages", entity_type="message",
        )
        await db_session.flush()
        row = await db_session.scalar(
            select(BHNotification).where(BHNotification.user_id == seller.id)
        )

        # in-app notification
        assert notification is not None, "create_notification returned None (muted?)"
        assert row is not None, "in-app notification did not persist"
        assert row.notification_type == NotificationType.MESSAGE_RECEIVED
        assert "New offer" in (row.title or "")

        # Telegram forward
        assert len(calls) == 1, f"expected exactly one Telegram forward, got {len(calls)}"
        assert calls[0][0] == "999000111", "forwarded to the wrong chat_id"
        assert "New offer" in calls[0][1] and "180" in calls[0][1], "TG text lost the offer/price"
        assert row.telegram_sent is True, "telegram_sent flag not set from the sender result"
    finally:
        await db_session.execute(delete(BHNotification).where(BHNotification.user_id == seller.id))
        await db_session.execute(delete(BHUser).where(BHUser.id == seller.id))
        await db_session.commit()
