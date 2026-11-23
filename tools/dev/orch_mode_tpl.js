/* 오케스트라 퀴즈 그림·사진·정답 카드·힌트 — orchestra-quiz.html 전용.
   악기는 실제 사진을 우선 보여 줘요(🌐 사진). 사진은 이 저장소(GitHub)나 서버에 두지 않고, 사용자가 켜면 쓰는 폰이 위키백과·위키미디어 커먼즈에서 직접 불러와요.
   사진은 공개 도메인·CC0·CC BY·CC BY-SA 표시가 있는 것만 쓰고(비영리·변경금지 제한 사진은 제외), 사진 아래에 사진가·라이선스·원본 링크를 꼭 보여 줘요. 맞는 사진이 없거나 인터넷이 없으면 직접 그린 단순한 그림(SVG)이 나와요.
   폰에 저장할지는 사용자가 따로 골라요(기본 묻기·언제든 끄고 켜기). 이 파일은 tools/dev/set45.py 가 만들어요(직접 고치지 말고 tools/dev/orch_mode_tpl.js 와 set45.py 를 고치세요). */
(function () {
  "use strict";
  var DATA = /*DATA*/null;   // I: 악기 정보, SVG: 악기 그림, SEAT: 배치도 그림, IMG: {질문: ["i", 악기id] | ["s", 번호]}, INFO: {질문: 악기id}
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  var PK = "orch-photo-v1", AS = "orch-autosave-v1", SV = "orch-saved-v1", CACHE = "fg-orch-saved-v1", photo = false, hintUsed = false, saved = null, blobUrls = {};
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var CONSENT = "🌐 악기 사진을 켜요.\n\n· 인터넷에서 악기 실제 사진을 불러와요. 공개 도메인·CC0·CC BY·CC BY-SA 라이선스 사진만 쓰고, 사진 아래에 사진가와 라이선스를 보여 줘요. 맞는 사진이 없으면 그림이 나와요.\n· 불러올 때 이 기기의 인터넷 주소가 위키백과·위키미디어 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n\n켤까요?";
  var SAVEASK = "📥 본 사진을 이 폰에 저장할까요?\n\n· 저장하면 다음부터 인터넷 없이도 사진이 나와요(사진 1장 약 50~100KB).\n· 저장하지 않으면 볼 때마다 인터넷이 필요해요(없으면 그림이 나와요).\n· 나중에 언제든 바꾸거나 지울 수 있어요.\n\n[확인] 저장해요   [취소] 저장하지 않고 보기만 해요";
  var online = function () { return !!window.fgOnline && fgOnline.enabled && fgOnline.on() && navigator.onLine !== false; };
  var savedCount = function () { return saved ? Object.keys(saved).length : 0; };

  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.sm{padding:6px 10px;font-size:.85rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}.amode small{color:var(--muted,#666)}" +
      ".oimg{display:flex;flex-direction:column;align-items:center;gap:4px;margin:0 0 10px}.oimg svg,.oimg img{width:min(240px,74vw);height:auto;border-radius:12px;display:block}.oimg img{max-height:280px;object-fit:contain;background:#f6efe0}.oimg small{color:var(--muted,#666);font-size:.76rem;text-align:center;line-height:1.4}" +
      ".acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}";
    document.head.appendChild(st);
  }
  var bar;
  function drawBar() {
    var on = online(), n = savedCount();
    var h = '<b>📷 악기 그림 보기</b><div class="row"><button type="button" data-p="1" class="' + (photo ? "on" : "") + '"' + (window.fgOnline && fgOnline.enabled ? "" : " disabled") + '>📷 실제 사진(온라인)</button><button type="button" data-p="0" class="' + (photo ? "" : "on") + '">🎨 그림</button></div><small>' +
      (photo ? (on ? "인터넷에서 악기 실제 사진을 불러와요(사진가·라이선스를 사진 아래에 보여 줘요). 맞는 사진이 없으면 그림이 나와요." : (n ? "지금은 인터넷이 없어서 이 폰에 저장된 사진(" + n + "장)만 나오고, 나머지는 그림이에요." : "지금은 인터넷이 없어서 그림으로 나와요.")) : "직접 그린 단순한 그림이에요. 인터넷이 필요 없어요.") + " · 저장된 사진 " + n + "장</small>";
    if (photo && window.fgOnline && fgOnline.enabled) h += '<div class="row"><button type="button" class="sm" data-p="auto">💾 본 사진 자동 저장: ' + (lsGet(AS) === "1" ? "켜짐" : "꺼짐") + "</button>" + (n ? '<button type="button" class="sm" data-p="clear">🗑️ 저장한 사진 지우기</button>' : "") + "<small>끄면 저장 없이 보기만 해요.</small></div>";
    bar.innerHTML = h;
  }
  function askSave() { if (lsGet(AS) !== null) return; var yes = false; try { yes = window.confirm(SAVEASK); } catch (e) {} lsSet(AS, yes ? "1" : "0"); }
  function clearSaved() {
    try { if (!window.confirm("이 폰에 저장한 악기 사진 " + savedCount() + "장을 지울까요? (다시 보면 또 저장돼요)")) return; } catch (e) {}
    try { if ("caches" in window) caches.delete(CACHE); } catch (e) {} try { localStorage.removeItem(SV); } catch (e) {} saved = null; blobUrls = {}; drawBar();
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "orchmode";
    var hh = document.querySelector("h1"); if (hh) hh.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return; var v = b.dataset.p;
      if (v === "auto") { lsSet(AS, lsGet(AS) === "1" ? "0" : "1"); drawBar(); return; }
      if (v === "clear") { clearSaved(); return; }
      if (v === "1") { if (!(window.fgOnline && fgOnline.ask(CONSENT))) return; photo = true; askSave(); } else photo = false;
      lsSet(PK, photo ? "1" : "0"); drawBar(); if (isQuiz) { var cur = qs && qs[i]; if (cur && !locked) show(); } else decorateGal(true);
    });
    drawBar();
  }

  // ── 사진 하나 얻기: ① 이 폰에 저장한 것 → ② 온라인(공개 도메인·CC0·CC BY·CC BY-SA)
  function fromSaved(id) {
    var e = saved && saved[id]; if (!e || !("caches" in window)) return Promise.resolve(null);
    if (blobUrls[id]) return Promise.resolve({ src: blobUrls[id], e: e });
    return caches.open(CACHE).then(function (c) { return c.match(e.src); }).then(function (r) { return r ? r.blob() : null; }).then(function (b) { if (!b) return null; blobUrls[id] = URL.createObjectURL(b); return { src: blobUrls[id], e: e }; }).catch(function () { return null; });
  }
  function fromOnline(id) {
    var ins = DATA.I[id]; if (!online()) return Promise.resolve(null);
    return fgOnline.wikiImage(["en:" + ins.wiki.replace(/ /g, "_")], [ins.tok], "악기", { cc: true }).then(function (r) { return r ? { src: r.src, e: { src: r.src, page: r.filePage || r.page, title: r.title, license: r.license, licenseUrl: r.licenseUrl, artist: r.artist, label: r.label }, online: true } : null; });
  }
  function getPhoto(id) { return fromSaved(id).then(function (r) { return r || fromOnline(id); }); }
  function saveOne(id, r) {
    if (!r.online || lsGet(AS) !== "1" || (saved && saved[id]) || !("caches" in window)) return;
    fetch(r.src, { credentials: "omit", referrerPolicy: "no-referrer" }).then(function (resp) { if (!resp.ok) throw 0; return caches.open(CACHE).then(function (c) { return c.put(r.src, resp); }); })
      .then(function () { saved = saved || {}; saved[id] = r.e; lsSet(SV, JSON.stringify(saved)); if (bar) drawBar(); }).catch(function () {});
  }
  function credit(e) {
    var lic = e.licenseUrl ? '<a href="' + esc(e.licenseUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(e.license) + "</a>" : esc(e.license);
    return "📷 사진: " + (e.artist ? esc(e.artist) + " · " : "") + lic + ' · <a href="' + esc(e.page) + '" target="_blank" rel="noopener noreferrer">원본 보기(' + esc(e.label || "위키미디어") + ")</a>";
  }

  function decorate() {
    var cur = qs && qs[i]; hintUsed = false; if (!cur) return; var q = document.getElementById("q"), m = DATA.IMG[cur.d[0]]; if (!q) return;
    if (m) {
      var fig = document.createElement("div"); fig.className = "oimg"; fig.innerHTML = m[0] === "i" ? DATA.SVG[m[1]] : DATA.SEAT[String(m[1])]; q.insertBefore(fig, q.firstChild);
      if (m[0] === "i" && photo) {
        var id = m[1], myQ = cur.d[0];
        getPhoto(id).then(function (r) {
          if (!r || !qs || !qs[i] || qs[i].d[0] !== myQ || !fig.isConnected) return;
          var im = new Image(); im.alt = "악기 사진";
          im.onload = function () { if (!fig.isConnected) return; fig.innerHTML = ""; fig.appendChild(im); var c = document.createElement("small"); c.innerHTML = credit(r.e); fig.appendChild(c); saveOne(id, r); };
          im.src = r.src;
        });
      }
    }
    var iid = DATA.INFO[cur.d[0]];
    if (iid && m && m[0] === "i") {   // 힌트는 그림 문제에만: 악기군 → 연주 방법
      var ins2 = DATA.I[iid], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
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


  // ── 악기 도감: 카드의 그림을 사진으로 바꿔요(보이는 카드만 불러와요)
  var io = null;
  function decorateGal(reset) {
    var list = document.getElementById("list"); if (!list) return;
    list.querySelectorAll(".ar[data-id]").forEach(function (c) {
      if (reset) { var ic = c.querySelector(".ic"); if (ic) ic.innerHTML = DATA.SVG[c.dataset.id]; var cr = c.querySelector(".cr"); if (cr) cr.remove(); delete c.dataset.ph; }
      if (!photo || c.dataset.ph) return; c.dataset.ph = "1";
      if (!io && "IntersectionObserver" in window) io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); fillCard(e.target); } }); }, { rootMargin: "200px" });
      if (io) io.observe(c); else fillCard(c);
    });
  }
  function fillCard(c) {
    var id = c.dataset.id; getPhoto(id).then(function (r) {
      if (!r || !c.isConnected || !photo) return; var im = new Image(); im.alt = DATA.I[id].name + " 사진";
      im.onload = function () { var ic = c.querySelector(".ic"); if (!ic || !c.isConnected) return; ic.innerHTML = ""; ic.appendChild(im); var cr = document.createElement("small"); cr.className = "cr"; cr.innerHTML = credit(r.e); c.appendChild(cr); saveOne(id, r); };
      im.src = r.src;
    });
  }

  function boot() {
    try { saved = JSON.parse(lsGet(SV) || "null"); if (!saved || typeof saved !== "object" || !Object.keys(saved).length) saved = null; } catch (e) { saved = null; }
    var pref = lsGet(PK);
    if (pref === null && window.fgOnline && fgOnline.enabled) {   // 처음 한 번: 실제 사진을 쓸지 물어요
      photo = !!fgOnline.ask(CONSENT); lsSet(PK, photo ? "1" : "0"); if (photo) askSave();
    } else photo = pref === "1" && !!(window.fgOnline && fgOnline.on());
    buildBar();
    if (isGal) { new MutationObserver(function () { decorateGal(false); }).observe(document.getElementById("list"), { childList: true }); decorateGal(false); return; }
    var oShow = show, oPick = pick;
    show = function () { oShow(); decorate(); };
    pick = function (k) {
      if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k);
      if (c) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } addCard(c); }
    };
    if (qs && qs.length) show();
  }
  addEventListener("online", function () { if (bar) drawBar(); }); addEventListener("offline", function () { if (bar) drawBar(); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
