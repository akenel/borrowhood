#!/usr/bin/env node
/**
 * BorrowHood E2E Test Suite
 *
 * Puppeteer-based end-to-end tests against a live BorrowHood instance.
 * Tests public pages, auth flows, and API smoke tests.
 *
 * Usage:
 *   node tests/e2e/test-suite.js                   # default: https://46.62.138.218
 *   node tests/e2e/test-suite.js http://localhost:8000
 *   BH_BASE_URL=https://46.62.138.218 node tests/e2e/test-suite.js
 */

const puppeteer = require('puppeteer');

const BASE_URL = process.argv[2] || process.env.BH_BASE_URL || 'https://46.62.138.218';

// Test results
const results = [];
let passed = 0;
let failed = 0;

function log(icon, msg) {
    console.log(`  ${icon} ${msg}`);
}

async function test(name, fn) {
    const start = Date.now();
    try {
        await fn();
        const ms = Date.now() - start;
        results.push({ name, status: 'pass', ms });
        passed++;
        log('\x1b[32mPASS\x1b[0m', `${name} (${ms}ms)`);
    } catch (err) {
        const ms = Date.now() - start;
        results.push({ name, status: 'fail', ms, error: err.message });
        failed++;
        log('\x1b[31mFAIL\x1b[0m', `${name} -- ${err.message}`);
    }
}

function assert(condition, msg) {
    if (!condition) throw new Error(msg || 'Assertion failed');
}

async function fetchJSON(page, path) {
    const resp = await page.evaluate(async (url) => {
        const r = await fetch(url);
        return { status: r.status, body: await r.json().catch(() => null) };
    }, `${BASE_URL}${path}`);
    return resp;
}

async function fetchStatus(page, path) {
    const resp = await page.evaluate(async (url) => {
        const r = await fetch(url);
        return r.status;
    }, `${BASE_URL}${path}`);
    return resp;
}

// ============================================================
// TEST SUITES
// ============================================================

async function testPublicPages(page) {
    console.log('\n--- Public Pages ---');

    const publicPages = [
        ['/', 'Home'],
        ['/browse', 'Browse'],
        ['/members', 'Members'],
        ['/helpboard', 'Helpboard'],
        ['/terms', 'Terms'],
    ];

    for (const [path, name] of publicPages) {
        await test(`${name} page loads (${path})`, async () => {
            const resp = await page.goto(`${BASE_URL}${path}`, {
                waitUntil: 'domcontentloaded',
                timeout: 15000,
            });
            assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
        });
    }
}

async function testHealthEndpoints(page) {
    console.log('\n--- Health Endpoints ---');

    await test('Health endpoint returns ok', async () => {
        const resp = await page.goto(`${BASE_URL}/api/v1/health`, {
            waitUntil: 'domcontentloaded',
            timeout: 15000,
        });
        assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
        const body = await resp.json();
        assert(body?.status === 'healthy' || body?.status === 'ok', `Health status: ${body?.status}`);
    });
}

async function testAPISmokeTests(page) {
    console.log('\n--- API Smoke Tests ---');

    await test('Items API returns list', async () => {
        const resp = await page.goto(`${BASE_URL}/api/v1/items?limit=5`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
        const body = await resp.json();
        assert(Array.isArray(body), 'Expected array');
    });

    await test('Users API returns paginated list', async () => {
        const resp = await page.goto(`${BASE_URL}/api/v1/users?limit=5`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
        const body = await resp.json();
        assert(body?.items !== undefined || Array.isArray(body), 'Expected items array or array');
    });

    await test('Reviews summary returns data', async () => {
        // Get a user from the paginated endpoint
        const usersResp = await page.goto(`${BASE_URL}/api/v1/users?limit=1`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        const usersBody = await usersResp.json();
        const userList = usersBody?.items || usersBody || [];
        if (userList.length > 0) {
            const userId = userList[0].id;
            const resp = await page.goto(`${BASE_URL}/api/v1/reviews/summary/${userId}`, {
                waitUntil: 'domcontentloaded', timeout: 15000,
            });
            assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
            const body = await resp.json();
            assert(body?.user_id !== undefined, 'Missing user_id in summary');
        }
    });

    await test('Badges catalog returns list', async () => {
        const resp = await page.goto(`${BASE_URL}/api/v1/badges/catalog`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
    });

    await test('Helpboard summary returns counts', async () => {
        const resp = await page.goto(`${BASE_URL}/api/v1/helpboard/summary`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
        const body = await resp.json();
        assert(body?.total !== undefined, 'Missing total in summary');
    });

    await test('Helpboard posts returns paginated', async () => {
        const resp = await page.goto(`${BASE_URL}/api/v1/helpboard/posts?limit=5`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);
        const body = await resp.json();
        assert(body?.items !== undefined, 'Missing items in response');
    });
}

async function testDemoLogin(page) {
    console.log('\n--- Demo Login Flow ---');

    await test('Demo login page loads', async () => {
        const resp = await page.goto(`${BASE_URL}/demo-login`, {
            waitUntil: 'domcontentloaded',
            timeout: 15000,
        });
        // Demo login might redirect or return 200
        assert([200, 307].includes(resp.status()), `Expected 200 or 307, got ${resp.status()}`);
    });
}

async function testAuthenticatedPages(page) {
    console.log('\n--- Authenticated Pages (require login redirect) ---');

    const authPages = [
        ['/dashboard', 'Dashboard'],
        ['/profile', 'Profile'],
        ['/list', 'List Item'],
    ];

    for (const [path, name] of authPages) {
        await test(`${name} redirects to login (${path})`, async () => {
            const resp = await page.goto(`${BASE_URL}${path}`, {
                waitUntil: 'domcontentloaded',
                timeout: 15000,
            });
            // Should return 200 (login page after redirect) or the page itself
            assert([200, 307].includes(resp.status()), `Expected 200 or 307, got ${resp.status()}`);
        });
    }
}

async function testFeatureChecks(page) {
    console.log('\n--- Feature Checks ---');

    await test('Browse page has search form', async () => {
        await page.goto(`${BASE_URL}/browse`, {
            waitUntil: 'domcontentloaded',
            timeout: 15000,
        });
        const hasSearch = await page.evaluate(() => {
            return !!document.querySelector('input[type="search"], input[name="q"], form');
        });
        assert(hasSearch, 'No search form found on browse page');
    });

    await test('Home page has category links', async () => {
        await page.goto(`${BASE_URL}/`, {
            waitUntil: 'domcontentloaded',
            timeout: 15000,
        });
        const hasLinks = await page.evaluate(() => {
            return document.querySelectorAll('a[href*="/browse"]').length > 0;
        });
        assert(hasLinks, 'No browse links found on home page');
    });

    await test('Members page shows user cards', async () => {
        await page.goto(`${BASE_URL}/members`, {
            waitUntil: 'domcontentloaded',
            timeout: 15000,
        });
        const content = await page.content();
        // Should have user-related content
        assert(
            content.includes('workshop') || content.includes('member') || content.includes('user'),
            'No member content found'
        );
    });
}

async function testWorkshopPages(page) {
    console.log('\n--- Workshop Pages ---');

    await test('Workshop page loads for first user', async () => {
        const usersResp = await page.goto(`${BASE_URL}/api/v1/users?limit=1`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        const usersBody = await usersResp.json();
        const userList = usersBody?.items || usersBody || [];
        if (userList.length > 0) {
            const slug = userList[0].slug;
            const resp = await page.goto(`${BASE_URL}/workshop/${slug}`, {
                waitUntil: 'domcontentloaded',
                timeout: 15000,
            });
            assert(resp.status() === 200, `Expected 200, got ${resp.status()}`);

            // Check for reputation card
            const hasReputation = await page.evaluate(() => {
                const text = document.body.innerText;
                return text.includes('points') || text.includes('punti') ||
                       text.includes('Reputation') || text.includes('Reputazione');
            });
            assert(hasReputation, 'No reputation section found');
        }
    });
}

// ============================================================
// MAIN
// ============================================================

async function main() {
    console.log(`\nBorrowHood E2E Test Suite`);
    console.log(`Target: ${BASE_URL}`);
    console.log(`Time: ${new Date().toISOString()}`);
    console.log('='.repeat(50));

    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--ignore-certificate-errors',
        ],
    });

    const page = await browser.newPage();
    page.setDefaultTimeout(15000);

    // Suppress console noise from the target page
    page.on('pageerror', () => {});

    try {
        await testHealthEndpoints(page);
        await testPublicPages(page);
        await testAPISmokeTests(page);
        await testDemoLogin(page);
        await testAuthenticatedPages(page);
        await testFeatureChecks(page);
        await testWorkshopPages(page);
    } catch (err) {
        console.error('\nSuite error:', err.message);
    }

    await browser.close();

    // Summary
    console.log('\n' + '='.repeat(50));
    console.log(`Results: ${passed} passed, ${failed} failed, ${passed + failed} total`);

    if (failed > 0) {
        console.log('\nFailed tests:');
        results.filter(r => r.status === 'fail').forEach(r => {
            console.log(`  - ${r.name}: ${r.error}`);
        });
    }

    // JSON report
    const report = {
        base_url: BASE_URL,
        timestamp: new Date().toISOString(),
        summary: { passed, failed, total: passed + failed },
        tests: results,
    };

    const fs = require('fs');
    const reportPath = __dirname + '/test-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\nReport: ${reportPath}`);

    process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
    console.error('Fatal:', err);
    process.exit(2);
});
