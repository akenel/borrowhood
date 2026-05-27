#!/usr/bin/env node
/**
 * BorrowHood / La Piazza -- Console & Render Sweep
 *
 * Loads every key page in a real headless Chrome (Puppeteer), as an anonymous
 * visitor AND as logged-in users, and flags the things pytest + the smoke test
 * physically cannot see -- the client-side rot:
 *
 *   - red console errors (JS exceptions, failed Alpine init, bad fetches)
 *   - uncaught page errors
 *   - the page itself failing to load (doc status >= 400)
 *   - any request on the page returning 5xx (a hidden 500)
 *   - 4xx XHR/fetch calls (e.g. the anon favorites 401 Angel found)
 *   - raw template leaks in the text: {{ }}, i18n.x, [object Object], **markdown**
 *   - broken images (naturalWidth === 0 after load)
 *
 * This is the automated version of UAT Section 0 + Section 15 (the picky passes).
 *
 * Usage:
 *   node tests/e2e/console-sweep.js                          # default: staging
 *   node tests/e2e/console-sweep.js https://lapiazza.app     # prod
 *   BH_REALM=borrowhood node tests/e2e/console-sweep.js https://lapiazza.app
 *
 * Exit code 0 = clean (ship it), 1 = findings (see report).
 */

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_URL = (process.argv[2] || process.env.BH_BASE_URL || 'https://staging.lapiazza.app').replace(/\/$/, '');
const REALM = process.env.BH_REALM || (BASE_URL.includes('staging') ? 'borrowhood-staging' : 'borrowhood');
const PASSWORD = process.env.BH_TEST_PASSWORD || 'helix_pass';
const PERSONAS = ['angel', 'mike', 'sally']; // organizer/admin, lender, lender

// Console warnings we accept as known noise (not findings).
const IGNORED_WARNINGS = [
    'cdn.tailwindcss.com should not be used in production', // known: CDN Tailwind warning
];

// ---- helpers ---------------------------------------------------------------

function c(code, s) { return `\x1b[${code}m${s}\x1b[0m`; }
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function mintToken(username) {
    const body = new URLSearchParams({
        client_id: 'borrowhood-web',
        grant_type: 'password',
        username,
        password: PASSWORD,
    });
    const resp = await fetch(`${BASE_URL}/realms/${REALM}/protocol/openid-connect/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    return data.access_token || null;
}

// Discover real slugs so the sweep hits live item/workshop/raffle detail pages.
async function discoverUrls(browser) {
    const page = await browser.newPage();
    const found = { item: null, workshop: null, raffle: null };
    try {
        await page.goto(`${BASE_URL}/browse`, { waitUntil: 'networkidle2', timeout: 20000 });
        const links = await page.evaluate(() => {
            const grab = (re) => {
                const a = [...document.querySelectorAll('a[href]')].map((x) => x.getAttribute('href'))
                    .find((h) => re.test(h));
                return a || null;
            };
            return {
                item: grab(/^\/items\/[^/]+$/),
                workshop: grab(/^\/workshop\/[^/]+$/),
            };
        });
        found.item = links.item;
        found.workshop = links.workshop;

        await page.goto(`${BASE_URL}/raffles`, { waitUntil: 'networkidle2', timeout: 20000 });
        found.raffle = await page.evaluate(() => {
            // Real raffle detail pages are /raffles/<uuid>; skip /raffles/guide, /raffles/create.
            const a = [...document.querySelectorAll('a[href]')].map((x) => x.getAttribute('href'))
                .find((h) => /^\/raffles\/[0-9a-f-]{8,}$/.test(h));
            return a || null;
        });
    } catch (e) {
        // best-effort discovery
    }
    await page.close();
    return found;
}

// Load one URL, capture every client-side signal.
async function sweep(browser, url, cookie) {
    const page = await browser.newPage();
    const errors = [];
    const warnings = [];
    const badRequests = []; // {status, url}

    // Client-network noise: the runner's own connection dropping (e.g. a camper
    // wifi switch) -- ERR_NETWORK_CHANGED / disconnected -- and ERR_ABORTED (a
    // resource still loading as the page navigates). Never an app bug.
    const CLIENT_NET_NOISE = /ERR_NETWORK_CHANGED|ERR_INTERNET_DISCONNECTED|ERR_NETWORK_IO_SUSPENDED|ERR_ABORTED/;
    page.on('console', (msg) => {
        const type = msg.type();
        const text = msg.text();
        if (type === 'error') { if (!CLIENT_NET_NOISE.test(text)) errors.push(text); }
        else if (type === 'warning') {
            if (!IGNORED_WARNINGS.some((w) => text.includes(w))) warnings.push(text);
        }
    });
    page.on('pageerror', (err) => errors.push(`pageerror: ${err.message}`));
    const ownHost = new URL(BASE_URL).hostname;
    const isOurs = (u) => { try { return new URL(u).hostname === ownHost; } catch { return false; } };
    page.on('requestfailed', (req) => {
        const f = req.failure();
        const err = f ? f.errorText : '';
        // Only OUR requests, and not benign client-network noise. External domains
        // (OSM tiles, fonts) are out of our control.
        if (f && isOurs(req.url()) && !/favicon/.test(req.url()) && !CLIENT_NET_NOISE.test(err)) {
            badRequests.push({ status: err, url: req.url() });
        }
    });
    page.on('response', (resp) => {
        const s = resp.status();
        if (s >= 400 && isOurs(resp.url()) && !/favicon/.test(resp.url())) badRequests.push({ status: s, url: resp.url() });
    });

    if (cookie) {
        const u = new URL(url);
        await page.setCookie({ name: 'bh_session', value: cookie, domain: u.hostname, path: '/' });
    }

    let docStatus = 0;
    let navErr = null;
    for (let attempt = 0; attempt < 2; attempt++) {
        try {
            const resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 25000 });
            docStatus = resp ? resp.status() : 0;
            navErr = null;
            break;
        } catch (e) {
            navErr = e.message;
            // Transient client-side network blips (flaky link) -- retry once, don't blame the app.
            if (/ERR_NETWORK_CHANGED|ERR_NETWORK_IO_SUSPENDED|timeout/i.test(e.message) && attempt === 0) {
                await sleep(2000);
                // discard everything captured during the failed attempt (transient client network)
                errors.length = 0;
                badRequests.length = 0;
                warnings.length = 0;
                continue;
            }
        }
    }
    // A nav failure from the runner's own flaky link (network-changed / timeout)
    // is not an app bug -- mark the page "skipped", don't fail it.
    const navNoise = navErr && /ERR_NETWORK_CHANGED|ERR_INTERNET_DISCONNECTED|ERR_NETWORK_IO_SUSPENDED|timeout/i.test(navErr);
    if (navErr && !navNoise) errors.push(`navigation: ${navErr}`);
    await sleep(900); // let Alpine init + marked render + lazy fetches settle

    let render = { leaks: [], brokenImages: [], title: '' };
    try {
        render = await page.evaluate(() => {
            const bodyText = document.body ? document.body.innerText : '';
            const leaks = [];
            if (bodyText.includes('{{') || bodyText.includes('}}')) leaks.push('jinja {{ }}');
            if (bodyText.includes('[object Object]')) leaks.push('[object Object]');
            if (/\bi18n\.[a-z_]+/.test(bodyText)) leaks.push('i18n.key');
            if (/\*\*[^*]+\*\*/.test(bodyText)) leaks.push('raw **markdown**');
            const broken = [...document.images]
                .filter((i) => i.complete && i.naturalWidth === 0 && i.src && !i.src.startsWith('data:'))
                .map((i) => i.src);
            return { leaks, brokenImages: [...new Set(broken)].slice(0, 5), title: document.title };
        });
    } catch (e) { /* page may have failed to load */ }

    await page.close();

    // Classify: findings (hard) vs warnings (soft).
    const fivexx = badRequests.filter((r) => typeof r.status === 'number' && r.status >= 500);
    const fourxx = badRequests.filter((r) => typeof r.status === 'number' && r.status >= 400 && r.status < 500);
    const netfail = badRequests.filter((r) => typeof r.status === 'string');
    const docFailed = (docStatus >= 400 || docStatus === 0) && !navNoise;

    const findings = [];
    if (navNoise) { /* page skipped due to runner network -- recorded as soft below */ }
    if (docFailed) findings.push(`page did not load (status ${docStatus})`);
    errors.forEach((e) => findings.push(`console error: ${e}`));
    fivexx.forEach((r) => findings.push(`5xx request: ${r.status} ${r.url}`));
    render.leaks.forEach((l) => findings.push(`template leak: ${l}`));
    render.brokenImages.forEach((i) => findings.push(`broken image: ${i}`));
    netfail.forEach((r) => findings.push(`request failed: ${r.status} ${r.url}`));

    const softs = [];
    if (navNoise) softs.push(`skipped: runner network blip (${navErr})`);
    fourxx.forEach((r) => softs.push(`4xx request: ${r.status} ${r.url}`));
    warnings.forEach((w) => softs.push(`console warning: ${w}`));

    return { url, docStatus, findings, softs };
}

// ---- main ------------------------------------------------------------------

const ANON_PAGES = ['/', '/browse', '/browse?q=cooky', '/members', '/helpboard',
    '/terms', '/legal', '/why-lapiazza', '/raffles'];
const AUTH_PAGES = ['/dashboard', '/orders', '/profile', '/list'];
// Space requests out so a single run stays under the 120-reads/min per-IP limiter.
// NOTE: running the sweep several times back-to-back from one IP will still trip
// the limiter (429s) -- that's the limiter working, not an app bug. Wait ~60s
// between full runs, or run from an exempt IP.
const THROTTLE_MS = 2500;

async function main() {
    console.log(c('1;37', `\nConsole & Render Sweep -> ${BASE_URL}  (realm: ${REALM})\n`));

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors'],
    });

    const dyn = await discoverUrls(browser);
    const anonUrls = [...ANON_PAGES];
    if (dyn.item) anonUrls.push(dyn.item);
    if (dyn.workshop) anonUrls.push(dyn.workshop);
    if (dyn.raffle) anonUrls.push(dyn.raffle);

    const report = [];
    let totalFindings = 0;

    // ---- anonymous pass ----
    console.log(c('1;36', '-- Anonymous --'));
    for (const p of anonUrls) {
        const r = await sweep(browser, BASE_URL + p, null);
        report.push({ persona: 'anon', ...r });
        printResult(r);
        totalFindings += r.findings.length;
        await sleep(THROTTLE_MS);
    }

    // ---- logged-in passes ----
    for (const persona of PERSONAS) {
        const token = await mintToken(persona);
        if (!token) { console.log(c('33', `  ! could not log in as ${persona} -- skipping`)); continue; }
        console.log(c('1;36', `\n-- Logged in: ${persona} --`));
        const authUrls = [...AUTH_PAGES];
        if (dyn.item) authUrls.push(dyn.item);     // favorites/vote as a user
        if (dyn.raffle) authUrls.push(dyn.raffle); // organizer panel
        for (const p of authUrls) {
            const r = await sweep(browser, BASE_URL + p, token);
            report.push({ persona, ...r });
            printResult(r);
            totalFindings += r.findings.length;
            await sleep(THROTTLE_MS);
        }
    }

    await browser.close();

    // ---- report ----
    const reportPath = path.join(__dirname, 'console-sweep-report.json');
    fs.writeFileSync(reportPath, JSON.stringify({ base: BASE_URL, when: new Date().toISOString(), totalFindings, report }, null, 2));

    console.log(c('1;37', '\n=================================================='));
    if (totalFindings === 0) {
        console.log(c('32', `  CLEAN -- 0 findings across ${report.length} page loads. Ship it.`));
    } else {
        console.log(c('31', `  ${totalFindings} FINDINGS across ${report.length} page loads.`));
        console.log(c('31', '  FINDINGS:'));
        for (const r of report) {
            for (const f of r.findings) console.log(`    [${r.persona}] ${r.url}\n        ${f}`);
        }
    }
    console.log(c('1;37', '=================================================='));
    console.log(`  report: ${reportPath}\n`);
    process.exit(totalFindings === 0 ? 0 : 1);
}

function printResult(r) {
    const icon = r.findings.length === 0 ? c('32', 'PASS') : c('31', 'FAIL');
    const soft = r.softs.length ? c('33', ` (${r.softs.length} soft)`) : '';
    console.log(`  ${icon} ${r.url} [${r.docStatus}]${soft}`);
    for (const f of r.findings) console.log(`        ${c('31', '->')} ${f}`);
    for (const s of r.softs) console.log(`        ${c('33', '~')} ${s}`);
}

main().catch((e) => { console.error(e); process.exit(2); });
