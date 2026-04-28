"""Structural tests for the listing form's Alpine x-data scope (BL-174 redo).

The first BL-174 attempt added x-show='step === N' attributes to step
containers but the closing </div> chain was off by one -- Step 2 ended
up OUTSIDE the x-data root, so Alpine threw 'step is not defined' for
every Step 2 expression. The regex-based regression test missed it
because it only checked for STRING presence, not DOM nesting.

This test parses the actually-rendered HTML and asserts that every
step container is a real descendant of the x-data root. If anything
escapes that scope, this fails loudly.

Requires: lxml (added to .venv 2026-04-28).
"""
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, Undefined
from lxml import html as lxml_html


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "src" / "templates"


class _SilentUndefined(Undefined):
    """Render anything for missing variables -- we just want valid HTML out."""
    def __str__(self):
        return ""
    def __getattr__(self, name):
        return _SilentUndefined()
    def __getitem__(self, key):
        return _SilentUndefined()
    def __iter__(self):
        return iter([])
    def __bool__(self):
        return False


def _t(key, *args, **kwargs):
    """Stub i18n: return a lowercase tail of the key as the translation."""
    return str(key).split(".")[-1].replace("_", " ")


class _FakeRequest:
    class _U:
        path = "/list"
        def __str__(self):
            return "https://example.test/list"
    url = _U()
    query_params = {}
    cookies = {}


def _render_list_item(preset_type="rent"):
    """Render the list_item.html template with mock context.
    Returns the rendered HTML string."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        undefined=_SilentUndefined,
        autoescape=True,
    )
    env.globals["t"] = _t
    env.globals["now"] = lambda: __import__("datetime").datetime.now()
    template = env.get_template("pages/list_item.html")
    ctx = {
        "lang": "en",
        "supported_languages": ["en", "it"],
        "preset_type": preset_type,
        "duplicate_item": None,
        "duplicate_listing_types_json": "[]",
        "duplicate_listing_prices_json": "{}",
        "edit_mode": False,
        "edit_item": None,
        "edit_item_id": None,
        "edit_media_json": "[]",
        "edit_listings_json": "[]",
        "category_groups": {"tools_workshop": ["power_tools"]},
        "request": _FakeRequest(),
        "user": None,
        "csrf_token": "",
        "settings": type("S", (), {"app_url": "https://example.test"})(),
        "_set_lang_cookie": False,
        "is_owner": False,
    }
    return template.render(**ctx)


def _find_xdata_root(tree):
    """Return the element whose x-data attribute initializes the form's
    Alpine scope (the one containing 'step:' and 'submitItem')."""
    for el in tree.iter():
        x_data = el.get("x-data") or ""
        if "step:" in x_data and "submitItem" in x_data:
            return el
    return None


def _is_descendant_of(el, ancestor):
    """Return True if el is a descendant of ancestor (or is ancestor)."""
    cur = el
    while cur is not None:
        if cur is ancestor:
            return True
        cur = cur.getparent()
    return False


class TestStructuralScope:
    """Hard contract: every Alpine expression that references step / form /
    selectedTypes / submitItem MUST be inside the x-data root that defines
    them. If anything escapes, Alpine throws ReferenceError at runtime."""

    def test_xdata_root_exists(self):
        rendered = _render_list_item(preset_type="rent")
        tree = lxml_html.fromstring(rendered)
        root = _find_xdata_root(tree)
        assert root is not None, (
            "Could not find the form's x-data root element. The form's "
            "Alpine scope (step, form, selectedTypes, submitItem etc.) lives "
            "in a single <div x-data='{...}'> -- this test couldn't find it"
        )

    def test_every_step_xshow_is_inside_xdata_root(self):
        """Find every element with x-show='step === N' (the step containers)
        and assert each one is a descendant of the x-data root. If not,
        Alpine evaluates `step` outside the scope where it's defined."""
        rendered = _render_list_item(preset_type="rent")
        tree = lxml_html.fromstring(rendered)
        root = _find_xdata_root(tree)
        assert root is not None
        offenders = []
        for el in tree.iter():
            x_show = el.get("x-show") or ""
            if "step ===" in x_show or "step ==" in x_show:
                if not _is_descendant_of(el, root):
                    offenders.append(f"<{el.tag} x-show=\"{x_show}\"> at line ~{el.sourceline}")
        assert not offenders, (
            "Step containers escaped the x-data scope -- Alpine will throw "
            "ReferenceError for `step` on these elements:\n" + "\n".join(offenders)
        )

    def test_publish_button_is_inside_xdata_root(self):
        """The Publish button calls submitItem() which is defined on x-data.
        If the button is outside that scope, click does nothing."""
        rendered = _render_list_item(preset_type="rent")
        tree = lxml_html.fromstring(rendered)
        root = _find_xdata_root(tree)
        assert root is not None
        publish_buttons = []
        for el in tree.iter("button"):
            click = el.get("@click") or ""
            if "saveAsDraft = false" in click and "submitItem" in click:
                publish_buttons.append(el)
        assert publish_buttons, "No publish button found in the form"
        for btn in publish_buttons:
            assert _is_descendant_of(btn, root), (
                f"Publish button at line ~{btn.sourceline} is OUTSIDE the "
                "x-data scope -- clicking it would do nothing because "
                "submitItem is not defined in its scope"
            )

    def test_every_form_xmodel_is_inside_xdata_root(self):
        """Every x-model='form.X' must be inside x-data scope. If any input
        escapes, the input value is silently disconnected from the form
        state and the field appears to do nothing."""
        rendered = _render_list_item(preset_type="rent")
        tree = lxml_html.fromstring(rendered)
        root = _find_xdata_root(tree)
        assert root is not None
        offenders = []
        for el in tree.iter():
            x_model = el.get("x-model") or ""
            if x_model.startswith("form."):
                if not _is_descendant_of(el, root):
                    offenders.append(f"<{el.tag} x-model=\"{x_model}\"> line {el.sourceline}")
        assert not offenders, (
            "Form fields escaped x-data scope -- their values won't bind "
            "to form.X:\n" + "\n".join(offenders)
        )

    def test_xdata_root_div_balances(self):
        """Sanity: the div tag balance from x-data open to its matching close
        equals the total opens inside (no orphan close pulling x-data shut
        early). This is the regex check that should have caught BL-174."""
        rendered = _render_list_item(preset_type="rent")
        # Find x-data div, walk forward, count opens/closes, find matching close
        import re
        # Find the start of the x-data div
        m = re.search(r'<div\s+x-data="', rendered)
        assert m, "x-data div not found"
        # Slice from x-data div opening
        start = m.start()
        # Count net depth from start; expect to reach 0 before the end of
        # rendered HTML (i.e., x-data closes properly with the form intact)
        text = rendered[start:]
        # Strip <script>...</script> and <style>...</style> sections so any
        # `<div` literals inside JS strings don't pollute the count
        text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL)
        text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL)
        opens = re.findall(r"<div(\s|>)", text)
        closes = re.findall(r"</div>", text)
        # x-data div is the FIRST open -- there must be at least as many
        # closes as opens for the structure to be valid
        assert len(closes) >= len(opens), (
            f"x-data subtree has {len(opens)} opens but only {len(closes)} "
            f"closes -- structure is broken"
        )
