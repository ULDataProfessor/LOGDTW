const STATIC_CACHE = 'logdtw2002-static-v1';
const RUNTIME_CACHE = 'logdtw2002-runtime-v1';
const ASSETS = [
  '/',
  '/css/style.css',
  '/css/terminal.css',
  '/js/game.js',
  '/offline.html',
  '/icons/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== RUNTIME_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const isAPI = url.pathname.startsWith('/api/');

  if (isAPI) {
    // Network-first for API
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request))
    );
  } else {
    // Cache-first for static assets
    event.respondWith(
      caches.match(request).then((cached) =>
        cached || fetch(request)
          .then((response) => {
            const copy = response.clone();
            caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy));
            return response;
          })
          .catch(() => {
            if (request.mode === 'navigate') {
              return caches.match('/offline.html');
            }
          })
      )
    );
  }
});


