import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 원카드 ----------
make(H+"one-card.html", "원카드", "🂡", 8, "onecard-best-v1",
 "같은 <b>무늬</b>나 같은 <b>숫자</b>의 카드를 내서 손에 든 카드를 <b>먼저 모두 없애는</b> 사람이 이겨요. 낼 카드가 없으면 '카드 받기'를 눌러요. 특별 카드: <b>2</b>=상대 +2장, <b>A</b>=상대 +3장 (같은 숫자로 막으면 더해져 넘어가요), <b>J·Q·K</b>=한 번 더, <b>7</b>=무늬 바꾸기. 카드가 15장이 되면 져요!",
 r'''  <div class="stats"><div class="stat"><small>컴퓨터 카드</small><b id="cn">0</b></div><div class="stat"><small>내 카드</small><b id="mn">0</b></div><div class="stat"><small>누적 승리</small><b id="wins">0</b></div></div>
  <div class="table"><button type="button" class="oc back" id="deckb" aria-label="카드 받기">🂠<small id="atk"></small></button><div class="oc" id="top"></div><div class="want" id="want"></div></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="oh" id="hand"></div>
  <div class="seg" id="suits" style="--n:4" hidden></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const SU = ["♠", "♥", "♦", "♣"], RK = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
let deck = [], disc = [], mine = [], cpu = [], turn = 0, over = false, busy = false, atk = 0, atkRank = -1, want = -1, wins = ld(KEY) || 0, tempo = 1, pickSuit = false;
const red = c => c.s === 1 || c.s === 2, nm = c => RK[c.r] + SU[c.s];
function mk() { return shuf(Array.from({ length: 52 }, (_, k) => ({ r: k % 13, s: Math.floor(k / 13) }))); }
function draw(n) { const out = []; for (let k = 0; k < n; k++) { if (!deck.length) { const t = disc.pop(); deck = shuf(disc); disc = [t]; } if (deck.length) out.push(deck.pop()); } return out; }
function newGame() { deck = mk(); mine = deck.splice(0, 7); cpu = deck.splice(0, 7); disc = [deck.pop()]; while ([0, 1, 6, 10, 11, 12].includes(disc[0].r)) { deck.unshift(disc.pop()); disc = [deck.pop()]; } turn = 0; over = false; busy = false; atk = 0; atkRank = -1; want = -1; pickSuit = false; $("res").hidden = true; $("suits").hidden = true; $("msg").textContent = "내 차례! 낼 카드를 고르세요"; render(); }
const topCard = () => disc[disc.length - 1];
function canPlay(c) { if (atk > 0) return c.r === atkRank; const t = topCard(), s = want >= 0 ? want : t.s; return c.r === t.r || c.s === s || (c.r === 6 && false); }
function render() {
  const t = topCard(); $("top").className = "oc" + (red(t) ? " red" : ""); $("top").innerHTML = `<b>${nm(t)}</b>`; $("want").textContent = want >= 0 ? `바뀐 무늬: ${SU[want]}` : ""; $("atk").textContent = atk ? "+" + atk : "";
  $("hand").innerHTML = mine.map((c, k) => `<button type="button" class="oc${red(c) ? " red" : ""}${turn === 0 && !over && !busy && canPlay(c) ? " can" : ""}" data-k="${k}" ${turn !== 0 || over || busy || pickSuit ? "disabled" : ""}><b>${nm(c)}</b></button>`).join("");
  $("cn").textContent = cpu.length; $("mn").textContent = mine.length; $("wins").textContent = wins; $("deckb").disabled = turn !== 0 || over || busy || pickSuit;
}
function finish(w) { over = true; if (w) { wins++; sv(KEY, wins); } $("res").innerHTML = `<b>${w ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"}</b><p class="muted">누적 승리 ${wins}번</p>`; $("res").hidden = false; render(); }
function playCard(hand, k, who) {
  const c = hand.splice(k, 1)[0]; disc.push(c); want = -1; let again = false, msg = ""; 
  if (c.r === 1) { atk += 2; atkRank = 1; } else if (c.r === 0) { atk += 3; atkRank = 0; } else if (c.r >= 10) { again = true; msg = "한 번 더!"; } 
  if (!hand.length) { finish(who === 0); return "end"; } return { again, seven: c.r === 6 };
}
async function after(who, res) {
  if (res === "end") return; if (res.seven) { if (who === 0) { pickSuit = true; $("suits").hidden = false; $("suits").innerHTML = SU.map((s, k) => `<button type="button" data-s="${k}">${s}</button>`).join(""); render(); return; } want = cpuSuit(); $("msg").textContent = `컴퓨터가 무늬를 ${SU[want]}(으)로 바꿨어요`; }
  endTurn(who, res.again);
}
function endTurn(who, again) { if (over) return; if (!again) turn = 1 - turn; render(); if (turn === 1 && !over) { busy = true; render(); setTimeout(cpuMove, 900 * tempo); } else if (turn === 0) { busy = false; $("msg").textContent = again ? "한 번 더 내세요!" : atk ? `공격 받았어요! 같은 숫자로 막거나 카드 ${atk}장을 받으세요` : "내 차례!"; render(); } }
function takeCards(who) { const hand = who === 0 ? mine : cpu, n = atk || 1; hand.push(...draw(n)); atk = 0; atkRank = -1; if (hand.length >= 15) { finish(who === 1); return true; } return false; }
function cpuSuit() { const cnt = [0, 0, 0, 0]; cpu.forEach(c => cnt[c.s]++); return cnt.indexOf(Math.max(...cnt)); }
async function cpuMove() {
  const pl = cpu.map((c, k) => [c, k]).filter(([c]) => canPlay(c)); busy = true;
  if (!pl.length) { const n = atk || 1; if (takeCards(1)) return; $("msg").textContent = `컴퓨터가 카드 ${n}장을 받았어요`; turn = 0; busy = false; if (atk === 0 && n > 1) $("msg").textContent += " — 내 차례!"; render(); return; }
  pl.sort((a, b) => (b[0].r === 1 || b[0].r === 0 ? 2 : b[0].r >= 10 ? 1 : 0) - (a[0].r === 1 || a[0].r === 0 ? 2 : a[0].r >= 10 ? 1 : 0) + (Math.random() - .5)); const [c, k] = pl[0]; const res = playCard(cpu, k, 1); $("msg").textContent = `컴퓨터가 ${nm(c)}를 냈어요${res !== "end" && res.again ? " (한 번 더)" : ""}`; render(); if (res === "end") return;
  if (res.again) { setTimeout(() => after(1, res), 700 * tempo); } else after(1, res);
}
$("hand").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (!b || turn !== 0 || over || busy) return; const k = +b.dataset.k; if (!canPlay(mine[k])) { $("msg").textContent = "그 카드는 낼 수 없어요"; return; } const res = playCard(mine, k, 0); render(); after(0, res); });
$("deckb").onclick = () => { if (turn !== 0 || over || busy) return; const n = atk || 1; if (takeCards(0)) return; $("msg").textContent = `카드 ${n}장을 받았어요`; turn = 1; render(); busy = true; render(); setTimeout(cpuMove, 900 * tempo); };
$("suits").addEventListener("click", e => { const b = e.target.closest("[data-s]"); if (!b) return; want = +b.dataset.s; pickSuit = false; $("suits").hidden = true; $("msg").textContent = `무늬를 ${SU[want]}(으)로 바꿨어요`; endTurn(0, false); });
$("again").onclick = newGame; newGame();''',
 css=".table{display:flex;gap:12px;align-items:center;justify-content:center}.oc{width:64px;height:90px;border-radius:10px;border:2px solid var(--line);background:#fff;color:#111;font-size:1.1rem;padding:0;display:inline-flex;align-items:center;justify-content:center;position:relative;min-width:0}.oc.red{color:#d6453a}.oc.back{background:repeating-linear-gradient(45deg,#2f6fdf,#2f6fdf 6px,#1f4fa0 6px,#1f4fa0 12px);color:#fff;font-size:1.8rem}.oc.back small{position:absolute;bottom:2px;right:6px;font-size:.9rem;background:var(--bad);border-radius:8px;padding:0 4px}.oh{display:flex;flex-wrap:wrap;gap:6px;justify-content:center}.oh .oc{width:54px;height:76px}.oh .oc.can{border-color:var(--accent);transform:translateY(-4px);box-shadow:0 3px 0 var(--accent)}.oh .oc:disabled{opacity:1}.want{font-weight:700;min-width:80px}")

# ---------- 윷놀이 ----------
make(H+"yut-nori.html", "윷놀이", "🥢", 38, "yutnori-best-v1",
 "컴퓨터와 <b>간단한 윷놀이</b>를 해요. 윷가락 4개를 던져서 나온 칸만큼 말을 움직여요. <b>도=1칸 개=2 걸=3 윷=4 모=5</b>. 윷이나 모가 나오거나 <b>상대 말을 잡으면 한 번 더</b> 던져요! 말 2개를 먼저 한 바퀴(20칸) 돌려 도착시키면 이겨요.",
 r'''  <div class="stats"><div class="stat"><small>나 도착</small><b id="d1">0/2</b></div><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">나</b></div><div class="stat"><small>컴퓨터 도착</small><b id="d2">0/2</b></div></div>
  <svg class="yb" id="svg" viewBox="0 0 300 300"></svg>
  <div class="card center"><div class="sticks" id="sticks">🥢🥢🥢🥢</div><p class="big" id="res" style="font-size:2rem;min-height:1.3em"></p><p class="muted" id="msg">윷을 던져 보세요!</p></div>
  <div class="row"><button class="btn" id="throw" type="button">🥢 윷 던지기</button></div>
  <div class="row" id="pick" hidden><button class="btn ghost" data-p="0" type="button">내 말 1 이동</button><button class="btn ghost" data-p="1" type="button">내 말 2 이동</button></div>
  <div class="res" id="fin" hidden></div>
  <button class="btn ghost" id="again" type="button">새 게임</button>''',
 r'''const NAMES = ["", "도", "개", "걸", "윷", "모"], TR = 20;
let pos = [[0, 0], [0, 0]], turn = 0, steps = 0, over = false, busy = false, wins = ld(KEY) || 0, tempo = 1, stage = "throw";   // pos[who][i]: 0 대기, 1..19 판 위, 20 도착
const fin = w => pos[w].filter(v => v >= TR).length;
function newGame() { pos = [[0, 0], [0, 0]]; turn = 0; steps = 0; over = false; busy = false; stage = "throw"; $("fin").hidden = true; $("pick").hidden = true; $("res").textContent = ""; $("msg").textContent = "윷을 던져 보세요!"; render(); }
const xy = k => { const a = (k / TR) * Math.PI * 2 + Math.PI / 2; return [150 + 115 * Math.cos(a), 150 + 115 * Math.sin(a)]; };
function render() {
  let h = `<circle cx="150" cy="150" r="115" fill="none" stroke="var(--line)" stroke-width="30"/>`; for (let k = 1; k <= TR; k++) { const [x, y] = xy(k % TR); h += `<circle cx="${x}" cy="${y}" r="9" class="cell${k === TR ? " goal" : ""}"/>`; } const [sx, sy] = xy(0); h += `<text x="${sx}" y="${sy + 28}" text-anchor="middle" class="lab">출발·도착</text>`;
  [0, 1].forEach(w => pos[w].forEach((v, i) => { if (v >= TR) return; const [x, y] = xy(v % TR), off = w === 0 ? -7 : 7; h += `<text x="${x + off}" y="${y + 5}" text-anchor="middle" class="tok">${w === 0 ? (i ? "🔵" : "🟦") : (i ? "🔴" : "🟥")}</text>`; }));
  $("svg").innerHTML = h; $("d1").textContent = fin(0) + "/2"; $("d2").textContent = fin(1) + "/2"; $("turn").textContent = over ? "-" : turn ? "컴퓨터" : "나"; $("throw").disabled = over || busy || turn !== 0 || stage !== "throw";
}
function toss() { const flat = Array.from({ length: 4 }, () => Math.random() < .5), n = flat.filter(Boolean).length; return { n: n === 0 ? 5 : n, flat }; }
function showToss(t) { $("sticks").textContent = t.flat.map(f => (f ? "▬" : "◖")).join(" "); $("res").textContent = NAMES[t.n] + (t.n >= 4 ? "!" : ""); }
function move(w, i, n) { let captured = false; pos[w][i] = Math.min(TR, pos[w][i] + n); const v = pos[w][i]; if (v > 0 && v < TR) pos[1 - w].forEach((q, j) => { if (q === v) { pos[1 - w][j] = 0; captured = true; } }); return captured; }
function checkWin() { for (const w of [0, 1]) if (fin(w) === 2) { over = true; if (w === 0) { wins++; sv(KEY, wins); } $("fin").innerHTML = `<b>${w === 0 ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"}</b><p class="muted">누적 승리 ${wins}번</p>`; $("fin").hidden = false; render(); return true; } return false; }
$("throw").onclick = () => { if (turn !== 0 || over || busy) return; const t = toss(); showToss(t); steps = t.n; const movable = [0, 1].filter(i => pos[0][i] < TR); if (movable.length === 1) return finishMove(0, movable[0]); stage = "pick"; $("pick").hidden = false; $("msg").textContent = `${NAMES[steps]}! 어떤 말을 움직일까요?`; render(); };
$("pick").addEventListener("click", e => { const b = e.target.closest("[data-p]"); if (!b || stage !== "pick") return; const i = +b.dataset.p; if (pos[0][i] >= TR) return; finishMove(0, i); });
function finishMove(w, i) { const cap = move(w, i, steps), extra = steps >= 4 || cap; $("pick").hidden = true; stage = "throw"; $("msg").textContent = (w ? "컴퓨터" : "나") + (cap ? "가 상대 말을 잡았어요! 한 번 더" : extra ? "(이)가 한 번 더 던져요" : "의 이동 끝"); render(); if (checkWin()) return; if (!extra) turn = 1 - w; render(); if (turn === 1) { busy = true; render(); setTimeout(cpuThrow, 1000 * tempo); } else busy = false; if (turn === 0) render(); }
function cpuThrow() { if (over) return; const t = toss(); showToss(t); steps = t.n; setTimeout(() => { const mv = [0, 1].filter(i => pos[1][i] < TR); let pick = mv[0]; if (mv.length > 1) { const cap = mv.find(i => pos[0].includes(pos[1][i] + steps) && pos[1][i] + steps < TR); pick = cap !== undefined ? cap : pos[1][mv[0]] >= pos[1][mv[1]] ? mv[0] : mv[1]; } finishMove(1, pick); }, 800 * tempo); }
$("again").onclick = newGame; newGame();''',
 css=".yb{width:100%;max-width:340px;margin:0 auto;display:block}.yb .cell{fill:var(--surface);stroke:var(--fg);stroke-width:2}.yb .goal{fill:var(--accent)}.yb .lab{font-size:11px;fill:var(--muted)}.yb .tok{font-size:18px}.sticks{font-size:1.8rem;letter-spacing:.2em;margin-bottom:6px}")
