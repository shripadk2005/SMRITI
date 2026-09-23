/**
 * MINDCARE NER - Service Worker for Offline PWA Capabilities
 * Network-First for dynamic HTML & API, Cache-First for static assets
 */

const CACHE_NAME = 'mindcare-ner-v2';
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/games.js',
  '/static/js/voice.js',
  '/static/js/translations.js',
  '/static/js/offline_sync.js',
  '/static/js/dashboard.js',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('📦 Pre-caching static MindCare assets');
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('Some assets could not be pre-cached:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('🧹 Purging outdated cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Ignore non-GET requests
  if (req.method !== 'GET') return;

  // API calls: Network-first with offline JSON fallback
  if (req.url.includes('/api/')) {
    event.respondWith(
      fetch(req).catch(() => {
        return new Response(
          JSON.stringify({ offline: true, message: 'Currently offline. Actions queued locally.' }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      })
    );
    return;
  }

  // Navigation requests (HTML pages): Network-First, fallback to cache
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return networkResponse;
        })
        .catch(() => {
          // If offline, check cache for requested page, then cached root
          return caches.match(req).then((cached) => cached || caches.match('/'));
        })
    );
    return;
  }

  // Static assets (CSS, JS, images, fonts): Stale-while-revalidate / Cache-first
  event.respondWith(
    caches.match(req).then((cached) => {
      const fetchPromise = fetch(req)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const copy = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return networkResponse;
        })
        .catch(() => cached);

      return cached || fetchPromise;
    })
  );
});
