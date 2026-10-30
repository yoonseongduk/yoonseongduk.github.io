import sys, json
sys.path.insert(0, ".")
from mkpage import make
from mkarcade import make as make_arcade
H = "out/"

# ---------- 낱말 섞기 ----------
WORDS = "사과 바나나 포도 딸기 수박 참외 토마토 오렌지 복숭아 고구마 강아지 고양이 토끼 코끼리 호랑이 원숭이 거북이 다람쥐 펭귄 기린 학교 선생님 도서관 운동장 교실 칠판 연필 지우개 공책 가방 비행기 자전거 기차 버스 자동차 오토바이 소방차 무지개 구름 태양 달빛 별똥별 바다 파도 모래 조개 불가사리 김치 비빔밥 떡볶이 불고기 라면 햄버거 피자 아이스크림 초콜릿 사탕 컴퓨터 키보드 마우스 전화기 텔레비전 냉장고 세탁기 청소기 에어컨 선풍기 장난감 인형 풍선 연날리기 눈사람 크리스마스 생일 선물 케이크 축구 야구 농구 수영 태권도 피아노 바이올린 기타 노래 그림".split()
make(H+"word-scramble.html", "낱말 섞기", "🔀", 160, "wordscramble-best-v1",
 "글자가 <b>뒤죽박죽 섞여 있어요</b>. 아래 글자 조각을 순서대로 눌러서 <b>원래 낱말</b>을 만들어 보세요! 힌트로 첫 글자를 볼 수 있지만 점수가 줄어요. 10문제예요.",
 r'''  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="muted">내가 만든 낱말</p><div class="line" id="line"></div></div>
  <div class="bank" id="bank"></div>
  <div class="row"><button class="btn ghost" id="undo" type="button">⌫ 지우기</button><button class="btn ghost" id="hint" type="button">💡 힌트 (−1점)</button></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>
  <div class="res" id="res" hidden></div>''',
 r'''const WORDS = ''' + json.dumps(WORDS, ensure_ascii=False) + r''';
let qs = [], i = 0, score = 0, best = ld(KEY) || 0, picked = [], letters = [], locked = false, hinted = false, gain = 2;
function newRound() { qs = shuf(WORDS).slice(0, 10); i = 0; score = 0; $("res").hidden = true; show(); }
function show() { const w = qs[i]; locked = false; picked = []; hinted = false; letters = [...w]; let order; do { order = shuf(letters.map((_, k) => k)); } while (order.every((v, k) => v === k)); bank = order; $("msg").textContent = ""; $("next").hidden = true; $("hint").disabled = false; $("undo").disabled = false; render(); $("no").textContent = (i + 1) + "/10"; $("score").textContent = score; $("best").textContent = best; }
let bank = [];
function render() { const w = qs[i]; $("line").innerHTML = [...w].map((_, k) => `<span class="slot">${picked[k] !== undefined ? letters[picked[k]] : ""}</span>`).join(""); $("bank").innerHTML = bank.map(k => `<button type="button" class="lt" data-k="${k}" ${picked.includes(k) || locked ? "disabled" : ""}>${letters[k]}</button>`).join(""); }
function check() { const w = qs[i], got = picked.map(k => letters[k]).join(""); locked = true; $("hint").disabled = $("undo").disabled = true; const ok = got === w; if (ok) { score += hinted ? 1 : 2; $("msg").textContent = hinted ? "⭕ 정답! (+1점)" : "⭕ 정답! (+2점)"; $("msg").style.color = "var(--ok)"; } else { $("msg").textContent = "❌ 정답은 '" + w + "'"; $("msg").style.color = "var(--bad)"; } $("score").textContent = score; $("next").textContent = i === 9 ? "결과 보기" : "다음 문제"; $("next").hidden = false; render(); }
function finish() { let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록!"; } $("next").hidden = true; $("msg").textContent = ""; $("line").innerHTML = "끝!"; $("bank").innerHTML = ""; $("res").innerHTML = `<b>${score}점 / 20점</b><p class="muted">${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("res").hidden = false; $("best").textContent = best; $("again").onclick = newRound; }
$("bank").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (!b || locked) return; picked.push(+b.dataset.k); render(); if (picked.length === letters.length) check(); });
$("undo").onclick = () => { if (!locked) { picked.pop(); render(); } };
$("hint").onclick = () => { if (locked || hinted) return; hinted = true; const w = qs[i]; picked = []; const k = bank.find(q => letters[q] === w[0]); picked.push(k); $("msg").textContent = "첫 글자 '" + w[0] + "'(으)로 시작해요"; $("msg").style.color = ""; render(); };
$("next").onclick = () => { if (i === 9) finish(); else { i++; show(); } }; newRound();''',
 css=".line{display:flex;gap:6px;justify-content:center;margin-top:8px;flex-wrap:wrap}.slot{width:46px;height:56px;border-radius:12px;border:2px dashed var(--accent);display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:1.8rem}.bank{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}.lt{width:52px;height:56px;border-radius:12px;border:2px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.8rem;padding:0}.lt:disabled{opacity:.25}")

# ---------- 이진수 맞추기 ----------
make(H+"binary-game.html", "이진수 맞추기", "💾", 215, "binary-best-v1",
 "컴퓨터는 <b>0과 1</b>만 써요! 아래 스위치를 눌러 켜면(1) 그 자리의 값이 더해져요. 맨 오른쪽부터 <b>1, 2, 4, 8, 16, 32</b>예요. 목표 숫자와 똑같이 만들어 보세요. 예) 5 = 4 + 1 → 000101. 10문제를 풀어요.",
 r'''  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="muted">이 숫자를 만들어 보세요</p><p class="big" id="target" style="font-size:3.5rem">0</p><p class="muted">내가 만든 값: <b id="cur">0</b></p></div>
  <div class="bits" id="bits"></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <button class="btn" id="check" type="button">확인</button>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>
  <div class="res" id="res" hidden></div>''',
 r'''const VAL = [32, 16, 8, 4, 2, 1];
let qs = [], i = 0, score = 0, best = ld(KEY) || 0, bits = [0, 0, 0, 0, 0, 0], locked = false;
const curVal = () => bits.reduce((s, b, k) => s + b * VAL[k], 0);
function newRound() { qs = Array.from({ length: 10 }, (_, k) => ri(1, k < 4 ? 15 : k < 8 ? 31 : 63)); i = 0; score = 0; $("res").hidden = true; show(); }
function show() { locked = false; bits = [0, 0, 0, 0, 0, 0]; $("target").textContent = qs[i]; $("msg").textContent = ""; $("check").hidden = false; $("next").hidden = true; render(); $("no").textContent = (i + 1) + "/10"; $("score").textContent = score; $("best").textContent = best; }
function render() { $("bits").innerHTML = bits.map((b, k) => `<button type="button" class="bt${b ? " on" : ""}" data-k="${k}" ${locked ? "disabled" : ""}><small>${VAL[k]}</small><b>${b}</b></button>`).join(""); $("cur").textContent = curVal(); }
$("bits").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && !locked) { bits[+b.dataset.k] ^= 1; render(); } });
$("check").onclick = () => { if (locked) return; locked = true; const ok = curVal() === qs[i]; if (ok) score++; $("msg").textContent = ok ? "⭕ 정답!" : `❌ 정답은 ${qs[i].toString(2).padStart(6, "0")} (${VAL.filter((v, k) => (qs[i] & v)).join(" + ")})`; $("msg").style.color = ok ? "var(--ok)" : "var(--bad)"; $("score").textContent = score; $("check").hidden = true; $("next").textContent = i === 9 ? "결과 보기" : "다음 문제"; $("next").hidden = false; render(); };
$("next").onclick = () => { if (i === 9) { let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록!"; } $("next").hidden = true; $("bits").innerHTML = ""; $("res").innerHTML = `<b>10문제 중 ${score}개 정답</b><p class="muted">${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("res").hidden = false; $("best").textContent = best; $("again").onclick = newRound; } else { i++; show(); } }; newRound();''',
 css=".bits{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}.bt{border-radius:12px;border:2px solid var(--line);background:var(--surface);padding:10px 0;display:flex;flex-direction:column;align-items:center;gap:4px;min-width:0}.bt small{color:var(--muted)}.bt b{font-family:var(--font-display);font-weight:400;font-size:1.8rem}.bt.on{background:var(--accent);border-color:var(--accent);color:var(--accent-fg)}.bt.on small{color:var(--accent-fg);opacity:.85}")

# ---------- 기사의 여행 ----------
make(H+"knights-tour.html", "기사의 여행", "♞", 28, "knightstour-best-v1",
 "체스의 <b>기사(말)</b>는 'ㄱ'자(2칸 가고 1칸 옆)로 움직여요. 같은 칸을 <b>두 번 밟지 않고</b> 판의 <b>모든 칸을 한 번씩</b> 밟아 보세요! 어느 칸에서 시작해도 돼요. 갈 수 있는 칸은 연한 초록으로 보여요.",
 r'''  <div class="seg" id="lv" style="--n:2"><button type="button" data-n="5" class="on">5×5<small>보통</small></button><button type="button" data-n="6">6×6<small>어려움</small></button></div>
  <div class="stats"><div class="stat"><small>밟은 칸</small><b id="vis">0</b></div><div class="stat"><small>전체 칸</small><b id="tot">25</b></div><div class="stat"><small>최고 기록</small><b id="best">0</b></div></div>
  <div class="kb" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <div class="row"><button class="btn ghost" id="undo" type="button">↩ 한 수 물리기</button><button class="btn ghost" id="again" type="button">처음부터</button></div>''',
 r'''let N = 5, path = [], best = ld(KEY) || {};
const MV = [[1, 2], [2, 1], [-1, 2], [-2, 1], [1, -2], [2, -1], [-1, -2], [-2, -1]];
function newGame() { path = []; $("res").hidden = true; $("tot").textContent = N * N; $("grid").style.gridTemplateColumns = `repeat(${N}, 1fr)`; render(); }
const at = (r, c) => path.findIndex(([y, x]) => y === r && x === c);
function moves() { if (!path.length) return null; const [r, c] = path[path.length - 1]; return MV.map(([a, b]) => [r + a, c + b]).filter(([y, x]) => y >= 0 && y < N && x >= 0 && x < N && at(y, x) < 0); }
function render() {
  const mv = moves(), last = path[path.length - 1];
  $("grid").innerHTML = Array.from({ length: N * N }, (_, k) => { const r = Math.floor(k / N), c = k % N, idx = at(r, c), can = mv === null || mv.some(([y, x]) => y === r && x === c), dark = (r + c) % 2; return `<button type="button" class="kc${dark ? " d" : ""}${idx >= 0 ? " v" : ""}${can && idx < 0 ? " can" : ""}${last && last[0] === r && last[1] === c ? " cur" : ""}" data-r="${r}" data-c="${c}">${last && last[0] === r && last[1] === c ? "♞" : idx >= 0 ? idx + 1 : ""}</button>`; }).join("");
  $("vis").textContent = path.length; $("best").textContent = best[N] || 0;
}
function tap(r, c) {
  const mv = moves(); if (mv !== null && !mv.some(([y, x]) => y === r && x === c)) return; if (mv === null && at(r, c) >= 0) return; path.push([r, c]); render();
  const m = moves(); if (path.length > (best[N] || 0)) { best[N] = path.length; sv(KEY, best); $("best").textContent = best[N]; }
  if (path.length === N * N) { $("res").innerHTML = `<b>🎉 모든 칸을 밟았어요!</b><p class="muted">대단해요! 기사의 여행 성공</p>`; $("res").hidden = false; } else if (!m.length) { $("res").innerHTML = `<b>더 갈 수 있는 칸이 없어요</b><p class="muted">${path.length}칸까지 갔어요. '한 수 물리기'나 '처음부터'를 눌러 다시 해 보세요.</p>`; $("res").hidden = false; }
}
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-r]"); if (b) tap(+b.dataset.r, +b.dataset.c); });
$("undo").onclick = () => { if (path.length) { path.pop(); $("res").hidden = true; render(); } }; $("again").onclick = newGame;
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); N = +b.dataset.n; newGame(); }); newGame();''',
 css=".kb{display:grid;gap:0;border:3px solid var(--fg);border-radius:8px;overflow:hidden;max-width:380px;margin:0 auto;width:100%}.kc{aspect-ratio:1;border:0;background:#f0d9b5;padding:0;min-width:0;font-family:var(--font-display);font-size:clamp(1rem,5vw,1.4rem);color:#5a3b1a}.kc.d{background:#b58863}.kc.v{background:#7aa874;color:#fff}.kc.can{box-shadow:inset 0 0 0 4px #7ed67e}.kc.cur{background:#e4572e;color:#fff;font-size:1.8rem}")

# ---------- N 퀸 ----------
make(H+"n-queens.html", "퀸 놓기 퍼즐", "♛", 330, "nqueens-best-v1",
 "체스의 <b>퀸(♛)</b>은 가로, 세로, 대각선으로 얼마든지 움직여요. 판에 퀸을 <b>서로 잡을 수 없게</b> 칸 수만큼 놓아 보세요! 서로 공격할 수 있는 퀸은 <b>빨갛게</b> 보여요. 칸을 누르면 놓고, 다시 누르면 치워요.",
 r'''  <div class="seg" id="lv" style="--n:3"><button type="button" data-n="4" class="on">4×4<small>쉬움</small></button><button type="button" data-n="6">6×6<small>보통</small></button><button type="button" data-n="8">8×8<small>어려움</small></button></div>
  <div class="stats"><div class="stat"><small>놓은 퀸</small><b id="cnt">0</b></div><div class="stat"><small>필요한 퀸</small><b id="need">4</b></div><div class="stat"><small>서로 잡는 쌍</small><b id="bad">0</b></div></div>
  <div class="qb" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">모두 치우기</button>''',
 r'''let N = 4, q = [];
const key = (r, c) => r * N + c;
function conflicts() { const bad = new Set(); let pairs = 0; for (let i = 0; i < q.length; i++) for (let j = i + 1; j < q.length; j++) { const [a, b] = q[i], [c, d] = q[j]; if (a === c || b === d || Math.abs(a - c) === Math.abs(b - d)) { bad.add(i); bad.add(j); pairs++; } } return { bad, pairs }; }
function render() { const { bad, pairs } = conflicts(); $("grid").style.gridTemplateColumns = `repeat(${N}, 1fr)`;
  $("grid").innerHTML = Array.from({ length: N * N }, (_, k) => { const r = Math.floor(k / N), c = k % N, i = q.findIndex(([y, x]) => y === r && x === c); return `<button type="button" class="qc${(r + c) % 2 ? " d" : ""}${i >= 0 && bad.has(i) ? " bad" : ""}" data-r="${r}" data-c="${c}">${i >= 0 ? "♛" : ""}</button>`; }).join("");
  $("cnt").textContent = q.length; $("need").textContent = N; $("bad").textContent = pairs; $("res").hidden = !(q.length === N && !pairs); if (q.length === N && !pairs) $("res").innerHTML = `<b>🎉 성공! 퀸 ${N}개를 모두 놓았어요</b>`; }
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-r]"); if (!b) return; const r = +b.dataset.r, c = +b.dataset.c, i = q.findIndex(([y, x]) => y === r && x === c); if (i >= 0) q.splice(i, 1); else if (q.length < N) q.push([r, c]); render(); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); N = +b.dataset.n; q = []; render(); }); $("again").onclick = () => { q = []; render(); }; render();''',
 css=".qb{display:grid;gap:0;border:3px solid var(--fg);border-radius:8px;overflow:hidden;max-width:380px;margin:0 auto;width:100%}.qc{aspect-ratio:1;border:0;background:#f0d9b5;padding:0;min-width:0;font-size:clamp(1.2rem,8vw,2rem);color:#222;display:flex;align-items:center;justify-content:center}.qc.d{background:#b58863}.qc.bad{background:#e57373;color:#7a0000}")

# ---------- 공 튀기기 ----------
make_arcade(H+"ball-juggle.html", "공 튀기기", "🏐", 40, "balljuggle-best-v1", 300, 420, "튕긴 횟수", "공이 땅에 떨어지지 않게 튕겨 올리세요",
 "<b>공을 눌러서 위로 튕겨 올리세요</b>! 공의 <b>왼쪽을 누르면 오른쪽으로</b>, 오른쪽을 누르면 왼쪽으로 날아가요. 한가운데를 누르면 똑바로 올라가요. 공이 땅에 닿거나 옆으로 나가면 끝이에요. 높이 올라갈수록 점수가 높아요!",
 r'''
let ball, hits, shake;
function reset() { ball = { x: W / 2, y: 150, vx: 0, vy: 0, r: 26 }; hits = 0; setInfo(0); }
function pointer(t, x, y) { if (t !== "down") return; const dx = x - ball.x, dy = y - ball.y; if (Math.hypot(dx, dy) < ball.r + 26) { ball.vy = -(430 + Math.min(80, hits * 2)); ball.vx = clamp(-dx * 7, -220, 220) + rand(-15, 15); hits++; setInfo(hits); addScore(1 + Math.floor((H - ball.y) / 140)); } }
function update(dt) { ball.vy += 640 * dt; ball.x += ball.vx * dt; ball.y += ball.vy * dt; if (ball.x < ball.r) { ball.x = ball.r; ball.vx = Math.abs(ball.vx) * .8; } if (ball.x > W - ball.r) { ball.x = W - ball.r; ball.vx = -Math.abs(ball.vx) * .8; } if (ball.y > H - ball.r - 6) end(); }
function draw(c) { c.fillStyle = C.muted; c.fillRect(0, H - 6, W, 6); c.font = ball.r * 2 + "px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("🏐", ball.x, ball.y + 2); c.fillStyle = "rgba(0,0,0,.15)"; c.beginPath(); c.ellipse(ball.x, H - 8, ball.r * (1 - ball.y / H * .6), 5, 0, 0, 7); c.fill(); }
''')

# ---------- 개구리 점프 ----------
make_arcade(H+"frog-jump.html", "개구리 점프", "🐸", 120, "frogjump-best-v1", 300, 400, "연잎", "연잎을 건너 멀리 가세요",
 "화면을 <b>꾹 누르고 있으면 힘이 모이고</b>, 손을 떼면 개구리가 뛰어요! 오래 누를수록 멀리 뛰어요. 다음 연잎에 정확히 내려앉으세요. 물에 빠지면 끝! 연잎은 갈수록 멀어지고 작아져요.",
 r'''
let pads, frog, charge, holding, camX, state2, t2;
function reset() { pads = [{ x: 40, r: 30 }]; for (let k = 1; k < 8; k++) addPad(); frog = { x: 40, y: 0, jumping: false, vx: 0, vy: 0, on: 0 }; charge = 0; holding = false; camX = 0; state2 = "ready"; setInfo(0); }
function addPad() { const p = pads[pads.length - 1], lvl = pads.length; pads.push({ x: p.x + rand(70, Math.min(150, 90 + lvl * 4)), r: Math.max(16, 30 - lvl * .6) }); }
function pointer(t) { if (frog.jumping) return; if (t === "down") { holding = true; charge = 0; } else if (t === "up" && holding) { holding = false; const power = 120 + charge * 190; frog.jumping = true; frog.vx = power * .62; frog.vy = -330; frog.y = 0; } }
function key(t, k) { if (k === "space" && !frog.jumping) { if (!holding) { holding = true; charge = 0; } else pointer("up"); } }
function update(dt) {
  if (holding) charge = Math.min(1, charge + dt * .9);
  if (frog.jumping) { frog.x += frog.vx * dt; frog.vy += 900 * dt; frog.y += frog.vy * dt;
    if (frog.y >= 0 && frog.vy > 0) { const hit = pads.findIndex((p, k) => Math.abs(p.x - frog.x) < p.r + 6); if (hit >= 0) { frog.jumping = false; frog.y = 0; frog.x = pads[hit].x; if (hit > frog.on) { addScore(hit - frog.on); frog.on = hit; setInfo(hit); while (pads.length < frog.on + 8) addPad(); } } else if (frog.y > 60) end(); } }
  camX += (frog.x - 60 - camX) * Math.min(1, dt * 5);
}
function draw(c) {
  c.fillStyle = "rgba(60,150,220,.35)"; c.fillRect(0, H * .62, W, H); c.save(); c.translate(-camX, 0);
  c.font = "26px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; for (const p of pads) { if (p.x < camX - 50 || p.x > camX + W + 50) continue; c.fillStyle = "#3fa34d"; c.beginPath(); c.ellipse(p.x, H * .62, p.r + 4, p.r * .38 + 3, 0, 0, 7); c.fill(); c.fillStyle = "#58c26a"; c.beginPath(); c.ellipse(p.x, H * .62 - 2, p.r, p.r * .32, 0, 0, 7); c.fill(); }
  c.font = "34px sans-serif"; const sq = holding ? 1 - charge * .25 : 1; c.save(); c.translate(frog.x, H * .62 - 22 + frog.y); c.scale(1 / sq, sq); c.fillText("🐸", 0, 0); c.restore(); c.restore();
  if (holding) { c.fillStyle = C.line; c.fillRect(20, 24, W - 40, 12); c.fillStyle = charge > .85 ? C.bad : C.accent; c.fillRect(20, 24, (W - 40) * charge, 12); }
}
''')

# ---------- 스무고개 ----------
AN = [("🐶", "강아지", "10110110101".replace("", "")), ]
ANIMALS = [["🐶","강아지",[1,0,0,1,1,1,0,1,0,0,1]],["🐱","고양이",[1,0,0,1,0,1,0,1,0,0,1]],["🐰","토끼",[1,0,0,0,1,1,0,1,0,0,1]],["🐯","호랑이",[1,0,0,1,0,1,1,0,1,0,1]],["🦁","사자",[1,0,0,1,0,1,1,0,0,0,1]],["🐘","코끼리",[1,0,0,0,1,1,1,0,0,0,0]],["🦒","기린",[1,0,0,0,1,1,1,0,1,0,1]],["🐻","곰",[1,0,0,1,1,1,1,0,0,0,1]],["🐋","고래",[1,0,1,1,0,0,1,0,0,0,0]],["🐬","돌고래",[1,0,1,1,0,0,0,0,0,0,0]],["🐧","펭귄",[0,0,1,1,0,0,0,0,0,1,0]],["🦅","독수리",[0,1,0,1,0,0,1,0,0,1,0]],["🐦","참새",[0,1,0,0,1,0,0,0,0,1,0]],["🦜","앵무새",[0,1,0,0,1,0,0,1,1,1,0]],["🐔","닭",[0,0,0,0,1,0,0,1,0,1,0]],["🐊","악어",[0,0,1,1,0,1,1,0,0,1,0]],["🐢","거북이",[0,0,1,0,1,1,0,1,0,1,0]],["🐍","뱀",[0,0,0,1,0,0,0,0,1,1,0]],["🐸","개구리",[0,0,1,1,0,1,0,0,0,1,0]],["🦋","나비",[0,1,0,0,1,0,0,0,1,1,0]],["🐠","금붕어",[0,0,1,0,1,0,0,1,0,1,0]],["🦈","상어",[0,0,1,1,0,0,1,0,0,1,0]],["🐪","낙타",[1,0,0,0,1,1,1,0,0,0,1]],["🐷","돼지",[1,0,0,1,1,1,0,1,0,0,0]]]
QS = ["포유류인가요? (새끼를 낳아 젖을 먹여요)", "날 수 있나요?", "물에서 사나요?", "고기를 먹나요?", "풀·열매·곡식을 먹나요?", "다리가 네 개 있나요?", "사람보다 몸집이 큰가요?", "집에서 키울 수 있나요?", "몸에 무늬(줄·점)가 있나요?", "알을 낳나요?", "몸에 털이 있나요?"]
make(H+"twenty-questions.html", "동물 스무고개", "❓", 200, "twentyq-best-v1",
 "컴퓨터가 <b>비밀 동물</b>을 하나 정했어요! 아래 질문을 눌러서 힌트를 얻고, 알 것 같으면 <b>'정답 맞히기'</b>로 동물을 골라 보세요. 질문을 <b>적게 할수록</b> 좋은 기록이에요. 질문은 최대 11개예요.",
 r'''  <div class="stats"><div class="stat"><small>쓴 질문</small><b id="used">0</b></div><div class="stat"><small>남은 후보</small><b id="cand">24</b></div><div class="stat"><small>최소 질문</small><b id="best">-</b></div></div>
  <div class="card"><div id="qs"></div></div>
  <div class="card"><b>🔍 알게 된 것</b><div id="log" class="muted">아직 질문을 하지 않았어요</div></div>
  <button class="btn" id="guess" type="button">🎯 정답 맞히기</button>
  <div class="grid" id="zoo" hidden></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const AN = ''' + json.dumps(ANIMALS, ensure_ascii=False) + r''', QS = ''' + json.dumps(QS, ensure_ascii=False) + r''';
let secret, asked = {}, over = false, best = ld(KEY);
function newGame() { secret = AN[ri(0, AN.length - 1)]; asked = {}; over = false; $("res").hidden = true; $("zoo").hidden = true; $("guess").hidden = false; render(); }
function candidates() { return AN.filter(a => Object.entries(asked).every(([k, v]) => a[2][+k] === v)); }
function render() {
  $("qs").innerHTML = QS.map((q, k) => `<button type="button" class="qb2${asked[k] !== undefined ? " done" : ""}" data-q="${k}" ${asked[k] !== undefined || over ? "disabled" : ""}>${q}${asked[k] !== undefined ? ` <b>${asked[k] ? "⭕ 네" : "❌ 아니요"}</b>` : ""}</button>`).join("");
  const keys = Object.keys(asked); $("used").textContent = keys.length; $("cand").textContent = candidates().length; $("best").textContent = best || "-";
  $("log").innerHTML = keys.length ? keys.map(k => `${asked[k] ? "⭕" : "❌"} ${QS[k].replace(/\?.*/, "?")}`).join("<br>") : "아직 질문을 하지 않았어요";
}
$("qs").addEventListener("click", e => { const b = e.target.closest("[data-q]"); if (!b || over) return; asked[+b.dataset.q] = secret[2][+b.dataset.q]; render(); });
$("guess").onclick = () => { if (over) return; $("zoo").hidden = false; $("zoo").innerHTML = AN.map((a, k) => `<button type="button" data-g="${k}" ${candidates().includes(a) ? "" : 'class="out"'}><span>${a[0]}</span><small>${a[1]}</small></button>`).join(""); $("zoo").scrollIntoView({ behavior: "smooth", block: "nearest" }); };
$("zoo").addEventListener("click", e => { const b = e.target.closest("[data-g]"); if (!b || over) return; const g = AN[+b.dataset.g], n = Object.keys(asked).length; over = true; if (g === secret) { const nb = !best || n < best; if (nb) { best = n; sv(KEY, best); } $("res").innerHTML = `<b>🎉 정답! ${secret[0]} ${secret[1]}</b><p class="muted">질문 ${n}개로 맞혔어요 ${nb ? "· 신기록!" : "· 최소 " + best + "개"}</p>`; } else $("res").innerHTML = `<b>😢 아쉬워요. 정답은 ${secret[0]} ${secret[1]}</b><p class="muted">${g[1]}이(가) 아니었어요</p>`; $("res").hidden = false; $("zoo").hidden = true; $("guess").hidden = true; render(); });
$("again").onclick = newGame; newGame();''',
 css=".qb2{display:flex;justify-content:space-between;align-items:center;gap:8px;width:100%;text-align:left;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:9px 12px;margin-bottom:6px;font-size:.95rem}.qb2.done{background:var(--soft);color:var(--muted)}.qb2 b{white-space:nowrap}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}.grid button{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:8px 0;display:flex;flex-direction:column;align-items:center;min-width:0}.grid button span{font-size:1.8rem}.grid button small{font-size:.75rem}.grid button.out{opacity:.35}")
