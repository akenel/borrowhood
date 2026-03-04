#!/usr/bin/env node
/**
 * THE CRASH -- Recording Script
 *
 * Drones, deposits, disputes & account deletion.
 * Two-act structure with long overlay cards for viewer comprehension.
 *
 * ACT 1 -- THE CRASH (Drone Rental Gone Wrong):
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- dark blue
 *   3.  Browse Pietro's drone workshop (guest)
 *   4.  Card: PIETRO FERRETTI (drone fleet intro)
 *   5.  Scroll through items -- 3 drones
 *   6.  Card: SALLY THOMPSON (she wants to rent a drone)
 *   7.  Login as Sally, rent Mini 4 Pro
 *   8.  Card: DEPOSIT HELD (explain deposits)
 *   9.  Create deposit via API
 *  10.  Card: PICKUP DAY (explain pickup)
 *  11.  Sally picks up (status -> PICKED_UP)
 *  12.  Card: THE RETURN (damage found)
 *  13.  Sally returns item (status -> RETURNED)
 *  14.  Card: PIETRO FILES A DISPUTE (explain dispute process)
 *  15.  Login as Pietro, file dispute (ITEM_DAMAGED)
 *  16.  Card: SALLY'S REBUTTAL (explain response)
 *  17.  Login as Sally, respond to dispute
 *  18.  Card: THE RESOLUTION (explain partial deposit)
 *  19.  Login as Pietro, resolve dispute (partial deposit)
 *  20.  Show deposit status (PARTIAL_RELEASE)
 *
 * ACT 2 -- THE CLEAN EXIT (Account Deletion):
 *  21.  Card: THE CLEAN EXIT (recap from EP14)
 *  22.  Login as Sally, try to delete (still blocked -- open dispute rental?)
 *  23.  Card: RESOLVE FIRST (explain what blocks her)
 *  24.  Sally cancels her service quote from EP14
 *  25.  Sally tries to delete again -- success!
 *  26.  Card: GONE (profile disappeared)
 *  27.  Visit Sally's profile as guest (404)
 *  28.  GREEN "FEATURE COMPLETE" card
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
  h1 { font-size: 128px; font-weight: 900; margin-bottom: 24px; text-shadow: 4px 4px 16px rgba(0,0,0,0.4); letter-spacing: -3px; line-height: 1.0; }
  h2 { font-size: 56px; font-weight: 400; opacity: 0.9; margin-bottom: 20px; line-height: 1.3; }
  .extra { font-size: 40px; opacity: 0.7; margin-top: 16px; line-height: 1.5; max-width: 1600px; }
  .badge { display: inline-block; padding: 12px 32px; border-radius: 12px; background: rgba(255,255,255,0.2); font-size: 44px; font-weight: 700; margin-top: 24px; }
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

// ── API helper ─
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

async function demoLogout(page) {
  await apiCall(page, 'POST', '/api/v1/demo/logout', {});
  await sleep(300);
}

// ── DOM overlay (stays on BASE origin) ─ LONGER durations for EP15
async function showOverlay(page, name, subtitle, extra = '', duration = 7000) {
  await page.evaluate(() => { document.body.style.zoom = '1'; });
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
      padding: 40px 80px;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:128px; font-weight:900; margin-bottom:24px;
                 text-shadow:4px 4px 16px rgba(0,0,0,0.4); letter-spacing:-3px">${n}</h1>
      <h2 style="font-size:56px; font-weight:400; opacity:0.9;
                 margin-bottom:20px; line-height:1.3">${s}</h2>
      ${e ? `<div style="font-size:36px; opacity:0.7; margin-top:16px; line-height:1.6; max-width:1400px">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
  }, name, subtitle, extra);
  await sleep(duration);
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

// ── Smooth scroll ─
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

// ── Set 150% zoom ─
async function setZoom(page) {
  await page.evaluate(() => { document.body.style.zoom = '1.5'; });
  await sleep(300);
}

// ── Show red click ring (Rule 3) ─
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

// ── Click element by text with ring ─
async function clickWithRing(page, text, scope = 'button') {
  const pos = await page.evaluate((txt, s) => {
    const els = document.querySelectorAll(s);
    for (const el of els) {
      if (el.textContent.trim().includes(txt) && !el.closest('.fixed')) {
        const box = el.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
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
      if (el.textContent.trim().includes(txt) && !el.closest('.fixed')) { el.click(); return; }
    }
  }, text, scope);
  await sleep(2000);
  return true;
}

// ── Click link by href with ring ─
async function clickLinkWithRing(page, hrefPart) {
  const pos = await page.evaluate((href) => {
    const el = document.querySelector(`a[href*="${href}"]`);
    if (!el) return null;
    const box = el.getBoundingClientRect();
    return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  }, hrefPart);
  if (!pos) { console.log(`  WARN: link "${hrefPart}" not found`); return false; }
  await showRing(page, pos.x, pos.y);
  await sleep(400);
  await page.evaluate((href) => {
    const el = document.querySelector(`a[href*="${href}"]`);
    if (el) el.click();
  }, hrefPart);
  await sleep(2000);
  return true;
}

// ── Type into input with visible typing ─
async function typeSlowly(page, selector, text, delay = 60) {
  await page.focus(selector);
  for (const char of text) {
    await page.keyboard.type(char, { delay });
  }
  await sleep(500);
}

// ── Show toast notification ─
async function showToast(page, message, type = 'success') {
  await page.evaluate((msg, t) => {
    window.dispatchEvent(new CustomEvent('toast', {
      detail: { type: t, message: msg }
    }));
  }, message, type);
  await sleep(3000);
}

// ── Show error banner (red) at top of page ─
async function showErrorBanner(page, message) {
  await page.evaluate((msg) => {
    const banner = document.createElement('div');
    banner.id = 'error-banner';
    banner.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100%; z-index: 99998;
      background: #DC2626; color: white; padding: 16px 24px;
      font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px;
      font-weight: 600; text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    banner.textContent = msg;
    document.body.appendChild(banner);
  }, message);
  await sleep(5000);
  await page.evaluate(() => {
    const b = document.getElementById('error-banner');
    if (b) b.remove();
  });
}


// ══════════════════════════════════════════════════════════════
// ══ MAIN ═════════════════════════════════════════════════════
// ══════════════════════════════════════════════════════════════
(async () => {
  console.log(`\n  THE CRASH -- Recording Script`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Auth: demoLogin (fast, no Keycloak form)`);
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
  // SCENE 2: FEATURE INTRO (DARK BLUE) -- 10s
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
  // SCENE 3: PIETRO FERRETTI (character card -- 8s)
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
  // SCENE 4: PIETRO'S WORKSHOP (guest view)
  // ============================================================
  console.log('  Scene 4: Pietro\'s workshop profile');
  await page.goto(`${BASE}/workshop/pietros-drones`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll to show skills (Drone Piloting, Aerial Photography)
  console.log('  Scene 4b: Skills + reputation');
  await smoothScroll(page, 400);
  await sleep(4000);

  // Scroll to show items (3 drones)
  console.log('  Scene 4c: Drone fleet');
  await smoothScroll(page, 500);
  await sleep(5000);


  // ============================================================
  // SCENE 5: SALLY THOMPSON (character card -- 8s)
  // ============================================================
  console.log('  Scene 5: Sally character card');
  await showOverlay(page,
    'SALLY THOMPSON',
    'She wants to rent a drone for vacation photos.',
    'The DJI Mini 4 Pro. Under 249g. No license needed.<br>EUR 25/day. EUR 100 deposit.',
    8000
  );


  // ============================================================
  // SCENE 6: Login as Sally, browse Mini 4 Pro listing
  // ============================================================
  console.log('  Scene 6: Sally views Mini 4 Pro');
  await demoLogin(page, 'sally');
  await page.goto(`${BASE}/items/dji-mini-4-pro-beginner-friendly`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Scroll to see rental details + deposit info
  await smoothScroll(page, 350);
  await sleep(4000);


  // ============================================================
  // SCENE 7: Sally requests rental
  // ============================================================
  console.log('  Scene 7: Sally requests rental');

  // Find the rental listing for Mini 4 Pro
  const miniListings = await apiCall(page, 'GET', '/api/v1/listings?item_slug=dji-mini-4-pro-beginner-friendly');
  let miniRentListingId = null;
  if (miniListings.data && miniListings.data.items) {
    const rentListing = miniListings.data.items.find(l => l.listing_type === 'rent');
    if (rentListing) miniRentListingId = rentListing.id;
  }
  // Fallback: search all Pietro's listings
  if (!miniRentListingId) {
    const allListings = await apiCall(page, 'GET', '/api/v1/listings?q=Mini+4+Pro&listing_type=rent');
    if (allListings.data && allListings.data.items && allListings.data.items.length > 0) {
      miniRentListingId = allListings.data.items[0].id;
    }
  }
  console.log(`  Mini 4 Pro rent listing ID: ${miniRentListingId}`);

  // Try the Rent This Item button
  const hasRentBtn = await clickWithRing(page, 'Rent This Item', 'button, a');
  if (hasRentBtn) {
    await sleep(1000);
    // Fill rental form if modal opens
    const textarea = await page.$('textarea');
    if (textarea) {
      await typeSlowly(page, 'textarea',
        'Vacation in Scopello next week. Want aerial shots of the coastline.', 30);
      await sleep(1000);
      await clickWithRing(page, 'Submit', 'button');
      await sleep(2000);
    }
  } else if (miniRentListingId) {
    // API fallback
    const startDate = new Date(Date.now() + 3 * 86400000).toISOString();
    const endDate = new Date(Date.now() + 5 * 86400000).toISOString();
    const rentalResp = await apiCall(page, 'POST', '/api/v1/rentals', {
      listing_id: miniRentListingId,
      requested_start: startDate,
      requested_end: endDate,
      renter_message: 'Vacation in Scopello next week. Want aerial shots of the coastline.',
    });
    console.log(`  Rental created: ${JSON.stringify(rentalResp.data?.id || rentalResp.data)}`);
    await showToast(page, 'Rental request sent to Pietro!');
  }
  await sleep(3000);

  // Get the rental ID we just created
  const myRentals = await apiCall(page, 'GET', '/api/v1/rentals?role=renter&status=pending');
  let rentalId = null;
  if (myRentals.data && myRentals.data.length > 0) {
    // Find the one for Mini 4 Pro
    rentalId = myRentals.data[0].id;
  }
  console.log(`  Rental ID: ${rentalId}`);
  await demoLogout(page);


  // ============================================================
  // SCENE 8: Pietro approves the rental (fast, via API)
  // ============================================================
  console.log('  Scene 8: Pietro approves');
  await demoLogin(page, 'pietro');
  if (rentalId) {
    const approveResp = await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, {
      status: 'approved',
      message: 'Approved! Come pick it up Saturday morning. I will give you a 15-minute tutorial.',
    });
    console.log(`  Rental approved: ${approveResp.data?.status || approveResp.status}`);
  }
  await demoLogout(page);


  // ============================================================
  // SCENE 9: DEPOSIT HELD (explainer card -- 10s)
  // ============================================================
  console.log('  Scene 9: Deposit explainer card');
  await demoLogin(page, 'sally');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await showOverlay(page,
    'DEPOSIT HELD',
    'EUR 100 collected before pickup.',
    'The deposit protects the owner.<br>Return the item undamaged -- you get it all back.<br>Damage it -- the owner keeps some or all.<br><br><span style="color:#FCD34D; font-weight:700">Status: HELD</span>',
    10000
  );

  // Create deposit via API
  if (rentalId) {
    const depositResp = await apiCall(page, 'POST', '/api/v1/deposits', {
      rental_id: rentalId,
      amount: 100.0,
      currency: 'EUR',
    });
    console.log(`  Deposit created: ${depositResp.data?.id || depositResp.status}`);
    await showToast(page, 'Deposit paid: EUR 100.00 held');
  }
  await sleep(3000);


  // ============================================================
  // SCENE 10: PICKUP DAY (card -- 8s)
  // ============================================================
  console.log('  Scene 10: Pickup day card');
  await showOverlay(page,
    'PICKUP DAY',
    'Sally collects the Mini 4 Pro from Pietro.',
    'Rental status changes from APPROVED to PICKED_UP.<br>The clock starts ticking.',
    8000
  );

  // Transition to PICKED_UP
  if (rentalId) {
    const pickupResp = await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, {
      status: 'picked_up',
    });
    console.log(`  Rental picked up: ${pickupResp.data?.status || pickupResp.status}`);
    await showToast(page, 'Item picked up! Rental is active.');
  }
  await sleep(3000);


  // ============================================================
  // SCENE 11: THE RETURN -- DAMAGE (card -- 10s)
  // ============================================================
  console.log('  Scene 11: Return / damage card');
  await showOverlay(page,
    'THE RETURN',
    'Two days later. The drone comes back.',
    'Gimbal cracked. One propeller snapped.<br>Sally says it was a wind gust over the cliffs.<br><br>Rental status: PICKED_UP to RETURNED.<br><span style="color:#FCA5A5; font-weight:700">But the damage is real.</span>',
    10000
  );

  // Return the item
  if (rentalId) {
    const returnResp = await apiCall(page, 'PATCH', `/api/v1/rentals/${rentalId}/status`, {
      status: 'returned',
      message: 'Returning the drone. Sorry about the gimbal -- strong wind near the cliffs.',
    });
    console.log(`  Rental returned: ${returnResp.data?.status || returnResp.status}`);
    await showToast(page, 'Item returned. Owner will inspect.');
  }
  await demoLogout(page);
  await sleep(2000);


  // ============================================================
  // SCENE 12: PIETRO FILES A DISPUTE (card -- 10s)
  // ============================================================
  console.log('  Scene 12: Dispute explainer card');
  await demoLogin(page, 'pietro');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await showOverlay(page,
    'PIETRO FILES A DISPUTE',
    'The gimbal is cracked. A propeller snapped.',
    'Reason: ITEM DAMAGED<br>Evidence: photos of the cracked gimbal<br><br>The rental status changes to DISPUTED.<br>Now Sally gets to respond -- her side of the story.',
    10000
  );

  // File dispute via API
  let disputeId = null;
  if (rentalId) {
    const disputeResp = await apiCall(page, 'POST', '/api/v1/disputes', {
      rental_id: rentalId,
      reason: 'item_damaged',
      description: 'DJI Mini 4 Pro returned with cracked gimbal and one propeller snapped off. Gimbal replacement costs EUR 55, propeller set EUR 15. Total damage: EUR 70.',
    });
    disputeId = disputeResp.data?.id;
    console.log(`  Dispute filed: ${disputeId || disputeResp.status}`);
    await showToast(page, 'Dispute filed: item_damaged');
  }

  // Show Pietro's dashboard with rental in DISPUTED state
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  // Click My Rentals tab
  await clickWithRing(page, 'My Rentals', '[role="tab"], button, a');
  await sleep(3000);
  // Click Incoming Requests to see the disputed rental
  await clickWithRing(page, 'Incoming Requests', '[role="tab"], button, a');
  await sleep(4000);

  await demoLogout(page);


  // ============================================================
  // SCENE 13: SALLY'S REBUTTAL (card -- 10s)
  // ============================================================
  console.log('  Scene 13: Rebuttal explainer card');
  await demoLogin(page, 'sally');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await showOverlay(page,
    "SALLY'S REBUTTAL",
    'Both sides get heard.',
    'Sally responds to the dispute with her side.<br>"Wind gust over the Scopello cliffs -- not negligence."<br><br>Status moves from FILED to UNDER_REVIEW.<br><span style="color:#FCD34D; font-weight:700">The platform does not take sides. It tracks both.</span>',
    10000
  );

  // Sally responds to dispute
  if (disputeId) {
    const respondResp = await apiCall(page, 'PATCH', `/api/v1/disputes/${disputeId}/respond`, {
      response: 'Wind gust caught the drone over the Scopello cliffs. I followed all safety instructions Pietro gave me. The gimbal housing was already loose when I picked it up. I accept the propeller cost but not the full gimbal replacement.',
    });
    console.log(`  Dispute response: ${respondResp.data?.dispute_status || respondResp.status}`);
    await showToast(page, 'Response submitted. Dispute is now UNDER REVIEW.');
  }
  await sleep(3000);
  await demoLogout(page);


  // ============================================================
  // SCENE 14: THE RESOLUTION (card -- 12s)
  // ============================================================
  console.log('  Scene 14: Resolution explainer card');
  await demoLogin(page, 'pietro');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await showOverlay(page,
    'THE RESOLUTION',
    'Pietro decides: partial deposit.',
    'EUR 100 deposit was held.<br><br>EUR 70 to Pietro -- gimbal (EUR 55) + propeller (EUR 15)<br>EUR 30 back to Sally<br><br>Resolution: <span style="color:#FCD34D; font-weight:700">PARTIAL DEPOSIT RELEASE</span><br><br><span style="opacity:0.5">Both sides documented. Both sides heard. Fair outcome.</span>',
    12000
  );

  // Get deposit ID for this rental
  let depositId = null;
  const deposits = await apiCall(page, 'GET', '/api/v1/deposits?status=held');
  if (deposits.data && deposits.data.length > 0) {
    const rentalDeposit = deposits.data.find(d => d.rental_id === rentalId);
    if (rentalDeposit) depositId = rentalDeposit.id;
    else depositId = deposits.data[0].id;
  }
  console.log(`  Deposit ID: ${depositId}`);

  // Resolve dispute with partial deposit forfeiture
  if (disputeId) {
    const resolveResp = await apiCall(page, 'PATCH', `/api/v1/disputes/${disputeId}/resolve`, {
      resolution: 'partial_refund',
      resolution_notes: 'Partial deposit release. EUR 70 retained for gimbal + propeller repair. EUR 30 returned to renter. Both parties documented their positions.',
    });
    console.log(`  Dispute resolved: ${resolveResp.data?.resolution || resolveResp.status}`);
  }

  // Release deposit partially: EUR 70 forfeited (to Pietro), EUR 30 released (to Sally)
  if (depositId) {
    const forfeitResp = await apiCall(page, 'PATCH', `/api/v1/deposits/${depositId}/forfeit`, {
      forfeited_amount: 70.0,
      reason: 'Gimbal replacement EUR 55 + propeller set EUR 15 = EUR 70 damage cost.',
    });
    console.log(`  Deposit forfeited/partial: ${JSON.stringify(forfeitResp.data)}`);
    await showToast(page, 'Deposit resolved: EUR 70 to owner, EUR 30 to renter');
  }
  await sleep(4000);
  await demoLogout(page);


  // ============================================================
  // SCENE 15: DEPOSIT STATUS (show on Sally's dashboard)
  // ============================================================
  console.log('  Scene 15: Deposit status visible');
  await demoLogin(page, 'sally');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await clickWithRing(page, 'My Rentals', '[role="tab"], button, a');
  await sleep(4000);

  // Show deposit outcome overlay
  await showOverlay(page,
    'DEPOSIT OUTCOME',
    'Sally gets EUR 30 back. Pietro keeps EUR 70.',
    'Deposit Status: <span style="color:#FCD34D; font-weight:700">PARTIAL RELEASE</span><br><br>The deposit did its job -- protected the owner<br>without bankrupting the renter.',
    8000
  );


  // ════════════════════════════════════════════════════════════
  // ══ ACT 2: THE CLEAN EXIT ═════════════════════════════════
  // ════════════════════════════════════════════════════════════

  // ============================================================
  // SCENE 16: ACT 2 INTRO (card -- 10s)
  // ============================================================
  console.log('\n  === ACT 2: THE CLEAN EXIT ===\n');
  console.log('  Scene 16: Act 2 intro card');
  await page.goto(card(
    'linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #7f1d1d 100%)',
    'THE CLEAN EXIT',
    'Can Sally leave BorrowHood?',
    '<div class="extra">Last episode, she was blocked. Active service quote.<br>This time she resolves everything first.<br><br><span class="hl">GDPR says: your data, your choice.</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 17: Sally tries to delete (should she be blocked?)
  // ============================================================
  console.log('  Scene 17: Sally goes to Settings');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await clickWithRing(page, 'Settings', '[role="tab"], button, a');
  await sleep(3000);

  // Scroll to Danger Zone
  await smoothScroll(page, 300);
  await sleep(3000);

  // Try to delete -- should be blocked by active service quote from EP14
  console.log('  Scene 17b: Try to delete (expect blocked)');
  await clickWithRing(page, 'Delete Account', 'button');
  await sleep(1000);

  // Handle confirm dialog
  page.once('dialog', async dialog => {
    console.log(`  Dialog: ${dialog.message()}`);
    await dialog.accept();
  });
  await clickWithRing(page, 'Delete Account', 'button');
  await sleep(2000);

  // The API should return 409 -- show the error
  const deleteAttempt = await apiCall(page, 'DELETE', '/api/v1/users/me');
  console.log(`  Delete attempt: ${deleteAttempt.status} ${JSON.stringify(deleteAttempt.data)}`);
  if (deleteAttempt.status === 409) {
    await showErrorBanner(page, deleteAttempt.data?.detail || 'Cannot delete account: active obligations remain.');
  }
  await sleep(4000);


  // ============================================================
  // SCENE 18: RESOLVE FIRST (card -- 10s)
  // ============================================================
  console.log('  Scene 18: Resolve explainer card');
  await showOverlay(page,
    'RESOLVE FIRST',
    'Sally has 1 active service quote.',
    'From Episode 14: furniture repair, EUR 135.<br>Status: ACCEPTED (work not started yet).<br><br>She needs to cancel or complete it<br>before the platform lets her leave.<br><br><span style="color:#6EE7B7; font-weight:700">Cancel the quote. Then try again.</span>',
    10000
  );


  // ============================================================
  // SCENE 19: Sally cancels her service quote
  // ============================================================
  console.log('  Scene 19: Cancel service quote');

  // Find Sally's active service quotes
  const quotesResp = await apiCall(page, 'GET', '/api/v1/service-quotes?role=customer');
  let activeQuoteId = null;
  if (quotesResp.data) {
    const activeQuote = quotesResp.data.find(q =>
      q.status === 'accepted' || q.status === 'requested' || q.status === 'quoted' || q.status === 'in_progress'
    );
    if (activeQuote) activeQuoteId = activeQuote.id;
  }
  console.log(`  Active quote ID: ${activeQuoteId}`);

  if (activeQuoteId) {
    const cancelResp = await apiCall(page, 'PATCH', `/api/v1/service-quotes/${activeQuoteId}/status`, {
      status: 'cancelled',
      cancel_reason: 'Leaving the platform. Will find another woodworker.',
    });
    console.log(`  Quote cancelled: ${cancelResp.data?.status || cancelResp.status}`);
    await showToast(page, 'Service quote cancelled.');
  }
  await sleep(3000);


  // ============================================================
  // SCENE 20: Sally deletes her account (success!)
  // ============================================================
  console.log('  Scene 20: Delete account -- should succeed');

  // Navigate to Settings again
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await clickWithRing(page, 'Settings', '[role="tab"], button, a');
  await sleep(2000);
  await smoothScroll(page, 300);
  await sleep(2000);

  // Click Delete Account
  await clickWithRing(page, 'Delete Account', 'button');
  await sleep(1500);

  // Handle confirm dialog
  page.once('dialog', async dialog => {
    console.log(`  Dialog: ${dialog.message()}`);
    await dialog.accept();
  });

  // Wait for the actual deletion -- the front-end JS should handle it
  // But if the button triggers the JS flow directly, we just wait
  await sleep(3000);

  // If the front-end didn't trigger, do it via API
  const deleteResp = await apiCall(page, 'DELETE', '/api/v1/users/me');
  console.log(`  Delete response: ${deleteResp.status} ${JSON.stringify(deleteResp.data)}`);
  if (deleteResp.status === 200) {
    await showToast(page, 'Account deleted. Goodbye, Sally.');
  }
  await sleep(4000);


  // ============================================================
  // SCENE 21: GONE (card -- 10s)
  // ============================================================
  console.log('  Scene 21: Gone card');
  await demoLogout(page);

  await showOverlay(page,
    'GONE',
    'Sally\'s profile has disappeared.',
    'deleted_at: set<br>account_status: DEACTIVATED<br>Listings: PAUSED<br>Telegram link: cleared<br>Audit log: recorded<br><br><span style="color:#6EE7B7; font-weight:700">The platform forgets. The data stays safe.</span>',
    10000
  );


  // ============================================================
  // SCENE 22: Visit Sally's profile (404)
  // ============================================================
  console.log('  Scene 22: Sally\'s profile -- 404');
  // Find Sally's user ID from the member directory (she won't appear)
  await page.goto(`${BASE}/members`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Search for Sally -- should not appear
  const searchInput = await page.$('input[type="search"], input[placeholder*="Search"], input[name="q"]');
  if (searchInput) {
    await typeSlowly(page, 'input[type="search"], input[placeholder*="Search"], input[name="q"]', 'Sally', 80);
    await sleep(3000);
  }

  // Show that Sally is not in results
  await showOverlay(page,
    'NOT FOUND',
    'Sally Thompson no longer appears.',
    'The member directory filters deleted accounts.<br>WHERE deleted_at IS NULL<br><br><span style="opacity:0.5">Clean exit. No ghost profiles. No zombie data.</span>',
    8000
  );


  // ============================================================
  // SCENE 23: FEATURE COMPLETE (GREEN) -- 12s
  // ============================================================
  console.log('  Scene 23: Feature Complete');
  await page.goto(card(
    '#059669',
    'FEATURE COMPLETE',
    'The Crash',
    `<div class="extra" style="text-align:left; font-size:36px">
      <span class="check">&#10003;</span> Drone Fleet with Rental Deposits<br>
      <span class="check">&#10003;</span> Deposit Lifecycle: HELD to PARTIAL RELEASE<br>
      <span class="check">&#10003;</span> Dispute Filing with Evidence<br>
      <span class="check">&#10003;</span> Rebuttal -- Both Sides Heard<br>
      <span class="check">&#10003;</span> Resolution: Partial Deposit Split<br>
      <span class="check">&#10003;</span> Account Deletion: Blocked, Resolved, Deleted<br>
      <span class="check">&#10003;</span> GDPR-Ready Soft Delete<br>
      <span class="dim" style="font-size:32px; margin-top:16px; display:block">Built with Claude Code (Opus)</span>
    </div>`
  ));
  await sleep(12000);


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
