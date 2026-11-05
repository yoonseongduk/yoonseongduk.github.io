/* 모든 화면 공용: 맨 위에 "🏠 처음으로" 버튼을 넣어요(시작 화면 제외).
   같이 하기 안(화면 속 화면)에서는 넣지 않아요. 화면이 window.fgLeaveCheck()를 두면, 누를 때 그 결과가 false면 이동하지 않아요(예: 같이 하기 연결 중 확인). */
(function () {
  if (window.parent !== window || /\/(index\.html)?$/.test(location.pathname) || location.protocol === "about:") return;
  function add() {
    if (document.getElementById("fg-home")) return;
    var a = document.createElement("a"); a.id = "fg-home"; a.href = "index.html"; a.textContent = "🏠 처음으로";
    a.style.cssText = "display:inline-flex;align-items:center;gap:4px;align-self:flex-start;margin:0 0 6px;padding:6px 12px;border-radius:999px;border:1px solid var(--line,#ccd);background:var(--surface,#fff);color:var(--fg,#1c2233);font:700 .88rem/1.2 system-ui,sans-serif;text-decoration:none";
    a.onclick = function (e) { if (typeof window.fgLeaveCheck === "function" && !window.fgLeaveCheck()) e.preventDefault(); };
    var m = document.querySelector("main") || document.body; m.insertBefore(a, m.firstChild);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add); else add();
})();
