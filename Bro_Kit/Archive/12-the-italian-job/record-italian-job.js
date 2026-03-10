#!/usr/bin/env node
/**
 * THE ITALIAN JOB -- Recording Script (EP6 in Garage Sessions / folder 12)
 *
 * Multilingual live switch: English to Italian and back.
 * Uses demoLogin() exclusively (no Keycloak form).
 * DOM overlays for character cards (stay on BASE origin).
 *
 * Improvements over earlier scripts:
 *   - 128px headings, 64px subtitles, 48px body (mobile-first)
 *   - 5s minimum scenes, 8-12s for text-heavy cards
 *   - 150% browser zoom for UI pages
 *
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- sky blue, flag emoji
 *   3.  Home page in English -- hero, stats, how-it-works
 *   4.  Overlay: "WATCH THE SWITCH"
 *   5.  Home page in Italian -- same layout, all text translated
 *   6.  Browse page in Italian -- filters, categories, item cards
 *   7.  Switch to English -- browse page re-renders
 *   8.  Item detail in English -- full listing
 *   9.  Switch to Italian -- same item, Italian UI
 *  10.  Members page in Italian -- translated badges, labels
 *  11.  Help Board in Italian -- posts, filters, status labels
 *  12.  Profile page in Italian -- badges, stats
 *  13.  Switch to English -- profile re-renders
 *  14.  List Item form in Italian -- translated form labels
 *  15.  SKY BLUE "FEATURE COMPLETE" card
 *
 * Usage: node record-italian-job.js [base_url]
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
  h1 { font-size: 128px; font-weight: 900; margin-bottom: 24px; text-shadow: 4px 4px 16px rgba(0,0,0,0.4); letter-spacing: -3px; }
  h2 { font-size: 64px; font-weight: 400; opacity: 0.9; margin-bottom: 20px; }
  .extra { font-size: 48px; opacity: 0.7; margin-top: 16px; line-height: 1.4; }
  .badge { display: inline-block; padding: 12px 32px; border-radius: 12px; background: rgba(255,255,255,0.2); font-size: 48px; font-weight: 700; margin-top: 24px; }
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
async function showOverlay(page, name, subtitle, extra = '', duration = 5000) {
  // Reset zoom so overlay fills the real viewport
  await page.evaluate(() => { document.body.style.zoom = '1'; });
  await sleep(100);

  await page.evaluate((n, s, e) => {
    const old = document.getElementById('name-card-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'name-card-overlay';
    overlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      z-index: 99999; display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      background: rgba(30,41,59,0.95); color: white;
      font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:128px; font-weight:900; margin-bottom:24px;
                 text-shadow:4px 4px 16px rgba(0,0,0,0.4); letter-spacing:-3px">${n}</h1>
      <h2 style="font-size:64px; font-weight:400; opacity:0.9;
                 margin-bottom:20px">${s}</h2>
      ${e ? `<div style="font-size:48px; opacity:0.7; margin-top:16px; line-height:1.4">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
  }, name, subtitle, extra);
  await sleep(duration);
  // Remove overlay and restore zoom
  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o) { o.style.transition = 'opacity 0.5s'; o.style.opacity = '0'; }
  });
  await sleep(600);
  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o) o.remove();
    document.body.style.zoom = '1.5';
  });
}

// ── Language switch banner (top-right floating indicator) ───
async function showLangBanner(page, flag, langName, duration = 3000) {
  await page.evaluate((f, ln) => {
    const old = document.getElementById('lang-banner');
    if (old) old.remove();

    const banner = document.createElement('div');
    banner.id = 'lang-banner';
    banner.style.cssText = `
      position: fixed; top: 30px; right: 30px; z-index: 99999;
      display: flex; align-items: center; gap: 16px;
      padding: 20px 36px; border-radius: 16px;
      background: rgba(0,0,0,0.9); color: white;
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 36px; font-weight: 700;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      animation: slideIn 0.4s ease-out;
    `;
    banner.innerHTML = `<span style="font-size:48px">${f}</span> ${ln}`;

    const style = document.createElement('style');
    style.textContent = `@keyframes slideIn { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`;
    banner.appendChild(style);
    document.body.appendChild(banner);

    setTimeout(() => {
      banner.style.transition = 'opacity 0.5s';
      banner.style.opacity = '0';
      setTimeout(() => banner.remove(), 600);
    }, 4000);
  }, flag, langName);
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

// ── Set 150% zoom for UI pages ──────────────────────────────
async function setZoom(page) {
  await page.evaluate(() => { document.body.style.zoom = '1.5'; });
  await sleep(300);
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  THE ITALIAN JOB -- Recording Script`);
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

  // Pre-flight: establish cookie domain
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  console.log('  Pre-flight: ready\n');

  // ============================================================
  // SCENE 1: OBS CHECK (RED) -- wait for operator
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured',
    '<div class="extra">THE ITALIAN JOB | BorrowHood EP6</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: INTRO (SKY BLUE) -- 8s
  // ============================================================
  console.log('  Scene 2: Intro');
  await page.goto(card(
    '#0284C7',
    'THE ITALIAN JOB',
    'One Click. Tutto Cambia.',
    '<div class="badge">ENGLISH &#8596; ITALIANO</div>' +
    '<div class="extra" style="margin-top:24px">' +
    '547 translated strings<br>' +
    'Every page, every label, every form' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 3: HOME PAGE -- English -- 10s
  // ============================================================
  console.log('  Scene 3: Home page (English)');
  await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);
  await showLangBanner(page, '\uD83C\uDDEC\uD83C\uDDE7', 'English');
  await sleep(2000);
  // Scroll to show how-it-works section
  await smoothScroll(page, 600);
  await sleep(2500);
  // Scroll to recently listed
  await smoothScroll(page, 400);
  await sleep(2500);

  // ============================================================
  // SCENE 4: SWITCH TO ITALIAN -- the money shot -- 12s
  // ============================================================
  console.log('  Scene 4: Switch to Italian (Home page)');
  // Scroll back to top
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(1000);

  // Overlay announcing the switch
  await showOverlay(page,
    '\uD83C\uDDEE\uD83C\uDDF9 ITALIANO',
    'Watch the entire page change',
    'Same layout. Every label translated.'
  );

  // Navigate to Italian
  await page.goto(`${BASE}/?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Italiano');
  await sleep(2500);
  // Scroll through translated content
  await smoothScroll(page, 600);
  await sleep(2500);
  await smoothScroll(page, 400);
  await sleep(2500);

  // ============================================================
  // SCENE 5: BROWSE PAGE -- Italian -- 8s
  // ============================================================
  console.log('  Scene 5: Browse page (Italian)');
  await page.goto(`${BASE}/browse?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Esplora Oggetti');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2500);

  // ============================================================
  // SCENE 6: BROWSE PAGE -- switch to English -- 7s
  // ============================================================
  console.log('  Scene 6: Browse page (switch to English)');
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  await showLangBanner(page, '\uD83C\uDDEC\uD83C\uDDE7', 'Browse Items');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2500);

  // ============================================================
  // SCENE 7: ITEM DETAIL -- English -- 7s
  // ============================================================
  console.log('  Scene 7: Item detail (English)');
  // Login as marco to have a session
  await demoLogin(page, 'marco');

  // Get first item from browse API
  const itemsResp = await apiCall(page, 'GET', '/api/v1/items?limit=1');
  const firstItem = itemsResp.data?.items?.[0] || itemsResp.data?.[0];
  if (firstItem) {
    const itemSlug = firstItem.slug || firstItem.id;
    await page.goto(`${BASE}/items/${itemSlug}?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
    await setZoom(page);
    await sleep(2500);
    await smoothScroll(page, 400);
    await sleep(2500);

    // ============================================================
    // SCENE 8: ITEM DETAIL -- switch to Italian -- 7s
    // ============================================================
    console.log('  Scene 8: Item detail (switch to Italian)');
    await page.goto(`${BASE}/items/${itemSlug}?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
    await setZoom(page);
    await sleep(1500);
    await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Italiano');
    await sleep(2500);
    await smoothScroll(page, 400);
    await sleep(2500);
  } else {
    console.log('  WARNING: No items found, skipping item detail scenes');
  }

  // ============================================================
  // SCENE 9: MEMBERS PAGE -- Italian -- 7s
  // ============================================================
  console.log('  Scene 9: Members page (Italian)');
  await page.goto(`${BASE}/members?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Membri');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2500);

  // ============================================================
  // SCENE 10: HELP BOARD -- Italian -- 7s
  // ============================================================
  console.log('  Scene 10: Help Board (Italian)');
  await page.goto(`${BASE}/helpboard?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Bacheca Aiuto');
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(2500);

  // ============================================================
  // SCENE 11: PROFILE -- Italian -- 7s
  // ============================================================
  console.log('  Scene 11: Profile (Italian)');
  await page.goto(`${BASE}/profile?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Profilo');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2500);

  // ============================================================
  // SCENE 12: PROFILE -- switch to English -- 7s
  // ============================================================
  console.log('  Scene 12: Profile (switch to English)');
  await page.goto(`${BASE}/profile?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  await showLangBanner(page, '\uD83C\uDDEC\uD83C\uDDE7', 'Profile');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2500);

  // ============================================================
  // SCENE 13: LIST ITEM FORM -- Italian -- 7s
  // ============================================================
  console.log('  Scene 13: List Item form (Italian)');
  await page.goto(`${BASE}/list?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Pubblica Oggetto');
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(2500);

  // ============================================================
  // SCENE 14: FEATURE COMPLETE (SKY BLUE) -- 10s
  // ============================================================
  console.log('  Scene 14: Feature complete');
  await page.goto(card(
    '#0284C7',
    'MULTILINGUAL',
    'Completo.',
    '<div class="badge">i18n</div>' +
    '<div class="extra" style="margin-top:24px">' +
    '547 translated strings<br>' +
    'English and Italiano<br>' +
    'Every page. Every label. Every form.<br>' +
    'One click -- instant language switch' +
    '</div>'
  ));
  await sleep(10000);

  // ============================================================
  // DONE
  // ============================================================
  await page.goto(card('#1E293B', 'CUT', 'Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
