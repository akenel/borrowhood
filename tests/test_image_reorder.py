"""Drag-to-reorder photos in the listing form (BL-169, April 27, 2026).

Edit mode already had this -- this test locks in the same UX for the
new-listing CREATE flow (uploadPreviews grid). Cover photo is whichever
sits at index 0; users need a way to put it there before submit.
"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LIST_ITEM_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "list_item.html").read_text()


def _upload_grid_block() -> str:
    """The uploadPreviews grid block we're guarding (CREATE-mode preview grid)."""
    start = LIST_ITEM_HTML.find("BL-169: drag-to-reorder")
    assert start > 0, "BL-169 marker not found in list_item.html"
    end = LIST_ITEM_HTML.find("<!-- Image preview (AI generated)", start)
    return LIST_ITEM_HTML[start:end]


class TestUploadPreviewReorder:
    def test_block_marked_with_bl_169(self):
        # Compile-time guarantee that the preview grid carries the BL marker
        assert "BL-169" in LIST_ITEM_HTML

    def test_grid_has_drag_state(self):
        block = _upload_grid_block()
        assert "upDragIdx:" in block and "upDragOverIdx:" in block, (
            "Upload preview grid must track drag source + drop target indices"
        )

    def test_moveUpload_swaps_files_and_previews_in_lockstep(self):
        block = _upload_grid_block()
        # Both arrays must shift together so the file at sort position N
        # corresponds to preview N
        assert "uploadFiles.splice(from, 1)" in block
        assert "uploadFiles.splice(to, 0," in block
        assert "uploadPreviews.splice(from, 1)" in block
        assert "uploadPreviews.splice(to, 0," in block

    def test_video_cannot_become_cover(self):
        block = _upload_grid_block()
        # Same defense as edit-mode: refuse to move a video to slot 0
        assert "Cover image cannot be a video" in block, (
            "moveUpload must reject moving __video__ to index 0 -- the "
            "cover is what platforms use for OG image and videos don't preview"
        )

    def test_drag_handlers_present(self):
        block = _upload_grid_block()
        for handler in ("@dragstart", "@dragover.prevent", "@drop.prevent", "@dragend"):
            assert handler in block, f"Upload grid items must wire {handler}"

    def test_tap_to_cover_button_for_touch_fallback(self):
        block = _upload_grid_block()
        # Touch users who can't drag get a tap-to-cover button instead
        assert "setUploadCover(idx)" in block, (
            "Upload grid must include a tap-to-cover button so touch-only "
            "users (iOS, restrictive Android) can still control the cover"
        )

    def test_cover_badge_renders_on_first_item(self):
        block = _upload_grid_block()
        assert 'x-show="idx === 0"' in block and 'Cover' in block

    def test_drag_to_reorder_hint_visible_when_multiple(self):
        block = _upload_grid_block()
        assert "drag_to_reorder" in block, (
            "Hint text must use the i18n key i18n.drag_to_reorder so it "
            "translates to IT consistently"
        )

    def test_position_indicator_per_card(self):
        block = _upload_grid_block()
        # 1/3 style indicator helps users count how many they have
        assert "(idx+1) + '/' + uploadPreviews.length" in block
