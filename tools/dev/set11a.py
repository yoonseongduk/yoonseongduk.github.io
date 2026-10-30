import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 스트룹 ----------
make(H+"stroop-color.html", "글자 색깔 맞히기", "🎨", 330, "stroop-best-v1",
 "화면에 나온 <b>글자의 뜻이 아니라, 글자가 칠해진 색깔</b>을 맞혀 보세요! 예를 들어 <b style='color:#d6453a'>파랑</b>이라고 쓰여 있지만 빨간색이면 '빨강'을 눌러야 해요. 30초 동안 몇 개 맞히는지 겨뤄요.",
 r'''  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">30</b></div><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="big" id="word" style="font-size:clamp(3rem,18vw,4.5rem)">준비</p></div>
  <div class="opts4" id="opts"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''const COL = [["빨강", "#d6453a"], ["파랑", "#2f6fdf"], ["초록", "#1f9d62"], ["노랑", "#d9a400"]];
let score = 0, sec = 30, timer = 0, run = false, cur = null, best = ld(KEY) || 0, tempo = 1, miss = 0;
function next() { const w = ri(0, 3); let c = ri(0, 3); if (Math.random() < 0.8) while (c === w) c = ri(0, 3); cur = { w, c }; $("word").textContent = COL[w][0]; $("word").style.color = COL[c][1]; }
function start() { score = 0; miss = 0; sec = 30; run = true; $("res").hidden = true; $("start").hidden = true; $("opts").innerHTML = COL.map((c, k) => `<button type="button" data-k="${k}" style="background:${c[1]}">${c[0]}</button>`).join(""); next(); upd(); clearInterval(timer); timer = setInterval(() => { sec--; upd(); if (sec <= 0) end(); }, 1000 * tempo); }
function upd() { $("score").textContent = score; $("time").textContent = sec; $("best").textContent = best; }
function pick(k) { if (!run) return; if (k === cur.c) score++; else { miss++; score = Math.max(0, score - 1); } upd(); next(); }
function end() { run = false; clearInterval(timer); let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>${score}점!</b><p class="muted">틀린 횟수 ${miss}번${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; $("opts").innerHTML = ""; $("word").textContent = "끝!"; $("word").style.color = ""; upd(); }
$("opts").addEventListener("pointerdown", e => { const b = e.target.closest("[data-k]"); if (b) { e.preventDefault(); pick(+b.dataset.k); } });
$("start").onclick = start; upd();''',
 css=".opts4{display:grid;grid-template-columns:1fr 1fr;gap:10px}.opts4 button{border:0;border-radius:14px;padding:18px 0;color:#fff;font-family:var(--font-display);font-size:1.5rem;text-shadow:0 1px 2px rgba(0,0,0,.4)}")

# ---------- 구구단 스피드 ----------
make(H+"times-table.html", "구구단 스피드", "✖️", 48, "timestable-best-v1",
 "구구단 문제를 <b>60초 동안 최대한 많이</b> 풀어 보세요! 숫자 키패드로 답을 입력하고 ✔를 누르거나, 정답 자릿수가 다 차면 자동으로 넘어가요. 단을 골라서 연습할 수도 있어요.",
 r'''  <div class="chips" id="dans"></div>
  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">60</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="big" id="q">준비</p><p class="big" id="ans" style="color:var(--accent);min-height:1.3em"></p></div>
  <div class="pad" id="pad"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''let dans = new Set([2, 3, 4, 5, 6, 7, 8, 9]), a = 0, b = 0, typed = "", score = 0, sec = 60, run = false, timer = 0, best = ld(KEY) || 0, tempo = 1, tries = 0;
function chips() { $("dans").innerHTML = [2, 3, 4, 5, 6, 7, 8, 9].map(d => `<button type="button" class="chip${dans.has(d) ? " on" : ""}" data-d="${d}">${d}단</button>`).join(""); }
function nextQ() { const ds = [...dans]; a = ds[ri(0, ds.length - 1)]; b = ri(1, 9); typed = ""; $("q").textContent = `${a} × ${b} = ?`; $("ans").textContent = ""; }
function start() { if (!dans.size) return; score = 0; tries = 0; sec = 60; run = true; $("res").hidden = true; $("start").hidden = true; nextQ(); upd(); clearInterval(timer); timer = setInterval(() => { sec--; upd(); if (sec <= 0) end(); }, 1000 * tempo); }
function upd() { $("score").textContent = score; $("time").textContent = sec; $("best").textContent = best; }
function key(v) {
  if (!run) return; if (v === "x") { typed = typed.slice(0, -1); } else if (v === "ok") { submit(); return; } else if (typed.length < 2) typed += v; $("ans").textContent = typed;
  if (typed.length === String(a * b).length) submit();
}
function submit() { if (!typed) return; tries++; const ok = +typed === a * b; if (ok) score++; $("ans").style.color = ok ? "var(--ok)" : "var(--bad)"; upd(); setTimeout(() => { $("ans").style.color = "var(--accent)"; if (run) nextQ(); }, 120 * tempo); typed = ""; }
function end() { run = false; clearInterval(timer); let note = ""; if (dans.size === 8 && score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>${score}개 맞혔어요!</b><p class="muted">푼 문제 ${tries}개 · 정확도 ${tries ? Math.round(score / tries * 100) : 0}%${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; $("q").textContent = "끝!"; $("ans").textContent = ""; upd(); }
$("pad").innerHTML = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map(n => `<button type="button" data-v="${n}">${n}</button>`).join("") + `<button type="button" data-v="x">⌫</button><button type="button" data-v="ok" class="okb">✔</button>`;
$("pad").addEventListener("pointerdown", e => { const t = e.target.closest("[data-v]"); if (t) { e.preventDefault(); key(t.dataset.v); } });
$("dans").addEventListener("click", e => { const t = e.target.closest("[data-d]"); if (t && !run) { const d = +t.dataset.d; dans.has(d) ? dans.delete(d) : dans.add(d); chips(); } });
$("start").onclick = start; chips(); upd();''',
 css=".pad{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}.pad button{padding:14px 0;border-radius:12px;border:1px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.5rem;min-width:0}.pad .okb{background:var(--accent);color:var(--accent-fg);border:0}.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.9rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}")

# ---------- 위치 기억 ----------
make(H+"spot-memory.html", "위치 기억", "🎯", 5, "spotmemory-best-v1",
 "잠깐 <b>빨갛게 켜지는 칸들의 위치</b>를 기억했다가, 사라지면 같은 칸을 눌러 보세요. 맞힐수록 켜지는 칸이 늘어나요. 한 번 틀리면 끝!",
 r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lv">1</b></div><div class="stat"><small>최고 단계</small><b id="best">0</b></div><div class="stat"><small>상태</small><b id="st" style="font-size:1.05rem">준비</b></div></div>
  <div class="sg" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''let lv = 1, targets = new Set(), got = new Set(), state = "idle", best = ld(KEY) || 0, tempo = 1, gen = 0, n = 3;
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
const sizeFor = l => (l < 4 ? 3 : l < 9 ? 4 : 5);
function build() { n = sizeFor(lv); $("grid").style.gridTemplateColumns = `repeat(${n}, 1fr)`; $("grid").innerHTML = Array.from({ length: n * n }, (_, k) => `<button type="button" class="sc" data-k="${k}" aria-label="칸 ${k + 1}"></button>`).join(""); }
function setSt(t) { $("st").textContent = t; $("lv").textContent = lv; $("best").textContent = best; }
const cell = k => document.querySelector(`[data-k="${k}"]`);
async function show() { const my = ++gen; state = "show"; build(); got = new Set(); setSt("잘 보세요"); const cnt = Math.min(2 + lv, Math.floor(n * n / 2)); targets = new Set(shuf([...Array(n * n).keys()]).slice(0, cnt)); await sleep(600); if (my !== gen) return; targets.forEach(k => cell(k).classList.add("lit")); await sleep(900 + cnt * 150); if (my !== gen) return; targets.forEach(k => cell(k).classList.remove("lit")); state = "input"; setSt("눌러 보세요"); }
function start() { lv = 1; $("res").hidden = true; $("start").hidden = true; show(); }
async function press(k) {
  if (state !== "input" || got.has(k)) return;
  if (!targets.has(k)) { state = "over"; gen++; cell(k).classList.add("bad"); targets.forEach(t => { if (!got.has(t)) cell(t).classList.add("miss"); }); const reached = lv - 1; if (reached > best) { best = reached; sv(KEY, best); } setSt("끝"); $("res").innerHTML = `<b>${reached}단계까지 성공!</b><p class="muted">${reached >= 8 ? "기억력 천재 🧠" : reached >= 4 ? "잘했어요 👍" : "다시 도전해 볼까요?"}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; return; }
  got.add(k); cell(k).classList.add("ok");
  if (got.size === targets.size) { state = "wait"; setSt("정답! 👍"); await sleep(700); lv++; show(); }
}
$("grid").addEventListener("pointerdown", e => { const c = e.target.closest("[data-k]"); if (c) { e.preventDefault(); press(+c.dataset.k); } });
$("start").onclick = start; build(); setSt("준비");''',
 css=".sg{display:grid;gap:8px;max-width:380px;margin:0 auto;width:100%;touch-action:manipulation}.sc{aspect-ratio:1;border-radius:14px;border:2px solid var(--line);background:var(--surface);padding:0;min-width:0}.sc.lit{background:#e53935;border-color:#e53935}.sc.ok{background:var(--ok);border-color:var(--ok)}.sc.bad{background:var(--bad);border-color:var(--bad)}.sc.miss{border-color:#e53935;border-style:dashed}")

# ---------- 숫자 거꾸로 기억 ----------
make(H+"reverse-memory.html", "거꾸로 기억", "🔁", 215, "reversememory-best-v1",
 "화면에 나타나는 <b>숫자를 잘 보고</b>, 사라지면 <b>거꾸로(마지막 숫자부터)</b> 입력해 보세요. 예) 3 8 1 이었다면 1 → 8 → 3 순서로! 단계가 오를수록 숫자가 길어져요.",
 r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lv">1</b></div><div class="stat"><small>최고 단계</small><b id="best">0</b></div><div class="stat"><small>상태</small><b id="st" style="font-size:1.05rem">준비</b></div></div>
  <div class="card center"><p class="big" id="show" style="font-size:clamp(2.2rem,12vw,3.4rem);letter-spacing:.15em;min-height:1.4em"></p><p class="big" id="typed" style="color:var(--accent);min-height:1.4em"></p></div>
  <div class="pad" id="pad"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''let lv = 1, seq = [], typed = [], state = "idle", best = ld(KEY) || 0, tempo = 1, gen = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
function setSt(t) { $("st").textContent = t; $("lv").textContent = lv; $("best").textContent = best; }
async function round() { const my = ++gen; state = "show"; typed = []; $("typed").textContent = ""; setSt("잘 보세요"); seq = Array.from({ length: lv + 2 }, () => ri(0, 9)); await sleep(500);
  for (const d of seq) { if (my !== gen) return; $("show").textContent = d; await sleep(650); $("show").textContent = ""; await sleep(200); } if (my !== gen) return; state = "input"; setSt("거꾸로 입력!"); $("show").textContent = "?"; }
function start() { lv = 1; $("res").hidden = true; $("start").hidden = true; round(); }
async function key(v) {
  if (state !== "input") return; if (v === "x") { typed.pop(); $("typed").textContent = typed.join(" "); return; }
  typed.push(+v); $("typed").textContent = typed.join(" "); const want = [...seq].reverse();
  if (typed[typed.length - 1] !== want[typed.length - 1]) { state = "over"; gen++; const reached = lv - 1; if (reached > best) { best = reached; sv(KEY, best); } setSt("끝"); $("show").textContent = want.join(" "); $("res").innerHTML = `<b>${reached}단계까지 성공!</b><p class="muted">정답(거꾸로): ${want.join(" ")}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; return; }
  if (typed.length === want.length) { state = "wait"; setSt("정답! 👍"); await sleep(700); lv++; round(); }
}
$("pad").innerHTML = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0].map(n => `<button type="button" data-v="${n}">${n}</button>`).join("") + `<button type="button" data-v="x" class="er">⌫</button>`;
$("pad").addEventListener("pointerdown", e => { const t = e.target.closest("[data-v]"); if (t) { e.preventDefault(); key(t.dataset.v); } });
$("start").onclick = start; setSt("준비");''',
 css=".pad{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.pad button{padding:14px 0;border-radius:12px;border:1px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:1.5rem;min-width:0}")

# ---------- 리듬 탭 ----------
make(H+"rhythm-tap.html", "리듬 탭", "🥁", 350, "rhythmtap-best-v1",
 "위에서 <b>내려오는 동그라미가 아래 선에 닿을 때</b> 그 줄을 눌러 보세요. 정확할수록 높은 점수! 놓치면 하트가 줄고, 하트 3개를 모두 잃으면 끝이에요.",
 r'''  <div class="stats"><div class="stat"><small>점수</small><b id="score">0</b></div><div class="stat"><small>콤보</small><b id="combo">0</b></div><div class="stat"><small>하트</small><b id="hp">❤️❤️❤️</b></div></div>
  <div class="lane" id="lane"><div class="line"></div></div>
  <div class="taps" id="taps"><button type="button" data-l="0">●</button><button type="button" data-l="1">●</button><button type="button" data-l="2">●</button><button type="button" data-l="3">●</button></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
 r'''const LANES = 4, FALL = 1.6;   // FALL: 위에서 아래 선까지 내려오는 시간(초)
let notes = [], score = 0, combo = 0, maxCombo = 0, hp = 3, run = false, last = 0, spawnT = 0, gapT = 0.7, best = ld(KEY) || 0, raf = 0, tempo = 1, el = {};
function reset() { notes = []; score = 0; combo = 0; maxCombo = 0; hp = 3; spawnT = 0.6; gapT = 0.75; $("lane").querySelectorAll(".note").forEach(n => n.remove()); upd(); }
function upd() { $("score").textContent = score; $("combo").textContent = combo; $("hp").textContent = "❤️".repeat(hp) + "🖤".repeat(3 - hp); }
function spawn() { const l = ri(0, LANES - 1), d = document.createElement("div"); d.className = "note"; d.style.left = (l * 25 + 12.5) + "%"; $("lane").appendChild(d); notes.push({ l, t: 0, d }); }
function update(dt) {
  if (!run) return; spawnT -= dt; if (spawnT <= 0) { spawn(); gapT = Math.max(0.32, gapT - 0.008); spawnT = gapT * (0.8 + Math.random() * 0.5); }
  for (const n of notes) { n.t += dt / FALL; n.d.style.top = (n.t * 86) + "%"; }
  for (let k = notes.length - 1; k >= 0; k--) if (notes[k].t > 1.18) { notes[k].d.remove(); notes.splice(k, 1); miss(); }
}
function miss() { combo = 0; hp--; flash("놓쳤어요!", false); upd(); if (hp <= 0) end(); }
function flash(t, ok) { $("msg").textContent = t; $("msg").style.color = ok ? "var(--ok)" : "var(--bad)"; }
function hit(l) {
  if (!run) return; const c = notes.filter(n => n.l === l).sort((a, b) => Math.abs(a.t - 1) - Math.abs(b.t - 1))[0]; if (!c) { combo = 0; flash("빈 줄!", false); upd(); return; }
  const diff = Math.abs(c.t - 1) * FALL;      // 초 단위 오차
  if (diff > 0.28) { combo = 0; flash("너무 일러요", false); upd(); return; }
  const pts = diff < 0.07 ? 100 : diff < 0.15 ? 60 : 30; combo++; maxCombo = Math.max(maxCombo, combo); score += pts + Math.min(combo, 20) * 2; flash(diff < 0.07 ? "완벽! ✨" : diff < 0.15 ? "좋아요!" : "조금 어긋났어요", true);
  c.d.remove(); notes.splice(notes.indexOf(c), 1); upd();
}
function loop(ts) { if (!run) return; const dt = Math.min(0.05, (ts - last) / 1000 * tempo); last = ts; update(dt); raf = requestAnimationFrame(loop); }
function start() { reset(); run = true; $("res").hidden = true; $("start").hidden = true; flash("", true); last = performance.now(); raf = requestAnimationFrame(loop); }
function end() { run = false; cancelAnimationFrame(raf); let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>${score}점!</b><p class="muted">최고 콤보 ${maxCombo} · 최고 점수 ${best}${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; }
$("taps").addEventListener("pointerdown", e => { const b = e.target.closest("[data-l]"); if (b) { e.preventDefault(); hit(+b.dataset.l); b.classList.add("p"); setTimeout(() => b.classList.remove("p"), 90); } });
$("start").onclick = start; upd();''',
 css=".lane{position:relative;height:min(52vh,420px);background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;background-image:linear-gradient(to right,transparent 24.8%,var(--line) 25%,transparent 25.2%,transparent 49.8%,var(--line) 50%,transparent 50.2%,transparent 74.8%,var(--line) 75%,transparent 75.2%)}.line{position:absolute;left:0;right:0;top:86%;height:4px;margin-top:16px;background:var(--accent)}.note{position:absolute;width:44px;height:44px;margin-left:-22px;border-radius:50%;background:var(--accent);box-shadow:0 2px 0 rgba(0,0,0,.25)}.taps{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.taps button{padding:22px 0;border-radius:14px;border:2px solid var(--accent);background:var(--surface);color:var(--accent);font-size:1.5rem;touch-action:manipulation}.taps button.p{background:var(--accent);color:var(--accent-fg)}")
