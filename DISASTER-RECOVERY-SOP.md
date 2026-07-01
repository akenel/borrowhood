# Disaster Recovery SOP -- La Piazza (BorrowHood) + Banco

> **This box runs TWO production databases. This SOP covers BOTH.**
> - **PART 1 — `borrowhood`** (La Piazza): hourly, plaintext gzip, `/opt/backups/borrowhood/`. *(below)*
> - **PART 2 — `banco_prod`** (Banco POS — the DB Felix's shop runs on): daily, **GPG-encrypted**,
>   restore-drilled, and **copied offsite to Google Drive**. Different restore path (you must
>   **decrypt** first). *(jump to [PART 2 — BANCO](#part-2--banco-banco_prod))*
>
> If the box is dead and you need the SHOP back, you want **PART 2, Scenario B3**.

**Last tested:** borrowhood April 6, 2026 -- PASSED (328 users, 813 items). banco_prod restore drill
runs and passes nightly (decrypt+restore, row counts matched — see `/opt/backups/banco/backup.log`).
**banco_prod offsite + KeePass key VERIFIED July 1, 2026** — decrypted an offsite Drive/laptop blob with
the KeePass passphrase → valid `PostgreSQL database dump`. Full DR pair proven (ciphertext ↔ key).

---

# PART 1 — BORROWHOOD (La Piazza)

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

---

# PART 2 — BANCO (`banco_prod`)

**This is the POS database Felix's shop runs on. It is handled differently from borrowhood:**
encrypted at rest, restore-drilled nightly, and copied offsite to Google Drive.

## How Banco Backups Work

- **Nightly** cron on Hetzner: `0 3 * * *` → `/opt/backups/banco_backup.sh`
- Full Postgres dump of `banco_prod`, gzipped, then **GPG-encrypted (AES256)** — dumps hold
  customer PII, so they are ciphertext at rest.
- **Verified restore drill every night:** the fresh blob is DECRYPTED, restored into a throwaway
  DB, and row counts (`transactions`/`products`/`line_items`) are compared. A backup that won't
  decrypt-and-restore fails loudly.
- **30 encrypted blobs** kept on the box: `/opt/backups/banco/banco_prod_*.sql.gz.gpg` (~1 MB each)
- Log: `/opt/backups/banco/backup.log`
- **OFFSITE:** `scripts/ops/banco_offsite_pull.py` (laptop `@hourly`) pulls the blobs box→laptop
  (`~/backups/banco-offsite/`, sha256-verified) then `rclone copy` → **Google Drive**
  `ecolution-gdrive:HelixNet-DB-Backups/banco` (MD5-verified). So Banco backups live in
  **3 places: box + laptop + Drive** — the same Drive as this SOP and the kdbx.

## 🔑 The Encryption Key — WITHOUT IT THE OFFSITE BACKUPS ARE BRICKS

- Lives on the box at `/root/.banco-backup-key` (root-only). The file is **65 bytes = a
  64-character passphrase + a trailing newline**.
- gpg uses **only the first line** (the **64 chars**, no newline). The fingerprint of THAT value —
  the one your KeePass copy must match — is **sha256[:16] = `40a186b8c701f205`**. (The whole-file
  hash `4de994a0ef02fd82` includes the newline and is NOT what gpg uses — don't verify against it.)
- A **copy of the exact 64 chars MUST be in the KeePass kdbx** (which is itself on Drive). The Drive
  blobs are AES256 ciphertext — with no key, they are unrecoverable. Key in kdbx + ciphertext on
  Drive = the DR pair. Get the value with `ssh root@46.62.138.218 'head -1 /root/.banco-backup-key | tr -d "\n"; echo'`.
- **PROVE it works — see "Verify your KeePass key" at the bottom. Do this at least once.**

## Quick Reference (Banco)

```bash
# Check banco backup health (box)
ssh root@46.62.138.218 "ls -lh /opt/backups/banco/*.sql.gz.gpg | tail -5; tail -5 /opt/backups/banco/backup.log"

# Check the offsite copies (laptop)
cat ~/backups/banco-offsite/STATUS.txt
rclone lsf ecolution-gdrive:HelixNet-DB-Backups/banco | tail -5
```

---

## SCENARIO B1: Test the Banco Backup (Safe -- No Downtime)

**When:** Monthly, or anytime you're nervous. **Risk:** ZERO (throwaway DB). This mirrors the
automatic nightly drill — run it by hand to see it pass with your own eyes.

```bash
ssh root@46.62.138.218
KEY=/root/.banco-backup-key
FILE=$(ls -t /opt/backups/banco/banco_prod_*.sql.gz.gpg | head -1)
echo "Testing: $FILE"

# 1. throwaway DB
docker exec postgres psql -U helix_user -d postgres -c "CREATE DATABASE banco_dr_test OWNER helix_user;"

# 2. DECRYPT -> gunzip -> restore  (the extra decrypt step vs borrowhood)
gpg --batch --quiet --decrypt --passphrase-file "$KEY" "$FILE" | gunzip \
  | docker exec -i postgres psql -U helix_user -d banco_dr_test

# 3. compare row counts to production
docker exec postgres psql -U helix_user -d banco_dr_test -c "SELECT count(*) FROM transactions;"
docker exec postgres psql -U helix_user -d banco_prod    -c "SELECT count(*) FROM transactions;"

# 4. counts match = SUCCESS. clean up:
docker exec postgres psql -U helix_user -d postgres -c "DROP DATABASE banco_dr_test;"
```

---

## SCENARIO B2: Banco DB Corrupted -- Restore on the Box

**When:** `banco_prod` is corrupted / a bad query wrecked it, but the box is alive.
**Downtime:** ~2 minutes. **⚠ Back up the current state first if you possibly can.**

```bash
ssh root@46.62.138.218
KEY=/root/.banco-backup-key

# 1. stop the Banco app (prevent new writes)
docker stop helix-platform-banco

# 2. pick the latest GOOD encrypted backup (from BEFORE the damage)
ls -lh /opt/backups/banco/banco_prod_*.sql.gz.gpg | tail -10
FILE=/opt/backups/banco/banco_prod_XXXXXXXX_XXXX.sql.gz.gpg

# 3. drop + recreate
docker exec postgres psql -U helix_user -d postgres -c "DROP DATABASE banco_prod;"
docker exec postgres psql -U helix_user -d postgres -c "CREATE DATABASE banco_prod OWNER helix_user;"

# 4. decrypt -> restore
gpg --batch --quiet --decrypt --passphrase-file "$KEY" "$FILE" | gunzip \
  | docker exec -i postgres psql -U helix_user -d banco_prod

# 5. restart + verify
docker start helix-platform-banco
sleep 5 && curl -s https://banco.lapiazza.app/api/v1/health
docker exec postgres psql -U helix_user -d banco_prod -c "SELECT count(*) FROM transactions;"
```

---

## SCENARIO B3: Box is DEAD -- Restore Banco from Google Drive

**When:** Hetzner is gone. This is the scenario P5 exists for — the encrypted backups are safe on
Drive, and you rebuild on a new server. **You need the KeePass kdbx (for the encryption key).**

```bash
# --- on any machine with internet ---
# 1. Get the kdbx from Google Drive, open in KeePass, find the ".banco-backup-key" entry.

# 2. Download the latest Banco backup from Drive (rclone, or the Drive web UI):
rclone copy ecolution-gdrive:HelixNet-DB-Backups/banco ./banco-restore \
  --include "*.sql.gz.gpg" --max-age 2d      # newest blob(s)
cd banco-restore && ls -t *.sql.gz.gpg | head -1

# 3. Stand up the new server: follow PART 1 Scenario 3 steps 1-5 (Docker, clone repo, start postgres),
#    then create the DB:
docker exec postgres psql -U helix_user -d postgres -c "CREATE DATABASE banco_prod OWNER helix_user;"

# 4. DECRYPT with the key from KeePass (paste the passphrase at the prompt), then restore:
gpg --output banco_prod.sql.gz --decrypt banco_prod_XXXXXXXX_XXXX.sql.gz.gpg
gunzip -c banco_prod.sql.gz | docker exec -i postgres psql -U helix_user -d banco_prod

# 5. Start the Banco app + point DNS (banco.lapiazza.app) at the new IP, then verify:
curl https://banco.lapiazza.app/api/v1/health
```

**Also re-arm the safety nets on the new box:** copy `banco_backup.sh` to `/opt/backups/`, restore
the `0 3 * * *` cron, drop the key back to `/root/.banco-backup-key` (from KeePass), and re-point
the laptop offsite pull. See `scripts/ops/README.md`.

---

## ✅ Verify your KeePass key (DO THIS ONCE — the seal check)

The offsite backups are only as good as the key in your kdbx. **Prove your KeePass copy actually
decrypts a real blob** — don't assume the 65-byte box key and your KeePass entry match.

```bash
# On the LAPTOP (has an offsite blob already). Paste the passphrase from KeePass at the gpg prompt —
# it is never typed into a command or shown on screen:
FILE=$(ls -t ~/backups/banco-offsite/*.sql.gz.gpg | head -1)
gpg --decrypt "$FILE" 2>/dev/null | gunzip 2>/dev/null | head -c 120; echo

# ✅ CORRECT KEY  -> you see SQL, e.g.  "-- PostgreSQL database dump"
# ❌ WRONG KEY    -> gpg errors ("decryption failed: Bad session key") or you see nothing.
#                   The KeePass value does NOT match the box key — fix it before trusting the offsite.
```

---

*"If one seal fails, check all the seals."*
*Test your backups. The backup you don't test is the backup that doesn't work.*
*The DR key you never decrypted with is the key that doesn't work either.*
