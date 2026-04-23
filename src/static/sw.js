/**
 * La Piazza Service Worker
 *
 * Strategy:
 * - Static assets (CSS, JS, fonts, images): cache-first
 * - HTML pages and API calls: network-first with offline fallback
 */

const CACHE_NAME = 'lp-v13';
const STATIC_ASSETS = [
  '/',
  '/browse',
  '/members',
  '/helpboard',
  '/static/images/icon-192.svg',
  '/static/images/icon-512.svg',
];

// Install: pre-cache shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: strategy based on request type
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip external requests
  if (url.origin !== location.origin) return;

  // API calls: network-only (no caching)
  if (url.pathname.startsWith('/api/')) return;

  // Static assets: cache-first
  if (url.pathname.startsWith('/static/') || url.pathname.match(/\.(svg|png|jpg|ico|woff2?)$/)) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request).then((resp) => {
        const clone = resp.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return resp;
      }))
    );
    return;
  }

  // HTML pages: network-first, fallback to cache, then offline page
  event.respondWith(
    fetch(event.request)
      .then((resp) => {
        const clone = resp.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return resp;
      })
      .catch(() => caches.match(event.request).then((cached) =>
        cached || caches.match('/') || new Response('Offline', { status: 503, statusText: 'Offline' })
      ))
  );
});
