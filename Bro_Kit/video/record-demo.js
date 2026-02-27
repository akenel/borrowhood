#!/usr/bin/env node
/**
 * BorrowHood Demo Video - Puppeteer Screenshot Capture
 *
 * Captures high-res screenshots of the happy flow.
 * Each frame becomes a scene in the final video.
 *
 * Usage: node record-demo.js [base_url]
 * Default: https://46.62.138.218
 */

const puppeteer = require('puppeteer');
const path = require('path');

const BASE = process.argv[2] || 'https://46.62.138.218';
const FRAMES = path.join(__dirname, 'frames');
const WIDTH = 1920;
const HEIGHT = 1080;

// Scene definitions: [filename, url, scrollY, waitMs, description]
// ORDER MATTERS: All English scenes first, then Italian last (cookie sticks)
const SCENES = [
  // --- ENGLISH SCENES (lang=en) ---
  // 1. Homepage hero
  ['01-hero.png', '/?lang=en', 0, 2000, 'Homepage hero section'],
  // 2. Homepage recently listed (scroll down)
  ['02-recently-listed.png', '/', 800, 1500, 'Recently listed items'],
  // 3. Homepage origin story (scroll more)
  ['03-origin-story.png', '/', 1800, 1500, 'Origin story + footer'],
  // 4. Browse page -- full grid
  ['04-browse-grid.png', '/browse', 0, 2000, 'Browse neighborhood items'],
  // 5. Browse -- search drill + tools filter
  ['05-browse-search.png', '/browse?q=drill&category=tools', 0, 2000, 'Search and filter'],
  // 6. Item detail -- Bosch Drill (hero)
  ['06-item-detail-top.png', '/items/bosch-professional-drill-driver-set', 0, 2000, 'Item detail page'],
  // 7. Item detail -- scroll to reviews
  ['07-item-detail-reviews.png', '/items/bosch-professional-drill-driver-set', 600, 1500, 'Reviews + social proof'],
  // 8. Workshop profile -- Sally's Kitchen
  ['08-workshop.png', '/workshop/sallys-kitchen', 0, 2000, 'Workshop storefront'],
  // 9. List an item -- AI form
  ['09-list-item.png', '/list', 0, 2000, 'AI-powered listing form'],
  // 10. Onboarding flow
  ['10-onboarding.png', '/onboarding', 0, 2000, 'Onboarding wizard'],
  // --- ITALIAN SCENES (switch lang, cookie will stick) ---
  // 11. Italian homepage
  ['11-italian-home.png', '/?lang=it', 0, 2000, 'Bilingual - Italian homepage'],
  // 12. Italian browse
  ['12-italian-browse.png', '/browse', 0, 2000, 'Bilingual - Italian browse'],
];

async function capture() {
  console.log(`\n  BorrowHood Demo Capture`);
  console.log(`  Target: ${BASE}`);
  console.log(`  Resolution: ${WIDTH}x${HEIGHT}`);
  console.log(`  Scenes: ${SCENES.length}\n`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--ignore-certificate-errors',
      `--window-size=${WIDTH},${HEIGHT}`,
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT });

  // Helper: wait N ms (puppeteer v22+ removed waitForTimeout)
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  // Suppress console noise from the app
  page.on('console', () => {});
  page.on('pageerror', () => {});

  for (const [filename, urlPath, scrollY, waitMs, desc] of SCENES) {
    const url = `${BASE}${urlPath}`;
    process.stdout.write(`  ${filename.padEnd(30)} ${desc}... `);

    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });

      // Wait for content to render (Alpine.js, images, etc.)
      await sleep(waitMs);

      // Scroll if needed
      if (scrollY > 0) {
        await page.evaluate((y) => {
          window.scrollTo({ top: y, behavior: 'instant' });
        }, scrollY);
        await sleep(500);
      }

      // Capture
      await page.screenshot({
        path: path.join(FRAMES, filename),
        fullPage: false, // viewport only (1920x1080)
      });

      console.log('OK');
    } catch (err) {
      console.log(`FAIL: ${err.message.slice(0, 60)}`);
    }
  }

  await browser.close();
  console.log(`\n  Done. ${SCENES.length} frames in ${FRAMES}/\n`);
}

capture().catch(console.error);
