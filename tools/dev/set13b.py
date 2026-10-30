import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 퀴즈 버저 ----------
make(H+"quiz-buzzer.html", "퀴즈 버저", "🔔", 45, "quiz-buzzer-v1",
 "가족 퀴즈 대회용 <b>버저</b>예요! 진행자가 문제를 읽고 <b>'문제 시작'</b>을 누르면, 참가자들이 <b>자기 버튼을 가장 먼저</b> 눌러요. 제일 먼저 누른 사람에게 답할 권리가 생기고, 진행자가 ⭕/❌를 눌러 점수를 줘요.",
 r'''  <div class="seg" id="np" style="--n:3"><button type="button" data-n="2">2명</button><button type="button" data-n="3" class="on">3명</button><button type="button" data-n="4">4명</button></div>
  <div class="card center"><p class="big" id="state" style="min-height:1.4em">문제를 읽은 뒤 시작을 누르세요</p></div>
  <div class="bz" id="bz"></div>
  <div class="row" id="judge" hidden><button class="btn ghost" id="no" type="button">❌ 오답</button><button class="btn" id="yes" type="button">⭕ 정답 (+1점)</button></div>
  <button class="btn" id="start" type="button">문제 시작</button>
  <button class="btn ghost" id="reset" type="button">점수 초기화</button>''',
 r'''const COLS = ["#e4572e", "#2f6fdf", "#1f9d62", "#d9a400"], NAMES = ["빨강", "파랑", "초록", "노랑"];
let np = 3, pts = [0, 0, 0, 0], live = false, winner = -1, locked = [false, false, false, false];
function render() { $("bz").style.gridTemplateColumns = `repeat(${np > 2 ? 2 : np}, 1fr)`; $("bz").innerHTML = Array.from({ length: np }, (_, k) => `<button type="button" class="b${winner === k ? " win" : ""}${locked[k] ? " lock" : ""}" data-k="${k}" style="background:${COLS[k]}"><span>${NAMES[k]}</span><b>${pts[k]}점</b></button>`).join(""); }
function startQ() { live = true; winner = -1; locked = [false, false, false, false]; $("state").textContent = "🔔 눌러요!"; $("judge").hidden = true; $("start").hidden = true; render(); }
function buzz(k) { if (!live || locked[k]) return; live = false; winner = k; $("state").textContent = `${NAMES[k]} 팀이 가장 먼저 눌렀어요!`; if (navigator.vibrate) navigator.vibrate(120); $("judge").hidden = false; render(); }
$("yes").onclick = () => { pts[winner]++; $("state").textContent = `⭕ ${NAMES[winner]} 정답! +1점`; $("judge").hidden = true; $("start").hidden = false; $("start").textContent = "다음 문제"; winner = -1; render(); };
$("no").onclick = () => { locked[winner] = true; if (locked.slice(0, np).every(Boolean)) { $("state").textContent = "모두 틀렸어요! 정답을 알려 주세요"; $("judge").hidden = true; $("start").hidden = false; $("start").textContent = "다음 문제"; winner = -1; render(); return; } live = true; winner = -1; $("state").textContent = `❌ 오답! 다른 팀은 누르세요 🔔`; $("judge").hidden = true; render(); };
$("bz").addEventListener("pointerdown", e => { const b = e.target.closest("[data-k]"); if (b) { e.preventDefault(); buzz(+b.dataset.k); } });
$("np").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#np button").forEach(x => x.classList.toggle("on", x === b)); np = +b.dataset.n; pts = [0, 0, 0, 0]; live = false; winner = -1; $("start").hidden = false; $("start").textContent = "문제 시작"; $("judge").hidden = true; render(); });
$("start").onclick = startQ; $("reset").onclick = () => { pts = [0, 0, 0, 0]; render(); }; render();''',
 css=".bz{display:grid;gap:10px}.bz .b{border:0;border-radius:18px;min-height:130px;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-family:var(--font-display);font-size:1.4rem;touch-action:manipulation}.bz .b b{font-weight:400;font-size:2.2rem}.bz .b.lock{opacity:.35}.bz .b.win{outline:6px solid var(--fg);outline-offset:-6px}")

# ---------- 피그 주사위 ----------
make(H+"pig-dice.html", "피그 주사위", "🐷", 345, "pigdice-best-v1",
 "차례마다 주사위를 <b>굴려서 나온 눈을 모아요</b>. 원하는 때 <b>'저금'</b>을 누르면 모은 점수가 내 점수가 돼요. 하지만 <b>1이 나오면</b> 이번 차례에 모은 점수를 모두 잃고 차례가 넘어가요! 먼저 <b>100점</b>을 모으는 사람이 이겨요. 컴퓨터와 겨뤄 보세요.",
 r'''  <div class="stats"><div class="stat"><small>나</small><b id="s1">0</b></div><div class="stat"><small>이번 차례</small><b id="t">0</b></div><div class="stat"><small>컴퓨터</small><b id="s2">0</b></div></div>
  <div class="card center"><p class="big" id="die" style="font-size:5rem;line-height:1.2">🎲</p><p class="muted" id="msg">주사위를 굴려 보세요</p></div>
  <div class="row"><button class="btn" id="roll" type="button">🎲 굴리기</button><button class="btn ghost" id="bank" type="button">💰 저금</button></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const FACE = ["", "1", "2", "3", "4", "5", "6"], GOAL = 100;
let s = [0, 0], turnSum = 0, who = 0, over = false, busy = false, wins = ld(KEY) || 0, tempo = 1;
function render() { $("s1").textContent = s[0]; $("s2").textContent = s[1]; $("t").textContent = turnSum; $("roll").disabled = $("bank").disabled = who !== 0 || over || busy; }
function newGame() { s = [0, 0]; turnSum = 0; who = 0; over = false; busy = false; $("die").textContent = "🎲"; $("msg").textContent = "내 차례! 주사위를 굴려 보세요"; $("res").hidden = true; render(); }
function die(n) { $("die").textContent = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][n]; }
function endTurn(reason) { turnSum = 0; who = 1 - who; $("msg").textContent = reason + (who === 0 ? " 내 차례!" : " 컴퓨터 차례..."); render(); if (who === 1 && !over) setTimeout(cpu, 800 * tempo); }
function roll() { const n = ri(1, 6); die(n); if (n === 1) { endTurn(who === 0 ? "😱 1이 나왔어요! 점수를 잃었어요." : "컴퓨터가 1을 굴렸어요!"); return 0; } turnSum += n; render(); return n; }
function bank() { s[who] += turnSum; turnSum = 0; if (s[who] >= GOAL) { over = true; if (who === 0) { wins++; sv(KEY, wins); } $("res").innerHTML = `<b>${who === 0 ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"} (${s[0]} : ${s[1]})</b><p class="muted">누적 승리 ${wins}번</p>`; $("res").hidden = false; render(); return; } endTurn(who === 0 ? "💰 저금했어요." : "컴퓨터가 저금했어요."); }
function cpu() { if (over || who !== 1) return; busy = true; const goal = Math.min(GOAL - s[1], s[0] >= 80 ? 30 : 20); const step = () => { if (over || who !== 1) { busy = false; return; } if (turnSum >= goal) { busy = false; bank(); return; } const r = roll(); if (!r) { busy = false; return; } setTimeout(step, 600 * tempo); }; step(); }
$("roll").onclick = () => { if (who === 0 && !over) { roll(); } }; $("bank").onclick = () => { if (who === 0 && !over && turnSum > 0) bank(); };
$("again").onclick = newGame; newGame();''')

# ---------- 31 게임 ----------
make(H+"game-31.html", "31 게임", "🔢", 15, "game31-best-v1",
 "컴퓨터와 번갈아 가며 숫자를 <b>1부터 순서대로 1개~3개</b> 외쳐요. 예) 내가 1, 2 → 컴퓨터 3, 4, 5 …. <b>31을 말하는 사람이 져요!</b> 어떻게 해야 컴퓨터를 이길 수 있을지 생각해 보세요. 쉬움/어려움 중에 고를 수 있어요.",
 r'''  <div class="seg" id="lv" style="--n:2"><button type="button" data-l="easy" class="on">쉬움<small>컴퓨터가 가끔 실수</small></button><button type="button" data-l="hard">어려움<small>컴퓨터는 완벽해요</small></button></div>
  <div class="stats"><div class="stat"><small>현재 숫자</small><b id="cur">0</b></div><div class="stat"><small>나의 승리</small><b id="w">0</b></div><div class="stat"><small>컴퓨터 승리</small><b id="l">0</b></div></div>
  <div class="seq" id="seq"></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="row3" id="pick"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''let n = 0, turn = 0, lv = "easy", over = false, rec = ld(KEY) || [0, 0], first = 0, tempo = 1, hist = [];
function newGame() { n = 0; over = false; hist = []; first = 1 - first; turn = first; $("res").hidden = true; render(); if (turn === 1) setTimeout(cpu, 600 * tempo); }
function render() { $("cur").textContent = n; $("w").textContent = rec[0]; $("l").textContent = rec[1]; $("seq").innerHTML = hist.map(h => `<span class="${h.w ? "me" : "cp"}">${h.v}</span>`).join(""); $("pick").innerHTML = [1, 2, 3].map(k => `<button type="button" class="btn" data-k="${k}" ${turn !== 0 || over || n + k > 31 && k > 1 && false ? "disabled" : ""}>${k}개</button>`).join(""); $("msg").textContent = over ? "" : turn === 0 ? "내 차례! 1~3개를 외쳐요" : "컴퓨터 차례..."; }
function say(k, w) { for (let i = 0; i < k && n < 31; i++) { n++; hist.push({ v: n, w }); } if (n >= 31) { over = true; const lose = hist[hist.length - 1].w; if (lose) rec[1]++; else rec[0]++; sv(KEY, rec); $("res").innerHTML = `<b>${lose ? "😢 내가 31을 말했어요… 졌어요" : "🎉 컴퓨터가 31을 말했어요! 내가 이겼어요"}</b>`; $("res").hidden = false; render(); return; } turn = 1 - turn; render(); if (turn === 1) setTimeout(cpu, 700 * tempo); }
function cpu() { if (over || turn !== 1) return; let k = (31 - 1 - n) % 4 || 0; k = (30 - n) % 4; if (k === 0) k = ri(1, 3); else if (lv === "easy" && Math.random() < .35) k = ri(1, 3); say(k, false); }
$("pick").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && turn === 0 && !over) say(+b.dataset.k, true); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); lv = b.dataset.l; first = 1; newGame(); });
$("again").onclick = newGame; first = 1; newGame();''',
 css=".seq{display:flex;flex-wrap:wrap;gap:4px;min-height:44px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px}.seq span{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9rem;color:#fff}.seq .me{background:#2f6fdf}.seq .cp{background:#e4572e}.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}")

# ---------- 카드 짝 맞추기 2인 ----------
make(H+"memory-duel.html", "카드 짝 대결 (2인)", "🂠", 195, "memoryduel-v1",
 "둘이서 <b>번갈아</b> 카드를 두 장씩 뒤집어요. <b>그림이 같으면 내 점수 1점</b>을 얻고 한 번 더! 다르면 다시 뒤집히고 상대 차례예요. 카드를 모두 짝 맞췄을 때 점수가 더 높은 사람이 이겨요.",
 r'''  <div class="stats"><div class="stat"><small id="n1">🔵 1번</small><b id="s1">0</b></div><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">🔵</b></div><div class="stat"><small id="n2">🔴 2번</small><b id="s2">0</b></div></div>
  <div class="mg" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const EMO = "🍎🍌🍇🍓🍊🍑🍉🍍🥕🐶🐱🐰🐻🐼🦊🐸🌸🌻🚗🚀🎈🎁⚽🎵".match(/\p{Extended_Pictographic}️?/gu);
let cards = [], open = [], cur = 0, sc = [0, 0], lock = false, tempo = 1;
function newGame() { const f = shuf(EMO).slice(0, 8); cards = shuf([...f, ...f]).map((e, k) => ({ e, up: false, done: false })); open = []; cur = 0; sc = [0, 0]; lock = false; $("res").hidden = true; render(); }
function render() { $("grid").innerHTML = cards.map((c, k) => `<button type="button" class="mc${c.up || c.done ? " up" : ""}${c.done ? " done" + (c.by) : ""}" data-k="${k}" aria-label="카드 ${k + 1}"><span>${c.up || c.done ? c.e : ""}</span></button>`).join(""); $("s1").textContent = sc[0]; $("s2").textContent = sc[1]; $("turn").textContent = cards.every(c => c.done) ? "-" : cur ? "🔴" : "🔵"; }
async function flip(k) {
  if (lock || cards[k].up || cards[k].done) return; cards[k].up = true; open.push(k); render(); if (open.length < 2) return; lock = true; await new Promise(r => setTimeout(r, 750 * tempo));
  const [a, b] = open; if (cards[a].e === cards[b].e) { cards[a].done = cards[b].done = true; cards[a].by = cards[b].by = cur; cards[a].up = cards[b].up = false; sc[cur]++; } else { cards[a].up = cards[b].up = false; cur = 1 - cur; }
  open = []; lock = false; render();
  if (cards.every(c => c.done)) $("res").innerHTML = `<b>${sc[0] === sc[1] ? "비겼어요 🤝" : sc[0] > sc[1] ? "🔵 1번 승리! 🎉" : "🔴 2번 승리! 🎉"} (${sc[0]} : ${sc[1]})</b>`, $("res").hidden = false;
}
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) flip(+b.dataset.k); });
$("again").onclick = newGame; newGame();''',
 css=".mg{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.mc{aspect-ratio:1;border-radius:12px;border:2px solid var(--line);background:var(--accent);padding:0;font-size:clamp(1.6rem,9vw,2.4rem);display:flex;align-items:center;justify-content:center;min-width:0}.mc.up{background:var(--surface)}.mc.done{background:var(--surface);opacity:.75}.mc.done0{border-color:#2f6fdf}.mc.done1{border-color:#e4572e}")

# ---------- 순서 정하기 ----------
make(H+"order-picker.html", "순서·벌칙 정하기", "📋", 90, "order-picker-v1",
 "이름을 적고 <b>'순서 정하기'</b>를 누르면 모두의 순서가 무작위로 정해져요. <b>'벌칙자 뽑기'</b>는 한 명을 랜덤으로 골라 줘요. 누가 먼저 할지, 누가 설거지할지 공평하게 정해 보세요!",
 r'''  <div class="card"><div id="names"></div><div class="row"><button class="btn ghost" id="add" type="button">+ 이름 추가</button><button class="btn ghost" id="clear" type="button">모두 지우기</button></div></div>
  <div class="row"><button class="btn" id="order" type="button">🔀 순서 정하기</button><button class="btn" id="pick" type="button" style="background:var(--bad)">🎯 벌칙자 뽑기</button></div>
  <div class="card center" id="out" hidden></div>''',
 r'''let names = ld(KEY) || ["아빠", "엄마", "나", "동생"];
function save() { sv(KEY, names); }
function render() { $("names").innerHTML = names.map((n, k) => `<div class="nr"><span>${k + 1}</span><input type="text" value="${esc(n)}" data-k="${k}" maxlength="8" placeholder="이름" aria-label="이름 ${k + 1}"><button type="button" data-d="${k}" aria-label="삭제">✕</button></div>`).join(""); }
const valid = () => names.map(n => n.trim()).filter(Boolean);
$("names").addEventListener("input", e => { const k = e.target.dataset.k; if (k !== undefined) { names[+k] = e.target.value; save(); } });
$("names").addEventListener("click", e => { const d = e.target.closest("[data-d]"); if (d) { names.splice(+d.dataset.d, 1); save(); render(); } });
$("add").onclick = () => { if (names.length < 12) { names.push(""); render(); } }; $("clear").onclick = () => { names = [""]; save(); render(); };
$("order").onclick = () => { const v = valid(); if (v.length < 2) return show("이름을 2개 이상 적어 주세요"); show("<b>🔀 순서</b>" + shuf(v).map((n, k) => `<div class="ord"><b>${k + 1}</b> ${esc(n)}</div>`).join("")); };
$("pick").onclick = async () => { const v = valid(); if (v.length < 2) return show("이름을 2개 이상 적어 주세요"); for (let k = 0; k < 14; k++) { show(`<p class="big">🎯 ${esc(v[ri(0, v.length - 1)])}</p>`); await new Promise(r => setTimeout(r, 70 + k * 18)); } const w = v[ri(0, v.length - 1)]; show(`<b>벌칙자는…</b><p class="big">😱 ${esc(w)}</p>`); if (navigator.vibrate) navigator.vibrate(200); };
function show(h) { $("out").hidden = false; $("out").innerHTML = h; } render();''',
 css=".nr{display:flex;align-items:center;gap:8px;margin-bottom:8px}.nr span{width:24px;text-align:center;color:var(--muted);font-weight:700}.nr input{flex:1}.nr button{width:36px;height:36px;border-radius:50%;border:1px solid var(--line);background:var(--soft);padding:0}.ord{padding:8px 12px;margin-top:6px;background:var(--soft);border-radius:10px;font-size:1.1rem;text-align:left}.ord b{display:inline-block;width:28px;color:var(--accent)}")
