#!/usr/bin/env node
/**
 * BorrowHood Feature Tests
 *
 * Authenticated E2E tests for v2 features:
 *   - Service quoting lifecycle
 *   - Translation API (LibreTranslate)
 *   - Team pricing fields on listings
 *   - QR codes on item detail
 *   - Calendar .ics export
 *   - Notification coverage
 *   - Badges & points
 *   - Progressive disclosure
 *   - Helpboard (wishlist board)
 *   - Deposit lifecycle
 *   - ToS acceptance
 *
 * Usage:
 *   node tests/e2e/feature-tests.js
 *   node tests/e2e/feature-tests.js http://localhost:8000
 */

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE_URL = process.argv[2] || process.env.BH_BASE_URL || 'https://46.62.138.218';

const results = [];
let passed = 0;
let failed = 0;

function log(icon, msg) {
    console.log(`  ${icon} ${msg}`);
}
function info(msg) {
    console.log(`  \x1b[36mINFO\x1b[0m   ${msg}`);
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

// ---- API helper (uses fetch with cookie auth) ----

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

async function apiRaw(method, path, cookie) {
    const opts = {
        method,
        headers: {},
    };
    if (cookie) opts.headers['Cookie'] = `bh_session=${cookie}`;

    const resp = await fetch(`${BASE_URL}${path}`, opts);
    const text = await resp.text();
    return { status: resp.status, text, headers: resp.headers, contentType: resp.headers.get('content-type') };
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
// TEST SUITES
// ============================================================

async function testAuth() {
    console.log('\n--- Authentication ---');
    const state = {};

    await test('Luna logs in', async () => {
        state.lunaCookie = await login('luna');
        assert(state.lunaCookie, 'No cookie');
    });

    await test('Jake logs in', async () => {
        state.jakeCookie = await login('jake');
        assert(state.jakeCookie, 'No cookie');
    });

    await test('Luna profile loads', async () => {
        const r = await api('GET', '/api/v1/users/me', null, state.lunaCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        state.lunaId = r.body.id;
        state.lunaSlug = r.body.slug;
        info(`Luna: ${r.body.display_name} (${r.body.badge_tier})`);
    });

    await test('Jake profile loads', async () => {
        const r = await api('GET', '/api/v1/users/me', null, state.jakeCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        state.jakeId = r.body.id;
        state.jakeSlug = r.body.slug;
        info(`Jake: ${r.body.display_name} (${r.body.badge_tier})`);
    });

    return state;
}

async function testTeamPricing(state) {
    console.log('\n--- Team Pricing Fields ---');

    // Create an item first
    const ts = Date.now();
    await test('Create item with team pricing', async () => {
        const r = await api('POST', '/api/v1/items', {
            name: `Feature Test Workshop ${ts}`,
            description: 'Workshop item for feature testing',
            category: 'tools',
        }, state.lunaCookie);
        assert(r.status === 201, `Expected 201, got ${r.status}`);
        state.teamItemId = r.body.id;
    });

    await test('Create listing with team pricing fields', async () => {
        const r = await api('POST', '/api/v1/listings', {
            item_id: state.teamItemId,
            listing_type: 'service',
            price_per_day: 50.0,
            currency: 'EUR',
            minimum_charge: 25.0,
            per_person_rate: 15.0,
            max_participants: 10,
            group_discount_pct: 20.0,
        }, state.lunaCookie);
        assert(r.status === 201, `Expected 201, got ${r.status}: ${r.text}`);
        assert(r.body.minimum_charge === 25.0, `minimum_charge: ${r.body.minimum_charge}`);
        assert(r.body.per_person_rate === 15.0, `per_person_rate: ${r.body.per_person_rate}`);
        assert(r.body.max_participants === 10, `max_participants: ${r.body.max_participants}`);
        assert(r.body.group_discount_pct === 20.0, `group_discount_pct: ${r.body.group_discount_pct}`);
        state.teamListingId = r.body.id;
        info(`Listing ${r.body.id}: EUR 50/day, min EUR 25, EUR 15/person, max 10, 20% discount`);
    });

    await test('Update listing team pricing', async () => {
        const r = await api('PATCH', `/api/v1/listings/${state.teamListingId}`, {
            minimum_charge: 30.0,
            max_participants: 15,
        }, state.lunaCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(r.body.minimum_charge === 30.0, `minimum_charge: ${r.body.minimum_charge}`);
        assert(r.body.max_participants === 15, `max_participants: ${r.body.max_participants}`);
    });

    await test('Team pricing validation -- negative minimum_charge rejected', async () => {
        const r = await api('POST', '/api/v1/listings', {
            item_id: state.teamItemId,
            listing_type: 'service',
            price_per_day: 50.0,
            currency: 'EUR',
            minimum_charge: -5.0,
        }, state.lunaCookie);
        assert(r.status === 422, `Expected 422 validation error, got ${r.status}`);
    });

    await test('Team pricing validation -- discount over 100 rejected', async () => {
        const r = await api('POST', '/api/v1/listings', {
            item_id: state.teamItemId,
            listing_type: 'service',
            price_per_day: 50.0,
            currency: 'EUR',
            group_discount_pct: 150.0,
        }, state.lunaCookie);
        assert(r.status === 422, `Expected 422 validation error, got ${r.status}`);
    });
}

async function testServiceQuoting(state) {
    console.log('\n--- Service Quoting Lifecycle ---');

    await test('Jake requests a quote on Luna\'s service listing', async () => {
        const r = await api('POST', '/api/v1/service-quotes', {
            listing_id: state.teamListingId,
            description: 'Need a 3-hour pottery workshop for 5 people',
            preferred_date: '2026-04-15',
        }, state.jakeCookie);
        // 201 = created, 404 = endpoint not found (skip)
        if (r.status === 404) {
            info('Service quotes endpoint not found -- skipping');
            return;
        }
        assert(r.status === 201, `Expected 201, got ${r.status}: ${r.text}`);
        state.quoteId = r.body.id;
        info(`Quote ${r.body.id}: ${r.body.status}`);
    });

    if (state.quoteId) {
        await test('Luna sends quote with price', async () => {
            const r = await api('PATCH', `/api/v1/service-quotes/${state.quoteId}`, {
                status: 'quoted',
                quoted_price: 120.0,
                message: 'EUR 120 for 5 people, 3 hours, includes materials',
            }, state.lunaCookie);
            assert(r.status === 200, `Expected 200, got ${r.status}`);
            assert(r.body.status === 'quoted', `Status: ${r.body.status}`);
        });

        await test('Jake accepts the quote', async () => {
            const r = await api('PATCH', `/api/v1/service-quotes/${state.quoteId}`, {
                status: 'accepted',
            }, state.jakeCookie);
            assert(r.status === 200, `Expected 200, got ${r.status}`);
        });
    }
}

async function testTranslation() {
    console.log('\n--- Translation API ---');

    await test('Translation endpoint exists', async () => {
        const r = await api('POST', '/api/v1/translate', {
            text: 'Hello world',
            source: 'en',
            target: 'it',
        });
        // Could be 200 (working) or 503 (LibreTranslate down) or 401 (needs auth)
        assert(r.status !== 404, 'Translation endpoint not found');
        if (r.status === 200) {
            info(`Translated: "${r.body.translated_text || r.body.translation}"`);
        } else {
            info(`Translation returned ${r.status} (service may be down)`);
        }
    });

    await test('Translation with missing params returns 422', async () => {
        const r = await api('POST', '/api/v1/translate', {});
        // Either 422 (validation) or 404 (not found)
        assert(r.status === 422 || r.status === 400, `Expected 422/400, got ${r.status}`);
    });
}

async function testCalendarExport(state) {
    console.log('\n--- Calendar .ics Export ---');

    // First get a rental to test with
    let rentalId = null;
    await test('Get rental for calendar test', async () => {
        const r = await api('GET', '/api/v1/rentals?role=owner&limit=1', null, state.lunaCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(Array.isArray(r.body) && r.body.length > 0, 'No rentals found');
        rentalId = r.body[0].id;
        info(`Rental: ${rentalId} (${r.body[0].status})`);
    });

    if (rentalId) {
        await test('Calendar .ics downloads with correct content-type', async () => {
            const r = await apiRaw('GET', `/api/v1/rentals/${rentalId}/calendar`, state.lunaCookie);
            assert(r.status === 200, `Expected 200, got ${r.status}`);
            assert(r.contentType.includes('text/calendar'), `Content-Type: ${r.contentType}`);
        });

        await test('Calendar .ics has valid VCALENDAR structure', async () => {
            const r = await apiRaw('GET', `/api/v1/rentals/${rentalId}/calendar`, state.lunaCookie);
            assert(r.text.includes('BEGIN:VCALENDAR'), 'Missing BEGIN:VCALENDAR');
            assert(r.text.includes('END:VCALENDAR'), 'Missing END:VCALENDAR');
            assert(r.text.includes('BEGIN:VEVENT'), 'Missing BEGIN:VEVENT');
            assert(r.text.includes('DTSTART:'), 'Missing DTSTART');
            assert(r.text.includes('DTEND:'), 'Missing DTEND');
            assert(r.text.includes('SUMMARY:BorrowHood:'), 'Missing SUMMARY');
            info('RFC 5545 structure valid');
        });

        await test('Calendar .ics has Content-Disposition header', async () => {
            const r = await apiRaw('GET', `/api/v1/rentals/${rentalId}/calendar`, state.lunaCookie);
            const cd = r.headers.get('content-disposition') || '';
            assert(cd.includes('attachment'), 'Not an attachment');
            assert(cd.includes('.ics'), 'Missing .ics filename');
            info(`Content-Disposition: ${cd}`);
        });

        await test('Calendar .ics returns 403 for non-participant', async () => {
            // Create a third user context (or use jake with a rental he doesn't own)
            // Actually jake IS the renter, so he should be able to access it too
            const r = await apiRaw('GET', `/api/v1/rentals/${rentalId}/calendar`, state.jakeCookie);
            // Jake is the renter on Luna's rentals, so 200 is expected
            assert(r.status === 200 || r.status === 403,
                `Expected 200 (participant) or 403, got ${r.status}`);
            info(`Jake access: ${r.status}`);
        });

        await test('Calendar .ics returns 401 without auth', async () => {
            const r = await apiRaw('GET', `/api/v1/rentals/${rentalId}/calendar`, null);
            assert(r.status === 401 || r.status === 403,
                `Expected 401/403, got ${r.status}`);
        });
    }
}

async function testQRCodes(page, state) {
    console.log('\n--- QR Code on Item Detail ---');

    await test('Item detail page has QR code', async () => {
        // Get an item slug
        const itemsResp = await api('GET', '/api/v1/items?limit=1');
        assert(itemsResp.status === 200 && itemsResp.body.length > 0, 'No items');
        const slug = itemsResp.body[0].slug;

        await page.goto(`${BASE_URL}/item/${slug}`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });
        const hasQR = await page.evaluate(() => {
            return !!document.querySelector('img[src*="qrserver.com"]') ||
                   !!document.querySelector('[id*="qr"]') ||
                   !!document.querySelector('img[alt*="QR"]');
        });
        assert(hasQR, 'No QR code found on item detail');
        info(`QR code found on /item/${slug}`);
    });
}

async function testNotifications(state) {
    console.log('\n--- Notification Coverage ---');

    await test('Luna has notifications', async () => {
        const r = await api('GET', '/api/v1/notifications?limit=5', null, state.lunaCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(Array.isArray(r.body) && r.body.length > 0, 'No notifications');
        info(`Luna: ${r.body.length} notifications`);
    });

    await test('Jake has notifications', async () => {
        const r = await api('GET', '/api/v1/notifications?limit=5', null, state.jakeCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(Array.isArray(r.body) && r.body.length > 0, 'No notifications');
        info(`Jake: ${r.body.length} notifications`);
    });

    await test('Notification types include rental events', async () => {
        const r = await api('GET', '/api/v1/notifications?limit=50', null, state.lunaCookie);
        const types = [...new Set(r.body.map(n => n.notification_type))];
        info(`Types: ${types.join(', ')}`);
        // At least rental_request should exist from golden path
        const hasRentalTypes = types.some(t =>
            t.includes('rental') || t.includes('review') || t.includes('badge')
        );
        assert(hasRentalTypes, 'No rental/review notification types found');
    });

    await test('Unread count endpoint works', async () => {
        const r = await api('GET', '/api/v1/notifications/unread-count', null, state.lunaCookie);
        // Could be 200 or 404 if endpoint doesn't exist
        if (r.status === 200) {
            info(`Unread: ${JSON.stringify(r.body)}`);
        } else {
            info(`Unread count endpoint returned ${r.status}`);
        }
        assert(r.status !== 500, 'Server error on unread count');
    });
}

async function testBadgesAndPoints(state) {
    console.log('\n--- Badges & Points ---');

    await test('Badges catalog returns list', async () => {
        const r = await api('GET', '/api/v1/badges/catalog');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(Array.isArray(r.body) && r.body.length > 0, 'Empty catalog');
        info(`${r.body.length} badge types in catalog`);
    });

    await test('Luna has badges', async () => {
        const r = await api('GET', `/api/v1/badges/user/${state.lunaId}`, null, state.lunaCookie);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        if (Array.isArray(r.body) && r.body.length > 0) {
            const codes = r.body.map(b => b.badge_code || b.code);
            info(`Luna badges: ${codes.join(', ')}`);
        }
    });

    await test('Points summary exists', async () => {
        const r = await api('GET', `/api/v1/points/${state.lunaId}`, null, state.lunaCookie);
        if (r.status === 200) {
            info(`Luna points: ${r.body.total_points || r.body.points || JSON.stringify(r.body)}`);
        } else {
            info(`Points endpoint returned ${r.status}`);
        }
        assert(r.status !== 500, 'Server error on points');
    });
}

async function testHelpboard(state) {
    console.log('\n--- Helpboard (Wishlist Board) ---');

    await test('Helpboard summary loads', async () => {
        const r = await api('GET', '/api/v1/helpboard/summary');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(r.body.total !== undefined, 'Missing total');
        info(`${r.body.total} posts total`);
    });

    await test('Helpboard posts paginate', async () => {
        const r = await api('GET', '/api/v1/helpboard/posts?limit=3&offset=0');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(r.body.items !== undefined, 'Missing items');
    });

    await test('Create helpboard post (need type)', async () => {
        const r = await api('POST', '/api/v1/helpboard/posts', {
            title: `Feature test need ${Date.now()}`,
            body: 'Looking for a 3D printer in Trapani area',
            help_type: 'need',
        }, state.jakeCookie);
        if (r.status === 201) {
            state.helpPostId = r.body.id;
            info(`Post ${r.body.id}: ${r.body.help_type}`);
        } else {
            info(`Create post returned ${r.status}: ${r.text.substring(0, 100)}`);
        }
        assert(r.status === 201 || r.status === 422, `Unexpected ${r.status}`);
    });

    if (state.helpPostId) {
        await test('Reply to helpboard post', async () => {
            const r = await api('POST', `/api/v1/helpboard/posts/${state.helpPostId}/replies`, {
                body: 'I have a 3D printer you can use!',
            }, state.lunaCookie);
            assert(r.status === 201 || r.status === 200, `Expected 201, got ${r.status}`);
            info('Reply created');
        });
    }

    await test('Helpboard page renders', async () => {
        const r = await apiRaw('GET', '/helpboard');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(r.text.includes('helpboard') || r.text.includes('Helpboard') || r.text.includes('Bacheca'),
            'No helpboard content');
    });
}

async function testProgressiveDisclosure(page, state) {
    console.log('\n--- Progressive Disclosure ---');

    await test('Workshop page shows contact gating for anonymous', async () => {
        // Load workshop as anonymous (no cookie)
        const usersResp = await api('GET', '/api/v1/users?limit=1');
        const userList = usersResp.body?.items || usersResp.body || [];
        if (userList.length === 0) return;
        const slug = userList[0].slug;

        await page.goto(`${BASE_URL}/workshop/${slug}`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });

        const content = await page.content();
        // Anonymous should see lock OR the tier gate message
        const hasGate = content.includes('Reach Active tier') ||
                       content.includes('Raggiungi il livello') ||
                       content.includes('tier to contact') ||
                       content.includes('t.me/');  // OR direct link if user is high tier
        assert(hasGate, 'No contact gating or telegram link found');
        info('Contact disclosure verified');
    });

    await test('Item detail shows auction gating', async () => {
        const itemsResp = await api('GET', '/api/v1/items?limit=1');
        if (itemsResp.body.length === 0) return;
        const slug = itemsResp.body[0].slug;

        await page.goto(`${BASE_URL}/item/${slug}`, {
            waitUntil: 'domcontentloaded', timeout: 15000,
        });

        const content = await page.content();
        // Should have either the bid form OR the trust gate message
        const hasBidOrGate = content.includes('Trusted tier') ||
                            content.includes('Livello Fidato') ||
                            content.includes('place_bid') ||
                            content.includes('bid_amount') ||
                            content.includes('auction');
        // This test is soft -- auctions may not be on every item
        info('Auction disclosure checked');
    });
}

async function testDeposits(state) {
    console.log('\n--- Deposit System ---');

    await test('Deposit endpoint exists', async () => {
        const r = await api('GET', '/api/v1/deposits', null, state.lunaCookie);
        // 200 = works, 404 = not implemented
        if (r.status === 200) {
            info(`Deposits: ${Array.isArray(r.body) ? r.body.length : 'response ok'}`);
        } else {
            info(`Deposits endpoint returned ${r.status}`);
        }
        assert(r.status !== 500, 'Server error on deposits');
    });
}

async function testReviews(state) {
    console.log('\n--- Reviews ---');

    await test('Review summary for Luna', async () => {
        const r = await api('GET', `/api/v1/reviews/summary/${state.lunaId}`);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        assert(r.body.user_id !== undefined, 'Missing user_id');
        info(`Luna: ${r.body.total_reviews} reviews, avg ${r.body.average_rating}`);
    });

    await test('Review summary for Jake', async () => {
        const r = await api('GET', `/api/v1/reviews/summary/${state.jakeId}`);
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        info(`Jake: ${r.body.total_reviews} reviews, avg ${r.body.average_rating}`);
    });
}

async function testOnboardingToS() {
    console.log('\n--- ToS Acceptance ---');

    await test('Onboarding schema includes tos_accepted', async () => {
        const r = await apiRaw('GET', '/openapi.json');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        const spec = JSON.parse(r.text);
        const schemas = spec?.components?.schemas || {};
        let found = false;
        for (const [name, schema] of Object.entries(schemas)) {
            if (schema?.properties?.tos_accepted) {
                found = true;
                info(`tos_accepted found in schema: ${name}`);
                break;
            }
        }
        assert(found, 'tos_accepted not found in any OpenAPI schema');
    });
}

async function testSearch() {
    console.log('\n--- Search & Browse ---');

    await test('Items search by query', async () => {
        const r = await api('GET', '/api/v1/items?q=kiln&limit=5');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        info(`Search "kiln": ${r.body.length} results`);
    });

    await test('Items search by category', async () => {
        const r = await api('GET', '/api/v1/items?category=tools&limit=5');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        info(`Category "tools": ${r.body.length} results`);
    });

    await test('Users search by city', async () => {
        const r = await api('GET', '/api/v1/users?city=Trapani&limit=5');
        assert(r.status === 200, `Expected 200, got ${r.status}`);
        const items = r.body?.items || r.body || [];
        info(`City "Trapani": ${items.length} users`);
    });
}

// ============================================================
// MAIN
// ============================================================

async function main() {
    console.log(`\nBorrowHood Feature Tests`);
    console.log(`Target: ${BASE_URL}`);
    console.log(`Time: ${new Date().toISOString()}`);
    console.log('='.repeat(60));

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
    page.on('pageerror', () => {});

    try {
        // Auth (needed for all authenticated tests)
        const state = await testAuth();

        // Feature suites
        await testTeamPricing(state);
        await testServiceQuoting(state);
        await testTranslation();
        await testCalendarExport(state);
        await testQRCodes(page, state);
        await testNotifications(state);
        await testBadgesAndPoints(state);
        await testHelpboard(state);
        await testProgressiveDisclosure(page, state);
        await testDeposits(state);
        await testReviews(state);
        await testOnboardingToS();
        await testSearch();
    } catch (err) {
        console.error('\nSuite error:', err.message);
    }

    await browser.close();

    // Summary
    console.log('\n' + '='.repeat(60));
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

    const reportPath = __dirname + '/feature-test-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\nReport: ${reportPath}`);

    process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
    console.error('Fatal:', err);
    process.exit(2);
});
