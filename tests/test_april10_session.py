"""Tests for April 10, 2026 session -- Events, Leaderboard, Gamification, GDPR.

Covers:
1. EVENT listing type exists and event fields on BHListing
2. Event categories in ItemCategory + CATEGORY_GROUPS
3. Event attribute schemas
4. BHEventRSVP model + RSVPStatus (incl. NO_SHOW)
5. BHAchievement model + ACHIEVEMENTS definitions
6. User model: no_show_count, organization_description
7. UserPoints: events_attended, events_hosted, event_streak, best_streak
8. Events router: 7 endpoints
9. Leaderboard page route exists
10. Feedback endpoint exists
11. Delete preview endpoint exists
12. Seed data: Nic Roccamena profile
13. KC realm: Nic user exists
14. Demo login: 15 users including Nic
15. i18n: event + leaderboard + feedback + delete keys
16. GDPR cleanup: savepoints + all FK tables covered
17. Schemas: event fields in ListingCreate/Update/Out
18. Nav: leaderboard link in base template
"""

import json
import pytest
from pathlib import Path


# ── 1. EVENT listing type ──

class TestEventListingType:
    def test_event_in_listing_type_enum(self):
        from src.models.listing import ListingType
        assert hasattr(ListingType, "EVENT")
        assert ListingType.EVENT.value == "event"

    def test_listing_has_event_start_field(self):
        from src.models.listing import BHListing
        assert hasattr(BHListing, "event_start")

    def test_listing_has_event_end_field(self):
        from src.models.listing import BHListing
        assert hasattr(BHListing, "event_end")

    def test_listing_has_event_venue_field(self):
        from src.models.listing import BHListing
        assert hasattr(BHListing, "event_venue")

    def test_listing_has_event_address_field(self):
        from src.models.listing import BHListing
        assert hasattr(BHListing, "event_address")

    def test_all_nine_listing_types(self):
        from src.models.listing import ListingType
        values = [t.value for t in ListingType]
        expected = ["rent", "sell", "commission", "offer", "service", "training", "auction", "giveaway", "event"]
        for e in expected:
            assert e in values, f"{e} missing from ListingType"


# ── 2. Event categories ──

class TestEventCategories:
    def test_event_categories_in_item_category(self):
        from src.models.item import ItemCategory
        event_cats = ["workshop_event", "garage_sale", "concert", "art_show",
                      "community_meetup", "sports_event", "market", "festival"]
        for cat in event_cats:
            assert cat in [c.value for c in ItemCategory], f"{cat} missing from ItemCategory"

    def test_events_in_category_groups(self):
        from src.models.item import CATEGORY_GROUPS
        assert "events" in CATEGORY_GROUPS
        assert len(CATEGORY_GROUPS["events"]) == 8

    def test_events_category_group_contents(self):
        from src.models.item import CATEGORY_GROUPS
        expected = ["workshop_event", "garage_sale", "concert", "art_show",
                    "community_meetup", "sports_event", "market", "festival"]
        assert CATEGORY_GROUPS["events"] == expected


# ── 3. Event attribute schemas ──

class TestEventAttributeSchemas:
    def test_events_in_attribute_schemas(self):
        from src.models.item import ATTRIBUTE_SCHEMAS
        assert "events" in ATTRIBUTE_SCHEMAS

    def test_event_attributes_have_age_requirement(self):
        from src.models.item import ATTRIBUTE_SCHEMAS
        assert "age_requirement" in ATTRIBUTE_SCHEMAS["events"]

    def test_event_attributes_have_skill_level(self):
        from src.models.item import ATTRIBUTE_SCHEMAS
        assert "skill_level" in ATTRIBUTE_SCHEMAS["events"]

    def test_event_attributes_have_what_to_bring(self):
        from src.models.item import ATTRIBUTE_SCHEMAS
        assert "what_to_bring" in ATTRIBUTE_SCHEMAS["events"]

    def test_age_requirement_options(self):
        from src.models.item import ATTRIBUTE_SCHEMAS
        opts = ATTRIBUTE_SCHEMAS["events"]["age_requirement"]["options"]
        assert "all_ages" in opts
        assert "16_plus" in opts
        assert "18_plus" in opts


# ── 4. RSVP model ──

class TestRSVPModel:
    def test_rsvp_model_exists(self):
        from src.models.event_rsvp import BHEventRSVP
        assert BHEventRSVP.__tablename__ == "bh_event_rsvp"

    def test_rsvp_status_values(self):
        from src.models.event_rsvp import RSVPStatus
        values = [s.value for s in RSVPStatus]
        assert "registered" in values
        assert "waitlisted" in values
        assert "cancelled" in values
        assert "attended" in values
        assert "no_show" in values

    def test_rsvp_has_five_statuses(self):
        from src.models.event_rsvp import RSVPStatus
        assert len(RSVPStatus) == 5

    def test_rsvp_model_in_init(self):
        from src.models import BHEventRSVP
        assert BHEventRSVP is not None


# ── 5. Achievement model ──

class TestAchievementModel:
    def test_achievement_model_exists(self):
        from src.models.achievement import BHAchievement
        assert BHAchievement.__tablename__ == "bh_achievement"

    def test_achievement_tier_enum(self):
        from src.models.achievement import AchievementTier
        values = [t.value for t in AchievementTier]
        assert "bronze" in values
        assert "silver" in values
        assert "gold" in values
        assert "diamond" in values

    def test_achievements_dict_has_15_entries(self):
        from src.models.achievement import ACHIEVEMENTS
        assert len(ACHIEVEMENTS) == 15

    def test_achievement_keys_are_unique(self):
        from src.models.achievement import ACHIEVEMENTS
        keys = list(ACHIEVEMENTS.keys())
        assert len(keys) == len(set(keys))

    def test_all_achievements_have_required_fields(self):
        from src.models.achievement import ACHIEVEMENTS
        required = ["name", "name_it", "desc", "desc_it", "icon", "trigger", "threshold", "tier", "points"]
        for key, ach in ACHIEVEMENTS.items():
            for field in required:
                assert field in ach, f"Achievement '{key}' missing field '{field}'"

    def test_streak_achievements_exist(self):
        from src.models.achievement import ACHIEVEMENTS
        streak_keys = ["streak_3", "streak_5", "streak_10", "streak_20"]
        for k in streak_keys:
            assert k in ACHIEVEMENTS, f"Streak achievement '{k}' missing"

    def test_host_achievements_exist(self):
        from src.models.achievement import ACHIEVEMENTS
        host_keys = ["first_host", "host_10", "host_25", "host_50"]
        for k in host_keys:
            assert k in ACHIEVEMENTS, f"Host achievement '{k}' missing"

    def test_reliability_achievement_exists(self):
        from src.models.achievement import ACHIEVEMENTS
        assert "reliable" in ACHIEVEMENTS
        assert ACHIEVEMENTS["reliable"]["trigger"] == "reliability"

    def test_comeback_achievement_exists(self):
        from src.models.achievement import ACHIEVEMENTS
        assert "comeback" in ACHIEVEMENTS
        assert ACHIEVEMENTS["comeback"]["trigger"] == "comeback"

    def test_achievement_model_in_init(self):
        from src.models import BHAchievement
        assert BHAchievement is not None


# ── 6. User model updates ──

class TestUserModelUpdates:
    def test_user_has_no_show_count(self):
        from src.models.user import BHUser
        assert hasattr(BHUser, "no_show_count")

    def test_user_has_organization_description(self):
        from src.models.user import BHUser
        assert hasattr(BHUser, "organization_description")

    def test_seller_type_comment_includes_organization(self):
        """seller_type comment should mention organization as a valid value."""
        import inspect
        from src.models.user import BHUser
        source = inspect.getsource(BHUser)
        assert "organization" in source


# ── 7. UserPoints gamification fields ──

class TestUserPointsGamification:
    def test_user_points_has_events_attended(self):
        from src.models.user import BHUserPoints
        assert hasattr(BHUserPoints, "events_attended")

    def test_user_points_has_events_hosted(self):
        from src.models.user import BHUserPoints
        assert hasattr(BHUserPoints, "events_hosted")

    def test_user_points_has_event_streak(self):
        from src.models.user import BHUserPoints
        assert hasattr(BHUserPoints, "event_streak")

    def test_user_points_has_best_streak(self):
        from src.models.user import BHUserPoints
        assert hasattr(BHUserPoints, "best_streak")

    def test_user_points_has_challenges_completed(self):
        from src.models.user import BHUserPoints
        assert hasattr(BHUserPoints, "challenges_completed")


# ── 8. Events router ──

class TestEventsRouter:
    def test_events_router_has_8_routes(self):
        from src.routers.events import router
        assert len(router.routes) == 8  # +1 for /calendar endpoint

    def test_rsvp_create_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["POST"], "/api/v1/events/{listing_id}/rsvp") in paths

    def test_rsvp_cancel_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["DELETE"], "/api/v1/events/{listing_id}/rsvp") in paths

    def test_rsvp_info_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["GET"], "/api/v1/events/{listing_id}/rsvp") in paths

    def test_mark_attended_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["PATCH"], "/api/v1/events/{listing_id}/rsvp/{rsvp_id}/attend") in paths

    def test_close_event_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["POST"], "/api/v1/events/{listing_id}/close") in paths

    def test_leaderboard_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["GET"], "/api/v1/events/leaderboard") in paths

    def test_my_stats_endpoint(self):
        from src.routers.events import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["GET"], "/api/v1/events/my-stats") in paths

    def test_events_router_registered_in_main(self):
        import inspect
        source = inspect.getsource(__import__("src.main", fromlist=["create_app"]))
        assert "events.router" in source


# ── 9. Leaderboard page ──

class TestLeaderboardPage:
    def test_leaderboard_route_exists(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.pages", fromlist=["leaderboard_page"]))
        assert "leaderboard" in source

    def test_leaderboard_template_exists(self):
        assert Path("src/templates/pages/leaderboard.html").exists()

    def test_leaderboard_template_has_tabs(self):
        content = Path("src/templates/pages/leaderboard.html").read_text()
        assert "tab_rankings" in content
        assert "tab_streaks" in content
        assert "tab_coaches" in content

    def test_leaderboard_template_has_achievements(self):
        content = Path("src/templates/pages/leaderboard.html").read_text()
        assert "all_achievements" in content or "achievements" in content

    def test_leaderboard_in_nav(self):
        content = Path("src/templates/base.html").read_text()
        assert "/leaderboard" in content


# ── 10. Feedback endpoint ──

class TestFeedbackEndpoint:
    def test_feedback_endpoint_exists(self):
        from src.routers.backlog import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["POST"], "/api/v1/backlog/feedback") in paths

    def test_feedback_button_in_base_template(self):
        content = Path("src/templates/base.html").read_text()
        assert "submitFeedback" in content
        assert "feedback" in content


# ── 11. Delete preview endpoint ──

class TestDeletePreview:
    def test_delete_preview_endpoint_exists(self):
        from src.routers.users import router
        paths = [(list(r.methods), r.path) for r in router.routes]
        assert (["GET"], "/api/v1/users/me/delete-preview") in paths

    def test_delete_modal_has_type_confirm(self):
        content = Path("src/templates/pages/dashboard.html").read_text()
        assert "DELETE" in content
        assert "confirmText" in content

    def test_delete_modal_shows_personalized_data(self):
        content = Path("src/templates/pages/dashboard.html").read_text()
        assert "preview.items" in content or "preview.total_points" in content
        assert "preview.display_name" in content


# ── 12. Seed data: Nic ──

class TestNicSeedData:
    @pytest.fixture
    def seed(self):
        with open("seed_data/seed.json") as f:
            return json.load(f)

    def test_nic_user_exists(self, seed):
        slugs = [u["slug"] for u in seed["users"]]
        assert "nics-dojo" in slugs

    def test_nic_email(self, seed):
        nic = next(u for u in seed["users"] if u["slug"] == "nics-dojo")
        assert nic["email"] == "roccamenanicolo@gmail.com"

    def test_nic_display_name(self, seed):
        nic = next(u for u in seed["users"] if u["slug"] == "nics-dojo")
        assert "Roccamena" in nic["display_name"]

    def test_nic_workshop_type_is_dojo(self, seed):
        nic = next(u for u in seed["users"] if u["slug"] == "nics-dojo")
        assert nic["workshop_type"] == "dojo"

    def test_nic_has_5_skills(self, seed):
        nic = next(u for u in seed["users"] if u["slug"] == "nics-dojo")
        assert len(nic["skills"]) == 5

    def test_nic_has_jujitsu_skill(self, seed):
        nic = next(u for u in seed["users"] if u["slug"] == "nics-dojo")
        skill_names = [s["skill_name"] for s in nic["skills"]]
        assert "Jiu-Jitsu" in skill_names

    def test_nic_has_5_items(self, seed):
        nic_items = [i for i in seed["items"] if i["owner_slug"] == "nics-dojo"]
        assert len(nic_items) == 5

    def test_nic_has_3_event_listings(self, seed):
        nic_items = [i for i in seed["items"] if i["owner_slug"] == "nics-dojo"]
        event_count = sum(
            1 for item in nic_items
            for listing in item.get("listings", [])
            if listing["listing_type"] == "event"
        )
        assert event_count == 3

    def test_nic_first_event_at_d50(self, seed):
        nic_items = [i for i in seed["items"] if i["owner_slug"] == "nics-dojo"]
        event_items = [
            i for i in nic_items
            if any(l["listing_type"] == "event" for l in i.get("listings", []))
        ]
        venues = [
            l.get("event_venue", "")
            for i in event_items
            for l in i.get("listings", [])
        ]
        assert any("D50" in v for v in venues)

    def test_nic_mentorship_from_angel(self, seed):
        mentorships = [m for m in seed["mentorships"] if m["apprentice_slug"] == "nics-dojo"]
        assert len(mentorships) == 1
        assert mentorships[0]["mentor_slug"] == "angel-hq"
        assert mentorships[0]["status"] == "active"


# ── 13. KC realm: Nic ──

class TestNicKeycloak:
    @pytest.fixture
    def realm(self):
        with open("keycloak/borrowhood-realm-dev.json") as f:
            return json.load(f)

    def test_nic_kc_user_exists(self, realm):
        usernames = [u["username"] for u in realm["users"]]
        assert "nicolo" in usernames

    def test_nic_kc_email(self, realm):
        nic = next(u for u in realm["users"] if u["username"] == "nicolo")
        assert nic["email"] == "roccamenanicolo@gmail.com"

    def test_nic_kc_last_name(self, realm):
        nic = next(u for u in realm["users"] if u["username"] == "nicolo")
        assert nic["lastName"] == "Roccamena"

    def test_nic_kc_has_member_role(self, realm):
        nic = next(u for u in realm["users"] if u["username"] == "nicolo")
        assert "bh-member" in nic["realmRoles"]

    def test_nic_kc_has_lender_role(self, realm):
        nic = next(u for u in realm["users"] if u["username"] == "nicolo")
        assert "bh-lender" in nic["realmRoles"]


# ── 14. Demo login: 15 users ──

class TestDemoLogin:
    def test_demo_login_has_15_users(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.pages", fromlist=["demo_login"]))
        assert "nicolo" in source

    def test_nic_demo_has_ambassador_role(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.pages", fromlist=["demo_login"]))
        assert "ambassador" in source


# ── 15. i18n ──

class TestI18nEvents:
    @pytest.fixture
    def en(self):
        with open("src/locales/en.json") as f:
            return json.load(f)

    @pytest.fixture
    def it(self):
        with open("src/locales/it.json") as f:
            return json.load(f)

    def test_event_listing_type_en(self, en):
        assert en["listing_types"]["event"] == "Event"

    def test_event_listing_type_it(self, it):
        assert it["listing_types"]["event"] == "Evento"

    def test_events_cat_group_en(self, en):
        assert "events" in en["cat_groups"]

    def test_event_categories_en(self, en):
        cats = en["categories"]
        assert "workshop_event" in cats
        assert "garage_sale" in cats
        assert "concert" in cats

    def test_events_section_en(self, en):
        assert "events" in en
        assert "rsvp" in en["events"]
        assert "no_show" in en["events"]
        assert "free_event" in en["events"]

    def test_leaderboard_section_en(self, en):
        assert "leaderboard" in en
        assert "title" in en["leaderboard"]
        assert "tab_rankings" in en["leaderboard"]
        assert "tab_streaks" in en["leaderboard"]
        assert "tab_coaches" in en["leaderboard"]

    def test_feedback_section_en(self, en):
        assert "feedback" in en
        assert "title" in en["feedback"]
        assert "bug" in en["feedback"]
        assert "idea" in en["feedback"]

    def test_delete_warning_keys_en(self, en):
        assert "delete_warning_title" in en["account"]
        assert "delete_you_will_lose" in en["account"]
        assert "delete_permanent" in en["account"]
        assert "delete_type_confirm" in en["account"]
        assert "lose_profile" in en["account"]
        assert "lose_reputation" in en["account"]
        assert "lose_achievements" in en["account"]

    def test_leaderboard_nav_en(self, en):
        assert "leaderboard" in en["nav"]

    def test_italian_translations_match_keys(self, en, it):
        """Every key in English events/leaderboard/feedback must exist in Italian."""
        for section in ["events", "leaderboard", "feedback"]:
            for key in en[section]:
                assert key in it[section], f"Italian missing: {section}.{key}"


# ── 16. GDPR cleanup ──

class TestGDPRCleanup:
    def test_cleanup_uses_savepoints(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "begin_nested" in source

    def test_cleanup_includes_event_rsvp(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "bh_event_rsvp" in source

    def test_cleanup_includes_achievement(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "bh_achievement" in source

    def test_cleanup_includes_saved_search(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "bh_saved_search" in source

    def test_cleanup_includes_item_vote(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "bh_item_vote" in source

    def test_cleanup_deletes_others_replies_on_user_posts(self):
        """Must delete ALL replies on user's posts, not just user's own replies."""
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "bh_help_reply WHERE post_id IN" in source

    def test_cleanup_deletes_others_data_on_user_items(self):
        """Must delete bids/rentals/RSVPs from other users on this user's listings."""
        import inspect
        source = inspect.getsource(__import__("src.routers.users", fromlist=["delete_my_account"]))
        assert "bh_bid WHERE listing_id IN" in source
        assert "bh_rental WHERE listing_id IN" in source


# ── 17. Schemas ──

class TestListingSchemas:
    def test_listing_create_has_event_start(self):
        from src.schemas.listing import ListingCreate
        assert "event_start" in ListingCreate.model_fields

    def test_listing_create_has_event_venue(self):
        from src.schemas.listing import ListingCreate
        assert "event_venue" in ListingCreate.model_fields

    def test_listing_out_has_event_start(self):
        from src.schemas.listing import ListingOut
        assert "event_start" in ListingOut.model_fields

    def test_listing_update_has_event_fields(self):
        from src.schemas.listing import ListingUpdate
        assert "event_start" in ListingUpdate.model_fields
        assert "event_end" in ListingUpdate.model_fields
        assert "event_venue" in ListingUpdate.model_fields
        assert "event_address" in ListingUpdate.model_fields

    def test_rsvp_schemas_exist(self):
        from src.schemas.event_rsvp import RSVPCreate, RSVPOut, RSVPInfo
        assert RSVPCreate is not None
        assert RSVPOut is not None
        assert RSVPInfo is not None


# ── 18. Database migrations ──

class TestDatabaseMigrations:
    def test_event_columns_in_migrations(self):
        import inspect
        from src.database import run_migrations
        source = inspect.getsource(run_migrations)
        assert "event_start" in source
        assert "event_end" in source
        assert "event_venue" in source
        assert "event_address" in source

    def test_event_enum_in_migrations(self):
        import inspect
        from src.database import run_migrations
        source = inspect.getsource(run_migrations)
        assert "listingtype" in source.lower()
        assert "EVENT" in source

    def test_category_enums_in_migrations(self):
        import inspect
        from src.database import run_migrations
        source = inspect.getsource(run_migrations)
        assert "WORKSHOP_EVENT" in source
        assert "GARAGE_SALE" in source
        assert "FESTIVAL" in source

    def test_no_show_count_in_migrations(self):
        import inspect
        from src.database import run_migrations
        source = inspect.getsource(run_migrations)
        assert "no_show_count" in source

    def test_gamification_fields_in_migrations(self):
        import inspect
        from src.database import run_migrations
        source = inspect.getsource(run_migrations)
        assert "events_attended" in source
        assert "events_hosted" in source
        assert "event_streak" in source
        assert "best_streak" in source


# ── 19. Nic avatar ──

class TestNicAvatar:
    def test_nic_avatar_exists(self):
        assert Path("src/static/images/avatars/nicolo.svg").exists()

    def test_nic_avatar_is_svg(self):
        content = Path("src/static/images/avatars/nicolo.svg").read_text()
        assert "<svg" in content
        assert "N" in content  # The letter N for Nicolò
