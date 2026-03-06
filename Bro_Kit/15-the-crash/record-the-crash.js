#!/usr/bin/env node
/**
 * THE CRASH -- Recording Script (v4 -- "Syd Field Edition")
 *
 * Every click visible. Every login visible. Every status change on screen.
 * No API shortcuts that skip what the viewer needs to see.
 * Follow the money: rental fee + deposit shown separately, always.
 *
 * ACT 1 -- THE RENTAL (Scenes 1-15):
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- "THE CRASH"
 *   3.  Pietro character overlay on homepage
 *   4.  Pietro's workshop profile (guest) -- scroll through skills + drones
 *   5.  Sally character overlay
 *   6.  Demo login page -- click Sally (VISIBLE login)
 *   7.  Sally views Mini 4 Pro listing
 *   8.  Sally clicks "Rent This Item", fills form, clicks "Send Request"
 *   9.  Sally's dashboard -> My Rentals -> sees PENDING rental
 *  10.  Card: THE INVOICE (rental EUR 50 + deposit EUR 100 = EUR 150)
 *  11.  Deposit created via API, toast visible
 *  12.  Demo login page -- click Pietro (VISIBLE login switch)
 * 12b.  Pietro checks notification bell
 *  13.  Pietro's dashboard -> Incoming Requests -> sees pending rental
 *  14.  Pietro clicks APPROVE button (visible click + ring)
 *
 * ACT 2 -- THE FLIGHT (Scenes 15-19):
 *  15.  Card: PICKUP DAY (shows total paid, clock starts)
 *  16.  Demo login page -- click Sally
 * 16b.  Sally checks notification bell -- approval
 *  17.  Sally's My Rentals -> sees APPROVED rental + lockbox codes
 *  18.  Sally clicks "I've Picked It Up"
 *  19.  Sally's My Rentals -> status: PICKED_UP
 *
 * ACT 3 -- THE CRASH (Scenes 20-26):
 *  20.  Card: THE RETURN (drone comes back damaged)
 *  21.  Sally clicks "I've Returned It"
 *  22.  Card: PIETRO FILES A DISPUTE
 *  23.  Demo login page -- click Pietro
 *  24.  Pietro's Incoming Requests -> sees RETURNED rental
 *  25.  Pietro files dispute via UI (select reason, type description, submit)
 *  26.  Pietro sees DISPUTED status
 *
 * ACT 4 -- THE RESOLUTION (Scenes 27-35):
 *  27.  Card: SALLY'S REBUTTAL (both sides get heard)
 *  28.  Demo login page -- click Sally
 *  29.  Sally sees DISPUTED rental
 *  30.  Sally submits rebuttal via UI
 *  31.  Card: THE RESOLUTION (full money breakdown: rental paid + deposit split)
 *  32.  Demo login page -- click Pietro
 *  33.  Pietro resolves dispute via UI
 *  34.  Card: MONEY SETTLEMENT (rental EUR 50 paid, deposit: EUR 70 to Pietro, EUR 30 to Sally)
 *  35.  Sally sees final status
 *
 * ACT 5 -- THE SEED (Scenes 36-41):
 *  36.  Card: THE SEED (every problem is a door)
 *  37.  Pietro browses Sally's workshop
 *  38.  Pietro rents cookie cutters (rental EUR 35 + deposit EUR 20 = EUR 55)
 *  39.  Card: THE COOKIE ORDER (the peace offering)
 *  40.  Sally sees notification, approves
 *  41.  Card: FULL CIRCLE (overlay chat)
 *
 * EPILOGUE (Scenes 42-44):
 *  42.  Card: THE LIGHTBULB (Sally can't deliver, Pietro has a drone)
 *  43.  Card: THE PARTNERSHIP (drone delivery for cookies)
 *  44.  GREEN "TO BE CONTINUED" card
 *
 * Usage: node record-the-crash.js [base_url]
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

function card(bg, title, subtitle, extra = '') {
  return `data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html><html><head><style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: ${bg}; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100vh; width: 100vw;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: white; text-align: center; padding: 40px 60px;
  }
  h1 { font-size: 148px; font-weight: 900; margin-bottom: 20px; text-shadow: 4px 4px 16px rgba(0,0,0,0.4); letter-spacing: -3px; line-height: 1.0; }
  h2 { font-size: 64px; font-weight: 400; opacity: 0.9; margin-bottom: 16px; line-height: 1.3; }
  .extra { font-size: 46px; opacity: 0.75; margin-top: 12px; line-height: 1.5; max-width: 1600px; }
  .badge { display: inline-block; padding: 12px 32px; border-radius: 12px; background: rgba(255,255,255,0.2); font-size: 48px; font-weight: 700; margin-top: 20px; }
  .hl { color: #FCD34D; font-weight: 700; }
  .red { color: #FCA5A5; font-weight: 700; }
  .green { color: #6EE7B7; font-weight: 700; }
  .check { color: #34D399; }
  .dim { opacity: 0.5; }
  .step { font-size: 36px; opacity: 0.65; margin-top: 12px; line-height: 1.6; max-width: 1400px; }
</style></head><body>
  <h1>${title}</h1><h2>${subtitle}</h2>${extra}
</body></html>`)}`;
}

// -- API helper --
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

// -- VISIBLE demo login: navigate to /demo-login, click username --
// NOTE: Do NOT setZoom before clicking -- zoom=1.5 shifts getBoundingClientRect
// coordinates vs fixed-position ring overlay, making the ring land on the wrong card.
async function visibleLogin(page, username) {
  await page.goto(`${BASE}/demo-login`, { waitUntil: 'networkidle2', timeout: 15000 });
  // Show full cast at 100% for 3s so viewer sees all characters
  await page.evaluate(() => { document.body.style.zoom = '1'; });
  await sleep(3000);

  // Scroll to make sure the user card is visible
  await page.evaluate((u) => {
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
      if (btn.textContent.includes('@' + u)) {
        btn.scrollIntoView({ block: 'center' });
        return;
      }
    }
  }, username);
  await sleep(500);

  // Find the BUTTON element specifically (not a parent div)
  // The demo-login template uses: <button @click="login('username')"> with @username inside
  const clickPos = await page.evaluate((u) => {
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
      if (btn.textContent.includes('@' + u)) {
        const box = btn.getBoundingClientRect();
        if (box.width > 0 && box.height > 0) {
          return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        }
      }
    }
    return null;
  }, username);

  if (clickPos) {
    await showRing(page, clickPos.x, clickPos.y);
    await sleep(400);
    // Click the button via page.click at coordinates (triggers real mouse event)
    await page.mouse.click(clickPos.x, clickPos.y);
    console.log(`  Clicked @${username} card`);
  } else {
    console.log(`  WARN: Could not find @${username} button on demo-login, using API fallback`);
    await demoLogin(page, username);
    await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
    console.log(`  Logged in as ${username} (API fallback)`);
    return;
  }

  // Wait for redirect to /dashboard (login does window.location.href = '/dashboard')
  try {
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
  } catch (e) {
    // If navigation already happened, this times out -- that's OK
  }
  await sleep(1000);

  // Verify we're authenticated: nav should NOT show "Log In" button
  const isLoggedIn = await page.evaluate(() => {
    const nav = document.querySelector('nav') || document.querySelector('header');
    return nav ? !nav.textContent.includes('Log In') : false;
  });
  if (!isLoggedIn) {
    console.log(`  WARN: Login may have failed (nav still shows "Log In"), trying API fallback`);
    await demoLogin(page, username);
  }
  console.log(`  Logged in as ${username} (visible)`);
}

// -- API-only demo login (fallback) --
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

async function demoLogout(page) {
  await apiCall(page, 'POST', '/api/v1/demo/logout', {});
  await sleep(300);
}

// -- DOM overlay (stays on BASE origin) --
// Auto-scrolls if content overflows viewport so viewer reads everything.
async function showOverlay(page, name, subtitle, extra = '', duration = 9000) {
  await page.evaluate(() => { document.body.style.zoom = '1'; });
  await page.evaluate((n, s, e) => {
    const old = document.getElementById('name-card-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'name-card-overlay';
    overlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      z-index: 99999; display: flex; flex-direction: column;
      align-items: center; justify-content: flex-start;
      background: rgba(30,41,59,0.95); color: white;
      font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
      padding: 60px 80px 80px; overflow-y: auto;
      scroll-behavior: smooth;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:128px; font-weight:900; margin-bottom:16px;
                 text-shadow:4px 4px 16px rgba(0,0,0,0.4); letter-spacing:-3px; flex-shrink:0">${n}</h1>
      <h2 style="font-size:56px; font-weight:400; opacity:0.9;
                 margin-bottom:12px; line-height:1.3; flex-shrink:0">${s}</h2>
      ${e ? `<div id="overlay-extra" style="font-size:40px; opacity:0.75; margin-top:8px; line-height:1.6; max-width:1500px; flex-shrink:0">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
  }, name, subtitle, extra);

  // Give viewer time to read the top, then auto-scroll if content overflows
  const halfDuration = Math.floor(duration / 2);
  await sleep(halfDuration);

  // Auto-scroll overlay to bottom if it has overflow
  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o && o.scrollHeight > o.clientHeight) {
      o.scrollTo({ top: o.scrollHeight, behavior: 'smooth' });
    }
  });
  await sleep(halfDuration);

  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o) { o.style.transition = 'opacity 0.5s'; o.style.opacity = '0'; }
  });
  await sleep(600);
  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o) o.remove();
  });
}

// -- Smooth scroll --
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

// -- Set 150% zoom --
async function setZoom(page) {
  await page.evaluate(() => { document.body.style.zoom = '1.5'; });
  await sleep(300);
}

// -- Show red click ring --
async function showRing(page, x, y) {
  await page.evaluate((px, py) => {
    const ring = document.createElement('div');
    ring.style.cssText = `
      position: fixed; left: ${px - 30}px; top: ${py - 30}px;
      width: 60px; height: 60px; border-radius: 50%;
      border: 5px solid #DC2626; background: rgba(220,38,38,0.15);
      z-index: 99999; pointer-events: none;
      animation: clickRingPulse 1.2s ease-out forwards;
    `;
    if (!document.getElementById('click-ring-style')) {
      const style = document.createElement('style');
      style.id = 'click-ring-style';
      style.textContent = `
        @keyframes clickRingPulse {
          0% { transform: scale(0.5); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.8; }
          100% { transform: scale(1.5); opacity: 0; }
        }
      `;
      document.head.appendChild(style);
    }
    document.body.appendChild(ring);
    setTimeout(() => ring.remove(), 1500);
  }, x, y);
}

// -- Click element by text with ring --
async function clickWithRing(page, text, scope = 'button') {
  const pos = await page.evaluate((txt, s) => {
    const els = document.querySelectorAll(s);
    for (const el of els) {
      if (el.textContent.trim().includes(txt) && !el.closest('.fixed')) {
        const box = el.getBoundingClientRect();
        if (box.width > 0 && box.height > 0) {
          return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        }
      }
    }
    return null;
  }, text, scope);
  if (!pos) { console.log(`  WARN: "${text}" not found`); return false; }
  await showRing(page, pos.x, pos.y);
  await sleep(400);
  await page.evaluate((txt, s) => {
    const els = document.querySelectorAll(s);
    for (const el of els) {
      if (el.textContent.trim().includes(txt) && !el.closest('.fixed')) {
        el.click();
        return;
      }
    }
  }, text, scope);
  await sleep(2000);
  return true;
}

// -- Type into input with visible typing --
async function typeSlowly(page, selector, text, delay = 60) {
  await page.focus(selector);
  for (const char of text) {
    await page.keyboard.type(char, { delay });
  }
  await sleep(500);
}

// -- Show toast notification --
async function showToast(page, message, type = 'success') {
  await page.evaluate((msg, t) => {
    window.dispatchEvent(new CustomEvent('toast', {
      detail: { type: t, message: msg }
    }));
  }, message, type);
  await sleep(3000);
}

// -- Navigate to dashboard tab --
async function goToDashboardTab(page, tabName) {
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  await clickWithRing(page, tabName, '[role="tab"], button, a');
  await sleep(3000);
}


// ======================================================================
// == MAIN ==============================================================
// ======================================================================
(async () => {
  console.log(`\n  THE CRASH -- Recording Script (v3)`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Auth: visibleLogin (demo-login page clicks)`);
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
      '--disable-features=TranslateUI',
      '--lang=en',
    ]
  });

  const page = await browser.newPage();
  await page.setViewport(VP);

  // Pre-flight: establish cookie domain
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  console.log('  Pre-flight: ready\n');

  // ============================================================
  // SCENE 1: OBS CHECK (RED)
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured',
    '<div class="extra">THE CRASH | BorrowHood | EP15</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');


  // ============================================================
  // SCENE 2: INTRO CARD (10s)
  // ============================================================
  console.log('  Scene 2: Intro card');
  await page.goto(card(
    'linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%)',
    'THE CRASH',
    'Drones, Deposits & Disputes',
    '<div class="badge">EDGE CASE</div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 3: PIETRO FERRETTI (character overlay on homepage, 8s)
  // ============================================================
  console.log('  Scene 3: Pietro character card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  await showOverlay(page,
    'PIETRO FERRETTI',
    'Licensed drone pilot. Scopello, Sicily.',
    'He has 3 drones. From beginner Mini to pro Mavic.<br>Rent the gear or hire the pilot.',
    8000
  );


  // ============================================================
  // SCENE 4: PIETRO'S WORKSHOP (guest view -- scroll through)
  // ============================================================
  console.log('  Scene 4: Pietro\'s workshop profile');
  await page.goto(`${BASE}/workshop/pietros-drones`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  console.log('  Scene 4b: Skills + reputation');
  await smoothScroll(page, 400);
  await sleep(4000);

  console.log('  Scene 4c: Drone fleet');
  await smoothScroll(page, 500);
  await sleep(5000);


  // ============================================================
  // SCENE 5: SALLY THOMPSON (character overlay, 8s)
  // ============================================================
  console.log('  Scene 5: Sally character card');
  await showOverlay(page,
    'SALLY THOMPSON',
    'She wants to rent a drone for vacation photos.',
    'The DJI Mini 4 Pro. Under 249g. No license needed.<br>EUR 25/day. EUR 100 deposit.',
    8000
  );


  // ============================================================
  // SCENE 6: VISIBLE LOGIN AS SALLY
  // ============================================================
  console.log('  Scene 6: Login as Sally (visible)');
  await visibleLogin(page, 'sally');


  // ============================================================
  // SCENE 7: SALLY VIEWS MINI 4 PRO
  // ============================================================
  console.log('  Scene 7: Sally views Mini 4 Pro');
  await page.goto(`${BASE}/items/dji-mini-4-pro-beginner-friendly`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Scroll to see details
  await smoothScroll(page, 350);
  await sleep(3000);


  // ============================================================
  // SCENE 8: SALLY REQUESTS RENTAL (visible form)
  // ============================================================
  console.log('  Scene 8: Sally requests rental');

  // Scroll back up to see Rent button
  await page.evaluate(() => window.scrollTo(0, 0));
  await sleep(1000);

  // Get listing ID for API fallback
  const miniRentListingId = await page.evaluate(() => {
    const rentalDiv = document.querySelector('[x-data*="listingId"]');
    if (!rentalDiv) return null;
    if (rentalDiv._x_dataStack && rentalDiv._x_dataStack.length > 0) {
      return rentalDiv._x_dataStack[0].listingId;
    }
    const match = rentalDiv.getAttribute('x-data').match(/listingId:\s*'([^']+)'/);
    return match ? match[1] : null;
  });
  console.log(`  Mini 4 Pro rent listing ID: ${miniRentListingId}`);

  // Calculate dates
  const startDate = new Date(Date.now() + 3 * 86400000);
  const endDate = new Date(Date.now() + 5 * 86400000);
  const startISO = startDate.toISOString();
  const endISO = endDate.toISOString();
  const startStr = startDate.toISOString().split('T')[0];
  const endStr = endDate.toISOString().split('T')[0];

  // Debug: check auth state and button availability
  const pageDebug = await page.evaluate(() => {
    const cookies = document.cookie;
    const hasBhSession = cookies.includes('bh_session');
    const allBtns = Array.from(document.querySelectorAll('button')).map(b => ({
      text: b.textContent.trim().substring(0, 60),
      visible: b.getBoundingClientRect().width > 0,
      inFixed: !!b.closest('.fixed'),
    }));
    const allLinks = Array.from(document.querySelectorAll('a')).filter(a =>
      a.textContent.includes('Rent') || a.textContent.includes('Login') || a.textContent.includes('rent')
    ).map(a => ({ text: a.textContent.trim().substring(0, 60), href: a.href }));
    return { hasBhSession, buttonCount: allBtns.length, buttons: allBtns.slice(0, 15), rentLinks: allLinks };
  });
  console.log(`  Auth cookie present: ${pageDebug.hasBhSession}`);
  console.log(`  Buttons on page: ${pageDebug.buttonCount}`);
  if (pageDebug.buttons.length > 0) {
    for (const b of pageDebug.buttons) {
      console.log(`    [${b.visible ? 'VIS' : 'HID'}] ${b.inFixed ? '(fixed) ' : ''}${b.text}`);
    }
  }
  if (pageDebug.rentLinks.length > 0) {
    console.log(`  Rent/Login links: ${JSON.stringify(pageDebug.rentLinks)}`);
  }

  // Wait for "Rent This Item" button to render (depends on auth cookie + Alpine init)
  try {
    await page.waitForFunction(() => {
      const btns = document.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.trim().includes('Rent This Item') && btn.getBoundingClientRect().width > 0) return true;
      }
      return false;
    }, { timeout: 8000 });
  } catch (e) {
    console.log('  WARN: "Rent This Item" button did not appear within 8s -- user may not be authenticated');
  }

  // Click "Rent This Item"
  const hasRentBtn = await clickWithRing(page, 'Rent This Item', 'button, a');
  if (hasRentBtn) {
    await sleep(1500);

    // Fill dates
    await page.evaluate((s, e) => {
      const dateInputs = document.querySelectorAll('input[type="date"]');
      if (dateInputs[0]) { dateInputs[0].value = s; dateInputs[0].dispatchEvent(new Event('input', {bubbles:true})); }
      if (dateInputs[1]) { dateInputs[1].value = e; dateInputs[1].dispatchEvent(new Event('input', {bubbles:true})); }
      // Also sync Alpine
      const rentalDiv = document.querySelector('[x-data*="listingId"]');
      if (rentalDiv && rentalDiv._x_dataStack && rentalDiv._x_dataStack.length > 0) {
        rentalDiv._x_dataStack[0].rentalForm.start = s;
        rentalDiv._x_dataStack[0].rentalForm.end = e;
      }
    }, startStr, endStr);
    console.log(`  Pickup: ${startStr}, Return: ${endStr}`);
    await sleep(1000);

    // Type message
    const textarea = await page.$('textarea');
    if (textarea) {
      await typeSlowly(page, 'textarea',
        'Vacation in Scopello next week. Want aerial shots of the coastline.', 30);
      await page.evaluate(() => {
        const ta = document.querySelector('textarea');
        const rentalDiv = document.querySelector('[x-data*="listingId"]');
        if (ta && rentalDiv && rentalDiv._x_dataStack && rentalDiv._x_dataStack.length > 0) {
          rentalDiv._x_dataStack[0].rentalForm.message = ta.value;
        }
      });
      await sleep(1000);
    }

    // Click Send Request
    const submitted = await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.trim().includes('Send Request') ||
            btn.classList.contains('bg-indigo-600') ||
            btn.getAttribute('@click') === 'submitRental()') {
          const box = btn.getBoundingClientRect();
          if (box.width > 0 && box.height > 0) {
            btn.click();
            return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
          }
        }
      }
      return null;
    });
    if (submitted) {
      await showRing(page, submitted.x, submitted.y);
      console.log('  Clicked Send Request');
    }
    await sleep(3000);
  }

  // Check if rental was created via UI
  const myRentals = await apiCall(page, 'GET', '/api/v1/rentals?role=renter&status=pending');
  let rentalId = null;
  if (myRentals.data && myRentals.data.length > 0) {
    rentalId = myRentals.data[0].id;
    console.log(`  Rental created via UI: ${rentalId}`);
  }

  // API fallback
  if (!rentalId && miniRentListingId) {
    console.log('  UI form failed -- creating rental via API fallback');
    const rentalResp = await apiCall(page, 'POST', '/api/v1/rentals', {
      listing_id: miniRentListingId,
      requested_start: startISO,
      requested_end: endISO,
      renter_message: 'Vacation in Scopello next week. Want aerial shots of the coastline.',
    });
    console.log(`  API fallback response: ${rentalResp.status} ${JSON.stringify(rentalResp.data)}`);
    if (rentalResp.data && rentalResp.data.id) {
      rentalId = rentalResp.data.id;
    }
    if (rentalId) {
      await showToast(page, 'Rental request sent to Pietro!');
    }
  }
  await sleep(2000);

  // HARD FAIL
  if (!rentalId) {
    console.error('\n  FATAL: Rental creation failed. rentalId is null.');
    await page.goto(card('#DC2626', 'SCRIPT ERROR', 'Rental creation failed',
      '<div class="extra">rentalId is null. Check console.</div>'));
    await waitForEnter('Fix the issue and restart. Press ENTER to close');
    await browser.close();
    process.exit(1);
  }
  console.log(`  Rental ID confirmed: ${rentalId}`);


  // ============================================================
  // SCENE 9: SALLY'S MY RENTALS -- SEE PENDING
  // ============================================================
  console.log('  Scene 9: Sally sees PENDING rental');
  await goToDashboardTab(page, 'My Rentals');
  await sleep(4000);  // Let viewer read the rental card + PENDING badge


  // ============================================================
  // SCENE 10: DEPOSIT HELD OVERLAY (10s)
  // ============================================================
  console.log('  Scene 10: Invoice explainer card');
  await showOverlay(page,
    'THE INVOICE',
    'Two charges. Always.',
    '<div style="text-align:left; font-size:30px; line-height:1.8">' +
    '<span style="color:#6EE7B7">RENTAL FEE:</span> EUR 25/day x 2 days = <span style="color:#FCD34D; font-weight:700">EUR 50</span><br>' +
    '<span style="opacity:0.6">(This is the cost of borrowing. Non-refundable.)</span><br><br>' +
    '<span style="color:#6EE7B7">SECURITY DEPOSIT:</span> <span style="color:#FCD34D; font-weight:700">EUR 100</span><br>' +
    '<span style="opacity:0.6">(Return it undamaged -- you get this back in full.)</span><br><br>' +
    '<span style="border-top:1px solid rgba(255,255,255,0.3); padding-top:8px; display:block">' +
    'TOTAL CHARGED: <span style="color:#FCD34D; font-weight:700; font-size:36px">EUR 150</span></span><br>' +
    '<span style="opacity:0.5">Same as every car rental, every equipment hire, every Airbnb.</span></div>',
    14000
  );


  // ============================================================
  // SCENE 11: CREATE DEPOSIT (API + visible toast)
  // ============================================================
  console.log('  Scene 11: Deposit created');
  const depositResp = await apiCall(page, 'POST', '/api/v1/deposits', {
    rental_id: rentalId,
    amount: 100.0,
    currency: 'EUR',
  });
  console.log(`  Deposit created: ${depositResp.data?.id || depositResp.status}`);
  await showToast(page, 'Payment: EUR 50 rental + EUR 100 deposit held');
  await sleep(3000);
  await demoLogout(page);


  // ============================================================
  // SCENE 12: VISIBLE LOGIN AS PIETRO
  // ============================================================
  console.log('  Scene 12: Login as Pietro (visible)');
  await visibleLogin(page, 'pietro');


  // ============================================================
  // SCENE 12b: PIETRO CHECKS NOTIFICATION BELL
  // ============================================================
  console.log('  Scene 12b: Pietro sees rental request notification');
  // Navigate to dashboard first so bell is visible
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Click the notification bell
  const bellClicked = await page.evaluate(() => {
    // The bell button is inside a div with x-data containing loadSummary
    const bellBtn = document.querySelector('button svg path[d*="M15 17h5l-1.405"]');
    if (bellBtn) {
      const btn = bellBtn.closest('button');
      if (btn) {
        const box = btn.getBoundingClientRect();
        btn.click();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  });
  if (bellClicked) {
    await showRing(page, bellClicked.x, bellClicked.y);
    console.log('  Bell icon clicked');
  }
  await sleep(3000);  // Let dropdown open and load notifications -- viewer sees the list
  await sleep(3000);  // Extra pause so viewer can read the notification text

  // Close the dropdown by clicking elsewhere
  await page.click('body');
  await sleep(1000);


  // ============================================================
  // SCENE 13: PIETRO'S INCOMING REQUESTS -- SEES PENDING
  // ============================================================
  console.log('  Scene 13: Pietro sees pending rental');
  await goToDashboardTab(page, 'Incoming Requests');
  await sleep(4000);  // Viewer sees: "DJI Mini 4 Pro" + Sally's message + PENDING badge


  // ============================================================
  // SCENE 14: PIETRO CLICKS APPROVE (visible!)
  // ============================================================
  console.log('  Scene 14: Pietro clicks Approve');
  const approved = await clickWithRing(page, 'Approve', 'button');
  if (approved) {
    console.log('  Approve button clicked');
  } else {
    // Fallback via API
    console.log('  WARN: Approve button not found, using API');
    await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, { status: 'approved' });
    await showToast(page, 'Rental approved!');
  }
  await sleep(4000);  // Wait for page to reload/update, show APPROVED badge
  await demoLogout(page);


  // ================================================================
  // == ACT 2: THE FLIGHT ==========================================
  // ================================================================
  console.log('\n  === ACT 2: THE FLIGHT ===\n');

  // ============================================================
  // SCENE 15: PICKUP DAY OVERLAY (10s)
  // ============================================================
  console.log('  Scene 15: Pickup day card');
  // Navigate to a neutral page for overlay background
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await showOverlay(page,
    'ACT II \u00BB THE FLIGHT',
    'Sally collects the Mini 4 Pro from Pietro.',
    '<div style="text-align:left; font-size:30px; line-height:1.8">' +
    '<span style="color:#6EE7B7">Rental paid:</span> EUR 50 (2 days)<br>' +
    '<span style="color:#6EE7B7">Deposit held:</span> EUR 100 (refundable)<br>' +
    '<span style="color:#6EE7B7">Lockbox code:</span> generated by Pietro<br><br>' +
    'Status: APPROVED to PICKED_UP.<br>' +
    '<span style="color:#FCD34D; font-weight:700">The clock starts ticking.</span></div>',
    10000
  );


  // ============================================================
  // SCENE 16: VISIBLE LOGIN AS SALLY
  // ============================================================
  console.log('  Scene 16: Login as Sally (visible)');
  await visibleLogin(page, 'sally');


  // ============================================================
  // SCENE 16b: SALLY CHECKS NOTIFICATION BELL -- SEES APPROVED
  // ============================================================
  console.log('  Scene 16b: Sally sees approval notification');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Click the notification bell
  const sallyBell = await page.evaluate(() => {
    const bellBtn = document.querySelector('button svg path[d*="M15 17h5l-1.405"]');
    if (bellBtn) {
      const btn = bellBtn.closest('button');
      if (btn) {
        const box = btn.getBoundingClientRect();
        btn.click();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  });
  if (sallyBell) {
    await showRing(page, sallyBell.x, sallyBell.y);
    console.log('  Bell icon clicked');
  }
  await sleep(3000);  // Dropdown opens, notifications load
  await sleep(3000);  // Viewer reads: "Your rental request has been approved"

  // Close dropdown
  await page.click('body');
  await sleep(1000);


  // ============================================================
  // SCENE 17: SALLY'S MY RENTALS -- SEES APPROVED + LOCKBOX
  // ============================================================
  console.log('  Scene 17: Sally sees APPROVED rental');
  await goToDashboardTab(page, 'My Rentals');
  await sleep(3000);

  // Generate lockbox codes as Pietro (API) so Sally can see them
  // First login as Pietro silently to generate codes
  await demoLogout(page);
  await demoLogin(page, 'pietro');
  const lockResp = await apiCall(page, 'POST', `/api/v1/lockbox/${rentalId}/generate`, {
    location_hint: 'Pietro\'s workshop, blue shelf, top row',
    instructions: 'Enter the 6-digit code on the combination lock. Pull to open.',
  });
  console.log(`  Lockbox codes generated: ${lockResp.data?.pickup_code || lockResp.status}`);
  await demoLogout(page);

  // Back to Sally
  await demoLogin(page, 'sally');
  await goToDashboardTab(page, 'My Rentals');
  await sleep(3000);  // Viewer sees lockbox codes + "I've Picked It Up" button


  // ============================================================
  // SCENE 18: SALLY CLICKS "I'VE PICKED IT UP"
  // ============================================================
  console.log('  Scene 18: Sally clicks pickup');
  const pickedUp = await clickWithRing(page, "I've Picked It Up", 'button');
  if (pickedUp) {
    console.log('  Pickup button clicked');
    await sleep(4000);  // Page reloads after verify
  } else {
    // Fallback: transition via API
    console.log('  WARN: Pickup button not found, using API');
    await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, { status: 'picked_up' });
    await showToast(page, 'Item picked up! Rental is active.');
    await sleep(2000);
  }


  // ============================================================
  // SCENE 19: SALLY'S MY RENTALS -- STATUS PICKED_UP
  // ============================================================
  console.log('  Scene 19: Sally sees PICKED_UP status');
  await goToDashboardTab(page, 'My Rentals');
  await sleep(4000);  // Viewer sees: PICKED_UP badge + return code


  // ================================================================
  // == ACT 3: THE CRASH ==========================================
  // ================================================================
  console.log('\n  === ACT 3: THE CRASH ===\n');

  // ============================================================
  // SCENE 20: THE RETURN OVERLAY (12s)
  // ============================================================
  console.log('  Scene 20: Return / damage card');
  await showOverlay(page,
    'ACT III \u00BB THE CRASH',
    'Two days later. The drone comes back.',
    '<div style="text-align:left; font-size:30px; line-height:1.8">' +
    'Gimbal cracked. One propeller snapped.<br>' +
    'Sally says it was a wind gust over the Scopello cliffs.<br><br>' +
    '<span style="color:#6EE7B7">Rental fee (EUR 50):</span> already paid. Non-refundable.<br>' +
    '<span style="color:#FCD34D">Deposit (EUR 100):</span> still held. This is where it gets interesting.<br><br>' +
    '<span style="color:#FCA5A5; font-weight:700">The damage is real. Now what?</span></div>',
    12000
  );


  // ============================================================
  // SCENE 21: SALLY CLICKS "I'VE RETURNED IT"
  // ============================================================
  console.log('  Scene 21: Sally clicks return');
  // Reload dashboard to see return button
  await goToDashboardTab(page, 'My Rentals');
  await sleep(2000);

  const returned = await clickWithRing(page, "I've Returned It", 'button');
  if (returned) {
    console.log('  Return button clicked');
    await sleep(4000);
  } else {
    console.log('  WARN: Return button not found, using API');
    await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, { status: 'returned' });
    await showToast(page, 'Item returned. Owner will inspect.');
    await sleep(2000);
  }
  await demoLogout(page);


  // ============================================================
  // SCENE 22: DISPUTE EXPLAINER OVERLAY (10s)
  // ============================================================
  console.log('  Scene 22: Dispute explainer card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await showOverlay(page,
    'PIETRO FILES A DISPUTE',
    'The gimbal is cracked. A propeller snapped.',
    'Reason: ITEM DAMAGED<br>Evidence: photos of the cracked gimbal<br><br>The rental status changes to DISPUTED.<br>Now Sally gets to respond -- her side of the story.',
    10000
  );


  // ============================================================
  // SCENE 23: VISIBLE LOGIN AS PIETRO
  // ============================================================
  console.log('  Scene 23: Login as Pietro (visible)');
  await visibleLogin(page, 'pietro');


  // ============================================================
  // SCENE 24: PIETRO'S INCOMING REQUESTS -- SEES RETURNED
  // ============================================================
  console.log('  Scene 24: Pietro sees RETURNED rental');
  await goToDashboardTab(page, 'Incoming Requests');
  await sleep(4000);


  // ============================================================
  // SCENE 25: FILE DISPUTE (visible UI form)
  // ============================================================
  console.log('  Scene 25: Pietro files dispute via UI');

  // Click "File Dispute" button
  await clickWithRing(page, 'File Dispute', 'button');
  await sleep(2000);

  // Select reason from dropdown
  await page.select('select[x-model="disputeReason"]', 'item_damaged');
  await sleep(1500);

  // Type description in textarea
  const disputeDesc = 'DJI Mini 4 Pro returned with cracked gimbal and one propeller snapped off. Gimbal replacement costs EUR 55, propeller set EUR 15. Total damage: EUR 70.';
  await page.click('textarea[x-model="disputeDescription"]');
  await page.type('textarea[x-model="disputeDescription"]', disputeDesc, { delay: 15 });
  await sleep(2000);

  // Click Submit Dispute
  await clickWithRing(page, 'Submit Dispute', 'button');
  await sleep(4000); // Wait for toast + reload

  // Grab dispute ID for later scenes
  let disputeId = null;
  try {
    const dResp = await apiCall(page, 'GET', '/api/v1/disputes?limit=1');
    if (dResp.data && dResp.data.length > 0) {
      disputeId = dResp.data[0].id;
    }
  } catch(e) { console.log('  Could not fetch dispute ID:', e.message); }
  console.log(`  Dispute filed: ${disputeId || 'unknown'}`);


  // ============================================================
  // SCENE 26: PIETRO'S INCOMING REQUESTS -- STATUS DISPUTED
  // ============================================================
  console.log('  Scene 26: Pietro sees DISPUTED status');
  // Reload to show updated status
  await goToDashboardTab(page, 'Incoming Requests');
  await sleep(4000);  // Viewer sees: DISPUTED badge
  await demoLogout(page);


  // ================================================================
  // == ACT 4: THE RESOLUTION ======================================
  // ================================================================
  console.log('\n  === ACT 4: THE RESOLUTION ===\n');

  // ============================================================
  // SCENE 27: SALLY'S REBUTTAL OVERLAY (10s)
  // ============================================================
  console.log('  Scene 27: Rebuttal explainer card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await showOverlay(page,
    "ACT IV \u00BB SALLY'S REBUTTAL",
    'Both sides get heard.',
    'Sally responds to the dispute with her side.<br>"Wind gust over the Scopello cliffs -- not negligence."<br><br>Status moves from FILED to UNDER_REVIEW.<br><span style="color:#FCD34D; font-weight:700">The platform does not take sides. It tracks both.</span>',
    10000
  );


  // ============================================================
  // SCENE 28: VISIBLE LOGIN AS SALLY
  // ============================================================
  console.log('  Scene 28: Login as Sally (visible)');
  await visibleLogin(page, 'sally');


  // ============================================================
  // SCENE 29: SALLY'S MY RENTALS -- SEES DISPUTED
  // ============================================================
  console.log('  Scene 29: Sally sees DISPUTED rental');
  await goToDashboardTab(page, 'My Rentals');
  await sleep(4000);


  // ============================================================
  // SCENE 30: SALLY SUBMITS REBUTTAL (visible UI form)
  // ============================================================
  console.log('  Scene 30: Sally submits rebuttal via UI');

  // The dispute response form should be visible on the DISPUTED rental card
  const rebuttalText = 'Wind gust caught the drone over the Scopello cliffs. I followed all safety instructions Pietro gave me. The gimbal housing was already loose when I picked it up. I accept the propeller cost but not the full gimbal replacement.';
  await page.click('textarea[x-model="responseText"]');
  await page.type('textarea[x-model="responseText"]', rebuttalText, { delay: 15 });
  await sleep(2000);

  // Click Submit Response
  await clickWithRing(page, 'Submit Response', 'button');
  await sleep(4000); // Wait for toast + reload
  console.log('  Rebuttal submitted via UI');
  await demoLogout(page);


  // ============================================================
  // SCENE 31: THE RESOLUTION OVERLAY (12s)
  // ============================================================
  console.log('  Scene 31: Resolution explainer card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await showOverlay(page,
    'THE RESOLUTION',
    'Pietro decides: partial deposit.',
    '<div style="text-align:left; font-size:28px; line-height:1.8">' +
    '<span style="text-decoration:underline; color:#6EE7B7">WHAT SALLY PAID:</span><br>' +
    '&nbsp;&nbsp;Rental fee: EUR 50 (2 days x EUR 25) -- <span style="opacity:0.6">non-refundable, already paid</span><br>' +
    '&nbsp;&nbsp;Security deposit: EUR 100 -- <span style="color:#FCD34D">held, now disputed</span><br><br>' +
    '<span style="text-decoration:underline; color:#6EE7B7">THE DAMAGE:</span><br>' +
    '&nbsp;&nbsp;Gimbal replacement: EUR 55<br>' +
    '&nbsp;&nbsp;Propeller set: EUR 15<br>' +
    '&nbsp;&nbsp;Total repair cost: <span style="color:#FCA5A5; font-weight:700">EUR 70</span><br><br>' +
    '<span style="text-decoration:underline; color:#6EE7B7">THE SPLIT:</span><br>' +
    '&nbsp;&nbsp;Pietro keeps: EUR 70 (covers repairs)<br>' +
    '&nbsp;&nbsp;Sally gets back: EUR 30<br><br>' +
    'Resolution: <span style="color:#FCD34D; font-weight:700">PARTIAL DEPOSIT RELEASE</span></div>',
    14000
  );


  // ============================================================
  // SCENE 32: VISIBLE LOGIN AS PIETRO
  // ============================================================
  console.log('  Scene 32: Login as Pietro (visible)');
  await visibleLogin(page, 'pietro');


  // ============================================================
  // SCENE 33: PIETRO RESOLVES DISPUTE (visible UI form)
  // ============================================================
  console.log('  Scene 33: Pietro resolves dispute via UI');
  await goToDashboardTab(page, 'Incoming Requests');
  await sleep(3000);

  // The resolution form should be visible on the DISPUTED rental card
  // Scroll down so the resolution form is visible to the viewer
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea[x-model="resolutionNotes"]');
    if (textarea) textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(1500);

  // Select resolution type from dropdown
  await page.select('select[x-model="resolutionType"]', 'partial_refund');
  await sleep(1500);

  // Type resolution notes
  const resNotes = 'Partial deposit release. EUR 70 retained for gimbal + propeller repair. EUR 30 returned to renter.';
  await page.click('textarea[x-model="resolutionNotes"]');
  await page.type('textarea[x-model="resolutionNotes"]', resNotes, { delay: 15 });
  await sleep(2000);

  // Click Resolve Dispute
  await clickWithRing(page, 'Resolve Dispute', 'button');
  await sleep(4000); // Wait for toast + reload
  console.log('  Dispute resolved via UI');
  await demoLogout(page);


  // ============================================================
  // SCENE 34: DEPOSIT OUTCOME OVERLAY (8s)
  // ============================================================
  console.log('  Scene 34: Money settlement card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await showOverlay(page,
    'MONEY SETTLEMENT',
    'Follow the money.',
    '<div style="text-align:left; font-size:28px; line-height:1.8">' +
    '<span style="color:#6EE7B7; font-weight:700">PIETRO RECEIVED:</span><br>' +
    '&nbsp;&nbsp;Rental fee: EUR 50 (paid at booking)<br>' +
    '&nbsp;&nbsp;Deposit retained: EUR 70 (repair costs)<br>' +
    '&nbsp;&nbsp;Total: <span style="color:#FCD34D; font-weight:700">EUR 120</span><br><br>' +
    '<span style="color:#F472B6; font-weight:700">SALLY PAID:</span><br>' +
    '&nbsp;&nbsp;Rental fee: EUR 50 (non-refundable)<br>' +
    '&nbsp;&nbsp;Deposit lost: EUR 70 (damage)<br>' +
    '&nbsp;&nbsp;Deposit returned: EUR 30<br>' +
    '&nbsp;&nbsp;Total cost: <span style="color:#FCD34D; font-weight:700">EUR 120</span><br><br>' +
    '<span style="opacity:0.6">The deposit did its job -- protected the owner<br>' +
    'without bankrupting the renter.</span></div>',
    12000
  );


  // ============================================================
  // SCENE 35: SALLY'S FINAL STATUS
  // ============================================================
  console.log('  Scene 35: Sally sees final status');
  await visibleLogin(page, 'sally');
  await goToDashboardTab(page, 'My Rentals');
  await sleep(5000);


  // ================================================================
  // == ACT 2: THE SEED =============================================
  // ================================================================

  // ============================================================
  // SCENE 36: ACT 2 INTRO CARD (12s)
  // ============================================================
  console.log('\n  === ACT 5: THE SEED ===\n');
  console.log('  Scene 36: Act 5 intro card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #2563eb 50%, #1e3a5f 100%)',
    'ACT V \u00BB THE SEED',
    'Every problem is a door.',
    '<div class="extra">The dispute is resolved. The money settled.<br>But something unexpected is about to happen.<br><br><span class="hl" style="font-size:54px">The crash wasn\'t the end. It was the beginning.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 37: PIETRO BROWSES SALLY'S COOKIE ITEMS
  // ============================================================
  console.log('  Scene 37: Pietro browses Sally\'s items');
  // Navigate to BASE first -- demoLogout uses fetch() which needs a server origin (not data: URL)
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle2', timeout: 15000 });
  await demoLogout(page);
  await visibleLogin(page, 'pietro');
  await sleep(2000);

  // Pietro visits Sally's workshop -- he remembers her from the dispute
  await page.goto(`${BASE}/workshop/sallys-kitchen`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  await showOverlay(page,
    'A PEACE OFFERING',
    'Pietro visits Sally\'s workshop.',
    '"Retired pastry chef. 40 years in commercial kitchens."<br><br><span style="color:#FCD34D; font-weight:700">"Those cookie cutters look incredible."</span>',
    10000
  );

  // Scroll through Sally's items
  await smoothScroll(page, 300);
  await sleep(3000);

  // Pietro clicks Favorite on Sally's workshop
  const favClicked = await page.evaluate(() => {
    const btns = [...document.querySelectorAll('button')];
    const fav = btns.find(b => b.textContent.toLowerCase().includes('favorite') || b.querySelector('svg[data-icon="heart"]'));
    if (fav) { fav.click(); return true; }
    // Try heart icon SVG
    const hearts = document.querySelectorAll('svg');
    for (const h of hearts) {
      if (h.innerHTML.includes('M4.318') || h.innerHTML.includes('heart')) {
        h.closest('button')?.click();
        return true;
      }
    }
    return false;
  });
  if (favClicked) {
    console.log('  Pietro favorited Sally\'s workshop');
    await sleep(2000);
  } else {
    // API fallback: favorite via API
    const sallyUser = await apiCall(page, 'GET', '/api/v1/users?q=sally');
    if (sallyUser.data && sallyUser.data.length > 0) {
      await apiCall(page, 'POST', `/api/v1/favorites`, { target_user_id: sallyUser.data[0].id });
      console.log('  Pietro favorited Sally (API)');
      await showToast(page, 'Added to favorites!');
    }
    await sleep(2000);
  }

  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 38: PIETRO CLICKS ON COOKIE CUTTER SET
  // ============================================================
  console.log('  Scene 38: Pietro views cookie cutter listing');
  await page.goto(`${BASE}/items/professional-cookie-cutter-set-200-pieces`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Scroll to see the listing details
  await smoothScroll(page, 200);
  await sleep(3000);

  // Pietro clicks "Rent This Item" (visible click, then fill form)
  await clickWithRing(page, 'Rent This Item', 'a, button');
  await sleep(2000);

  // Scroll down to the rental request form so the viewer sees it
  await page.evaluate(() => {
    const form = document.querySelector('form[x-data], [x-data*="rental"], textarea[name="message"], input[type="date"]');
    if (form) form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(1500);

  // Fill in dates visually (tomorrow to next week)
  const cookieStart = new Date(); cookieStart.setDate(cookieStart.getDate() + 1);
  const cookieEnd = new Date(); cookieEnd.setDate(cookieEnd.getDate() + 7);
  const cookieStartStr = cookieStart.toISOString().split('T')[0];
  const cookieEndStr = cookieEnd.toISOString().split('T')[0];

  // Try to fill the date inputs visually
  const dateInputs = await page.$$('input[type="date"]');
  if (dateInputs.length >= 2) {
    await dateInputs[0].click();
    await page.evaluate((el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles:true})); }, dateInputs[0], cookieStartStr);
    await sleep(800);
    await dateInputs[1].click();
    await page.evaluate((el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles:true})); }, dateInputs[1], cookieEndStr);
    await sleep(800);
  }

  // Type the message visually so the viewer reads along
  const msgArea = await page.$('textarea[name="message"], textarea');
  const pieceMsg = 'Hi Sally! I know we had a rough start with the drone, but I saw your cookie cutter collection and I have to try them. My niece Sofia\'s birthday is next week -- 200 shapes to choose from? She\'ll love it. Consider this a peace offering. -- Pietro';
  if (msgArea) {
    await msgArea.click();
    await msgArea.type(pieceMsg, { delay: 12 });
    await sleep(2000);
  }

  // Submit via visible button click or API fallback
  const submitClicked = await clickWithRing(page, 'Send Request', 'button').catch(() => false);
  await sleep(2000);

  // API fallback: create the rental if form submit didn't work
  const cookieItems = await apiCall(page, 'GET', '/api/v1/items?q=cookie+cutter');
  let cookieListingId = null;
  if (cookieItems.data && cookieItems.data.length > 0) {
    const cookieItem = cookieItems.data[0];
    console.log(`  Cookie item: ${cookieItem.name} (${cookieItem.id})`);
    const cookieListings = await apiCall(page, 'GET', `/api/v1/listings?item_id=${cookieItem.id}`);
    if (cookieListings.data) {
      const rentListing = cookieListings.data.find(l => l.listing_type === 'rent' || l.listing_type === 'RENT');
      if (rentListing) cookieListingId = rentListing.id;
    }
  }
  console.log(`  Cookie cutter listing ID: ${cookieListingId}`);

  if (cookieListingId) {
    const rentalResp = await apiCall(page, 'POST', '/api/v1/rentals', {
      listing_id: cookieListingId,
      start_date: cookieStartStr,
      end_date: cookieEndStr,
      message: pieceMsg,
    });
    console.log(`  Cookie rental created: ${rentalResp.status} ${rentalResp.data?.id || ''}`);
    await showToast(page, 'Rental: EUR 35 (7 days) + Deposit: EUR 20 = EUR 55 total');
  }
  await sleep(3000);


  // ============================================================
  // SCENE 39: THE COOKIE ORDER OVERLAY (14s)
  // ============================================================
  console.log('  Scene 39: The Cookie Cutter Order card');
  await showOverlay(page,
    'THE COOKIE CUTTER ORDER',
    'Pietro rents Sally\'s cookie cutters.',
    '<div style="text-align:left; font-size:38px; line-height:1.6">' +
    '<span style="text-decoration:underline; color:#6EE7B7">INVOICE:</span> ' +
    'Rental EUR 35 + Deposit EUR 20 = <span style="color:#FCD34D; font-weight:700">EUR 55</span><br><br>' +
    '<span style="color:#60A5FA">Pietro:</span> "Your collection is amazing. My niece Sofia\'s birthday is next week."<br><br>' +
    '<span style="color:#F472B6">Sally:</span> "Wait -- you\'re the drone guy?"<br><br>' +
    '<span style="color:#60A5FA">Pietro:</span> "Yeah... no hard feelings. Fixed it myself."<br><br>' +
    '<span style="color:#F472B6">Sally:</span> "Let me throw in extra shapes for Sofia."</div>',
    16000
  );
  await demoLogout(page);


  // ============================================================
  // SCENE 40: SALLY SEES PIETRO'S REQUEST + NOTIFICATION BELL
  // ============================================================
  console.log('  Scene 40: Sally sees the request');
  await visibleLogin(page, 'sally');
  await sleep(2000);

  // Click notification bell
  const bell40 = await page.evaluate(() => {
    const paths = document.querySelectorAll('svg path');
    for (const p of paths) {
      if (p.getAttribute('d') && p.getAttribute('d').includes('M15 17h5l-1.405')) {
        const btn = p.closest('button');
        if (btn) { btn.click(); return true; }
      }
    }
    return false;
  });
  if (bell40) {
    console.log('  Bell clicked -- notification panel open');
    await sleep(4000);
  }

  // Go to dashboard to see the incoming request
  await goToDashboardTab(page, 'Incoming Requests');
  await sleep(4000);

  await showOverlay(page,
    'SURPRISE',
    'Sally sees a new rental request... from Pietro.',
    '"Hi Sally! I know we had a rough start with the drone,<br>but I saw your cookie cutter collection..."<br><br><span style="color:#6EE7B7; font-weight:700">She smiles. She hits Approve.</span>',
    10000
  );


  // ============================================================
  // SCENE 41: SALLY APPROVES PIETRO'S RENTAL
  // ============================================================
  console.log('  Scene 41: Sally approves Pietro\'s cookie rental');
  // Find and approve the cookie rental
  const sallyRentals = await apiCall(page, 'GET', '/api/v1/rentals?role=owner');
  let cookieRentalId = null;
  if (sallyRentals.data) {
    const pending = sallyRentals.data.find(r => r.status === 'pending' || r.status === 'PENDING');
    if (pending) cookieRentalId = pending.id;
  }
  console.log(`  Cookie rental ID: ${cookieRentalId}`);

  if (cookieRentalId) {
    // Try to click the Approve button visually first
    await clickWithRing(page, 'Approve', 'button');
    await sleep(4000);

    // Verify via API if needed
    const checkRental = await apiCall(page, 'GET', `/api/v1/rentals/${cookieRentalId}`);
    if (checkRental.data?.status !== 'approved' && checkRental.data?.status !== 'APPROVED') {
      await apiCall(page, 'PATCH', `/api/v1/rentals/${cookieRentalId}/status`, { status: 'approved' });
      await showToast(page, 'Rental approved!');
    }
  }
  await sleep(3000);

  await showOverlay(page,
    'FULL CIRCLE',
    'Two weeks ago, a crashed drone. Today, cookie cutters.',
    '<div style="text-align:left; font-size:38px; line-height:1.6">' +
    '<span style="color:#F472B6">Sally:</span> "I threw in some cherry cookie cutters<br>' +
    '&nbsp;&nbsp;as a freebie. For Sofia."<br><br>' +
    '<span style="color:#60A5FA">Pietro:</span> "That\'s so kind. You know...<br>' +
    '&nbsp;&nbsp;I love your cookies."<br><br>' +
    '<span style="color:#F472B6">Sally:</span> "And I love your drones.<br>' +
    '&nbsp;&nbsp;We should work together."</div>',
    14000
  );
  await demoLogout(page);


  // ================================================================
  // == EPILOGUE ===================================================
  // ================================================================
  console.log('\n  === EPILOGUE ===\n');

  // ============================================================
  // SCENE 42: THE LIGHTBULB (12s)
  // ============================================================
  console.log('  Scene 42: The Lightbulb card');
  await page.goto(card(
    'linear-gradient(135deg, #92400e 0%, #d97706 50%, #92400e 100%)',
    'EPILOGUE \u00BB THE LIGHTBULB',
    'Sally bakes. But she can\'t deliver.',
    '<div class="extra" style="text-align:left; font-size:42px; line-height:1.6">' +
    'Sally bakes the best cookies in Trapani.<br>' +
    'But she can\'t deliver -- wheelchair, no bicycle.<br>' +
    'UPS costs a fortune. Johnny Abela\'s bike is always broken.<br><br>' +
    'Pietro has a licensed drone. He needs steady work.<br><br>' +
    '<span class="hl" style="font-size:50px">What if the drone guy... delivered the cookies?</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 43: THE PARTNERSHIP (12s)
  // ============================================================
  console.log('  Scene 43: The Partnership card');
  await page.goto(card(
    'linear-gradient(135deg, #065f46 0%, #059669 50%, #065f46 100%)',
    'THE PARTNERSHIP',
    'Sally bakes. Pietro flies. Together, they deliver.',
    '<div class="extra" style="text-align:left; font-size:38px; line-height:1.6">' +
    '<span style="color:#60A5FA">Pietro:</span> "I\'ll do the first delivery free."<br><br>' +
    '<span style="color:#F472B6">Sally:</span> "I have 3 regular customers. Every week.<br>' +
    '&nbsp;&nbsp;You could be my logistics guy."<br><br>' +
    '<span style="color:#60A5FA">Pietro:</span> "I was thinking the same thing."<br><br>' +
    '<span style="color:#FCD34D; font-size:44px; font-weight:700">A crashed drone brought them together.<br>' +
    'BorrowHood planted a seed.</span></div>'
  ));
  await sleep(16000);


  // ============================================================
  // SCENE 44: TO BE CONTINUED (GREEN -- 14s)
  // ============================================================
  console.log('  Scene 44: To Be Continued');
  // Custom card -- end on THE QUESTION, not a checklist
  await page.goto(`data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html><html><head><style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0f172a; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100vh; width: 100vw;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: white; text-align: center; padding: 40px 80px;
  }
  .setup { font-size: 42px; line-height: 1.6; opacity: 0.7; max-width: 1000px; margin-bottom: 40px; }
  .name { color: #60A5FA; font-weight: 700; }
  .question {
    font-size: 72px; font-weight: 900; color: #FCD34D;
    text-shadow: 0 0 40px rgba(252,211,77,0.3);
    max-width: 1100px; line-height: 1.3; margin-bottom: 50px;
  }
  .continued {
    font-size: 36px; font-weight: 300; opacity: 0.4;
    letter-spacing: 12px; text-transform: uppercase;
  }
  .credit { font-size: 18px; opacity: 0.25; margin-top: 20px; }
</style></head><body>
  <div class="setup">
    <span class="name">Sally</span> bakes the best cookies in Trapani.<br>
    <span class="name">Sofia</span> just got 200 cookie cutters for her birthday.<br>
    <span class="name">Johnny Abela's</span> bike is broken.<br>
    <span class="name">Pietro</span> has a licensed drone.
  </div>
  <div class="question">What if the drone guy... delivered the cookies?</div>
  <div class="continued">to be continued</div>
  <div class="credit">Notion Motion Pictures &raquo; Built with Claude Code (Opus 4.6)</div>
</body></html>`)}`);
  await sleep(16000);


  // ============================================================
  // DONE
  // ============================================================
  await waitForEnter('Recording complete. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done. Check OBS for raw footage.\n');

})().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
