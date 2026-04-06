# Disaster Recovery SOP -- La Piazza (BorrowHood)

**Last tested:** April 6, 2026 -- PASSED (328 users, 813 items, all rows matched)

---

## How Backups Work

- **Automatic hourly backups** via cron on Hetzner
- Runs every hour at :00
- Full Postgres dump, gzipped (~770KB)
- 48 backups kept (2 days of hourly recovery points)
- Older backups auto-deleted
- Backup location: `/opt/backups/borrowhood/`
- Log file: `/opt/backups/borrowhood/backup.log`

---

## Quick Reference

### Check backup health
```bash
ssh root@46.62.138.218 "ls -lh /opt/backups/borrowhood/*.sql.gz | tail -5"
```

### Check backup log
```bash
ssh root@46.62.138.218 "tail -20 /opt/backups/borrowhood/backup.log"
```

### Download latest backup to your laptop
```bash
ssh root@46.62.138.218 "ls -t /opt/backups/borrowhood/*.sql.gz | head -1"
# Copy the filename, then:
scp root@46.62.138.218:/opt/backups/borrowhood/borrowhood_XXXXXXXX_XXXX.sql.gz ~/Desktop/
```

---

## SCENARIO 1: Test the Backup (Safe -- No Downtime)

**When:** Monthly, or anytime you're nervous.
**Risk:** ZERO. Uses a separate test database.

```bash
ssh root@46.62.138.218

# 1. Create a test database
docker exec postgres psql -U helix_user -d postgres -c "CREATE DATABASE borrowhood_dr_test OWNER helix_user;"

# 2. Find the latest backup
ls -t /opt/backups/borrowhood/*.sql.gz | head -1
# Example output: /opt/backups/borrowhood/borrowhood_20260406_0905.sql.gz

# 3. Restore into the test database
gunzip -c /opt/backups/borrowhood/borrowhood_20260406_0905.sql.gz | docker exec -i postgres psql -U helix_user -d borrowhood_dr_test

# 4. Verify -- count rows
docker exec postgres psql -U helix_user -d borrowhood_dr_test -c "SELECT count(*) FROM bh_user;"
docker exec postgres psql -U helix_user -d borrowhood_dr_test -c "SELECT count(*) FROM bh_item;"

# 5. Compare to production
docker exec postgres psql -U helix_user -d borrowhood -c "SELECT count(*) FROM bh_user;"
docker exec postgres psql -U helix_user -d borrowhood -c "SELECT count(*) FROM bh_item;"

# 6. If counts match: SUCCESS. Clean up:
docker exec postgres psql -U helix_user -d postgres -c "DROP DATABASE borrowhood_dr_test;"
```

---

## SCENARIO 2: Database Corrupted -- Restore from Backup

**When:** Database won't start, data is corrupted, someone ran a bad query.
**Downtime:** ~2 minutes.

```bash
ssh root@46.62.138.218

# 1. Stop the app (prevents new writes)
cd /opt/helixnet/hetzner
docker compose -f docker-compose.uat.yml stop borrowhood

# 2. Find the latest GOOD backup
ls -lh /opt/backups/borrowhood/*.sql.gz | tail -10
# Pick the one from BEFORE the corruption happened

# 3. Drop and recreate the database
docker exec postgres psql -U helix_user -d postgres -c "DROP DATABASE borrowhood;"
docker exec postgres psql -U helix_user -d postgres -c "CREATE DATABASE borrowhood OWNER helix_user;"

# 4. Restore
gunzip -c /opt/backups/borrowhood/borrowhood_XXXXXXXX_XXXX.sql.gz | docker exec -i postgres psql -U helix_user -d borrowhood

# 5. Restart the app
docker compose -f docker-compose.uat.yml up -d borrowhood

# 6. Verify the site works
curl -s http://localhost:8000/api/v1/health
# Should return: {"status": "healthy", "app": "La Piazza", ...}

# 7. Check data
docker exec postgres psql -U helix_user -d borrowhood -c "SELECT count(*) FROM bh_user;"
```

---

## SCENARIO 3: Hetzner Server Dead -- Full Rebuild

**When:** Server is gone. Starting from zero on a new server.

```bash
# 1. Get a new server (Hetzner, any provider with Docker)

# 2. Install Docker + Docker Compose
curl -fsSL https://get.docker.com | sh

# 3. Clone the repo
git clone https://github.com/akenel/borrowhood.git /opt/helixnet/BorrowHood

# 4. Set up the compose directory
mkdir -p /opt/helixnet/hetzner
# Copy docker-compose.uat.yml and borrowhood.env from your laptop backup
# OR recreate borrowhood.env with the secrets:
#   - BH_DATABASE_URL
#   - BH_KEYCLOAK_URL, CLIENT_ID, CLIENT_SECRET
#   - BH_OLLAMA_URL, BH_OLLAMA_KEY, BH_OLLAMA_MODEL
#   - BH_TELEGRAM_BOT_TOKEN
#   - BH_GOOGLE_API_KEY (optional)
#   - PayPal/Stripe keys

# 5. Start Postgres
docker compose -f docker-compose.uat.yml up -d postgres
# Wait for it to be healthy

# 6. Restore from backup (if you have one)
gunzip -c borrowhood_backup.sql.gz | docker exec -i postgres psql -U helix_user -d borrowhood

# 7. OR seed from scratch (if no backup)
docker compose -f docker-compose.uat.yml up -d borrowhood
# The app auto-seeds on first start

# 8. Start Keycloak + Caddy
docker compose -f docker-compose.uat.yml up -d

# 9. Update DNS to point to new server IP
# DuckDNS: https://www.duckdns.org
# OR Porkbun: update lapiazza.app A record

# 10. Verify
curl https://lapiazza.app/api/v1/health
```

---

## SCENARIO 4: Accidentally Deleted Data (Single Table)

**When:** "I deleted all the reviews by mistake!"

```bash
ssh root@46.62.138.218

# 1. Find a backup from BEFORE the deletion
ls -lh /opt/backups/borrowhood/*.sql.gz

# 2. Restore into a temp database
docker exec postgres psql -U helix_user -d postgres -c "CREATE DATABASE borrowhood_recovery OWNER helix_user;"
gunzip -c /opt/backups/borrowhood/borrowhood_XXXXXXXX_XXXX.sql.gz | docker exec -i postgres psql -U helix_user -d borrowhood_recovery

# 3. Copy JUST the table you need back to production
docker exec postgres pg_dump -U helix_user -d borrowhood_recovery --table=bh_review --data-only | docker exec -i postgres psql -U helix_user -d borrowhood

# 4. Verify
docker exec postgres psql -U helix_user -d borrowhood -c "SELECT count(*) FROM bh_review;"

# 5. Clean up
docker exec postgres psql -U helix_user -d postgres -c "DROP DATABASE borrowhood_recovery;"
```

---

## Secrets Checklist

These are NOT in git. If you lose the server, you need these from memory/password manager:

| Secret | Where to get it |
|--------|----------------|
| Keycloak admin password | You set it during setup |
| Keycloak client secret | Keycloak admin UI > Clients > borrowhood |
| Ollama API key | https://ollama.com > Settings > Keys |
| Telegram bot token | @BotFather on Telegram |
| Google API key | console.cloud.google.com |
| DuckDNS token | https://www.duckdns.org |
| Porkbun API key | https://porkbun.com/account/api |
| PayPal client ID/secret | developer.paypal.com |
| Stripe keys | dashboard.stripe.com |

**TIP:** Keep a copy of `borrowhood.env` in your password manager (1Password, Bitwarden, etc). That one file has everything.

---

## Cron Verification

The backup cron should be running. To verify:

```bash
ssh root@46.62.138.218 "crontab -l | grep borrowhood"
# Expected: 0 * * * * /opt/backups/borrowhood/backup.sh >> /opt/backups/borrowhood/backup.log 2>&1
```

If it's missing, re-add it:
```bash
ssh root@46.62.138.218
(crontab -l 2>/dev/null; echo '0 * * * * /opt/backups/borrowhood/backup.sh >> /opt/backups/borrowhood/backup.log 2>&1') | crontab -
```

---

*"If one seal fails, check all the seals."*
*Test your backups. The backup you don't test is the backup that doesn't work.*
