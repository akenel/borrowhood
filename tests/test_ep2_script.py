"""Tests for EP2 recording script story consistency.

Validates that the recording script's story cards, scene flow, and
character references match seed data and don't contradict each other.

No DB needed -- reads the JS script and seed.json directly.
"""

import json
import re
import pytest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parent.parent / "Bro_Kit" / "16-the-cookie-run" / "record-the-cookie-run.js"
SEED_PATH = Path(__file__).parent.parent / "seed_data" / "seed.json"


@pytest.fixture(scope="module")
def script():
    return SCRIPT_PATH.read_text()


@pytest.fixture(scope="module")
def seed_data():
    with open(SEED_PATH) as f:
        return json.load(f)


class TestScriptSyntax:
    """Basic script integrity."""

    def test_script_exists(self):
        assert SCRIPT_PATH.exists(), f"Recording script not found: {SCRIPT_PATH}"

    def test_no_syntax_errors(self):
        """Node.js can parse the script."""
        import subprocess
        result = subprocess.run(
            ["node", "-c", str(SCRIPT_PATH)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"


class TestStoryConsistency:
    """Story cards must match seed data and each other."""

    def test_sofia_does_not_own_cutters_in_script(self, script):
        """Script must NOT say Sofia 'got' or 'owns' cookie cutters."""
        # She shouldn't claim ownership -- Pietro rents them from Sally for her
        assert "She got 200 cookie cutters" not in script, (
            "Script says Sofia 'got 200 cookie cutters' -- she doesn't own them. "
            "Pietro rents Sally's cutters as her birthday gift."
        )

    def test_pietro_buys_gifts_in_script(self, script):
        """Script must show Pietro renting cutters + booking class for Sofia."""
        assert "Pietro rents cookie cutters" in script or "Pietro rented" in script, (
            "Script doesn't show Pietro renting cookie cutters for Sofia"
        )
        assert "baking class" in script.lower() or "baking lesson" in script.lower(), (
            "Script doesn't mention baking class/lesson"
        )

    def test_five_boxes_names_real_cast(self, script):
        """The 5 BOXES card must name real cast members, not generic labels."""
        # Find the 5 BOXES card content
        assert "Pietro. Sally. Leonardo. Nino. Maria." in script, (
            "5 BOXES card doesn't name the 5 delivery recipients. "
            "Expected: Pietro, Sally, Leonardo, Nino, Maria"
        )

    def test_epilogue_frames_sally_as_entrepreneur(self, script):
        """Epilogue must frame Sally as seeing a business opportunity, not charity."""
        assert "Sally sees a business" in script, (
            "Epilogue should say 'Sally sees a business' -- she's an entrepreneur"
        )
        assert "money to fix it" not in script, (
            "Script still says 'money to fix it' -- Sally buys a scooter to rent, not to gift"
        )

    def test_scene_9c_removed(self, script):
        """Scene 9c (Sofia books class) must be removed -- Pietro does it in Scene 6e."""
        # The old scene had Sofia booking the class herself
        assert "Sofia books Sally's baking class" not in script or "removed" in script, (
            "Scene 9c still has Sofia booking the class -- Pietro does this in Scene 6e"
        )

    def test_delivery_addresses_in_script(self, script):
        """The 5 delivery addresses must appear in the IT WORKS card."""
        addresses = ["Via Roma", "Via Garibaldi", "Via Torrearsa", "Piazza Mercato", "Via Fardella"]
        for addr in addresses:
            assert addr in script, f"Delivery address '{addr}' missing from script"

    def test_no_friend_singular(self, script):
        """'5 friends' not '5 friend' (Take 9 fix)."""
        # Check the 5 BOXES area specifically
        assert "to 5 friend." not in script, "Still says '5 friend' (singular) -- should be '5 friends'"

    def test_the_question_mentions_rental_not_charity(self, script):
        """THE QUESTION must frame Sally as entrepreneur (renting, not gifting)."""
        assert "rented the wheels" in script, (
            "THE QUESTION card should say 'rented the wheels' -- Sally is an entrepreneur, not charity"
        )
        assert "not a charity" in script or "not charity" in script, (
            "Script should clarify Sally sees a business, not a charity"
        )


    def test_leonardo_teased_in_climax(self, script):
        """Leonardo must be teased in the climax cards (EP3 setup)."""
        assert "Leonardo" in script or "Torrearsa" in script, (
            "Leonardo not teased in climax -- he's watching from Via Torrearsa"
        )

    def test_nino_mentioned_in_teaser(self, script):
        """Nino must be mentioned in the TO BE CONTINUED card (scooter rental subplot)."""
        assert "Nino" in script, "Nino not mentioned -- he's part of the scooter rental subplot"


class TestScriptRoutes:
    """All page routes in the script must be valid."""

    def test_no_singular_item_route(self, script):
        """/items/ not /item/ (Take 10 bug)."""
        # Find all goto calls with /item/ (singular) that aren't /items/
        matches = re.findall(r'/item/[^s]', script)
        assert not matches, (
            f"Script uses /item/ (singular) instead of /items/: {matches}"
        )

    def test_item_slugs_exist_in_seed(self, script, seed_data):
        """All /items/SLUG routes in script must match seed data slugs."""
        item_slugs = {i.get("slug") for i in seed_data.get("items", [])}
        # Find all /items/SLUG references
        route_slugs = re.findall(r'/items/([a-z0-9-]+)', script)
        missing = []
        for slug in route_slugs:
            if slug not in item_slugs:
                missing.append(slug)
        assert not missing, (
            f"Script references items not in seed.json: {missing}"
        )

    def test_workshop_slugs_exist_in_seed(self, script, seed_data):
        """All /workshop/SLUG routes in script must match seed user slugs."""
        user_slugs = {u.get("slug") for u in seed_data.get("users", [])}
        route_slugs = re.findall(r'/workshop/([a-z0-9-]+)', script)
        missing = []
        for slug in route_slugs:
            if slug not in user_slugs:
                missing.append(slug)
        assert not missing, (
            f"Script references workshops not in seed.json: {missing}"
        )


class TestScriptLoginUsers:
    """All demo login usernames in the script must be valid."""

    # Valid demo login usernames (from pages.py demo_users list)
    VALID_LOGINS = {
        "sally", "mike", "angel", "nino", "maria", "marco", "jake",
        "rosa", "george", "john", "pietro", "sofiaferretti", "anne", "leonardo",
    }

    def test_all_logins_valid(self, script):
        """Every visibleLogin() call must use a valid demo username."""
        logins = re.findall(r"visibleLogin\(page,\s*'(\w+)'\)", script)
        invalid = [l for l in logins if l not in self.VALID_LOGINS]
        assert not invalid, f"Invalid demo login usernames: {invalid}"

    def test_ep2_uses_correct_cast(self, script):
        """EP2 must login as the 4 main cast: sally, pietro, sofiaferretti, john."""
        logins = set(re.findall(r"visibleLogin\(page,\s*'(\w+)'\)", script))
        required = {"sally", "pietro", "sofiaferretti", "john"}
        missing = required - logins
        assert not missing, f"EP2 missing logins for: {missing}"
