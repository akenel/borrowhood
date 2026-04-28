"""Item create regression guards (BL-178/179, April 28, 2026).

Angel reproduced losing tags + AI-generated story on first save. Root
cause: the POST /api/v1/items route accepted these fields in the
ItemCreate schema but NEVER COPIED them to the new BHItem instance.
Edit-save (PATCH) used a setattr loop so it preserved all fields,
which is why edit looked fine but create silently dropped them.

These tests assert each field accepted by ItemCreate is actually
written to the BHItem on create_item. They scan the route source
because adding integration fixtures would require Keycloak auth.
"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CRUD_PY = (REPO_ROOT / "src" / "routers" / "items" / "crud.py").read_text()


def _create_block():
    """Return the BHItem(...) constructor block inside create_item."""
    start = CRUD_PY.find("@router.post(\"/\"")
    assert start > 0, "POST /api/v1/items handler not found"
    end = CRUD_PY.find("db.add(item)", start)
    assert end > start
    return CRUD_PY[start:end]


class TestCreateItemPersistsAllSchemaFields:
    """Every field on ItemCreate that maps to a column on BHItem must be
    set in the create route's BHItem(...) call. Otherwise users who
    fill the field on first save get it silently dropped."""

    def test_story_is_set_on_create(self):
        block = _create_block()
        assert "story=data.story" in block, (
            "BL-178/179: create_item must set story=data.story on the BHItem. "
            "Schema accepts it; if the route doesn't copy it, AI-generated "
            "stories disappear on first save."
        )

    def test_tags_is_set_on_create(self):
        block = _create_block()
        assert "tags=data.tags" in block, (
            "BL-178/179: create_item must set tags=data.tags on the BHItem. "
            "Schema accepts it; if missing, user-set tags disappear on first save."
        )

    def test_age_restricted_is_set_on_create(self):
        block = _create_block()
        assert "age_restricted=data.age_restricted" in block, (
            "create_item must set age_restricted on the BHItem. Defaults to "
            "False on the schema but user can flip it; if missing, the safety "
            "flag is silently dropped."
        )

    def test_safety_notes_is_set_on_create(self):
        block = _create_block()
        assert "safety_notes=data.safety_notes" in block, (
            "create_item must set safety_notes. If missing, user warnings "
            "about how to use the item safely vanish on first save."
        )

    def test_existing_fields_still_set(self):
        """Sanity: don't accidentally regress the fields that DID work."""
        block = _create_block()
        for must_have in (
            "name=data.name",
            "description=data.description",
            "category=data.category",
            "item_type=data.item_type",
            "condition=data.condition",
            "brand=data.brand",
            "attributes=data.attributes",
        ):
            assert must_have in block, f"Lost a previously-working field: {must_have}"


class TestAITagsAutoApply:
    """The aiSuggest() handler must auto-apply the AI-suggested tags to
    form.tags so the user doesn't have to click each chip manually
    (Angel's 'I lost all 5 tags' bug)."""

    def test_aiSuggest_merges_tags_into_form(self):
        list_html = (REPO_ROOT / "src" / "templates" / "pages" / "list_item.html").read_text()
        # The reference test for the auto-merge logic
        assert "this.aiTags = data.tags || []" in list_html, (
            "aiSuggest must still populate aiTags for chip display"
        )
        # And the new auto-merge into form.tags
        assert "if (this.aiTags.length > 0) {" in list_html and "this.form.tags = merged.join" in list_html, (
            "BL-178/179: aiSuggest must merge ALL ai-suggested tags into "
            "form.tags automatically -- chips are a refinement UI, not a "
            "required step. Users who skip clicking chips should still get "
            "their AI tags saved."
        )
