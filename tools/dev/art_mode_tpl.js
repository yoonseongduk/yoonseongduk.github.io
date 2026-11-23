/* 명화 그림 모드 — 명화 작가 퀴즈(art-quiz.html)와 명화 작가별 모음(art-gallery.html) 공용.
   그림 보기 3가지: 📴 글로만(기본·오프라인) / 🌐 온라인(저작권이 끝난 명화만 위키백과에서 불러옴) / 📦 내장(art-img/ 에 받아 둔 그림).
   이 파일은 tools/dev/set43.py 가 만들어요(직접 고치지 말고 tools/dev/art_mode_tpl.js 와 set43.py 를 고치세요).
   안전장치: 온라인 그림은 ① 위키백과 항목 설명에 작가 이름이 있고 ② 그림 파일이 공개 도메인으로 표시돼 있을 때만 보여요. 하나라도 틀리면 그림 없이 글로 나와요. */
(function () {
  "use strict";
  var DATA = /*DATA*/null;
  var MK = "art-img-mode-v1", mode = "text", local = null;
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var norm = function (s) { return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  var shuffle = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; };

  // ── 그림 하나 얻기: 통과하면 {src, page, title, license}, 아니면 null
  function preload(src) { return new Promise(function (res) { var im = new Image(), t = setTimeout(function () { res(false); }, 9000); im.onload = function () { clearTimeout(t); res(true); }; im.onerror = function () { clearTimeout(t); res(false); }; im.src = src; }); }
  function getImage(title) {
    var w = DATA.W[title]; if (!w) return Promise.resolve(null);
    var p;
    if (mode === "local") { var e = local && local[title]; p = Promise.resolve(e ? { src: "art-img/" + e.f, page: e.p, title: e.t || title, license: e.l || "공개 도메인" } : null); }
    else if (mode === "online" && window.fgOnline && fgOnline.on()) p = fgOnline.wikiImage(w.k, w.t.map(norm));
    else p = Promise.resolve(null);
    return p.then(function (r) { return r ? preload(r.src).then(function (ok) { return ok ? r : null; }) : null; });
  }
  var has = function (title) { return !!DATA.W[title] && (mode === "online" || (mode === "local" && !!local && !!local[title])); };
  var credit = function (r) { return '🖼️ 그림 출처: <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">위키백과 「' + esc(r.title) + "」</a> (" + esc(r.license) + ")"; };

  // ── 화면 위 모드 선택
  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}.amode button:disabled{opacity:.45;cursor:default}" +
      ".amode small{color:var(--muted,#666)}.aimg{margin:0 0 10px}.aimg img,.gf img{display:block;max-width:100%;max-height:300px;margin:0 auto;border-radius:12px;background:#0001}.gf{margin:6px 0 2px}.gf figcaption{font-size:.78rem;color:var(--muted,#666);text-align:center;margin-top:4px}";
    document.head.appendChild(st);
  }
  var bar, note;
  function drawBar() {
    var n = local ? Object.keys(local).length : 0, online = !!window.fgOnline && fgOnline.enabled;
    bar.querySelector(".row").innerHTML =
      '<button type="button" data-m="text" class="' + (mode === "text" ? "on" : "") + '">📴 글로만</button>' +
      '<button type="button" data-m="online" class="' + (mode === "online" ? "on" : "") + '"' + (online ? "" : " disabled") + ">🌐 온라인 그림</button>" +
      '<button type="button" data-m="local" class="' + (mode === "local" ? "on" : "") + '"' + (n ? "" : " disabled") + ">📦 내장 그림" + (n ? " (" + n + "장)" : " (준비 중)") + "</button>";
    note.textContent = mode === "text" ? "인터넷 없이 글로만 풀어요. 그림을 보려면 위에서 골라요." :
      mode === "online" ? (navigator.onLine === false ? "지금은 인터넷이 없어서 글로만 나와요." : "인터넷에서 저작권이 끝난 명화만 불러와요(위키백과·위키미디어 서버에 이 기기의 주소가 전달돼요). 못 불러오면 글로 나와요.") :
      "앱에 저장된 그림이에요. 그림 아래에 출처가 나와요.";
  }
  function setMode(m) {
    if (m === "online" && !(window.fgOnline && fgOnline.ask("🌐 온라인 그림을 켜요.\n\n· 인터넷에서 저작권이 끝난 명화만 불러와요.\n· 불러올 때 이 기기의 인터넷 주소가 위키백과·위키미디어 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 언제든 '글로만'으로 끌 수 있어요.\n\n켤까요?"))) return;
    mode = m; lsSet(MK, m); drawBar(); if (isQuiz) start(); else decorateAll(true);
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "artmode";
    bar.innerHTML = "<b>🖼️ 그림 보기</b><div class=\"row\"></div><small id=\"artnote\"></small>"; note = bar.querySelector("#artnote");
    var h = document.querySelector("h1"); if (h) h.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) { var b = e.target.closest("[data-m]"); if (b && !b.disabled) setMode(b.dataset.m); });
    drawBar();
  }

  // ── 퀴즈: 라운드에 그림 문제를 최대 3개 섞기
  var roundId = 0;
  function mix() {
    var id = ++roundId;
    var pool = shuffle(DATA.Q.filter(function (q) { return (!lv || q[4] === lv) && (cat === "전체" || q[3] === cat) && has(q[5]); })).slice(0, 9);
    if (!pool.length) return;
    Promise.all(pool.map(function (q) { return getImage(q[5]).then(function (r) { return r ? { q: q, r: r } : null; }); })).then(function (all) {
      var ok = all.filter(Boolean); if (id !== roundId || !ok.length || !qs || qs.length < 2) return;
      var slots = []; for (var k = i + 1; k < qs.length; k++) slots.push(k);
      slots = shuffle(slots).slice(0, Math.min(3, ok.length));
      slots.forEach(function (pos, n) {
        var q = ok[n].q, d = [q[0], q[1], q[2], q[3], q[6]]; d.img = ok[n].r; d.alt = "‘" + q[5] + "’의 작가는 누구일까요?";
        qs[pos] = { d: d, opts: options(d) };
      });
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

  // ── 시작
  function boot() {
    buildBar();
    if (isQuiz) {
      var oS = start, oShow = show, oPick = pick;
      start = function () { oS(); if (mode !== "text") mix(); };
      show = function () { oShow(); decorateQ(); };
      pick = function (k) { oPick(k); creditQ(); };
    } else if (isGal) {
      new MutationObserver(function () { decorateAll(false); }).observe(document.getElementById("list"), { childList: true });
    }
    var saved = lsGet(MK);
    fetch("art-img/index.json").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (idx) {
      local = idx && typeof idx === "object" && Object.keys(idx).length ? idx : null;
      if (saved === "local" && local) mode = "local"; else if (saved === "online" && window.fgOnline && fgOnline.on()) mode = "online";
      drawBar(); if (mode !== "text") { if (isQuiz) start(); else decorateAll(false); }
    });
  }
  addEventListener("online", function () { if (bar) drawBar(); }); addEventListener("offline", function () { if (bar) drawBar(); });   // 인터넷 연결 상태가 바뀌면 안내 문구도 바꿔요
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
