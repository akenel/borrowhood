"""Duplicate listing flow regression guards (BL-150, April 26, 2026).

After someone sells an item, repeat sellers (Sally's cookies, Angel's
postcards) need a one-tap relist. The flow:

  1. Dashboard My Items card has a "Duplicate" action -> /list?duplicate_from=ID
  2. /list route detects duplicate_from, verifies ownership, pulls source data
  3. list_item.html renders the form pre-filled with name + ' (copy)',
     description, story, category, attributes, listing types, pricing
  4. Submit creates a brand new item (not editing the source).

Most of the contract is template-side. These tests lock it in so an
unrelated refactor can't silently break the relist path.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LIST_ITEM_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "list_item.html").read_text()
DASHBOARD_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "dashboard.html").read_text()
ITEM_PY = (REPO_ROOT / "src" / "routers" / "pages" / "item.py").read_text()


class TestDashboardDuplicateButton:
    """The dashboard My Items card must expose a Duplicate action that links
    to the list form with duplicate_from set to the item's UUID."""

    def test_dashboard_has_duplicate_link(self):
        assert '/list?duplicate_from={{ item.id }}' in DASHBOARD_HTML, (
            "Dashboard My Items card must link to /list?duplicate_from={item.id} "
            "so users can relist after a sale"
        )

    def test_duplicate_link_sits_between_edit_and_delete(self):
        edit_idx = DASHBOARD_HTML.find('/items/{{ item.slug }}/edit')
        dup_idx = DASHBOARD_HTML.find('/list?duplicate_from={{ item.id }}')
        del_idx = DASHBOARD_HTML.find('confirm_delete_item')
        assert edit_idx < dup_idx < del_idx, (
            "Duplicate action should be between Edit and Delete in the card "
            "footer for natural left-to-right action ordering"
        )


class TestListItemDuplicateMode:
    """The /list page must render a duplicate-mode branch when the route
    passes duplicate_item -- pre-fills _editForm without setting _editData
    so editMode stays false and the form POSTs (creates) instead of PATCHes."""

    def test_template_has_duplicate_branch(self):
        assert "{% elif duplicate_item %}" in LIST_ITEM_HTML, (
            "list_item.html needs a duplicate-mode Jinja branch parallel "
            "to the edit-mode branch"
        )

    def test_duplicate_appends_copy_suffix_to_name(self):
        # Source name + ' (copy)' so the user instantly sees this is a fresh listing
        assert "duplicate_item.name + ' (copy)'" in LIST_ITEM_HTML, (
            "Duplicate-mode form name must append ' (copy)' so the user "
            "knows this is a new listing, not the original"
        )

    def test_duplicate_does_not_set_editData(self):
        # Inside the elif duplicate_item block, _editData must be set to null
        # so editMode stays false and the form creates instead of patches
        elif_block_start = LIST_ITEM_HTML.find("{% elif duplicate_item %}")
        elif_block_end = LIST_ITEM_HTML.find("{% else %}", elif_block_start)
        elif_block = LIST_ITEM_HTML[elif_block_start:elif_block_end]
        assert "window._editData = null" in elif_block, (
            "Duplicate mode must set window._editData = null so editMode "
            "stays false (the form must POST a new item, not PATCH)"
        )

    def test_duplicate_sets_selected_types_global(self):
        elif_block_start = LIST_ITEM_HTML.find("{% elif duplicate_item %}")
        elif_block_end = LIST_ITEM_HTML.find("{% else %}", elif_block_start)
        elif_block = LIST_ITEM_HTML[elif_block_start:elif_block_end]
        assert "window._duplicateSelectedTypes" in elif_block, (
            "Duplicate mode must populate window._duplicateSelectedTypes "
            "so the source's listing types pre-select"
        )

    def test_duplicate_sets_listing_prices_global(self):
        elif_block_start = LIST_ITEM_HTML.find("{% elif duplicate_item %}")
        elif_block_end = LIST_ITEM_HTML.find("{% else %}", elif_block_start)
        elif_block = LIST_ITEM_HTML[elif_block_start:elif_block_end]
        assert "window._duplicateListingPrices" in elif_block, (
            "Duplicate mode must populate window._duplicateListingPrices "
            "so the source's pricing pre-fills"
        )

    def test_alpine_init_honors_duplicate_globals(self):
        # selectedTypes initializer must check the duplicate global first
        assert "window._duplicateSelectedTypes && window._duplicateSelectedTypes.length" in LIST_ITEM_HTML, (
            "selectedTypes initial value must read from "
            "window._duplicateSelectedTypes when set"
        )
        # init() must swap listingPrices when the duplicate global is set
        assert "if (window._duplicateListingPrices)" in LIST_ITEM_HTML, (
            "Alpine init() must replace listingPrices with "
            "window._duplicateListingPrices when set"
        )
        # itemAttributes must also honor the duplicate global
        assert "window._duplicateAttributes" in LIST_ITEM_HTML, (
            "itemAttributes initializer must fall back to "
            "window._duplicateAttributes when no _editData"
        )

    def test_duplicate_hint_banner_present(self):
        # The hint must mention the source item's name so the user knows what
        # they're duplicating from, and the copy must explain "add fresh photos"
        assert "duplicate_item.name" in LIST_ITEM_HTML
        assert "Duplicating:" in LIST_ITEM_HTML or "Stai duplicando:" in LIST_ITEM_HTML, (
            "The duplicate-mode hint banner must include the source name "
            "so the user can confirm they picked the right item"
        )


class TestListRouteDuplicateFromQueryParam:
    """The /list backend route must accept ?duplicate_from=UUID, verify
    ownership, and pass duplicate_item + JSON globals to the template."""

    def test_route_reads_duplicate_from_param(self):
        assert "duplicate_from" in ITEM_PY, (
            "/list route must read the duplicate_from query param"
        )

    def test_route_verifies_ownership(self):
        # Owner check prevents users from duplicating other people's items
        # (which would leak the source's description, attributes, etc.)
        assert "source.owner_id == user.id" in ITEM_PY, (
            "Duplicate route must verify the requesting user owns the "
            "source item -- otherwise users could duplicate strangers' items"
        )

    def test_route_passes_listing_types_json_to_template(self):
        assert "duplicate_listing_types_json" in ITEM_PY
        assert "duplicate_listing_prices_json" in ITEM_PY, (
            "Both listing types and per-type pricing must be JSON-serialized "
            "for the template to inject as window._duplicate* globals"
        )
