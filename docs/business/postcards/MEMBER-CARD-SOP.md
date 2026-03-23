# LaPiazza Member Business Card -- Production SOP

**How to create a business card for any LaPiazza member.**

---

## Prerequisites

Before making a card, the member must have:
1. At least 4 items listed on LaPiazza (for 4 unique front images)
2. A completed profile (display name, workshop name, tagline, bio)
3. Contact info they want on the card (phone, email, website, Instagram, etc.)
4. Approval of which 4 photos to use

## Step 1: Gather Member Info

From their LaPiazza profile or directly from them:

| Field | Example | Required? |
|-------|---------|-----------|
| Full name | Corrado Sassi | YES |
| Workshop/studio name | Sassi Studio Trapani | YES |
| Category | Art & Photography | YES |
| City, Country | Trapani, IT | YES |
| Phone | +39 335 806 0169 | Optional |
| Email | corrado.sassi@gmail.com | Optional |
| Website | corradosassi.com | Optional |
| Instagram | instagram.com/corradosassistudio | Optional |
| LinkedIn | linkedin.com/in/name | Optional |
| Tagline | "Every wall is a gallery." | Optional |
| Workshop slug (for QR) | artemisthinking-gmail-com | YES |

**At least 2 contact methods required.** Phone + one online link minimum.

## Step 2: Collect 4 Photos

- Get 4 high-quality images from the member (their best work/items)
- Landscape orientation preferred (cards are wider than tall)
- Minimum 800x600px resolution
- Save to: `docs/business/postcards/lapiazza-member-card/images/`
- Name them: `pick-1.jpg`, `pick-2.jpg`, `pick-3.jpg`, `pick-4.jpg`

## Step 3: Copy the Template

```bash
# Copy Corrado's card as starting point
cp docs/business/postcards/lapiazza-member-card/corrado-sassi-card.html \
   docs/business/postcards/lapiazza-member-card/NEW-MEMBER-card.html
```

## Step 4: Edit the HTML

Replace in the new file:
1. `<title>` -- member's name
2. Front: `src="images/pick-1.jpg"` etc. -- their 4 photos
3. Back: Name, studio, category, contact lines
4. QR code URL -- change the `data=` parameter to their workshop URL:
   `https://lapiazza.app/workshop/THEIR-SLUG`
   URL-encode it for the QR API.

**QR code generator URL pattern:**
```
https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https%3A%2F%2Flapiazza.app%2Fworkshop%2FTHEIR-SLUG
```

## Step 5: Generate PDF

```bash
node scripts/postcard-to-pdf.js \
  docs/business/postcards/lapiazza-member-card/NEW-MEMBER-card.html \
  docs/business/postcards/lapiazza-member-card/NEW-MEMBER-card.pdf
```

## Step 6: Verify Before Printing

- [ ] Open the PDF -- 2 pages (fronts + backs)
- [ ] Front: 4 different photos, full bleed, no text
- [ ] Back: Member name, contact info, QR code all correct
- [ ] Scan QR with phone -- confirms it opens their workshop page
- [ ] LaPiazza branding at bottom with wolf logo
- [ ] Bilingual CTA: "Your neighbors are already here" + Italian
- [ ] No text cut off or overflowing the card edges
- [ ] Send PDF to member for approval before printing

## Step 7: Print at ISOTTO

Copy PDF to USB and deliver to ISOTTO Sport with these instructions:
- A4 Landscape
- 300gsm paper (or 170gsm for draft/sample)
- Full color both sides
- SHORT EDGE FLIP duplex (Voltare sul lato corto)
- 100% scale, no margins
- 2 cuts: horizontal at 105mm, vertical at 148.5mm

## Card Specifications

| Property | Value |
|----------|-------|
| Card size | 142.5mm x 99mm |
| Page size | A4 Landscape (297 x 210mm) |
| Cards per sheet | 4 |
| Front | Full-bleed photo, unique per card |
| Back | Member info + LaPiazza branding |
| QR code | Links to member's workshop page (never goes stale) |
| Languages | English + Italian |

## Pricing Guide

| Quantity | Sheets | Print Cost (est.) | Suggested Price |
|----------|--------|-------------------|-----------------|
| 4 cards (sample) | 1 | EUR 1-2 | FREE (onboarding) |
| 20 cards | 5 | EUR 5-10 | EUR 10 |
| 100 cards | 25 | EUR 25-50 | EUR 40 |

First batch is FREE for the first 10 members -- sponsored by Angel to onboard them.

## Template Files

```
docs/business/postcards/lapiazza-member-card/
  corrado-sassi-card.html    -- Corrado's card (reference/template)
  corrado-sassi-card.pdf     -- Corrado's print-ready PDF
  PRINT-INSTRUCTIONS.md      -- ISOTTO print specs for Corrado
  MEMBER-CARD-SOP.md         -- THIS FILE
  images/
    pick-1.jpg ... pick-4.jpg  -- Current member's photos
    wolf-logo.png              -- LaPiazza wolf logo
```

## Design Principles

1. **Front is 100% the member's.** No LaPiazza branding on the photo side.
2. **Back serves two purposes:** business card for the member + recruitment for LaPiazza.
3. **QR links to workshop page** (not a specific item) -- never goes stale.
4. **Bilingual** -- English + Italian on every card.
5. **Big fonts** -- readable without glasses. Boomers are the target.
6. **"Your neighbors are already here"** -- FOMO, not a sales pitch.
7. **"Zero fees. Zero catches."** -- addresses suspicion directly.

---

*Created: March 23, 2026*
*"The postcard is the handshake. The coffee is the close."*
