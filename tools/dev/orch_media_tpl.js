/* 오답 노트용 오케스트라 그림·소리 보기(set45.py가 만들어요 — 직접 고치지 마세요). 오답 노트(wrong-notes.html)가 틀린 그림·배치도·소리 문제를 다시 보여 줄 때 써요.
   m = {k:"i", id} 악기 그림 / {k:"s", n} 배치도 / {k:"a", id} 악기 소리(선택·온라인, 파일은 저장하지 않아요) */
(function () {
  "use strict";
  var M = /*MEDIA*/null; M.N = M.N || {}; Object.keys(M.NAME).forEach(function (nm) { M.N[M.NAME[nm]] = nm; });
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var ASK = "🔊 악기 소리를 인터넷에서 불러와요.\n\n· 위키미디어·인터넷 아카이브 서버에 이 기기의 인터넷 주소가 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 저작권이 끝났거나 CC BY·CC BY-SA 표시가 있는 소리만 쓰고 녹음한 사람과 라이선스를 보여 줘요.\n· 소리 파일은 이 폰에 저장하지 않아요.\n\n켤까요?";
  var cur = null;
  function stop() { if (cur) { try { cur.a.pause(); } catch (e) {} if (cur.b) cur.b.textContent = "🔊 소리 듣기"; cur = null; } }
  function sound(box, id, blind) {
    var names = M.SND[id]; if (!names || !names.length) { box.innerHTML = '<small class="muted">이 악기는 들려줄 소리가 없어요.</small>'; return; }
    box.innerHTML = '<button type="button" class="wmb">🔊 소리 듣기</button><small class="wmcr"' + (blind ? " hidden" : "") + "></small>";
    var b = box.querySelector("button"), cr = box.querySelector("small");
    b.addEventListener("click", function () {
      if (cur && cur.b === b) { stop(); return; } stop();
      if (!window.fgOnline || !fgOnline.enabled) { cr.hidden = false; cr.textContent = "이 기능은 인터넷에서만 쓸 수 있어요."; return; }
      if (!fgOnline.on() && !fgOnline.ask(ASK)) { cr.hidden = false; cr.textContent = "소리를 들으려면 묻는 창에서 ‘확인’을 눌러 인터넷 사용을 허용해 주세요."; return; } if (navigator.onLine === false) { cr.hidden = false; cr.textContent = "인터넷이 연결되면 들을 수 있어요."; return; }
      b.textContent = "⏳ 찾는 중…"; cr.hidden = false; cr.textContent = "인터넷에서 소리를 찾고 있어요(서버가 느리면 몇 초 걸려요)…"; var me = { b: b, a: new Audio() }; cur = me;
      fgOnline.audioFiles(names, 0, true).then(function (list) {
        var k = 0;
        (function next() {
          if (cur !== me) return; var r = list[k++]; if (!r) { b.textContent = "🔊 다시 눌러 보기"; cr.hidden = false; cr.textContent = "소리를 불러오지 못했어요. 위키 서버가 느리거나 막혔을 수 있어요. 잠시 뒤 다시 눌러 보세요. 악기 도감(" + (M.N[id] || "") + ")에서도 들을 수 있어요."; cur = null; return; }
          var a = new Audio(), started = false, tm = setTimeout(function () { if (!started) { a.src = ""; next(); } }, 12000); a.preload = "auto"; me.a = a;
          a.addEventListener("playing", function () { started = true; clearTimeout(tm); b.textContent = "⏸ 멈추기";
            var who = r.artist && !/no machine-readable/i.test(r.artist) ? r.artist : "", ttl = M.SNDT && M.SNDT[r.title];
            cr.innerHTML = (ttl ? "🎵 " + esc(ttl) + "<br>" : "") + "녹음: " + (who ? esc(who) + " · " : "") + (r.licenseUrl ? '<a href="' + esc(r.licenseUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(r.license) + "</a>" : esc(r.license)) + ' · <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">원본</a>'; });
          a.addEventListener("error", function () { if (!started) { clearTimeout(tm); next(); } });
          a.addEventListener("ended", function () { if (cur === me) { b.textContent = "🔁 다시 듣기"; cur = null; } });
          a.src = r.src; var p = a.play(); if (p && p.catch) p.catch(function () { if (!started) { clearTimeout(tm); next(); } });
        })();
      }).catch(function () { if (cur === me) { b.textContent = "🔊 다시 눌러 보기"; cr.hidden = false; cr.textContent = "소리를 불러오지 못했어요. 인터넷 연결을 확인해 주세요."; cur = null; } });
    });
  }
  // 그림을 누르면 크게 보여 줘요(다시 누르면 닫혀요)
  function zoom(svgHtml) {
    var v = document.createElement("div"); v.setAttribute("role", "dialog"); v.style.cssText = "position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.82);display:flex;align-items:center;justify-content:center;padding:16px";
    v.innerHTML = '<div style="background:var(--surface,#fff);border-radius:16px;padding:12px;max-width:96vw;max-height:92vh;overflow:auto;width:min(96vw,640px)">' + svgHtml + '<p style="margin:8px 0 0;text-align:center;font-size:.85rem;color:var(--muted,#666)">화면을 누르면 닫혀요</p></div>';
    v.querySelectorAll("svg").forEach(function (s) { s.style.cssText = "width:100%;height:auto;max-height:78vh;display:block"; });
    v.addEventListener("click", function () { v.remove(); }); document.body.appendChild(v);
  }
  // 예전에 기록돼 그림·소리 정보(m)가 없는 오케스트라 퀴즈 오답에서, 문제 글과 정답(악기 이름)으로 그림·소리·배치도를 찾아 줘요
  function infer(x) {
    if (!x || x.m || !/^orchestra-quiz/.test(x.f || "")) return x && x.m || null; var q = String(x.q || ""), id = M.NAME[x.a], n = (q.match(/(\d+)번 자리/) || [])[1];
    if (/소리 문제|🔊 소리|소리 \d+번/.test(q)) return id ? { k: "a", id: id } : null;
    if (/배치도/.test(q) && n) return { k: "s", n: +n };
    if (/그림/.test(q) && id) return { k: "i", id: id };
    return null;
  }
  // ── 실제 사진(선택, 온라인): 악기 도감·퀴즈와 같은 방법으로 위키백과 사진을 찾아요(이 폰에 저장해 둔 사진이 있으면 그것을 먼저 써요)
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function savedPhoto(id) {
    try { var sv = JSON.parse(lsGet("orch-saved-v1") || "null"), e = sv && sv[id]; if (!e || !("caches" in window)) return Promise.resolve(null);
      return caches.open("fg-orch-saved-v1").then(function (c) { return c.match(e.src); }).then(function (r) { return r ? r.blob() : null; }).then(function (b) { return b ? { src: URL.createObjectURL(b), e: e } : null; }).catch(function () { return null; }); } catch (er) { return Promise.resolve(null); }
  }
  function onlinePhoto(id) {
    var ins = M.P[id]; if (!ins || !window.fgOnline || !fgOnline.on() || navigator.onLine === false) return Promise.resolve(null);
    var probe = function (src) { return new Promise(function (ok) { var im = new Image(), tm = setTimeout(function () { ok(false); }, 15000); im.onload = function () { clearTimeout(tm); ok(true); }; im.onerror = function () { clearTimeout(tm); ok(false); }; im.src = src; }); };
    var pack = function (r) { return r ? { src: r.src, e: { page: r.filePage || r.page, title: r.title, license: r.license, licenseUrl: r.licenseUrl, artist: r.artist, label: r.label } } : null; };
    var viaFiles = ins.files && fgOnline.commonsPhoto ? fgOnline.commonsPhoto(ins.files, true).then(function (r) { return r ? probe(r.src).then(function (ok) { return ok ? r : null; }) : null; }).then(pack) : Promise.resolve(null);
    var keys = ["en:" + (ins.wiki || "").replace(/ /g, "_")], toks = [ins.tok];
    if (ins.ko) { keys.push("ko:" + ins.ko.replace(/ /g, "_")); toks.push(ins.ko); } if (ins.de) { keys.push("de:" + ins.de.replace(/ /g, "_")); toks.push(ins.de); }
    return viaFiles.then(function (pin) { if (pin) return pin; if (ins.files) return null; return fgOnline.wikiImage(keys, toks, "악기", { cc: true }).then(pack); });
  }
  function creditHtml(e) { var lic = e.licenseUrl ? '<a href="' + esc(e.licenseUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(e.license) + "</a>" : esc(e.license); return "📷 사진: " + (e.artist ? esc(e.artist) + " · " : "") + lic + ' · <a href="' + esc(e.page) + '" target="_blank" rel="noopener noreferrer">원본 보기</a>'; }
  function addPhoto(box, id, svgHtml) {
    if (!M.P[id]) return;
    var bar = document.createElement("div"); bar.className = "wmph"; box.appendChild(bar); var start;
    var show = function (r) {   // 사진으로 바꿔 보여 줘요(누르면 크게, 단추로 그림과 바꿔 볼 수 있어요)
      var im = new Image(); im.alt = (M.N[id] || "악기") + " 사진"; im.style.cssText = "width:min(300px,86vw);height:auto;max-height:300px;object-fit:contain;border-radius:12px;display:block;margin:0 auto;cursor:zoom-in";
      im.onload = function () { var img = box.querySelector(".wmimg"); if (!img) return; img.innerHTML = ""; img.appendChild(im); img.onclick = function (e) { e.stopPropagation(); zoomImg(im.src); };
        bar.innerHTML = '<small class="wmcr" style="display:block">' + creditHtml(r.e) + '</small><button type="button" class="wmb sm">✏️ 그림으로 보기</button>'; var showing = true;
        bar.querySelector("button").onclick = function () { showing = !showing; if (showing) { img.innerHTML = ""; img.appendChild(im); this.textContent = "✏️ 그림으로 보기"; } else { img.innerHTML = svgHtml; this.textContent = "📷 사진으로 보기"; } }; };
      im.onerror = function () { bar.innerHTML = '<small class="wmcr" style="display:block">사진을 불러오지 못했어요(서버가 느리거나 막혔을 수 있어요). 아래 그림은 직접 그린 것이에요.</small><button type="button" class="wmb sm">📷 다시 찾기</button>'; bar.querySelector("button").onclick = start; }; im.src = r.src;
    };
    start = function () { bar.innerHTML = '<small class="wmcr" style="display:block">📷 사진을 찾고 있어요…</small>'; savedPhoto(id).then(function (r) { return r || onlinePhoto(id); }).then(function (r) { if (r) show(r); else bar.innerHTML = '<small class="wmcr" style="display:block">알맞은 사진을 못 찾았어요. 아래 그림은 직접 그린 것이에요.</small><button type="button" class="wmb sm">📷 다시 찾기</button>'; if (!r) bar.querySelector("button").onclick = start; }); };
    if (window.fgOnline && fgOnline.on() && lsGet("orch-photo-v1") !== "0") start();
    else { bar.innerHTML = '<button type="button" class="wmb sm">📷 실제 사진 보기</button>'; bar.querySelector("button").onclick = function () { if (!window.fgOnline || !fgOnline.enabled) return; if (!fgOnline.on() && !fgOnline.ask("📷 악기 실제 사진을 인터넷에서 불러와요.\n\n· 위키백과·위키미디어 서버에 이 기기의 인터넷 주소가 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 사진가와 라이선스를 사진 아래에 보여 줘요. 사진은 저장하지 않아요.\n\n켤까요?")) return; try { localStorage.setItem("orch-photo-v1", "1"); } catch (e) {} start(); }; }
  }
  function zoomImg(src) { zoom('<img src="' + esc(src) + '" alt="" style="width:100%;height:auto;max-height:78vh;object-fit:contain;display:block">'); }

  window.fgOrchMedia = {
    infer: infer,
    ok: function (m) { return !!m && ((m.k === "i" && !!M.SVG[m.id]) || (m.k === "s" && !!M.SEAT[String(m.n)]) || (m.k === "a" && !!M.SND[m.id])); },
    render: function (box, m, blind) {
      stop(); box.innerHTML = "";
      if (m.k === "i" || m.k === "s") { var h = m.k === "i" ? M.SVG[m.id] : M.SEAT[String(m.n)]; box.innerHTML = '<div class="wmimg" role="button" tabindex="0" style="cursor:zoom-in">' + h + '</div><small class="muted" style="display:block;margin-top:4px">그림을 누르면 크게 보여요</small>'; var wi = box.querySelector(".wmimg"); wi.onclick = function () { zoom(h); }; if (m.k === "i") addPhoto(box, m.id, h); }
      else if (m.k === "a") sound(box, m.id, !!blind);
      var iid = m.k === "s" ? null : m.id; if (iid && M.EN && M.EN[iid]) box.insertAdjacentHTML("beforeend", '<a class="wmyt" href="https://www.youtube.com/results?search_query=' + encodeURIComponent(M.EN[iid] + " solo classical music") + '" target="_blank" rel="noopener noreferrer"' + (blind ? " hidden" : "") + ">🎧 유튜브에서 " + esc(M.N[iid] || "") + " 독주곡 듣기</a>");
    },
    reveal: function (root) { (root || document).querySelectorAll(".wmcr").forEach(function (x) { if (x.textContent) x.hidden = false; }); (root || document).querySelectorAll(".wmyt").forEach(function (x) { x.hidden = false; }); },
    stop: stop
  };
})();
