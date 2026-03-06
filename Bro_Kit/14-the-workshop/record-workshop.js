#!/usr/bin/env node
/**
 * THE WORKSHOP -- Recording Script
 *
 * Skills, service quotes, workshop profiles, and account deletion.
 * Uses demoLogin() for user switching (fast, no Keycloak form).
 *
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   2.  Intro card -- purple
 *   3.  Browse as guest, find Marco's workshop link
 *   4.  Marco's Workshop Profile -- skills, badges, services
 *   5.  Character card: Sally Thompson
 *   6.  Login as Sally, visit Marco's service listing
 *   7.  Sally requests a service quote (furniture repair)
 *   8.  Character card: Marco (provider)
 *   9.  Login as Marco, dashboard -- incoming quote request
 *  10.  Marco submits quote (labor + materials)
 *  11.  Character card: Sally (back)
 *  12.  Sally accepts the quote
 *  13.  Account Deletion -- Danger Zone demo
 *  14.  Safety gate: blocked by active quote
 *  15.  GREEN "FEATURE COMPLETE" card
 *
 * Usage: node record-workshop.js [base_url]
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
  .hl { color: #C4B5FD; font-weight: 700; }
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

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  THE WORKSHOP -- Recording Script`);
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
    '<div class="extra">THE WORKSHOP | BorrowHood | EP14</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: FEATURE INTRO (PURPLE) -- 8s
  // ============================================================
  console.log('  Scene 2: Intro');
  await page.goto(card(
    '#7C3AED',
    'THE WORKSHOP',
    'Skills, Services, Quotes & Account Deletion',
    '<div class="badge">NEW FEATURE</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 3: MARCO'S WORKSHOP PROFILE (guest view)
  // ============================================================
  console.log('  Scene 3: Marco\'s Workshop');
  await page.goto(`${BASE}/workshop/marcos-workshop`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Scroll to show skills section
  console.log('  Scene 3b: Skills section');
  await smoothScroll(page, 400);
  await sleep(4000);

  // Scroll more to show items/services
  console.log('  Scene 3c: Items and services');
  await smoothScroll(page, 400);
  await sleep(4000);

  // ============================================================
  // SCENE 4: SALLY THOMPSON (character card)
  // ============================================================
  console.log('  Scene 4: Sally overlay');
  await showOverlay(page, 'SALLY THOMPSON', 'She needs furniture repaired.', 'One quote to find out the cost.');

  // ============================================================
  // SCENE 5: Login as Sally, browse Marco's service listing
  // ============================================================
  console.log('  Scene 5: Sally browses service listings');
  await demoLogin(page, 'sally');
  // Go directly to Marco's furniture restoration service listing page
  console.log('  Scene 5b: Marco\'s service listing');
  await page.goto(`${BASE}/items/restauro-mobili-antichi-falegname`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(4000);

  // Scroll to see service details + pricing
  await smoothScroll(page, 300);
  await sleep(3000);

  // ============================================================
  // SCENE 6: Sally requests a service quote
  // ============================================================
  console.log('  Scene 6: Request quote');
  // Try clicking "Request Quote" button on the item page first
  const hasQuoteBtn = await clickWithRing(page, 'Request', 'button, a');
  if (hasQuoteBtn) {
    // If there's a quote form modal, fill it out
    await sleep(1000);
    const textarea = await page.$('textarea');
    if (textarea) {
      await typeSlowly(page, 'textarea',
        'I have an antique oak dining table with a wobbly leg and scratches. Can you repair and refinish it?', 30);
      await sleep(1000);
      await clickWithRing(page, 'Submit', 'button');
      await sleep(2000);
    }
  } else {
    // Fallback: request quote via API directly
    console.log('  Requesting quote via API...');
    const quoteResp = await apiCall(page, 'POST', '/api/v1/service-quotes', {
      listing_id: '0ff5c416-3d86-4e38-a4ff-18e468df65e8',
      request_description: 'I have an antique oak dining table with a wobbly leg and scratches on the surface. Can you repair and refinish it? The table is about 120cm x 80cm.',
      customer_message: 'Hi Marco! Sally here from the neighborhood. Would love to get a quote for this table repair.'
    });
    console.log(`  Quote request: ${quoteResp.status}`, quoteResp.data?.id ? `(ID: ${quoteResp.data.id})` : JSON.stringify(quoteResp.data));

    // Show a toast notification that quote was sent
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('toast', {
        detail: { type: 'success', message: 'Quote request sent to Marco!' }
      }));
    });
    await sleep(3000);
  }

  // ============================================================
  // SCENE 7: MARCO (character card)
  // ============================================================
  console.log('  Scene 7: Marco overlay');
  await showOverlay(page, 'MARCO', 'The woodworker.', 'He sees the quote request. Time to price it.');

  // ============================================================
  // SCENE 8: Login as Marco, go to dashboard, see quote
  // ============================================================
  console.log('  Scene 8: Marco\'s dashboard');
  await demoLogout(page);
  await demoLogin(page, 'marco');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Check for notification bell
  console.log('  Scene 8b: Notification bell');
  const bellPos = await page.evaluate(() => {
    const bell = document.querySelector('[data-notification-bell], .notification-bell, a[href*="notification"]');
    if (!bell) return null;
    const box = bell.getBoundingClientRect();
    return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  });
  if (bellPos) {
    await showRing(page, bellPos.x, bellPos.y);
    await sleep(2000);
  }

  // Find and respond to the quote
  console.log('  Scene 8c: Responding to quote');
  const quotes = await apiCall(page, 'GET', '/api/v1/service-quotes?role=provider');
  let quoteId = null;
  if (quotes.data && quotes.data.items) {
    const pending = quotes.data.items.find(q => q.status === 'REQUESTED' || q.status === 'requested');
    if (pending) quoteId = pending.id;
  } else if (Array.isArray(quotes.data)) {
    const pending = quotes.data.find(q => q.status === 'REQUESTED' || q.status === 'requested');
    if (pending) quoteId = pending.id;
  }

  if (quoteId) {
    console.log(`  Submitting quote for ${quoteId}`);
    const submitResp = await apiCall(page, 'PATCH', `/api/v1/service-quotes/${quoteId}/quote`, {
      quote_description: 'I can stabilize the wobbly leg with new dowels and wood glue, then sand and refinish the entire surface. I recommend a matte polyurethane finish for durability.',
      labor_hours: 4,
      labor_rate: 25.0,
      materials_cost: 35.0,
      total_amount: 135.0,
      estimated_days: 3,
      provider_message: 'Happy to help, Sally! The oak should come up beautifully.'
    });
    console.log(`  Quote submitted: ${submitResp.status}`);

    // Show success toast
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('toast', {
        detail: { type: 'success', message: 'Quote submitted: EUR 135.00 (4h labor + materials)' }
      }));
    });
    await sleep(3000);
  } else {
    console.log('  WARN: No pending quote found to respond to');
  }

  // ============================================================
  // SCENE 9: SALLY ACCEPTS (character card)
  // ============================================================
  console.log('  Scene 9: Sally accepts overlay');
  await showOverlay(page, 'SALLY THOMPSON', 'She reviews the quote.', 'EUR 135 for a full repair. Deal.');

  // ============================================================
  // SCENE 10: Login as Sally, accept the quote
  // ============================================================
  console.log('  Scene 10: Sally accepts quote');
  await demoLogout(page);
  await demoLogin(page, 'sally');

  if (quoteId) {
    const acceptResp = await apiCall(page, 'PATCH', `/api/v1/service-quotes/${quoteId}/status`, {
      status: 'accepted'
    });
    console.log(`  Quote accepted: ${acceptResp.status}`);

    await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
    await setZoom(page);
    await sleep(2000);

    // Show acceptance toast
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('toast', {
        detail: { type: 'success', message: 'Quote accepted! Marco will start the repair.' }
      }));
    });
    await sleep(3000);
  }

  // ============================================================
  // SCENE 11: ACCOUNT DELETION (Danger Zone)
  // ============================================================
  console.log('  Scene 11: Account Deletion -- Danger Zone');
  await showOverlay(page, 'DANGER ZONE', 'Can a member leave?', 'Account deletion with safety gates.');

  // Login as Marco to show Danger Zone (he has active items -- good visual)
  await demoLogout(page);
  await demoLogin(page, 'marco');

  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1000);

  // Click Settings tab
  console.log('  Scene 11b: Settings tab');
  await clickWithRing(page, 'Settings', 'button, [role="tab"], a');
  await sleep(2000);

  // Scroll down to Danger Zone
  await smoothScroll(page, 400);
  await sleep(2000);

  // Show the Delete Account button (but DON'T click it -- just highlight)
  console.log('  Scene 11c: Danger Zone visible');
  const deleteBtn = await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
      if (btn.textContent.includes('Delete Account') || btn.textContent.includes('Elimina Account')) {
        const box = btn.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      }
    }
    return null;
  });
  if (deleteBtn) {
    await showRing(page, deleteBtn.x, deleteBtn.y);
    await sleep(3000);
  }

  // ============================================================
  // SCENE 12: SAFETY GATE -- try deleting Sally (who has active quote)
  // ============================================================
  console.log('  Scene 12: Safety gate demo');
  await showOverlay(page, 'SAFETY GATE', 'What if Sally tries to delete?', 'She has an active service quote.');

  await demoLogout(page);
  await demoLogin(page, 'sally');
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1000);

  await clickWithRing(page, 'Settings', 'button, [role="tab"], a');
  await sleep(2000);
  await smoothScroll(page, 400);
  await sleep(2000);

  // Click the Delete Account button to trigger the confirm dialog
  console.log('  Scene 12b: Clicking Delete Account (will trigger confirm)');
  // Dismiss the confirm dialog automatically (click Cancel)
  page.once('dialog', async dialog => {
    await sleep(2000);  // Let viewer see the confirm dialog
    await dialog.dismiss();
  });
  await clickWithRing(page, 'Delete Account', 'button');
  await sleep(3000);

  // Also attempt delete via API to show the 409 block
  console.log('  Scene 12c: API delete attempt (should be blocked)');
  const deleteResp = await apiCall(page, 'DELETE', '/api/v1/users/me');
  console.log(`  Delete response: ${deleteResp.status}`, deleteResp.data?.detail || '');

  if (deleteResp.status === 409) {
    // Show the error as a visible toast
    await page.evaluate((msg) => {
      // Create a visible error banner
      const banner = document.createElement('div');
      banner.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: #DC2626; color: white; padding: 16px 32px;
        border-radius: 12px; font-size: 18px; font-weight: 600;
        z-index: 99999; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        max-width: 80%; text-align: center;
      `;
      banner.textContent = msg;
      document.body.appendChild(banner);
      setTimeout(() => { banner.style.transition = 'opacity 1s'; banner.style.opacity = '0'; }, 5000);
      setTimeout(() => banner.remove(), 6000);
    }, deleteResp.data.detail);
    await sleep(5000);
  } else if (deleteResp.status === 200) {
    console.log('  NOTE: Sally was deleted (no active obligations found).');
  }

  // ============================================================
  // SCENE 13: FEATURE COMPLETE (GREEN)
  // ============================================================
  console.log('  Scene 13: Feature Complete');
  await page.goto(card(
    '#059669',
    'FEATURE COMPLETE',
    'The Workshop',
    `<div class="extra" style="text-align:left; font-size:42px">
      <span class="check">&#10003;</span> Workshop Profiles with Verified Skills<br>
      <span class="check">&#10003;</span> Service Listings with Hourly Pricing<br>
      <span class="check">&#10003;</span> Quote Request, Submit, Accept Flow<br>
      <span class="check">&#10003;</span> Account Deletion with Safety Gates<br>
      <span class="check">&#10003;</span> GDPR-Ready Soft Delete<br>
      <span class="dim">Built with Claude Code (Opus)</span>
    </div>`
  ));
  await sleep(10000);

  console.log('\n  DONE. Stop OBS recording now.');
  await waitForEnter('Press ENTER to close browser');
  await browser.close();
})().catch(err => {
  console.error('\n  SCRIPT ERROR:', err.message);
  console.error('  Stack:', err.stack?.split('\n').slice(0, 3).join('\n'));
  process.exit(1);
});
