"""Task #30: BacklogItemUpdate + BacklogItemRead must expose resolution_sha
and resolution_note so the API can record and surface fix information.

These are schema-shape contract tests — catch silent field-drop regressions
the way BL-192 fix was originally blocked.
"""


def test_backlog_item_update_accepts_resolution_fields():
    """PUT /api/v1/backlog/items/{id} must accept resolution_sha + resolution_note.

    Prior to task #30, BacklogItemUpdate silently dropped these fields, so
    callers got 200 OK but the DB never persisted them.
    """
    from src.schemas.backlog import BacklogItemUpdate

    upd = BacklogItemUpdate(
        resolution_sha="b50d48c",
        resolution_note="Shipped via PR #1 -- one-line WHERE clause swap",
    )
    assert upd.resolution_sha == "b50d48c"
    assert upd.resolution_note == "Shipped via PR #1 -- one-line WHERE clause swap"


def test_backlog_item_update_resolution_fields_optional():
    """Existing callers that don't set resolution fields must still validate."""
    from src.schemas.backlog import BacklogItemUpdate

    upd = BacklogItemUpdate(status=None)
    assert upd.resolution_sha is None
    assert upd.resolution_note is None


def test_backlog_item_update_resolution_sha_length_cap():
    """resolution_sha capped at 64 chars (sha256 hex max)."""
    import pytest
    from pydantic import ValidationError
    from src.schemas.backlog import BacklogItemUpdate

    # 64-char hex (full sha256) is allowed
    sha64 = "a" * 64
    BacklogItemUpdate(resolution_sha=sha64)

    # 65 chars is rejected
    with pytest.raises(ValidationError):
        BacklogItemUpdate(resolution_sha="a" * 65)


def test_backlog_item_read_includes_resolution_fields():
    """GET responses must include resolution_sha + resolution_note so the UI
    can surface them on done items.
    """
    from src.schemas.backlog import BacklogItemRead

    fields = BacklogItemRead.model_fields
    assert "resolution_sha" in fields, (
        "BacklogItemRead missing resolution_sha — API consumers can't see fix info"
    )
    assert "resolution_note" in fields, (
        "BacklogItemRead missing resolution_note — API consumers can't see fix info"
    )
