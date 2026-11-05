import sys, re, json
sys.path.insert(0, ".")
from set32 import duo, party   # set32(→set31→set30)를 불러오면 앞의 같이 하기 게임도 모두 다시 만들어져요

# ───────── 같이 하기 게임 4차: 원카드·체커·윷놀이(두 사람), 주사위 족보·제시어 추리(여러 명). 목록은 set30.py의 GAMES.
_wt = open("../../word-trick.html", encoding="utf-8").read()
TOPICS = dict(re.findall(r'"([^"]+)": "([^"]+)"', _wt[_wt.index("const TOPICS"):_wt.index("};", _wt.index("const TOPICS"))]))   # 시작 화면 제시어 추리 게임의 주제·제시어 그대로

# ── 원카드: 같은 무늬·숫자 내기, 2=+2·A=+3(같은 숫자로 막으면 더해져 넘어감), J·Q·K=한 번 더, 7=무늬 바꾸기, 먼저 다 내면 승리, 15장이 되면 짐.
#   카드 번호 = 무늬×13 + 숫자(0=A, 1=2 … 10=J, 11=Q, 12=K). 패는 방장만 알고 각자에게 privTo로 보내요.
duo("net-onecard.html", "원카드 (같이 하기)", "🃏", 0, "net-onecard-v1",
    "같은 무늬나 같은 숫자의 카드를 내서 손에 든 카드를 먼저 모두 없애면 이겨요. 낼 카드가 없으면 '카드 받기'. 특별 카드: 2=상대 +2장, A=상대 +3장(같은 숫자로 막으면 더해져 넘어가요), J·Q·K=한 번 더, 7=무늬 바꾸기. 카드가 15장이 되면 져요! 내 카드는 내 폰에만 보여요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="big" id="top"></div><p class="center" id="info"></p><div class="row" id="suits" hidden></div><button class="btn ghost" id="draw" type="button" hidden>카드 받기</button><div class="hand" id="hand"></div>',
    r'''
const SU = ["♠", "♥", "♦", "♣"], RK = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"], red = s => s === 1 || s === 2;
const cs = c => Math.floor(c / 13), cr = c => c % 13, label = c => SU[cs(c)] + RK[cr(c)];
let hand = [], seven = null;
function newRound() { H.deck = shuf(Array.from({ length: 52 }, (_, i) => i)); H.hands = { [P.a]: H.deck.splice(0, 7), [P.b]: H.deck.splice(0, 7) }; let top = H.deck.pop(); while (cr(top) === 0 || cr(top) === 1 || cr(top) === 6 || cr(top) >= 10) { H.deck.unshift(top); top = H.deck.pop(); } H.pile = [top];
  return { ph: "play", top, suit: cs(top), pen: 0, turn: P.first, cnt: { [P.a]: 7, [P.b]: 7 }, deckN: H.deck.length, msg: "" }; }
function afterPush() { if (H.hands) [P.a, P.b].forEach(id => privTo(id, { hand: H.hands[id] })); }
function onPriv(d) { if (Array.isArray(d.hand)) { hand = d.hand.slice().sort((x, y) => cs(x) - cs(y) || cr(x) - cr(y)); render(); } }
const playable = c => P.pen ? cr(c) === cr(P.top) && (cr(c) === 0 || cr(c) === 1) : cs(c) === P.suit || cr(c) === cr(P.top);
function take(id, n) { for (let i = 0; i < n; i++) { if (!H.deck.length) { const t = H.pile.pop(); H.deck = shuf(H.pile); H.pile = [t]; } if (!H.deck.length) break; H.hands[id].push(H.deck.pop()); } }
function onAct(from, d) {
  if (P.ph === "play" && from === P.turn && d.t === "play") { const c = +d.c, k = H.hands[from].indexOf(c); if (k < 0 || !playable(c)) return;
    H.hands[from].splice(k, 1); H.pile.push(c); P.top = c; P.suit = cr(c) === 6 && d.suit >= 0 && d.suit < 4 ? +d.suit : cs(c); const r = cr(c), nmF = nameOf(from);
    if (r === 1) P.pen += 2; if (r === 0) P.pen += 3;
    P.msg = r === 1 || r === 0 ? `${nmF}: ${label(c)} 공격! 받을 카드 ${P.pen}장` : r >= 10 ? `${nmF}: ${label(c)} 한 번 더!` : r === 6 ? `${nmF}: 무늬를 ${SU[P.suit]}로 바꿨어요` : "";
    if (!H.hands[from].length) finish(from); else if (r < 10) P.turn = oppOf(from); }
  else if (P.ph === "play" && from === P.turn && d.t === "draw") { const n = P.pen || 1; take(from, n); P.msg = `${nameOf(from)}가 카드 ${n}장을 받았어요`; P.pen = 0; if (H.hands[from].length >= 15) { P.msg = `${nameOf(from)} 카드가 15장이 됐어요!`; finish(oppOf(from)); } else P.turn = oppOf(from); }
  else if (d.t === "again" && P.ph === "end") { round(true); }
  else return;
  if (H.hands) { P.cnt = { [P.a]: H.hands[P.a].length, [P.b]: H.hands[P.b].length }; P.deckN = H.deck.length; } pushS();
}
function changed(was) {}
function cardHtml(c, big) { return `<span class="cd${red(cs(c)) ? " rd" : ""}${big ? " bg" : ""}">${SU[cs(c)]}<b>${RK[cr(c)]}</b></span>`; }
function render() {
  if (!P || P.top === undefined) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("hand").innerHTML = ""; $("draw").hidden = true; if (P) common(); return; }
  const pl = amPlayer(), can = P.ph === "play" && P.turn === me;
  $("st").textContent = P.ph === "end" ? endText() : (P.msg ? P.msg + " · " : "") + (!pl ? `구경 중 · ${nm(P.turn)} 차례` : can ? (P.pen ? `공격받았어요! 같은 숫자로 막거나 ${P.pen}장 받기` : "내 차례! 낼 카드를 골라요") : "상대 차례예요…");
  $("cnt").innerHTML = [P.a, P.b].map(id => `<div class="stat"><small>${esc(nm(id))}</small><b>${P.cnt[id]}장</b></div>`).join("") + `<div class="stat"><small>더미</small><b>${P.deckN}</b></div>`;
  $("top").innerHTML = cardHtml(P.top, true); $("info").textContent = `지금 무늬: ${SU[P.suit]}${P.pen ? ` · 공격 ${P.pen}장` : ""}`;
  $("draw").hidden = !(pl && can); $("draw").textContent = P.pen ? `😵 카드 ${P.pen}장 받기` : "🂠 카드 받기";
  $("hand").innerHTML = pl ? hand.map(c => `<button type="button" data-c="${c}"${can && playable(c) ? "" : " disabled"}>${cardHtml(c)}</button>`).join("") : '<p class="note center">두 사람이 대결 중이에요</p>';
  $("hand").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => { const c = +b.dataset.c; if (cr(c) === 6) { seven = c; $("suits").hidden = false; return; } act({ t: "play", c }); });
  $("suits").innerHTML = SU.map((x, i) => `<button type="button" class="btn ghost sm" data-s="${i}" style="${red(i) ? "color:#d6453a" : ""}">${x}</button>`).join("");
  $("suits").style.gridTemplateColumns = "repeat(4,1fr)"; if (!can) $("suits").hidden = true;
  $("suits").querySelectorAll("[data-s]").forEach(b => b.onclick = () => { $("suits").hidden = true; act({ t: "play", c: seven, suit: +b.dataset.s }); });
  common();
}
$("draw").onclick = () => act({ t: "draw" });
render();
''', '''
.hand{display:flex;flex-wrap:wrap;gap:4px;justify-content:center}.hand button{border:0;background:none;padding:0}.hand button[disabled]{opacity:.45}
.cd{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;width:42px;height:58px;border-radius:8px;border:1px solid var(--line);background:#fff;color:#1c2233;font-size:.9rem;line-height:1.1}.cd b{font-family:var(--font-display);font-size:1.2rem}.cd.rd{color:#d6453a}
.cd.bg{width:72px;height:100px;font-size:1.4rem}.cd.bg b{font-size:2rem}''')

# ── 체커: 8×8 어두운 칸, 대각선 앞으로 한 칸, 뛰어넘어 잡기(잡을 수 있으면 반드시, 이어서 잡기), 끝줄에 닿으면 왕(뒤로도). 상대 말을 다 잡거나 못 움직이게 하면 승리.
#   먼저 하는 사람 🔵은 아래(6~8줄)에서 위로, 🔴는 위에서 아래로. 각자 화면에서는 내 말이 아래쪽에 보여요. 칸 값: 1 🔵, 2 🔴, 3 🔵왕, 4 🔴왕.
duo("net-checkers.html", "체커 (같이 하기)", "♛", 210, "net-checkers-v1",
    "내 말을 눌러 고르고 갈 칸을 눌러요. 말은 대각선 앞으로 한 칸 움직여요. 상대 말을 뛰어넘으면 잡을 수 있고, 잡을 수 있을 땐 반드시 잡아야 해요(이어서 더 잡을 수 있으면 계속). 끝줄에 닿으면 왕(♛)이 되어 뒤로도 움직여요. 상대 말을 모두 잡거나 움직일 수 없게 하면 승리! 내 말은 항상 아래쪽에 보여요.",
    '<p class="center" id="st"></p><div class="stats" id="cnt"></div><div class="grid8" id="bd" style="grid-template-columns:repeat(8,1fr);gap:0;border:3px solid #6b4423;border-radius:6px"></div>',
    r'''
const N = 8, own = v => v === 1 || v === 3 ? 1 : v ? 2 : 0, isKing = v => v >= 3;
const colorOf = id => id === P.first ? 1 : 2;
let sel = -1;
function newRound() { const g = Array(64).fill(0); for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) if ((r + c) % 2 === 1) { if (r < 3) g[r * 8 + c] = 2; else if (r > 4) g[r * 8 + c] = 1; } return { ph: "play", g, turn: P.first, chain: -1, last: [] }; }
function stepsOf(g, i) { const v = g[i], col = own(v), r = Math.floor(i / 8), c = i % 8, dirs = isKing(v) ? [[-1, -1], [-1, 1], [1, -1], [1, 1]] : col === 1 ? [[-1, -1], [-1, 1]] : [[1, -1], [1, 1]], mv = [], jp = [];
  for (const [dr, dc] of dirs) { const r1 = r + dr, c1 = c + dc, r2 = r + 2 * dr, c2 = c + 2 * dc; if (r1 < 0 || c1 < 0 || r1 > 7 || c1 > 7) continue; const a = g[r1 * 8 + c1];
    if (!a) mv.push([i, r1 * 8 + c1, -1]); else if (own(a) !== col && r2 >= 0 && c2 >= 0 && r2 < 8 && c2 < 8 && !g[r2 * 8 + c2]) jp.push([i, r2 * 8 + c2, r1 * 8 + c1]); }
  return { mv, jp }; }
function legal(g, col, chain) { if (chain >= 0) return stepsOf(g, chain).jp; let mv = [], jp = []; g.forEach((v, i) => { if (own(v) === col) { const s = stepsOf(g, i); mv = mv.concat(s.mv); jp = jp.concat(s.jp); } }); return jp.length ? jp : mv; }
function onAct(from, d) {
  if (d.t === "mv" && P.ph === "play" && from === P.turn) { const col = colorOf(from), L = legal(P.g, col, P.chain), m = L.find(x => x[0] === +d.f && x[1] === +d.to); if (!m) return;
    const g = P.g, v = g[m[0]]; g[m[1]] = v; g[m[0]] = 0; if (m[2] >= 0) g[m[2]] = 0; P.last = [m[0], m[1]]; const row = Math.floor(m[1] / 8); let crowned = false;
    if (!isKing(v) && ((col === 1 && row === 0) || (col === 2 && row === 7))) { g[m[1]] = v + 2; crowned = true; }
    if (m[2] >= 0 && !crowned && stepsOf(g, m[1]).jp.length) P.chain = m[1];
    else { P.chain = -1; const o = oppOf(from); if (!legal(g, colorOf(o), -1).length) finish(from); else P.turn = o; }
    pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) { sel = -1; }
function render() {
  if (!P || !P.g) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; $("cnt").innerHTML = ""; if (P) common(); return; }
  const pl = amPlayer(), col = pl ? colorOf(me) : 1, can = P.ph === "play" && P.turn === me, L = can ? legal(P.g, col, P.chain) : [], flip = col === 2;
  if (P.chain >= 0 && can) sel = P.chain; if (sel >= 0 && !L.some(x => x[0] === sel)) sel = -1;
  const must = L.length && L[0][2] >= 0, chip = id => (id === P.first ? "🔵 " : "🔴 ") + nm(id);
  $("st").textContent = P.ph === "end" ? endText() : !pl ? `구경 중 · ${chip(P.turn)} 차례` : can ? (P.chain >= 0 ? "이어서 한 번 더 잡아요!" : must ? "잡을 수 있어요! 반드시 잡아야 해요" : `내 차례예요 (${col === 1 ? "🔵" : "🔴"}) · 말을 골라요`) : "상대 차례예요…";
  $("cnt").innerHTML = [1, 2].map(k => `<div class="stat"><small>${k === 1 ? "🔵" : "🔴"} ${esc(nm(k === 1 ? P.first : oppOf(P.first)))}</small><b>${P.g.filter(v => own(v) === k).length}개</b></div>`).join("") + `<div class="stat"><small>왕</small><b>${P.g.filter(isKing).length}</b></div>`;
  const targets = L.filter(x => x[0] === sel).map(x => x[1]), from = new Set(L.map(x => x[0]));
  let h = ""; for (let k = 0; k < 64; k++) { const i = flip ? 63 - k : k, r = Math.floor(i / 8), c = i % 8, dark = (r + c) % 2 === 1, v = P.g[i], tg = targets.includes(i), pick = from.has(i);
    h += `<button type="button" data-i="${i}" style="background:${!dark ? "#f0d9b5" : tg ? "#7fbf6a" : i === sel ? "#c9a227" : P.last.includes(i) ? "#a07c4f" : "#8b5a2b"};border-radius:0"${(pick || tg) ? "" : " disabled"}>${v ? `<span class="pc ${own(v) === 1 ? "b" : "r"}">${isKing(v) ? "♛" : ""}</span>` : tg ? "•" : ""}</button>`; }
  $("bd").innerHTML = h;
  $("bd").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => { const i = +b.dataset.i; if (targets.includes(i)) { act({ t: "mv", f: sel, to: i }); sel = -1; } else { sel = i; render(); } });
  common();
}
render();
''', '''.pc{display:inline-flex;width:78%;aspect-ratio:1;border-radius:50%;align-items:center;justify-content:center;color:#ffd54a;font-size:1rem;box-shadow:inset 0 -3px 0 rgba(0,0,0,.3)}.pc.b{background:#2f6fdf}.pc.r{background:#d6453a}''')

# ── 윷놀이: 시작 화면의 윷놀이와 같은 간단 규칙(20칸 한 바퀴, 말 2개, 지름길 없음). 도1 개2 걸3 윷4 모5(확률은 윷가락 4개처럼 4·6·4·1·1/16).
#   윷·모가 나오거나 상대 말을 잡으면 한 번 더. 말 2개를 먼저 도착시키면 승리. 말 위치: 0 = 아직 출발 전, 1~19 = 판 위, 20 = 도착.
duo("net-yut.html", "윷놀이 (같이 하기)", "🪵", 25, "net-yut-v1",
    "윷을 던져 나온 칸만큼 말을 움직여요. 도=1칸, 개=2, 걸=3, 윷=4, 모=5. 윷이나 모가 나오거나 상대 말을 잡으면 한 번 더 던져요! 말 2개를 먼저 한 바퀴(20칸) 돌려 도착시키면 이겨요.",
    '<p class="center" id="st"></p><div class="track" id="tr"></div><div class="row" id="pcs"></div><button class="btn" id="th" type="button" hidden>🪵 윷 던지기</button>',
    r'''
const NAMES = ["", "도", "개", "걸", "윷", "모"], TR = 20;
const throwYut = () => { const f = [0, 0, 0, 0].reduce(a => a + (Math.random() < .5 ? 1 : 0), 0); return f === 0 ? 5 : f; };   // 평평한 면 개수: 1도 2개 3걸 4윷, 0이면 모
function newRound() { return { ph: "play", pos: { [P.a]: [0, 0], [P.b]: [0, 0] }, turn: P.first, roll: 0, msg: "" }; }
function onAct(from, d) {
  if (P.ph !== "play" || from !== P.turn) { if (d.t === "again" && P.ph === "end") { round(true); pushS(); } return; }
  if (d.t === "throw" && !P.roll) { P.roll = throwYut(); P.msg = `${nameOf(from)}: ${NAMES[P.roll]}!`; }
  else if (d.t === "move" && P.roll && (d.k === 0 || d.k === 1) && P.pos[from][d.k] < TR) { const o = oppOf(from), np = Math.min(TR, P.pos[from][d.k] + P.roll); let extra = P.roll >= 4, cap = false;
    P.pos[from][d.k] = np; if (np < TR) P.pos[o] = P.pos[o].map(x => { if (x === np) { cap = true; return 0; } return x; });
    if (cap) { extra = true; P.msg = `${nameOf(from)}가 상대 말을 잡았어요! 한 번 더`; } else if (extra) P.msg = `${NAMES[P.roll]}! 한 번 더 던져요`; else P.msg = np >= TR ? `${nameOf(from)}의 말이 도착했어요!` : "";
    P.roll = 0; if (P.pos[from].every(x => x >= TR)) finish(from); else if (!extra) P.turn = o; }
  else return;
  pushS();
}
function changed(was) {}
// 판: 6×6 테두리 20칸. 1번 칸은 오른쪽 아래에서 위로, 시계 반대 방향으로 돌아 20번(도착)이 출발점.
const CELL = (() => { const a = []; for (let r = 4; r >= 0; r--) a.push([r, 5]); for (let c = 4; c >= 0; c--) a.push([0, c]); for (let r = 1; r <= 5; r++) a.push([r, 0]); for (let c = 1; c <= 5; c++) a.push([5, c]); return a; })();
function render() {
  if (!P || !P.pos) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("tr").innerHTML = ""; $("th").hidden = true; $("pcs").innerHTML = ""; if (P) common(); return; }
  const pl = amPlayer(), can = P.ph === "play" && P.turn === me, mark = id => id === P.first ? "🔵" : "🔴";
  $("st").textContent = P.ph === "end" ? endText() : (P.msg ? P.msg + " · " : "") + (!pl ? `구경 중 · ${mark(P.turn)} ${nm(P.turn)} 차례` : can ? (P.roll ? `${NAMES[P.roll]}(${P.roll}칸)! 움직일 말을 골라요` : "내 차례! 윷을 던져요") : "상대 차례예요…");
  const at = {}; [P.a, P.b].forEach(id => P.pos[id].forEach((x, k) => { if (x > 0 && x < TR) (at[x] = at[x] || []).push(mark(id) + (k + 1)); }));
  let h = ""; for (let r = 0; r < 6; r++) for (let c = 0; c < 6; c++) { const n = CELL.findIndex(([y, x]) => y === r && x === c) + 1;
    h += n ? `<div class="tc${n === 20 ? " go" : n % 5 === 0 ? " cn" : ""}">${n === 20 ? "출발·도착" : (at[n] || []).join("")}</div>` : (r === 1 && c === 1 ? `<div class="mid">${P.roll ? NAMES[P.roll] : "🪵"}<small>${[P.a, P.b].map(id => `${mark(id)} ${esc(nm(id))}: 대기 ${P.pos[id].filter(x => !x).length} · 도착 ${P.pos[id].filter(x => x >= TR).length}`).join("<br>")}</small></div>` : r >= 1 && r <= 4 && c >= 1 && c <= 4 ? "" : "<div></div>"); }
  $("tr").innerHTML = h; $("th").hidden = !(can && !P.roll);
  $("pcs").innerHTML = can && P.roll ? P.pos[me].map((x, k) => x < TR ? `<button class="btn ghost sm" type="button" data-k="${k}">${mark(me)}${k + 1} 말 (${x ? x + "번 칸" : "출발 전"} → ${Math.min(TR, x + P.roll) >= TR ? "도착" : Math.min(TR, x + P.roll) + "번 칸"})</button>` : "").join("") : "";
  $("pcs").querySelectorAll("[data-k]").forEach(b => b.onclick = () => act({ t: "move", k: +b.dataset.k }));
  common();
}
$("th").onclick = () => act({ t: "throw" });
render();
''', '''.track{display:grid;grid-template-columns:repeat(6,1fr);gap:3px;width:min(100%,330px);margin:0 auto}.tc{aspect-ratio:1;border-radius:50%;background:var(--soft);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:.8rem;line-height:1;text-align:center;flex-wrap:wrap}
.tc.cn{background:color-mix(in srgb,var(--accent) 22%,var(--surface))}.tc.go{border-radius:10px;font-size:.6rem;background:color-mix(in srgb,var(--ok) 25%,var(--surface))}
.mid{grid-column:2/6;grid-row:2/6;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:var(--font-display);font-size:2.4rem;text-align:center}.mid small{font-family:var(--font-body);font-size:.75rem;line-height:1.5;color:var(--muted)}''')

# ── 주사위 족보(여러 명, 2~6명): 시작 화면 주사위 족보와 같은 12칸 점수표. 차례마다 3번까지 굴리고, 고정한 주사위는 그대로. 12칸을 모두 채우면 끝.
party("net-yacht.html", "주사위 족보 (같이 하기)", "🎲", 330, "net-yacht-v1",
      "연결된 사람이 차례대로 해요. 주사위 5개를 한 차례에 최대 3번 굴리고, 마음에 드는 주사위는 눌러서 고정해요. 점수표에서 칸을 골라 채우면 다음 사람 차례! 12칸을 모두 채우면 끝나요. 1~6의 합이 63점 이상이면 보너스 35점.",
      '<p class="center" id="st"></p><div class="dice" id="dice"></div><div class="row" id="rb"><button class="btn" id="roll" type="button">🎲 굴리기</button><button class="btn ghost" id="newg" type="button" hidden>새 판</button></div><div style="overflow-x:auto"><table class="sc" id="sc"></table></div>',
      r'''
const NAMES = ["1의 눈", "2의 눈", "3의 눈", "4의 눈", "5의 눈", "6의 눈", "초이스", "포카드", "풀하우스", "S 스트레이트", "L 스트레이트", "파이브"], DIE = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"];
function scoreOf(c, d) { const cn = [0, 0, 0, 0, 0, 0, 0]; d.forEach(v => cn[v]++); const sum = d.reduce((a, b) => a + b, 0), has = a => a.every(v => cn[v] > 0);
  if (c < 6) return cn[c + 1] * (c + 1); if (c === 6) return sum; if (c === 7) return cn.some(x => x >= 4) ? sum : 0; if (c === 8) return cn.includes(3) && cn.includes(2) ? sum : 0;
  if (c === 9) return has([1, 2, 3, 4]) || has([2, 3, 4, 5]) || has([3, 4, 5, 6]) ? 15 : 0; if (c === 10) return has([1, 2, 3, 4, 5]) || has([2, 3, 4, 5, 6]) ? 30 : 0; return cn.some(x => x === 5) ? 50 : 0; }
const upper = a => a.slice(0, 6).reduce((x, y) => x + (y || 0), 0), total = a => a.reduce((x, y) => x + (y || 0), 0) + (upper(a) >= 63 ? 35 : 0);
function initState() { const ord = ids().slice(0, 6); return { ph: "play", ord, cur: 0, dice: [1, 2, 3, 4, 5], held: [0, 0, 0, 0, 0], left: 3, sc: Object.fromEntries(ord.map(id => [id, Array(12).fill(null)])), rno: 1 }; }
const curId = () => P.ord[P.cur];
function next() { if (P.ord.every(id => P.sc[id].every(v => v !== null))) { P.ph = "end"; const best = Math.max(...P.ord.map(id => total(P.sc[id]))); P.win = P.ord.filter(id => total(P.sc[id]) === best); return; }
  for (let k = 0; k < P.ord.length; k++) { P.cur = (P.cur + 1) % P.ord.length; if (P.sc[curId()].some(v => v === null)) break; } P.left = 3; P.held = [0, 0, 0, 0, 0]; }
// 나간 사람은 점수표에서 빼요. 차례였던 사람이 나가면 다음 사람부터 새로 굴려요. 새로 들어온 사람은 다음 판부터 참가.
function onRoster() { const live = ids(); if (P.ord.every(id => live.includes(id))) return; const cur = curId(); P.ord = P.ord.filter(id => live.includes(id));
  if (!P.ord.length) { const r = P.rno; P = initState(); P.rno = r; return; } const k = P.ord.indexOf(cur); if (k >= 0) P.cur = k; else { P.cur = P.cur % P.ord.length; P.left = 3; P.held = [0, 0, 0, 0, 0]; } }
function onAct(from, d) {
  if (d.t === "new" && from === "host") { const r = P.rno + 1; P = initState(); P.rno = r; }
  else if (P.ph !== "play" || from !== curId()) return;
  else if (d.t === "roll" && P.left > 0) { P.dice = P.dice.map((v, i) => P.held[i] && P.left < 3 ? v : ri(1, 6)); P.left--; }
  else if (d.t === "hold" && P.left < 3 && P.left > 0 && d.i >= 0 && d.i < 5) P.held[d.i] = P.held[d.i] ? 0 : 1;
  else if (d.t === "pick" && P.left < 3 && d.c >= 0 && d.c < 12 && P.sc[from][d.c] === null) { P.sc[from][d.c] = scoreOf(d.c, P.dice); next(); }
  else return;
  pushS();
}
function onPriv() {}
function changed(was) {}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  const cur = curId(), mine = P.ph === "play" && cur === me, rolled = P.left < 3, inGame = P.ord.includes(me);
  $("st").textContent = P.ph === "end" ? (P.win.includes(me) ? (P.win.length > 1 ? "🤝 공동 1등!" : "🎉 1등이에요!") : `🎉 ${P.win.map(pn).join(", ")} 1등!`) : mine ? (rolled ? `남은 굴리기 ${P.left}번 · 주사위를 눌러 고정하거나 점수 칸을 골라요` : "내 차례! 주사위를 굴려요") : `${pn(cur)} 차례${inGame ? "" : " · 다음 판부터 참가해요"}`;
  $("dice").innerHTML = P.dice.map((v, i) => `<button type="button" data-i="${i}" class="${P.held[i] ? "on" : ""}"${mine && rolled && P.left > 0 ? "" : " disabled"}>${rolled || P.ph === "end" ? DIE[v] : "🎲"}</button>`).join("");
  $("dice").querySelectorAll("button:not([disabled])").forEach(b => b.onclick = () => act({ t: "hold", i: +b.dataset.i }));
  $("roll").hidden = !mine || P.left === 0; $("roll").textContent = `🎲 굴리기 (${P.left}번 남음)`; $("newg").hidden = !isHost || P.ph !== "end";
  const th = "<tr><th></th>" + P.ord.map(id => `<th class="${id === cur && P.ph === "play" ? "cur" : ""}">${esc(pn(id))}</th>`).join("") + "</tr>";
  const rows = NAMES.map((n, c) => `<tr><td>${n}</td>` + P.ord.map(id => { const v = P.sc[id][c]; return v !== null ? `<td>${v}</td>` : id === me && mine && rolled ? `<td><button type="button" data-c="${c}">${scoreOf(c, P.dice)}</button></td>` : "<td class='e'>·</td>"; }).join("") + "</tr>").join("");
  const foot = `<tr><td>보너스 (1~6 합 ${"≥"}63)</td>${P.ord.map(id => `<td>${upper(P.sc[id])}${upper(P.sc[id]) >= 63 ? " +35" : ""}</td>`).join("")}</tr><tr class="tot"><td>합계</td>${P.ord.map(id => `<td>${total(P.sc[id])}</td>`).join("")}</tr>`;
  $("sc").innerHTML = th + rows + foot; $("sc").querySelectorAll("[data-c]").forEach(b => b.onclick = () => act({ t: "pick", c: +b.dataset.c }));
}
$("roll").onclick = () => act({ t: "roll" }); $("newg").onclick = () => act({ t: "new" });
render();
''', '''.dice{display:flex;justify-content:center;gap:6px}.dice button{width:54px;height:54px;font-size:2.6rem;line-height:1;border-radius:12px;border:2px solid var(--line);background:var(--surface);padding:0}.dice button.on{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 25%,var(--surface))}
.sc{width:100%;border-collapse:collapse;font-size:.82rem}.sc th,.sc td{border-bottom:1px solid var(--line);padding:4px 3px;text-align:center;white-space:nowrap}.sc td:first-child{text-align:left}.sc th.cur{color:var(--accent)}.sc td.e{color:var(--muted)}
.sc td button{border:1px solid var(--accent);background:color-mix(in srgb,var(--accent) 15%,var(--surface));border-radius:8px;padding:3px 8px;font-weight:700}.sc tr.tot td{font-weight:700;font-size:.95rem}''')

# ── 제시어 추리(여러 명): 한 명(모르쇠)만 제시어를 모르고 주제만 알아요. 각자 폰에서 몰래 확인 → 돌아가며 설명 → 폰으로 투표 → 공개.
party("net-wordtrick.html", "제시어 추리 (같이 하기)", "🤫", 290, "net-wordtrick-v1",
      "모두가 같은 제시어를 받고, 한 명(모르쇠)만 제시어를 몰라요(주제는 알아요). 각자 폰에서 몰래 확인하고, 돌아가며 제시어를 설명하면서 모르쇠를 찾아요. 방장이 투표를 시작하면 각자 폰으로 모르쇠라고 생각하는 사람을 골라요. 폰을 돌릴 필요가 없어요!",
      '<p class="center" id="st"></p><div id="host" hidden style="display:grid;gap:8px"><label class="lb" for="tp">주제</label><select id="tp"></select><button class="btn" id="deal" type="button">🃏 제시어 나눠 주기</button></div>'
      '<div id="mine" style="display:grid;gap:8px"></div><div class="choice" id="vote" style="grid-template-columns:repeat(2,1fr)"></div><button class="btn" id="vgo" type="button" hidden>🗳️ 투표 시작</button><button class="btn ghost" id="show" type="button" hidden>📢 결과 공개</button><div id="res"></div>',
      r'''
const TOPICS = ''' + json.dumps(TOPICS, ensure_ascii=False) + r''';
let myCard = null, myRno = 0, see = false;
function initState() { return { ph: "set", topic: "랜덤", rno: 0, parts: [], votes: {}, reveal: null }; }
function onRoster() { if (P.ph === "vote" && P.parts.every(id => P.votes[id] || !ids().includes(id))) reveal(); }
function reveal() { const cnt = {}; Object.values(P.votes).forEach(t => { cnt[t] = (cnt[t] || 0) + 1; }); const top = Math.max(0, ...Object.values(cnt)), tops = Object.keys(cnt).filter(k => cnt[k] === top);
  P.ph = "reveal"; P.reveal = { liar: H.liar, word: H.word, cnt, caught: tops.length === 1 && tops[0] === H.liar }; }
function onAct(from, d) {
  if (from === "host" && d.t === "topic" && (d.v === "랜덤" || TOPICS[d.v])) P.topic = d.v;
  else if (from === "host" && d.t === "deal") { const ps = ids(); if (ps.length < 3) { alert("3명 이상 연결돼야 해요."); return; } const tp = P.topic === "랜덤" ? shuf(Object.keys(TOPICS))[0] : P.topic, ws = TOPICS[tp].split(" ");
    H.word = ws[ri(0, ws.length - 1)]; H.liar = ps[ri(0, ps.length - 1)]; H.tp = tp; P.ph = "show"; P.rno++; P.parts = ps; P.votes = {}; P.reveal = null; P.shownTopic = tp; }
  else if (from === "host" && d.t === "vote" && P.ph === "show") { P.ph = "vote"; P.votes = {}; }
  else if (d.t === "pick" && P.ph === "vote" && P.parts.includes(from) && P.parts.includes(d.to) && d.to !== from) { P.votes[from] = d.to; if (P.parts.every(id => P.votes[id] || !ids().includes(id))) reveal(); }
  else if (from === "host" && d.t === "open" && P.ph === "vote") reveal();
  else return;
  pushS();
}
function afterPush() { if (P.ph === "show" || P.ph === "vote") P.parts.forEach(id => privTo(id, { rno: P.rno, topic: H.tp, word: id === H.liar ? null : H.word })); }
function onPriv(d) { if (d.rno !== myRno) { myRno = d.rno; myCard = d; see = false; buzzV(100); render(); } }
function changed(was) {}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  $("host").hidden = !isHost || P.ph === "show" || P.ph === "vote"; $("tp").innerHTML = ["랜덤", ...Object.keys(TOPICS)].map(t => `<option${t === P.topic ? " selected" : ""}>${t}</option>`).join(""); $("deal").textContent = P.rno ? "🃏 새 제시어로 다시" : "🃏 제시어 나눠 주기";
  $("vgo").hidden = !(isHost && P.ph === "show"); $("show").hidden = !(isHost && P.ph === "vote");
  const inG = P.parts.includes(me), voted = Object.keys(P.votes).length;
  $("st").textContent = P.ph === "set" ? (isHost ? `참가자 ${ids().length}명 · 주제를 고르고 나눠 주세요` : "방장이 제시어를 나눠 주기를 기다려요…") : P.ph === "show" ? `주제: ${P.shownTopic} · 돌아가며 제시어를 설명해요` : P.ph === "vote" ? `🗳️ 모르쇠는 누구? (투표 ${voted}/${P.parts.length})` : P.reveal.caught ? "🎉 모르쇠를 찾았어요!" : "🤫 모르쇠가 숨는 데 성공했어요!";
  const c = myCard && myRno === P.rno ? myCard : null;
  $("mine").innerHTML = (P.ph === "show" || P.ph === "vote") && inG ? (!c ? '<p class="note center">카드를 받는 중…</p>' : see ? `<div class="big">${c.word ? esc(c.word) : "🤫 모르쇠"}</div><p class="center">${c.word ? `주제: ${esc(c.topic)}` : `나만 제시어를 몰라요! 주제는 <b>${esc(c.topic)}</b>. 들키지 않게 설명해요`}</p><button class="btn ghost" id="hide" type="button">🙈 숨기기</button>` : '<button class="btn" id="see" type="button" style="padding:26px">👀 내 제시어 보기 (주변에서 안 보이게!)</button>') : "";
  if ($("see")) $("see").onclick = () => { see = true; render(); }; if ($("hide")) $("hide").onclick = () => { see = false; render(); };
  $("vote").innerHTML = P.ph === "vote" && inG ? P.parts.filter(id => id !== me).map(id => `<button type="button" data-to="${id}" class="${P.votes[me] === id ? "on" : ""}" style="${P.votes[me] === id ? "border-color:var(--accent);background:color-mix(in srgb,var(--accent) 25%,var(--surface))" : ""}">${esc(pn(id))}</button>`).join("") : "";
  $("vote").querySelectorAll("[data-to]").forEach(b => b.onclick = () => act({ t: "pick", to: b.dataset.to }));
  const r = P.reveal; $("res").innerHTML = P.ph === "reveal" && r ? `<p class="center">모르쇠는 <b>${esc(pn(r.liar))}</b>, 제시어는 <b>${esc(r.word)}</b>였어요!</p>` + '<div class="lb">투표 결과</div>' + P.parts.map(id => `<div class="li"><span>${id === r.liar ? "🤫 " : ""}${esc(pn(id))}</span><b>${r.cnt[id] || 0}표</b></div>`).join("") + (r.caught ? '<p class="note center">모르쇠는 이제 제시어를 맞혀 보세요. 맞히면 모르쇠 승리!</p>' : "") : "";
}
$("tp").onchange = () => act({ t: "topic", v: $("tp").value }); $("deal").onclick = () => act({ t: "deal" }); $("vgo").onclick = () => act({ t: "vote" }); $("show").onclick = () => act({ t: "open" });
render();
''', "select{width:100%;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:inherit}")
