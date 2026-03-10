#!/usr/bin/env node
/**
 * BORROWHOOD -- The Complete Walkthrough (v3)
 *
 * One story. Two neighbors. One rental. Every step.
 *
 * v3 improvements over v2:
 *   - Red pulsing click indicators so viewer sees every button press
 *   - page.mouse.click() on bounding boxes (proper mouse events, visible OS cursor)
 *   - Fixed selectors: x-model attributes + page.$$('button') text search
 *     (v2 bug: document.querySelector('.fixed') hit the toast container, not the modal)
 *   - API fallback for rental creation
 *   - API calls for state transitions (bulletproof)
 *   - Visible cursor movement to every interactive element
 *
 * PRE-RECORDING -- clean stale rentals from previous takes:
 *   ssh root@46.62.138.218 "docker exec postgres psql -U helix_user -d borrowhood -c \"
 *     DELETE FROM bh_lockbox_access WHERE rental_id IN
 *       (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
 *     DELETE FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
 *   \""
 *
 * Usage: node record-full-walkthrough.js [base_url]
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
      if (el.offsetWidth === 0 && el.offsetHeight === 0) return null;       // hidden
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
//  MAIN RECORDING
// ═══════════════════════════════════════════════════════════════

(async () => {
  console.log(`\n  BORROWHOOD -- The Complete Walkthrough v3`);
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

  let rentalId  = null;
  let pickupCode = null;
  let returnCode = null;


  // ──────────────────────────────────────────────────────────
  //  SCENE 1 : OBS CHECK
  // ──────────────────────────────────────────────────────────
  await page.goto(card('#DC2626','OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">THE COMPLETE WALKTHROUGH v3 | BorrowHood</div>'));
  await waitForEnter('OBS is recording and showing this RED screen?');


  // ──────────────────────────────────────────────────────────
  //  SCENE 2 : INTRO
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 2: Intro');
  await page.goto(card('#1E293B','BORROWHOOD','Every garage becomes a rental shop.',
    '<div class="extra">' +
    'Your neighbor has a drill you need once.<br>' +
    'You have a stand mixer sitting idle.<br>' +
    'BorrowHood connects you. No middlemen. No fees.<br><br>' +
    'This is the full walkthrough. Two neighbors. One rental. Every step.</div>'));
  await sleep(10000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 3 : HOME PAGE
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 3: Home page');
  await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 600, behavior: 'smooth' }));
  await sleep(3000);
  await page.evaluate(() => window.scrollBy({ top: 600, behavior: 'smooth' }));
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 4 : BROWSE
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 4: Browse');
  await page.goto(card('#4338CA','STEP 1',
    'Sally needs a drill for her deck project.',
    '<div class="extra">She opens BorrowHood and browses the neighborhood.</div>'));
  await sleep(5000);

  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 5 : DRILL DETAIL
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 5: Drill detail');
  await page.goto(storyCard('#4338CA',"MIKE'S DRILL",
    'Bosch Professional -- EUR 8/day + EUR 30 deposit',
    "Mike listed his drill last month. It sits in his garage most days.<br>" +
    "EUR 8/day to rent. EUR 30 deposit in case something breaks.<br>" +
    "Sally found it on Browse. Let's take a look."));
  await sleep(6000);

  await page.goto(`${BASE}/items/bosch-professional-drill-driver-set?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  // Scroll to price + deposit
  await page.evaluate(() => {
    for (const el of document.querySelectorAll('*'))
      if (el.textContent.includes('deposit') && el.offsetHeight < 50)
        { el.scrollIntoView({ behavior:'smooth', block:'center' }); return; }
  });
  await sleep(3000);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(2000);

  // Reviews
  await page.evaluate(() => {
    const el = document.querySelector('[x-data*="reviewSection"]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 6 : SALLY LOGS IN + RENTS THE DRILL
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 6: Sally rents');
  await page.goto(storyCard('#7C3AED','SALLY THOMPSON',
    'She wants the drill. Time to rent it.',
    "Sally logs in and requests the rental.<br>" +
    "She picks her dates and sends Mike a message."));
  await sleep(5000);

  await kcLogin(page, 'sally');

  await page.goto(`${BASE}/items/bosch-professional-drill-driver-set?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await injectClickStyle(page);
  await sleep(2000);

  // Scroll to "Rent This Item" and click with visible cursor
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(1000);
  console.log('    Opening rental modal...');
  await clickButton(page, 'Rent This Item');
  await sleep(2000);

  // Fill dates using x-model selectors (NOT the broken .fixed selector)
  console.log('    Filling rental form...');
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

  // Type message character-by-character (visible to viewer)
  const msgSel = '[x-model="rentalForm.message"]';
  await page.evaluate((sel) => {
    const ta = document.querySelector(sel);
    if (ta) { ta.focus(); ta.value = ''; }
  }, msgSel);
  await page.type(msgSel,
    "Hi Mike! I'm building a new deck this weekend and need a good drill. " +
    "I'll take great care of it. Can pick up Friday morning.",
    { delay: 30 });
  await sleep(3000);  // let the viewer read it

  // Click "Send Request" with visible cursor + red ring
  console.log('    Clicking Send Request...');
  const submitted = await clickButton(page, 'Send Request');
  await sleep(4000);  // wait for Alpine to submit + modal to close

  // ── Capture rental ID ──
  console.log('    Capturing rental ID...');

  // Check if the form actually submitted (modal closed = success)
  const modalOpen = await page.evaluate(() => {
    const overlay = document.querySelector('[x-show="showRentalModal"]');
    return overlay && overlay.offsetHeight > 0;
  });

  if (modalOpen) {
    console.log('    Modal still open -- form submit failed. Using API fallback...');
    // Extract listing ID from page's Alpine component
    const listingId = await page.evaluate(() => {
      for (const el of document.querySelectorAll('[x-data]')) {
        const attr = el.getAttribute('x-data') || '';
        const m = attr.match(/listingId:\s*'([^']+)'/);
        if (m) return m[1];
      }
      return null;
    });

    if (listingId) {
      const rental = await apiCall(page, 'POST', '/api/v1/rentals', {
        listing_id: listingId,
        requested_start: new Date(startStr).toISOString(),
        requested_end:   new Date(endStr).toISOString(),
        renter_message: "Hi Mike! I'm building a new deck this weekend and need a good drill. " +
                        "I'll take great care of it. Can pick up Friday morning.",
      });
      rentalId = rental.id;
      console.log(`    Rental created via API: ${rentalId}`);
      // Close modal by navigating away
    } else {
      console.error('    Could not extract listing ID from page');
    }
  }

  // Query API for the rental ID (whether created by form or by fallback above)
  if (!rentalId) {
    try {
      await ensureOnSite(page);
      const rentals = await apiCall(page, 'GET', '/api/v1/rentals?status=pending&role=renter&limit=5');
      if (Array.isArray(rentals) && rentals.length > 0) {
        rentalId = rentals[0].id;
      }
    } catch (e) {
      console.log(`    Rental query error: ${e.message}`);
    }
  }

  if (!rentalId) {
    console.error('\n  *** FATAL: No rental created. Cannot continue. ***\n');
    await waitForEnter('Press ENTER to close browser');
    await browser.close();
    return;
  }
  console.log(`    Rental ID: ${rentalId}`);

  // Show Sally's dashboard -- PENDING (amber badge)
  console.log('    Sally dashboard (PENDING)...');
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 7 : MIKE APPROVES
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 7: Mike approves');
  await kcLogout(page);

  await page.goto(storyCard('#1E40AF','MIKE KENEL',
    "He gets a notification. Sally wants his drill.",
    "Mike opens his dashboard and sees the request.<br>" +
    "He reads Sally's message and clicks Approve."));
  await sleep(5000);

  await kcLogin(page, 'mike');

  // Show Mike's Incoming Requests -- PENDING with Sally's message
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId);
  await sleep(5000);

  // Click "Approve" with visible cursor + red ring
  const approved = await clickButton(page, 'Approve');
  if (approved) {
    // Button click triggers Alpine's updateStatus('approved') which reloads the page
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(2000);
    // Re-show Incoming tab after reload
    await injectClickStyle(page);
    await clickButton(page, 'Incoming');
    await sleep(2000);
  } else {
    // Fallback: approve via API
    console.log('    Approve button not found, using API...');
    await ensureOnSite(page);
    await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, { status: 'approved' });
    await showDashboard(page, 'Incoming', 2000);
  }
  await highlightRental(page, rentalId);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 8 : LOCKBOX CODES
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 8: Lockbox codes');
  await page.goto(storyCard('#D97706','LOCKBOX CODES',
    'Contactless exchange. No meetup needed.',
    "Mike generates two codes: pickup and return.<br>" +
    "Sally gets the pickup code on her dashboard.<br>" +
    "No schedule coordination. Just a code and a shed."));
  await sleep(6000);

  // Generate codes via API (Mike is still logged in)
  await ensureOnSite(page);
  console.log('    Generating lockbox codes...');
  const lockbox = await apiCall(page, 'POST', `/api/v1/lockbox/${rentalId}/generate`, {
    location_hint: 'Garden shed, left shelf, behind the mower',
    instructions: 'Side gate code: 4521. Drill is in the red case.'
  });
  pickupCode = lockbox.pickup_code;
  returnCode = lockbox.return_code;
  console.log(`    Pickup: ${pickupCode}  Return: ${returnCode}`);

  // Show Mike's dashboard with codes visible (amber box)
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId);
  await sleep(6000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 9 : SALLY PICKS UP
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 9: Sally picks up');
  await kcLogout(page);

  await page.goto(storyCard('#7C3AED','SALLY PICKS UP',
    'She sees the pickup code on her dashboard.',
    "Sally goes to Mike's garden shed.<br>" +
    "She finds the drill in the red case, just like Mike said.<br>" +
    "She enters the pickup code to confirm."));
  await sleep(6000);

  await kcLogin(page, 'sally');

  // Show Sally's dashboard -- APPROVED with pickup code (blue box)
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId);
  await sleep(4000);

  // Click "I've Picked It Up" button with visible cursor
  const pickedUp = await clickButton(page, "Picked It Up");
  if (pickedUp) {
    // Button calls verifyCode(pickup_code) -> reloads page
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(2000);
    await injectClickStyle(page);
    await clickButton(page, 'My Rental');
    await sleep(2000);
  } else {
    // Fallback: verify via API
    console.log('    Pickup button not found, using API...');
    await apiCall(page, 'POST', `/api/v1/lockbox/${rentalId}/verify`, { code: pickupCode });
    await showDashboard(page, 'My Rental', 2000);
  }
  await highlightRental(page, rentalId);
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 10 : SALLY RETURNS
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 10: Sally returns');
  await page.goto(storyCard('#7C3AED','SALLY RETURNS IT',
    'Deck is done. Drill goes back.',
    "Sally puts the drill back in the red case.<br>" +
    "Returns it to the garden shed.<br>" +
    "She enters the return code to confirm."));
  await sleep(5000);

  // Sally still logged in -- navigate back to dashboard
  await showDashboard(page, 'My Rental', 2000);
  await highlightRental(page, rentalId);
  await sleep(3000);

  // Click "I've Returned It" with visible cursor
  const returned = await clickButton(page, "Returned It");
  if (returned) {
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(2000);
    await injectClickStyle(page);
    await clickButton(page, 'My Rental');
    await sleep(2000);
  } else {
    console.log('    Return button not found, using API...');
    await ensureOnSite(page);
    await apiCall(page, 'POST', `/api/v1/lockbox/${rentalId}/verify`, { code: returnCode });
    await showDashboard(page, 'My Rental', 2000);
  }
  await highlightRental(page, rentalId);
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 11 : MIKE COMPLETES
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 11: Mike completes');
  await kcLogout(page);

  await page.goto(storyCard('#1E40AF','MIKE COMPLETES',
    'Drill is back. All good.',
    "Mike checks his garden shed. Drill is there, in the red case.<br>" +
    "He marks the rental as complete.<br>" +
    "Sally's EUR 30 deposit is automatically released back to her."));
  await sleep(6000);

  await kcLogin(page, 'mike');

  // Show Mike's dashboard -- RETURNED with Complete button
  await showDashboard(page, 'Incoming', 2000);
  await highlightRental(page, rentalId);
  await sleep(4000);

  // Click "Complete" with visible cursor + red ring
  const completed = await clickButton(page, 'Complete');
  if (completed) {
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(2000);
    await injectClickStyle(page);
    await clickButton(page, 'Incoming');
    await sleep(2000);
  } else {
    console.log('    Complete button not found, using API...');
    await ensureOnSite(page);
    await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, { status: 'completed' });
    await showDashboard(page, 'Incoming', 2000);
  }
  await highlightRental(page, rentalId);
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 12 : RECAP
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 12: Recap');
  await kcLogout(page);

  await page.goto(card('#059669','DONE.',"That's the whole flow.",
    '<div class="extra" style="line-height:2">' +
    'Sally found the drill on Browse<br>' +
    'She requested the rental with dates and a message<br>' +
    'Mike approved it from his dashboard<br>' +
    'Mike generated lockbox codes (no meetup needed)<br>' +
    'Sally picked it up using the code<br>' +
    'Sally returned it when she was done<br>' +
    'Mike completed the rental<br>' +
    'Deposit auto-released back to Sally<br>' +
    'Both earned reputation points and badges</div>'));
  await sleep(12000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 13 : WORKSHOP PROFILES
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 13: Workshop profiles');
  await page.goto(card('#1E293B','EVERY USER IS A WORKSHOP',
    "Mike's garage. Sally's kitchen. Your skill.",
    '<div class="extra">Workshop profiles show skills, languages, items, and reputation.</div>'));
  await sleep(5000);

  await page.goto(`${BASE}/workshop/mikes-garage?lang=en`, { waitUntil:'networkidle2', timeout:15000 });
  await waitForImages(page);
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 500, behavior: 'smooth' }));
  await sleep(3000);

  await page.goto(`${BASE}/workshop/sallys-kitchen?lang=en`, { waitUntil:'networkidle2', timeout:15000 });
  await waitForImages(page);
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 500, behavior: 'smooth' }));
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 14 : MEMBERS
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 14: Members');
  await page.goto(`${BASE}/members?lang=en`, { waitUntil:'networkidle2', timeout:15000 });
  await waitForImages(page);
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 15 : HELPBOARD
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 15: Helpboard');
  await page.goto(card('#1E293B','HELPBOARD','Need something? Ask the neighborhood.',
    '<div class="extra">"I need a ladder this Saturday"<br>' +
    '"Anyone have a pressure washer?"<br>' +
    'Post a request. Get replies. Track status.</div>'));
  await sleep(5000);

  await page.goto(`${BASE}/helpboard?lang=en`, { waitUntil:'networkidle2', timeout:15000 });
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 16 : ITALIAN
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 16: Italian');
  await page.goto(card('#1E293B','ITALIANO','One click. Every label. Instant.',
    '<div class="extra">476 translated strings. Navigation, forms, badges,<br>' +
    'categories, filters, error messages -- nothing left behind.</div>'));
  await sleep(5000);

  await page.goto(`${BASE}/browse?lang=it`, { waitUntil:'networkidle2', timeout:15000 });
  await waitForImages(page);
  await sleep(4000);
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 17 : OUTRO
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 17: Outro');
  await page.goto(card('#1E293B','BORROWHOOD','Every garage becomes a rental shop.',
    '<div class="extra" style="line-height:2">' +
    'Open source. No platform fees. Forever.<br><br>' +
    'github.com/akenel/borrowhood<br>' +
    'Built from a camper van in Trapani, Sicily.<br><br>' +
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
