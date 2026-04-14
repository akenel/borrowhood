# Filters SOP -- The La Piazza Way

*Modern filter design rules. If you're adding a new filter anywhere on the app,
this document is the spec. If you're redesigning existing filters, this is the
acceptance test.*

**Last updated:** April 15, 2026

---

## Rule 1: Pills, Never Dropdown Panels

A "filter panel" is a 2010 pattern. Modern UX is **inline pills** on the page,
always visible, always clickable.

**DO:**
```html
<label class="relative inline-flex items-center">
    <select class="appearance-none pl-10 pr-9 py-2 bg-white border border-gray-200
                   rounded-full text-sm font-medium hover:bg-gray-50
                   focus:ring-2 focus:ring-indigo-500 cursor-pointer shadow-sm">
        <option>Newest</option>
    </select>
    <svg class="absolute left-3 w-4 h-4 text-gray-400"><!-- lead icon --></svg>
    <svg class="absolute right-3 w-4 h-4 text-gray-400"><!-- chevron --></svg>
</label>
```

**DON'T:**
- Hide filters in a collapsible "Filters" drawer (old eBay pattern)
- Use a separate "Apply" button -- every change is live
- Stack filters in a column -- they go horizontally as pills, wrapping on mobile

---

## Rule 2: Live Submit, No Apply Button

Every filter change auto-submits. No "Apply" button. Ever.

**Pattern:**
```html
<form x-ref="filterForm" method="GET" action="/browse">
    <select name="sort" @change="$refs.filterForm.submit()">...</select>
    <select name="price_max" @change="$refs.filterForm.submit()">...</select>
</form>
```

**Why:** Users change filter -> results update. No hunting for a button.
Eliminates the "did I apply that?" confusion.

**Edge case:** Text search still has a submit button because you type many
characters before wanting to search. Dropdowns/checkboxes submit immediately.

---

## Rule 3: Icons + Emojis for Scanning

Every filter pill has a **lead icon** on the left (Heroicons SVG) and a
**chevron** on the right (indicates it's a dropdown).

Dropdown OPTIONS can use emoji prefixes when they help scanability:
```
🏠 Rent
💰 Buy
🎉 Events
🔧 Services
📚 Training
🎨 Made-to-Order
🔥 Auctions
🎁 Free / Giveaway
```

**When to emoji:** Options that represent concepts the user is scanning for.
**When NOT to emoji:** Strict data values (prices, dates, sort order labels).

---

## Rule 4: Active State Makes It Obvious

When a filter is applied, the pill MUST look different:

```html
<!-- Active -->
class="bg-indigo-50 border-indigo-300 text-indigo-700"

<!-- Inactive -->
class="bg-white border-gray-200 text-gray-700 hover:bg-gray-50"
```

**Color by filter type:**
- Sort / default filters: **indigo** (bg-indigo-50 + text-indigo-700)
- Free / giveaway toggles: **emerald** (bg-emerald-50 + text-emerald-700)
- Price / money filters: **indigo**
- Category filters: use the category's color (rose, red, teal, etc)

---

## Rule 5: Clear Filters Link

When ANY filter is active beyond defaults, show a "Clear filters" link
on the right side. Small, gray, becomes red on hover.

```html
{% if selected_listing_type or selected_price_max or selected_free_only ... %}
<a href="/browse{% if selected_category %}?category={{ selected_category }}{% endif %}"
   class="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-red-600 ml-auto">
    <svg><!-- X icon --></svg>
    Clear filters
</a>
{% endif %}
```

**Keep what stays, clear what you set.** Clearing filters preserves the category
context but removes sort, price, type, free_only. Don't nuke everything.

---

## Rule 6: Empty-String Safe Backend

Live-submit forms send `?price_max=&free_only=` when fields are empty. FastAPI
will 422 on `Optional[float] = None` if you send `price_max=`. The fix:

```python
# Accept as str, coerce manually
price_max: Optional[str] = None,
free_only: Optional[str] = None,
...
# In the body:
price_max_val: Optional[float] = None
if price_max:
    try:
        price_max_val = float(price_max)
    except (TypeError, ValueError):
        price_max_val = None
free_only_val = bool(free_only and free_only.lower() in ("true", "1", "on"))
```

**Always coerce empty strings at the boundary.** Downstream code should
only see `None` or a valid value, never `""`.

---

## Rule 7: URL State is the Source of Truth

Every filter value lives in the URL query string. This means:
- Refresh preserves filters
- Back button works
- Sharing a filtered view is just copy/paste
- Saved searches are just URL snapshots

**Never store filter state in JS/Alpine only.** Put it in the form, let
the URL carry it.

---

## Rule 8: Mobile First, Wrapping Is Fine

Pills should `flex-wrap` on narrow screens. No horizontal scroll, no drawer.
6 filter pills wrap to 2 rows on a phone -- that's fine.

```html
<div class="flex items-center flex-wrap gap-2">
    <!-- pills -->
</div>
```

**Never hide filters behind a hamburger on mobile.** They are part of the page,
not a secondary menu.

---

## Rule 9: Context Pills for the Unfiltered State

When no category is selected, show "Browse by category" cards (big, colorful).

When a category IS selected, show:
1. A **breadcrumb pill** with the category name and an X to clear
2. An **"Alert me"** pill (saved search trigger)
3. The filter pill bar

```
[Property & Rentals ×]  [🔔 Alert me for new matches]
[Newest ↓] [Looking for ▾] [€ ≤ 50 ▾] [🎁 Free only] [More filters]
```

---

## Rule 10: Advanced Filters Go Behind "More filters"

Category-specific attribute filters (year, bedrooms, fuel type) hide behind a
"More filters" button. They only appear for categories that HAVE attribute schemas
(vehicles, property, jobs).

```python
# Backend: only populate attribute_schema when it applies
active_attr_schema = {}
if category_group in ATTRIBUTE_SCHEMAS:
    active_attr_schema = ATTRIBUTE_SCHEMAS[category_group]
```

```html
{% if attribute_schema %}
<button @click="filtersOpen = !filtersOpen"
        class="... {{ 'bg-indigo-50 border-indigo-300' if filtersOpen else '' }}">
    More filters
</button>
{% endif %}

<div x-show="filtersOpen" x-cloak x-transition>
    <!-- year, bedrooms, fuel_type, etc -->
</div>
```

---

## Rule 11: Don't Fetch for Anonymous Users

Auth-gated API calls (like `/api/v1/items/me/favorite-ids`) should be skipped
for logged-out users. Guard with `loggedIn` flag:

```html
x-data="{
    loggedIn: {{ 'true' if user else 'false' }},
    async init() {
        if (!this.loggedIn) return;
        // fetch ...
    }
}"
```

**Why:** Console noise hurts trust. Anonymous browse should have zero 401s.

---

## Rule 12: Test Every Empty-String Combination

When adding a new filter, add a test that passes ALL filters as empty strings:

```python
@pytest.mark.asyncio
async def test_browse_all_empty_strings_ok(db_client):
    resp = await db_client.get(
        "/browse?q=&category=&listing_type=&price_max=&free_only=&sort=newest"
    )
    assert resp.status_code == 200
```

**Why:** Live-submit forms WILL send empty strings. This is the first thing
that breaks when you add a `Optional[float]` or `Optional[int]` param.

---

## Quick Checklist for New Filters

When you add a new filter, verify:

- [ ] Backend param is `Optional[str]` with manual coercion (empty-string safe)
- [ ] Template pill is a `<label>` with `<select>` or `<input>`
- [ ] Pill has lead icon + chevron + active-state color
- [ ] Uses `@change="$refs.filterForm.submit()"` for live submit
- [ ] Hidden inputs preserve other filters (category, q, etc)
- [ ] Template test: empty string doesn't crash
- [ ] Template test: each valid value works
- [ ] "Clear filters" link updated to include the new filter
- [ ] Emoji/icon in dropdown options if it aids scanning
- [ ] Mobile: pill wraps gracefully, still tappable (44px min height)

---

## Reference Implementation

**`src/templates/pages/browse.html`** is the canonical implementation.
Copy its pattern when adding filters elsewhere.

Backend reference: **`src/routers/pages.py`** `browse()` function
-- see the `price_max_val` / `free_only_val` coercion pattern.

Test reference: **`tests/test_april15_feedback.py`**
-- empty-string safety, every dropdown value tested.

---

*"If the filter makes the user think, the filter failed."*
