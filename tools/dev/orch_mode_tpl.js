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
      ".oimg{display:flex;flex-direction:column;align-items:center;gap:4px;margin:0 0 10px}.oimg svg,.oimg img{width:min(240px,74vw);height:auto;border-radius:12px;display:block}.oimg img{max-height:280px;object-fit:contain;background:#f6efe0}.prow{display:flex;align-items:flex-end;justify-content:center;gap:6px;width:100%}.prow figure{margin:0;text-align:center;min-width:0;display:flex;flex-direction:column;align-items:center}.prow img,.prow svg{height:auto;width:auto;max-width:none;background:#f6efe0;border-radius:8px;display:block}.prow figcaption{max-width:90px}.prow .hl img,.prow .hl svg{outline:3px solid #e8742a}.prow figcaption{font-size:.7rem;line-height:1.3;color:var(--muted,#666)}.prows details{font-size:.72rem;color:var(--muted,#666);text-align:left;width:100%}.prows details a{word-break:break-all}.oimg.cmp{align-self:stretch;width:100%}.oimg.cmp svg{width:100%;max-width:330px;height:auto;border-radius:12px}.acard .oimg{align-self:stretch}.oimg small{color:var(--muted,#666);font-size:.76rem;text-align:center;line-height:1.4}" +
      ".spec{display:grid;grid-template-columns:4.2em 1fr;gap:2px 8px;font-size:.84rem;margin-top:6px;padding-top:6px;border-top:1px dashed var(--line,#ccc);text-align:left}.spec dt{color:var(--muted,#666)}.spec dd{margin:0}.acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}";
    st.textContent += ".oimg img,.oimg svg,.prow img,.prow svg,.ar .ic img,.ar .ic svg{cursor:zoom-in}" + "#aview{position:fixed;inset:0;z-index:9999;background:#000e;display:flex;flex-direction:column;user-select:none;-webkit-user-select:none}#aview .vb{display:flex;gap:6px;align-items:center;justify-content:flex-end;flex-wrap:wrap;padding:8px 10px}#aview .vb button{border:0;border-radius:999px;padding:8px 13px;font-size:.95rem;background:#fff;color:#111}#aview .vz{color:#fff;font-size:.85rem;min-width:3.2em;text-align:center}#aview .vi{flex:1;overflow:hidden;position:relative;touch-action:none;display:flex;align-items:center;justify-content:center}#aview .vi img{max-width:100%;max-height:100%;object-fit:contain;transform-origin:center center;will-change:transform;cursor:grab}#aview .vc{color:#fff;font-size:.8rem;padding:8px 12px;text-align:center}#aview .vh{color:#ccc}";
    st.textContent += ".osnd{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:8px 0 0}.osnd button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:7px 12px;font-size:.9rem;font-family:inherit}.osnd button.on{background:var(--accent,#3a6);color:#fff;border-color:transparent}.osnd small{font-size:.75rem;color:var(--muted,#666);flex-basis:100%;overflow-wrap:anywhere}.osnd small a{color:inherit}";
    document.head.appendChild(st);
  }
  var bar;
  function drawBar() {
    var on = online(), n = savedCount();
    var h = '<b>📷 악기 그림 보기</b><div class="row"><button type="button" data-p="1" class="' + (photo ? "on" : "") + '"' + (window.fgOnline && fgOnline.enabled ? "" : " disabled") + '>📷 실제 사진(온라인)</button><button type="button" data-p="0" class="' + (photo ? "" : "on") + '">🎨 그림</button></div><small>' +
      (photo ? (on ? "인터넷에서 악기 실제 사진을 불러와요(사진가·라이선스를 사진 아래에 보여 줘요). 맞는 사진이 없으면 그림이 나와요." : (n ? "지금은 인터넷이 없어서 이 폰에 저장된 사진(" + n + "장)만 나오고, 나머지는 그림이에요." : "지금은 인터넷이 없어서 그림으로 나와요.")) : "직접 그린 단순한 그림이에요. 인터넷이 필요 없어요.") + " · 저장된 사진 " + n + " / 전체 " + Object.keys(DATA.I).length + "종 · <a href=\"offline-media.html\">📊 저장 현황</a></small>";
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
    var probe = function (src) { return new Promise(function (ok) { var im = new Image(), tm = setTimeout(function () { ok(false); }, 15000); im.onload = function () { clearTimeout(tm); ok(true); }; im.onerror = function () { clearTimeout(tm); ok(false); }; im.src = src; }); };
    var viaFiles = ins.files && fgOnline.commonsPhoto ? fgOnline.commonsPhoto(ins.files, true).then(function (r) { return r ? probe(r.src).then(function (okLoad) { return okLoad ? r : null; }) : null; }).then(function (r) { return r ? { src: r.src, e: { src: r.src, page: r.filePage || r.page, title: r.title, license: r.license, licenseUrl: r.licenseUrl, artist: r.artist, label: r.label }, online: true } : null; }) : Promise.resolve(null);
    var keys = ["en:" + ins.wiki.replace(/ /g, "_")], toks = [ins.tok];   // A 영어 위키백과 → B 한국어 → C 독일어 → (이어서 커먼즈 검색·Openverse·클리블랜드)
    if (ins.ko) { keys.push("ko:" + ins.ko.replace(/ /g, "_")); toks.push(ins.ko); } if (ins.de) { keys.push("de:" + ins.de.replace(/ /g, "_")); toks.push(ins.de); }
    return viaFiles.then(function (pin) { if (pin) return pin; if (ins.files) return null; /* 사진을 직접 정해 둔 악기는 실패하면 그림을 보여 줘요(콜라주·악보 같은 엉뚱한 사진을 막아요) */ return fgOnline.wikiImage(keys, toks, "악기", { cc: true }).then(function (r) { return r ? { src: r.src, e: { src: r.src, page: r.filePage || r.page, title: r.title, license: r.license, licenseUrl: r.licenseUrl, artist: r.artist, label: r.label }, online: true } : null; }); });
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

  // 악기 그림 한 칸을 그려요: 기본은 직접 그린 그림, 사진 모드면 사진으로 바꾸고 출처를 붙여요
  function paint(fig, id, still) {
    fig.innerHTML = DATA.SVG[id];
    if (!photo) return;
    getPhoto(id).then(function (r) {
      if (!r || !fig.isConnected || !still()) return;
      var im = new Image(); im.alt = "악기 사진";
      im.onload = function () { if (!fig.isConnected || !still()) return; fig.innerHTML = ""; fig.appendChild(im); var c = document.createElement("small"); c.innerHTML = credit(r.e); fig.appendChild(c); saveOne(id, r); };
      im.src = r.src;
    });
  }

  // ── 현악기 네 가지 사진을 같은 크기 칸에 나란히(모양 비교). 크기 비율은 위의 비교 그림이 맡고, 사진은 자르거나 고치지 않고 그대로 보여 줘요.
  var STRS = [["violin", 60], ["viola", 67], ["cello", 120], ["doublebass", 180]];

  // 사진 높이를 악기의 실제 길이(cm)에 비례하게 맞춰요(사진마다 악기가 높이의 93~97%를 채워서 대략 정확해요). 사진은 자르지 않고 크기만 바꿔 보여 줘요.
  function fitRow(wrap) {
    var row = wrap.querySelector(".prow"); if (!row) return; var figs = row.querySelectorAll("figure"), sum = 0, items = [];
    figs.forEach(function (f, k) { var el = f.querySelector("img,svg"), cm = STRS[k][1], asp = 0.7; if (el && el.tagName === "IMG" && el.naturalHeight) asp = el.naturalWidth / el.naturalHeight; else if (el) asp = 1; items.push({ el: el, cm: cm, asp: asp }); sum += asp * cm; });
    var avail = (wrap.clientWidth || 300) - 6 * 3, K = Math.min(1.05, avail / sum);
    items.forEach(function (x) { if (!x.el) return; x.el.style.height = Math.round(x.cm * K) + "px"; x.el.style.width = Math.round(x.cm * K * x.asp) + "px"; });
  }
  var isStr = function (id) { return STRS.some(function (s) { return s[0] === id; }); };
  function photoRow(hl, names, still) {
    if (!photo) return Promise.resolve(null);
    return Promise.all(STRS.map(function (s) { return getPhoto(s[0]).then(function (r) { return r ? new Promise(function (res) { var im = new Image(); im.alt = DATA.I[s[0]].name + " 사진"; im.onload = function () { res({ id: s[0], cm: s[1], im: im, r: r }); }; im.onerror = function () { res(null); }; im.src = r.src; }) : null; }); })).then(function (rows) {
      if (!still() || rows.every(function (x) { return !x; })) return null;
      var wrap = document.createElement("div"); wrap.className = "prows"; var row = document.createElement("div"); row.className = "prow"; var cr = [];
      STRS.forEach(function (s, k) {
        var f = document.createElement("figure"); if (s[0] === hl) f.className = "hl"; var x = rows[k];
        if (x) { f.appendChild(x.im); cr.push((names ? DATA.I[s[0]].name + ": " : (k + 1) + "번: ") + credit(x.r.e).replace("📷 사진: ", "")); saveOne(s[0], x.r); } else f.innerHTML = DATA.SVG[s[0]];
        var c = document.createElement("figcaption"); c.textContent = names ? DATA.I[s[0]].name + " 약 " + s[1] + "cm" : (s[0] === hl ? "이 악기" : "·"); f.appendChild(c); row.appendChild(f);
      });
      wrap.appendChild(row); var d = document.createElement("details"); d.innerHTML = "<summary>📷 사진 출처 " + cr.length + "건</summary>" + cr.map(function (x) { return "<div>" + x + "</div>"; }).join(""); wrap.appendChild(d); return wrap;
    });
  }
  var specHtml = function (a) { return a.spec && a.spec.length ? '<dl class="spec">' + a.spec.map(function (x) { return "<dt>" + esc(x[0]) + "</dt><dd>" + esc(x[1]) + "</dd>"; }).join("") + "</dl>" : ""; };
  function decorate() {
    var cur = qs && qs[i]; hintUsed = false; if (!cur) return; var q = document.getElementById("q"), key = cur.d[0], m = DATA.IMG[key], showId = DATA.SHOW[key]; if (!q) return;
    if (m && m[0] === "s") { var f0 = document.createElement("div"); f0.className = "oimg"; f0.innerHTML = DATA.SEAT[String(m[1])]; q.insertBefore(f0, q.firstChild); }
    else if (m || showId) {   // 그림 문제(이름 맞히기) 또는 이름이 나온 악기의 그림·사진
      var fig = document.createElement("div"); fig.className = "oimg"; q.insertBefore(fig, q.firstChild);
      var sid = m ? m[1] : showId;
      if (!m && showId) { var sp0 = document.createElement("div"); sp0.className = "acard"; sp0.innerHTML = "<b>📐 사양</b>" + specHtml(DATA.I[showId]); q.insertBefore(sp0, q.children[1] || null); }
      paint(fig, sid, function () { return qs && qs[i] && qs[i].d[0] === key; });
      if (DATA.CMP[sid]) { var cf2 = document.createElement("div"); cf2.className = "oimg cmp"; cf2.innerHTML = DATA.CMP[sid] + (isStr(sid) ? "<small>📏 크기 비교: 주황 점이 이 악기예요(비슷하게 생긴 현악기끼리, 사람 키와 함께)</small>" : "<small>📏 크기 비교: 주황 점이 이 악기예요(막대 길이가 실제 길이예요, 바순·콘트라바순은 접은 높이)</small>"); fig.insertAdjacentElement("afterend", cf2); (isStr(sid) ? photoRow(sid, false, function () { return qs && qs[i] && qs[i].d[0] === key; }) : Promise.resolve(null)).then(function (w) { if (w && cf2.isConnected) { var lab = document.createElement("small"); lab.textContent = "📷 실제 사진(높이를 실제 길이에 맞춰 보여 줘요, 주황 테두리가 이 악기)"; var box = document.createElement("div"); box.className = "oimg cmp"; box.appendChild(w); box.appendChild(lab); cf2.insertAdjacentElement("afterend", box); fitRow(w); } }); }
    }
    var iid = DATA.INFO[key];
    if (iid && m && m[0] === "i") {   // 힌트는 그림 문제에만: 악기군 → 연주 방법
      var ins2 = DATA.I[iid], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
      var btn = hb.querySelector("button"), out = hb.querySelector("div"), lvl = 0;
      btn.addEventListener("click", function () { if (locked) return; hintUsed = true; lvl++; out.hidden = false; out.textContent = lvl === 1 ? "악기군: " + ins2.fam : lvl === 2 ? "악기군: " + ins2.fam + " · 연주 방법: " + ins2.how : "악기군: " + ins2.fam + " · 연주 방법: " + ins2.how + " · 사양: " + (ins2.spec || []).slice(0, 2).map(function (x) { return x[0] + " " + x[1]; }).join(" / "); if (lvl >= 3) btn.disabled = true; else btn.textContent = "💡 힌트 한 번 더"; });
      q.appendChild(hb);
    }
  }
  function addCard(cur) {
    var key = cur.d[0], id = DATA.INFO[key]; if (!id) return; var a = DATA.I[id], q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><div class="oimg"></div><b>' + esc(a.name) + " <small>(" + esc(a.en) + ")</small></b><span>" + esc(a.fam) + " · " + esc(a.rng) + " 소리 · 도감 " + a.n + "번</span><span>🎼 " + esc(a.how) + "</span><span>" + esc(a.desc) + "</span><span>🎵 " + esc(a.use) + "</span>" + specHtml(a) + (DATA.CMPN[id] ? '<div class="oimg cmp">' + DATA.CMPN[id] + "<small>📏 실제 크기 비교(약 길이)</small></div>" : "") + "</div>");
    if (DATA.CMPN[id] && isStr(id)) { var cardEl = q.querySelector(".acard"); photoRow(id, true, function () { return qs && qs[i] && qs[i].d[0] === key; }).then(function (w) { if (w && cardEl.isConnected) { var box = document.createElement("div"); box.className = "oimg cmp"; box.appendChild(w); var lab = document.createElement("small"); lab.textContent = "📷 사진 높이를 실제 길이에 맞춰 보여 줘요(대략)"; box.appendChild(lab); cardEl.appendChild(box); fitRow(w); } }); }
    var cf = q.querySelector(".acard .oimg"), already = q.querySelector(":scope > .oimg");
    if (already && DATA.IMG[key] && DATA.IMG[key][0] === "i") cf.remove();   // 그림 문제는 위에 이미 그림이 있어요
    else paint(cf, id, function () { return qs && qs[i] && qs[i].d[0] === key; });
  }

  // 한 판(10문제)에 그림 문제가 모자라면 그림 문제를 더 섞어 넣어요(최소 4개)
  var MINIMG = 4;
  function biasImages() {
    if (!qs || qs.length < 2 || typeof D === "undefined") return;
    var isImg = function (d) { var m = DATA.IMG[d[0]]; return !!m && m[0] === "i"; };
    var have = qs.filter(function (x) { return isImg(x.d); }).length; if (have >= MINIMG) return;
    var used = {}; qs.forEach(function (x) { used[x.d[0]] = 1; });
    var pool = D.filter(function (d, n) { return isImg(d) && !used[d[0]] && (!lv || lvOf(n) === lv) && !isFlag(d[0]) && (cat === "전체" || d[3] === cat); });
    if (!pool.length) return;
    var slots = []; qs.forEach(function (x, k) { if (!isImg(x.d)) slots.push(k); });
    for (var k = slots.length - 1; k > 0; k--) { var j = Math.floor(Math.random() * (k + 1)), tmp = slots[k]; slots[k] = slots[j]; slots[j] = tmp; }
    for (var k2 = pool.length - 1; k2 > 0; k2--) { var j2 = Math.floor(Math.random() * (k2 + 1)), t2 = pool[k2]; pool[k2] = pool[j2]; pool[j2] = t2; }
    for (var x = 0; x < Math.min(MINIMG - have, pool.length, slots.length); x++) qs[slots[x]] = { d: pool[x], opts: options(pool[x]) };
    show();
  }

  // ── 악기 도감: 카드의 그림을 사진으로 바꿔요(보이는 카드만 불러와요)
  var io = null;
  function decorateGal(reset) {
    var list = document.getElementById("list"); if (!list) return;
    list.querySelectorAll(".ar[data-id]").forEach(function (c) {
      addSound(c);
      if (reset) { var ic = c.querySelector(".ic"); if (ic) ic.innerHTML = DATA.SVG[c.dataset.id]; var cr = c.querySelector(".cr"); if (cr) cr.remove(); delete c.dataset.ph; }
      if (!photo || c.dataset.ph) return; c.dataset.ph = "1";
      if (!io && "IntersectionObserver" in window) io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); fillCard(e.target); } }); }, { rootMargin: "200px" });
      if (io) io.observe(c); else fillCard(c);
    });
  }
  // ── 🔊 악기 소리 듣기(도감, 2026-11-24 사용자 요청): 악기마다 미리 골라 둔 커먼즈 녹음(그 악기 혼자 연주한 독주곡 우선, 없으면 악기 소리 견본,
  //    공개 도메인·CC0만, 오래된 녹음 제외·음질 분석 통과)을 누를 때 인터넷에서 불러와 들려줘요. 소리 파일은 저장소·서버에 두지 않아요.
  var SCONSENT = "🔊 악기 소리를 들어요.\n\n· 인터넷(위키미디어 커먼즈)에서 저작권이 끝난(공개 도메인·CC0) 녹음만 불러와 들려줘요.\n· 듣는 동안 이 기기의 인터넷 주소가 위키미디어 서버에 전달돼요(이 앱은 아무것도 모으지 않아요).\n· 인터넷 데이터를 써요(곡 하나 약 1~5MB).\n\n계속할까요?";
  var snd = null;
  function stopSnd() { if (snd) { try { snd.a.pause(); } catch (e) {} if (snd.b) { snd.b.classList.remove("on"); snd.b.textContent = "🔊 소리 듣기"; } snd = null; } }
  function addSound(c) {
    var id = c.dataset.id, names = DATA.SND && DATA.SND[id]; if (!names || !names.length || c.querySelector(".osnd") || !(window.fgOnline && fgOnline.enabled)) return;
    var w = document.createElement("div"); w.className = "osnd"; w.innerHTML = '<button type="button">🔊 소리 듣기</button><small hidden></small>';
    var top = c.querySelector(".top"); if (top) top.insertAdjacentElement("afterend", w); else c.appendChild(w);
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".osnd button"); if (!b) return; var c = b.closest(".ar"), id = c && c.dataset.id, cr = b.parentNode.querySelector("small");
    if (snd && snd.b === b) { if (!snd.a.paused) { snd.a.pause(); b.textContent = "▶ 이어서 듣기"; } else { snd.a.play(); b.textContent = "⏸ 멈추기"; } return; }
    stopSnd(); if (!fgOnline.ask(SCONSENT)) return;
    if (navigator.onLine === false) { b.textContent = "인터넷 없음"; setTimeout(function () { b.textContent = "🔊 소리 듣기"; }, 2500); return; }
    b.textContent = "⏳ 찾는 중…"; var me = { b: b, a: new Audio() }; snd = me;
    fgOnline.audioFiles(DATA.SND[id], 0, true).then(function (list) {
      var k = 0;
      (function tryNext() {
        if (snd !== me) return;
        var r = list[k++]; if (!r) { b.textContent = "소리를 못 찾았어요"; snd = null; setTimeout(function () { b.textContent = "🔊 소리 듣기"; }, 3000); return; }
        var a = new Audio(); a.preload = "auto"; me.a = a; var started = false, tm = setTimeout(function () { if (!started) { a.src = ""; tryNext(); } }, 12000);
        a.addEventListener("playing", function () { started = true; clearTimeout(tm); if (snd !== me) { a.pause(); return; } b.classList.add("on"); b.textContent = "⏸ 멈추기";
          cr.hidden = false; var who = r.artist && !/no machine-readable/i.test(r.artist) ? r.artist : ""; var tt = DATA.SNDT && DATA.SNDT[r.title]; cr.innerHTML = (tt ? "<b>🎵 곡: " + esc(tt) + "</b><br>" : "") + "🔊 녹음: " + (who ? esc(who) + " · " : "") + (r.licenseUrl ? '<a href="' + esc(r.licenseUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(r.license) + "</a>" : esc(r.license)) + ' · <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">원본 보기(위키미디어 커먼즈)</a>'; });
        a.addEventListener("error", function () { if (!started) { clearTimeout(tm); tryNext(); } });
        a.addEventListener("ended", function () { if (snd === me) { b.classList.remove("on"); b.textContent = "🔁 다시 듣기"; snd = null; } });
        a.src = r.src; var p = a.play(); if (p && p.catch) p.catch(function () { if (!started) { clearTimeout(tm); tryNext(); } });
      })();
    }).catch(function () { if (snd === me) { b.textContent = "🔊 소리 듣기"; snd = null; } });
  });
  function fillCard(c) {
    var id = c.dataset.id;
    if (DATA.CMP[id] && isStr(id)) photoRow(id, true, function () { return c.isConnected && photo; }).then(function (w) { if (w && c.isConnected && !c.querySelector(".prows")) { c.appendChild(w); fitRow(w); } }); getPhoto(id).then(function (r) {
      if (!r || !c.isConnected || !photo) return; var im = new Image(); im.alt = DATA.I[id].name + " 사진";
      im.onload = function () { var ic = c.querySelector(".ic"); if (!ic || !c.isConnected) return; ic.innerHTML = ""; ic.appendChild(im); var cr = document.createElement("small"); cr.className = "cr"; cr.innerHTML = credit(r.e); c.appendChild(cr); saveOne(id, r); };
      im.src = r.src;
    });
  }


  // ── 그림·사진 크게 보기: 누르면 전체 화면으로 열려요. 두 손가락 벌리기·＋/－·마우스 휠·두 번 누르기로 확대(최대 8배), 끌어서 이동, 확대하면 더 큰 사진(1280px)으로 바뀌어요.
  var ZMAX = 8;
  function bigSrc(src) {
    if (/\/(?:lossy-page1-)?\d+px-[^\/]+$/.test(src || "") && /upload\.wikimedia\.org/.test(src)) return src.replace(/\/((?:lossy-page1-)?)\d+px-([^\/]+)$/, "/$11280px-$2");
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
    var el = e.target.closest && e.target.closest(".oimg img, .oimg svg, .prow img, .prow svg, .ar .ic img, .ar .ic svg"); if (!el || el.closest("#aview")) return;
    var src, cap = "", oi = el.closest(".oimg"), card = el.closest(".ar"), sm = oi ? oi.querySelector("small") : (card ? card.querySelector(".cr") : null), cname = card && card.querySelector("h2") ? card.querySelector("h2").childNodes[card.querySelector("h2").childNodes.length - 2].textContent.replace("★", "").trim() : "";
    if (el.tagName.toLowerCase() === "img") src = el.currentSrc || el.src;
    else { var cl = el.cloneNode(true), vb = el.viewBox && el.viewBox.baseVal; cl.setAttribute("width", 900); cl.setAttribute("height", vb && vb.width ? Math.round(900 * vb.height / vb.width) : 900); src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(new XMLSerializer().serializeToString(cl)); }
    if (!src) return;
    var fig = el.closest("figure"), name = fig && fig.querySelector("figcaption") ? fig.querySelector("figcaption").textContent : "";
    cap = ((name || cname) ? "<b>" + esc(name || cname) + "</b><br>" : "") + (sm && !fig ? sm.innerHTML : (el.getAttribute("alt") || el.getAttribute("aria-label") || ""));
    openViewer(src, cap);
  });

  function boot() {
    try { saved = JSON.parse(lsGet(SV) || "null"); if (!saved || typeof saved !== "object" || !Object.keys(saved).length) saved = null; } catch (e) { saved = null; }
    var pref = lsGet(PK);
    if (pref === null && window.fgOnline && fgOnline.enabled) {   // 처음 한 번: 실제 사진을 쓸지 물어요
      photo = !!fgOnline.ask(CONSENT); lsSet(PK, photo ? "1" : "0"); if (photo) askSave();
    } else photo = pref === "1" && !!(window.fgOnline && fgOnline.on());
    buildBar();
    if (isGal) { new MutationObserver(function () { decorateGal(false); }).observe(document.getElementById("list"), { childList: true }); decorateGal(false); return; }
    var oShow = show, oPick = pick, oStart = start;
    start = function () { oStart(); biasImages(); };
    show = function () { oShow(); decorate(); };
    pick = function (k) {
      if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k);
      if (c) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } addCard(c); }
    };
    if (qs && qs.length) { biasImages(); show(); }
  }
  addEventListener("online", function () { if (bar) drawBar(); }); addEventListener("offline", function () { if (bar) drawBar(); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
