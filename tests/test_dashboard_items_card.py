"""Dashboard 'My Items' card regression guards (BL-161, April 25, 2026).

The redesigned card must keep these elements:
- Card-level rounded container with border
- Bigger thumbnail (sm:w-20 sm:h-20)
- Line-clamp-2 title (no more harsh truncate)
- Clickable category chip linking to /browse?category=
- Per-listing row with: type badge, price, status pill, pause/resume button
- Action row with View / Edit / Delete (Delete confirms before firing)
- View link opens in new tab (target=_blank rel=noopener)

If any of these go missing, the card silently regresses to the old
cramped pattern.
"""

from pathlib import Path


DASHBOARD_HTML = (
    Path(__file__).resolve().parent.parent
    / "src" / "templates" / "pages" / "dashboard.html"
).read_text()


class TestDashboardItemsCard:
    def test_card_uses_redesigned_container(self):
        # The new card uses bg-white rounded-xl with hover state -- old was
        # a flat divide-y list inside a single bg-white block.
        assert "hover:shadow-sm transition-all" in DASHBOARD_HTML, (
            "Cards must have rounded container + hover shadow -- the old "
            "flat divide-y list pattern was not robust enough"
        )

    def test_thumbnail_responsive_size(self):
        # Mobile 64px (w-16), desktop 80px (sm:w-20). Old was always 56px.
        assert "w-16 h-16 sm:w-20 sm:h-20" in DASHBOARD_HTML, (
            "Thumbnail must scale responsively (16->20) for better hierarchy"
        )

    def test_title_uses_line_clamp_not_truncate(self):
        # Old `truncate` cut titles harshly mid-word. line-clamp-2 wraps
        # to 2 lines so multi-word titles stay readable.
        assert "line-clamp-2 leading-snug" in DASHBOARD_HTML, (
            "Title must use line-clamp-2 (not truncate) so 2-line titles "
            "wrap cleanly instead of cutting off mid-word"
        )

    def test_category_chip_links_to_browse(self):
        # Old category was a non-clickable <p>. Now it's an <a> linking
        # to /browse?category=X so user can find similar items.
        assert 'href="/browse?category={{ item.category }}"' in DASHBOARD_HTML, (
            "Category must link to /browse?category=X for sibling discovery"
        )

    def test_listing_type_badges_per_type(self):
        # Each listing type gets a distinct color badge for at-a-glance
        # scanning.
        for lt in ['sell', 'rent', 'service', 'training', 'event', 'giveaway', 'auction', 'offer']:
            assert f"lt == '{lt}'" in DASHBOARD_HTML, (
                f"Listing type '{lt}' must have a colored badge variant"
            )

    def test_price_with_unit_displayed(self):
        # Price like "EUR 25.00/hour" or "EUR 100.00" (flat).
        assert "listing.currency or 'EUR'" in DASHBOARD_HTML
        assert 'listing.price_unit and listing.price_unit != \'flat\'' in DASHBOARD_HTML, (
            "Price must include /unit suffix when not flat (e.g. /hour, /day)"
        )

    def test_view_action_opens_new_tab(self):
        # Sellers want to preview their item as buyers see it without
        # losing their dashboard tab.
        assert '<a href="/items/{{ item.slug }}" target="_blank" rel="noopener"' in DASHBOARD_HTML, (
            "View action must open item detail in new tab (target=_blank "
            "rel=noopener) so seller doesn't lose dashboard context"
        )

    def test_delete_confirms_before_firing(self):
        # Delete is destructive; must confirm.
        assert "if(confirm(" in DASHBOARD_HTML and "/api/v1/items/{{ item.id }}',{method:'DELETE'}" in DASHBOARD_HTML, (
            "Delete must require confirm() before DELETE request"
        )

    def test_pause_resume_publish_handlers_intact(self):
        # The functional contract from the old card must survive: each
        # listing status has its appropriate toggle button.
        assert "JSON.stringify({status:'paused'})" in DASHBOARD_HTML, (
            "Pause action must POST status=paused"
        )
        assert "JSON.stringify({status:'active'})" in DASHBOARD_HTML, (
            "Resume + Publish actions must POST status=active"
        )

    def test_no_listing_branch_has_add_listing_cta(self):
        # When item has no listings, show a primary 'Add listing' CTA so
        # the user knows what to do next.
        assert "i18n.add_listing" in DASHBOARD_HTML, (
            "Items with no listings must show an 'Add listing' CTA"
        )

    def test_old_truncate_pattern_removed(self):
        # Catch accidental revert to the old harsh truncate.
        # (`truncate` could appear elsewhere in the template, but the
        # specific pattern from the items list must be gone.)
        assert 'class="text-sm font-semibold text-gray-900 truncate hover:text-indigo-600 transition-colors"' not in DASHBOARD_HTML, (
            "Old truncate-based title pattern detected -- the redesigned "
            "card uses line-clamp-2 instead"
        )
