#!/usr/bin/env node
/**
 * MULTILINGUAL LIVE SWITCH -- Recording Script (EP5)
 *
 * Uses demoLogin() exclusively (no Keycloak form).
 * DOM overlays for character cards (stay on BASE origin).
 *
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card (sky blue)
 *   3.  Home page in English -- hero, stats, how-it-works
 *   4.  Click language switcher -> Italian -- watch everything change
 *   5.  Home page in Italian -- same layout, all text translated
 *   6.  Browse page in Italian -- filters, categories, item cards
 *   7.  Switch to English -- browse page re-renders
 *   8.  Item detail in English -- full listing
 *   9.  Switch to Italian -- same item, Italian UI
 *  10.  Members page in Italian -- translated badges, labels
 *  11.  Help Board in Italian -- posts, filters, status labels
 *  12.  Profile page -- badges, stats in Italian
 *  13.  Switch to English -- profile re-renders
 *  14.  SKY BLUE "FEATURE COMPLETE" card
 *
 * Usage: node record-multilingual.js [base_url]
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

// ── Language switch overlay -- shows which language is active ───
async function showLangBanner(page, flag, langName, duration = 2000) {
  await page.evaluate((f, ln) => {
    const old = document.getElementById('lang-banner');
    if (old) old.remove();

    const banner = document.createElement('div');
    banner.id = 'lang-banner';
    banner.style.cssText = `
      position: fixed; top: 30px; right: 30px; z-index: 99999;
      display: flex; align-items: center; gap: 12px;
      padding: 16px 28px; border-radius: 12px;
      background: rgba(0,0,0,0.85); color: white;
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 28px; font-weight: 700;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      animation: slideIn 0.4s ease-out;
    `;
    banner.innerHTML = `<span style="font-size:36px">${f}</span> ${ln}`;

    const style = document.createElement('style');
    style.textContent = `@keyframes slideIn { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`;
    banner.appendChild(style);
    document.body.appendChild(banner);

    setTimeout(() => {
      banner.style.transition = 'opacity 0.5s';
      banner.style.opacity = '0';
      setTimeout(() => banner.remove(), 600);
    }, 3000);
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

// ── Click the language dropdown and select a language ─────────
async function clickLangSwitch(page, targetLang) {
  // Click the lang dropdown button
  await page.evaluate(() => {
    const btn = document.querySelector('[x-data*="langOpen"] button');
    if (btn) btn.click();
  });
  await sleep(600);

  // Click the target language link
  await page.evaluate((lang) => {
    const links = document.querySelectorAll('[x-data*="langOpen"] a');
    for (const link of links) {
      if (link.href && link.href.includes(`lang=${lang}`)) {
        link.click();
        return;
      }
    }
  }, targetLang);
  await sleep(2000);
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  MULTILINGUAL LIVE SWITCH -- Recording Script`);
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
    '<div class="extra">MULTILINGUAL LIVE SWITCH | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: INTRO (SKY BLUE) -- 6s
  // ============================================================
  console.log('  Scene 2: Intro');
  await page.goto(card(
    '#0284C7',
    'MULTILINGUAL',
    'One Click. Every Label. Instant Switch.',
    '<div class="badge">ENGLISH &harr; ITALIANO</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Full i18n across every page.<br>' +
    'Navigation, forms, badges, categories -- everything translates live.' +
    '</div>'
  ));
  await sleep(6000);

  // ============================================================
  // SCENE 3: HOME PAGE -- English -- 8s
  // ============================================================
  console.log('  Scene 3: Home page (English)');
  await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await showLangBanner(page, '\uD83C\uDDEC\uD83C\uDDE7', 'English');
  await sleep(2000);
  // Scroll to show how-it-works section
  await smoothScroll(page, 600);
  await sleep(2000);
  // Scroll to recently listed
  await smoothScroll(page, 400);
  await sleep(2000);

  // ============================================================
  // SCENE 4: SWITCH TO ITALIAN on home page -- the money shot
  // ============================================================
  console.log('  Scene 4: Switch to Italian (Home page)');
  // Scroll back to top to show the switch
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(1000);

  // Show overlay announcing the switch
  await showOverlay(page, '\uD83C\uDDEE\uD83C\uDDF9 ITALIANO', 'Watch the entire page change',
    'Same layout. Every label translated. One click.');

  // Navigate to Italian version
  await page.goto(`${BASE}/?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Italiano');
  await sleep(2000);
  // Scroll to show translated how-it-works
  await smoothScroll(page, 600);
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(2000);

  // ============================================================
  // SCENE 5: BROWSE PAGE -- Italian -- filters + categories
  // ============================================================
  console.log('  Scene 5: Browse page (Italian)');
  await page.goto(`${BASE}/browse?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Esplora Oggetti');
  await sleep(1500);
  // Scroll through items
  await smoothScroll(page, 500);
  await sleep(2000);

  // ============================================================
  // SCENE 6: BROWSE PAGE -- switch to English
  // ============================================================
  console.log('  Scene 6: Browse page (switch to English)');
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1500);
  await showLangBanner(page, '\uD83C\uDDEC\uD83C\uDDE7', 'Browse Items');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2000);

  // ============================================================
  // SCENE 7: ITEM DETAIL -- English
  // ============================================================
  console.log('  Scene 7: Item detail (English)');
  // Login as marco to have a session, then visit an item
  await demoLogin(page, 'marco');

  // Get first item from browse API
  const itemsResp = await apiCall(page, 'GET', '/api/v1/items?limit=1');
  const firstItem = itemsResp.data?.items?.[0] || itemsResp.data?.[0];
  if (firstItem) {
    const itemSlug = firstItem.slug || firstItem.id;
    await page.goto(`${BASE}/items/${itemSlug}?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2500);
    await smoothScroll(page, 400);
    await sleep(2000);

    // ============================================================
    // SCENE 8: ITEM DETAIL -- switch to Italian
    // ============================================================
    console.log('  Scene 8: Item detail (switch to Italian)');
    await page.goto(`${BASE}/items/${itemSlug}?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(1500);
    await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Italiano');
    await sleep(2000);
    await smoothScroll(page, 400);
    await sleep(2000);
  } else {
    console.log('  WARNING: No items found, skipping item detail scenes');
  }

  // ============================================================
  // SCENE 9: MEMBERS PAGE -- Italian
  // ============================================================
  console.log('  Scene 9: Members page (Italian)');
  await page.goto(`${BASE}/members?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Membri');
  await sleep(1500);
  await smoothScroll(page, 500);
  await sleep(2000);

  // ============================================================
  // SCENE 10: HELP BOARD -- Italian
  // ============================================================
  console.log('  Scene 10: Help Board (Italian)');
  await page.goto(`${BASE}/helpboard?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Bacheca Aiuto');
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(2000);

  // ============================================================
  // SCENE 11: PROFILE -- Italian (logged in as marco)
  // ============================================================
  console.log('  Scene 11: Profile (Italian)');
  await page.goto(`${BASE}/profile?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Profilo');
  await sleep(1500);
  await smoothScroll(page, 500);
  await sleep(2500);

  // ============================================================
  // SCENE 12: PROFILE -- switch to English
  // ============================================================
  console.log('  Scene 12: Profile (switch to English)');
  await page.goto(`${BASE}/profile?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1500);
  await showLangBanner(page, '\uD83C\uDDEC\uD83C\uDDE7', 'Profile');
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(2000);

  // ============================================================
  // SCENE 13: LIST ITEM FORM -- Italian (show translated form)
  // ============================================================
  console.log('  Scene 13: List Item form (Italian)');
  await page.goto(`${BASE}/list?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2500);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Pubblica Oggetto');
  await sleep(1500);
  await smoothScroll(page, 400);
  await sleep(2000);

  // ============================================================
  // SCENE 14: FEATURE COMPLETE (SKY BLUE)
  // ============================================================
  console.log('  Scene 14: Feature complete');
  await page.goto(card(
    '#0284C7',
    'MULTILINGUAL',
    'Complete',
    '<div class="badge">i18n</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'English &harr; Italiano<br>' +
    'Every page. Every label. Every form.<br>' +
    'Navigation, badges, categories, filters, errors<br>' +
    'One click -- instant language switch' +
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
