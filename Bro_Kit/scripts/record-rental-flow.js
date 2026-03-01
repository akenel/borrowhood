#!/usr/bin/env node
/**
 * RENTAL FLOW -- End to End Recording Script
 *
 * Layout: Non-headless browser at 1920x1080 (OBS captures screen)
 * Flow:
 *   1.  RED "OBS CHECK" card
 *   2.  Feature intro card
 *   3.  Browse page -- rental items with blue "Rent" badges + prices
 *   4.  Item detail -- Mike's Bosch Drill: EUR 8/day + EUR 30 deposit
 *   5.  Login as Sally, request rental (pick dates, type message)
 *   6.  Switch to Mike, approve on Incoming Requests tab
 *   7.  Mike generates lockbox codes (location + instructions)
 *   8.  Switch to Sally, My Rentals tab -- see pickup code, click "I've Picked It Up"
 *   9.  Sally's dashboard reloads -- see return code, click "I've Returned It"
 *  10.  Switch to Mike, Incoming Requests -- click "Complete"
 *  11.  GREEN "FEATURE COMPLETE" card
 *
 * Pre-flight: cleans up any PENDING/APPROVED rental on the drill
 *             so the flow starts fresh every take.
 *
 * Usage: node record-rental-flow.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://46.62.138.218';
const VP = { width: 1920, height: 1080 };
const DRILL_SLUG = 'bosch-professional-drill-driver-set';

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

// ── Auth helpers ──────────────────────────────────────────────
async function kcLogin(page, username) {
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(1500);
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

// ── Cookie/token helper -- get session token for API calls ───
async function getToken(page) {
  return await page.evaluate(() => {
    const cookies = document.cookie.split(';').map(c => c.trim());
    for (const c of cookies) {
      if (c.startsWith('access_token=')) return c.split('=')[1];
    }
    return null;
  });
}

// ── Pre-flight cleanup ───────────────────────────────────────
async function cleanupDrillRentals(page) {
  console.log('  Pre-flight: cleaning up stale drill rentals...');
  const token = await getToken(page);
  if (!token) { console.log('    No token, skipping cleanup'); return; }

  // Fetch rentals where Mike is owner
  const resp = await page.evaluate(async (base, tok) => {
    const r = await fetch(`${base}/api/v1/rentals?role=owner&limit=50`, {
      headers: { 'Authorization': `Bearer ${tok}` }
    });
    if (!r.ok) return [];
    return r.json();
  }, BASE, token);

  for (const rental of resp) {
    // Find drill rentals that aren't completed/declined/cancelled
    const name = rental.listing?.item?.name || '';
    if (!name.includes('Bosch') && !name.includes('Drill')) continue;
    if (['completed', 'declined', 'cancelled'].includes(rental.status)) continue;

    console.log(`    Cancelling rental ${rental.id} (status: ${rental.status})`);
    await page.evaluate(async (base, tok, rid) => {
      await fetch(`${base}/api/v1/rentals/${rid}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${tok}` },
        body: JSON.stringify({ status: 'cancelled', reason: 'Cleanup for recording' })
      });
    }, BASE, token, rental.id);
  }
  console.log('  Pre-flight: done');
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log(`\n  RENTAL FLOW -- End to End Recording Script`);
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

  // ── Pre-flight: login as Mike and cleanup ──────────────────
  console.log('  Pre-flight: login as Mike for cleanup');
  await kcLogin(page, 'mike');
  await cleanupDrillRentals(page);
  await kcLogout(page);

  // ============================================================
  // SCENE 1: OBS CHECK (RED)
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">RENTAL FLOW | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: FEATURE INTRO
  // ============================================================
  await page.goto(card(
    '#4338CA',
    'RENTAL FLOW',
    'Request. Approve. Pick up. Return. Complete.',
    '<div class="badge">END TO END</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Date pickers. Lock box codes. Contactless exchange.<br>' +
    'The full state machine in under 2 minutes.' +
    '</div>'
  ));
  await sleep(6000);

  // ============================================================
  // SCENE 3: BROWSE -- Rental items visible
  // ============================================================
  console.log('  Scene 3: Browse page with rental items');
  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll to find rental items (look for Mike's items)
  await page.evaluate(() => {
    const cards = document.querySelectorAll('.grid a');
    for (const c of cards) {
      if (c.textContent.includes('Bosch') || c.textContent.includes('Drill')) {
        c.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(3000);

  // ============================================================
  // SCENE 4: ITEM DETAIL -- Bosch Drill
  // ============================================================
  console.log('  Scene 4: Bosch Drill item detail');
  await page.goto(`${BASE}/items/${DRILL_SLUG}`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll to the "Rent This" button area
  await page.evaluate(() => {
    const btn = document.querySelector('.bg-indigo-600');
    if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(3000);

  // ============================================================
  // SCENE 5: LOGIN AS SALLY + REQUEST RENTAL
  // ============================================================
  console.log('  Scene 5: Login as Sally');

  await page.goto(card(
    '#1E293B',
    'SALLY THOMPSON',
    'Logging in to rent the drill',
    '<div class="extra">Sally needs a drill for her deck project this weekend.</div>'
  ));
  await sleep(4000);

  await kcLogin(page, 'sally');

  // Navigate to the drill item
  await page.goto(`${BASE}/items/${DRILL_SLUG}`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(3000);

  // Scroll to and click "Rent This" button
  console.log('  Scene 5b: Click Rent This');
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Rent This') && !b.closest('.fixed')) { b.click(); break; }
    }
  });
  await sleep(2000);

  // Fill in dates -- start tomorrow, end in 3 days
  console.log('  Scene 5c: Pick dates');
  try {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 3);

    const startStr = tomorrow.toISOString().split('T')[0];
    const endStr = endDate.toISOString().split('T')[0];

    // Find the modal with date inputs
    await page.evaluate((s, e) => {
      const fixeds = document.querySelectorAll('.fixed');
      for (const f of fixeds) {
        const dateInputs = f.querySelectorAll('input[type="date"]');
        if (dateInputs.length >= 2) {
          // Set start date
          const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          nativeInputValueSetter.call(dateInputs[0], s);
          dateInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
          dateInputs[0].dispatchEvent(new Event('change', { bubbles: true }));
          // Set end date
          nativeInputValueSetter.call(dateInputs[1], e);
          dateInputs[1].dispatchEvent(new Event('input', { bubbles: true }));
          dateInputs[1].dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, startStr, endStr);
    await sleep(1500);

    // Type message in the modal textarea
    console.log('  Scene 5d: Type rental message');
    await page.evaluate(() => {
      const fixeds = document.querySelectorAll('.fixed');
      for (const f of fixeds) {
        const ta = f.querySelector('textarea');
        if (ta) { ta.focus(); ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); break; }
      }
    });
    await page.type('.fixed textarea',
      "Hi Mike! Need the drill for a deck project this weekend. Will take good care of it!",
      { delay: 30 }
    );
    await sleep(2000);

    // Submit -- click the indigo button inside the modal
    console.log('  Scene 5e: Submit rental request');
    await page.evaluate(() => {
      const fixeds = document.querySelectorAll('.fixed');
      for (const f of fixeds) {
        if (!f.querySelector('textarea')) continue;
        const btns = f.querySelectorAll('button');
        for (const b of btns) {
          if (b.classList.contains('bg-indigo-600') || b.textContent.trim() === 'Request') {
            b.click(); return;
          }
        }
      }
    });
    await sleep(3000);
  } catch (err) {
    console.log(`    Rental request error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 6: SWITCH TO MIKE -- APPROVE
  // ============================================================
  console.log('  Scene 6: Switch to Mike');
  await kcLogout(page);

  await page.goto(card(
    '#1E293B',
    'MIKE KENEL',
    'Switching to item owner',
    '<div class="extra">Mike sees Sally\'s rental request. Time to approve.</div>'
  ));
  await sleep(4000);

  await kcLogin(page, 'mike');

  // Dashboard -- Incoming Requests
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  console.log('  Scene 6b: Incoming Requests tab');
  await page.evaluate(() => {
    const tabs = document.querySelectorAll('button, a, [role="tab"]');
    for (const t of tabs) {
      if (t.textContent.trim().includes('Incoming')) { t.click(); break; }
    }
  });
  await sleep(3000);

  // Scroll to the Bosch Drill request
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
    for (const row of rows) {
      if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
        row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(2000);

  // Click Approve
  console.log('  Scene 6c: Approve the rental');
  try {
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
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

    // Click Incoming Requests tab again after reload
    await page.evaluate(() => {
      const tabs = document.querySelectorAll('button, a, [role="tab"]');
      for (const t of tabs) {
        if (t.textContent.trim().includes('Incoming')) { t.click(); break; }
      }
    });
    await sleep(2000);

    // Scroll to show the approved rental with lock box form
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
          row.scrollIntoView({ behavior: 'smooth', block: 'center' });
          break;
        }
      }
    });
    await sleep(2000);
    console.log('  Scene 6d: Rental approved -- lock box section visible');
  } catch (err) {
    console.log(`    Approve error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 7: MIKE GENERATES LOCK BOX CODES
  // ============================================================
  console.log('  Scene 7: Generate lock box codes');
  try {
    // Type location hint
    await page.evaluate(() => {
      const inputs = document.querySelectorAll('input[type="text"]');
      for (const inp of inputs) {
        if (inp.placeholder && inp.placeholder.toLowerCase().includes('location')) {
          inp.focus();
          break;
        }
      }
    });
    // Find and type into the location hint input (first input in the lockbox section)
    const locationInput = await page.evaluateHandle(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
          const inputs = row.querySelectorAll('input[type="text"]');
          if (inputs.length >= 1) return inputs[0];
        }
      }
      return null;
    });

    if (locationInput) {
      await locationInput.type('Garage side door, key under flower pot', { delay: 30 });
      await sleep(1000);
    }

    // Type instructions into second input
    const instrInput = await page.evaluateHandle(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
          const inputs = row.querySelectorAll('input[type="text"]');
          if (inputs.length >= 2) return inputs[1];
        }
      }
      return null;
    });

    if (instrInput) {
      await instrInput.type('Drill is on the top shelf, red case', { delay: 30 });
      await sleep(1500);
    }

    // Click "Generate Codes" button
    console.log('  Scene 7b: Click Generate Codes');
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
          const btns = row.querySelectorAll('button');
          for (const b of btns) {
            if (b.textContent.includes('Generate')) { b.click(); return; }
          }
        }
      }
    });
    await sleep(3000);

    // Scroll to show the generated codes in amber box
    await page.evaluate(() => {
      const amberBox = document.querySelector('.bg-amber-50');
      if (amberBox) amberBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await sleep(3000);
    console.log('  Scene 7c: Lock box codes generated');
  } catch (err) {
    console.log(`    Lock box error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 8: SWITCH TO SALLY -- PICKUP
  // ============================================================
  console.log('  Scene 8: Switch to Sally for pickup');
  await kcLogout(page);

  await page.goto(card(
    '#1E293B',
    'SALLY THOMPSON',
    'Picking up the drill',
    '<div class="extra">Sally goes to Mike\'s garage. Key under the flower pot.</div>'
  ));
  await sleep(4000);

  await kcLogin(page, 'sally');

  // Dashboard -- My Rentals tab
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  console.log('  Scene 8b: My Rentals tab');
  await page.evaluate(() => {
    const tabs = document.querySelectorAll('button, a, [role="tab"]');
    for (const t of tabs) {
      if (t.textContent.trim().includes('My Rentals') || t.textContent.trim().includes('Rental')) { t.click(); break; }
    }
  });
  await sleep(3000);

  // Scroll to show the pickup code (blue box)
  await page.evaluate(() => {
    const blueBox = document.querySelector('.bg-blue-50');
    if (blueBox) blueBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(3000);

  // Click "I've Picked It Up" button
  console.log('  Scene 8c: Click "I\'ve Picked It Up"');
  try {
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes("Picked It Up")) { b.click(); return; }
      }
    });

    // Wait for page reload (verifyCode calls window.location.reload after 1.5s)
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2000);

    // Click My Rentals tab again after reload
    await page.evaluate(() => {
      const tabs = document.querySelectorAll('button, a, [role="tab"]');
      for (const t of tabs) {
        if (t.textContent.trim().includes('My Rentals') || t.textContent.trim().includes('Rental')) { t.click(); break; }
      }
    });
    await sleep(2000);

    console.log('  Scene 8d: Status changed to picked_up -- return code visible');
  } catch (err) {
    console.log(`    Pickup error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 9: SALLY RETURNS THE DRILL
  // ============================================================
  console.log('  Scene 9: Sally returns the drill');
  await sleep(2000);

  // Scroll to show the return code (green box)
  await page.evaluate(() => {
    const greenBox = document.querySelector('.bg-emerald-50');
    if (greenBox) greenBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await sleep(3000);

  // Click "I've Returned It" button
  console.log('  Scene 9b: Click "I\'ve Returned It"');
  try {
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes("Returned It")) { b.click(); return; }
      }
    });

    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2000);

    // Click My Rentals tab again
    await page.evaluate(() => {
      const tabs = document.querySelectorAll('button, a, [role="tab"]');
      for (const t of tabs) {
        if (t.textContent.trim().includes('My Rentals') || t.textContent.trim().includes('Rental')) { t.click(); break; }
      }
    });
    await sleep(2000);
    console.log('  Scene 9c: Status changed to returned');
  } catch (err) {
    console.log(`    Return error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 10: SWITCH TO MIKE -- COMPLETE
  // ============================================================
  console.log('  Scene 10: Switch to Mike to complete');
  await kcLogout(page);

  await page.goto(card(
    '#1E293B',
    'MIKE KENEL',
    'Confirming the return',
    '<div class="extra">Drill is back. Time to close the rental.</div>'
  ));
  await sleep(4000);

  await kcLogin(page, 'mike');

  // Dashboard -- Incoming Requests
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  console.log('  Scene 10b: Incoming Requests tab');
  await page.evaluate(() => {
    const tabs = document.querySelectorAll('button, a, [role="tab"]');
    for (const t of tabs) {
      if (t.textContent.trim().includes('Incoming')) { t.click(); break; }
    }
  });
  await sleep(3000);

  // Scroll to the drill rental
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
    for (const row of rows) {
      if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
        row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
    }
  });
  await sleep(2000);

  // Click "Complete"
  console.log('  Scene 10c: Click Complete');
  try {
    await page.evaluate(() => {
      const rows = document.querySelectorAll('.bg-white.rounded-lg.border');
      for (const row of rows) {
        if (row.textContent.includes('Bosch') || row.textContent.includes('Drill')) {
          const btns = row.querySelectorAll('button');
          for (const b of btns) {
            if (b.textContent.trim() === 'Complete') { b.click(); return; }
          }
        }
      }
    });

    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
    await sleep(2000);

    // Show the final state -- Incoming Requests tab
    await page.evaluate(() => {
      const tabs = document.querySelectorAll('button, a, [role="tab"]');
      for (const t of tabs) {
        if (t.textContent.trim().includes('Incoming')) { t.click(); break; }
      }
    });
    await sleep(3000);
    console.log('  Scene 10d: Rental COMPLETED');
  } catch (err) {
    console.log(`    Complete error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 11: FEATURE COMPLETE (GREEN)
  // ============================================================
  await page.goto(card(
    '#4338CA',
    'RENTAL FLOW',
    'Complete',
    '<div class="badge">END TO END</div>' +
    '<div class="extra" style="margin-top:20px">' +
    'Sally requested the drill with dates and a message<br>' +
    'Mike approved and generated lock box codes<br>' +
    'Sally picked up with the pickup code<br>' +
    'Sally returned with the return code<br>' +
    'Mike completed the rental -- both earn points' +
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
