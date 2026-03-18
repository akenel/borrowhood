#!/usr/bin/env node
// ============================================================
// EP5 Shared Helpers — Used by all shot scripts
// ============================================================

const puppeteer = require('puppeteer');
const readline = require('readline');

const BASE = process.argv[2] || 'https://borrowhood.duckdns.org';
const VP = { width: 1920, height: 1080 };

// ── Utilities ─────────────────────────────────────────────

function waitForEnter(msg) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(`\n>>> ${msg} [ENTER] `, () => { rl.close(); resolve(); }));
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// Retry wrapper for network-sensitive operations (hotspot micro-drops)
async function retry(fn, label = 'operation', attempts = 3) {
  for (let i = 1; i <= attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === attempts) throw err;
      const isNetwork = err.message && (
        err.message.includes('ERR_NETWORK') ||
        err.message.includes('ERR_CONNECTION') ||
        err.message.includes('ERR_NAME') ||
        err.message.includes('net::')
      );
      if (!isNetwork) throw err;
      console.log(`  RETRY ${i}/${attempts}: ${label} (${err.message.split(' at ')[0].trim()})`);
      await sleep(2000 * i);
    }
  }
}

// ── Title Cards ───────────────────────────────────────────

function card(bg, title, subtitle, extra) {
  return `data:text/html,${encodeURIComponent(`<!DOCTYPE html>
<html><head><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:100vw;height:100vh;display:flex;flex-direction:column;
justify-content:center;align-items:center;text-align:center;
font-family:'Georgia',serif;color:#fff;overflow:hidden;
zoom:1 !important;
background:${bg}}
h1{font-size:148px;line-height:1.1;margin-bottom:24px;text-shadow:0 4px 30px rgba(0,0,0,.4)}
h2{font-size:64px;opacity:.85;font-weight:normal;margin-bottom:16px}
.extra{font-size:46px;opacity:.65;margin-top:20px;line-height:1.4}
.hl{color:#f5a623}.red{color:#e94560}.green{color:#6bcb77}
.dim{opacity:.5}.step{color:#aaa;font-size:38px}
</style></head><body>
<h1>${title}</h1>
${subtitle ? `<h2>${subtitle}</h2>` : ''}
${extra ? `<div class="extra">${extra}</div>` : ''}
</body></html>`)}`;
}

// ── API ───────────────────────────────────────────────────

async function apiCall(page, method, path, body) {
  return page.evaluate(async (b, m, p, bd) => {
    const r = await fetch(`${b}${p}`, {
      method: m, credentials: 'include',
      headers: bd ? { 'Content-Type': 'application/json' } : {},
      body: bd ? JSON.stringify(bd) : undefined
    });
    return { status: r.status, data: await r.json().catch(() => null) };
  }, BASE, method, path, body);
}

// ── Login / Logout ────────────────────────────────────────

async function visibleLogin(page, username) {
  await retry(() => page.goto(`${BASE}/demo-login`, { waitUntil: 'networkidle2', timeout: 15000 }), `login ${username}`);
  await sleep(1500);
  await setZoom(page);
  await sleep(500);

  const clicked = await page.evaluate((uname) => {
    const buttons = [...document.querySelectorAll('button, a, [role="button"]')];
    const btn = buttons.find(b => {
      const text = (b.textContent || '').toLowerCase();
      return text.includes(`@${uname}`) || text.includes(uname);
    });
    if (btn) {
      btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return { found: true, x: btn.getBoundingClientRect().x + btn.getBoundingClientRect().width / 2,
               y: btn.getBoundingClientRect().y + btn.getBoundingClientRect().height / 2 };
    }
    return { found: false };
  }, username);

  if (clicked.found) {
    await sleep(600);
    await showRing(page, clicked.x, clicked.y);
    await sleep(400);
    await page.mouse.click(clicked.x, clicked.y);
    await sleep(2000);
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
  }

  const loggedIn = await page.evaluate(() => {
    const nav = document.querySelector('nav');
    return nav ? !nav.textContent.includes('Log In') : true;
  });

  if (!loggedIn) {
    console.log(`  WARN: visibleLogin failed for ${username}, falling back to API`);
    await demoLogin(page, username);
  }
}

async function demoLogin(page, username) {
  // Navigate to demo-login page and click the user button (sets cookie via real browser action)
  await retry(() => page.goto(`${BASE}/demo-login`, { waitUntil: 'networkidle2', timeout: 15000 }), `demoLogin ${username}`);
  await sleep(1000);
  const clicked = await page.evaluate((uname) => {
    const buttons = [...document.querySelectorAll('button, a, [role="button"]')];
    const btn = buttons.find(b => {
      const text = (b.textContent || '').toLowerCase();
      return text.includes(`@${uname}`) || text.includes(uname);
    });
    if (btn) { btn.click(); return true; }
    return false;
  }, username);
  if (clicked) {
    await sleep(2000);
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
  } else {
    // Fallback to API + page reload
    await apiCall(page, 'POST', '/api/v1/demo/login', { username, password: 'helix_pass' });
    await retry(() => page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 10000 }), `demoLogin fallback ${username}`);
  }
}

async function demoLogout(page) {
  const url = page.url();
  if (url.startsWith('data:')) {
    await retry(() => page.goto(BASE, { waitUntil: 'networkidle2', timeout: 10000 }), 'logout nav');
    await sleep(500);
  }
  // bh_session is httponly -- document.cookie can't touch it. Use CDP.
  const domain = new URL(BASE).hostname;
  await page.deleteCookie({ name: 'bh_session', domain, path: '/' });
  await sleep(300);
}

// ── Visual Effects ────────────────────────────────────────

function showOverlay(page, name, subtitle, extra, duration = 4000) {
  return page.evaluate(async (n, s, e, d) => {
    // Reset zoom so overlay covers the full viewport
    const origZoom = document.body.style.zoom || '1';
    document.body.style.zoom = '1';
    const ov = document.createElement('div');
    ov.id = 'scene-overlay';
    Object.assign(ov.style, {
      position: 'fixed', top: '0', left: '0', width: '100vw', height: '100vh',
      display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
      textAlign: 'center', zIndex: '99999', fontFamily: 'Georgia, serif', color: '#fff',
      background: 'rgba(0,0,0,0.92)', opacity: '0', transition: 'opacity 0.6s ease',
      overflow: 'auto', padding: '40px'
    });
    ov.innerHTML = `<h1 style="font-size:96px;margin-bottom:16px;text-shadow:0 4px 20px rgba(0,0,0,.5)">${n}</h1>
      ${s ? `<h2 style="font-size:48px;opacity:.85;font-weight:normal">${s}</h2>` : ''}
      ${e ? `<div style="font-size:36px;opacity:.6;margin-top:20px">${e}</div>` : ''}`;
    document.body.appendChild(ov);
    await new Promise(r => setTimeout(r, 50));
    ov.style.opacity = '1';
    await new Promise(r => setTimeout(r, d));
    ov.style.opacity = '0';
    await new Promise(r => setTimeout(r, 600));
    ov.remove();
    // Restore original zoom
    document.body.style.zoom = origZoom;
  }, name, subtitle, extra, duration);
}

async function showRing(page, x, y) {
  await page.evaluate((rx, ry) => {
    const ring = document.createElement('div');
    Object.assign(ring.style, {
      position: 'fixed', left: `${rx - 30}px`, top: `${ry - 30}px`,
      width: '60px', height: '60px', borderRadius: '50%',
      border: '5px solid #DC2626', zIndex: '99999',
      pointerEvents: 'none', animation: 'clickRingPulse 1.2s ease-out'
    });
    if (!document.querySelector('#clickRingStyle')) {
      const style = document.createElement('style');
      style.id = 'clickRingStyle';
      style.textContent = `@keyframes clickRingPulse {
        0% { transform: scale(0.5); opacity: 1; }
        100% { transform: scale(2); opacity: 0; }
      }`;
      document.head.appendChild(style);
    }
    document.body.appendChild(ring);
    setTimeout(() => ring.remove(), 1500);
  }, x, y);
}

async function smoothScroll(page, pixels, duration = 1500) {
  await page.evaluate(async (px, dur) => {
    const start = window.scrollY;
    const startTime = performance.now();
    await new Promise(resolve => {
      function step(now) {
        const t = Math.min((now - startTime) / dur, 1);
        const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        window.scrollTo(0, start + px * ease);
        if (t < 1) requestAnimationFrame(step); else resolve();
      }
      requestAnimationFrame(step);
    });
  }, pixels, duration);
}

async function setZoom(page) {
  await page.evaluate(() => { document.body.style.zoom = '1.5'; });
  await sleep(300);
}

// ── Click Helpers ─────────────────────────────────────────

async function clickWithRing(page, text, scope = 'body') {
  const coords = await page.evaluate((t, s) => {
    const els = [...document.querySelectorAll(`${s} button, ${s} a, ${s} [role="button"], ${s} input[type="submit"]`)];
    const el = els.find(e => {
      const r = e.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && e.textContent.trim().includes(t);
    });
    if (!el) return null;
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const r = el.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  }, text, scope);

  if (!coords) {
    console.log(`  WARN: clickWithRing could not find "${text}" in ${scope}`);
    return false;
  }
  await sleep(600);
  await showRing(page, coords.x, coords.y);
  await sleep(400);
  await page.mouse.click(coords.x, coords.y);
  await sleep(1500);
  return true;
}

async function clickSelector(page, selector) {
  const coords = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const r = el.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  }, selector);

  if (!coords) {
    console.log(`  WARN: clickSelector could not find "${selector}"`);
    return false;
  }
  await sleep(400);
  await showRing(page, coords.x, coords.y);
  await sleep(400);
  await page.mouse.click(coords.x, coords.y);
  await sleep(1000);
  return true;
}

// ── User ID Resolution ────────────────────────────────────

const userIdCache = {};

async function getMyId(page) {
  return page.evaluate(async (b) => {
    const r = await fetch(`${b}/api/v1/users/me`, { credentials: 'include' });
    if (r.ok) { const d = await r.json(); return d.id; }
    return null;
  }, BASE);
}

async function resolveUserIds(page) {
  const cast = ['john', 'leonardo', 'mike', 'sally', 'nino', 'sofiaferretti'];
  const domain = new URL(BASE).hostname;
  await sleep(1000); // Let page context settle before first fetch

  for (const username of cast) {
    try {
      const url = page.url();
      if (!url.startsWith(BASE)) {
        await retry(() => page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 }), 'resolveUserIds nav');
        await sleep(500);
      }
      await retry(() => apiCall(page, 'POST', '/api/v1/demo/login', { username, password: 'helix_pass' }), `login ${username}`);
      const id = await getMyId(page);
      if (id) {
        userIdCache[username] = id;
        console.log(`  Resolved ${username} → ${id}`);
      } else {
        console.log(`  WARN: Could not resolve ID for ${username}`);
      }
    } catch (err) {
      console.log(`  WARN: resolveUserIds failed for ${username}: ${err.message}`);
    }
    await page.deleteCookie({ name: 'bh_session', domain, path: '/' });
  }

  // Retry any that failed (hotspot micro-drops)
  const missing = cast.filter(u => !userIdCache[u]);
  for (const username of missing) {
    try {
      await retry(() => page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 }), `retry nav ${username}`);
      await sleep(500);
      await retry(() => apiCall(page, 'POST', '/api/v1/demo/login', { username, password: 'helix_pass' }), `retry login ${username}`);
      const id = await getMyId(page);
      if (id) {
        userIdCache[username] = id;
        console.log(`  Resolved ${username} → ${id} (retry)`);
      }
    } catch (err) {
      console.log(`  WARN: retry failed for ${username}: ${err.message}`);
    }
    await page.deleteCookie({ name: 'bh_session', domain, path: '/' });
  }
}

function getUserId(username) {
  return userIdCache[username] || null;
}

// ── Navigation ────────────────────────────────────────────

async function navigateTo(page, path) {
  await retry(() => page.goto(`${BASE}${path}`, { waitUntil: 'networkidle2', timeout: 15000 }), `navigate ${path}`);
  await sleep(1000);
  await setZoom(page);
  await sleep(500);
}

async function typeSlowly(page, selector, text, delay = 40) {
  await page.focus(selector);
  await sleep(200);
  for (const ch of text) {
    await page.keyboard.type(ch, { delay });
  }
  await sleep(300);
}

// ── Browser Launcher ──────────────────────────────────────

async function launchBrowser() {
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--start-fullscreen', '--no-sandbox', '--ignore-certificate-errors',
           '--disable-features=TranslateUI', '--lang=en'],
  });
  const page = (await browser.pages())[0];
  await page.setViewport(VP);

  // Block heavy images on non-recording pages to save hotspot data.
  // Call page.setRequestInterception(false) before going on camera.
  // Pollinations images are 200-500KB each -- 10 listing cards = 3-5MB wasted.
  await page.setRequestInterception(true);
  page._blockImages = true;
  page.on('request', req => {
    if (page._blockImages && req.resourceType() === 'image') {
      req.abort();
    } else {
      req.continue();
    }
  });

  return { browser, page };
}

// Call before going on camera -- re-enables images for recording
async function enableImages(page) {
  page._blockImages = false;
}

// Call after recording -- blocks images again to save data
async function disableImages(page) {
  page._blockImages = true;
}

// ── Connection Check ─────────────────────────────────────

// Verify server is reachable before burning a take.
// Hits a lightweight endpoint, retries 3x with backoff.
async function checkConnection(page) {
  console.log('  Connection check...');
  for (let i = 1; i <= 3; i++) {
    try {
      const result = await page.evaluate(async (b) => {
        const r = await fetch(`${b}/api/v1/health`, { credentials: 'include' });
        return r.ok;
      }, BASE);
      if (result) {
        console.log('  Connection OK');
        return true;
      }
    } catch (err) {
      console.log(`  Connection attempt ${i}/3 failed: ${err.message.split(' at ')[0].trim()}`);
      if (i < 3) await sleep(3000 * i);
    }
  }
  console.log('  WARN: Connection unstable -- proceed with caution');
  return false;
}

// Warm up the connection -- makes the first real page load faster.
// TLS handshake + DNS resolution happen here, not on camera.
async function warmConnection(page) {
  console.log('  Warming connection...');
  await retry(() => page.goto(BASE, { waitUntil: 'networkidle2', timeout: 20000 }), 'warmup');
  await sleep(1000);
  // Hit demo-login to warm Keycloak too (the main failure point)
  await retry(() => page.goto(`${BASE}/demo-login`, { waitUntil: 'networkidle2', timeout: 20000 }), 'keycloak warmup');
  await sleep(1000);
  console.log('  Connection warm');
}

// ── Pre-Roll / End-Roll Cards ────────────────────────────

async function preRoll(page, shotLabel) {
  await page.goto(card(
    '#DC2626',
    'RECORDING',
    shotLabel,
    '<span class="dim">OBS should be running</span>'
  ), { waitUntil: 'load' });
  await sleep(5000);
}

async function endRoll(page) {
  await page.goto(card(
    '#1a1a2e',
    'STOP OBS NOW',
    'Shot complete',
    '<span class="dim">Press ENTER in terminal when OBS is stopped</span>'
  ), { waitUntil: 'load' });
}

// ── Exports ───────────────────────────────────────────────

module.exports = {
  BASE, VP,
  waitForEnter, sleep, retry, card,
  apiCall, visibleLogin, demoLogin, demoLogout,
  showOverlay, showRing, smoothScroll, setZoom,
  clickWithRing, clickSelector,
  userIdCache, getMyId, resolveUserIds, getUserId,
  navigateTo, typeSlowly,
  launchBrowser, enableImages, disableImages,
  checkConnection, warmConnection,
  preRoll, endRoll,
};
