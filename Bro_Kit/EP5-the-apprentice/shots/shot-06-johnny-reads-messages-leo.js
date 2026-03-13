#!/usr/bin/env node
// Shot 06: Johnny reads Nino's message, then uses New Message to write Leo (~2m)
//
// THE SCENE:
//   1. Johnny logs in visibly on demo page
//   2. Johnny sees the message notification badge in navbar
//   3. Johnny clicks the messages icon (ring click)
//   4. Johnny sees Nino's message in conversations, clicks it
//   5. Johnny reads "Bro. Did you see Leo's new listing? Is that... your bike?"
//   6. Pause for viewer to absorb
//   7. Johnny clicks the "New Message" compose button (pen icon)
//   8. Johnny types "Leo" in the search box
//   9. Leonardo appears in results — Johnny clicks him
//  10. Johnny types a practical message about the bike
//  11. Johnny sends it, viewer sees the bubble + single checkmark
//  12. Hold for viewer to read
//
const {
  launchBrowser, waitForEnter, sleep, BASE,
  demoLogout, navigateTo, showOverlay,
  showRing, apiCall, resolveUserIds, getUserId,
  preRoll, endRoll, retry, setZoom, typeSlowly,
} = require('./helpers');

const JOHNNY_MSG = "Leo, I saw the Bianchi. That's my old bike. Can you hold it for me? I'll confirm the purchase for EUR 50. Is the frame straight now? Did you oil the chain and check the brakes?";

(async () => {
  const { browser, page } = await launchBrowser();

  // ── Off-camera setup ──────────────────────────────────
  console.log('Resolving cast IDs...');
  await retry(() => page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 }), 'initial load');
  await resolveUserIds(page);

  const leoId = getUserId('leonardo');
  if (!leoId) console.log('  WARN: Could not resolve leonardo user ID');
  else console.log(`  Leo ID: ${leoId}`);

  await demoLogout(page);

  await waitForEnter('SHOT 06 — Johnny reads Nino, uses New Message for Leo. Start OBS, then ENTER');
  await preRoll(page, 'S1E5 — Shot 06');

  console.log('Scene: Johnny reads messages, writes to Leo');

  // ── 1. Johnny logs in on demo page ────────────────────
  await retry(() => page.goto(`${BASE}/demo-login`, { waitUntil: 'networkidle2', timeout: 15000 }), 'demo-login');
  await sleep(2000);

  // Find Johnny's login card by @username
  const johnBtn = await page.evaluate(() => {
    const buttons = [...document.querySelectorAll('button')];
    const btn = buttons.find(b => (b.textContent || '').includes('@john'));
    if (btn) {
      btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const r = btn.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (johnBtn) {
    await sleep(800);
    await showRing(page, johnBtn.x, johnBtn.y);
    await sleep(600);
    await page.mouse.click(johnBtn.x, johnBtn.y);
    console.log('  Clicked Johnny login card');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
    await sleep(2000);
  } else {
    console.log('  WARN: Johnny button not found, using API login');
    await apiCall(page, 'POST', '/api/v1/demo/login', { username: 'john', password: 'helix_pass' });
    await retry(() => page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 10000 }), 'post-login');
    await sleep(1500);
  }

  // ── 2. Johnny is on dashboard -- show the notification badge ──
  await setZoom(page);
  await sleep(2000);

  // ── 3. Click the messages icon in navbar (blue badge) ──
  console.log('  Looking for messages icon in navbar...');
  const msgIconCoords = await page.evaluate(() => {
    const msgLink = document.querySelector('a[href="/messages"]');
    if (msgLink && msgLink.offsetHeight > 0) {
      const r = msgLink.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (msgIconCoords) {
    await sleep(1000);
    await showRing(page, msgIconCoords.x, msgIconCoords.y);
    await sleep(800);
    await page.mouse.click(msgIconCoords.x, msgIconCoords.y);
    console.log('  Clicked messages icon');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
    await setZoom(page);
    await sleep(2000);
  } else {
    console.log('  WARN: Messages icon not found, navigating directly');
    await navigateTo(page, '/messages');
    await sleep(2000);
  }

  // ── 4. Click Nino's conversation to read his message ──
  console.log('  Looking for Nino conversation...');
  const ninoThread = await page.evaluate(() => {
    const buttons = [...document.querySelectorAll('button')];
    const btn = buttons.find(b => {
      const text = (b.textContent || '').toLowerCase();
      return text.includes('nino');
    });
    if (btn && btn.offsetHeight > 0) {
      btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const r = btn.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (ninoThread) {
    await sleep(800);
    await showRing(page, ninoThread.x, ninoThread.y);
    await sleep(600);
    await page.mouse.click(ninoThread.x, ninoThread.y);
    console.log('  Opened Nino conversation');
  } else {
    console.log('  WARN: Could not find Nino thread');
  }

  // ── 5. Pause for viewer to read Nino's message ────────
  await sleep(5000);
  console.log('  Johnny reads Nino\'s message. Pause.');

  // ── 6. Click the "New Message" compose button ─────────
  console.log('  Clicking New Message button...');
  const composeBtn = await page.evaluate(() => {
    // The compose button is the pen/edit icon button in the sidebar header
    // It's the button next to "Conversations" heading with the SVG icon
    const sidebar = document.querySelector('.md\\:col-span-1');
    if (!sidebar) return null;
    const btns = [...sidebar.querySelectorAll('button')];
    // Find the button with the compose SVG (has title="New message" or similar)
    const btn = btns.find(b => {
      const svg = b.querySelector('svg');
      return svg && b.closest('.bg-gray-50');
    });
    if (btn && btn.offsetHeight > 0) {
      const r = btn.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (composeBtn) {
    await sleep(500);
    await showRing(page, composeBtn.x, composeBtn.y);
    await sleep(600);
    await page.mouse.click(composeBtn.x, composeBtn.y);
    console.log('  Clicked New Message button');
    await sleep(1000);
  } else {
    console.log('  WARN: New Message button not found');
  }

  // ── 7. Type "Leo" in the member search ────────────────
  console.log('  Searching for Leo...');
  // Wait for the search input to appear
  await page.waitForSelector('input[placeholder*="Search members"], input[placeholder*="Cerca membro"]', { visible: true, timeout: 5000 }).catch(() => {});
  await sleep(500);

  const searchInput = await page.evaluate(() => {
    const input = document.querySelector('input[placeholder*="Search members"], input[placeholder*="Cerca membro"]');
    if (input && input.offsetHeight > 0) {
      const r = input.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (searchInput) {
    await page.mouse.click(searchInput.x, searchInput.y);
    await sleep(300);
    await typeSlowly(page, 'input[placeholder*="Search members"], input[placeholder*="Cerca membro"]', 'Leo', 80);
    console.log('  Typed "Leo" in search');
    await sleep(2000); // Wait for debounce + API response
  }

  // ── 8. Click Leonardo in search results ───────────────
  console.log('  Looking for Leonardo in results...');
  const leoResult = await page.evaluate(() => {
    // Search result buttons inside the dropdown
    const dropdown = document.querySelector('.absolute.z-10');
    if (!dropdown) return null;
    const btns = [...dropdown.querySelectorAll('button')];
    const btn = btns.find(b => {
      const text = (b.textContent || '').toLowerCase();
      return text.includes('leo');
    });
    if (btn && btn.offsetHeight > 0) {
      const r = btn.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (leoResult) {
    await sleep(500);
    await showRing(page, leoResult.x, leoResult.y);
    await sleep(600);
    await page.mouse.click(leoResult.x, leoResult.y);
    console.log('  Selected Leonardo from search results');
    await sleep(2000);
  } else {
    // Fallback: navigate directly
    console.log('  WARN: Leonardo not found in search, using direct navigation');
    if (leoId) {
      await navigateTo(page, `/messages?to=${leoId}`);
      await sleep(3000);
    }
  }

  // ── 9. Type the message live ──────────────────────────
  console.log('  Typing message to Leo...');
  await page.waitForSelector('input[x-model="newMessage"]', { visible: true, timeout: 10000 }).catch(() => {});
  await sleep(500);
  await page.click('input[x-model="newMessage"]');
  await sleep(500);
  await typeSlowly(page, 'input[x-model="newMessage"]', JOHNNY_MSG, 30);
  await sleep(2000);

  // ── 10. Click Send with ring ──────────────────────────
  const sendCoords = await page.evaluate(() => {
    const btn = document.querySelector('form button[type="submit"]');
    if (btn && btn.offsetHeight > 0) {
      const r = btn.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }
    return null;
  });

  if (sendCoords) {
    await showRing(page, sendCoords.x, sendCoords.y);
    await sleep(600);
    await page.mouse.click(sendCoords.x, sendCoords.y);
    console.log('  Message sent to Leo!');
  } else {
    console.log('  WARN: Send button not found, submitting form');
    await page.evaluate(() => {
      const form = document.querySelector('form');
      if (form) form.dispatchEvent(new Event('submit', { cancelable: true }));
    });
  }

  // ── 11. Hold for viewer to absorb ─────────────────────
  // Viewer sees: sent bubble + single checkmark (not yet read by Leo)
  await sleep(6000);

  // ── End ────────────────────────────────────────────────
  await endRoll(page);
  await waitForEnter('SHOT 06 done. Stop OBS, then ENTER');
  await browser.close();
  console.log('Shot 06 complete.');
})();
