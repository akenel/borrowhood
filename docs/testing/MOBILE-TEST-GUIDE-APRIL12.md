# Mobile Test Guide -- April 12, 2026

**URL:** https://lapiazza.app  
**Login:** /demo (pick any cast member)  
**Tests:** 853 passed

---

## 1. Community Calendar

**Page:** /calendar

- [ ] Calendar grid shows April with dots on event days (10, 13, 15, 18, 20, 22, 25, 27)
- [ ] Tap an event dot -- goes to item detail page
- [ ] Month name shows in your language
- [ ] Prev/Next arrows change month
- [ ] May has 3 events (3, 10, 17)
- [ ] Event cards show image, title, date, venue, price
- [ ] Free events show green "Free" label
- [ ] Paid events show EUR price

## 2. My Events Tab

**Page:** /calendar -> "My Events" tab

- [ ] Log in as Sally -- she has 4 RSVPs
- [ ] Switch to "My Events" -- see her 4 events
- [ ] Registered badge shows "Registered" in indigo
- [ ] Cancel RSVP on one event -- it disappears from My Events
- [ ] Switch back to Community -- event still shows, RSVP button is back

## 3. My Rentals Tab

**Page:** /calendar -> "My Rentals" tab

- [ ] Tab shows emerald green when active
- [ ] If no rentals, shows empty state with "Browse Items" link
- [ ] If logged in user has active rentals, cards show:
  - Role badge (Lending / Borrowing)
  - Date range
  - Other party name
  - Status badge (pending, approved, etc.)
  - Listing type

## 4. RSVP Flow

**Page:** /calendar (Community tab)

- [ ] Tap RSVP on "Welding Basics Workshop" -- button flips to "Cancel RSVP"
- [ ] RSVP count updates (e.g., 2/8 -> 3/8)
- [ ] Cancel RSVP -- button flips back, count decreases
- [ ] Try RSVP while logged out -- redirects to login

## 5. Share Button

**Page:** /calendar

- [ ] Share icon appears on each event card
- [ ] Tap share -- native share sheet opens (or link copied)
- [ ] Share a NEW event link on WhatsApp/Telegram
- [ ] Preview card shows: image, title, date/time/venue/price in description

## 6. Availability Calendar (Item Detail)

**Page:** /items/welding-basics-workshop (or any rental/service listing)

- [ ] Below listings section, "Availability" calendar appears
- [ ] Mini month grid with green (available) and red (booked) days
- [ ] Month navigation arrows work
- [ ] Legend shows green = available, red = booked
- [ ] Min/max rental days shown if set

## 7. Team Pricing (Service/Training Items)

**Page:** Any service/training listing item detail

- [ ] "Number of Participants" input appears in booking form
- [ ] Change participant count -- price calculates live
- [ ] 3+ participants shows group discount line (if configured)
- [ ] Total displayed with breakdown (subtotal, discount, total)

## 8. Dashboard -- Analytics Tab

**Page:** /dashboard -> dropdown -> "Analytics"

- [ ] Summary cards: Total Views, Orders, Revenue, Conversion
- [ ] Per-item table showing each item's views, orders, revenue, CTR
- [ ] Items sorted by views (most viewed first)
- [ ] Click an item row -- goes to item detail

## 9. Dashboard -- Mentorships Tab

**Page:** /dashboard -> dropdown -> "Mentorships"

- [ ] Shows active mentorships (Angel -> Nic should appear)
- [ ] Status badge (proposed, active, completed)
- [ ] "Log" button opens inline form (hours, milestones, notes)
- [ ] "Complete" button marks mentorship done
- [ ] "Accept" button on proposed mentorships
- [ ] "Cancel" button on active ones

## 10. Dashboard -- Saved Searches Tab

**Page:** /dashboard -> dropdown -> "Saved Searches"

- [ ] Shows saved searches (if any exist)
- [ ] Bell icon toggles notifications on/off
- [ ] Trash icon deletes the search
- [ ] Match count badge shows "X new" in red
- [ ] Empty state links to /browse

## 11. Delivery Tracking Page

**Page:** /delivery/{rental_id}

- [ ] Status banner (color-coded: amber=preparing, blue=in transit, green=delivered)
- [ ] Map with destination pin (if GPS coordinates exist)
- [ ] Event timeline with dots and timestamps
- [ ] Accessible from dashboard rental cards

## 12. Mobile-Specific Checks

- [ ] Calendar grid: dots on mobile, text chips on desktop
- [ ] All tabs fit on screen without horizontal scroll
- [ ] Touch targets are 44px+ (buttons, inputs)
- [ ] No text overflow or clipping
- [ ] Share button works on mobile (native share API)
- [ ] Font size A+/A- still works correctly

---

**How to create test data:**
- Go to /browse, filter by category, tap "Alert me" to save a search
- Go to /calendar, RSVP to events
- Dashboard analytics start populating as people view items

**Report bugs:** Use the floating feedback button (rose dot, bottom-right)
