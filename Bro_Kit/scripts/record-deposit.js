#!/usr/bin/env node
/**
 * DEPOSIT & DISPUTE RESOLUTION -- Recording Script
 *
 * Layout: Non-headless browser at 1920x1080 (OBS captures screen)
 * Flow:
 *   1. RED "OBS CHECK" card
 *   2. Feature intro card -- Security Deposits
 *   3. Browse page -- items showing deposit amounts
 *   4. Item detail -- DJI Mini 3 Pro: €35/day + €250 deposit
 *   5. Item detail -- MacBook Pro M2: €25/day + €200 deposit
 *   6. Lifecycle card -- Hold > Release > Forfeit
 *   7. Dispute resolution card -- 3-step flow
 *   8. API demo card -- 4 endpoints
 *   9. GREEN "FEATURE COMPLETE" card
 *
 * Usage: node record-deposit.js [base_url]
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

function diagramCard(bg, title, htmlBody) {
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
  h1 { font-size: 64px; font-weight: 800; margin-bottom: 40px; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
  .flow { display: flex; align-items: center; gap: 20px; margin: 20px 0; flex-wrap: wrap; justify-content: center; }
  .step { background: rgba(255,255,255,0.15); border-radius: 16px; padding: 24px 32px; min-width: 200px; }
  .step-num { font-size: 48px; font-weight: 800; opacity: 0.5; }
  .step-title { font-size: 28px; font-weight: 700; margin-top: 8px; }
  .step-desc { font-size: 18px; opacity: 0.8; margin-top: 6px; }
  .arrow { font-size: 48px; opacity: 0.5; }
  .note { font-size: 20px; opacity: 0.6; margin-top: 30px; max-width: 900px; }
</style></head><body>
  <h1>${title}</h1>${htmlBody}
</body></html>`)}`;
}

(async () => {
  console.log(`\n  DEPOSIT & DISPUTE -- Recording Script`);
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
    ]
  });

  const page = await browser.newPage();
  await page.setViewport(VP);

  // ============================================================
  // SCENE 1: OBS CHECK (RED)
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">DEPOSIT & DISPUTE RESOLUTION | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: FEATURE INTRO
  // ============================================================
  await page.goto(card(
    '#1E40AF',
    'SECURITY DEPOSITS',
    'Protect your stuff. Protect your money.',
    '<div class="badge">DEPOSIT + DISPUTE SYSTEM</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Hold at pickup. Auto-release on return.<br>' +
    'Forfeit on damage. Dispute resolution built in.' +
    '</div>'
  ));
  await sleep(7000);

  // ============================================================
  // SCENE 3: BROWSE -- Items showing deposit amounts
  // ============================================================
  console.log('  Scene 3: Browse page -- items with deposits visible');
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Wait for images
  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img => {
      if (img.complete) return Promise.resolve();
      return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
    })
  ));

  // Scroll to find an item with deposit text visible
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a, .grid > div');
    for (const c of cards) {
      if (c.textContent.includes('deposit')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
  });
  await sleep(4000);

  // ============================================================
  // SCENE 4: ITEM DETAIL -- DJI Mini 3 Pro (€250 deposit)
  // ============================================================
  console.log('  Scene 4: DJI Mini 3 Pro -- €250 deposit');
  await page.goto(`${BASE}/items/drone-dji-mini-3-pro`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  // Wait for images to load
  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img => {
      if (img.complete) return Promise.resolve();
      return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
    })
  ));
  await sleep(2000);

  // Scroll to where the price + deposit info is shown
  await page.evaluate(() => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.includes('deposit') && el.offsetHeight < 50) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
  });
  await sleep(4000);

  // ============================================================
  // SCENE 5: ITEM DETAIL -- MacBook Pro M2 (€200 deposit)
  // ============================================================
  console.log('  Scene 5: MacBook Pro M2 -- €200 deposit');
  await page.goto(`${BASE}/items/macbook-pro-m2-14-inch`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img => {
      if (img.complete) return Promise.resolve();
      return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
    })
  ));
  await sleep(2000);

  // Scroll to price + deposit
  await page.evaluate(() => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.includes('deposit') && el.offsetHeight < 50) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
  });
  await sleep(4000);

  // ============================================================
  // SCENE 6: DEPOSIT LIFECYCLE DIAGRAM
  // ============================================================
  console.log('  Scene 6: Deposit lifecycle diagram');
  await page.goto(diagramCard(
    '#1E40AF',
    'DEPOSIT LIFECYCLE',
    `<div class="flow">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-title">HOLD</div>
        <div class="step-desc">Renter pays deposit<br>at pickup</div>
      </div>
      <div class="arrow">&#8594;</div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-title">RELEASE</div>
        <div class="step-desc">Auto-released when<br>rental completes</div>
      </div>
      <div class="arrow">&#8594;</div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-title">OR FORFEIT</div>
        <div class="step-desc">Owner keeps deposit<br>if item damaged</div>
      </div>
    </div>
    <div class="note">
      Partial release supported: owner can release part and forfeit part.<br>
      Every action sends a notification to both parties.
    </div>`
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 7: DISPUTE RESOLUTION DIAGRAM
  // ============================================================
  console.log('  Scene 7: Dispute resolution flow');
  await page.goto(diagramCard(
    '#7C3AED',
    'DISPUTE RESOLUTION',
    `<div class="flow">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-title">FILE</div>
        <div class="step-desc">Either party files<br>a dispute with reason</div>
      </div>
      <div class="arrow">&#8594;</div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-title">RESPOND</div>
        <div class="step-desc">Other party responds<br>with their side</div>
      </div>
      <div class="arrow">&#8594;</div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-title">RESOLVE</div>
        <div class="step-desc">Resolution applied<br>deposit action auto-wired</div>
      </div>
    </div>
    <div class="note" style="margin-top: 25px;">
      8 dispute reasons: Damaged, Not Returned, Wrong Item, Late Return,<br>
      Not as Described, Unauthorized Use, Safety Concern, Other<br><br>
      7 resolutions: Deposit Returned, Deposit Forfeited, Partial Refund,<br>
      Full Refund, Replacement, No Action, Escalated
    </div>`
  ));
  await sleep(10000);

  // ============================================================
  // SCENE 8: API ENDPOINTS CARD
  // ============================================================
  console.log('  Scene 8: API endpoints');
  await page.goto(diagramCard(
    '#0F766E',
    'DEPOSIT API',
    `<div style="text-align: left; font-family: monospace; font-size: 22px; line-height: 2.2; background: rgba(0,0,0,0.3); padding: 30px 50px; border-radius: 16px; margin-top: 10px;">
      <span style="color: #4ADE80; font-weight: bold;">POST</span> &nbsp; /api/v1/deposits &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style="opacity: 0.6;">Hold deposit at pickup</span><br>
      <span style="color: #60A5FA; font-weight: bold;">GET</span> &nbsp;&nbsp; /api/v1/deposits &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style="opacity: 0.6;">List my deposits</span><br>
      <span style="color: #FBBF24; font-weight: bold;">PATCH</span>  /api/v1/deposits/:id/release &nbsp; <span style="opacity: 0.6;">Release back to renter</span><br>
      <span style="color: #F87171; font-weight: bold;">PATCH</span>  /api/v1/deposits/:id/forfeit &nbsp; <span style="opacity: 0.6;">Forfeit for damage</span>
    </div>
    <div class="note" style="margin-top: 25px;">
      Dispute resolution auto-wires to deposit actions.<br>
      Rental completion auto-releases held deposits.
    </div>`
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 9: BACK TO BROWSE -- Show more items with deposits
  // ============================================================
  console.log('  Scene 9: Browse -- more deposit items');

  // Show Canon EOS R5 or Kitesurf Kit
  await page.goto(`${BASE}/items/canon-eos-r5-camera-kit`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);
  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img => {
      if (img.complete) return Promise.resolve();
      return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
    })
  ));

  // Scroll to deposit info
  await page.evaluate(() => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.includes('deposit') && el.offsetHeight < 50) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
  });
  await sleep(4000);

  // ============================================================
  // SCENE 10: FEATURE COMPLETE (GREEN)
  // ============================================================
  await page.goto(card(
    '#059669',
    'DEPOSITS & DISPUTES',
    'Feature Complete',
    '<div class="badge">LIVE ON HETZNER</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Security deposits on 39 listings<br>' +
    'Hold, release, forfeit, partial release<br>' +
    'Auto-release on rental completion<br>' +
    '3-step dispute resolution<br>' +
    '8 reasons, 7 resolution types<br>' +
    'Deposit actions wired to dispute outcomes' +
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
