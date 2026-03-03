#!/usr/bin/env node
/**
 * BorrowHood Payment Path E2E Test
 *
 * Tests the payment system boundary: auth, validation, DB layer,
 * and graceful degradation when PayPal/Stripe credentials are not configured.
 *
 * Without sandbox credentials, PayPal/Stripe calls return 502.
 * This test validates everything BorrowHood controls:
 * - Auth guards on all payment endpoints
 * - Input validation (rental ownership, amounts, types)
 * - Graceful 502 when provider is unavailable
 * - Payment list returns user's payments
 * - Stripe endpoints mirror PayPal behavior
 *
 * To test actual PayPal flow: set BH_PAYPAL_CLIENT_ID + BH_PAYPAL_CLIENT_SECRET
 *
 * Usage:
 *   node tests/e2e/payment-path.js                   # default: https://46.62.138.218
 *   node tests/e2e/payment-path.js http://localhost:8000
 */

// Disable TLS verification for self-signed certs
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const BASE_URL = process.argv[2] || process.env.BH_BASE_URL || 'https://46.62.138.218';

// Test state
const state = {
    lunaCookie: null,
    jakeCookie: null,
    lunaUserId: null,
    jakeUserId: null,
    itemId: null,
    listingId: null,
    rentalId: null,
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

    const setCookie = resp.headers.get('set-cookie') || '';
    const match = setCookie.match(/bh_session=([^;]+)/);
    assert(match, `No bh_session cookie for ${username}`);
    return match[1];
}

// ============================================================
// PAYMENT PATH STEPS
// ============================================================

async function main() {
    console.log(`\nBorrowHood Payment Path E2E`);
    console.log(`Target: ${BASE_URL}`);
    console.log(`Time: ${new Date().toISOString()}`);
    console.log('='.repeat(60));
    console.log('\nTests: Auth guards, validation, graceful 502 when provider unavailable');
    console.log('='.repeat(60));

    try {
        // --- ACT 1: SETUP ---
        console.log('\n--- Act 1: Setup (Auth + Rental) ---');

        await step('Luna logs in', async () => {
            state.lunaCookie = await login('luna');
            assert(state.lunaCookie.length > 50, 'Cookie too short');
        });

        await step('Jake logs in', async () => {
            state.jakeCookie = await login('jake');
            assert(state.jakeCookie.length > 50, 'Cookie too short');
        });

        await step('Fetch user IDs', async () => {
            const lunaResp = await api('GET', '/api/v1/users?q=Luna+Chen&limit=10', null, state.lunaCookie);
            const lunaUsers = lunaResp.body?.items || lunaResp.body || [];
            const luna = lunaUsers.find(u => u.slug === 'lunas-studio' || u.display_name?.includes('Luna'));
            assert(luna, 'Luna not found');
            state.lunaUserId = luna.id;

            const jakeResp = await api('GET', '/api/v1/users?q=Jake+Morrison&limit=10', null, state.jakeCookie);
            const jakeUsers = jakeResp.body?.items || jakeResp.body || [];
            const jake = jakeUsers.find(u => u.slug === 'jakes-electronics' || u.display_name?.includes('Jake'));
            assert(jake, 'Jake not found');
            state.jakeUserId = jake.id;
        });

        await step('Luna creates item + listing', async () => {
            const itemResp = await api('POST', '/api/v1/items', {
                name: `Payment Path Table Saw ${Date.now()}`,
                description: 'Professional cabinet saw with riving knife and dust collection.',
                item_type: 'physical',
                category: 'woodworking',
                condition: 'good',
            }, state.lunaCookie);
            assert(itemResp.status === 201, `Create item: ${itemResp.status}`);
            state.itemId = itemResp.body.id;

            const listingResp = await api('POST', '/api/v1/listings', {
                item_id: state.itemId,
                listing_type: 'rent',
                price: 45.00,
                price_unit: 'per_day',
                currency: 'EUR',
                deposit: 150.00,
            }, state.lunaCookie);
            assert(listingResp.status === 201, `Create listing: ${listingResp.status}`);
            state.listingId = listingResp.body.id;
        });

        await step('Jake creates rental', async () => {
            const now = new Date();
            const resp = await api('POST', '/api/v1/rentals', {
                listing_id: state.listingId,
                requested_start: new Date(now.getTime() + 86400000).toISOString(),
                requested_end: new Date(now.getTime() + 86400000 * 3).toISOString(),
                renter_message: 'Payment test rental.',
                idempotency_key: `payment-path-${Date.now()}`,
            }, state.jakeCookie);
            assert(resp.status === 201, `Create rental: ${resp.status}`);
            state.rentalId = resp.body.id;
            log('\x1b[36mINFO\x1b[0m', `  Rental: ${state.rentalId}`);
        });

        // --- ACT 2: AUTH GUARDS ---
        console.log('\n--- Act 2: Auth Guards ---');

        await step('PayPal create-order requires auth', async () => {
            const resp = await api('POST', '/api/v1/payments/create-order', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 45.00,
            });
            assert(resp.status === 401 || resp.status === 403, `Expected 401/403, got ${resp.status}`);
        });

        await step('PayPal capture requires auth', async () => {
            const resp = await api('POST', '/api/v1/payments/capture', {
                payment_id: '00000000-0000-0000-0000-000000000000',
                paypal_order_id: 'FAKE',
            });
            assert(resp.status === 401 || resp.status === 403, `Expected 401/403, got ${resp.status}`);
        });

        await step('Payment list requires auth', async () => {
            const resp = await api('GET', '/api/v1/payments');
            assert(resp.status === 401 || resp.status === 403, `Expected 401/403, got ${resp.status}`);
        });

        await step('Stripe create-session requires auth', async () => {
            const resp = await api('POST', '/api/v1/payments/stripe/create-session', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 45.00,
            });
            assert(resp.status === 401 || resp.status === 403, `Expected 401/403, got ${resp.status}`);
        });

        // --- ACT 3: PAYPAL VALIDATION ---
        console.log('\n--- Act 3: PayPal Input Validation ---');

        await step('Create-order rejects bad rental_id', async () => {
            const resp = await api('POST', '/api/v1/payments/create-order', {
                rental_id: '00000000-0000-0000-0000-000000000000',
                payment_type: 'rental',
                amount: 45.00,
            }, state.jakeCookie);
            assert(resp.status === 404, `Expected 404, got ${resp.status}`);
        });

        await step('Create-order rejects owner as payer', async () => {
            // Luna is owner, not renter -- should get 403
            const resp = await api('POST', '/api/v1/payments/create-order', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 45.00,
            }, state.lunaCookie);
            assert(resp.status === 403, `Expected 403, got ${resp.status}`);
        });

        await step('Create-order rejects zero amount', async () => {
            const resp = await api('POST', '/api/v1/payments/create-order', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 0,
            }, state.jakeCookie);
            assert(resp.status === 422, `Expected 422, got ${resp.status}`);
        });

        await step('Create-order rejects negative amount', async () => {
            const resp = await api('POST', '/api/v1/payments/create-order', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: -10,
            }, state.jakeCookie);
            assert(resp.status === 422, `Expected 422, got ${resp.status}`);
        });

        // --- ACT 4: PAYPAL GRACEFUL 502 ---
        console.log('\n--- Act 4: PayPal Graceful 502 (No Credentials) ---');

        await step('Create-order returns 502 when PayPal not configured', async () => {
            const resp = await api('POST', '/api/v1/payments/create-order', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 45.00,
                currency: 'EUR',
            }, state.jakeCookie);
            // 502 = PayPal order creation failed (no credentials)
            assert(resp.status === 502, `Expected 502 (PayPal not configured), got ${resp.status}`);
            assert(resp.body?.detail?.includes('PayPal'), `Error detail: ${resp.body?.detail}`);
            log('\x1b[36mINFO\x1b[0m', `  Graceful: "${resp.body?.detail}"`);
        });

        // --- ACT 5: STRIPE VALIDATION + 502 ---
        console.log('\n--- Act 5: Stripe Validation + Graceful 502 ---');

        await step('Stripe create-session rejects bad rental', async () => {
            const resp = await api('POST', '/api/v1/payments/stripe/create-session', {
                rental_id: '00000000-0000-0000-0000-000000000000',
                payment_type: 'rental',
                amount: 45.00,
            }, state.jakeCookie);
            assert(resp.status === 404, `Expected 404, got ${resp.status}`);
        });

        await step('Stripe create-session rejects owner as payer', async () => {
            const resp = await api('POST', '/api/v1/payments/stripe/create-session', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 45.00,
            }, state.lunaCookie);
            assert(resp.status === 403, `Expected 403, got ${resp.status}`);
        });

        await step('Stripe create-session returns 502 when not configured', async () => {
            const resp = await api('POST', '/api/v1/payments/stripe/create-session', {
                rental_id: state.rentalId,
                payment_type: 'rental',
                amount: 45.00,
                currency: 'EUR',
            }, state.jakeCookie);
            assert(resp.status === 502, `Expected 502 (Stripe not configured), got ${resp.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Graceful: "${resp.body?.detail}"`);
        });

        // --- ACT 6: CAPTURE + REFUND VALIDATION ---
        console.log('\n--- Act 6: Capture + Refund Validation ---');

        await step('Capture rejects non-existent payment', async () => {
            const resp = await api('POST', '/api/v1/payments/capture', {
                payment_id: '00000000-0000-0000-0000-000000000000',
                paypal_order_id: 'FAKE_ORDER',
            }, state.jakeCookie);
            assert(resp.status === 404, `Expected 404, got ${resp.status}`);
        });

        await step('Refund rejects non-existent payment', async () => {
            const resp = await api('POST', '/api/v1/payments/00000000-0000-0000-0000-000000000000/refund', {
                reason: 'Test refund',
            }, state.lunaCookie);
            assert(resp.status === 404, `Expected 404, got ${resp.status}`);
        });

        await step('Stripe confirm rejects non-existent payment', async () => {
            const resp = await api('POST', '/api/v1/payments/stripe/confirm', {
                payment_id: '00000000-0000-0000-0000-000000000000',
                stripe_session_id: 'cs_fake_123',
            }, state.jakeCookie);
            assert(resp.status === 404, `Expected 404, got ${resp.status}`);
        });

        await step('Stripe refund rejects non-existent payment', async () => {
            const resp = await api('POST', '/api/v1/payments/stripe/00000000-0000-0000-0000-000000000000/refund', {
                reason: 'Test refund',
            }, state.lunaCookie);
            assert(resp.status === 404, `Expected 404, got ${resp.status}`);
        });

        // --- ACT 7: LIST PAYMENTS ---
        console.log('\n--- Act 7: Payment List ---');

        await step('Jake can list his payments (empty or existing)', async () => {
            const resp = await api('GET', '/api/v1/payments?limit=10', null, state.jakeCookie);
            assert(resp.status === 200, `List payments: ${resp.status}`);
            assert(Array.isArray(resp.body), 'Response is not an array');
            log('\x1b[36mINFO\x1b[0m', `  Jake has ${resp.body.length} payments`);
        });

        await step('Luna can list her payments (empty or existing)', async () => {
            const resp = await api('GET', '/api/v1/payments?limit=10', null, state.lunaCookie);
            assert(resp.status === 200, `List payments: ${resp.status}`);
            assert(Array.isArray(resp.body), 'Response is not an array');
            log('\x1b[36mINFO\x1b[0m', `  Luna has ${resp.body.length} payments`);
        });

        // --- ACT 8: PAYMENT TYPE COVERAGE ---
        console.log('\n--- Act 8: All Payment Types Accepted ---');

        const paymentTypes = ['rental', 'deposit', 'purchase', 'auction', 'service'];
        for (const ptype of paymentTypes) {
            await step(`PayPal accepts payment_type="${ptype}"`, async () => {
                const resp = await api('POST', '/api/v1/payments/create-order', {
                    rental_id: state.rentalId,
                    payment_type: ptype,
                    amount: 10.00,
                }, state.jakeCookie);
                // 502 = reached PayPal (validation passed), not 422 (invalid type)
                assert(resp.status === 502, `Expected 502 for type ${ptype}, got ${resp.status}`);
            });
        }

    } catch (err) {
        console.log(`\n\x1b[31mPayment path STOPPED at step ${stepNum}\x1b[0m`);
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    const total = passed + failed;
    if (failed === 0) {
        console.log(`\x1b[32mPAYMENT PATH: ALL ${total} STEPS PASSED\x1b[0m`);
    } else {
        console.log(`\x1b[31mPAYMENT PATH: ${passed}/${total} passed, ${failed} failed\x1b[0m`);
    }

    console.log('\nNote: PayPal/Stripe return 502 because sandbox credentials');
    console.log('are not configured. Set BH_PAYPAL_CLIENT_ID + BH_PAYPAL_CLIENT_SECRET');
    console.log('for full payment flow testing.');

    // JSON report
    const fs = require('fs');
    const report = {
        base_url: BASE_URL,
        timestamp: new Date().toISOString(),
        summary: { passed, failed, total },
        artifacts: state,
        steps: results,
    };
    const reportPath = __dirname + '/payment-path-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`Report: ${reportPath}`);

    process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
    console.error('Fatal:', err);
    process.exit(2);
});
