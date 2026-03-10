#!/usr/bin/env node
/**
 * THE SCOOTER -- Recording Script (S1 EP03)
 *
 * Picks up right where EP02 "The Cookie Run" left off:
 *   "What if the cookie queen... rented the wheels?"
 *
 * Every click visible. Every login visible. Every status change on screen.
 * 6-act structure + epilogue. Know the ending before you write.
 *
 * THE ENDING: The bike is reborn in Leo's Bottega. Johnny doesn't know yet.
 *   Leo learned to weld in 5 seconds. Mike got a legend as a favorite.
 *   THE QUESTION: What happens when a legend... fixes what everyone said was scrap?
 *
 * ACT I -- THE RESCUE (Scenes 1-14):
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- "THE SCOOTER"
 *   3.  "Previously on BorrowHood" recap card
 *   4.  Leonardo character overlay on homepage
 *   5.  Login as Leonardo -- his Bottega workshop (first time)
 *   6.  Leo browses listings -- finds Johnny's broken bike (FREE for parts)
 *   7.  Leo claims the giveaway bike (pickup)
 *   8.  Leo picks up bike at Johnny's -- Johnny tells his story
 *   9.  Card: JOHNNY'S STORY (scrap yard, loves the bike, hopes someone does something)
 *  10.  Card: Leo walks away with bike on shoulder. Maker brain kicks in.
 *  11.  Leo pulls out phone -- finds Mike's welding course (EUR 30)
 *  12.  Mike character overlay
 *  13.  Leo books Mike's training on BorrowHood
 *  14.  Leo walks bike to Mike's Garage
 *
 * ACT II -- THE WIND (Scenes 15-21):
 *  15.  Card: TRAPANI WIND -- 50 km/h gusts
 *  16.  Login as Pietro -- drone grounded
 *  17.  Card: "The wind doesn't care about your drone license"
 *  18.  Login as Sally -- activates scooter listing
 *  19.  Card: THE LISTING GOES LIVE
 *  20.  Login as Sofia -- 12+ new cookie orders
 *  21.  Card: DELIVERY PROBLEM IS BACK
 *
 * ACT III -- JOHNNY RENTS THE SCOOTER (Scenes 22-24):
 *  22.  Login as Johnny -- sees Sally's scooter
 *  23.  Johnny rents the scooter (EUR 5/day + EUR 50 deposit)
 *  24.  Card: WHEELS
 *
 * ACT IV -- THE DELIVERY (Scenes 25-30):
 *  25.  Johnny's dashboard -- rental confirmed
 *  26.  Johnny delivers 12 cookie boxes (overlay count)
 *  27.  Card: WIND DOESN'T STOP WHEELS
 *  28.  Sofia's dashboard -- orders fulfilled
 *  29.  Johnny's dashboard -- earnings
 *  30.  Card: THE MATH WORKS (12 x 5 = 60, scooter 5, profit 55)
 *
 * ACT V -- THE WELD (Scenes 31-38):
 *  31.  Card: AFTER LUNCH -- Mike's Garage
 *  32.  Mike's workshop (MIG 200A, tools)
 *  33.  Mike does 5-second demo. Leo says "got it."
 *  34.  Leo welds the frame. Invisible. First try.
 *  35.  Mike: "How long have you been welding?!" Leo: "How long did that take?"
 *  36.  Mike refunds EUR 30 (Cancel & Refund button)
 *  37.  Mike looks up Leo on BorrowHood -- legend badge -- favorites him
 *  38.  THE GARAGE TALK -- Leo teaches Mike about liability waivers
 *  39.  Card: TWO TEACHERS
 *  40.  Back at Bottega -- sprocket, chain, tune gears. Bike reborn.
 *
 * EPILOGUE (Scenes 41-43):
 *  41.  Recap overlay
 *  42.  THE QUESTION (gold text) -- "What happens when a legend... fixes what everyone said was scrap?"
 *  43.  TO BE CONTINUED
 *
 * Usage: node record-the-scooter.js [base_url]
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
  // First scroll the element into view
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

  // Now get position after scroll
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
  console.log(`\n  THE SCOOTER -- Recording Script (S1 EP03)`);
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
    'linear-gradient(135deg, #1e3a5f 0%, #0c4a6e 30%, #0369a1 70%, #0ea5e9 100%)',
    'THE SCOOTER',
    'Season 1 \u00BB Episode 3',
    '<div class="extra">Wind, Wheels & a Welding Job</div>'
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
    'Sofia baked 5 cookie boxes. Pietro delivered them by drone.<br>' +
    'Johnny stood there with his broken bike watching the sky.<br>' +
    'He did nothing that day.<br><br>' +
    'Sally\'s cookie sales this week: <span class="hl">EUR 235</span><br>' +
    'A used electric scooter: <span class="hl">EUR 200</span><br><br>' +
    '<span class="dim">"What if the cookie queen... rented the wheels?"</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 4: LEONARDO CHARACTER OVERLAY (10s)
  // ============================================================
  console.log('\n  === ACT I: THE RESCUE ===\n');
  console.log('  Scene 4: Leonardo character card');
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  await showOverlay(page,
    'LEONARDO DA VINCI',
    'Legend. Moderator. The Original Maker.',
    'Born 1452. Still learning.<br>' +
    'Painter, inventor, engineer, anatomist.<br>' +
    'Runs Leonardo\'s Bottega on BorrowHood.<br><br>' +
    '<span class="hl">If it\'s broken, he sees a machine waiting to work again.</span>',
    12000
  );


  // ============================================================
  // SCENE 5: LOGIN AS LEONARDO -- HIS BOTTEGA (first time)
  // ============================================================
  console.log('  Scene 5: Login as Leonardo');
  await visibleLogin(page, 'leonardo');

  console.log('  Scene 5b: Leonardo\'s Bottega');
  await page.goto(`${BASE}/workshop/leonardos-bottega`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);
  await smoothScroll(page, 500);
  await sleep(4000);


  // ============================================================
  // SCENE 6: LEO BROWSES -- FINDS JOHNNY'S BROKEN BIKE
  // ============================================================
  console.log('  Scene 6: Leo browses, finds broken bike');
  await page.goto(`${BASE}/browse?q=bike`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Click into Johnny's broken bike listing
  await page.goto(`${BASE}/items/johnnys-delivery-bike-broken`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);
  await smoothScroll(page, 400);
  await sleep(4000);


  // ============================================================
  // SCENE 7: LEO FAVORITES + CLAIMS THE GIVEAWAY BIKE
  // ============================================================
  console.log('  Scene 7: Leo favorites the bike, then claims it');

  // 7a: Click the favorite heart on the bike page
  const bikeHeartPos = await page.evaluate(() => {
    const favBtn = document.querySelector('[x-data*="favorited"] button, button[\\@click*="toggleFav"]');
    if (favBtn) {
      favBtn.scrollIntoView({ block: 'center' });
      const box = favBtn.getBoundingClientRect();
      return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
    }
    return null;
  });
  if (bikeHeartPos) {
    await showRing(page, bikeHeartPos.x, bikeHeartPos.y);
    await sleep(400);
    await page.evaluate(() => {
      const btn = document.querySelector('[x-data*="favorited"] button, button[\\@click*="toggleFav"]');
      if (btn) btn.click();
    });
    console.log('  Favorited the bike');
    await sleep(3000);
  } else {
    console.log('  WARN: Favorite button not found on bike page');
  }

  // 7b: Click the "Claim This Item" button to open modal
  await clickWithRing(page, 'Claim', 'button, a');
  await sleep(2000);

  // 7c: Type a message in the claim modal textarea
  await page.evaluate(() => {
    const textarea = document.querySelector('textarea[x-model="rentalForm.message"]');
    if (textarea) {
      textarea.value = "Can I pick the bike up this morning? I'll be there in less than an hour.";
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  console.log('  Typed claim message');
  await sleep(3000);

  // 7d: Click the submit button in the modal
  let claimed = await clickWithRing(page, 'Claim', 'button');
  if (!claimed) {
    // Fallback: find submit button in modal by class
    await page.evaluate(() => {
      const modal = document.querySelector('[x-show="showRentalModal"]');
      if (modal) {
        const submitBtn = modal.querySelector('button.bg-green-600, button.bg-indigo-600');
        if (submitBtn) submitBtn.click();
      }
    });
    console.log('  Clicked modal submit (fallback)');
  }
  await sleep(3000);


  // ============================================================
  // SCENE 8-9: JOHNNY'S STORY (overlay)
  // ============================================================
  console.log('  Scene 8-9: Johnny\'s story');
  await showOverlay(page,
    'JOHNNY\'S STORY',
    'The scrap yard is across town.',
    '<div style="text-align:left; font-size:36px; line-height:1.8">' +
    'Half a day carrying it on his shoulder. For pennies.<br><br>' +
    'Johnny still loves this bike. The trailer hitch pulls his<br>' +
    'power washer, garden tools, heavy loads.<br><br>' +
    'He doesn\'t want to see it melted down.<br>' +
    'Maybe someone on BorrowHood can do something with it.<br><br>' +
    '<span class="dim">He thinks it\'s beyond repair.</span><br>' +
    '<span class="dim">He listed it for parts.</span></div>',
    14000
  );


  // ============================================================
  // SCENE 10: LEO WALKS AWAY -- MAKER BRAIN KICKS IN
  // ============================================================
  console.log('  Scene 10: Maker brain kicks in');
  await page.goto(card(
    'linear-gradient(135deg, #1c1917 0%, #292524 40%, #44403c 100%)',
    'THE WALK HOME',
    'Leo carries the bike on his shoulder.',
    '<div class="extra">He feels the frame. Runs his hand over the crack.<br><br>' +
    'His maker brain kicks in:<br>' +
    '<span class="hl">"This frame needs a weld.<br>Maybe I should take a welding lesson."</span><br><br>' +
    'Leo pulls out his phone.</div>'
  ));
  await sleep(12000);


  // ============================================================
  // SCENE 11: LEO FINDS MIKE'S WELDING COURSE ON BORROWHOOD
  // ============================================================
  console.log('  Scene 11: Leo finds Mike\'s welding course');
  await page.goto(`${BASE}/items/welding-machine-mig-200a`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);
  await smoothScroll(page, 400);
  await sleep(3000);


  // ============================================================
  // SCENE 12: MIKE CHARACTER OVERLAY
  // ============================================================
  console.log('  Scene 12: Mike character card');
  await showOverlay(page,
    'MIKE KENEL',
    'Pillar. Garage Guy. "If it\'s broken, I can fix it."',
    'Mechanic by trade. Tinkerer by nature.<br>' +
    'Inherited his father\'s tool collection -- 500 tools,<br>' +
    'every one with a story.<br><br>' +
    '<span class="hl">MIG 200A welder. 3-hour training: EUR 30.</span><br>' +
    '<span class="dim">"NOT for beginners -- unless you\'re Leonardo da Vinci."</span>',
    12000
  );


  // ============================================================
  // SCENE 13: LEO BOOKS THE TRAINING
  // ============================================================
  console.log('  Scene 13: Leo books training');
  // Navigate back to Mike's item page (overlay replaced it)
  await page.goto(`${BASE}/items/welding-machine-mig-200a`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // The welding item has RENT as primary listing, so button says "Rent This Item"
  // Try all possible button texts
  let booked = await clickWithRing(page, 'Book This Service', 'button, a');
  if (!booked) booked = await clickWithRing(page, 'Rent This Item', 'button, a');
  if (!booked) booked = await clickWithRing(page, 'Rent', 'button, a');
  await sleep(2000);

  // If a modal opened, fill in message and dates, then submit
  if (booked) {
    await sleep(1500); // Wait for Alpine to render modal

    // Fill in the message
    await page.evaluate(() => {
      const modal = document.querySelector('[x-show="showRentalModal"]');
      if (modal) {
        const textarea = modal.querySelector('textarea');
        if (textarea) {
          textarea.value = "Hi Mike, I'd like to book the 3-hour welding course. Can I come by this afternoon? Thanks, Leo";
          textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
        // Fill in dates (today and today)
        const dateInputs = modal.querySelectorAll('input[type="date"]');
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(inp => {
          inp.value = today;
          inp.dispatchEvent(new Event('input', { bubbles: true }));
          inp.dispatchEvent(new Event('change', { bubbles: true }));
        });
      }
    });
    console.log('  Typed booking message for Mike');
    await sleep(3000);

    // Submit
    let sent = await clickWithRing(page, 'Send Booking Request', 'button');
    if (!sent) sent = await clickWithRing(page, 'Send Request', 'button');
    if (!sent) {
      await page.evaluate(() => {
        const modal = document.querySelector('[x-show="showRentalModal"]');
        if (modal) {
          const submitBtn = modal.querySelector('button.bg-indigo-600, button.bg-green-600');
          if (submitBtn) submitBtn.click();
        }
      });
      console.log('  Clicked modal submit (fallback)');
    }
  }
  await sleep(3000);

  await showOverlay(page,
    'BOOKED',
    'Mike\'s 3-Hour Welding Course -- EUR 30',
    '<span class="hl">"The cracked Bianchi frame is the perfect training project."</span><br><br>' +
    '<span class="dim">Leo books it right there on the street, phone in one hand,<br>' +
    'broken bike on his shoulder.</span>',
    10000
  );


  // ============================================================
  // SCENE 14: TRANSITION CARD
  // ============================================================
  console.log('  Scene 14: Transition');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    'ACT I \u00BB COMPLETE',
    'Leo walks the bike to Mike\'s Garage.',
    '<div class="extra">It\'s on the way home.<br>' +
    '<span class="dim">Mike will take him after lunch.</span></div>'
  ));
  await sleep(8000);


  // ============================================================
  // SCENE 15: TRAPANI WIND CARD
  // ============================================================
  console.log('\n  === ACT II: THE WIND ===\n');
  console.log('  Scene 15: Wind card');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #0c4a6e 40%, #164e63 100%)',
    'ACT II \u00BB THE WIND',
    'Trapani. 50 km/h gusts.',
    '<div class="extra">Mediterranean fury. Salt spray. Shutters rattling.<br>' +
    'Not a day for flying.<br><br>' +
    '<span class="dim">But wheels don\'t care about wind.</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 16: LOGIN AS PIETRO -- DRONE GROUNDED
  // ============================================================
  console.log('  Scene 16: Login as Pietro');
  await visibleLogin(page, 'pietro');

  console.log('  Scene 16b: Pietro\'s workshop -- drone fleet');
  await page.goto(`${BASE}/workshop/pietros-drones`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  await showOverlay(page,
    'GROUNDED',
    'Pietro\'s DJI Mini 4 Pro stays in the case today.',
    '50 km/h gusts. EU A1/A3 regulations say no.<br>' +
    'Common sense says no.<br><br>' +
    '<span class="red">No drone delivery today.</span>',
    10000
  );


  // ============================================================
  // SCENE 17: WIND CARD
  // ============================================================
  console.log('  Scene 17: Wind doesn\'t care card');
  await page.goto(card(
    'linear-gradient(135deg, #164e63 0%, #0e7490 100%)',
    'NO FLIGHT TODAY',
    '"The wind doesn\'t care about your drone license."',
    ''
  ));
  await sleep(8000);


  // ============================================================
  // SCENE 18-19: LOGIN AS SALLY -- ACTIVATE SCOOTER
  // ============================================================
  console.log('  Scene 18: Login as Sally');
  await visibleLogin(page, 'sally');

  console.log('  Scene 18b: Sally\'s dashboard');
  await goToDashboardTab(page, 'My Items');
  await sleep(3000);

  // Navigate to Sally's scooter listing
  console.log('  Scene 19: Activate scooter listing');
  await page.goto(`${BASE}/items/sallys-electric-scooter-for-delivery`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Actually activate the listing via API
  // First find the listing ID
  const sallyListings = await apiCall(page, 'GET', '/api/v1/listings?owner=me', null);
  const scooterListing = sallyListings.data?.find(l => l.listing_type === 'rent');
  if (scooterListing) {
    const activateResult = await apiCall(page, 'PATCH', `/api/v1/listings/${scooterListing.id}`, { status: 'active' });
    console.log('  Scooter activated:', activateResult.status);
    // Reload page to show active state
    await page.goto(`${BASE}/items/sallys-electric-scooter-for-delivery`, { waitUntil: 'networkidle2', timeout: 15000 });
    await setZoom(page);
    await sleep(3000);
  } else {
    console.log('  WARN: Could not find scooter rent listing to activate');
  }

  await showOverlay(page,
    'THE LISTING GOES LIVE',
    'Sally activates her electric scooter.',
    '<div style="text-align:left; font-size:36px; line-height:2">' +
    '<span class="green">Item:</span> Electric Scooter (Used -- Perfect for Deliveries)<br>' +
    '<span class="green">Price:</span> <span class="hl">EUR 5/day</span><br>' +
    '<span class="green">Deposit:</span> EUR 50<br>' +
    '<span class="green">Status:</span> PAUSED \u2192 <span class="green">ACTIVE</span><br><br>' +
    '<span class="dim">Sally invested EUR 200 in the scooter.<br>' +
    '40 rentals and it pays for itself.</span></div>',
    12000
  );


  // ============================================================
  // SCENE 20: LOGIN AS SOFIA -- COOKIE ORDERS
  // ============================================================
  console.log('  Scene 20: Login as Sofia');
  await visibleLogin(page, 'sofiaferretti');

  console.log('  Scene 20b: Sofia\'s dashboard');
  await goToDashboardTab(page, 'Incoming');
  await sleep(4000);

  await showOverlay(page,
    'ORDERS POURING IN',
    'Sofia has 12 new cookie orders.',
    '12 addresses across Trapani.<br>' +
    'EUR 15 per box. EUR 180 in revenue.<br><br>' +
    'But the drone is grounded.<br>' +
    '<span class="red">Who delivers?</span>',
    10000
  );


  // ============================================================
  // SCENE 21: DELIVERY PROBLEM CARD
  // ============================================================
  console.log('  Scene 21: Delivery problem card');
  await page.goto(card(
    'linear-gradient(135deg, #7f1d1d 0%, #991b1b 40%, #b91c1c 100%)',
    'THE PROBLEM',
    'No drone. No bike. 12 boxes. 12 addresses.',
    '<div class="extra"><span class="dim">Sound familiar?</span></div>'
  ));
  await sleep(8000);


  // ============================================================
  // SCENE 22-23: JOHNNY RENTS THE SCOOTER
  // ============================================================
  console.log('\n  === ACT III: JOHNNY RENTS THE SCOOTER ===\n');
  console.log('  Scene 22: Login as Johnny');
  await visibleLogin(page, 'john');

  console.log('  Scene 22b: Johnny finds Sally\'s scooter');
  await page.goto(`${BASE}/items/sallys-electric-scooter-for-delivery`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  console.log('  Scene 23: Johnny rents the scooter');
  const rented = await clickWithRing(page, 'Rent This Item', 'button, a');
  if (!rented) {
    await clickWithRing(page, 'Rent', 'button, a');
  }
  await sleep(2000); // Wait for modal + Alpine.js to render

  // Fill in the message and dates
  await page.evaluate(() => {
    const modal = document.querySelector('[x-show="showRentalModal"]');
    if (modal) {
      const textarea = modal.querySelector('textarea');
      if (textarea) {
        textarea.value = "Hi Sally, I need the scooter for deliveries today. Can I pick it up this morning? Thanks, Johnny";
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const dateInputs = modal.querySelectorAll('input[type="date"]');
      const today = new Date().toISOString().split('T')[0];
      dateInputs.forEach(inp => {
        inp.value = today;
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }
  });
  console.log('  Typed rental message for Sally');
  await sleep(3000);

  // Submit
  let sentRental = await clickWithRing(page, 'Send Request', 'button');
  if (!sentRental) {
    await page.evaluate(() => {
      const modal = document.querySelector('[x-show="showRentalModal"]');
      if (modal) {
        const submitBtn = modal.querySelector('button.bg-indigo-600, button.bg-green-600');
        if (submitBtn) submitBtn.click();
      }
    });
    console.log('  Clicked modal submit (fallback)');
  }
  await sleep(3000);


  // ============================================================
  // SCENE 24: WHEELS CARD
  // ============================================================
  console.log('  Scene 24: Wheels card');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #047857 40%, #10b981 100%)',
    'WHEELS',
    'Sally\'s electric scooter. EUR 5/day. EUR 50 deposit.',
    '<div class="extra">No broken chains.<br>No cracked frames.<br>No excuses.<br><br>' +
    '<span class="hl">Johnny has wheels.</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 25: JOHNNY'S DASHBOARD -- RENTAL CONFIRMED
  // ============================================================
  console.log('\n  === ACT IV: THE DELIVERY ===\n');
  console.log('  Scene 25: Johnny\'s dashboard');
  await goToDashboardTab(page, 'My Orders');
  await sleep(4000);


  // ============================================================
  // SCENE 26-27: DELIVERY MONTAGE
  // ============================================================
  console.log('  Scene 26: Delivery montage');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #065f46 40%, #047857 100%)',
    'FIRST RIDE',
    'Cookie boxes loaded. Scooter charged.',
    '<div class="extra">Johnny knows every street in Trapani.<br>' +
    'Every shortcut. Every broken doorbell.<br><br>' +
    '<span class="hl">Now he has wheels that match his knowledge.</span></div>'
  ));
  await sleep(10000);

  console.log('  Scene 27: Deliveries counting');
  await showOverlay(page,
    'DELIVERIES',
    'Wind doesn\'t stop wheels.',
    '<div style="text-align:left; font-size:36px; line-height:2">' +
    'Delivery 1: Via Roma -- <span class="green">delivered</span><br>' +
    'Delivery 2: Via Garibaldi -- <span class="green">delivered</span><br>' +
    'Delivery 3: Via Torrearsa -- <span class="green">delivered</span><br>' +
    'Delivery 4: Piazza Mercato -- <span class="green">delivered</span><br>' +
    'Delivery 5: Via Fardella -- <span class="green">delivered</span><br>' +
    'Delivery 6: Corso Italia -- <span class="green">delivered</span><br>' +
    'Delivery 7: Via Pepoli -- <span class="green">delivered</span><br>' +
    'Delivery 8: Lungomare -- <span class="green">delivered</span><br>' +
    'Delivery 9: Via Ammiraglio -- <span class="green">delivered</span><br>' +
    'Delivery 10: Piazza Vittorio -- <span class="green">delivered</span><br>' +
    'Delivery 11: Via Libertà -- <span class="green">delivered</span><br>' +
    'Delivery 12: Via San Francesco -- <span class="green">delivered</span></div>',
    16000
  );


  // ============================================================
  // SCENE 28: WIND DOESN'T STOP WHEELS
  // ============================================================
  console.log('  Scene 28: Wind card');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #047857 100%)',
    'WIND DOESN\'T',
    'STOP WHEELS',
    '<div class="extra">50 km/h gusts off the Mediterranean.<br>' +
    'The scooter cuts through. No pedaling. No sweat.<br><br>' +
    '<span class="hl">12 for 12.</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 29: SOFIA'S DASHBOARD -- ORDERS FULFILLED
  // ============================================================
  console.log('  Scene 29: Sofia\'s dashboard');
  await visibleLogin(page, 'sofiaferretti');
  await goToDashboardTab(page, 'Incoming');
  await sleep(4000);


  // ============================================================
  // SCENE 30: THE MATH WORKS
  // ============================================================
  console.log('  Scene 30: The Math Works');
  await page.goto(card(
    'linear-gradient(135deg, #064e3b 0%, #065f46 40%, #047857 100%)',
    'THE MATH WORKS',
    '',
    '<div class="extra" style="text-align:left; font-size:40px; line-height:2">' +
    '12 deliveries x EUR 5 = <span class="green">EUR 60</span><br>' +
    'Scooter rental: <span class="red">EUR 5/day</span><br>' +
    'Day profit: <span class="hl">EUR 55</span><br><br>' +
    '<span class="dim">On the old bike?</span><br>' +
    '<span class="dim">Maybe 3-4 deliveries. Pedaling into Trapani wind.</span><br>' +
    '<span class="dim">EUR 15-20/day. Maybe.</span><br><br>' +
    '<span class="hl">The scooter is 3x the money.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 31: AFTER LUNCH -- MIKE'S GARAGE
  // ============================================================
  console.log('\n  === ACT V: THE WELD ===\n');
  console.log('  Scene 31: After lunch card');
  await page.goto(card(
    'linear-gradient(135deg, #422006 0%, #78350f 40%, #a16207 100%)',
    'ACT V \u00BB THE WELD',
    'After lunch. Mike\'s Garage.',
    '<div class="extra">The MIG 200A is ready.<br>' +
    'The cracked Bianchi frame is on the workbench.<br><br>' +
    '<span class="dim">Time to learn.</span></div>'
  ));
  await sleep(10000);


  // ============================================================
  // SCENE 32: MIKE'S WORKSHOP
  // ============================================================
  console.log('  Scene 32: Mike\'s workshop');
  await visibleLogin(page, 'mike');

  await page.goto(`${BASE}/workshop/mikes-garage`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);
  await smoothScroll(page, 500);
  await sleep(4000);


  // ============================================================
  // SCENE 33-35: THE 5-SECOND WELD
  // ============================================================
  console.log('  Scene 33: Mike demos');
  await showOverlay(page,
    'THE 3-HOUR COURSE',
    'First lesson: Mike does a 5-second stitch weld on scrap metal.',
    '<div style="text-align:left; font-size:36px; line-height:1.8">' +
    'MIG 200A welder. Scrap steel plate. One demo.<br><br>' +
    '"Torch here. Watch the puddle. Run the bead.<br>' +
    'That\'s all there is to it."<br><br>' +
    '<span class="hl">5 seconds. One clean bead.</span><br>' +
    '<span class="dim">The 3-hour course just started.</span></div>',
    10000
  );

  console.log('  Scene 34: Leo nails it');
  await showOverlay(page,
    'LEO WELDS',
    '"Got it."',
    'Leo takes the welder.<br>' +
    'Lines up the cracked Bianchi frame.<br>' +
    'Runs one bead along the crack.<br><br>' +
    '<span class="hl">Perfect. Invisible. First try.</span><br><br>' +
    '<span class="dim">Because he\'s Leonardo da Vinci.</span>',
    12000
  );

  console.log('  Scene 35: Mike\'s reaction');
  await showOverlay(page,
    '"HOW LONG HAVE YOU BEEN WELDING?!"',
    '',
    '<div style="font-size:48px; line-height:1.8">' +
    '<span class="hl">Leo:</span> "How long did that take?"<br><br>' +
    '<span class="dim">They both laugh.</span><br><br>' +
    'Mike: "Bro, you still want the 3-hour course?<br>' +
    'You don\'t need it. I can\'t charge you for 5 minutes."</div>',
    12000
  );


  // ============================================================
  // SCENE 36: MIKE REFUNDS -- CANCEL & REFUND BUTTON
  // ============================================================
  console.log('  Scene 36: Mike refunds');
  // Mike is logged in. Go to dashboard incoming requests
  await goToDashboardTab(page, 'Incoming');
  await sleep(3000);

  // First approve Leo's booking (it's PENDING, needs APPROVED before Cancel & Refund shows)
  const approved = await clickWithRing(page, 'Approve', 'button');
  if (approved) {
    console.log('  Approved Leo\'s booking');
    await sleep(3000);
    // Page should refresh/update -- reload to see Cancel & Refund button
    await goToDashboardTab(page, 'Incoming');
    await sleep(3000);
  }

  // Register dialog handler BEFORE clicking (confirm dialog fires during click)
  page.once('dialog', async dialog => {
    await dialog.accept();
  });

  // Click "Cancel & Refund" on Leo's now-approved booking
  await clickWithRing(page, 'Cancel & Refund', 'button');
  await sleep(3000);

  await showOverlay(page,
    'FULL REFUND',
    'EUR 30 returned to Leonardo.',
    'Service paid. Service not needed.<br>' +
    'Mike can\'t charge for 5 minutes of training<br>' +
    'when the student is Leonardo da Vinci.<br><br>' +
    '<span class="dim">The platform handles it. One click.</span>',
    10000
  );


  // ============================================================
  // SCENE 37: MIKE LOOKS UP LEO ON BORROWHOOD
  // ============================================================
  console.log('  Scene 37: Mike looks up Leo');
  await page.goto(`${BASE}/workshop/leonardos-bottega`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(5000);

  // Click the favorite heart button (SVG icon, no text -- find by title or parent x-data)
  const heartPos = await page.evaluate(() => {
    // Find the workshopFavorite button by its surrounding x-data
    const favDiv = document.querySelector('[x-data*="workshopFavorite"]');
    if (favDiv) {
      const btn = favDiv.querySelector('button');
      if (btn) {
        btn.scrollIntoView({ block: 'center' });
        const box = btn.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  });
  if (heartPos) {
    await showRing(page, heartPos.x, heartPos.y);
    await sleep(400);
    await page.evaluate(() => {
      const favDiv = document.querySelector('[x-data*="workshopFavorite"]');
      if (favDiv) { const btn = favDiv.querySelector('button'); if (btn) btn.click(); }
    });
    console.log('  Clicked favorite heart');
  } else {
    console.log('  WARN: Could not find favorite heart button');
  }
  await sleep(3000);

  await showOverlay(page,
    'THE REAL McCOY',
    'Mike looks up Leo on BorrowHood.',
    '<div style="text-align:left; font-size:36px; line-height:2">' +
    'Badge: <span class="hl">LEGEND</span><br>' +
    'Points: <span class="hl">1,400</span><br>' +
    'Reviews: <span class="hl">45</span><br>' +
    'Role: <span class="hl">Moderator</span><br><br>' +
    '<span class="dim">Mike favorites Leo.</span><br>' +
    '<span class="dim">The wheels start turning in Mike\'s head.</span><br>' +
    '<span class="dim">"I could learn from this guy."</span></div>',
    12000
  );

  // Scroll through Leo's offerings
  await smoothScroll(page, 600);
  await sleep(4000);


  // ============================================================
  // SCENE 38: THE GARAGE TALK -- LIABILITY WAIVERS
  // ============================================================
  console.log('  Scene 38: Garage talk');
  await showOverlay(page,
    'THE GARAGE TALK',
    'While the weld cools.',
    '<div style="text-align:left; font-size:32px; line-height:1.8">' +
    '<span class="hl">Mike:</span> "I only list some of my stuff. I\'ve got a wood chipper,<br>' +
    'a concrete saw, heavy power tools -- but I\'m afraid<br>' +
    'someone will get hurt and I\'ll be liable."<br><br>' +
    '<span class="hl">Leo:</span> "Have them sign a rental agreement.<br>' +
    'Rent at your own risk. There are special insurances<br>' +
    'for exactly this. If they hurt themselves, that\'s on them --<br>' +
    'as long as you\'ve got the paperwork."<br><br>' +
    '<span class="green">Mike didn\'t know that.</span><br>' +
    '<span class="green">Leo just unlocked 20 more listings for Mike\'s Garage.</span></div>',
    16000
  );


  // ============================================================
  // SCENE 39: TWO TEACHERS CARD
  // ============================================================
  console.log('  Scene 39: Two teachers card');
  await page.goto(card(
    'linear-gradient(135deg, #422006 0%, #78350f 40%, #a16207 100%)',
    'TWO TEACHERS',
    '',
    '<div class="extra">Mike taught Leo to weld in <span class="hl">5 seconds</span>.<br>' +
    'Leo taught Mike about liability in <span class="hl">5 minutes</span>.<br><br>' +
    'Mike made EUR 0 today.<br>' +
    'But gained a legend as a favorite,<br>' +
    '20 new listings to post,<br>' +
    'and a connection who knows business.<br><br>' +
    '<span class="dim">Priceless.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 40: BACK AT BOTTEGA -- SPROCKET & CHAIN
  // ============================================================
  console.log('  Scene 40: Bottega rebuild');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    'THE BOTTEGA',
    'Leo finishes the job.',
    '<div class="extra" style="text-align:left; font-size:36px; line-height:1.8">' +
    '<span class="check">&#10003;</span> Frame welded -- invisible joint<br>' +
    '<span class="check">&#10003;</span> Sprocket replaced from Leo\'s own stock<br>' +
    '<span class="dim">(That\'s why the chain kept snapping -- bad sprocket all along)</span><br>' +
    '<span class="check">&#10003;</span> New chain installed<br>' +
    '<span class="check">&#10003;</span> Gears tuned<br><br>' +
    '<span class="hl">The Bianchi Kuma 26 is reborn.</span></div>'
  ));
  await sleep(14000);


  // ============================================================
  // SCENE 41: EPILOGUE -- RECAP
  // ============================================================
  console.log('\n  === EPILOGUE ===\n');
  console.log('  Scene 41: Recap');
  await page.goto(card(
    'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    'EPILOGUE',
    'Every problem opens a door.',
    '<div class="extra" style="text-align:left; font-size:30px; line-height:1.6">' +
    'Leo grabbed Johnny\'s broken bike -- <span class="green">FREE</span><br>' +
    'Leo booked Mike\'s welding course -- <span class="red">EUR 30</span><br>' +
    'Leo welded the frame in 5 seconds -- <span class="green">REFUND</span><br>' +
    'Mike refunded EUR 30 -- <span class="green">can\'t charge for 5 minutes</span><br>' +
    'Leo replaced the sprocket -- <span class="green">FREE</span> (from his stock)<br>' +
    'Sally activated her scooter -- <span class="hl">EUR 5/day</span><br>' +
    'Johnny rented the scooter -- <span class="red">EUR 5</span><br>' +
    'Johnny delivered 12 cookie boxes -- <span class="green">EUR 60</span><br>' +
    '<span class="hl">Johnny:</span> +EUR 60 deliveries, -EUR 5 scooter = <span class="green">+EUR 55</span><br>' +
    '<span class="hl">Leo:</span> -EUR 30 training, +EUR 30 refund = <span class="green">EUR 0</span> and a new skill<br>' +
    '<span class="hl">Mike:</span> EUR 0 cash + Leo as a favorite + legal knowledge = <span class="green">priceless</span><br>' +
    '<span class="hl">Sally:</span> EUR 5/day passive income<br>' +
    '<span class="dim">Two transactions. Five people. The bike is reborn. Johnny doesn\'t know yet.</span></div>'
  ));
  await sleep(10000);
  await smoothScroll(page, 300);
  await sleep(10000);


  // ============================================================
  // SCENE 42: THE QUESTION (gold text, 16s)
  // ============================================================
  console.log('  Scene 42: The Question');
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
    The Bianchi sits in <span class="name">Leonardo's</span> Bottega. Welded. New sprocket. New chain.<br>
    <span class="name">Johnny</span> is out delivering on <span class="name">Sally's</span> scooter. Making EUR 55 a day.<br>
    He thinks his bike is scrap metal in someone's garage.<br>
    He doesn't know Leo fixed it. He doesn't know it's better than new.
  </div>
  <div class="question">What happens when a legend... fixes what everyone said was scrap?</div>
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
