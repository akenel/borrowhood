#!/usr/bin/env node
/**
 * AUCTION -- Competitive Bidding Recording Script (v3)
 *
 * KEY CHANGES from v2:
 *   - Uses demoLogin() exclusively (no Keycloak form -- fast + reliable)
 *   - Navigates to BASE before API calls to avoid data: URL CORS issues
 *   - Character name cards shown as DOM overlays (stay on BASE origin)
 *   - No kcLogout() needed (demoLogin overwrites the session cookie)
 *
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   --- Auction created HERE (2 min timer) ---
 *   2.  Intro card (amber)
 *   3.  Browse page -- Mountain Bike with amber "Auction" badge
 *   4.  Item detail as Dave -- countdown ticking
 *   5.  Sally overlay card -> bids EUR 50
 *   6.  Rosa overlay card -> outbids EUR 75
 *   7.  Sally overlay card -> bids EUR 130 (reserve met)
 *   8.  Dave overlay card -> watches countdown to zero
 *   9.  Dave ends auction -- winner announced
 *  10.  AMBER "FEATURE COMPLETE" card
 *
 * Pre-flight (before OBS):
 *   - Demo login as Dave, get item ID
 *   - Cleanup stale auction listings
 *
 * Usage: node record-auction.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://46.62.138.218';
const VP = { width: 1920, height: 1080 };
const BIKE_SLUG = 'mountain-bike-specialized-rockhopper';
const AUCTION_DURATION_SEC = 120; // 2 minutes -- real countdown

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
// Does NOT remove itself -- the next page.goto() wipes the DOM naturally.
// This prevents a brief flash of the underlying page between card and navigation.
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
  // Overlay stays visible until next page.goto() replaces the page
}

// ── Scroll to auction panel ──────────────────────────────────
async function scrollToAuction(page) {
  await page.evaluate(() => {
    const panel = document.querySelector('.border-amber-300');
    if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}

// ── Place bid visually (type amount + click button) ──────────
async function placeBidVisual(page, amount) {
  // Clear input and type new amount
  await page.evaluate(() => {
    const panel = document.querySelector('.border-amber-300');
    if (!panel) return;
    const input = panel.querySelector('input[type="number"]');
    if (input) {
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
      ).set;
      nativeSetter.call(input, '');
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.focus();
    }
  });
  await page.type('.border-amber-300 input[type="number"]', String(amount), { delay: 60 });
  await sleep(1000);

  // Click Place Bid button
  await page.evaluate(() => {
    const panel = document.querySelector('.border-amber-300');
    if (!panel) return;
    const btns = panel.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Place Bid') || b.textContent.includes('Bid')) {
        b.click(); return;
      }
    }
  });
  await sleep(3000); // Wait for success feedback + summary refresh
}

// ── Switch user: demoLogin + navigate to item page ───────────
async function switchUser(page, username, itemUrl) {
  // demoLogin works because we're on BASE origin (overlay on item page)
  await demoLogin(page, username);
  // Navigate to item page -- loads with new user's session
  await page.goto(itemUrl, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1000);
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  AUCTION -- Competitive Bidding Recording Script (v3)`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Auction duration: ${AUCTION_DURATION_SEC}s`);
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
    ]
  });

  const page = await browser.newPage();
  await page.setViewport(VP);

  const itemUrl = `${BASE}/items/${BIKE_SLUG}?lang=en`;

  // ── Pre-flight: establish cookie domain + cleanup ──────────
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);

  console.log('  Pre-flight: cleanup...');
  await demoLogin(page, 'dave');

  // Get bike item ID
  const itemsResp = await apiCall(page, 'GET', '/api/v1/items?category=sports&limit=100');
  const bikeItem = (itemsResp.data || []).find(i => i.slug === BIKE_SLUG);
  if (!bikeItem) {
    console.error('  FATAL: Mountain Bike not found!');
    await browser.close();
    process.exit(1);
  }
  console.log(`  Item: ${bikeItem.name} (${bikeItem.id})`);

  // Cleanup existing active auctions
  const listingsResp = await apiCall(page, 'GET', `/api/v1/listings?item_id=${bikeItem.id}`);
  for (const l of (listingsResp.data || [])) {
    if (l.listing_type === 'auction' && l.status === 'active') {
      console.log(`  Ending stale auction ${l.id}`);
      await apiCall(page, 'POST', `/api/v1/bids/${l.id}/end`);
    }
  }
  console.log('  Pre-flight: done\n');

  // ============================================================
  // SCENE 1: OBS CHECK (RED) -- data: URL, no API calls
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">AUCTION | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ── CREATE AUCTION NOW (timer starts!) ─────────────────────
  // Navigate back to BASE before API calls (data: URL = null origin = CORS block)
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });

  const auctionEnd = new Date(Date.now() + AUCTION_DURATION_SEC * 1000).toISOString();
  console.log(`  Creating auction (ends in ${AUCTION_DURATION_SEC}s at ${auctionEnd})`);
  await demoLogin(page, 'dave');
  const createResp = await apiCall(page, 'POST', '/api/v1/listings', {
    item_id: bikeItem.id,
    listing_type: 'auction',
    currency: 'EUR',
    pickup_only: true,
    notes: 'Size L frame, 29" wheels. Helmet included. Highest bidder wins!',
    starting_bid: 50.0,
    reserve_price: 120.0,
    bid_increment: 5.0,
    auction_end: auctionEnd,
  });
  if (createResp.status !== 201) {
    console.error(`  FATAL: ${JSON.stringify(createResp.data)}`);
    await browser.close();
    process.exit(1);
  }
  const listingId = createResp.data.id;
  console.log(`  Auction live: ${listingId}`);
  console.log(`  EUR 50 start | EUR 120 reserve | EUR 5 increment\n`);

  function timeLeft() {
    const sec = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
    if (sec < 0) return '0:00';
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  // ============================================================
  // SCENE 2: INTRO (AMBER) -- 5s -- data: URL, no API calls
  // ============================================================
  console.log(`  Scene 2: Intro [timer: ${timeLeft()}]`);
  await page.goto(card(
    '#B45309',
    'AUCTION',
    'Competitive Bidding. Reserve Price. Live Countdown.',
    '<div class="badge">REAL-TIME</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Dave lists his Mountain Bike. Sally and Rosa bid.<br>' +
    'The timer counts down. Winner takes all.' +
    '</div>'
  ));
  await sleep(5000);

  // ============================================================
  // SCENE 3: BROWSE -- Mountain Bike with "Auction" badge -- 4s
  // (Back on BASE origin from here on)
  // ============================================================
  console.log(`  Scene 3: Browse [timer: ${timeLeft()}]`);
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a');
    for (const c of cards) {
      if (c.textContent.includes('Mountain Bike') || c.textContent.includes('Specialized')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(2000);

  // ============================================================
  // SCENE 4: ITEM DETAIL (as Dave) -- auction panel + countdown
  // ============================================================
  console.log(`  Scene 4: Item detail as Dave [timer: ${timeLeft()}]`);
  await page.goto(itemUrl, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await scrollToAuction(page);
  await sleep(2000);

  // ============================================================
  // SCENE 5: SALLY BIDS EUR 50
  // Overlay card on item page (stays on BASE origin -- demoLogin works)
  // ============================================================
  console.log(`  Scene 5: Sally bids 50 [timer: ${timeLeft()}]`);
  await showOverlay(page, 'SALLY THOMPSON', 'First bid on the Mountain Bike',
    'She wants it for trail rides around Erice.');

  await switchUser(page, 'sally', itemUrl);
  await scrollToAuction(page);
  await sleep(1000);
  await placeBidVisual(page, 50);
  console.log(`  Sally bid placed [timer: ${timeLeft()}]`);

  // ============================================================
  // SCENE 6: ROSA OUTBIDS SALLY
  // ============================================================
  console.log(`  Scene 6: Rosa outbids [timer: ${timeLeft()}]`);
  await showOverlay(page, 'ROSA FERRARA', 'Outbidding Sally',
    'Rosa wants the bike for her son. She goes higher.');

  await switchUser(page, 'rosa', itemUrl);
  await scrollToAuction(page);
  await sleep(1000);
  await placeBidVisual(page, 75);
  console.log(`  Rosa bid placed [timer: ${timeLeft()}]`);

  // ============================================================
  // SCENE 7: SALLY WINS WITH EUR 130 (RESERVE MET)
  // ============================================================
  console.log(`  Scene 7: Sally winning bid [timer: ${timeLeft()}]`);
  await showOverlay(page, 'SALLY THOMPSON', 'Coming back with a bigger bid',
    'EUR 130 -- all in. Reserve price met.');

  await switchUser(page, 'sally', itemUrl);
  await scrollToAuction(page);
  await sleep(1000);
  await placeBidVisual(page, 130);
  console.log(`  Sally winning bid placed [timer: ${timeLeft()}]`);

  // Show the reserve met indicator
  await page.evaluate(() => {
    const panel = document.querySelector('.border-amber-300');
    if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  await sleep(2000);

  // ============================================================
  // SCENE 8: DAVE WATCHES THE COUNTDOWN
  // ============================================================
  console.log(`  Scene 8: Dave watches countdown [timer: ${timeLeft()}]`);
  await showOverlay(page, 'DAVE WILSON', 'Watching the auction end',
    '3 bids. Reserve met. The clock is ticking.');

  await switchUser(page, 'dave', itemUrl);
  await scrollToAuction(page);

  // Now wait for the timer to hit zero
  const remaining = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
  console.log(`  Watching countdown: ${remaining}s remaining`);

  if (remaining > 0) {
    const checkInterval = setInterval(() => {
      const left = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
      if (left <= 15) {
        process.stdout.write(`  ${left}s... `);
      }
      if (left <= 0) {
        clearInterval(checkInterval);
        console.log('\n  TIMER HIT ZERO!');
      }
    }, 1000);

    // Wait for the full duration + 3s buffer
    await sleep((remaining + 3) * 1000);
  }

  // The Alpine.js panel should now show "Auction ended"
  await sleep(3000);
  console.log(`  "Auction ended" visible on screen`);

  // ============================================================
  // SCENE 9: DAVE ENDS AUCTION OFFICIALLY
  // ============================================================
  console.log('  Scene 9: Dave ends auction officially');

  // End via API (Dave is logged in, on BASE origin)
  const endResp = await apiCall(page, 'POST', `/api/v1/bids/${listingId}/end`);
  console.log(`  End result: winner=${endResp.data?.winner_id ? 'YES' : 'NO'}, amount=${endResp.data?.winning_amount}`);

  // Reload to show final state
  await page.reload({ waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await scrollToAuction(page);
  await sleep(4000);

  // ============================================================
  // SCENE 10: FEATURE COMPLETE (AMBER) -- data: URL, no API calls
  // ============================================================
  await page.goto(card(
    '#B45309',
    'AUCTION',
    'Complete',
    '<div class="badge">COMPETITIVE BIDDING</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Dave listed the Mountain Bike with a 2-minute countdown<br>' +
    'Sally bid EUR 50 -- Rosa outbid at EUR 75<br>' +
    'Sally came back at EUR 130 -- reserve price met<br>' +
    'Timer hit zero -- Sally wins the bike' +
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
