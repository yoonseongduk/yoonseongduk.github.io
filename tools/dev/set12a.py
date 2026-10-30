import sys
sys.path.insert(0, ".")
from mkarcade import make
H = "out/"

# 1. 코인 먹기
make(H+"coin-chase.html", "코인 먹기", "🪙", 48, "coinchase-best-v1", 300, 400, "목숨", "코인을 모으고 유령을 피하세요",
 "화면을 <b>손가락으로 눌러 끌면</b> 캐릭터가 그쪽으로 움직여요. 🪙 코인을 모으고 쫓아오는 👻 유령에게 닿지 않게 피하세요. 코인을 먹을 때마다 유령이 하나씩 늘어나요!",
 r'''
let me, tgt, coin, ghosts, lives, inv;
function reset() { me = { x: W / 2, y: H / 2 }; tgt = { x: W / 2, y: H / 2 }; ghosts = [{ x: 30, y: 30, sp: 50 }]; lives = 3; inv = 0; newCoin(); setInfo("❤️" + lives); }
function newCoin() { do { coin = { x: rand(24, W - 24), y: rand(24, H - 24) }; } while (Math.hypot(coin.x - me.x, coin.y - me.y) < 80); }
function pointer(t, x, y) { if (t === "up") return; tgt = { x: clamp(x, 12, W - 12), y: clamp(y, 12, H - 12) }; }
function update(dt) {
  tgt.x = clamp(tgt.x + (keys.r - keys.l) * 220 * dt, 12, W - 12); tgt.y = clamp(tgt.y + (keys.d - keys.u) * 220 * dt, 12, H - 12);
  const dx = tgt.x - me.x, dy = tgt.y - me.y, d = Math.hypot(dx, dy) || 1, sp = Math.min(d, 175 * dt); me.x += dx / d * sp; me.y += dy / d * sp; inv = Math.max(0, inv - dt);
  if (Math.hypot(coin.x - me.x, coin.y - me.y) < 22) { addScore(1); newCoin(); if (ghosts.length < 7) { const a = Math.random() < .5; ghosts.push({ x: a ? 10 : W - 10, y: Math.random() < .5 ? 10 : H - 10, sp: 48 + score * 1.5 }); } ghosts.forEach(g => { g.sp = Math.min(105, g.sp + 2); }); }
  for (const g of ghosts) { const gx = me.x - g.x, gy = me.y - g.y, gd = Math.hypot(gx, gy) || 1; g.x += gx / gd * g.sp * dt; g.y += gy / gd * g.sp * dt; if (!inv && gd < 20) { lives--; inv = 1.5; setInfo("❤️" + Math.max(0, lives)); ghosts.forEach((q, k) => { q.x = k % 2 ? W - 10 : 10; q.y = k < 2 ? 10 : H - 10; }); if (lives <= 0) end(); } }
}
function draw(c) {
  c.font = "22px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("🪙", coin.x, coin.y); for (const g of ghosts) c.fillText("👻", g.x, g.y);
  c.globalAlpha = inv > 0 && Math.floor(inv * 10) % 2 ? .4 : 1; c.fillText("😀", me.x, me.y); c.globalAlpha = 1;
}
''')

# 2. 낚시
make(H+"fishing.html", "낚시 게임", "🎣", 205, "fishing-best-v1", 300, 420, "남은 시간", "45초 동안 물고기를 낚으세요",
 "화면을 <b>누르고 있으면 낚싯줄이 내려가고</b>, 손을 떼면 올라와요. 물고기에 닿으면 걸려 올라오고, 배까지 끌어올리면 점수! 깊은 곳 물고기일수록 점수가 높아요. 🪼 해파리는 피하세요!",
 r'''
let hook, fish, t, left, caught, spawnT, shake;
function reset() { hook = { x: W / 2, y: 70, down: false }; fish = []; t = 0; left = 45; caught = null; spawnT = 0; shake = 0; setInfo(45); for (let k = 0; k < 5; k++) spawn(true); }
function spawn(init) { const jelly = Math.random() < .16, lane = ri(0, 4), y = 120 + lane * 58, dir = Math.random() < .5 ? 1 : -1, e = jelly ? "🪼" : ["🐟", "🐠", "🐡", "🦑", "🐙"][lane]; fish.push({ x: init ? rand(20, W - 20) : (dir > 0 ? -20 : W + 20), y, dir, vx: rand(30, 70) * dir, e, jelly, pts: jelly ? 0 : lane + 1 }); }
function pointer(type, x) { if (type === "down") hook.down = true; if (type === "up") hook.down = false; if (type !== "up") hook.x = clamp(x, 14, W - 14); }
function key(type, k) { if (k === "space") hook.down = !hook.down; }
function update(dt) {
  t += dt; left -= dt; setInfo(Math.max(0, Math.ceil(left))); if (left <= 0) return end(); hook.x = clamp(hook.x + (keys.r - keys.l) * 160 * dt, 14, W - 14);
  if (keys.d) hook.down = true; spawnT -= dt; if (spawnT <= 0 && fish.length < 9) { spawn(false); spawnT = rand(.6, 1.4); }
  hook.y += (hook.down && !caught ? 150 : -190) * dt; hook.y = clamp(hook.y, 70, H - 20);
  if (caught) { caught.x = hook.x; caught.y = hook.y + 12; if (hook.y <= 72) { addScore(caught.pts * 2); fish.splice(fish.indexOf(caught), 1); caught = null; shake = .2; } }
  for (const f of fish) { if (f === caught) continue; f.x += f.vx * dt; }
  fish = fish.filter(f => f === caught || (f.x > -40 && f.x < W + 40));
  if (!caught && hook.down) for (const f of fish) if (Math.hypot(f.x - hook.x, f.y - (hook.y + 8)) < 20) { if (f.jelly) { left = Math.max(0, left - 4); fish.splice(fish.indexOf(f), 1); hook.down = false; } else { caught = f; hook.down = false; } break; }
}
function draw(c) {
  c.fillStyle = "rgba(60,150,220,.28)"; c.fillRect(0, 90, W, H - 90); c.font = "26px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("⛵", W / 2, 55);
  c.strokeStyle = C.fg; c.lineWidth = 1.5; c.beginPath(); c.moveTo(hook.x, 72); c.lineTo(hook.x, hook.y); c.stroke(); c.fillText("🪝", hook.x, hook.y + 8);
  for (const f of fish) { c.save(); c.translate(f.x, f.y); if (f.vx > 0 && !f.jelly) c.scale(-1, 1); c.fillText(f.e, 0, 0); c.restore(); }
}
''')

# 3. 자동차 피하기
make(H+"car-dodge.html", "자동차 피하기", "🚗", 0, "cardodge-best-v1", 300, 440, "속도", "달려오는 차를 피해 오래 달리세요",
 "화면의 <b>왼쪽을 누르면 왼쪽 차선으로, 오른쪽을 누르면 오른쪽 차선으로</b> 움직여요. 3개 차선에서 달려오는 차들을 피하세요. 시간이 갈수록 빨라져요! 🛢️ 기름통을 모으면 보너스 점수예요.",
 r'''
const LANE = [60, 150, 240];
let lane, y, cars, spd, spawnT, dist, roadOff;
function reset() { lane = 1; cars = []; spd = 190; spawnT = 0; dist = 0; roadOff = 0; setInfo("1"); }
function pointer(t, x) { if (t === "down") move(x < W / 2 ? -1 : 1); }
function key(t, k) { if (k === "l") move(-1); if (k === "r") move(1); }
const move = d => { lane = clamp(lane + d, 0, 2); };
function update(dt) {
  dist += spd * dt; spd = Math.min(520, spd + dt * 7); roadOff = (roadOff + spd * dt) % 40; setScore(Math.floor(dist / 25)); setInfo(Math.round(spd / 100 * 10) / 10 + "x");
  spawnT -= dt; if (spawnT <= 0) { spawnT = rand(.45, .95) * (200 / spd) * 1.7; const free = ri(0, 2), n = Math.random() < .35 ? 2 : 1, ls = [0, 1, 2].filter(l => l !== free); shuf3(ls).slice(0, n).forEach(l => cars.push({ l, y: -50 })); if (Math.random() < .25) cars.push({ l: free, y: -50, oil: true }); }
  for (const c of cars) c.y += (spd - (c.oil ? 0 : 60)) * dt;
  for (const c of cars) if (!c.done && c.l === lane && Math.abs(c.y - (H - 80)) < 34) { if (c.oil) { c.done = true; addScore(20); } else end(); }
  cars = cars.filter(c => c.y < H + 40 && !c.done);
}
const shuf3 = a => a.sort(() => Math.random() - .5);
function draw(c) {
  c.fillStyle = "#555"; c.fillRect(20, 0, W - 40, H); c.strokeStyle = "#fff"; c.lineWidth = 3; c.setLineDash([22, 18]); c.lineDashOffset = -roadOff; for (const x of [105, 195]) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); } c.setLineDash([]);
  c.font = "34px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; for (const k of cars) { c.save(); c.translate(LANE[k.l], k.y); if (!k.oil) c.rotate(Math.PI / 2 * 0); c.fillText(k.oil ? "🛢️" : "🚙", 0, 0); c.restore(); } c.fillText("🏎️", LANE[lane], H - 80);
}
''')

# 4. 스페이스 인베이더
make(H+"space-invaders.html", "우주 침략자", "👽", 285, "invaders-best-v1", 300, 440, "목숨", "외계인을 모두 물리치세요",
 "<b>손가락을 좌우로 끌어서</b> 우주선을 움직이세요. 총알은 자동으로 발사돼요! 외계인이 아래까지 내려오거나 총알에 3번 맞으면 끝이에요. 모두 물리치면 더 빠른 다음 단계가 시작돼요.",
 r'''
let px, bullets, aliens, ebul, dir, lives, wave, shotT, inv, stepT;
function reset() { px = W / 2; bullets = []; ebul = []; lives = 3; wave = 1; shotT = 0; inv = 0; spawnWave(); setInfo("❤️" + lives); }
function spawnWave() { aliens = []; dir = 1; for (let r = 0; r < 4; r++) for (let c = 0; c < 7; c++) aliens.push({ x: 40 + c * 36, y: 50 + r * 30, e: ["👾", "👽", "🛸", "🤖"][r], alive: true }); stepT = 0; }
function pointer(t, x) { px = clamp(x, 16, W - 16); }
function update(dt) {
  px = clamp(px + (keys.r - keys.l) * 240 * dt, 16, W - 16); shotT -= dt; inv = Math.max(0, inv - dt); if (shotT <= 0) { bullets.push({ x: px, y: H - 50 }); shotT = .34; }
  for (const b of bullets) b.y -= 380 * dt; bullets = bullets.filter(b => b.y > -10);
  const alive = aliens.filter(a => a.alive), spd = 22 + wave * 7 + (28 - alive.length) * 2.4; let edge = false;
  for (const a of alive) { a.x += dir * spd * dt; if (a.x < 14 || a.x > W - 14) edge = true; }
  if (edge) { dir = -dir; for (const a of alive) { a.y += 14; a.x = clamp(a.x, 14, W - 14); } }
  for (const b of bullets) for (const a of alive) if (a.alive && b.y > 0 && Math.abs(a.x - b.x) < 14 && Math.abs(a.y - b.y) < 14) { a.alive = false; b.y = -99; addScore(10); }
  if (alive.length && Math.random() < dt * (0.8 + wave * .25)) { const s = alive[ri(0, alive.length - 1)]; ebul.push({ x: s.x, y: s.y + 10 }); }
  for (const e of ebul) e.y += 170 * dt; ebul = ebul.filter(e => e.y < H + 10);
  for (const e of ebul) if (!inv && Math.abs(e.x - px) < 15 && Math.abs(e.y - (H - 36)) < 14) { e.y = H + 99; lives--; inv = 1.2; setInfo("❤️" + Math.max(0, lives)); if (lives <= 0) return end(); }
  if (alive.some(a => a.y > H - 70)) return end(); if (!alive.length) { wave++; addScore(50); spawnWave(); }
}
function draw(c) {
  c.font = "22px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; for (const a of aliens) if (a.alive) c.fillText(a.e, a.x, a.y);
  c.fillStyle = C.accent; for (const b of bullets) c.fillRect(b.x - 2, b.y - 7, 4, 12); c.fillStyle = C.bad; for (const e of ebul) c.fillRect(e.x - 2, e.y - 6, 4, 12);
  c.globalAlpha = inv > 0 && Math.floor(inv * 10) % 2 ? .4 : 1; c.font = "28px sans-serif"; c.fillText("🚀", px, H - 36); c.globalAlpha = 1;
}
''')

# 5. 동굴 비행
make(H+"cave-flyer.html", "동굴 비행", "🚁", 160, "caveflyer-best-v1", 300, 420, "거리", "벽에 닿지 않고 멀리 날아가세요",
 "화면을 <b>누르고 있으면 위로 올라가고</b>, 떼면 아래로 내려가요. 위아래 벽에 닿지 않게 동굴을 지나가세요. 점점 빨라지고 길이 좁아져요!",
 r'''
let hy, vy, hold, cols, off, spd, gap, mid, dist;
const CW = 10;
function reset() { hy = H / 2; vy = 0; hold = false; spd = 120; gap = 190; mid = H / 2; dist = 0; off = 0; cols = []; for (let k = 0; k < W / CW + 3; k++) addCol(); setInfo("0m"); }
function addCol() { mid = clamp(mid + rand(-9, 9), gap / 2 + 14, H - gap / 2 - 14); cols.push(mid); }
function pointer(t) { if (t === "down") hold = true; if (t === "up") hold = false; }
function key(t, k) { if (k === "u" || k === "space") hold = true; }
function update(dt) {
  vy += ((hold || keys.u) ? -520 : 480) * dt; vy = clamp(vy, -230, 230); hy += vy * dt;
  spd = Math.min(260, spd + dt * 5); gap = Math.max(110, gap - dt * 2.2); off += spd * dt; dist += spd * dt; while (off >= CW) { off -= CW; cols.shift(); addCol(); }
  setScore(Math.floor(dist / 10)); setInfo(Math.floor(dist / 10) + "m");
  const idx = Math.floor((60 + off) / CW), m = cols[idx] || H / 2; if (hy < m - gap / 2 + 8 || hy > m + gap / 2 - 8) end();
}
function draw(c) {
  c.fillStyle = C.muted; for (let k = 0; k < cols.length; k++) { const x = k * CW - off; c.fillRect(x, 0, CW + 1, cols[k] - gap / 2); c.fillRect(x, cols[k] + gap / 2, CW + 1, H); }
  c.font = "28px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.save(); c.translate(60, hy); c.rotate(vy / 700); c.fillText("🚁", 0, 0); c.restore();
}
''')

# 6. 중력 뒤집기
make(H+"gravity-flip.html", "중력 뒤집기", "🔄", 262, "gravityflip-best-v1", 300, 380, "속도", "중력을 뒤집어 장애물을 피하세요",
 "화면을 <b>누르면 중력이 뒤집혀서</b> 바닥↔천장으로 이동해요. 땅과 천장에 나타나는 가시를 피해 계속 달리세요! 가시가 있는 쪽에 있을 때 타이밍을 맞춰 뒤집어야 해요.",
 r'''
let y, vy, g, obs, spd, spawnT, dist;
const GY = 40, R = 15;
function reset() { y = H - GY - R; vy = 0; g = 1; obs = []; spd = 150; spawnT = 1; dist = 0; setInfo("1.0x"); }
function flip() { g = -g; }
function pointer(t) { if (t === "down") flip(); }
function key(t, k) { if (k === "space" || k === "u" || k === "d") flip(); }
function update(dt) {
  spd = Math.min(340, spd + dt * 4.5); dist += spd * dt; setScore(Math.floor(dist / 20)); setInfo((spd / 150).toFixed(1) + "x");
  vy += g * 1500 * dt; y += vy * dt; if (y > H - GY - R) { y = H - GY - R; vy = 0; } if (y < GY + R) { y = GY + R; vy = 0; }
  spawnT -= dt; if (spawnT <= 0) { spawnT = rand(.8, 1.5) * 190 / spd; const top = Math.random() < .5, n = Math.random() < .3 ? 2 : 1; for (let k = 0; k < n; k++) obs.push({ x: W + 20 + k * 26, top }); }
  for (const o of obs) o.x -= spd * dt; obs = obs.filter(o => o.x > -30);
  for (const o of obs) { const oy = o.top ? GY : H - GY; if (Math.abs(o.x - 70) < 16 && Math.abs(y - (o.top ? GY + 14 : H - GY - 14)) < 22) end(); }
}
function draw(c) {
  c.fillStyle = C.muted; c.fillRect(0, 0, W, GY); c.fillRect(0, H - GY, W, GY); c.fillStyle = C.bad; for (const o of obs) { c.beginPath(); if (o.top) { c.moveTo(o.x - 12, GY); c.lineTo(o.x + 12, GY); c.lineTo(o.x, GY + 26); } else { c.moveTo(o.x - 12, H - GY); c.lineTo(o.x + 12, H - GY); c.lineTo(o.x, H - GY - 26); } c.fill(); }
  c.font = "28px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.save(); c.translate(70, y); if (g < 0) c.scale(1, -1); c.fillText("🏃", 0, 0); c.restore();
}
''')

# 7. 대포 쏘기
make(H+"cannon-shot.html", "대포 쏘기", "💣", 20, "cannonshot-best-v1", 300, 400, "남은 포탄", "과녁을 모두 쓰러뜨리세요",
 "화면을 <b>손가락으로 눌러서 뒤로 끌었다가 놓으면</b> 대포가 발사돼요. 끈 방향과 길이에 따라 각도와 힘이 정해져요. 포탄 5개로 📦 상자를 모두 맞혀 쓰러뜨리세요! 단계가 올라가면 상자가 늘어나요.",
 r'''
let ball, shots, boxes, aim, level, wait, msg;
const GX = 36, GY = H - 40, G = 380;
function reset() { level = 1; setup(); setScore(0); }
function setup() { shots = 5; ball = null; aim = null; wait = 0; boxes = []; const n = 2 + level; for (let k = 0; k < n; k++) boxes.push({ x: rand(150, W - 24), y: GY - 12 - (k % 3) * 0, alive: true, vy: 0 }); setInfo(shots); }
function pointer(t, x, y) { if (ball) return; if (t === "down") aim = { sx: x, sy: y, x, y }; else if (t === "move" && aim) { aim.x = x; aim.y = y; } else if (t === "up" && aim) { const dx = aim.sx - aim.x, dy = aim.sy - aim.y, d = Math.hypot(dx, dy); aim = null; if (d < 12) return; const p = Math.min(d, 110) / 110 * 560; ball = { x: GX, y: GY, vx: dx / d * p, vy: dy / d * p }; shots--; setInfo(shots); } }
function update(dt) {
  if (ball) { ball.vy += G * dt; ball.x += ball.vx * dt; ball.y += ball.vy * dt;
    for (const b of boxes) if (b.alive && Math.abs(ball.x - b.x) < 20 && Math.abs(ball.y - b.y) < 20) { b.alive = false; addScore(10); }
    if (ball.y > GY + 12 || ball.x > W + 20 || ball.x < -20) { ball = null; wait = .4; } }
  else if (wait > 0) { wait -= dt; if (wait <= 0) { if (boxes.every(b => !b.alive)) { level++; addScore(20); setup(); } else if (shots <= 0) end(); } }
  else if (boxes.every(b => !b.alive)) { level++; addScore(20); setup(); } else if (shots <= 0) end();
}
function draw(c) {
  c.fillStyle = C.muted; c.fillRect(0, GY + 12, W, H); c.font = "30px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("🔫", GX - 4, GY);
  for (const b of boxes) if (b.alive) c.fillText("📦", b.x, b.y);
  if (aim) { const dx = aim.sx - aim.x, dy = aim.sy - aim.y, d = Math.hypot(dx, dy) || 1, p = Math.min(d, 110) / 110 * 560, ux = dx / d * p, uy = dy / d * p; c.fillStyle = C.accent; for (let k = 1; k <= 14; k++) { const t = k * .07; c.beginPath(); c.arc(GX + ux * t, GY + uy * t + .5 * G * t * t, 3, 0, 7); c.fill(); } }
  if (ball) { c.fillStyle = C.fg; c.beginPath(); c.arc(ball.x, ball.y, 6, 0, 7); c.fill(); }
}
''')
