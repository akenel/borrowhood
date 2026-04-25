"""Per-item analytics on dashboard cards (BL-162, April 25, 2026).

Backend: account.py builds item_stats dict {item_id: {views, favorites,
conversations}} from 3 batched aggregate queries.

Template: each card renders a metric strip when the item has any activity.
- Views: last 30 days (BHItemView.created_at >= now - 30d)
- Favorites: lifetime, soft-delete aware
- Conversations: distinct senders who messaged about any of the item's
  listings, excluding the owner's own messages

These tests guard the data plumbing -- a refactor that drops `item_stats`
from context or removes the metric strip would silently regress the
seller's at-a-glance traction view.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "dashboard.html").read_text()
ACCOUNT_PY = (REPO_ROOT / "src" / "routers" / "pages" / "account.py").read_text()


class TestAnalyticsBackend:
    def test_item_stats_passed_to_template(self):
        assert "item_stats=item_stats" in ACCOUNT_PY, (
            "Dashboard route must pass item_stats dict in template context"
        )

    def test_views_query_uses_30day_window(self):
        # 30-day window is the contract -- showing lifetime views would
        # be misleading for items listed years ago.
        assert "thirty_days_ago" in ACCOUNT_PY
        assert "timedelta(days=30)" in ACCOUNT_PY, (
            "Views must be limited to last 30 days, not lifetime"
        )
        assert "BHItemView.created_at >= thirty_days_ago" in ACCOUNT_PY

    def test_views_query_grouped_by_item_id(self):
        # Single batched query, NOT N+1 per-card subqueries
        assert "func.count(BHItemView.id))" in ACCOUNT_PY
        assert ".group_by(BHItemView.item_id)" in ACCOUNT_PY, (
            "Views query must be batched + grouped by item_id (one query "
            "for all items, not N queries)"
        )

    def test_favorites_query_respects_soft_delete(self):
        # BHItemFavorite has soft-delete via deleted_at; a removed favorite
        # should not count.
        assert "BHItemFavorite.deleted_at.is_(None)" in ACCOUNT_PY, (
            "Favorites query must exclude soft-deleted rows (deleted_at IS NULL)"
        )

    def test_conversations_excludes_owner_own_messages(self):
        # Don't count the owner's own outgoing messages as 'interested users'
        assert "BHMessage.sender_id != db_user.id" in ACCOUNT_PY, (
            "Conversations query must exclude the owner's own messages -- "
            "we count INTERESTED parties, not the seller's outgoing chatter"
        )

    def test_conversations_counts_distinct_senders(self):
        # 5 messages from same buyer = 1 interested party, not 5
        assert "func.count(func.distinct(BHMessage.sender_id))" in ACCOUNT_PY, (
            "Conversations must use COUNT(DISTINCT sender_id) so multiple "
            "messages from one buyer = 1 interested party"
        )

    def test_conversations_joins_listing_to_get_item_id(self):
        # BHMessage has listing_id but not item_id; need a join
        assert ".join(BHMessage, BHMessage.listing_id == BHListing.id)" in ACCOUNT_PY


class TestAnalyticsTemplate:
    def test_metric_strip_only_when_activity(self):
        # Don't show 0/0/0 strip on every fresh item -- only when there's
        # something worth surfacing.
        assert "if _stats.views or _stats.favorites or _stats.conversations" in DASHBOARD_HTML, (
            "Metric strip must only render when item has at least one "
            "view/fav/conversation (avoid noise on fresh listings)"
        )

    def test_metric_strip_reads_item_stats_safely(self):
        # If item_stats is missing or item not in dict, default to zeros
        assert "item_stats.get(item.id|string, {'views': 0, 'favorites': 0, 'conversations': 0})" in DASHBOARD_HTML, (
            "Template must default to zeros if item_stats is missing the "
            "item -- prevents UndefinedError in edge cases"
        )

    def test_each_metric_has_icon_and_count(self):
        # All three metrics rendered with their counts
        assert "_stats.views" in DASHBOARD_HTML
        assert "_stats.favorites" in DASHBOARD_HTML
        assert "_stats.conversations" in DASHBOARD_HTML

    def test_italian_translations_present(self):
        # Mike or Pietro switching to IT should see Italian labels, not
        # English fallback
        for it_label in ['viste', 'interessati', 'Visualizzazioni', 'Preferiti']:
            assert it_label in DASHBOARD_HTML, (
                f"Italian label '{it_label}' missing from metric strip"
            )
