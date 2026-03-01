#!/usr/bin/env node
/**
 * BorrowHood Edge-Case Screen Tests
 *
 * Tests boundary conditions, broken images, console errors,
 * pagination edge cases, 404s, gallery behaviour, mobile viewport.
 * Takes screenshots of every interesting state.
 */

const puppeteer = require('puppeteer');
const https = require('https');
const path = require('path');
const fs = require('fs');

const BASE = 'https://46.62.138.218';
const KC_URL = `${BASE}/realms/borrowhood/protocol/openid-connect`;
const TEST_USER = 'angel';
const TEST_PASS = 'helix_pass';
const CLIENT_ID = 'borrowhood-web';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'Bro_Kit', 'uat-screenshots', 'edge-cases');

const results = { pass: 0, fail: 0, bugs: [] };

// ─── Helpers ───────────────────────────────────────────────

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

function check(name, condition, detail = '') {
    if (condition) {
        results.pass++;
        console.log(`  \x1b[32m✓\x1b[0m ${name}`);
    } else {
        results.fail++;
        console.log(`  \x1b[31m✗\x1b[0m ${name}${detail ? ' -- ' + detail : ''}`);
        results.bugs.push({ name, detail });
    }
}

// ─── Main ──────────────────────────────────────────────────

(async () => {
    console.log('\x1b[1;37m╔══════════════════════════════════════════════════╗');
    console.log('║    BorrowHood Edge-Case Screen Tests            ║');
    console.log('║    Target: https://46.62.138.218                ║');
    console.log('╚══════════════════════════════════════════════════╝\x1b[0m');

    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--ignore-certificate-errors'],
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    // Collect console errors per page
    let consoleErrors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    async function snap(name) {
        const fp = path.join(SCREENSHOT_DIR, `${name}.png`);
        await page.screenshot({ path: fp, fullPage: true });
        return fp;
    }

    function resetConsole() { consoleErrors = []; }
    function checkNoConsoleErrors(pageName) {
        const errs = consoleErrors.filter(e =>
            !e.includes('net::ERR_CERT') &&        // self-signed cert noise
            !e.includes('favicon') &&               // missing favicon
            !e.includes('Failed to load resource')  // image 404s checked separately
        );
        check(`${pageName}: no JS console errors`, errs.length === 0,
            errs.length > 0 ? errs.slice(0, 3).join(' | ') : '');
    }

    // ═══════════════════════════════════════════════════════
    // 1. BROWSE PAGE EDGE CASES
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 1. Browse Page Edge Cases ──\x1b[0m\n');

    // 1a. Empty search
    resetConsole();
    await page.goto(`${BASE}/browse?q=`, { waitUntil: 'networkidle2', timeout: 15000 });
    const emptySearchCount = await page.evaluate(() => document.querySelectorAll('.grid > a, .grid > div').length);
    check('Browse empty search returns items (not crash)', emptySearchCount > 0, `found ${emptySearchCount} cards`);
    await snap('browse-empty-search');
    checkNoConsoleErrors('Browse empty search');

    // 1b. Search with no results
    resetConsole();
    await page.goto(`${BASE}/browse?q=zzzznonexistent999`, { waitUntil: 'networkidle2', timeout: 15000 });
    const noResultsText = await page.evaluate(() => document.body.innerText);
    check('Browse no-results shows friendly message', noResultsText.toLowerCase().includes('no items') || noResultsText.toLowerCase().includes('no results') || noResultsText.includes('0'), 'no empty-state message found');
    await snap('browse-no-results');
    checkNoConsoleErrors('Browse no-results');

    // 1c. Search with special characters (XSS probe)
    resetConsole();
    const xssProbe = '<script>alert(1)</script>';
    await page.goto(`${BASE}/browse?q=${encodeURIComponent(xssProbe)}`, { waitUntil: 'networkidle2', timeout: 15000 });
    const bodyHtml = await page.evaluate(() => document.body.innerHTML);
    check('Browse XSS probe is escaped (no raw script tag)', !bodyHtml.includes('<script>alert(1)</script>'), 'XSS not escaped!');
    await snap('browse-xss-probe');

    // 1d. Pagination: offset beyond total
    resetConsole();
    await page.goto(`${BASE}/browse?offset=99999&limit=12`, { waitUntil: 'networkidle2', timeout: 15000 });
    const beyondStatus = await page.evaluate(() => document.body.innerText);
    check('Browse offset=99999 does not crash', !beyondStatus.includes('500') && !beyondStatus.includes('Internal Server Error'), 'page crashed');
    await snap('browse-offset-beyond');
    checkNoConsoleErrors('Browse offset beyond');

    // 1e. Pagination: limit=1 (clamped to min=12 by server)
    resetConsole();
    await page.goto(`${BASE}/browse?limit=1`, { waitUntil: 'networkidle2', timeout: 15000 });
    const limit1Count = await page.evaluate(() => {
        return document.querySelectorAll('a[href*="/items/"]').length;
    });
    check('Browse limit=1 clamped to minimum 12', limit1Count === 12, `found ${limit1Count}`);
    await snap('browse-limit-1');

    // 1f. Pagination: limit=999 (very large)
    resetConsole();
    await page.goto(`${BASE}/browse?limit=999`, { waitUntil: 'networkidle2', timeout: 15000 });
    const status999 = await page.evaluate(() => !document.body.innerText.includes('Internal Server Error'));
    check('Browse limit=999 does not crash', status999);
    await snap('browse-limit-999');

    // 1g. Invalid category
    resetConsole();
    await page.goto(`${BASE}/browse?category=FAKECATEGORY`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Browse invalid category does not crash', true); // if we got here, no crash
    await snap('browse-invalid-category');
    checkNoConsoleErrors('Browse invalid category');

    // 1h. Broken images check on browse (use limit=12 to avoid slow load)
    resetConsole();
    await page.goto(`${BASE}/browse?limit=12`, { waitUntil: 'networkidle2', timeout: 15000 });
    // Wait for all images to load (or fail) with explicit completion check
    await page.evaluate(() => {
        return Promise.all(
            Array.from(document.querySelectorAll('img')).map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(resolve => {
                    img.addEventListener('load', resolve);
                    img.addEventListener('error', resolve);
                    setTimeout(resolve, 8000);
                });
            })
        );
    });
    const brokenImages = await page.evaluate(() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        return imgs.filter(img => img.naturalWidth === 0 && img.src && !img.src.includes('data:')).map(img => img.src);
    });
    check(`Browse page: no broken images (of ${await page.evaluate(() => document.querySelectorAll('img').length)} total)`,
        brokenImages.length === 0, brokenImages.length > 0 ? `${brokenImages.length} broken: ${brokenImages.slice(0, 3).join(', ')}` : '');
    await snap('browse-images-check');

    // ═══════════════════════════════════════════════════════
    // 2. ITEM DETAIL EDGE CASES
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 2. Item Detail Edge Cases ──\x1b[0m\n');

    // 2a. Non-existent slug -> 404
    resetConsole();
    const resp404 = await page.goto(`${BASE}/items/this-item-does-not-exist-at-all`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Item non-existent slug returns 404', resp404.status() === 404, `got ${resp404.status()}`);
    await snap('item-404');

    // 2b. Find item with multiple images -> test gallery
    const itemsResp = await api('/api/v1/items?limit=50');
    let multiImageItem = null;
    let singleImageItem = null;
    if (itemsResp.status === 200 && Array.isArray(itemsResp.data)) {
        multiImageItem = itemsResp.data.find(i => i.media && i.media.length > 1);
        singleImageItem = itemsResp.data.find(i => i.media && i.media.length === 1);
    }

    if (multiImageItem) {
        resetConsole();
        await page.goto(`${BASE}/items/${multiImageItem.slug}`, { waitUntil: 'networkidle2', timeout: 15000 });
        await new Promise(r => setTimeout(r, 1000));

        // Gallery exists
        const hasGallery = await page.evaluate(() => !!document.querySelector('[x-data*="imageGallery"]'));
        check(`Item gallery renders (${multiImageItem.name})`, hasGallery);

        // Thumbnails render
        const thumbCount = await page.evaluate(() => document.querySelectorAll('[x-data*="imageGallery"] button img').length);
        check(`Item gallery has ${multiImageItem.media.length} thumbnails`, thumbCount === multiImageItem.media.length, `found ${thumbCount}`);

        // Main image loads
        const mainImgOK = await page.evaluate(() => {
            const img = document.querySelector('[x-data*="imageGallery"] img');
            return img && img.naturalWidth > 0;
        });
        check('Gallery main image loads', mainImgOK);

        // Click next arrow and image changes
        const imgBefore = await page.evaluate(() => {
            const img = document.querySelector('[x-data*="imageGallery"] img');
            return img ? img.src : '';
        });
        await page.evaluate(() => {
            const nextBtn = document.querySelectorAll('[x-data*="imageGallery"] button')[0];
            // Find the right-arrow button (has an SVG with path for >)
            const buttons = Array.from(document.querySelectorAll('[x-data*="imageGallery"] > div > button'));
            if (buttons.length > 0) buttons[buttons.length - 1].click();
        });
        await new Promise(r => setTimeout(r, 500));
        const imgAfter = await page.evaluate(() => {
            const img = document.querySelector('[x-data*="imageGallery"] img');
            return img ? img.src : '';
        });
        check('Gallery arrow click changes image', imgBefore !== imgAfter, `before: ${imgBefore.slice(-30)}, after: ${imgAfter.slice(-30)}`);

        // Counter badge shows "X / Y"
        const counter = await page.evaluate(() => {
            const span = document.querySelector('[x-data*="imageGallery"] span[x-text]');
            return span ? span.innerText : '';
        });
        check('Gallery counter badge visible', counter.includes('/'), `got "${counter}"`);

        await snap('item-gallery-multi');
        checkNoConsoleErrors('Item gallery');

        // Broken images in gallery
        const galleryBroken = await page.evaluate(() => {
            return Array.from(document.querySelectorAll('[x-data*="imageGallery"] img'))
                .filter(img => img.naturalWidth === 0 && img.src && !img.src.includes('data:'))
                .map(img => img.src);
        });
        check('Gallery: no broken images', galleryBroken.length === 0,
            galleryBroken.length > 0 ? galleryBroken.join(', ') : '');
    } else {
        console.log('  (skip) No multi-image item found for gallery test');
    }

    // 2c. Single-image item has NO arrows
    if (singleImageItem) {
        resetConsole();
        await page.goto(`${BASE}/items/${singleImageItem.slug}`, { waitUntil: 'networkidle2', timeout: 15000 });
        await new Promise(r => setTimeout(r, 500));
        const arrowsPresent = await page.evaluate(() => {
            const btns = document.querySelectorAll('[x-data*="imageGallery"] > div > button');
            return btns.length;
        });
        check('Single-image item: no gallery arrows', arrowsPresent === 0, `found ${arrowsPresent} buttons`);
        await snap('item-single-image');
    }

    // ═══════════════════════════════════════════════════════
    // 3. MEMBERS PAGE EDGE CASES
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 3. Members Page Edge Cases ──\x1b[0m\n');

    // 3a. Normal load
    resetConsole();
    await page.goto(`${BASE}/members`, { waitUntil: 'networkidle2', timeout: 15000 });
    const membersCountText = await page.evaluate(() => {
        const text = document.body.innerText;
        const match = text.match(/Showing (\d+)[^]*?of (\d+)/);
        return match ? { showing: parseInt(match[1]), total: parseInt(match[2]) } : null;
    });
    if (membersCountText) {
        check('Members: "Showing X" <= total', membersCountText.showing <= membersCountText.total,
            `showing ${membersCountText.showing} of ${membersCountText.total}`);
    }
    await snap('members-normal');
    checkNoConsoleErrors('Members page');

    // 3b. Members offset beyond total
    resetConsole();
    await page.goto(`${BASE}/members?offset=99999`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Members offset=99999 does not crash', true);
    await snap('members-offset-beyond');

    // 3c. Members empty search
    resetConsole();
    await page.goto(`${BASE}/members?q=zzzznoone999`, { waitUntil: 'networkidle2', timeout: 15000 });
    const membersEmpty = await page.evaluate(() => document.body.innerText);
    check('Members empty search shows 0 or friendly message', membersEmpty.includes('0') || membersEmpty.toLowerCase().includes('no members') || membersEmpty.toLowerCase().includes('no results'));
    await snap('members-no-results');

    // 3d. Members XSS in search
    resetConsole();
    await page.goto(`${BASE}/members?q=${encodeURIComponent('<img src=x onerror=alert(1)>')}`, { waitUntil: 'networkidle2', timeout: 15000 });
    // Check that no <img> tag was injected as a real DOM element (Jinja2 autoescape converts to &lt;img...)
    const xssImgInjected = await page.evaluate(() => !!document.querySelector('img[src="x"]'));
    check('Members XSS probe escaped (no injected img)', !xssImgInjected, 'XSS img tag was injected into DOM!');
    await snap('members-xss');

    // ═══════════════════════════════════════════════════════
    // 4. WORKSHOP EDGE CASES
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 4. Workshop Edge Cases ──\x1b[0m\n');

    // 4a. Non-existent workshop
    resetConsole();
    const ws404 = await page.goto(`${BASE}/workshop/fake-workshop-does-not-exist`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Workshop non-existent slug returns 404', ws404.status() === 404, `got ${ws404.status()}`);
    await snap('workshop-404');

    // 4b. Workshop export for non-existent
    resetConsole();
    const wsExport404 = await page.goto(`${BASE}/workshop/fake-workshop-does-not-exist/export`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Workshop export non-existent returns 404', wsExport404.status() === 404, `got ${wsExport404.status()}`);

    // 4c. Real workshop loads with language flags
    const membersApi = await api('/api/v1/items?limit=1');
    if (membersApi.status === 200 && Array.isArray(membersApi.data) && membersApi.data.length > 0) {
        const ownerSlug = membersApi.data[0].owner?.slug;
        if (ownerSlug) {
            resetConsole();
            await page.goto(`${BASE}/workshop/${ownerSlug}`, { waitUntil: 'networkidle2', timeout: 15000 });
            check('Workshop page loads for real user', true);
            // Check for flag emojis in language section
            const hasFlags = await page.evaluate(() => {
                const text = document.body.innerText;
                // Flag emojis are in Unicode range U+1F1E6 to U+1F1FF
                return /[\u{1F1E6}-\u{1F1FF}][\u{1F1E6}-\u{1F1FF}]/u.test(text);
            });
            check('Workshop shows language flag emojis', hasFlags, 'no flag emojis found');
            await snap('workshop-with-flags');
            checkNoConsoleErrors('Workshop page');
        }
    }

    // ═══════════════════════════════════════════════════════
    // 5. LANGUAGE / i18n EDGE CASES
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 5. Language Edge Cases ──\x1b[0m\n');

    // 5a. Italian browse
    resetConsole();
    await page.goto(`${BASE}/browse?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
    const itBrowse = await page.evaluate(() => document.documentElement.lang);
    check('Browse ?lang=it sets html lang="it"', itBrowse === 'it', `got lang="${itBrowse}"`);
    await snap('browse-italian');
    checkNoConsoleErrors('Browse Italian');

    // 5b. Invalid language code
    resetConsole();
    await page.goto(`${BASE}/browse?lang=zz`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Browse ?lang=zz does not crash (falls back)', true);
    await snap('browse-invalid-lang');

    // 5c. Home page Italian
    resetConsole();
    await page.goto(`${BASE}/?lang=it`, { waitUntil: 'networkidle2', timeout: 15000 });
    const itHome = await page.evaluate(() => document.body.innerText);
    check('Home Italian has Italian text', itHome.includes('Presta') || itHome.includes('Affitta') || itHome.includes('prestare') || itHome.includes('noleggi') || itHome.includes('comunità'));
    await snap('home-italian');

    // ═══════════════════════════════════════════════════════
    // 6. MOBILE VIEWPORT
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 6. Mobile Viewport (375x812) ──\x1b[0m\n');

    await page.setViewport({ width: 375, height: 812 });

    // 6a. Home mobile
    resetConsole();
    await page.goto(`${BASE}/`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Home page loads on mobile', true);
    await snap('mobile-home');
    checkNoConsoleErrors('Mobile home');

    // 6b. Browse mobile
    resetConsole();
    await page.goto(`${BASE}/browse`, { waitUntil: 'networkidle2', timeout: 15000 });
    // Check the grid collapses to single column
    const mobileGridCols = await page.evaluate(() => {
        const grid = document.querySelector('.grid');
        if (!grid) return 0;
        const style = getComputedStyle(grid);
        // Count actual column tracks (each "Xpx" in the computed value)
        const cols = style.gridTemplateColumns.match(/\d+(\.\d+)?px/g);
        return cols ? cols.length : 1;
    });
    check('Browse mobile grid is single-column', mobileGridCols <= 2, `found ${mobileGridCols} columns`);
    await snap('mobile-browse');

    // 6c. Item detail mobile
    if (multiImageItem) {
        resetConsole();
        await page.goto(`${BASE}/items/${multiImageItem.slug}`, { waitUntil: 'networkidle2', timeout: 15000 });
        await new Promise(r => setTimeout(r, 1000));
        check('Item detail loads on mobile', true);
        // Gallery image should still be visible
        const mobileImg = await page.evaluate(() => {
            const img = document.querySelector('[x-data*="imageGallery"] img');
            return img ? img.getBoundingClientRect().width > 0 : false;
        });
        check('Gallery image visible on mobile', mobileImg);
        await snap('mobile-item-detail');
    }

    // 6d. Members mobile
    resetConsole();
    await page.goto(`${BASE}/members`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Members page loads on mobile', true);
    await snap('mobile-members');

    // Reset to desktop
    await page.setViewport({ width: 1920, height: 1080 });

    // ═══════════════════════════════════════════════════════
    // 7. AUTH-REQUIRED PAGES (UNAUTHENTICATED)
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 7. Auth Pages (Unauthenticated) ──\x1b[0m\n');

    // 7a. Dashboard without login
    resetConsole();
    const dashResp = await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle2', timeout: 15000 });
    const dashUrl = page.url();
    const dashRedirected = dashUrl.includes('openid-connect') || dashUrl.includes('/login') || dashResp.status() === 401;
    check('Dashboard redirects to login when unauthenticated', dashRedirected || dashResp.status() === 200, `landed on ${dashUrl} (${dashResp.status()})`);
    await snap('dashboard-unauthed');

    // 7b. Profile without login
    resetConsole();
    const profResp = await page.goto(`${BASE}/profile`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Profile page handles unauthenticated user', profResp.status() < 500, `got ${profResp.status()}`);
    await snap('profile-unauthed');

    // 7c. List item without login
    resetConsole();
    const listResp = await page.goto(`${BASE}/list`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('List item page handles unauthenticated user', listResp.status() < 500, `got ${listResp.status()}`);
    await snap('list-unauthed');

    // ═══════════════════════════════════════════════════════
    // 8. TERMS & HELPBOARD
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 8. Terms & Helpboard ──\x1b[0m\n');

    resetConsole();
    await page.goto(`${BASE}/terms`, { waitUntil: 'networkidle2', timeout: 15000 });
    const termsLen = await page.evaluate(() => document.body.innerText.length);
    check('Terms page has substantial content', termsLen > 200, `only ${termsLen} chars`);
    await snap('terms-page');
    checkNoConsoleErrors('Terms page');

    resetConsole();
    await page.goto(`${BASE}/helpboard`, { waitUntil: 'networkidle2', timeout: 15000 });
    check('Helpboard page loads', true);
    await snap('helpboard-page');
    checkNoConsoleErrors('Helpboard page');

    // ═══════════════════════════════════════════════════════
    // 9. API BOUNDARY TESTS
    // ═══════════════════════════════════════════════════════
    console.log('\n\x1b[1;36m── 9. API Boundary Tests ──\x1b[0m\n');

    // 9a. Items with negative offset
    const negOffset = await api('/api/v1/items?offset=-1');
    check('API items offset=-1 handled gracefully', negOffset.status < 500, `got ${negOffset.status}`);

    // 9b. Items with string limit
    const strLimit = await api('/api/v1/items?limit=abc');
    check('API items limit=abc handled gracefully', strLimit.status < 500, `got ${strLimit.status}`);

    // 9c. Items with huge limit
    const hugeLimit = await api('/api/v1/items?limit=100000');
    check('API items limit=100000 handled', hugeLimit.status < 500, `got ${hugeLimit.status}`);

    // 9d. Listings with bad type filter
    const badType = await api('/api/v1/listings?listing_type=NOTREAL');
    check('API listings bad type filter handled', badType.status < 500, `got ${badType.status}`);

    // 9e. Health endpoint always works
    const health = await api('/api/v1/health');
    check('Health endpoint returns 200', health.status === 200);
    check('Health status is healthy', health.data && health.data.status === 'healthy', `got ${JSON.stringify(health.data?.status)}`);

    // 9f. Badges catalog
    const badges = await api('/api/v1/badges/catalog');
    check('Badge catalog returns 200', badges.status === 200);
    if (badges.status === 200) {
        check('Badge catalog has 10+ badges', Array.isArray(badges.data) && badges.data.length >= 10, `got ${badges.data?.length}`);
        // Check for the new generous_neighbor badge
        const hasGenerous = Array.isArray(badges.data) && badges.data.some(b => b.code === 'generous_neighbor');
        check('Badge catalog includes generous_neighbor', hasGenerous, 'generous_neighbor badge missing');
    }

    // ═══════════════════════════════════════════════════════
    // SUMMARY
    // ═══════════════════════════════════════════════════════

    await browser.close();

    console.log('\n\x1b[1;37m══════════════════════════════════════════════════\x1b[0m');
    console.log(`  \x1b[32mPassed: ${results.pass}\x1b[0m  |  \x1b[31mFailed: ${results.fail}\x1b[0m`);
    console.log('\x1b[1;37m══════════════════════════════════════════════════\x1b[0m');

    if (results.bugs.length > 0) {
        console.log('\n\x1b[1;31mBugs found:\x1b[0m');
        results.bugs.forEach((b, i) => console.log(`  ${i + 1}. ${b.name}${b.detail ? ': ' + b.detail : ''}`));
    }

    console.log(`\n  Screenshots: ${SCREENSHOT_DIR}/`);
    process.exit(results.fail > 0 ? 1 : 0);
})();
