# Manual Test Script -- March 28, 2026
## JSONB Attributes + Vehicles/Property/Jobs + AI Skill Suggestions

**URL:** https://lapiazza.app (or https://borrowhood.duckdns.org)

---

### TEST 1: Browse Page -- New Category Cards

1. Go to `/browse`
2. **VERIFY:** You see 12 category cards (was 10)
3. **VERIFY:** New cards visible: "Vehicles & Auto" (red) and "Jobs & Gigs" (teal)
4. Click **"Vehicles & Auto"** card
5. **VERIFY:** URL shows `?category_group=vehicles`
6. **VERIFY:** Items with category "vehicles" AND "automotive" both appear
7. Click "Clear filter" link
8. Click **"Property & Rentals"** card
9. **VERIFY:** Items from apartment, house, room, vacation_rental categories appear
10. Click "Clear filter"
11. Click **"Jobs & Gigs"** card
12. **VERIFY:** Job listings appear (if seeded -- may need reseed)

**PASS:** [ ] All 12 cards visible, group filtering works

---

### TEST 2: Attribute Filters on Browse

1. Go to `/browse?category_group=vehicles`
2. **VERIFY:** Below the main filters, an "Specifications" section appears
3. **VERIFY:** You see dropdowns for Fuel Type, Transmission, Body Type, Euro Class
4. Select **Fuel Type: Diesel**
5. **VERIFY:** Page reloads with `?attr_fuel_type=diesel` in URL
6. **VERIFY:** Only diesel vehicles shown (if seeded data has them)
7. Clear filter, go to `/browse?category_group=property`
8. **VERIFY:** Property filters appear (Energy Class, Heating, Furnished)
9. Check **Air Conditioning** checkbox
10. **VERIFY:** Filters by `attr_air_conditioning=true`

**PASS:** [ ] Attribute filters render and filter correctly

---

### TEST 3: List Item -- Vehicle with Attributes

1. Log in as any user
2. Go to `/list` (List an Item)
3. Type name: "My Test Car"
4. In category dropdown, select **"Vehicles & Transport"**
5. **VERIFY:** A blue "Specifications" panel appears with fields:
   - Year, Mileage (km), Fuel Type, Transmission, Engine (cc), Body Type,
   - Doors, Seats, Color, Euro Class, Previous Owners, Accident Free
6. Fill in: Year=2019, Mileage=45000, Fuel Type=diesel, Transmission=manual
7. Check "Accident Free"
8. Submit the item
9. **VERIFY:** Item detail page shows the attributes in a "Specifications" grid
10. **VERIFY:** "Accident Free" shows a green checkmark
11. Delete the test item after

**PASS:** [ ] Vehicle attributes saved and displayed correctly

---

### TEST 4: List Item -- Property with Attributes

1. Go to `/list`
2. Type name: "My Test Apartment"
3. Select category **"Apartment"** (under Property & Rentals)
4. **VERIFY:** Specifications panel shows property fields:
   - Bedrooms, Bathrooms, Floor Area, Floor, Elevator, Energy Class,
   - Heating, Furnished, Parking, Balcony, Garden, Air Conditioning, etc.
5. Fill in: Bedrooms=2, Bathrooms=1, Floor Area=65, Energy Class=D, Furnished=furnished
6. **VERIFY:** Item type auto-set to "space", listing type auto-set to "rent"
7. Submit and verify attributes display on detail page
8. Delete test item

**PASS:** [ ] Property attributes saved and displayed correctly

---

### TEST 5: List Item -- Job Listing

1. Go to `/list`
2. Type name: "Looking for a Mechanic"
3. Select category **"Full-Time Job"** (under Jobs & Gigs)
4. **VERIFY:** Specifications panel shows job fields:
   - Job Type, Salary Min, Salary Max, Salary Period, Experience Level,
   - Remote Work, Industry, Application Deadline
5. Fill in: Salary Min=1400, Salary Max=1800, Experience=mid, Remote=on_site
6. **VERIFY:** Item type auto-set to "service", listing type auto-set to "offer"
7. Submit and verify
8. Delete test item

**PASS:** [ ] Job attributes saved and displayed correctly

---

### TEST 6: Item Detail -- Specifications Grid

1. Find any seeded vehicle (e.g., "Fiat Panda 4x4 1990 Classic" if reseeded)
2. **VERIFY:** Below the category/brand tags, a "Specifications" section appears
3. **VERIFY:** Grid shows year, mileage, fuel type, transmission, etc.
4. **VERIFY:** Boolean values like "Accident Free" show a green checkmark
5. **VERIFY:** Values are title-cased (e.g., "Diesel" not "diesel")
6. Check a property listing for bedrooms/sqm display
7. Check a job listing for salary/experience display

**PASS:** [ ] Specifications grid renders correctly on detail pages

---

### TEST 7: Edit Item -- Attributes Persist

1. Go to a listing you own that has attributes
2. Click "Edit Listing"
3. **VERIFY:** The attribute fields are pre-filled with saved values
4. Change one value (e.g., mileage)
5. Save
6. **VERIFY:** Updated value shows on detail page

**PASS:** [ ] Attributes persist through edit round-trip

---

### TEST 8: Skills CRUD on Profile

1. Log in, go to `/profile`
2. **VERIFY:** Skills section appears (even if empty)
3. **VERIFY:** "+ Add Skill" button visible
4. Click "+ Add Skill"
5. **VERIFY:** Form appears with: skill name, category dropdown, rating (1-5), years exp.
6. Type "Bread Baking", select category "Kitchen", rating 4, years 10
7. Click "Save"
8. **VERIFY:** Toast "Skill added", skill appears as a tag
9. Hover over the skill tag
10. **VERIFY:** X button appears to delete
11. Click X, confirm
12. **VERIFY:** Toast "Bread Baking removed"

**PASS:** [ ] Skills CRUD works end-to-end

---

### TEST 9: AI Skill Suggestions from Bio

**Prerequisite:** User must have a bio with 20+ characters.

1. Go to `/profile`, ensure you have a bio
2. **VERIFY:** "Suggest from Bio" button visible (purple, next to Add Skill)
3. Click "Suggest from Bio"
4. **VERIFY:** Button shows spinner with "Analyzing..."
5. Wait for AI response (3-10 seconds)
6. **VERIFY:** Purple panel appears with checkboxes for each suggested skill
7. **VERIFY:** Each skill shows: name, category, rating, years, confidence %
8. Uncheck any unwanted skills
9. Click "Accept Selected"
10. **VERIFY:** Toast shows "X skills added"
11. **VERIFY:** Skills appear in the skills tag list
12. Click "Suggest from Bio" again
13. **VERIFY:** No duplicates suggested (AI excludes existing skills)

**PASS:** [ ] AI skill suggestions work with review/accept flow

---

### TEST 10: API Endpoint Verification (curl)

Run these from terminal:

```bash
# Attribute schemas
curl -s https://lapiazza.app/api/v1/items/attribute-schemas | python3 -m json.tool | head -20

# Vehicle schema
curl -s https://lapiazza.app/api/v1/items/attribute-schema/vehicles | python3 -m json.tool | head -20

# Property schema
curl -s https://lapiazza.app/api/v1/items/attribute-schema/apartment | python3 -m json.tool | head -20

# Job schema
curl -s https://lapiazza.app/api/v1/items/attribute-schema/job_full_time | python3 -m json.tool | head -20

# Category group filter (items API)
curl -s "https://lapiazza.app/api/v1/items?category_group=vehicles&limit=5" | python3 -m json.tool | head -20

# Skills endpoints (should return 401 without auth)
curl -s https://lapiazza.app/api/v1/users/me/skills
curl -s -X POST https://lapiazza.app/api/v1/users/me/skills/suggest
```

**PASS:** [ ] All API endpoints return expected responses

---

### TEST 11: Mobile Responsiveness

1. Open browser devtools, switch to mobile view (iPhone 12 / Galaxy S21)
2. Go to `/browse`
3. **VERIFY:** Category cards scroll horizontally (no overflow)
4. **VERIFY:** New cards (Vehicles, Jobs) visible in scroll
5. Go to `/list`, pick a vehicle category
6. **VERIFY:** Attribute fields stack in single column on mobile
7. Go to `/profile`
8. **VERIFY:** Skills section readable, Add/Suggest buttons accessible
9. **VERIFY:** AI suggestions panel fits mobile width

**PASS:** [ ] Mobile layout works for all new features

---

### TEST 12: Italian Language

1. Switch to Italian (click language toggle or `/lang/it`)
2. Go to `/browse`
3. **VERIFY:** "Veicoli e Auto" and "Lavoro e Collaborazioni" cards visible
4. Go to `/list`, pick "Appartamento"
5. **VERIFY:** Attribute labels in Italian (Locali, Bagni, Superficie, etc.)
6. Go to `/profile`
7. **VERIFY:** "Competenze" heading, "Aggiungi" button, "Suggerisci dal Bio" button

**PASS:** [ ] Italian translations complete for all new features

---

## Summary

| # | Test | Status |
|---|------|--------|
| 1 | Browse category cards | [ ] |
| 2 | Attribute filters | [ ] |
| 3 | List vehicle | [ ] |
| 4 | List property | [ ] |
| 5 | List job | [ ] |
| 6 | Item detail specs | [ ] |
| 7 | Edit attributes | [ ] |
| 8 | Skills CRUD | [ ] |
| 9 | AI skill suggestions | [ ] |
| 10 | API endpoints | [ ] |
| 11 | Mobile responsive | [ ] |
| 12 | Italian language | [ ] |

**Tested by:** _______________
**Date:** _______________
**Build:** ce8d925
