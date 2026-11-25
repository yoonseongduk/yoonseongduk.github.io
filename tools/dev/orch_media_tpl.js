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
  window.fgOrchMedia = {
    infer: infer,
    ok: function (m) { return !!m && ((m.k === "i" && !!M.SVG[m.id]) || (m.k === "s" && !!M.SEAT[String(m.n)]) || (m.k === "a" && !!M.SND[m.id])); },
    render: function (box, m, blind) {
      stop(); box.innerHTML = "";
      if (m.k === "i" || m.k === "s") { var h = m.k === "i" ? M.SVG[m.id] : M.SEAT[String(m.n)]; box.innerHTML = '<div class="wmimg" role="button" tabindex="0" style="cursor:zoom-in">' + h + '</div><small class="muted" style="display:block;margin-top:4px">그림을 누르면 크게 보여요</small>'; box.querySelector(".wmimg").addEventListener("click", function () { zoom(h); }); }
      else if (m.k === "a") sound(box, m.id, !!blind);
    },
    reveal: function (root) { (root || document).querySelectorAll(".wmcr").forEach(function (x) { if (x.textContent) x.hidden = false; }); },
    stop: stop
  };
})();
