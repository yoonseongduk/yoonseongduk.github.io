import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 로봇 길 안내 ----------
make(H+"robot-path.html", "로봇 길 안내", "🤖", 175, "robotpath-v1",
 "로봇이 ⭐까지 가도록 <b>명령(⬆️⬇️⬅️➡️)을 차례로 눌러</b> 순서를 만든 뒤 ▶ 실행을 누르세요. 벽(⬛)에 부딪히면 제자리에 멈춰요. 명령은 적을수록 별을 많이 받아요!",
 r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lv">1/8</b></div><div class="stat"><small>명령 수</small><b id="cnt">0</b></div><div class="stat"><small>별</small><b id="stars">0</b></div></div>
  <div class="rgrid" id="grid"></div>
  <div class="prog" id="prog"></div>
  <div class="cmds"><button type="button" data-c="U">⬆️</button><button type="button" data-c="D">⬇️</button><button type="button" data-c="L">⬅️</button><button type="button" data-c="R">➡️</button></div>
  <div class="row"><button class="btn ghost" id="undo" type="button">⌫ 한 칸 지우기</button><button class="btn" id="run" type="button">▶ 실행</button></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <button class="btn" id="next" type="button" hidden>다음 단계</button>''',
 r'''// 맵: S 시작, G 별, # 벽, . 길. 최소 명령 수는 계산해서 별 개수를 정한다
const MAPS = [
 ["S..", "...", "..G"], ["S.#.", "..#.", "...G"], ["S...", ".##.", "...G"], ["S.#..", "..#.#", "....G"],
 ["S.#...", "..#.#.", "....#G", "###..."], ["S....", "####.", "....G"], ["S#...", ".#.#.", ".#.#.", "...#G"], ["S.....", ".####.", ".#..#.", ".#G##.", "......"]];
let lv = 0, prog = [], pos = [0, 0], grid = [], running = false, stars = ld(KEY) || 0, tempo = 1, best = 0, token = 0;
const DIR = { U: [-1, 0], D: [1, 0], L: [0, -1], R: [0, 1] }, ARROW = { U: "⬆️", D: "⬇️", L: "⬅️", R: "➡️" };
function bfs(m) { let s, g; m.forEach((row, r) => [...row].forEach((c, k) => { if (c === "S") s = [r, k]; if (c === "G") g = [r, k]; })); const q = [[s, 0]], seen = new Set([s + ""]); while (q.length) { const [[r, c], d] = q.shift(); if (r === g[0] && c === g[1]) return d; for (const [dr, dc] of Object.values(DIR)) { let nr = r, nc = c; while (nr + dr >= 0 && nr + dr < m.length && nc + dc >= 0 && nc + dc < m[0].length && m[nr + dr][nc + dc] !== "#") { nr += dr; nc += dc; break; } if (!seen.has([nr, nc] + "")) { seen.add([nr, nc] + ""); q.push([[nr, nc], d + 1]); } } } return 99; }
function load(l) { lv = l; grid = MAPS[l].map(r => [...r]); grid.forEach((row, r) => row.forEach((c, k) => { if (c === "S") pos = [r, k]; })); prog = []; running = false; token++; $("msg").textContent = ""; $("next").hidden = true; $("run").disabled = false; best = bfs(MAPS[l]); render(); }
function render(hl = -1) {
  $("grid").style.gridTemplateColumns = `repeat(${grid[0].length}, 1fr)`;
  $("grid").innerHTML = grid.map((row, r) => row.map((c, k) => `<div class="rc${c === "#" ? " w" : ""}">${r === pos[0] && k === pos[1] ? "🤖" : c === "G" ? "⭐" : ""}</div>`).join("")).join("");
  $("prog").innerHTML = prog.length ? prog.map((c, k) => `<span class="${k === hl ? "hl" : ""}">${ARROW[c]}</span>`).join("") : '<span class="muted">명령을 눌러 순서를 만들어 보세요</span>';
  $("lv").textContent = (lv + 1) + "/" + MAPS.length; $("cnt").textContent = prog.length; $("stars").textContent = stars;
}
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
async function run() {
  if (running || !prog.length) return; running = true; const my = ++token; $("run").disabled = true; let reset = MAPS[lv].map(r => [...r]); grid.forEach((row, r) => row.forEach((c, k) => { if (c === "S") pos = [r, k]; }));
  for (let k = 0; k < prog.length; k++) { if (my !== token) return; const [dr, dc] = DIR[prog[k]], nr = pos[0] + dr, nc = pos[1] + dc; if (nr >= 0 && nr < grid.length && nc >= 0 && nc < grid[0].length && grid[nr][nc] !== "#") pos = [nr, nc]; render(k); await sleep(350); if (grid[pos[0]][pos[1]] === "G") break; }
  running = false; $("run").disabled = false; render();
  if (grid[pos[0]][pos[1]] === "G") { const n = prog.length, got = n <= best ? 3 : n <= best + 2 ? 2 : 1; stars += got; sv(KEY, stars); $("msg").textContent = `🎉 도착! ${"⭐".repeat(got)} (최소 ${best}개)`; $("stars").textContent = stars; if (lv < MAPS.length - 1) $("next").hidden = false; else $("msg").textContent += " 모든 단계를 끝냈어요!"; }
  else { $("msg").textContent = "아직 도착하지 못했어요. 명령을 고쳐 다시 해 보세요."; grid.forEach((row, r) => row.forEach((c, k) => { if (c === "S") pos = [r, k]; })); render(); }
}
document.querySelector(".cmds").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b && !running && prog.length < 30) { prog.push(b.dataset.c); render(); } });
$("undo").onclick = () => { if (!running) { prog.pop(); render(); } }; $("run").onclick = run; $("next").onclick = () => load(lv + 1); load(0);''',
 css=".rgrid{display:grid;gap:4px;background:var(--line);padding:4px;border-radius:12px;max-width:380px;margin:0 auto;width:100%}.rc{aspect-ratio:1;background:var(--surface);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:clamp(1.3rem,8vw,2rem)}.rc.w{background:var(--fg)}.prog{min-height:48px;display:flex;flex-wrap:wrap;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px}.prog span{font-size:1.3rem;padding:0 2px;border-radius:6px}.prog span.hl{background:var(--soft);outline:2px solid var(--accent)}.cmds{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.cmds button{padding:12px 0;border-radius:12px;border:1px solid var(--line);background:var(--surface);font-size:1.5rem}.rgrid + .prog{}")

# ---------- 파이프 연결 ----------
make(H+"pipe-connect.html", "파이프 연결", "🔧", 190, "pipeconnect-best-v1",
 "파이프 조각을 <b>눌러서 돌려</b> 왼쪽 위 💧 물 나오는 곳에서 모든 파이프가 이어지도록 만드세요. 물이 닿은 파이프는 파랗게 변해요. 모든 파이프가 파랗게 되면 성공!",
 r'''  <div class="seg" id="lv" style="--n:3"><button type="button" data-n="4" class="on">4×4<small>쉬움</small></button><button type="button" data-n="5">5×5<small>보통</small></button><button type="button" data-n="6">6×6<small>어려움</small></button></div>
  <div class="stats"><div class="stat"><small>돌린 횟수</small><b id="moves">0</b></div><div class="stat"><small>연결</small><b id="conn">0</b></div><div class="stat"><small>최소 기록</small><b id="best">-</b></div></div>
  <div class="pgrid" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 판</button>''',
 r'''// 조각의 연결 방향을 비트로: 1 위, 2 오른쪽, 4 아래, 8 왼쪽
let N = 4, mask = [], SOL = [], moves = 0, done = false, best = ld(KEY) || {};
const rot = m => ((m << 1) | (m >> 3)) & 15;
function gen() {
  const adj = Array(N * N).fill(0), seen = new Set([0]), st = [0];                       // 무작위 신장 트리로 파이프 길을 만든다
  while (seen.size < N * N) { const a = [...seen][ri(0, seen.size - 1)], r = Math.floor(a / N), c = a % N, nb = [[r - 1, c, 1, 4], [r, c + 1, 2, 8], [r + 1, c, 4, 1], [r, c - 1, 8, 2]].filter(([y, x]) => y >= 0 && y < N && x >= 0 && x < N && !seen.has(y * N + x)); if (!nb.length) continue; const [y, x, d1, d2] = nb[ri(0, nb.length - 1)]; adj[a] |= d1; adj[y * N + x] |= d2; seen.add(y * N + x); }
  return adj;
}
function newGame() { const sol = gen(); SOL = sol; mask = sol.map(m => { let t = m; for (let k = ri(0, 3); k > 0; k--) t = rot(t); return t; }); if (wet().size === N * N) return newGame(); moves = 0; done = false; $("res").hidden = true; $("grid").style.gridTemplateColumns = `repeat(${N}, 1fr)`; render(); }
function wet() { const w = new Set([0]), st = [0]; while (st.length) { const a = st.pop(), r = Math.floor(a / N), c = a % N; for (const [y, x, d1, d2] of [[r - 1, c, 1, 4], [r, c + 1, 2, 8], [r + 1, c, 4, 1], [r, c - 1, 8, 2]]) { if (y < 0 || y >= N || x < 0 || x >= N) continue; const b = y * N + x; if ((mask[a] & d1) && (mask[b] & d2) && !w.has(b)) { w.add(b); st.push(b); } } } return w; }
function render() {
  const w = wet(); $("grid").innerHTML = mask.map((m, k) => `<button type="button" class="pp${w.has(k) ? " wet" : ""}" data-k="${k}" aria-label="파이프 ${k + 1}">${k === 0 ? '<b class="src">💧</b>' : ""}<i class="${m & 1 ? "u" : ""}"></i><i class="${m & 2 ? "r" : ""}"></i><i class="${m & 4 ? "d" : ""}"></i><i class="${m & 8 ? "l" : ""}"></i><s></s></button>`).join("");
  $("moves").textContent = moves; $("conn").textContent = w.size + "/" + N * N; $("best").textContent = best[N] || "-";
}
function turn(k) {
  if (done) return; mask[k] = rot(mask[k]); moves++; render();
  if (wet().size === N * N) { done = true; const nb = !best[N] || moves < best[N]; if (nb) { best[N] = moves; sv(KEY, best); } $("res").innerHTML = `<b>🎉 모두 연결! ${moves}번</b><p class="muted">${nb ? "신기록이에요!" : "최소 기록 " + best[N] + "번"}</p>`; $("res").hidden = false; render(); }
}
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) turn(+b.dataset.k); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); N = +b.dataset.n; newGame(); });
$("again").onclick = newGame; newGame();''',
 css=".pgrid{display:grid;gap:3px;background:var(--line);padding:3px;border-radius:12px;max-width:380px;margin:0 auto;width:100%}.pp{position:relative;aspect-ratio:1;background:var(--surface);border:0;border-radius:6px;padding:0;min-width:0}.pp i{position:absolute;background:var(--muted);display:none}.pp i.u,.pp i.r,.pp i.d,.pp i.l{display:block}.pp i.u{left:42%;width:16%;top:0;height:50%}.pp i.d{left:42%;width:16%;bottom:0;height:50%}.pp i.l{top:42%;height:16%;left:0;width:50%}.pp i.r{top:42%;height:16%;right:0;width:50%}.pp s{position:absolute;left:38%;top:38%;width:24%;height:24%;border-radius:50%;background:var(--muted)}.pp.wet i,.pp.wet s{background:#2f8fe0}.pp.wet{background:color-mix(in srgb,#2f8fe0 12%,var(--surface))}.src{position:absolute;z-index:2;left:2px;top:0;font-size:.9rem}")

# ---------- 대칭 맞추기 ----------
make(H+"mirror-pattern.html", "대칭 맞추기", "🪞", 300, "mirror-best-v1",
 "가운데 선을 거울이라고 생각하고, <b>왼쪽 무늬와 똑같이 오른쪽을 칠해</b> 보세요. 오른쪽 칸을 눌러 색을 켜고 끌 수 있어요. 모두 맞으면 다음 문제로 넘어가요!",
 r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lv">1</b></div><div class="stat"><small>남은 시간</small><b id="time">-</b></div><div class="stat"><small>최고 단계</small><b id="best">0</b></div></div>
  <div class="mirror" id="board"></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="row"><button class="btn ghost" id="clear" type="button">모두 지우기</button><button class="btn" id="check" type="button">확인</button></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="again" type="button" hidden>다시 하기</button>''',
 r'''let lv = 1, W = 3, Hh = 4, left = [], mine = [], timer = 0, sec = 0, best = ld(KEY) || 0, over = false, tempo = 1;
function newPuzzle() {
  W = lv < 4 ? 3 : lv < 8 ? 4 : 5; Hh = lv < 3 ? 4 : lv < 7 ? 5 : 6; const n = W * Hh, fill = Math.max(3, Math.round(n * 0.45));
  left = Array(n).fill(false); shuf([...Array(n).keys()]).slice(0, fill).forEach(k => { left[k] = true; }); mine = Array(n).fill(false);
  sec = Math.max(12, 30 - lv * 2); clearInterval(timer); timer = setInterval(() => { sec--; $("time").textContent = sec + "초"; if (sec <= 0) lose("시간이 다 됐어요 ⏰"); }, 1000 * tempo); $("msg").textContent = ""; render();
}
function render() {
  let h = ""; for (let r = 0; r < Hh; r++) { for (let c = 0; c < W; c++) h += `<div class="mc${left[r * W + c] ? " on" : ""}"></div>`; h += `<div class="axis"></div>`; for (let c = 0; c < W; c++) { const k = r * W + c; h += `<button type="button" class="mc m${mine[k] ? " on" : ""}" data-k="${k}" aria-label="${r + 1}행 ${c + 1}열"></button>`; } }
  $("board").style.gridTemplateColumns = `repeat(${W}, 1fr) 6px repeat(${W}, 1fr)`; $("board").innerHTML = h; $("lv").textContent = lv; $("best").textContent = best; $("time").textContent = sec + "초";
}
// 오른쪽은 왼쪽의 거울 모습: 왼쪽 맨 오른쪽 칸 ↔ 오른쪽 맨 왼쪽 칸
const mirror = k => { const r = Math.floor(k / W), c = k % W; return r * W + (W - 1 - c); };
function check() { if (over) return; const ok = left.every((v, k) => v === mine[mirror(k)]); if (ok) { lv++; if (lv - 1 > best) { best = lv - 1; sv(KEY, best); } $("msg").textContent = "⭕ 정답! 다음 문제"; $("msg").style.color = "var(--ok)"; newPuzzle(); } else { $("msg").textContent = "❌ 아직 달라요. 다시 살펴봐요"; $("msg").style.color = "var(--bad)"; } }
function lose(t) { over = true; clearInterval(timer); if (lv - 1 > best) { best = lv - 1; sv(KEY, best); } $("res").innerHTML = `<b>${t}</b><p class="muted">${lv - 1}단계까지 성공했어요 · 최고 ${best}단계</p>`; $("res").hidden = false; $("again").hidden = false; render(); }
$("board").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && !over) { mine[+b.dataset.k] = !mine[+b.dataset.k]; render(); } });
$("clear").onclick = () => { mine = mine.map(() => false); render(); }; $("check").onclick = check; $("again").onclick = () => { lv = 1; over = false; $("res").hidden = true; $("again").hidden = true; newPuzzle(); }; newPuzzle();''',
 css=".mirror{display:grid;gap:4px;max-width:380px;margin:0 auto;width:100%}.mc{aspect-ratio:1;border-radius:8px;background:var(--surface);border:2px solid var(--line);padding:0;min-width:0}.mc.on{background:var(--accent);border-color:var(--accent)}.mc.m{border-style:dashed}.axis{background:var(--fg);border-radius:3px}")
