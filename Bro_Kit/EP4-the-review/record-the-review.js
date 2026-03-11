#!/usr/bin/env node
/**
 * THE REVIEW -- Recording Script (S1 EP04)
 *
 * Picks up right where EP03 "The Scooter" left off:
 *   "What happens when a legend... fixes what everyone said was scrap?"
 *
 * Every click visible. Every login visible. Every status change on screen.
 * 3-act structure + epilogue. Know the ending before you write.
 *
 * THE ENDING: Johnny was about to trash an EUR 80 pressure washer over a
 *   50-cent gasket. Leo had a bag of them. Mike knew the fix from a photo.
 *   THE QUESTION: "What if asking for help... was the bravest thing you ever did?"
 *
 * INTRO (Scenes 1-3):
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- "THE REVIEW"
 *   3.  "Previously on BorrowHood" recap card
 *
 * ACT I -- THE FALL (Scenes 4-12):
 *   4.  Login as Johnny -- dashboard
 *   5.  Card: JOHNNY'S PROBLEM (pressure washer broken)
 *   6.  Johnny opens Browse, looks at giveaway option
 *   7.  Card: "LAST TIME HE GAVE AWAY THE BIKE FOR FREE. LEO SOLD IT FOR EUR 50."
 *   8.  Johnny opens Help Board (first time)
 *   9.  Help Board overview -- summary cards, filters
 *  10.  Johnny clicks "New Post" -- empty form
 *  11.  AI DRAFT -- Johnny types problem, AI returns title + body + EUR 80-120 value
 *  12.  Johnny edits draft, hits Post
 *
 * ACT II -- THE RESPONSE (Scenes 13-22):
 *  13.  Card: "24 HOURS LATER"
 *  14.  Login as Leo -- Help Board morning routine
 *  15.  Leo replies to Johnny's post (gasket fix)
 *  16.  Login as Mike -- posts safety OFFER on Help Board
 *  17.  Mike replies to Johnny's post (unloader valve tip)
 *  18.  Johnny edits his post with updates
 *  19.  Card: "NEXT DAY -- LEO'S BOTTEGA"
 *  20.  Johnny marks post as Resolved (Leo as helper)
 *  21.  Leo's profile -- "Helped 1 neighbor"
 *
 * ACT III -- THE REVIEWS (Scenes 22-38):
 *  22.  Card: "THE REVIEWS"
 *  23.  Login as Sofia -- dashboard, completed orders
 *  24.  Sofia opens completed order (Johnny delivered)
 *  25.  Sofia writes 5-star review of Johnny's delivery
 *  26.  Card: DELIVERY TRACKING (show timeline)
 *  27.  Login as Leo -- completed cookie order (drone)
 *  28.  Leo writes 3-star review (cookies great, drone delivery bad)
 *  29.  Sofia sees notification -- rating drops to 4.0
 *  30.  Login as Sally -- shows Sofia the review
 *  31.  Sofia responds to Leo's review (owner response + edit lock)
 *  32.  Login as Pietro -- reads reviews on item page
 *  33.  Star distribution chart shown
 *  34.  Pietro clicks "Helpful" on Leo's review
 *  35.  Pietro writes his own 5-star review
 *  36.  Recommendation rate: 100%
 *  37.  Breadcrumb navigation: Home > Food > Sofia's Kitchen > Cookies
 *
 * EPILOGUE (Scenes 38-42):
 *  38.  Login as Johnny -- dashboard
 *  39.  Johnny views his resolved Help Board post
 *  40.  Card: JOHNNY'S LESSON
 *  41.  THE QUESTION (gold text)
 *  42.  Grace Hopper post-production narration card
 *
 * Usage: node record-the-review.js [base_url]
 * Default: https://borrowhood.duckdns.org
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://borrowhood.duckdns.org';
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
  // Must be on a real HTTP page for fetch() to work (data: URLs can't fetch)
  const url = page.url();
  if (!url.startsWith('http')) {
    await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await sleep(300);
  }
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
      opacity: 0; transition: opacity 0.5s ease;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:128px; font-weight:900; margin-bottom:16px;
                 text-shadow:4px 4px 16px rgba(0,0,0,0.4); letter-spacing:-3px; flex-shrink:0">${n}</h1>
      <h2 style="font-size:56px; font-weight:400; opacity:0.9;
                 margin-bottom:12px; line-height:1.3; flex-shrink:0">${s}</h2>
      ${e ? `<div id="overlay-extra" style="font-size:40px; opacity:0.75; margin-top:8px; line-height:1.6; max-width:1500px; flex-shrink:0">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
    void overlay.offsetWidth;
    overlay.style.opacity = '1';
  }, name, subtitle, extra);

  const visibleTime = duration - 1000;
  const halfVisible = Math.floor(Math.max(visibleTime, 0) / 2);
  await sleep(500 + halfVisible);

  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o && o.scrollHeight > o.clientHeight) {
      o.scrollTo({ top: o.scrollHeight, behavior: 'smooth' });
    }
  });
  await sleep(halfVisible);

  await page.evaluate(() => {
    const o = document.getElementById('name-card-overlay');
    if (o) { o.style.opacity = '0'; }
  });
  await sleep(500);
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
// Visibility check: element has size and is not hidden (works for fixed/modal elements too)
function _isVisible(el) {
  const box = el.getBoundingClientRect();
  return box.width > 0 && box.height > 0;
}

async function clickWithRing(page, text, scope = 'button') {
  const found = await page.evaluate((txt, s) => {
    const els = document.querySelectorAll(s);
    for (const el of els) {
      const box = el.getBoundingClientRect();
      if (el.textContent.trim().includes(txt) && box.width > 0 && box.height > 0) {
        el.scrollIntoView({ block: 'center', behavior: 'smooth' });
        return true;
      }
    }
    return false;
  }, text, scope);
  if (!found) { console.log(`  WARN: "${text}" not found`); return false; }
  await sleep(600);

  const pos = await page.evaluate((txt, s) => {
    const els = document.querySelectorAll(s);
    for (const el of els) {
      const box = el.getBoundingClientRect();
      if (el.textContent.trim().includes(txt) && box.width > 0 && box.height > 0) {
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  }, text, scope);
  if (!pos) { console.log(`  WARN: "${text}" position not found`); return false; }
  await showRing(page, pos.x, pos.y);
  await sleep(400);
  // Use page.mouse.click for proper browser-level events (Alpine.js needs real MouseEvent)
  await page.mouse.click(pos.x, pos.y);
  await sleep(2000);
  return true;
}

// -- Click element by CSS selector with ring --
async function clickSelector(page, selector) {
  const pos = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (el) {
      el.scrollIntoView({ block: 'center', behavior: 'smooth' });
      const box = el.getBoundingClientRect();
      return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
    }
    return null;
  }, selector);
  if (!pos) { console.log(`  WARN: selector "${selector}" not found`); return false; }
  await sleep(400);
  await showRing(page, pos.x, pos.y);
  await sleep(400);
  await page.click(selector);
  await sleep(2000);
  return true;
}

// -- Type into a field slowly (visible) --
async function typeSlowly(page, selector, text, delay = 40) {
  await page.focus(selector);
  await sleep(300);
  for (const char of text) {
    await page.keyboard.type(char, { delay });
  }
  await sleep(500);
}

// -- Navigate to dashboard tab --
async function goToDashboardTab(page, tabName) {
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);
  await clickWithRing(page, tabName, '[role="tab"], button, a');
  await sleep(3000);
}

// -- Open a Help Board post by title text (Alpine SPA) --
// clickWithRing shows the ring but Alpine @click on template x-for divs
// can be unreliable. This function: ring + mouse click, then fallback to
// calling openPost() directly via Alpine data if the detail panel doesn't load.
async function openHelpPost(page, titleText) {
  // First try: normal clickWithRing (now uses page.mouse.click)
  const clicked = await clickWithRing(page, titleText, '.bg-white, div, a, h3, h4, button');
  await sleep(2000);

  // Check if post detail loaded (reply textarea appears)
  let loaded = await page.evaluate(() => {
    return document.querySelector('textarea[x-model="newReplyBody"]') !== null;
  });
  if (loaded) {
    console.log('  Post detail loaded via click');
    return true;
  }

  // Fallback: call openPost() directly via Alpine data
  console.log('  Click didn\'t open post detail, using Alpine.js openPost() fallback');
  const opened = await page.evaluate((txt) => {
    // Find the post id from the Alpine component's posts array
    const comp = document.querySelector('[x-data]');
    if (comp && comp._x_dataStack) {
      const data = comp._x_dataStack[0];
      if (data.posts && Array.isArray(data.posts)) {
        const post = data.posts.find(p =>
          (p.title || '').toLowerCase().includes(txt.toLowerCase())
        );
        if (post && typeof data.openPost === 'function') {
          data.openPost(post.id);
          return true;
        }
      }
    }
    return false;
  }, titleText);

  if (opened) {
    await sleep(3000);
    loaded = await page.evaluate(() => {
      return document.querySelector('textarea[x-model="newReplyBody"]') !== null;
    });
    if (loaded) {
      console.log('  Post detail loaded via Alpine.js openPost()');
      return true;
    }
  }

  // Last resort: navigate to API-fetched post URL if available
  console.log('  WARN: Could not open post detail for "' + titleText + '"');
  return false;
}

// -- Click "Leave Review" on dashboard with proper event dispatch --
// The button uses $dispatch('open-review', {...}) which needs real DOM events.
// After clickWithRing (now mouse-based), verify modal appeared.
async function clickLeaveReview(page) {
  // Scroll to find it first
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
      if (btn.textContent.trim().includes('Leave Review')) {
        btn.scrollIntoView({ block: 'center' });
        return true;
      }
    }
    return false;
  });
  await sleep(1000);

  const clicked = await clickWithRing(page, 'Leave Review', 'button');
  if (!clicked) {
    console.log('  WARN: "Leave Review" button not found on page');
    return false;
  }
  await sleep(2000);

  // Verify modal appeared
  const modalOpen = await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      // Check computed style -- Alpine x-show sets display
      const style = window.getComputedStyle(modal);
      return style.display !== 'none';
    }
    return false;
  });

  if (!modalOpen) {
    console.log('  Modal didn\'t open, dispatching open-review event manually');
    await page.evaluate(() => {
      // Find the Leave Review button and extract its dispatch payload
      const btns = document.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.trim().includes('Leave Review')) {
          // Trigger a real click via dispatchEvent
          btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
          return true;
        }
      }
      return false;
    });
    await sleep(2000);
  }

  return true;
}


// ======================================================================
// == MAIN ==============================================================
// ======================================================================
(async () => {
  console.log(`\n  THE REVIEW -- Recording Script (S1 EP04)`);
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
    ],
  });

  const page = (await browser.pages())[0];
  await page.setViewport(VP);

  await waitForEnter('Start OBS recording, then press ENTER');


  // ============================================================
  // SCENE 1: OBS CHECK (5s)
  // ============================================================
  console.log('  Scene 1: OBS check card');
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify: Screen Capture, NOT Window Capture',
    '<div class="extra">If you see this card in OBS, you\'re good.<br>Resolution: 1920x1080</div>'
  ));
  await sleep(5000);


  // ============================================================
  // SCENE 2: INTRO CARD (8s)
  // ============================================================
  console.log('  Scene 2: Intro card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #0c4a6e 30%, #065f46 70%, #047857 100%)',
    'THE REVIEW',
    'Season One \u00BB Episode Four',
    '<div class="extra">Help Boards, Gaskets & the 3-Star Truth</div>'
  ));
  await sleep(8000);


  // ============================================================
  // SCENE 3: PREVIOUSLY ON BORROWHOOD (14s)
  // ============================================================
  console.log('  Scene 3: Recap card');
  await page.goto(card(
    'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
    'PREVIOUSLY ON',
    'BorrowHood',
    '<div class="extra" style="text-align:left; font-size:36px; line-height:1.8">' +
    'Leo welded the bike frame in 5 seconds. Invisible joint.<br>' +
    'Mike taught the course, then refunded <span class="hl">30 euros</span> -- "That wasn\'t a student."<br>' +
    'Sally\'s scooter rented. Johnny delivered 8 cookie boxes on wheels.<br>' +
    'Sofia\'s kitchen is booming. The neighborhood is moving.<br><br>' +
    '<span class="dim">"What happens when a legend... fixes what everyone said was scrap?"</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  //  ACT I -- THE FALL
  // ============================================================
  console.log('\n  === ACT I: THE FALL ===\n');


  // ============================================================
  // SCENE 4: LOGIN AS JOHNNY -- DASHBOARD (8s)
  // ============================================================
  console.log('  Scene 4: Login as Johnny');
  await visibleLogin(page, 'john');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);
  // Show his delivery history in the Orders tab
  await clickWithRing(page, 'Orders', '[role="tab"], button, a');
  await sleep(4000);
  await smoothScroll(page, 400);
  await sleep(3000);


  // ============================================================
  // SCENE 5: CARD -- JOHNNY'S PROBLEM (12s)
  // ============================================================
  console.log('  Scene 5: Johnny\'s problem card');
  await page.goto(card(
    'linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #b91c1c 100%)',
    'JOHNNY\'S PROBLEM',
    'His pressure washer is broken.',
    '<div class="extra" style="text-align:left; font-size:38px; line-height:1.7">' +
    'Trigger stuck. Pump leaks. All plastic.<br>' +
    'He thinks it\'s done. Big garbage day is Thursday.<br>' +
    'He\'s already picturing it on the curb.<br><br>' +
    '<span class="hl">But last time he gave away the bike for free...</span></div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 6: JOHNNY BROWSES -- LOOKS AT GIVEAWAY (6s)
  // ============================================================
  console.log('  Scene 6: Johnny browses, considers giveaway');
  await page.goto(`${BASE}/browse?category=tools`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);
  // Scroll to show he's thinking about listing as free
  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 7: CARD -- THE BIKE LESSON (10s)
  // ============================================================
  console.log('  Scene 7: Bike lesson card');
  await page.goto(card(
    'linear-gradient(135deg, #78350f 0%, #92400e 50%, #b45309 100%)',
    'NOT THIS TIME.',
    '',
    '<div class="extra" style="font-size:42px; line-height:1.7">' +
    'Last time he gave away the bike for free.<br>' +
    'Leo fixed it. Now it\'s worth <span class="hl">50 euros</span>.<br><br>' +
    '<span class="red">He\'s not making that mistake twice.</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 8: JOHNNY OPENS HELP BOARD (5s)
  // ============================================================
  console.log('  Scene 8: Johnny opens Help Board');
  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);


  // ============================================================
  // SCENE 9: HELP BOARD OVERVIEW -- SUMMARY CARDS, FILTERS (6s)
  // ============================================================
  console.log('  Scene 9: Help Board overview');
  // Show the summary cards (needs, offers, resolved counts)
  await sleep(2000);
  await smoothScroll(page, 300);
  await sleep(4000);


  // ============================================================
  // SCENE 10: JOHNNY CLICKS "NEW POST" (6s)
  // ============================================================
  console.log('  Scene 10: Johnny clicks New Post');
  await page.evaluate(() => { window.scrollTo(0, 0); });
  await sleep(500);
  await clickWithRing(page, 'New Post', 'button, a');
  await sleep(3000);
  // Modal or create form should be open now
  await sleep(3000);


  // ============================================================
  // SCENE 11: AI DRAFT (20s)
  // Johnny types his problem, AI returns a full draft with value estimate
  // ============================================================
  console.log('  Scene 11: AI Draft');

  // Type the problem into the AI Draft input field (x-model="aiDraftInput")
  await page.evaluate(() => {
    // Target the AI draft input by Alpine x-model attribute or placeholder
    const aiInput = document.querySelector('input[x-model="aiDraftInput"]') ||
      document.querySelector('input[placeholder*="bike frame"]') ||
      document.querySelector('input[placeholder*="e.g."]');
    if (aiInput) {
      aiInput.scrollIntoView({ block: 'center' });
      aiInput.focus();
      aiInput.value = 'pressure washer trigger stuck pump leaking all plastic';
      aiInput.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }
    return false;
  });
  await sleep(3000);

  // Click "Draft with AI" button (exact text in helpboard.html)
  await clickWithRing(page, 'Draft with AI', 'button') ||
  await clickWithRing(page, 'Draft', 'button');
  await sleep(8000); // Wait for AI to auto-fill title + body via Alpine.js

  // Show the AI-populated form -- scroll through it
  await smoothScroll(page, 400);
  await sleep(5000);

  // No Accept/Use step needed -- AI auto-fills the form fields directly


  // ============================================================
  // SCENE 12: JOHNNY EDITS AND POSTS (10s)
  // If the AI draft auto-filled the form, Johnny just needs to submit.
  // Otherwise, fill in manually.
  // ============================================================
  console.log('  Scene 12: Johnny edits draft and posts');

  // Set the title, body, and category via Alpine.js data + DOM (belt and suspenders)
  await page.evaluate(() => {
    const title = 'Need Help: Pressure Washer -- Trigger Stuck & Pump Leaking';
    const body = 'My Karcher K5 pressure washer has a stuck trigger and the pump is leaking. Everything is plastic so I thought it was done for. Was about to put it on the curb for big garbage day Thursday.\n\nThe AI says this could be worth EUR 80-120 working. The fix might be a simple gasket replacement -- EUR 0.50 in parts and 20 minutes with a pocket knife.\n\nAnyone have spare gaskets or know how to fix this? Photo of the leaking pump attached.';

    // Try Alpine.js data first
    const modal = document.querySelector('[x-show="showCreate"]');
    if (modal) {
      const comp = modal.closest('[x-data]') || document.querySelector('[x-data]');
      if (comp && comp._x_dataStack) {
        const data = comp._x_dataStack[0];
        if (data.newPost) {
          if (!data.newPost.title) data.newPost.title = title;
          if (!data.newPost.body) data.newPost.body = body;
          data.newPost.category = 'home_improvement';
        }
      }
    }

    // Also set DOM values as fallback
    const titleInput = document.querySelector('input[x-model="newPost.title"], input[x-model*="title"]');
    if (titleInput && !titleInput.value) {
      titleInput.value = title;
      titleInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    const bodyInput = document.querySelector('textarea[x-model="newPost.body"], textarea[x-model*="body"]');
    if (bodyInput && !bodyInput.value) {
      bodyInput.value = body;
      bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    const cat = document.querySelector('select[x-model="newPost.category"], select[x-model*="category"]');
    if (cat) {
      cat.value = 'home_improvement';
      cat.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await sleep(2000);

  // Scroll modal to show "Add photos or videos" option (visible on camera)
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showCreate"]');
    if (modal) {
      const scrollable = modal.querySelector('.overflow-y-auto') || modal;
      scrollable.scrollTop = scrollable.scrollHeight;
    }
  });
  await sleep(3000);

  // Submit the post -- click inside the modal
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showCreate"]');
    if (modal) {
      const btns = modal.querySelectorAll('button');
      for (const btn of btns) {
        const txt = btn.textContent.trim();
        if (txt === 'Post' || txt === 'Posting...' || txt.includes('Post')) {
          btn.click(); return;
        }
      }
    }
  });
  // Fallback: try clickWithRing (now works in fixed containers)
  await sleep(1000);
  await clickWithRing(page, 'Post', 'button');
  await sleep(5000);

  // Show the posted result
  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  //  ACT II -- THE RESPONSE
  // ============================================================
  console.log('\n  === ACT II: THE RESPONSE ===\n');


  // ============================================================
  // SCENE 13: CARD -- 24 HOURS LATER (6s)
  // ============================================================
  console.log('  Scene 13: 24 hours later card');
  await page.goto(card(
    'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    '24 HOURS LATER',
    '',
    '<div class="extra" style="font-size:42px">The neighborhood reads the Help Board every morning.</div>'
  ));
  await sleep(6000);


  // ============================================================
  // SCENE 14: LOGIN AS LEO -- HELP BOARD MORNING ROUTINE (8s)
  // ============================================================
  console.log('  Scene 14: Login as Leo');
  await demoLogout(page);
  await visibleLogin(page, 'leonardo');

  // Leo goes straight to Help Board -- this is his morning routine
  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Click "Needs" filter to see who needs help
  await clickWithRing(page, 'Needs', 'button, [role="tab"], a') ||
  await clickWithRing(page, 'need', 'button, [role="tab"], a');
  await sleep(3000);


  // ============================================================
  // SCENE 15: LEO REPLIES TO JOHNNY'S POST (15s)
  // ============================================================
  console.log('  Scene 15: Leo replies to Johnny\'s post');

  // Click on Johnny's pressure washer post (Alpine SPA -- needs special handling)
  await openHelpPost(page, 'Pressure Washer');
  await sleep(2000);

  // Show the post detail -- scroll to reply area
  await smoothScroll(page, 400);
  await sleep(3000);

  // Type Leo's expert reply (textarea uses x-model="newReplyBody")
  const replyText = 'Johnny, that\'s a Karcher K-series. The trigger assembly pops off with a flat-head. The pump gasket is a standard O-ring -- I have a bag of 50 in my Bottega. Come by tomorrow, we\'ll fix it in the field in 20 minutes. Bring a pocket knife.';
  await page.evaluate((txt) => {
    // Try Alpine.js data
    const comp = document.querySelector('[x-data]');
    if (comp && comp._x_dataStack) {
      comp._x_dataStack[0].newReplyBody = txt;
    }
    // Also set DOM
    const textarea = document.querySelector('textarea[x-model="newReplyBody"]');
    if (textarea) {
      textarea.focus();
      textarea.value = txt;
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, replyText);
  await sleep(4000);

  // Submit reply -- the indigo Reply button (px-4 py-2 font-semibold) near the textarea
  // Use clickWithRing which now dispatches proper mouse events for Alpine
  const leoReplyClicked = await clickWithRing(page, 'Reply', 'button.bg-indigo-600') ||
    await clickWithRing(page, 'Reply', 'button');
  if (!leoReplyClicked) {
    // Last resort: call submitReply directly via Alpine
    await page.evaluate(() => {
      const comp = document.querySelector('[x-data]');
      if (comp && comp._x_dataStack && typeof comp._x_dataStack[0].submitReply === 'function') {
        comp._x_dataStack[0].submitReply(null);
      }
    });
  }
  await sleep(3000);

  // Show Leo's business model card
  await showOverlay(page,
    'LEO\'S BUSINESS MODEL',
    'He doesn\'t buy inventory. He reads the Help Board.',
    'The giveaway page is his supply chain.<br>' +
    'The Help Board is his scouting report.<br><br>' +
    'Pick up free stuff. Fix it with parts that cost nothing.<br>' +
    'Sell or rent it back. <span class="hl">That\'s how a Legend operates.</span>',
    12000
  );


  // ============================================================
  // SCENE 16: LOGIN AS MIKE -- POSTS SAFETY OFFER (12s)
  // ============================================================
  console.log('  Scene 16: Login as Mike');
  await demoLogout(page);
  await visibleLogin(page, 'mike');

  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Mike creates a new OFFER post
  await clickWithRing(page, 'New Post', 'button, a');
  await sleep(2000);

  // Fill Mike's offer via Alpine.js data
  await page.evaluate(() => {
    const comp = document.querySelector('[x-data]');
    if (comp && comp._x_dataStack) {
      const data = comp._x_dataStack[0];
      if (data.newPost) {
        data.newPost.help_type = 'offer';
        data.newPost.title = 'I Can Help With: Power Tool & Equipment Safety';
        data.newPost.body = '30 years in the garage. I\'ve seen what happens when you skip the safety check. If you\'re renting a pressure washer, chipper, or saw for the first time -- message me. Free. No appointment. And for the love of God, don\'t stick your arm in the chipper.';
        data.newPost.category = 'home_improvement';
      }
    }
    // DOM fallback
    const titleInput = document.querySelector('input[x-model="newPost.title"]');
    if (titleInput) { titleInput.value = 'I Can Help With: Power Tool & Equipment Safety'; titleInput.dispatchEvent(new Event('input', { bubbles: true })); }
    const bodyInput = document.querySelector('textarea[x-model="newPost.body"]');
    if (bodyInput) { bodyInput.value = '30 years in the garage. I\'ve seen what happens when you skip the safety check. If you\'re renting a pressure washer, chipper, or saw for the first time -- message me. Free. No appointment. And for the love of God, don\'t stick your arm in the chipper.'; bodyInput.dispatchEvent(new Event('input', { bubbles: true })); }
    const cat = document.querySelector('select[x-model="newPost.category"]');
    if (cat) { cat.value = 'home_improvement'; cat.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  await sleep(2000);

  // Submit
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showCreate"]');
    if (modal) {
      const btns = modal.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Post' || btn.textContent.includes('Post')) { btn.click(); return; }
      }
    }
  });
  await sleep(4000);


  // ============================================================
  // SCENE 17: MIKE REPLIES TO JOHNNY'S POST (10s)
  // ============================================================
  console.log('  Scene 17: Mike replies to Johnny\'s post');

  // Navigate to Johnny's post
  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await openHelpPost(page, 'Pressure Washer');
  await sleep(2000);

  await smoothScroll(page, 400);
  await sleep(2000);

  const mikeReply = 'Johnny, the pump gasket is 50 cents at any hardware store. But check the unloader valve too -- if that\'s stuck, the trigger won\'t release pressure. I can walk you through it. And next time -- POST HERE FIRST before throwing things out.';
  await page.evaluate((txt) => {
    const comp = document.querySelector('[x-data]');
    if (comp && comp._x_dataStack) {
      comp._x_dataStack[0].newReplyBody = txt;
    }
    const textarea = document.querySelector('textarea[x-model="newReplyBody"]');
    if (textarea) {
      textarea.focus();
      textarea.value = txt;
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, mikeReply);
  await sleep(3000);

  // Submit reply -- indigo Reply button
  const mikeReplyClicked = await clickWithRing(page, 'Reply', 'button.bg-indigo-600') ||
    await clickWithRing(page, 'Reply', 'button');
  if (!mikeReplyClicked) {
    await page.evaluate(() => {
      const comp = document.querySelector('[x-data]');
      if (comp && comp._x_dataStack && typeof comp._x_dataStack[0].submitReply === 'function') {
        comp._x_dataStack[0].submitReply(null);
      }
    });
  }
  await sleep(3000);


  // ============================================================
  // SCENE 18: JOHNNY EDITS HIS POST (8s)
  // ============================================================
  console.log('  Scene 18: Johnny edits his post');
  await demoLogout(page);
  await visibleLogin(page, 'john');

  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Click into Johnny's own post (Alpine SPA)
  await openHelpPost(page, 'Pressure Washer');
  await sleep(2000);

  // Click Edit Post
  await clickWithRing(page, 'Edit Post', 'button');
  await sleep(2000);

  // Update the body via Alpine.js
  await page.evaluate(() => {
    const comp = document.querySelector('[x-data]');
    if (comp && comp._x_dataStack) {
      const data = comp._x_dataStack[0];
      if (data.editBody !== undefined) {
        data.editBody += '\n\nUPDATE: Leo has the gasket! Going to his Bottega tomorrow. Mike says check the unloader valve too.';
      }
    }
    // DOM fallback
    const bodyInput = document.querySelector('textarea[x-model="editBody"]');
    if (bodyInput) {
      bodyInput.value += '\n\nUPDATE: Leo has the gasket! Going to his Bottega tomorrow. Mike says check the unloader valve too.';
      bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(3000);

  // Save
  await clickWithRing(page, 'Save', 'button');
  await sleep(3000);


  // ============================================================
  // SCENE 19: CARD -- NEXT DAY (6s)
  // ============================================================
  console.log('  Scene 19: Next day card');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%)',
    'NEXT DAY',
    'LEO\'S BOTTEGA',
    '<div class="extra">New gasket. Trigger works. Pump sealed.<br>' +
    'Total cost: <span class="hl">zero euros</span>. Twenty minutes.</div>'
  ));
  await sleep(8000);


  // ============================================================
  // SCENE 20: JOHNNY MARKS POST AS RESOLVED (8s)
  // ============================================================
  console.log('  Scene 20: Johnny marks post as resolved');
  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Click into the post (Alpine SPA)
  await openHelpPost(page, 'Pressure Washer');
  await sleep(2000);

  // Scroll down to see the Resolve button
  await smoothScroll(page, 600);
  await sleep(2000);

  // Click "Mark as Resolved"
  await clickWithRing(page, 'Mark as Resolved', 'button');
  await sleep(3000);

  // Pick Leo as the helper -- repliers show as clickable buttons with author names
  await clickWithRing(page, 'Leonardo', 'button') ||
  await page.evaluate(() => {
    // Find button containing Leo's name in the resolve picker
    const buttons = document.querySelectorAll('button');
    for (const b of buttons) {
      if (b.textContent.includes('Leonardo') || b.textContent.includes('Leo')) {
        const onclick = b.getAttribute('@click') || '';
        if (onclick.includes('resolvePost')) { b.click(); return true; }
      }
    }
    return false;
  });
  await sleep(4000);


  // ============================================================
  // SCENE 21: LEO'S PROFILE -- "Helped 1 neighbor" (6s)
  // ============================================================
  console.log('  Scene 21: Leo\'s profile');
  await demoLogout(page);
  await page.goto(`${BASE}/members`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Search for Leo
  await page.evaluate(() => {
    const search = document.querySelector('input[type="search"], input[name="q"], input[placeholder*="Search"]');
    if (search) {
      search.value = 'Leonardo';
      search.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(3000);
  await smoothScroll(page, 200);
  await sleep(3000);


  // ============================================================
  //  ACT III -- THE REVIEWS
  // ============================================================
  console.log('\n  === ACT III: THE REVIEWS ===\n');


  // ============================================================
  // SCENE 22: CARD -- THE REVIEWS (6s)
  // ============================================================
  console.log('  Scene 22: The Reviews card');
  await page.goto(card(
    'linear-gradient(135deg, #4c1d95 0%, #6d28d9 50%, #7c3aed 100%)',
    'THE REVIEWS',
    'Three stars of truth. Five stars of heart.',
    ''
  ));
  await sleep(6000);


  // ============================================================
  // SCENE 23: LOGIN AS SOFIA -- DASHBOARD (6s)
  // ============================================================
  console.log('  Scene 23: Login as Sofia');
  await visibleLogin(page, 'sofiaferretti');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Click Orders tab to see completed orders
  await clickWithRing(page, 'Orders', '[role="tab"], button, a');
  await sleep(3000);
  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 24: SOFIA OPENS COMPLETED ORDER (4s)
  // ============================================================
  console.log('  Scene 24: Sofia opens completed order');

  // Scroll to find a completed cookie order with "Leave Review" button
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
      if (btn.textContent.trim().includes('Leave Review')) {
        btn.scrollIntoView({ block: 'center' });
        return true;
      }
    }
    return false;
  });
  await sleep(3000);


  // ============================================================
  // SCENE 25: SOFIA WRITES 5-STAR REVIEW (20s)
  // ============================================================
  console.log('  Scene 25: Sofia writes 5-star review');

  // Click the first "Leave Review" button (cookie order)
  await clickLeaveReview(page);
  await sleep(2000);

  // Review modal is now open (class="fixed" container)
  // Use Alpine.js data manipulation -- the modal uses x-data with reviewRating, etc.
  // Set 5 stars via Alpine
  await page.evaluate(() => {
    // Find the review modal's Alpine component
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      const comp = modal.closest('[x-data]');
      if (comp && comp._x_dataStack) {
        const data = comp._x_dataStack[0];
        data.reviewRating = 5;
        data.rAccuracy = 5;
        data.rCommunication = 5;
        data.rValue = 5;
        data.rTimeliness = 5;
        data.wouldRecommend = true;
        data.reviewBody = 'Johnny delivered my cookies in 20 minutes, still warm. He even asked if the customer was happy before leaving. If you need delivery in Trapani, Johnny is your man. He deserves every star.';
        return true;
      }
    }
    // Fallback: click the 5th star button inside the modal
    const fixedModal = document.querySelector('.fixed [x-show="showReviewModal"]') ||
                       document.querySelector('[x-show="showReviewModal"]');
    if (fixedModal) {
      const starBtns = fixedModal.querySelectorAll('button');
      // Stars are in groups of 5, first group is overall rating
      let starCount = 0;
      for (const btn of starBtns) {
        if (btn.querySelector('svg') && btn.closest('.flex.items-center')) {
          starCount++;
          if (starCount === 5) { btn.click(); break; } // 5th star = 5 stars
        }
      }
    }
    return false;
  });
  await sleep(2000);

  // Show the filled form visually -- scroll modal content
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"] .overflow-y-auto');
    if (modal) modal.scrollTop = modal.scrollHeight;
  });
  await sleep(3000);

  // Click "Submit Review" inside the modal
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      const btns = modal.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.includes('Submit Review') || btn.textContent.includes('Update Review')) {
          btn.click();
          return;
        }
      }
    }
  });
  await sleep(5000);


  // ============================================================
  // SCENE 26: CARD -- DELIVERY TRACKING (8s)
  // ============================================================
  console.log('  Scene 26: Delivery tracking card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    'DELIVERY TRACKING',
    'Every cookie box. Every minute.',
    '<div class="extra" style="text-align:left; font-size:36px; line-height:1.8">' +
    '<span class="check">10:10</span> Johnny picked up cookies from Sofia<br>' +
    '<span class="check">10:30</span> Cookies delivered to front door<br>' +
    '<span class="check">10:35</span> Customer confirmed happy<br><br>' +
    'Dispatched to delivered: <span class="hl">20 minutes</span><br>' +
    'Still warm: <span class="green">YES</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 27: LOGIN AS LEO -- COMPLETED COOKIE ORDER (6s)
  // ============================================================
  console.log('  Scene 27: Login as Leo');
  await visibleLogin(page, 'leonardo');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  await clickWithRing(page, 'Orders', '[role="tab"], button, a');
  await sleep(3000);
  await smoothScroll(page, 300);
  await sleep(3000);


  // ============================================================
  // SCENE 28: LEO WRITES 3-STAR REVIEW (20s)
  // ============================================================
  console.log('  Scene 28: Leo writes 3-star review');

  // Click Leave Review button on Leo's completed cookie order
  await clickLeaveReview(page);
  await sleep(2000);

  // Review modal open -- set 3 stars, mixed subcategories, via Alpine.js
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      const comp = modal.closest('[x-data]');
      if (comp && comp._x_dataStack) {
        const data = comp._x_dataStack[0];
        data.reviewRating = 3;
        data.rAccuracy = 5;
        data.rCommunication = 2;
        data.rValue = 5;
        data.rTimeliness = 1;
        data.wouldRecommend = true;
        data.reviewBody = 'Best cookies in Trapani. But if Johnny delivers them, get the bike option. The drone left mine on the balcony like a seagull dropping a fish. Cookies were cold 3 hours later.';
      }
    }
  });
  await sleep(4000);

  // Show the filled form
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"] .overflow-y-auto');
    if (modal) modal.scrollTop = modal.scrollHeight;
  });
  await sleep(3000);

  // Submit
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      const btns = modal.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.includes('Submit Review')) { btn.click(); return; }
      }
    }
  });
  await sleep(5000);


  // ============================================================
  // SCENE 29: SOFIA'S RATING DROPS (6s)
  // ============================================================
  console.log('  Scene 29: Sofia sees rating drop');
  await page.goto(card(
    'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)',
    '4.0',
    'Sofia\'s new average rating.',
    '<div class="extra">One 5-star. One 3-star.<br>She panics.</div>'
  ));
  await sleep(6000);


  // ============================================================
  // SCENE 30: SALLY SHOWS SOFIA THE REVIEW (8s)
  // ============================================================
  console.log('  Scene 30: Sally shows Sofia the review');
  await demoLogout(page);
  await visibleLogin(page, 'sally');

  // Sally opens Sofia's cookies item page to show her the review
  await page.goto(`${BASE}/items/cookie-jar-refill-ooak-cookies-750g`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Scroll down to reviews section
  await smoothScroll(page, 800);
  await sleep(4000);

  await showOverlay(page,
    'SALLY',
    '"Read what he ACTUALLY said."',
    '"The cookies are perfect. The delivery method was the problem.<br>' +
    'Leo recommended you. Even with 3 stars. That\'s what matters."',
    10000
  );


  // ============================================================
  // SCENE 31: SOFIA RESPONDS TO LEO'S REVIEW (12s)
  // ============================================================
  console.log('  Scene 31: Sofia responds to Leo\'s review');
  await demoLogout(page);
  await visibleLogin(page, 'sofiaferretti');

  // Navigate to Sofia's cookie item page
  await page.goto(`${BASE}/items/cookie-jar-refill-ooak-cookies-750g`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Scroll to reviews
  await smoothScroll(page, 800);
  await sleep(3000);

  // Click "Respond" on Leo's review (owner response)
  await clickWithRing(page, 'Respond', 'button');
  await sleep(2000);

  // Type the owner response
  await page.evaluate(() => {
    const textareas = document.querySelectorAll('textarea');
    for (const textarea of textareas) {
      if (textarea.offsetParent !== null && !textarea.value) {
        textarea.focus();
        textarea.value = 'Leo, thank you! Johnny is our best delivery rider. We\'ve disabled drone delivery for now -- your cookies deserve a human touch.';
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        break;
      }
    }
  });
  await sleep(4000);

  // Submit response
  await clickWithRing(page, 'Submit Response', 'button') ||
  await clickWithRing(page, 'Submit', 'button') ||
  await clickWithRing(page, 'Send', 'button');
  await sleep(5000);

  // Show the response appeared + edit lock
  await smoothScroll(page, 200);
  await sleep(3000);


  // ============================================================
  // SCENE 32: LOGIN AS PIETRO -- READS REVIEWS (8s)
  // ============================================================
  console.log('  Scene 32: Login as Pietro');
  await demoLogout(page);
  await visibleLogin(page, 'pietro');

  await page.goto(`${BASE}/items/cookie-jar-refill-ooak-cookies-750g`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Scroll to reviews section
  await smoothScroll(page, 800);
  await sleep(5000);


  // ============================================================
  // SCENE 33: STAR DISTRIBUTION CHART (6s)
  // ============================================================
  console.log('  Scene 33: Star distribution chart');
  // The chart should already be visible on the item page
  // Scroll to make sure it's fully in view
  await page.evaluate(() => {
    const chart = document.querySelector('[class*="distribution"], [class*="star-chart"], [x-data*="summary"]');
    if (chart) chart.scrollIntoView({ block: 'center', behavior: 'smooth' });
  });
  await sleep(6000);


  // ============================================================
  // SCENE 34: PIETRO CLICKS "HELPFUL" ON LEO'S REVIEW (6s)
  // ============================================================
  console.log('  Scene 34: Pietro clicks Helpful');

  // Find the helpful (thumbs-up) button -- it's an SVG icon with title="Helpful"
  // Use clickSelector with proper mouse event for Alpine @click binding
  const helpfulClicked = await clickSelector(page, 'button[title="Helpful"]');
  if (!helpfulClicked) {
    console.log('  WARN: Helpful button not found by title, trying fallback');
    // Fallback: find by Alpine @click attribute via evaluate + mouse click
    const helpfulPos = await page.evaluate(() => {
      const allBtns = document.querySelectorAll('button');
      for (const btn of allBtns) {
        const onclick = btn.getAttribute('@click') || '';
        if (onclick.includes('voteReview') && onclick.includes('true')) {
          btn.scrollIntoView({ block: 'center' });
          const box = btn.getBoundingClientRect();
          return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        }
      }
      return null;
    });
    if (helpfulPos) {
      await showRing(page, helpfulPos.x, helpfulPos.y);
      await sleep(400);
      await page.mouse.click(helpfulPos.x, helpfulPos.y);
    }
  }
  await sleep(4000);


  // ============================================================
  // SCENE 35: PIETRO WRITES HIS OWN 5-STAR REVIEW (15s)
  // ============================================================
  console.log('  Scene 35: Pietro writes 5-star review');

  // Pietro needs a completed rental to review -- go to dashboard
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await clickWithRing(page, 'Orders', '[role="tab"], button, a');
  await sleep(3000);

  // Click Leave Review button on a completed order
  await clickLeaveReview(page);
  await sleep(2000);

  // Review modal open -- set 5 stars via Alpine.js
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      const comp = modal.closest('[x-data]');
      if (comp && comp._x_dataStack) {
        const data = comp._x_dataStack[0];
        data.reviewRating = 5;
        data.rAccuracy = 5;
        data.rCommunication = 5;
        data.rValue = 5;
        data.rTimeliness = 5;
        data.wouldRecommend = true;
        data.reviewBody = 'I always pick Johnny delivery. Cookies arrive warm. RTFM on the delivery options, people.';
      }
    }
  });
  await sleep(3000);

  // Submit
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showReviewModal"]');
    if (modal) {
      const btns = modal.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent.includes('Submit Review')) { btn.click(); return; }
      }
    }
  });
  await sleep(5000);


  // ============================================================
  // SCENE 36: RECOMMENDATION RATE 100% (6s)
  // ============================================================
  console.log('  Scene 36: Recommendation rate');
  // Go back to cookie item page to show updated stats
  await page.goto(`${BASE}/items/cookie-jar-refill-ooak-cookies-750g`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Scroll to review summary showing 100% recommendation rate
  await smoothScroll(page, 600);
  await sleep(5000);

  await showOverlay(page,
    '100%',
    'Recommendation Rate',
    'All 3 reviewers said YES. Even the 3-star guy.<br><br>' +
    '<span class="hl">The rating tells you the score.<br>The recommendation tells you the truth.</span>',
    8000
  );


  // ============================================================
  // SCENE 37: BREADCRUMB NAVIGATION (8s)
  // ============================================================
  console.log('  Scene 37: Breadcrumb navigation');

  // Show breadcrumbs at top of Sofia's cookie page
  await page.evaluate(() => { window.scrollTo(0, 0); });
  await sleep(1000);
  await setZoom(page);
  await sleep(2000);

  // Click through breadcrumbs: show the navigation path
  // Home > Browse > Food > Sofia's Kitchen > Cookies
  await page.evaluate(() => {
    const breadcrumbs = document.querySelector('.breadcrumb, nav[aria-label*="breadcrumb"], [class*="breadcrumb"]');
    if (breadcrumbs) {
      breadcrumbs.scrollIntoView({ block: 'center' });
    }
  });
  await sleep(3000);

  // Click "Home" in breadcrumbs
  await clickWithRing(page, 'Home', 'a');
  await sleep(3000);

  // Navigate to browse
  await page.goto(`${BASE}/browse?category=kitchen`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Click through to Sofia's cookies
  await clickWithRing(page, 'Cookie', 'a, h3, h4');
  await sleep(3000);


  // ============================================================
  //  EPILOGUE
  // ============================================================
  console.log('\n  === EPILOGUE ===\n');


  // ============================================================
  // SCENE 38: LOGIN AS JOHNNY -- DASHBOARD (6s)
  // ============================================================
  console.log('  Scene 38: Login as Johnny');
  await demoLogout(page);
  await visibleLogin(page, 'john');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);


  // ============================================================
  // SCENE 39: JOHNNY VIEWS RESOLVED HELP BOARD POST (8s)
  // ============================================================
  console.log('  Scene 39: Johnny views resolved Help Board post');
  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Click into his resolved post (Alpine SPA)
  await openHelpPost(page, 'Pressure Washer');
  await sleep(2000);

  // Scroll through -- show Leo's reply, Mike's reply, the RESOLVED badge
  await smoothScroll(page, 500);
  await sleep(5000);


  // ============================================================
  // SCENE 40: CARD -- JOHNNY'S LESSON (14s)
  // ============================================================
  console.log('  Scene 40: Johnny\'s lesson card');
  await page.goto(card(
    'linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%)',
    'JOHNNY\'S LESSON',
    '',
    '<div class="extra" style="text-align:left; font-size:36px; line-height:1.8">' +
    '"I was going to put it on the curb Thursday.<br>' +
    'Big garbage day.<br><br>' +
    'An <span class="hl">80-euro</span> pressure washer,<br>' +
    'trashed over a <span class="hl">fifty-cent gasket</span>.<br><br>' +
    'Leo had a bag of them.<br>' +
    'Mike knew exactly what was wrong from a photo.<br><br>' +
    'They were already here, walking around, waiting to help.<br>' +
    '<span class="green">I just had to ask.</span>"</div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 41: THE QUESTION (10s)
  // ============================================================
  console.log('  Scene 41: THE QUESTION');
  await page.goto(card(
    'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    '',
    '',
    '<div style="font-size:64px; color:#FCD34D; font-weight:700; line-height:1.4; max-width:1200px">' +
    '"What if asking for help...<br>was the bravest thing you ever did?"</div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 42: GRACE HOPPER POST-PRODUCTION NARRATION
  // This card appears at the END of recording.
  // Grace Hopper delivers the episode wrap-up for voiceover.
  // ============================================================
  console.log('  Scene 42: Grace Hopper narration card');
  await page.goto(card(
    'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
    '',
    '',
    '<div class="extra" style="text-align:left; font-size:26px; line-height:1.65; max-width:1400px; opacity:0.9">' +
    '<span class="hl" style="font-size:32px">GRACE (V.O.):</span><br><br>' +
    '"A ship in port is safe, but that\'s not what ships are built for."<br><br>' +
    'Johnny\'s pressure washer sat in his hallway for two weeks.<br>' +
    'He walked past it every morning. Thought about the curb.<br>' +
    'Thought about big garbage day. Thought about giving up.<br><br>' +
    'Then he typed seven words into a text box.<br>' +
    '<span class="hl">"Pressure washer trigger stuck pump leaking."</span><br><br>' +
    'Leo answered in four hours. Mike in six.<br>' +
    'The gasket cost fifty cents. The fix took twenty minutes.<br>' +
    'The machine was worth eighty euros.<br><br>' +
    'Sofia got a three-star review and thought the sky was falling.<br>' +
    'But every single reviewer -- even the three-star one --<br>' +
    'clicked <span class="green">YES</span> on "Would you recommend?"<br><br>' +
    'The rating tells you the score.<br>' +
    'The recommendation tells you the truth.<br><br>' +
    'And Johnny? He learned the hardest lesson of all:<br>' +
    '<span class="hl">Asking for help is not weakness. It\'s the first step.</span><br><br>' +
    '<span class="dim">-- Rear Admiral Grace Hopper, USN</span></div>'
  ));
  await sleep(25000);


  // ============================================================
  // END CARD
  // ============================================================
  console.log('  End card: TO BE CONTINUED');
  await page.goto(card(
    '#0f172a',
    'TO BE CONTINUED',
    'Season 1 \u00BB Episode Four \u00BB "The Review"',
    '<div class="extra">BorrowHood: The Garage Sessions</div>'
  ));
  await sleep(8000);


  // ============================================================
  // DONE
  // ============================================================
  await waitForEnter('Stop OBS recording, then press ENTER to close browser');
  await browser.close();

  console.log('\n  ============================');
  console.log('  RECORDING COMPLETE');
  console.log('  ============================\n');
  console.log('  Post-production checklist:');
  console.log('    1. Play first 10 seconds -- verify browser content, not desktop');
  console.log('    2. Trim raw footage: ffmpeg -i raw.mp4 -ss START -to END -an -c:v libx264 -crf 18 review-silent.mp4');
  console.log('    3. Add Brotherhood Run at 30%: see Bro_Kit/CLAUDE.md pipeline');
  console.log('    4. Grace Hopper V.O.: Record voiceover for Scene 42 card');
  console.log('    5. Update chapter timestamps in youtube-kit/description.txt');
  console.log('    6. Render thumbnail: node youtube-kit/render-thumbnail.js');
  console.log('');

})().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
