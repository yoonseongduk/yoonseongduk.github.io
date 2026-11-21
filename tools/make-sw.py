#!/usr/bin/env python3
"""sw.js(폰에 게임을 저장하는 서비스 워커)를 다시 만든다.

게임 파일을 고치거나 추가한 뒤, 사이트에 올리기 전에 한 번 실행하세요.
    python tools/make-sw.py
파일 내용이 바뀌면 버전 이름이 바뀌어서 폰이 새 버전을 내려받아요.
"""
import glob, os, json, hashlib, re, datetime
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..") + os.sep
files = ["./"] + sorted(os.path.basename(f) for f in glob.glob(R + "*.html"))
files += ["manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "favicon-48.png", "fonts/fonts.css"]
files += ["fonts/" + os.path.basename(f) for f in sorted(glob.glob(R + "fonts/*.woff2"))]
files += ["data/" + os.path.basename(f) for f in sorted(glob.glob(R + "data/*"))]
files += ["cards/" + os.path.basename(f) for f in sorted(glob.glob(R + "cards/*.svg"))]   # 맞고 화투 그림(CC BY-SA, cards/LICENSE.txt)
files += ["cards-gemini/" + os.path.basename(f) for f in sorted(glob.glob(R + "cards-gemini/*.webp"))]   # 맞고 화투 그림(Gemini 생성 새 민화)
files += ["cards-trump/" + os.path.basename(f) for f in sorted(glob.glob(R + "cards-trump/*.webp"))]   # 트럼프 카드 그림
files += ["cards-minhwa/" + os.path.basename(f) for f in sorted(glob.glob(R + "cards-minhwa/*.svg"))]   # 맞고 화투 그림(직접 그린 민화풍)
files += ["yut-img/" + os.path.basename(f) for f in sorted(glob.glob(R + "yut-img/yut_*.svg"))]   # 윷 결과 카드 그림(PNG·GIF는 용량이 커서 저장하지 않음)
files += ["snake-img/" + os.path.basename(f) for f in sorted(glob.glob(R + "snake-img/*.webp"))]   # 뱀사다리 판 배경 그림(AI 생성 민화풍)
files += [os.path.basename(f) for f in sorted(glob.glob(R + "*.js")) if os.path.basename(f) != "sw.js"]
h = hashlib.md5(b"sw-format-2")                                           # 서비스 워커 방식(아래 js 틀)을 바꾸면 이 글자도 바꿔서 새 버전 이름이 나오게 해요(예전 저장 공간과 섞이지 않게)
TEXT = (".html", ".css", ".webmanifest", ".js", ".txt", ".json", ".svg")   # Windows가 줄 끝 표시(CRLF)를 바꿔도 같은 버전이 되도록 맞춘다
hashes = {}                                                              # 파일별 지문: 폰이 업데이트할 때 바뀐 파일만 새로 받는 데 써요
for f in files:
    if f != "./":
        data = open(R + f, "rb").read()
        if f.endswith(TEXT):
            data = data.replace(b"\r\n", b"\n")
        h.update(data)
        hashes[f] = hashlib.md5(data).hexdigest()[:8]
hashes["./"] = hashes.get("index.html", "")                              # "./"(주소 맨 처음)은 시작 화면 파일과 같아요
ver = "family-games-" + h.hexdigest()[:10]
old = open(R + "sw.js", encoding="utf-8").read() if os.path.exists(R + "sw.js") else ""
mv, mb = re.search(r'VERSION = "([^"]+)"', old), re.search(r'BUILD = "([^"]+)"', old)
kst = datetime.timezone(datetime.timedelta(hours=9))
build = mb.group(1) if (mv and mv.group(1) == ver and mb) else datetime.datetime.now(kst).strftime("%Y-%m-%d %H:%M")   # 내용이 바뀐 때만 새 날짜
games = len([f for f in files if f.endswith(".html") and f not in ("index.html",)])
js = '''// 오프라인에서도 게임이 실행되도록 모든 파일을 폰에 저장해 두는 서비스 워커예요. (자동 생성 파일)
const VERSION = "%s";
const BUILD = "%s";      // 이 버전을 만든 날짜(한국 시간)
const GAMES = %d;         // 들어 있는 게임 수
const PRECACHE = %s;      // 파일 이름 → 파일 지문(내용이 같으면 같은 값)
const FILES = Object.keys(PRECACHE), META = "family-games-meta";

// 업데이트: 새 저장 공간을 통째로 만들되(중간에 끊겨도 예전 것은 그대로), 지문이 같은 파일은 인터넷에서 다시 받지 않고
// 예전 저장 공간에서 복사해요. 바뀐 파일만 새로 받아요. (예전 지문표가 없으면 한 번은 전부 받아요)
async function readMeta() { try { const r = await (await caches.open(META)).match("manifest"); return r ? await r.json() : null; } catch (e) { return null; } }
self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const prev = await readMeta();
    if (!prev || prev.version !== VERSION) await caches.delete(VERSION);   // 이전에 끊긴 설치가 남긴 반쪽짜리를 지우고 새로 시작(쓰고 있는 저장 공간은 지우지 않아요)
    const oldC = prev && prev.version && prev.version !== VERSION && await caches.has(prev.version) ? await caches.open(prev.version) : null;
    const c = await caches.open(VERSION), done = {};
    await Promise.all(FILES.map(async u => {
      const req = new Request(u);
      if (oldC && prev.hashes && prev.hashes[u] === PRECACHE[u]) {  // 바뀌지 않은 파일: 복사
        const hit = await oldC.match(req); if (hit) { await c.put(req, hit); done[u] = PRECACHE[u]; return; }
      }
      try { const r = await fetch(new Request(u, { cache: "reload" })); if (!r.ok) throw 0; await c.put(req, r); done[u] = PRECACHE[u]; }   // 바뀐 파일·새 파일: 새로 받기
      catch (err) {                                                 // 못 받았으면 예전 것을 그대로 두고(지문은 예전 값) 다음 업데이트 때 다시 시도
        const hit = oldC && await oldC.match(req); if (hit) { await c.put(req, hit); done[u] = (prev.hashes && prev.hashes[u]) || ""; }
      }
    }));
    try { await (await caches.open(META)).put("manifest", new Response(JSON.stringify({ version: VERSION, hashes: done }))); } catch (err) {}
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== VERSION && k !== META) await caches.delete(k);
    await self.clients.claim();
  })());
});

// 저장된 파일을 먼저 보여 주고, 인터넷이 되면 뒤에서 새 버전으로 바꿔 둔다
self.addEventListener("fetch", e => {
  const req = e.request;
  const u = new URL(req.url);
  if (req.method !== "GET" || u.origin !== self.location.origin || u.pathname.endsWith("/sw.js")) return;      // sw.js는 항상 인터넷에서 확인해요
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

self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil((async () => {
    const cs = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of cs) if ("focus" in c) return c.focus();
    return self.clients.openWindow("med-check.html");
  })());
});

self.addEventListener("message", e => {
  if (e.data && e.data.type === "status" && e.ports[0]) {
    e.waitUntil((async () => {
      const c = await caches.open(VERSION);
      e.ports[0].postMessage({ count: (await c.keys()).length, total: FILES.length, version: VERSION, build: BUILD, games: GAMES });
    })());
  }
});
''' % (ver, build, games, json.dumps(hashes, ensure_ascii=False, separators=(",", ":")))
open(R + "sw.js", "w", encoding="utf-8", newline="\n").write(js)
print("sw.js 갱신:", ver, "| 저장 대상 파일", len(files), "개")
