#!/usr/bin/env node
/**
 * BADGE SYSTEM & REPUTATION -- Recording Script
 *
 * Uses demoLogin() exclusively (no Keycloak form).
 * DOM overlays for character cards (stay on BASE origin).
 *
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card (emerald)
 *   3.  Members directory -- tier badges on every user
 *   4.  Marco Vitale -- Legend tier, profile + badges
 *   5.  Sally Thompson -- Trusted tier, profile + badges
 *   6.  Mike Kenel -- Active tier, profile + workshop
 *   7.  Angel Kenel -- Newcomer, trigger badge check, earn badges live
 *   8.  Badge catalog -- all 15 badges (overlay)
 *   9.  EMERALD "FEATURE COMPLETE" card
 *
 * Usage: node record-badges.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://46.62.138.218';
const VP = { width: 1920, height: 1080 };

function waitForEnter(msg) {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(`\n>>> ${msg} [ENTER] `, () => { rl.close(); resolve(); });
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Full-page cards (data: URLs -- for scenes with NO api calls) ─
function card(bg, title, subtitle, extra = '') {
  return `data:text/html,${encodeURIComponent(`
<!DOCTYPE html><html><head><style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: ${bg}; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100vh; width: 100vw;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: white; text-align: center;
  }
  h1 { font-size: 72px; font-weight: 800; margin-bottom: 20px; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
  h2 { font-size: 36px; font-weight: 400; opacity: 0.9; margin-bottom: 15px; }
  .extra { font-size: 24px; opacity: 0.7; margin-top: 10px; }
  .badge { display: inline-block; padding: 8px 24px; border-radius: 8px; background: rgba(255,255,255,0.2); font-size: 28px; font-weight: 600; margin-top: 20px; }
</style></head><body>
  <h1>${title}</h1><h2>${subtitle}</h2>${extra}
</body></html>`)}`;
}

// ── API helper (uses bh_session cookie -- MUST be on BASE origin) ─
async function apiCall(page, method, path, body) {
  return page.evaluate(async (base, m, p, b) => {
    const opts = {
      method: m,
      headers: { 'Content-Type': 'application/json' },
    };
    if (b) opts.body = JSON.stringify(b);
    const r = await fetch(`${base}${p}`, opts);
    const data = await r.json().catch(() => null);
    return { status: r.status, data };
  }, BASE, method, path, body);
}

async function demoLogin(page, username) {
  const resp = await apiCall(page, 'POST', '/api/v1/demo/login', {
    username, password: 'helix_pass'
  });
  if (resp.status !== 200) {
    console.error(`  LOGIN FAILED for ${username}: ${JSON.stringify(resp.data)}`);
    return false;
  }
  console.log(`  Logged in as ${username}`);
  return true;
}

// ── DOM overlay card (stays on current page = BASE origin) ────
async function showOverlay(page, name, subtitle, extra = '', duration = 3000) {
  await page.evaluate((n, s, e) => {
    const old = document.getElementById('name-card-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'name-card-overlay';
    overlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      z-index: 99999; display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      background: #1E293B; color: white;
      font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:72px; font-weight:800; margin-bottom:20px;
                 text-shadow:2px 2px 8px rgba(0,0,0,0.3)">${n}</h1>
      <h2 style="font-size:36px; font-weight:400; opacity:0.9;
                 margin-bottom:15px">${s}</h2>
      ${e ? `<div style="font-size:24px; opacity:0.7; margin-top:10px">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
  }, name, subtitle, extra);
  await sleep(duration);
}

// ── Smooth scroll helper ─────────────────────────────────────
async function smoothScroll(page, pixels, duration = 1500) {
  await page.evaluate((px, dur) => {
    const start = window.scrollY;
    const startTime = Date.now();
    function step() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / dur, 1);
      const ease = progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;
      window.scrollTo(0, start + px * ease);
      if (progress < 1) requestAnimationFrame(step);
    }
    step();
  }, pixels, duration);
  await sleep(duration + 200);
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  BADGE SYSTEM -- Recording Script`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Auth: demoLogin`);
  console.log(`  Resolution: ${VP.width}x${VP.height}\n`);

  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: VP,
    args: [
      `--window-size=${VP.width},${VP.height}`,
      '--window-position=0,0',
      '--start-fullscreen',
      '--no-sandbox',
      '--ignore-certificate-errors',
    ]
  });

  const page = await browser.newPage();
  await page.setViewport(VP);

  // ── Pre-flight: establish cookie domain ────────────────────
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  console.log('  Pre-flight: ready\n');

  // ============================================================
  // SCENE 1: OBS CHECK (RED)
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">BADGE SYSTEM | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: INTRO (EMERALD) -- 6s
  // ============================================================
  console.log('  Scene 2: Intro');
  await page.goto(card(
    '#059669',
    'BADGE SYSTEM',
    'Earn Badges. Build Reputation. Rise Through the Ranks.',
    '<div class="badge">15 BADGES &bull; 5 TIERS</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Every listing, rental, and review earns points.<br>' +
    'Newcomer to Legend -- your reputation tells your story.' +
    '</div>'
  ));
  await sleep(6000);

  // ============================================================
  // SCENE 3: MEMBERS DIRECTORY -- tier badges visible -- 8s
  // Navigate to BASE first (leaving data: URL)
  // ============================================================
  console.log('  Scene 3: Members directory');
  await page.goto(`${BASE}/members?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);
  // Slow scroll to show tier badges on multiple user cards
  await smoothScroll(page, 600);
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(2000);

  // ============================================================
  // SCENE 4: MARCO VITALE -- Legend tier
  // ============================================================
  console.log('  Scene 4: Marco Vitale (Legend)');
  await showOverlay(page, 'MARCO VITALE', 'Legend',
    'The highest tier. Earned through years of community contribution.');

  await demoLogin(page, 'marco');
  await page.goto(`${BASE}/profile?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);
  // Scroll down to badge grid
  await smoothScroll(page, 500);
  await sleep(3000);

  // Show workshop with tier in header
  await page.goto(`${BASE}/workshop/marcos-workshop?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(4000);

  // ============================================================
  // SCENE 5: SALLY THOMPSON -- Trusted tier
  // ============================================================
  console.log('  Scene 5: Sally Thompson (Trusted)');
  await showOverlay(page, 'SALLY THOMPSON', 'Trusted',
    '5 badges earned. A reliable member of the community.');

  await demoLogin(page, 'sally');
  await page.goto(`${BASE}/profile?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);
  await smoothScroll(page, 500);
  await sleep(3000);

  // ============================================================
  // SCENE 6: MIKE KENEL -- Active tier, 7 badges
  // ============================================================
  console.log('  Scene 6: Mike Kenel (Active)');
  await showOverlay(page, 'MIKE KENEL', 'Active -- 7 Badges',
    'Most badges on the platform. Super Lender, Multilingual, and more.');

  await demoLogin(page, 'mike');
  await page.goto(`${BASE}/profile?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);
  await smoothScroll(page, 500);
  await sleep(3000);

  // Mike's workshop
  await page.goto(`${BASE}/workshop/mikes-garage?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // ============================================================
  // SCENE 7: ANGEL KENEL -- Newcomer, trigger badge check
  // ============================================================
  console.log('  Scene 7: Angel Kenel (Newcomer -> earns badges)');
  await showOverlay(page, 'ANGEL KENEL', 'Newcomer',
    'Even the founder starts at the bottom. Let\'s check for new badges...');

  await demoLogin(page, 'angel');
  await page.goto(`${BASE}/profile?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Trigger badge check -- Angel should earn badges
  console.log('  Triggering badge check for Angel...');
  const checkResult = await apiCall(page, 'POST', '/api/v1/badges/check');
  const newBadges = checkResult.data?.new_badges || [];
  console.log(`  New badges earned: ${newBadges.length}`);
  for (const nb of newBadges) console.log(`    + ${nb.name}`);

  // Reload profile to show newly earned badges
  await page.reload({ waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(4000);

  // ============================================================
  // SCENE 8: BADGE CATALOG -- all 15 badges (overlay)
  // ============================================================
  console.log('  Scene 8: Badge catalog');
  const catalogResp = await apiCall(page, 'GET', '/api/v1/badges/catalog');
  const catalog = catalogResp.data || [];

  // Build a styled overlay showing all 15 badges
  const badgeHTML = catalog.map(b => `
    <div style="display:flex;align-items:center;gap:12px;padding:8px 16px;
                background:rgba(255,255,255,0.08);border-radius:8px;">
      <div style="width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.15);
                  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">
        ${b.icon === 'package' ? '📦' : b.icon === 'gift' ? '🎁' : b.icon === 'handshake' ? '🤝' :
          b.icon === 'shield-check' ? '🛡' : b.icon === 'star' ? '⭐' : b.icon === 'megaphone' ? '📢' :
          b.icon === 'sparkles' ? '✨' : b.icon === 'globe' ? '🌍' : b.icon === 'wrench' ? '🔧' :
          b.icon === 'trophy' ? '🏆' : b.icon === 'rocket' ? '🚀' : b.icon === 'crown' ? '👑' :
          b.icon === 'heart' ? '❤' : b.icon === 'building-storefront' ? '🏪' : '🎖'}
      </div>
      <div style="text-align:left;">
        <div style="font-weight:700;font-size:16px;">${b.name}</div>
        <div style="font-size:13px;opacity:0.7;">${b.description}</div>
      </div>
    </div>
  `).join('');

  await page.evaluate((html) => {
    const old = document.getElementById('name-card-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'name-card-overlay';
    overlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      z-index: 99999; display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      background: #0F172A; color: white;
      font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
      padding: 40px;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:48px; font-weight:800; margin-bottom:30px;
                 text-shadow:2px 2px 8px rgba(0,0,0,0.3)">All 15 Badges</h1>
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:12px;
                  max-width:1200px; width:100%;">
        ${html}
      </div>
      <div style="margin-top:30px; font-size:20px; opacity:0.6;">
        Every action builds your reputation
      </div>
    `;
    document.body.appendChild(overlay);
  }, badgeHTML);
  await sleep(8000);

  // ============================================================
  // SCENE 9: FEATURE COMPLETE (EMERALD)
  // ============================================================
  console.log('  Scene 9: Feature complete');
  await page.goto(card(
    '#059669',
    'BADGE SYSTEM',
    'Complete',
    '<div class="badge">REPUTATION</div>' +
    '<div class="extra" style="margin-top:20px">' +
    '15 badges across 5 tiers<br>' +
    'Newcomer &rarr; Active &rarr; Trusted &rarr; Pillar &rarr; Legend<br>' +
    'Every listing, rental, review, and giveaway counts<br>' +
    'Your reputation is your handshake' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // DONE
  // ============================================================
  await page.goto(card('#1E293B', 'CUT', 'Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
