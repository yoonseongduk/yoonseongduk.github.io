import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 페그 솔리테어 ----------
make(H+"peg-solitaire.html", "페그 솔리테어", "📍", 30, "pegsolitaire-best-v1",
 "구슬을 하나 눌러 고른 뒤, <b>바로 옆 구슬을 뛰어넘어</b> 빈 구멍에 내려놓으면 뛰어넘은 구슬이 사라져요. 가로·세로로만 움직일 수 있어요. 구슬을 <b>하나만 남기면</b> 성공! 남은 구슬이 적을수록 좋은 기록이에요.",
 r'''  <div class="stats"><div class="stat"><small>남은 구슬</small><b id="left">0</b></div><div class="stat"><small>움직인 횟수</small><b id="mv">0</b></div><div class="stat"><small>최고(적을수록)</small><b id="best">-</b></div></div>
  <div class="pg" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <div class="row"><button class="btn ghost" id="undo" type="button">↩ 한 수 물리기</button><button class="btn ghost" id="again" type="button">새로 하기</button></div>''',
 r'''const MAP = ["  ###  ", "  ###  ", "#######", "###.###", "#######", "  ###  ", "  ###  "];
let b = [], sel = null, hist = [], moves = 0, best = ld(KEY);
function newGame() { b = MAP.map(r => [...r].map(c => c === "#" ? 1 : c === "." ? 0 : -1)); sel = null; hist = []; moves = 0; $("res").hidden = true; render(); }
const count = () => b.flat().filter(v => v === 1).length;
function canMoves() { for (let r = 0; r < 7; r++) for (let c = 0; c < 7; c++) if (b[r][c] === 1) for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const y = r + 2 * dr, x = c + 2 * dc; if (y >= 0 && y < 7 && x >= 0 && x < 7 && b[y][x] === 0 && b[r + dr][c + dc] === 1) return true; } return false; }
function render() { $("grid").innerHTML = b.map((row, r) => row.map((v, c) => v < 0 ? `<i></i>` : `<button type="button" class="pp${v ? " peg" : ""}${sel && sel[0] === r && sel[1] === c ? " sel" : ""}" data-r="${r}" data-c="${c}" aria-label="${r + 1}행 ${c + 1}열 ${v ? "구슬" : "빈칸"}"></button>`).join("")).join(""); $("left").textContent = count(); $("mv").textContent = moves; $("best").textContent = best || "-"; }
function tap(r, c) {
  if (b[r][c] === 1) { sel = sel && sel[0] === r && sel[1] === c ? null : [r, c]; return render(); }
  if (!sel || b[r][c] !== 0) return; const [sr, sc] = sel, dr = r - sr, dc = c - sc;
  if (!((Math.abs(dr) === 2 && dc === 0) || (Math.abs(dc) === 2 && dr === 0)) || b[sr + dr / 2][sc + dc / 2] !== 1) return;
  hist.push(JSON.stringify(b)); b[sr][sc] = 0; b[sr + dr / 2][sc + dc / 2] = 0; b[r][c] = 1; sel = null; moves++; render();
  if (!canMoves()) { const n = count(), nb = !best || n < best; if (nb) { best = n; sv(KEY, best); } $("res").innerHTML = `<b>${n === 1 ? "🎉 완벽해요! 구슬 1개!" : "더 움직일 수 없어요"}</b><p class="muted">남은 구슬 ${n}개 · ${nb ? "신기록이에요!" : "최고 " + best + "개"}</p>`; $("res").hidden = false; render(); }
}
$("grid").addEventListener("click", e => { const t = e.target.closest("[data-r]"); if (t) tap(+t.dataset.r, +t.dataset.c); });
$("undo").onclick = () => { if (hist.length) { b = JSON.parse(hist.pop()); moves--; sel = null; $("res").hidden = true; render(); } }; $("again").onclick = newGame; newGame();''',
 css=".pg{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;max-width:360px;margin:0 auto;width:100%}.pg i{display:block}.pp{aspect-ratio:1;border-radius:50%;border:2px solid var(--line);background:color-mix(in srgb,var(--fg) 10%,var(--surface));padding:0;min-width:0}.pp.peg{background:radial-gradient(circle at 35% 30%,#ff9a7a,#d6453a 60%,#9c2a22);border-color:#9c2a22}.pp.sel{outline:4px solid var(--accent);outline-offset:1px}")

# ---------- 칼라하 ----------
make(H+"mancala.html", "칼라하 (콩 옮기기)", "🫘", 28, "mancala-best-v1",
 "내 구멍(아래쪽)을 눌러 <b>콩을 모두 꺼내</b> 시계 반대 방향으로 한 알씩 뿌려요. <b>마지막 콩이 내 창고(오른쪽)</b>에 들어가면 한 번 더! 마지막 콩이 <b>내 빈 구멍</b>에 떨어지면 맞은편 구멍의 콩을 모두 가져와요. 한쪽 구멍이 모두 비면 끝나고 창고가 더 큰 쪽이 이겨요.",
 r'''  <div class="stats"><div class="stat"><small>내 창고</small><b id="m">0</b></div><div class="stat"><small>차례</small><b id="t" style="font-size:1.1rem">나</b></div><div class="stat"><small>컴퓨터 창고</small><b id="c">0</b></div></div>
  <div class="man"><div class="store" id="st1">0</div><div class="pits"><div class="row6" id="top"></div><div class="row6" id="bot"></div></div><div class="store" id="st0">0</div></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''// 칸 번호: 0~5 내 구멍(왼→오), 6 내 창고, 7~12 컴퓨터 구멍(오→왼), 13 컴퓨터 창고
let p = [], turn = 0, over = false, busy = false, wins = ld(KEY) || 0, tempo = 1;
function newGame() { p = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]; turn = 0; over = false; busy = false; $("res").hidden = true; $("msg").textContent = "내 차례! 아래 구멍을 눌러요"; render(); }
function render() {
  $("bot").innerHTML = [0, 1, 2, 3, 4, 5].map(i => `<button type="button" class="pit" data-i="${i}" ${turn !== 0 || over || busy || !p[i] ? "disabled" : ""}>${p[i]}</button>`).join(""); $("top").innerHTML = [12, 11, 10, 9, 8, 7].map(i => `<div class="pit cp">${p[i]}</div>`).join("");
  $("st0").textContent = p[6]; $("st1").textContent = p[13]; $("m").textContent = p[6]; $("c").textContent = p[13]; $("t").textContent = over ? "-" : turn ? "컴퓨터" : "나";
}
function sow(i, who) {
  const mine = who === 0 ? [0, 5, 6] : [7, 12, 13], skip = who === 0 ? 13 : 6; let n = p[i], k = i; p[i] = 0; while (n > 0) { k = (k + 1) % 14; if (k === skip) continue; p[k]++; n--; }
  const store = who === 0 ? 6 : 13; let extra = k === store;
  if (!extra && p[k] === 1 && ((who === 0 && k <= 5) || (who === 1 && k >= 7 && k <= 12)) && p[12 - k]) { p[store] += p[12 - k] + 1; p[12 - k] = 0; p[k] = 0; }
  return extra;
}
function checkEnd() { const a = p.slice(0, 6).every(v => !v), b = p.slice(7, 13).every(v => !v); if (!a && !b) return false; for (let k = 0; k < 6; k++) { p[6] += p[k]; p[k] = 0; p[13] += p[k + 7]; p[k + 7] = 0; } over = true; const w = p[6] > p[13]; if (w) { wins++; sv(KEY, wins); } $("res").innerHTML = `<b>${p[6] === p[13] ? "비겼어요 🤝" : w ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"} (${p[6]} : ${p[13]})</b><p class="muted">누적 승리 ${wins}번</p>`; $("res").hidden = false; render(); return true; }
async function cpuTurn() {
  busy = true; while (!over && turn === 1) { await new Promise(r => setTimeout(r, 800 * tempo)); const ms = [7, 8, 9, 10, 11, 12].filter(i => p[i]); let best = -1, bi = ms[0];
    for (const i of ms) { const save = [...p]; const ex = sow(i, 1); const sc = p[13] - save[13] + (ex ? 3 : 0) + Math.random(); p = save; if (sc > best) { best = sc; bi = i; } }
    const ex = sow(bi, 1); if (checkEnd()) break; if (!ex) turn = 0; $("msg").textContent = ex ? "컴퓨터가 한 번 더!" : "내 차례!"; render(); } busy = false; render();
}
async function play(i) { if (turn !== 0 || over || busy || !p[i]) return; const ex = sow(i, 0); if (checkEnd()) return; if (!ex) { turn = 1; $("msg").textContent = "컴퓨터 차례..."; render(); cpuTurn(); } else { $("msg").textContent = "한 번 더!"; render(); } }
$("bot").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b) play(+b.dataset.i); });
$("again").onclick = newGame; newGame();''',
 css=".man{display:flex;gap:8px;align-items:stretch}.store{width:56px;border-radius:28px;border:2px solid var(--line);background:var(--surface);display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:1.6rem}.pits{flex:1;display:flex;flex-direction:column;gap:8px}.row6{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}.pit{aspect-ratio:1;border-radius:50%;border:2px solid var(--line);background:color-mix(in srgb,#a0713a 18%,var(--surface));font-family:var(--font-display);font-size:1.3rem;padding:0;min-width:0;display:flex;align-items:center;justify-content:center}button.pit:not(:disabled){border-color:var(--accent)}.pit.cp{opacity:.9}")

# ---------- 헥스 ----------
make(H+"hex-game.html", "헥스", "⬢", 205, "hex-best-v1",
 "육각형 판에서 번갈아 칸을 차지해요. <b>🔵 나는 왼쪽 변과 오른쪽 변</b>을, <b>🔴 컴퓨터는 위쪽 변과 아래쪽 변</b>을 끊기지 않는 길로 먼저 이으면 이겨요. 비기는 일은 없어요. 상대 길을 막으면서 내 길을 만들어 보세요!",
 r'''  <div class="seg" id="lv" style="--n:2"><button type="button" data-l="easy" class="on">쉬움<small>5×5</small></button><button type="button" data-l="hard">보통<small>7×7</small></button></div>
  <div class="stats"><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">🔵 나</b></div><div class="stat"><small>누적 승리</small><b id="wins">0</b></div><div class="stat"><small>놓은 돌</small><b id="cnt">0</b></div></div>
  <svg class="hx" id="svg"></svg>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''let N = 5, g = [], over = false, busy = false, wins = ld(KEY) || 0, tempo = 1;     // 0 비었음, 1 나(왼↔오른), 2 컴퓨터(위↔아래)
const NB = [[-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0]];
function newGame() { g = Array.from({ length: N }, () => Array(N).fill(0)); over = false; busy = false; $("res").hidden = true; render(); }
function dist(pl) {        // 0-1 BFS: pl가 이어야 하는 두 변 사이의 최소 빈칸 수
  const INF = 99, d = Array.from({ length: N }, () => Array(N).fill(INF)), q = []; const w = (r, c) => g[r][c] === pl ? 0 : g[r][c] === 0 ? 1 : INF;
  for (let i = 0; i < N; i++) { const [r, c] = pl === 1 ? [i, 0] : [0, i]; if (w(r, c) < INF) { d[r][c] = w(r, c); q.push([r, c]); } }
  q.sort((a, b) => d[a[0]][a[1]] - d[b[0]][b[1]]); while (q.length) { q.sort((a, b) => d[a[0]][a[1]] - d[b[0]][b[1]]); const [r, c] = q.shift(); for (const [dr, dc] of NB) { const y = r + dr, x = c + dc; if (y < 0 || y >= N || x < 0 || x >= N) continue; const ww = w(y, x); if (ww < INF && d[r][c] + ww < d[y][x]) { d[y][x] = d[r][c] + ww; q.push([y, x]); } } }
  let m = INF; for (let i = 0; i < N; i++) m = Math.min(m, pl === 1 ? d[i][N - 1] : d[N - 1][i]); return m;
}
const won = pl => dist(pl) === 0;
function render() {
  const S = 34, ox = 40, oy = 36; let h = "";
  const pos = (r, c) => [ox + c * S * 1.0 + r * S * .5, oy + r * S * .87];
  const hexp = (x, y, s) => Array.from({ length: 6 }, (_, k) => [x + s * Math.cos(Math.PI / 6 + k * Math.PI / 3), y + s * Math.sin(Math.PI / 6 + k * Math.PI / 3)].join(",")).join(" ");
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const [x, y] = pos(r, c); h += `<polygon class="hc c${g[r][c]}" data-r="${r}" data-c="${c}" points="${hexp(x, y, S * .56)}"/>`; }
  const W = ox * 2 + (N - 1) * S + (N - 1) * S * .5 + 10, Hh = oy * 2 + (N - 1) * S * .87; $("svg").setAttribute("viewBox", `0 0 ${W} ${Hh}`);
  const [tx0, ty0] = pos(0, 0), [tx1, ty1] = pos(0, N - 1), [bx0, by0] = pos(N - 1, 0), [bx1, by1] = pos(N - 1, N - 1), o = S * .62;
  const ln = (x1, y1, x2, y2, col) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${col}" stroke-width="9" stroke-linecap="round" opacity=".8"/>`;
  h = h + ln(tx0 - 24, ty0 - 4, bx0 - 24, by0 - 4, "#2f6fdf") + ln(tx1 + 24, ty1 + 4, bx1 + 24, by1 + 4, "#2f6fdf") + ln(tx0 - 8, ty0 - 24, tx1 + 8, ty1 - 24, "#e4572e") + ln(bx0 - 8, by0 + 24, bx1 + 8, by1 + 24, "#e4572e");
  $("svg").innerHTML = h; $("wins").textContent = wins; $("cnt").textContent = g.flat().filter(Boolean).length; $("turn").textContent = over ? "-" : busy ? "🔴 컴퓨터" : "🔵 나";
}
async function play(r, c) {
  if (over || busy || g[r][c]) return; g[r][c] = 1; render(); if (won(1)) { over = true; wins++; sv(KEY, wins); $("res").innerHTML = `<b>🎉 내가 이겼어요!</b>`; $("res").hidden = false; return render(); }
  busy = true; render(); await new Promise(x => setTimeout(x, 450 * tempo));
  let best = null, bs = 1e9; for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (!g[y][x]) { g[y][x] = 2; const s = dist(2) * 3 - dist(1) + Math.random() * (N === 5 ? 1.4 : .5); g[y][x] = 0; if (s < bs) { bs = s; best = [y, x]; } }
  g[best[0]][best[1]] = 2; if (won(2)) { over = true; $("res").innerHTML = `<b>😢 컴퓨터가 이겼어요</b>`; $("res").hidden = false; } busy = false; render();
}
$("svg").addEventListener("click", e => { const h = e.target.closest("[data-r]"); if (h) play(+h.dataset.r, +h.dataset.c); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); N = b.dataset.l === "easy" ? 5 : 7; newGame(); });
$("again").onclick = newGame; newGame();''',
 css=".hx{width:100%;max-width:400px;margin:0 auto;display:block;touch-action:manipulation}.hc{stroke:var(--fg);stroke-width:1.5;cursor:pointer}.hc.c0{fill:var(--surface)}.hc.c1{fill:#2f6fdf}.hc.c2{fill:#e4572e}.hc.c0:hover{fill:var(--soft)}")

# ---------- 포커 드로우 ----------
make(H+"poker-draw.html", "5장 포커", "🎴", 345, "pokerdraw-best-v1",
 "카드 5장을 받아요. <b>남기고 싶은 카드를 눌러 '고정'</b>하고 나머지를 <b>교체</b>한 뒤, 컴퓨터와 <b>족보</b>를 겨뤄요! 높은 족보가 이겨요. (원 페어 < 투 페어 < 트리플 < 스트레이트 < 플러시 < 풀하우스 < 포카드 < 스트레이트 플러시) 5판 중 많이 이기면 승리!",
 r'''  <div class="stats"><div class="stat"><small>나</small><b id="s1">0</b></div><div class="stat"><small>판</small><b id="rd">1/5</b></div><div class="stat"><small>컴퓨터</small><b id="s2">0</b></div></div>
  <p class="muted center">컴퓨터의 카드</p><div class="hand" id="ch"></div><p class="center" id="cn" style="min-height:1.4em"></p>
  <p class="muted center">내 카드 — 남길 카드를 눌러 고정하세요</p><div class="hand" id="mh"></div><p class="center" id="mn" style="min-height:1.4em;font-weight:700"></p>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="act" type="button">카드 교체하기</button>''',
 r'''const SU = ["♠", "♥", "♦", "♣"], RK = "23456789TJQKA";
let deck, mine, cpu, hold, phase, rd, s1, s2, wins = ld(KEY) || 0, tempo = 1;
const mkDeck = () => shuf(Array.from({ length: 52 }, (_, k) => ({ r: k % 13, s: Math.floor(k / 13) })));
const cardName = c => (c.r === 8 ? "10" : RK[c.r]) + SU[c.s];
function evalHand(h) {
  const r = h.map(c => c.r).sort((a, b) => b - a), cnt = {}; r.forEach(x => { cnt[x] = (cnt[x] || 0) + 1; }); const groups = Object.entries(cnt).map(([v, n]) => [n, +v]).sort((a, b) => b[0] - a[0] || b[1] - a[1]), flush = h.every(c => c.s === h[0].s);
  let straight = new Set(r).size === 5 && r[0] - r[4] === 4, hi = r[0]; if (!straight && JSON.stringify(r) === JSON.stringify([12, 3, 2, 1, 0])) { straight = true; hi = 3; }
  const g0 = groups[0][0], g1 = groups[1] ? groups[1][0] : 0; let cat, nm;
  if (straight && flush) { cat = 8; nm = "스트레이트 플러시"; } else if (g0 === 4) { cat = 7; nm = "포카드"; } else if (g0 === 3 && g1 === 2) { cat = 6; nm = "풀하우스"; } else if (flush) { cat = 5; nm = "플러시"; } else if (straight) { cat = 4; nm = "스트레이트"; } else if (g0 === 3) { cat = 3; nm = "트리플"; } else if (g0 === 2 && g1 === 2) { cat = 2; nm = "투 페어"; } else if (g0 === 2) { cat = 1; nm = "원 페어"; } else { cat = 0; nm = "하이 카드"; }
  return { v: [cat, ...(straight ? [hi] : groups.map(g => g[1]))], nm };
}
const cmp = (a, b) => { for (let k = 0; k < Math.max(a.length, b.length); k++) { if ((a[k] || 0) !== (b[k] || 0)) return (a[k] || 0) - (b[k] || 0); } return 0; };
function cardHtml(c, back, k, held) { return `<button type="button" class="cd${back ? " back" : ""}${c && c.s % 3 === 1 || c && c.s === 2 ? " red" : ""}${held ? " hold" : ""}" data-k="${k}" ${phase !== "pick" || back ? "disabled" : ""}>${back ? "" : `<b>${cardName(c)}</b>`}${held ? "<small>고정</small>" : ""}</button>`; }
function render(showCpu) { $("mh").innerHTML = mine.map((c, k) => cardHtml(c, false, k, hold[k])).join(""); $("ch").innerHTML = cpu.map((c, k) => cardHtml(c, !showCpu, k, false)).join(""); $("s1").textContent = s1; $("s2").textContent = s2; $("rd").textContent = Math.min(rd + 1, 5) + "/5"; }
function deal() { deck = mkDeck(); mine = deck.splice(0, 5).sort((a, b) => a.r - b.r); cpu = deck.splice(0, 5); hold = Array(5).fill(false); phase = "pick"; $("cn").textContent = ""; $("mn").textContent = evalHand(mine).nm; $("res").hidden = true; $("act").textContent = "카드 교체하기"; $("act").disabled = false; render(false); }
function newGame() { rd = 0; s1 = s2 = 0; deal(); }
function cpuDraw() { const e = evalHand(cpu), r = cpu.map(c => c.r), keep = cpu.map(() => false), cnt = {}; r.forEach(x => { cnt[x] = (cnt[x] || 0) + 1; }); if (e.v[0] >= 4) keep.fill(true); else cpu.forEach((c, k) => { if (cnt[c.r] >= 2) keep[k] = true; }); if (!keep.some(Boolean)) { const mx = Math.max(...r); cpu.forEach((c, k) => { if (c.r === mx) keep[k] = true; }); } cpu = cpu.map((c, k) => keep[k] ? c : deck.shift()); }
$("act").onclick = async () => {
  if (phase === "pick") { phase = "show"; mine = mine.map((c, k) => hold[k] ? c : deck.shift()); cpuDraw(); render(true); const a = evalHand(mine), b = evalHand(cpu), d = cmp(a.v, b.v); $("mn").textContent = a.nm; $("cn").textContent = b.nm; if (d > 0) s1++; else if (d < 0) s2++; rd++; render(true);
    $("res").innerHTML = `<b>${d > 0 ? "🎉 내가 이겼어요!" : d < 0 ? "😢 컴퓨터가 이겼어요" : "🤝 비겼어요"}</b><p class="muted">${a.nm} vs ${b.nm}</p>`; $("res").hidden = false;
    if (rd >= 5) { const w = s1 > s2; if (w) { wins++; sv(KEY, wins); } $("res").innerHTML += `<p><b>${s1 === s2 ? "최종 무승부" : w ? "🏆 최종 승리!" : "최종 패배"} (${s1} : ${s2})</b> · 누적 승리 ${wins}번</p>`; $("act").textContent = "새 게임"; phase = "end"; } else { $("act").textContent = "다음 판"; phase = "next"; } }
  else if (phase === "next") deal(); else if (phase === "end") newGame();
};
document.addEventListener("click", e => { const c = e.target.closest("#mh [data-k]"); if (c && phase === "pick") { hold[+c.dataset.k] = !hold[+c.dataset.k]; render(false); } });
newGame();''',
 css=".hand{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.cd{aspect-ratio:3/4.2;border-radius:10px;border:2px solid var(--line);background:#fff;color:#111;font-size:1.1rem;padding:0;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative}.cd.red{color:#d6453a}.cd.back{background:repeating-linear-gradient(45deg,#2f6fdf,#2f6fdf 6px,#1f4fa0 6px,#1f4fa0 12px);border-color:#1f4fa0}.cd.hold{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 35%,transparent);transform:translateY(-6px)}.cd small{position:absolute;bottom:3px;font-size:.62rem;color:var(--accent)}.cd:disabled{opacity:1;cursor:default}")
