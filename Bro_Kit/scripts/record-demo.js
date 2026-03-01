#!/usr/bin/env node
/**
 * BorrowHood Demo Video - Full Authenticated Capture
 *
 * Captures the COMPLETE flow: public pages, login, authenticated dashboard,
 * rentals, badges, notifications, and logout.
 *
 * Usage: node record-demo.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const path = require('path');

const BASE = process.argv[2] || 'https://46.62.138.218';
const FRAMES = path.join(__dirname, 'frames');
const WIDTH = 1920;
const HEIGHT = 1080;

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// --- SCENE DEFINITIONS ---
// Phase 1: Public pages (English)
// Phase 2: Login as Mike Kenel
// Phase 3: Authenticated flows (dashboard, rentals, badges, profile)
// Phase 4: Logout
// Phase 5: Italian bilingual showcase

async function capture() {
  console.log(`\n  BorrowHood Demo - Full Capture`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Resolution: ${WIDTH}x${HEIGHT}\n`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--ignore-certificate-errors',
      `--window-size=${WIDTH},${HEIGHT}`,
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT });
  page.on('console', () => {});
  page.on('pageerror', () => {});

  let sceneNum = 1;

  async function snap(filename, desc, scrollY = 0) {
    const padded = String(sceneNum).padStart(2, '0');
    const fullName = `${padded}-${filename}`;
    process.stdout.write(`  ${fullName.padEnd(35)} ${desc}... `);
    if (scrollY > 0) {
      await page.evaluate((y) => window.scrollTo({ top: y, behavior: 'instant' }), scrollY);
      await sleep(500);
    }
    await page.screenshot({
      path: path.join(FRAMES, fullName),
      fullPage: false,
    });
    console.log('OK');
    sceneNum++;
  }

  // =========================================================
  // PHASE 1: PUBLIC PAGES (English)
  // =========================================================
  console.log('\n  --- Phase 1: Public Pages ---');

  // Homepage hero
  await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('hero.png', 'Homepage hero + stats');

  // Recently listed items
  await snap('recently-listed.png', 'Recently listed items', 800);

  // Origin story
  await snap('origin-story.png', 'Origin story + footer', 1800);

  // Browse grid
  await page.goto(`${BASE}/browse`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('browse-grid.png', 'Browse all items');

  // Search + filter
  await page.goto(`${BASE}/browse?q=drill&category=tools`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('browse-search.png', 'Search + filter');

  // Item detail
  await page.goto(`${BASE}/items/bosch-professional-drill-driver-set`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2500);
  await snap('item-detail-top.png', 'Item detail + map');

  // Reviews section
  await snap('item-reviews.png', 'Weighted reviews + trust', 600);

  // Workshop profile
  await page.goto(`${BASE}/workshop/sallys-kitchen`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('workshop.png', 'Workshop storefront');

  // =========================================================
  // PHASE 2: LOGIN
  // =========================================================
  console.log('\n  --- Phase 2: Login as Mike Kenel ---');

  // Click login -- capture the Keycloak form
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('keycloak-login.png', 'Keycloak OIDC login page');

  // Fill credentials and submit
  try {
    await page.type('#username', 'mike', { delay: 50 });
    await page.type('#password', 'helix_pass', { delay: 50 });
    await sleep(500);
    await snap('keycloak-filled.png', 'Credentials entered');

    // Submit login -- wait for full redirect chain (KC -> callback -> home)
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }),
      page.click('#kc-login'),
    ]);
    // Give the redirect chain a moment, then force-navigate to homepage
    await sleep(1000);
    await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2000);
    await snap('logged-in-home.png', 'Logged in as Mike Kenel');
  } catch (err) {
    console.log(`  Login error: ${err.message.slice(0, 80)}`);
    // Try to continue anyway -- navigate to home with session cookie
    await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2000);
    await snap('login-result.png', 'After login attempt');
  }

  // =========================================================
  // PHASE 3: AUTHENTICATED FLOWS
  // =========================================================
  console.log('\n  --- Phase 3: Authenticated Flows ---');

  // Dashboard
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2500);
  await snap('dashboard.png', 'Dashboard - my items + rentals');

  // Dashboard - click "Incoming Requests" tab
  try {
    await page.evaluate(() => {
      const tabs = document.querySelectorAll('[role="tab"], button, a');
      for (const t of tabs) {
        if (t.textContent.trim() === 'Incoming Requests') { t.click(); break; }
      }
    });
    await sleep(1500);
  } catch (e) { /* tab click optional */ }
  await snap('dashboard-rentals.png', 'Incoming rental requests');

  // Profile page (badges, reputation)
  await page.goto(`${BASE}/workshop/mikes-garage`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('my-workshop.png', 'My workshop profile + badges');

  // Scroll to items
  await snap('my-items.png', 'My listed items', 500);

  // List new item page (authenticated)
  await page.goto(`${BASE}/list`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('list-item-auth.png', 'List item form (authenticated)');

  // Onboarding (shows the full wizard)
  await page.goto(`${BASE}/onboarding`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('onboarding.png', 'Onboarding wizard');

  // =========================================================
  // PHASE 4: LOGOUT
  // =========================================================
  console.log('\n  --- Phase 4: Logout ---');

  await page.goto(`${BASE}/logout`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1000);
  // Keycloak shows "Logging out" confirmation -- click it
  try {
    await page.click('#kc-logout');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
  } catch (e) { /* fallback: force navigate */ }
  // Make sure we land on the homepage (logged out)
  await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('logged-out.png', 'Logged out - back to homepage');

  // =========================================================
  // PHASE 5: ITALIAN BILINGUAL
  // =========================================================
  console.log('\n  --- Phase 5: Italian ---');

  await page.goto(`${BASE}/?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('italian-home.png', 'Full Italian homepage');

  await page.goto(`${BASE}/browse`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await snap('italian-browse.png', 'Italian browse + category pills');

  // =========================================================
  // DONE
  // =========================================================
  await browser.close();
  console.log(`\n  Done. ${sceneNum - 1} frames captured.\n`);
}

capture().catch(console.error);
