#!/usr/bin/env python3
"""sw.js(폰에 게임을 저장하는 서비스 워커)를 다시 만든다.

게임 파일을 고치거나 추가한 뒤, 사이트에 올리기 전에 한 번 실행하세요.
    python tools/make-sw.py
파일 내용이 바뀌면 버전 이름이 바뀌어서 폰이 새 버전을 내려받아요.
"""
import glob, os, json, hashlib
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..") + os.sep
files = ["./"] + sorted(os.path.basename(f) for f in glob.glob(R + "*.html"))
files += ["manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "favicon-48.png", "fonts/fonts.css"]
files += ["fonts/" + os.path.basename(f) for f in sorted(glob.glob(R + "fonts/*.woff2"))]
files += ["data/" + os.path.basename(f) for f in sorted(glob.glob(R + "data/*"))]
h = hashlib.md5()
TEXT = (".html", ".css", ".webmanifest", ".js", ".txt", ".json")   # Windows가 줄 끝 표시(CRLF)를 바꿔도 같은 버전이 되도록 맞춘다
for f in files:
    if f != "./":
        data = open(R + f, "rb").read()
        if f.endswith(TEXT):
            data = data.replace(b"\r\n", b"\n")
        h.update(data)
ver = "family-games-" + h.hexdigest()[:10]
js = '''// 오프라인에서도 게임이 실행되도록 모든 파일을 폰에 저장해 두는 서비스 워커예요. (자동 생성 파일)
const VERSION = "%s";
const PRECACHE = %s;

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(VERSION);
    await Promise.all(PRECACHE.map(u => c.add(new Request(u, { cache: "reload" })).catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== VERSION) await caches.delete(k);
    await self.clients.claim();
  })());
});

// 저장된 파일을 먼저 보여 주고, 인터넷이 되면 뒤에서 새 버전으로 바꿔 둔다
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  e.respondWith((async () => {
    const c = await caches.open(VERSION);
    const hit = await c.match(req, { ignoreSearch: true });
    const net = fetch(req).then(r => { if (r && r.ok) c.put(req, r.clone()); return r; }).catch(() => null);
    if (hit) { e.waitUntil(net); return hit; }
    const r = await net;
    if (r) return r;
    if (req.mode === "navigate") return (await c.match("index.html")) || Response.error();
    return Response.error();
  })());
});

self.addEventListener("message", e => {
  if (e.data && e.data.type === "status" && e.ports[0]) {
    e.waitUntil((async () => {
      const c = await caches.open(VERSION);
      e.ports[0].postMessage({ count: (await c.keys()).length, total: PRECACHE.length, version: VERSION });
    })());
  }
});
''' % (ver, json.dumps(files, ensure_ascii=False))
open(R + "sw.js", "w", encoding="utf-8", newline="\n").write(js)
print("sw.js 갱신:", ver, "| 저장 대상 파일", len(files), "개")
