#!/usr/bin/env node
/**
 * THE COOKIE RUN -- Recording Script (S1 EP02)
 *
 * Picks up right where EP01 "The Crash" left off:
 *   "What if the drone guy... delivered the cookies?"
 *
 * Every click visible. Every login visible. Every status change on screen.
 * Syd Field 5-act structure + epilogue. Know the ending before you write.
 *
 * THE ENDING: Johnny watches the drone deliver cookies. He's left behind.
 *   Sally sees his face. She has the money. He needs wheels.
 *   THE QUESTION: What if the cookie queen... bought the delivery kid his wheels?
 *
 * ACT 1 -- THE APPRENTICE (Scenes 1-10):
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- "THE COOKIE RUN"
 *   3.  "Previously on BorrowHood" recap card
 *   4.  Sofia character overlay on homepage
 *   5.  Sally character overlay
 *   6.  Demo login as Sally -- visit Sofia's workshop (Sofia's Bakes)
 *   7.  Sally views mentorship -- she's Sofia's baking mentor
 *   8.  Demo login as Sofia -- Sofia's dashboard (newcomer, first time)
 *   9.  Sofia visits Sally's workshop -- sees cookie cutters + KitchenAid
 *  10.  Card: THE FIRST BAKE (Sally teaches, Sofia learns)
 *
 * ACT 2 -- THE ORDER (Scenes 11-17):
 *  11.  Card: SOFIA'S BIRTHDAY (she wants to send cookie boxes)
 *  12.  Sofia creates a commission listing -- "Sofia's Birthday Cookie Box"
 *  13.  Sofia's dashboard -- sees her first listing live
 *  14.  Demo login as Pietro -- Pietro sees Sofia's listing
 *  15.  Pietro orders a cookie box (rental request / commission)
 *  16.  Sofia gets notification -- her first order ever
 *  17.  Card: 5 BOXES, 5 ADDRESSES (the delivery problem)
 *
 * ACT 3 -- THE PROBLEM (Scenes 18-23):
 *  18.  Card: MEET JOHNNY ABELA (broken bike, delivery dream)
 *  19.  Johnny character overlay
 *  20.  Demo login as Johnny -- Johnny's workshop (Johnny's Runs)
 *  21.  Johnny's broken bike listing -- "Needs Repair"
 *  22.  Johnny's delivery service listing -- EUR 5/delivery
 *  23.  Card: THE CHAIN SNAPS (bike can't make it)
 *
 * ACT 4 -- THE FLIGHT (Scenes 24-31):
 *  24.  Card: PIETRO'S IDEA ("I have a drone")
 *  25.  Demo login as Pietro -- Pietro's drone fleet
 *  26.  Sofia rents Pietro's drone service (the callback to EP01)
 *  27.  Card: FIRST DELIVERY (cookie box strapped to Mini 4 Pro)
 *  28.  Pietro's dashboard -- delivery in progress
 *  29.  Card: IT WORKS (drone delivers, crowd watches)
 *  30.  Sofia's dashboard -- orders fulfilled, reviews coming in
 *  31.  Card: 5 FOR 5 (all deliveries complete)
 *
 * ACT 5 -- THE GAP (Scenes 32-36):
 *  32.  Card: JOHNNY WATCHES (he was supposed to be the delivery kid)
 *  33.  Demo login as Sally -- Sally's dashboard, cookie sales EUR 235
 *  34.  Sally visits Johnny's workshop -- sees the broken bike
 *  35.  Card: THE MATH (scooter = EUR 200, Sally has EUR 235)
 *  36.  Sally visits Johnny's delivery service listing
 *
 * EPILOGUE (Scenes 37-39):
 *  37.  Card: THE DOOR (every problem opens one)
 *  38.  Card: THE QUESTION (gold text)
 *  39.  GREEN "TO BE CONTINUED" card
 *
 * Usage: node record-the-cookie-run.js [base_url]
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
async function visibleLogin(page, username) {
  await page.goto('about:blank');
  await sleep(300);
  await page.goto(`${BASE}/demo-login`, { waitUntil: 'networkidle2', timeout: 15000 });
  await page.evaluate(() => { document.body.style.zoom = '1'; });
  await sleep(3000);

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
    await page.mouse.click(clickPos.x, clickPos.y);
    console.log(`  Clicked @${username} card`);
  } else {
    console.log(`  WARN: Could not find @${username} button, using API fallback`);
    await demoLogin(page, username);
    await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
    return;
  }

  try {
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
  } catch (e) { /* already navigated */ }
  await sleep(1000);

  const isLoggedIn = await page.evaluate(() => {
    const nav = document.querySelector('nav') || document.querySelector('header');
    return nav ? !nav.textContent.includes('Log In') : false;
  });
  if (!isLoggedIn) {
    console.log(`  WARN: Login may have failed, trying API fallback`);
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

// -- DOM overlay --
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
      background: rgba(30,41,59,1.0); color: white;
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

  const halfDuration = Math.floor(duration / 2);
  await sleep(halfDuration);

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
  console.log(`\n  THE COOKIE RUN -- Recording Script (S1 EP02)`);
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
    '<div class="extra">THE COOKIE RUN | BorrowHood S1 EP02</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');


  // ============================================================
  // SCENE 2: INTRO CARD (10s)
  // ============================================================
  console.log('  Scene 2: Intro card');
  await page.goto(card(
    'linear-gradient(135deg, #7c2d12 0%, #9a3412 40%, #c2410c 100%)',
    'THE COOKIE RUN',
    'Baking, Drones & Broken Bikes',
    '<div class="badge">SEASON 1 &raquo; EPISODE 2</div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 3: PREVIOUSLY ON BORROWHOOD (12s)
  // ============================================================
  console.log('  Scene 3: Previously on BorrowHood');
  await page.goto(card(
    '#0f172a',
    'PREVIOUSLY ON<br>BORROWHOOD',
    '',
    '<div class="extra" style="text-align:left; font-size:36px; line-height:2">' +
    '<span class="hl">Sally</span> rented <span class="hl">Pietro\'s</span> drone. It crashed.<br>' +
    'Dispute filed. Deposit split. <span class="green">EUR 70/30.</span><br>' +
    'Then Pietro rented Sally\'s cookie cutters. For his niece <span class="hl">Sofia</span>.<br><br>' +
    'The question was:<br>' +
    '<span style="color:#FCD34D; font-size:44px; font-weight:700">' +
    '"What if the drone guy... delivered the cookies?"</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 4: SOFIA FERRETTI (character overlay, 8s)
  // ============================================================
  console.log('  Scene 4: Sofia character card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  await showOverlay(page,
    'SOFIA FERRETTI',
    'Pietro\'s niece. 17 years old. Newcomer.',
    'She got 200 cookie cutters for her birthday.<br>' +
    'She wants to learn to bake.<br>' +
    'Sally is her mentor.',
    10000
  );


  // ============================================================
  // SCENE 5: SALLY THOMPSON (character overlay, 8s)
  // ============================================================
  console.log('  Scene 5: Sally character card');
  await showOverlay(page,
    'SALLY THOMPSON',
    'Cookie queen. Trusted member. Mentor.',
    'She has a KitchenAid, 200 cookie cutters, and recipes<br>' +
    'handed down from her grandmother.<br>' +
    'Today she teaches Sofia.',
    8000
  );


  // ============================================================
  // SCENE 6: LOGIN AS SALLY -- VISIT SOFIA'S WORKSHOP
  // ============================================================
  console.log('  Scene 6: Login as Sally');
  await visibleLogin(page, 'sally');

  console.log('  Scene 6b: Sally visits Sofia\'s workshop');
  await page.goto(`${BASE}/workshop/sofias-bakes`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll through Sofia's profile
  console.log('  Scene 6c: Scroll Sofia\'s profile');
  await smoothScroll(page, 400);
  await sleep(4000);


  // ============================================================
  // SCENE 7: MENTORSHIP OVERLAY (10s)
  // ============================================================
  console.log('  Scene 7: Mentorship explainer');
  await showOverlay(page,
    'THE MENTORSHIP',
    'Sally teaches. Sofia learns.',
    '<div style="text-align:left; font-size:32px; line-height:2">' +
    '<span class="hl">Mentor:</span> Sally Thompson (Baking)<br>' +
    '<span class="hl">Apprentice:</span> Sofia Ferretti<br>' +
    '<span class="hl">Status:</span> <span class="green">Active</span><br>' +
    '<span class="hl">Type:</span> Apprenticeship (long-term skill building)<br><br>' +
    '<span class="dim">The platform tracks who teaches whom.</span><br>' +
    '<span class="dim">Mentors earn reputation. Apprentices earn skills.</span></div>',
    12000
  );


  // ============================================================
  // SCENE 8: LOGIN AS SOFIA -- HER DASHBOARD (first time)
  // ============================================================
  console.log('  Scene 8: Login as Sofia');
  await visibleLogin(page, 'sofiaferretti');

  console.log('  Scene 8b: Sofia\'s dashboard');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Show My Items tab -- she has 1 item (Birthday Cookie Box)
  await clickWithRing(page, 'My Items', '[role="tab"], button, a');
  await sleep(4000);


  // ============================================================
  // SCENE 9: SOFIA VISITS SALLY'S WORKSHOP
  // ============================================================
  console.log('  Scene 9: Sofia visits Sally\'s workshop');
  await page.goto(`${BASE}/workshop/sallys-kitchen`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll to items -- cookie cutters + KitchenAid
  console.log('  Scene 9b: Sally\'s items');
  await smoothScroll(page, 500);
  await sleep(5000);


  // ============================================================
  // SCENE 10: THE FIRST BAKE (overlay, 12s)
  // ============================================================
  console.log('  Scene 10: The First Bake card');
  await showOverlay(page,
    'ACT I \u00BB THE FIRST BAKE',
    'Sally\'s Kitchen. Saturday morning.',
    '<div style="text-align:left; font-size:32px; line-height:1.8">' +
    'Sofia arrives at 8am with her cookie cutters.<br>' +
    'Sally has the KitchenAid running. Almond flour, vanilla, powdered sugar.<br><br>' +
    'First batch: 6 burned. 4 perfect.<br>' +
    '<span class="hl">"That\'s how it works,"</span> Sally says.<br>' +
    '<span class="hl">"You learn from the ones that burn."</span></div>',
    14000
  );


  // ============================================================
  // SCENE 11: SOFIA'S BIRTHDAY (overlay, 10s)
  // ============================================================
  console.log('\n  === ACT 2: THE ORDER ===\n');
  console.log('  Scene 11: Sofia\'s Birthday card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3b82f6 100%)',
    'ACT II \u00BB THE ORDER',
    'Sofia\'s birthday is next week.',
    '<div class="extra">She wants to send cookie boxes to 5 friends.<br>' +
    'Her first real order. Her first commission listing.</div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 12: SOFIA CREATES A COMMISSION LISTING
  // ============================================================
  console.log('  Scene 12: Sofia creates commission listing');
  // Sofia is already logged in from Scene 8
  // Navigate to her items -- the Birthday Cookie Box already exists in seed data
  await page.goto(`${BASE}/items/sofias-birthday-cookie-box`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll through the listing details
  await smoothScroll(page, 400);
  await sleep(4000);


  // ============================================================
  // SCENE 13: SOFIA'S DASHBOARD -- HER FIRST LISTING
  // ============================================================
  console.log('  Scene 13: Sofia\'s dashboard -- listing live');
  await goToDashboardTab(page, 'My Items');
  await sleep(4000);

  await showOverlay(page,
    'HER FIRST LISTING',
    'Sofia Ferretti. Newcomer. Age 17.',
    '<span class="hl">1 item listed.</span> Sofia\'s Birthday Cookie Box (Custom Order).<br>' +
    'Badge: Newcomer. Points: 10.<br><br>' +
    '<span class="dim">Everyone starts somewhere.</span>',
    10000
  );


  // ============================================================
  // SCENE 14: PIETRO SEES SOFIA'S LISTING
  // ============================================================
  console.log('  Scene 14: Login as Pietro');
  await visibleLogin(page, 'pietro');

  console.log('  Scene 14b: Pietro visits Sofia\'s workshop');
  await page.goto(`${BASE}/workshop/sofias-bakes`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Scroll to items
  await smoothScroll(page, 400);
  await sleep(3000);

  // Click on Birthday Cookie Box
  console.log('  Scene 14c: Pietro views cookie box listing');
  await page.goto(`${BASE}/items/sofias-birthday-cookie-box`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);


  // ============================================================
  // SCENE 15: PIETRO ORDERS A COOKIE BOX
  // ============================================================
  console.log('  Scene 15: Pietro orders cookie box');

  // Calculate dates
  const startDate = new Date(Date.now() + 5 * 86400000);
  const endDate = new Date(Date.now() + 6 * 86400000);
  const startStr = startDate.toISOString().split('T')[0];
  const endStr = endDate.toISOString().split('T')[0];

  // Try to rent via UI
  const hasRentBtn = await clickWithRing(page, 'Buy This', 'button, a') || await clickWithRing(page, 'Rent This', 'button, a');
  if (hasRentBtn) {
    await sleep(1500);

    // Fill dates (only visible for rental/service types, hidden for sell/offer)
    await page.evaluate((s, e) => {
      const dateInputs = document.querySelectorAll('input[type="date"]');
      if (dateInputs[0]) { dateInputs[0].value = s; dateInputs[0].dispatchEvent(new Event('input', {bubbles:true})); }
      if (dateInputs[1]) { dateInputs[1].value = e; dateInputs[1].dispatchEvent(new Event('input', {bubbles:true})); }
      // Alpine v3: use Alpine.$data() to set form values
      const listingEl = document.querySelector('[x-data*="listingId"]');
      if (listingEl) {
        const data = window.Alpine?.$data(listingEl) ||
                     (listingEl._x_dataStack && listingEl._x_dataStack[0]);
        if (data) {
          data.rentalForm.start = s;
          data.rentalForm.end = e;
        }
      }
    }, startStr, endStr);
    await sleep(1000);

    // Type message
    const textarea = await page.$('textarea');
    if (textarea) {
      await typeSlowly(page, 'textarea',
        'For Sofia\'s birthday! Her uncle Pietro here. She\'ll love these.', 30);
      await page.evaluate(() => {
        const ta = document.querySelector('textarea');
        const listingEl = document.querySelector('[x-data*="listingId"]');
        if (ta && listingEl) {
          const data = window.Alpine?.$data(listingEl) ||
                       (listingEl._x_dataStack && listingEl._x_dataStack[0]);
          if (data) {
            data.rentalForm.message = ta.value;
          }
        }
      });
      await sleep(1000);
    }

    // Click Send Request -- find the submit button INSIDE the modal overlay
    const submitted = await page.evaluate(() => {
      // The modal is in a div with class "fixed inset-0"
      const modal = document.querySelector('.fixed.inset-0');
      if (!modal) return null;
      const btns = modal.querySelectorAll('button');
      for (const btn of btns) {
        const txt = btn.textContent.trim();
        if (txt.includes('Send') || txt.includes('Request') || txt.includes('Purchase')) {
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

  // Check if rental was created
  let cookieRentalId = null;
  const myRentals = await apiCall(page, 'GET', '/api/v1/rentals?role=renter&status=pending');
  if (myRentals.data && myRentals.data.length > 0) {
    cookieRentalId = myRentals.data[0].id;
    console.log(`  Cookie box rental created: ${cookieRentalId}`);
  }

  // API fallback
  if (!cookieRentalId) {
    console.log('  UI form failed -- creating rental via API fallback');
    // Find the listing ID for Sofia's cookie box
    const itemResp = await apiCall(page, 'GET', '/api/v1/items?search=Sofia%20Birthday%20Cookie');
    const cookieItem = itemResp.data?.find(i => i.slug?.includes('birthday-cookie'));
    if (cookieItem) {
      const listingsResp = await apiCall(page, 'GET', `/api/v1/listings?item_id=${cookieItem.id}`);
      const listing = listingsResp.data?.[0];
      if (listing) {
        const rentalResp = await apiCall(page, 'POST', '/api/v1/rentals', {
          listing_id: listing.id,
          requested_start: startDate.toISOString(),
          requested_end: endDate.toISOString(),
          renter_message: 'For Sofia\'s birthday! Her uncle Pietro here.',
        });
        if (rentalResp.data?.id) {
          cookieRentalId = rentalResp.data.id;
          await showToast(page, 'Order sent to Sofia!');
        }
      }
    }
    console.log(`  API fallback rental: ${cookieRentalId}`);
  }

  if (!cookieRentalId) {
    console.error('\n  FATAL: Cookie box rental creation failed.');
    await page.goto(card('#DC2626', 'SCRIPT ERROR', 'Cookie rental failed',
      '<div class="extra">Could not create rental. Check console.</div>'));
    await waitForEnter('Fix and restart. ENTER to close');
    await browser.close();
    process.exit(1);
  }
  await sleep(2000);


  // ============================================================
  // SCENE 16: SOFIA GETS NOTIFICATION
  // ============================================================
  console.log('  Scene 16: Sofia sees notification');
  await visibleLogin(page, 'sofiaferretti');

  // Check notification bell
  console.log('  Scene 16b: Sofia checks bell');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Try clicking the bell
  const bellPos = await page.evaluate(() => {
    const bell = document.querySelector('[x-data*="notification"], .notification-bell, [aria-label*="notification"]') ||
                 document.querySelector('nav button svg, nav a svg')?.closest('button, a');
    if (bell) {
      const box = bell.getBoundingClientRect();
      return box.width > 0 ? { x: box.x + box.width / 2, y: box.y + box.height / 2 } : null;
    }
    return null;
  });
  if (bellPos) {
    await showRing(page, bellPos.x, bellPos.y);
    await page.mouse.click(bellPos.x, bellPos.y);
    await sleep(3000);
  }

  // Go to Incoming Requests
  await clickWithRing(page, 'Incoming', '[role="tab"], button, a');
  await sleep(4000);

  await showOverlay(page,
    'FIRST ORDER!',
    'Uncle Pietro wants a birthday cookie box.',
    '<span class="hl">EUR 15</span> commission. Her very first sale.<br>' +
    'The notification bell rang. Sofia\'s heart raced.',
    8000
  );


  // ============================================================
  // SCENE 17: 5 BOXES CARD (10s)
  // ============================================================
  console.log('  Scene 17: 5 Boxes card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    '5 BOXES',
    '5 addresses across Trapani',
    '<div class="extra">Pietro. Two neighbors. A teacher. Her best friend.<br>' +
    'All want Sofia\'s birthday cookies.<br><br>' +
    'One problem: <span class="red">how do you deliver them?</span></div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 18: MEET JOHNNY (overlay intro card)
  // ============================================================
  console.log('\n  === ACT 3: THE PROBLEM ===\n');
  console.log('  Scene 18: Meet Johnny card');
  await page.goto(card(
    'linear-gradient(135deg, #422006 0%, #78350f 40%, #a16207 100%)',
    'ACT III \u00BB THE PROBLEM',
    'Enter Johnny Abela.',
    '<div class="extra">The delivery kid with the broken bike.<br>' +
    'He knows every street in Trapani.<br>' +
    'But his chain snapped. Again.</div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 19: JOHNNY CHARACTER OVERLAY (8s)
  // ============================================================
  console.log('  Scene 19: Johnny character card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  await showOverlay(page,
    'JOHNNY ABELA',
    'Age 25. Maltese-Sicilian. Newcomer.',
    'Cleaner by day. Delivery kid by bike (when it works).<br>' +
    'Knows every shortcut, every doorbell that doesn\'t work.<br><br>' +
    'Dream: an electric scooter and a proper delivery service.',
    10000
  );


  // ============================================================
  // SCENE 20: LOGIN AS JOHNNY -- HIS WORKSHOP
  // ============================================================
  console.log('  Scene 20: Login as Johnny');
  await visibleLogin(page, 'john');

  console.log('  Scene 20b: Johnny\'s workshop');
  await page.goto(`${BASE}/workshop/johns-cleaning`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll through skills and items
  await smoothScroll(page, 500);
  await sleep(4000);


  // ============================================================
  // SCENE 21: JOHNNY'S BROKEN BIKE LISTING
  // ============================================================
  console.log('  Scene 21: Broken bike listing');
  await page.goto(`${BASE}/items/johnnys-delivery-bike-broken`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll to read the description
  await smoothScroll(page, 300);
  await sleep(4000);


  // ============================================================
  // SCENE 22: JOHNNY'S DELIVERY SERVICE LISTING
  // ============================================================
  console.log('  Scene 22: Delivery service listing');
  await page.goto(`${BASE}/items/johnny-local-delivery-trapani`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 23: THE CHAIN SNAPS (overlay, 10s)
  // ============================================================
  console.log('  Scene 23: Chain snaps card');
  await showOverlay(page,
    'THE CHAIN SNAPS',
    'Johnny loads the first cookie box. Rides 200 meters.',
    '<span class="red">Chain breaks. Cookies on the ground.</span><br><br>' +
    'The bike is done. The frame is bent.<br>' +
    'Johnny needs help. But he can\'t afford a repair.<br><br>' +
    '<span class="dim">5 boxes. 5 addresses. No wheels.</span>',
    12000
  );


  // ============================================================
  // SCENE 24: PIETRO'S IDEA (card, 10s)
  // ============================================================
  console.log('\n  === ACT 4: THE FLIGHT ===\n');
  console.log('  Scene 24: Pietro\'s idea card');
  await page.goto(card(
    'linear-gradient(135deg, #0c4a6e 0%, #0369a1 40%, #0ea5e9 100%)',
    'ACT IV \u00BB THE FLIGHT',
    '"I have a drone."',
    '<div class="extra"><span class="hl">Pietro Ferretti</span> remembers The Crash.<br>' +
    'The DJI Mini 4 Pro. Under 249g. Perfect for a cookie box.<br><br>' +
    'The idea from Episode 1 becomes real.</div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 25: LOGIN AS PIETRO -- DRONE FLEET
  // ============================================================
  console.log('  Scene 25: Login as Pietro');
  await visibleLogin(page, 'pietro');

  console.log('  Scene 25b: Pietro\'s workshop -- drone fleet');
  await page.goto(`${BASE}/workshop/pietros-drones`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Scroll to drones
  await smoothScroll(page, 500);
  await sleep(5000);


  // ============================================================
  // SCENE 26: SOFIA RENTS PIETRO'S DRONE SERVICE
  // ============================================================
  console.log('  Scene 26: Drone service rental overlay');
  await showOverlay(page,
    'THE DEAL',
    'Sofia rents Pietro\'s aerial delivery service.',
    '<div style="text-align:left; font-size:32px; line-height:2">' +
    '<span class="green">SERVICE:</span> Aerial Photography & Video<br>' +
    '<span class="green">PILOT:</span> Pietro Ferretti (licensed, EU A1/A3)<br>' +
    '<span class="green">DRONE:</span> DJI Mini 4 Pro<br>' +
    '<span class="green">MISSION:</span> 5 cookie box deliveries across Trapani centro<br>' +
    '<span class="green">PRICE:</span> <span class="hl">EUR 25</span> (family discount)<br><br>' +
    '<span class="dim">Uncle delivers for his niece. That\'s how neighborhoods work.</span></div>',
    14000
  );


  // ============================================================
  // SCENE 27: FIRST DELIVERY (card, 10s)
  // ============================================================
  console.log('  Scene 27: First delivery card');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #047857 40%, #10b981 100%)',
    'FIRST DELIVERY',
    'Cookie box strapped to the Mini 4 Pro.',
    '<div class="extra">Sofia watches from her phone.<br>' +
    'Pietro flies. 400 meters. Steady. Landing on the balcony.<br>' +
    'Customer films it. Posts it on Instagram.</div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 28: PIETRO'S DASHBOARD -- DELIVERY IN PROGRESS
  // ============================================================
  console.log('  Scene 28: Pietro\'s dashboard');
  // Pietro is still logged in
  await goToDashboardTab(page, 'My Orders');
  await sleep(4000);

  // Show incoming requests too
  await clickWithRing(page, 'Incoming', '[role="tab"], button, a');
  await sleep(4000);


  // ============================================================
  // SCENE 29: IT WORKS (overlay, 10s)
  // ============================================================
  console.log('  Scene 29: It works card');
  await showOverlay(page,
    'IT WORKS',
    '5 deliveries. 5 happy customers.',
    'Delivery 1: Via Roma -- <span class="green">delivered</span><br>' +
    'Delivery 2: Via Garibaldi -- <span class="green">delivered</span><br>' +
    'Delivery 3: Via Torrearsa -- <span class="green">delivered</span><br>' +
    'Delivery 4: Piazza Mercato -- <span class="green">delivered</span><br>' +
    'Delivery 5: Via Fardella -- <span class="green">delivered</span><br><br>' +
    '<span class="hl">People on the street pointed at the sky.</span>',
    12000
  );


  // ============================================================
  // SCENE 30: SOFIA'S DASHBOARD -- ORDERS FULFILLED
  // ============================================================
  console.log('  Scene 30: Sofia\'s dashboard');
  await visibleLogin(page, 'sofiaferretti');
  await goToDashboardTab(page, 'My Items');
  await sleep(4000);

  // Show incoming requests
  await clickWithRing(page, 'Incoming', '[role="tab"], button, a');
  await sleep(4000);


  // ============================================================
  // SCENE 31: 5 FOR 5 (overlay, 10s)
  // ============================================================
  console.log('  Scene 31: 5 for 5 card');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #065f46 40%, #047857 100%)',
    '5 FOR 5',
    'All deliveries complete.',
    '<div class="extra" style="text-align:left; font-size:32px; line-height:2">' +
    '<span class="check">&#10003;</span> 5 cookie boxes baked by Sofia<br>' +
    '<span class="check">&#10003;</span> 5 deliveries by drone (Pietro)<br>' +
    '<span class="check">&#10003;</span> 5 happy customers<br>' +
    '<span class="check">&#10003;</span> 2 five-star reviews already<br><br>' +
    'Revenue: <span class="hl">EUR 75</span> (5 x EUR 15)<br>' +
    'Drone cost: <span class="red">EUR 25</span><br>' +
    'Sofia\'s profit: <span class="green">EUR 50</span><br><br>' +
    '<span class="dim">Not bad for a 17-year-old\'s first week.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 32: JOHNNY WATCHES (card, 12s)
  // ============================================================
  console.log('\n  === ACT 5: THE GAP ===\n');
  console.log('  Scene 32: Johnny watches card');
  await page.goto(card(
    'linear-gradient(135deg, #1c1917 0%, #292524 40%, #44403c 100%)',
    'ACT V \u00BB THE GAP',
    'Johnny watches the drone land.',
    '<div class="extra">He was supposed to be the delivery kid.<br>' +
    'He knows every street. Every shortcut. Every broken doorbell.<br><br>' +
    'But the drone can fly.<br>' +
    'And Johnny\'s bike is dead.<br><br>' +
    '<span class="red">He did nothing today.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 33: LOGIN AS SALLY -- COOKIE SALES
  // ============================================================
  console.log('  Scene 33: Login as Sally');
  await visibleLogin(page, 'sally');

  console.log('  Scene 33b: Sally\'s dashboard');
  await goToDashboardTab(page, 'My Items');
  await sleep(4000);

  await showOverlay(page,
    'SALLY\'S WEEK',
    'Cookie sales are growing.',
    '<div style="text-align:left; font-size:32px; line-height:2">' +
    'Cookie cutters rented: 3 times this month<br>' +
    'Custom orders: 4 fulfilled<br>' +
    'Training sessions: 2 (including Sofia)<br><br>' +
    'Total revenue this week: <span class="hl">EUR 235</span><br><br>' +
    '<span class="dim">Not bad for a kitchen in Trapani.</span></div>',
    12000
  );


  // ============================================================
  // SCENE 34: SALLY VISITS JOHNNY'S WORKSHOP
  // ============================================================
  console.log('  Scene 34: Sally visits Johnny\'s workshop');
  await page.goto(`${BASE}/workshop/johns-cleaning`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Scroll to items -- see the broken bike
  await smoothScroll(page, 500);
  await sleep(4000);

  // Click into the broken bike listing
  console.log('  Scene 34b: Sally sees Johnny\'s broken bike');
  await page.goto(`${BASE}/items/johnnys-delivery-bike-broken`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 35: THE MATH (overlay, 12s)
  // ============================================================
  console.log('  Scene 35: The Math card');
  await showOverlay(page,
    'THE MATH',
    'Sally does the numbers.',
    '<div style="text-align:left; font-size:36px; line-height:2">' +
    'Sally\'s cookie earnings: <span class="green">EUR 235</span><br>' +
    'Used electric scooter: <span class="hl">EUR 200</span><br>' +
    'Left over: <span class="green">EUR 35</span><br><br>' +
    'Johnny\'s bike repair: too expensive, frame is bent<br>' +
    'Johnny\'s delivery fee: <span class="hl">EUR 5 per run</span><br><br>' +
    '<span class="dim">A scooter pays for itself in 40 deliveries.</span><br>' +
    '<span class="dim">Johnny does 40 deliveries in two weeks.</span></div>',
    14000
  );


  // ============================================================
  // SCENE 36: SALLY VIEWS JOHNNY'S DELIVERY SERVICE
  // ============================================================
  console.log('  Scene 36: Sally views delivery service');
  await page.goto(`${BASE}/items/johnny-local-delivery-trapani`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 37: THE DOOR (epilogue card, 12s)
  // ============================================================
  console.log('\n  === EPILOGUE ===\n');
  console.log('  Scene 37: The Door card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    'EPILOGUE \u00BB THE DOOR',
    'Every problem opens one.',
    '<div class="extra">' +
    'A crashed drone led to cookie cutters.<br>' +
    'Cookie cutters led to Sofia\'s baking.<br>' +
    'Sofia\'s baking needed delivery.<br>' +
    'Delivery exposed Johnny\'s broken bike.<br><br>' +
    '<span class="hl">And Sally has the money to fix it.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 38: THE QUESTION (gold text, dark background, 16s)
  // ============================================================
  console.log('  Scene 38: The Question');
  await page.goto(card(
    '#0f172a',
    'THE PARTNERSHIP',
    '',
    '<div class="extra" style="text-align:left; font-size:36px; line-height:1.8; margin-bottom:30px">' +
    'The drone flies but can\'t knock on doors.<br>' +
    'Johnny knocks on doors but can\'t fly.<br>' +
    'Sally bakes but can\'t deliver.<br>' +
    'Sofia bakes AND sells but needs both.</div>'
  ));
  await sleep(8000);


  // ============================================================
  // SCENE 39: TO BE CONTINUED (GREEN -- 16s)
  // ============================================================
  console.log('  Scene 39: To Be Continued');
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
    <span class="name">Sally's</span> cookies are selling. EUR 235 this week.<br>
    <span class="name">Johnny's</span> bike is dead. His dream is delivery.<br>
    A used electric scooter costs EUR 200.<br>
    <span class="name">Sally</span> sees his face.
  </div>
  <div class="question">What if the cookie queen... bought the delivery kid his wheels?</div>
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
