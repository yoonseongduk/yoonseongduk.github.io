/* 모든 화면 공용: 맨 위 줄에 "🏠 처음으로" 버튼(시작 화면 제외)과 "👤 지금 하는 사람 · ⭐ 포인트" 칩을 넣어요.
   같이 하기 안(화면 속 화면)에서는 넣지 않아요. 화면이 window.fgLeaveCheck()를 두면, 누를 때 그 결과가 false면 이동하지 않아요(예: 같이 하기 연결 중 확인).
   지금 하는 사람을 바꾸면 그 사람의 게임 기록·포인트로 바뀌어요(사람별 저장은 person.js). */
(function () {
  if (window.parent !== window || location.protocol === "about:") return;
  var isIndex = /\/(index\.html)?$/.test(location.pathname);
  // 시작 화면의 '🕘 최근에 한 게임'을 위해 지금 연 화면을 기록해요(최근 12개, 시작 화면·같이 하기 게임 제외)
  (function () { if (isIndex) return; var f = (location.pathname.split("/").pop() || ""); if (!/\.html$/.test(f) || /^net-/.test(f)) return;
    try { var a = JSON.parse(localStorage.getItem("fg-recent-v1") || "[]"); if (!Array.isArray(a)) a = []; a = [f].concat(a.filter(function (x) { return x !== f; })).slice(0, 12); localStorage.setItem("fg-recent-v1", JSON.stringify(a)); } catch (e) {} })();
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
    b.textContent = (who ? "👤 " + who : "👤 누가 하나요?") + " · ⭐ " + pts + "p"; // 이름을 안 골라도 내 포인트는 항상 보인다
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
      item("🏅 가족 순위표", function () { if (leaveOk()) location.href = "family-ranking.html"; });
      item("🎯 오늘의 미션", function () { if (leaveOk()) location.href = "daily-mission.html"; });
      b.parentNode.insertBefore(m, b.nextSibling);
      m.style.position = "static"; m.style.marginTop = "6px"; m.style.flexBasis = "100%";
    };
    return b;
  }
  // 이 게임에서 오늘 받은 포인트 / 하루 최대 (포인트를 주는 게임에서만)
  function gameText() { var g = window.fgPerson.game(); if (g.bet) return "🎮 오늘 이 게임 손익 " + (g.earned > 0 ? "+" : "") + g.earned + "p · 판돈은 내 포인트"; return g.unlimited ? "🎮 오늘 이 게임 " + g.earned + "p · 제한 없음" : "🎮 오늘 이 게임 " + g.earned + " / " + g.max + "p"; }
  // 오늘 이 게임의 포인트 이력 패널(칸을 누르면 열린다)
  function fillHist() {
    var p = document.getElementById("fg-ghist"), P = window.fgPerson; if (!p || !P) return;
    var h = P.history(), g = P.game(), tot = 0, t = document.createElement("table"), pad = function (n) { return (n < 10 ? "0" : "") + n; };
    p.textContent = ""; var head = document.createElement("div"); head.style.cssText = "font-weight:800;margin-bottom:4px"; p.appendChild(head);
    t.style.cssText = "width:100%;border-collapse:collapse";
    h.slice().reverse().forEach(function (x) { tot += x.p; var tr = document.createElement("tr"), d = new Date(x.t); [pad(d.getHours()) + ":" + pad(d.getMinutes()), (x.p > 0 ? "+" : "") + x.p + "p", x.w].forEach(function (c, i) { var td = document.createElement("td"); td.textContent = c; td.style.cssText = "padding:3px 4px;border-bottom:1px solid var(--line,#e6e1ea)" + (i === 1 ? ";font-weight:800;text-align:right;white-space:nowrap" : ""); tr.appendChild(td); }); t.appendChild(tr); });
    head.textContent = g.bet ? "📜 오늘 이 게임 판돈·정산 기록 · 손익 " + (tot > 0 ? "+" : "") + tot + "p" : "📜 오늘 이 게임에서 받은 포인트 · 합계 " + tot + "p" + (g.unlimited ? " (제한 없음)" : "");
    if (g.bet) { var bt = document.createElement("div"); bt.textContent = "판돈은 내 포인트로 내고, 이기면 돌려받아요. 횟수·금액 제한은 없고 포인트가 없으면 할 수 없어요."; bt.style.cssText = "font-weight:600;font-size:.76rem;color:var(--muted,#5b6275);margin-bottom:4px"; p.appendChild(bt); }
    else if (!g.unlimited) { var nt = document.createElement("div"); nt.textContent = "오늘 받은 횟수: 플레이 " + g.plays + "/" + g.per + "번 · 이김·최고 기록 " + g.bonus + "/" + g.per + "번 (넘으면 더 안 올라요). 하루 최대 " + g.max + "p는 기본 한도에 처음 해 본·연속 출석 보너스를 받은 만큼을 더한 값이에요."; nt.style.cssText = "font-weight:600;font-size:.76rem;color:var(--muted,#5b6275);margin-bottom:4px"; p.appendChild(nt); }
    if (!h.length) { var n = document.createElement("div"); n.textContent = g.bet ? "아직 판돈 기록이 없어요. 딜을 눌러 시작해요." : "아직 받은 포인트가 없어요. 게임을 10초 이상 하거나 이기면 쌓여요."; n.style.cssText = "color:var(--muted,#5b6275)"; p.appendChild(n); } else p.appendChild(t);
  }
  function gamePill() {
    var P = window.fgPerson; if (!P || !P.game || !P.game().listed) return null;
    var s = document.createElement("button"); s.type = "button"; s.id = "fg-gpt"; s.textContent = gameText();
    s.title = "이 게임에서 오늘 받은 포인트(보너스 포함)와 하루 최대 포인트예요. 누르면 오늘 받은 이력을 볼 수 있어요.";
    s.style.cssText = "display:inline-flex;align-items:center;padding:6px 12px;border-radius:999px;border:1px dashed var(--line,#ccd);background:var(--soft,#f4f1f6);color:var(--muted,#5b6275);font:700 .8rem/1.2 system-ui,sans-serif;cursor:pointer";
    s.onclick = function () { var o = document.getElementById("fg-ghist"); if (o) { o.remove(); return; } var p = document.createElement("div"); p.id = "fg-ghist"; p.style.cssText = "flex-basis:100%;background:var(--surface,#fff);color:var(--fg,#1c2233);border:1px solid var(--line,#ccd);border-radius:14px;padding:10px 12px;font:600 .85rem/1.5 system-ui,sans-serif"; s.parentNode.insertBefore(p, s.nextSibling); fillHist(); };
    return s;
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
    var gp = gamePill(); if (gp) bar.appendChild(gp);
    addEventListener("fgpoints", function () { var w = document.getElementById("fg-who"), P = window.fgPerson; if (w && P) w.textContent = (P.player() ? "👤 " + P.player() : "👤 누가 하나요?") + " · ⭐ " + P.points() + "p"; var g = document.getElementById("fg-gpt"); if (g) g.textContent = gameText(); fillHist(); });
    var m = document.querySelector("main") || document.body; m.insertBefore(bar, m.firstChild);
    modes();
  }
  // 비슷한 게임을 합친 묶음(tools/dev/merged.json → merge_apply.py 가 아래 칸을 채워요): 제목 아래에 모드 단추를 달아 서로 오가요
  /*MODES*/var MODES = [[["color-match.html", "연속 보너스"], ["stroop-color.html", "기본"]], [["number-tap.html", "1부터 순서대로"], ["reverse-tap.html", "큰 수부터 거꾸로"]], [["number-memory.html", "그대로 기억"], ["reverse-memory.html", "거꾸로 입력"]], [["pattern-memory.html", "순서대로 누르기"], ["spot-memory.html", "위치만 기억"]], [["sudoku.html", "9×9"], ["mini-sudoku.html", "4×4·6×6"]], [["space-shooter.html", "우주 슈터"], ["alien-defense.html", "외계인 방어"]], [["quick-math.html", "암산 60초"], ["times-table.html", "구구단 스피드"]], [["stopwatch-timer.html", "스톱워치·타이머"], ["pomodoro.html", "집중 타이머"]], [["play-together.html", "같이 하기"], ["link-test.html", "연결 테스트"]], [["earth-quiz.html", "지구과학"], ["weather-quiz.html", "날씨"]], [["click-speed.html", "혼자 기록 재기"], ["tap-duel.html", "둘이 대결"]], [["reaction-test.html", "혼자 기록 재기"], ["reaction-duel.html", "둘이 대결"]], [["memory-match.html", "혼자 하기"], ["memory-duel.html", "둘이 번갈아"]], [["rps-streak.html", "연승 도전"], ["rps-tournament.html", "4명 대회"]], [["animal-quiz.html", "동물"], ["sea-quiz.html", "바다 생물"], ["insect-quiz.html", "곤충"], ["plant-quiz.html", "식물"], ["dino-quiz.html", "공룡"], ["bio-check.html", "📷 사진 모아 보기"]], [["hero-quiz.html", "우리나라 인물"], ["worldhero-quiz.html", "세계 위인"]], [["korean-food-quiz.html", "우리 음식"], ["world-food-quiz.html", "세계 음식"]], [["purekorean-quiz.html", "순우리말"], ["onomatopoeia-quiz.html", "의성어·의태어"], ["dialect-quiz.html", "사투리"]], [["capital-quiz.html", "세계 수도"], ["flag-quiz.html", "국기"]], [["english-quiz.html", "영단어 뜻"], ["emoji-english-quiz.html", "그림 보고 영어"]], [["tradition-quiz.html", "우리 전통"], ["heritage-quiz.html", "문화재"]], [["music-quiz.html", "음악 상식"], ["orchestra-quiz.html", "오케스트라"]], [["dice-roller.html", "주사위"], ["coin-flip.html", "동전"]], [["decision-roulette.html", "결정 룰렛"], ["lots.html", "제비뽑기"], ["order-picker.html", "순서·벌칙"], ["menu-picker.html", "오늘 뭐 먹지"]], [["calendar-tools.html", "음양력·절기"], ["dday-counter.html", "디데이"], ["age-calc.html", "나이 계산"]], [["bmr-calc.html", "대사량·칼로리"], ["bmi-calc.html", "BMI"], ["exercise-kcal.html", "운동 칼로리"]], [["family-points.html", "가족 포인트"], ["family-ranking.html", "가족 순위표"]]];/*/MODES*/
  function modes() {
    if (isIndex || document.getElementById("fg-modes")) return;
    var f = location.pathname.split("/").pop() || "", g = null;
    MODES.forEach(function (x) { if (x.some(function (y) { return y[0] === f; })) g = x; }); if (!g) return;
    var nav = document.createElement("nav"); nav.id = "fg-modes"; nav.setAttribute("aria-label", "모드 고르기");
    nav.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:2px 0 4px;font:600 .88rem/1.2 system-ui,sans-serif";
    var lab = document.createElement("span"); lab.textContent = "🔀 모드"; lab.style.cssText = "color:var(--muted,#667);margin-right:2px"; nav.appendChild(lab);
    g.forEach(function (y) {
      var on = y[0] === f, el = document.createElement(on ? "span" : "a"); el.textContent = y[1];
      if (!on) { el.href = y[0]; el.onclick = function (e) { if (!leaveOk()) e.preventDefault(); }; }
      el.style.cssText = "padding:6px 12px;border-radius:999px;text-decoration:none;border:1px solid " + (on ? "var(--fg,#1c2233)" : "var(--line,#ccd)") + ";background:" + (on ? "var(--fg,#1c2233)" : "var(--surface,#fff)") + ";color:" + (on ? "var(--bg,#fff)" : "var(--fg,#1c2233)");
      if (on) el.setAttribute("aria-current", "page"); nav.appendChild(el);
    });
    var h = document.querySelector("h1"); if (h && h.parentNode) h.parentNode.insertBefore(nav, h.nextSibling);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add); else add();
})();
