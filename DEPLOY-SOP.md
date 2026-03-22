# La Piazza -- Deploy SOP

**One branch. One truth. No shortcuts.**

---

## The Golden Rule

```
Build -> Commit -> Push -> Pull -> Restart (if needed) -> Smoke Test
```

Every. Single. Time. In that order. No skipping steps.

---

## What Changed -> What To Do

| What you changed | git pull | Restart container | Rebuild container | ALTER TABLE |
|------------------|----------|-------------------|-------------------|-------------|
| Templates (HTML/Jinja2) | YES | NO | NO | NO |
| Locale files (en.json, it.json) | YES | YES | NO | NO |
| Python code (routers, models, services) | YES | -- | YES (rebuild) | NO |
| New DB column on existing table | YES | -- | YES (rebuild) | YES |
| New DB table (brand new model) | YES | -- | YES (rebuild) | NO (create_all handles it) |
| Static files (JS, CSS, images) | YES | NO | NO | NO |
| Keycloak realm JSON | N/A | N/A | N/A | Admin API or nuke KC DB |
| Keycloak theme files | YES | Restart KC | NO | NO |
| Service worker (sw.js) | YES | NO | NO | Bump CACHE_NAME |
| requirements.txt | YES | -- | YES (rebuild) | NO |
| Dockerfile | YES | -- | YES (rebuild) | NO |
| Caddyfile | N/A | Restart Caddy | NO | NO |

---

## Commands

### Template-only deploy (fastest)
```bash
git push origin main
ssh root@46.62.138.218 "cd /opt/helixnet/BorrowHood && git pull origin main"
```

### Locale file deploy (needs restart)
```bash
git push origin main
ssh root@46.62.138.218 "cd /opt/helixnet/BorrowHood && git pull origin main"
ssh root@46.62.138.218 "cd /opt/helixnet/hetzner && docker compose -f docker-compose.uat.yml restart borrowhood"
```

### Python code deploy (needs rebuild)
```bash
git push origin main
ssh root@46.62.138.218 "cd /opt/helixnet/BorrowHood && git pull origin main"
ssh root@46.62.138.218 "cd /opt/helixnet/hetzner && docker compose -f docker-compose.uat.yml up -d --build --no-deps borrowhood"
```

### New column on existing table
```bash
# 1. Push and pull
git push origin main
ssh root@46.62.138.218 "cd /opt/helixnet/BorrowHood && git pull origin main"

# 2. Add the column (SQLAlchemy create_all does NOT alter existing tables)
ssh root@46.62.138.218 "docker exec postgres psql -U helix_user -d borrowhood -c \
  \"ALTER TABLE bh_xxx ADD COLUMN IF NOT EXISTS col_name VARCHAR(500);\""

# 3. Rebuild
ssh root@46.62.138.218 "cd /opt/helixnet/hetzner && docker compose -f docker-compose.uat.yml up -d --build --no-deps borrowhood"
```

### Automated deploy script
```bash
bash scripts/deploy-prod.sh              # Full rebuild
bash scripts/deploy-prod.sh --templates-only  # Templates only
```

---

## Keycloak Changes

Keycloak ignores the realm JSON after first boot (`IGNORE_EXISTING` strategy).

| What you want | How to do it |
|---------------|-------------|
| Add/change IDP, mapper, or setting | Admin API: `POST /admin/realms/borrowhood/partialImport` with `ifResourceExists: OVERWRITE` |
| Update realm setting (e.g. password policy) | Admin API: `PUT /admin/realms/borrowhood` |
| Full realm reset | Drop KC database (`helix_db`), restart KC. BorrowHood data (`borrowhood` DB) is NOT affected. |
| Theme change | Restart KC container. Clear cache: `rm -rf /data/tmp/kc-gzip-cache` inside container. |

---

## Lessons Learned (the hard way)

### 1. SCP is not a deploy (March 22, 2026)
SCP'd files to server without committing. Git repo drifted from reality.
30+ files on the server didn't match git. Took an hour to untangle.
**Rule:** Never SCP. Always commit -> push -> pull.

### 2. Locale files are cached in memory (March 22, 2026)
Changed `en.json` and `it.json`, did `git pull`, but button still showed raw key.
Python loads locale files once at startup and caches them.
**Rule:** Locale changes need container restart (not just pull).

### 3. SQLAlchemy create_all doesn't ALTER (March 22, 2026)
Added `message_type`, `offered_price` columns to `bh_message`. Rebuilt container.
Columns didn't appear. `create_all()` only creates NEW tables, not new columns on existing ones.
**Rule:** New columns on existing tables need manual `ALTER TABLE`.

### 4. CSS inside `<style type="text/tailwindcss">` is invisible to browsers (March 22, 2026)
Put `html { font-size: 24px }` inside Tailwind's special style tag. Browsers skip
unknown style types entirely. Only Tailwind's JS processes it -- unreliably.
**Rule:** Regular CSS goes in regular `<style>` tags. Only Tailwind utilities in the special tag.

### 5. Tailwind JS overrides static CSS (March 22, 2026)
Even after moving to `<style>`, Tailwind's runtime-generated styles overrode our font-size.
**Rule:** Use `!important` when you need to override Tailwind's generated styles.

### 6. Service worker caches stale HTML (March 22, 2026)
Old SW cache (`bh-v1`) served stale pages to logged-out users. Logged-in pages were fresh
because auth changes the response (cache miss).
**Rule:** Bump `CACHE_NAME` in `sw.js` when HTML structure changes significantly. Current: `lp-v2`.

### 7. v2-dev branch caused drift (March 22, 2026)
Server was on `main`, local was on `v2-dev`. Deploy script referenced `v2-dev`.
Merge commits on `main` made the history confusing.
**Rule:** Solo team = one branch (`main`). v2-dev deleted.

### 8. `docker compose restart` doesn't reload env vars (earlier lesson)
Only `docker compose up -d` recreates the container with fresh env.
**Rule:** Use `up -d` for env/config changes, `restart` only for code reloads.

### 9. Translation keys with Jinja2 syntax don't work (March 22, 2026)
`"pause_all": "Pause All ({{ active_count }})"` -- the `{{ }}` inside the translation
value is not re-processed by Jinja2. The `t()` function returns the literal string.
**Rule:** Never put template syntax inside translation values. Render variables separately in the template.

---

## Smoke Test Checklist

After every deploy:

```
curl -sf "https://lapiazza.app/api/v1/health"     # API healthy
curl -sf -o /dev/null -w "%{http_code}" "https://lapiazza.app/"         # Home 200
curl -sf -o /dev/null -w "%{http_code}" "https://lapiazza.app/browse"   # Browse 200
curl -sf -o /dev/null -w "%{http_code}" "https://lapiazza.app/profile"  # Profile 200
```

## Test Suite

```bash
.venv/bin/python -m pytest tests/test_auth.py tests/test_pages.py -v
```

25 auth tests + 12 page tests = 37 tests that run without a database.
If any auth test fails, login is broken -- do NOT deploy.

---

## Server Quick Reference

| What | Where |
|------|-------|
| App code | `/opt/helixnet/BorrowHood/src/` |
| Compose file | `/opt/helixnet/hetzner/docker-compose.uat.yml` |
| App container | `borrowhood` |
| App DB | `borrowhood` (Postgres) |
| KC DB | `helix_db` (Postgres, separate) |
| Uploads | `/opt/helixnet/BorrowHood/src/static/uploads/` (bind-mounted, persists across rebuilds) |
| Env vars | `/opt/helixnet/hetzner/borrowhood.env` (server-only, NOT in git) |
| Domain | `lapiazza.app` |
| Server IP | `46.62.138.218` |
| SSH | `ssh root@46.62.138.218` |

---

*Created: March 22, 2026 -- Night shift lessons*
*"If one seal fails, check all the seals."*
