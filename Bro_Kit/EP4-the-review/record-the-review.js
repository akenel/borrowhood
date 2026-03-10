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
async function clickWithRing(page, text, scope = 'button') {
  const found = await page.evaluate((txt, s) => {
    const els = document.querySelectorAll(s);
    for (const el of els) {
      if (el.textContent.trim().includes(txt) && !el.closest('.fixed')) {
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
      if (el.textContent.trim().includes(txt) && !el.closest('.fixed')) {
        const box = el.getBoundingClientRect();
        if (box.width > 0 && box.height > 0) {
          return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        }
      }
    }
    return null;
  }, text, scope);
  if (!pos) { console.log(`  WARN: "${text}" position not found`); return false; }
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
    'Leo sold it for <span class="hl">50 euros</span>.<br><br>' +
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

  // Try to find and click the AI assist button
  const aiClicked = await clickWithRing(page, 'AI', 'button');
  if (!aiClicked) {
    // Fallback: look for "Draft" or "Generate" or "Assist"
    await clickWithRing(page, 'Draft', 'button') ||
    await clickWithRing(page, 'Generate', 'button') ||
    await clickWithRing(page, 'Assist', 'button');
  }
  await sleep(2000);

  // Type the problem description into the AI prompt field
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('textarea, input[type="text"]');
    for (const input of inputs) {
      const placeholder = (input.placeholder || '').toLowerCase();
      if (placeholder.includes('describe') || placeholder.includes('problem') || placeholder.includes('help') || placeholder.includes('prompt')) {
        input.scrollIntoView({ block: 'center' });
        input.focus();
        input.value = 'pressure washer trigger stuck pump leaking all plastic';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      }
    }
    // Fallback: find any visible textarea
    for (const input of inputs) {
      if (input.offsetParent !== null) {
        input.focus();
        input.value = 'pressure washer trigger stuck pump leaking all plastic';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      }
    }
    return false;
  });
  await sleep(3000);

  // Click generate/submit
  await clickWithRing(page, 'Generate', 'button') ||
  await clickWithRing(page, 'Draft', 'button') ||
  await clickWithRing(page, 'Submit', 'button');
  await sleep(8000); // Wait for AI to generate

  // Show the AI result -- scroll through it
  await smoothScroll(page, 400);
  await sleep(5000);

  // Accept the draft
  await clickWithRing(page, 'Accept', 'button') ||
  await clickWithRing(page, 'Use', 'button') ||
  await clickWithRing(page, 'Apply', 'button');
  await sleep(3000);


  // ============================================================
  // SCENE 12: JOHNNY EDITS AND POSTS (10s)
  // If the AI draft auto-filled the form, Johnny just needs to submit.
  // Otherwise, fill in manually.
  // ============================================================
  console.log('  Scene 12: Johnny edits draft and posts');

  // Set the title if not already filled
  await page.evaluate(() => {
    const titleInput = document.querySelector('input[name="title"], input[placeholder*="Title"], input[x-model*="title"]');
    if (titleInput && !titleInput.value) {
      titleInput.value = 'Need Help: Pressure Washer -- Trigger Stuck & Pump Leaking';
      titleInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(1000);

  // Set the body if not already filled
  await page.evaluate(() => {
    const bodyInput = document.querySelector('textarea[name="body"], textarea[x-model*="body"]');
    if (bodyInput && !bodyInput.value) {
      bodyInput.value = 'My Karcher K5 pressure washer has a stuck trigger and the pump is leaking. Everything is plastic so I thought it was done for. Was about to put it on the curb for big garbage day Thursday.\n\nThe AI says this could be worth EUR 80-120 working. The fix might be a simple gasket replacement -- EUR 0.50 in parts and 20 minutes with a pocket knife.\n\nAnyone have spare gaskets or know how to fix this? Photo of the leaking pump attached.';
      bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(2000);

  // Select category if dropdown exists
  await page.evaluate(() => {
    const cat = document.querySelector('select[name="category"], select[x-model*="category"]');
    if (cat) {
      cat.value = 'home_improvement';
      cat.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await sleep(500);

  // Submit the post
  await clickWithRing(page, 'Post', 'button') ||
  await clickWithRing(page, 'Submit', 'button') ||
  await clickWithRing(page, 'Create', 'button');
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

  // Click on Johnny's pressure washer post
  await clickWithRing(page, 'Pressure Washer', 'a, h3, h4, div, button');
  await sleep(3000);

  // Show the post detail
  await smoothScroll(page, 300);
  await sleep(3000);

  // Click Reply
  await clickWithRing(page, 'Reply', 'button, a');
  await sleep(2000);

  // Type Leo's expert reply
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea');
    if (textarea) {
      textarea.focus();
      textarea.value = 'Johnny, that\'s a Karcher K-series. The trigger assembly pops off with a flat-head. The pump gasket is a standard O-ring -- I have a bag of 50 in my Bottega. Come by tomorrow, we\'ll fix it in the field in 20 minutes. Bring a pocket knife.';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(4000);

  // Submit reply
  await clickWithRing(page, 'Reply', 'button') ||
  await clickWithRing(page, 'Submit', 'button') ||
  await clickWithRing(page, 'Post', 'button');
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

  // Fill in Mike's offer
  await page.evaluate(() => {
    // Set type to offer
    const typeSelect = document.querySelector('select[name="help_type"], select[x-model*="type"], select[x-model*="help_type"]');
    if (typeSelect) {
      typeSelect.value = 'offer';
      typeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }
    // Check for radio buttons instead
    const offerRadio = document.querySelector('input[value="offer"], button[data-value="offer"]');
    if (offerRadio) offerRadio.click();
  });
  await sleep(1000);

  await page.evaluate(() => {
    const titleInput = document.querySelector('input[name="title"], input[x-model*="title"]');
    if (titleInput) {
      titleInput.value = 'I Can Help With: Power Tool & Equipment Safety';
      titleInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(1000);

  await page.evaluate(() => {
    const bodyInput = document.querySelector('textarea[name="body"], textarea[x-model*="body"]');
    if (bodyInput) {
      bodyInput.value = '30 years in the garage. I\'ve seen what happens when you skip the safety check. If you\'re renting a pressure washer, chipper, or saw for the first time -- message me. Free. No appointment. And for the love of God, don\'t stick your arm in the chipper.';
      bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(2000);

  await page.evaluate(() => {
    const cat = document.querySelector('select[name="category"], select[x-model*="category"]');
    if (cat) {
      cat.value = 'home_improvement';
      cat.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await sleep(500);

  await clickWithRing(page, 'Post', 'button') ||
  await clickWithRing(page, 'Submit', 'button') ||
  await clickWithRing(page, 'Create', 'button');
  await sleep(4000);


  // ============================================================
  // SCENE 17: MIKE REPLIES TO JOHNNY'S POST (10s)
  // ============================================================
  console.log('  Scene 17: Mike replies to Johnny\'s post');

  // Navigate to Johnny's post
  await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await clickWithRing(page, 'Pressure Washer', 'a, h3, h4, div, button');
  await sleep(3000);

  await clickWithRing(page, 'Reply', 'button, a');
  await sleep(2000);

  await page.evaluate(() => {
    const textarea = document.querySelector('textarea');
    if (textarea) {
      textarea.focus();
      textarea.value = 'Johnny, the pump gasket is 50 cents at any hardware store. But check the unloader valve too -- if that\'s stuck, the trigger won\'t release pressure. I can walk you through it. And next time -- POST HERE FIRST before throwing things out.';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(3000);

  await clickWithRing(page, 'Reply', 'button') ||
  await clickWithRing(page, 'Submit', 'button');
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

  // Click into Johnny's own post
  await clickWithRing(page, 'Pressure Washer', 'a, h3, h4, div, button');
  await sleep(3000);

  // Click Edit
  await clickWithRing(page, 'Edit', 'button, a');
  await sleep(2000);

  // Update the body
  await page.evaluate(() => {
    const bodyInput = document.querySelector('textarea[name="body"], textarea[x-model*="body"]');
    if (bodyInput) {
      bodyInput.value += '\n\nUPDATE: Leo has the gasket! Going to his Bottega tomorrow. Mike says check the unloader valve too.';
      bodyInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(3000);

  // Save
  await clickWithRing(page, 'Save', 'button') ||
  await clickWithRing(page, 'Update', 'button');
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

  // Click into the post
  await clickWithRing(page, 'Pressure Washer', 'a, h3, h4, div, button');
  await sleep(3000);

  // Click "Mark as Resolved" or "Resolve"
  await clickWithRing(page, 'Resolve', 'button') ||
  await clickWithRing(page, 'Mark as Resolved', 'button');
  await sleep(3000);

  // Pick Leo as the helper (if a picker appears)
  await page.evaluate(() => {
    // Look for a helper picker -- dropdown, radio, or button with Leo's name
    const leoOption = document.querySelector('[data-helper*="leonardo"], option[value*="leonardo"]');
    if (leoOption) leoOption.click();
    // Or select from dropdown
    const select = document.querySelector('select[name="helper"], select[x-model*="helper"]');
    if (select) {
      const options = select.querySelectorAll('option');
      for (const opt of options) {
        if (opt.textContent.includes('Leonardo') || opt.textContent.includes('Leo')) {
          select.value = opt.value;
          select.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }
  });
  await sleep(2000);

  // Confirm resolve
  await clickWithRing(page, 'Confirm', 'button') ||
  await clickWithRing(page, 'Save', 'button') ||
  await clickWithRing(page, 'Resolve', 'button');
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

  // Look for a completed order with "Review" button (Johnny delivered)
  // The review buttons use $dispatch pattern, look for them
  const reviewBtnFound = await page.evaluate(() => {
    const btns = document.querySelectorAll('span[data-rental-id], button');
    for (const btn of btns) {
      if (btn.textContent.trim() === 'Review') {
        btn.scrollIntoView({ block: 'center' });
        return true;
      }
    }
    return false;
  });
  if (reviewBtnFound) {
    await sleep(1000);
  }
  await sleep(3000);


  // ============================================================
  // SCENE 25: SOFIA WRITES 5-STAR REVIEW (20s)
  // ============================================================
  console.log('  Scene 25: Sofia writes 5-star review');

  // Click the Review button (uses $dispatch)
  await clickWithRing(page, 'Review', 'span, button');
  await sleep(3000);

  // The review modal should be open now
  // Fill in 5 stars -- click the 5th star
  await page.evaluate(() => {
    // Find star rating buttons (usually radio inputs or clickable stars)
    const stars = document.querySelectorAll('[data-rating="5"], .star-5, input[value="5"]');
    if (stars.length > 0) {
      stars[0].click();
      return;
    }
    // Try finding star buttons by position (5th star element)
    const allStars = document.querySelectorAll('.star, [x-on\\:click*="rating"], svg[class*="star"]');
    if (allStars.length >= 5) {
      allStars[4].click();
    }
  });
  await sleep(2000);

  // Fill subcategory ratings if visible
  await page.evaluate(() => {
    const selects = document.querySelectorAll('select');
    for (const sel of selects) {
      const label = sel.closest('label, div')?.textContent?.toLowerCase() || '';
      if (label.includes('accuracy') || label.includes('communication') ||
          label.includes('value') || label.includes('timeli')) {
        sel.value = '5';
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    // Also try radio/star inputs for subcategories
    const subInputs = document.querySelectorAll('[name*="accuracy"], [name*="communication"], [name*="value"], [name*="timeli"]');
    for (const input of subInputs) {
      if (input.value === '5') input.click();
    }
  });
  await sleep(2000);

  // Would recommend: YES
  await clickWithRing(page, 'Yes', 'button, label') ||
  await page.evaluate(() => {
    const rec = document.querySelector('input[name*="recommend"][value="true"], button[data-recommend="true"]');
    if (rec) rec.click();
  });
  await sleep(1000);

  // Write the review body
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea[name="body"], textarea[x-model*="body"], textarea[placeholder*="review"], textarea[placeholder*="Review"]');
    if (textarea) {
      textarea.focus();
      textarea.value = 'Johnny delivered my cookies in 20 minutes, still warm. He even asked if the customer was happy before leaving. If you need delivery in Trapani, Johnny is your man. He deserves every star.';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(4000);

  // Scroll to show the full review form
  await smoothScroll(page, 200);
  await sleep(2000);

  // Submit
  await clickWithRing(page, 'Submit', 'button') ||
  await clickWithRing(page, 'Post', 'button') ||
  await clickWithRing(page, 'Save', 'button');
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

  // Click Review button on Leo's completed cookie order
  await clickWithRing(page, 'Review', 'span, button');
  await sleep(3000);

  // 3 stars overall
  await page.evaluate(() => {
    const stars = document.querySelectorAll('[data-rating="3"], .star-3, input[value="3"]');
    if (stars.length > 0) {
      stars[0].click();
      return;
    }
    const allStars = document.querySelectorAll('.star, [x-on\\:click*="rating"], svg[class*="star"]');
    if (allStars.length >= 3) {
      allStars[2].click();
    }
  });
  await sleep(2000);

  // Subcategories: Accuracy 5, Communication 2, Value 5, Timeliness 1
  await page.evaluate(() => {
    const selects = document.querySelectorAll('select');
    for (const sel of selects) {
      const label = sel.closest('label, div')?.textContent?.toLowerCase() || '';
      if (label.includes('accuracy')) {
        sel.value = '5'; sel.dispatchEvent(new Event('change', { bubbles: true }));
      } else if (label.includes('communication')) {
        sel.value = '2'; sel.dispatchEvent(new Event('change', { bubbles: true }));
      } else if (label.includes('value')) {
        sel.value = '5'; sel.dispatchEvent(new Event('change', { bubbles: true }));
      } else if (label.includes('timeli')) {
        sel.value = '1'; sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
  });
  await sleep(2000);

  // Would recommend: YES (despite 3 stars)
  await clickWithRing(page, 'Yes', 'button, label') ||
  await page.evaluate(() => {
    const rec = document.querySelector('input[name*="recommend"][value="true"], button[data-recommend="true"]');
    if (rec) rec.click();
  });
  await sleep(1000);

  // Leo's review body
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea[name="body"], textarea[x-model*="body"], textarea[placeholder*="review"], textarea[placeholder*="Review"]');
    if (textarea) {
      textarea.focus();
      textarea.value = 'Best cookies in Trapani. But if Johnny delivers them, get the bike option. The drone left mine on the balcony like a seagull dropping a fish. Cookies were cold 3 hours later.';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(4000);

  // Submit
  await clickWithRing(page, 'Submit', 'button') ||
  await clickWithRing(page, 'Post', 'button');
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

  // Find Leo's review (the 3-star one) and click helpful
  await clickWithRing(page, 'Helpful', 'button') ||
  await page.evaluate(() => {
    const helpfulBtns = document.querySelectorAll('button');
    for (const btn of helpfulBtns) {
      if (btn.textContent.includes('Helpful') || btn.innerHTML.includes('thumbs-up')) {
        btn.click();
        break;
      }
    }
  });
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

  // Click Review button on a completed order
  await clickWithRing(page, 'Review', 'span, button');
  await sleep(3000);

  // 5 stars
  await page.evaluate(() => {
    const stars = document.querySelectorAll('[data-rating="5"], .star-5, input[value="5"]');
    if (stars.length > 0) {
      stars[0].click();
      return;
    }
    const allStars = document.querySelectorAll('.star, [x-on\\:click*="rating"], svg[class*="star"]');
    if (allStars.length >= 5) {
      allStars[4].click();
    }
  });
  await sleep(2000);

  // Would recommend: YES
  await clickWithRing(page, 'Yes', 'button, label');
  await sleep(1000);

  // Pietro's review body
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea[name="body"], textarea[x-model*="body"], textarea[placeholder*="review"], textarea[placeholder*="Review"]');
    if (textarea) {
      textarea.focus();
      textarea.value = 'I always pick Johnny delivery. Cookies arrive warm. RTFM on the delivery options, people.';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await sleep(3000);

  // Submit
  await clickWithRing(page, 'Submit', 'button');
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
  await page.goto(`${BASE}/browse?category=food_and_drinks`, { waitUntil: 'networkidle2', timeout: 15000 });
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

  // Click into his resolved post
  await clickWithRing(page, 'Pressure Washer', 'a, h3, h4, div, button');
  await sleep(3000);

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
    'GRACE HOPPER',
    'Post-Production Narration',
    '<div class="extra" style="text-align:left; font-size:32px; line-height:1.8; max-width:1500px">' +
    '<span class="hl">GRACE (V.O.):</span><br><br>' +
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
