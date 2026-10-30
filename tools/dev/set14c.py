import sys, json
sys.path.insert(0, ".")
from mkpage import make
from mkarcade import make as make_arcade
H = "out/"

# ---------- 체커 ----------
make(H+"checkers.html", "체커 (서양 장기)", "🔴", 12, "checkers-best-v1",
 "🔵 내 말은 아래에서 위로, 🔴 컴퓨터 말은 위에서 아래로 <b>대각선 앞으로 한 칸</b> 움직여요. 상대 말을 <b>뛰어넘으면 잡을 수 있고</b>, 잡을 수 있을 땐 <b>반드시 잡아야</b> 해요! 끝줄에 닿으면 <b>왕(♛)</b>이 되어 뒤로도 움직여요. 상대 말을 모두 잡거나 움직일 수 없게 하면 승리!",
 r'''  <div class="stats"><div class="stat"><small>내 말</small><b id="a">12</b></div><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">🔵 나</b></div><div class="stat"><small>컴퓨터 말</small><b id="c">12</b></div></div>
  <div class="ck" id="board"></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''// 0 빈칸, 1 내 말, 3 내 왕, 2 컴퓨터 말, 4 컴퓨터 왕
let b = [], sel = null, moves = [], turn = 0, over = false, busy = false, wins = ld(KEY) || 0, tempo = 1, quiet = 0;
const mine = v => v === 1 || v === 3, theirs = v => v === 2 || v === 4;
function newGame() { b = Array.from({ length: 8 }, (_, r) => Array.from({ length: 8 }, (_, c) => (r + c) % 2 === 1 ? (r < 3 ? 2 : r > 4 ? 1 : 0) : 0)); sel = null; turn = 0; over = false; busy = false; quiet = 0; $("res").hidden = true; $("msg").textContent = ""; moves = legal(0); render(); }
function dirs(v) { return v === 1 ? [[-1, -1], [-1, 1]] : v === 2 ? [[1, -1], [1, 1]] : [[-1, -1], [-1, 1], [1, -1], [1, 1]]; }
const inb = (r, c) => r >= 0 && r < 8 && c >= 0 && c < 8;
function jumpsFrom(bd, r, c, v, who, caps, out, start) {
  let any = false; for (const [dr, dc] of dirs(v)) { const mr = r + dr, mc = c + dc, lr = r + 2 * dr, lc = c + 2 * dc; if (!inb(lr, lc)) continue; const e = bd[mr][mc]; if (!(who === 0 ? theirs(e) : mine(e)) || caps.some(([y, x]) => y === mr && x === mc)) continue; const landEmpty = bd[lr][lc] === 0 || (lr === start[0] && lc === start[1]); if (!landEmpty) continue; any = true; const nc = [...caps, [mr, mc]], crown = (who === 0 && lr === 0 && v === 1) || (who === 1 && lr === 7 && v === 2); if (crown) out.push({ from: start, to: [lr, lc], caps: nc, crown: true }); else { const before = out.length; jumpsFrom(bd, lr, lc, v, who, nc, out, start); if (out.length === before) out.push({ from: start, to: [lr, lc], caps: nc }); } }
  return any;
}
function legal(who, bd = b) {
  const jumps = [], steps = [];
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) { const v = bd[r][c]; if (!(who === 0 ? mine(v) : theirs(v))) continue; jumpsFrom(bd, r, c, v, who, [], jumps, [r, c]); for (const [dr, dc] of dirs(v)) { const y = r + dr, x = c + dc; if (inb(y, x) && bd[y][x] === 0) steps.push({ from: [r, c], to: [y, x], caps: [], crown: (who === 0 && y === 0 && v === 1) || (who === 1 && y === 7 && v === 2) }); } }
  return jumps.length ? jumps : steps;
}
function apply(m) { const [r, c] = m.from, v = b[r][c]; b[r][c] = 0; m.caps.forEach(([y, x]) => { b[y][x] = 0; }); b[m.to[0]][m.to[1]] = m.crown ? (v === 1 ? 3 : 4) : v; quiet = m.caps.length || v === 1 || v === 2 ? 0 : quiet + 1; }
function count() { const a = b.flat().filter(mine).length, c = b.flat().filter(theirs).length; return [a, c]; }
function render() {
  const dest = sel ? moves.filter(m => m.from[0] === sel[0] && m.from[1] === sel[1]).map(m => m.to) : [], froms = moves.map(m => m.from);
  $("board").innerHTML = b.map((row, r) => row.map((v, c) => { const dark = (r + c) % 2 === 1, d = dest.some(([y, x]) => y === r && x === c), s = sel && sel[0] === r && sel[1] === c, can = turn === 0 && !over && !busy && froms.some(([y, x]) => y === r && x === c); return `<button type="button" class="sq${dark ? " dk" : ""}${d ? " dest" : ""}${s ? " sel" : ""}${can && !sel ? " can" : ""}" data-r="${r}" data-c="${c}" ${dark ? "" : "disabled"}>${v ? `<i class="pc ${mine(v) ? "me" : "cp"}">${v > 2 ? "♛" : ""}</i>` : ""}</button>`; }).join("")).join("");
  const [a, c] = count(); $("a").textContent = a; $("c").textContent = c; $("turn").textContent = over ? "-" : turn ? "🔴 컴퓨터" : "🔵 나";
}
function endCheck() { const [a, c] = count(); const mv = legal(turn); if (!mv.length || !a || !c) { over = true; const iWin = turn === 1 || !c; if (iWin) { wins++; sv(KEY, wins); } $("res").innerHTML = `<b>${iWin ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"}</b><p class="muted">누적 승리 ${wins}번</p>`; $("res").hidden = false; render(); return true; } if (quiet >= 40) { over = true; $("res").innerHTML = `<b>🤝 비겼어요</b>`; $("res").hidden = false; render(); return true; } moves = mv; return false; }
function tap(r, c) {
  if (over || busy || turn !== 0) return; const v = b[r][c];
  if (mine(v) && moves.some(m => m.from[0] === r && m.from[1] === c)) { sel = [r, c]; return render(); }
  if (sel && v === 0) { const cand = moves.filter(m => m.from[0] === sel[0] && m.from[1] === sel[1] && m.to[0] === r && m.to[1] === c).sort((x, y) => y.caps.length - x.caps.length)[0]; if (!cand) return; apply(cand); sel = null; turn = 1; if (endCheck()) return; render(); busy = true; $("msg").textContent = "컴퓨터 차례..."; setTimeout(cpuMove, 700 * tempo); }
}
function cpuMove() {
  if (over) return; const mv = legal(1), best = Math.max(...mv.map(m => m.caps.length)); let pool = mv.filter(m => m.caps.length === best); const risk = m => { const sb = b.map(r => [...r]), sq = quiet; apply(m); const o = legal(0), rk = o.length ? Math.max(...o.map(x => x.caps.length)) : 0; b = sb; quiet = sq; return rk; }; const score = m => m.caps.length * 10 + (m.crown ? 6 : 0) + m.to[0] * .6 + Math.random() * 3 - risk(m) * 9; pool.sort((x, y) => score(y) - score(x)); apply(pool[0]); turn = 0; busy = false; $("msg").textContent = pool[0].caps.length ? "컴퓨터가 내 말을 잡았어요!" : "내 차례!"; if (endCheck()) return; render();
}
$("board").addEventListener("click", e => { const s = e.target.closest("[data-r]"); if (s) tap(+s.dataset.r, +s.dataset.c); });
$("again").onclick = newGame; newGame();''',
 css=".ck{display:grid;grid-template-columns:repeat(8,1fr);gap:0;border:3px solid var(--fg);border-radius:8px;overflow:hidden;max-width:380px;margin:0 auto;width:100%}.sq{aspect-ratio:1;border:0;padding:0;background:#f0d9b5;display:flex;align-items:center;justify-content:center;min-width:0}.sq.dk{background:#8b5a2b}.sq.dest{background:#c9a227}.sq.sel{background:#d9b13a}.sq.can .pc{box-shadow:0 0 0 3px var(--accent)}.sq:disabled{opacity:1;cursor:default}.pc{display:flex;align-items:center;justify-content:center;width:78%;height:78%;border-radius:50%;font-style:normal;font-size:1.1rem;color:#ffe08a;border:3px solid rgba(255,255,255,.55)}.pc.me{background:#2f6fdf}.pc.cp{background:#d6453a}")

# ---------- 알까기 ----------
make_arcade(H+"alkkagi.html", "알까기", "⚫", 28, "alkkagi-best-v1", 300, 420, "내 돌 : 적 돌", "상대 돌을 모두 판 밖으로 밀어내세요",
 "내 돌(파랑)을 <b>누른 채 뒤로 끌었다가 놓으면</b> 튕겨 나가요. 끌수록 세게 날아가요! 상대 돌(빨강)을 부딪혀서 <b>판 밖으로 떨어뜨리면</b> 점수! 내 돌이 떨어지면 안 돼요. 내 돌 5개, 컴퓨터 돌 5개로 시작해요.",
 r'''
let st, turn, moving, sel, aim, wait, nMe, nCp;
const R = 15, L = 8;
function reset() { st = []; for (let i = 0; i < 5; i++) { st.push({ x: 40 + i * 55, y: 330, vx: 0, vy: 0, o: 0 }); st.push({ x: 40 + i * 55, y: 90, vx: 0, vy: 0, o: 1 }); } turn = 0; moving = false; sel = null; aim = null; wait = 0; updInfo(); }
function updInfo() { nMe = st.filter(s => s.o === 0).length; nCp = st.filter(s => s.o === 1).length; setInfo(nMe + " : " + nCp); }
function pointer(t, x, y) { if (turn !== 0 || moving) return; if (t === "down") { sel = st.filter(s => s.o === 0).find(s => Math.hypot(s.x - x, s.y - y) < R + 10) || null; if (sel) aim = { x, y }; } else if (t === "move" && sel) { aim = { x, y }; } else if (t === "up" && sel) { const dx = sel.x - aim.x, dy = sel.y - aim.y, d = Math.hypot(dx, dy); if (d > 10) { const sp = Math.min(d, 110) * 5.2; sel.vx = dx / d * sp; sel.vy = dy / d * sp; moving = true; } sel = null; aim = null; } }
function update(dt) {
  if (!moving && turn === 1) { wait -= dt; if (wait <= 0) { const cs = st.filter(s => s.o === 1), ps = st.filter(s => s.o === 0); if (cs.length && ps.length) { let bestS = null, bd = 1e9; for (const c of cs) for (const p of ps) { const d = Math.hypot(c.x - p.x, c.y - p.y); if (d < bd + Math.random() * 60) { bd = d; bestS = [c, p]; } } const [c, p] = bestS, a = Math.atan2(p.y - c.y, p.x - c.x) + (Math.random() - .5) * .22, sp = rand(330, 520); c.vx = Math.cos(a) * sp; c.vy = Math.sin(a) * sp; moving = true; } } }
  if (!moving) return;
  const sub = 3; for (let q = 0; q < sub; q++) { const h = dt / sub; for (const s of st) { s.x += s.vx * h; s.y += s.vy * h; }
    for (let i = 0; i < st.length; i++) for (let j = i + 1; j < st.length; j++) { const a = st[i], b = st[j], dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy); if (d < 2 * R && d > 0) { const nx = dx / d, ny = dy / d, ov = 2 * R - d; a.x -= nx * ov / 2; a.y -= ny * ov / 2; b.x += nx * ov / 2; b.y += ny * ov / 2; const va = a.vx * nx + a.vy * ny, vb = b.vx * nx + b.vy * ny, diff = vb - va; if (diff < 0) { a.vx += diff * nx * .95; a.vy += diff * ny * .95; b.vx -= diff * nx * .95; b.vy -= diff * ny * .95; } } } }
  const f = Math.pow(.14, dt); for (const s of st) { s.vx *= f; s.vy *= f; if (Math.hypot(s.vx, s.vy) < 6) { s.vx = s.vy = 0; } }
  for (let k = st.length - 1; k >= 0; k--) { const s = st[k]; if (s.x < L || s.x > W - L || s.y < L || s.y > H - L) { if (s.o === 1) addScore(10); st.splice(k, 1); } }
  updInfo();
  if (st.every(s => !s.vx && !s.vy)) { moving = false; if (!nCp) { addScore(30); return end(); } if (!nMe) return end(); turn = 1 - turn; wait = .9; }
}
function draw(c) {
  c.fillStyle = "#d9b27c"; c.fillRect(L, L, W - 2 * L, H - 2 * L); c.strokeStyle = "#5a3b1a"; c.lineWidth = 3; c.strokeRect(L, L, W - 2 * L, H - 2 * L); c.strokeStyle = "rgba(90,59,26,.35)"; c.lineWidth = 1; for (let i = 1; i < 8; i++) { c.beginPath(); c.moveTo(L, L + i * (H - 2 * L) / 8); c.lineTo(W - L, L + i * (H - 2 * L) / 8); c.stroke(); }
  for (const s of st) { c.fillStyle = "rgba(0,0,0,.25)"; c.beginPath(); c.arc(s.x + 2, s.y + 3, R, 0, 7); c.fill(); c.fillStyle = s.o ? "#d6453a" : "#2f6fdf"; c.beginPath(); c.arc(s.x, s.y, R, 0, 7); c.fill(); c.fillStyle = "rgba(255,255,255,.35)"; c.beginPath(); c.arc(s.x - 4, s.y - 5, R * .4, 0, 7); c.fill(); }
  if (sel && aim) { c.strokeStyle = C.accent; c.lineWidth = 3; c.setLineDash([6, 5]); c.beginPath(); c.moveTo(sel.x, sel.y); c.lineTo(sel.x + (sel.x - aim.x), sel.y + (sel.y - aim.y)); c.stroke(); c.setLineDash([]); }
  c.font = "700 14px sans-serif"; c.fillStyle = C.fg; c.textAlign = "center"; c.fillText(turn === 0 && !moving ? "내 차례: 파란 돌을 끌었다 놓으세요" : turn === 1 && !moving ? "컴퓨터 차례..." : "", W / 2, H / 2);
}
''')
