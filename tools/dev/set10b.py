import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 식 만들기 ----------
make(H+"equation-fill.html", "식 만들기", "➕", 20, "equation-fill-best-v1",
 "숫자 사이의 <b>빈칸(?)을 눌러서 + − × 중에서 골라</b> 식의 결과가 오른쪽 숫자와 같게 만드세요. 곱셈이 덧셈·뺄셈보다 먼저 계산돼요! 10문제를 풀면 끝이에요.",
 r'''  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="big eq" id="eq"></p><p class="muted" id="msg">빈칸을 눌러 바꿔 보세요</p></div>
  <button class="btn" id="check" type="button">확인</button>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>
  <div class="res" id="res" hidden></div>''',
 r'''const OPS = ["?", "+", "−", "×"];
let qs = [], i = 0, score = 0, best = ld(KEY) || 0, ops = [], locked = false;
const calc = (nums, o) => { const n = [...nums], p = [...o]; for (let k = 0; k < p.length;) { if (p[k] === "×") { n.splice(k, 2, n[k] * n[k + 1]); p.splice(k, 1); } else k++; } let r = n[0]; p.forEach((x, k) => { r = x === "+" ? r + n[k + 1] : r - n[k + 1]; }); return r; };
function makeQ(k) {
  const m = k < 4 ? 3 : 4;
  for (;;) { const nums = Array.from({ length: m }, () => ri(1, 9)), o = Array.from({ length: m - 1 }, () => OPS[ri(1, 3)]), t = calc(nums, o); if (t > 0 && t < 100) return { nums, t, sol: o }; }
}
function newRound() { qs = Array.from({ length: 10 }, (_, k) => makeQ(k)); i = 0; score = 0; $("res").hidden = true; show(); }
function show() {
  const q = qs[i]; locked = false; ops = q.nums.slice(1).map(() => "?"); $("next").hidden = true; $("check").hidden = false; $("msg").textContent = "빈칸을 눌러 바꿔 보세요"; $("msg").style.color = "";
  render(); $("no").textContent = (i + 1) + "/10"; $("score").textContent = score; $("best").textContent = best;
}
function render() { const q = qs[i]; $("eq").innerHTML = q.nums.map((n, k) => `<span>${n}</span>` + (k < ops.length ? `<button type="button" class="op" data-k="${k}">${ops[k]}</button>` : "")).join("") + `<span>= ${q.t}</span>`; }
function check() {
  if (locked) return; const q = qs[i]; if (ops.includes("?")) { $("msg").textContent = "빈칸을 모두 채워 주세요"; return; }
  locked = true; const ok = calc(q.nums, ops) === q.t; if (ok) score++;
  $("msg").textContent = ok ? "⭕ 정답!" : "❌ 아쉬워요. 하나의 답은 " + q.nums.map((n, k) => n + (q.sol[k] || "")).join(" ") + " = " + q.t; $("msg").style.color = ok ? "var(--ok)" : "var(--bad)";
  $("score").textContent = score; $("check").hidden = true; $("next").textContent = i === 9 ? "결과 보기" : "다음 문제"; $("next").hidden = false;
}
function finish() { let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("next").hidden = true; $("eq").textContent = "끝!"; $("res").innerHTML = `<b>10문제 중 ${score}개 정답</b><p class="muted">${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("res").hidden = false; $("best").textContent = best; $("again").onclick = newRound; }
$("eq").addEventListener("click", e => { const b = e.target.closest(".op"); if (!b || locked) return; const k = +b.dataset.k; ops[k] = OPS[(OPS.indexOf(ops[k]) % 3) + 1]; render(); });
$("check").onclick = check; $("next").onclick = () => { if (i === 9) finish(); else { i++; show(); } }; newRound();''',
 css=".eq{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:center}.op{width:52px;height:52px;border-radius:14px;border:2px dashed var(--accent);background:var(--soft);font-family:var(--font-display);font-size:1.8rem;padding:0}")

# ---------- 숫자 피라미드 ----------
make(H+"number-pyramid.html", "숫자 피라미드", "🔺", 42, "pyramid-best-v1",
 "아래 두 칸을 더하면 바로 위 칸의 숫자가 돼요. <b>빈칸을 눌러서 숫자를 채워</b> 피라미드를 완성하세요. 칸을 누르고 아래 숫자 키패드를 눌러 입력해요.",
 r'''  <div class="seg" id="lv" style="--n:2"><button type="button" data-n="4" class="on">4층<small>쉬움</small></button><button type="button" data-n="5">5층<small>보통</small></button></div>
  <div class="stats"><div class="stat"><small>시간</small><b id="time">0:00</b></div><div class="stat"><small>빈칸</small><b id="left">0</b></div><div class="stat"><small>최고 기록</small><b id="best">-</b></div></div>
  <div class="pyr" id="pyr"></div>
  <div class="pad" id="pad"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 문제</button>''',
 r'''let L = 4, full = [], cur = [], given = [], sel = -1, done = false, t0 = 0, best = ld(KEY) || {};
const idx = (r, c) => r * (r + 1) / 2 + c;                       // r층(위=0) c번째 칸 번호
const fmt = s => Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
function newGame() {
  full = []; for (let r = L - 1; r >= 0; r--) for (let c = 0; c <= r; c++) full[idx(r, c)] = r === L - 1 ? ri(1, 9) : full[idx(r + 1, c)] + full[idx(r + 1, c + 1)];
  const total = L * (L + 1) / 2, hide = L === 4 ? 5 : 8; given = Array(total).fill(true);
  for (const k of shuf([...Array(total).keys()]).slice(0, hide)) given[k] = false;
  cur = full.map((v, k) => given[k] ? v : 0); sel = -1; done = false; t0 = Date.now(); $("res").hidden = true; render();
}
const valid = () => { for (let r = 0; r < L - 1; r++) for (let c = 0; c <= r; c++) if (cur[idx(r, c)] !== cur[idx(r + 1, c)] + cur[idx(r + 1, c + 1)]) return false; return cur.every(v => v > 0); };
function render() {
  let h = ""; for (let r = 0; r < L; r++) { h += `<div class="pr">`; for (let c = 0; c <= r; c++) { const k = idx(r, c); h += `<button type="button" class="pc${given[k] ? " fx" : ""}${k === sel ? " sel" : ""}" data-k="${k}">${cur[k] || ""}</button>`; } h += `</div>`; }
  $("pyr").innerHTML = h; $("left").textContent = cur.filter(v => !v).length; $("best").textContent = best[L] ? fmt(best[L]) : "-";
  $("pad").innerHTML = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map(n => `<button type="button" data-v="${n}">${n}</button>`).join("") + `<button type="button" data-v="x" class="er">지우기</button>`;
}
function key(v) {
  if (done || sel < 0 || given[sel]) return;
  cur[sel] = v === "x" ? 0 : (cur[sel] && cur[sel] < 10 ? cur[sel] * 10 + +v : +v); if (cur[sel] > 99) cur[sel] = +v; render();
  if (valid()) { done = true; const s = Math.round((Date.now() - t0) / 1000), nb = !best[L] || s < best[L]; if (nb) { best[L] = s; sv(KEY, best); } $("res").innerHTML = `<b>🎉 완성! ${fmt(s)}</b><p class="muted">${nb ? "신기록이에요!" : "최고 기록 " + fmt(best[L])}</p>`; $("res").hidden = false; render(); }
}
$("pyr").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && !done) { sel = +b.dataset.k; render(); } });
$("pad").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (b) key(b.dataset.v); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); L = +b.dataset.n; newGame(); });
$("again").onclick = newGame; setInterval(() => { if (!done) $("time").textContent = fmt(Math.floor((Date.now() - t0) / 1000)); }, 500); newGame();''',
 css=".pyr{display:flex;flex-direction:column;gap:6px;align-items:center}.pr{display:flex;gap:6px}.pc{width:clamp(46px,16vw,62px);height:clamp(42px,12vw,52px);border-radius:10px;border:2px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.3rem;padding:0;color:var(--accent)}.pc.fx{background:var(--soft);color:var(--fg)}.pc.sel{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 30%,transparent)}.pad{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.pad button{padding:10px 0;border-radius:10px;border:1px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.3rem;min-width:0}.pad .er{grid-column:1/-1;font-family:var(--font-body);font-size:1rem;font-weight:700}")

# ---------- 블록 퍼즐 ----------
make(H+"block-puzzle.html", "블록 퍼즐", "🧱", 215, "blockpuzzle-best-v1",
 "아래 <b>블록 3개 중 하나를 눌러 고른 뒤</b>, 판의 빈 곳을 눌러 놓으세요. <b>누른 칸이 블록의 시작(맨 위 왼쪽) 칸</b>이 되고, 놓일 자리가 연하게 미리 보여요(컴퓨터에서 마우스를 올렸을 때). 가로줄이나 세로줄이 가득 차면 사라지고 점수를 얻어요. 놓을 곳이 없으면 끝이에요!",
 r'''  <div class="stats"><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>최고 점수</small><b id="best">0</b></div><div class="stat"><small>고른 블록</small><b id="pick">-</b></div></div>
  <div class="bgrid" id="board"></div>
  <div class="tray" id="tray"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">다시 하기</button>''',
 r'''const N = 8, SHAPES = [[[0, 0]], [[0, 0], [0, 1]], [[0, 0], [1, 0]], [[0, 0], [0, 1], [0, 2]], [[0, 0], [1, 0], [2, 0]], [[0, 0], [0, 1], [0, 2], [0, 3]], [[0, 0], [1, 0], [2, 0], [3, 0]], [[0, 0], [0, 1], [1, 0], [1, 1]], [[0, 0], [1, 0], [1, 1]], [[0, 0], [0, 1], [1, 0]], [[0, 1], [1, 0], [1, 1]], [[0, 0], [0, 1], [1, 1]], [[0, 0], [0, 1], [0, 2], [1, 0], [2, 0]], [[0, 0], [0, 1], [0, 2], [1, 1]], [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]], [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]];
let b = [], pieces = [], sel = -1, score = 0, over = false, best = ld(KEY) || 0, prev = null;
const COLORS = ["#e4572e", "#29a3a3", "#e9a23b", "#6a4c93", "#3fa34d", "#d1495b"];
function deal() { pieces = [0, 1, 2].map(() => ({ s: SHAPES[ri(0, SHAPES.length - 1)], c: ri(0, COLORS.length - 1), used: false })); sel = -1; }
function newGame() { b = Array.from({ length: N }, () => Array(N).fill(-1)); score = 0; over = false; $("res").hidden = true; deal(); render(); }
const center = s => [...s].sort((a, b) => a[0] - b[0] || a[1] - b[1])[0];      // 누른 칸이 블록의 '시작 칸'(맨 위 줄의 맨 왼쪽 칸)이 되도록
const cellsAt = (s, r, c) => { const [cr, cc] = center(s); return s.map(([dr, dc]) => [r + dr - cr, c + dc - cc]); };
const fits = (s, r, c) => cellsAt(s, r, c).every(([y, x]) => y >= 0 && y < N && x >= 0 && x < N && b[y][x] < 0);
const anyFit = s => { for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (fits(s, r, c)) return true; return false; };
function render() {
  const gh = new Set(); if (sel >= 0 && prev && !pieces[sel].used) { const ok = fits(pieces[sel].s, prev[0], prev[1]); if (ok) cellsAt(pieces[sel].s, prev[0], prev[1]).forEach(([y, x]) => gh.add(y * N + x)); }
  $("board").innerHTML = b.map((row, r) => row.map((v, c) => `<button type="button" class="bc${gh.has(r * N + c) ? " gh" : ""}" data-r="${r}" data-c="${c}" style="${v >= 0 ? "background:" + COLORS[v] : gh.has(r * N + c) ? "background:" + COLORS[pieces[sel].c] + ";opacity:.45" : ""}" aria-label="${r + 1}행 ${c + 1}열"></button>`).join("")).join("");
  $("tray").innerHTML = pieces.map((p, k) => { const h = Math.max(...p.s.map(x => x[0])) + 1, w = Math.max(...p.s.map(x => x[1])) + 1; return `<button type="button" class="pc${k === sel ? " sel" : ""}" data-k="${k}" ${p.used || over ? "disabled" : ""} style="${p.used ? "visibility:hidden" : ""}"><span class="mini" style="grid-template-columns:repeat(${w},14px)">${Array.from({ length: h * w }, (_, q) => `<i style="${p.s.some(([dr, dc]) => dr * w + dc === q) ? "background:" + COLORS[p.c] : "background:transparent"}"></i>`).join("")}</span></button>`; }).join("");
  $("score").textContent = score; $("best").textContent = best; $("pick").textContent = sel >= 0 ? "블록 " + (sel + 1) : "-";
}
function place(r, c) {
  if (over || sel < 0) return; const p = pieces[sel]; if (!fits(p.s, r, c)) return;
  cellsAt(p.s, r, c).forEach(([y, x]) => { b[y][x] = p.c; }); score += p.s.length; p.used = true; sel = -1;
  const rows = [], cols = []; for (let k = 0; k < N; k++) { if (b[k].every(v => v >= 0)) rows.push(k); if (b.every(row => row[k] >= 0)) cols.push(k); }
  rows.forEach(y => { for (let x = 0; x < N; x++) b[y][x] = -1; }); cols.forEach(x => { for (let y = 0; y < N; y++) b[y][x] = -1; });
  const lines = rows.length + cols.length; if (lines) score += lines * 10 + (lines - 1) * 10;
  if (pieces.every(q => q.used)) deal();
  if (!pieces.filter(q => !q.used).some(q => anyFit(q.s))) { over = true; if (score > best) { best = score; sv(KEY, best); } $("res").innerHTML = `<b>더 놓을 곳이 없어요! ${score}점</b><p class="muted">최고 점수 ${best}점</p>`; $("res").hidden = false; }
  render();
}
$("tray").addEventListener("click", e => { const k = e.target.closest("[data-k]"); if (k) { sel = sel === +k.dataset.k ? -1 : +k.dataset.k; render(); } });
$("board").addEventListener("click", e => { const c = e.target.closest("[data-r]"); if (c) place(+c.dataset.r, +c.dataset.c); });
$("board").addEventListener("pointerover", e => { const c = e.target.closest("[data-r]"); if (c && sel >= 0 && e.pointerType === "mouse") { const q = [+c.dataset.r, +c.dataset.c]; if (!prev || prev[0] !== q[0] || prev[1] !== q[1]) { prev = q; render(); } } });
$("again").onclick = newGame; newGame();''',
 css=".bgrid{display:grid;grid-template-columns:repeat(8,1fr);gap:3px;background:var(--line);padding:3px;border-radius:12px}.bc{aspect-ratio:1;border:0;border-radius:6px;background:var(--surface);padding:0;min-width:0}.tray{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.tray .pc{height:92px;border:2px solid var(--line);border-radius:14px;background:var(--surface);display:flex;align-items:center;justify-content:center}.tray .pc.sel{border-color:var(--accent);background:var(--soft)}.mini{display:grid;gap:2px}.mini i{width:14px;height:14px;border-radius:3px;display:block}")
