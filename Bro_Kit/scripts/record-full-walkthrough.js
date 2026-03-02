#!/usr/bin/env node
/**
 * BORROWHOOD -- The Complete Walkthrough
 *
 * One story. Two neighbors. One transaction. Every step.
 *
 * Mike has a Bosch drill in his garage (EUR 8/day + EUR 30 deposit).
 * Sally needs it for her deck project.
 * Full lifecycle: list > browse > rent > approve > lockbox > pickup > return > complete > review.
 *
 * Layout: Non-headless browser at 1920x1080 (OBS captures screen)
 * Duration: ~5-8 minutes, real pace, no rush
 *
 * Usage: node record-full-walkthrough.js [base_url]
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
  .extra { font-size: 24px; opacity: 0.7; margin-top: 10px; line-height: 1.6; }
  .badge { display: inline-block; padding: 8px 24px; border-radius: 8px; background: rgba(255,255,255,0.2); font-size: 28px; font-weight: 600; margin-top: 20px; }
</style></head><body>
  <h1>${title}</h1><h2>${subtitle}</h2>${extra}
</body></html>`)}`;
}

function storyCard(bg, who, action, detail) {
  return card(bg, who, action,
    `<div class="extra">${detail}</div>`
  );
}

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
  await sleep(500);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }),
    page.click('#kc-login'),
  ]);
  console.log(`    Logged in as ${username}`);
  await sleep(2000);
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

async function waitForImages(page) {
  await page.evaluate(() => Promise.all(
    Array.from(document.querySelectorAll('img')).map(img => {
      if (img.complete) return Promise.resolve();
      return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
    })
  ));
}

async function smoothScroll(page, selector, block = 'center') {
  await page.evaluate((sel, blk) => {
    const el = document.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: blk });
  }, selector, block);
  await sleep(1500);
}

(async () => {
  console.log(`\n  BORROWHOOD -- The Complete Walkthrough`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Resolution: ${VP.width}x${VP.height}`);
  console.log(`  Duration: ~5-8 minutes\n`);

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
    '<div class="extra">THE COMPLETE WALKTHROUGH | BorrowHood</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: INTRO -- What is BorrowHood?
  // ============================================================
  console.log('  Scene 2: Intro');
  await page.goto(card(
    '#1E293B',
    'BORROWHOOD',
    'Every garage becomes a rental shop.',
    '<div class="extra">' +
    'Your neighbor has a drill you need once.<br>' +
    'You have a stand mixer sitting idle.<br>' +
    'BorrowHood connects you. No middlemen. No fees.<br><br>' +
    'This is the full walkthrough. Two neighbors. One rental. Every step.' +
    '</div>'
  ));
  await sleep(10000);

  // ============================================================
  // SCENE 3: HOME PAGE
  // ============================================================
  console.log('  Scene 3: Home page');
  await page.goto(`${BASE}/?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  // Scroll down slowly to show the full home page
  await page.evaluate(() => window.scrollBy({ top: 600, behavior: 'smooth' }));
  await sleep(3000);
  await page.evaluate(() => window.scrollBy({ top: 600, behavior: 'smooth' }));
  await sleep(3000);

  // ============================================================
  // SCENE 4: BROWSE PAGE -- Finding what you need
  // ============================================================
  console.log('  Scene 4: Browse page');
  await page.goto(card(
    '#4338CA',
    'STEP 1',
    'Sally needs a drill for her deck project.',
    '<div class="extra">She opens BorrowHood and browses the neighborhood.</div>'
  ));
  await sleep(5000);

  await page.goto(`${BASE}/browse?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  // Scroll to show items with prices and deposits
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);

  // ============================================================
  // SCENE 5: ITEM DETAIL -- Mike's Bosch Drill
  // ============================================================
  console.log('  Scene 5: Bosch Drill detail');
  await page.goto(card(
    '#4338CA',
    'MIKE\'S DRILL',
    'Bosch Professional -- EUR 8/day + EUR 30 deposit',
    '<div class="extra">' +
    'Mike listed his drill last month. It sits in his garage most days.<br>' +
    'EUR 8/day to rent. EUR 30 deposit in case something breaks.<br>' +
    'Sally found it on Browse. Let\'s take a look.' +
    '</div>'
  ));
  await sleep(6000);

  await page.goto(`${BASE}/items/bosch-professional-drill-driver-set?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  // Scroll to see price, deposit, and Rent button
  await page.evaluate(() => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.includes('deposit') && el.offsetHeight < 50) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
  });
  await sleep(3000);

  // Scroll to see gallery images
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await sleep(2000);

  // Scroll down to reviews section
  await page.evaluate(() => {
    const el = document.querySelector('[x-data*="reviewSection"]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  await sleep(4000);

  // ============================================================
  // SCENE 6: SALLY LOGS IN + RENTS
  // ============================================================
  console.log('  Scene 6: Sally logs in');
  await page.goto(storyCard(
    '#7C3AED',
    'SALLY THOMPSON',
    'She wants the drill. Time to rent it.',
    'Sally logs in and requests the rental.<br>' +
    'She picks her dates and sends Mike a message.'
  ));
  await sleep(5000);

  await kcLogin(page, 'sally');

  // Navigate to the drill
  await page.goto(`${BASE}/items/bosch-professional-drill-driver-set?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(3000);

  // Scroll to Rent button
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Rent')) { b.scrollIntoView({ behavior: 'smooth', block: 'center' }); break; }
    }
  });
  await sleep(2000);

  // Click "Rent This Item"
  console.log('    Clicking Rent This Item...');
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Rent') && !b.closest('.fixed')) { b.click(); break; }
    }
  });
  await sleep(2000);

  // Fill in the rental form
  console.log('    Filling rental form...');
  try {
    // Set dates
    const today = new Date();
    const start = new Date(today);
    start.setDate(start.getDate() + 2);
    const end = new Date(today);
    end.setDate(end.getDate() + 5);
    const startStr = start.toISOString().split('T')[0];
    const endStr = end.toISOString().split('T')[0];

    await page.evaluate((s, e) => {
      const inputs = document.querySelectorAll('.fixed input[type="date"]');
      if (inputs[0]) { inputs[0].value = s; inputs[0].dispatchEvent(new Event('input', { bubbles: true })); }
      if (inputs[1]) { inputs[1].value = e; inputs[1].dispatchEvent(new Event('input', { bubbles: true })); }
    }, startStr, endStr);
    await sleep(1000);

    // Type message
    await page.evaluate(() => {
      const ta = document.querySelector('.fixed textarea');
      if (ta) { ta.focus(); ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); }
    });
    await page.type('.fixed textarea',
      "Hi Mike! I'm building a new deck this weekend and need a good drill. I'll take great care of it. Can pick up Friday morning.",
      { delay: 30 }
    );
    await sleep(3000);

    // Submit
    console.log('    Submitting rental request...');
    await page.evaluate(() => {
      const modal = document.querySelector('.fixed');
      if (!modal) return;
      const btns = modal.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Submit') || b.textContent.includes('Request') || b.textContent.includes('Rent')) {
          b.click(); return;
        }
      }
    });
    await sleep(3000);
  } catch (err) {
    console.log(`    Rental form error: ${err.message.slice(0, 80)}`);
  }

  // Show Sally's dashboard -- My Rentals tab
  console.log('    Sally\'s dashboard...');
  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  // Click "My Rentals" tab
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('My Rental') || b.textContent.includes('Renting')) { b.click(); break; }
    }
  });
  await sleep(4000);

  // ============================================================
  // SCENE 7: MIKE SEES THE REQUEST + APPROVES
  // ============================================================
  console.log('  Scene 7: Mike approves');
  await kcLogout(page);

  await page.goto(storyCard(
    '#1E40AF',
    'MIKE KENEL',
    'He gets a notification. Sally wants his drill.',
    'Mike opens his dashboard and sees the request.<br>' +
    'He reads Sally\'s message and clicks Approve.'
  ));
  await sleep(5000);

  await kcLogin(page, 'mike');

  // Mike's dashboard -- Incoming Requests
  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  // Click Incoming Requests tab
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Incoming')) { b.click(); break; }
    }
  });
  await sleep(4000);

  // Find the Bosch Drill request and click Approve
  console.log('    Approving the rental...');
  try {
    await page.evaluate(() => {
      // Find the card with "Bosch" or "Drill" and click Approve
      const cards = document.querySelectorAll('.bg-white.rounded-lg.border, [class*="rounded-lg"]');
      for (const card of cards) {
        if (card.textContent.includes('Bosch') || card.textContent.includes('Drill')) {
          const btns = card.querySelectorAll('button');
          for (const b of btns) {
            if (b.textContent.trim() === 'Approve') { b.click(); return; }
          }
        }
      }
    });

    // Wait for page reload
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(3000);
  } catch (err) {
    console.log(`    Approve error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 8: MIKE GENERATES LOCKBOX CODES
  // ============================================================
  console.log('  Scene 8: Lockbox codes');
  await page.goto(storyCard(
    '#D97706',
    'LOCKBOX CODES',
    'Contactless exchange. No meetup needed.',
    'Mike types where the drill is and generates two codes:<br>' +
    'a pickup code and a return code.<br>' +
    'Sally sees the pickup code on her dashboard.'
  ));
  await sleep(6000);

  // Go to Mike's dashboard, Incoming Requests tab
  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Incoming')) { b.click(); break; }
    }
  });
  await sleep(3000);

  // Fill in lockbox form: location + instructions, then generate codes
  try {
    // Find the location input in the lockbox section
    const locationInput = await page.$('input[placeholder*="location" i], input[x-model="locationHint"]');
    if (locationInput) {
      await locationInput.click();
      await locationInput.type('Garden shed, left shelf, behind the mower', { delay: 40 });
      await sleep(500);
    }

    const instructionsInput = await page.$('input[placeholder*="instruction" i], input[x-model="instructions"]');
    if (instructionsInput) {
      await instructionsInput.click();
      await instructionsInput.type('Side gate code: 4521. Drill is in the red case.', { delay: 40 });
      await sleep(500);
    }

    await sleep(2000);

    // Click Generate Codes
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Generate')) { b.click(); return; }
      }
    });
    await sleep(4000);
  } catch (err) {
    console.log(`    Lockbox error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 9: SALLY PICKS UP (sees pickup code, confirms)
  // ============================================================
  console.log('  Scene 9: Sally picks up');
  await kcLogout(page);

  await page.goto(storyCard(
    '#7C3AED',
    'SALLY PICKS UP',
    'She sees the pickup code on her dashboard.',
    'Sally goes to Mike\'s garden shed.<br>' +
    'She finds the drill in the red case, just like Mike said.<br>' +
    'She clicks "I\'ve Picked It Up" on her phone.'
  ));
  await sleep(6000);

  await kcLogin(page, 'sally');

  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  // Click My Rentals tab
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('My Rental') || b.textContent.includes('Renting')) { b.click(); break; }
    }
  });
  await sleep(4000);

  // Click "I've Picked It Up" button
  try {
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Picked It Up')) { b.click(); return; }
      }
    });
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(3000);

    // Click My Rentals tab again after reload
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('My Rental') || b.textContent.includes('Renting')) { b.click(); break; }
      }
    });
    await sleep(3000);
  } catch (err) {
    console.log(`    Pickup error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 10: SALLY RETURNS THE DRILL
  // ============================================================
  console.log('  Scene 10: Sally returns');
  await page.goto(storyCard(
    '#7C3AED',
    'SALLY RETURNS IT',
    'Deck is done. Drill goes back.',
    'Sally puts the drill back in the red case.<br>' +
    'Returns it to the garden shed.<br>' +
    'Clicks "I\'ve Returned It" on her dashboard.'
  ));
  await sleep(5000);

  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('My Rental') || b.textContent.includes('Renting')) { b.click(); break; }
    }
  });
  await sleep(3000);

  // Click "I've Returned It"
  try {
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Returned It')) { b.click(); return; }
      }
    });
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(3000);

    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('My Rental') || b.textContent.includes('Renting')) { b.click(); break; }
      }
    });
    await sleep(3000);
  } catch (err) {
    console.log(`    Return error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 11: MIKE COMPLETES THE RENTAL
  // ============================================================
  console.log('  Scene 11: Mike completes');
  await kcLogout(page);

  await page.goto(storyCard(
    '#1E40AF',
    'MIKE COMPLETES',
    'Drill is back. All good.',
    'Mike checks his garden shed. Drill is there, in the red case.<br>' +
    'He clicks "Complete" on his dashboard.<br>' +
    'Sally\'s EUR 30 deposit is automatically released back to her.'
  ));
  await sleep(6000);

  await kcLogin(page, 'mike');

  await page.goto(`${BASE}/dashboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(2000);

  // Incoming Requests tab
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    for (const b of btns) {
      if (b.textContent.includes('Incoming')) { b.click(); break; }
    }
  });
  await sleep(3000);

  // Click Complete
  try {
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.trim() === 'Complete') { b.click(); return; }
      }
    });
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
    await sleep(3000);

    // Show the completed state
    await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const b of btns) {
        if (b.textContent.includes('Incoming')) { b.click(); break; }
      }
    });
    await sleep(4000);
  } catch (err) {
    console.log(`    Complete error: ${err.message.slice(0, 80)}`);
  }

  // ============================================================
  // SCENE 12: WHAT JUST HAPPENED (recap card)
  // ============================================================
  console.log('  Scene 12: Recap');
  await kcLogout(page);

  await page.goto(card(
    '#059669',
    'DONE.',
    'That\'s the whole flow.',
    '<div class="extra" style="line-height: 2;">' +
    'Sally found the drill on Browse<br>' +
    'She requested the rental with dates and a message<br>' +
    'Mike approved it from his dashboard<br>' +
    'Mike generated lockbox codes (no meetup needed)<br>' +
    'Sally picked it up using the code<br>' +
    'Sally returned it when she was done<br>' +
    'Mike completed the rental<br>' +
    'Deposit auto-released back to Sally<br>' +
    'Both earned reputation points and badges' +
    '</div>'
  ));
  await sleep(12000);

  // ============================================================
  // SCENE 13: WORKSHOP PROFILE -- Every user is a shop
  // ============================================================
  console.log('  Scene 13: Workshop profile');
  await page.goto(card(
    '#1E293B',
    'EVERY USER IS A WORKSHOP',
    'Mike\'s garage. Sally\'s kitchen. Your skill.',
    '<div class="extra">Workshop profiles show skills, languages, items, and reputation.</div>'
  ));
  await sleep(5000);

  await page.goto(`${BASE}/workshop/mikes-garage?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  await page.evaluate(() => window.scrollBy({ top: 500, behavior: 'smooth' }));
  await sleep(3000);

  // Sally's workshop too
  await page.goto(`${BASE}/workshop/sallys-kitchen?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  await page.evaluate(() => window.scrollBy({ top: 500, behavior: 'smooth' }));
  await sleep(3000);

  // ============================================================
  // SCENE 14: MEMBERS PAGE
  // ============================================================
  console.log('  Scene 14: Members');
  await page.goto(`${BASE}/members?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);

  // ============================================================
  // SCENE 15: HELPBOARD
  // ============================================================
  console.log('  Scene 15: Helpboard');
  await page.goto(card(
    '#1E293B',
    'HELPBOARD',
    'Need something? Ask the neighborhood.',
    '<div class="extra">"I need a ladder this Saturday"<br>"Anyone have a pressure washer?"<br>Post a request. Get replies. Track status.</div>'
  ));
  await sleep(5000);

  await page.goto(`${BASE}/helpboard?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(4000);

  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);

  // ============================================================
  // SCENE 16: ITALIAN -- One click, everything translates
  // ============================================================
  console.log('  Scene 16: Italian');
  await page.goto(card(
    '#1E293B',
    'ITALIANO',
    'One click. Every label. Instant.',
    '<div class="extra">476 translated strings. Navigation, forms, badges,<br>categories, filters, error messages -- nothing left behind.</div>'
  ));
  await sleep(5000);

  await page.goto(`${BASE}/browse?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
  await waitForImages(page);
  await sleep(4000);

  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await sleep(3000);

  // ============================================================
  // SCENE 17: OUTRO
  // ============================================================
  console.log('  Scene 17: Outro');
  await page.goto(card(
    '#1E293B',
    'BORROWHOOD',
    'Every garage becomes a rental shop.',
    '<div class="extra" style="line-height: 2;">' +
    'Open source. No platform fees. Forever.<br><br>' +
    'github.com/akenel/borrowhood<br>' +
    'Built from a camper van in Trapani, Sicily.<br><br>' +
    '<em>"Every neighborhood has a garage like his."</em>' +
    '</div>'
  ));
  await sleep(10000);

  // ============================================================
  // DONE
  // ============================================================
  await page.goto(card('#1E293B', 'CUT', 'Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
