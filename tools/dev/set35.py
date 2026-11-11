# 가족 포인트 화면 (family-points.html) — 포인트 규칙의 숫자는 person.js 의 CFG 한 곳에서만 가져온다
import sys
sys.path.insert(0, ".")
from mkpage import make
CSS = '''.li{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}.li:last-child{border-bottom:0}.note{font-size:.85rem;color:var(--muted)}.rk{font-family:var(--font-display);font-size:1.3rem;min-width:2ch}.pt{font-family:var(--font-display);font-size:1.3rem}.me{background:var(--soft);border-radius:10px;padding:8px 6px}.g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.tbl{width:100%;border-collapse:collapse;font-size:.9rem}.tbl td{padding:4px 2px;border-bottom:1px solid var(--line)}.tbl td:last-child{text-align:right;color:var(--muted)}'''
BODY = '''  <div class="card"><b>🏆 가족 포인트 순위</b><div id="rank"></div><div class="note" id="rnote"></div></div>
  <div class="card"><b id="whot">👤 내 포인트</b><div class="g3"><div class="stat"><small>합계</small><b id="s-total">0</b></div><div class="stat"><small>오늘</small><b id="s-today">0</b></div><div class="stat"><small>연속 출석</small><b id="s-streak">0일</b></div></div><div id="log"></div></div>
  <div class="card"><b>📘 포인트는 이렇게 얻어요</b><table class="tbl"><tbody id="rules"></tbody></table><div class="note">게임을 10초 이상 하면 한 판으로 쳐요. 같은 게임은 하루에 몇 번까지만 받아요. 포인트는 이 폰에만 저장되고, 놀이용 숫자라 다른 것으로 바꿀 수 없어요.</div></div>'''
JS = r'''
const P = window.fgPerson;
let titles = {};
const raw = () => { try { return JSON.parse(localStorage.getItem(P.pointsKey)); } catch (e) { return null; } };
const day = t => { const d = new Date(t); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); };
const tname = f => titles[f] || f.replace(/\.html$/, "");
function render() {
  const data = (raw() || {}).p || {}, fam = (() => { try { const a = JSON.parse(localStorage.getItem("family-members-v1")); return Array.isArray(a) ? a : []; } catch (e) { return []; } })();
  const names = [...new Set([...fam, ...Object.keys(data), P.owner()].filter(Boolean))];
  const cur = P.player() || "(이 폰)";
  const rows = names.map(n => ({ n, t: data[n] ? data[n].total : 0 })).sort((a, b) => b.t - a.t);
  $("rank").innerHTML = rows.length ? rows.map((r, i) => `<div class="li${r.n === cur ? " me" : ""}"><span><span class="rk">${i === 0 && r.t > 0 ? "🥇" : i + 1}</span> ${esc(r.n)}</span><span class="pt">${r.t}p</span></div>`).join("") : '<div class="note">아직 포인트가 없어요. 게임을 해 보세요!</div>';
  $("rnote").textContent = P.player() ? "" : "맨 위 칩에서 '누가 하나요?'를 고르면 사람별로 쌓여요.";
  const u = data[cur] || { total: 0, today: {}, bonus: {}, log: [], streak: 0, day: "" };
  $("whot").textContent = "👤 " + cur + "의 포인트";
  const td = day(Date.now()), todayPts = (u.log || []).filter(l => day(l.t) === td).reduce((s, l) => s + l.p, 0);
  $("s-total").textContent = u.total + "p"; $("s-today").textContent = todayPts + "p"; $("s-streak").textContent = (u.day === td || u.lastDay === day(Date.now() - 86400000) ? u.streak : 0) + "일";
  $("log").innerHTML = (u.log || []).slice(-12).reverse().map(l => `<div class="li"><span>${esc(tname(l.f))}<br><span class="note">${esc(l.w)} · ${new Date(l.t).toLocaleString("ko-KR", { month: "numeric", day: "numeric", hour: "numeric", minute: "numeric" })}</span></span><span class="pt">+${l.p}</span></div>`).join("") || '<div class="note">아직 받은 포인트가 없어요.</div>';
}
(function rules() {
  const c = P.cfg;
  const r = [["게임 한 판 (기본)", "+" + c.base + "p"], ["같은 게임 하루 최대", c.perDay + "판"], ["이겼어요·클리어", "+" + c.win + "p"], ["최고 기록 세우기", "+" + c.best + "p"], ["처음 해 보는 게임", "+" + c.first + "p"], ["어려운 게임", "×" + c.hard], ["연속 출석(하루마다)", "+" + c.streakStep + "p씩, 최대 " + c.streakMax + "p"]];
  $("rules").innerHTML = r.map(x => `<tr><td>${x[0]}</td><td>${x[1]}</td></tr>`).join("");
})();
render();
fetch("index.html").then(r => r.text()).then(t => { for (const m of t.matchAll(/\["([^"]+\.html)", "[^"]*", "([^"]*)"/g)) titles[m[1]] = m[2]; render(); }).catch(() => {});
'''
make("out/family-points.html", "가족 포인트", "⭐", 45, "fg-points-v1",
 "게임을 하면 기본 점수와 가산 점수가 쌓여요. 위쪽 칩에서 누가 하는지 고르면 그 사람의 포인트로 쌓여요.", BODY, JS, CSS)
