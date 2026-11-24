/* 클래식 듣고 맞히기 — 클래식 작곡가 퀴즈(classic-quiz.html)와 작곡가별 모음(classic-gallery.html) 공용.
   음원은 이 저장소(GitHub)나 서버에 두지 않아요. 사용자가 🌐 온라인 듣기를 허락하면 ① 위키미디어 커먼즈에서 곡 음원을 찾고 ② 파일 이름에 곡 낱말이 있고 ③ 라이선스가 공개 도메인·CC0 표시일 때만 불러와
   처음 듣는 동안 이 폰의 저장 공간(Cache)에 앞부분(약 900KB, 20~30초)을 저장해요. 그다음부터는 인터넷 없이도 들려요. 하나라도 틀리면 그 곡은 음원 없이 글로만 나와요.
   이 파일은 tools/dev/set44.py 가 만들어요(직접 고치지 말고 tools/dev/classic_mode_tpl.js 와 set44.py 를 고치세요). */
(function () {
  "use strict";
  var DATA = /*DATA*/null;   // W: {곡: [작곡가, 연도, 갈래, 시대, 유명도, 나라, 작곡가id]}, C: [[작곡가, 시대, id]], AMBIG, P: {곡: [음질 선별을 통과한 커먼즈 파일 이름들]}
  var AS = "classic-autosave-v1", LM = "classic-limit-v1", BADK = "classic-badaudio-v1", FS = "classic-fullsave-v1", MK = "classic-listen-mode-v1", WK = "classic-wrong-v1", SAVED = "classic-saved-v1", CACHE = "fg-classic-saved-v1", KEEP = 900000, FULLMAX = 40000000, LIMIT = [15, 30, 60].indexOf(+lsGet2("classic-limit-v1")) >= 0 ? +lsGet2("classic-limit-v1") : 30;
  function lsGet2(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  var mode = "off", saved = null;   // mode: off | mix | only
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var shuffle = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i], a2 = a[j]; a[i] = a2; a[j] = t; } return a; };
  var CONSENT = "🌐 온라인 듣기를 켜요.\n\n· 인터넷에서 저작권이 끝난(공개 도메인·CC0) 클래식 녹음만 찾아서 들려줘요.\n· 찾고 들을 때 이 기기의 인터넷 주소가 위키미디어 또는 인터넷 아카이브 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 들은 곡의 앞부분(약 1MB 이하)은 이 폰에 저장해서, 다음부터는 인터넷 없이도 들을 수 있어요(설정에서 지울 수 있어요).\n· 조건에 맞는 녹음이 없으면 그 곡은 글로만 나와요.\n\n켤까요?";
  var online = function () { return !!window.fgOnline && fgOnline.enabled && fgOnline.on() && navigator.onLine !== false; };
  var badList = function () { try { var a = JSON.parse(lsGet(BADK) || "[]"); return Array.isArray(a) ? a : []; } catch (e) { return []; } };
  var isBad = function (name) { return badList().indexOf(name) >= 0; };
  var savedCount = function () { return saved ? Object.keys(saved).length : 0; };
  var credit = function (e) { return '🎧 음원: <a href="' + esc(e.page) + '" target="_blank" rel="noopener noreferrer">' + esc(e.label || '위키미디어 커먼즈') + ' 「' + esc(e.title) + "」</a> (" + esc(e.license) + ")"; };
  var inCache = function (cb) { return "caches" in window ? caches.open(CACHE).then(cb).catch(function () { return null; }) : Promise.resolve(null); };

  // ── 음원 하나 얻기: ① 폰에 저장된 것 → ② 온라인에서 찾기 (통과하면 {src, page, title, license, kind}, 아니면 null)
  var blobUrls = {};
  function fromSaved(t) {
    var e = saved && saved[t]; if (!e || isBad(e.title)) return Promise.resolve(null);
    if (blobUrls[t]) return Promise.resolve({ src: blobUrls[t], page: e.page, title: e.title, license: e.license, kind: "saved", label: e.label, remote: e.src });
    return inCache(function (c) { return c.match(e.src); }).then(function (r) { return r ? r.blob() : null; }).then(function (b) {
      if (!b) return null; blobUrls[t] = URL.createObjectURL(b); return { src: blobUrls[t], page: e.page, title: e.title, license: e.license, kind: "saved", label: e.label, remote: e.src };
    }).catch(function () { return null; });
  }
  // 소리가 실제로 나올 수 있는지 잠깐 확인(메타데이터만 받아 봐요). 9초 안에 안 되면 다음 후보(다른 서버)로 넘어가요
  function playable(src) {
    return new Promise(function (ok) {
      var a = new Audio(), done = false, t = setTimeout(function () { f(false); }, 9000);
      function f(v) { if (done) return; done = true; clearTimeout(t); try { a.removeAttribute("src"); a.load(); } catch (e) {} ok(v); }
      a.preload = "metadata"; a.addEventListener("loadedmetadata", function () { f(true); }); a.addEventListener("error", function () { f(false); }); a.src = src;
    });
  }
  function fromOnline(t) {
    var names = DATA.P[t]; if (!names || !online()) return Promise.resolve(null);
    return fgOnline.audioFiles(names, 80000000).then(function (list) {
      list = (list || []).filter(function (x) { return !isBad(x.title); }); var k = 0;
      function next() {
        if (k >= list.length) return null; var r = list[k++];
        return playable(r.src).then(function (okp) { return okp ? r : next(); });
      }
      return next().then(function (r) { r = r || list[0]; return r ? { src: r.src, page: r.page, title: r.title, license: r.license, label: r.label, size: r.size, kind: "online", remote: r.src } : null; });
    });
  }
  function getAudio(t) { return fromSaved(t).then(function (r) { return r || fromOnline(t); }); }
  var hasAudioCandidate = function (t) { return !!DATA.P[t] && (!!(saved && saved[t]) || online()); };
  var candidates = function () { return Object.keys(DATA.W).filter(hasAudioCandidate); };

  // 처음 들을 때 앞부분만 폰에 저장(mp3·ogg 계열은 앞 900KB, 작은 파일은 통째로, 큰 wav·flac 은 저장하지 않고 들을 때마다 불러와요)
  function saveOne(t, r) {
    if (lsGet(AS) !== "1" || r.kind !== "online" || (saved && saved[t]) || !("caches" in window)) return;   // 저장은 사용자가 고른 경우에만
    storeOne(t, r);
  }
  function storeOne(t, r) {   // 저장에 성공하면 true(약속), 저장할 수 없는 파일이면 false
    var ext = (r.title.match(/\.(\w+)$/) || [, ""])[1].toLowerCase(), full = lsGet(FS) === "1" && r.size && r.size <= FULLMAX, small = full || (r.size && r.size <= 2000000), lossy = /^(ogg|oga|opus|mp3)$/.test(ext);
    if (!small && !lossy) return Promise.resolve(false);
    return fetch(r.src, { credentials: "omit", referrerPolicy: "no-referrer", headers: small ? {} : { Range: "bytes=0-" + (KEEP - 1) } }).then(function (resp) {
      if (!resp.ok) throw 0; return resp.blob().then(function (b) { return { b: b, type: resp.headers.get("content-type") || "audio/ogg" }; });
    }).then(function (x) {
      if (!x.b.size || x.b.size < 20000) throw 0;
      return inCache(function (c) { return c.put(r.src, new Response(x.b, { status: 200, headers: { "Content-Type": x.type } })); }).then(function () {
        saved = saved || {}; saved[t] = { src: r.src, page: r.page, title: r.title, license: r.license, label: r.label }; lsSet(SAVED, JSON.stringify(saved)); if (bar && !dl.running) drawBar(); return true;
      });
    }).catch(function (e) { if (e && e.name === "QuotaExceededError") dl.full = true; return false; });
  }

  // ── 📥 모든 곡 저장하기(그림의 '📥 그림 저장하기'와 같은 방식, 2026-11-24 사용자 요청): 듣기 가능한 곡을 한 번에 이 폰에 저장해요.
  //    저장하는 범위는 '전곡 저장' 설정을 따라요(꺼짐 = 곡마다 앞부분 약 0.9MB). 검증(공개 도메인·CC0 표시)을 통과한 녹음만 저장해요.
  var dl = { running: false, cancel: false, msg: "", full: false };
  function pmap(items, fn, limit) { var k = 0; function w() { if (k >= items.length) return Promise.resolve(); var it = items[k++]; return Promise.resolve(fn(it)).then(w); } var ws = []; for (var i = 0; i < Math.min(limit, items.length); i++) ws.push(w()); return Promise.all(ws); }
  function saveAll() {
    if (dl.running) { dl.cancel = true; dl.msg = "멈추는 중…"; drawBar(); return; }
    if (!(window.fgOnline && fgOnline.ask(CONSENT)) || !("caches" in window)) return;
    if (navigator.onLine === false) { dl.msg = "지금은 인터넷이 없어서 저장할 수 없어요."; drawBar(); return; }
    var todo = Object.keys(DATA.P).filter(function (t) { return !(saved && saved[t]); });
    if (!todo.length) { dl.msg = "저장할 곡이 없어요(모두 저장됨)."; drawBar(); return; }
    var full = lsGet(FS) === "1", mb = full ? "수백 MB까지(곡 전체)" : "약 " + Math.round(todo.length * 0.9) + "MB(곡마다 앞부분)";
    try { if (!window.confirm("음원 " + todo.length + "곡, " + mb + "을 이 폰에 저장해요. 와이파이에서 몇 분 걸릴 수 있어요.\n저작권이 끝난 녹음만 저장하고, 찾지 못한 곡은 건너뛰어요.\n\n저장할까요?")) return; } catch (e) {}
    var okc = 0, bad = 0; dl.running = true; dl.cancel = false; dl.full = false; drawBar();
    pmap(todo, function (t) {
      if (dl.cancel || dl.full) return null;
      return fromOnline(t).then(function (r) { return r ? storeOne(t, r) : false; }).catch(function () { return false; }).then(function (ok) {
        if (ok) okc++; else bad++;
        dl.msg = "저장 중… " + (okc + bad) + "/" + todo.length + " (저장 " + okc + "곡, 건너뜀 " + bad + ")"; drawBar();
      });
    }, 2).then(function () {
      dl.running = false;
      dl.msg = (dl.cancel ? "멈췄어요. " : dl.full ? "폰 저장 공간이 모자라 멈췄어요. " : "끝났어요. ") + "저장 " + okc + "곡" + (bad ? ", 건너뜀 " + bad + "곡(검증을 통과한 녹음을 찾지 못했거나 불러오지 못한 곡)" : "") + ".";
      dl.cancel = false; drawBar();
    });
  }
  function clearSaved() {
    try { if (!window.confirm("이 폰에 저장한 음원 " + savedCount() + "곡을 지울까요? (다시 들으면 또 저장돼요)")) return; } catch (e) {}
    try { if ("caches" in window) caches.delete(CACHE); } catch (e) {}
    try { localStorage.removeItem(SAVED); } catch (e) {} saved = null; blobUrls = {}; stopAudio(); if (bar) drawBar();
  }

  // ── 소리 재생(한 번에 하나, 앞 LIMIT초만)
  var cur = null;
  function stopAudio() { if (cur) { try { cur.pause(); } catch (e) {} } }
  function player(r, lim) {
    stopAudio(); var a = new Audio(r.src); a.preload = "auto"; a._lim = lim === undefined ? LIMIT : lim; cur = a;
    a.addEventListener("timeupdate", function () { if (a.currentTime >= a._lim) { a.pause(); a.dispatchEvent(new Event("ended")); } });
    return a;
  }

  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}.amode button.sm{padding:6px 10px;font-size:.85rem}" +
      ".amode small{color:var(--muted,#666)}.aplay{display:flex;flex-direction:column;align-items:center;gap:6px;margin:0 0 10px}.aplay button{border:0;border-radius:999px;background:var(--accent,#c4552b);color:var(--accent-fg,#fff);font-size:1.15rem;font-weight:700;padding:14px 26px;min-width:200px}" +
      ".aplay small{color:var(--muted,#666)}.acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".row2{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}.ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}" +
      ".cbtn,.gplay{margin-left:6px;border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:2px 10px;font-size:.8rem}a.cbtn{display:inline-block;text-decoration:none}.ytrow{margin-top:8px;font-weight:400;font-family:var(--font-body,inherit);display:flex;gap:6px;align-items:center;flex-wrap:wrap}.ytrow small{color:var(--muted,#666);font-size:.8rem}.ytrow .cbtn{margin-left:0}.gplay.on,.cbtn.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent}";
    document.head.appendChild(st);
  }
  function askSave() {
    if (lsGet(AS) !== null || !(window.fgOnline && fgOnline.on())) return; var yes = false;
    try { yes = window.confirm("📥 들은 곡의 앞부분(약 1MB 이하)을 이 폰에 저장할까요?\n\n· 저장하면 다음부터 인터넷 없이도 들을 수 있어요.\n· 저장하지 않으면 들을 때마다 인터넷이 필요해요.\n· 나중에 언제든 바꾸거나 지울 수 있어요.\n\n[확인] 저장해요   [취소] 저장하지 않고 듣기만 해요"); } catch (e) {}
    lsSet(AS, yes ? "1" : "0");
  }
  var bar;
  function drawBar() {
    var n = savedCount(), on = online(), can = on || n > 0;
    var h = '<b>🎧 듣고 맞히기</b><div class="row">' +
      '<button type="button" data-m="off" class="' + (mode === "off" ? "on" : "") + '">📴 글로만</button>' +
      '<button type="button" data-m="mix" class="' + (mode === "mix" ? "on" : "") + '">🔀 섞어서(한 판 최대 3개)</button>' +
      '<button type="button" data-m="only" class="' + (mode === "only" ? "on" : "") + '">🎧 듣기 문제만</button></div>';
    h += "<small>" + (mode === "off" ? "듣기 문제를 풀려면 아래에서 골라요. 처음 한 번은 인터넷이 필요하고, 들은 곡은 이 폰에 저장돼서 다음부터는 인터넷 없이도 들려요." :
      (on ? "인터넷에서 저작권이 끝난 녹음을 찾아 들려줘요(위키미디어·인터넷 아카이브 서버에 이 기기의 주소가 전달돼요). 선택한 시간(" + LIMIT + "초) 동안 들려요." : (n ? "지금은 인터넷이 없어서 이 폰에 저장된 음원(" + n + "곡)만 나와요." : "지금은 인터넷이 없고 저장된 음원도 없어서 글로만 나와요."))) + " · 저장된 음원 " + n + " / 듣기 가능 " + Object.keys(DATA.P).length + "곡 · <a href=\"offline-media.html\">📊 저장 현황</a></small>";
    h += '<div class="row"><small>듣기 시간:</small>' + [15, 30, 60].map(function (s) { return '<button type="button" class="sm' + (LIMIT === s ? " on" : "") + '" data-m="lim" data-s="' + s + '">' + s + "초</button>"; }).join("") + "<small>(모음 화면과 정답 뒤에는 끝까지 들어요)</small></div>";
    h += '<div class="row"><button type="button" class="sm" data-m="fullsave">📦 전곡 저장: ' + (lsGet(FS) === "1" ? "켜짐" : "꺼짐") + "</button><small>켜면 곡 전체를 저장해요(한 곡 수 MB~수십 MB, 와이파이 권장). 끄면 앞부분만 저장해요.</small></div>";
    h += '<div class="row"><button type="button" class="sm" data-m="auto">💾 들은 곡 자동 저장: ' + (lsGet(AS) === "1" ? "켜짐" : "꺼짐") + "</button>" + (n && !dl.running ? '<button type="button" class="sm" data-m="clear">🗑️ 저장한 음원 지우기</button>' : "") + "</div>";
    if (window.fgOnline && fgOnline.enabled) {
      var left = Object.keys(DATA.P).length - n;
      h += '<div class="row">' + ("caches" in window ? '<button type="button" class="sm" data-m="saveall"' + (!dl.running && !left ? " disabled" : "") + ">" + (dl.running ? "⏹ 멈추기" : !left ? "✅ 모두 저장됨" : n ? "📥 남은 곡 저장하기 (" + left + "곡)" : "📥 모든 곡 저장하기(오프라인용)") + "</button>" : "") +
        "<small>" + esc(dl.msg || "한 번에 저장해 두면 인터넷 없이도 듣기 문제를 풀 수 있어요.") + "</small></div>";
    }
    if (isQuiz && wrongList.length && mode !== "off") h += '<div class="row"><button type="button" class="sm" id="clsreview" data-m="review">' + reviewLabel() + "</button><small>틀린 곡만 다시 들어요.</small></div>";
    bar.innerHTML = h;
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "clsmode";
    var hh = document.querySelector("h1"); if (hh) hh.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return; var m = b.dataset.m;
      if (m === "review") startReview(); else if (m === "saveall") saveAll(); else if (m === "clear") clearSaved(); else if (m === "auto") { lsSet(AS, lsGet(AS) === "1" ? "0" : "1"); drawBar(); }
      else if (m === "lim") { LIMIT = +b.dataset.s; lsSet(LM, String(LIMIT)); drawBar(); }
      else if (m === "fullsave") { if (lsGet(FS) === "1") lsSet(FS, "0"); else { var ok = false; try { ok = window.confirm("📦 곡 전체를 이 폰에 저장할까요?\n\n· 한 곡이 수 MB~수십 MB(길게는 80MB)까지 있어요. 폰 저장 공간과 데이터를 많이 써요.\n· 와이파이에서 쓰는 걸 권해요.\n· 이미 저장한 앞부분은 그대로 두고, 앞으로 저장하는 곡부터 전체를 저장해요.\n· 언제든 끄거나 '저장한 음원 지우기'로 지울 수 있어요."); } catch (x) {} if (ok) lsSet(FS, "1"); } drawBar(); }
      else {
        if (m !== "off" && !online() && !savedCount()) { try { window.alert("지금은 인터넷이 없어요. 인터넷이 켜진 곳에서 한 번 들어 보면 이 폰에 저장돼요."); } catch (x) {} }
        if (m !== "off" && window.fgOnline && !fgOnline.on() && !fgOnline.ask(CONSENT) && !savedCount()) return;
        askSave(); mode = m; lsSet(MK, mode); drawBar(); stopAudio(); start();
      }
    });
    drawBar();
  }

  // ── 문제 만들기: 곡 → 작곡가 또는 곡 → 제목
  function wrongComposers(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []), mine = w[6], era = w[3], lvl = w[4];
    var pool = DATA.C.filter(function (c) { return c[2] !== mine && ban.indexOf(c[2]) < 0; });
    var same = shuffle(pool.filter(function (c) { return c[1] === era; })), diff = shuffle(pool.filter(function (c) { return c[1] !== era; }));
    var n = lvl === 1 ? 0 : lvl === 2 ? 1 : 2, out = same.slice(0, n); diff.concat(same.slice(n)).forEach(function (c) { if (out.length < 3 && out.indexOf(c) < 0) out.push(c); });
    return out.slice(0, 3).map(function (c) { return c[0]; });
  }
  function wrongTitles(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []);
    return shuffle(Object.keys(DATA.W).filter(function (x) { var v = DATA.W[x]; return x !== t && v[6] !== w[6] && ban.indexOf(v[6]) < 0 && v[4] <= 2 && (DATA.AMBIG[x] || []).indexOf(w[6]) < 0; })).slice(0, 3);
  }
  function mkItem(t, kind, r) {
    var w = DATA.W[t], d;
    if (kind === "t") d = ["이 곡의 제목은 무엇일까요?", t, wrongTitles(t), w[3], w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    else d = ["이 곡의 작곡가는 누구일까요?", w[0], wrongComposers(t), w[3], "‘" + t + "’ — " + w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    d.tt = t; d.aud = r; d.kind = kind; return d;
  }
  function pmap(items, fn, limit) { var out = new Array(items.length), k = 0; function w() { if (k >= items.length) return Promise.resolve(); var n = k++; return Promise.resolve(fn(items[n], n)).then(function (r) { out[n] = r; return w(); }); } var ws = []; for (var q = 0; q < Math.min(limit, items.length); q++) ws.push(w()); return Promise.all(ws).then(function () { return out; }); }
  var roundId = 0;
  function mix() {
    var id = ++roundId, want = mode === "only" ? 10 : 3, first = i === 0 && !locked;
    var pool = shuffle(candidates().filter(function (t) { var w = DATA.W[t]; return (!lv || w[4] === lv) && (cat === "전체" || w[3] === cat); })).slice(0, want + (mode === "only" ? 8 : 3));
    if (!pool.length) return;
    pmap(pool, function (t) { return getAudio(t).then(function (r) { return r ? { t: t, r: r } : null; }); }, 2).then(function (all) {
      var ok = all.filter(Boolean); if (id !== roundId || !ok.length || !qs || qs.length < 2) return;
      var slots = []; for (var k = first ? 0 : i + 1; k < qs.length; k++) slots.push(k);
      slots = (first ? [0].concat(shuffle(slots.slice(1))) : shuffle(slots)).slice(0, Math.min(want, ok.length));
      slots.forEach(function (pos, n) { var d = mkItem(ok[n].t, Math.random() < 0.5 ? "t" : "c", ok[n].r); qs[pos] = { d: d, opts: options(d) }; });
      if (first && slots.indexOf(0) >= 0) show();
    });
  }
  var hintUsed = false;
  function decorateQ() {
    var c = qs && qs[i]; stopAudio(); hintUsed = false; if (!c || !c.d.aud) return;
    var q = document.getElementById("q"), box = document.createElement("div"), r = c.d.aud; box.className = "aplay";
    box.innerHTML = '<button type="button">▶ 소리 듣기</button><small>눌러서 듣고, 몇 번이든 다시 들을 수 있어요(' + LIMIT + "초, 정답을 고르면 끝까지 들을 수 있어요).</small>";
    var btn = box.querySelector("button"), a = null;
    function bind() {
      a = player(r); a.addEventListener("ended", function () { btn.textContent = "🔁 다시 듣기"; });
      a.addEventListener("error", function () { btn.textContent = "소리를 불러오지 못했어요"; btn.disabled = true; });
    }
    btn.addEventListener("click", function () {
      if (!a) { bind(); saveOne(c.d.tt, r); }
      if (!a.paused && !a.ended) { a.pause(); btn.textContent = "▶ 이어서 듣기"; return; }
      if (a.ended || a.currentTime >= a._lim) a.currentTime = 0; stopAudioExcept(a); var p = a.play(); if (p && p.catch) p.catch(function () { btn.textContent = "소리를 불러오지 못했어요"; }); btn.textContent = "⏸ 멈추기";
    });
    q.insertBefore(box, q.firstChild);
    var m = DATA.W[c.d.tt], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
    var hbtn = hb.querySelector("button"), out = hb.querySelector("div"), lvl = 0;
    hbtn.addEventListener("click", function () { if (locked) return; hintUsed = true; lvl++; out.hidden = false; out.textContent = lvl === 1 ? "시대: " + m[3] + (c.d.kind === "c" ? " · 갈래: " + m[2] : "") : "시대: " + m[3] + " · 갈래: " + m[2] + " · 작곡가의 나라: " + m[5]; if (lvl >= 2) hbtn.disabled = true; else hbtn.textContent = "💡 힌트 한 번 더"; });
    q.appendChild(hb);
  }
  function stopAudioExcept(a) { if (cur && cur !== a) { try { cur.pause(); } catch (e) {} } cur = a; }
  function addCard() {
    var c = qs && qs[i]; if (!c || !c.d.aud) return; var m = DATA.W[c.d.tt], q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><b>‘' + esc(c.d.tt) + "’</b><span>" + esc(m[0]) + " (" + esc(m[5]) + ")</span><span>" + esc(m[3]) + " · " + esc(m[2]) + " · " + esc(m[1]) + '</span></div><div class="row2"><button type="button" class="cbtn" id="clsfull">▶ 끝까지 듣기</button><button type="button" class="cbtn" id="clsbad">🔇 음질이 나빠요</button></div><small id="clsmsg" class="note"></small><span class="note">' + credit(c.d.aud) + "</span>");
    var fb = document.getElementById("clsfull"), bb = document.getElementById("clsbad"), msg = document.getElementById("clsmsg"), r = c.d.aud, remote = r.remote || r.src;
    fb.addEventListener("click", function () {
      if (cur && cur._full && !cur.paused) { cur.pause(); fb.textContent = "▶ 이어서 듣기"; return; }
      if (cur && cur._full && cur.paused && !cur.ended) { cur.play(); fb.textContent = "⏸ 멈추기"; return; }
      if (r.kind === "saved" && !online()) { msg.textContent = "저장된 건 앞부분만 있어요. 인터넷이 켜지면 끝까지 들을 수 있어요."; }
      var src = (r.kind === "saved" && !online()) ? r.src : remote; var a = player({ src: src }, Infinity); a._full = true; a.addEventListener("ended", function () { fb.textContent = "🔁 다시 듣기"; }); a.addEventListener("error", function () { msg.textContent = "끝까지 불러오지 못했어요. 잠시 뒤 다시 눌러 보세요."; fb.textContent = "▶ 끝까지 듣기"; });
      var p = a.play(); if (p && p.catch) p.catch(function () {}); fb.textContent = "⏸ 멈추기";
    });
    bb.addEventListener("click", function () {
      var a = badList(); if (a.indexOf(r.title) < 0) a.push(r.title); lsSet(BADK, JSON.stringify(a.slice(-100)));
      if (saved && saved[c.d.tt]) { delete saved[c.d.tt]; lsSet(SAVED, JSON.stringify(saved)); delete blobUrls[c.d.tt]; }
      bb.disabled = true; msg.textContent = "알려 줘서 고마워요. 이 녹음은 이제 쓰지 않고 다른 녹음으로 바꿔요(없으면 이 곡은 글로만 나와요).";
    });
  }
  // ── 틀린 곡 복습
  var wrongList = [];
  function loadWrong() { try { var a = JSON.parse(lsGet(WK) || "[]"); wrongList = Array.isArray(a) ? a.filter(function (t) { return DATA.W[t]; }) : []; } catch (e) { wrongList = []; } }
  var reviewLabel = function () { return "🔁 틀린 곡 복습 (" + wrongList.length + ")"; };
  function record(c, ok) {
    if (!c || !c.d.tt) return; var k = wrongList.indexOf(c.d.tt);
    if (ok) { if (k >= 0) wrongList.splice(k, 1); } else { if (k >= 0) wrongList.splice(k, 1); wrongList.push(c.d.tt); }
    lsSet(WK, JSON.stringify(wrongList.slice(-60))); var b = document.getElementById("clsreview"); if (b) b.textContent = reviewLabel();
  }
  function startReview() {
    var ts = shuffle(wrongList.filter(hasAudioCandidate)).slice(0, 10); if (!ts.length) return;
    start(); roundId++;
    pmap(ts, getAudio, 2).then(function (rs) {
      var items = []; ts.forEach(function (t, n) { if (rs[n]) { var d = mkItem(t, Math.random() < 0.5 ? "t" : "c", rs[n]); items.push({ d: d, opts: options(d) }); } });
      if (!items.length) return; qs = items; i = 0; score = 0; show();
    });
  }

  // ── 🎧 유튜브에서 듣기: 곡 이름으로 유튜브 검색 결과를 앱 밖(새 창·유튜브 앱)에서 열어요. 앱 안에서 재생하거나 소리를 받아 오지 않아요(유튜브 약관).
  //    정답을 고른 뒤에만 보여서 정답이 미리 드러나지 않아요. 온라인 기능을 끈 판(fgOnline.enabled=false)에서는 보이지 않아요.
  var ytOk = function () { return !!window.fgOnline && fgOnline.enabled; };
  var TITLES = Object.keys(DATA.W).sort(function (a, b) { return b.length - a.length; });
  function ytUrl(t) { var w = DATA.W[t], q = (w ? w[0] + " " : "") + String(t).replace(/[‘’'"“”]/g, ""); return "https://www.youtube.com/results?search_query=" + encodeURIComponent(q); }
  function ytLink(t) { return '<a class="cbtn yt" href="' + esc(ytUrl(t)) + '" target="_blank" rel="noopener noreferrer">🎧 유튜브에서 듣기</a>'; }
  function songOf(d) { if (!d) return null; if (d.tt && DATA.W[d.tt]) return d.tt; var s = [d[0], d[1], d[4]].join(" "); for (var k = 0; k < TITLES.length; k++) if (s.indexOf(TITLES[k]) >= 0) return TITLES[k]; return null; }
  function addYt() {
    if (!ytOk()) return; var c = qs && qs[i], t = c && songOf(c.d), q = document.getElementById("q"); if (!t || !q || q.querySelector(".yt")) return;
    q.insertAdjacentHTML("beforeend", '<div class="row2 ytrow">' + ytLink(t) + '<small>‘' + esc(t) + "’ 연주를 유튜브에서 찾아요(앱 밖에서 열려요)</small></div>");
  }

  // ── 모음: 곡 옆에 ▶ 듣기 단추(눌렀을 때 허락·검색·재생)
  function decorateGal() {
    var list = document.getElementById("list"); if (!list) return;
    list.querySelectorAll("li").forEach(function (li) {
      if (li.dataset.cls) return; li.dataset.cls = "1"; var b = li.querySelector("b"); if (!b) return;
      if (ytOk() && DATA.W[b.textContent]) b.insertAdjacentHTML("afterend", ytLink(b.textContent).replace("🎧 유튜브에서 듣기", "🎧 유튜브"));
      if (!DATA.P[b.textContent]) return;
      var btn = document.createElement("button"); btn.type = "button"; btn.className = "gplay"; btn.textContent = "▶ 듣기"; btn.dataset.t = b.textContent; b.insertAdjacentElement("afterend", btn);
    });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".gplay"); if (!b) return;
    var t = b.dataset.t, on = b.classList.contains("on"); document.querySelectorAll(".gplay.on").forEach(function (x) { x.classList.remove("on"); x.textContent = "▶ 듣기"; }); stopAudio();
    if (on) return;
    if (!(saved && saved[t]) && window.fgOnline && !fgOnline.on() && !fgOnline.ask(CONSENT)) return;
    askSave(); b.textContent = "⏳ 찾는 중…";
    getAudio(t).then(function (r) {
      if (!r) { b.textContent = "음원 없음"; b.disabled = true; return; }
      var a = player(r, Infinity); b.classList.add("on"); b.textContent = "⏹ 멈추기"; saveOne(t, r);
      a.addEventListener("ended", function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; });
      a.addEventListener("error", function () { b.classList.remove("on"); b.textContent = "불러오지 못함"; });
      var p = a.play(); if (p && p.catch) p.catch(function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; });
    });
  });

  function boot() {
    loadWrong();
    try { saved = JSON.parse(lsGet(SAVED) || "null"); if (!saved || typeof saved !== "object" || !Object.keys(saved).length) saved = null; } catch (e) { saved = null; }
    if (isQuiz) {
      buildBar();
      var oS = start, oShow = show, oPick = pick;
      start = function () { oS(); if (mode !== "off") mix(); };
      show = function () { oShow(); decorateQ(); };
      pick = function (k) { if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k); if (c && c.d.aud) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } record(c, ok); addCard(); } addYt(); };
      var m = lsGet(MK); if ((m === "mix" || m === "only") && (savedCount() || online())) { mode = m; drawBar(); start(); }
    } else if (isGal) {
      injectCss();
      new MutationObserver(decorateGal).observe(document.getElementById("list"), { childList: true }); decorateGal();
    }
  }
  addEventListener("online", function () { if (bar) drawBar(); }); addEventListener("offline", function () { if (bar) drawBar(); });
  addEventListener("pagehide", stopAudio);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
