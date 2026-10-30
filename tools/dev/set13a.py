import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 점 잇기 상자 ----------
make(H+"dots-boxes.html", "점 잇기 상자", "🔲", 205, "dotsboxes-v1",
 "번갈아 가며 <b>점과 점 사이의 선</b>을 하나씩 그어요. 네모 한 칸의 <b>네 번째 선</b>을 그으면 그 칸이 내 것이 되고 한 번 더 할 수 있어요. 칸을 더 많이 차지한 사람이 이겨요! 컴퓨터와 하거나 둘이 할 수 있어요.",
 r'''  <div class="seg" id="mode" style="--n:2"><button type="button" data-m="cpu" class="on">컴퓨터와<small>1인</small></button><button type="button" data-m="two">둘이서<small>2인</small></button></div>
  <div class="stats"><div class="stat"><small id="n1">나(🔵)</small><b id="s1">0</b></div><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">🔵</b></div><div class="stat"><small id="n2">컴퓨터(🔴)</small><b id="s2">0</b></div></div>
  <svg class="db" id="svg" viewBox="0 0 300 300" aria-label="점 잇기 판"></svg>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const N = 4, P = 60, O = 30;     // 네모 4×4, 점 5×5
let hl, vl, own, cur, mode = "cpu", scores = [0, 0], over = false, busy = false, tempo = 1;
function newGame() { hl = Array.from({ length: N + 1 }, () => Array(N).fill(0)); vl = Array.from({ length: N }, () => Array(N + 1).fill(0)); own = Array.from({ length: N }, () => Array(N).fill(-1)); cur = 0; scores = [0, 0]; over = false; busy = false; $("res").hidden = true; $("n2").textContent = mode === "cpu" ? "컴퓨터(🔴)" : "친구(🔴)"; $("n1").textContent = mode === "cpu" ? "나(🔵)" : "나(🔵)"; render(); }
const sides = (r, c) => (hl[r][c] > 0) + (hl[r + 1][c] > 0) + (vl[r][c] > 0) + (vl[r][c + 1] > 0);
function render() {
  let h = ""; for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (own[r][c] >= 0) h += `<rect x="${O + c * P + 3}" y="${O + r * P + 3}" width="${P - 6}" height="${P - 6}" rx="8" fill="${own[r][c] ? "#e4572e" : "#2f6fdf"}" opacity=".35"/>`;
  const L1 = [], L2 = [];
  for (let r = 0; r <= N; r++) for (let c = 0; c < N; c++) { const a = `x1="${O + c * P}" y1="${O + r * P}" x2="${O + (c + 1) * P}" y2="${O + r * P}"`; L1.push(`<line class="e${hl[r][c] ? " on" + (hl[r][c] - 1) : ""}" ${a}/>`); if (!hl[r][c]) L2.push(`<line class="hit" data-t="h" data-r="${r}" data-c="${c}" ${a}/>`); }
  for (let r = 0; r < N; r++) for (let c = 0; c <= N; c++) { const a = `x1="${O + c * P}" y1="${O + r * P}" x2="${O + c * P}" y2="${O + (r + 1) * P}"`; L1.push(`<line class="e${vl[r][c] ? " on" + (vl[r][c] - 1) : ""}" ${a}/>`); if (!vl[r][c]) L2.push(`<line class="hit" data-t="v" data-r="${r}" data-c="${c}" ${a}/>`); }
  h += L1.join("");
  for (let r = 0; r <= N; r++) for (let c = 0; c <= N; c++) h += `<circle cx="${O + c * P}" cy="${O + r * P}" r="5" class="d"/>`;
  h += L2.join(""); $("svg").innerHTML = h; $("s1").textContent = scores[0]; $("s2").textContent = scores[1]; $("turn").textContent = over ? "-" : cur ? "🔴" : "🔵";
}
function play(t, r, c) {
  if (over) return false; const a = t === "h" ? hl : vl; if (a[r][c]) return false; a[r][c] = cur + 1; let got = 0;
  const check = (y, x) => { if (y >= 0 && y < N && x >= 0 && x < N && own[y][x] < 0 && sides(y, x) === 4) { own[y][x] = cur; scores[cur]++; got++; } };
  if (t === "h") { check(r - 1, c); check(r, c); } else { check(r, c - 1); check(r, c); }
  if (scores[0] + scores[1] === N * N) { over = true; render(); const w = scores[0] === scores[1] ? "비겼어요 🤝" : scores[0] > scores[1] ? "🔵 승리! 🎉" : (mode === "cpu" ? "컴퓨터 승리 😢" : "🔴 승리! 🎉"); $("res").innerHTML = `<b>${w}</b><p class="muted">${scores[0]} : ${scores[1]}</p>`; $("res").hidden = false; return true; }
  if (!got) cur = 1 - cur; render(); return true;
}
function allMoves() { const m = []; for (let r = 0; r <= N; r++) for (let c = 0; c < N; c++) if (!hl[r][c]) m.push(["h", r, c]); for (let r = 0; r < N; r++) for (let c = 0; c <= N; c++) if (!vl[r][c]) m.push(["v", r, c]); return m; }
function cpuPick() {
  const ms = allMoves(), score = ([t, r, c]) => { const adj = t === "h" ? [[r - 1, c], [r, c]] : [[r, c - 1], [r, c]]; let s = 0; for (const [y, x] of adj) if (y >= 0 && y < N && x >= 0 && x < N) { const k = sides(y, x); if (k === 3) s += 100; else if (k === 2) s -= 30; } return s + Math.random(); };
  return ms.sort((a, b) => score(b) - score(a))[0];
}
async function cpuTurn() { busy = true; while (!over && cur === 1) { await new Promise(r => setTimeout(r, 450 * tempo)); const [t, r, c] = cpuPick(); play(t, r, c); } busy = false; }
$("svg").addEventListener("click", e => { const l = e.target.closest("[data-t]"); if (!l || busy || over) return; if (mode === "cpu" && cur === 1) return; const was = cur; if (play(l.dataset.t, +l.dataset.r, +l.dataset.c) && mode === "cpu" && cur === 1 && !over) cpuTurn(); });
$("mode").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (!b) return; document.querySelectorAll("#mode button").forEach(x => x.classList.toggle("on", x === b)); mode = b.dataset.m; newGame(); });
$("again").onclick = newGame; newGame();''',
 css=".db{width:100%;max-width:380px;margin:0 auto;display:block;background:var(--surface);border:1px solid var(--line);border-radius:16px;touch-action:manipulation}.db .e{stroke:var(--line);stroke-width:9;stroke-linecap:round;pointer-events:none}.db .hit{stroke:transparent;stroke-width:30;stroke-linecap:round;cursor:pointer}.db .hit:hover{stroke:rgba(120,120,120,.25)}.db .e.on0{stroke:#2f6fdf}.db .e.on1{stroke:#e4572e}.db .d{fill:var(--fg);pointer-events:none}")

# ---------- 전함 게임 ----------
make(H+"battleship.html", "전함 게임", "🚢", 215, "battleship-best-v1",
 "컴퓨터의 바다(위쪽 판)에 숨은 <b>전함</b>을 찾아 칸을 눌러 포탄을 쏘세요! 💥 명중, 🌊 빗나감. 컴퓨터도 내 바다(아래쪽 판)에 포탄을 쏴요. 상대 전함을 <b>먼저 모두 침몰</b>시키면 이겨요.",
 r'''  <div class="stats"><div class="stat"><small>적 함선 남음</small><b id="e">0</b></div><div class="stat"><small>내 함선 남음</small><b id="m">0</b></div><div class="stat"><small>최소 발사</small><b id="best">-</b></div></div>
  <p class="muted center">📍 적의 바다 — 여기를 눌러 공격!</p>
  <div class="bs" id="eg"></div>
  <p class="muted center">🛟 내 바다</p>
  <div class="bs mine" id="mg"></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const N = 6, SHIPS = [3, 2, 2, 1];
let eb, mb, es, ms, shots = 0, over = false, busy = false, best = ld(KEY), tempo = 1, cpuHits = [];
function place() { const b = Array.from({ length: N }, () => Array(N).fill(0)), ships = []; for (const len of SHIPS) { for (;;) { const h = Math.random() < .5, r = ri(0, N - (h ? 1 : len)), c = ri(0, N - (h ? len : 1)), cells = Array.from({ length: len }, (_, k) => [r + (h ? 0 : k), c + (h ? k : 0)]); const near = cells.some(([y, x]) => { for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (b[y + dy] && b[y + dy][x + dx]) return true; return false; }); if (near) continue; cells.forEach(([y, x]) => { b[y][x] = ships.length + 1; }); ships.push({ cells, hit: 0 }); break; } } return { b, ships }; }
function newGame() { const e = place(), m = place(); eb = e.b; es = e.ships; mb = m.b; ms = m.ships; ge = Array.from({ length: N }, () => Array(N).fill(0)); gm = Array.from({ length: N }, () => Array(N).fill(0)); shots = 0; over = false; busy = false; cpuHits = []; $("msg").textContent = ""; $("res").hidden = true; render(); }
let ge, gm;
const alive = ships => ships.filter(s => s.hit < s.cells.length).length;
function render() {
  $("eg").style.gridTemplateColumns = $("mg").style.gridTemplateColumns = `repeat(${N}, 1fr)`;
  $("eg").innerHTML = ge.map((row, r) => row.map((v, c) => `<button type="button" class="bc${v === 1 ? " miss" : v === 2 ? " hit" : ""}" data-r="${r}" data-c="${c}" ${v || over ? "disabled" : ""}>${v === 1 ? "🌊" : v === 2 ? "💥" : ""}</button>`).join("")).join("");
  $("mg").innerHTML = gm.map((row, r) => row.map((v, c) => `<div class="bc${mb[r][c] ? " ship" : ""}${v === 1 ? " miss" : v === 2 ? " hit" : ""}">${v === 1 ? "🌊" : v === 2 ? "💥" : mb[r][c] ? "🚢" : ""}</div>`).join("")).join("");
  $("e").textContent = alive(es); $("m").textContent = alive(ms); $("best").textContent = best ? best + "발" : "-";
}
function fire(b, ships, g, r, c) { if (b[r][c]) { g[r][c] = 2; const s = ships[b[r][c] - 1]; s.hit++; return s.hit === s.cells.length ? "sunk" : "hit"; } g[r][c] = 1; return "miss"; }
function cpuShot() {
  let cand = []; for (const [r, c] of cpuHits) for (const [dy, dx] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const y = r + dy, x = c + dx; if (y >= 0 && y < N && x >= 0 && x < N && !gm[y][x]) cand.push([y, x]); }
  if (!cand.length) for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (!gm[r][c] && (r + c) % 2 === 0) cand.push([r, c]); if (!cand.length) for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (!gm[r][c]) cand.push([r, c]);
  const [r, c] = cand[ri(0, cand.length - 1)], res = fire(mb, ms, gm, r, c); if (res === "hit") cpuHits.push([r, c]); if (res === "sunk") cpuHits = []; return res;
}
async function attack(r, c) {
  if (over || busy || ge[r][c]) return; busy = true; shots++; const res = fire(eb, es, ge, r, c); $("msg").textContent = res === "sunk" ? "💥 침몰시켰어요!" : res === "hit" ? "💥 명중!" : "🌊 빗나갔어요"; render();
  if (!alive(es)) { over = true; const nb = !best || shots < best; if (nb) { best = shots; sv(KEY, best); } $("res").innerHTML = `<b>🎉 승리! ${shots}발 만에 모두 침몰</b><p class="muted">${nb ? "신기록이에요!" : "최소 기록 " + best + "발"}</p>`; $("res").hidden = false; render(); busy = false; return; }
  await new Promise(r2 => setTimeout(r2, 500 * tempo)); const rr = cpuShot(); $("msg").textContent += rr === "miss" ? "  (적도 빗나감)" : "  ⚠️ 적의 공격에 당했어요!"; render();
  if (!alive(ms)) { over = true; $("res").innerHTML = `<b>😢 내 함선이 모두 침몰했어요</b>`; $("res").hidden = false; render(); } busy = false;
}
$("eg").addEventListener("click", e => { const b = e.target.closest("[data-r]"); if (b) attack(+b.dataset.r, +b.dataset.c); });
$("again").onclick = newGame; newGame();''',
 css=".bs{display:grid;gap:4px;max-width:300px;margin:0 auto;width:100%}.bc{aspect-ratio:1;border-radius:8px;border:1px solid var(--line);background:color-mix(in srgb,#2f8fe0 20%,var(--surface));padding:0;font-size:1.2rem;min-width:0;display:flex;align-items:center;justify-content:center}.bc.miss{background:var(--surface)}.bc.hit{background:color-mix(in srgb,var(--bad) 28%,var(--surface))}.mine .bc.ship{background:var(--soft)}.bc:disabled{opacity:1;cursor:default}")

# ---------- 하이카드 ----------
make(H+"high-card.html", "하이카드 대결", "🃏", 355, "highcard-best-v1",
 "카드 10장(1~13 중 랜덤)을 받아요. 매 판 <b>내 카드 한 장을 골라 내면</b> 컴퓨터도 한 장을 내고, <b>숫자가 큰 쪽이 점수 1점</b>! 큰 카드를 언제 쓸지 잘 생각하세요. 10판 뒤 더 많이 이긴 쪽이 승리해요.",
 r'''  <div class="stats"><div class="stat"><small>나</small><b id="s1">0</b></div><div class="stat"><small>판</small><b id="rd">1/10</b></div><div class="stat"><small>컴퓨터</small><b id="s2">0</b></div></div>
  <div class="table"><div class="slot" id="cpuc">?</div><span class="vs">VS</span><div class="slot" id="myc">?</div></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700">낼 카드를 고르세요</p>
  <div class="hand" id="hand"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''let mine = [], cpu = [], round = 0, s1 = 0, s2 = 0, busy = false, wins = ld(KEY) || 0, tempo = 1;
const draw10 = () => shuf(Array.from({ length: 13 }, (_, k) => k + 1)).slice(0, 10).sort((a, b) => a - b);
const face = n => ({ 1: "A", 11: "J", 12: "Q", 13: "K" }[n] || n);
function newGame() { mine = draw10(); cpu = shuf(draw10()); round = 0; s1 = s2 = 0; busy = false; $("cpuc").textContent = "?"; $("myc").textContent = "?"; $("msg").textContent = "낼 카드를 고르세요"; $("res").hidden = true; render(); }
function render() { $("hand").innerHTML = mine.map((n, k) => `<button type="button" class="pc ${mine[k] === 0 ? "used" : ""}" data-k="${k}" ${mine[k] === 0 || busy ? "disabled" : ""}>${mine[k] === 0 ? "" : face(n)}</button>`).join(""); $("s1").textContent = s1; $("s2").textContent = s2; $("rd").textContent = Math.min(round + 1, 10) + "/10"; }
async function play(k) {
  if (busy || !mine[k]) return; busy = true; const m = mine[k], c = cpu[round]; mine[k] = 0; $("myc").textContent = face(m); $("cpuc").textContent = face(c);
  if (m > c) { s1++; $("msg").textContent = `${face(m)} > ${face(c)} 내가 이겼어요!`; } else if (m < c) { s2++; $("msg").textContent = `${face(m)} < ${face(c)} 컴퓨터 승!`; } else $("msg").textContent = "같은 숫자! 무승부";
  round++; render(); await new Promise(r => setTimeout(r, 900 * tempo));
  if (round >= 10) { const w = s1 > s2; if (w) { wins++; sv(KEY, wins); } $("res").innerHTML = `<b>${s1 === s2 ? "비겼어요 🤝" : w ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"} (${s1} : ${s2})</b><p class="muted">누적 승리 ${wins}번</p>`; $("res").hidden = false; } else { $("cpuc").textContent = "?"; $("myc").textContent = "?"; $("msg").textContent = "낼 카드를 고르세요"; }
  busy = false; render();
}
$("hand").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) play(+b.dataset.k); });
$("again").onclick = newGame; newGame();''',
 css=".table{display:flex;align-items:center;justify-content:center;gap:16px}.slot{width:90px;height:120px;border-radius:14px;border:2px solid var(--line);background:var(--surface);display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:3rem}.vs{font-family:var(--font-display);color:var(--muted)}.hand{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.pc{aspect-ratio:3/4;border-radius:10px;border:2px solid var(--accent);background:var(--surface);font-family:var(--font-display);font-size:1.6rem;padding:0;min-width:0}.pc.used{visibility:hidden}")

# ---------- 마피아 역할 배정 ----------
make(H+"mafia-helper.html", "역할 뽑기 (마피아)", "🕵️", 270, "mafia-helper-v1",
 "마피아 게임에서 <b>진행자 없이도</b> 역할을 나눠 주는 도우미예요! 인원을 정하고 시작하면, 한 사람씩 <b>폰을 받아서 '내 역할 보기'</b>를 누르고 확인한 뒤 '숨기기'를 눌러 다음 사람에게 넘겨 주세요.",
 r'''  <div class="card" id="setup"><div class="step"><span>참가 인원</span><div><button type="button" id="minus">−</button><b id="pn">6</b><button type="button" id="plus">+</button></div></div><p class="muted" id="plan"></p><button class="btn" id="go" type="button">역할 나눠 주기</button></div>
  <div class="card center" id="deal" hidden><p class="muted" id="who"></p><p class="big" id="role" style="min-height:1.6em">?</p><p class="muted" id="desc" style="min-height:3em"></p><button class="btn" id="show" type="button">내 역할 보기</button><button class="btn ghost" id="hide" type="button" hidden>숨기기 → 다음 사람</button></div>
  <div class="res" id="res" hidden></div>''',
 r'''const INFO = { "마피아": "밤마다 시민 한 명을 몰래 지목해 없애요. 정체를 들키지 마세요!", "경찰": "밤에 한 명을 골라 마피아인지 확인할 수 있어요.", "의사": "밤에 한 명을 골라 마피아의 공격에서 살릴 수 있어요.", "시민": "낮 토론으로 마피아를 찾아내 투표로 몰아내세요." };
let n = 6, roles = [], idx = 0;
function plan(n) { const m = n >= 9 ? 3 : n >= 6 ? 2 : 1, r = Array(m).fill("마피아"); if (n >= 5) r.push("경찰"); if (n >= 6) r.push("의사"); while (r.length < n) r.push("시민"); return r; }
function renderPlan() { const p = plan(n), c = {}; p.forEach(x => { c[x] = (c[x] || 0) + 1; }); $("pn").textContent = n; $("plan").textContent = "구성: " + Object.entries(c).map(([k, v]) => `${k} ${v}`).join(" · "); }
$("minus").onclick = () => { n = Math.max(4, n - 1); renderPlan(); }; $("plus").onclick = () => { n = Math.min(14, n + 1); renderPlan(); };
$("go").onclick = () => { roles = shuf(plan(n)); idx = 0; $("setup").hidden = true; $("deal").hidden = false; $("res").hidden = true; showWho(); };
function showWho() { $("who").textContent = `${idx + 1}번째 사람 (${idx + 1}/${n})`; $("role").textContent = "?"; $("desc").textContent = "다른 사람이 보지 못하게 가려 주세요"; $("show").hidden = false; $("hide").hidden = true; }
$("show").onclick = () => { const r = roles[idx]; $("role").textContent = r === "마피아" ? "🔪 마피아" : r === "경찰" ? "👮 경찰" : r === "의사" ? "🩺 의사" : "🙂 시민"; $("desc").textContent = INFO[r]; $("show").hidden = true; $("hide").hidden = false; $("hide").textContent = idx === n - 1 ? "숨기기 → 끝내기" : "숨기기 → 다음 사람"; };
$("hide").onclick = () => { idx++; if (idx >= n) { $("deal").hidden = true; $("res").innerHTML = `<b>역할 배정 끝!</b><p class="muted">이제 진행자(또는 아무나)가 밤과 낮을 진행하세요. 마피아끼리는 서로를 몰래 알아보세요.</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 배정하기</button>`; $("res").hidden = false; $("again").onclick = () => { $("res").hidden = true; $("setup").hidden = false; }; } else showWho(); };
renderPlan();''',
 css=".step button{width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--soft);font-size:1.4rem;line-height:1}")

# ---------- 몸으로 말해요 ----------
CH = {"동물": "사자 코끼리 원숭이 토끼 펭귄 기린 개구리 뱀 독수리 고양이 강아지 악어 곰 오리 나비 달팽이 말 닭 돼지 고래".split(), "직업": "의사 소방관 요리사 가수 경찰관 농부 선생님 우주비행사 마술사 운전사 화가 미용사 군인 낚시꾼 기자".split(), "행동": "양치질 샤워 낚시 수영 줄넘기 피아노치기 운전 청소 요리 사진찍기 달리기 자전거타기 빨래 춤추기 낮잠".split(), "물건": "우산 냉장고 선풍기 시계 안경 가위 전화기 청소기 자전거 로봇 기타 텔레비전 비행기 칫솔 바나나".split(), "운동": "축구 야구 농구 탁구 수영 태권도 볼링 양궁 스키 골프 줄다리기 씨름 배드민턴 복싱 피겨스케이팅".split()}
make(H+"charades.html", "몸으로 말해요", "🙈", 18, "charades-best-v1",
 "한 사람이 <b>화면을 보고 몸짓으로만</b> 설명하고, 나머지 사람들은 정답을 맞혀요. 말이나 소리를 내면 안 돼요! 맞히면 <b>✔ 정답</b>, 어려우면 <b>➡ 패스</b>. 60초 동안 몇 개나 맞힐 수 있을까요? 폰을 이마에 대고 하면 더 재미있어요.",
 r'''  <div class="chips" id="cats"></div>
  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">60</b></div><div class="stat"><small>정답</small><b id="ok">0</b></div><div class="stat"><small>패스</small><b id="pass">0</b></div></div>
  <div class="card center" id="word" style="min-height:160px;justify-content:center"><p class="big" id="w" style="font-size:clamp(2.4rem,14vw,4rem)">준비</p></div>
  <div class="row" id="btns" hidden><button class="btn ghost" id="passb" type="button">➡ 패스</button><button class="btn" id="okb" type="button">✔ 정답</button></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''const W = ''' + json.dumps(CH, ensure_ascii=False) + r''';
let cat = "전체", sec = 60, ok = 0, pass = 0, queue = [], timer = 0, run = false, best = ld(KEY) || 0, tempo = 1, passed = [], okList = [];
function chips() { $("cats").innerHTML = ["전체", ...Object.keys(W)].map(c => `<button type="button" class="chip${c === cat ? " on" : ""}" data-c="${c}">${c}</button>`).join(""); }
function nextWord() { if (!queue.length) queue = shuf(cat === "전체" ? Object.values(W).flat() : W[cat]); $("w").textContent = queue.pop(); }
function upd() { $("time").textContent = sec; $("ok").textContent = ok; $("pass").textContent = pass; }
function start() { ok = 0; pass = 0; sec = 60; queue = []; passed = []; okList = []; run = true; $("res").hidden = true; $("start").hidden = true; $("btns").hidden = false; nextWord(); upd(); clearInterval(timer); timer = setInterval(() => { sec--; upd(); if (sec <= 0) end(); }, 1000 * tempo); }
function act(isOk) { if (!run) return; const w = $("w").textContent; if (isOk) { ok++; okList.push(w); } else { pass++; passed.push(w); } upd(); nextWord(); }
function end() { run = false; clearInterval(timer); let note = ""; if (ok > best) { best = ok; sv(KEY, best); note = " 🏆 최고 기록!"; } $("w").textContent = "끝!"; $("btns").hidden = true; $("res").innerHTML = `<b>${ok}개 맞혔어요!${note}</b><p class="muted">맞힌 말: ${okList.join(", ") || "-"}<br>패스: ${passed.join(", ") || "-"}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; }
$("okb").onclick = () => act(true); $("passb").onclick = () => act(false); $("start").onclick = start;
$("cats").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b && !run) { cat = b.dataset.c; chips(); } }); chips(); upd();''',
 css=".chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.9rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}")

# ---------- 초성 파티 ----------
CHO = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
make(H+"choseong-party.html", "초성 파티", "🗣️", 330, "choseong-party-v1",
 "화면에 나온 <b>초성 두 글자</b>로 시작하는 단어를 돌아가며 말해요! 예) <b>ㅅㄱ</b> → 사과, 수건. 정해진 시간 안에 말하지 못하거나 이미 나온 말을 하면 탈락! 가장 오래 버티는 사람이 이겨요. 점수판 + 제한 시간 타이머로 쓰세요.",
 r'''  <div class="card center"><p class="big" id="cho" style="font-size:clamp(3rem,20vw,5rem);letter-spacing:.1em">ㅅㄱ</p><p class="muted" id="msg">다음 사람은 이 초성으로 시작하는 말을 하세요</p></div>
  <div class="bar"><i id="bar"></i></div>
  <div class="row"><button class="btn ghost" id="new" type="button">🔄 초성 바꾸기</button><button class="btn" id="timer" type="button">⏱ 타이머 시작</button></div>
  <div class="card"><b>점수판</b><div id="board"></div><div class="row"><button class="btn ghost" id="addp" type="button">+ 사람 추가</button><button class="btn ghost" id="reset" type="button">점수 초기화</button></div></div>''',
 r'''const CH = "''' + CHO + r'''";
let names = ["1번", "2번", "3번", "4번"], pts = [0, 0, 0, 0], left = 0, total = 10, timer = 0, tempo = 1, sec = 10;
function newCho() { const a = CH[ri(0, CH.length - 1)], b = CH[ri(0, CH.length - 1)]; $("cho").textContent = a + b; stopTimer(); $("msg").textContent = "다음 사람은 이 초성으로 시작하는 말을 하세요"; }
function stopTimer() { clearInterval(timer); timer = 0; $("bar").style.width = "100%"; $("timer").textContent = "⏱ 타이머 시작"; }
function startTimer() { if (timer) return stopTimer(); left = total; $("timer").textContent = "⏹ 멈추기"; timer = setInterval(() => { left -= 0.1; $("bar").style.width = Math.max(0, left / total * 100) + "%"; if (left <= 0) { stopTimer(); $("msg").textContent = "⏰ 시간 초과! 탈락(또는 감점)"; if (navigator.vibrate) navigator.vibrate(300); } }, 100 * tempo); }
function render() { $("board").innerHTML = names.map((n, k) => `<div class="pl"><input type="text" value="${esc(n)}" data-n="${k}" maxlength="6" aria-label="이름"><button type="button" data-d="${k}" data-v="-1">−</button><b>${pts[k]}</b><button type="button" data-d="${k}" data-v="1">+</button></div>`).join(""); }
$("board").addEventListener("click", e => { const b = e.target.closest("[data-d]"); if (b) { pts[+b.dataset.d] += +b.dataset.v; render(); } });
$("board").addEventListener("input", e => { const i = e.target.dataset.n; if (i !== undefined) names[+i] = e.target.value; });
$("addp").onclick = () => { if (names.length < 8) { names.push((names.length + 1) + "번"); pts.push(0); render(); } }; $("reset").onclick = () => { pts = pts.map(() => 0); render(); };
$("new").onclick = newCho; $("timer").onclick = startTimer; newCho(); render();''',
 css=".bar{height:10px;border-radius:5px;background:var(--line);overflow:hidden}.bar i{display:block;height:100%;width:100%;background:var(--accent)}.pl{display:flex;align-items:center;gap:8px;margin:8px 0}.pl input{flex:1}.pl button{width:38px;height:38px;border-radius:50%;border:1px solid var(--line);background:var(--soft);font-size:1.2rem;padding:0}.pl b{min-width:2ch;text-align:center;font-family:var(--font-display);font-weight:400;font-size:1.4rem}")
