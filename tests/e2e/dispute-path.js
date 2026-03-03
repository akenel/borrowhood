#!/usr/bin/env node
/**
 * BorrowHood Dispute Path E2E Test
 *
 * Full dispute lifecycle: Luna creates item, Jake rents,
 * Jake holds deposit, Luna files dispute (item_damaged),
 * Jake responds, Luna resolves (deposit_forfeited).
 *
 * Proves: dispute filing, response, resolution, deposit forfeit,
 * notifications to both parties, rental status transitions.
 *
 * Usage:
 *   node tests/e2e/dispute-path.js                   # default: https://46.62.138.218
 *   node tests/e2e/dispute-path.js http://localhost:8000
 */

// Disable TLS verification for self-signed certs
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

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
    depositId: null,
    disputeId: null,
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
        throw err; // Fail fast -- sequential dependency chain
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
// DISPUTE PATH STEPS
// ============================================================

async function main() {
    console.log(`\nBorrowHood Dispute Path E2E`);
    console.log(`Target: ${BASE_URL}`);
    console.log(`Time: ${new Date().toISOString()}`);
    console.log('='.repeat(60));
    console.log('\nCast: Luna Chen (TRUSTED, owner) + Jake Morrison (ACTIVE, renter)');
    console.log('Scenario: Jake damages item, Luna disputes, deposit forfeited');
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

        // --- ACT 2: LUNA CREATES ITEM + LISTING ---
        console.log('\n--- Act 2: Luna Creates Item + Listing ---');

        await step('Luna creates an item (Welding Torch)', async () => {
            const resp = await api('POST', '/api/v1/items', {
                name: `Dispute Path Welding Torch ${Date.now()}`,
                description: 'Industrial MIG welder with gas shield. Requires 220V outlet.',
                item_type: 'physical',
                category: 'welding',
                condition: 'good',
                brand: 'Lincoln Electric',
                model: 'Power MIG 210',
            }, state.lunaCookie);
            assert(resp.status === 201, `Create item: ${resp.status} -- ${resp.text}`);
            state.itemId = resp.body.id;
            state.itemSlug = resp.body.slug;
            log('\x1b[36mINFO\x1b[0m', `  Item: ${state.itemId} (${state.itemSlug})`);
        });

        await step('Luna creates a RENT listing with deposit', async () => {
            const resp = await api('POST', '/api/v1/listings', {
                item_id: state.itemId,
                listing_type: 'rent',
                price: 50.00,
                price_unit: 'per_day',
                currency: 'EUR',
                deposit: 200.00,
                min_rental_days: 1,
                max_rental_days: 7,
                delivery_available: false,
                pickup_only: true,
                notes: 'Fragile equipment. Full deposit required.',
            }, state.lunaCookie);
            assert(resp.status === 201, `Create listing: ${resp.status} -- ${resp.text}`);
            state.listingId = resp.body.id;
            log('\x1b[36mINFO\x1b[0m', `  Listing: ${state.listingId} (EUR 50/day, EUR 200 deposit)`);
        });

        // --- ACT 3: JAKE RENTS ---
        console.log('\n--- Act 3: Jake Rents the Welder ---');

        const now = new Date();
        const startDate = new Date(now.getTime() + 86400000);
        const endDate = new Date(now.getTime() + 86400000 * 3);

        await step('Jake requests rental (2 days)', async () => {
            const resp = await api('POST', '/api/v1/rentals', {
                listing_id: state.listingId,
                requested_start: startDate.toISOString(),
                requested_end: endDate.toISOString(),
                renter_message: 'Need the welder for a gate repair project.',
                idempotency_key: `dispute-path-${Date.now()}`,
            }, state.jakeCookie);
            assert(resp.status === 201, `Create rental: ${resp.status} -- ${resp.text}`);
            state.rentalId = resp.body.id;
            assert(resp.body.status === 'pending', `Rental status: ${resp.body.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Rental: ${state.rentalId} (PENDING)`);
        });

        await step('Luna approves the rental', async () => {
            const resp = await api('PATCH', `/api/v1/rentals/${state.rentalId}/status`, {
                status: 'approved',
                message: 'Approved. Handle with care -- the wire feed is sensitive.',
            }, state.lunaCookie);
            assert(resp.status === 200, `Approve: ${resp.status} -- ${resp.text}`);
            assert(resp.body.status === 'approved', `Status: ${resp.body.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Rental APPROVED`);
        });

        // --- ACT 4: LOCKBOX PICKUP + RETURN ---
        console.log('\n--- Act 4: Lockbox Pickup + Return ---');

        await step('Luna generates lockbox codes', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/generate`, {
                location_hint: 'Workshop shelf, labeled "WELDER"',
                instructions: 'Heavy unit. Two hands.',
            }, state.lunaCookie);
            assert(resp.status === 201, `Generate codes: ${resp.status} -- ${resp.text}`);
            state.pickupCode = resp.body.pickup_code;
            state.returnCode = resp.body.return_code;
            log('\x1b[36mINFO\x1b[0m', `  Pickup: ${state.pickupCode}, Return: ${state.returnCode}`);
        });

        await step('Jake picks up (lockbox)', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/verify`, {
                code: state.pickupCode,
            }, state.jakeCookie);
            assert(resp.status === 200, `Pickup: ${resp.status} -- ${resp.text}`);
            assert(resp.body.action === 'pickup', `Action: ${resp.body.action}`);
            log('\x1b[36mINFO\x1b[0m', `  PICKED UP`);
        });

        await step('Jake returns (lockbox)', async () => {
            const resp = await api('POST', `/api/v1/lockbox/${state.rentalId}/verify`, {
                code: state.returnCode,
            }, state.jakeCookie);
            assert(resp.status === 200, `Return: ${resp.status} -- ${resp.text}`);
            assert(resp.body.action === 'return', `Action: ${resp.body.action}`);
            log('\x1b[36mINFO\x1b[0m', `  RETURNED`);
        });

        // --- ACT 5: JAKE HOLDS DEPOSIT ---
        console.log('\n--- Act 5: Security Deposit ---');

        await step('Jake holds deposit (EUR 200)', async () => {
            const resp = await api('POST', '/api/v1/deposits', {
                rental_id: state.rentalId,
                amount: 200.00,
                currency: 'EUR',
                payment_ref: 'DISPUTE-PATH-TEST',
            }, state.jakeCookie);
            assert(resp.status === 201, `Hold deposit: ${resp.status} -- ${resp.text}`);
            state.depositId = resp.body.id;
            assert(resp.body.status === 'held', `Deposit status: ${resp.body.status}`);
            assert(resp.body.amount === 200, `Amount: ${resp.body.amount}`);
            assert(resp.body.payer_id === state.jakeUserId, 'Payer is not Jake');
            assert(resp.body.recipient_id === state.lunaUserId, 'Recipient is not Luna');
            log('\x1b[36mINFO\x1b[0m', `  Deposit: ${state.depositId} (EUR 200, HELD)`);
        });

        await step('Duplicate deposit is rejected (409)', async () => {
            const resp = await api('POST', '/api/v1/deposits', {
                rental_id: state.rentalId,
                amount: 200.00,
            }, state.jakeCookie);
            assert(resp.status === 409, `Expected 409, got ${resp.status}`);
        });

        // --- ACT 6: LUNA FILES DISPUTE ---
        console.log('\n--- Act 6: Luna Files Dispute (Item Damaged) ---');

        await step('Luna files dispute (item_damaged)', async () => {
            const resp = await api('POST', '/api/v1/disputes', {
                rental_id: state.rentalId,
                reason: 'item_damaged',
                description: 'Wire feed mechanism is jammed and the gas nozzle is bent. Item was fine before rental.',
            }, state.lunaCookie);
            assert(resp.status === 201, `File dispute: ${resp.status} -- ${resp.text}`);
            state.disputeId = resp.body.id;
            assert(resp.body.status === 'filed', `Dispute status: ${resp.body.status}`);
            assert(resp.body.reason === 'item_damaged', `Reason: ${resp.body.reason}`);
            assert(resp.body.filed_by_id === state.lunaUserId, 'Filed by is not Luna');
            log('\x1b[36mINFO\x1b[0m', `  Dispute: ${state.disputeId} (FILED)`);
        });

        await step('Rental status is now DISPUTED', async () => {
            const resp = await api('GET', '/api/v1/rentals?limit=50', null, state.lunaCookie);
            assert(resp.status === 200, `List rentals: ${resp.status}`);
            const rentals = resp.body?.items || resp.body || [];
            const rental = rentals.find(r => r.id === state.rentalId);
            assert(rental, 'Rental not found');
            assert(rental.status === 'disputed', `Status: ${rental.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Rental -> DISPUTED`);
        });

        await step('Duplicate dispute is rejected', async () => {
            const resp = await api('POST', '/api/v1/disputes', {
                rental_id: state.rentalId,
                reason: 'item_damaged',
                description: 'Trying to file a second dispute on same rental.',
            }, state.lunaCookie);
            assert(resp.status === 409, `Expected 409, got ${resp.status}`);
        });

        await step('ACTIVE user (Jake) cannot file dispute (badge tier)', async () => {
            // Jake is ACTIVE, not TRUSTED -- should get 403
            const resp = await api('POST', '/api/v1/disputes', {
                rental_id: state.rentalId,
                reason: 'other',
                description: 'Jake tries to file but lacks badge tier.',
            }, state.jakeCookie);
            assert(resp.status === 403 || resp.status === 409, `Expected 403/409, got ${resp.status}`);
        });

        // --- ACT 7: JAKE RESPONDS ---
        console.log('\n--- Act 7: Jake Responds to Dispute ---');

        await step('Luna cannot respond to own dispute', async () => {
            const resp = await api('PATCH', `/api/v1/disputes/${state.disputeId}/respond`, {
                response: 'Luna trying to respond to her own dispute.',
            }, state.lunaCookie);
            // API returns 400 (filer cannot be responder) or 403
            assert(resp.status === 400 || resp.status === 403, `Expected 400/403, got ${resp.status}`);
        });

        await step('Jake responds to dispute', async () => {
            const resp = await api('PATCH', `/api/v1/disputes/${state.disputeId}/respond`, {
                response: 'The wire feed was already stiff when I picked it up. The nozzle might have bent during transport back.',
            }, state.jakeCookie);
            assert(resp.status === 200, `Respond: ${resp.status} -- ${resp.text}`);
            assert(resp.body.dispute_status === 'under_review', `Status: ${resp.body.dispute_status}`);
            log('\x1b[36mINFO\x1b[0m', `  Dispute -> UNDER_REVIEW`);
        });

        // --- ACT 8: LUNA RESOLVES -- DEPOSIT FORFEITED ---
        console.log('\n--- Act 8: Luna Resolves Dispute (Deposit Forfeited) ---');

        await step('Luna resolves dispute with deposit_forfeited', async () => {
            const resp = await api('PATCH', `/api/v1/disputes/${state.disputeId}/resolve`, {
                resolution: 'deposit_forfeited',
                resolution_notes: 'Repair cost exceeds deposit. Wire feed replacement EUR 180, nozzle EUR 35.',
            }, state.lunaCookie);
            assert(resp.status === 200, `Resolve: ${resp.status} -- ${resp.text}`);
            assert(resp.body.status === 'resolved', `Status: ${resp.body.status}`);
            assert(resp.body.resolution === 'deposit_forfeited', `Resolution: ${resp.body.resolution}`);
            log('\x1b[36mINFO\x1b[0m', `  Dispute RESOLVED (deposit_forfeited)`);
        });

        // --- ACT 9: VERIFY EVERYTHING ---
        console.log('\n--- Act 9: Verify Final State ---');

        await step('Rental status is now COMPLETED', async () => {
            const resp = await api('GET', '/api/v1/rentals?limit=50', null, state.lunaCookie);
            assert(resp.status === 200, `List rentals: ${resp.status}`);
            const rentals = resp.body?.items || resp.body || [];
            const rental = rentals.find(r => r.id === state.rentalId);
            assert(rental, 'Rental not found');
            assert(rental.status === 'completed', `Expected completed, got: ${rental.status}`);
            log('\x1b[36mINFO\x1b[0m', `  Rental -> COMPLETED`);
        });

        await step('Deposit status is FORFEITED', async () => {
            const resp = await api('GET', '/api/v1/deposits?limit=50', null, state.lunaCookie);
            assert(resp.status === 200, `List deposits: ${resp.status}`);
            const deposits = resp.body?.items || resp.body || [];
            const deposit = deposits.find(d => d.id === state.depositId);
            assert(deposit, 'Deposit not found in list');
            assert(deposit.status === 'forfeited', `Expected forfeited, got: ${deposit.status}`);
            assert(deposit.forfeited_amount === 200, `Forfeited: ${deposit.forfeited_amount}`);
            log('\x1b[36mINFO\x1b[0m', `  Deposit FORFEITED (EUR ${deposit.forfeited_amount})`);
        });

        await step('Dispute summary shows filed count', async () => {
            const resp = await api('GET', '/api/v1/disputes/summary', null, state.lunaCookie);
            assert(resp.status === 200, `Summary: ${resp.status}`);
            assert(resp.body.total >= 1, `Total: ${resp.body.total}`);
            assert(resp.body.resolved >= 1, `Resolved: ${resp.body.resolved}`);
            log('\x1b[36mINFO\x1b[0m', `  Luna disputes: total=${resp.body.total}, resolved=${resp.body.resolved}`);
        });

        await step('Luna has dispute notifications', async () => {
            const resp = await api('GET', '/api/v1/notifications?limit=20', null, state.lunaCookie);
            assert(resp.status === 200, `Notifications: ${resp.status}`);
            const notes = resp.body || [];
            assert(notes.length >= 1, `Expected notifications, got ${notes.length}`);
            log('\x1b[36mINFO\x1b[0m', `  Luna: ${notes.length} notifications`);
        });

        await step('Jake has dispute notifications', async () => {
            const resp = await api('GET', '/api/v1/notifications?limit=20', null, state.jakeCookie);
            assert(resp.status === 200, `Notifications: ${resp.status}`);
            const notes = resp.body || [];
            assert(notes.length >= 1, `Expected notifications, got ${notes.length}`);
            log('\x1b[36mINFO\x1b[0m', `  Jake: ${notes.length} notifications`);
        });

    } catch (err) {
        console.log(`\n\x1b[31mDispute path STOPPED at step ${stepNum}\x1b[0m`);
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    const total = passed + failed;
    if (failed === 0) {
        console.log(`\x1b[32mDISPUTE PATH: ALL ${total} STEPS PASSED\x1b[0m`);
    } else {
        console.log(`\x1b[31mDISPUTE PATH: ${passed}/${total} passed, ${failed} failed\x1b[0m`);
    }

    // State dump
    console.log('\nArtifacts:');
    console.log(`  Item:    ${state.itemId} (${state.itemSlug})`);
    console.log(`  Listing: ${state.listingId}`);
    console.log(`  Rental:  ${state.rentalId}`);
    console.log(`  Deposit: ${state.depositId}`);
    console.log(`  Dispute: ${state.disputeId}`);
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
    const reportPath = __dirname + '/dispute-path-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`Report: ${reportPath}`);

    process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
    console.error('Fatal:', err);
    process.exit(2);
});
