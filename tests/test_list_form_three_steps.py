"""Listing form 3-step Bruce Lee flow regression guards (BL-174, April 27, 2026).

Angel reproduced 'pricing always blank in draft mode' on the chainsaw edit
page and noticed two step containers visible at once -- the multi-step
gating felt broken AND the form's density made it easy to miss optional
fields. The fix: three crystal-clear steps where each is mutually
exclusive and the final commitment (price + publish) is the last step.

Step 1 = What is it (name / photos / category)
Step 2 = How does it work (delivery / notes / return policy / availability)
Step 3 = How much (listing types + pricing) -- has Save Draft + Publish

These tests pin the contract so a future refactor can't silently
re-introduce the 'all steps visible' bug or move Submit off the final step.
"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LIST_HTML = (REPO_ROOT / "src" / "templates" / "pages" / "list_item.html").read_text()


class TestThreeStepGating:
    """Each of the three steps must use x-show with mutually-exclusive
    conditions, and only one set of Save/Publish buttons may exist
    (the publish button on the final step)."""

    def test_step_1_visible_only_when_step_eq_1(self):
        assert 'x-show="step === 1"' in LIST_HTML, (
            "Step 1 (item details) container must use x-show=\"step === 1\""
        )

    def test_step_2_visible_only_when_step_eq_2(self):
        assert 'x-show="step === 2"' in LIST_HTML, (
            "Step 2 (delivery + notes + policy + availability) container "
            "must use x-show=\"step === 2\""
        )

    def test_step_3_visible_only_when_step_eq_3(self):
        assert 'x-show="step === 3"' in LIST_HTML, (
            "Step 3 (listing types + pricing) container must use "
            "x-show=\"step === 3\""
        )

    def test_only_one_publish_button_in_template(self):
        """The original bug had Submit/Publish on a non-final step and a
        Next button next to it. Now there's exactly one Submit on Step 3."""
        # Count occurrences of the publish click handler
        publish_clicks = LIST_HTML.count("saveAsDraft = false; submitItem()")
        assert publish_clicks == 1, (
            f"Expected exactly one Publish button (saveAsDraft=false) but "
            f"found {publish_clicks}. It must live only on the final step."
        )

    def test_only_one_save_draft_button_in_template(self):
        """Same defense for Save Draft -- only on the final step."""
        save_draft_clicks = LIST_HTML.count("saveAsDraft = true; submitItem()")
        assert save_draft_clicks == 1, (
            f"Expected exactly one Save Draft button but found "
            f"{save_draft_clicks}. Must live only on the final step."
        )


class TestStepNavigation:
    """Forward/backward movement between steps must be wired correctly."""

    def test_step_1_advances_to_step_2(self):
        # The "Next" on Step 1 must check name and set step=2
        assert "if(form.name.trim()) step = 2" in LIST_HTML, (
            "Step 1's Next button must require form.name and advance to step=2"
        )

    def test_step_2_back_goes_to_step_1(self):
        # Step 2's Back must reset step to 1
        # Look for a button with @click="step = 1" in the step-2 region
        step2_idx = LIST_HTML.find('x-show="step === 2"')
        # Step 2 in DOM runs from its open until the form closes (DOM-third)
        step2_block = LIST_HTML[step2_idx:]
        end_marker = step2_block.find("{% endblock %}")
        if end_marker > 0:
            step2_block = step2_block[:end_marker]
        assert '@click="step = 1"' in step2_block, (
            "Step 2 must have a Back button that sets step = 1"
        )

    def test_step_2_advances_to_step_3(self):
        step2_idx = LIST_HTML.find('x-show="step === 2"')
        step2_block = LIST_HTML[step2_idx:]
        end_marker = step2_block.find("{% endblock %}")
        if end_marker > 0:
            step2_block = step2_block[:end_marker]
        assert '@click="step = 3"' in step2_block, (
            "Step 2 must have a Next button that sets step = 3"
        )

    def test_step_3_back_goes_to_step_2(self):
        # Step 3 block is large -- scope from its open to the next step container
        step3_idx = LIST_HTML.find('x-show="step === 3"')
        step2_idx = LIST_HTML.find('x-show="step === 2"', step3_idx)
        step3_block = LIST_HTML[step3_idx:step2_idx]
        assert '@click="step = 2"' in step3_block, (
            "Step 3 must have a Back button that sets step = 2"
        )


class TestStepIndicator:
    """The numbered circle indicator at the top must reflect all three
    steps (was a 1-2 indicator before)."""

    def test_indicator_renders_three_circles(self):
        # The indicator uses x-for over [1, 2, 3]
        assert "[1, 2, 3]" in LIST_HTML, (
            "Top-of-page step indicator must iterate three steps, not two"
        )

    def test_indicator_highlights_completed_steps(self):
        # Each circle is highlighted when step >= n
        assert "step >= n" in LIST_HTML, (
            "Step indicator circles must light up progressively (step >= n)"
        )


class TestSubmitOnFinalStepOnly:
    """The publish flow must be: user MUST land on Step 3 to submit.
    Submit on a non-final step would skip price entry."""

    def test_publish_button_inside_step_3_block(self):
        # Scope to the actual Step 3 region (open to next step container)
        step3_idx = LIST_HTML.find('x-show="step === 3"')
        step2_idx = LIST_HTML.find('x-show="step === 2"', step3_idx)
        step3_block = LIST_HTML[step3_idx:step2_idx]
        assert "saveAsDraft = false; submitItem()" in step3_block, (
            "Publish button must live inside the Step 3 (pricing) container"
        )

    def test_publish_button_NOT_in_step_2(self):
        step2_idx = LIST_HTML.find('x-show="step === 2"')
        # Step 2 in DOM comes AFTER Step 3 -- runs to end of file's form section
        step2_block = LIST_HTML[step2_idx:]
        # Stop at the form's closing tag area (look for </main> or </form>)
        end_marker = step2_block.find("{% endblock %}")
        if end_marker > 0:
            step2_block = step2_block[:end_marker]
        assert "saveAsDraft = false; submitItem()" not in step2_block, (
            "Publish button must NOT appear in Step 2 -- the user has not "
            "set the price yet at that point"
        )

    def test_save_draft_button_inside_step_3_block(self):
        step3_idx = LIST_HTML.find('x-show="step === 3"')
        step2_idx = LIST_HTML.find('x-show="step === 2"', step3_idx)
        step3_block = LIST_HTML[step3_idx:step2_idx]
        assert "saveAsDraft = true; submitItem()" in step3_block, (
            "Save Draft button must also live on the final step so the "
            "draft includes a price decision"
        )


# ---- Negative / breaking guards: things that MUST NOT exist ----

class TestNoBackdoorPublishPaths:
    """Things that would silently break the 3-step contract. These tests
    fail loud if anyone re-introduces a forbidden pattern."""

    def test_no_orphan_step_eq_4_or_higher(self):
        """No future code path should accidentally jump to a non-existent
        step. Catches typos like step = 4 or step === 4."""
        forbidden = ['step === 4', 'step === 0', 'step = 4', 'step = 0', 'step = -1']
        offenders = [p for p in forbidden if p in LIST_HTML]
        assert not offenders, (
            f"Forbidden step values found in template: {offenders}. "
            f"Only steps 1, 2, 3 are valid."
        )

    def test_no_publish_button_outside_x_show_block(self):
        """A publish button OUTSIDE any x-show step container would fire
        regardless of which step is showing -- catastrophic UX."""
        # All publish buttons must follow an x-show="step === ..." attribute
        # earlier in their containing div. Practical proxy: the only Publish
        # in the file should be lexically AFTER 'x-show="step === 3"'.
        step3_idx = LIST_HTML.find('x-show="step === 3"')
        publish_idx = LIST_HTML.find("saveAsDraft = false; submitItem()")
        assert step3_idx > 0 and publish_idx > step3_idx, (
            "Publish button must appear lexically after the Step 3 x-show "
            "anchor -- otherwise it's escaping the gating"
        )

    def test_no_naked_x_show_without_explicit_step_value(self):
        """Catches lazy refactors like x-show='step' (truthy) instead of
        x-show='step === N'. The latter is mutually exclusive; the former
        is true for any non-zero step (would show all containers)."""
        import re
        # Match x-show="step" without === N
        bad = re.findall(r'x-show="step"\s', LIST_HTML)
        assert not bad, (
            "Naked x-show=\"step\" found -- always use strict equality "
            "(x-show=\"step === N\") so containers stay mutually exclusive"
        )

    def test_step_initial_value_is_one(self):
        """The user must always land on Step 1 -- never auto-jumped to a
        later step (which would skip required fields like name)."""
        # Look for step: 1 in the Alpine x-data block
        assert "step: 1," in LIST_HTML or "step:1," in LIST_HTML, (
            "Form's Alpine state must initialize step to 1 so users start "
            "at the WHAT step every time"
        )

    def test_step_required_fields_block_advance(self):
        """The Next button on Step 1 must be disabled when name is empty.
        Otherwise users could submit a nameless item all the way to publish."""
        # The Step 1 Next button has :disabled="!form.name.trim()"
        assert ':disabled="!form.name.trim()"' in LIST_HTML, (
            "Step 1's Next button must disable when form.name is empty -- "
            "the only required field gate before pricing"
        )
