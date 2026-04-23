# Staging Environment Setup

**Goal:** A near-production mirror where we test every commit before it reaches real users.

**Decision log (April 23, 2026):**
- Same Hetzner box (CX32). Second container + second DB on same postgres instance. ~EUR 0 extra.
- `staging.lapiazza.app` via Cloudflare DNS (A record, no proxy). Let's Encrypt through Caddy.
- Auto-deploy to staging on push to `main`. Manual promote to prod on Angel's `deploy` command.
- Gate B: pytest green + clean git tree required before prod promotion.

---

## Architecture

```
                    46.62.138.218 (Hetzner CX32)
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Caddy (ports 80/443)                                      │
│   ├─ lapiazza.app → borrowhood (prod)                      │
│   └─ staging.lapiazza.app → borrowhood_staging             │
│                                                            │
│  ┌─────────────────┐   ┌─────────────────────────┐         │
│  │ borrowhood      │   │ borrowhood_staging      │         │
│  │ (prod)          │   │ mem: 1GB, cpu: 1.0      │         │
│  │ env: .env       │   │ env: .env.staging       │         │
│  └────────┬────────┘   └────────┬────────────────┘         │
│           │                     │                          │
│           ▼                     ▼                          │
│  ┌────────────────────────────────────────┐                │
│  │ postgres (one instance, two databases) │                │
│  │  ├─ borrowhood        (prod, real)     │                │
│  │  └─ borrowhood_staging (staging, fake) │                │
│  └────────────────────────────────────────┘                │
│                                                            │
│  ┌────────────────────────────────────────┐                │
│  │ keycloak (one instance, two realms)    │                │
│  │  ├─ realm: borrowhood         (prod)   │                │
│  │  └─ realm: borrowhood-staging (staging)│                │
│  └────────────────────────────────────────┘                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Changes to each layer

### 1. Cloudflare DNS (Angel does)
- Add A record: `staging` → `46.62.138.218`
- Proxy status: **DNS only** (grey cloud). Direct TLS via Caddy's Let's Encrypt.
- TTL: 1 minute during setup, can raise to auto after confirmed.

### 2. Postgres (one shell command)
```sql
CREATE DATABASE borrowhood_staging;
CREATE USER staging_user WITH PASSWORD '<generated>';
GRANT ALL PRIVILEGES ON DATABASE borrowhood_staging TO staging_user;
```
Note: we'll seed staging by dumping prod and restoring (or running fresh migrations + a small seed script).

### 3. Keycloak (~5 min UI work or JSON import)
- Admin Console → Create realm `borrowhood-staging`
- Copy client config from `borrowhood` realm (client ID `borrowhood-web`)
- Redirect URIs: `https://staging.lapiazza.app/*`
- Copy identity provider config (GitHub/Google/Facebook) OR leave blank and use username/password only for staging (simpler).

### 4. New files in the repo
- `hetzner/docker-compose.staging.yml` — single service `borrowhood_staging`, overlay on main compose
- `hetzner/Caddyfile` — add `staging.lapiazza.app { ... }` block
- `hetzner/.env.staging` — staging secrets (NEVER committed; stored on server only)
- `scripts/deploy-prod.sh` — one-click prod promotion with checks
- `scripts/deploy-staging.sh` — auto-deploy helper (called by CI)
- `.github/workflows/deploy-staging.yml` — GitHub Action

### 5. Code changes (small)
- `src/config.py` reads `BH_ENVIRONMENT` env var (default `prod`)
- Footer or small corner badge shows "STAGING" when `BH_ENVIRONMENT=staging`
- `NOTIFY_TELEGRAM_ENABLED=false` by default on staging

---

## Deploy pipeline

### Auto-staging on push to main
1. GitHub push triggers `deploy-staging.yml`
2. Workflow SSHs to Hetzner, pulls latest, rebuilds `borrowhood_staging` image, restarts container
3. Angel gets notified (Telegram? email? TBD — minimal for now: workflow status)

### Manual prod promotion
```bash
./scripts/deploy-prod.sh <commit-or-tag>
```
Script checks:
- Git tree clean (`git status` empty)
- `pytest tests/ -q` passes
- Commit exists on `origin/main`
- Prompts: "Deploy <sha> to production? [yes/no]"
- If confirmed: pulls, rebuilds, restarts prod container
- Tags the commit as `prod-<date>` for audit

**Only Angel can run this script.** There's no automated prod deploy.

---

## Concerns I'll flag before we flip the switch

1. **Shared Keycloak user base.** If a prod user (e.g. Gemma) navigates to staging, they hit the staging realm and cannot log in with their prod credentials. Good — isolates data. Document this.
2. **Shared MinIO storage.** Files uploaded on staging go to the same bucket. Low risk (file URLs are unguessable), but we should namespace staging uploads under `staging/` prefix.
3. **Shared email server (MailHog).** Both environments send to the same MailHog inbox. Fine for now — just be aware messages mix.
4. **Shared Telegram bot.** Staging must NOT use the prod bot token, or test notifications go to real phones. Set `NOTIFY_TELEGRAM_ENABLED=false` on staging or create a second bot.
5. **Staging DB seed drift.** Staging DB won't have prod's real users by default. Option A: periodic anonymized dump from prod. Option B: staging has fake users only. Start with B.
6. **SW cache.** PWA installed at prod origin has its own cache. Installing at staging origin is a separate install. Users should never see both.

---

## Order of operations tonight

1. ☐ Angel creates Cloudflare A record for `staging.lapiazza.app` → `46.62.138.218`
2. ☐ I write code changes (env awareness + staging badge)
3. ☐ I write `docker-compose.staging.yml` + Caddyfile addition + `deploy-prod.sh`
4. ☐ On server: create `borrowhood_staging` database
5. ☐ On server: create `borrowhood-staging` KC realm (Angel UI click or JSON import)
6. ☐ On server: write `.env.staging`
7. ☐ First staging deploy manually: `docker compose -f docker-compose.staging.yml up -d`
8. ☐ Caddy reload
9. ☐ Smoke: curl `https://staging.lapiazza.app/` → 200
10. ☐ MCP smoke as a staging test user
11. ☐ GitHub Actions workflow (optional — can defer to tomorrow if tired)
12. ☐ Update CLAUDE.md / MEMORY.md with new workflow
