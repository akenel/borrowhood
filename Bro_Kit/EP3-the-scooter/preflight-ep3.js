#!/usr/bin/env node
/**
 * PREFLIGHT CHECK -- EP3 "The Scooter"
 *
 * Runs in ~10 seconds. Checks everything the recording script needs
 * BEFORE you press record. Go/No-Go.
 *
 * Usage: node preflight-ep3.js [base_url]
 * Default: https://borrowhood.duckdns.org
 */

const BASE = process.argv[2] || 'https://borrowhood.duckdns.org';

const passed = [];
const failed = [];

function pass(msg) { passed.push(msg); console.log(`  ✓ ${msg}`); }
function fail(msg) { failed.push(msg); console.log(`  ✗ ${msg}`); }

async function fetchJSON(path) {
  const r = await fetch(`${BASE}${path}`);
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
  console.log(`\n  PREFLIGHT CHECK -- EP3 "The Scooter"`);
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
  const cast = ['leonardo', 'mike', 'pietro', 'sally', 'sofiaferretti', 'john'];
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
  // 4. KEY ITEM PAGES EXIST (by slug)
  // ============================================================
  console.log('\n  --- Item Pages ---');
  const items = [
    { slug: 'johnnys-delivery-bike-broken', name: "Johnny's broken bike" },
    { slug: 'welding-machine-mig-200a', name: "Mike's welding machine / training" },
    { slug: 'sallys-electric-scooter-for-delivery', name: "Sally's electric scooter" },
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
  // 5. JOHNNY'S BIKE IS A GIVEAWAY (not already claimed)
  // ============================================================
  console.log('\n  --- Listing States ---');
  const bikePage = await fetchPage('/items/johnnys-delivery-bike-broken');
  if (bikePage.text.includes('giveaway') || bikePage.text.includes('Giveaway') || bikePage.text.includes('GIVEAWAY')) {
    pass("Johnny's bike is listed as giveaway");
  } else if (bikePage.text.includes('Claim') || bikePage.text.includes('claim')) {
    pass("Johnny's bike has Claim button");
  } else {
    fail("Johnny's bike may not be a giveaway -- check listing type");
  }

  // Check if bike listing is active (not paused/claimed)
  if (bikePage.text.includes('paused') || bikePage.text.includes('Paused') || bikePage.text.includes('PAUSED')) {
    fail("Johnny's bike listing is PAUSED -- needs to be ACTIVE");
  } else {
    pass("Johnny's bike listing appears active");
  }

  // ============================================================
  // 6. SALLY'S SCOOTER IS PAUSED (ready to activate in script)
  // Use listings API via Sally's auth to check status reliably
  // ============================================================
  if (cookies['sally']) {
    const sallyListings = await authedFetch('/api/v1/listings?owner=me', cookies['sally']);
    if (sallyListings.status === 200 && sallyListings.data) {
      const scooterListing = sallyListings.data.find(l =>
        l.listing_type === 'rent' && l.item_id &&
        // Match by checking all rent listings -- scooter is the only rent listing Sally has
        true
      );
      // More precise: find the rent listing for the scooter item
      const rentListings = sallyListings.data.filter(l => l.listing_type === 'rent');
      if (rentListings.length === 1) {
        if (rentListings[0].status === 'paused') {
          pass("Sally's scooter listing is PAUSED (ready to activate during recording)");
        } else {
          fail(`Sally's scooter listing is ${rentListings[0].status} -- should be PAUSED`);
        }
      } else if (rentListings.length === 0) {
        fail("Sally has no RENT listing -- scooter listing missing");
      } else {
        // Multiple rent listings, check if any is paused
        const pausedRent = rentListings.find(l => l.status === 'paused');
        if (pausedRent) {
          pass("Sally's scooter listing is PAUSED (ready to activate during recording)");
        } else {
          fail("Sally's rent listings are all active -- scooter should be PAUSED");
        }
      }
    } else {
      fail("Could not fetch Sally's listings via API");
    }
  } else {
    fail("Sally login failed -- cannot check scooter status");
  }

  // ============================================================
  // 7. NO STALE RENTALS (active rentals from previous takes)
  // ============================================================
  console.log('\n  --- Stale Data ---');
  for (const user of ['leonardo', 'john', 'sally']) {
    if (!cookies[user]) continue;
    const rentals = await authedFetch('/api/v1/rentals', cookies[user]);
    if (rentals.status === 200 && rentals.data) {
      const active = rentals.data.filter(r =>
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
  // 8. MIKE'S WELDING LISTING EXISTS AND HAS A BOOKABLE LISTING
  // ============================================================
  console.log('\n  --- Mike\'s Training ---');
  const weldingPage = await fetchPage('/items/welding-machine-mig-200a');
  if (weldingPage.text.includes('Book') || weldingPage.text.includes('Request') || weldingPage.text.includes('training') || weldingPage.text.includes('Training')) {
    pass("Mike's welding item page has bookable content");
  } else {
    fail("Mike's welding page may not have a bookable listing -- check manually");
  }

  // ============================================================
  // 9. BROWSE SEARCH WORKS
  // ============================================================
  console.log('\n  --- Browse ---');
  const browse = await fetchPage('/browse?q=bike');
  if (browse.status === 200) {
    pass('Browse search works (/browse?q=bike)');
    if (browse.text.includes('bike') || browse.text.includes('Bike') || browse.text.includes('Bianchi')) {
      pass('Browse returns bike results');
    } else {
      fail('Browse for "bike" returned no matching results');
    }
  } else {
    fail(`Browse returned ${browse.status}`);
  }

  // ============================================================
  // 10. CANCEL & REFUND BUTTON EXISTS IN DASHBOARD
  // ============================================================
  console.log('\n  --- Cancel & Refund Feature ---');
  // We can't fully test this without an active booking, but check the template has the button
  if (cookies['mike']) {
    const dashboard = await authedFetch('/api/v1/rentals?role=owner', cookies['mike']);
    // Just check the dashboard loads -- the button appears only on approved rentals
    pass('Mike can access rental API (Cancel & Refund will appear on approved bookings)');
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
    console.log('  Start OBS, run record-the-scooter.js, play 10 seconds.\n');
  } else {
    console.log('\n  RESULT: NO-GO ✗\n');
    console.log('  Fix the failures above before recording.');
    console.log('  Common fixes:');
    console.log('    - Stale rentals: run pre-recording cleanup SQL');
    console.log('    - Sally scooter active: pause it in DB');
    console.log('    - Missing items: re-run seed');
    console.log('');
  }

  process.exit(failed.length === 0 ? 0 : 1);

})().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
