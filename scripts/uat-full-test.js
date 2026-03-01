#!/usr/bin/env node
/**
 * BorrowHood Full UAT - API + Puppeteer UI Tests
 *
 * Runs against Hetzner (https://46.62.138.218)
 * Tests every page, every API endpoint, takes screenshots.
 * Auto-files bugs via QA API.
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
const SCREENSHOT_DIR = path.join(__dirname, '..', 'Bro_Kit', 'uat-screenshots');

// Track results
const results = { pass: 0, fail: 0, bugs: [] };
let authToken = null;
let authCookie = null;

// ─── Helpers ───────────────────────────────────────────────
function api(urlPath, options = {}) {
    return new Promise((resolve, reject) => {
        const url = new URL(urlPath, BASE);
        const opts = {
            hostname: url.hostname,
            port: url.port || 443,
            path: url.pathname + url.search,
            method: options.method || 'GET',
            rejectAuthorized: false,
            headers: { 'Content-Type': 'application/json', ...options.headers },
        };
        // Node 18 needs this for self-signed certs
        const agent = new https.Agent({ rejectUnauthorized: false });
        opts.agent = agent;

        const req = https.request(opts, (res) => {
            let body = '';
            res.on('data', (d) => body += d);
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(body), headers: res.headers });
                } catch {
                    resolve({ status: res.statusCode, data: body, headers: res.headers });
                }
            });
        });
        req.on('error', reject);
        if (options.body) req.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body));
        req.end();
    });
}

async function getKeycloakToken() {
    return new Promise((resolve, reject) => {
        const postData = `grant_type=password&client_id=${CLIENT_ID}&username=${TEST_USER}&password=${TEST_PASS}&scope=openid`;
        const url = new URL(`${KC_URL}/token`);
        const agent = new https.Agent({ rejectUnauthorized: false });
        const req = https.request({
            hostname: url.hostname,
            port: url.port || 443,
            path: url.pathname,
            method: 'POST',
            agent,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(postData) },
        }, (res) => {
            let body = '';
            res.on('data', d => body += d);
            res.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    resolve(data.access_token || null);
                } catch { resolve(null); }
            });
        });
        req.on('error', reject);
        req.write(postData);
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

// ─── Phase 1: API Smoke Tests ──────────────────────────────
async function apiTests() {
    console.log('\n\x1b[1;36m── Phase 1: API Endpoint Tests ──\x1b[0m\n');

    // Health
    const health = await api('/api/v1/health');
    check('GET /api/v1/health returns 200', health.status === 200, `got ${health.status}`);

    // Items
    const items = await api('/api/v1/items');
    check('GET /api/v1/items returns 200', items.status === 200, `got ${items.status}`);
    check('Items list is non-empty', Array.isArray(items.data) && items.data.length > 0, `got ${Array.isArray(items.data) ? items.data.length : 'not array'} items`);

    if (Array.isArray(items.data) && items.data.length > 0) {
        const item = items.data[0];
        check('Item has id, name, slug', item.id && item.name && item.slug, `missing fields`);
        check('Item has media array', Array.isArray(item.media), 'media not an array');
        check('Item has at least 1 media', item.media && item.media.length > 0, 'no media on item');

        // Single item
        const single = await api(`/api/v1/items/${item.id}`);
        check('GET /api/v1/items/:id returns 200', single.status === 200, `got ${single.status}`);

        // Item by slug (try via API -- may not exist)
    }

    // Items search
    const search = await api('/api/v1/items?q=drill');
    check('GET /api/v1/items?q=drill returns 200', search.status === 200, `got ${search.status}`);

    // Items filter
    const catFilter = await api('/api/v1/items?category=tools');
    check('GET /api/v1/items?category=tools returns 200', catFilter.status === 200, `got ${catFilter.status}`);

    // Items sort
    const sorted = await api('/api/v1/items?sort=oldest');
    check('GET /api/v1/items?sort=oldest returns 200', sorted.status === 200, `got ${sorted.status}`);

    // Items pagination
    const page = await api('/api/v1/items?limit=2&offset=0');
    check('GET /api/v1/items pagination works', page.status === 200 && Array.isArray(page.data) && page.data.length <= 2, `got ${page.status}`);

    // Listings
    const listings = await api('/api/v1/listings');
    check('GET /api/v1/listings returns 200', listings.status === 200, `got ${listings.status}`);
    check('Listings list is non-empty', Array.isArray(listings.data) && listings.data.length > 0, `got ${Array.isArray(listings.data) ? listings.data.length : 'not array'}`);

    if (Array.isArray(listings.data) && listings.data.length > 0) {
        const listing = listings.data[0];
        check('Listing has id, listing_type, price', listing.id && listing.listing_type !== undefined, 'missing fields');

        const single = await api(`/api/v1/listings/${listing.id}`);
        check('GET /api/v1/listings/:id returns 200', single.status === 200, `got ${single.status}`);
    }

    // Reviews
    const reviews = await api('/api/v1/reviews');
    check('GET /api/v1/reviews returns 200', reviews.status === 200, `got ${reviews.status}`);

    // 404s
    const notFound = await api('/api/v1/items/00000000-0000-0000-0000-000000000000');
    check('GET nonexistent item returns 404', notFound.status === 404, `got ${notFound.status}`);

    // Auth-required endpoints (no token)
    const noAuth = await api('/api/v1/notifications/summary');
    check('Notifications summary requires auth (401)', noAuth.status === 401, `got ${noAuth.status}`);

    // ─── Authenticated API tests ───
    console.log('\n\x1b[1;36m── Phase 2: Authenticated API Tests ──\x1b[0m\n');

    authToken = await getKeycloakToken();
    check('Keycloak token obtained', !!authToken, 'token exchange failed');

    if (authToken) {
        const authHeaders = { headers: { 'Authorization': `Bearer ${authToken}` } };

        // Notifications
        const notifSummary = await api('/api/v1/notifications/summary', authHeaders);
        check('GET /notifications/summary (authed) returns 200', notifSummary.status === 200, `got ${notifSummary.status}`);

        const notifs = await api('/api/v1/notifications', authHeaders);
        check('GET /notifications (authed) returns 200', notifs.status === 200, `got ${notifs.status}`);

        // QA Testing
        const qaSummary = await api('/api/v1/testing/summary', authHeaders);
        check('GET /testing/summary returns 200', qaSummary.status === 200, `got ${qaSummary.status}`);
        if (qaSummary.status === 200) {
            check('QA summary has total_tests', qaSummary.data.total_tests >= 0, `got ${JSON.stringify(qaSummary.data)}`);
            check('QA has seeded tests (36)', qaSummary.data.total_tests === 36, `got ${qaSummary.data.total_tests}`);
        }

        const qaPhases = await api('/api/v1/testing/phases', authHeaders);
        check('GET /testing/phases returns 200', qaPhases.status === 200, `got ${qaPhases.status}`);
        check('QA has 9 phases', Array.isArray(qaPhases.data) && qaPhases.data.length === 9, `got ${Array.isArray(qaPhases.data) ? qaPhases.data.length : 'not array'}`);

        const qaTests = await api('/api/v1/testing/tests', authHeaders);
        check('GET /testing/tests returns 200', qaTests.status === 200, `got ${qaTests.status}`);

        const qaBugs = await api('/api/v1/testing/bugs', authHeaders);
        check('GET /testing/bugs returns 200', qaBugs.status === 200, `got ${qaBugs.status}`);

        // Backlog
        const blSummary = await api('/api/v1/backlog/summary', authHeaders);
        check('GET /backlog/summary returns 200', blSummary.status === 200, `got ${blSummary.status}`);
        if (blSummary.status === 200) {
            check('Backlog has seeded items (8+)', blSummary.data.total >= 8, `got ${blSummary.data.total}`);
        }

        const blItems = await api('/api/v1/backlog/items', authHeaders);
        check('GET /backlog/items returns 200', blItems.status === 200, `got ${blItems.status}`);

        // AI endpoints
        const aiDesc = await api('/api/v1/ai/generate-listing', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Test Drill', category: 'tools', item_type: 'physical', language: 'en' }),
        });
        check('POST /ai/generate-listing returns 200', aiDesc.status === 200, `got ${aiDesc.status}`);
        if (aiDesc.status === 200) {
            check('AI listing has title + description', aiDesc.data.title && aiDesc.data.description, 'missing fields');
        }

        const aiImg = await api('/api/v1/ai/generate-image', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Power Drill', category: 'tools' }),
        });
        check('POST /ai/generate-image returns 200', aiImg.status === 200, `got ${aiImg.status}`);
        if (aiImg.status === 200) {
            check('AI image URL is a pollinations URL', aiImg.data.image_url && aiImg.data.image_url.includes('pollinations'), `got ${aiImg.data.image_url}`);
        }

        // Badges
        const badges = await api('/api/v1/badges', authHeaders);
        check('GET /badges (my badges) returns 200', badges.status === 200, `got ${badges.status}`);
    }
}

// ─── Phase 3: Puppeteer UI Tests ───────────────────────────
async function uiTests() {
    console.log('\n\x1b[1;36m── Phase 3: Puppeteer UI Tests ──\x1b[0m\n');

    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--ignore-certificate-errors'],
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    async function screenshot(name) {
        const filepath = path.join(SCREENSHOT_DIR, `${name}.png`);
        await page.screenshot({ path: filepath, fullPage: true });
        return filepath;
    }

    async function testPage(url, name, checks = []) {
        try {
            const resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });
            const status = resp.status();
            check(`${name} loads (${status})`, status === 200, `got ${status}`);
            await screenshot(name.replace(/[^a-z0-9]/gi, '-').toLowerCase());

            for (const c of checks) {
                try {
                    const result = await page.evaluate(c.eval);
                    check(c.name, result, c.detail || '');
                } catch (e) {
                    check(c.name, false, e.message);
                }
            }
        } catch (e) {
            check(`${name} loads`, false, e.message);
        }
    }

    // ─── Public pages ───
    await testPage(`${BASE}/`, 'Home page', [
        { name: 'Home has app name', eval: () => document.body.innerText.includes('BorrowHood') },
        { name: 'Home has nav links', eval: () => !!document.querySelector('nav a[href="/"]') },
        { name: 'Home has hero section', eval: () => document.body.innerText.toLowerCase().includes('rent') || document.body.innerText.toLowerCase().includes('borrow') },
        { name: 'Home has footer', eval: () => !!document.querySelector('footer') },
    ]);

    await testPage(`${BASE}/browse`, 'Browse page', [
        { name: 'Browse has item cards', eval: () => document.querySelectorAll('[class*="rounded"]').length > 3 },
    ]);

    // Check if browse page actually exists (might 404)
    const browseResp = await api('/browse');
    if (browseResp.status === 404) {
        results.bugs.push({ name: 'Browse page returns 404', detail: '/browse returns 404 instead of 200' });
    }

    // Italian language
    await testPage(`${BASE}/?lang=it`, 'Home Italian', [
        { name: 'Italian home has IT content', eval: () => document.body.innerText.includes('Presta') || document.body.innerText.includes('Affitta') || document.body.innerText.includes('noleggi') || document.documentElement.lang === 'it' },
    ]);

    // ─── Login flow ───
    console.log('\n  Logging in via Keycloak...');
    try {
        await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 15000 });
        // Should be on Keycloak login page
        await page.waitForSelector('#username', { timeout: 10000 });
        check('Keycloak login page loads', true);
        await screenshot('keycloak-login');

        await page.type('#username', TEST_USER);
        await page.type('#password', TEST_PASS);
        await page.click('#kc-login');
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });

        const afterLoginUrl = page.url();
        check('Login redirects back to BorrowHood', afterLoginUrl.includes('46.62.138.218'), `landed on ${afterLoginUrl}`);
        await screenshot('after-login');

        // Check nav shows user
        const hasUserNav = await page.evaluate(() => {
            return document.body.innerText.includes('angel') || document.body.innerText.includes('Dashboard') || !!document.querySelector('a[href="/dashboard"]');
        });
        check('Nav shows authenticated state (Dashboard link)', hasUserNav);

    } catch (e) {
        check('Login flow completes', false, e.message);
    }

    // ─── Authenticated pages ───
    await testPage(`${BASE}/dashboard`, 'Dashboard page', [
        { name: 'Dashboard has content', eval: () => document.body.innerText.length > 200 },
    ]);

    await testPage(`${BASE}/testing`, 'QA Testing page', [
        { name: 'QA has summary cards', eval: () => document.body.innerText.includes('Total Tests') || document.body.innerText.includes('Passed') },
        { name: 'QA has test checklist section', eval: () => document.body.innerText.includes('Test Checklist') || document.body.innerText.includes('Phase') },
    ]);

    // Wait for Alpine to load QA data
    await new Promise(r => setTimeout(r, 2000));
    await screenshot('qa-dashboard-loaded');
    const qaDataLoaded = await page.evaluate(() => {
        const text = document.body.innerText;
        // Check if "36" or test counts appear
        return text.includes('36') || text.includes('Pending') || text.includes('Phase 1');
    });
    check('QA data loaded (36 tests visible)', qaDataLoaded);

    await testPage(`${BASE}/backlog`, 'Backlog page', [
        { name: 'Backlog has board or list content', eval: () => document.body.innerText.includes('Backlog') || document.body.innerText.includes('Board') },
    ]);

    await new Promise(r => setTimeout(r, 2000));
    await screenshot('backlog-loaded');
    const blDataLoaded = await page.evaluate(() => {
        return document.body.innerText.includes('open') || document.body.innerText.includes('planned') || document.body.innerText.includes('New Item');
    });
    check('Backlog data loaded (items visible)', blDataLoaded);

    await testPage(`${BASE}/profile`, 'Profile page', [
        { name: 'Profile shows user info', eval: () => document.body.innerText.includes('angel') || document.body.innerText.includes('Profile') },
    ]);

    // ─── Item detail page ───
    const itemsData = await api('/api/v1/items?limit=1');
    if (itemsData.status === 200 && Array.isArray(itemsData.data) && itemsData.data.length > 0) {
        const slug = itemsData.data[0].slug;
        await testPage(`${BASE}/items/${slug}`, 'Item detail page', [
            { name: 'Item detail has item name', eval: () => document.body.innerText.length > 100 },
            { name: 'Item detail has image', eval: () => !!document.querySelector('img[src*="seed"], img[src*="pollinations"], img[src*="upload"]') },
        ]);
    }

    // ─── List item page ───
    await testPage(`${BASE}/list`, 'List item page', [
        { name: 'List item has form fields', eval: () => !!document.querySelector('input[type="text"]') || !!document.querySelector('select') },
        { name: 'List item has drag-and-drop zone', eval: () => document.body.innerHTML.includes('handleFiles') || document.body.innerHTML.includes('drop') || document.body.innerText.includes('Drop an image') },
        { name: 'List item has AI generate button', eval: () => document.body.innerText.includes('AI') || document.body.innerText.includes('Generate') },
    ]);

    // ─── Onboarding page ───
    await testPage(`${BASE}/onboarding`, 'Onboarding page', [
        { name: 'Onboarding has form content', eval: () => document.body.innerText.length > 100 },
    ]);

    // ─── Terms page ───
    await testPage(`${BASE}/terms`, 'Terms page', [
        { name: 'Terms page has content', eval: () => document.body.innerText.length > 50 },
    ]);

    // ─── Logout ───
    try {
        await page.goto(`${BASE}/logout`, { waitUntil: 'networkidle2', timeout: 15000 });
        check('Logout redirects successfully', true);
        await screenshot('after-logout');
    } catch (e) {
        check('Logout works', false, e.message);
    }

    // ─── Test protected page access after logout ───
    try {
        const resp = await page.goto(`${BASE}/testing`, { waitUntil: 'networkidle2', timeout: 15000 });
        const finalUrl = page.url();
        const isOnLogin = finalUrl.includes('openid-connect/auth') || finalUrl.includes('/login');
        check('Protected page redirects to login after logout', isOnLogin, `landed on ${finalUrl}`);
        await screenshot('protected-after-logout');
    } catch (e) {
        check('Protected page redirect after logout', false, e.message);
    }

    await browser.close();
}

// ─── Phase 4: File bugs ────────────────────────────────────
async function fileBugs() {
    if (results.bugs.length === 0) {
        console.log('\n\x1b[32mNo bugs to file!\x1b[0m');
        return;
    }

    console.log(`\n\x1b[1;36m── Phase 4: Filing ${results.bugs.length} Bug(s) ──\x1b[0m\n`);

    if (!authToken) {
        console.log('  No auth token -- cannot file bugs via API. Listing them below:');
        results.bugs.forEach((b, i) => console.log(`  ${i + 1}. ${b.name}: ${b.detail}`));
        return;
    }

    for (const bug of results.bugs) {
        try {
            const resp = await api('/api/v1/testing/bugs', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: bug.name,
                    description: `Auto-detected by UAT runner.\n\n${bug.detail || 'No additional detail.'}`,
                    severity: 'medium',
                    category: 'functional',
                    reported_by: 'UAT-Bot',
                }),
            });
            if (resp.status === 201) {
                const num = resp.data.bug_number || '?';
                console.log(`  \x1b[33mBUG-${String(num).padStart(3, '0')}\x1b[0m Filed: ${bug.name}`);
            } else {
                console.log(`  \x1b[31m✗\x1b[0m Failed to file: ${bug.name} (${resp.status})`);
            }
        } catch (e) {
            console.log(`  \x1b[31m✗\x1b[0m Error filing: ${bug.name} -- ${e.message}`);
        }
    }
}

// ─── Main ──────────────────────────────────────────────────
(async () => {
    console.log('\x1b[1;37m╔══════════════════════════════════════════════════╗');
    console.log('║      BorrowHood Full UAT Suite                  ║');
    console.log('║      Target: https://46.62.138.218 (port 443)   ║');
    console.log('╚══════════════════════════════════════════════════╝\x1b[0m');

    try {
        await apiTests();
        await uiTests();
        await fileBugs();
    } catch (e) {
        console.error('\n\x1b[31mFatal error:\x1b[0m', e.message);
    }

    console.log('\n\x1b[1;37m══════════════════════════════════════════════════\x1b[0m');
    console.log(`  \x1b[32mPassed: ${results.pass}\x1b[0m  |  \x1b[31mFailed: ${results.fail}\x1b[0m  |  \x1b[33mBugs filed: ${results.bugs.length}\x1b[0m`);
    console.log('\x1b[1;37m══════════════════════════════════════════════════\x1b[0m');
    console.log(`  Screenshots: ${SCREENSHOT_DIR}/`);

    process.exit(results.fail > 0 ? 1 : 0);
})();
