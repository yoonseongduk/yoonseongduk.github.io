import sys, json
sys.path.insert(0, ".")
from mkpage import make

# ---------------- 플러드 잇 ----------------
make("out/flood-it.html", "플러드 잇", "🌊", 205, "floodit-best-v1",
     "왼쪽 위 칸에서 시작해 <b>아래 색 버튼을 눌러 그 덩어리의 색을 바꿔요.</b> 이웃한 같은 색 칸이 계속 합쳐져 덩어리가 커져요. 정해진 횟수 안에 판 전체를 한 가지 색으로 만들면 성공!",
     r'''  <div class="seg" id="lv" role="radiogroup" aria-label="난이도"></div>
  <div class="stats"><div class="stat"><small>남은 횟수</small><b id="left">0</b></div><div class="stat"><small>사용</small><b id="used">0</b></div><div class="stat"><small>최고(적은 횟수)</small><b id="best">-</b></div></div>
  <div class="field" id="field" aria-label="색 판"></div>
  <div class="pal" id="pal"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="new" type="button">새 판</button>''',
     r'''const COLORS = ["#e8453c", "#f2c200", "#3cc46a", "#3f9be0", "#a75be0", "#f08a24"], NAMES = ["빨강", "노랑", "초록", "파랑", "보라", "주황"];
const LV = { easy: { n: 8, slack: 6, label: "쉬움", hint: "8×8 · 여유 많음" }, normal: { n: 12, slack: 3, label: "보통", hint: "12×12" }, hard: { n: 14, slack: 1, label: "어려움", hint: "14×14 · 빠듯함" } };
let lv = (ld(KEY + "-lv") in LV) ? ld(KEY + "-lv") : "easy", g, n, used, limit, over, best = ld(KEY) || {};
const clone = a => a.map(r => r.slice());
// 왼쪽 위 칸과 이어진 같은 색 덩어리를 color로 바꾼다 (너비 우선 탐색). 바뀐 칸 수를 돌려준다
function flood(grid, color) {
  const n = grid.length, from = grid[0][0]; if (from === color) return 0; const st = [[0, 0]], seen = new Set(["0,0"]); let c = 0;
  while (st.length) { const [y, x] = st.pop(); grid[y][x] = color; c++; for (const [dy, dx] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const yy = y + dy, xx = x + dx, k = yy + "," + xx; if (yy >= 0 && xx >= 0 && yy < n && xx < n && !seen.has(k) && grid[yy][xx] === from) { seen.add(k); st.push([yy, xx]); } } }
  return c;
}
const regionSize = grid => { const t = clone(grid); return flood(t, -1); };
const solved = grid => grid.every(r => r.every(v => v === grid[0][0]));
// 욕심쟁이 풀이: 매번 덩어리가 가장 커지는 색을 고른다. 이 횟수를 '기준'으로 삼아 여유를 더해 제한 횟수로 쓴다
function greedy(grid) { const t = clone(grid); let k = 0; while (!solved(t) && k < 200) { let bc = -1, bs = -1; for (let c = 0; c < 6; c++) { if (c === t[0][0]) continue; const u = clone(t); flood(u, c); const s = regionSize(u); if (s > bs) { bs = s; bc = c; } } flood(t, bc); k++; } return k; }
function newGame() {
  n = LV[lv].n; g = Array.from({ length: n }, () => Array.from({ length: n }, () => ri(0, 5))); used = 0; over = false; limit = greedy(g) + LV[lv].slack; $("res").hidden = true; render();
}
function play(c) {
  if (over || c === g[0][0]) return; flood(g, c); used++;
  if (solved(g)) { over = true; let t = `${used}번 만에 한 가지 색으로 만들었어요.`; if (!best[lv] || used < best[lv]) { best[lv] = used; sv(KEY, best); t += " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>🎉 성공!</b><p class="muted">${t}</p>`; $("res").hidden = false; }
  else if (used >= limit) { over = true; $("res").innerHTML = `<b>😢 횟수를 모두 썼어요</b><p class="muted">새 판으로 다시 도전해 보세요!</p>`; $("res").hidden = false; }
  render();
}
function render() {
  $("field").style.gridTemplateColumns = `repeat(${n}, 1fr)`; $("field").innerHTML = g.map(r => r.map(v => `<i style="background:${COLORS[v]}"></i>`).join("")).join("");
  $("pal").innerHTML = COLORS.map((c, i) => `<button type="button" data-c="${i}" style="background:${c}" aria-label="${NAMES[i]}" ${over || i === g[0][0] ? "disabled" : ""}></button>`).join("");
  $("left").textContent = Math.max(0, limit - used); $("used").textContent = used; $("best").textContent = best[lv] ? best[lv] + "번" : "-";
  $("lv").style.setProperty("--n", 3); $("lv").innerHTML = Object.keys(LV).map(k => `<button type="button" class="${k === lv ? "on" : ""}" data-l="${k}" role="radio" aria-checked="${k === lv}">${LV[k].label}<small>${LV[k].hint}</small></button>`).join("");
}
$("pal").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b && !b.disabled) play(+b.dataset.c); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b && b.dataset.l !== lv) { lv = b.dataset.l; sv(KEY + "-lv", lv); newGame(); } });
$("new").onclick = newGame; newGame();''',
     css=".field{display:grid;gap:0;border-radius:12px;overflow:hidden;border:2px solid var(--line);aspect-ratio:1}.field i{display:block}.pal{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}.pal button{aspect-ratio:1;border-radius:50%;border:3px solid var(--surface);box-shadow:0 0 0 1px var(--line);padding:0}.pal button:disabled{opacity:.25;cursor:default}")

# ---------------- 숫자 정렬 ----------------
make("out/number-sort.html", "숫자 정렬", "🔃", 285, "numsort-best-v1",
     "숫자 카드를 <b>작은 수부터 큰 수 순서로</b> 왼쪽에서 오른쪽으로 정렬하세요. 카드 하나를 누른 뒤 <b>바로 옆 카드</b>를 누르면 서로 자리를 바꿔요. 가장 적은 횟수(최소)로 정렬하면 ⭐ 별 3개!",
     r'''  <div class="seg" id="lv" role="radiogroup" aria-label="카드 수"></div>
  <div class="stats"><div class="stat"><small>바꾼 횟수</small><b id="moves">0</b></div><div class="stat"><small>최소 횟수</small><b id="par">0</b></div><div class="stat"><small>최고</small><b id="best">-</b></div></div>
  <div class="cards" id="cards"></div>
  <div class="res" id="res" hidden></div>
  <div class="row"><button class="btn ghost" id="undo" type="button">↶ 되돌리기</button><button class="btn" id="new" type="button">새 판</button></div>''',
     r'''const LV = { 6: { label: "6장", hint: "쉬움" }, 8: { label: "8장", hint: "보통" }, 10: { label: "10장", hint: "어려움" } };
let lv = [6, 8, 10].includes(ld(KEY + "-lv")) ? ld(KEY + "-lv") : 8, a, sel = -1, moves = 0, par = 0, hist = [], done = false, best = ld(KEY) || {};
// 이웃한 두 카드만 바꿀 수 있으므로, 정렬에 필요한 최소 횟수는 '순서가 뒤집힌 쌍'의 수와 같다
const inversions = arr => { let c = 0; for (let i = 0; i < arr.length; i++) for (let j = i + 1; j < arr.length; j++) if (arr[i] > arr[j]) c++; return c; };
const isSorted = arr => arr.every((v, i) => !i || arr[i - 1] < v);
function newGame() { do { a = shuf(Array.from({ length: lv }, (_, i) => i + 1)); } while (isSorted(a)); par = inversions(a); sel = -1; moves = 0; hist = []; done = false; $("res").hidden = true; render(); }
function tap(i) {
  if (done) return; if (sel < 0) { sel = i; return render(); } if (sel === i) { sel = -1; return render(); }
  if (Math.abs(sel - i) !== 1) { sel = i; return render(); }
  hist.push(a.slice()); [a[sel], a[i]] = [a[i], a[sel]]; moves++; sel = -1;
  if (isSorted(a)) { done = true; const stars = moves <= par ? 3 : moves <= par + 3 ? 2 : 1; let t = `${moves}번 만에 정렬했어요. (최소 ${par}번)`; if (moves <= par && (!best[lv] || moves < best[lv])) { best[lv] = moves; sv(KEY, best); } if (!best[lv] || moves < best[lv]) { best[lv] = moves; sv(KEY, best); t += " 🏆 최고 기록이에요!"; }
    $("res").innerHTML = `<b>${"⭐".repeat(stars)}${"☆".repeat(3 - stars)} 정렬 완성!</b><p class="muted">${t}</p>`; $("res").hidden = false; }
  render();
}
function render() {
  $("cards").innerHTML = a.map((v, i) => `<button type="button" class="nc ${sel === i ? "sel" : ""} ${done ? "ok" : ""}" data-i="${i}" style="--h:${v / lv * 270}" aria-label="${v}">${v}</button>`).join("");
  $("moves").textContent = moves; $("par").textContent = par; $("best").textContent = best[lv] ? best[lv] + "번" : "-"; $("undo").disabled = !hist.length || done;
  $("lv").style.setProperty("--n", 3); $("lv").innerHTML = Object.keys(LV).map(k => `<button type="button" class="${+k === lv ? "on" : ""}" data-l="${k}" role="radio" aria-checked="${+k === lv}">${LV[k].label}<small>${LV[k].hint}</small></button>`).join("");
}
$("cards").addEventListener("click", e => { const c = e.target.closest("[data-i]"); if (c) tap(+c.dataset.i); });
$("undo").onclick = () => { if (!hist.length || done) return; a = hist.pop(); moves--; sel = -1; render(); }; $("new").onclick = newGame;
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b && +b.dataset.l !== lv) { lv = +b.dataset.l; sv(KEY + "-lv", lv); newGame(); } }); newGame();''',
     css=".cards{display:flex;gap:6px;justify-content:center;padding:16px 4px}.nc{flex:1;min-width:0;aspect-ratio:.7;max-width:56px;border-radius:12px;border:3px solid hsl(var(--h) 60% 45%);background:hsl(var(--h) 80% 90%);color:hsl(var(--h) 60% 25%);font-family:var(--font-display);font-size:1.6rem;padding:0;transition:transform .12s}.nc.sel{transform:translateY(-12px);box-shadow:0 6px 0 rgba(0,0,0,.18);background:var(--accent);color:var(--accent-fg);border-color:var(--accent)}.nc.ok{background:hsl(var(--h) 65% 55%);color:#fff}@media(prefers-color-scheme:dark){.nc{background:hsl(var(--h) 35% 22%);color:#fff}}")

# ---------------- 보물찾기 ----------------
make("out/treasure-hunt.html", "보물찾기", "🗺️", 40, "treasure-best-v1",
     "섬 어딘가에 보물이 묻혀 있어요. 칸을 눌러 땅을 파면 <b>보물과 얼마나 가까운지</b> 색과 말로 알려 줘요. 🔥 뜨거울수록 가까워요! 적게 파고 찾을수록 좋아요.",
     r'''  <div class="seg" id="lv" role="radiogroup" aria-label="섬 크기"></div>
  <div class="stats"><div class="stat"><small>판 횟수</small><b id="tries">0</b></div><div class="stat"><small>최근 힌트</small><b id="hint" style="font-size:1.05rem">-</b></div><div class="stat"><small>최고(적게)</small><b id="best">-</b></div></div>
  <div class="isle" id="isle" role="grid" aria-label="보물 섬"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="new" type="button">새 섬</button>''',
     r'''const LV = { 5: { label: "작은 섬", hint: "5×5" }, 7: { label: "보통 섬", hint: "7×7" }, 9: { label: "큰 섬", hint: "9×9" } };
let lv = [5, 7, 9].includes(ld(KEY + "-lv")) ? ld(KEY + "-lv") : 7, T, dug, tries, done, best = ld(KEY) || {}, lastHint = "-";
const dist = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);                      // 가로+세로로 몇 칸 떨어져 있는지
const heat = d => (d === 0 ? ["보물!", 5] : d === 1 ? ["🔥 아주 뜨거워요", 4] : d === 2 ? ["♨️ 뜨거워요", 3] : d <= 4 ? ["🙂 따뜻해요", 2] : d <= 6 ? ["😐 미지근해요", 1] : ["🥶 차가워요", 0]);
const COLS = ["#8fb8e8", "#a9d0d8", "#f4e3a0", "#f6b86a", "#ee6a4a", "#ffd23f"];
function newGame() { T = [ri(0, lv - 1), ri(0, lv - 1)]; dug = new Map(); tries = 0; done = false; lastHint = "-"; $("res").hidden = true; render(); }
function dig(y, x) {
  const k = y + "," + x; if (done || dug.has(k)) return; tries++; const d = dist([y, x], T), h = heat(d); dug.set(k, h[1]); lastHint = h[0];
  if (d === 0) { done = true; let t = `${tries}번 만에 보물을 찾았어요!`; if (!best[lv] || tries < best[lv]) { best[lv] = tries; sv(KEY, best); t += " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>💎 보물 발견!</b><p class="muted">${t}</p>`; $("res").hidden = false; }
  render();
}
function render() {
  $("isle").style.gridTemplateColumns = `repeat(${lv}, 1fr)`;
  $("isle").innerHTML = Array.from({ length: lv * lv }, (_, i) => { const y = Math.floor(i / lv), x = i % lv, k = y + "," + x, h = dug.get(k); return `<button type="button" class="ic" data-y="${y}" data-x="${x}" style="${h !== undefined ? "background:" + COLS[h] : ""}" ${h !== undefined ? "disabled" : ""} aria-label="${y + 1}행 ${x + 1}열">${h === 5 ? "💎" : h !== undefined ? "" : ""}</button>`; }).join("");
  $("tries").textContent = tries; $("hint").textContent = lastHint; $("best").textContent = best[lv] ? best[lv] + "번" : "-";
  $("lv").style.setProperty("--n", 3); $("lv").innerHTML = Object.keys(LV).map(k => `<button type="button" class="${+k === lv ? "on" : ""}" data-l="${k}" role="radio" aria-checked="${+k === lv}">${LV[k].label}<small>${LV[k].hint}</small></button>`).join("");
}
$("isle").addEventListener("click", e => { const c = e.target.closest("[data-y]"); if (c) dig(+c.dataset.y, +c.dataset.x); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b && +b.dataset.l !== lv) { lv = +b.dataset.l; sv(KEY + "-lv", lv); newGame(); } }); $("new").onclick = newGame; newGame();''',
     css=".isle{display:grid;gap:4px;background:#5aa0d8;padding:8px;border-radius:16px}.ic{aspect-ratio:1;border:0;border-radius:8px;background:#e6c98a;font-size:1.3rem;padding:0;box-shadow:inset 0 -3px 0 rgba(0,0,0,.15)}.ic:disabled{box-shadow:none;cursor:default}")

# ---------------- 업다운 ----------------
make("out/up-down.html", "업다운", "🎯", 15, "updown-best-v1",
     "컴퓨터가 1부터 100 사이의 숫자 하나를 정했어요. 숫자를 말하면 <b>더 큰지(UP), 더 작은지(DOWN)</b> 알려 줘요. 기회 안에 맞혀 보세요. 범위를 반으로 줄여 가며 찍으면 7번 안에 항상 맞힐 수 있어요!",
     r'''  <div class="seg" id="lv" role="radiogroup" aria-label="난이도"></div>
  <div class="stats"><div class="stat"><small>남은 기회</small><b id="left">0</b></div><div class="stat"><small>범위</small><b id="range" style="font-size:1.15rem">1~100</b></div><div class="stat"><small>최고(적게)</small><b id="best">-</b></div></div>
  <div class="res" id="msg" aria-live="polite"><div class="big" id="bigmsg">숫자를 입력해 보세요</div></div>
  <div class="row"><input type="number" id="g" inputmode="numeric" min="1" max="100" placeholder="1~100" aria-label="추측한 숫자"><button class="btn" id="go" type="button">확인</button></div>
  <div class="card"><h2>지난 추측</h2><p class="muted" id="hist">-</p></div>
  <button class="btn ghost" id="new" type="button">새 게임</button>''',
     r'''const LV = { easy: { tries: 10, max: 100, label: "쉬움", hint: "10번 · 1~100" }, normal: { tries: 7, max: 100, label: "보통", hint: "7번 · 1~100" }, hard: { tries: 10, max: 1000, label: "어려움", hint: "10번 · 1~1000" } };
let lv = (ld(KEY + "-lv") in LV) ? ld(KEY + "-lv") : "normal", secret, lo, hi, left, hist, over, best = ld(KEY) || {};
const judge = (g, s) => (g === s ? "hit" : g < s ? "up" : "down");               // 내 숫자가 정답보다 작으면 UP(더 크게), 크면 DOWN
function newGame() { const L = LV[lv]; secret = ri(1, L.max); lo = 1; hi = L.max; left = L.tries; hist = []; over = false; $("g").value = ""; $("g").placeholder = "1~" + L.max; $("g").max = L.max; $("bigmsg").textContent = "숫자를 입력해 보세요"; render(); }
function guess() {
  if (over) return; const L = LV[lv], v = parseInt($("g").value, 10);
  if (!Number.isInteger(v) || v < lo || v > hi) { $("bigmsg").textContent = `${lo}부터 ${hi} 사이로 입력하세요`; return; }
  const r = judge(v, secret); left--; hist.push(v + (r === "up" ? "⬆️" : r === "down" ? "⬇️" : "✅")); $("g").value = "";
  if (r === "hit") { over = true; $("bigmsg").textContent = `🎉 정답! ${LV[lv].tries - left}번 만에!`; const used = L.tries - left; if (!best[lv] || used < best[lv]) { best[lv] = used; sv(KEY, best); } }
  else { if (r === "up") lo = v + 1; else hi = v - 1; if (left <= 0) { over = true; $("bigmsg").textContent = `😢 기회를 모두 썼어요. 정답은 ${secret}`; } else $("bigmsg").textContent = r === "up" ? `⬆️ UP! ${v}보다 커요` : `⬇️ DOWN! ${v}보다 작아요`; }
  render();
}
function render() { $("left").textContent = left; $("range").textContent = lo + "~" + hi; $("best").textContent = best[lv] ? best[lv] + "번" : "-"; $("hist").textContent = hist.length ? hist.join("  ·  ") : "-"; $("go").disabled = over; $("lv").style.setProperty("--n", 3); $("lv").innerHTML = Object.keys(LV).map(k => `<button type="button" class="${k === lv ? "on" : ""}" data-l="${k}" role="radio" aria-checked="${k === lv}">${LV[k].label}<small>${LV[k].hint}</small></button>`).join(""); }
$("go").onclick = guess; $("g").addEventListener("keydown", e => { if (e.key === "Enter") guess(); }); $("new").onclick = newGame;
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b && b.dataset.l !== lv) { lv = b.dataset.l; sv(KEY + "-lv", lv); newGame(); } }); newGame();''')
