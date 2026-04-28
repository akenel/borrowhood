"""BL-182: Unblock raffle creation when user has no date_of_birth.

Angel hit a 404 trying to set up a raffle. The trust-tier banner on
/raffles/new said "Add your date of birth in Settings" and linked to
/settings, which doesn't exist. There was also no DOB editor anywhere
in the app -- the column existed and was checked, but nothing wrote it.

These tests guard the two-part fix:
1. PATCH /api/v1/users/me must accept date_of_birth in its allowlist.
2. raffle_create.html must NOT link to the dead /settings route.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_users_me_patch_allows_date_of_birth():
    src = (REPO_ROOT / "src" / "routers" / "users" / "me.py").read_text()
    # The allowed-fields set must contain date_of_birth so the PATCH endpoint
    # actually persists the value the inline raffle banner sends.
    assert '"date_of_birth"' in src, (
        "PATCH /api/v1/users/me must include date_of_birth in its allowlist. "
        "Without this, the inline DOB form on /raffles/new silently no-ops "
        "and Angel stays gated."
    )


def test_users_me_patch_parses_iso_date():
    src = (REPO_ROOT / "src" / "routers" / "users" / "me.py").read_text()
    # date_of_birth arrives as a JSON string from <input type="date"> --
    # we must parse it into a date() before assignment, otherwise SQLAlchemy
    # writes a string into a DATE column and the age check explodes later.
    assert "_date.fromisoformat(raw)" in src, (
        "date_of_birth must be parsed via date.fromisoformat -- "
        "HTML5 date inputs send 'YYYY-MM-DD' as a string."
    )


def test_raffle_create_does_not_link_to_dead_settings_route():
    html = (REPO_ROOT / "src" / "templates" / "pages" / "raffle_create.html").read_text()
    # /settings is a 404. Use an inline DOB form here, or link to an actual
    # page that exists. Either way: never /settings.
    assert 'href="/settings"' not in html, (
        "raffle_create.html still links to /settings -- this route 404s. "
        "BL-182: replaced with inline DOB save-and-reload form."
    )


def test_raffle_create_has_inline_dob_form():
    html = (REPO_ROOT / "src" / "templates" / "pages" / "raffle_create.html").read_text()
    # The fix puts the DOB input right in the trust-tier banner so users
    # never leave the raffle flow.
    assert 'type="date"' in html and "/api/v1/users/me" in html, (
        "raffle_create.html must include an inline date input + PATCH to "
        "/api/v1/users/me so users can clear the age gate without leaving."
    )
