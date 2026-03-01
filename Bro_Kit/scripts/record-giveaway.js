#!/usr/bin/env node
/**
 * GIVEAWAY FEATURE -- Recording Script
 *
 * Layout: Non-headless browser at 1920x1080 (OBS captures screen)
 * Flow:
 *   1. RED "OBS CHECK" card
 *   2. Feature intro card
 *   3. Browse page -- giveaway items with FREE badges + emerald "Give Away" pills
 *   4. Item detail -- Mike's garden hose: FREE badge + green "Claim This Item"
 *   5. Login as Sally, claim the garden hose (simplified modal, no dates)
 *   6. Login as Mike, approve claim (auto-completes, listing paused)
 *   7. List item form -- "Give Away" option with hidden price fields
 *   8. Browse page Italian -- "Regalo" pills
 *   9. GREEN "FEATURE COMPLETE" card
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

async function kcLogin(page, username) {
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1500);
  // Clear any pre-filled values
  await page.evaluate(() => {
    const u = document.querySelector('#username');
    const p = document.querySelector('#password');
    if (u) u.value = '';
    if (p) p.value = '';
  });
  await page.type('#username', username, { delay: 60 });
  await page.type('#password', 'helix_pass', { delay: 60 });
  await sleep(500);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }),
    page.click('#kc-login'),
  ]);
  await sleep(1500);
}

async function kcLogout(page) {
  await page.goto(`${BASE}/logout`, { waitUntil: 'networkidle2', timeout: 10000 });
  await sleep(300);
  try {
    const logoutBtn = await page.$('#kc-logout');
    if (logoutBtn) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }),
        logoutBtn.click(),
      ]);
    }
  } catch (e) { /* already logged out */ }
  await sleep(300);
}

(async () => {
  console.log(`\n  GIVEAWAY FEATURE -- Recording Script`);
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
    '<div class="extra">GIVEAWAY FEATURE | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: FEATURE INTRO
  // ============================================================
  await page.goto(card(
    '#059669',
    'GIVEAWAY',
    'Free items. Claim it. Pick it up. Done.',
    '<div class="badge">NEW FEATURE</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'No pricing. No deposits. No return dates.<br>' +
    'Generous Neighbor badge at 3+ giveaways' +
    '</div>'
  ));
  await sleep(6000);

  // ============================================================
  // SCENE 3: BROWSE -- Giveaway items visible
  // ============================================================
  console.log('  Scene 3: Browse page with giveaway items');
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll down to find giveaway items
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a');
    for (const c of cards) {
      if (c.textContent.includes('Give Away') || c.textContent.includes('Garden Hose')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(3000);

  // ============================================================
  // SCENE 4: ITEM DETAIL -- Garden hose (giveaway)
  // ============================================================
  console.log('  Scene 4: Garden hose item detail');
  await page.goto(`${BASE}/items/garden-hose-30m-free`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll to see the "FREE -- Pick Up Only" badge and Claim button
  await page.evaluate(() => {
    const btn = document.querySelector('.bg-green-600');
    if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(3000);

  // ============================================================
  // SCENE 5: LOGIN AS SALLY + CLAIM
  // ============================================================
  console.log('  Scene 5: Login as Sally');

  // Transition card
  await page.goto(card(
    '#1E293B',
    'SALLY THOMPSON',
    'Logging in to claim the garden hose',
    '<div class="extra">Sally sees the giveaway. She wants it.</div>'
  ));
  await sleep(4000);

  await kcLogin(page, 'sally');

  // Navigate to the giveaway item
  await page.goto(`${BASE}/items/garden-hose-30m-free`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll to the Claim button first
  console.log('  Scene 5b: Scroll to Claim button');
  await page.evaluate(() => {
    const btn = document.querySelector('.bg-green-600');
    if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(2000);

  // Click "Claim This Item" button (the one NOT inside the modal)
  console.log('  Scene 5c: Click Claim, open modal');
  try {
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Claim This Item') && !b.closest('.fixed')) { b.click(); break; }
      }
    });
    await sleep(2000);

    // Type claim message into the modal textarea
    console.log('  Scene 5d: Typing claim message');
    await page.evaluate(() => {
      // Find the modal that has a textarea (not just any .fixed element)
      const fixeds = document.querySelectorAll('.fixed');
      for (const f of fixeds) {
        const ta = f.querySelector('textarea');
        if (ta) { ta.focus(); ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); break; }
      }
    });
    await page.type('.fixed textarea',
      "Hi Mike! I would love this hose for my garden. Can pick up this weekend!",
      { delay: 35 }
    );
    await sleep(3000);

    // Submit -- click the green button INSIDE the modal (find modal with textarea)
    console.log('  Scene 5e: Submit claim');
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
  } catch (err) {
    console.log(`    Claim error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 6: SWITCH TO MIKE -- APPROVE
  // ============================================================
  console.log('  Scene 6: Switch to Mike');

  // Logout Sally first (fast, no visual delay)
  await kcLogout(page);

  // Now show the transition card
  await page.goto(card(
    '#1E293B',
    'MIKE KENEL',
    'Switching to item owner',
    '<div class="extra">Mike sees the claim request. One click to approve.</div>'
  ));
  await sleep(4000);

  await kcLogin(page, 'mike');

  // Dashboard -- incoming requests
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Click "Incoming Requests" tab
  console.log('  Scene 6b: Incoming requests');
  await page.evaluate(() => {
    const tabs = document.querySelectorAll('button, a, [role="tab"]');
    for (const t of tabs) {
      if (t.textContent.trim().includes('Incoming')) { t.click(); break; }
    }
  });
  await sleep(3000);

  // Find the Garden Hose claim and click Approve
  console.log('  Scene 6c: Approve the garden hose claim');
  try {
    // Scroll to the Garden Hose row
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Garden Hose')) {
          row.scrollIntoView({ behavior: 'smooth', block: 'center' });
          break;
        }
      }
    });
    await sleep(2000);

    // Click the Approve button on the Garden Hose row
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Garden Hose')) {
          const btns = row.querySelectorAll('button');
          for (const b of btns) {
            if (b.textContent.trim() === 'Approve') { b.click(); return; }
          }
        }
      }
    });

    // Wait for page reload (updateStatus calls window.location.reload)
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2000);

    // Click Incoming Requests tab again (page reloaded to default tab)
    await page.evaluate(() => {
      const tabs = document.querySelectorAll('button, a, [role="tab"]');
      for (const t of tabs) {
        if (t.textContent.trim().includes('Incoming')) { t.click(); break; }
      }
    });
    await sleep(3000);
    console.log('  Scene 6d: Garden hose approved -- giveaway auto-completed');
  } catch (err) {
    console.log(`    Approve error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 7: LIST ITEM -- "Give Away" option
  // ============================================================
  console.log('  Scene 7: List item form with Give Away');

  await page.goto(`${BASE}/list`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  // Fill in item name to get to step 2
  try {
    await page.type('input[type="text"]', 'Old Table Lamp', { delay: 40 });
    await sleep(500);

    // Click Next to step 2
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Next')) { b.click(); break; }
      }
    });
    await sleep(2000);

    // Click "Give Away" checkbox
    await page.evaluate(() => {
      const labels = document.querySelectorAll('label');
      for (const l of labels) {
        if (l.textContent.includes('Give Away')) { l.click(); break; }
      }
    });
    await sleep(3000);
  } catch (err) {
    console.log(`    List item error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 8: ITALIAN -- "Regalo" labels
  // ============================================================
  console.log('  Scene 8: Italian browse');

  // Logout Mike first (fast), then transition card, then navigate
  await kcLogout(page);

  await page.goto(card(
    '#1E293B',
    'ITALIANO',
    'Full Italian localization',
    '<div class="extra">Every label, button, and badge -- translated.</div>'
  ));
  await sleep(3000);

  await page.goto(`${BASE}/browse?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll to giveaway items
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a');
    for (const c of cards) {
      if (c.textContent.includes('Regalo') || c.textContent.includes('Garden Hose')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(3000);

  // ============================================================
  // SCENE 9: FEATURE COMPLETE (GREEN)
  // ============================================================
  await page.goto(card(
    '#059669',
    'GIVEAWAY',
    'Feature Complete',
    '<div class="badge">LIVE ON HETZNER</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'New GIVEAWAY listing type<br>' +
    'Green "Claim This Item" button, no dates<br>' +
    'Auto-complete on approve, listing paused<br>' +
    'Generous Neighbor badge at 3+ giveaways<br>' +
    '25 points per giveaway (generosity valued)' +
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
