# SOP: Chrome DevTools MCP — Tiger Drives the Browser

*"Stop screenshotting for me, bro. I'll drive."*

---

## What This Is

**Chrome DevTools MCP** is a Model Context Protocol server from the Chrome team that gives an AI agent (me, Tigs) direct control of a Chrome browser: navigate, resize viewport, click, fill forms, read console, capture screenshots, run Lighthouse audits, trace performance.

Before this: Angel screenshots → Tigs guesses → Angel refreshes → repeat.
After this: Tigs opens Chrome at 360px, screenshots, fixes, verifies — all without Angel.

---

## Why We Use It

| Task | Before MCP | With MCP |
|---|---|---|
| Mobile nav at 360px look-check | Angel opens DevTools, takes screenshot, pastes | Tigs emulates iPhone SE, captures PNG |
| Verify a CSS fix went live | Angel refreshes, re-screenshots | Tigs reloads the page in the driven browser |
| Hit every page in the 10-rule Fat-Finger audit | Angel clicks 20 links, screenshots each | Tigs walks the URL list once, returns a bundle |
| Console errors during a flow | Angel opens Console tab, pastes red text | Tigs reads console output directly |
| Lighthouse score | Angel runs manually, screenshots scores | Tigs runs audit, returns JSON |
| Network waterfall during a broken API call | Angel exports HAR | Tigs lists requests with timings |

---

## Prerequisites (one-time, per dev machine)

### 1. Node.js 20.19+ or 22.12+ or 23+
The MCP server's `package.json` engines field rejects anything below this.

**Current machine check:**
```bash
node --version
# v18.x → must upgrade
# v20.19+ / v22.12+ → OK
```

**Upgrade on Debian (nodesource repo):**
```bash
# Nuke old nodesource, install 22 LTS
sudo apt-get remove -y nodejs
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # should be v22.x
npm --version   # should be 10.x or 11.x
```

### 2. Google Chrome installed
The MCP spawns its own Chrome instance (in a dedicated profile). Already set up on this box at `/usr/bin/google-chrome` (147.x, installed via `.deb` because the Chromium snap was broken on Debian 12).

### 3. `.mcp.json` entry in the project
Already wired in `BorrowHood/.mcp.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--headless",
        "--no-usage-statistics"
      ]
    }
  }
}
```

Flags explained:
- `-y` — skip npx's interactive install prompt
- `--headless` — no visible Chrome window (keeps the AI-driven instance separate from Angel's browsing)
- `--no-usage-statistics` — opt out of Chrome usage telemetry for the spawned instance

---

## Activation Procedure

1. **Upgrade Node** (above) if not done
2. **Restart Claude Code** — MCP servers are loaded at session start, not on-the-fly
3. **Approve the server on first run** — Claude Code prompts once per project; hit "yes"
4. **Verify** — ask Tigs: "list your MCP tools starting with mcp__chrome-devtools__" — should return 29 tools

---

## How Tiger Uses It (Cheatsheet)

When Angel says "check the mobile nav at 360px", Tigs does this internally:

```
1. mcp__chrome-devtools__emulate_device     → set viewport 360x640
2. mcp__chrome-devtools__navigate           → https://lapiazza.app/
3. mcp__chrome-devtools__screenshot         → capture, analyze
4. (if change needed) edit template, deploy
5. mcp__chrome-devtools__reload             → bust cache
6. mcp__chrome-devtools__screenshot         → verify fix
```

**Angel doesn't have to refresh anything.** Just says "fix it" or "next rule".

---

## The 10-Rule Audit Flow (automated)

For the Fat-Finger UX audit against `docs/SOP-FAT-FINGER-UX.md`, Tigs can walk the whole list at 360px:

| Rule | Automated check |
|---|---|
| 1. 60px primary CTA | `evaluateScript` returns button heights |
| 2. 8px spacing | DOM rect calculation |
| 3. One primary action | visual check via screenshot |
| 4. 16px body text | computed `font-size` via `getComputedStyle` |
| 5. Bottom tab bar | screenshot |
| 6. Kill hamburger | screenshot of top nav |
| 7. No hover UX | click elements, check if they do anything |
| 8. Undo over confirm | flow test: click "cancel ticket", check for toast vs modal |
| 9. Wizard long forms | screenshot /raffles/create, count visible inputs |
| 10. 360px works | the viewport setting IS the test |

The output is a bullet list per page: "PASS / FAIL / needs fix — here's the selector".

---

## Security Boundaries (don't fight these)

1. **Only drive Chrome on trusted sites.** Driven Chrome with remote debug port is not something you point at a banking login.
2. **Headless means no persistent state by default.** If an audit needs login, Tigs uses the "demo login" route (`pages.py` line 668, the 14 cast members), never real Keycloak.
3. **Screenshots land in agent memory, not disk.** If Angel wants a permanent artifact, Tigs saves explicitly to `Bro_Kit/uat/screenshots/`.
4. **Never commit the Chrome DevTools MCP user data dir** if it ever leaks into the repo tree. Add to `.gitignore` if it appears.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "npx error: unsupported engine" | Node < 20.19 — upgrade per prereqs |
| MCP tool not listed in Tigs | Claude Code needs restart after `.mcp.json` edit |
| "Chrome not found" | Install `google-chrome-stable` .deb (see CLAUDE.md — the snap is broken on Debian 12) |
| Headless Chrome hangs on Wayland | MCP spawns its own; not affected by Angel's Wayland session |
| Screenshots all blank | Probably navigated before page loaded — use `waitFor` first |
| Can't access localhost | The MCP's Chrome runs as same user; localhost:8000 works once local uvicorn works (separate blocker: stale DB IP in `.env`) |

---

## When NOT to Use It

- **Cross-browser testing** — Chrome only. For Firefox/Safari parity, use Playwright MCP or manual testing.
- **Visual regression** — no pixel-diff. If we need pre/post image diffs, we shell out to ImageMagick or a separate tool.
- **Real-device testing** — emulation ≠ actual Android. Angel's phone is still the final gate for important screens.

---

## The Tiger-Wolf Rule

**Angel still drives the narrative; Tiger drives the browser.**

- Angel says what to check → Tigs executes the audit
- Angel says what's wrong → Tigs proposes + applies the fix
- Angel says "ship" → Tigs commits, pushes, deploys
- Angel says "next" → Tigs moves down the checklist

Tiger does not invent UX opinions. Tiger executes, measures, reports.

---

*"If one seal fails, check all the seals. If one nav button overlaps, run the 10-rule audit on all 26 pages."*

*— Tiger + Wolf, La Piazza, Trapani*
*Filed April 18, 2026 alongside the mobile UX punchlist*
