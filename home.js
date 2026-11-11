/* 모든 화면 공용: 맨 위 줄에 "🏠 처음으로" 버튼(시작 화면 제외)과 "👤 지금 하는 사람 · ⭐ 포인트" 칩을 넣어요.
   같이 하기 안(화면 속 화면)에서는 넣지 않아요. 화면이 window.fgLeaveCheck()를 두면, 누를 때 그 결과가 false면 이동하지 않아요(예: 같이 하기 연결 중 확인).
   지금 하는 사람을 바꾸면 그 사람의 게임 기록·포인트로 바뀌어요(사람별 저장은 person.js). */
(function () {
  if (window.parent !== window || location.protocol === "about:") return;
  var isIndex = /\/(index\.html)?$/.test(location.pathname);
  var st = { fam: function () { try { var a = JSON.parse(localStorage.getItem("family-members-v1")); return Array.isArray(a) ? a.filter(function (x) { return typeof x === "string" && x; }) : []; } catch (e) { return []; } } };
  function names() {
    var P = window.fgPerson, o = P ? P.owner() : "", a = st.fam().slice();
    if (o && a.indexOf(o) < 0) a.unshift(o);
    return a;
  }
  function leaveOk() { return !(typeof window.fgLeaveCheck === "function" && !window.fgLeaveCheck()); }
  function chip() {
    var P = window.fgPerson; if (!P) return null;
    var b = document.createElement("button"); b.type = "button"; b.id = "fg-who";
    var who = P.player(), pts = P.points();
    b.textContent = who ? "👤 " + who + " · ⭐ " + pts + "p" : "👤 누가 하나요?";
    b.style.cssText = "display:inline-flex;align-items:center;gap:4px;padding:6px 12px;border-radius:999px;border:1px solid var(--line,#ccd);background:var(--surface,#fff);color:var(--fg,#1c2233);font:700 .88rem/1.2 system-ui,sans-serif;cursor:pointer";
    b.onclick = function () {
      var old = document.getElementById("fg-whomenu"); if (old) { old.remove(); return; }
      var list = names(), m = document.createElement("div"); m.id = "fg-whomenu";
      m.style.cssText = "position:absolute;z-index:99996;margin-top:4px;min-width:200px;max-width:90vw;background:var(--surface,#fff);color:var(--fg,#1c2233);border:1px solid var(--line,#ccd);border-radius:14px;box-shadow:0 8px 28px rgba(0,0,0,.3);padding:6px;font:700 .95rem/1.3 system-ui,sans-serif";
      function item(txt, fn, on) { var x = document.createElement("button"); x.type = "button"; x.textContent = txt; x.style.cssText = "display:block;width:100%;text-align:left;padding:10px 12px;border:0;border-radius:10px;background:" + (on ? "var(--soft,#eef)" : "transparent") + ";color:inherit;font:inherit;cursor:pointer"; x.onclick = fn; m.appendChild(x); }
      if (!list.length) item("가족 명단을 먼저 만들어요 ➜", function () { if (leaveOk()) location.href = "family-members.html"; });
      list.forEach(function (n) {
        item((n === who ? "✔ " : "") + n + (n === P.owner() ? " (이 폰 주인)" : "") + " · " + P.points(n) + "p", function () {
          if (n === who) { m.remove(); return; }
          if (!leaveOk()) return;
          if (!confirm(n + "(으)로 바꿀게요. 지금 화면을 새로 열어요.")) return;
          P.setPlayer(n); location.reload();
        }, n === who);
      });
      item("⭐ 포인트 보기", function () { if (leaveOk()) location.href = "family-points.html"; });
      b.parentNode.insertBefore(m, b.nextSibling);
      m.style.position = "static"; m.style.marginTop = "6px"; m.style.flexBasis = "100%";
    };
    return b;
  }
  function add() {
    if (document.getElementById("fg-bar")) return;
    var bar = document.createElement("div"); bar.id = "fg-bar"; bar.style.cssText = "display:flex;flex-wrap:wrap;align-items:center;gap:8px;align-self:flex-start;margin:0 0 6px";
    if (!isIndex) {
      var a = document.createElement("a"); a.id = "fg-home"; a.href = "index.html"; a.textContent = "🏠 처음으로";
      a.style.cssText = "display:inline-flex;align-items:center;gap:4px;padding:6px 12px;border-radius:999px;border:1px solid var(--line,#ccd);background:var(--surface,#fff);color:var(--fg,#1c2233);font:700 .88rem/1.2 system-ui,sans-serif;text-decoration:none";
      a.onclick = function (e) { if (!leaveOk()) e.preventDefault(); };
      bar.appendChild(a);
    }
    var c = chip(); if (c) bar.appendChild(c);
    var m = document.querySelector("main") || document.body; m.insertBefore(bar, m.firstChild);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add); else add();
})();
