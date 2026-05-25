"""Regression test for the enum-casing traps that bit the quote + rental
filter parsers (and the quote template comparisons) in May 2026.

Two layers:

1. **Static grep** -- no router code should call `SomeStatus(value.upper())`
   when the enum values are lowercase. That pattern silently swallows
   ValueError and drops the filter. Same for `.lower()` against an
   uppercase-valued enum (rarer but symmetrical).

2. **Round-trip** -- for every `*Status` enum in src/models, iterate its
   members and confirm `SomeStatus(member.value)` returns the same member.
   This catches accidental case mismatches between the python enum value
   and any URL parameter or DB-stored string the parser receives.

If either layer fails, do NOT fix the test -- fix the bug. The reason
this file exists is that the QuoteStatus / RentalStatus filter parsers
silently dropped queries for months, and Angel kept hitting it.
"""

import importlib
import pkgutil
import re
from pathlib import Path

import pytest

SRC_ROUTERS = Path(__file__).resolve().parent.parent / "src" / "routers"
SRC_MODELS = Path(__file__).resolve().parent.parent / "src" / "models"


def _all_status_enums():
    """Discover every *Status enum defined under src/models/."""
    import enum
    discovered = []
    for mod_info in pkgutil.iter_modules([str(SRC_MODELS)]):
        mod_name = f"src.models.{mod_info.name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for name in dir(mod):
            obj = getattr(mod, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, enum.Enum)
                and name.endswith("Status")
                and obj.__module__ == mod_name
            ):
                discovered.append((name, obj))
    return discovered


# ── Layer 1: static grep ────────────────────────────────────────────────

# Match `SomethingStatus(<expr>.upper())` or `SomethingStatus(<expr>.lower())`
# in router code. Both are suspect: they assume the enum values are in the
# opposite case from what URL params or DB strings carry, and history shows
# we've been wrong every single time.
_BAD_PATTERN = re.compile(r"\b\w*Status\s*\(\s*[^)]*\.(upper|lower)\s*\(\s*\)\s*\)")


def test_no_status_enum_case_coercion_in_routers():
    """Static check: no router should call SomeStatus(value.upper()) /
    .lower() before constructing an enum. Pass the raw URL/DB value
    straight in; if it doesn't match, that's a real validation error,
    not something to silently coerce."""
    offenders = []
    for path in SRC_ROUTERS.rglob("*.py"):
        text = path.read_text()
        for match in _BAD_PATTERN.finditer(text):
            line = text[:match.start()].count("\n") + 1
            offenders.append(f"{path.relative_to(SRC_ROUTERS.parent.parent)}:{line}  {match.group(0)}")
    assert not offenders, (
        "Status enum constructed with .upper()/.lower() coercion -- this is the "
        "casing trap that has bitten the quote + rental filter parsers. Pass "
        "raw URL params straight into the enum (the dropdown values must already "
        "match the enum's .value). Offenders:\n  " + "\n  ".join(offenders)
    )


# ── Layer 2: round-trip every enum value through its own constructor ───

@pytest.mark.parametrize("enum_name, enum_cls", _all_status_enums(),
                         ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_status_enum_round_trip(enum_name, enum_cls):
    """For each *Status enum, constructing from .value must return the
    same member. If this ever fails it means the enum is misdefined
    (duplicate values, wrong type, etc) and any URL filter using it will
    silently drop queries."""
    for member in enum_cls:
        assert enum_cls(member.value) is member, (
            f"{enum_name}({member.value!r}) did not round-trip back to "
            f"{enum_name}.{member.name}. URL filters will silently fail."
        )


# ── Layer 3: every value is lowercase (matches dropdown convention) ────

# All HTML status dropdowns in src/templates use lowercase option values
# (status=requested, status=pending, etc). The router parser passes those
# straight to the enum constructor. So every Status enum value MUST be
# lowercase, or the dropdown will silently fail.
@pytest.mark.parametrize("enum_name, enum_cls", _all_status_enums(),
                         ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_status_enum_values_are_lowercase(enum_name, enum_cls):
    """All status enum string values must be lowercase. Anything else
    means the HTML dropdown values won't match and the filter drops."""
    offenders = [m.value for m in enum_cls if m.value != m.value.lower()]
    assert not offenders, (
        f"{enum_name} has non-lowercase values: {offenders!r}. "
        f"The HTML dropdowns send lowercase, so the filter will silently fail."
    )
