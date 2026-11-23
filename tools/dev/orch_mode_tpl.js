/* 오케스트라 퀴즈 그림·정답 카드·힌트 — orchestra-quiz.html 전용.
   기본 그림은 직접 그린 SVG(이 파일 안의 글자)라 인터넷 없이 항상 나와요. 🌐 사진을 켜면(사용자 선택) 위키백과의 공개 도메인·CC0 사진을 불러와서 그림 대신 보여 주고, 없으면 그림이 그대로 나와요(사진은 저장하지 않고 볼 때마다 불러와요).
   이 파일은 tools/dev/set45.py 가 만들어요(직접 고치지 말고 tools/dev/orch_mode_tpl.js 와 set45.py 를 고치세요). */
(function () {
  "use strict";
  var DATA = /*DATA*/null;   // I: 악기 정보, SVG: 악기 그림, SEAT: 배치도 그림, IMG: {질문: ["i", 악기id] | ["s", 번호]}, INFO: {질문: 악기id}
  var PK = "orch-photo-v1", photo = false, hintUsed = false;
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var CONSENT = "🌐 악기 사진을 켜요.\n\n· 인터넷에서 저작권이 끝난(공개 도메인·CC0) 악기 사진을 불러와요. 없는 악기는 그림이 그대로 나와요.\n· 불러올 때 이 기기의 인터넷 주소가 위키백과·위키미디어 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 사진은 저장하지 않고 볼 때마다 불러와요.\n\n켤까요?";
  var online = function () { return !!window.fgOnline && fgOnline.enabled && fgOnline.on() && navigator.onLine !== false; };

  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}.amode small{color:var(--muted,#666)}" +
      ".oimg{display:flex;flex-direction:column;align-items:center;gap:4px;margin:0 0 10px}.oimg svg,.oimg img{width:min(220px,70vw);height:auto;border-radius:12px;display:block}.oimg img{max-height:260px;object-fit:contain;background:#f6efe0}.oimg small{color:var(--muted,#666);font-size:.78rem;text-align:center}" +
      ".acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}";
    document.head.appendChild(st);
  }
  var bar;
  function drawBar() {
    bar.innerHTML = '<b>🎷 그림 보기</b><div class="row"><button type="button" data-p="0" class="' + (photo ? "" : "on") + '">🎨 그림(기본)</button><button type="button" data-p="1" class="' + (photo ? "on" : "") + '"' + (window.fgOnline && fgOnline.enabled ? "" : " disabled") + '>🌐 사진(온라인)</button></div><small>' +
      (photo ? (online() ? "공개 도메인 악기 사진을 인터넷에서 불러와요. 없는 악기는 그림으로 나와요." : "지금은 인터넷이 없어서 그림으로 나와요.") : "직접 그린 단순한 그림이에요. 인터넷이 필요 없어요.") + "</small>";
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "orchmode";
    var hh = document.querySelector("h1"); if (hh) hh.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return;
      if (b.dataset.p === "1") { if (!(window.fgOnline && fgOnline.ask(CONSENT))) return; photo = true; } else photo = false;
      lsSet(PK, photo ? "1" : "0"); drawBar(); var cur = qs && qs[i]; if (cur && !locked) { show(); }
    });
    drawBar();
  }

  function decorate() {
    var cur = qs && qs[i]; hintUsed = false; if (!cur) return; var q = document.getElementById("q"), m = DATA.IMG[cur.d[0]]; if (!q) return;
    if (m) {
      var fig = document.createElement("div"); fig.className = "oimg"; fig.innerHTML = m[0] === "i" ? DATA.SVG[m[1]] : DATA.SEAT[String(m[1])]; q.insertBefore(fig, q.firstChild);
      if (m[0] === "i" && photo && online()) {
        var ins = DATA.I[m[1]], myQ = cur.d[0];
        fgOnline.wikiImage(["en:" + ins.wiki.replace(/ /g, "_")], [ins.tok], "악기").then(function (r) {
          if (!r || !qs || !qs[i] || qs[i].d[0] !== myQ || !fig.isConnected) return;
          var im = new Image(); im.alt = "악기 사진"; im.onload = function () { if (!fig.isConnected) return; fig.innerHTML = ""; fig.appendChild(im); var c = document.createElement("small"); c.innerHTML = '📷 <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">' + esc(r.label || "위키백과") + " 「" + esc(r.title) + "」</a> (" + esc(r.license) + ")"; fig.appendChild(c); };
          im.src = r.src;
        });
      }
    }
    var id = DATA.INFO[cur.d[0]];
    if (id && m && m[0] === "i") {   // 힌트는 그림 문제에만: 악기군 → 연주 방법
      var ins2 = DATA.I[id], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
      var btn = hb.querySelector("button"), out = hb.querySelector("div"), lvl = 0;
      btn.addEventListener("click", function () { if (locked) return; hintUsed = true; lvl++; out.hidden = false; out.textContent = lvl === 1 ? "악기군: " + ins2.fam : "악기군: " + ins2.fam + " · 연주 방법: " + ins2.how; if (lvl >= 2) btn.disabled = true; else btn.textContent = "💡 힌트 한 번 더"; });
      q.appendChild(hb);
    }
  }
  function addCard(cur) {
    var id = DATA.INFO[cur.d[0]]; if (!id) return; var a = DATA.I[id], q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><b>' + esc(a.name) + " <small>(" + esc(a.en) + ")</small></b><span>" + esc(a.fam) + " · " + esc(a.rng) + " 소리 · 도감 " + a.n + "번</span><span>🎼 " + esc(a.how) + "</span><span>" + esc(a.desc) + "</span><span>🎵 " + esc(a.use) + "</span></div>");
  }

  function boot() {
    photo = lsGet(PK) === "1" && !!(window.fgOnline && fgOnline.on());
    buildBar();
    var oShow = show, oPick = pick;
    show = function () { oShow(); decorate(); };
    pick = function (k) {
      if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k);
      if (c) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } addCard(c); }
    };
    if (qs && qs.length) show();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
