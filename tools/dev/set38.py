# 오늘의 미션 화면 (daily-mission.html) — 날짜로 게임 3개를 정해(온 가족 같은 미션), 해 봤는지는 포인트 기록(fg-points-v1)의 log 로 알아낸다.
# 3개를 다 하면 그날 도장. 도장은 사람별로 daily-mission-v1 에 날짜 목록으로 남기고, 연속 일수·최근 14일 도장판·가족 현황을 보여 준다.
# 포인트(점수)는 주지 않는다(포인트 규칙 D6 은 person.js 한 곳에서만 고치기 때문).
import sys
sys.path.insert(0, ".")
from mkpage import make

CSS = '''.li{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}.li:last-child{border-bottom:0}
.note{font-size:.85rem;color:var(--muted)}.done{color:var(--ok);font-weight:700}.go{font-size:.9rem;color:var(--accent);white-space:nowrap}
.dots{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}.dot{aspect-ratio:1;border-radius:10px;border:1px solid var(--line);background:var(--soft);display:flex;align-items:center;justify-content:center;font-size:.8rem;color:var(--muted)}
.dot.on{background:var(--ok);color:#fff;border-color:var(--ok);font-weight:700}.dot.today{outline:2px solid var(--accent)}
.big2{font-family:var(--font-display);font-size:1.6rem}.me{font-weight:700;color:var(--accent)}
'''

BODY = '''  <div class="card"><b id="mt">🎯 오늘의 미션</b><div id="ms"></div><div class="note" id="mn"></div></div>
  <div class="card"><b>🔥 연속 도장</b><div class="big2" id="streak">0일</div><div class="note" id="total"></div><div class="dots" id="dots"></div></div>
  <div class="card"><b>👨‍👩‍👧 가족 오늘 현황</b><div id="fam"></div></div>
  <p class="muted">미션 3개는 날짜마다 바뀌고 가족이 모두 같아요. 게임을 한 판 하면(10초 이상, 또는 끝까지) 미션이 완료돼요. 위쪽 칩에서 누가 하는지 고르면 그 사람의 도장이 쌓여요. 도장은 놀이용이라 포인트는 따로 주지 않아요.</p>
'''

JS = r'''
const FP = window.fgPerson, SK = "daily-mission-v1";
const POOLG = ["brain", "quiz", "react", "board", "arcade"];       // 미션을 뽑는 분류(같이 하기·생활 제외)
const SKIP = new Set(["wrong-notes.html", "go-stop.html", "blackjack.html", "hanja-today.html"]); // 너무 길거나 포인트 계산이 다른 화면
let INFO = {};                                                      // 파일 → {e, t, g} (시작 화면 목록에서 읽음)
const jget = k => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
const ymd = t => { const d = new Date(t); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); };
const ownerN = () => FP.owner() || "(이 폰)";
function hashStr(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
function rngOf(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
// 그 날짜의 미션 3개: 분류 5개 중 3개를 날짜로 고르고, 각 분류에서 게임 1개를 고른다(같은 날짜면 언제나 같은 결과)
function missionsOf(date) {
  const byG = {};
  Object.keys(FP.games).forEach(f => { const i = INFO[f]; if (i && POOLG.includes(i.g) && !SKIP.has(f)) (byG[i.g] = byG[i.g] || []).push(f); });
  Object.values(byG).forEach(a => a.sort());
  const r = rngOf(hashStr("mission:" + date)), gs = POOLG.filter(g => byG[g] && byG[g].length);
  for (let i = gs.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [gs[i], gs[j]] = [gs[j], gs[i]]; }
  return gs.slice(0, 3).map(g => byG[g][Math.floor(r() * byG[g].length)]);
}
// 사람별로 날짜마다 해 본 게임 모으기(포인트 기록의 log)
function playedBy(name) { const m = {}, u = ((jget(FP.pointsKey) || {}).p || {})[name]; ((u && u.log) || []).forEach(x => { (m[ymd(x.t)] = m[ymd(x.t)] || new Set()).add(x.f); }); return m; }
function allNames() { const fam = jget("family-members-v1"), set = new Set([ownerN()]); (Array.isArray(fam) ? fam : []).forEach(n => typeof n === "string" && n && set.add(n)); Object.keys((jget(FP.pointsKey) || {}).p || {}).forEach(n => n && set.add(n)); return [...set]; }
const icon = e => /^img:/.test(e) ? `<img src="${esc(e.slice(4))}" alt="" style="height:1.3em;vertical-align:-.25em">` : esc(e); // 트럼프 카드 게임은 이모지 대신 그림 주소(img:)를 쓴다
function load() { const s = jget(SK); return s && typeof s === "object" ? s : {}; }
function render() {
  const today = ymd(Date.now()), cur = FP.player() || ownerN(), store = load(), ms = missionsOf(today), names = allNames();
  const isDone = {};
  names.forEach(n => {
    const pl = playedBy(n), have = new Set(store[n] || []);
    for (let k = 0; k < 14; k++) { const d = ymd(Date.now() - k * 86400000); if (have.has(d)) continue; const mm = missionsOf(d), p = pl[d]; if (p && mm.length === 3 && mm.every(f => p.has(f))) have.add(d); }
    store[n] = [...have].sort().slice(-400); isDone[n] = pl[today] || new Set();
  });
  try { localStorage.setItem(SK, JSON.stringify(store)); } catch (e) {}
  $("mt").textContent = "🎯 오늘의 미션 · " + today.slice(5).replace("-", "월 ") + "일";
  const mine = isDone[cur] || new Set(), cnt = ms.filter(f => mine.has(f)).length;
  $("ms").innerHTML = ms.length ? ms.map(f => { const i = INFO[f] || { e: "🎮", t: f }, ok = mine.has(f); return `<div class="li"><span>${ok ? "✅" : "⬜"} ${icon(i.e)} ${esc(i.t)}</span>${ok ? `<span class="done">완료</span>` : `<a class="go" href="${f}">하러 가기 ›</a>`}</div>`; }).join("") : `<div class="note">게임 목록을 불러오는 중이에요…</div>`;
  $("mn").textContent = cnt === 3 ? "🎉 " + cur + "님, 오늘 미션 완료! 도장을 받았어요." : cur + "님: " + cnt + "/3 완료";
  const have = new Set(store[cur] || []);
  let st = 0; for (let k = have.has(today) ? 0 : 1; k < 400; k++) { if (have.has(ymd(Date.now() - k * 86400000))) st++; else break; }
  if (cnt === 3) have.add(today);
  $("streak").textContent = st + "일";
  $("total").textContent = "지금까지 도장 " + have.size + "개";
  let dots = ""; for (let k = 13; k >= 0; k--) { const t = Date.now() - k * 86400000, d = ymd(t), on = have.has(d) || (k === 0 && cnt === 3); dots += `<div class="dot${on ? " on" : ""}${k === 0 ? " today" : ""}" title="${d}">${new Date(t).getDate()}</div>`; }
  $("dots").innerHTML = dots;
  $("fam").innerHTML = names.map(n => { const c = ms.filter(f => (isDone[n] || new Set()).has(f)).length; return `<div class="li${n === cur ? " me" : ""}"><span>${c === 3 ? "🏅" : "👤"} ${esc(n)}</span><b>${c}/3</b></div>`; }).join("");
}
fetch("index.html").then(r => r.text()).then(t => { for (const m of t.matchAll(/\["([^"]+\.html)", "([^"]*)", "([^"]*)", "[^"]*", "([^"]*)"/g)) INFO[m[1]] = { e: m[2], t: m[3], g: m[4] }; render(); }).catch(() => render());
render();
addEventListener("pageshow", render);
'''

make("out/daily-mission.html", "오늘의 미션", "🎯", 15, "daily-mission-v1",
     "날짜마다 게임 3개가 정해져요. 가족이 모두 같은 미션을 하고, 다 하면 도장을 받아요.", BODY, JS, CSS)
