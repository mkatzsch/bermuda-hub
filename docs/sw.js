// Bermuda Hub service worker: keeps the last copy of the Hub for when there is no signal.
// Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
// Version: 1.0
// Last Updated: 2026-11-24
// Change Log
//   1.0 2026-11-24  First version. Network first, saved copy when offline. Depends on: nothing.
const KEEP = 'bermuda-hub-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== self.location.origin) return;
  e.respondWith(fetch(r).then(res => {
    if (res && res.ok) { const copy = res.clone(); caches.open(KEEP).then(c => c.put(r, copy)); }
    return res;
  }).catch(() => caches.match(r, {ignoreSearch: true}).then(hit => hit || caches.match('./'))));
});
