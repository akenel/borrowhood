#!/usr/bin/env node
/**
 * Take fresh screenshots for README / dev.to post.
 * Captures: home, browse, item-detail (with gallery), workshop (with flags),
 * dashboard (authenticated), members, profile.
 */

const puppeteer = require('puppeteer');
const https = require('https');
const path = require('path');
const fs = require('fs');

const BASE = 'https://46.62.138.218';
const KC_URL = `${BASE}/realms/borrowhood/protocol/openid-connect`;
const SCREENSHOT_DIR = path.join(__dirname, '..', 'docs', 'screenshots');

function api(urlPath) {
    return new Promise((resolve, reject) => {
        const url = new URL(urlPath, BASE);
        const agent = new https.Agent({ rejectUnauthorized: false });
        const req = https.request({
            hostname: url.hostname, port: url.port || 443,
            path: url.pathname + url.search, method: 'GET', agent,
            headers: { 'Content-Type': 'application/json' },
        }, (res) => {
            let body = '';
            res.on('data', d => body += d);
            res.on('end', () => {
                try { resolve({ status: res.statusCode, data: JSON.parse(body) }); }
                catch { resolve({ status: res.statusCode, data: body }); }
            });
        });
        req.on('error', reject);
        req.end();
    });
}

(async () => {
    console.log('Taking fresh screenshots...\n');
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--ignore-certificate-errors'],
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });

    async function snap(name, fullPage = false) {
        const fp = path.join(SCREENSHOT_DIR, `${name}.png`);
        await page.screenshot({ path: fp, fullPage });
        const size = fs.statSync(fp).size;
        console.log(`  ${name}.png (${(size / 1024).toFixed(0)} KB)`);
        return fp;
    }

    // ── 1. Home page ──
    await page.goto(`${BASE}/`, { waitUntil: 'networkidle2', timeout: 20000 });
    await snap('home');

    // ── 2. Browse page (with items loaded) ──
    await page.goto(`${BASE}/browse`, { waitUntil: 'networkidle2', timeout: 20000 });
    // Wait for images to load
    await page.evaluate(() => Promise.all(
        Array.from(document.querySelectorAll('img')).map(img => {
            if (img.complete) return Promise.resolve();
            return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
        })
    ));
    await snap('browse');

    // ── 3. Item detail (find one with multiple images for gallery) ──
    const itemsResp = await api('/api/v1/items?limit=50');
    let detailSlug = null;
    if (itemsResp.status === 200 && Array.isArray(itemsResp.data)) {
        const multi = itemsResp.data.find(i => i.media && i.media.length > 1);
        detailSlug = multi ? multi.slug : itemsResp.data[0]?.slug;
    }
    if (detailSlug) {
        await page.goto(`${BASE}/items/${detailSlug}`, { waitUntil: 'networkidle2', timeout: 20000 });
        await new Promise(r => setTimeout(r, 1500)); // let gallery + Alpine init
        await page.evaluate(() => Promise.all(
            Array.from(document.querySelectorAll('img')).map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(r => { img.onload = r; img.onerror = r; setTimeout(r, 5000); });
            })
        ));
        await snap('item-detail');
    }

    // ── 4. Workshop profile (find one with languages for flag display) ──
    if (itemsResp.status === 200 && Array.isArray(itemsResp.data)) {
        const ownerSlug = itemsResp.data[0]?.owner?.slug;
        if (ownerSlug) {
            await page.goto(`${BASE}/workshop/${ownerSlug}`, { waitUntil: 'networkidle2', timeout: 20000 });
            await new Promise(r => setTimeout(r, 1000));
            await snap('workshop');
        }
    }

    // ── 5. Members page ──
    await page.goto(`${BASE}/members`, { waitUntil: 'networkidle2', timeout: 20000 });
    await new Promise(r => setTimeout(r, 1000));
    await snap('members');

    // ── 6. Login and take authenticated screenshots ──
    console.log('\n  Logging in as angel...');
    try {
        await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 20000 });
        await page.waitForSelector('#username', { timeout: 10000 });
        await page.type('#username', 'angel');
        await page.type('#password', 'helix_pass');
        await page.click('#kc-login');
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
        console.log('  Logged in.\n');

        // ── 7. Dashboard ──
        await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 20000 });
        await new Promise(r => setTimeout(r, 2000)); // let Alpine load rentals
        await snap('dashboard');

        // ── 8. Profile ──
        await page.goto(`${BASE}/profile`, { waitUntil: 'networkidle2', timeout: 20000 });
        await new Promise(r => setTimeout(r, 1500));
        await snap('profile');

    } catch (e) {
        console.log(`  Login failed: ${e.message}`);
    }

    await browser.close();
    console.log(`\nDone. Screenshots in: ${SCREENSHOT_DIR}/`);
})();
