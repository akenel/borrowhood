# LaPiazza Member Business Card -- Print Instructions

**Client:** Corrado Sassi (PoC -- first member card)
**Date:** March 23, 2026
**Printer:** ISOTTO Sport, Trapani

---

## Files

| File | Purpose |
|------|---------|
| `corrado-sassi-card.pdf` | Print-ready PDF (2 pages: fronts + backs) |
| `corrado-sassi-card.html` | Source HTML (for edits, regenerate with Puppeteer) |
| `images/` | Photos and wolf logo used by the HTML |

## Print Settings

| Setting | Value |
|---------|-------|
| **Paper** | A4 (297 x 210mm) |
| **Orientation** | Landscape |
| **Paper weight** | 300gsm (business card stock) or 170gsm (PoC sample) |
| **Color** | Full color, both sides |
| **Duplex** | YES -- SHORT EDGE FLIP (Voltare sul lato corto) |
| **Scale** | 100% (no scaling, no fit-to-page) |
| **Margins** | None (borderless if possible) |

## CRITICAL: Short Edge Flip

The backs are designed for SHORT EDGE duplex printing.
- Page 1 = Fronts (4 photo cards)
- Page 2 = Backs (4 info cards)
- When printed duplex with short-edge flip, each front aligns with its back.

Tell the printer: **"Stampa fronte-retro, voltare sul lato CORTO"**

## Cutting

After printing, TWO cuts produce 4 identical cards:

```
   ┌──────────────┬──────────────┐
   │              │              │
   │   Card 1     │   Card 2     │
   │              │              │
   │──── CUT 1 (horizontal) ────│  at 105mm from top
   │              │              │
   │   Card 3     │   Card 4     │
   │              │              │
   └──────────────┴──────────────┘
                  ^
             CUT 2 (vertical) at 148.5mm from left
```

| Cut | Direction | Position |
|-----|-----------|----------|
| Cut 1 | Horizontal | 105mm from top edge |
| Cut 2 | Vertical | 148.5mm from left edge |

**Result:** 4 cards, each 142.5mm x 99mm (slightly larger than standard business card 85x55mm)

## Card Layout

**Front (per card):** Full-bleed photograph, no text. Each of the 4 cards has a DIFFERENT image.

**Back (all 4 identical):**
- Top: QR code + member name, studio, category, contact info
- Bottom (gray strip): LaPiazza.app branding + bilingual CTA

## Order Quantity

| Sheets | Cards | Cost (est.) |
|--------|-------|-------------|
| 1 | 4 | EUR 1-2 |
| 5 | 20 | EUR 5-10 |
| 25 | 100 | EUR 25-50 |

## Quality Checklist

- [ ] Photos are sharp and not pixelated
- [ ] QR code scans correctly (test with phone camera)
- [ ] QR opens: https://lapiazza.app/workshop/artemisthinking-gmail-com
- [ ] Text is readable without glasses
- [ ] Front/back alignment is correct after cutting
- [ ] Colors match screen (no dark shadows from printer)

## To Regenerate PDF

If you need to edit the HTML and regenerate:

```bash
node scripts/postcard-to-pdf.js \
  docs/business/postcards/lapiazza-member-card/corrado-sassi-card.html \
  docs/business/postcards/lapiazza-member-card/corrado-sassi-card.pdf
```

Requires: Node.js + Puppeteer (Chrome headless)

---

*"Every wall is a gallery." -- Corrado Sassi*
