#!/usr/bin/env node
/**
 * PREFLIGHT CHECK -- EP4 "The Review"
 *
 * Runs in ~15 seconds. Checks everything the recording script needs
 * BEFORE you press record. Go/No-Go.
 *
 * Usage: node preflight-ep4.js [base_url]
 * Default: https://borrowhood.duckdns.org
 */

const BASE = process.argv[2] || 'https://borrowhood.duckdns.org';

const passed = [];
const failed = [];

function pass(msg) { passed.push(msg); console.log(`  ✓ ${msg}`); }
function fail(msg) { failed.push(msg); console.log(`  ✗ ${msg}`); }

async function fetchJSON(path, opts = {}) {
  const r = await fetch(`${BASE}${path}`, opts);
  return { status: r.status, data: await r.json().catch(() => null) };
}

async function fetchPage(path) {
  const r = await fetch(`${BASE}${path}`);
  return { status: r.status, text: await r.text() };
}

async function demoLogin(username) {
  const r = await fetch(`${BASE}/api/v1/demo/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });
  const data = await r.json().catch(() => null);
  const cookie = r.headers.get('set-cookie') || '';
  return { status: r.status, data, cookie };
}

async function authedFetch(path, cookie) {
  const r = await fetch(`${BASE}${path}`, {
    headers: { 'Cookie': cookie },
  });
  return { status: r.status, data: await r.json().catch(() => null) };
}

(async () => {
  console.log(`\n  PREFLIGHT CHECK -- EP4 "The Review"`);
  console.log(`  Target: ${BASE}`);
  console.log(`  ${new Date().toISOString()}\n`);

  // ============================================================
  // 1. SERVER IS UP
  // ============================================================
  console.log('  --- Server ---');
  try {
    const home = await fetchPage('/');
    if (home.status === 200) pass('Server is up');
    else fail(`Server returned ${home.status}`);
  } catch (e) {
    fail(`Server unreachable: ${e.message}`);
    console.log('\n  RESULT: NO-GO (server down)\n');
    process.exit(1);
  }

  // ============================================================
  // 2. DEMO LOGIN PAGE
  // ============================================================
  console.log('\n  --- Demo Login ---');
  const demoPage = await fetchPage('/demo-login');
  if (demoPage.status === 200) pass('Demo login page loads');
  else fail(`Demo login page returned ${demoPage.status}`);

  // ============================================================
  // 3. ALL CAST MEMBERS CAN LOG IN
  // ============================================================
  console.log('\n  --- Cast Logins ---');
  const cast = ['john', 'leonardo', 'mike', 'sofiaferretti', 'sally', 'pietro'];
  const cookies = {};

  for (const user of cast) {
    const login = await demoLogin(user);
    if (login.status === 200 && login.cookie) {
      pass(`@${user} can log in`);
      cookies[user] = login.cookie;
    } else {
      fail(`@${user} login failed (status ${login.status})`);
    }
  }

  // ============================================================
  // 4. KEY ITEM PAGES EXIST
  // ============================================================
  console.log('\n  --- Item Pages ---');
  const items = [
    { slug: 'pressure-washer-karcher-k5', name: "Johnny's pressure washer" },
    { slug: 'cookie-jar-refill-ooak-cookies-750g', name: "Sofia's cookies" },
    { slug: 'welding-machine-mig-200a', name: "Mike's welding machine" },
  ];

  for (const item of items) {
    const page = await fetchPage(`/items/${item.slug}`);
    if (page.status === 200) {
      pass(`${item.name} page loads (/items/${item.slug})`);
    } else {
      fail(`${item.name} page returned ${page.status} (/items/${item.slug})`);
    }
  }

  // ============================================================
  // 5. PRESSURE WASHER IS LISTED AND ACTIVE
  // ============================================================
  console.log('\n  --- Listing States ---');
  const pwPage = await fetchPage('/items/pressure-washer-karcher-k5');
  if (pwPage.text.includes('PAUSED') || pwPage.text.includes('paused')) {
    fail("Pressure washer listing is PAUSED -- needs to be ACTIVE");
  } else {
    pass("Pressure washer listing appears active");
  }

  // ============================================================
  // 6. HELP BOARD HAS COMMUNITY POSTS (6 seeded, Johnny creates his live)
  // ============================================================
  console.log('\n  --- Help Board ---');
  const helpPage = await fetchPage('/helpboard');
  if (helpPage.status === 200) {
    pass('Help Board page loads');
  } else {
    fail(`Help Board page returned ${helpPage.status}`);
  }

  const helpSummary = await fetchJSON('/api/v1/helpboard/summary');
  if (helpSummary.status === 200 && helpSummary.data) {
    if (helpSummary.data.total >= 5) {
      pass(`Help Board has ${helpSummary.data.total} community posts (seeded)`);
    } else {
      fail(`Help Board has ${helpSummary.data.total} posts -- should be 6+ (run cleanup SQL)`);
    }
  } else {
    fail('Could not fetch Help Board summary');
  }

  // ============================================================
  // 7. REVIEWS ARE CLEAN (0 reviews -- created live on camera)
  // ============================================================
  console.log('\n  --- Reviews ---');
  // Check Sofia's cookies have no reviews
  const cookieReviews = await fetchJSON('/api/v1/reviews?reviewee_slug=sofias-kitchen');
  if (cookieReviews.status === 200) {
    const count = Array.isArray(cookieReviews.data) ? cookieReviews.data.length :
                  cookieReviews.data?.items?.length ?? 0;
    if (count === 0) {
      pass('Sofia has 0 reviews (clean for recording)');
    } else {
      fail(`Sofia has ${count} review(s) -- should be 0 (run cleanup SQL)`);
    }
  }

  // ============================================================
  // 8. COMPLETED COOKIE RENTALS EXIST (for review creation)
  // ============================================================
  console.log('\n  --- Seed Data ---');

  // Check Johnny's completed cookie deliveries via Sofia's dashboard
  if (cookies['sofiaferretti']) {
    const sofiaRentals = await authedFetch('/api/v1/rentals?role=owner', cookies['sofiaferretti']);
    if (sofiaRentals.status === 200 && sofiaRentals.data) {
      const completed = Array.isArray(sofiaRentals.data) ?
        sofiaRentals.data.filter(r => r.status?.toLowerCase() === 'completed') :
        sofiaRentals.data.items?.filter(r => r.status?.toLowerCase() === 'completed') ?? [];
      if (completed.length >= 4) {
        pass(`Sofia has ${completed.length} completed cookie orders (need 4+ for Johnny bike deliveries)`);
      } else {
        fail(`Sofia has only ${completed.length} completed orders -- need 4+ (run cleanup SQL)`);
      }
    }
  }

  // Check Leo's completed cookie order (the drone one)
  if (cookies['leonardo']) {
    const leoRentals = await authedFetch('/api/v1/rentals', cookies['leonardo']);
    if (leoRentals.status === 200 && leoRentals.data) {
      const leoCompleted = Array.isArray(leoRentals.data) ?
        leoRentals.data.filter(r => r.status?.toLowerCase() === 'completed') :
        leoRentals.data.items?.filter(r => r.status?.toLowerCase() === 'completed') ?? [];
      if (leoCompleted.length >= 1) {
        pass(`Leo has ${leoCompleted.length} completed rental(s) (need 1+ for 3-star review)`);
      } else {
        fail('Leo has 0 completed rentals -- need at least 1 drone cookie order (run cleanup SQL)');
      }
    }
  }

  // ============================================================
  // 9. NO STALE RENTALS
  // ============================================================
  console.log('\n  --- Stale Data ---');
  for (const user of ['john', 'leonardo', 'sofiaferretti']) {
    if (!cookies[user]) continue;
    const rentals = await authedFetch('/api/v1/rentals', cookies[user]);
    if (rentals.status === 200 && rentals.data) {
      const data = Array.isArray(rentals.data) ? rentals.data : rentals.data.items ?? [];
      const active = data.filter(r =>
        !['completed', 'declined', 'cancelled'].includes(r.status?.toLowerCase())
      );
      if (active.length === 0) {
        pass(`@${user} has no stale rentals`);
      } else {
        fail(`@${user} has ${active.length} active rental(s) -- run cleanup SQL`);
      }
    }
  }

  // ============================================================
  // 10. MIKE'S WORKSHOP EXISTS
  // ============================================================
  console.log('\n  --- Workshops ---');
  const mikeWorkshop = await fetchPage('/workshop/mikes-garage');
  if (mikeWorkshop.status === 200) {
    pass("Mike's Garage workshop page loads");
  } else {
    fail(`Mike's workshop returned ${mikeWorkshop.status}`);
  }

  const leoWorkshop = await fetchPage('/workshop/leonardos-bottega');
  if (leoWorkshop.status === 200) {
    pass("Leonardo's Bottega workshop page loads");
  } else {
    fail(`Leo's workshop returned ${leoWorkshop.status}`);
  }

  // ============================================================
  // 11. GEORGE EXISTS (breadcrumb cameo)
  // ============================================================
  console.log('\n  --- Cameo ---');
  const george = await fetchPage('/members');
  if (george.status === 200 && george.text.includes('George')) {
    pass('George appears in members page (breadcrumb cameo ready)');
  } else {
    pass('Members page loads (George cameo optional)');
  }

  // ============================================================
  // 12. REVIEW API WORKS
  // ============================================================
  console.log('\n  --- Review API ---');
  if (cookies['sofiaferretti']) {
    const reviewEndpoint = await authedFetch('/api/v1/reviews?limit=1', cookies['sofiaferretti']);
    if (reviewEndpoint.status === 200) {
      pass('Review API endpoint responds');
    } else {
      fail(`Review API returned ${reviewEndpoint.status}`);
    }
  }

  // ============================================================
  // 13. AI DRAFT ENDPOINT EXISTS (Help Board)
  // ============================================================
  console.log('\n  --- AI Draft ---');
  if (cookies['john']) {
    const draftCheck = await fetch(`${BASE}/api/v1/helpboard/draft`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies['john'],
      },
      body: JSON.stringify({ prompt: 'test' }),
    });
    // 200 or 422 (validation) means endpoint exists; 404 means missing
    if (draftCheck.status !== 404) {
      pass(`AI Draft endpoint exists (status ${draftCheck.status})`);
    } else {
      fail('AI Draft endpoint returns 404 -- feature may not be deployed');
    }
  }

  // ============================================================
  // RESULT
  // ============================================================
  console.log('\n  ============================');
  console.log(`  PASSED: ${passed.length}`);
  console.log(`  FAILED: ${failed.length}`);
  console.log('  ============================');

  if (failed.length === 0) {
    console.log('\n  RESULT: GO ✓\n');
    console.log('  All checks passed. Ready to record.');
    console.log('  Start OBS, run record-the-review.js, play 10 seconds.\n');
  } else {
    console.log('\n  RESULT: NO-GO ✗\n');
    console.log('  Fix the failures above before recording.');
    console.log('  Common fixes:');
    console.log('    - Stale data: run pre-recording-cleanup.sql');
    console.log('    - Missing items: re-run seed');
    console.log('    - Reviews exist: cleanup SQL deletes them');
    console.log('    - Help posts exist: cleanup SQL deletes them');
    console.log('');
  }

  process.exit(failed.length === 0 ? 0 : 1);

})().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
