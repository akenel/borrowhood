#!/usr/bin/env node
/**
 * Record BorrowHood demo GIF frames from live server.
 * Captures: home hero -> scroll -> browse page -> filter -> item detail
 */
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const BASE = 'https://46.62.138.218';
const OUT = path.join(__dirname, '..', 'docs', 'gif-frames');
const WIDTH = 1280;
const HEIGHT = 720;

let frame = 0;

async function snap(page, label, delay = 300) {
    await new Promise(r => setTimeout(r, delay));
    const file = path.join(OUT, `${String(frame).padStart(3, '0')}-${label}.png`);
    await page.screenshot({ path: file, type: 'png' });
    console.log(`  [${frame}] ${label}`);
    frame++;
}

(async () => {
    if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--ignore-certificate-errors', `--window-size=${WIDTH},${HEIGHT}`],
    });

    const page = await browser.newPage();
    await page.setViewport({ width: WIDTH, height: HEIGHT });

    console.log('Recording BorrowHood demo...');

    // Scene 1: Home page hero
    await page.goto(`${BASE}/`, { waitUntil: 'networkidle2', timeout: 15000 });
    await snap(page, 'home-hero', 500);
    await snap(page, 'home-hero-hold', 800);

    // Scene 2: Scroll down to see stats / recent items
    await page.evaluate(() => window.scrollBy(0, 600));
    await snap(page, 'home-scroll-1', 400);
    await snap(page, 'home-scroll-1-hold', 600);

    await page.evaluate(() => window.scrollBy(0, 500));
    await snap(page, 'home-scroll-2', 400);
    await snap(page, 'home-scroll-2-hold', 600);

    // Scene 3: Browse page
    await page.goto(`${BASE}/browse`, { waitUntil: 'networkidle2', timeout: 15000 });
    await snap(page, 'browse-grid', 500);
    await snap(page, 'browse-grid-hold', 800);

    // Scene 4: Scroll browse
    await page.evaluate(() => window.scrollBy(0, 400));
    await snap(page, 'browse-scroll', 400);
    await snap(page, 'browse-scroll-hold', 600);

    // Scene 5: Click first item to see detail
    const itemLink = await page.$('a[href*="/items/"]');
    if (itemLink) {
        await itemLink.click();
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
        await snap(page, 'item-detail-top', 500);
        await snap(page, 'item-detail-top-hold', 800);

        // Scroll to see reviews/details
        await page.evaluate(() => window.scrollBy(0, 500));
        await snap(page, 'item-detail-scroll', 400);
        await snap(page, 'item-detail-scroll-hold', 600);
    }

    // Scene 6: Members page
    await page.goto(`${BASE}/members`, { waitUntil: 'networkidle2', timeout: 15000 });
    await snap(page, 'members', 500);
    await snap(page, 'members-hold', 800);

    // Scene 7: Workshop profile (first user link)
    const workshopLink = await page.$('a[href*="/workshop/"]');
    if (workshopLink) {
        await workshopLink.click();
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
        await snap(page, 'workshop-profile', 500);
        await snap(page, 'workshop-profile-hold', 800);
    }

    // Scene 8: Italian version
    await page.goto(`${BASE}/?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
    await snap(page, 'home-italian', 500);
    await snap(page, 'home-italian-hold', 800);

    // Final hold on home
    await page.goto(`${BASE}/`, { waitUntil: 'networkidle2', timeout: 15000 });
    await snap(page, 'home-final', 500);
    await snap(page, 'home-final-hold', 1000);

    await browser.close();
    console.log(`\nDone: ${frame} frames in ${OUT}`);
})();
