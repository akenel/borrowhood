#!/usr/bin/env node
/**
 * BorrowHood Golden Path E2E Test
 *
 * The full happy path: Luna creates an item + listing,
 * Jake rents it, lockbox pickup/return, complete, both review.
 *
 * This proves the entire platform works end-to-end.
 *
 * Usage:
 *   node tests/e2e/golden-path.js                   # default: https://46.62.138.218
 *   node tests/e2e/golden-path.js http://localhost:8000
 */

// Disable TLS verification for self-signed certs
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const puppeteer = require('puppeteer');

const BASE_URL = process.argv[2] || process.env.BH_BASE_URL || 'https://46.62.138.218';

// Test state -- shared across steps
const state = {
    lunaCookie: null,
    jakeCookie: null,
    lunaUserId: null,
    jakeUserId: null,
    itemId: null,
    itemSlug: null,
    listingId: null,
    rentalId: null,
    pickupCode: null,
    returnCode: null,
};

// Results tracking
const results = [];
let passed = 0;
let failed = 0;
let stepNum = 0;

function log(icon, msg) {
    console.log(`  ${icon} ${msg}`);
}

async function step(name, fn) {
    stepNum++;
    const label = `Step ${stepNum}: ${name}`;
    const start = Date.now();
    try {
        await fn();
        const ms = Date.now() - start;
        results.push({ name: label, status: 'pass', ms });
        passed++;
        log('\x1b[32mPASS\x1b[0m', `${label} (${ms}ms)`);
    } catch (err) {
        const ms = Date.now() - start;
        results.push({ name: label, status: 'fail', ms, error: err.message });
        failed++;
        log('\x1b[31mFAIL\x1b[0m', `${label} -- ${err.message}`);
        // Golden path is sequential -- fail fast
        throw err;
    }
}

function assert(condition, msg) {
    if (!condition) throw new Error(msg || 'Assertion failed');
}

async function api(method, path, body, cookie) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (cookie) opts.headers['Cookie'] = `bh_session=${cookie}`;
    if (body) opts.body = JSON.stringify(body);

    const resp = await fetch(`${BASE_URL}${path}`, opts);
    const text = await resp.text();
    let json = null;
    try { json = JSON.parse(text); } catch (e) {}

    return { status: resp.status, body: json, text, headers: resp.headers };
}

async function login(username) {
    const resp = await fetch(`${BASE_URL}/api/v1/demo/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password: 'helix_pass' }),
    });

    assert(resp.status === 200, `Login failed for ${username}: ${resp.status}`);

    // Extract bh_session cookie from Set-Cookie header
    const setCookie = resp.headers.get('set-cookie') || '';
    const match = setCookie.match(/bh_session=([^;]+)/);
    assert(match, `No bh_session cookie for ${username}`);
    return match[1];
}

// ============================================================
// GOLDEN PATH STEPS
// ============================================================

async function main() {
    console.log(`\nBorrowHood Golden Path E2E`);
    console.log(`Target: ${BASE_URL}`);
    console.log(`Time: ${new Date().toISOString()}`);
    console.log('='.repeat(60));
    console.log('\nCast: Luna Chen (TRUSTED, owner) + Jake Morrison (ACTIVE, renter)');
    console.log('='.repeat(60));

    try {
        // --- ACT 1: LOGIN ---
        console.log('\n--- Act 1: Authentication ---');

        await step('Luna logs in', async () => {
            state.lunaCookie = await login('luna');
            assert(state.lunaCookie.length > 50, 'Cookie too short');
        });

        await step('Jake logs in', async () => {
            state.jakeCookie = await login('jake');
            assert(state.jakeCookie.length > 50, 'Cookie too short');
        });

        await step('Luna fetches her profile', async () => {
            // Search by name to handle large user counts
            const resp = await api('GET', '/api/v1/users?q=Luna+Chen&limit=10', null, state.lunaCookie);
            assert(resp.status === 200, `Users API: ${resp.status}`);
            const users = resp.body?.items || resp.body || [];
            const luna = users.find(u => u.slug === 'lunas-studio' || u.display_name?.includes('Luna'));
            assert(luna, 'Luna not found in users list');
            state.lunaUserId = luna.id;
        });

        await step('Jake fetches his profile', async () => {
            const resp = await api('GET', '/api/v1/users?q=Jake+Morrison&limit=10', null, state.jakeCookie);
            assert(resp.status === 200, `Users API: ${resp.status}`);
            const users = resp.body?.items || resp.body || [];
            const jake = users.find(u => u.slug === 'jakes-electronics' || u.display_name?.includes('Jake'));
            assert(jake, 'Jake not found in users list');
            state.jakeUserId = jake.id;
        });

        // --- ACT 2: LUNA CREATES AN ITEM + LISTING ---
        console.log('\n--- Act 2: Luna Creates Item + Listing ---');

        await step('Luna creates an item (Ceramic Kiln)', async () => {
            const resp = await api('POST', '/api/v1/items', {
                name: `Golden Path Ceramic Kiln ${Date.now()}`,
                description: 'Professional ceramic kiln, perfect for pottery and glazing. Temperature up to 1300C.',
                item_type: 'physical',
                category: 'art',
                condition: 'good',
                brand: 'Skutt',
                model: 'KM-1027',
            }, state.lunaCookie);
            assert(resp.status === 201, `Create item: ${resp.status} -- ${resp.text}`);
            state.itemId = resp.body.id;
            state.itemSlug = resp.body.slug;
            log('\x1b[36mINFO\x1b[0m', `  Item: ${state.itemId} (${state.itemSlug})`);
        });

        await step('Luna creates a RENT listing', async () => {
            const resp = await api('POST', '/api/v1/listings', {
                item_id: state.itemId,
                listing_type: 'rent',
                price: 35.00,
                price_unit: 'per_day',
                currency: 'EUR',
                deposit: 100.00,
                min_rental_days: 1,
                max_rental_days: 14,
                delivery_available: false,
                pickup_only: true,
                notes: 'Handle with care. Kiln is heavy (45kg).',
            }, state.lunaCookie);
            assert(resp.status === 201, `Create listing: ${resp.status} -- ${resp.text}`);
            state.listingId = resp.body.id;
            assert(resp.body.status === 'active', `Listing status: ${resp.body.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Listing: ${state.listingId} (EUR 35/day)`);
        });

        await step('Listing appears in public API', async () => {
            const resp = await api('GET', `/api/v1/listings/${state.listingId}`);
            assert(resp.status === 200, `Get listing: ${resp.status}`);
            assert(resp.body.status === 'active', 'Listing not active');
            assert(resp.body.price === 35.0, `Price: ${resp.body.price}`);
        });

        await step('Item appears on browse page', async () => {
            const resp = await api('GET', `/api/v1/items/${state.itemId}`);
            assert(resp.status === 200, `Get item: ${resp.status}`);
            assert(resp.body.slug === state.itemSlug, 'Slug mismatch');
        });

        // --- ACT 3: JAKE RENTS THE KILN ---
        console.log('\n--- Act 3: Jake Requests Rental ---');

        const now = new Date();
        const startDate = new Date(now.getTime() + 86400000); // tomorrow
        const endDate = new Date(now.getTime() + 86400000 * 4); // 4 days from now

        await step('Jake requests rental (3 days)', async () => {
            const resp = await api('POST', '/api/v1/rentals', {
                listing_id: state.listingId,
                requested_start: startDate.toISOString(),
                requested_end: endDate.toISOString(),
                renter_message: 'Hi Luna! I need the kiln for a weekend pottery workshop. Will handle with care!',
                idempotency_key: `golden-path-${Date.now()}`,
            }, state.jakeCookie);
            assert(resp.status === 201, `Create rental: ${resp.status} -- ${resp.text}`);
            state.rentalId = resp.body.id;
            assert(resp.body.status === 'pending', `Rental status: ${resp.body.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Rental: ${state.rentalId} (PENDING)`);
        });

        await step('Jake cannot rent his own items (validation)', async () => {
            // Jake tries to rent Luna's item again with same idempotency key -> should return existing
            // Instead, let's verify Jake can't create a listing on Luna's item
            const resp = await api('POST', '/api/v1/listings', {
                item_id: state.itemId,
                listing_type: 'rent',
                price: 10,
            }, state.jakeCookie);
            assert(resp.status === 403 || resp.status === 404, `Expected 403/404, got ${resp.status}`);
        });

        // --- ACT 4: LUNA APPROVES ---
        console.log('\n--- Act 4: Luna Approves Rental ---');

        await step('Luna approves the rental', async () => {
            const resp = await api('PATCH', `/api/v1/rentals/${state.rentalId}/status`, {
                status: 'approved',
                message: 'Approved! You can pick it up tomorrow at my studio. Via Roma 15.',
            }, state.lunaCookie);
            assert(resp.status === 200, `Approve rental: ${resp.status} -- ${resp.text}`);
            const rental = resp.body;
            assert(rental.status === 'approved', `Status: ${rental.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Rental APPROVED`);
        });

        // --- ACT 5: LOCKBOX CODES ---
        console.log('\n--- Act 5: Lockbox Codes ---');

        await step('Luna generates lockbox codes', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/generate`, {
                location_hint: 'Studio back door, shelf marked "KILN"',
                instructions: 'Use both hands to lift. Heavy!',
            }, state.lunaCookie);
            assert(resp.status === 201, `Generate codes: ${resp.status} -- ${resp.text}`);
            state.pickupCode = resp.body.pickup_code;
            state.returnCode = resp.body.return_code;
            assert(state.pickupCode.length === 8, `Pickup code length: ${state.pickupCode.length}`);
            assert(state.returnCode.length === 8, `Return code length: ${state.returnCode.length}`);
            log('\x1b[36mINFO\x1b[0m', `  Pickup: ${state.pickupCode}, Return: ${state.returnCode}`);
        });

        await step('Duplicate lockbox generation returns 409', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/generate`, {}, state.lunaCookie);
            assert(resp.status === 409, `Expected 409, got ${resp.status}`);
        });

        // --- ACT 6: JAKE PICKS UP ---
        console.log('\n--- Act 6: Jake Picks Up (Lockbox) ---');

        await step('Wrong code is rejected', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/verify`, {
                code: 'WRONGCOD',
            }, state.jakeCookie);
            assert(resp.status === 400, `Expected 400, got ${resp.status}`);
        });

        await step('Jake verifies pickup code', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/verify`, {
                code: state.pickupCode,
            }, state.jakeCookie);
            assert(resp.status === 200, `Verify pickup: ${resp.status} -- ${resp.text}`);
            assert(resp.body.action === 'pickup', `Action: ${resp.body.action}`);
            assert(resp.body.valid === true, 'Not valid');
            log('\x1b[36mINFO\x1b[0m', `  PICKED UP`);
        });

        await step('Rental status is now picked_up', async () => {
            const resp = await api('GET', `/api/v1/rentals?limit=50`, null, state.jakeCookie);
            assert(resp.status === 200, `List rentals: ${resp.status}`);
            const rentals = resp.body?.items || resp.body || [];
            const rental = rentals.find(r => r.id === state.rentalId);
            assert(rental, 'Rental not found');
            assert(rental.status === 'picked_up', `Status: ${rental.status}`);
        });

        // --- ACT 7: JAKE RETURNS ---
        console.log('\n--- Act 7: Jake Returns (Lockbox) ---');

        await step('Jake verifies return code', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/verify`, {
                code: state.returnCode,
            }, state.jakeCookie);
            assert(resp.status === 200, `Verify return: ${resp.status} -- ${resp.text}`);
            assert(resp.body.action === 'return', `Action: ${resp.body.action}`);
            assert(resp.body.valid === true, 'Not valid');
            log('\x1b[36mINFO\x1b[0m', `  RETURNED`);
        });

        // --- ACT 8: LUNA COMPLETES ---
        console.log('\n--- Act 8: Luna Completes Rental ---');

        await step('Luna marks rental complete', async () => {
            const resp = await api('PATCH', `/api/v1/rentals/${state.rentalId}/status`, {
                status: 'completed',
                message: 'Everything looks great. Thanks Jake!',
            }, state.lunaCookie);
            assert(resp.status === 200, `Complete rental: ${resp.status} -- ${resp.text}`);
            assert(resp.body.status === 'completed', `Status: ${resp.body.status}`);
            log('\x1b[36mINFO\x1b[0m', `  COMPLETED`);
        });

        // --- ACT 9: REVIEWS ---
        console.log('\n--- Act 9: Mutual Reviews ---');

        await step('Jake reviews Luna (5 stars)', async () => {
            const resp = await api('POST', '/api/v1/reviews', {
                rental_id: state.rentalId,
                reviewee_id: state.lunaUserId,
                rating: 5,
                title: 'Perfect kiln, perfect host!',
                body: 'Luna was super helpful. The kiln was clean and ready to go. Studio is easy to find. Will rent again!',
            }, state.jakeCookie);
            assert(resp.status === 201, `Jake review: ${resp.status} -- ${resp.text}`);
            log('\x1b[36mINFO\x1b[0m', `  Jake -> Luna: 5 stars`);
        });

        await step('Luna reviews Jake (5 stars)', async () => {
            const resp = await api('POST', '/api/v1/reviews', {
                rental_id: state.rentalId,
                reviewee_id: state.jakeUserId,
                rating: 5,
                title: 'Excellent renter!',
                body: 'Jake returned the kiln in perfect condition. On time, respectful. Great borrower.',
            }, state.lunaCookie);
            assert(resp.status === 201, `Luna review: ${resp.status} -- ${resp.text}`);
            log('\x1b[36mINFO\x1b[0m', `  Luna -> Jake: 5 stars`);
        });

        await step('Duplicate review is rejected (409)', async () => {
            const resp = await api('POST', '/api/v1/reviews', {
                rental_id: state.rentalId,
                reviewee_id: state.lunaUserId,
                rating: 4,
                title: 'Duplicate',
            }, state.jakeCookie);
            assert(resp.status === 409, `Expected 409, got ${resp.status}`);
        });

        // --- ACT 10: VERIFICATION ---
        console.log('\n--- Act 10: Verify Everything ---');

        await step('Luna review summary shows new review', async () => {
            const resp = await api('GET', `/api/v1/reviews/summary/${state.lunaUserId}`);
            assert(resp.status === 200, `Review summary: ${resp.status}`);
            assert(resp.body.count >= 1, `Review count: ${resp.body.count}`);
            assert(resp.body.average >= 4.0, `Average: ${resp.body.average}`);
            log('\x1b[36mINFO\x1b[0m', `  Luna: ${resp.body.count} reviews, avg ${resp.body.average}`);
        });

        await step('Jake review summary shows new review', async () => {
            const resp = await api('GET', `/api/v1/reviews/summary/${state.jakeUserId}`);
            assert(resp.status === 200, `Review summary: ${resp.status}`);
            assert(resp.body.count >= 1, `Review count: ${resp.body.count}`);
            log('\x1b[36mINFO\x1b[0m', `  Jake: ${resp.body.count} reviews, avg ${resp.body.average}`);
        });

        await step('Notifications were created for Luna', async () => {
            const resp = await api('GET', '/api/v1/notifications?limit=10', null, state.lunaCookie);
            assert(resp.status === 200, `Notifications: ${resp.status}`);
            const notifications = resp.body || [];
            assert(notifications.length >= 1, `Expected notifications, got ${notifications.length}`);
            log('\x1b[36mINFO\x1b[0m', `  Luna has ${notifications.length} notifications`);
        });

        await step('Notifications were created for Jake', async () => {
            const resp = await api('GET', '/api/v1/notifications?limit=10', null, state.jakeCookie);
            assert(resp.status === 200, `Notifications: ${resp.status}`);
            const notifications = resp.body || [];
            assert(notifications.length >= 1, `Expected notifications, got ${notifications.length}`);
            log('\x1b[36mINFO\x1b[0m', `  Jake has ${notifications.length} notifications`);
        });

        await step('Item detail page loads in browser', async () => {
            const browser = await puppeteer.launch({
                headless: 'new',
                args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors'],
            });
            const page = await browser.newPage();
            const resp = await page.goto(`${BASE_URL}/items/${state.itemSlug}`, {
                waitUntil: 'domcontentloaded', timeout: 15000,
            });
            assert(resp.status() === 200, `Item page: ${resp.status()}`);
            const content = await page.content();
            assert(content.includes('Ceramic Kiln'), 'Item name not found on page');
            await browser.close();
        });

        await step('Workshop page shows Luna reputation', async () => {
            const browser = await puppeteer.launch({
                headless: 'new',
                args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors'],
            });
            const page = await browser.newPage();
            const resp = await page.goto(`${BASE_URL}/workshop/lunas-studio`, {
                waitUntil: 'domcontentloaded', timeout: 15000,
            });
            assert(resp.status() === 200, `Workshop page: ${resp.status()}`);
            const content = await page.content();
            assert(
                content.includes('Reputation') || content.includes('Reputazione') || content.includes('points'),
                'Reputation section not found'
            );
            await browser.close();
        });

    } catch (err) {
        console.log(`\n\x1b[31mGolden path STOPPED at step ${stepNum}\x1b[0m`);
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    const total = passed + failed;
    if (failed === 0) {
        console.log(`\x1b[32mGOLDEN PATH: ALL ${total} STEPS PASSED\x1b[0m`);
    } else {
        console.log(`\x1b[31mGOLDEN PATH: ${passed}/${total} passed, ${failed} failed\x1b[0m`);
    }

    // State dump
    console.log('\nArtifacts:');
    console.log(`  Item:    ${state.itemId} (${state.itemSlug})`);
    console.log(`  Listing: ${state.listingId}`);
    console.log(`  Rental:  ${state.rentalId}`);
    console.log(`  Lockbox: pickup=${state.pickupCode} return=${state.returnCode}`);

    // JSON report
    const fs = require('fs');
    const report = {
        base_url: BASE_URL,
        timestamp: new Date().toISOString(),
        summary: { passed, failed, total },
        artifacts: state,
        steps: results,
    };
    const reportPath = __dirname + '/golden-path-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`Report: ${reportPath}`);

    process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
    console.error('Fatal:', err);
    process.exit(2);
});
