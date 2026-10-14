// 냉장쿡 서비스 워커: 앱 파일을 저장해 두고 오프라인에서도 열리게 함.
// 앱을 고칠 때마다 아래 버전 숫자를 올리면 휴대폰에 새 버전이 반영됨.
const VERSION = "naengjangcook-v0.9";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// 인터넷이 되면 최신 파일, 안 되면 저장해 둔 파일
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(res => { const copy = res.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return res; })
      .catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});
