import sys
sys.path.insert(0, ".")
from mkarcade import make
H = "out/"

# 1. 볼링
make(H+"bowling.html", "볼링", "🎳", 220, "bowling-best-v1", 300, 440, "프레임", "핀을 최대한 많이 쓰러뜨리세요",
 "화면을 <b>누르고 위쪽으로 끌었다 놓으면</b> 공이 굴러가요. 끈 방향이 공이 가는 방향이고, 길게 끌수록 빨라요. 한 프레임에 2번 던지고 모두 5프레임이에요. 한 번에 모두 쓰러뜨리면(스트라이크) 보너스!",
 r'''
let ball, pins, fr, throwNo, aim, wait, bx, standing;
const PX = [[0, 0], [-1, 1], [1, 1], [-2, 2], [0, 2], [2, 2], [-3, 3], [-1, 3], [1, 3], [3, 3]];
function rack() { pins = PX.map(([c, r]) => ({ x: W / 2 + c * 15, y: 70 + r * 26, up: true })); standing = 10; }
function reset() { fr = 1; throwNo = 1; ball = null; aim = null; wait = 0; bx = W / 2; rack(); setInfo("1/5"); }
function pointer(t, x, y) {
  if (ball || wait > 0) return;
  if (t === "down") { aim = { sx: x, sy: y, x, y }; bx = clamp(x, 50, W - 50); } else if (t === "move" && aim) { aim.x = x; aim.y = y; }
  else if (t === "up" && aim) { const dx = aim.x - aim.sx, dy = aim.y - aim.sy; aim = null; if (dy > -14) return; const d = Math.hypot(dx, dy), sp = clamp(d * 4.5, 260, 560); ball = { x: bx, y: H - 40, vx: dx / d * sp, vy: dy / d * sp }; }
}
function knock() {
  const hit = []; for (const p of pins) if (p.up && Math.hypot(p.x - ball.x, p.y - ball.y) < 15) { p.up = false; hit.push(p); }
  for (let i = 0; i < hit.length; i++) for (const p of pins) if (p.up && Math.hypot(p.x - hit[i].x, p.y - hit[i].y) < 31 && Math.random() < .55) { p.up = false; hit.push(p); }
}
function settle() {
  const now = pins.filter(p => p.up).length, down = standing - now; standing = now; addScore(down);
  if (throwNo === 1 && now === 0) { addScore(10); return nextFrame(); } if (throwNo === 1) { throwNo = 2; return; } if (now === 0) addScore(5); nextFrame();
}
function nextFrame() { fr++; throwNo = 1; if (fr > 5) return end(); rack(); setInfo(fr + "/5"); }
function update(dt) {
  if (ball) { ball.x += ball.vx * dt; ball.y += ball.vy * dt; if (ball.x < 22 || ball.x > W - 22) { ball = null; wait = .7; return; } knock(); if (ball.y < 40) { ball = null; wait = .7; } }
  else if (wait > 0) { wait -= dt; if (wait <= 0) settle(); }
}
function draw(c) {
  c.fillStyle = "rgba(200,160,90,.35)"; c.fillRect(22, 0, W - 44, H); c.font = "20px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle";
  for (const p of pins) { c.globalAlpha = p.up ? 1 : .15; c.fillText("🎳", p.x, p.y); } c.globalAlpha = 1;
  if (aim) { c.strokeStyle = C.accent; c.lineWidth = 3; c.setLineDash([6, 6]); c.beginPath(); c.moveTo(bx, H - 40); c.lineTo(bx + (aim.x - aim.sx), H - 40 + (aim.y - aim.sy)); c.stroke(); c.setLineDash([]); }
  if (!ball && wait <= 0) { c.fillStyle = C.fg; c.beginPath(); c.arc(bx, H - 40, 12, 0, 7); c.fill(); } if (ball) { c.fillStyle = C.fg; c.beginPath(); c.arc(ball.x, ball.y, 11, 0, 7); c.fill(); }
}
''')

# 2. 농구 슛
make(H+"basketball-shoot.html", "농구 슛", "🏀", 25, "basketball-best-v1", 300, 400, "남은 공", "타이밍을 맞춰 골을 넣으세요",
 "아래 <b>게이지가 왔다 갔다</b> 해요. 초록 구간에서 화면을 눌러 슛을 던지세요! 연속으로 넣으면 보너스 점수. 공은 10개이고, 골대 거리가 매번 달라져요.",
 r'''
let balls, meter, mdir, zone, ball, hoopX, wait, streak, msg, msgT;
function reset() { balls = 10; meter = 0; mdir = 1; streak = 0; ball = null; wait = 0; msg = ""; msgT = 0; newShot(); setInfo(balls); }
function newShot() { hoopX = rand(170, 260); const c = clamp((hoopX - 150) / 120, 0, 1); zone = [.25 + c * .45 - .06 - (score > 15 ? .02 : 0), .25 + c * .45 + .06 + (score > 15 ? 0 : .02)]; }
function pointer(t) { if (t === "down") shoot(); }
function key(t, k) { if (k === "space" || k === "u") shoot(); }
function shoot() {
  if (ball || wait > 0 || balls <= 0) return; const ok = meter >= zone[0] && meter <= zone[1], err = meter < zone[0] ? meter - zone[0] : meter - zone[1];
  balls--; setInfo(balls); const endX = ok ? hoopX : hoopX + (err * 260), endY = 120; ball = { t: 0, ok, sx: 50, sy: H - 40, ex: endX, ey: endY, hx: hoopX };
}
function update(dt) {
  if (!ball) { meter += mdir * dt * (1.1 + score * .01); if (meter > 1) { meter = 1; mdir = -1; } if (meter < 0) { meter = 0; mdir = 1; } }
  if (ball) { ball.t += dt / .9; if (ball.t >= 1) { if (ball.ok) { streak++; addScore(2 + Math.min(streak, 5)); msg = "골인! 🎉"; } else { streak = 0; msg = "아쉬워요"; } msgT = .8; ball = null; wait = .6; } }
  else if (wait > 0) { wait -= dt; if (wait <= 0) { if (balls <= 0) return end(); newShot(); } } msgT = Math.max(0, msgT - dt);
}
function draw(c) {
  c.font = "34px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillStyle = C.muted; c.fillRect(hoopX - 22, 112, 44, 6); c.fillRect(hoopX + 22, 80, 5, 44); c.fillText("🧑", 50, H - 30);
  const b = ball; if (b) { const x = b.sx + (b.ex - b.sx) * b.t, y = b.sy + (b.ey - b.sy) * b.t - Math.sin(b.t * Math.PI) * 130; c.fillText("🏀", x, y); } else c.fillText("🏀", 70, H - 50);
  c.fillStyle = C.line; c.fillRect(30, H - 14, W - 60, 10); c.fillStyle = C.ok; c.fillRect(30 + zone[0] * (W - 60), H - 14, (zone[1] - zone[0]) * (W - 60), 10); c.fillStyle = C.fg; c.fillRect(30 + meter * (W - 60) - 3, H - 20, 6, 22);
  if (msgT > 0) { c.font = "700 22px sans-serif"; c.fillStyle = C.fg; c.fillText(msg, W / 2, 190); }
}
''')

# 3. 양궁
make(H+"archery.html", "양궁", "🏹", 120, "archery-best-v1", 300, 400, "남은 화살", "과녁 한가운데를 맞히세요",
 "<b>흔들리는 조준점</b>이 과녁 가운데에 올 때 화면을 눌러 화살을 쏘세요! 가운데에 가까울수록 높은 점수예요. 화살은 10개이고, 갈수록 바람이 세져서 더 많이 흔들려요.",
 r'''
let arrows, t, shots, flash;
const CX = W / 2, CY = 180, R = 120;
function reset() { arrows = 10; t = 0; shots = []; flash = 0; setInfo(arrows); }
function aimPos() { const k = 1 + (10 - arrows) * .12, a = 62 + (10 - arrows) * 4; return [CX + Math.sin(t * 1.9 * k) * a + Math.sin(t * 3.1) * 12, CY + Math.cos(t * 1.4 * k) * a * .8 + Math.sin(t * 2.3) * 10]; }
function pointer(tp) { if (tp === "down") fire(); }
function key(tp, k) { if (k === "space") fire(); }
function fire() { if (arrows <= 0) return; const [x, y] = aimPos(), d = Math.hypot(x - CX, y - CY), pts = d > R ? 0 : Math.max(1, 10 - Math.floor(d / (R / 10))); shots.push({ x, y, pts }); addScore(pts); arrows--; setInfo(arrows); flash = .35; if (arrows <= 0) setTimeout(() => { if (state === "play") end(); }, 800); }
function update(dt) { t += dt; flash = Math.max(0, flash - dt); }
function draw(c) {
  const cols = ["#fff", "#fff", "#222", "#222", "#3b8fe0", "#3b8fe0", "#e04a3b", "#e04a3b", "#f2c230", "#f2c230"];
  for (let k = 0; k < 10; k++) { c.fillStyle = cols[k]; c.beginPath(); c.arc(CX, CY, R - k * (R / 10), 0, 7); c.fill(); }
  c.strokeStyle = "rgba(0,0,0,.25)"; c.lineWidth = 1; for (let k = 1; k < 10; k++) { c.beginPath(); c.arc(CX, CY, R - k * (R / 10), 0, 7); c.stroke(); }
  c.font = "18px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; for (const s of shots) c.fillText("📍", s.x, s.y);
  if (arrows > 0) { const [x, y] = aimPos(); c.strokeStyle = C.fg; c.lineWidth = 2; c.beginPath(); c.arc(x, y, 14, 0, 7); c.moveTo(x - 20, y); c.lineTo(x + 20, y); c.moveTo(x, y - 20); c.lineTo(x, y + 20); c.stroke(); }
  c.font = "700 20px sans-serif"; c.fillStyle = C.fg; if (shots.length) c.fillText("마지막 " + shots[shots.length - 1].pts + "점", W / 2, H - 40);
}
''')

# 4. 승부차기
make(H+"penalty-kick.html", "승부차기", "⚽", 135, "penalty-best-v1", 300, 400, "남은 킥", "골키퍼를 속이고 골을 넣으세요",
 "골대 안쪽 <b>원하는 곳을 눌러서</b> 공을 차세요! 골키퍼는 한쪽으로 몸을 날려요. 구석을 노릴수록 막기 어렵지만 너무 구석이면 골대를 벗어나요. 10번 차서 몇 골을 넣을 수 있을까요?",
 r'''
let kicks, ball, keeper, wait, msg, msgT;
const GL = 40, GR = W - 40, GT = 70, GB = 200;
function reset() { kicks = 10; ball = null; keeper = { x: W / 2, tx: W / 2 }; wait = 0; msg = ""; msgT = 0; setInfo(kicks); }
function pointer(t, x, y) { if (t !== "down" || ball || wait > 0 || kicks <= 0) return; if (y > GB + 40 || y < GT - 40) return; const tx = clamp(x, GL - 10, GR + 10), ty = clamp(y, GT - 10, GB + 8); kicks--; setInfo(kicks); const side = Math.random(), dive = score > 4 ? (Math.random() < .55 ? tx + rand(-40, 40) : rand(GL, GR)) : rand(GL + 10, GR - 10); keeper.tx = clamp(dive, GL + 20, GR - 20); ball = { t: 0, tx, ty, x: W / 2, y: H - 50 }; }
function update(dt) {
  if (ball) { ball.t += dt / .55; keeper.x += (keeper.tx - keeper.x) * Math.min(1, dt * 7); const k = Math.min(1, ball.t); ball.x = W / 2 + (ball.tx - W / 2) * k; ball.y = H - 50 + (ball.ty - (H - 50)) * k;
    if (ball.t >= 1) { const out = ball.tx < GL || ball.tx > GR || ball.ty < GT || ball.ty > GB, saved = Math.abs(ball.tx - keeper.x) < 34 && ball.ty > GT - 10; if (out) msg = "골대를 벗어났어요!"; else if (saved) msg = "막혔어요! 🧤"; else { msg = "골인! ⚽🎉"; addScore(1); } msgT = 1; ball = null; wait = .9; } }
  else if (wait > 0) { wait -= dt; keeper.x += (W / 2 - keeper.x) * Math.min(1, dt * 4); if (wait <= 0) { if (kicks <= 0) return end(); } } msgT = Math.max(0, msgT - dt);
}
function draw(c) {
  c.strokeStyle = C.fg; c.lineWidth = 5; c.strokeRect(GL, GT, GR - GL, GB - GT); c.strokeStyle = C.line; c.lineWidth = 1; for (let x = GL; x <= GR; x += 16) { c.beginPath(); c.moveTo(x, GT); c.lineTo(x, GB); c.stroke(); } for (let y = GT; y <= GB; y += 16) { c.beginPath(); c.moveTo(GL, y); c.lineTo(GR, y); c.stroke(); }
  c.font = "42px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("🧤", keeper.x, GB - 28); c.font = ball ? "26px sans-serif" : "30px sans-serif"; c.fillText("⚽", ball ? ball.x : W / 2, ball ? ball.y : H - 50);
  if (msgT > 0) { c.font = "700 20px sans-serif"; c.fillStyle = C.fg; c.fillText(msg, W / 2, 255); }
}
''')

# 5. 미니 골프
make(H+"mini-golf.html", "미니 골프", "⛳", 100, "minigolf-best-v1", 300, 440, "타수", "공을 구멍에 넣으세요",
 "공 근처를 <b>누르고 뒤로 끌었다가 놓으면</b> 반대 방향으로 공이 굴러가요. 끌수록 세게 쳐요. 벽에 튕기니까 잘 계산해서 구멍(⛳)에 넣으세요. 적은 타수로 넣을수록 점수가 높아요. 모두 5개 홀!",
 r'''
const HOLES = [
 { s: [150, 380], h: [150, 70], w: [] },
 { s: [60, 380], h: [240, 70], w: [[100, 200, 100, 20]] },
 { s: [150, 380], h: [150, 60], w: [[40, 230, 120, 20], [140, 150, 120, 20]] },
 { s: [40, 390], h: [260, 60], w: [[110, 90, 20, 200], [190, 160, 20, 200]] },
 { s: [150, 390], h: [150, 50], w: [[60, 280, 60, 18], [180, 280, 60, 18], [110, 180, 80, 18], [40, 100, 90, 18], [170, 100, 90, 18]] }];
let hole, ball, strokes, aim, sunk, wait;
function load(i) { hole = i; const H0 = HOLES[i]; ball = { x: H0.s[0], y: H0.s[1], vx: 0, vy: 0 }; strokes = 0; sunk = false; wait = 0; setInfo((i + 1) + "홀 · 0타"); }
function reset() { aim = null; load(0); }
function pointer(t, x, y) { if (sunk || Math.hypot(ball.vx, ball.vy) > 0) return; if (t === "down" && Math.hypot(x - ball.x, y - ball.y) < 60) aim = { x, y }; else if (t === "move" && aim) { aim.x = x; aim.y = y; } else if (t === "up" && aim) { const dx = ball.x - aim.x, dy = ball.y - aim.y, d = Math.min(Math.hypot(dx, dy), 120); aim = null; if (d < 8) return; const sp = d * 4.2; ball.vx = dx / Math.hypot(dx, dy) * sp; ball.vy = dy / Math.hypot(dx, dy) * sp; strokes++; setInfo((hole + 1) + "홀 · " + strokes + "타"); } }
function update(dt) {
  const HO = HOLES[hole]; if (sunk) { wait -= dt; if (wait <= 0) { if (hole >= HOLES.length - 1) end(); else load(hole + 1); } return; }
  const steps = 3; for (let s = 0; s < steps; s++) { ball.x += ball.vx * dt / steps; ball.y += ball.vy * dt / steps;
    if (ball.x < 10) { ball.x = 10; ball.vx = Math.abs(ball.vx) * .8; } if (ball.x > W - 10) { ball.x = W - 10; ball.vx = -Math.abs(ball.vx) * .8; } if (ball.y < 10) { ball.y = 10; ball.vy = Math.abs(ball.vy) * .8; } if (ball.y > H - 10) { ball.y = H - 10; ball.vy = -Math.abs(ball.vy) * .8; }
    for (const [x, y, w, h] of HO.w) { const cx = clamp(ball.x, x, x + w), cy = clamp(ball.y, y, y + h), dx = ball.x - cx, dy = ball.y - cy; if (dx * dx + dy * dy < 49) { if (Math.abs(dx) > Math.abs(dy)) { ball.vx = (dx > 0 ? 1 : -1) * Math.abs(ball.vx) * .85; ball.x = cx + (dx > 0 ? 8 : -8); } else { ball.vy = (dy > 0 ? 1 : -1) * Math.abs(ball.vy) * .85; ball.y = cy + (dy > 0 ? 8 : -8); } } } }
  const f = Math.pow(.35, dt); ball.vx *= f; ball.vy *= f; if (Math.hypot(ball.vx, ball.vy) < 3) { ball.vx = ball.vy = 0; }
  if (Math.hypot(ball.x - HO.h[0], ball.y - HO.h[1]) < 12 && Math.hypot(ball.vx, ball.vy) < 260) { sunk = true; wait = .8; addScore(Math.max(1, 7 - strokes) * 10); ball.vx = ball.vy = 0; ball.x = HO.h[0]; ball.y = HO.h[1]; }
  else if (strokes >= 9 && !Math.hypot(ball.vx, ball.vy)) { sunk = true; wait = .8; }
}
function draw(c) {
  const HO = HOLES[hole]; c.fillStyle = "rgba(60,160,80,.3)"; c.fillRect(0, 0, W, H); c.fillStyle = C.fg; for (const [x, y, w, h] of HO.w) c.fillRect(x, y, w, h);
  c.fillStyle = "#111"; c.beginPath(); c.arc(HO.h[0], HO.h[1], 11, 0, 7); c.fill(); c.font = "22px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("⛳", HO.h[0] + 2, HO.h[1] - 14);
  if (aim) { c.strokeStyle = C.accent; c.lineWidth = 3; c.beginPath(); c.moveTo(ball.x, ball.y); c.lineTo(ball.x + (ball.x - aim.x), ball.y + (ball.y - aim.y)); c.stroke(); }
  c.fillStyle = "#fff"; c.strokeStyle = "#555"; c.lineWidth = 2; c.beginPath(); c.arc(ball.x, ball.y, 7, 0, 7); c.fill(); c.stroke();
}
''')

# 6. 구슬 떨어뜨리기
make(H+"plinko.html", "구슬 떨어뜨리기", "🔮", 285, "plinko-best-v1", 300, 440, "남은 구슬", "높은 점수 칸에 구슬을 넣으세요",
 "위쪽에서 <b>구슬을 떨어뜨릴 위치를 눌러</b> 보세요. 못에 튕기면서 내려와 아래 칸에 들어가요. 가운데는 낮은 점수, 양쪽 끝은 높은 점수! 구슬은 10개예요.",
 r'''
let pegs, balls, left, bins;
const BV = [50, 20, 10, 5, 2, 5, 10, 20, 50];
function reset() { pegs = []; for (let r = 0; r < 9; r++) { const n = r % 2 ? 8 : 9; for (let c = 0; c < n; c++) pegs.push({ x: (r % 2 ? 33.3 : 16.7) + c * 33.3, y: 90 + r * 32 }); } balls = []; left = 10; bins = []; setInfo(left); }
function pointer(t, x) { if (t !== "down" || left <= 0 || balls.some(b => b.alive && b.y < 70)) return; left--; setInfo(left); balls.push({ x: clamp(x, 14, W - 14), y: 40, vx: rand(-8, 8), vy: 0, alive: true }); }
function update(dt) {
  for (const b of balls) { if (!b.alive) continue; b.vy += 700 * dt; b.x += b.vx * dt; b.y += b.vy * dt; b.st = Math.abs(b.vy) < 25 ? (b.st || 0) + dt : 0; if (b.st > .35) { b.vy = -120; b.vx = rand(-90, 90); b.st = 0; } if (b.x < 8) { b.x = 8; b.vx = Math.abs(b.vx) * .6; } if (b.x > W - 8) { b.x = W - 8; b.vx = -Math.abs(b.vx) * .6; }
    for (const p of pegs) { const dx = b.x - p.x, dy = b.y - p.y, d = Math.hypot(dx, dy); if (d < 11) { const nx = dx / (d || 1), ny = dy / (d || 1), dot = b.vx * nx + b.vy * ny; b.vx = (b.vx - 1.6 * dot * nx) * .8 + rand(-12, 12); b.vy = (b.vy - 1.6 * dot * ny) * .8; b.x = p.x + nx * 11.5; b.y = p.y + ny * 11.5; } }
    if (b.y > H - 40) { b.alive = false; const k = clamp(Math.floor(b.x / (W / 9)), 0, 8); addScore(BV[k]); bins.push({ k, t: .6 }); } }
  bins.forEach(q => { q.t -= dt; }); bins = bins.filter(q => q.t > 0); balls = balls.filter(b => b.alive);
  if (left <= 0 && !balls.length) end();
}
function draw(c) {
  c.fillStyle = C.fg; for (const p of pegs) { c.beginPath(); c.arc(p.x, p.y, 4, 0, 7); c.fill(); }
  const bw = W / 9; c.font = "700 14px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; for (let k = 0; k < 9; k++) { const hit = bins.some(q => q.k === k); c.fillStyle = hit ? C.accent : C.line; c.fillRect(k * bw + 2, H - 36, bw - 4, 34); c.fillStyle = hit ? "#fff" : C.fg; c.fillText(BV[k], k * bw + bw / 2, H - 19); }
  c.fillStyle = C.accent; for (const b of balls) { c.beginPath(); c.arc(b.x, b.y, 7, 0, 7); c.fill(); } c.fillStyle = C.muted; c.fillRect(0, 56, W, 3); c.font = "13px sans-serif"; c.fillStyle = C.muted; c.fillText("▼ 여기를 눌러 구슬을 떨어뜨려요", W / 2, 30);
}
''')

# 7. 에어하키
make(H+"air-hockey.html", "에어하키", "🏒", 195, "airhockey-best-v1", 300, 440, "내 골 : 컴퓨터", "컴퓨터보다 먼저 5골을 넣으세요",
 "<b>손가락으로 아래쪽 판</b>에서 내 채를 움직여 퍽을 쳐서 위쪽 골대에 넣으세요. 컴퓨터가 5골을 먼저 넣으면 끝나요. 이길 때마다 컴퓨터가 더 빨라져요!",
 r'''
let puck, me, cpu, my, cp, level, wait;
function reset() { my = 0; cp = 0; level = 1; wait = 0; me = { x: W / 2, y: H - 70, px: W / 2, py: H - 70 }; cpu = { x: W / 2, y: 70 }; serve(1); setInfo("0 : 0"); }
function serve(d) { puck = { x: W / 2, y: H / 2, vx: rand(-60, 60), vy: d * 120 }; wait = .6; }
function pointer(t, x, y) { me.px = clamp(x, 26, W - 26); me.py = clamp(y, H / 2 + 26, H - 26); }
function update(dt) {
  me.x += (me.px - me.x) * Math.min(1, dt * 22); me.y += (me.py - me.y) * Math.min(1, dt * 22); me.x = clamp(me.x + (keys.r - keys.l) * 260 * dt, 26, W - 26); me.y = clamp(me.y + (keys.d - keys.u) * 260 * dt, H / 2 + 26, H - 26);
  if (wait > 0) { wait -= dt; return; }
  const sp = 90 + level * 28; let tx, ty;
  if (puck.y < cpu.y - 4 && puck.y < H / 2) { tx = puck.x < W / 2 ? puck.x + 45 : puck.x - 45; ty = Math.min(H / 2 - 30, cpu.y + 40); }      // 퍽이 뒤에 있으면 돌아서 간다
  else if (puck.y < H / 2 && puck.vy < 60) { tx = puck.x; ty = clamp(puck.y - 30, 40, H / 2 - 30); } else { tx = W / 2; ty = 70; }
  const nearWall = puck.y < 22 || puck.y > H - 22 || puck.x < 22 || puck.x > W - 22; puck.wt = nearWall ? (puck.wt || 0) + dt : 0; if (puck.wt > 1.2) { serve(puck.y < H / 2 ? 1 : -1); return; }
  cpu.x += clamp(tx - cpu.x, -sp * dt, sp * dt); cpu.y += clamp(ty - cpu.y, -sp * .7 * dt, sp * .7 * dt); cpu.x = clamp(cpu.x, 26, W - 26);
  puck.x += puck.vx * dt; puck.y += puck.vy * dt; puck.vx *= 1 - .25 * dt; puck.vy *= 1 - .25 * dt;
  if (puck.x < 10) { puck.x = 10; puck.vx = Math.abs(puck.vx); } if (puck.x > W - 10) { puck.x = W - 10; puck.vx = -Math.abs(puck.vx); }
  for (const p of [me, cpu]) { const dx = puck.x - p.x, dy = puck.y - p.y, d = Math.hypot(dx, dy); if (d < 36) { const nx = dx / (d || 1), ny = dy / (d || 1), v = Math.hypot(puck.vx, puck.vy), nv = clamp(Math.max(v, 150) + 140, 160, 560); puck.vx = nx * nv; puck.vy = ny * nv; puck.x = p.x + nx * 37; puck.y = p.y + ny * 37; } }
  const gx = puck.x > W / 2 - 50 && puck.x < W / 2 + 50;
  if (puck.y < 6) { if (gx) { my++; level++; addScore(1); setInfo(my + " : " + cp); serve(1); } else { puck.y = 6; puck.vy = Math.abs(puck.vy); } }
  if (puck.y > H - 6) { if (gx) { cp++; setInfo(my + " : " + cp); if (cp >= 5) return end(); serve(-1); } else { puck.y = H - 6; puck.vy = -Math.abs(puck.vy); } }
}
function draw(c) {
  c.strokeStyle = C.line; c.lineWidth = 3; c.beginPath(); c.moveTo(0, H / 2); c.lineTo(W, H / 2); c.stroke(); c.beginPath(); c.arc(W / 2, H / 2, 40, 0, 7); c.stroke(); c.fillStyle = C.fg; c.fillRect(W / 2 - 50, 0, 100, 5); c.fillRect(W / 2 - 50, H - 5, 100, 5);
  c.fillStyle = C.bad; c.beginPath(); c.arc(cpu.x, cpu.y, 24, 0, 7); c.fill(); c.fillStyle = C.ok; c.beginPath(); c.arc(me.x, me.y, 24, 0, 7); c.fill(); c.fillStyle = "#222"; c.beginPath(); c.arc(puck.x, puck.y, 12, 0, 7); c.fill();
}
''')
