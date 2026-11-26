/* 오답 노트용 명화 그림 보기(set43.py가 만들어요 — 직접 고치지 마세요). m = {k:"w", t:"작품 제목"} — 틀린 명화 그림 문제의 그림을 오답 노트에서 다시 보여 줘요.
   그림은 저장소에 없고, 온라인 기능을 켠 폰이 위키백과에서 직접 받아 보여 줘요(공개 도메인 확인을 통과한 것만). */
(function () {
  "use strict";
  var W = /*MEDIA*/null;
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var norm = function (s) { return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function saved(t) {   // 이 폰에 저장해 둔 그림이 있으면 먼저 써요
    try { var sv = JSON.parse(lsGet("art-saved-v1") || "null"), e = sv && sv[t]; if (!e || e.pending || !("caches" in window)) return Promise.resolve(null);
      return caches.open("fg-art-saved-v1").then(function (c) { return c.match(e.src); }).then(function (r) { return r ? r.blob() : null; }).then(function (b) { return b ? { src: URL.createObjectURL(b), page: e.page, title: e.title || t, license: e.license || "공개 도메인" } : null; }).catch(function () { return null; }); } catch (er) { return Promise.resolve(null); }
  }
  function online(t) { var w = W[t]; return w && window.fgOnline && fgOnline.on() && navigator.onLine !== false ? fgOnline.wikiImage(w.k, w.t.map(norm), w.kd, { cc: !!w.cc, nofb: !!w.cc }) : Promise.resolve(null); }
  function zoom(src) {
    var v = document.createElement("div"); v.setAttribute("role", "dialog"); v.style.cssText = "position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.85);display:flex;align-items:center;justify-content:center;padding:12px";
    v.innerHTML = '<img src="' + esc(src) + '" alt="" style="max-width:100%;max-height:90vh;object-fit:contain;border-radius:8px">'; v.addEventListener("click", function () { v.remove(); }); document.body.appendChild(v);
  }
  window.fgArtMedia = {
    ok: function (m) { return !!m && m.k === "w" && !!W[m.t]; },
    infer: function () { return null; },
    render: function (box, m) {
      var t = m.t; box.innerHTML = '<div class="wmimg"></div><div class="wmph"></div>'; var holder = box.querySelector(".wmimg"), bar = box.querySelector(".wmph"), start;
      var show = function (r) {
        var im = new Image(); im.alt = "작품 그림"; im.style.cssText = "max-width:100%;max-height:320px;object-fit:contain;border-radius:10px;display:block;margin:0 auto;cursor:zoom-in";
        im.onload = function () { holder.innerHTML = ""; holder.appendChild(im); im.onclick = function () { zoom(im.src); }; bar.innerHTML = '<small class="wmcr" style="display:block">🖼️ 그림 출처: <a href="' + esc(r.page) + '" target="_blank" rel="noopener noreferrer">' + esc(r.label || "위키백과") + ' 「' + esc(r.title) + "」</a> (" + esc(r.license) + ") · 누르면 크게 보여요</small>"; };
        im.onerror = function () { bar.innerHTML = '<small class="wmcr" style="display:block">그림을 불러오지 못했어요(서버가 느리거나 막혔을 수 있어요).</small><button type="button" class="wmb sm">🖼️ 다시 찾기</button>'; bar.querySelector("button").onclick = start; }; im.src = r.src;
      };
      start = function () { bar.innerHTML = '<small class="wmcr" style="display:block">🖼️ 그림을 찾고 있어요…</small>'; saved(t).then(function (r) { return r || online(t); }).then(function (r) { if (r) show(r); else { bar.innerHTML = '<small class="wmcr" style="display:block">알맞은 그림을 못 찾았어요. 위의 문제 글(작품 이름)로 풀어 보세요.</small><button type="button" class="wmb sm">🖼️ 다시 찾기</button>'; bar.querySelector("button").onclick = start; } }); };
      if (window.fgOnline && fgOnline.on()) start();
      else { bar.innerHTML = '<button type="button" class="wmb sm">🖼️ 그림 보기</button>'; bar.querySelector("button").onclick = function () { if (!window.fgOnline || !fgOnline.enabled) return; if (!fgOnline.on() && !fgOnline.ask("🌐 온라인 그림을 켜요.\n\n· 인터넷에서 저작권이 끝난 명화만 불러와요.\n· 불러올 때 이 기기의 인터넷 주소가 위키백과·위키미디어 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n\n켤까요?")) return; start(); }; }
    },
    reveal: function () {}, stop: function () {}
  };
})();
