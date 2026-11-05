import sys
sys.path.insert(0, ".")
from mkpage import make
from set31 import DUO_JS, AGAIN, NET_JS, NET_CSS, LINK_CSS   # set31(→set30)을 불러오면 앞의 같이 하기 게임도 함께 다시 만들어져요

# ───────── 같이 하기 게임 3차: 두 사람 대결 9개 + 여러 명 파티 5개. 목록은 set30.py의 GAMES.
CSS = LINK_CSS + NET_CSS + '''
.grid8{display:grid;gap:3px;width:min(100%,340px);margin:0 auto}.grid8 button{aspect-ratio:1;border-radius:6px;border:0;padding:0;font-size:1.3rem;line-height:1}
.big{font-family:var(--font-display);font-size:clamp(2rem,12vw,3.4rem);text-align:center;line-height:1.2}
.choice{display:grid;gap:8px}.choice button{padding:14px 8px;border-radius:14px;border:1px solid var(--line);background:var(--soft);font-family:var(--font-display);font-size:1.3rem}.choice button[disabled]{opacity:.4}
.li{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--line)}.li:last-child{border-bottom:0}'''

def duo(fn, title, emoji, hue, key, help_, body, js, css=""):
    make("out/" + fn, title, emoji, hue, key, help_, '  <div class="card">' + body + AGAIN + '</div>', DUO_JS + js, CSS + css)

# ── 뒤집기 보드: 8×8, 상대 돌을 사이에 끼우면 뒤집기, 둘 곳이 없으면 자동으로 넘어감, 판이 끝나면 돌이 많은 쪽이 승리. 먼저 하는 사람이 ⚫.
duo("net-flip.html", "뒤집기 보드 (같이 하기)", "⚫", 140, "net-flip-v1",
    "내 돌을 놓아 상대 돌을 사이에 끼우면 모두 뒤집혀요. 점이 보이는 칸에만 놓을 수 있고, 둘 곳이 없으면 자동으로 넘어가요. 더 둘 곳이 없으면 돌이 많은 쪽이 이겨요. 먼저 하는 사람이 ⚫예요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="grid8" id="bd" style="grid-template-columns:repeat(8,1fr);background:#1f7a4a;padding:4px;border-radius:10px"></div>',
    r'''
const N = 8, D8 = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]];
function flips(g, i, v) { const out = []; if (g[i]) return out; const x0 = i % N, y0 = Math.floor(i / N);
  for (const [dx, dy] of D8) { const line = []; let x = x0 + dx, y = y0 + dy; while (x >= 0 && y >= 0 && x < N && y < N && g[y * N + x] === 3 - v) { line.push(y * N + x); x += dx; y += dy; }
    if (line.length && x >= 0 && y >= 0 && x < N && y < N && g[y * N + x] === v) out.push(...line); }
  return out; }
const movesOf = (g, v) => g.map((_, i) => i).filter(i => flips(g, i, v).length);
const colorOf = id => id === P.first ? 1 : 2;
function newRound() { const g = Array(N * N).fill(0); g[27] = g[36] = 2; g[28] = g[35] = 1; return { ph: "play", g, turn: P.first, last: -1, pass: null }; }
function onAct(from, d) {
  if (d.t === "put" && P.ph === "play" && from === P.turn) { const i = +d.i, v = colorOf(from), f = flips(P.g, i, v); if (!f.length) return;
    P.g[i] = v; f.forEach(x => { P.g[x] = v; }); P.last = i; P.pass = null; const o = oppOf(from);
    if (movesOf(P.g, colorOf(o)).length) P.turn = o; else if (movesOf(P.g, v).length) P.pass = o;
    else { const c1 = P.g.filter(x => x === 1).length, c2 = P.g.filter(x => x === 2).length; finish(c1 === c2 ? "D" : c1 > c2 ? P.first : oppOf(P.first)); }
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.g) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; $("cnt").innerHTML = ""; if (P) common(); return; }
  const can = P.ph === "play" && P.turn === me, mv = can ? movesOf(P.g, colorOf(me)) : [], chip = id => (id === P.first ? "⚫ " : "⚪ ") + nm(id);
  $("st").textContent = P.ph === "end" ? endText() : (P.pass ? `${nm(P.pass)}는 둘 곳이 없어서 넘어가요. ` : "") + (!amPlayer() ? `구경 중 · ${chip(P.turn)} 차례` : can ? `내 차례예요 (${colorOf(me) === 1 ? "⚫" : "⚪"}) · 점이 있는 칸에 놓아요` : "상대 차례예요…");
  $("cnt").innerHTML = [P.first, oppOf(P.first)].map((id, k) => `<div class="stat"><small>${k ? "⚪" : "⚫"} ${esc(nm(id))}</small><b>${P.g.filter(x => x === k + 1).length}</b></div>`).join("") + `<div class="stat"><small>빈 칸</small><b>${P.g.filter(x => !x).length}</b></div>`;
  $("bd").innerHTML = P.g.map((v, i) => `<button type="button" data-i="${i}" style="background:${i === P.last ? "#2f9a63" : "#27894f"}"${mv.includes(i) ? "" : " disabled"} aria-label="${Math.floor(i / N) + 1}행 ${i % N + 1}열">${v === 1 ? "⚫" : v === 2 ? "⚪" : mv.includes(i) ? "<small style='opacity:.6'>•</small>" : ""}</button>`).join("");
  $("bd").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "put", i: +b.dataset.i }));
  common();
}
render();
''')

# ── 점 잇기 상자: 4×4칸, 번갈아 선 하나, 네모의 네 번째 선을 그으면 그 칸을 차지하고 한 번 더. 칸이 많은 쪽이 승리.
duo("net-dots.html", "점 잇기 상자 (같이 하기)", "🟦", 220, "net-dots-v1",
    "번갈아 점과 점 사이의 선을 하나씩 그어요. 네모 한 칸의 네 번째 선을 그으면 그 칸이 내 것이 되고 한 번 더 해요. 칸을 더 많이 차지한 사람이 이겨요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="dots" id="bd"></div>',
    r'''
const N = 4, NH = (N + 1) * N, NL = NH + N * (N + 1);
const hI = (r, c) => r * N + c, vI = (r, c) => NH + r * (N + 1) + c, boxLines = (r, c) => [hI(r, c), hI(r + 1, c), vI(r, c), vI(r, c + 1)];
const colorOf = id => id === P.first ? 1 : 2, COL = ["", "#2f6fdf", "#e4572e"];
function newRound() { return { ph: "play", L: Array(NL).fill(0), B: Array(N * N).fill(0), turn: P.first, last: -1 }; }
function onAct(from, d) {
  if (d.t === "line" && P.ph === "play" && from === P.turn) { const l = +d.l; if (!(l >= 0 && l < NL) || P.L[l]) return; const v = colorOf(from); P.L[l] = v; P.last = l; let got = 0;
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (!P.B[r * N + c] && boxLines(r, c).every(x => P.L[x])) { P.B[r * N + c] = v; got++; }
    if (P.B.every(Boolean)) { const c1 = P.B.filter(x => x === 1).length, c2 = P.B.length - c1; finish(c1 === c2 ? "D" : c1 > c2 ? P.first : oppOf(P.first)); }
    else if (!got) P.turn = oppOf(from);
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.L) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; $("cnt").innerHTML = ""; if (P) common(); return; }
  const can = P.ph === "play" && P.turn === me, chip = id => (id === P.first ? "🔵 " : "🔴 ") + nm(id);
  $("st").textContent = P.ph === "end" ? endText() : !amPlayer() ? `구경 중 · ${chip(P.turn)} 차례` : can ? `내 차례예요 (${colorOf(me) === 1 ? "🔵" : "🔴"}) · 선을 하나 그어요` : "상대 차례예요…";
  $("cnt").innerHTML = [P.first, oppOf(P.first)].map((id, k) => `<div class="stat"><small>${k ? "🔴" : "🔵"} ${esc(nm(id))}</small><b>${P.B.filter(x => x === k + 1).length}칸</b></div>`).join("") + `<div class="stat"><small>남은 칸</small><b>${P.B.filter(x => !x).length}</b></div>`;
  let h = "";
  for (let R = 0; R <= 2 * N; R++) for (let C = 0; C <= 2 * N; C++) {
    if (R % 2 === 0 && C % 2 === 0) h += '<i class="dt"></i>';
    else if (R % 2 === 0 || C % 2 === 0) { const l = R % 2 === 0 ? hI(R / 2, (C - 1) / 2) : vI((R - 1) / 2, C / 2), v = P.L[l];
      h += `<button type="button" class="${R % 2 === 0 ? "hl" : "vl"}" data-l="${l}" style="${v ? "background:" + COL[v] : ""}${l === P.last ? ";outline:2px solid var(--fg)" : ""}"${can && !v ? "" : " disabled"} aria-label="선"></button>`; }
    else { const v = P.B[((R - 1) / 2) * N + (C - 1) / 2]; h += `<b class="bx" style="${v ? "background:color-mix(in srgb," + COL[v] + " 30%,transparent)" : ""}">${v === 1 ? "🔵" : v === 2 ? "🔴" : ""}</b>`; }
  }
  $("bd").innerHTML = h; $("bd").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "line", l: +b.dataset.l }));
  common();
}
render();
''', '''
.dots{display:grid;grid-template-columns:repeat(4,18px 1fr) 18px;grid-template-rows:repeat(4,18px 1fr) 18px;width:min(100%,320px);aspect-ratio:1;margin:0 auto}
.dots .dt{background:var(--fg);border-radius:50%}.dots button{border:0;padding:0;background:var(--line);border-radius:4px;margin:5px 0}.dots button.vl{margin:0 5px}.dots .dt{margin:3px}
.dots button:not([disabled]){background:color-mix(in srgb,var(--line) 60%,transparent);cursor:pointer}.dots .bx{display:flex;align-items:center;justify-content:center;font-size:1.2rem;font-weight:400}''')

# ── 칼라하: 구멍 6개에 콩 4알. 내 구멍의 콩을 시계 반대 방향으로 한 알씩(상대 창고는 건너뜀). 마지막 콩이 내 창고면 한 번 더,
#   (콩판은 P.bd — P.b는 공통 틀의 두 번째 선수라 쓰면 안 돼요) 내 빈 구멍이면 맞은편 콩까지 내 창고로. 한쪽 구멍이 모두 비면 남은 콩은 각자 창고로, 창고가 큰 쪽이 승리.
duo("net-mancala.html", "칼라하 (같이 하기)", "🫘", 30, "net-mancala-v1",
    "내 구멍(아래쪽)을 눌러 콩을 모두 꺼내 시계 반대 방향으로 한 알씩 뿌려요. 마지막 콩이 내 창고(오른쪽)에 들어가면 한 번 더! 마지막 콩이 내 빈 구멍에 떨어지면 맞은편 구멍의 콩을 모두 가져와요. 한쪽 구멍이 모두 비면 끝나고 창고가 더 큰 쪽이 이겨요.",
    '<p class="center" id="st"></p><div class="kal" id="bd"></div><p class="center note" id="who"></p>',
    r'''
const pits = s => s ? [7, 8, 9, 10, 11, 12] : [0, 1, 2, 3, 4, 5], store = s => s ? 13 : 6;
const sideOf = id => id === P.first ? 0 : 1;
function newRound() { return { ph: "play", bd: [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0], turn: P.first, last: -1, msg: "" }; }
function onAct(from, d) {
  if (d.t === "sow" && P.ph === "play" && from === P.turn) { const s = sideOf(from), i = +d.i, b = P.bd; if (!pits(s).includes(i) || !b[i]) return;
    let n = b[i], k = i; b[i] = 0; while (n) { k = (k + 1) % 14; if (k === store(1 - s)) continue; b[k]++; n--; }
    P.last = k; P.msg = ""; const extra = k === store(s);
    if (!extra && pits(s).includes(k) && b[k] === 1 && b[12 - k] > 0) { P.msg = `${nameOf(from)}가 맞은편 콩 ${b[12 - k]}알을 가져갔어요!`; b[store(s)] += b[12 - k] + 1; b[12 - k] = 0; b[k] = 0; }
    if (pits(0).every(x => !b[x]) || pits(1).every(x => !b[x])) { [0, 1].forEach(t => pits(t).forEach(x => { b[store(t)] += b[x]; b[x] = 0; })); finish(b[6] === b[13] ? "D" : b[6] > b[13] ? P.first : oppOf(P.first)); }
    else if (extra) P.msg = `${nameOf(from)}가 창고에 넣어서 한 번 더!`; else P.turn = oppOf(from);
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.bd) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; if (P) common(); return; }
  const s = amPlayer() ? sideOf(me) : 0, o = 1 - s, can = P.ph === "play" && P.turn === me, b = P.bd, ownerOf = t => t === 0 ? P.first : oppOf(P.first);
  $("st").textContent = P.ph === "end" ? endText() : (P.msg ? P.msg + " · " : "") + (!amPlayer() ? `구경 중 · ${nm(P.turn)} 차례` : can ? "내 차례예요 · 아래쪽 내 구멍을 눌러요" : "상대 차례예요…");
  const pit = (i, mine) => `<button type="button" data-i="${i}" class="${i === P.last ? "last" : ""}"${mine && can && b[i] ? "" : " disabled"}><b>${b[i]}</b></button>`;
  $("bd").innerHTML = `<div class="st" style="grid-row:1/3;grid-column:1">${b[store(o)]}<small>${esc(nm(ownerOf(o)))}</small></div>`
    + pits(o).slice().reverse().map(i => pit(i, false)).join("") + pits(s).map(i => pit(i, true)).join("")
    + `<div class="st" style="grid-row:1/3;grid-column:8">${b[store(s)]}<small>${esc(nm(ownerOf(s)))}</small></div>`;
  $("bd").querySelectorAll("button:not([disabled])").forEach(x => x.onclick = () => act({ t: "sow", i: +x.dataset.i }));
  $("who").textContent = `위쪽: ${nm(ownerOf(o))} · 아래쪽: ${nm(ownerOf(s))}`;
  common();
}
render();
''', '''
.kal{display:grid;grid-template-columns:1.1fr repeat(6,1fr) 1.1fr;grid-template-rows:1fr 1fr;gap:5px;width:min(100%,360px);margin:0 auto;background:#8a5a2b;padding:6px;border-radius:14px}
.kal button{aspect-ratio:1;border-radius:50%;border:0;background:#c99a63;color:#2b1a08;padding:0;font-family:var(--font-display);font-size:1.2rem}.kal button:not([disabled]){background:#f0c98f;box-shadow:0 0 0 2px #fff inset}
.kal button.last{outline:3px solid #ffd54a}.kal .st{background:#c99a63;border-radius:18px;color:#2b1a08;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:var(--font-display);font-size:1.5rem;min-width:0;overflow:hidden}.kal .st small{font-size:.6rem;font-family:var(--font-body);white-space:nowrap}''')

# ── 헥스: 5×5 육각 판, 번갈아 칸 차지. 먼저 하는 사람 🔵은 왼쪽↔오른쪽, 상대 🔴는 위↔아래를 먼저 이으면 승리(비김 없음).
duo("net-hex.html", "헥스 (같이 하기)", "🔷", 250, "net-hex-v1",
    "육각형 판에서 번갈아 칸을 차지해요. 🔵(먼저 하는 사람)는 왼쪽 변과 오른쪽 변을, 🔴는 위쪽 변과 아래쪽 변을 끊기지 않는 길로 먼저 이으면 이겨요. 비기는 일은 없어요.",
    '<p class="center" id="st"></p><div class="hexb" id="bd"></div><p class="center note">🔵 왼쪽 ↔ 오른쪽 · 🔴 위 ↕ 아래</p>',
    r'''
const N = 5, NB = [[-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0]];
const colorOf = id => id === P.first ? 1 : 2;
function linked(g, v) { const st = [], seen = new Set();
  for (let k = 0; k < N; k++) { const i = v === 1 ? k * N : k; if (g[i] === v) { st.push(i); seen.add(i); } }
  while (st.length) { const i = st.pop(), r = Math.floor(i / N), c = i % N; if (v === 1 ? c === N - 1 : r === N - 1) return true;
    for (const [dr, dc] of NB) { const rr = r + dr, cc = c + dc, j = rr * N + cc; if (rr >= 0 && cc >= 0 && rr < N && cc < N && g[j] === v && !seen.has(j)) { seen.add(j); st.push(j); } } }
  return false; }
function newRound() { return { ph: "play", g: Array(N * N).fill(0), turn: P.first, last: -1 }; }
function onAct(from, d) {
  if (d.t === "put" && P.ph === "play" && from === P.turn) { const i = +d.i; if (!(i >= 0 && i < N * N) || P.g[i]) return; P.g[i] = colorOf(from); P.last = i;
    if (linked(P.g, colorOf(from))) finish(from); else P.turn = oppOf(from); pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.g) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; if (P) common(); return; }
  const can = P.ph === "play" && P.turn === me, chip = id => (id === P.first ? "🔵 " : "🔴 ") + nm(id);
  $("st").textContent = P.ph === "end" ? endText() : !amPlayer() ? `구경 중 · ${chip(P.turn)} 차례` : can ? `내 차례예요 (${colorOf(me) === 1 ? "🔵 왼쪽↔오른쪽" : "🔴 위↕아래"})` : "상대 차례예요…";
  $("bd").innerHTML = Array.from({ length: N }, (_, r) => `<div class="hr" style="margin-left:${r * 6.6}%">${Array.from({ length: N }, (_, c) => { const i = r * N + c, v = P.g[i];
    return `<button type="button" data-i="${i}" class="${v === 1 ? "b" : v === 2 ? "r" : ""}${i === P.last ? " last" : ""}"${can && !v ? "" : " disabled"} aria-label="${r + 1}행 ${c + 1}열"></button>`; }).join("")}</div>`).join("");
  $("bd").querySelectorAll("button:not([disabled])").forEach(x => x.onclick = () => act({ t: "put", i: +x.dataset.i }));
  common();
}
render();
''', '''
.hexb{width:min(100%,340px);margin:0 auto;padding:8px 6px;border-left:6px solid #2f6fdf;border-right:6px solid #2f6fdf;border-top:6px solid #e4572e;border-bottom:6px solid #e4572e;border-radius:10px}
.hexb .hr{display:flex;gap:2px;margin-bottom:-9px;width:66%}.hexb button{flex:1;aspect-ratio:1/1.1;border:0;padding:0;background:var(--line);clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)}
.hexb button:not([disabled]){background:color-mix(in srgb,var(--line) 70%,var(--surface));cursor:pointer}.hexb button.b{background:#2f6fdf}.hexb button.r{background:#e4572e}.hexb button.last{filter:brightness(1.25)}''')

# ── 31 게임: 1부터 순서대로 번갈아 1~3개 외치기, 31을 말하면 짐.
duo("net-31.html", "31 게임 (같이 하기)", "🔢", 0, "net-31-v1",
    "번갈아 가며 숫자를 1부터 순서대로 1개~3개 외쳐요. 31을 말하는 사람이 져요!",
    '<p class="center" id="st"></p><div class="big" id="num"></div><div class="choice" id="ch" style="grid-template-columns:repeat(3,1fr)"></div><div id="log"></div>',
    r'''
function newRound() { return { ph: "play", n: 0, turn: P.first, log: [] }; }
function onAct(from, d) {
  if (d.t === "say" && P.ph === "play" && from === P.turn) { const k = +d.k; if (!(k >= 1 && k <= 3)) return; const nums = []; for (let j = 0; j < k && P.n < 31; j++) { P.n++; nums.push(P.n); }
    P.log.push([from, nums]); if (P.n >= 31) finish(oppOf(from)); else P.turn = oppOf(from); pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || P.n === undefined) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("ch").innerHTML = ""; if (P) common(); return; }
  const can = P.ph === "play" && P.turn === me;
  $("st").textContent = P.ph === "end" ? endText() + ` (31을 말한 사람: ${nm(oppOf(P.win))})` : !amPlayer() ? `구경 중 · ${nm(P.turn)} 차례` : can ? "내 차례! 몇 개 외칠까요?" : "상대 차례예요…";
  $("num").textContent = P.n ? P.n : "시작!";
  $("ch").innerHTML = [1, 2, 3].map(k => { const ns = Array.from({ length: k }, (_, j) => P.n + j + 1).filter(x => x <= 31); return `<button type="button" data-k="${k}"${can && ns.length === k ? "" : " disabled"}>${ns.join(", ") || "-"}</button>`; }).join("");
  $("ch").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "say", k: +b.dataset.k }));
  $("log").innerHTML = P.log.slice(-6).reverse().map(([id, ns]) => `<div class="li"><span>${esc(nm(id))}</span><b>${ns.join(", ")}</b></div>`).join("");
  common();
}
render();
''')

# ── 피그 주사위: 굴려 나온 눈을 모으다 '저금'하면 내 점수, 1이 나오면 이번 차례 점수를 잃고 넘어감. 먼저 100점이면 승리.
duo("net-pig.html", "피그 주사위 (같이 하기)", "🎲", 330, "net-pig-v1",
    "차례마다 주사위를 굴려서 나온 눈을 모아요. 원하는 때 '저금'을 누르면 모은 점수가 내 점수가 돼요. 하지만 1이 나오면 이번 차례에 모은 점수를 모두 잃고 차례가 넘어가요! 먼저 100점을 모으는 사람이 이겨요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="big" id="die"></div><p class="center" id="tp"></p><div class="row" id="btns"><button class="btn" id="roll" type="button">🎲 굴리기</button><button class="btn ghost" id="hold" type="button">💰 저금</button></div>',
    r'''
const GOAL = 100, DIE = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"];
function newRound() { return { ph: "play", pts: { [P.a]: 0, [P.b]: 0 }, tp: 0, roll: 0, turn: P.first, msg: "" }; }
function onAct(from, d) {
  if (P.ph === "play" && from === P.turn && d.t === "roll") { const r = ri(1, 6); P.roll = r; if (r === 1) { P.msg = `${nameOf(from)}: 1이 나와서 ${P.tp}점을 잃었어요!`; P.tp = 0; P.turn = oppOf(from); } else { P.tp += r; P.msg = ""; } pushS(); }
  else if (P.ph === "play" && from === P.turn && d.t === "hold" && P.tp) { P.pts[from] += P.tp; P.msg = `${nameOf(from)}가 ${P.tp}점을 저금했어요`; P.tp = 0; P.roll = 0; if (P.pts[from] >= GOAL) finish(from); else P.turn = oppOf(from); pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.pts) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("btns").hidden = true; if (P) common(); return; }
  const can = P.ph === "play" && P.turn === me;
  $("st").textContent = P.ph === "end" ? endText() : (P.msg ? P.msg + " · " : "") + (!amPlayer() ? `구경 중 · ${nm(P.turn)} 차례` : can ? "내 차례! 굴릴까요, 저금할까요?" : "상대 차례예요…");
  $("cnt").innerHTML = [P.a, P.b].map(id => `<div class="stat"><small>${esc(nm(id))}</small><b>${P.pts[id]}</b></div>`).join("") + `<div class="stat"><small>목표</small><b>${GOAL}</b></div>`;
  $("die").textContent = P.roll ? DIE[P.roll] : "🎲"; $("tp").textContent = P.ph === "play" ? `이번 차례에 모은 점수: ${P.tp}점` : "";
  $("btns").hidden = !can; $("hold").disabled = !P.tp;
  common();
}
$("roll").onclick = () => act({ t: "roll" }); $("hold").onclick = () => act({ t: "hold" });
render();
''')

# ── 카드 짝 대결: 16장(8쌍), 번갈아 두 장씩 뒤집어 같으면 1점 + 한 번 더. 카드 그림은 방장 폰만 알고, 뒤집힌 카드만 모두에게 보여요.
duo("net-memory.html", "카드 짝 대결 (같이 하기)", "🃏", 300, "net-memory-v1",
    "번갈아 카드를 두 장씩 뒤집어요. 그림이 같으면 1점을 얻고 한 번 더! 다르면 다시 뒤집히고 상대 차례예요. 모두 짝을 맞췄을 때 점수가 더 높은 사람이 이겨요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="grid8" id="bd" style="grid-template-columns:repeat(4,1fr)"></div>',
    r'''
const EMOS = ["🍎", "🍌", "🍇", "🍓", "🍊", "🍑", "🍉", "🍍", "🥕", "🐶", "🐱", "🐰", "🐻", "🐼", "🦊", "🐸", "🌸", "🌻", "🚗", "🚀", "🎈", "🎁", "⚽", "🎵"];
function newRound() { const pick = shuf(EMOS).slice(0, 8); H.deck = shuf([...pick, ...pick]); return { ph: "play", show: {}, open: [], own: {}, pts: { [P.a]: 0, [P.b]: 0 }, turn: P.first, busy: false }; }
function onAct(from, d) {
  if (d.t === "flip" && P.ph === "play" && from === P.turn && !P.busy) { const i = +d.i; if (!(i >= 0 && i < 16) || P.own[i] || P.open.includes(i)) return;
    P.open.push(i); P.show[i] = H.deck[i];
    if (P.open.length === 2) { const [x, y] = P.open;
      if (H.deck[x] === H.deck[y]) { P.own[x] = P.own[y] = from; P.pts[from]++; P.open = []; if (Object.keys(P.own).length === 16) { const pa = P.pts[P.a], pb = P.pts[P.b]; finish(pa === pb ? "D" : pa > pb ? P.a : P.b); } }
      else { P.busy = true; pushS(); setTimeout(() => { delete P.show[x]; delete P.show[y]; P.open = []; P.busy = false; P.turn = oppOf(from); pushS(); }, 1100); return; } }
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.show) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; if (P) common(); return; }
  const can = P.ph === "play" && P.turn === me && !P.busy;
  $("st").textContent = P.ph === "end" ? endText() : P.busy ? "아쉬워요, 짝이 아니에요!" : !amPlayer() ? `구경 중 · ${nm(P.turn)} 차례` : can ? "내 차례! 카드 두 장을 뒤집어요" : "상대 차례예요…";
  $("cnt").innerHTML = [P.a, P.b].map(id => `<div class="stat"><small>${esc(nm(id))}</small><b>${P.pts[id]}쌍</b></div>`).join("") + `<div class="stat"><small>남은 짝</small><b>${8 - Object.keys(P.own).length / 2}</b></div>`;
  $("bd").innerHTML = Array.from({ length: 16 }, (_, i) => { const e = P.show[i], o = P.own[i]; return `<button type="button" data-i="${i}" style="font-size:1.8rem;background:${o ? (o === P.a ? "color-mix(in srgb,#2f6fdf 25%,var(--surface))" : "color-mix(in srgb,#e4572e 25%,var(--surface))") : e ? "var(--surface)" : "var(--accent)"};border:1px solid var(--line)"${can && !e && !o ? "" : " disabled"} aria-label="카드">${e || ""}</button>`; }).join("");
  $("bd").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "flip", i: +b.dataset.i }));
  common();
}
render();
''')

# ── 가위바위보 대결: 둘이 몰래 고르고 동시에 공개, 3번 먼저 이기면 승리.
duo("net-rps.html", "가위바위보 대결 (같이 하기)", "✊", 15, "net-rps-v1",
    "둘이 각자 폰에서 몰래 고르면 동시에 공개돼요. 바위는 가위를, 가위는 보를, 보는 바위를 이겨요. 3번 먼저 이기면 승리!",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="big" id="rev"></div><div class="choice" id="ch" style="grid-template-columns:repeat(3,1fr)"></div>',
    r'''
const HANDS = [["✊", "바위"], ["✌️", "가위"], ["✋", "보"]], WIN = 3;   // 0>1, 1>2, 2>0
function newRound() { return { ph: "play", w: { [P.a]: 0, [P.b]: 0 }, picked: {}, rev: null, rno: 1 }; }
function onAct(from, d) {
  if (d.t === "pick" && P.ph === "play" && !P.rev && !P.picked[from]) { const h = +d.h; if (!(h >= 0 && h < 3)) return; H[from] = h; P.picked[from] = 1;
    if (P.picked[P.a] && P.picked[P.b]) { const ha = H[P.a], hb = H[P.b], win = ha === hb ? null : (ha + 1) % 3 === hb ? P.a : P.b;
      P.rev = { [P.a]: ha, [P.b]: hb, win }; if (win) P.w[win]++; delete H[P.a]; delete H[P.b];
      if (win && P.w[win] >= WIN) finish(win); else setTimeout(() => { if (P.ph !== "play") return; P.rev = null; P.picked = {}; P.rno++; pushS(); }, 1800); }
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.w) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("ch").innerHTML = ""; if (P) common(); return; }
  const pl = amPlayer(), can = pl && P.ph === "play" && !P.rev && !P.picked[me], r = P.rev;
  $("st").textContent = P.ph === "end" ? endText() : r ? (r.win ? `${nm(r.win) === "나" ? "이번 판은 내가 이겼어요!" : nm(r.win) + " 이겼어요!"}` : "비겼어요! 다시!") : !pl ? `구경 중 · ${P.rno}번째 판` : can ? `${P.rno}번째 판 · 몰래 골라요!` : "상대를 기다려요…";
  $("cnt").innerHTML = [P.a, P.b].map(id => `<div class="stat"><small>${esc(nm(id))}</small><b>${P.w[id]}승</b></div>`).join("") + `<div class="stat"><small>목표</small><b>${WIN}승</b></div>`;
  $("rev").innerHTML = r ? `${HANDS[r[P.a]][0]} <small style="font-size:.4em">vs</small> ${HANDS[r[P.b]][0]}<div class="note">${esc(nm(P.a))} · ${esc(nm(P.b))}</div>` : [P.a, P.b].map(id => P.picked[id] ? "🫵" : "🤔").join(" ");
  $("ch").innerHTML = pl ? HANDS.map(([e, n], i) => `<button type="button" data-h="${i}"${can ? "" : " disabled"}>${e}<div class="note">${n}</div></button>`).join("") : "";
  $("ch").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "pick", h: +b.dataset.h }));
  common();
}
render();
''')

# ── 하이카드 대결: 각자 카드 10장(1~13), 매 판 몰래 한 장씩 내서 큰 쪽이 1점, 10판 뒤 많이 이긴 쪽이 승리. 패는 각자 폰에만(방장이 따로 보냄).
duo("net-highcard.html", "하이카드 대결 (같이 하기)", "🂡", 45, "net-highcard-v1",
    "카드 10장(1~13 중 랜덤)을 받아요. 매 판 내 카드 한 장을 몰래 골라 내면 동시에 공개되고, 숫자가 큰 쪽이 1점! 큰 카드를 언제 쓸지 잘 생각하세요. 10판 뒤 더 많이 이긴 쪽이 승리해요. 내 카드는 내 폰에만 보여요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="big" id="rev"></div><div class="choice" id="hand" style="grid-template-columns:repeat(5,1fr)"></div><div id="log"></div>',
    r'''
let hand = [];
function newRound() { const deal = () => Array.from({ length: 10 }, () => ri(1, 13)).sort((x, y) => x - y); H.hand = { [P.a]: deal(), [P.b]: deal() }; H.pick = {};
  return { ph: "play", rno: 1, w: { [P.a]: 0, [P.b]: 0 }, picked: {}, rev: null, log: [] }; }
function afterPush() { if (H.hand) [P.a, P.b].forEach(id => privTo(id, { hand: H.hand[id] })); }
function onPriv(d) { if (Array.isArray(d.hand)) { hand = d.hand; render(); } }
function onAct(from, d) {
  if (d.t === "play" && P.ph === "play" && !P.rev && !P.picked[from]) { const c = +d.c, k = H.hand[from].indexOf(c); if (k < 0) return; H.hand[from].splice(k, 1); H.pick[from] = c; P.picked[from] = 1;
    if (P.picked[P.a] && P.picked[P.b]) { const ca = H.pick[P.a], cb = H.pick[P.b], win = ca === cb ? null : ca > cb ? P.a : P.b; if (win) P.w[win]++;
      P.rev = { [P.a]: ca, [P.b]: cb, win }; P.log.push([ca, cb]); H.pick = {};
      if (P.rno >= 10) { const wa = P.w[P.a], wb = P.w[P.b]; finish(wa === wb ? "D" : wa > wb ? P.a : P.b); }
      else setTimeout(() => { if (P.ph !== "play") return; P.rev = null; P.picked = {}; P.rno++; pushS(); }, 1600); }
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
function render() {
  if (!P || !P.w) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("hand").innerHTML = ""; if (P) common(); return; }
  const pl = amPlayer(), can = pl && P.ph === "play" && !P.rev && !P.picked[me], r = P.rev;
  $("st").textContent = P.ph === "end" ? endText() : r ? (r.win ? (r.win === me ? "이번 판은 내가 이겼어요!" : `${nm(r.win)} 이겼어요!`) : "같은 숫자! 비겼어요") : !pl ? `구경 중 · ${P.rno}/10판` : can ? `${P.rno}/10판 · 낼 카드를 골라요` : "상대를 기다려요…";
  $("cnt").innerHTML = [P.a, P.b].map(id => `<div class="stat"><small>${esc(nm(id))}</small><b>${P.w[id]}점</b></div>`).join("") + `<div class="stat"><small>판</small><b>${Math.min(P.rno, 10)}/10</b></div>`;
  $("rev").innerHTML = r ? `${r[P.a]} <small style="font-size:.4em">vs</small> ${r[P.b]}<div class="note">${esc(nm(P.a))} · ${esc(nm(P.b))}</div>` : [P.a, P.b].map(id => P.picked[id] ? "🂠" : "🤔").join(" ");
  $("hand").innerHTML = pl && P.ph === "play" ? hand.map(c => `<button type="button" data-c="${c}"${can ? "" : " disabled"}>${c}</button>`).join("") : "";
  $("hand").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => { act({ t: "play", c: +b.dataset.c }); });
  $("log").innerHTML = P.log.length ? `<div class="lb">지난 판 (${esc(nm(P.a))} : ${esc(nm(P.b))})</div>` + P.log.map(([x, y], i) => `<div class="li"><span>${i + 1}판</span><b>${x} : ${y}</b></div>`).reverse().join("") : "";
  common();
}
render();
''')

# ───────── 여러 명 파티 게임 공통: 모든 기기가 참가, 방장 게임이 진행·판정하고 공개 상태 P를 나눠 줘요. 한 사람에게만 보낼 것은 privTo.
# 게임마다 initState()·onRoster()·onAct(from, d)·onPriv(d)·changed(was)·render()를 만들어요.
PARTY_JS = NET_JS + r'''
let me = null, isHost = false, P = null, players = [];
const H = {};
function pushS() { if (!isHost) return; P.nm = Object.fromEntries(players.map(p => [p.id, p.name])); NET.send("*", { t: "state", P }); render(); if (typeof afterPush === "function") afterPush(); }
const act = d => { if (isHost) onAct("host", d); else NET.send("host", d); };
const privTo = (id, d) => { d.t = "priv"; if (id === me) onPriv(d); else NET.send(id, d); };
const pn = id => id === me ? "나" : (P && P.nm && P.nm[id]) || "?";
const ids = () => players.map(p => p.id);
NET.on("init", m => { me = m.me.id; isHost = m.isHost; players = m.players; if (isHost) { P = initState(); pushS(); } else NET.send("host", { t: "hello" }); render(); });
NET.on("roster", ps => { players = ps; if (isHost && P) { onRoster(); pushS(); } else render(); });
NET.on("msg", (from, d) => { if (isHost) { if (d.t === "hello") pushS(); else onAct(from, d); } else if (d.t === "state") { const was = P; P = d.P; changed(was); render(); } else if (d.t === "priv") onPriv(d); });
const buzzV = ms => { try { navigator.vibrate && navigator.vibrate(ms); } catch (e) {} };
'''
def party(fn, title, emoji, hue, key, help_, body, js, css=""):
    make("out/" + fn, title, emoji, hue, key, help_, '  <div class="card">' + body + '</div>', PARTY_JS + js, CSS + css)

# ── 퀴즈 버저: 방장(진행자)이 문제를 내고 읽으면, 모든 폰이 각자 버저. 먼저 누른 순서대로 답할 기회. 방장이 ⭕(+1점)/❌(다음 사람에게).
#   문제는 방장이 직접 내도 되고, '🎲 문제 뽑아 주기'로 시작 화면의 퀴즈(43개)에서 뽑을 수 있어요(정답은 방장 화면에만). 퀴즈 파일을 그때 받아서 문제 목록(const D)만 꺼내 써요.
import json as _j, gamenum as _gn
_NUMS = _gn.ensure()
QUIZZES = [[g[0], g[1], g[2], _NUMS[g[0]]] for g in _gn.index_games() if g[4] == "quiz" and "const D = [" in open("../../" + g[0], encoding="utf-8").read()]
party("net-buzzer.html", "퀴즈 버저 (같이 하기)", "🔔", 0, "net-buzzer-v1",
      "TV 퀴즈처럼 '먼저 누르기' 대결이에요. 방장(진행자)이 문제를 소리 내어 읽고 '문제 시작'을 누르면, 답을 아는 사람은 자기 폰의 큰 버튼을 눌러요. 가장 먼저 누른 사람이 소리 내어 답하고, 방장이 ⭕(정답 +1점)/❌(오답 → 다음 사람에게 기회)를 눌러요. 문제는 방장이 직접 내도 되고 '🎲 문제 뽑아 주기'로 시작 화면의 퀴즈(한국사·일본어·한자·상식 등)에서 뽑아도 돼요.",
      '<details class="guide" id="guide" open><summary><b>❓ 어떻게 하나요?</b></summary><ol id="steps"></ol></details>'
      '<p class="center" id="st"></p><div id="qshow" class="qbox" hidden></div>'
      '<div id="host" hidden style="display:grid;gap:8px">'
      '<div class="qbox host"><div class="row" style="grid-template-columns:1fr auto"><select id="qcat" aria-label="퀴즈 고르기"></select><button class="btn ghost sm" id="qpick" type="button">🎲 문제 뽑아 주기</button></div><div id="qhost" class="note">직접 문제를 내도 되고, 버튼을 눌러 문제를 뽑아도 돼요. (정답은 방장 화면에만 보여요)</div>'
      '<label class="note" style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="qall" checked> 문제를 모두의 화면에도 보여 주기 (정답은 빼고)</label><label class="note" style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="qopt" checked> 보기 4개도 함께 보여 주기</label></div>'
      '<label class="note" style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="mc" checked> 방장은 진행만 해요 (버저 안 누름)</label>'
      '<button class="btn" id="go" type="button">▶ 문제 시작 (버저 켜기)</button><div class="row"><button class="btn ghost" id="okb" type="button">⭕ 정답 (+1점)</button><button class="btn ghost" id="nob" type="button">❌ 오답</button></div></div>'
      '<button type="button" id="bz" class="buzz">누르기!</button><div id="ord"></div><div id="score"></div><button class="btn ghost sm" id="rst" type="button" hidden>점수 초기화</button>',
      r'''
const QUIZZES = ''' + _j.dumps(QUIZZES, ensure_ascii=False) + r''';
let curQ = null; const qCache = {};
// 퀴즈 파일에서 문제 목록(const D = [[문제, 정답, [오답…]], …])만 꺼내요
async function loadQuiz(f) { if (qCache[f]) return qCache[f]; const t = await (await fetch(f)).text(), i = t.indexOf("const D = ["), j = i + t.slice(i).search(/\];\r?\n/); const d = JSON.parse(t.slice(i + 10, j + 1)).filter(x => x && x[0] && x[1]); qCache[f] = d; return d; }
function initState() { return { ph: "idle", order: [], out: [], pts: {}, mc: true, q: 0, qtext: "", ans: "" }; }
function onRoster() { P.order = P.order.filter(id => ids().includes(id)); }
const canBuzz = id => !(P.mc && id === "host");
function onAct(from, d) {
  if (d.t === "buzz") { if (P.ph === "idle" || !canBuzz(from) || P.order.includes(from) || P.out.includes(from)) return; P.order.push(from); if (P.ph === "open") P.ph = "locked"; buzzV(150); }
  else if (from !== "host") return;
  else if (d.t === "go") { P.ph = "open"; P.order = []; P.out = []; P.q++; P.qtext = d.q || ""; P.opts = Array.isArray(d.o) ? d.o.slice(0, 4) : []; P.ans = ""; }
  else if (d.t === "ok" && P.order.length) { const w = P.order[0]; P.pts[w] = (P.pts[w] || 0) + 1; P.ph = "idle"; P.order = []; P.out = []; P.ans = d.a || ""; P.lastWin = w; }
  else if (d.t === "no" && P.order.length) { P.out.push(P.order.shift()); P.ph = P.order.length ? "locked" : "open"; }
  else if (d.t === "mc") { P.mc = !!d.v; }
  else if (d.t === "rst") { P.pts = {}; }
  else return;
  pushS();
}
function onPriv() {}
function changed(was) { if (P.order[0] === me && (!was || was.order[0] !== me)) buzzV([200, 80, 200]); }
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  const host = isHost, rank = P.order.indexOf(me), eligible = canBuzz(me);
  $("steps").innerHTML = host ? "<li>문제를 직접 생각하거나 <b>🎲 문제 뽑아 주기</b>를 눌러요.</li><li>문제를 소리 내어 읽고 <b>▶ 문제 시작</b>을 눌러요. 그때부터 모두의 버저가 켜져요.</li><li>가장 먼저 누른 사람이 소리 내어 답하면 <b>⭕ 정답</b>(+1점) 또는 <b>❌ 오답</b>(다음으로 누른 사람에게 기회)을 눌러요.</li>"
    : "<li>방장(진행자)이 문제를 소리 내어 읽어요.</li><li>방장이 문제를 시작하면 아래 <b>큰 빨간 버튼</b>이 켜져요. 답을 알면 누구보다 먼저 눌러요!</li><li>1등으로 누르면 소리 내어 답해요. 맞으면 +1점, 틀리면 다음으로 누른 사람에게 기회가 가요.</li>";
  $("host").hidden = !host; $("rst").hidden = !host; $("mc").checked = P.mc;
  $("okb").disabled = $("nob").disabled = !P.order.length; $("go").disabled = P.ph !== "idle";
  $("st").textContent = P.ph === "idle" ? (host ? (P.q ? `${P.q}번 문제 끝! 다음 문제를 내 주세요` : "문제를 정하고 '▶ 문제 시작'을 눌러요") : `${P.q ? P.q + "번 문제 끝! " : ""}방장이 다음 문제를 시작하면 버저를 눌러요`) : P.order.length ? `🙋 ${pn(P.order[0])} 답하세요!` : "🔔 지금 누르세요!";
  $("qshow").hidden = !(P.qtext || P.ans) || host; $("qshow").innerHTML = (P.qtext ? `<b>Q${P.q}.</b> ${esc(P.qtext)}` : "") + ((P.opts || []).length ? `<ol class="opts">${P.opts.map(o => `<li>${esc(o)}</li>`).join("")}</ol>` : "") + (P.ans ? `<div class="ok">정답: ${esc(P.ans)}</div>` : "");
  $("bz").hidden = !eligible; $("bz").disabled = P.ph === "idle" || rank >= 0 || P.out.includes(me);
  $("bz").textContent = rank === 0 ? "1등! 답하세요 🙋" : rank > 0 ? `${rank + 1}번째로 눌렀어요` : P.out.includes(me) ? "이번 문제는 끝 ❌" : P.ph === "idle" ? "기다려요…" : "누르기!";
  $("bz").classList.toggle("on", rank === 0);
  $("ord").innerHTML = P.order.length ? '<div class="lb">누른 순서</div>' + P.order.map((id, i) => `<div class="li"><span>${i + 1}. ${esc(pn(id))}</span>${i === 0 ? "<b>답할 차례</b>" : ""}</div>`).join("") : "";
  const ps = players.filter(p => canBuzz(p.id));
  $("score").innerHTML = '<div class="lb">점수</div>' + ps.map(p => `<div class="li"><span>${esc(pn(p.id))}</span><b>${P.pts[p.id] || 0}점</b></div>`).join("");
}
$("qcat").innerHTML = '<option value="">🎲 아무 퀴즈</option>' + QUIZZES.map(([f, e, t, n]) => `<option value="${f}">#${n} ${e} ${esc(t)}</option>`).join("");
{ const pre = decodeURIComponent((location.hash.match(/quiz=([^&]+)/) || [])[1] || ""), g = QUIZZES.find(x => x[0] === pre); if (g) { $("qcat").value = pre; $("qhost").innerHTML = `<b>${g[1]} ${esc(g[2])}</b> 퀴즈를 골랐어요. '🎲 문제 뽑아 주기'를 눌러 시작해요.`; } }
$("qpick").onclick = async () => { const f = $("qcat").value || QUIZZES[ri(0, QUIZZES.length - 1)][0], g = QUIZZES.find(x => x[0] === f); $("qhost").textContent = "문제를 가져오는 중…";
  try { const d = await loadQuiz(f), x = d[ri(0, d.length - 1)], opts = shuf([x[1], ...(x[2] || []).slice(0, 3)]);
    curQ = { q: x[0], a: x[1], c: g ? g[2] : "", o: opts.length > 1 ? opts : [] };
    $("qhost").innerHTML = `<b>[${esc(curQ.c)}]</b> ${esc(curQ.q)}` + (curQ.o.length ? `<ol class="opts">${curQ.o.map(o => `<li${o === curQ.a ? ' class="ok"' : ""}>${esc(o)}</li>`).join("")}</ol>` : "") + `<div class="ok">정답: ${esc(curQ.a)}</div>`;
  } catch (e) { curQ = null; $("qhost").textContent = "⚠️ 문제를 가져오지 못했어요. 다시 눌러 주세요."; } };
$("bz").onclick = () => act({ t: "buzz" });
$("go").onclick = () => { const sh = curQ && $("qall").checked; act({ t: "go", q: sh ? curQ.q : "", o: sh && $("qopt").checked ? curQ.o : [] }); if (P && P.q > 0) $("guide").open = false; };
$("okb").onclick = () => { act({ t: "ok", a: curQ ? curQ.a : "" }); curQ = null; $("qhost").textContent = "다음 문제를 직접 내거나 뽑아 주세요."; };
$("nob").onclick = () => act({ t: "no" });
$("mc").onchange = () => act({ t: "mc", v: $("mc").checked }); $("rst").onclick = () => { if (confirm("점수를 모두 0으로 할까요?")) act({ t: "rst" }); };
render();
''', '''
.buzz{width:min(100%,260px);aspect-ratio:1;margin:8px auto;display:block;border-radius:50%;border:0;background:#e4572e;color:#fff;font-family:var(--font-display);font-size:1.8rem;box-shadow:0 8px 0 #a33a1c}
.buzz:active:not([disabled]){transform:translateY(4px);box-shadow:0 4px 0 #a33a1c}.buzz[disabled]{background:#9aa3b5;box-shadow:0 8px 0 #6b7385}.buzz.on{background:#1f9d62;box-shadow:0 8px 0 #146b42}
.guide{background:var(--soft);border-radius:12px;padding:10px 12px}.guide ol{margin:6px 0 0;padding-left:20px;display:grid;gap:4px;font-size:.92rem}
.opts{margin:4px 0 0;padding-left:22px;display:grid;gap:2px}.opts li.ok{color:var(--ok);font-weight:700}
.qbox{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:10px 12px;display:grid;gap:6px}.qbox .ok{color:var(--ok);font-weight:700}
select{width:100%;background:var(--surface);color:var(--fg);border:1px solid var(--line);border-radius:10px;padding:8px 10px;font:inherit}''')

# ── 역할 뽑기(마피아): 방장이 인원 구성을 정하고 나눠 주면, 각자 폰에 자기 역할만 보여요. 방장을 진행자로 하면 방장은 모두의 역할을 봐요.
party("net-mafia.html", "역할 뽑기 (같이 하기)", "🕵️", 270, "net-mafia-v1",
      "방장이 마피아 수와 경찰·의사를 정하고 '역할 나눠 주기'를 누르면, 각자 폰에 자기 역할만 몰래 보여요. 폰을 돌릴 필요가 없어요. 방장을 진행자로 하면 방장은 역할 없이 모두의 역할을 볼 수 있어요.",
      '<p class="center" id="st"></p><div id="host" hidden style="display:grid;gap:8px">'
      '<label class="lb" for="mf">마피아 수</label><select id="mf"><option>1</option><option>2</option><option>3</option></select>'
      '<label class="note" style="display:flex;gap:8px"><input type="checkbox" id="po" checked> 👮 경찰 넣기</label><label class="note" style="display:flex;gap:8px"><input type="checkbox" id="dr" checked> 🩺 의사 넣기</label>'
      '<label class="note" style="display:flex;gap:8px"><input type="checkbox" id="mcm"> 🎙️ 방장은 진행자 (역할 없음, 모두의 역할 보기)</label><button class="btn" id="deal" type="button">🎭 역할 나눠 주기</button></div>'
      '<div id="mine" style="display:grid;gap:8px"></div><div id="all"></div>',
      r'''
const INFO = { "마피아": "밤마다 시민 한 명을 몰래 지목해 없애요. 정체를 들키지 마세요!", "경찰": "밤에 한 명을 골라 마피아인지 확인할 수 있어요.", "의사": "밤에 한 명을 골라 마피아의 공격에서 살릴 수 있어요.", "시민": "낮 토론으로 마피아를 찾아내 투표로 몰아내세요." };
const EMO = { "마피아": "🔪", "경찰": "👮", "의사": "🩺", "시민": "🙂" };
let myRole = null, myRno = 0, showRole = false;
function initState() { return { ph: "set", mf: 1, po: true, dr: true, mc: false, rno: 0, got: [], cnt: {} }; }
function onRoster() {}
const parts = () => ids().filter(id => !(P.mc && id === "host"));
function onAct(from, d) {
  if (from !== "host") return;
  if (d.t === "opt") { Object.assign(P, { mf: Math.max(1, Math.min(3, +d.mf || 1)), po: !!d.po, dr: !!d.dr, mc: !!d.mc }); }
  else if (d.t === "deal") { const ps = parts(); if (ps.length < 3) { alert("역할을 나누려면 참가자가 3명 이상이어야 해요."); return; }
    const mf = Math.min(P.mf, Math.max(1, Math.floor((ps.length - 1) / 2))), roles = Array(mf).fill("마피아"); if (P.po && roles.length < ps.length - 1) roles.push("경찰"); if (P.dr && roles.length < ps.length - 1) roles.push("의사");
    while (roles.length < ps.length) roles.push("시민"); const sh = shuf(roles); H.roles = {}; ps.forEach((id, i) => { H.roles[id] = sh[i]; });
    P.rno++; P.ph = "dealt"; P.got = ps; P.cnt = sh.reduce((o, r) => (o[r] = (o[r] || 0) + 1, o), {}); }
  else return;
  pushS();
}
function afterPush() { if (H.roles) Object.entries(H.roles).forEach(([id, role]) => privTo(id, { role, rno: P.rno })); }
function onPriv(d) { if (d.rno !== myRno) { myRno = d.rno; myRole = d.role; showRole = false; buzzV(120); render(); } }
function changed(was) {}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  $("host").hidden = !isHost; $("mf").value = P.mf; $("po").checked = P.po; $("dr").checked = P.dr; $("mcm").checked = P.mc; $("deal").textContent = P.rno ? "🔄 다시 나눠 주기" : "🎭 역할 나눠 주기";
  const comp = Object.entries(P.cnt).map(([r, n]) => `${EMO[r]} ${r} ${n}`).join(" · ");
  $("st").textContent = P.ph === "set" ? (isHost ? `참가자 ${parts().length}명 · 구성을 정하고 나눠 주세요` : "방장이 역할을 나눠 주기를 기다려요…") : `${P.rno}번째 판 · ${comp}`;
  const inGame = P.got.includes(me) && myRno === P.rno && myRole;
  $("mine").innerHTML = P.ph !== "dealt" ? "" : !P.got.includes(me) ? (P.mc && me === "host" ? "" : '<p class="note center">이번 판에는 역할이 없어요 (다음 판부터 참가)</p>') : !inGame ? '<p class="note center">역할을 받는 중…</p>'
    : showRole ? `<div class="big">${EMO[myRole]}<div>${myRole}</div></div><p class="center">${INFO[myRole]}</p><button class="btn ghost" id="hide" type="button">🙈 숨기기</button>` : '<button class="btn" id="see" type="button" style="padding:28px">👀 내 역할 보기 (주변에서 안 보이게!)</button>';
  if ($("see")) $("see").onclick = () => { showRole = true; render(); }; if ($("hide")) $("hide").onclick = () => { showRole = false; render(); };
  $("all").innerHTML = isHost && P.mc && P.ph === "dealt" && H.roles ? '<div class="lb">🎙️ 진행자만 보는 역할표</div>' + Object.entries(H.roles).map(([id, r]) => `<div class="li"><span>${esc(pn(id))}</span><b>${EMO[r]} ${r}</b></div>`).join("") : "";
}
const sendOpt = () => act({ t: "opt", mf: +$("mf").value, po: $("po").checked, dr: $("dr").checked, mc: $("mcm").checked });
["mf", "po", "dr", "mcm"].forEach(id => { $(id).onchange = sendOpt; });
$("deal").onclick = () => act({ t: "deal" });
render();
''', "select{width:100%;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:inherit}")

# ── 반응 대결(여러 명): 방장이 시작하면 각 폰이 몇 초 뒤 초록색으로 바뀌고, 각자 폰에서 잰 반응 시간을 겨뤄요(통신 지연과 상관없이 공평).
party("net-react.html", "반응 대결 (같이 하기)", "⚡", 120, "net-react-v1",
      "방장이 '시작'을 누르면 모든 폰이 빨간색이 됐다가, 잠시 뒤 초록색 '지금!'으로 바뀌어요. 그 순간 내 폰 화면을 누르세요! 반응 시간은 각자 폰에서 재서 공평해요. 너무 일찍 누르면 실격이에요. 가장 빠른 사람이 1점!",
      '<p class="center" id="st"></p><button type="button" id="pad" class="pad">기다려요</button><button class="btn" id="go" type="button" hidden>▶ 시작</button><div id="res"></div><div id="score"></div>',
      r'''
let armed = 0, t0 = 0, green = false, tmr = null, sent = 0;
function initState() { return { ph: "idle", rno: 0, wait: 0, res: {}, pts: {}, win: null }; }
function onRoster() { if (P.ph === "arm" && ids().every(id => P.res[id] !== undefined)) done(); }
function done() { if (P.ph !== "arm") return; P.ph = "done"; const ok = Object.entries(P.res).filter(([, v]) => v >= 0).sort((a, b) => a[1] - b[1]); P.win = ok.length ? ok[0][0] : null; if (P.win) P.pts[P.win] = (P.pts[P.win] || 0) + 1; }
function onAct(from, d) {
  if (d.t === "go" && from === "host" && P.ph !== "arm") { P.rno++; P.ph = "arm"; P.res = {}; P.win = null; P.wait = Math.round(1500 + Math.random() * 2500); const r = P.rno; setTimeout(() => { if (P.rno === r && P.ph === "arm") { done(); pushS(); } }, P.wait + 6000); }
  else if (d.t === "res" && P.ph === "arm" && d.r === P.rno && P.res[from] === undefined) { P.res[from] = d.foul ? -1 : Math.max(0, Math.round(+d.ms || 0)); if (ids().every(id => P.res[id] !== undefined)) done(); }
  else return;
  pushS();
}
function onPriv() {}
function changed(was) {}
function arm() { armed = P.rno; green = false; sent = 0; clearTimeout(tmr); tmr = setTimeout(() => { if (armed !== P.rno || P.ph !== "arm") return; green = true; t0 = performance.now(); buzzV(60); render(); }, P.wait); }
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  if (P.ph === "arm" && armed !== P.rno) arm();
  const mine = sent === P.rno || (P.res && P.res[me] !== undefined), pad = $("pad");
  $("go").hidden = !isHost || P.ph === "arm"; $("go").textContent = P.rno ? "▶ 다음 판" : "▶ 시작";
  pad.className = "pad " + (P.ph !== "arm" ? "" : mine ? "sent" : green ? "g" : "r");
  pad.textContent = P.ph !== "arm" ? (P.ph === "done" ? (P.win === me ? "🏆 내가 1등!" : "끝!") : "방장이 시작을 누르면…") : mine ? (P.res[me] === -1 ? "😅 너무 일찍 눌렀어요" : "다른 사람을 기다려요…") : green ? "지금!" : "초록색이 되면 누르세요";
  $("st").textContent = P.ph === "done" ? (P.win ? `🏆 ${pn(P.win)} 가장 빨랐어요!` : "모두 실격이에요!") : P.ph === "arm" ? `${P.rno}번째 판` : "준비됐나요?";
  const rs = Object.entries(P.res || {}).sort((a, b) => (a[1] < 0) - (b[1] < 0) || a[1] - b[1]);
  $("res").innerHTML = P.ph === "done" ? '<div class="lb">이번 판 결과</div>' + players.map(p => [p.id, P.res[p.id]]).sort((a, b) => ((a[1] ?? 1e9) < 0 ? 1e9 : (a[1] ?? 1e9)) - ((b[1] ?? 1e9) < 0 ? 1e9 : (b[1] ?? 1e9))).map(([id, v]) => `<div class="li"><span>${id === P.win ? "🏆 " : ""}${esc(pn(id))}</span><b>${v === undefined ? "—" : v < 0 ? "실격" : v + " ms"}</b></div>`).join("") : "";
  $("score").innerHTML = '<div class="lb">점수</div>' + players.map(p => `<div class="li"><span>${esc(pn(p.id))}</span><b>${P.pts[p.id] || 0}점</b></div>`).join("");
}
$("pad").onclick = () => { if (!P || P.ph !== "arm" || sent === P.rno || armed !== P.rno) return; sent = P.rno; if (green) act({ t: "res", r: P.rno, ms: performance.now() - t0 }); else { clearTimeout(tmr); act({ t: "res", r: P.rno, foul: true }); } render(); };
$("go").onclick = () => act({ t: "go" });
render();
''', '''
.pad{width:100%;height:220px;border:0;border-radius:18px;background:var(--soft);color:var(--fg);font-family:var(--font-display);font-size:1.8rem;touch-action:manipulation}
.pad.r{background:#d6453a;color:#fff}.pad.g{background:#1f9d62;color:#fff}.pad.sent{background:var(--line)}''')

# ── 폭탄 돌리기(여러 명): 폭탄은 한 폰에만 있어요. 들고 있는 사람이 다른 사람에게 넘기고, 언제 터질지는 아무도 몰라요. 터질 때 든 사람이 벌칙.
party("net-bomb.html", "폭탄 돌리기 (같이 하기)", "💣", 10, "net-bomb-v1",
      "방장이 시작하면 누군가의 폰에 폭탄이 생겨요. 폭탄을 든 사람은 얼른 다른 사람 이름을 눌러 넘기세요! 언제 터질지는 아무도 몰라요. 터질 때 들고 있는 사람이 벌칙이에요. (폭탄을 든 폰은 째깍 소리와 진동이 나요)",
      '<p class="center" id="st"></p><div class="big" id="bomb"></div><div class="choice" id="to"></div><div id="host" hidden style="display:grid;gap:8px"><div class="seg" id="lv" style="--n:3"></div><button class="btn" id="go" type="button">💣 폭탄 켜기</button></div>',
      r'''
const LV = { short: { min: 6, max: 14, label: "짧게", hint: "6~14초" }, normal: { min: 12, max: 26, label: "보통", hint: "12~26초" }, long: { min: 22, max: 45, label: "길게", hint: "22~45초" } };
const PEN = ["노래 한 소절 부르기", "성대모사 하나 하기", "10초 동안 웃지 않기", "옆 사람 칭찬 3가지", "애교 한 번 보여주기", "팔굽혀펴기 5번", "가장 부끄러운 비밀 하나", "다음 판 폭탄 먼저 잡기", "손뼉 치며 구구단 3단", "엉덩이로 이름 쓰기", "오늘의 큰절 올리기", "제일 좋아하는 음식 몸으로 설명하기"];
let tick = null, boomSeen = 0;
function initState() { return { ph: "idle", lv: "normal", holder: null, loser: null, pen: "", rno: 0, passes: 0 }; }
function onRoster() { if (P.ph === "run" && !ids().includes(P.holder)) P.holder = shuf(ids())[0]; }
function onAct(from, d) {
  if (d.t === "lv" && from === "host" && P.ph !== "run" && LV[d.v]) P.lv = d.v;
  else if (d.t === "go" && from === "host" && P.ph !== "run") { if (ids().length < 2) { alert("2명 이상 연결돼야 해요."); return; } const L = LV[P.lv]; P.ph = "run"; P.rno++; P.holder = shuf(ids())[0]; P.loser = null; P.passes = 0; const r = P.rno;
    setTimeout(() => { if (P.rno !== r || P.ph !== "run") return; P.ph = "boom"; P.loser = P.holder; P.pen = PEN[ri(0, PEN.length - 1)]; pushS(); }, Math.round((L.min + Math.random() * (L.max - L.min)) * 1000)); }
  else if (d.t === "pass" && P.ph === "run" && from === P.holder && d.to !== from && ids().includes(d.to)) { P.holder = d.to; P.passes++; }
  else return;
  pushS();
}
function onPriv() {}
function changed(was) {}
function beep(f, len) { try { const A = window.AudioContext || window.webkitAudioContext, c = beep.c || (beep.c = new A()), o = c.createOscillator(), g = c.createGain(); o.frequency.value = f; o.connect(g); g.connect(c.destination); g.gain.setValueAtTime(.15, c.currentTime); g.gain.exponentialRampToValueAtTime(.001, c.currentTime + len); o.start(); o.stop(c.currentTime + len); } catch (e) {} }
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  const mine = P.ph === "run" && P.holder === me;
  clearInterval(tick); tick = null; if (mine) { buzzV(80); tick = setInterval(() => beep(900, .05), 500); }
  if (P.ph === "boom" && boomSeen !== P.rno) { boomSeen = P.rno; buzzV(P.loser === me ? [600, 100, 600] : 200); beep(120, .6); }
  $("host").hidden = !isHost || P.ph === "run";
  $("lv").innerHTML = Object.entries(LV).map(([k, v]) => `<button type="button" data-v="${k}" class="${P.lv === k ? "on" : ""}">${v.label}<small>${v.hint}</small></button>`).join("");
  $("lv").querySelectorAll("[data-v]").forEach(b => b.onclick = () => act({ t: "lv", v: b.dataset.v }));
  $("go").textContent = P.rno ? "💣 한 판 더" : "💣 폭탄 켜기";
  $("st").textContent = P.ph === "idle" ? (isHost ? "시간을 고르고 폭탄을 켜요" : "방장이 폭탄을 켜기를 기다려요…") : P.ph === "run" ? (mine ? "💣 폭탄이 나한테 있어요! 얼른 넘겨요!" : `💣 ${pn(P.holder)}가 들고 있어요… (${P.passes}번 넘김)`) : `💥 펑! ${pn(P.loser)} 벌칙!`;
  $("bomb").innerHTML = P.ph === "run" ? (mine ? '<span class="shake">💣</span>' : "⏳") : P.ph === "boom" ? `💥<div class="note" style="font-size:1rem">벌칙: <b>${esc(P.pen)}</b></div>` : "💣";
  $("to").style.gridTemplateColumns = "repeat(2,1fr)";
  $("to").innerHTML = mine ? players.filter(p => p.id !== me).map(p => `<button type="button" data-to="${p.id}">➡️ ${esc(pn(p.id))}</button>`).join("") : "";
  $("to").querySelectorAll("[data-to]").forEach(b => b.onclick = () => act({ t: "pass", to: b.dataset.to }));
}
$("go").onclick = () => act({ t: "go" });
render();
''', '''.shake{display:inline-block;animation:sh .25s infinite}@keyframes sh{0%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}100%{transform:rotate(-8deg)}}''')

# ── 제비뽑기(여러 명): 연결된 사람 수만큼 카드, 당첨 수는 방장이 정해요. 각자 자기 폰에서 한 장씩 골라 뒤집으면 모두에게 공개.
party("net-lots.html", "제비뽑기 (같이 하기)", "🎟️", 50, "net-lots-v1",
      "연결된 사람 수만큼 제비(카드)가 생겨요. 당첨 수는 방장이 정해요. 각자 자기 폰에서 카드 한 장을 골라 뒤집으면 모두에게 공개돼요. 한 번 뒤집은 카드는 바꿀 수 없어요.",
      '<p class="center" id="st"></p><div id="host" hidden style="display:grid;gap:8px"><div class="step"><span>당첨 수</span><div><button type="button" id="wm" aria-label="줄이기">−</button><b id="wn">1</b><button type="button" id="wp" aria-label="늘리기">+</button></div></div><button class="btn" id="go" type="button">🎟️ 제비 만들기</button></div>'
      '<div class="grid8" id="cards" style="grid-template-columns:repeat(4,1fr)"></div><div id="sum"></div>',
      r'''
function initState() { return { ph: "set", win: 1, cards: [], who: {}, rno: 0 }; }
function onRoster() {}
function onAct(from, d) {
  if (d.t === "win" && from === "host" && P.ph !== "draw") P.win = Math.max(1, Math.min(Math.max(1, ids().length - 1), +d.v || 1));
  else if (d.t === "go" && from === "host") { const n = ids().length; if (n < 2) { alert("2명 이상 연결돼야 해요."); return; } const k = Math.min(P.win, n - 1); H.deck = shuf(Array.from({ length: n }, (_, i) => i < k ? 1 : 0)); P.cards = Array(n).fill(null); P.who = {}; P.ph = "draw"; P.rno++; P.k = k; }
  else if (d.t === "pick" && P.ph === "draw") { const i = +d.i; if (!(i >= 0 && i < P.cards.length) || P.cards[i] !== null || Object.values(P.who).includes(from)) return; P.who[i] = from; P.cards[i] = H.deck[i];
    if (P.cards.every(c => c !== null) || ids().every(id => Object.values(P.who).includes(id))) P.ph = "done"; }
  else return;
  pushS();
}
function onPriv() {}
function changed(was) {}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  const drew = Object.entries(P.who).find(([, id]) => id === me), canPick = P.ph === "draw" && !drew;
  $("host").hidden = !isHost || P.ph === "draw"; $("wn").textContent = P.win; $("go").textContent = P.rno ? "🎟️ 다시 만들기" : "🎟️ 제비 만들기";
  $("st").textContent = P.ph === "set" ? (isHost ? `참가자 ${ids().length}명 · 당첨 수를 정하고 제비를 만들어요` : "방장이 제비를 만들기를 기다려요…") : P.ph === "draw" ? (drew ? (P.cards[drew[0]] ? "🎉 당첨이에요!" : "😌 꽝이에요") + " · 다른 사람을 기다려요" : `카드 한 장을 골라요! (당첨 ${P.k}장)`) : "모두 뽑았어요!";
  $("cards").innerHTML = P.cards.map((c, i) => `<button type="button" data-i="${i}" style="aspect-ratio:3/4;font-size:1rem;border:1px solid var(--line);background:${c === null ? "var(--accent)" : c ? "color-mix(in srgb,var(--ok) 35%,var(--surface))" : "var(--soft)"}"${canPick && c === null ? "" : " disabled"}>${c === null ? "❓" : (c ? "🎉<br>당첨" : "꽝") + `<br><small>${esc(pn(P.who[i]))}</small>`}</button>`).join("");
  $("cards").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "pick", i: +b.dataset.i }));
  $("sum").innerHTML = P.ph === "done" ? `<p class="center">🎉 당첨: <b>${Object.entries(P.who).filter(([i]) => P.cards[i]).map(([, id]) => esc(pn(id))).join(", ") || "없음"}</b></p>` : "";
}
$("wm").onclick = () => act({ t: "win", v: P.win - 1 }); $("wp").onclick = () => act({ t: "win", v: P.win + 1 }); $("go").onclick = () => act({ t: "go" });
render();
''')
