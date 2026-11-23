/* 클래식 듣고 맞히기 — 클래식 작곡가 퀴즈(classic-quiz.html)와 작곡가별 모음(classic-gallery.html) 공용.
   음원은 앱 안의 classic-audio/ (tools/dev/music_fetch.py 가 PC에서 위키미디어 커먼즈의 공개 도메인·CC0 녹음을 받아 20초 조각으로 잘라 둠)만 써요. 인터넷이 필요 없어요.
   이 파일은 tools/dev/set44.py 가 만들어요(직접 고치지 말고 tools/dev/classic_mode_tpl.js 와 set44.py 를 고치세요). */
(function () {
  "use strict";
  var DATA = /*DATA*/null;   // W: {곡: [작곡가, 연도, 갈래, 시대, 유명도, 나라, 작곡가id]}, C: [[작곡가, 시대, id]], AMBIG
  var MK = "classic-listen-mode-v1", WK = "classic-wrong-v1";
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  var idx = null, mode = "off";   // off | mix | only
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var shuffle = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; };
  var has = function (t) { return !!(idx && idx[t] && DATA.W[t]); };
  var audioTitles = function () { return Object.keys(DATA.W).filter(has); };
  var credit = function (e) { return '🎧 음원: <a href="' + esc(e.p) + '" target="_blank" rel="noopener noreferrer">위키미디어 커먼즈 「' + esc(e.t) + "」</a> (" + esc(e.l) + ")"; };

  // ── 소리 재생(한 번에 하나만)
  var cur = null;
  function player(title) {
    if (cur) { try { cur.pause(); } catch (e) {} }
    var a = new Audio("classic-audio/" + idx[title].f); a.preload = "auto"; cur = a; return a;
  }
  function stopAudio() { if (cur) { try { cur.pause(); } catch (e) {} } }

  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}" +
      ".amode small{color:var(--muted,#666)}.aplay{display:flex;flex-direction:column;align-items:center;gap:6px;margin:0 0 10px}.aplay button{border:0;border-radius:999px;background:var(--accent,#c4552b);color:var(--accent-fg,#fff);font-size:1.15rem;font-weight:700;padding:14px 26px;min-width:200px}" +
      ".aplay small{color:var(--muted,#666)}.acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}" +
      ".gplay{margin-left:6px;border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:2px 10px;font-size:.8rem}.gplay.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent}";
    document.head.appendChild(st);
  }
  var bar;
  function drawBar() {
    var n = audioTitles().length;
    var h = '<b>🎧 듣고 맞히기</b><div class="row">' +
      '<button type="button" data-m="off" class="' + (mode === "off" ? "on" : "") + '">📴 글로만</button>' +
      '<button type="button" data-m="mix" class="' + (mode === "mix" ? "on" : "") + '"' + (n ? "" : " disabled") + ">🔀 섞어서(한 판 최대 3개)</button>" +
      '<button type="button" data-m="only" class="' + (mode === "only" ? "on" : "") + '"' + (n ? "" : " disabled") + ">🎧 듣기 문제만</button></div>";
    h += "<small>" + (n ? "인터넷 없이 앱에 들어 있는 짧은 음원(약 20초)으로 곡을 맞혀요. 소리가 나오니 주변을 확인하세요. 듣기 문제 " + n + "곡." : "음원을 아직 준비 중이에요.") + "</small>";
    if (isQuiz && wrongList.length && mode !== "off") h += '<div class="row"><button type="button" id="clsreview" data-m="review">' + reviewLabel() + "</button><small>틀린 곡만 다시 들어요. 맞히면 목록에서 빠져요.</small></div>";
    bar.innerHTML = h;
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "clsmode";
    var hh = document.querySelector("h1"); if (hh) hh.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return;
      if (b.dataset.m === "review") startReview(); else { mode = b.dataset.m; lsSet(MK, mode); drawBar(); stopAudio(); start(); }
    });
    drawBar();
  }

  // ── 문제 만들기: 곡 → 작곡가 또는 곡 → 제목(같은 곡이 둘 다 나오지 않게 번갈아)
  var composers = function () { return DATA.C; };
  function wrongComposers(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []), mine = w[6], era = w[3], lvl = w[4];
    var pool = composers().filter(function (c) { return c[2] !== mine && ban.indexOf(c[2]) < 0; });
    var same = shuffle(pool.filter(function (c) { return c[1] === era; })), diff = shuffle(pool.filter(function (c) { return c[1] !== era; }));
    var n = lvl === 1 ? 0 : lvl === 2 ? 1 : 2, out = same.slice(0, n); diff.concat(same.slice(n)).some(function (c) { if (out.length >= 3) return true; if (out.indexOf(c) < 0) out.push(c); return false; });
    return out.slice(0, 3).map(function (c) { return c[0]; });
  }
  function wrongTitles(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []);
    var pool = Object.keys(DATA.W).filter(function (x) { var v = DATA.W[x]; return x !== t && v[6] !== w[6] && ban.indexOf(v[6]) < 0 && v[4] <= 2 && (DATA.AMBIG[x] || []).indexOf(w[6]) < 0; });
    return shuffle(pool).slice(0, 3);
  }
  function mkItem(t, kind) {
    var w = DATA.W[t], d;
    if (kind === "t") d = ["이 곡의 제목은 무엇일까요?", t, wrongTitles(t), w[3], w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    else d = ["이 곡의 작곡가는 누구일까요?", w[0], wrongComposers(t), w[3], "‘" + t + "’ — " + w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    d.tt = t; d.aud = idx[t]; d.kind = kind; return d;
  }
  var roundId = 0;
  function mix() {
    var id = ++roundId, want = mode === "only" ? 10 : 3, first = i === 0 && !locked;
    var pool = shuffle(audioTitles().filter(function (t) { var w = DATA.W[t]; return (!lv || w[4] === lv) && (cat === "전체" || w[3] === cat); })).slice(0, want);
    if (!pool.length || !qs || qs.length < 2) return;
    var slots = []; for (var k = first ? 0 : i + 1; k < qs.length; k++) slots.push(k);
    slots = (first ? [0].concat(shuffle(slots.slice(1))) : shuffle(slots)).slice(0, pool.length);
    slots.forEach(function (pos, n) { var d = mkItem(pool[n], Math.random() < 0.5 ? "t" : "c"); qs[pos] = { d: d, opts: options(d) }; });
    if (first && slots.indexOf(0) >= 0) show();
  }
  var hintUsed = false;
  function decorateQ() {
    var c = qs && qs[i]; stopAudio(); hintUsed = false; if (!c || !c.d.aud) return;
    var q = document.getElementById("q"), box = document.createElement("div"); box.className = "aplay";
    box.innerHTML = '<button type="button">▶ 소리 듣기</button><small>눌러서 듣고, 몇 번이든 다시 들을 수 있어요(약 20초).</small>';
    var btn = box.querySelector("button"), a = player(c.d.tt);
    a.addEventListener("ended", function () { btn.textContent = "🔁 다시 듣기"; });
    a.addEventListener("error", function () { btn.textContent = "소리를 불러오지 못했어요"; btn.disabled = true; });
    btn.addEventListener("click", function () { if (!a.paused && !a.ended) { a.pause(); btn.textContent = "▶ 이어서 듣기"; } else { if (a.ended) a.currentTime = 0; var p = a.play(); if (p && p.catch) p.catch(function () {}); btn.textContent = "⏸ 멈추기"; } });
    q.insertBefore(box, q.firstChild);
    // 힌트: 시대·나라 → 갈래 (쓰면 맞혀도 0.5점)
    var m = DATA.W[c.d.tt], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
    var hbtn = hb.querySelector("button"), out = hb.querySelector("div"), lvl = 0;
    hbtn.addEventListener("click", function () { if (locked) return; hintUsed = true; lvl++; out.hidden = false; out.textContent = lvl === 1 ? "시대: " + m[3] + (c.d.kind === "c" ? " · 갈래: " + m[2] : "") : "시대: " + m[3] + " · 갈래: " + m[2] + " · 작곡가의 나라: " + m[5]; if (lvl >= 2) hbtn.disabled = true; else hbtn.textContent = "💡 힌트 한 번 더"; });
    q.appendChild(hb);
  }
  function addCard() {
    var c = qs && qs[i]; if (!c || !c.d.aud) return; var m = DATA.W[c.d.tt], q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><b>‘' + esc(c.d.tt) + "’</b><span>" + esc(m[0]) + " (" + esc(m[5]) + ")</span><span>" + esc(m[3]) + " · " + esc(m[2]) + " · " + esc(m[1]) + '</span></div><span class="note">' + credit(c.d.aud) + "</span>");
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
    var ts = shuffle(wrongList.filter(has)).slice(0, 10); if (!ts.length) return;
    start(); roundId++;
    qs = ts.map(function (t) { var d = mkItem(t, Math.random() < 0.5 ? "t" : "c"); return { d: d, opts: options(d) }; }); i = 0; score = 0; show();
  }

  // ── 모음: 곡 옆에 ▶ 단추
  function decorateGal() {
    var list = document.getElementById("list"); if (!list || !idx) return;
    list.querySelectorAll("li").forEach(function (li) {
      if (li.dataset.cls) return; li.dataset.cls = "1"; var b = li.querySelector("b"); if (!b) return; var t = b.textContent; if (!has(t)) return;
      var btn = document.createElement("button"); btn.type = "button"; btn.className = "gplay"; btn.textContent = "▶ 듣기"; btn.dataset.t = t; b.insertAdjacentElement("afterend", btn);
    });
  }
  var playing = null;
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".gplay"); if (!b) return;
    var t = b.dataset.t, on = b.classList.contains("on"); document.querySelectorAll(".gplay.on").forEach(function (x) { x.classList.remove("on"); x.textContent = "▶ 듣기"; }); stopAudio();
    if (on) return; var a = player(t); b.classList.add("on"); b.textContent = "⏹ 멈추기";
    a.addEventListener("ended", function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; }); a.play().catch(function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; });
  });

  function boot() {
    loadWrong();
    fetch("classic-audio/index.json").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (j) {
      idx = j && typeof j === "object" && Object.keys(j).length ? j : null;
      if (isQuiz) {
        buildBar();
        var oS = start, oShow = show, oPick = pick;
        start = function () { oS(); if (mode !== "off") mix(); };
        show = function () { oShow(); decorateQ(); };
        pick = function (k) { if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k); if (c && c.d.aud) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } record(c, ok); addCard(); } };
        var m = lsGet(MK); if (idx && (m === "mix" || m === "only")) { mode = m; drawBar(); start(); }
      } else if (isGal) {
        new MutationObserver(decorateGal).observe(document.getElementById("list"), { childList: true }); decorateGal();
      }
    });
  }
  addEventListener("pagehide", stopAudio);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
