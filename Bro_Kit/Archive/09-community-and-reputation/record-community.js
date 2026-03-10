#!/usr/bin/env node
/**
 * BORROWHOOD -- Community & Reputation (v1)
 *
 * Beyond the rental. Reviews, badges, member discovery, favorites, helpboard.
 *
 * Part 1: REVIEWS       -- Mike reviews Sally after a completed rental
 * Part 2: BADGES        -- Badge check, notifications, profile stats
 * Part 3: MEMBERS       -- Members directory, filter, search, favorite Maria
 * Part 4: HELPBOARD     -- Sally posts a need, Maria replies, resolved
 *
 * PRE-RECORDING -- clean stale data from previous takes:
 *   ssh root@46.62.138.218 "docker exec postgres psql -U helix_user -d borrowhood -c \"
 *     DELETE FROM bh_review WHERE reviewer_id = (SELECT id FROM bh_user WHERE slug='mikes-garage')
 *       AND reviewee_id = (SELECT id FROM bh_user WHERE slug='sallys-kitchen');
 *     DELETE FROM bh_user_favorite WHERE user_id = (SELECT id FROM bh_user WHERE slug='sallys-kitchen');
 *     DELETE FROM bh_help_reply WHERE post_id IN
 *       (SELECT id FROM bh_help_post WHERE author_id = (SELECT id FROM bh_user WHERE slug='sallys-kitchen')
 *        AND title LIKE '%wall anchors%');
 *     DELETE FROM bh_help_post WHERE author_id = (SELECT id FROM bh_user WHERE slug='sallys-kitchen')
 *       AND title LIKE '%wall anchors%';
 *     UPDATE bh_notification SET read=true WHERE user_id = (SELECT id FROM bh_user WHERE slug='sallys-kitchen');
 *     UPDATE bh_notification SET read=true WHERE user_id = (SELECT id FROM bh_user WHERE slug='mikes-garage');
 *   \""
 *
 * Usage: node record-community.js [base_url]
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

// Mobile-optimized card: 128px heading, 56px subtitle, 40px extra
function card(bg, title, subtitle, extra = '') {
  return `data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html><html><head>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:${bg};display:flex;flex-direction:column;align-items:center;
    justify-content:center;height:100vh;width:100vw;
    font-family:'Segoe UI',Arial,sans-serif;color:white;text-align:center;
    padding:40px}
  h1{font-size:128px;font-weight:800;margin-bottom:24px;text-shadow:2px 2px 8px rgba(0,0,0,0.3)}
  h2{font-size:56px;font-weight:400;opacity:0.9;margin-bottom:20px}
  .extra{font-size:40px;opacity:0.7;margin-top:16px;line-height:1.5;max-width:1400px}
</style></head><body>
  <h1>${title}</h1><h2>${subtitle}</h2>${extra}
</body></html>`)}`;
}

function storyCard(bg, who, action, detail) {
  return card(bg, who, action, `<div class="extra">${detail}</div>`);
}


// ═══════════════════════════════════════════════════════════════
//  CLICK INDICATORS  (mobile-optimized: 60px ring, 5px border)
// ═══════════════════════════════════════════════════════════════

async function injectClickStyle(page) {
  await page.evaluate(() => {
    if (document.getElementById('bh-click-css')) return;
    const s = document.createElement('style');
    s.id = 'bh-click-css';
    s.textContent = `
      @keyframes bh-ring { 0%{transform:translate(-50%,-50%) scale(0.5);opacity:1} 100%{transform:translate(-50%,-50%) scale(2.5);opacity:0} }
      .bh-click-ring{position:fixed;z-index:99999;width:60px;height:60px;border-radius:50%;
        border:5px solid #DC2626;box-shadow:0 0 20px rgba(220,38,38,0.4);
        pointer-events:none;animation:bh-ring .6s ease-out forwards}
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

async function findLink(page, text) {
  const links = await page.$$('a');
  for (const a of links) {
    const info = await page.evaluate(el => {
      if (el.offsetWidth === 0 && el.offsetHeight === 0) return null;
      if (window.getComputedStyle(el).display === 'none') return null;
      return el.textContent.trim();
    }, a);
    if (info && info.includes(text)) return a;
  }
  return null;
}

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
  await sleep(2000);  // Mobile-optimized: extra pause after click
  return true;
}

async function clickButton(page, text) {
  await injectClickStyle(page);
  const btn = await findButton(page, text);
  if (!btn) { console.log(`    Button not found: "${text}"`); return false; }
  return clickEl(page, btn, text);
}

async function clickLink(page, text) {
  await injectClickStyle(page);
  const a = await findLink(page, text);
  if (!a) { console.log(`    Link not found: "${text}"`); return false; }
  return clickEl(page, a, text);
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
//  PAGE HELPERS
// ═══════════════════════════════════════════════════════════════

async function waitForImages(page) {
  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img =>
      img.complete ? Promise.resolve()
        : new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); })
    )
  ));
}

/** Set browser zoom for UI pages (mobile-optimized). */
async function setZoom(page, factor = 1.5) {
  await page.evaluate((z) => { document.body.style.zoom = String(z); }, factor);
}

/** Show a DOM overlay with key-value info (for stats, badges, etc). */
async function showOverlay(page, title, lines, holdMs = 4000) {
  await page.evaluate((t, ls) => {
    const old = document.getElementById('bh-overlay');
    if (old) old.remove();
    const div = document.createElement('div');
    div.id = 'bh-overlay';
    div.style.cssText = `position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
      z-index:99999;background:rgba(0,0,0,0.92);color:white;padding:48px 64px;
      border-radius:16px;font-family:'Segoe UI',sans-serif;text-align:left;
      min-width:600px;max-width:900px;box-shadow:0 25px 50px rgba(0,0,0,0.5);
      border:1px solid rgba(255,255,255,0.1)`;
    div.innerHTML = `<h2 style="font-size:36px;font-weight:800;margin-bottom:24px;
      color:#fbbf24;letter-spacing:1px">${t}</h2>` +
      ls.map(l => `<div style="font-size:24px;margin:12px 0;line-height:1.5;
        color:rgba(255,255,255,0.9)">${l}</div>`).join('');
    document.body.appendChild(div);
  }, title, lines);
  await sleep(holdMs);
  await page.evaluate(() => {
    const el = document.getElementById('bh-overlay');
    if (el) el.remove();
  });
}

/** Show a grid overlay of badges. */
async function showBadgeGrid(page, badges, holdMs = 6000) {
  await page.evaluate((items) => {
    const old = document.getElementById('bh-overlay');
    if (old) old.remove();
    const ICONS = {
      FIRST_LISTING:'📦', FIRST_RENTAL:'🤝', FIRST_REVIEW:'⭐',
      FIVE_STAR:'✨', SUPER_LENDER:'🎁', TRUSTED_RENTER:'🛡️',
      COMMUNITY_VOICE:'📣', MULTILINGUAL:'🌐', SKILL_MASTER:'🔧',
      AUCTION_WINNER:'🏆', EARLY_ADOPTER:'🚀', PERFECT_RECORD:'👑',
      NEIGHBORHOOD_HERO:'❤️', WORKSHOP_PRO:'🏗️', GENEROUS_NEIGHBOR:'🎁'
    };
    const div = document.createElement('div');
    div.id = 'bh-overlay';
    div.style.cssText = `position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
      z-index:99999;background:rgba(0,0,0,0.95);color:white;padding:40px 48px;
      border-radius:16px;font-family:'Segoe UI',sans-serif;
      width:1200px;max-height:900px;overflow:auto;
      box-shadow:0 25px 50px rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.1)`;
    div.innerHTML = `<h2 style="font-size:32px;font-weight:800;margin-bottom:24px;
      color:#34d399;text-align:center;letter-spacing:2px">BADGE CATALOG</h2>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">` +
      items.map(b => `<div style="background:rgba(255,255,255,0.06);border-radius:12px;
        padding:16px;border:1px solid rgba(255,255,255,0.08)">
        <div style="font-size:28px;margin-bottom:6px">${ICONS[b.badge_code] || '🏅'}</div>
        <div style="font-size:18px;font-weight:700;color:white">${b.name}</div>
        <div style="font-size:14px;color:rgba(255,255,255,0.5);margin-top:4px">${b.description}</div>
      </div>`).join('') + '</div>';
    document.body.appendChild(div);
  }, badges);
  await sleep(holdMs);
  await page.evaluate(() => {
    const el = document.getElementById('bh-overlay');
    if (el) el.remove();
  });
}

async function showDashboard(page, tabText, waitMs = 3000) {
  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await injectClickStyle(page);
  await sleep(1500);
  if (tabText) {
    await clickButton(page, tabText);
  }
  await sleep(waitMs);
}

async function smoothScroll(page, pixels = 400) {
  await page.evaluate((px) => {
    window.scrollBy({ top: px, behavior: 'smooth' });
  }, pixels);
  await sleep(1500);
}


// ═══════════════════════════════════════════════════════════════
//  MAIN RECORDING
// ═══════════════════════════════════════════════════════════════

(async () => {
  console.log(`\n  BORROWHOOD -- Community & Reputation v1`);
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

  // Runtime IDs
  let sallyId = null;
  let mariaId = null;
  let rentalIdForReview = null;
  let helpPostId = null;


  // ──────────────────────────────────────────────────────────
  //  SCENE 1 : OBS CHECK
  // ──────────────────────────────────────────────────────────
  await page.goto(card('#DC2626','OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">COMMUNITY &amp; REPUTATION v1 | BorrowHood</div>'));
  await waitForEnter('OBS is recording and showing this RED screen?');


  // ──────────────────────────────────────────────────────────
  //  SCENE 2 : INTRO
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 2: Intro');
  await page.goto(card('#1E293B','BEYOND THE RENTAL',
    'Reviews. Badges. Neighbors. Help.',
    '<div class="extra">' +
    'A rental is a transaction.<br>' +
    'A review is a conversation.<br>' +
    'A badge is a reputation.<br>' +
    'A helpboard post is a hand raised.<br><br>' +
    'This is where BorrowHood becomes a neighborhood.</div>'));
  await sleep(10000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 3 : CONTEXT -- Where We Left Off
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 3: Context card');
  await page.goto(storyCard('#D97706','WHERE WE LEFT OFF',
    "Sally rented Mike's drill. The rental is complete.",
    "Sally already left Mike a 5-star review.<br>" +
    "But Mike hasn't reviewed Sally yet.<br>" +
    "He opens BorrowHood to say thanks."));
  await sleep(6000);


  // ══════════════════════════════════════════════════════════
  //  PART 1 : REVIEWS (Amber #D97706)
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 4 : Mike logs in, views Sally's workshop
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 4: Mike logs in, views Sally\'s workshop');
  await kcLogin(page, 'mike');

  // Navigate to Sally's workshop page
  await page.goto(`${BASE}/workshop/sallys-kitchen?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await injectClickStyle(page);
  await sleep(3000);

  // Scroll down to see reviews section
  await smoothScroll(page, 500);
  await sleep(3000);

  // Extract Sally's user ID from the page for later use
  sallyId = await page.evaluate(() => {
    for (const el of document.querySelectorAll('[x-data]')) {
      const attr = el.getAttribute('x-data') || '';
      const m = attr.match(/'([0-9a-f-]{36})'/);
      if (m) return m[1];
    }
    return null;
  });
  console.log(`    Sally's user ID (from page): ${sallyId || 'not found'}`);


  // ──────────────────────────────────────────────────────────
  //  SCENE 5 : Mike leaves a review
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 5: Mike leaves a review');
  await page.goto(storyCard('#D97706','MIKE SAYS THANKS',
    'Sally returned the drill in perfect condition.',
    'Time to leave a review.'));
  await sleep(5000);

  await ensureOnSite(page);

  // Find a completed rental where Mike is the owner and Sally is the renter
  const rentals = await apiCallStrict(page, 'GET', '/api/v1/rentals?status=completed&limit=20');
  console.log(`    Found ${Array.isArray(rentals) ? rentals.length : rentals?.items?.length || 0} completed rentals`);

  const rentalList = Array.isArray(rentals) ? rentals : (rentals?.items || []);
  let targetRental = null;
  for (const r of rentalList) {
    // Look for rental where Mike owns the item
    if (r.renter_slug === 'sallys-kitchen' || r.renter_display_name?.includes('Sally')) {
      targetRental = r;
      break;
    }
  }

  if (!targetRental && rentalList.length > 0) {
    targetRental = rentalList[0]; // Fallback: use any completed rental
    console.log(`    Using fallback rental: ${targetRental.id}`);
  }

  if (targetRental) {
    rentalIdForReview = targetRental.id;
    // Get Sally's ID from the rental if we didn't get it from the page
    if (!sallyId) {
      sallyId = targetRental.renter_id;
    }
    console.log(`    Rental for review: ${rentalIdForReview}`);
    console.log(`    Sally ID: ${sallyId}`);

    // Create the review
    const review = await apiCall(page, 'POST', '/api/v1/reviews', {
      rental_id: rentalIdForReview,
      reviewee_id: sallyId,
      rating: 5,
      title: 'Returned in perfect condition',
      body: 'Sally is the kind of neighbor you want. Picked up on time, returned the drill clean and fully charged. Would lend to her any day.',
      skill_name: 'Tool care',
      skill_rating: 5,
    });

    if (review && !review.error) {
      console.log(`    Review created: ${review.id}`);
    } else {
      console.log('    Review creation failed (may already exist), continuing...');
    }
  } else {
    console.log('    WARNING: No completed rental found for review');
  }

  // Show Sally's workshop with the new review
  await page.goto(`${BASE}/workshop/sallys-kitchen?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await sleep(2000);
  await smoothScroll(page, 500);
  await sleep(3000);

  // Fetch and show review summary
  if (sallyId) {
    const summary = await apiCall(page, 'GET', `/api/v1/reviews/summary/${sallyId}`);
    if (summary && !summary.error) {
      await showOverlay(page, 'REVIEW SUMMARY', [
        `Reviews: ${summary.count}`,
        `Average: ${'⭐'.repeat(Math.round(summary.average || 0))} ${(summary.average || 0).toFixed(1)}`,
        `Weighted: ${(summary.weighted_average || 0).toFixed(1)} (by reviewer tier)`,
      ], 4000);
    }
  }


  // ══════════════════════════════════════════════════════════
  //  PART 2 : BADGES & NOTIFICATIONS (Emerald #059669)
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 6 : Mike earns a badge
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 6: Badge check -- Mike');
  await page.goto(storyCard('#059669','REPUTATION GROWS',
    'Every review earns points. Points unlock badges.',
    "Let's check if Mike earned anything new."));
  await sleep(5000);

  await ensureOnSite(page);

  // Trigger badge check for Mike
  const mikeNewBadges = await apiCall(page, 'POST', '/api/v1/badges/check');
  if (mikeNewBadges && mikeNewBadges.new_badges && mikeNewBadges.new_badges.length > 0) {
    console.log(`    Mike earned ${mikeNewBadges.new_badges.length} new badge(s)!`);
    const badgeNames = mikeNewBadges.new_badges.map(b => `🏅 ${b.name}`);
    await showOverlay(page, 'NEW BADGE EARNED!', badgeNames, 4000);
  } else {
    console.log('    No new badges for Mike (may already have them)');
  }

  // Show Mike's profile with badges
  await page.goto(`${BASE}/profile?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await sleep(2000);
  await smoothScroll(page, 300);
  await sleep(4000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 7 : Switch to Sally -- notifications
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 7: Sally notifications');
  await kcLogout(page);

  await page.goto(storyCard('#059669','SALLY GETS A NOTIFICATION',
    'Mike just reviewed her. The system knows.',
    'She opens BorrowHood and sees the bell.'));
  await sleep(5000);

  await kcLogin(page, 'sally');

  // Navigate to dashboard
  await page.goto(`${BASE}/dashboard?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await injectClickStyle(page);
  await sleep(2000);

  // Check notification summary
  const notifSummary = await apiCall(page, 'GET', '/api/v1/notifications/summary');
  console.log(`    Notifications: ${notifSummary?.unread || 0} unread of ${notifSummary?.total || 0}`);

  // Try to click the notification bell in the UI
  const bellBtn = await page.$('button[x-ref="notifBtn"], [x-data*="notification"] button');
  if (bellBtn) {
    await clickEl(page, bellBtn, 'Notification bell');
    await sleep(2000);
  }

  // Fetch and display notifications via overlay
  const notifs = await apiCall(page, 'GET', '/api/v1/notifications?limit=5');
  if (notifs && !notifs.error) {
    const notifList = Array.isArray(notifs) ? notifs : (notifs?.items || []);
    if (notifList.length > 0) {
      const lines = notifList.slice(0, 5).map(n =>
        `${n.read ? '○' : '●'} ${n.title || n.notification_type}`
      );
      await showOverlay(page, `NOTIFICATIONS (${notifSummary?.unread || 0} unread)`, lines, 5000);

      // Mark the first unread notification as read
      const unread = notifList.find(n => !n.read);
      if (unread) {
        await apiCall(page, 'PATCH', `/api/v1/notifications/${unread.id}/read`);
      }
    }
  }


  // ──────────────────────────────────────────────────────────
  //  SCENE 8 : Sally's profile -- badges growing
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 8: Sally\'s profile + badges');

  // Trigger badge check for Sally
  await ensureOnSite(page);
  const sallyNewBadges = await apiCall(page, 'POST', '/api/v1/badges/check');
  if (sallyNewBadges && sallyNewBadges.new_badges && sallyNewBadges.new_badges.length > 0) {
    console.log(`    Sally earned ${sallyNewBadges.new_badges.length} new badge(s)!`);
    const badgeNames = sallyNewBadges.new_badges.map(b => `🏅 ${b.name}`);
    await showOverlay(page, 'NEW BADGES EARNED!', badgeNames, 4000);
  }

  // Show Sally's profile
  await page.goto(`${BASE}/profile?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(4000);


  // ══════════════════════════════════════════════════════════
  //  PART 3 : MEMBERS & FAVORITES (Indigo #4338CA)
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 9 : Transition to Members
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 9: Transition to Members');
  await page.goto(storyCard('#4338CA','WHO ELSE IS OUT THERE?',
    'Sally wonders who else is in the neighborhood.',
    'BorrowHood is not just Sally and Mike.<br>' +
    "There's a whole community. Let's meet them."));
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 10 : Members directory -- browse & filter
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 10: Members directory');
  await page.goto(`${BASE}/members?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await injectClickStyle(page);
  await sleep(3000);

  // Slow scroll to show member cards
  await smoothScroll(page, 300);
  await sleep(3000);
  await smoothScroll(page, -300); // scroll back up
  await sleep(1000);

  // Try to click badge tier filter
  const badgeTierSelect = await page.$('select[name="badge_tier"]');
  if (badgeTierSelect) {
    await clickEl(page, badgeTierSelect, 'Badge tier filter');
    await page.select('select[name="badge_tier"]', 'trusted');
    await sleep(2000);

    // Submit the filter form (click Apply or let it auto-submit)
    const applyBtn = await findButton(page, 'Apply');
    if (applyBtn) {
      await clickEl(page, applyBtn, 'Apply filter');
    } else {
      // Try form submit
      await page.evaluate(() => {
        const form = document.querySelector('form');
        if (form) form.submit();
      });
    }
    await sleep(3000);

    // Clear the filter
    const clearBtn = await findButton(page, 'Clear');
    if (clearBtn) {
      await clickEl(page, clearBtn, 'Clear filters');
      await sleep(2000);
    }
  }

  // Sort by badge tier
  const sortSelect = await page.$('select[name="sort"]');
  if (sortSelect) {
    await clickEl(page, sortSelect, 'Sort dropdown');
    await page.select('select[name="sort"]', 'badge_tier');
    await sleep(1000);
    const applyBtn2 = await findButton(page, 'Apply');
    if (applyBtn2) {
      await clickEl(page, applyBtn2, 'Apply sort');
    }
    await sleep(3000);
  }

  // Search for Maria
  const searchInput = await page.$('input[name="q"]');
  if (searchInput) {
    await clickEl(page, searchInput, 'Search box');
    await page.type('input[name="q"]', 'Maria', { delay: 60 });
    await sleep(500);
    // Submit search
    await page.keyboard.press('Enter');
    await sleep(3000);
  }

  // Pause to show Maria's card
  await sleep(2000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 11 : Sally favorites Maria
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 11: Sally favorites Maria');

  // Get Maria's user ID via API
  const mariaSearch = await apiCall(page, 'GET', '/api/v1/users?q=Maria&limit=1');
  const mariaList = mariaSearch?.items || (Array.isArray(mariaSearch) ? mariaSearch : []);
  if (mariaList.length > 0) {
    mariaId = mariaList[0].id;
    console.log(`    Maria's ID: ${mariaId}`);
  }

  // Try to click the heart button on Maria's card in the UI
  const heartBtn = await page.$('button[title*="favorite"], button[aria-label*="favorite"]');
  if (heartBtn) {
    await clickEl(page, heartBtn, 'Favorite heart');
  } else if (mariaId) {
    // Fallback: favorite via API
    console.log('    Heart button not found, using API...');
    const favResult = await apiCall(page, 'POST', `/api/v1/users/${mariaId}/favorite`, {
      note: 'Great neighbor with garden tools!'
    });
    if (favResult && !favResult.error) {
      console.log('    Favorited Maria via API');
    }
  }

  await showOverlay(page, 'FAVORITED', [
    "Sally saved Maria to her favorites.",
    "She can find her anytime from her profile.",
  ], 3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 12 : Sally visits Maria's workshop
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 12: Sally visits Maria\'s workshop');
  await page.goto(`${BASE}/workshop/marias-garden?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await injectClickStyle(page);
  await sleep(3000);

  // Scroll to see items, skills, reviews
  await smoothScroll(page, 400);
  await sleep(3000);
  await smoothScroll(page, 300);
  await sleep(3000);


  // ══════════════════════════════════════════════════════════
  //  PART 4 : HELPBOARD (Purple #7C3AED)
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 13 : Transition to Helpboard
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 13: Transition to Helpboard');
  await page.goto(storyCard('#7C3AED','THE HELPBOARD',
    'Not everything is about renting.',
    'Sometimes you just need a hand.<br>' +
    'The Helpboard is where neighbors help neighbors.'));
  await sleep(5000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 14 : Helpboard -- existing posts
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 14: Helpboard overview');
  await page.goto(`${BASE}/helpboard?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await injectClickStyle(page);
  await sleep(3000);

  // Show summary cards at top
  await sleep(2000);

  // Scroll through existing posts
  await smoothScroll(page, 400);
  await sleep(3000);
  await smoothScroll(page, -400);
  await sleep(1000);

  // Click "Needs" type pill
  const needsBtn = await findButton(page, 'Needs');
  if (needsBtn) {
    await clickEl(page, needsBtn, 'Needs filter');
    await sleep(2000);
  }

  // Click "Offers" pill
  const offersBtn = await findButton(page, 'Offers');
  if (offersBtn) {
    await clickEl(page, offersBtn, 'Offers filter');
    await sleep(2000);
  }

  // Click "All" to reset
  const allBtn = await findButton(page, 'All');
  if (allBtn) {
    await clickEl(page, allBtn, 'All filter');
    await sleep(1000);
  }

  // Sort by urgent first
  const helpSortSelect = await page.$('select[x-model="filter.sort"]');
  if (helpSortSelect) {
    await clickEl(page, helpSortSelect, 'Sort dropdown');
    await page.select('select[x-model="filter.sort"]', 'urgent_first');
    await sleep(3000);
  }


  // ──────────────────────────────────────────────────────────
  //  SCENE 15 : Sally creates a helpboard post
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 15: Sally creates a helpboard post');
  await page.goto(storyCard('#7C3AED','SALLY NEEDS HELP',
    'She needs to hang shelves on plaster walls.',
    "Toggle bolts? Molly bolts?<br>" +
    "She's not sure. She asks the neighborhood."));
  await sleep(5000);

  // Navigate back to helpboard
  await page.goto(`${BASE}/helpboard?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await injectClickStyle(page);
  await sleep(2000);

  // Click "+ New Post" or "Create Post" button
  let createBtn = await findButton(page, 'New Post');
  if (!createBtn) createBtn = await findButton(page, 'Create');
  if (!createBtn) createBtn = await findButton(page, 'Post');
  if (createBtn) {
    await clickEl(page, createBtn, 'Create Post');
    await sleep(1500);
  }

  // Fill the form via Alpine x-model bindings
  // Title
  const titleInput = await page.$('input[x-model="newPost.title"]');
  if (titleInput) {
    await clickEl(page, titleInput, 'Title input');
    await page.type('input[x-model="newPost.title"]',
      'Need help choosing wall anchors for plaster walls', { delay: 30 });
    await sleep(500);
  }

  // Body
  const bodyArea = await page.$('textarea[x-model="newPost.body"]');
  if (bodyArea) {
    await clickEl(page, bodyArea, 'Body textarea');
    await page.type('textarea[x-model="newPost.body"]',
      'Building floating shelves in my kitchen. The walls are old plaster and lathe. Toggle bolts? Molly bolts? Anyone dealt with this?',
      { delay: 20 });
    await sleep(500);
  }

  // Category
  const catSelect = await page.$('select[x-model="newPost.category"]');
  if (catSelect) {
    await clickEl(page, catSelect, 'Category select');
    // Try to select a reasonable category
    await page.evaluate(() => {
      const sel = document.querySelector('select[x-model="newPost.category"]');
      if (sel) {
        // Find an option containing "tool" or "power" or use first non-empty
        for (const opt of sel.options) {
          if (opt.value && (opt.value.includes('tool') || opt.value.includes('power') || opt.value.includes('home'))) {
            sel.value = opt.value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            return;
          }
        }
        // Fallback: first non-empty option
        for (const opt of sel.options) {
          if (opt.value) {
            sel.value = opt.value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            return;
          }
        }
      }
    });
    await sleep(500);
  }

  // Neighborhood
  const neighborInput = await page.$('input[x-model="newPost.neighborhood"]');
  if (neighborInput) {
    await clickEl(page, neighborInput, 'Neighborhood input');
    await page.type('input[x-model="newPost.neighborhood"]', 'Centro Storico', { delay: 40 });
    await sleep(500);
  }

  // Submit the post -- find the EXACT "Post" button inside the modal (not "+ New Post")
  const submitBtn = await page.evaluateHandle(() => {
    const btns = [...document.querySelectorAll('button')];
    // Match buttons whose trimmed text is exactly "Post" (not "New Post", "Cancel", etc.)
    return btns.find(b => {
      const text = b.textContent.trim();
      return text === 'Post' && b.offsetWidth > 0 && b.offsetHeight > 0;
    }) || null;
  });

  if (submitBtn && submitBtn.asElement()) {
    await clickEl(page, submitBtn, 'Submit post');
    await sleep(3000);
  } else {
    console.log('    Submit button not found in modal');
  }

  // Verify the post was created -- check via API
  await sleep(1000);
  const recentPosts = await apiCall(page, 'GET', '/api/v1/helpboard/posts?sort=newest&limit=3');
  const postList = recentPosts?.items || (Array.isArray(recentPosts) ? recentPosts : []);
  const uiPost = postList.find(p => p.title?.includes('wall anchors'));

  if (uiPost) {
    helpPostId = uiPost.id;
    console.log(`    Post created via UI: ${helpPostId}`);
  } else {
    // UI submit failed silently -- create via API as guaranteed fallback
    console.log('    UI submit did not create post, using API fallback...');
    const postResult = await apiCallStrict(page, 'POST', '/api/v1/helpboard/posts', {
      help_type: 'need',
      title: 'Need help choosing wall anchors for plaster walls',
      body: 'Building floating shelves in my kitchen. The walls are old plaster and lathe. Toggle bolts? Molly bolts? Anyone dealt with this?',
      category: 'power_tools',
      urgency: 'normal',
      neighborhood: 'Centro Storico',
      content_language: 'en',
    });
    helpPostId = postResult.id;
    console.log(`    Post created via API: ${helpPostId}`);
  }

  // Refresh helpboard sorted by NEWEST so the new post appears at the top
  await page.goto(`${BASE}/helpboard?lang=en&sort=newest`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await sleep(2000);

  // Set sort to "Newest" via Alpine to ensure correct rendering
  await page.evaluate(() => {
    const sel = document.querySelector('select[x-model="filter.sort"]');
    if (sel) {
      sel.value = 'newest';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 16 : Maria replies
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 16: Maria replies');
  await kcLogout(page);

  await page.goto(storyCard('#7C3AED','MARIA SEES THE POST',
    "She's dealt with plaster walls in her 100-year-old house.",
    'She knows exactly which anchors to use.'));
  await sleep(5000);

  await kcLogin(page, 'maria');

  // Navigate to helpboard sorted by newest so Sally's post is visible
  await page.goto(`${BASE}/helpboard?lang=en&sort=newest`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await injectClickStyle(page);
  await sleep(3000);

  // Reply to Sally's post via API
  if (helpPostId) {
    const replyResult = await apiCallStrict(page, 'POST',
      `/api/v1/helpboard/posts/${helpPostId}/replies`, {
        body: "Toggle bolts are the way to go for plaster! I hung my kitchen cabinets with them two years ago and they haven't budged. Get the 1/4 inch ones. I can show you how to install them if you want -- I live on Via Roma, just around the corner.",
      });
    console.log(`    Reply created: ${replyResult.id}`);
  } else {
    console.log('    WARNING: No helpPostId, cannot reply');
  }

  // Show confirmation overlay
  await showOverlay(page, 'REPLY POSTED', [
    'Maria: "Toggle bolts are the way to go for plaster!"',
    '"I can show you how -- I live on Via Roma."',
  ], 4000);

  // Reload helpboard sorted by newest to show Sally's post + updated reply count
  await page.goto(`${BASE}/helpboard?lang=en&sort=newest`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await sleep(3000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 17 : Sally marks post resolved
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 17: Sally marks post resolved');
  await kcLogout(page);

  await page.goto(storyCard('#7C3AED','PROBLEM SOLVED',
    'Toggle bolts it is.',
    'Sally marks the post as resolved.'));
  await sleep(4000);

  await kcLogin(page, 'sally');
  await ensureOnSite(page);

  // Resolve the post via API
  if (helpPostId) {
    await apiCallStrict(page, 'PATCH',
      `/api/v1/helpboard/posts/${helpPostId}/status?new_status=resolved`);
    console.log('    Post marked as resolved');
  }

  // Show helpboard with resolved badge -- sort by newest so Sally's post is visible
  await page.goto(`${BASE}/helpboard?lang=en&sort=newest`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await injectClickStyle(page);
  await sleep(4000);


  // ══════════════════════════════════════════════════════════
  //  WRAP-UP
  // ══════════════════════════════════════════════════════════


  // ──────────────────────────────────────────────────────────
  //  SCENE 18 : Badge catalog
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 18: Badge catalog');
  await ensureOnSite(page);

  const catalog = await apiCall(page, 'GET', '/api/v1/badges/catalog');
  if (catalog && !catalog.error) {
    const badgeList = Array.isArray(catalog) ? catalog : (catalog?.items || []);
    if (badgeList.length > 0) {
      await showBadgeGrid(page, badgeList, 8000);
    }
  }


  // ──────────────────────────────────────────────────────────
  //  SCENE 19 : Sally's favorites list
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 19: Sally\'s favorites');

  await page.goto(`${BASE}/profile?lang=en`,
    { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page, 1.5);
  await waitForImages(page);
  await sleep(2000);

  // Scroll down to favorites section
  await smoothScroll(page, 600);
  await sleep(4000);

  // Also show via overlay
  const favs = await apiCall(page, 'GET', '/api/v1/users/me/favorites');
  if (favs && !favs.error) {
    const favList = Array.isArray(favs) ? favs : (favs?.items || []);
    if (favList.length > 0) {
      const lines = favList.map(f =>
        `❤️ ${f.favorite_user?.display_name || f.favorite_user_id}` +
        (f.note ? ` -- "${f.note}"` : '')
      );
      await showOverlay(page, 'FAVORITE NEIGHBORS', lines, 4000);
    }
  }


  // ──────────────────────────────────────────────────────────
  //  SCENE 20 : Weighted reputation
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 20: Weighted reputation');
  await page.goto(storyCard('#D97706','WEIGHTED REPUTATION',
    'Not all reviews are equal.',
    "A Legend's review carries 10x the weight of a Newcomer's.<br>" +
    'Your reputation is earned, not gamed.'));
  await sleep(5000);

  await ensureOnSite(page);

  if (sallyId) {
    const repSummary = await apiCall(page, 'GET', `/api/v1/reviews/summary/${sallyId}`);
    if (repSummary && !repSummary.error) {
      await showOverlay(page, "SALLY'S REPUTATION", [
        `Reviews received: ${repSummary.count}`,
        `Simple average: ${(repSummary.average || 0).toFixed(1)} ⭐`,
        `Weighted average: ${(repSummary.weighted_average || 0).toFixed(1)} ⭐ (by reviewer tier)`,
        '',
        'Tier weights:',
        'Newcomer = 1x  |  Active = 2x  |  Trusted = 5x',
        'Pillar = 8x  |  Legend = 10x',
      ], 8000);
    }
  }


  // ──────────────────────────────────────────────────────────
  //  SCENE 21 : OUTRO
  // ──────────────────────────────────────────────────────────
  console.log('  Scene 21: Outro');
  await page.goto(card('#1E293B','BORROWHOOD',
    'More than a rental platform.',
    '<div class="extra" style="text-align:left;margin-top:24px;line-height:2">' +
    '✓ Reviews -- say thanks, build trust<br>' +
    '✓ Badges -- earn reputation through action<br>' +
    '✓ Members -- discover neighbors by tier and skill<br>' +
    '✓ Favorites -- save the people you trust<br>' +
    '✓ Helpboard -- ask for help, offer your skills<br>' +
    '✓ Notifications -- know when something happens<br><br>' +
    '<span style="opacity:0.6;font-style:italic">' +
    '"Every neighborhood has a garage like his."</span></div>'));
  await sleep(12000);


  // ──────────────────────────────────────────────────────────
  //  SCENE 22 : CUT
  // ──────────────────────────────────────────────────────────
  await page.goto(card('#1E293B','CUT','Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');

  await browser.close();
  console.log('\n  Done.\n');

})().catch(err => {
  console.error('\n  FATAL:', err.message);
  process.exit(1);
});
