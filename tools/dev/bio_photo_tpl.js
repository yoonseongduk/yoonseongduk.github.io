/* 생물 퀴즈 사진(선택, 기본 꺼짐) — 2026-11-28 사용자 요청. 이 파일은 tools/dev/bio_apply.py 가 bio_photo_tpl.js 로 만들어요(직접 고치지 마세요).
   정답이 생물 이름인 문제(MAP: 퀴즈 파일 → {정답: 한국어 위키백과 항목})에서 정답을 고른 뒤에만 사진을 보여 줘요(힌트가 되지 않게).
   MAP 값 = [커먼즈 사진 파일, 위키백과 항목]. 사진은 bio_build.py 가 '찍힌 것(depicts)' 기록으로 그 생물만 찍힌 사진(뼈·화석 제외, 공룡은 복원도)을 고른 것이고,
   폰은 online.js 의 commonsPhoto 로 그 파일만 불러오며 라이선스(공개 도메인·CC0·CC BY·CC BY-SA)를 다시 확인해요.
   사진은 폰·저장소에 저장하지 않고, 사진 아래에 찍은 사람·라이선스·원본 링크를 적어요.
   🌐 온라인을 허락하지 않았으면 「📷 사진 보기」 단추만 보이고, 누르면 한 번 허락을 받아요. 「사진 자동으로 안 보기」는 bio-photo-v1 = "off". */
(function () {
  "use strict";
  var MAP = /*MAP*/{}/*/MAP*/;
  var file = (location.pathname.split("/").pop() || "").replace(/\?.*$/, ""), M = MAP[file];
  if (!M || typeof window.pick !== "function" || !window.fgOnline) return;
  var PK = "bio-photo-v1";
  function get() { try { return localStorage.getItem(PK); } catch (e) { return null; } }
  function set(v) { try { if (v) localStorage.setItem(PK, v); else localStorage.removeItem(PK); } catch (e) {} }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var st = document.createElement("style");
  st.textContent = ".biop{display:block;margin:10px auto 0;text-align:center;font-size:.8rem;line-height:1.45}.biop img{display:block;max-width:100%;max-height:170px;margin:0 auto 4px;border-radius:10px;object-fit:contain;background:rgba(127,127,127,.12)}.biop .cap{opacity:.8;word-break:break-all}.biop a{color:inherit}.biop button{font:inherit;font-size:.85rem;padding:6px 12px;border-radius:999px;border:1px solid rgba(127,127,127,.45);background:transparent;color:inherit;cursor:pointer}.biop .off{margin-top:4px;font-size:.75rem;opacity:.7;border:0;padding:2px 6px;text-decoration:underline}";
  document.head.appendChild(st);
  var wikiUrl = function (t) { return "https://ko.wikipedia.org/wiki/" + encodeURIComponent(t.replace(/ /g, "_")); };
  function load(box, name, ent, token) {
    var file = ent[0], title = ent[1];
    box.innerHTML = "📷 " + esc(name) + " 사진을 불러오는 중…";
    window.fgOnline.commonsPhoto([file], true).then(function (r) {
      if (token !== cur || !box.isConnected) return;   // 그사이 다음 문제로 넘어갔으면 그리지 않아요
      if (!r) { box.innerHTML = '📷 사진을 찾지 못했어요 · <a href="' + wikiUrl(title) + '" target="_blank" rel="noopener">🔗 위키백과에서 보기</a>'; return; }
      var lic = r.licenseUrl ? '<a href="' + esc(r.licenseUrl) + '" target="_blank" rel="noopener">' + esc(r.license) + "</a>" : esc(r.license);
      box.innerHTML = '<img alt="' + esc(name) + ' 사진" loading="lazy" referrerpolicy="no-referrer" src="' + esc(r.src) + '">' +
        '<span class="cap">📷 ' + esc(name) + (r.artist ? " · 사진: " + esc(r.artist.slice(0, 60)) : "") + " · " + lic +
        ' · <a href="' + esc(r.filePage || r.page) + '" target="_blank" rel="noopener">원본</a> · <a href="' + wikiUrl(title) + '" target="_blank" rel="noopener">위키백과</a></span>' +
        '<button type="button" class="off">사진 자동으로 안 보기</button>';
      var img = box.querySelector("img"); img.onerror = function () { img.remove(); };
      box.querySelector(".off").onclick = function () { set("off"); button(box, name, title, token); };
    });
  }
  function button(box, name, title, token) {
    box.innerHTML = '<button type="button">📷 ' + esc(name) + " 사진 보기 🌐</button>";
    box.querySelector("button").onclick = function () {
      if (!window.fgOnline.ask("생물 사진을 위키백과(위키미디어 서버)에서 불러와요.\n인터넷을 쓰고, 사진은 폰에 저장하지 않아요. 사진 아래에 찍은 사람과 라이선스를 적어요.\n계속할까요?")) return;
      set(""); load(box, name, title, token);
    };
  }
  var cur = 0, op = window.pick, os = window.show;
  if (typeof os === "function") window.show = function () { cur++; document.querySelectorAll(".biop").forEach(function (x) { x.remove(); }); return os.apply(this, arguments); };   // 다음 문제로 가면 사진을 치워요
  if (typeof window.finish === "function") { var of = window.finish; window.finish = function () { cur++; document.querySelectorAll(".biop").forEach(function (x) { x.remove(); }); return of.apply(this, arguments); }; }
  window.pick = function (k) {
    var was = typeof locked !== "undefined" && locked;   // 이미 답한 문제를 또 누르면 아무것도 안 해요
    var r = op.apply(this, arguments);
    try {
      if (was) return r;
      var d = qs[i].d, name = String(d[1]), title = M[name], o = document.getElementById("opts"); if (!title || !o) return r;
      var box = document.createElement("div"); box.className = "biop"; o.parentNode.insertBefore(box, o.nextSibling); var token = ++cur;   // 보기 아래(문제·보기를 밀어내지 않게)
      if (window.fgOnline.on() && get() !== "off") load(box, name, title, token); else button(box, name, title, token);
    } catch (e) {}
    return r;
  };
})();
