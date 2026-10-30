import sys
sys.path.insert(0, ".")
from mkpage import make

DUELCSS = """.duel{display:flex;flex-direction:column;gap:8px;height:min(72vh,560px);min-height:360px}
.half{flex:1;border-radius:18px;border:2px solid var(--line);background:var(--surface);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;position:relative;overflow:hidden;touch-action:manipulation;font-family:var(--font-display);padding:8px}
.half.top{transform:rotate(180deg)}
.half>*{position:relative;z-index:1}
.half .fill{position:absolute;left:0;right:0;bottom:0;height:0;z-index:0;opacity:.28;background:var(--ok)}
.half.top .fill{background:var(--bad)}
.half .num{font-size:clamp(3rem,18vw,5rem);line-height:1;font-weight:400;font-variant-numeric:tabular-nums}
.half small{font-family:var(--font-body);color:var(--muted);font-size:.9rem}
.mid{min-height:48px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:var(--font-display);font-size:1.5rem;line-height:1.25}
"""

# ---------------- 탭 대결 ----------------
make("out/tap-duel.html", "탭 대결", "👆", 15, "tapduel-wins-v1",
     "둘이서 한 화면을 나눠 써요. <b>카운트다운이 끝나면</b> 자기 쪽 칸을 최대한 빨리 연타! 먼저 <b>40번</b> 누르는 사람이 이겨요.",
     r'''  <div class="duel">
    <button class="half top" id="h1" type="button" aria-label="위쪽 플레이어"><div class="fill" id="f1"></div><b class="num" id="n1">0</b><small>위 플레이어 · 40번이 목표</small></button>
    <div class="mid" id="msg">시작을 누르세요</div>
    <button class="half" id="h0" type="button" aria-label="아래쪽 플레이어"><div class="fill" id="f0"></div><b class="num" id="n0">0</b><small>아래 플레이어 · 40번이 목표</small></button>
  </div>
  <p class="center muted" id="score"></p>
  <button class="btn" id="start" type="button">시작</button>''',
     r'''const GOAL = 40;
let cnt = [0, 0], st = "idle", tempo = 1, gen = 0, wins = ld(KEY) || [0, 0];
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
const nm = p => (p ? "위" : "아래");
function render() {
  for (const p of [0, 1]) { $("n" + p).textContent = cnt[p]; $("f" + p).style.height = (cnt[p] / GOAL * 100) + "%"; }
  $("score").textContent = `누적 승리 · 아래 ${wins[0]} : ${wins[1]} 위`;
}
async function start() {
  const my = ++gen; cnt = [0, 0]; render(); $("start").hidden = true; st = "count";
  for (const t of ["3", "2", "1"]) { $("msg").textContent = t; await sleep(700); if (my !== gen) return; }
  $("msg").textContent = "탭! 탭! 탭!"; st = "play";
}
function finish(p) {
  st = "over"; wins[p]++; sv(KEY, wins); render();
  $("msg").textContent = `🎉 ${nm(p)} 플레이어 승리!`; $("start").hidden = false; $("start").textContent = "다시 하기";
}
function tap(p) { if (st !== "play") return; cnt[p]++; render(); if (cnt[p] >= GOAL) finish(p); }
for (const p of [0, 1]) $("h" + p).addEventListener("pointerdown", e => { e.preventDefault(); tap(p); });
$("start").onclick = start; render();''', css=DUELCSS)

# ---------------- 반응 대결 ----------------
make("out/reaction-duel.html", "반응 대결", "⚡", 130, "reactionduel-wins-v1",
     "둘이서 한 화면을 나눠 써요. 화면이 <b>초록색 '지금!'</b>으로 바뀌는 순간 자기 쪽을 먼저 누르면 1점! 너무 일찍 누르면 상대가 1점을 가져가요. 먼저 <b>3점</b>을 얻으면 승리!",
     r'''  <div class="duel">
    <button class="half top" id="h1" type="button" aria-label="위쪽 플레이어"><b class="num" id="t1" style="font-size:clamp(2rem,12vw,3.4rem)">준비</b><small id="p1"></small></button>
    <div class="mid" id="msg">시작을 누르세요</div>
    <button class="half" id="h0" type="button" aria-label="아래쪽 플레이어"><b class="num" id="t0" style="font-size:clamp(2rem,12vw,3.4rem)">준비</b><small id="p0"></small></button>
  </div>
  <p class="center muted" id="score"></p>
  <button class="btn" id="start" type="button">시작</button>''',
     r'''const NEED = 3;
let pts = [0, 0], st = "idle", tempo = 1, gen = 0, goAt = 0, wins = ld(KEY) || [0, 0];
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
const nm = p => (p ? "위" : "아래");
function setHalf(cls, txt) { for (const p of [0, 1]) { $("h" + p).className = "half " + (p ? "top " : "") + cls; $("t" + p).textContent = txt; } }
function render() {
  for (const p of [0, 1]) $("p" + p).textContent = "●".repeat(pts[p]) + "○".repeat(NEED - pts[p]);
  $("score").textContent = `누적 승리 · 아래 ${wins[0]} : ${wins[1]} 위`;
}
async function start() { pts = [0, 0]; render(); $("start").hidden = true; round(); }
async function round() {
  const my = ++gen; st = "wait"; setHalf("wait", "기다려…"); $("msg").textContent = "초록색이 되면 누르세요!";
  await sleep(ri(1500, 4000)); if (my !== gen) return;
  st = "go"; goAt = performance.now(); setHalf("go", "지금!"); $("msg").textContent = "⚡ 지금!";
}
async function award(w, text) {
  gen++; const my = gen; st = "between"; pts[w]++; render();
  for (const p of [0, 1]) { $("h" + p).className = "half " + (p ? "top " : "") + (p === w ? "win" : "lose"); $("t" + p).textContent = p === w ? "+1" : ""; }
  $("msg").textContent = text;
  if (pts[w] >= NEED) { st = "over"; wins[w]++; sv(KEY, wins); render(); $("msg").textContent = `🎉 ${nm(w)} 플레이어 승리! (${pts[0]} : ${pts[1]})`; $("start").hidden = false; $("start").textContent = "다시 하기"; return; }
  await sleep(1700); if (my !== gen) return; round();
}
function tap(p) {
  if (st === "wait") award(1 - p, `${nm(p)} 플레이어가 너무 일찍 눌렀어요! 상대 1점`);
  else if (st === "go") award(p, `${nm(p)} 플레이어 1점! (${((performance.now() - goAt) / 1000).toFixed(3)}초)`);
}
for (const p of [0, 1]) $("h" + p).addEventListener("pointerdown", e => { e.preventDefault(); tap(p); });
$("start").onclick = start; render(); setHalf("", "준비");''',
     css=DUELCSS + ".half.wait{background:color-mix(in srgb,var(--bad) 22%,var(--surface))}.half.go{background:color-mix(in srgb,var(--ok) 45%,var(--surface));border-color:var(--ok)}.half.win{background:color-mix(in srgb,var(--ok) 25%,var(--surface))}.half.lose{opacity:.7}.half small{letter-spacing:.2em;font-size:1.1rem}")

# ---------------- 요트 다이스 ----------------
make("out/yacht.html", "요트 다이스", "🎲", 38, "yacht-best-v1",
     "주사위 5개를 <b>한 턴에 최대 3번</b> 굴릴 수 있어요. 마음에 드는 주사위는 눌러서 <b>고정</b>하고 나머지만 다시 굴려요. 12개 족보를 한 번씩 채우면 끝! 1~6의 눈 합계가 63점 이상이면 <b>보너스 35점</b>. 스트레이트는 연속된 눈이 4개면 스몰(15점), 5개면 라지(30점), 같은 눈 5개는 요트(50점)예요.",
     r'''  <div class="stats"><div class="stat"><small>턴</small><b id="turn">1/12</b></div><div class="stat"><small>눈 합계</small><b id="upper">0/63</b></div><div class="stat"><small>총점</small><b id="total">0</b></div></div>
  <div class="dice" id="dice"></div>
  <button class="btn" id="roll" type="button">굴리기</button>
  <div class="cats" id="cats"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button" hidden>다시 하기</button>''',
     r'''const NAMES = ["1의 눈", "2의 눈", "3의 눈", "4의 눈", "5의 눈", "6의 눈", "초이스(합계)", "포카드", "풀하우스", "스몰 스트레이트", "라지 스트레이트", "요트"];
const HINT = ["1의 합", "2의 합", "3의 합", "4의 합", "5의 합", "6의 합", "다 더하기", "같은 눈 4개↑", "3개 + 2개", "연속 4개 15점", "연속 5개 30점", "5개 같음 50점"];
let dice = [0, 0, 0, 0, 0], held = [false, false, false, false, false], left = 3, used = Array(12).fill(null), turn = 0, over = false, best = ld(KEY) || 0;
function scoreOf(c, d) {
  const cn = [0, 0, 0, 0, 0, 0, 0]; d.forEach(v => cn[v]++); const sum = d.reduce((a, b) => a + b, 0);
  const has = a => a.every(v => cn[v] > 0);
  if (c < 6) return cn[c + 1] * (c + 1);
  if (c === 6) return sum;
  if (c === 7) return cn.some(x => x >= 4) ? sum : 0;
  if (c === 8) return cn.includes(3) && cn.includes(2) ? sum : 0;
  if (c === 9) return has([1, 2, 3, 4]) || has([2, 3, 4, 5]) || has([3, 4, 5, 6]) ? 15 : 0;
  if (c === 10) return has([1, 2, 3, 4, 5]) || has([2, 3, 4, 5, 6]) ? 30 : 0;
  return cn.some(x => x === 5) ? 50 : 0;
}
function upperSum() { return used.slice(0, 6).reduce((a, b) => a + (b || 0), 0); }
function totalSum() { return used.reduce((a, b) => a + (b || 0), 0) + (upperSum() >= 63 ? 35 : 0); }
function render() {
  $("turn").textContent = Math.min(turn + 1, 12) + "/12"; $("upper").textContent = upperSum() + "/63"; $("total").textContent = totalSum();
  $("dice").innerHTML = dice.map((v, i) => `<button type="button" class="die${held[i] ? " held" : ""}" data-i="${i}" aria-label="주사위 ${i + 1}${held[i] ? " 고정됨" : ""}" ${left === 3 || over ? "disabled" : ""}>${v || "?"}</button>`).join("");
  $("roll").textContent = over ? "게임 끝" : left === 3 ? "굴리기" : `다시 굴리기 (${left}번 남음)`; $("roll").disabled = over || left === 0;
  $("cats").innerHTML = NAMES.map((n, c) => {
    const u = used[c] !== null, can = !u && left < 3 && !over;
    return `<button type="button" class="cat${u ? " done" : ""}" data-c="${c}" ${can ? "" : "disabled"}><span>${n}<small>${HINT[c]}</small></span><b>${u ? used[c] : can ? scoreOf(c, dice) : "–"}</b></button>`;
  }).join("");
}
function roll() { if (over || left === 0) return; dice = dice.map((v, i) => (left === 3 || !held[i] ? ri(1, 6) : v)); left--; render(); }
function pick(c) {
  if (over || left === 3 || used[c] !== null) return;
  used[c] = scoreOf(c, dice); turn++; dice = [0, 0, 0, 0, 0]; held = [false, false, false, false, false]; left = 3;
  if (turn === 12) finish();
  render();
}
function finish() {
  over = true; const t = totalSum(), nb = t > best; if (nb) { best = t; sv(KEY, best); }
  $("res").innerHTML = `<b>총점 ${t}점</b><p class="muted">${upperSum() >= 63 ? "보너스 35점 포함 · " : ""}최고 기록 ${best}점${nb ? " 🎉 신기록!" : ""}</p>`; $("res").hidden = false; $("again").hidden = false;
}
function reset() { dice = [0, 0, 0, 0, 0]; held = [false, false, false, false, false]; left = 3; used = Array(12).fill(null); turn = 0; over = false; $("res").hidden = true; $("again").hidden = true; render(); }
$("dice").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b && left < 3 && !over) { held[+b.dataset.i] = !held[+b.dataset.i]; render(); } });
$("cats").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b) pick(+b.dataset.c); });
$("roll").onclick = roll; $("again").onclick = reset; render();''',
     css=".dice{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.die{aspect-ratio:1;border-radius:14px;border:2px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:clamp(1.6rem,9vw,2.4rem);min-width:0;padding:0}.die.held{border-color:var(--accent);background:var(--soft);box-shadow:0 4px 0 var(--accent);transform:translateY(-4px)}.die:disabled{opacity:1;cursor:default}.cats{display:grid;grid-template-columns:1fr 1fr;gap:8px}.cat{display:flex;align-items:center;justify-content:space-between;gap:6px;text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px 10px;min-width:0;font-weight:700;font-size:.92rem;line-height:1.25}.cat small{display:block;font-weight:400;font-size:.7rem;color:var(--muted)}.cat b{font-family:var(--font-display);font-weight:400;font-size:1.3rem;color:var(--muted)}.cat:not(:disabled) b{color:var(--accent)}.cat:not(:disabled){border-color:var(--accent)}.cat.done{background:var(--soft)}.cat.done b{color:var(--fg)}.cat:disabled{cursor:default}")

# ---------------- 미니 스도쿠 ----------------
make("out/mini-sudoku.html", "미니 스도쿠", "🔢", 262, "minisudoku-best-v1",
     "빈칸에 숫자를 채워요. <b>가로줄, 세로줄, 굵은 선으로 나뉜 작은 상자</b> 안에 같은 숫자가 겹치지 않아야 해요. 4×4는 1~4, 6×6은 1~6을 써요. 칸을 누르고 아래 숫자를 눌러 채우세요. 겹치는 숫자는 빨갛게 표시돼요.",
     r'''  <div class="seg" id="mode" style="--n:2"><button type="button" data-m="4" class="on">4×4<small>쉬움</small></button><button type="button" data-m="6">6×6<small>보통</small></button></div>
  <div class="stats"><div class="stat"><small>시간</small><b id="time">0:00</b></div><div class="stat"><small>빈칸</small><b id="left">0</b></div><div class="stat"><small>최고 기록</small><b id="best">-</b></div></div>
  <div class="sgrid" id="grid"></div>
  <div class="pad" id="pad"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 퍼즐</button>''',
     r'''const CFG = { 4: [2, 2, 8], 6: [2, 3, 20] };
let N = 4, BH = 2, BW = 2, sol = [], puz = [], cur = [], fixed = [], sel = -1, done = false, t0 = 0, best = ld(KEY) || {}, timer = 0;
function ok(g, i, v) {
  const r = Math.floor(i / N), c = i % N;
  for (let k = 0; k < N; k++) { if (r * N + k !== i && g[r * N + k] === v) return false; if (k * N + c !== i && g[k * N + c] === v) return false; }
  const r0 = r - (r % BH), c0 = c - (c % BW);
  for (let a = 0; a < BH; a++) for (let b = 0; b < BW; b++) { const j = (r0 + a) * N + c0 + b; if (j !== i && g[j] === v) return false; }
  return true;
}
function solveCount(g, limit) {
  const i = g.indexOf(0); if (i < 0) return 1; let n = 0;
  for (let v = 1; v <= N; v++) if (ok(g, i, v)) { g[i] = v; n += solveCount(g, limit - n); g[i] = 0; if (n >= limit) break; }
  return n;
}
function fillRandom(g) {
  const i = g.indexOf(0); if (i < 0) return true;
  for (const v of shuf(Array.from({ length: N }, (_, k) => k + 1))) if (ok(g, i, v)) { g[i] = v; if (fillRandom(g)) return true; g[i] = 0; }
  return false;
}
function newGame(m) {
  if (m) { N = m; [BH, BW] = CFG[m]; }
  sol = Array(N * N).fill(0); fillRandom(sol); puz = [...sol]; let removed = 0;
  for (const i of shuf([...Array(N * N).keys()])) {
    if (removed >= CFG[N][2]) break; const v = puz[i]; puz[i] = 0;
    if (solveCount([...puz], 2) !== 1) puz[i] = v; else removed++;
  }
  cur = [...puz]; fixed = puz.map(v => v > 0); sel = -1; done = false; t0 = Date.now(); $("res").hidden = true;
  $("grid").style.gridTemplateColumns = `repeat(${N}, 1fr)`; $("grid").className = "sgrid n" + N;
  $("pad").innerHTML = Array.from({ length: N }, (_, k) => `<button type="button" data-v="${k + 1}">${k + 1}</button>`).join("") + `<button type="button" data-v="0" class="er">지우기</button>`;
  $("pad").style.gridTemplateColumns = `repeat(${N}, 1fr)`; render();
}
function conflict(i) { return cur[i] > 0 && !ok(cur, i, cur[i]); }
function fmt(s) { return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }
function render() {
  $("grid").innerHTML = cur.map((v, i) => {
    const r = Math.floor(i / N), c = i % N, cl = ["cell"];
    if (fixed[i]) cl.push("fx"); if (i === sel) cl.push("sel"); else if (sel >= 0 && v && v === cur[sel]) cl.push("same"); if (conflict(i)) cl.push("bad");
    if ((c + 1) % BW === 0 && c < N - 1) cl.push("br"); if ((r + 1) % BH === 0 && r < N - 1) cl.push("bb");
    return `<button type="button" class="${cl.join(" ")}" data-i="${i}" aria-label="${r + 1}행 ${c + 1}열 ${v || "빈칸"}">${v || ""}</button>`;
  }).join("");
  $("left").textContent = cur.filter(v => v === 0).length; $("best").textContent = best[N] ? fmt(best[N]) : "-";
}
function check() {
  if (cur.every(v => v > 0) && cur.every((v, i) => !conflict(i))) {
    done = true; const s = Math.round((Date.now() - t0) / 1000), nb = !best[N] || s < best[N]; if (nb) { best[N] = s; sv(KEY, best); }
    $("res").innerHTML = `<b>🎉 완성! ${fmt(s)}</b><p class="muted">${nb ? "신기록이에요!" : "최고 기록 " + fmt(best[N])}</p>`; $("res").hidden = false; render();
  }
}
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b && !done) { sel = +b.dataset.i; render(); } });
$("pad").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (!b || done || sel < 0 || fixed[sel]) return; cur[sel] = +b.dataset.v; render(); check(); });
$("mode").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (!b) return; document.querySelectorAll("#mode button").forEach(x => x.classList.toggle("on", x === b)); newGame(+b.dataset.m); });
$("again").onclick = () => newGame();
timer = setInterval(() => { if (!done) $("time").textContent = fmt(Math.floor((Date.now() - t0) / 1000)); }, 500);
newGame(4);''',
     css=".sgrid{display:grid;gap:0;border:3px solid var(--fg);border-radius:12px;overflow:hidden;background:var(--surface);width:100%;max-width:400px;margin:0 auto}.cell{aspect-ratio:1;border:0;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:clamp(1.5rem,8vw,2.2rem);padding:0;min-width:0;color:var(--accent)}.cell.fx{color:var(--fg);background:var(--soft)}.cell.br{border-right:3px solid var(--fg)}.cell.bb{border-bottom:3px solid var(--fg)}.cell.same{background:color-mix(in srgb,var(--accent) 18%,var(--surface))}.cell.sel{background:color-mix(in srgb,var(--accent) 38%,var(--surface))}.cell.bad{color:var(--bad);background:color-mix(in srgb,var(--bad) 16%,var(--surface))}.pad{display:grid;gap:6px}.pad button{padding:10px 0;border-radius:12px;border:1px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.5rem}.pad .er{grid-column:1/-1;font-family:var(--font-body);font-size:1rem;font-weight:700}")

# ---------------- 마방진 ----------------
make("out/magic-square.html", "마방진 퍼즐", "🔮", 285, "magicsquare-best-v1",
     "3×3 칸에 <b>1부터 9까지</b>를 한 번씩 넣어요. <b>가로 3줄, 세로 3줄, 대각선 2줄</b>의 합이 모두 <b>15</b>가 되면 성공! 칸을 누르고 아래 숫자를 눌러 채우세요. 처음부터 들어 있는 숫자(회색 칸)는 바꿀 수 없어요. 오른쪽과 아래의 숫자는 그 줄의 합이에요.",
     r'''  <div class="seg" id="diff" style="--n:3"><button type="button" data-k="4" class="on">쉬움<small>힌트 4개</small></button><button type="button" data-k="3">보통<small>힌트 3개</small></button><button type="button" data-k="2">어려움<small>힌트 2개</small></button></div>
  <div class="stats"><div class="stat"><small>시간</small><b id="time">0:00</b></div><div class="stat"><small>↘ 대각선</small><b id="d1">?</b></div><div class="stat"><small>↙ 대각선</small><b id="d2">?</b></div></div>
  <div class="mgrid" id="grid"></div>
  <div class="pad" id="pad"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 퍼즐</button>''',
     r'''const BASE = [[2, 7, 6], [9, 5, 1], [4, 3, 8]];
let K = 4, sol = [], cur = [], fixed = [], sel = -1, done = false, t0 = 0, best = ld(KEY) || {};
function makeSquare() {
  let g = BASE.map(r => [...r]);
  for (let k = ri(0, 3); k > 0; k--) g = [0, 1, 2].map(r => [0, 1, 2].map(c => g[2 - c][r]));
  if (Math.random() < 0.5) g = g.map(r => [...r].reverse());
  return g.flat();
}
const LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
const lineSum = l => (l.every(i => cur[i] > 0) ? l.reduce((a, i) => a + cur[i], 0) : null);
function fmt(s) { return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }
function newGame() {
  sol = makeSquare(); cur = Array(9).fill(0); fixed = Array(9).fill(false);
  for (const i of shuf([0, 1, 2, 3, 4, 5, 6, 7, 8]).slice(0, K)) { cur[i] = sol[i]; fixed[i] = true; }
  sel = -1; done = false; t0 = Date.now(); $("res").hidden = true; render();
}
function sumCell(l) { const s = lineSum(l); return `<div class="sumc ${s === null ? "" : s === 15 ? "g" : "b"}">${s === null ? "?" : s}</div>`; }
function render() {
  let h = "";
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) { const i = r * 3 + c, v = cur[i]; h += `<button type="button" class="mc${fixed[i] ? " fx" : ""}${i === sel ? " sel" : ""}" data-i="${i}" aria-label="${r + 1}행 ${c + 1}열 ${v || "빈칸"}">${v || ""}</button>`; }
    h += sumCell(LINES[r]);
  }
  for (let c = 0; c < 3; c++) h += sumCell(LINES[3 + c]);
  h += `<div class="sumc ghost"></div>`;
  $("grid").innerHTML = h;
  $("pad").innerHTML = Array.from({ length: 9 }, (_, k) => `<button type="button" data-v="${k + 1}" ${cur.includes(k + 1) && !(sel >= 0 && cur[sel] === k + 1) ? 'class="usedn"' : ""}>${k + 1}</button>`).join("") + `<button type="button" data-v="0" class="er">지우기</button>`;
  const a = lineSum(LINES[6]), b = lineSum(LINES[7]);
  $("d1").textContent = a === null ? "?" : a; $("d2").textContent = b === null ? "?" : b;
  $("d1").style.color = a === 15 ? "var(--ok)" : a === null ? "" : "var(--bad)"; $("d2").style.color = b === 15 ? "var(--ok)" : b === null ? "" : "var(--bad)";
}
function check() {
  if (cur.every(v => v > 0) && LINES.every(l => lineSum(l) === 15)) {
    done = true; const s = Math.round((Date.now() - t0) / 1000), nb = !best[K] || s < best[K]; if (nb) { best[K] = s; sv(KEY, best); }
    $("res").innerHTML = `<b>🎉 마방진 완성! ${fmt(s)}</b><p class="muted">${nb ? "이 난이도의 신기록이에요!" : "최고 기록 " + fmt(best[K])}</p>`; $("res").hidden = false;
  }
}
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b && !done) { sel = +b.dataset.i; render(); } });
$("pad").addEventListener("click", e => {
  const b = e.target.closest("[data-v]"); if (!b || done || sel < 0 || fixed[sel]) return; const v = +b.dataset.v;
  if (v > 0) { const j = cur.findIndex((x, i) => x === v && !fixed[i]); if (j >= 0) cur[j] = 0; if (fixed.some((f, i) => f && cur[i] === v)) return; }
  cur[sel] = v; render(); check();
});
$("diff").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (!b) return; document.querySelectorAll("#diff button").forEach(x => x.classList.toggle("on", x === b)); K = +b.dataset.k; newGame(); });
$("again").onclick = newGame;
setInterval(() => { if (!done) $("time").textContent = fmt(Math.floor((Date.now() - t0) / 1000)); }, 500);
newGame();''',
     css=".mgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;width:100%;max-width:360px;margin:0 auto}.mc{aspect-ratio:1;border-radius:12px;border:2px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:clamp(1.8rem,10vw,2.6rem);padding:0;min-width:0;color:var(--accent)}.mc.fx{background:var(--soft);color:var(--fg)}.mc.sel{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 35%,transparent)}.sumc{display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:1.3rem;color:var(--muted);border-radius:12px;background:var(--bg)}.sumc.g{color:#fff;background:var(--ok)}.sumc.b{color:#fff;background:var(--bad)}.sumc.ghost{background:transparent}.pad{display:grid;grid-template-columns:repeat(9,1fr);gap:4px}.pad button{padding:10px 0;border-radius:10px;border:1px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.3rem;min-width:0}.pad .usedn{opacity:.35}.pad .er{grid-column:1/-1;font-family:var(--font-body);font-size:1rem;font-weight:700}")

# ---------------- 영어 워들 ----------------
W = """apple 사과|bread 빵|chair 의자|table 탁자|water 물|light 빛|music 음악|house 집|mouse 쥐|horse 말|tiger 호랑이|zebra 얼룩말|whale 고래|snake 뱀|sheep 양|eagle 독수리|ocean 바다|river 강|beach 해변|cloud 구름|storm 폭풍|plant 식물|grass 풀|stone 돌|earth 지구|space 우주|heart 심장|smile 미소|happy 행복한|angry 화난|sleep 잠자다|dream 꿈|money 돈|phone 전화기|clock 시계|watch 손목시계|shirt 셔츠|shoes 신발|dress 원피스|pants 바지|glass 유리잔|plate 접시|spoon 숟가락|knife 칼|fruit 과일|lemon 레몬|grape 포도|peach 복숭아|mango 망고|candy 사탕|pizza 피자|sugar 설탕|juice 주스|cream 크림|honey 꿀|salad 샐러드|bench 벤치|floor 바닥|brick 벽돌|paper 종이|story 이야기|dance 춤추다|paint 칠하다|color 색깔|black 검정|white 하양|green 초록|brown 갈색|small 작은|large 큰|young 젊은|early 이른|tired 피곤한|fresh 신선한|sweet 달콤한|sharp 날카로운|quiet 조용한|round 둥근|magic 마법|robot 로봇|giant 거인|queen 여왕|angel 천사|ghost 유령|tooth 이빨|mouth 입|brain 뇌|train 기차|plane 비행기|truck 트럭|world 세계|night 밤|today 오늘|party 파티|class 학급|teach 가르치다|learn 배우다|write 쓰다|speak 말하다|think 생각하다|laugh 웃다|drink 마시다|shine 빛나다|climb 오르다"""
words = [x.split(" ") for x in W.split("|")]
assert all(len(a) == 5 and a.isalpha() and a.islower() for a, _ in words), [a for a, _ in words if len(a) != 5]
assert len(set(a for a, _ in words)) == len(words)
print("단어 수", len(words))
wl = ",".join('["%s","%s"]' % (a, b) for a, b in words)

make("out/wordle-en.html", "영어 워들", "🔠", 150, "wordleen-stats-v1",
     "숨은 <b>영어 단어(5글자)</b>를 6번 안에 맞혀 보세요. 5글자를 입력하고 엔터를 누르면 색깔로 힌트를 줘요. <b>초록</b>=글자와 자리가 모두 맞음, <b>노랑</b>=단어에 있지만 자리가 달라요, <b>회색</b>=단어에 없어요. 어떤 5글자든 입력할 수 있어요.",
     r'''  <div class="stats"><div class="stat"><small>시도</small><b id="tries">0/6</b></div><div class="stat"><small>맞힌 횟수</small><b id="wins">0</b></div><div class="stat"><small>플레이</small><b id="played">0</b></div></div>
  <div class="board" id="board"></div>
  <p class="center" id="msg" style="min-height:1.6em;font-weight:700"></p>
  <div class="kb" id="kb"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="next" type="button" hidden>다음 단어</button>''',
     r'''const WORDS = [@@WL@@];
let ans = "", meaning = "", guesses = [], cur = "", over = false, keyst = {}, stats = ld(KEY) || { w: 0, p: 0 };
function scoreGuess(g, a) {
  const r = Array(5).fill("x"), lf = {};
  for (let i = 0; i < 5; i++) { if (g[i] === a[i]) r[i] = "g"; else lf[a[i]] = (lf[a[i]] || 0) + 1; }
  for (let i = 0; i < 5; i++) { if (r[i] === "g") continue; if (lf[g[i]] > 0) { r[i] = "y"; lf[g[i]]--; } }
  return r.join("");
}
function newWord() {
  let w; do { w = WORDS[ri(0, WORDS.length - 1)]; } while (w[0] === ans && WORDS.length > 1);
  [ans, meaning] = w; guesses = []; cur = ""; over = false; keyst = {}; $("res").hidden = true; $("next").hidden = true; $("msg").textContent = ""; render();
}
function render() {
  let h = "";
  for (let r = 0; r < 6; r++) {
    const g = r < guesses.length ? guesses[r] : null, sc = g ? scoreGuess(g, ans) : "", txt = g || (r === guesses.length ? cur : "");
    for (let c = 0; c < 5; c++) h += `<div class="t ${g ? sc[c] : txt[c] ? "f" : ""}">${(txt[c] || "").toUpperCase()}</div>`;
  }
  $("board").innerHTML = h;
  const rows = ["qwertyuiop", "asdfghjkl", "!zxcvbnm<"];
  $("kb").innerHTML = rows.map(row => `<div class="kr">${[...row].map(k => k === "!" ? `<button type="button" class="k w" data-k="Enter">입력</button>` : k === "<" ? `<button type="button" class="k w" data-k="Backspace" aria-label="지우기">⌫</button>` : `<button type="button" class="k ${keyst[k] || ""}" data-k="${k}">${k.toUpperCase()}</button>`).join("")}</div>`).join("");
  $("tries").textContent = guesses.length + "/6"; $("wins").textContent = stats.w; $("played").textContent = stats.p;
}
function press(k) {
  if (over) return;
  if (k === "Backspace") cur = cur.slice(0, -1);
  else if (k === "Enter") {
    if (cur.length < 5) { $("msg").textContent = "5글자를 입력하세요"; return; }
    guesses.push(cur); const sc = scoreGuess(cur, ans), rank = { x: 1, y: 2, g: 3 };
    [...cur].forEach((ch, i) => { if (!keyst[ch] || rank[sc[i]] > rank[keyst[ch]]) keyst[ch] = sc[i]; });
    const win = cur === ans; cur = ""; $("msg").textContent = "";
    if (win || guesses.length === 6) {
      over = true; stats.p++; if (win) stats.w++; sv(KEY, stats);
      $("res").innerHTML = win ? `<b>🎉 정답! ${ans.toUpperCase()}</b><p class="muted">${meaning} · ${guesses.length}번 만에 맞혔어요</p>` : `<b>아쉬워요 😢 정답은 ${ans.toUpperCase()}</b><p class="muted">뜻: ${meaning}</p>`;
      $("res").hidden = false; $("next").hidden = false;
    }
  } else if (/^[a-z]$/.test(k) && cur.length < 5) { cur += k; $("msg").textContent = ""; }
  render();
}
$("kb").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) press(b.dataset.k); });
document.addEventListener("keydown", e => { if (e.ctrlKey || e.metaKey || e.altKey) return; const k = e.key.length === 1 ? e.key.toLowerCase() : e.key; if (k === "Enter" || k === "Backspace" || /^[a-z]$/.test(k)) { if (e.target.tagName === "BUTTON" && k === "Enter") return; press(k); } });
$("next").onclick = newWord; newWord();'''.replace("@@WL@@", wl),
     css=".board{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;width:100%;max-width:320px;margin:0 auto}.t{aspect-ratio:1;border:2px solid var(--line);border-radius:10px;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:clamp(1.6rem,9vw,2.2rem);background:var(--surface)}.t.f{border-color:var(--muted)}.t.g{background:#1f7a4d;border-color:#1f7a4d;color:#fff}.t.y{background:#8a6a00;border-color:#8a6a00;color:#fff}.t.x{background:#5b6477;border-color:#5b6477;color:#fff}.kb{display:flex;flex-direction:column;gap:6px}.kr{display:flex;gap:4px;justify-content:center}.k{flex:1;min-width:0;height:46px;padding:0;border-radius:8px;border:0;background:var(--soft);font-weight:700;font-size:.95rem}.k.w{flex:1.7;font-size:.8rem}.k.g{background:#1f7a4d;color:#fff}.k.y{background:#8a6a00;color:#fff}.k.x{background:#5b6477;color:#fff;opacity:.7}")
