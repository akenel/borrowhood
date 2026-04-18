"""Meta-test: split router packages keep their public shape.

After the April 2026 fat-file refactor, every large router module was
turned into a package (e.g. `src/routers/items/__init__.py`). This test
catches the class of regression where a future refactor breaks a
package's public contract — e.g. forgetting to re-export `router`,
dropping a route from `__init__.py`'s `include_router` chain, or
accidentally changing a URL prefix.

If this test fails, something about the aggregator changed. The fix
is usually in the package's `__init__.py`, not here.
"""

import importlib

import pytest


ROUTER_PACKAGES = [
    # (module_path, expected_prefix, minimum_route_count)
    ("src.routers.pages",     "",                   20),
    ("src.routers.users",     "/api/v1/users",      15),
    ("src.routers.helpboard", "/api/v1/helpboard",  15),
    ("src.routers.items",     "/api/v1/items",      15),
    ("src.routers.messages",  "/api/v1/messages",   10),
    ("src.routers.events",    "/api/v1/events",      6),
    ("src.routers.payments",  "/api/v1/payments",    8),
    ("src.routers.qa",        "/api/v1/testing",     8),
    ("src.routers.reviews",   "/api/v1/reviews",     6),
]


@pytest.mark.parametrize("module_path,prefix,min_routes", ROUTER_PACKAGES)
def test_package_exports_router_with_expected_prefix(module_path, prefix, min_routes):
    mod = importlib.import_module(module_path)
    router = getattr(mod, "router", None)
    assert router is not None, f"{module_path} does not export `router`"
    assert router.prefix == prefix, (
        f"{module_path}: prefix changed from {prefix!r} to {router.prefix!r}"
    )
    assert len(router.routes) >= min_routes, (
        f"{module_path}: only {len(router.routes)} routes, expected at least {min_routes}. "
        "A submodule is probably missing from the aggregator's include_router chain."
    )


def test_qa_exports_both_routers():
    """qa/ is unusual — main.py imports `qa.router` AND `qa.html_router`."""
    from src.routers import qa

    assert qa.router.prefix == "/api/v1/testing"
    assert qa.html_router.prefix == ""
    # html_router has exactly one route today: GET /testing
    paths = [r.path for r in qa.html_router.routes]
    assert "/testing" in paths, f"qa.html_router lost /testing: have {paths}"


def test_llm_package_and_gemini_shim_expose_ai_entrypoints():
    """Both `src.services.llm` and the `src.services.gemini` shim must expose
    the five public AI functions used by the rest of the app."""
    expected = {
        "smart_listing",
        "review_analysis",
        "concierge_search",
        "helpboard_draft",
        "suggest_skills_from_bio",
    }
    from src.services import llm as llm_mod
    from src.services import gemini as gemini_shim

    missing_llm = expected - set(dir(llm_mod))
    missing_shim = expected - set(dir(gemini_shim))
    assert not missing_llm, f"src.services.llm missing: {missing_llm}"
    assert not missing_shim, f"src.services.gemini shim missing: {missing_shim}"


# Spot-checks for routes that live in sub-modules — if someone drops a
# submodule from __init__.py's include_router chain, the package still
# imports fine but the route disappears. These catch that.
ROUTE_SPOT_CHECKS = [
    # (module_path, method, path suffix that must exist)
    ("src.routers.items",    "GET",    "/api/v1/items/attribute-schemas"),
    ("src.routers.items",    "POST",   "/api/v1/items/by-slug/{slug}/whatsapp-connect"),
    ("src.routers.messages", "POST",   "/api/v1/messages/offers"),
    ("src.routers.events",   "GET",    "/api/v1/events/leaderboard"),
    ("src.routers.events",   "GET",    "/api/v1/events/calendar"),
    ("src.routers.payments", "GET",    "/api/v1/payments"),
    ("src.routers.payments", "POST",   "/api/v1/payments/stripe/connect/onboard"),
    ("src.routers.reviews",  "POST",   "/api/v1/reviews/{review_id}/vote"),
    ("src.routers.qa",       "POST",   "/api/v1/testing/bugs"),
]


@pytest.mark.parametrize("module_path,method,path", ROUTE_SPOT_CHECKS)
def test_submodule_routes_registered(module_path, method, path):
    mod = importlib.import_module(module_path)
    matches = [r for r in mod.router.routes if r.path == path and method in r.methods]
    assert matches, (
        f"{module_path} is missing {method} {path}. "
        "A submodule was likely dropped from include_router."
    )
