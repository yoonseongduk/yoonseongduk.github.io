import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 화살표 반응 ----------
make(H+"arrow-reaction.html", "화살표 반응", "🏹", 8, "arrowreact-best-v1",
 "화면에 나타나는 <b>화살표와 같은 방향 버튼</b>을 빨리 누르세요! 맞히면 점수, 틀리면 시간이 줄어요. 점점 제한 시간이 짧아져요. 30초 동안 높은 점수를 노려 보세요.",
 r'''  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">30</b></div><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="big" id="arrow" style="font-size:clamp(4rem,26vw,6.5rem);min-height:1.2em">⬆️</p><div class="bar"><i id="bar"></i></div></div>
  <div class="dpad"><button type="button" data-d="0" style="grid-column:2">⬆️</button><button type="button" data-d="2" style="grid-column:1;grid-row:2">⬅️</button><button type="button" data-d="3" style="grid-column:3;grid-row:2">➡️</button><button type="button" data-d="1" style="grid-column:2;grid-row:3">⬇️</button></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''const AR = ["⬆️", "⬇️", "⬅️", "➡️"];
let score = 0, sec = 30, run = false, cur = 0, limit = 1.6, t0 = 0, best = ld(KEY) || 0, timer = 0, bt = 0, tempo = 1, streak = 0;
function next() { cur = ri(0, 3); $("arrow").textContent = AR[cur]; t0 = Date.now(); $("bar").style.width = "100%"; }
function upd() { $("score").textContent = score; $("time").textContent = Math.max(0, Math.ceil(sec)); $("best").textContent = best; }
function start() { score = 0; sec = 30; limit = 1.6; streak = 0; run = true; $("res").hidden = true; $("start").hidden = true; next(); upd(); clearInterval(timer); clearInterval(bt);
  timer = setInterval(() => { sec -= 0.1; upd(); if (sec <= 0) end(); }, 100 * tempo);
  bt = setInterval(() => { const left = 1 - (Date.now() - t0) / (limit * 1000 * tempo); $("bar").style.width = Math.max(0, left * 100) + "%"; if (left <= 0 && run) { score = Math.max(0, score - 1); streak = 0; sec -= 1; upd(); next(); } }, 50); }
function pick(d) { if (!run) return; if (d === cur) { streak++; score += 1 + Math.floor(streak / 5); limit = Math.max(0.6, limit - 0.03); } else { streak = 0; score = Math.max(0, score - 1); sec -= 1; } upd(); next(); }
function end() { run = false; clearInterval(timer); clearInterval(bt); let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>${score}점!</b><p class="muted">${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; $("arrow").textContent = "끝!"; upd(); }
document.querySelector(".dpad").addEventListener("pointerdown", e => { const b = e.target.closest("[data-d]"); if (b) { e.preventDefault(); pick(+b.dataset.d); } });
$("start").onclick = start; upd();''',
 css=".dpad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.dpad button{padding:16px 0;border-radius:14px;border:1px solid var(--line);background:var(--surface);font-size:1.8rem;touch-action:manipulation}.bar{height:8px;border-radius:4px;background:var(--line);overflow:hidden;margin-top:8px}.bar i{display:block;height:100%;background:var(--accent);width:100%}")

# ---------- 홀짝 스피드 ----------
make(H+"odd-even.html", "홀짝 스피드", "⚖️", 262, "oddeven-best-v1",
 "화면에 나오는 숫자가 <b>홀수</b>인지 <b>짝수</b>인지 빠르게 눌러 보세요! 40초 동안 몇 개나 맞힐 수 있을까요? 연속으로 맞히면 보너스 점수가 있어요.",
 r'''  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">40</b></div><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="big" id="num" style="font-size:clamp(4rem,26vw,6.5rem)">?</p></div>
  <div class="row"><button class="btn" data-a="1" id="oddb" type="button" style="background:#e4572e">홀수</button><button class="btn" data-a="0" id="evenb" type="button" style="background:#2f6fdf">짝수</button></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="start" type="button">시작</button>''',
 r'''let score = 0, sec = 40, run = false, n = 0, combo = 0, best = ld(KEY) || 0, timer = 0, tempo = 1;
function next() { n = ri(1, 99); $("num").textContent = n; }
function upd() { $("score").textContent = score; $("time").textContent = sec; $("best").textContent = best; }
function start() { score = 0; sec = 40; combo = 0; run = true; $("res").hidden = true; $("start").hidden = true; next(); upd(); clearInterval(timer); timer = setInterval(() => { sec--; upd(); if (sec <= 0) end(); }, 1000 * tempo); }
function pick(a) { if (!run) return; if ((n % 2) === a) { combo++; score += 1 + (combo >= 5 ? 1 : 0) + (combo >= 10 ? 1 : 0); } else { combo = 0; score = Math.max(0, score - 2); } upd(); next(); }
function end() { run = false; clearInterval(timer); let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>${score}점!</b><p class="muted">${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; $("num").textContent = "끝!"; upd(); }
document.querySelector(".row").addEventListener("pointerdown", e => { const b = e.target.closest("[data-a]"); if (b) { e.preventDefault(); pick(+b.dataset.a); } });
$("start").onclick = start; upd();''', css=".row .btn{padding:24px 0;font-size:1.8rem}")

# ---------- 개수 세기 ----------
make(H+"count-flash.html", "번쩍 개수 세기", "👀", 140, "countflash-best-v1",
 "그림이 <b>아주 잠깐 나타났다 사라져요</b>. 몇 개였는지 보기에서 골라 보세요! 단계가 오를수록 개수가 많아지고 보여 주는 시간은 짧아져요. 틀리면 끝!",
 r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lv">1</b></div><div class="stat"><small>최고 단계</small><b id="best">0</b></div><div class="stat"><small>상태</small><b id="st" style="font-size:1.05rem">준비</b></div></div>
  <div class="field" id="field"></div>
  <div class="seg" id="opts" style="--n:4"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''const ICONS = ["🍎", "⭐", "🐟", "🌸", "🐝", "🎈"];
let lv = 1, cnt = 0, state = "idle", best = ld(KEY) || 0, tempo = 1, gen = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
function setSt(t) { $("st").textContent = t; $("lv").textContent = lv; $("best").textContent = best; }
async function round() {
  const my = ++gen; state = "show"; $("opts").innerHTML = ""; setSt("잘 보세요"); cnt = Math.min(2 + lv, 14); const ic = ICONS[ri(0, ICONS.length - 1)]; $("field").innerHTML = ""; await sleep(500); if (my !== gen) return;
  const used = []; for (let k = 0; k < cnt; k++) { let x, y, tries = 0; do { x = ri(6, 88); y = ri(6, 80); tries++; } while (tries < 60 && used.some(([a, b]) => Math.abs(a - x) < 11 && Math.abs(b - y) < 13)); used.push([x, y]); const s = document.createElement("span"); s.textContent = ic; s.style.left = x + "%"; s.style.top = y + "%"; $("field").appendChild(s); }
  await sleep(Math.max(450, 1300 - lv * 80)); if (my !== gen) return; $("field").innerHTML = ""; state = "input"; setSt("몇 개였을까요?");
  const wrong = new Set(); while (wrong.size < 3) { const w = cnt + ri(-3, 3); if (w !== cnt && w > 0) wrong.add(w); }
  $("opts").innerHTML = shuf([cnt, ...wrong]).map(o => `<button type="button" data-v="${o}">${o}개</button>`).join("");
}
function start() { lv = 1; $("res").hidden = true; $("start").hidden = true; round(); }
async function pick(v) { if (state !== "input") return; state = "wait"; if (v === cnt) { setSt("정답! 👍"); await sleep(600); lv++; round(); } else { state = "over"; gen++; const reached = lv - 1; if (reached > best) { best = reached; sv(KEY, best); } setSt("끝"); $("res").innerHTML = `<b>${reached}단계까지 성공!</b><p class="muted">정답은 ${cnt}개였어요</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; } }
$("opts").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (b) pick(+b.dataset.v); });
$("start").onclick = start; setSt("준비");''',
 css=".field{position:relative;height:min(46vh,300px);background:var(--surface);border:1px solid var(--line);border-radius:16px}.field span{position:absolute;font-size:clamp(1.6rem,8vw,2.2rem);line-height:1}.seg button{padding:14px 4px;font-family:var(--font-display);font-size:1.3rem;font-weight:400}")

# ---------- 같은 그림 찾기 ----------
make(H+"dobble-match.html", "같은 그림 찾기", "🔍", 34, "dobble-best-v1",
 "위아래 두 카드에는 <b>똑같은 그림이 딱 하나</b> 들어 있어요. 그 그림을 빨리 찾아서 눌러 보세요! 틀리면 시간이 줄어요. 40초 안에 몇 장이나 맞힐 수 있을까요?",
 r'''  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">40</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="dcard" id="c1"></div>
  <div class="dcard" id="c2"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''const POOL = "🍎🍌🍇🍓🍊🍑🍉🍍🥕🌽🍄🍔🍕🍩🍪🐶🐱🐰🐻🐼🦊🐸🐵🐯🦁🐷🐮🐔🐧🦉🦋🐝🐢🐙🐬🌸🌻🌲🌙⭐☀️⚡🔥💧🎈🎁⚽🏀🚗🚀✈️🚲⏰🔑🎵📚👑💎".match(/\p{Extended_Pictographic}️?/gu);
let score = 0, sec = 40, run = false, share = "", best = ld(KEY) || 0, timer = 0, tempo = 1;
function deal() { const s = shuf(POOL).slice(0, 13), common = s[0], A = s.slice(1, 7), B = s.slice(7, 13); share = common; draw("c1", shuf([common, ...A])); draw("c2", shuf([common, ...B])); }
function draw(id, arr) { $(id).innerHTML = arr.map((e, k) => `<button type="button" data-e="${e}" style="--r:${ri(-25, 25)}deg;font-size:${ri(28, 46)}px">${e}</button>`).join(""); }
function upd() { $("score").textContent = score; $("time").textContent = sec; $("best").textContent = best; }
function start() { score = 0; sec = 40; run = true; $("res").hidden = true; $("start").hidden = true; deal(); upd(); clearInterval(timer); timer = setInterval(() => { sec--; upd(); if (sec <= 0) end(); }, 1000 * tempo); }
function pick(e) { if (!run) return; if (e === share) { score++; deal(); } else { sec = Math.max(0, sec - 2); if (sec <= 0) end(); } upd(); }
function end() { run = false; clearInterval(timer); let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>${score}장 맞혔어요!</b><p class="muted">${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; $("c1").innerHTML = ""; $("c2").innerHTML = ""; upd(); }
document.addEventListener("pointerdown", e => { const b = e.target.closest("[data-e]"); if (b) { e.preventDefault(); pick(b.dataset.e); } });
$("start").onclick = start; upd();''',
 css=".dcard{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;align-items:center;background:var(--surface);border:2px solid var(--line);border-radius:50%/36%;padding:16px;min-height:150px}.dcard button{background:transparent;border:0;padding:4px 6px;transform:rotate(var(--r));line-height:1.1;touch-action:manipulation}")

# ---------- 큰 수부터 터치 ----------
make(H+"reverse-tap.html", "거꾸로 숫자 터치", "🔙", 12, "reversetap-best-v1",
 "흩어진 숫자를 <b>큰 수부터 작은 수 순서로</b> 눌러 보세요. 가장 큰 숫자부터 1까지! 빨리 끝낼수록 좋은 기록이에요. 틀리게 누르면 1초가 늘어나요.",
 r'''  <div class="seg" id="lv" style="--n:3"><button type="button" data-n="9" class="on">9개<small>쉬움</small></button><button type="button" data-n="16">16개<small>보통</small></button><button type="button" data-n="25">25개<small>어려움</small></button></div>
  <div class="stats"><div class="stat"><small>시간</small><b id="time">0.0</b></div><div class="stat"><small>다음 숫자</small><b id="nx">-</b></div><div class="stat"><small>최고 기록</small><b id="best">-</b></div></div>
  <div class="rt" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="again" type="button">새로 하기</button>''',
 r'''let N = 9, nums = [], next = 9, t0 = 0, pen = 0, done = false, started = false, best = ld(KEY) || {}, tm = 0, tempo = 1;
function newGame() { nums = shuf(Array.from({ length: N }, (_, k) => k + 1)); next = N; pen = 0; done = false; started = false; $("res").hidden = true; const c = Math.sqrt(N); $("grid").style.gridTemplateColumns = `repeat(${c}, 1fr)`; render(); }
function render() { $("grid").innerHTML = nums.map((v, k) => `<button type="button" class="tn${v > next ? " gone" : ""}" data-v="${v}">${v}</button>`).join(""); $("nx").textContent = done ? "-" : next; $("best").textContent = best[N] ? best[N].toFixed(1) + "초" : "-"; }
const elapsed = () => (started ? (Date.now() - t0) / 1000 : 0) + pen;
function tap(v) {
  if (done) return; if (!started) { started = true; t0 = Date.now(); }
  if (v === next) { next--; if (next === 0) { done = true; const s = elapsed(), nb = !best[N] || s < best[N]; if (nb) { best[N] = s; sv(KEY, best); } $("res").innerHTML = `<b>🎉 ${s.toFixed(1)}초!</b><p class="muted">${nb ? "신기록이에요!" : "최고 기록 " + best[N].toFixed(1) + "초"}</p>`; $("res").hidden = false; } }
  else if (v < next) { pen += 1; $("grid").classList.add("shake"); setTimeout(() => $("grid").classList.remove("shake"), 200); }
  render();
}
$("grid").addEventListener("pointerdown", e => { const b = e.target.closest("[data-v]"); if (b) { e.preventDefault(); tap(+b.dataset.v); } });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); N = +b.dataset.n; newGame(); });
$("again").onclick = newGame; tm = setInterval(() => { if (!done) $("time").textContent = elapsed().toFixed(1); }, 100); newGame();''',
 css=".rt{display:grid;gap:6px}.rt.shake{animation:sh .2s}@keyframes sh{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}.tn{aspect-ratio:1;border-radius:12px;border:2px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:clamp(1.2rem,6vw,1.8rem);padding:0;min-width:0;touch-action:manipulation}.tn.gone{visibility:hidden}")

# ---------- 정확히 멈춰라 ----------
make(H+"time-stop.html", "정확히 멈춰라", "⏱️", 195, "timestop-best-v1",
 "화면의 숫자가 빠르게 올라가요. <b>목표 시간(예: 5.00초)에 정확히 맞춰</b> 멈춤 버튼을 눌러 보세요! 도중에 숫자가 <b>가려지면</b> 감으로 맞춰야 해요. 5번 도전해서 오차가 가장 작은 기록을 노려요.",
 r'''  <div class="stats"><div class="stat"><small>목표</small><b id="target">5.00</b></div><div class="stat"><small>도전</small><b id="round">1/5</b></div><div class="stat"><small>평균 오차</small><b id="avg">-</b></div></div>
  <div class="card center"><p class="big" id="clock" style="font-size:clamp(3rem,18vw,5rem)">0.00</p><p class="muted" id="msg">시작을 누르세요</p></div>
  <button class="btn" id="go" type="button">시작</button>
  <ul class="log" id="log"></ul>
  <div class="res" id="res" hidden></div>''',
 r'''let target = 5, round = 0, errs = [], t0 = 0, running = false, raf = 0, hideAt = 0, best = ld(KEY), tempo = 1;
const fmt = v => v.toFixed(2);
function newSet() { round = 0; errs = []; $("log").innerHTML = ""; $("res").hidden = true; target = [3, 4, 5, 6, 7][ri(0, 4)] + (Math.random() < .5 ? 0 : .5); $("target").textContent = fmt(target); $("avg").textContent = "-"; $("round").textContent = "1/5"; $("clock").textContent = "0.00"; $("msg").textContent = `${fmt(target)}초에 멈춰 보세요`; $("go").textContent = "시작"; $("go").dataset.m = "start"; }
function tick() { if (!running) return; const t = (performance.now() - t0) / 1000 * tempo; $("clock").textContent = t > hideAt ? "?.??" : fmt(t); raf = requestAnimationFrame(tick); }
function go() {
  if ($("go").dataset.m === "again") return newSet();
  if (!running) { running = true; t0 = performance.now(); hideAt = round >= 2 ? target * 0.3 : 99; $("go").textContent = "멈춰!"; $("msg").textContent = round >= 2 ? "도중에 숫자가 가려져요 👀" : "타이밍을 잘 맞춰요"; raf = requestAnimationFrame(tick); return; }
  running = false; cancelAnimationFrame(raf); const t = (performance.now() - t0) / 1000 * tempo, e = Math.abs(t - target); errs.push(e); round++; $("clock").textContent = fmt(t);
  const li = document.createElement("li"); li.textContent = `${round}번째: ${fmt(t)}초 (오차 ${fmt(e)}초) ${e < 0.05 ? "🎯" : e < 0.15 ? "👍" : ""}`; $("log").appendChild(li);
  const avg = errs.reduce((a, b) => a + b, 0) / errs.length; $("avg").textContent = fmt(avg) + "초";
  if (round >= 5) { const nb = best === null || avg < best; if (nb) { best = avg; sv(KEY, best); } $("res").innerHTML = `<b>평균 오차 ${fmt(avg)}초</b><p class="muted">${nb ? "🏆 신기록이에요!" : "최고 기록 " + fmt(best) + "초"}</p>`; $("res").hidden = false; $("go").textContent = "다시 하기"; $("go").dataset.m = "again"; $("msg").textContent = ""; }
  else { $("round").textContent = (round + 1) + "/5"; $("go").textContent = "시작"; $("go").dataset.m = "start"; $("msg").textContent = `${fmt(target)}초에 멈춰 보세요`; }
}
$("go").addEventListener("pointerdown", e => { e.preventDefault(); go(); }); newSet();''',
 css=".log{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:4px}.log li{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:6px 10px;font-size:.95rem}")

# ---------- 신호등 ----------
make(H+"red-green-light.html", "빨간불 초록불", "🚦", 128, "redgreen-best-v1",
 "<b>초록불일 때</b> 버튼을 빠르게 눌러서 앞으로 가세요! <b>빨간불이 켜지면 손을 떼야</b> 해요. 빨간불에 누르면 처음 위치로 돌아가요. 결승선까지 먼저 도착해 보세요!",
 r'''  <div class="stats"><div class="stat"><small>걸린 시간</small><b id="time">0.0</b></div><div class="stat"><small>최고 기록</small><b id="best">-</b></div><div class="stat"><small>실패</small><b id="fails">0</b></div></div>
  <div class="card center"><div class="light" id="light"></div><div class="track"><i id="runner">🏃</i><b>🏁</b></div></div>
  <button class="btn" id="tap" type="button" style="padding:30px 0;font-size:2rem">누르기!</button>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="start" type="button">시작</button>''',
 r'''let pos = 0, green = true, run = false, t0 = 0, fails = 0, best = ld(KEY), switchAt = 0, raf = 0, last = 0, tempo = 1, tm = 0, gen = 0, holdWait = 0;
const GOAL = 30;
function setLight() { $("light").className = "light " + (green ? "g" : "r"); $("light").textContent = green ? "🟢 초록불! 달려요" : "🔴 빨간불! 손 떼세요"; }
function sched() { const my = gen; const wait = green ? ri(1200, 2600) : ri(900, 1800); setTimeout(() => { if (!run || my !== gen) return; green = !green; setLight(); if (!green) holdWait = 0.25; sched(); }, wait * tempo); }
function draw() { $("runner").style.left = (pos / GOAL * 86) + "%"; }
function press() {
  if (!run) return;
  if (!green) { if (holdWait > 0) return; pos = 0; fails++; $("fails").textContent = fails; draw(); $("light").classList.add("bad"); setTimeout(() => $("light").classList.remove("bad"), 250); return; }
  pos++; draw(); if (pos >= GOAL) win();
}
function win() { run = false; gen++; const s = (Date.now() - t0) / 1000, nb = best === null || s < best; if (nb) { best = s; sv(KEY, best); } $("res").innerHTML = `<b>🎉 도착! ${s.toFixed(1)}초</b><p class="muted">${nb ? "신기록이에요!" : "최고 기록 " + best.toFixed(1) + "초"} · 실패 ${fails}번</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; $("best").textContent = best.toFixed(1) + "초"; }
function start() { pos = 0; fails = 0; green = true; run = true; gen++; holdWait = 0; $("fails").textContent = 0; $("res").hidden = true; $("start").hidden = true; setLight(); draw(); t0 = Date.now(); sched(); clearInterval(tm); tm = setInterval(() => { if (run) { $("time").textContent = ((Date.now() - t0) / 1000).toFixed(1); if (holdWait > 0) holdWait -= 0.1 / tempo; } }, 100 * tempo); }
$("tap").addEventListener("pointerdown", e => { e.preventDefault(); press(); });
$("start").onclick = start; $("best").textContent = best === null ? "-" : best.toFixed(1) + "초"; setLight(); draw();''',
 css=".light{padding:14px;border-radius:14px;font-family:var(--font-display);font-size:1.4rem;background:var(--soft);transition:background .15s}.light.g{background:color-mix(in srgb,var(--ok) 30%,var(--surface))}.light.r{background:color-mix(in srgb,var(--bad) 30%,var(--surface))}.light.bad{animation:sh .25s}@keyframes sh{25%{transform:translateX(-8px)}75%{transform:translateX(8px)}}.track{position:relative;height:50px;margin-top:12px;border-bottom:4px dashed var(--line)}.track i{position:absolute;left:0;bottom:2px;font-size:2rem;font-style:normal;transition:left .08s}.track b{position:absolute;right:0;bottom:2px;font-size:2rem}")
