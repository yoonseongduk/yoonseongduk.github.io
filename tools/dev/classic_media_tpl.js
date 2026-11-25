/* 오답 노트용 클래식 소리 듣기(set44.py가 만들어요 — 직접 고치지 마세요). m = {k:"c", t:"곡 제목"} — 틀린 듣고 맞히기 문제의 소리를 오답 노트에서 다시 들려줘요.
   음원은 저장소에 없고, 온라인 기능을 켠 폰이 위키미디어·인터넷 아카이브에서 직접 받아 들려줘요(공개 도메인·CC0·CC BY·CC BY-SA만, 녹음한 사람·라이선스를 보여 줘요). */
(function () {
  "use strict";
  var P = /*MEDIA*/null, cur = null;
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var ASK = "🎧 클래식 소리를 인터넷에서 불러와요.\n\n· 위키미디어·인터넷 아카이브 서버에 이 기기의 인터넷 주소가 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 저작권이 끝났거나 CC BY·CC BY-SA 표시가 있는 녹음만 쓰고 녹음한 사람과 라이선스를 보여 줘요.\n· 소리 파일은 이 폰에 저장하지 않아요.\n\n켤까요?";
  function stop() { if (cur) { try { cur.a.pause(); } catch (e) {} if (cur.b) cur.b.textContent = "▶ 소리 듣기"; cur = null; } }
  window.fgClassicMedia = {
    ok: function (m) { return !!m && m.k === "c" && !!P[m.t] && P[m.t].length > 0; },
    infer: function () { return null; },
    render: function (box, m, blind) {
      stop(); var names = P[m.t]; box.innerHTML = '<button type="button" class="wmb">▶ 소리 듣기</button><small class="wmcr"' + (blind ? " hidden" : "") + "></small>";
      var b = box.querySelector("button"), cr = box.querySelector("small");
      b.addEventListener("click", function () {
        if (cur && cur.b === b) { stop(); return; } stop();
        if (!window.fgOnline || !fgOnline.enabled) { cr.hidden = false; cr.textContent = "이 기능은 인터넷에서만 쓸 수 있어요."; return; }
        if (!fgOnline.on() && !fgOnline.ask(ASK)) { cr.hidden = false; cr.textContent = "소리를 들으려면 묻는 창에서 ‘확인’을 눌러 인터넷 사용을 허용해 주세요."; return; }
        if (navigator.onLine === false) { cr.hidden = false; cr.textContent = "인터넷이 연결되면 들을 수 있어요."; return; }
        b.textContent = "⏳ 찾는 중…"; cr.hidden = false; cr.textContent = "인터넷에서 녹음을 찾고 있어요(서버가 느리면 몇 초 걸려요)…"; var me = { b: b, a: new Audio() }; cur = me;
        fgOnline.audioFiles(names, 0, true).then(function (list) {
          var k = 0;
          (function next() {
            if (cur !== me) return; var r = list[k++]; if (!r) { b.textContent = "▶ 다시 눌러 보기"; cr.hidden = false; cr.textContent = "소리를 불러오지 못했어요. 위키 서버가 느리거나 막혔을 수 있어요. 잠시 뒤 다시 눌러 보세요."; cur = null; return; }
            var a = new Audio(), started = false, tm = setTimeout(function () { if (!started) { a.src = ""; next(); } }, 12000); a.preload = "auto"; me.a = a;
            a.addEventListener("playing", function () { started = true; clearTimeout(tm); b.textContent = "⏸ 멈추기"; var who = r.artist && !/no machine-readable/i.test(r.artist) ? r.artist : "";
              cr.innerHTML = "🎧 녹음: " + (who ? esc(who) + " · " : "") + (r.licenseUrl ? '<a href="' + esc(r.licenseUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(r.license) + "</a>" : esc(r.license)) + ' · <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">원본(' + esc(r.label || "위키미디어 커먼즈") + ")</a>"; });
            a.addEventListener("error", function () { if (!started) { clearTimeout(tm); next(); } });
            a.addEventListener("timeupdate", function () { if (a.currentTime >= 40) { a.pause(); a.dispatchEvent(new Event("ended")); } });
            a.addEventListener("ended", function () { if (cur === me) { b.textContent = "🔁 다시 듣기"; cur = null; } });
            a.src = r.src; var p = a.play(); if (p && p.catch) p.catch(function () { if (!started) { clearTimeout(tm); next(); } });
          })();
        }).catch(function () { if (cur === me) { b.textContent = "▶ 다시 눌러 보기"; cr.hidden = false; cr.textContent = "소리를 불러오지 못했어요. 인터넷 연결을 확인해 주세요."; cur = null; } });
      });
    },
    reveal: function (root) { (root || document).querySelectorAll(".wmcr").forEach(function (x) { if (x.textContent) x.hidden = false; }); },
    stop: stop
  };
})();
