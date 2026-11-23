/* 명화 그림 모드 — 명화 작가 퀴즈(art-quiz.html)와 명화 작가별 모음(art-gallery.html) 공용.
   그림 보기 3가지: 📴 글로만(기본·오프라인) / 🌐 온라인(저작권이 끝난 명화만 위키백과에서 불러옴) / 📦 저장한 그림(오프라인).
   '저장한 그림' = ① 앱에 들어 있는 art-img/ (tools/dev/art_fetch.py 가 PC에서 받아 둠) + ② 이 폰에 📥 저장한 그림(Cache 저장소, 인터넷이 있을 때 한 번 저장하면 오프라인에서도 보임).
   이 파일은 tools/dev/set43.py 가 만들어요(직접 고치지 말고 tools/dev/art_mode_tpl.js 와 set43.py 를 고치세요).
   안전장치: 온라인·저장 모두 ① 위키백과 항목 설명에 작가 이름이 있고 ② 그림 파일이 공개 도메인으로 표시돼 있을 때만 써요. 하나라도 틀리면 그림 없이 글로 나와요. */
(function () {
  "use strict";
  var DATA = /*DATA*/null;
  var AS = "art-autosave-v1", MK = "art-img-mode-v1", ONLY = "art-img-only-v1", SAVED = "art-saved-v1", CACHE = "fg-art-saved-v1";
  var mode = "text", local = null, saved = null, onlyImg = false;
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var norm = function (s) { return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var shuffle = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; };
  var titles = Object.keys(DATA.W);
  // 동시에 limit 개씩만 처리(위키 서버에 부담을 주지 않게)
  function pmap(items, fn, limit) { var out = new Array(items.length), k = 0; function w() { if (k >= items.length) return Promise.resolve(); var n = k++; return Promise.resolve(fn(items[n], n)).then(function (r) { out[n] = r; return w(); }); } var ws = []; for (var i = 0; i < Math.min(limit, items.length); i++) ws.push(w()); return Promise.all(ws).then(function () { return out; }); }

  // ── 그림 하나 얻기: 통과하면 {src, page, title, license}, 아니면 null
  function preload(src) { return new Promise(function (res) { var im = new Image(), t = setTimeout(function () { res(false); }, 9000); im.onload = function () { clearTimeout(t); res(true); }; im.onerror = function () { clearTimeout(t); res(false); }; im.src = src; }); }
  var blobUrls = {};
  function fetchOnline(title) { var w = DATA.W[title]; return w && window.fgOnline && fgOnline.on() ? fgOnline.wikiImage(w.k, w.t.map(norm), w.kd) : Promise.resolve(null); }
  function localInfo(title) {   // 오프라인에 있는 그림 정보(없으면 null): 앱에 든 것 → 폰에 저장한 것
    var e = local && local[title]; if (e) return { kind: "file", src: "art-img/" + e.f, page: e.p, title: e.t || title, license: e.l || "공개 도메인" };
    e = saved && saved[title]; return e ? { kind: "cache", src: e.src, page: e.page, title: e.title || title, license: e.license || "공개 도메인" } : null;
  }
  function resolveLocal(title) {
    var e = localInfo(title); if (!e) return Promise.resolve(null);
    if (e.kind === "file") return Promise.resolve(e);
    if (blobUrls[title]) return Promise.resolve({ src: blobUrls[title], page: e.page, title: e.title, license: e.license });
    if (!("caches" in window)) return Promise.resolve(null);
    return caches.open(CACHE).then(function (c) { return c.match(e.src); }).then(function (r) { return r ? r.blob() : null; }).then(function (b) {
      if (!b) return null; blobUrls[title] = URL.createObjectURL(b); return { src: blobUrls[title], page: e.page, title: e.title, license: e.license };
    }).catch(function () { return null; });
  }
  function getImage(title) {
    if (!DATA.W[title]) return Promise.resolve(null);
    var p = mode === "local" ? resolveLocal(title) : mode === "online" ? fetchOnline(title) : Promise.resolve(null);
    return p.then(function (r) { return r ? preload(r.src).then(function (ok) { if (ok && mode === "online") autoSave(title, r); return ok ? r : null; }) : null; });
  }
  // 온라인으로 본 그림은 이 폰에 저절로 저장해요(다음부터는 인터넷 없이도 보임). 저장소 서버(GitHub)에는 그림을 두지 않아요.
  function autoSave(title, r) {
    if (lsGet(AS) !== "1" || (saved && saved[title]) || !("caches" in window) || !r || !r.src) return;   // 저장은 사용자가 고른 경우에만
    saved = saved || {}; saved[title] = { src: r.src, page: r.page, title: r.title, license: r.license, pending: 1 };
    fetch(r.src, { credentials: "omit", referrerPolicy: "no-referrer" }).then(function (resp) { if (!resp.ok) throw 0; return caches.open(CACHE).then(function (c) { return c.put(r.src, resp); }); })
      .then(function () { delete saved[title].pending; lsSet(SAVED, JSON.stringify(saved)); })
      .catch(function () { if (saved && saved[title] && saved[title].pending) delete saved[title]; });
  }
  var has = function (title) { return !!DATA.W[title] && (mode === "online" || (mode === "local" && !!localInfo(title))); };
  var localCount = function () { return titles.filter(function (t) { return !!localInfo(t); }).length; };
  var savedCount = function () { return saved ? Object.keys(saved).length : 0; };
  var credit = function (r) { return '🖼️ 그림 출처: <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">' + esc(r.label || "위키백과") + ' 「' + esc(r.title) + "」</a> (" + esc(r.license) + ")"; };
  var CONSENT = "🌐 온라인 그림을 켜요.\n\n· 인터넷에서 저작권이 끝난 명화만 불러와요.\n· 불러올 때 이 기기의 인터넷 주소가 위키백과·위키미디어 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 언제든 '글로만'으로 끌 수 있어요.\n\n켤까요?";

  // ── 화면 위 모드 선택
  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}.amode button:disabled{opacity:.45;cursor:default}" +
      ".amode button.sm{padding:6px 10px;font-size:.85rem}.amode small{color:var(--muted,#666)}.amode .sub{border-top:1px dashed var(--line,#ccc);padding-top:8px;display:flex;flex-direction:column;gap:6px}" +
      ".aimg{margin:0 0 10px}.aimg img,.gf img{display:block;max-width:100%;max-height:300px;margin:0 auto;border-radius:12px;background:#0001}.gf{margin:6px 0 2px}.aimg img,.gf img{cursor:zoom-in}.acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}.ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}#aview{position:fixed;inset:0;z-index:9999;background:#000e;display:flex;flex-direction:column;user-select:none;-webkit-user-select:none}#aview .vb{display:flex;gap:6px;align-items:center;justify-content:flex-end;flex-wrap:wrap;padding:8px 10px}#aview .vb button{border:0;border-radius:999px;padding:8px 13px;font-size:.95rem;background:#fff;color:#111}#aview .vz{color:#fff;font-size:.85rem;min-width:3.2em;text-align:center}#aview .vi{flex:1;overflow:hidden;position:relative;touch-action:none;display:flex;align-items:center;justify-content:center}#aview .vi img{max-width:100%;max-height:100%;object-fit:contain;transform-origin:center center;will-change:transform;cursor:grab}#aview .vc{color:#fff;font-size:.8rem;padding:8px 12px;text-align:center}#aview .vh{color:#ccc}.gf figcaption{font-size:.78rem;color:var(--muted,#666);text-align:center;margin-top:4px}";
    document.head.appendChild(st);
  }
  var bar, dl = { running: false, cancel: false, msg: "" };
  function levelNote() {
    var c = { 1: 0, 2: 0, 3: 0 }; DATA.Q.forEach(function (q) { if (has(q[5])) c[q[4]]++; });
    return "그림 문제 " + (c[1] + c[2] + c[3]) + "개 (🌱 초급 " + c[1] + " · 🌿 중급 " + c[2] + " · 🌳 고급 " + c[3] + ")";
  }
  function drawBar() {
    var n = localCount(), ns = savedCount(), left = titles.length - n, online = !!window.fgOnline && fgOnline.enabled, canSave = online && "caches" in window;
    var h = '<b>🖼️ 그림 보기</b><div class="row">' +
      '<button type="button" data-m="text" class="' + (mode === "text" ? "on" : "") + '">📴 글로만</button>' +
      '<button type="button" data-m="online" class="' + (mode === "online" ? "on" : "") + '"' + (online ? "" : " disabled") + ">🌐 온라인 그림</button>" +
      '<button type="button" data-m="local" class="' + (mode === "local" ? "on" : "") + '"' + (n ? "" : " disabled") + ">📦 저장한 그림" + (n ? " (" + n + "장)" : " (없음)") + "</button></div>";
    var note = mode === "text" ? "인터넷 없이 글로만 풀어요. 그림을 보려면 위에서 골라요." :
      (mode === "online" ? (navigator.onLine === false ? "지금은 인터넷이 없어서 글로만 나와요." : "인터넷에서 저작권이 끝난 명화만 불러와요(위키백과·위키미디어 서버에 이 기기의 주소가 전달돼요). 못 불러오면 글로 나와요.") :
      "이 폰(앱)에 저장된 그림이에요. 인터넷 없이도 보여요. 그림 아래에 출처가 나와요.");
    if (mode !== "text" && isQuiz) note += " · " + levelNote();
    h += '<small id="artnote">' + esc(note) + "</small>";
    if (isQuiz && mode !== "text") h += '<div class="row"><small>그림 문제:</small><button type="button" class="sm' + (onlyImg ? "" : " on") + '" data-o="0">섞어서 (한 판에 최대 3개)</button><button type="button" class="sm' + (onlyImg ? " on" : "") + '" data-o="1">그림 문제만</button></div>';
    if (online) {
      h += '<div class="sub"><div class="row"><button type="button" class="sm" data-s="auto">💾 본 그림 자동 저장: ' + (lsGet(AS) === "1" ? "켜짐" : "꺼짐") + '</button><small>끄면 저장 없이 보기만 해요.</small></div><small>' + esc(dl.msg || (ns ? "이 폰에 그림 " + ns + "장 저장됨(인터넷 없이도 '저장한 그림'으로 볼 수 있어요)." : "그림을 이 폰에 저장해 두면 인터넷이 없어도 볼 수 있어요.")) + '</small><div class="row">' +
        (canSave ? '<button type="button" class="sm" data-s="save"' + (!dl.running && ns && !left ? " disabled" : "") + '>' + (dl.running ? "⏹ 멈추기" : ns ? (left ? "📥 그림 더 저장하기" : "✅ 모두 저장됨") : "📥 그림 저장하기(오프라인용)") + "</button>" : "<small>이 브라우저는 그림 저장을 지원하지 않아요.</small>") +
        (ns && !dl.running ? '<button type="button" class="sm" data-s="clear">🗑️ 저장한 그림 지우기</button>' : "") + "</div></div>";
    }
    if (isQuiz && wrongList.length && mode !== "text") h += '<div class="row"><button type="button" class="sm" id="artreview" data-s="review">' + reviewLabel() + "</button><small>틀린 그림만 다시 풀어요. 맞히면 목록에서 빠져요.</small></div>";
    bar.innerHTML = h;
  }
  function setMode(m) {
    if (m === "online" && !(window.fgOnline && fgOnline.ask(CONSENT))) return;
    if (m === "online" && lsGet(AS) === null) { var yes = false; try { yes = window.confirm("📥 본 그림을 이 폰에 저장할까요?\n\n· 저장하면 다음부터 인터넷 없이도 볼 수 있어요(그림 1장 약 50KB).\n· 저장하지 않으면 볼 때마다 인터넷이 필요해요.\n· 나중에 언제든 바꾸거나 지울 수 있어요.\n\n[확인] 저장해요   [취소] 저장하지 않고 보기만 해요"); } catch (e) {} lsSet(AS, yes ? "1" : "0"); }
    mode = m; lsSet(MK, m); drawBar(); if (isQuiz) start(); else decorateAll(true);
  }

  // ── 폰에 그림 저장 / 지우기
  function saveAll() {
    if (dl.running) { dl.cancel = true; dl.msg = "멈추는 중…"; drawBar(); return; }
    if (!(window.fgOnline && fgOnline.ask(CONSENT)) || !("caches" in window)) return;
    if (navigator.onLine === false) { dl.msg = "지금은 인터넷이 없어서 저장할 수 없어요."; drawBar(); return; }
    var todo = titles.filter(function (t) { return !localInfo(t); });
    if (!todo.length) { dl.msg = "저장할 그림이 없어요(모두 저장됨)."; drawBar(); return; }
    var okc = 0, bad = 0, stop = false;
    try { if (!window.confirm("그림 최대 " + todo.length + "장(약 " + Math.round(todo.length * 0.04 * 10) / 10 + "MB)을 이 폰에 저장해요. 인터넷이 켜진 상태에서 몇 분 걸릴 수 있어요.\n저작권이 끝난 명화만 저장하고, 아닌 것은 건너뛰어요.\n\n저장할까요?")) return; } catch (e) {}
    dl.running = true; dl.cancel = false; saved = saved || {}; drawBar();
    caches.open(CACHE).then(function (cache) {
      return pmap(todo, function (t) {
        if (dl.cancel || stop) return null;
        return fetchOnline(t).then(function (r) {
          if (!r) { bad++; return null; }
          return fetch(r.src, { credentials: "omit", referrerPolicy: "no-referrer" }).then(function (resp) { if (!resp.ok) throw 0; return cache.put(r.src, resp); })
            .then(function () { saved[t] = { src: r.src, page: r.page, title: r.title, license: r.license }; okc++; })
            .catch(function (e) { bad++; if (e && e.name === "QuotaExceededError") stop = true; });
        }).then(function () { dl.msg = "저장 중… " + (okc + bad) + "/" + todo.length + " (저장 " + okc + "장, 건너뜀 " + bad + ")"; if ((okc + bad) % 5 === 0) { lsSet(SAVED, JSON.stringify(saved)); drawBar(); } });
      }, 2);
    }).catch(function () {}).then(function () {
      lsSet(SAVED, JSON.stringify(saved)); dl.running = false;
      dl.msg = (dl.cancel ? "멈췄어요. " : "끝났어요. ") + "저장 " + okc + "장" + (bad ? ", 건너뜀 " + bad + "장(저작권 표시·작가 확인을 통과하지 못했거나 불러오지 못한 그림)" : "") + ".";
      dl.cancel = false; drawBar();
    });
  }
  function clearSaved() {
    try { if (!window.confirm("이 폰에 저장한 그림 " + savedCount() + "장을 지울까요? (다시 저장할 수 있어요)")) return; } catch (e) {}
    try { if ("caches" in window) caches.delete(CACHE); } catch (e) {}
    try { localStorage.removeItem(SAVED); } catch (e) {} saved = null; blobUrls = {}; dl.msg = "저장한 그림을 지웠어요.";
    if (mode === "local" && !localCount()) { mode = "text"; lsSet(MK, mode); }
    drawBar(); if (isQuiz) start(); else decorateAll(true);
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "artmode";
    var h = document.querySelector("h1"); if (h) h.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return;
      if (b.dataset.m) setMode(b.dataset.m);
      else if (b.dataset.o) { onlyImg = b.dataset.o === "1"; lsSet(ONLY, onlyImg ? "1" : "0"); drawBar(); if (isQuiz) start(); }
      else if (b.dataset.s === "review") startReview(); else if (b.dataset.s === "auto") { lsSet(AS, lsGet(AS) === "1" ? "0" : "1"); drawBar(); } else if (b.dataset.s === "save") saveAll(); else if (b.dataset.s === "clear") clearSaved();
    });
    drawBar();
  }

  // ── 퀴즈: 라운드에 그림 문제 섞기(기본 최대 3개, '그림 문제만'이면 거의 전부)
  var roundId = 0;
  function mix() {
    var id = ++roundId, want = onlyImg ? 10 : 3;
    var pool = shuffle(DATA.Q.filter(function (q) { return (!lv || q[4] === lv) && (cat === "전체" || q[3] === cat) && has(q[5]); })).slice(0, onlyImg ? 24 : 9);
    if (!pool.length) return;
    pmap(pool, function (q) { return getImage(q[5]).then(function (r) { return r ? { q: q, r: r } : null; }); }, 6).then(function (all) {
      var ok = all.filter(Boolean); if (id !== roundId || !ok.length || !qs || qs.length < 2) return;
      var first = i === 0 && !locked, slots = []; for (var k = first ? 0 : i + 1; k < qs.length; k++) slots.push(k);   // 아직 답하지 않은 첫 문제도 그림으로 바꿔요
      slots = (first ? [0].concat(shuffle(slots.slice(1))) : shuffle(slots)).slice(0, Math.min(want, ok.length));   // 첫 문제는 꼭 그림으로
      slots.forEach(function (pos, n) {
        var q = ok[n].q, d = mkItem(q); d.img = ok[n].r;
        qs[pos] = { d: d, opts: options(d) };
      });
      if (first && slots.indexOf(0) >= 0) show();
    });
  }
  function decorateQ() {
    var cur = qs && qs[i]; if (!cur || !cur.d.img) return; var d = cur.d, q = document.getElementById("q");
    var wrap = document.createElement("div"); wrap.className = "aimg"; var im = new Image(); im.alt = "작품 그림"; im.src = d.img.src;
    im.onerror = function () { wrap.remove(); q.innerHTML = q.innerHTML.replace(esc(d[0]), esc(d.alt)); };   // 그림이 갑자기 안 보이면 글 문제로 바꿔요
    wrap.appendChild(im); q.insertBefore(wrap, q.firstChild);
  }
  function creditQ() { var cur = qs && qs[i]; if (cur && cur.d.img) document.getElementById("q").insertAdjacentHTML("beforeend", '<span class="note">' + credit(cur.d.img) + "</span>"); }

  // ── 모음: 작가 카드마다 대표작 그림 하나
  var io = null;
  function decorateAll(reset) {
    var list = document.getElementById("list"); if (!list) return;
    if (reset || mode === "text") list.querySelectorAll(".gf").forEach(function (f) { f.remove(); });
    list.querySelectorAll(".ar").forEach(function (c) { if (reset || mode === "text") delete c.dataset.img; });
    if (mode === "text") return;
    if (!io && "IntersectionObserver" in window) io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); fill(e.target); } }); }, { rootMargin: "200px" });
    list.querySelectorAll(".ar").forEach(function (c) { if (c.dataset.img) return; c.dataset.img = "1"; if (io) io.observe(c); else fill(c); });
  }
  function fill(card) {
    var nm = card.querySelector("h2").childNodes[0].textContent.trim(), aid = DATA.N[nm], t = aid && DATA.G[aid]; if (!t) return;
    getImage(t).then(function (r) {
      if (!r || card.querySelector(".gf") || mode === "text") return;
      var fg = document.createElement("figure"); fg.className = "gf"; fg.innerHTML = '<img loading="lazy" alt="' + esc(t) + '"><figcaption>‘' + esc(t) + "’ · " + credit(r) + "</figcaption>"; fg.querySelector("img").src = r.src;
      var bio = card.querySelector(".bio"); card.insertBefore(fg, bio || null);
    });
  }


  // ── 그림 크게 보기: 전체 화면 + 확대(손가락 두 개로 벌리기·마우스 휠·＋/－·두 번 누르기) + 끌어서 이동. 확대하면 더 큰 그림(1280px)을 불러와 선명하게 보여요(보기를 연 경우에만 인터넷을 써요).
  var ZMAX = 8;
  function bigSrc(src) {
    if (/\/\d+px-[^\/]+$/.test(src || "") && /upload\.wikimedia\.org/.test(src)) return src.replace(/\/\d+px-([^\/]+)$/, "/1280px-$1");
    if (/^https:\/\/www\.artic\.edu\/iiif\/.*\/full\/\d+,\//.test(src || "")) return src.replace(/\/full\/\d+,\//, "/full/1200,/");
    return null;
  }
  function openViewer(src, cap) {
    var old = document.getElementById("aview"); if (old) old.remove();
    var v = document.createElement("div"); v.id = "aview"; v.setAttribute("role", "dialog"); v.setAttribute("aria-label", "그림 크게 보기");
    v.innerHTML = '<div class="vb"><button type="button" data-v="in" aria-label="확대">＋</button><button type="button" data-v="out" aria-label="축소">－</button><button type="button" data-v="rs">⟲ 처음 크기</button><span class="vz">100%</span><button type="button" data-v="fs" hidden>⛶ 전체 화면</button><button type="button" data-v="x">✖ 닫기</button></div><div class="vi"><img alt="작품 그림" draggable="false"></div><div class="vc"></div>';
    var stage = v.querySelector(".vi"), img = stage.querySelector("img"), zl = v.querySelector(".vz"), vc = v.querySelector(".vc");
    vc.innerHTML = (cap || "") + '<br><small class="vh">두 손가락으로 벌리면 확대, 끌면 이동, 두 번 누르면 확대·축소</small>';
    var S = 1, X = 0, Y = 0, ptrs = {}, last = null, lastTap = 0;
    function box() { return { w: stage.clientWidth, h: stage.clientHeight }; }
    function clamp() { var b = box(), iw = img.clientWidth * S, ih = img.clientHeight * S, mx = Math.max(0, (iw - b.w) / 2) + 40, my = Math.max(0, (ih - b.h) / 2) + 40; X = Math.max(-mx, Math.min(mx, X)); Y = Math.max(-my, Math.min(my, Y)); }
    function apply() { clamp(); img.style.transform = "translate(" + X + "px," + Y + "px) scale(" + S + ")"; zl.textContent = Math.round(S * 100) + "%"; if (S > 1.4) loadBig(); }
    function zoomAt(ns, cx, cy) {   // 화면 위의 한 점(cx,cy)을 고정한 채 배율 바꾸기
      ns = Math.max(1, Math.min(ZMAX, ns)); var b = box(), px = cx - b.w / 2, py = cy - b.h / 2; X = px - (px - X) * ns / S; Y = py - (py - Y) * ns / S; S = ns; if (S === 1) { X = 0; Y = 0; } apply();
    }
    var bigDone = false;
    function loadBig() {
      if (bigDone) return; bigDone = true; var bs = bigSrc(src); if (!bs || navigator.onLine === false) return;
      var t = new Image(); t.onload = function () { if (document.getElementById("aview") === v) { img.src = bs; vc.querySelector(".vh").textContent = "고화질 그림으로 바뀌었어요"; } }; t.src = bs;
    }
    img.src = src;
    v.querySelector("[data-v=fs]").hidden = !(v.requestFullscreen && document.fullscreenEnabled);
    v.addEventListener("click", function (e) {
      var b = e.target.closest("button"), k = b && b.dataset.v, c = box();
      if (k === "x" || e.target === v || e.target === vc) { if (document.fullscreenElement) { try { document.exitFullscreen(); } catch (x) {} } v.remove(); }
      else if (k === "in") zoomAt(S * 1.6, c.w / 2, c.h / 2); else if (k === "out") zoomAt(S / 1.6, c.w / 2, c.h / 2);
      else if (k === "rs") zoomAt(1, c.w / 2, c.h / 2);
      else if (k === "fs") { try { if (document.fullscreenElement) document.exitFullscreen(); else v.requestFullscreen(); } catch (x) {} }
    });
    stage.addEventListener("wheel", function (e) { e.preventDefault(); var r = stage.getBoundingClientRect(); zoomAt(S * (e.deltaY < 0 ? 1.25 : 0.8), e.clientX - r.left, e.clientY - r.top); }, { passive: false });
    stage.addEventListener("pointerdown", function (e) {
      stage.setPointerCapture(e.pointerId); ptrs[e.pointerId] = { x: e.clientX, y: e.clientY }; last = null;
      var now = Date.now(); if (Object.keys(ptrs).length === 1 && now - lastTap < 300) { var r = stage.getBoundingClientRect(); zoomAt(S > 1.5 ? 1 : 3, e.clientX - r.left, e.clientY - r.top); lastTap = 0; } else lastTap = now;
    });
    stage.addEventListener("pointermove", function (e) {
      if (!ptrs[e.pointerId]) return; var ids = Object.keys(ptrs), prev = ptrs[e.pointerId]; ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
      if (ids.length === 1) { if (S > 1) { X += e.clientX - prev.x; Y += e.clientY - prev.y; apply(); } }
      else if (ids.length === 2) {
        var a = ptrs[ids[0]], b = ptrs[ids[1]], d = Math.hypot(a.x - b.x, a.y - b.y), mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2, r = stage.getBoundingClientRect();
        if (last) { X += mx - last.mx; Y += my - last.my; zoomAt(S * d / last.d, mx - r.left, my - r.top); } last = { d: d, mx: mx, my: my };
      }
    });
    function up(e) { delete ptrs[e.pointerId]; last = null; }
    stage.addEventListener("pointerup", up); stage.addEventListener("pointercancel", up);
    document.body.appendChild(v); apply();
  }
  document.addEventListener("keydown", function (e) {
    var v = document.getElementById("aview"); if (!v) return;
    if (e.key === "Escape") v.remove(); else if (e.key === "+" || e.key === "=") v.querySelector("[data-v=in]").click(); else if (e.key === "-") v.querySelector("[data-v=out]").click();
  });
  document.addEventListener("click", function (e) {
    var im = e.target.closest && e.target.closest(".aimg img, .gf img"); if (!im || !im.src) return;
    var f = im.closest(".gf"), cap = f ? (f.querySelector("figcaption") || {}).innerHTML : "";
    var cur = isQuiz && qs && qs[i]; if (cur && cur.d.img) cap = credit(cur.d.img);
    openViewer(im.src, cap);
  });

  // ── 힌트(그림 문제): 시대·나라 → 그려진 때. 쓰면 맞혀도 0.5점
  var hintUsed = false;
  function addHint() {
    var cur = qs && qs[i]; hintUsed = false; if (!cur || !cur.d.img || !cur.d.meta) return;
    var q = document.getElementById("q"), m = cur.d.meta, era = cur.d[3], lvl = 0;
    var box = document.createElement("div"); box.className = "ahint"; box.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
    var btn = box.querySelector("button"), out = box.querySelector("div");
    btn.addEventListener("click", function () {
      if (locked) return; hintUsed = true; lvl++; out.hidden = false;
      out.textContent = lvl === 1 ? "시대·화풍: " + era + " · 작가의 나라: " + m[5] : "시대·화풍: " + era + " · 나라: " + m[5] + " · 그려진 때: " + m[0];
      if (lvl >= 2) btn.disabled = true; else btn.textContent = "💡 힌트 한 번 더";
    });
    q.appendChild(box);
  }
  // ── 정답 뒤 작품 설명 카드
  function addCard() {
    var cur = qs && qs[i]; if (!cur || !cur.d.img || !cur.d.meta) return; var m = cur.d.meta, q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><b>‘' + esc(cur.d.tt) + "’</b><span>" + esc(m[3]) + " (" + esc(m[4]) + " · " + esc(m[5]) + ")</span><span>" + esc(cur.d[3]) + " · " + esc(m[2]) + " · " + esc(m[0]) + "</span>" + (m[1] ? "<span>📍 " + esc(m[1]) + "</span>" : "") + "</div>");
  }
  // ── 틀린 그림 복습: 틀린 그림 제목을 기억해 두고 다시 풀어요(맞히면 목록에서 빠져요)
  var WK = "art-wrong-v1", wrongList = [], reviewing = false;
  function loadWrong() { try { var a = JSON.parse(lsGet(WK) || "[]"); wrongList = Array.isArray(a) ? a.filter(function (t) { return DATA.W[t]; }) : []; } catch (e) { wrongList = []; } }
  function saveWrong() { lsSet(WK, JSON.stringify(wrongList.slice(-60))); }
  function recordResult(cur, ok) {
    if (!cur || !cur.d.tt) return; var k = wrongList.indexOf(cur.d.tt);
    if (ok) { if (k >= 0) wrongList.splice(k, 1); } else if (k < 0) wrongList.push(cur.d.tt); else { wrongList.splice(k, 1); wrongList.push(cur.d.tt); }
    saveWrong(); var b = document.getElementById("artreview"); if (b) b.textContent = reviewLabel();
  }
  var reviewLabel = function () { return "🔁 틀린 그림 복습 (" + wrongList.length + ")"; };
  function mkItem(q) { var d = [q[0], q[1], q[2], q[3], q[6]]; d.alt = "‘" + q[5] + "’의 작가는 누구일까요?"; d.tt = q[5]; d.meta = q[7]; return d; }
  function startReview() {
    if (!wrongList.length) return; var picks = shuffle(wrongList).slice(0, 10);
    start(); roundId++;   // 일반 문제 섞기를 멈추고
    var items = picks.map(function (t) { return DATA.Q.filter(function (q) { return q[5] === t; })[0]; }).filter(Boolean);
    pmap(items, function (q) { return getImage(q[5]); }, 4).then(function (imgs) {
      qs = items.map(function (q, n) { var d = mkItem(q); if (imgs[n]) d.img = imgs[n]; else d[0] = d.alt; return { d: d, opts: options(d) }; });
      i = 0; score = 0; reviewing = true; show();
    });
  }

  // ── 시작
  function boot() {
    try { saved = JSON.parse(lsGet(SAVED) || "null"); if (!saved || typeof saved !== "object" || !Object.keys(saved).length) saved = null; } catch (e) { saved = null; }
    onlyImg = lsGet(ONLY) === "1"; loadWrong(); buildBar();
    if (isQuiz) {
      var oS = start, oShow = show, oPick = pick;
      start = function () { reviewing = false; oS(); if (mode !== "text") mix(); };
      show = function () { oShow(); decorateQ(); addHint(); };
      pick = function (k) {
        if (locked) return; var cur = qs && qs[i], ok = cur && cur.opts[k] === cur.d[1], hu = hintUsed; oPick(k);
        if (ok && hu && cur.d.img) { score -= 0.5; document.getElementById("score").textContent = score; }
        recordResult(cur, ok); addCard(); creditQ();
      };
    } else if (isGal) {
      new MutationObserver(function () { decorateAll(false); }).observe(document.getElementById("list"), { childList: true });
    }
    var savedMode = lsGet(MK);
    fetch("art-img/index.json").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (idx) {
      local = idx && typeof idx === "object" && Object.keys(idx).length ? idx : null;
      if (savedMode === "local" && localCount()) mode = "local"; else if (savedMode === "online" && window.fgOnline && fgOnline.on()) mode = "online";
      drawBar(); if (mode !== "text") { if (isQuiz) start(); else decorateAll(false); }
    });
  }
  addEventListener("online", function () { if (bar) drawBar(); }); addEventListener("offline", function () { if (bar) drawBar(); });   // 인터넷 연결 상태가 바뀌면 안내 문구도 바꿔요
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
