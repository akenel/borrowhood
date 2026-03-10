#!/usr/bin/env node
/**
 * BORROWHOOD -- Edge Cases: When Things Go Wrong (v1)
 *
 * Four scenarios. Four ways a rental can go sideways.
 * Every edge case handled cleanly.
 *
 * Scenario 1: THE DECLINE     -- Sally requests, Mike declines
 * Scenario 2: THE CANCEL      -- Sally approved, cancels before pickup
 * Scenario 3: WRONG CODE      -- Wrong lockbox code, then correct
 * Scenario 4: THE DISPUTE     -- Item damaged, file + respond + resolve
 *
 * PRE-RECORDING -- clean stale data from previous takes:
 *   ssh root@46.62.138.218 "docker exec postgres psql -U helix_user -d borrowhood -c \"
 *     DELETE FROM bh_dispute WHERE rental_id IN
 *       (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
 *     DELETE FROM bh_lockbox_access WHERE rental_id IN
 *       (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
 *     DELETE FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
 *   \""
 *
 * Usage: node record-edge-cases.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://46.62.138.218';
const VP = { width: 1920, height: 1080 };


// ═══════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════

function waitForEnter(msg) {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(`\n>>> ${msg} [ENTER] `, () => { rl.close(); resolve(); });
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function card(bg, title, subtitle, extra = '') {
  return `data:text/html,${encodeURIComponent(`<!DOCTYPE html><html><head>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:${bg};display:flex;flex-direction:column;align-items:center;
    justify-content:center;height:100vh;width:100vw;
    font-family:'Segoe UI',Arial,sans-serif;color:white;text-align:center}
  h1{font-size:72px;font-weight:800;margin-bottom:20px;text-shadow:2px 2px 8px rgba(0,0,0,0.3)}
  h2{font-size:36px;font-weight:400;opacity:0.9;margin-bottom:15px}
  .extra{font-size:24px;opacity:0.7;margin-top:10px;line-height:1.6}
</style></head><body>
  <h1>${title}</h1><h2>${subtitle}</h2>${extra}
</body></html>`)}`;
}

function storyCard(bg, who, action, detail) {
  return card(bg, who, action, `<div class="extra">${detail}</div>`);
}


// ═══════════════════════════════════════════════════════════════
//  CLICK INDICATORS  (red ring animation at click point)
// ═══════════════════════════════════════════════════════════════

async function injectClickStyle(page) {
  await page.evaluate(() => {
    if (document.getElementById('bh-click-css')) return;
    const s = document.createElement('style');
    s.id = 'bh-click-css';
    s.textContent = `
      @keyframes bh-ring { 0%{transform:translate(-50%,-50%) scale(0.5);opacity:1} 100%{transform:translate(-50%,-50%) scale(2.5);opacity:0} }
      .bh-click-ring{position:fixed;z-index:99999;width:30px;height:30px;border-radius:50%;
        border:3px solid #DC2626;pointer-events:none;animation:bh-ring .6s ease-out forwards}
    `;
    document.head.appendChild(s);
  });
}

async function showRing(page, x, y) {
  await page.evaluate(({x, y}) => {
    const r = document.createElement('div');
    r.className = 'bh-click-ring';
    r.style.left = x + 'px';
    r.style.top = y + 'px';
    document.body.appendChild(r);
    setTimeout(() => r.remove(), 700);
  }, {x, y});
}


// ═══════════════════════════════════════════════════════════════
//  BUTTON HELPERS (find by text, click with visible cursor)
// ═══════════════════════════════════════════════════════════════

/** Find a VISIBLE button whose textContent includes `text`. */
async function findButton(page, text) {
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const info = await page.evaluate(el => {
      if (el.offsetWidth === 0 && el.offsetHeight === 0) return null;
      if (window.getComputedStyle(el).display === 'none') return null;
      return el.textContent.trim();
    }, btn);
    if (info && info.includes(text)) return btn;
  }
  return null;
}

/** Move cursor smoothly to element center, show red ring, click. */
async function clickEl(page, element, label) {
  const box = await element.boundingBox();
  if (!box) { console.log(`    (no bbox: ${label})`); return false; }
  const x = box.x + box.width / 2;
  const y = box.y + box.height / 2;
  await page.mouse.move(x, y, { steps: 15 });
  await sleep(250);
  await showRing(page, x, y);
  await page.mouse.click(x, y);
  console.log(`    Click: ${label}`);
  await sleep(400);
  return true;
}

/** Shorthand: find button by text then click with cursor. */
async function clickButton(page, text) {
  await injectClickStyle(page);
  const btn = await findButton(page, text);
  if (!btn) { console.log(`    Button not found: "${text}"`); return false; }
  return clickEl(page, btn, text);
}


// ═══════════════════════════════════════════════════════════════
//  API CALL  (via browser fetch -- uses session cookie)
// ═══════════════════════════════════════════════════════════════

async function apiCall(page, method, path, body = null) {
  const result = await page.evaluate(async (m, p, b, base) => {
    const url = p.startsWith('http') ? p : base + p;
    const opts = { method: m, headers: {'Content-Type':'application/json'}, credentials:'include' };
    if (b) opts.body = JSON.stringify(b);
    const resp = await fetch(url, opts);
    const data = await resp.json().catch(() => null);
    return { ok: resp.ok, status: resp.status, data };
  }, method, path, body, BASE);

  if (!result.ok) {
    const d = result.data?.detail || `HTTP ${result.status}`;
    console.error(`\n  *** API ERROR: ${method} ${path} => ${d} ***\n`);
    return { error: true, detail: d, status: result.status, data: result.data };
  }
  console.log(`    API: ${method} ${path} => OK`);
  return result.data;
}

/** Like apiCall but throws on error (for critical calls). */
async function apiCallStrict(page, method, path, body = null) {
  const result = await page.evaluate(async (m, p, b, base) => {
    const url = p.startsWith('http') ? p : base + p;
    const opts = { method: m, headers: {'Content-Type':'application/json'}, credentials:'include' };
    if (b) opts.body = JSON.stringify(b);
    const resp = await fetch(url, opts);
    const data = await resp.json().catch(() => null);
    return { ok: resp.ok, status: resp.status, data };
  }, method, path, body, BASE);

  if (!result.ok) {
    const d = result.data?.detail || `HTTP ${result.status}`;
    console.error(`\n  *** API ERROR: ${method} ${path} => ${d} ***\n`);
    throw new Error(`API: ${method} ${path} - ${d}`);
  }
  console.log(`    API: ${method} ${path} => OK`);
  return result.data;
}

/** Navigate to real page if we're on a data: URL (cookies need same-origin). */
async function ensureOnSite(page) {
  if (page.url().startsWith('data:')) {
    await page.goto(`${BASE}/?lang=en`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await sleep(500);
  }
}


// ═══════════════════════════════════════════════════════════════
//  AUTH HELPERS
// ═══════════════════════════════════════════════════════════════

async function kcLogin(page, username) {
  console.log(`    Logging in as ${username}...`);
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 20000 });
  await sleep(1500);
  await page.evaluate(() => {
    const u = document.querySelector('#username');
    const p = document.querySelector('#password');
    if (u) u.value = '';
    if (p) p.value = '';
  });
  await page.type('#username', username, { delay: 80 });
  await page.type('#password', 'helix_pass', { delay: 80 });
  await sleep(400);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }),
    page.click('#kc-login'),
  ]);
  console.log(`    Logged in as ${username}`);
  await sleep(1500);
}

async function kcLogout(page) {
  await page.goto(`${BASE}/logout`, { waitUntil: 'networkidle2', timeout: 10000 });
  await sleep(300);
  try {
    const btn = await page.$('#kc-logout');
    if (btn) await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }),
      btn.click(),
    ]);
  } catch (_) {}
  await sleep(300);
}


// ═══════════════════════════════════════════════════════════════
//  DASHBOARD HELPERS
// ═══════════════════════════════════════════════════════════════

async function waitForImages(page) {
  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img =>
      img.complete ? Promise.resolve()
        : new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); })
    )
  ));
}

/** Go to dashboard, click a tab with visible cursor, wait for Alpine to settle. */
async function showDashboard(page, tabText, waitMs = 3000) {
  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await injectClickStyle(page);
  await sleep(1500);
  if (tabText) {
    await clickButton(page, tabText);
  }
  await sleep(waitMs);
}

/** Scroll to + highlight the rental card matching rentalId (indigo ring). */
async function highlightRental(page, rentalId) {
  const found = await page.evaluate((id) => {
    const cards = document.querySelectorAll('[x-data]');
    for (const c of cards) {
      if ((c.getAttribute('x-data') || '').includes(id)) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        c.style.transition = 'all 0.3s ease';
        c.style.boxShadow = '0 0 0 3px rgba(79,70,229,0.5)';
        c.style.borderColor = '#4F46E5';
        setTimeout(() => { c.style.boxShadow = ''; c.style.borderColor = ''; }, 6000);
        return true;
      }
    }
    return false;
  }, rentalId);
  if (!found) console.log('    (rental card not visible on page)');
  await sleep(1500);
}


// ═══════════════════════════════════════════════════════════════
//  LISTING ID HELPER  (navigate to item page, extract from Alpine)
// ═══════════════════════════════════════════════════════════════

async function getListingId(page, itemSlug) {
  await page.goto(`${BASE}/items/${itemSlug}?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1000);

  const listingId = await page.evaluate(() => {
    for (const el of document.querySelectorAll('[x-data]')) {
      const attr = el.getAttribute('x-data') || '';
      const m = attr.match(/listingId:\s*'([^']+)'/);
      if (m) return m[1];
    }
    return null;
  });

  if (!listingId) {
    console.error(`    Could not extract listing ID from ${itemSlug}`);
    throw new Error(`No listing ID for ${itemSlug}`);
  }
  console.log(`    Listing ID for ${itemSlug}: ${listingId}`);
  return listingId;
}


// ═══════════════════════════════════════════════════════════════
//  RENTAL HELPER  (create rental via API, return rental object)
// ═══════════════════════════════════════════════════════════════

async function createRentalViaAPI(page, listingId, message) {
  const today = new Date();
  const start = new Date(today); start.setDate(start.getDate() + 2);
  const end   = new Date(today); end.setDate(end.getDate() + 5);

  const rental = await apiCallStrict(page, 'POST', '/api/v1/rentals', {
    listing_id: listingId,
    requested_start: start.toISOString(),
    requested_end: end.toISOString(),
    renter_message: message,
  });
  console.log(`    Rental created: ${rental.id} (${rental.status})`);
  return rental;
}


// ═══════════════════════════════════════════════════════════════
//  MAIN RECORDING
// ═══════════════════════════════════════════════════════════════

(async () => {
  console.log(`\n  BORROWHOOD -- Edge Cases: When Things Go Wrong v1`);
  console.log(`  Target: ${BASE}`);
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
      '--disable-web-security',
    ]
  });

  const page = await browser.newPage();
  await page.setViewport(VP);

  // We'll store IDs for each scenario
  let drillListingId = null;
  let jackListingId  = null;


  // ──────────────────────────────────────────────────────────
  //  SCENE 1 : OBS CHECK
  // ──────────────────────────────────────────────────────────
  await page.goto(card('#DC2626','OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">EDGE CASES v1 | BorrowHood</div>'));
  await waitForEnter('OBS is recording and showing this RED screen?');


  // ──────────────────────────────────────────────────────────
  //  SCENE 2 : INTRO
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 2: Intro');
  await page.goto(card('#1E293B','WHEN THINGS GO WRONG',
    'Declined. Cancelled. Wrong code. Disputed.',
    '<div class="extra">' +
    'Not every rental goes perfectly.<br>' +
    'Requests get declined. Plans change. Codes get mistyped.<br>' +
    'Sometimes items come back damaged.<br><br>' +
    'Here is how BorrowHood handles the messy parts.</div>'));
  await sleep(8000);


  // ══════════════════════════════════════════════════════════
  //  SCENARIO 1 : THE DECLINE
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 3 : DECLINE STORY CARD
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 3: Scenario 1 -- The Decline');
  await page.goto(storyCard('#DC2626','SCENARIO 1','The Decline',
    "Sally requests Mike's drill.<br>" +
    "Mike is busy this week and says no."));
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 4 : SALLY BROWSES + FINDS DRILL
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 4: Sally browses');
  await kcLogin(page, 'sally');

  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await injectClickStyle(page);
  await sleep(3000);

  // Click on drill item card (navigate to item detail)
  await page.goto(`${BASE}/items/bosch-professional-drill-driver-set?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(3000);

  // Extract listing ID from this page
  drillListingId = await page.evaluate(() => {
    for (const el of document.querySelectorAll('[x-data]')) {
      const attr = el.getAttribute('x-data') || '';
      const m = attr.match(/listingId:\s*'([^']+)'/);
      if (m) return m[1];
    }
    return null;
  });
  console.log(`    Drill listing ID: ${drillListingId}`);


  // ──────────────────────────────────────────────────────────
  //  SCENE 5 : SALLY REQUESTS RENTAL
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 5: Sally requests rental');

  // Scroll to rental section and click Rent This Item
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(1000);
  await clickButton(page, 'Rent This Item');
  await sleep(2000);

  // Fill dates
  const today = new Date();
  const start = new Date(today); start.setDate(start.getDate() + 2);
  const end   = new Date(today); end.setDate(end.getDate() + 5);
  const startStr = start.toISOString().split('T')[0];
  const endStr   = end.toISOString().split('T')[0];

  await page.evaluate((s, e) => {
    const si = document.querySelector('[x-model="rentalForm.start"]');
    const ei = document.querySelector('[x-model="rentalForm.end"]');
    if (si) { si.value = s; si.dispatchEvent(new Event('input', { bubbles: true })); }
    if (ei) { ei.value = e; ei.dispatchEvent(new Event('input', { bubbles: true })); }
  }, startStr, endStr);
  await sleep(800);

  // Type message
  const msgSel = '[x-model="rentalForm.message"]';
  await page.evaluate((sel) => {
    const ta = document.querySelector(sel);
    if (ta) { ta.focus(); ta.value = ''; }
  }, msgSel);
  await page.type(msgSel,
    "Hi Mike! Need the drill for a quick shelf project this weekend.",
    { delay: 30 });
  await sleep(2000);

  // Click Send Request
  console.log('    Clicking Send Request...');
  await clickButton(page, 'Send Request');
  await sleep(3000);

  // Capture rental ID -- check if modal closed (success) or use API fallback
  let rentalId1 = null;

  const modalOpen = await page.evaluate(() => {
    const overlay = document.querySelector('[x-show="showRentalModal"]');
    return overlay && overlay.offsetHeight > 0;
  });

  if (modalOpen && drillListingId) {
    console.log('    Modal still open, using API fallback...');
    const rental = await apiCallStrict(page, 'POST', '/api/v1/rentals', {
      listing_id: drillListingId,
      requested_start: start.toISOString(),
      requested_end: end.toISOString(),
      renter_message: "Hi Mike! Need the drill for a quick shelf project this weekend.",
    });
    rentalId1 = rental.id;
  }

  // Query for the rental ID if not captured yet
  if (!rentalId1) {
    try {
      await ensureOnSite(page);
      const rentals = await apiCallStrict(page, 'GET', '/api/v1/rentals?status=pending&role=renter&limit=5');
      if (Array.isArray(rentals) && rentals.length > 0) {
        rentalId1 = rentals[0].id;
      }
    } catch (e) {
      console.log(`    Rental query: ${e.message}`);
    }
  }

  if (!rentalId1) {
    console.error('\n  *** FATAL: No rental created for Scenario 1 ***\n');
    await waitForEnter('Press ENTER to close browser');
    await browser.close();
    return;
  }
  console.log(`    Scenario 1 rental: ${rentalId1}`);


  // ──────────────────────────────────────────────────────────
  //  SCENE 6 : SALLY DASHBOARD -- PENDING
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 6: Sally dashboard -- PENDING');
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId1);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 7 : MIKE SEES REQUEST
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 7: Mike sees incoming request');
  await kcLogout(page);

  await page.goto(storyCard('#DC2626','MIKE SEES THE REQUEST',
    "Sally wants his drill. But Mike is away this week.",
    "He opens his dashboard and sees the request.<br>" +
    "He can't lend it out right now."));
  await sleep(5000);

  await kcLogin(page, 'mike');
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId1);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 8 : MIKE DECLINES
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 8: Mike declines');

  // Try clicking Decline button on dashboard
  const declineClicked = await clickButton(page, 'Decline');
  if (declineClicked) {
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(2000);
  } else {
    // Fallback: decline via API
    console.log('    Decline button not found, using API...');
    await ensureOnSite(page);
    await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${rentalId1}/status`, {
      status: 'declined',
      message: 'Away this week, sorry!',
    });
  }

  // Show dashboard with DECLINED badge
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId1);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 9 : SALLY SEES THE DECLINE
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 9: Sally sees the decline');
  await kcLogout(page);

  await page.goto(storyCard('#DC2626','DECLINED',
    "Sally checks her dashboard.",
    "The rental shows DECLINED in red.<br>" +
    "No hard feelings. She'll try another time."));
  await sleep(4000);

  await kcLogin(page, 'sally');
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId1);
  await sleep(5000);


  // ══════════════════════════════════════════════════════════
  //  SCENARIO 2 : THE CANCEL
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 10 : CANCEL STORY CARD
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 10: Scenario 2 -- The Cancel');
  await page.goto(storyCard('#D97706','SCENARIO 2','The Cancel',
    "Sally rents Mike's floor jack.<br>" +
    "Mike approves. But Sally found one next door.<br>" +
    "She cancels before pickup."));
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 11 : SALLY REQUESTS FLOOR JACK
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 11: Sally requests floor jack');

  // Sally is already logged in -- navigate to floor jack
  await page.goto(`${BASE}/items/floor-jack-jack-stands-3-ton?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(2000);

  // Extract listing ID
  jackListingId = await page.evaluate(() => {
    for (const el of document.querySelectorAll('[x-data]')) {
      const attr = el.getAttribute('x-data') || '';
      const m = attr.match(/listingId:\s*'([^']+)'/);
      if (m) return m[1];
    }
    return null;
  });
  console.log(`    Floor jack listing ID: ${jackListingId}`);

  // Click Rent This Item + fill form
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(1000);
  await clickButton(page, 'Rent This Item');
  await sleep(2000);

  await page.evaluate((s, e) => {
    const si = document.querySelector('[x-model="rentalForm.start"]');
    const ei = document.querySelector('[x-model="rentalForm.end"]');
    if (si) { si.value = s; si.dispatchEvent(new Event('input', { bubbles: true })); }
    if (ei) { ei.value = e; ei.dispatchEvent(new Event('input', { bubbles: true })); }
  }, startStr, endStr);
  await sleep(800);

  await page.evaluate((sel) => {
    const ta = document.querySelector(sel);
    if (ta) { ta.focus(); ta.value = ''; }
  }, msgSel);
  await page.type(msgSel,
    "Hi Mike! Need the jack to change winter tires this weekend.",
    { delay: 30 });
  await sleep(1500);

  await clickButton(page, 'Send Request');
  await sleep(3000);

  // Capture rental ID
  let rentalId2 = null;

  const modal2Open = await page.evaluate(() => {
    const overlay = document.querySelector('[x-show="showRentalModal"]');
    return overlay && overlay.offsetHeight > 0;
  });

  if (modal2Open && jackListingId) {
    console.log('    Modal still open, API fallback...');
    const rental = await apiCallStrict(page, 'POST', '/api/v1/rentals', {
      listing_id: jackListingId,
      requested_start: start.toISOString(),
      requested_end: end.toISOString(),
      renter_message: "Hi Mike! Need the jack to change winter tires this weekend.",
    });
    rentalId2 = rental.id;
  }

  if (!rentalId2) {
    try {
      await ensureOnSite(page);
      const rentals = await apiCallStrict(page, 'GET', '/api/v1/rentals?status=pending&role=renter&limit=5');
      if (Array.isArray(rentals) && rentals.length > 0) {
        // Find the one that's not rentalId1
        for (const r of rentals) {
          if (r.id !== rentalId1) { rentalId2 = r.id; break; }
        }
        if (!rentalId2 && rentals.length > 0) rentalId2 = rentals[0].id;
      }
    } catch (e) {
      console.log(`    Rental query: ${e.message}`);
    }
  }

  if (!rentalId2) {
    console.error('\n  *** FATAL: No rental created for Scenario 2 ***\n');
    await waitForEnter('Press ENTER to close browser');
    await browser.close();
    return;
  }
  console.log(`    Scenario 2 rental: ${rentalId2}`);

  // Show Sally's dashboard briefly
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId2);
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 12 : MIKE APPROVES
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 12: Mike approves');
  await kcLogout(page);
  await kcLogin(page, 'mike');

  // Approve via API (quick, we showed UI approval in Scenario 1)
  await ensureOnSite(page);
  await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${rentalId2}/status`, { status: 'approved' });

  // Show Mike's dashboard with APPROVED badge
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId2);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 13 : SALLY CANCELS
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 13: Sally cancels');
  await kcLogout(page);

  await page.goto(storyCard('#D97706','SALLY CANCELS',
    "She found a jack next door. No need anymore.",
    "The rental was approved, but Sally cancels before pickup.<br>" +
    "No lockbox codes were generated. Clean cancel."));
  await sleep(5000);

  await kcLogin(page, 'sally');

  // Show APPROVED rental first
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId2);
  await sleep(3000);

  // Cancel via API (renter action)
  await ensureOnSite(page);
  await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${rentalId2}/status`, {
    status: 'cancelled',
    message: 'Found one next door, sorry for the trouble!',
  });

  // Show dashboard with CANCELLED badge
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId2);
  await sleep(5000);


  // ══════════════════════════════════════════════════════════
  //  SCENARIO 3 : WRONG LOCKBOX CODE
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 14 : WRONG CODE STORY CARD
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 14: Scenario 3 -- Wrong Lockbox Code');
  await page.goto(storyCard('#EA580C','SCENARIO 3','Wrong Lockbox Code',
    "Sally rents Mike's drill again.<br>" +
    "This time Mike approves and generates lockbox codes.<br>" +
    "Sally types the code wrong. Oops."));
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 15 : QUICK SETUP (create + approve + generate codes)
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 15: Quick setup -- create + approve + lockbox');

  // Sally is logged in -- create rental via API
  await ensureOnSite(page);
  const rental3 = await createRentalViaAPI(page, drillListingId,
    "Hi Mike! Back again for the drill. This time for real!");
  const rentalId3 = rental3.id;

  // Switch to Mike, approve + generate lockbox
  await kcLogout(page);
  await kcLogin(page, 'mike');
  await ensureOnSite(page);

  await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${rentalId3}/status`, { status: 'approved' });

  const lockbox3 = await apiCallStrict(page, 'POST', `/api/v1/lockbox/${rentalId3}/generate`, {
    location_hint: 'Garden shed, left shelf',
    instructions: 'Side gate code: 4521. Drill is in the red case.'
  });
  const pickupCode3 = lockbox3.pickup_code;
  const returnCode3 = lockbox3.return_code;
  console.log(`    Pickup code: ${pickupCode3}  Return code: ${returnCode3}`);

  // Show Mike's dashboard with lockbox codes visible
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId3);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 16 : SALLY TRIES WRONG CODE
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 16: Sally tries wrong code');
  await kcLogout(page);

  await page.goto(storyCard('#EA580C','WRONG CODE',
    "Sally is at the shed. She misreads the code.",
    "She types it wrong. The system rejects it.<br>" +
    'Error: "Invalid code"'));
  await sleep(5000);

  await kcLogin(page, 'sally');

  // Show Sally's dashboard with APPROVED rental
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId3);
  await sleep(3000);

  // Try the wrong code via API -- this will return an error (non-throwing)
  await ensureOnSite(page);
  const wrongResult = await apiCall(page, 'POST', `/api/v1/lockbox/${rentalId3}/verify`, { code: 'XXXXXXXX' });
  if (wrongResult && wrongResult.error) {
    console.log(`    Wrong code rejected: ${wrongResult.detail}`);
  }

  // Show an error card to make it visible on screen
  await page.goto(storyCard('#DC2626','INVALID CODE',
    'The lockbox rejected the code.',
    '"XXXXXXXX" is not the right code.<br>' +
    'Sally double-checks and tries again.'));
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 17 : SALLY ENTERS CORRECT CODE
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 17: Sally enters correct code');

  await page.goto(storyCard('#059669','CORRECT CODE',
    `Code: ${pickupCode3}`,
    "She checks the message from Mike again.<br>" +
    "Types the right code. Pickup confirmed!"));
  await sleep(4000);

  // Verify correct pickup code via API
  await ensureOnSite(page);
  await apiCallStrict(page, 'POST', `/api/v1/lockbox/${rentalId3}/verify`, { code: pickupCode3 });

  // Show dashboard with PICKED_UP status
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId3);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 18 : COMPLETE THE RENTAL CLEANLY
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 18: Complete rental cleanly');

  // Sally returns -- verify return code
  await ensureOnSite(page);
  await apiCallStrict(page, 'POST', `/api/v1/lockbox/${rentalId3}/verify`, { code: returnCode3 });

  // Show RETURNED status briefly
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId3);
  await sleep(2000);

  // Switch to Mike, complete
  await kcLogout(page);
  await kcLogin(page, 'mike');
  await ensureOnSite(page);
  await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${rentalId3}/status`, { status: 'completed' });

  // Quick flash of COMPLETED
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId3);
  await sleep(3000);


  // ══════════════════════════════════════════════════════════
  //  SCENARIO 4 : THE DISPUTE
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 19 : DISPUTE STORY CARD
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 19: Scenario 4 -- The Dispute');
  await page.goto(storyCard('#7C3AED','SCENARIO 4','The Dispute',
    "Sally rents the drill one more time.<br>" +
    "This time it comes back with a cracked housing.<br>" +
    "Mike files a dispute. They work it out."));
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 20 : QUICK SETUP (full flow to RETURNED via API)
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 20: Quick setup -- full flow to RETURNED');

  // Mike is logged in -- switch to Sally to create rental
  await kcLogout(page);
  await kcLogin(page, 'sally');
  await ensureOnSite(page);

  const rental4 = await createRentalViaAPI(page, drillListingId,
    "Hey Mike! One more time, building a bookshelf now.");
  const rentalId4 = rental4.id;

  // Switch to Mike: approve + generate lockbox
  await kcLogout(page);
  await kcLogin(page, 'mike');
  await ensureOnSite(page);

  await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${rentalId4}/status`, { status: 'approved' });

  const lockbox4 = await apiCallStrict(page, 'POST', `/api/v1/lockbox/${rentalId4}/generate`, {
    location_hint: 'Garden shed, same spot',
    instructions: 'Same as last time. Red case on the left shelf.'
  });

  // Switch to Sally: pickup
  await kcLogout(page);
  await kcLogin(page, 'sally');
  await ensureOnSite(page);
  await apiCallStrict(page, 'POST', `/api/v1/lockbox/${rentalId4}/verify`, { code: lockbox4.pickup_code });

  // Sally returns
  await apiCallStrict(page, 'POST', `/api/v1/lockbox/${rentalId4}/verify`, { code: lockbox4.return_code });

  // Show RETURNED status
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId4);
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 21 : MIKE FILES DISPUTE
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 21: Mike files dispute');
  await kcLogout(page);

  await page.goto(storyCard('#7C3AED','MIKE FINDS DAMAGE',
    "He checks the drill. Cracked housing.",
    "The drill housing has a crack on the left side.<br>" +
    "It was not there before the rental.<br>" +
    "Mike files a dispute through the system."));
  await sleep(5000);

  await kcLogin(page, 'mike');
  await ensureOnSite(page);

  // File dispute via API
  const dispute = await apiCallStrict(page, 'POST', '/api/v1/disputes', {
    rental_id: rentalId4,
    reason: 'item_damaged',
    description: 'Drill housing has a crack on the left side that was not there before the rental. Noticed immediately upon return inspection.',
  });
  const disputeId = dispute.id;
  console.log(`    Dispute filed: ${disputeId}`);

  // Show Mike's dashboard with DISPUTED badge
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId4);
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 22 : SALLY RESPONDS
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 22: Sally responds');
  await kcLogout(page);

  await page.goto(storyCard('#7C3AED','SALLY RESPONDS',
    "She gets a notification about the dispute.",
    "Sally acknowledges the damage.<br>" +
    "She should have reported it when she picked it up."));
  await sleep(5000);

  await kcLogin(page, 'sally');
  await ensureOnSite(page);

  // Respond to dispute via API
  await apiCallStrict(page, 'PATCH', `/api/v1/disputes/${disputeId}/respond`, {
    response: 'The crack was already there when I picked it up. I should have reported it right away. My mistake for not flagging it.',
  });

  // Show Sally's dashboard -- DISPUTED
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId4);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 23 : MIKE RESOLVES WITH PARTIAL REFUND
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 23: Mike resolves dispute');
  await kcLogout(page);

  await page.goto(storyCard('#7C3AED','RESOLUTION',
    "Mike reads Sally's response.",
    "They agree on a partial refund.<br>" +
    "Deposit split 50/50. Fair for both sides.<br>" +
    "Dispute resolved. Rental completed."));
  await sleep(5000);

  await kcLogin(page, 'mike');
  await ensureOnSite(page);

  // Resolve dispute via API
  await apiCallStrict(page, 'PATCH', `/api/v1/disputes/${disputeId}/resolve`, {
    resolution: 'partial_refund',
    resolution_notes: 'Agreed on partial refund. Deposit split 50/50 since damage was minor and pre-existing.',
  });

  // Show Mike's dashboard -- COMPLETED (dispute resolved)
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId4);
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 24 : OUTRO
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 24: Outro');
  await kcLogout(page);

  await page.goto(card('#1E293B','BORROWHOOD','Real situations. Real solutions.',
    '<div class="extra" style="line-height:2">' +
    'Declined -- request rejected, no hard feelings<br>' +
    'Cancelled -- plans changed, clean exit<br>' +
    'Wrong code -- rejected, try again<br>' +
    'Disputed -- damage reported, resolved with partial refund<br><br>' +
    'Every edge case handled. Every step transparent.<br><br>' +
    '<em>"Every neighborhood has a garage like his."</em></div>'));
  await sleep(10000);


  // ──────────────────────────────────────────────────────────
  //  DONE
  // ──────────────────────────────────────────────────────────
  await page.goto(card('#1E293B','CUT','Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
