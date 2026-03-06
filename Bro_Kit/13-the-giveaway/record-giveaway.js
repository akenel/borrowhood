#!/usr/bin/env node
/**
 * THE GIVEAWAY -- Recording Script (Take 2)
 *
 * Free items: claim, approve, auto-complete. No pricing, no deposits.
 * Uses demoLogin() for user switching (fast, no Keycloak form).
 *
 * Take 2 fixes:
 *   - Google Translate popup blocked (--disable-features=TranslateUI)
 *   - charset=utf-8 in data: URLs (no mojibake)
 *   - Card body padding fixed (no text overflow)
 *   - Click rings on all interactions (Rule 3)
 *   - Added: Notification bell scene (Mike sees Sally's claim)
 *   - Garden hose images updated in DB (3 real hose photos)
 *
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- emerald green
 *   3.  Browse page -- giveaway items with FREE badges
 *   4.  Mike's Garden Hose detail -- 3-photo gallery, Claim button
 *   5.  Character card: Sally Thompson
 *   6.  Login as Sally, claim the garden hose (modal + message)
 *   7.  Character card: Mike Kenel (owner)
 *   8.  Login as Mike, NOTIFICATION BELL, approve claim
 *   9.  Grace Hopper's giveaway -- Nanosecond Wire
 *  10.  List Item form -- "Give Away" option, price hidden
 *  11.  Browse Italian -- "Regalo" labels
 *  12.  GREEN "FEATURE COMPLETE" card
 *
 * Usage: node record-giveaway.js [base_url]
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
  h2 { font-size: 64px; font-weight: 400; opacity: 0.9; margin-bottom: 20px; line-height: 1.2; }
  .extra { font-size: 48px; opacity: 0.7; margin-top: 16px; line-height: 1.4; max-width: 1600px; }
  .badge { display: inline-block; padding: 12px 32px; border-radius: 12px; background: rgba(255,255,255,0.2); font-size: 48px; font-weight: 700; margin-top: 24px; }
  .hl { color: #6EE7B7; font-weight: 700; }
  .check { color: #34D399; }
  .dim { opacity: 0.5; }
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

// ── DOM overlay (stays on BASE origin) ─
async function showOverlay(page, name, subtitle, extra = '', duration = 5000) {
  // Reset zoom so the overlay text doesn't overflow at 150%
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
    `;
    overlay.innerHTML = `
      <h1 style="font-size:128px; font-weight:900; margin-bottom:24px;
                 text-shadow:4px 4px 16px rgba(0,0,0,0.4); letter-spacing:-3px">${n}</h1>
      <h2 style="font-size:64px; font-weight:400; opacity:0.9;
                 margin-bottom:20px">${s}</h2>
      ${e ? `<div style="font-size:48px; opacity:0.7; margin-top:16px; line-height:1.4">${e}</div>` : ''}
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

// ── Language banner ─
async function showLangBanner(page, flag, langName, duration = 3000) {
  await page.evaluate((f, ln) => {
    const old = document.getElementById('lang-banner');
    if (old) old.remove();

    const banner = document.createElement('div');
    banner.id = 'lang-banner';
    banner.style.cssText = `
      position: fixed; top: 30px; right: 30px; z-index: 99999;
      display: flex; align-items: center; gap: 16px;
      padding: 20px 36px; border-radius: 16px;
      background: rgba(0,0,0,0.9); color: white;
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 36px; font-weight: 700;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      animation: slideIn 0.4s ease-out;
    `;
    banner.innerHTML = `<span style="font-size:48px">${f}</span> ${ln}`;

    const style = document.createElement('style');
    style.textContent = `@keyframes slideIn { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`;
    banner.appendChild(style);
    document.body.appendChild(banner);

    setTimeout(() => {
      banner.style.transition = 'opacity 0.5s';
      banner.style.opacity = '0';
      setTimeout(() => banner.remove(), 600);
    }, 4000);
  }, flag, langName);
  await sleep(duration);
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

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  THE GIVEAWAY -- Recording Script (Take 2)`);
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
    '<div class="extra">THE GIVEAWAY | BorrowHood | Take 2</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: FEATURE INTRO (EMERALD GREEN) -- 8s
  // ============================================================
  console.log('  Scene 2: Intro');
  await page.goto(card(
    '#059669',
    'THE GIVEAWAY',
    'Free Items. Claim. Pick Up. Done.',
    '<div class="badge">NEW FEATURE</div>' +
    '<div class="extra" style="margin-top:24px">' +
    'No pricing. No deposits. No return dates.<br>' +
    'One click to claim. One click to approve.' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 3: BROWSE -- giveaway items visible -- 8s
  // ============================================================
  console.log('  Scene 3: Browse page with giveaway items');
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Scroll to find giveaway items (FREE badges)
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a, .grid > div');
    for (const c of cards) {
      if (c.textContent.includes('FREE') || c.textContent.includes('Give Away') || c.textContent.includes('Garden Hose')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(5000);

  // ============================================================
  // SCENE 4: ITEM DETAIL -- Garden Hose (Mike's giveaway) -- 8s
  // ============================================================
  console.log('  Scene 4: Garden hose detail');
  await page.goto(`${BASE}/items/garden-hose-30m-free?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Click through the image gallery (show multiple photos)
  console.log('  Scene 4b: Gallery navigation');
  const nextArrow = await page.$('button[\\@click="next()"]');
  if (nextArrow) {
    const box = await nextArrow.boundingBox();
    if (box) {
      await showRing(page, box.x + box.width / 2, box.y + box.height / 2);
      await sleep(400);
      await nextArrow.click();
      await sleep(2000);
      await showRing(page, box.x + box.width / 2, box.y + box.height / 2);
      await sleep(400);
      await nextArrow.click();
      await sleep(2000);
    }
  }

  // Scroll to see the FREE badge and Claim button
  await smoothScroll(page, 300, 1500);
  await sleep(3000);

  // ============================================================
  // SCENE 5: CHARACTER CARD -- Sally Thompson -- 5s
  // ============================================================
  console.log('  Scene 5: Sally character card');
  await showOverlay(page,
    'SALLY THOMPSON',
    'She wants the garden hose.',
    'One click to claim it.'
  );

  // ============================================================
  // SCENE 6: LOGIN AS SALLY + CLAIM -- 15s
  // ============================================================
  console.log('  Scene 6: Login as Sally, claim');
  await demoLogin(page, 'sally');

  // Navigate to the giveaway item
  await page.goto(`${BASE}/items/garden-hose-30m-free?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Scroll to Claim button
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Claim')) {
        b.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(2000);

  // Click "Claim This Item" with ring
  console.log('  Scene 6b: Click Claim');
  try {
    await clickWithRing(page, 'Claim', 'button');
    await sleep(500);

    // Type claim message
    console.log('  Scene 6c: Typing claim message');
    const textarea = await page.$('.fixed textarea');
    if (textarea) {
      await textarea.click();
      await page.type('.fixed textarea',
        "Hi Mike! I would love this hose for my garden. Can pick up this weekend!",
        { delay: 35 }
      );
      await sleep(3000);

      // Submit claim
      console.log('  Scene 6d: Submit claim');
      await page.evaluate(() => {
        const fixeds = document.querySelectorAll('.fixed');
        for (const f of fixeds) {
          if (!f.querySelector('textarea')) continue;
          const btns = f.querySelectorAll('button');
          for (const b of btns) {
            if (b.textContent.includes('Claim')) { b.click(); return; }
          }
        }
      });
      await sleep(3000);
    } else {
      console.log('    No textarea found in modal');
    }
  } catch (err) {
    console.log(`    Claim error: ${err.message.slice(0, 80)}`);
  }
  await sleep(2000);

  // ============================================================
  // SCENE 7: CHARACTER CARD -- Mike Kenel (owner) -- 5s
  // ============================================================
  console.log('  Scene 7: Mike character card');
  await demoLogout(page);

  // Navigate back to BASE to keep cookie domain
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(300);

  await showOverlay(page,
    'MIKE KENEL',
    'Item owner sees the claim request.',
    'One click to approve. Auto-completes.'
  );

  // ============================================================
  // SCENE 8: LOGIN AS MIKE + NOTIFICATION BELL + APPROVE -- 15s
  // ============================================================
  console.log('  Scene 8: Login as Mike, check notifications');
  await demoLogin(page, 'mike');

  // Go to browse first -- show navbar with notification bell
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Click the notification bell (shows unread count)
  console.log('  Scene 8b: Notification bell');
  const bellPos = await page.evaluate(() => {
    const notifDiv = document.querySelector('[x-data*="notifications"]');
    if (notifDiv) {
      const btn = notifDiv.querySelector('button');
      if (btn) {
        const box = btn.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  });
  if (bellPos) {
    await showRing(page, bellPos.x, bellPos.y);
    await sleep(400);
    await page.evaluate(() => {
      const notifDiv = document.querySelector('[x-data*="notifications"]');
      if (notifDiv) { const btn = notifDiv.querySelector('button'); if (btn) btn.click(); }
    });
    await sleep(4000);  // Show the dropdown with Sally's claim notification

    // Close dropdown
    await page.evaluate(() => document.body.click());
    await sleep(1000);
  } else {
    console.log('  WARN: Notification bell not found');
  }

  // Dashboard -- incoming requests
  console.log('  Scene 8c: Dashboard incoming requests');
  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Click "Incoming Requests" tab with ring
  await clickWithRing(page, 'Incoming', 'button, a, [role="tab"]');
  await sleep(3000);

  // Find Garden Hose claim and Approve with ring
  console.log('  Scene 8d: Approve garden hose');
  try {
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white, [class*="rounded-lg"]');
      for (const row of rows) {
        if (row.textContent.includes('Garden Hose') || row.textContent.includes('garden')) {
          row.scrollIntoView({ behavior: 'smooth', block: 'center' });
          break;
        }
      }
    });
    await sleep(2000);

    // Click Approve with ring
    const approvePos = await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white, [class*="rounded-lg"]');
      for (const row of rows) {
        if (row.textContent.includes('Garden Hose') || row.textContent.includes('garden')) {
          const btns = row.querySelectorAll('button');
          for (const b of btns) {
            if (b.textContent.trim() === 'Approve' || b.textContent.includes('Approve')) {
              const box = b.getBoundingClientRect();
              return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
            }
          }
        }
      }
      return null;
    });
    if (approvePos) {
      await showRing(page, approvePos.x, approvePos.y);
      await sleep(400);
      await page.evaluate(() => {
        const rows = document.querySelectorAll('.bg-white, [class*="rounded-lg"]');
        for (const row of rows) {
          if (row.textContent.includes('Garden Hose') || row.textContent.includes('garden')) {
            const btns = row.querySelectorAll('button');
            for (const b of btns) {
              if (b.textContent.trim() === 'Approve' || b.textContent.includes('Approve')) { b.click(); return; }
            }
          }
        }
      });
    }

    try {
      await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
    } catch (e) { /* page may not navigate */ }
    await sleep(3000);
    console.log('  Scene 8e: Giveaway auto-completed');
  } catch (err) {
    console.log(`    Approve error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 9: GRACE HOPPER'S GIVEAWAY -- Nanosecond Wire -- 7s
  // ============================================================
  console.log('  Scene 9: Grace Hopper giveaway');
  await demoLogout(page);
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(300);

  await showOverlay(page,
    'GRACE HOPPER',
    'The Queen of Code',
    'Her giveaway: Nanosecond Wire -- Teaching Aid'
  );

  await page.goto(`${BASE}/items/nanosecond-wire-teaching-aid?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);
  await smoothScroll(page, 400);
  await sleep(3000);

  // ============================================================
  // SCENE 10: LIST ITEM FORM -- "Give Away" option -- 8s
  // ============================================================
  console.log('  Scene 10: List item form');
  await demoLogin(page, 'sally');

  await page.goto(`${BASE}/list?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2500);

  // Show how the Give Away option works
  try {
    // Type item name
    const nameInput = await page.$('input[type="text"]');
    if (nameInput) {
      await page.type('input[type="text"]', 'Old Table Lamp', { delay: 40 });
      await sleep(1000);
    }

    // Click Next to step 2
    await clickWithRing(page, 'Next', 'button');
    await sleep(1000);

    // Click "Give Away" option with ring
    const gaPos = await page.evaluate(() => {
      const labels = document.querySelectorAll('label, button, [role="radio"]');
      for (const l of labels) {
        if (l.textContent.includes('Give Away') || l.textContent.includes('Giveaway')) {
          const box = l.getBoundingClientRect();
          return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        }
      }
      return null;
    });
    if (gaPos) {
      await showRing(page, gaPos.x, gaPos.y);
      await sleep(400);
      await page.evaluate(() => {
        const labels = document.querySelectorAll('label, button, [role="radio"]');
        for (const l of labels) {
          if (l.textContent.includes('Give Away') || l.textContent.includes('Giveaway')) { l.click(); return; }
        }
      });
    }
    await sleep(5000);
  } catch (err) {
    console.log(`    List item error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 11: BROWSE ITALIAN -- "Regalo" labels -- 7s
  // ============================================================
  console.log('  Scene 11: Italian browse (Regalo)');
  await demoLogout(page);
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(300);

  await showOverlay(page,
    '\uD83C\uDDEE\uD83C\uDDF9 REGALO',
    'Giveaway in Italian',
    'Every label translates. Even the new ones.'
  );

  await page.goto(`${BASE}/browse?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);
  await showLangBanner(page, '\uD83C\uDDEE\uD83C\uDDF9', 'Italiano');
  await sleep(2000);

  // Scroll to giveaway items
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a, .grid > div');
    for (const c of cards) {
      if (c.textContent.includes('Regalo') || c.textContent.includes('GRATIS') || c.textContent.includes('Garden Hose')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(5000);

  // ============================================================
  // SCENE 12: FEATURE COMPLETE (GREEN) -- 10s
  // ============================================================
  console.log('  Scene 12: Feature complete');
  await page.goto(card(
    'linear-gradient(135deg, #064E3B 0%, #047857 50%, #059669 100%)',
    'THE GIVEAWAY',
    'Feature Complete',
    '<div class="badge">LIVE</div>' +
    '<div class="extra" style="margin-top:24px; text-align:left; max-width:1400px; font-size:40px; line-height:1.8">' +
    '<span class="check">&#x2713;</span> <span class="hl">GIVEAWAY</span> listing type -- no price, no deposit, no return<br>' +
    '<span class="check">&#x2713;</span> Green <span class="hl">Claim This Item</span> button -- one click, message, done<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Auto-complete</span> on approve -- listing auto-pauses<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Notification bell</span> -- owner sees claim instantly<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Multi-image gallery</span> -- prev/next, thumbnails<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Generous Neighbor</span> badge at 3+ giveaways<br>' +
    '<span class="check">&#x2713;</span> Full <span class="hl">Italian</span> -- Regalo, Gratuito<br>' +
    '</div>'
  ));
  await sleep(12000);

  // ============================================================
  // DONE
  // ============================================================
  await page.goto(card('#1E293B', 'CUT', 'Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
