#!/usr/bin/env node
/**
 * THE LEGENDS -- 272 Members, 10 Eras, One Brotherhood (v1)
 *
 * What we built today:
 *   - 315 members (272 legends)
 *   - 721 items (acting classes, combat training, lab workshops, martial arts)
 *   - 216 DiceBear avatars (10 distinct styles mapped to era/personality)
 *   - 12 new workshop types (arena, dojo, laboratory, forge, fortress, observatory...)
 *   - 7 new item categories (education, science, engineering, tools, outdoor...)
 *
 * The video visits:
 *   CINEMA:    Bruce Lee's Dojo, Audrey Hepburn's Atelier
 *   WARRIORS:  Spartacus Arena, Joan of Arc's Banner Hall, Musashi's Dojo
 *   INVENTORS: Marie Curie's Lab, Galileo's Observatory
 *
 * Scene Map (20 scenes, ~4 minutes):
 *   1.  OBS CHECK (red)
 *   2.  Intro card -- "THE LEGENDS"
 *   3.  Stats card -- the numbers
 *   4.  Members page -- full grid, slow scroll
 *   5.  Filter to LEGEND tier -- the icons
 *   6.  CINEMA ERA card (amber)
 *   7.  Bruce Lee's Dojo -- profile visit
 *   8.  Audrey Hepburn's Atelier -- profile visit
 *   9.  WARRIOR ERA card (crimson)
 *  10.  Spartacus Arena -- profile visit
 *  11.  Joan of Arc's Banner Hall -- profile visit
 *  12.  Musashi's Niten Dojo -- profile visit
 *  13.  INVENTOR ERA card (indigo)
 *  14.  Marie Curie's Lab -- profile visit
 *  15.  Galileo's Observatory -- profile visit
 *  16.  Browse page -- 721 items
 *  17.  Filter browse by EDUCATION category
 *  18.  Filter browse by SCIENCE category
 *  19.  Feature recap card
 *  20.  CUT
 *
 * Improvements over EP10:
 *   - 128px headings, 64px subtitles, 48px body (bigger than EP10's 96/48/36)
 *   - 5s minimum on ALL scenes, 8-10s for text-heavy cards
 *   - Category-specific accent colors (amber cinema, crimson warriors, indigo inventors)
 *   - Profile visits: scroll to bio + items, inject highlight borders
 *   - Members page: smooth auto-scroll to show avatar variety
 *
 * Rules applied:
 *   - charset=utf-8 in data: URLs (no mojibake)
 *   - showRing() on all visible clicks (Rule 3)
 *   - 150% browser zoom on UI pages (Rule 13)
 *   - 60px click rings, 5px border (Rule 13)
 *   - Extra 2s pause after each UI click (Rule 13)
 *   - Mobile-first card text sizes (Rule 13)
 *
 * Usage: node record-legends.js [base_url]
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

// ── Full-page card (data: URL) ─────────────────────────────────
// IMPROVED: 128px headings, 64px subtitles, 48px body, tighter spacing
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
  h1 { font-size: 128px; font-weight: 800; margin-bottom: 20px; text-shadow: 3px 3px 12px rgba(0,0,0,0.4); letter-spacing: -2px; line-height: 1.0; }
  h2 { font-size: 64px; font-weight: 400; opacity: 0.9; margin-bottom: 16px; line-height: 1.2; }
  .extra { font-size: 48px; opacity: 0.8; margin-top: 12px; line-height: 1.4; max-width: 1600px; }
  .badge { display: inline-block; padding: 12px 36px; border-radius: 12px; background: rgba(255,255,255,0.2); font-size: 44px; font-weight: 600; margin-top: 16px; }
  .hl { color: #FCD34D; font-weight: 700; }
  .dim { opacity: 0.5; }
  .check { color: #34D399; }
  .warn { color: #FBBF24; }
  .stat { font-size: 96px; font-weight: 900; color: #FCD34D; display: block; line-height: 1.1; }
  .stat-label { font-size: 40px; opacity: 0.7; display: block; margin-bottom: 24px; }
  .stats-row { display: flex; justify-content: center; gap: 80px; margin-top: 32px; }
  .stat-block { text-align: center; }
</style></head><body>
  <h1>${title}</h1><h2>${subtitle}</h2>${extra}
</body></html>`)}`;
}

// ── DOM overlay card (stays on current page = BASE origin) ──────
// IMPROVED: bigger fonts, tighter layout, no zoom interference
async function showOverlay(page, name, subtitle, extra = '', bgColor = '#1E293B', duration = 5000) {
  await page.evaluate((n, s, e, bg) => {
    document.body.style.zoom = '1';
    const old = document.getElementById('name-card-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'name-card-overlay';
    overlay.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      z-index: 99999; display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      background: ${bg}; color: white;
      font-family: 'Segoe UI', Arial, sans-serif; text-align: center;
      padding: 40px 60px;
    `;
    overlay.innerHTML = `
      <h1 style="font-size:128px; font-weight:800; margin-bottom:16px;
                 text-shadow:3px 3px 12px rgba(0,0,0,0.4); letter-spacing:-2px; line-height:1.0">${n}</h1>
      <h2 style="font-size:56px; font-weight:400; opacity:0.9;
                 margin-bottom:16px; line-height:1.2">${s}</h2>
      ${e ? `<div style="font-size:44px; opacity:0.8; margin-top:8px; line-height:1.4; max-width:1500px">${e}</div>` : ''}
    `;
    document.body.appendChild(overlay);
  }, name, subtitle, extra, bgColor);
  await sleep(duration);
}

// ── Remove overlay ──────────────────────────────────────────────
async function removeOverlay(page) {
  await page.evaluate(() => {
    const el = document.getElementById('name-card-overlay');
    if (el) el.remove();
  });
}

// ── Show red click ring (Rule 3) ────────────────────────────────
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

// ── Click element with ring ─────────────────────────────────────
async function clickEl(page, selector) {
  const el = await page.$(selector);
  if (!el) { console.log(`  WARN: ${selector} not found`); return; }
  const box = await el.boundingBox();
  if (!box) return;
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  await showRing(page, cx, cy);
  await sleep(400);
  await el.click();
  await sleep(2000);
}

// ── Set browser zoom to 150% (Rule 13) ─────────────────────────
async function setZoom(page) {
  await page.evaluate(() => { document.body.style.zoom = '1.5'; });
}

// ── Smooth auto-scroll ──────────────────────────────────────────
async function smoothScroll(page, distance, duration) {
  await page.evaluate((dist, dur) => {
    const start = window.scrollY;
    const startTime = Date.now();
    function step() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / dur, 1);
      const ease = progress < 0.5
        ? 2 * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 2) / 2;
      window.scrollTo(0, start + dist * ease);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }, distance, duration);
  await sleep(duration + 200);
}

// ── Highlight profile section with colored border ───────────────
async function highlightSection(page, selector, color = '#DC2626') {
  await page.evaluate((sel, col) => {
    const el = document.querySelector(sel);
    if (el) {
      el.style.outline = `4px solid ${col}`;
      el.style.outlineOffset = '4px';
      el.style.borderRadius = '12px';
      el.style.transition = 'outline 0.3s ease';
    }
  }, selector, color);
}

// ── Visit a workshop profile ────────────────────────────────────
async function visitProfile(page, slug, accentColor, pauseMs = 6000) {
  console.log(`    -> visiting /workshop/${slug}`);
  await page.goto(`${BASE}/workshop/${slug}?lang=en`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(1500);

  // Scroll to show the bio section
  await smoothScroll(page, 300, 1500);
  await sleep(2000);

  // Scroll further to show items/skills
  await smoothScroll(page, 400, 1500);
  await sleep(pauseMs - 3500 > 0 ? pauseMs - 3500 : 2000);
}

// ── API helper ──────────────────────────────────────────────────
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


// ═══════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════
(async () => {
  console.log(`\n  THE LEGENDS -- 272 Members, 10 Eras, One Brotherhood`);
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

  // Pre-flight: establish cookie domain
  await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 15000 });
  await sleep(500);
  console.log('  PRE-FLIGHT: connected\n');

  // ============================================================
  // SCENE 1: OBS CHECK (RED)
  // ============================================================
  await page.goto(card(
    '#DC2626',
    'OBS CHECK',
    'Verify this screen is captured in OBS preview',
    '<div class="extra">THE LEGENDS | BorrowHood | Episode 11</div>'
  ));
  await waitForEnter('OBS is recording and showing this RED screen?');

  // ============================================================
  // SCENE 2: INTRO CARD (DEEP SLATE) -- 8s
  // ============================================================
  console.log('  Scene 2: Intro card');
  await page.goto(card(
    'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%)',
    'THE LEGENDS',
    '272 members. 10 eras. One brotherhood.',
    '<div class="extra">' +
    'From <span class="hl">ancient arenas</span> to <span class="hl">modern laboratories</span>.<br>' +
    'Movie stars. Warriors. Inventors.<br>' +
    'Every legend has a workshop. Every workshop has a story.' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 3: STATS CARD (DARK) -- 8s
  // The numbers. Let them sink in.
  // ============================================================
  console.log('  Scene 3: Stats card');
  await page.goto(card(
    '#0F172A',
    '',
    '',
    '<div class="stats-row">' +
    '<div class="stat-block"><span class="stat">315</span><span class="stat-label">Members</span></div>' +
    '<div class="stat-block"><span class="stat">721</span><span class="stat-label">Items</span></div>' +
    '<div class="stat-block"><span class="stat">272</span><span class="stat-label">Legends</span></div>' +
    '</div>' +
    '<div style="margin-top:48px; font-size:48px; opacity:0.6">' +
    '10 DiceBear avatar styles. 12 workshop types. 7 new categories.' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 4: MEMBERS PAGE -- full grid, slow scroll -- 12s
  // Show the scale. 315 profiles. Avatars everywhere.
  // ============================================================
  console.log('  Scene 4: Members page');
  await page.goto(`${BASE}/members?lang=en&limit=24`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(3000);

  // Slow scroll through the member grid
  await smoothScroll(page, 600, 3000);
  await sleep(3000);
  await smoothScroll(page, 600, 3000);
  await sleep(3000);

  // ============================================================
  // SCENE 5: FILTER TO LEGEND TIER -- 8s
  // Show the legend badge filter
  // ============================================================
  console.log('  Scene 5: Filter to legends');
  await page.goto(`${BASE}/members?lang=en&badge_tier=legend&limit=24`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Highlight the badge filter dropdown
  await highlightSection(page, 'select[name="badge_tier"]', '#8B5CF6');
  await sleep(2000);

  // Scroll the legend grid
  await smoothScroll(page, 500, 2500);
  await sleep(3000);

  // ============================================================
  // SCENE 6: CINEMA ERA CARD (AMBER) -- 8s
  // ============================================================
  console.log('  Scene 6: Cinema era card');
  await page.goto(card(
    'linear-gradient(135deg, #78350F 0%, #B45309 50%, #D97706 100%)',
    'THE MOVIE STARS',
    '34 cinema legends. Dojos, ateliers, screening rooms.',
    '<div class="extra">' +
    'Bruce Lee. Audrey Hepburn. Hitchcock. Kubrick.<br>' +
    'Acting classes. Dance lessons. Screenplay workshops.<br>' +
    '<span class="hl">The camera never lies.</span>' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 7: BRUCE LEE'S DOJO -- profile visit -- 8s
  // ============================================================
  console.log('  Scene 7: Bruce Lee profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "BRUCE LEE", "Bruce's Dojo",
    'Martial arts master. Philosopher. Water.',
    '#B45309', 5000);

  await visitProfile(page, 'bruces-dojo', '#D97706', 8000);

  // ============================================================
  // SCENE 8: AUDREY HEPBURN'S ATELIER -- profile visit -- 7s
  // ============================================================
  console.log('  Scene 8: Audrey Hepburn profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "AUDREY HEPBURN", "Audrey's Atelier",
    'Elegance is the only beauty that never fades.',
    '#B45309', 5000);

  await visitProfile(page, 'audreys-atelier', '#D97706', 7000);

  // ============================================================
  // SCENE 9: WARRIOR ERA CARD (CRIMSON) -- 8s
  // ============================================================
  console.log('  Scene 9: Warrior era card');
  await page.goto(card(
    'linear-gradient(135deg, #7F1D1D 0%, #991B1B 50%, #DC2626 100%)',
    'THE WARRIORS',
    '34 warrior legends. Arenas, fortresses, war councils.',
    '<div class="extra">' +
    'Spartacus. Joan of Arc. Musashi. Sun Tzu.<br>' +
    'Combat training. Strategy workshops. Survival skills.<br>' +
    '<span class="hl">Every revolution starts with one who refuses to kneel.</span>' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 10: SPARTACUS ARENA -- profile visit -- 8s
  // ============================================================
  console.log('  Scene 10: Spartacus profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "SPARTACUS", "Spartacus Arena",
    'A free man dies only once. A slave dies every day.',
    '#991B1B', 5000);

  await visitProfile(page, 'spartacus-arena', '#DC2626', 8000);

  // ============================================================
  // SCENE 11: JOAN OF ARC'S BANNER HALL -- profile visit -- 7s
  // ============================================================
  console.log('  Scene 11: Joan of Arc profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "JOAN OF ARC", "Joan's Banner Hall",
    'I am not afraid. I was born to do this.',
    '#991B1B', 5000);

  await visitProfile(page, 'joans-banner-hall', '#DC2626', 7000);

  // ============================================================
  // SCENE 12: MUSASHI'S DOJO -- profile visit -- 7s
  // ============================================================
  console.log('  Scene 12: Musashi profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "MIYAMOTO MUSASHI", "Musashi's Niten Dojo",
    'The way is in training. Do nothing which is of no use.',
    '#991B1B', 5000);

  await visitProfile(page, 'musashis-dojo', '#DC2626', 7000);

  // ============================================================
  // SCENE 13: INVENTOR ERA CARD (INDIGO) -- 8s
  // ============================================================
  console.log('  Scene 13: Inventor era card');
  await page.goto(card(
    'linear-gradient(135deg, #312E81 0%, #3730A3 50%, #4F46E5 100%)',
    'THE INVENTORS',
    '34 inventor legends. Laboratories, observatories, print shops.',
    '<div class="extra">' +
    'Marie Curie. Galileo. Edison. Tesla.<br>' +
    'Lab demonstrations. Science workshops. Engineering classes.<br>' +
    '<span class="hl">The ones who changed the world by asking why.</span>' +
    '</div>'
  ));
  await sleep(8000);

  // ============================================================
  // SCENE 14: MARIE CURIE'S LAB -- profile visit -- 8s
  // ============================================================
  console.log('  Scene 14: Marie Curie profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "MARIE CURIE", "Curie's Radiation Laboratory",
    'Nothing in life is to be feared. It is only to be understood.',
    '#3730A3', 5000);

  await visitProfile(page, 'curies-radiation-lab', '#4F46E5', 8000);

  // ============================================================
  // SCENE 15: GALILEO'S OBSERVATORY -- profile visit -- 7s
  // ============================================================
  console.log('  Scene 15: Galileo profile');
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await showOverlay(page, "GALILEO GALILEI", "Galileo's Observatory",
    'And yet it moves.',
    '#3730A3', 5000);

  await visitProfile(page, 'galileos-observatory', '#4F46E5', 7000);

  // ============================================================
  // SCENE 16: BROWSE PAGE -- 721 items -- 10s
  // Show the scale of the marketplace
  // ============================================================
  console.log('  Scene 16: Browse page - all items');
  await page.goto(`${BASE}/browse?lang=en&limit=24`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  // Slow scroll through the item grid
  await smoothScroll(page, 500, 2500);
  await sleep(2000);
  await smoothScroll(page, 500, 2500);
  await sleep(3000);

  // ============================================================
  // SCENE 17: BROWSE -- EDUCATION CATEGORY -- 8s
  // Filter to training services
  // ============================================================
  console.log('  Scene 17: Browse - education');
  await page.goto(`${BASE}/browse?lang=en&category=education&limit=24`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await highlightSection(page, 'select[name="category"]', '#059669');
  await sleep(1500);

  await smoothScroll(page, 400, 2000);
  await sleep(3000);

  // ============================================================
  // SCENE 18: BROWSE -- SCIENCE CATEGORY -- 8s
  // ============================================================
  console.log('  Scene 18: Browse - science');
  await page.goto(`${BASE}/browse?lang=en&category=science&limit=24`, { waitUntil: 'networkidle2', timeout: 15000 });
  await setZoom(page);
  await sleep(2000);

  await smoothScroll(page, 400, 2000);
  await sleep(3000);

  // ============================================================
  // SCENE 19: FEATURE RECAP (DEEP SLATE) -- 12s
  // Everything the viewer just saw. Let it breathe.
  // ============================================================
  console.log('  Scene 19: Feature recap');
  await page.goto(card(
    'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
    'THE LEGENDS',
    'Feature Complete',
    '<div class="extra" style="text-align:left; max-width:1400px; margin:0 auto; font-size:40px; line-height:1.8">' +
    '<span class="check">&#x2713;</span> <span class="hl">315 members</span> -- the biggest neighborhood on Earth<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">721 items</span> -- from power drills to philosophy workshops<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">272 legends</span> -- 10 eras, from Homer to Banksy<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">10 avatar styles</span> -- pixel-art, personas, avataaars, and more<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">12 workshop types</span> -- arenas, dojos, laboratories, observatories<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">7 new categories</span> -- education, science, engineering, outdoor<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Acting classes</span> from Audrey. <span class="hl">Combat training</span> from Spartacus.<br>' +
    '<span class="check">&#x2713;</span> <span class="hl">Lab workshops</span> from Curie. <span class="hl">Martial arts</span> from Bruce Lee.<br>' +
    '<br>' +
    '<span class="dim">Every legend has a workshop. Every workshop has a story.</span><br>' +
    '<span class="dim">This is BorrowHood.</span>' +
    '</div>'
  ));
  await sleep(12000);

  // ============================================================
  // SCENE 20: CUT
  // ============================================================
  await page.goto(card('#1E293B', 'CUT', 'Stop OBS recording now'));
  await waitForEnter('Recording done. Press ENTER to close browser');
  await browser.close();
  console.log('\n  Done.\n');
})();
