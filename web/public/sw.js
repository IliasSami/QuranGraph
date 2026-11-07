const CACHE_NAME = "qurangraph-cache-v2";
const STATIC_ASSETS = [
  "/",
  "/favicon.svg",
  "/manifest.json",
  "/surahs",
  "/search",
  "/graph",
  "/numbers",
  "/learn",
  "/sources",
  "/404"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Only handle GET requests
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);

  // CRITICAL FIX: Bypass Service Worker for streaming audio and Range requests.
  // Cache Storage cannot store 206 Partial Content responses and throws uncaught exceptions.
  if (
    url.pathname.endsWith(".mp3") ||
    url.origin.includes("everyayah.com") ||
    event.request.headers.has("range")
  ) {
    return;
  }

  // Google Fonts & Static Assets: Cache First, fallback to Network
  if (url.origin.includes("fonts.gstatic.com") || url.origin.includes("fonts.googleapis.com")) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return (
          cached ||
          fetch(event.request).then((response) => {
            if (response && response.status === 200) {
              const resClone = response.clone();
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, resClone);
              });
            }
            return response;
          })
        );
      })
    );
    return;
  }

  // Network First, fallback to Cache for HTML pages and app shell
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          const resClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, resClone);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cached) => {
          return cached || caches.match("/404");
        });
      })
  );
});
