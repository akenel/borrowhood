# What's New — Weekly La Piazza Posts

Friendly, share-ready summaries for Founding 20 + community Telegram/WhatsApp blasts.

## Workflow

Every Friday (or end of a sprint):

1. **Generate the technical changelog** — `docs/CHANGELOG.md` is the source of truth. Add the week's section there first (Keep-a-Changelog format).
2. **Write the friendly version** — copy this week's section into a new file `Bro_Kit/whats-new/YYYY-MM-DD.md`. Translate dev-speak to human:
   - `feat(orders): 8-box segmented lockbox code input` → "Picking up a rental? The code entry is now an 8-box OTP-style input."
   - Strip BL-XXX numbers, internal refactors, schema fixes.
   - Group into: ✨ New Things, 🔧 Polish, 🐛 Bugs Squashed, 🛡️ Trust & Safety.
3. **Sign with the Crew** — `— The La Piazza Crew 🐺`
4. **Share** — Telegram, WhatsApp, founding-20 list, eventual `/whats-new` page.

## Quick Generation

If a week's commits are in front of you and you want a fast draft:

```bash
git log --since="7 days ago" --pretty=format:"%h %ad %s" --date=short --no-merges
```

Then paste into the changelog-generator skill (or ask Tigs).

## Tone Rules

- Member-first language. "You" not "users".
- Lead with what *they* can now do, not what *we* built.
- Numbers help: "75 commits, 20 bugs killed" feels real.
- Keep it under one screen on mobile.
- One emoji per section header. No emoji explosion.
- Italian touches welcome but don't force it.

## Files

- `2026-04-25.md` — first weekly post (April 19–25 work)
