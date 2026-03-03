#!/usr/bin/env node
/**
 * THE AUCTION -- DJI Mini 3 Pro Drone (v6 -- production)
 *
 * Item:   DJI Mini 3 Pro with RC controller -- owned by Jake (Jake's Tech Bench)
 * Story:  Jake puts his drone up for auction. Sally and Mike both want it.
 *         Three bids. Reserve price. Countdown. Winner takes all.
 *
 * WHY THIS DRONE:
 *   - Under 249g = no licence needed in Italy (beginner-friendly!)
 *   - 4K/60fps, 48MP, obstacle avoidance
 *   - Jake includes 15-min orientation at pickup (neighbors helping neighbors)
 *   - Jake has a Keycloak account (can actually log in, unlike Pietro)
 *
 * DESIGN PHILOSOPHY:
 *   No dead time. Every second has content. The 2.5-minute countdown is
 *   broken into: bidding action + explainer cards + dramatic final seconds.
 *   A 5-year-old should understand what an auction is after watching this.
 *
 * Scene Map (18 scenes):
 *   1.  OBS CHECK (red)
 *       --- Auction created HERE (150s timer) ---
 *   2.  Intro card -- "THE AUCTION"
 *   3.  Context card -- "MEET THE DRONE" (who, what, why)
 *   4.  Browse page -- drone with amber "Auction" badge
 *   5.  Item detail (Jake) -- auction panel, countdown ticking
 *   6.  EXPLAINER: "WHAT IS AN AUCTION?" -- the rules in 6 seconds
 *   7.  Sally overlay -> bids EUR 80 (starting bid)
 *   8.  EXPLAINER: "FIRST BID IN" -- Sally is winning, reserve NOT met
 *   9.  Mike overlay -> bids EUR 150 (outbids Sally)
 *  10.  EXPLAINER: "OUTBID!" -- Mike leads, reserve still not met
 *  11.  EXPLAINER: "THE RESERVE PRICE" -- secret minimum, protection for owner
 *  12.  Sally overlay -> bids EUR 250 (above reserve, all in)
 *  13.  EXPLAINER: "RESERVE MET!" -- green badge, the sale is now valid
 *  14.  EXPLAINER: "ANTI-SNIPE" -- last-second bid protection
 *  15.  Jake overlay -> watches final countdown
 *  16.  EXPLAINER: "FINAL MOMENTS" -- what happens when timer hits zero
 *  17.  Timer hits zero -> Jake ends auction -> winner announced
 *  18.  FEATURE RECAP card -- checklist of every feature shown
 *
 * Auction config:
 *   Starting bid:  EUR 80
 *   Reserve price: EUR 200  (hidden from bidders)
 *   Bid increment: EUR 10
 *   Duration:      150s (2.5 minutes)
 *
 * Bids:
 *   Sally: EUR 80  (starting bid, below reserve)
 *   Mike:  EUR 150 (above starting, still below reserve)
 *   Sally: EUR 250 (above reserve, all in -- wins)
 *
 * Rules applied:
 *   - charset=utf-8 in data: URLs (no mojibake)
 *   - showRing() on all visible clicks (Rule 3)
 *   - 150% browser zoom on UI pages (Rule 13)
 *   - 60px click rings, 5px border (Rule 13)
 *   - Extra 2s pause after each UI click (Rule 13)
 *   - Mobile-first card text: 96px headings, 48px subtitles (Rule 13)
 *
 * Usage: node record-auction.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://46.62.138.218';
const VP = { width: 1920, height: 1080 };
const DRONE_SLUG = 'drone-dji-mini-3-pro';
const AUCTION_DURATION_SEC = 150; // 2.5 minutes -- real countdown

function waitForEnter(msg) {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(`\n>>> ${msg} [ENTER] `, () => { rl.close(); resolve(); });
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Full-page card (data: URL -- for scenes with NO api calls) ───
// charset=utf-8 prevents mojibake on ✓ and other unicode
function card(bg, title, subtitle, extra = '') {
  return `data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html><html><head><style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: ${bg}; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100vh; width: 100vw;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: white; text-align: center; padding: 40px;
  }
  h1 { font-size: 96px; font-weight: 800; margin-bottom: 24px; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
  h2 { font-size: 48px; font-weight: 400; opacity: 0.9; margin-bottom: 20px; line-height: 1.3; }
  .extra { font-size: 36px; opacity: 0.75; margin-top: 16px; line-height: 1.5; }
  .badge { display: inline-block; padding: 10px 28px; border-radius: 8px; background: rgba(255,255,255,0.2); font-size: 36px; font-weight: 600; margin-top: 20px; }
  .hl { color: #FCD34D; font-weight: 700; }
  .dim { opacity: 0.5; }
  .check { color: #34D399; }
  .warn { color: #FBBF24; }
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

// ── Show red click ring (Rule 3) ─────────────────────────────
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

// ── DOM overlay card (stays on current page = BASE origin) ────
// Does NOT remove itself -- next page.goto() wipes the DOM.
// IMPORTANT: Resets body zoom to 1.0 so overlay renders at true viewport size.
// The 150% zoom was causing overlays to overflow (96px heading * 1.5 = 144px!).
// Zoom gets restored by setZoom() when the next UI page loads.
async function showOverlay(page, name, subtitle, extra = '', bgColor = '#1E293B', duration = 3500) {
  await page.evaluate((n, s, e, bg) => {
    // Reset zoom -- overlay must render at true 1920x1080
    document.body.style.zoom = '1';

    const old = document.getElementById('name-card-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'name-card-overlay';
    overlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      z-index: 99999; display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      background: ${bg}; color: white;
      font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
      padding: 60px 80px;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:96px; font-weight:800; margin-bottom:24px;
                 text-shadow:2px 2px 8px rgba(0,0,0,0.3)">${n}</h1>
      <h2 style="font-size:44px; font-weight:400; opacity:0.9;
                 margin-bottom:20px; line-height:1.3">${s}</h2>
      ${e ? `<div style="font-size:32px; opacity:0.75; margin-top:16px; line-height:1.5; max-width:1200px">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
  }, name, subtitle, extra, bgColor);
  await sleep(duration);
}

// ── Set browser zoom to 150% (Rule 13) ──────────────────────
async function setZoom(page) {
  await page.evaluate(() => { document.body.style.zoom = '1.5'; });
}

// ── Scroll to auction panel ──────────────────────────────────
async function scrollToAuction(page) {
  await page.evaluate(() => {
    const panel = document.querySelector('.border-amber-300');
    if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}

// ── Place bid visually (type amount + click button with ring) ─
async function placeBidVisual(page, amount) {
  // Clear input and type new amount
  const inputSel = '.border-amber-300 input[type="number"]';
  await page.evaluate((sel) => {
    const input = document.querySelector(sel);
    if (input) {
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
      ).set;
      nativeSetter.call(input, '');
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.focus();
    }
  }, inputSel);
  await page.type(inputSel, String(amount), { delay: 80 });
  await sleep(1000);

  // Find and click Place Bid button with ring
  const bidBtn = await page.evaluateHandle(() => {
    const panel = document.querySelector('.border-amber-300');
    if (!panel) return null;
    const btns = [...panel.querySelectorAll('button')];
    return btns.find(b =>
      (b.textContent.includes('Place Bid') || b.textContent.includes('Bid'))
      && b.offsetWidth > 0 && b.offsetHeight > 0
    ) || null;
  });

  if (bidBtn) {
    const box = await bidBtn.boundingBox();
    if (box) {
      const cx = box.x + box.width / 2;
      const cy = box.y + box.height / 2;
      await showRing(page, cx, cy);
      await sleep(400);
      await bidBtn.click();
      await sleep(3000); // Wait for success feedback + summary refresh
    }
  }
}

// ── Switch user: demoLogin + navigate to item page ───────────
async function switchUser(page, username, itemUrl) {
  await demoLogin(page, username);
  await page.goto(itemUrl, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  await setZoom(page);
  await sleep(500);
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  THE AUCTION -- DJI Mini 3 Pro Drone (v6)`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Auction: ${AUCTION_DURATION_SEC}s | EUR 80 start | EUR 200 reserve | EUR 10 increment`);
  console.log(`  Cast: Jake (owner), Sally (bidder), Mike (bidder)`);
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

  const itemUrl = `${BASE}/items/${DRONE_SLUG}?lang=en`;

  // ── Pre-flight: establish cookie domain + cleanup ──────────
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);

  console.log('  PRE-FLIGHT');
  await demoLogin(page, 'jake');

  // Get drone item ID (API caps at limit=100, so page through)
  let allItems = [];
  for (let offset = 0; ; offset += 100) {
    const resp = await apiCall(page, 'GET', `/api/v1/items?limit=100&offset=${offset}`);
    const page_items = Array.isArray(resp.data) ? resp.data : [];
    allItems = allItems.concat(page_items);
    if (page_items.length < 100) break; // last page
  }
  console.log(`  Loaded ${allItems.length} items`);
  const droneItem = allItems.find(i => i.slug === DRONE_SLUG);
  if (!droneItem) {
    console.error('  FATAL: DJI Mini 3 Pro not found! Check seed data.');
    console.error('  Available:', allItems.slice(0, 10).map(i => i.slug).join(', '));
    await browser.close();
    process.exit(1);
  }
  console.log(`  Item: ${droneItem.name} (${droneItem.id})`);

  // Cleanup existing active auctions on this item
  const listingsResp = await apiCall(page, 'GET', `/api/v1/listings?item_id=${droneItem.id}`);
  for (const l of (listingsResp.data || [])) {
    if (l.listing_type === 'auction' && l.status === 'active') {
      console.log(`  Ending stale auction ${l.id}`);
      await apiCall(page, 'POST', `/api/v1/bids/${l.id}/end`);
    }
  }
  console.log('  Pre-flight: done\n');

  // ============================================================
  // SCENE 1: OBS CHECK (RED)
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">THE AUCTION | BorrowHood | DJI Mini 3 Pro</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ── CREATE AUCTION NOW (timer starts!) ─────────────────────
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });

  const auctionEnd = new Date(Date.now() + AUCTION_DURATION_SEC * 1000).toISOString();
  console.log(`  AUCTION CREATED (${AUCTION_DURATION_SEC}s countdown started)`);
  console.log(`  Ends at: ${auctionEnd}`);
  await demoLogin(page, 'jake');
  const createResp = await apiCall(page, 'POST', '/api/v1/listings', {
    item_id: droneItem.id,
    listing_type: 'auction',
    currency: 'EUR',
    pickup_only: true,
    notes: 'DJI Mini 3 Pro with RC controller. 4K/60fps, 48MP photos, obstacle avoidance. Under 249g -- no licence needed in Italy. 3 batteries, carrying case, ND filters. Winner gets a free 15-min orientation flight at pickup.',
    starting_bid: 80.0,
    reserve_price: 200.0,
    bid_increment: 10.0,
    auction_end: auctionEnd,
  });
  if (createResp.status !== 201) {
    console.error(`  FATAL: ${JSON.stringify(createResp.data)}`);
    await browser.close();
    process.exit(1);
  }
  const listingId = createResp.data.id;
  console.log(`  Listing: ${listingId}\n`);

  function timeLeft() {
    const sec = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
    if (sec < 0) return '0:00';
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  // ============================================================
  // SCENE 2: INTRO CARD (AMBER) -- 6s
  // "What is this video about?"
  // ============================================================
  console.log(`  Scene 2: Intro [${timeLeft()}]`);
  await page.goto(card(
    '#B45309',
    'THE AUCTION',
    'One drone. Two bidders. One winner.',
    '<div class="badge">LIVE COUNTDOWN</div>' +
    '<div class="extra" style="margin-top:24px">' +
    'Jake puts his DJI Mini 3 Pro up for auction.<br>' +
    'Sally and Mike both want it. The bidding war begins.' +
    '</div>'
  ));
  await sleep(6000);

  // ============================================================
  // SCENE 3: CONTEXT CARD (SLATE) -- 7s
  // "Meet the drone and the owner"
  // ============================================================
  console.log(`  Scene 3: Context [${timeLeft()}]`);
  await page.goto(card(
    '#1E293B',
    'MEET THE DRONE',
    'DJI Mini 3 Pro -- Beginner Friendly',
    '<div class="extra">' +
    'Owner: <span class="hl">Jake Morrison</span> (Jake\'s Tech Bench)<br>' +
    'Condition: <span class="hl">Like New</span> | Under 249g -- <span class="check">no licence needed</span><br>' +
    '4K/60fps, obstacle avoidance, 3 batteries, carrying case<br>' +
    '<span class="warn">Free 15-min orientation flight at pickup</span><br><br>' +
    '<span class="dim">Starting bid: EUR 80 | Bid increment: EUR 10</span><br>' +
    '<span class="dim">Reserve price: EUR ??? (hidden from bidders)</span>' +
    '</div>'
  ));
  await sleep(7000);

  // ============================================================
  // SCENE 4: BROWSE PAGE -- drone with "Auction" badge -- 6s
  // ============================================================
  console.log(`  Scene 4: Browse [${timeLeft()}]`);
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  // Scroll to the drone card
  await page.evaluate((slug) => {
    const links = document.querySelectorAll('.grid a');
    for (const link of links) {
      if (link.href && link.href.includes(slug)) {
        link.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  }, DRONE_SLUG);
  await sleep(1500);
  // Highlight the Auction badge on the card
  await page.evaluate((slug) => {
    const links = document.querySelectorAll('.grid a');
    for (const link of links) {
      if (link.href && link.href.includes(slug)) {
        const badge = link.querySelector('span');
        if (badge) {
          badge.style.outline = '3px solid #DC2626';
          badge.style.outlineOffset = '2px';
          badge.style.borderRadius = '999px';
        }
        break;
      }
    }
  }, DRONE_SLUG);
  await sleep(3000);

  // ============================================================
  // SCENE 5: ITEM DETAIL (Jake) -- auction panel + countdown
  // ============================================================
  console.log(`  Scene 5: Item detail [${timeLeft()}]`);
  await page.goto(itemUrl, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  await scrollToAuction(page);
  await sleep(4000);

  // ============================================================
  // SCENE 6: EXPLAINER -- "WHAT IS AN AUCTION?" (6s)
  // The rules, plain and simple. Even a 5-year-old gets it.
  // ============================================================
  console.log(`  Scene 6: Explainer - What is an auction? [${timeLeft()}]`);
  await page.goto(card(
    '#1E293B',
    'WHAT IS AN AUCTION?',
    'You put something up for sale.',
    '<div class="extra">' +
    'People bid money. Each bid must be <span class="hl">higher</span> than the last.<br>' +
    'A <span class="hl">countdown timer</span> ticks down.<br>' +
    'When the timer hits zero, the <span class="hl">highest bidder wins</span>.<br><br>' +
    '<span class="dim">That is it. That is the whole thing.</span>' +
    '</div>'
  ));
  await sleep(6000);

  // ============================================================
  // SCENE 7: SALLY BIDS EUR 100
  // First bid -- the opening move.
  // ============================================================
  console.log(`  Scene 7: Sally bids 80 [${timeLeft()}]`);
  // Navigate to BASE first (we were on a data: URL)
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, 'SALLY THOMPSON', 'First bid on the drone',
    'She wants a drone for aerial food photography.<br>' +
    'Under 249g, no licence needed -- perfect for a beginner.<br>' +
    'Her opening move: <span style="color:#FCD34D;font-weight:700">EUR 80</span> (the starting bid).');

  await switchUser(page, 'sally', itemUrl);
  await scrollToAuction(page);
  await sleep(1000);
  await placeBidVisual(page, 80);
  console.log(`  Sally bid EUR 80 placed [${timeLeft()}]`);

  // ============================================================
  // SCENE 8: EXPLAINER -- "FIRST BID IN" (6s)
  // What just happened? Sally is winning. But...
  // ============================================================
  console.log(`  Scene 8: Explainer - First bid in [${timeLeft()}]`);
  await showOverlay(page, 'FIRST BID IN',
    'Sally is the current high bidder at EUR 80.',
    'She sees <span style="color:#34D399;font-weight:700">"You are winning!"</span> in the panel.<br><br>' +
    'But notice: the reserve price is <span style="color:#FBBF24;font-weight:700">NOT met</span>.<br>' +
    'That means even if nobody else bids, the owner<br>' +
    'does not have to sell. The price is too low.',
    '#1E293B', 6000);

  // ============================================================
  // SCENE 9: MIKE OUTBIDS AT EUR 180
  // Competition arrives.
  // ============================================================
  console.log(`  Scene 9: Mike bids 150 [${timeLeft()}]`);
  await showOverlay(page, 'MIKE KENEL', 'He wants the drone too.',
    'Mike runs a garage and needs aerial shots for roof inspections.<br>' +
    'His bid: <span style="color:#FCD34D;font-weight:700">EUR 150</span>. Outbidding Sally.');

  await switchUser(page, 'mike', itemUrl);
  await scrollToAuction(page);
  await sleep(1000);
  await placeBidVisual(page, 150);
  console.log(`  Mike bid EUR 150 placed [${timeLeft()}]`);

  // ============================================================
  // SCENE 10: EXPLAINER -- "OUTBID!" (6s)
  // Sally just lost the lead. Explain what outbid means.
  // ============================================================
  console.log(`  Scene 10: Explainer - Outbid [${timeLeft()}]`);
  await showOverlay(page, 'OUTBID!',
    'Mike just bid EUR 150. Sally is no longer winning.',
    'Sally got a <span style="color:#FBBF24;font-weight:700">notification</span>: "You have been outbid."<br>' +
    'She can bid again, or walk away.<br><br>' +
    'Reserve price is <span style="color:#FBBF24;font-weight:700">STILL not met</span>.<br>' +
    '<span style="opacity:0.5">EUR 150 is close, but not enough.</span>',
    '#1E293B', 6000);

  // ============================================================
  // SCENE 11: EXPLAINER -- "THE RESERVE PRICE" (7s)
  // This is the safety net. Explain it like you are 5.
  // ============================================================
  console.log(`  Scene 11: Explainer - Reserve price [${timeLeft()}]`);
  await page.goto(card(
    '#1E293B',
    'THE RESERVE PRICE',
    'A secret minimum price set by the owner.',
    '<div class="extra">' +
    'Jake set a reserve of <span class="hl">EUR 200</span> (hidden from bidders).<br><br>' +
    'If the highest bid is <span class="warn">below EUR 200</span>, Jake does not have to sell.<br>' +
    'If the highest bid is <span class="check">at or above EUR 200</span>, the sale is guaranteed.<br><br>' +
    'Think of it as a <span class="hl">safety net</span> for the owner.<br>' +
    '<span class="dim">"I will sell, but only if the price is right."</span>' +
    '</div>'
  ));
  await sleep(7000);

  // ============================================================
  // SCENE 12: SALLY BIDS EUR 300 (RESERVE MET!)
  // All in. No more playing around.
  // ============================================================
  console.log(`  Scene 12: Sally bids 250 [${timeLeft()}]`);
  // Navigate to BASE first (we were on a data: URL)
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, 'SALLY THOMPSON', 'She is not giving up.',
    'Sally comes back with <span style="color:#FCD34D;font-weight:700">EUR 250</span>.<br>' +
    'That is above the reserve price.<br>' +
    'All in. Winner takes all.');

  await switchUser(page, 'sally', itemUrl);
  await scrollToAuction(page);
  await sleep(1000);
  await placeBidVisual(page, 250);
  console.log(`  Sally bid EUR 250 placed [${timeLeft()}]`);

  // Hold on the "Reserve Met" indicator
  await page.evaluate(() => {
    const panel = document.querySelector('.border-amber-300');
    if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  await sleep(3000);

  // ============================================================
  // SCENE 13: EXPLAINER -- "RESERVE MET!" (6s)
  // The sale is now real. Explain the green badge.
  // ============================================================
  console.log(`  Scene 13: Explainer - Reserve met [${timeLeft()}]`);
  await showOverlay(page, 'RESERVE MET!',
    'Sally bid EUR 250. The reserve was EUR 200.',
    '<span style="color:#34D399;font-weight:700">The panel now shows a green badge: "Reserve Met"</span><br><br>' +
    'This means the sale is <span style="color:#34D399;font-weight:700">guaranteed</span>.<br>' +
    'When the timer hits zero, the highest bidder<br>' +
    'WILL get the drone. No take-backs.',
    '#1E293B', 6000);

  // ============================================================
  // SCENE 14: EXPLAINER -- "ANTI-SNIPE PROTECTION" (7s)
  // Last-second bid protection. Important auction feature.
  // ============================================================
  console.log(`  Scene 14: Explainer - Anti-snipe [${timeLeft()}]`);
  await page.goto(card(
    '#1E293B',
    'ANTI-SNIPE',
    'No sneaky last-second bids.',
    '<div class="extra">' +
    'What if someone bids in the <span class="warn">last 60 seconds</span>?<br><br>' +
    'The system adds <span class="hl">2 more minutes</span> to the timer.<br>' +
    'This gives everyone a fair chance to respond.<br><br>' +
    'No more "sniping" -- placing a bid so late<br>' +
    'that nobody else can react.<br><br>' +
    '<span class="dim">Fair play. Built into the system.</span>' +
    '</div>'
  ));
  await sleep(7000);

  // ============================================================
  // SCENE 15: PIETRO WATCHES THE FINAL COUNTDOWN
  // Switch to the owner. The clock is ticking.
  // ============================================================
  console.log(`  Scene 15: Jake watches countdown [${timeLeft()}]`);
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, 'JAKE MORRISON', 'Watching the auction close.',
    '3 bids placed. Reserve met. EUR 250 on the table.<br>' +
    'The clock is ticking down...');

  await switchUser(page, 'jake', itemUrl);
  await scrollToAuction(page);

  // ============================================================
  // SCENE 16: EXPLAINER -- "FINAL MOMENTS" (overlay, 5s)
  // What happens when the timer hits zero?
  // ============================================================
  const remaining16 = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
  console.log(`  Scene 16: Final moments explainer [${timeLeft()}] (${remaining16}s until zero)`);

  // If there is still a lot of time, show the explainer card first
  if (remaining16 > 25) {
    await showOverlay(page, 'WHAT HAPPENS NEXT?',
      'When the timer hits zero...',
      'The auction <span style="color:#FBBF24;font-weight:700">locks</span>. No more bids.<br>' +
      'The owner clicks "End Auction" to make it official.<br>' +
      'The system marks the highest bid as <span style="color:#34D399;font-weight:700">WON</span>.<br>' +
      'The winner gets a notification: "You won the auction!"',
      '#1E293B', 5000);

    // Return to item page to watch the last seconds
    await page.goto(itemUrl, { waitUntil: 'networkidle2', timeout: 15000 });
    await setZoom(page);
    await sleep(500);
    await scrollToAuction(page);
  }

  // ── Watch the countdown tick to zero ───────────────────────
  const remaining = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
  console.log(`  Watching countdown: ${remaining}s remaining`);

  if (remaining > 0) {
    const checkInterval = setInterval(() => {
      const left = Math.round((new Date(auctionEnd) - Date.now()) / 1000);
      if (left <= 20 && left > 0) {
        process.stdout.write(`  ${left}... `);
      }
      if (left <= 0) {
        clearInterval(checkInterval);
        console.log('\n  TIMER HIT ZERO!');
      }
    }, 1000);

    await sleep((remaining + 3) * 1000);
  }

  // The Alpine.js panel should now show "Auction ended"
  await sleep(3000);
  console.log(`  Auction ended visible on screen`);

  // ============================================================
  // SCENE 17: JAKE ENDS AUCTION -- WINNER ANNOUNCED
  // ============================================================
  console.log('  Scene 17: End auction + winner');

  // End via API (Jake is logged in, on BASE origin)
  const endResp = await apiCall(page, 'POST', `/api/v1/bids/${listingId}/end`);
  console.log(`  End: winner=${endResp.data?.winner_id ? 'YES' : 'NO'}, amount=EUR ${endResp.data?.winning_amount}, reserve=${endResp.data?.reserve_met}`);

  // Show winner announcement overlay (the UI removes the auction panel after
  // ending, so the viewer needs to see the result as an overlay card)
  await showOverlay(page, 'SALLY WINS!',
    'DJI Mini 3 Pro -- EUR 250',
    '3 bids placed. Reserve met. Auction closed.<br><br>' +
    '<span style="color:#34D399;font-weight:700">Sally Thompson is the winner.</span><br>' +
    'She picks up the drone and gets her<br>' +
    'free 15-min orientation flight from Jake.<br><br>' +
    '<span style="opacity:0.5">Every neighborhood has a garage like his.</span>',
    '#059669', 8000);

  // ============================================================
  // SCENE 18: FEATURE RECAP (AMBER) -- 10s
  // Everything the viewer just learned, as a checklist.
  // ============================================================
  await page.goto(card(
    '#B45309',
    'THE AUCTION',
    'Feature Complete',
    '<div class="extra" style="text-align:left; max-width:1100px; margin:0 auto; font-size:30px; line-height:1.7">' +
    '<span class="check">&#x2713;</span> <span class="hl">Live bidding</span> -- place bids in real time<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Starting bid</span> -- minimum price to enter<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Bid increment</span> -- must bid at least EUR 10 more each time<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Reserve price</span> -- secret minimum, protects the owner<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Live countdown</span> -- timer ticks in real time<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Outbid notifications</span> -- know instantly when someone beats you<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Anti-snipe</span> -- last-minute bids extend the timer<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Winner announced</span> -- auction ends, highest bidder wins<br>' +
    '<br>' +
    '<span style="opacity:0.5">Jake listed the drone. Sally and Mike bid.</span><br>' +
    '<span style="opacity:0.5">Sally won at EUR 250. Every feature worked.</span>' +
    '</div>'
  ));
  await sleep(10000);

  // ============================================================
  // CUT
  // ============================================================
  await page.goto(card('#1E293B', 'CUT', 'Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
