import sys
sys.path.insert(0, ".")
import set33                      # set33(→set32→set31→set30)을 불러오면 앞의 같이 하기 게임도 모두 다시 만들어져요
from set32 import party

# ───────── 같이 하기 게임 5차: 여러 명 카드 게임 6개(훌라·포커·도둑잡기·블랙잭·대통령·세븐). 목록은 set30.py의 GAMES(묶음 "card").
#   카드 번호 = 무늬×13 + 숫자(0=A, 1=2 … 9=10, 10=J, 11=Q, 12=K), 52 = 조커. 패는 방장만 알고, 각자에게 privTo로 내 패만 보내요.
#   공통 틀 CARD_JS: 방장이 ▶ 시작하기 → 판(P.rno) 시작. 판 도중에 참가자가 나가면 판을 멈추고 방장이 새 판을 시작해요.
CARD_JS = r'''
const SU = ["♠", "♥", "♦", "♣"], RK = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const cs = c => Math.floor(c / 13), cr = c => c % 13, isRed = c => c < 52 && (cs(c) === 1 || cs(c) === 2);
const label = c => c === 52 ? "조커" : SU[cs(c)] + RK[cr(c)];
function cardHtml(c, x) { x = x ? " " + x : ""; if (c === 52) return `<span class="cd jk${x}">🃏<b>JK</b></span>`; if (c === null || c === undefined || c < 0) return `<span class="cd bk${x}"></span>`; return `<span class="cd${isRed(c) ? " rd" : ""}${x}">${SU[cs(c)]}<b>${RK[cr(c)]}</b></span>`; }
const deck52 = () => shuf(Array.from({ length: 52 }, (_, i) => i));
const nmOf = id => { const p = players.find(q => q.id === id); return p ? p.name : (P && P.nm && P.nm[id]) || "?"; };
let hand = [], myR = -1, sel = [];
function sendHands() { if (H.hands && P.ord) P.ord.forEach(id => privTo(id, { rno: P.rno, hand: (H.hands[id] || []).slice() })); }
function afterPush() { sendHands(); }
function onPriv(d) { if (!Array.isArray(d.hand)) return; if (d.rno !== myR) sel = []; myR = d.rno; hand = d.hand; sel = sel.filter(c => hand.includes(c)); render(); }
const myHand = () => (P && myR === P.rno && P.ord && P.ord.includes(me)) ? hand.slice() : [];
function nextIn(list, id, ok) { const n = list.length; let k = list.indexOf(id); for (let s = 0; s < n; s++) { k = (k + 1) % n; if (ok(list[k])) return list[k]; } return null; }
function onRoster() { if (P.ph === "play" && P.ord.some(id => !ids().includes(id))) { P.ph = "wait"; P.msg = "참가자가 나가서 이번 판을 멈췄어요. 방장이 새 판을 시작해 주세요."; H.hands = null; } }
function sync() { if (H.hands && P.ord) P.cnt = Object.fromEntries(P.ord.map(id => [id, (H.hands[id] || []).length])); }
function changed(was) { if (!was || was.rno !== P.rno) sel = []; }
function canStart(min, max) { const n = ids().length; if (n < min) { alert(min + "명 이상 연결돼야 해요."); return null; } return ids().slice(0, max); }
function goBtn() { const b = $("go"); b.hidden = !isHost || P.ph === "play"; b.textContent = P.rno ? `🔁 새 판 시작 (지금 ${ids().length}명)` : `▶ 시작하기 (지금 ${ids().length}명)`; }
function waitText(min, max) { return (P.msg ? P.msg + " · " : "") + (isHost ? `${min}~${max}명이 할 수 있어요. ▶ 시작하기를 눌러요` : "방장이 시작하기를 기다려요…"); }
function handBox(cards, ok) { return cards.map(c => ok ? `<button type="button" data-c="${c}" class="${sel.includes(c) ? "on" : ""}"${ok(c) ? "" : " disabled"}>${cardHtml(c)}</button>` : cardHtml(c)).join(""); }
function bindHand(fn) { $("hand").querySelectorAll("button[data-c]:not([disabled])").forEach(b => b.onclick = () => fn(+b.dataset.c)); }
function toggle(c, max) { if (sel.includes(c)) sel = sel.filter(x => x !== c); else if (!max || sel.length < max) sel = [...sel, c]; render(); }
function seats(fn) { return '<div class="seats">' + P.ord.map(id => `<div class="seat${P.ph === "play" && id === P.turn ? " cur" : ""}"><small>${esc(pn(id))}</small><b>${fn(id)}</b></div>`).join("") + "</div>"; }
function totHtml() { const t = P.tot || {}, ks = Object.keys(t); return ks.length ? `<p class="note center">누적 점수 · ${ks.map(id => `${esc(pn(id))} ${t[id] > 0 ? "+" : ""}${t[id]}`).join(" · ")}</p>` : ""; }
function idle() { $("tbl").innerHTML = totHtml(); $("hand").innerHTML = ""; $("acts").innerHTML = ""; }
$("go").onclick = () => act({ t: "start" });
'''
BODY = '<p class="center" id="st"></p><div id="tbl"></div><div class="hand" id="hand"></div><div id="acts"></div><button class="btn" id="go" type="button" hidden>▶ 시작하기</button>'
CARD_CSS = '''
#tbl{display:grid;gap:8px}#acts{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}#acts .btn{flex:1 1 140px}
.hand{display:flex;flex-wrap:wrap;gap:4px;justify-content:center}.hand button{border:0;background:none;padding:0;transition:transform .1s}.hand button[disabled]{opacity:.5}
.hand button.on{transform:translateY(-8px)}.hand button.on .cd{outline:3px solid var(--accent)}
.cd{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;width:40px;height:56px;border-radius:7px;border:1px solid #c9c2b4;background:#fff;color:#1c2233;font-size:.85rem;line-height:1.05;flex:none}
.cd b{font-family:var(--font-display);font-size:1.15rem;font-weight:400}.cd.rd{color:#d6453a}.cd.jk{color:#7a3fd0}
.cd.bk{background:repeating-linear-gradient(45deg,#3d5fb8 0 6px,#2f4c99 6px 12px);border-color:#22397a}.cd.e{opacity:.25}
.cd.bg{width:60px;height:84px;font-size:1.2rem}.cd.bg b{font-size:1.7rem}
.hand.sm{gap:3px}.hand.sm .cd{width:30px;height:42px;font-size:.7rem}.hand.sm .cd b{font-size:.9rem}
.seats{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:6px}.seat{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:6px 8px;text-align:center;min-width:0}
.seat small{display:block;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.seat b{font-size:.9rem;font-weight:700}.seat.cur{border-color:var(--accent);box-shadow:inset 0 0 0 2px var(--accent)}
.tb{display:flex;gap:6px;justify-content:center;align-items:center;flex-wrap:wrap;min-height:90px}.tb small{color:var(--muted);width:100%;text-align:center}
.pile{display:flex;gap:18px;justify-content:center}.pile>div{display:flex;flex-direction:column;align-items:center;gap:2px}.pile small{color:var(--muted);font-size:.75rem}
.meld{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:4px 0;border-bottom:1px solid var(--line)}.meld small{min-width:44px;color:var(--muted)}.meld .hand{justify-content:flex-start;flex:1}
.sv{display:grid;grid-template-columns:repeat(14,minmax(0,1fr));gap:2px;font-size:.7rem;text-align:center;margin-bottom:2px}.sv b{font-size:.9rem}.sv span{background:#fff;color:#1c2233;border-radius:4px;padding:3px 0;border:1px solid #c9c2b4}
.sv span.rd{color:#d6453a}.sv span.e{background:transparent;border:1px dashed var(--line)}
.bjr{display:grid;gap:4px;padding:4px 0;border-bottom:1px solid var(--line)}.bjr .hand{justify-content:flex-start}'''

def card(fn, title, emoji, hue, key, help_, js):
    party(fn, title, emoji, hue, key, help_, BODY, CARD_JS + js, CARD_CSS)

# ── 도둑잡기(2~6명): 카드 52장 + 조커 1장을 모두 나누고 같은 숫자 두 장은 자동으로 버려요. 차례가 되면 다음 사람의 카드(뒷면)를 한 장 뽑아요.
#   짝이 맞으면 버리고, 카드를 다 없앤 사람은 빠져나가요. 마지막에 조커(도둑)를 든 사람이 져요.
card("net-oldmaid.html", "도둑잡기 (같이 하기)", "🤡", 280, "net-oldmaid-v1",
     "카드 52장과 조커 1장을 모두 나눠 가지고, 같은 숫자 두 장은 자동으로 버려요. 내 차례가 되면 다음 사람의 카드(뒷면) 가운데 한 장을 뽑아요. 같은 숫자가 생기면 짝을 맞춰 버려요. 카드를 다 없애면 빠져나가요. 마지막까지 조커(도둑)를 들고 있는 사람이 져요! 내 카드는 내 폰에만 보여요.",
     r'''
function initState() { return { ph: "wait", rno: 0, ord: [], cnt: {}, out: [], turn: null, loser: null, msg: "" }; }
const live = id => !P.out.includes(id);
function pairOff(h) { const by = {}; h.forEach(c => { const k = c === 52 ? "j" : cr(c); (by[k] = by[k] || []).push(c); }); const keep = []; Object.values(by).forEach(a => { if (a.length % 2) keep.push(a[0]); }); return shuf(keep); }
function check() { P.ord.forEach(id => { if (live(id) && !H.hands[id].length) P.out.push(id); }); const L = P.ord.filter(live); if (L.length <= 1) { P.ph = "end"; P.loser = L[0] || null; } }
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") { const ps = canStart(2, 6); if (!ps) return;
    const dk = shuf([...Array.from({ length: 52 }, (_, i) => i), 52]); H.hands = {}; ps.forEach(id => H.hands[id] = []); dk.forEach((c, i) => H.hands[ps[i % ps.length]].push(c)); ps.forEach(id => H.hands[id] = pairOff(H.hands[id]));
    Object.assign(P, { ph: "play", rno: P.rno + 1, ord: ps, out: [], loser: null, msg: "같은 숫자 두 장은 자동으로 버렸어요" }); P.turn = ps[(P.rno - 1) % ps.length]; check(); if (P.ph === "play" && !live(P.turn)) P.turn = nextIn(ps, P.turn, live); }
  else if (d.t === "pick" && P.ph === "play" && from === P.turn) { const tg = nextIn(P.ord, from, id => live(id) && id !== from); if (!tg) return; const th = H.hands[tg], k = +d.k; if (!(k >= 0 && k < th.length)) return;
    const c = th.splice(k, 1)[0], mine = H.hands[from], j = c === 52 ? -1 : mine.findIndex(x => x !== 52 && cr(x) === cr(c));
    if (j >= 0) { mine.splice(j, 1); P.msg = `${nmOf(from)}: ${nmOf(tg)}에게서 뽑아 ${RK[cr(c)]} 짝을 맞췄어요!`; } else { mine.push(c); P.msg = `${nmOf(from)}: ${nmOf(tg)}에게서 한 장 뽑았어요`; }
    H.hands[tg] = shuf(th); H.hands[from] = shuf(mine); check(); if (P.ph === "play") P.turn = nextIn(P.ord, from, live); }
  else return;
  sync(); pushS();
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn(); if (P.ph === "wait") { $("st").textContent = waitText(2, 6); idle(); return; }
  const h = myHand().sort((a, b) => (a === 52 ? 99 : cr(a)) - (b === 52 ? 99 : cr(b)) || a - b), mine = P.ph === "play" && P.turn === me, tg = P.ph === "play" ? nextIn(P.ord, P.turn, id => live(id) && id !== P.turn) : null;
  $("st").textContent = P.ph === "end" ? (P.loser === me ? "😱 도둑(조커)이 나에게 남았어요!" : P.loser ? `🎉 ${pn(P.loser)}에게 도둑(조커)이 남았어요!` : "끝!") : (P.msg ? P.msg + " · " : "") + (mine ? `내 차례! ${pn(tg)}의 카드를 한 장 뽑아요` : !P.ord.includes(me) ? `구경 중 · ${pn(P.turn)} 차례` : `${pn(P.turn)} 차례 (${pn(tg)}에게서 뽑아요)`);
  $("tbl").innerHTML = seats(id => P.loser === id ? "🃏 도둑!" : P.out.includes(id) ? "🏁 빠져나감" : `${P.cnt[id]}장`)
    + (mine && tg ? `<p class="lb center">👇 ${esc(pn(tg))}의 카드 한 장을 눌러 뽑아요</p><div class="hand">${Array.from({ length: P.cnt[tg] }, (_, k) => `<button type="button" data-k="${k}">${cardHtml(-1)}</button>`).join("")}</div>` : "")
    + (h.length ? '<p class="lb center">내 카드</p>' : "");
  $("tbl").querySelectorAll("[data-k]").forEach(b => b.onclick = () => act({ t: "pick", k: +b.dataset.k }));
  $("hand").innerHTML = handBox(h); $("acts").innerHTML = "";
}
render();
''')

# ── 블랙잭(1~6명, 컴퓨터 딜러와 대결): 카드 합을 21에 가깝게. A=1 또는 11, J·Q·K=10. 21을 넘으면 짐. 딜러는 16 이하면 반드시 더 받아요.
#   점수: 이김 +1, 처음 두 장이 21(블랙잭) +2, 비김 0, 짐 -1. 카드는 모두 앞면이라 숨길 것이 없어요(딜러의 두 번째 카드만 나중에 공개).
card("net-21.html", "블랙잭 21 (같이 하기)", "🎴", 150, "net-21-v1",
     "모두 함께 컴퓨터 딜러와 겨뤄요. 카드 합을 21에 가깝게 만들면 이겨요. A는 1 또는 11, J·Q·K는 10이에요. '한 장 더'로 카드를 받고, 그만 받으려면 '멈추기'. 21을 넘으면 바로 져요! 딜러는 16 이하면 반드시 더 받아요. 이기면 +1, 처음 두 장이 21(블랙잭)이면 +2, 지면 -1점이에요. 돈이 아니라 점수 놀이예요.",
     r'''
const val = h => { let s = 0, a = 0; h.forEach(c => { if (c < 0) return; const r = cr(c); if (r === 0) { s += 11; a++; } else s += r >= 9 ? 10 : r + 1; }); while (s > 21 && a) { s -= 10; a--; } return s; };
const RES = { win: "🎉 이김 +1", bj: "🌟 블랙잭 +2", push: "🤝 비김", lose: "😢 짐 -1", bust: "💥 21 넘음 -1" };
function initState() { return { ph: "wait", rno: 0, ord: [], hs: {}, dl: [], st: {}, res: {}, tot: {}, turn: null, msg: "" }; }
const deal1 = () => { if (!H.dk || !H.dk.length) H.dk = deck52(); return H.dk.pop(); };
function nextP() { P.turn = P.ord.find(id => P.st[id] === "play") || null; if (!P.turn) dealer(); }
function dealer() { P.dl[1] = H.hole; const anyLive = P.ord.some(id => P.st[id] !== "bust"); while (anyLive && val(P.dl) < 17) P.dl.push(deal1()); const dv = val(P.dl), dbj = P.dl.length === 2 && dv === 21;
  P.ord.forEach(id => { const pv = val(P.hs[id]), s = P.st[id]; const r = s === "bust" ? "bust" : s === "bj" ? (dbj ? "push" : "bj") : dv > 21 || pv > dv ? "win" : pv === dv ? "push" : "lose";
    P.res[id] = r; P.tot[id] = (P.tot[id] || 0) + ({ win: 1, bj: 2, push: 0, lose: -1, bust: -1 })[r]; });
  P.ph = "end"; P.msg = dv > 21 ? `딜러가 ${dv}점으로 21을 넘었어요!` : `딜러는 ${dv}점`; }
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") { const ps = canStart(1, 6); if (!ps) return; H.dk = deck52(); P.ord = ps; P.hs = {}; P.st = {}; P.res = {};
    ps.forEach(id => { P.hs[id] = [deal1(), deal1()]; P.st[id] = val(P.hs[id]) === 21 ? "bj" : "play"; }); H.hole = deal1(); P.dl = [deal1(), -1]; P.ph = "play"; P.rno++; P.msg = ""; nextP(); }
  else if (P.ph === "play" && from === P.turn && d.t === "hit") { P.hs[from].push(deal1()); const v = val(P.hs[from]); P.msg = "";
    if (v > 21) { P.st[from] = "bust"; P.msg = `${nmOf(from)}: ${v}점, 21을 넘었어요!`; nextP(); } else if (v === 21) { P.st[from] = "stand"; P.msg = `${nmOf(from)}: 21점!`; nextP(); } }
  else if (P.ph === "play" && from === P.turn && d.t === "stand") { P.st[from] = "stand"; P.msg = `${nmOf(from)}: ${val(P.hs[from])}점에서 멈췄어요`; nextP(); }
  else return;
  pushS();
}
function row(name, list, extra) { return `<div class="bjr"><div class="li"><span>${name}</span><b>${extra}</b></div><div class="hand sm">${list.map(c => cardHtml(c)).join("")}</div></div>`; }
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn(); if (P.ph === "wait") { $("st").textContent = waitText(1, 6); idle(); return; }
  const mine = P.ph === "play" && P.turn === me;
  $("st").textContent = P.ph === "end" ? (P.res[me] ? RES[P.res[me]] + " · " : "") + P.msg : mine ? `${P.msg ? P.msg + " · " : ""}내 차례! 지금 ${val(P.hs[me])}점이에요` : (P.msg ? P.msg + " · " : "") + (P.turn ? `${pn(P.turn)} 차례` : "");
  $("tbl").innerHTML = row("🎩 딜러 (컴퓨터)", P.dl, P.dl.includes(-1) ? `${val(P.dl)} + ?` : `${val(P.dl)}점`)
    + P.ord.map(id => row(`${P.ph === "play" && id === P.turn ? "👉 " : ""}${esc(pn(id))}`, P.hs[id], P.ph === "end" ? `${val(P.hs[id])}점 · ${RES[P.res[id]]}` : `${val(P.hs[id])}점${P.st[id] === "bj" ? " 🌟" : P.st[id] === "bust" ? " 💥" : P.st[id] === "stand" ? " ✋" : ""}`)).join("") + totHtml();
  $("hand").innerHTML = "";
  $("acts").innerHTML = mine ? '<button class="btn" id="hit" type="button">🂠 한 장 더</button><button class="btn ghost" id="sty" type="button">✋ 멈추기</button>' : "";
  if (mine) { $("hit").onclick = () => act({ t: "hit" }); $("sty").onclick = () => act({ t: "stand" }); }
}
render();
''')

# ── 대통령 게임(2~6명): 카드를 모두 나누고 ♣3을 가진 사람부터. 세기는 3 < 4 < … < K < A < 2. 같은 숫자 1~4장을 내고,
#   다음 사람은 같은 장수로 더 센 숫자를 내거나 패스. 패스하면 그 바닥에서는 다시 낼 수 없어요. 모두 패스하면 마지막에 낸 사람이 새로 내요.
#   먼저 다 낸 순서대로 대통령·부통령·평민…, 마지막 사람이 거지.
card("net-president.html", "대통령 게임 (같이 하기)", "👑", 45, "net-president-v1",
     "카드를 모두 나눠 갖고 ♣3을 가진 사람부터 시작해요. 같은 숫자 카드를 1~4장 내고, 다음 사람은 같은 장수로 더 센 숫자를 내거나 '패스'해요. 세기는 3이 가장 약하고 … K < A < 2 (2가 가장 세요). 모두 패스하면 마지막에 낸 사람이 아무 카드나 새로 내요. 카드를 먼저 다 낸 사람이 대통령, 마지막 사람은 거지! 카드를 눌러 고르고 '내기'를 눌러요.",
     r'''
const pw = c => (cr(c) + 11) % 13, PWN = "3 4 5 6 7 8 9 10 J Q K A 2";
function initState() { return { ph: "wait", rno: 0, ord: [], cnt: {}, turn: null, tb: [], last: null, passed: [], fin: [], msg: "" }; }
const live = id => !P.fin.includes(id);
const okPlay = L => L.length > 0 && L.length <= 4 && L.every(c => cr(c) === cr(L[0])) && (!P.tb.length || (L.length === P.tb.length && pw(L[0]) > pw(P.tb[0])));
const rankName = (k, n) => k === 0 ? "👑 대통령" : k === n - 1 ? "🧹 거지" : k === 1 ? "🎩 부통령" : "🙂 평민";
function advance(from) { const nx = nextIn(P.ord, from, id => live(id) && !P.passed.includes(id) && id !== P.last); if (nx) { P.turn = nx; return; }
  const lead = live(P.last) ? P.last : nextIn(P.ord, P.last, live); P.msg = `모두 패스! 이제 ${nmOf(lead)} 차례, 아무 카드나 새로 내요`; P.tb = []; P.passed = []; P.last = null; P.turn = lead; }
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") { const ps = canStart(2, 6); if (!ps) return; const dk = deck52(); H.hands = {}; ps.forEach(id => H.hands[id] = []); dk.forEach((c, i) => H.hands[ps[i % ps.length]].push(c));
    Object.assign(P, { ph: "play", rno: P.rno + 1, ord: ps, tb: [], last: null, passed: [], fin: [], msg: "♣3을 가진 사람이 먼저 내요" }); P.turn = ps.find(id => H.hands[id].includes(41)) || ps[0]; }
  else if (d.t === "play" && P.ph === "play" && from === P.turn && Array.isArray(d.cs)) { const L = [...new Set(d.cs.map(Number))], h = H.hands[from]; if (!L.every(c => h.includes(c)) || !okPlay(L)) return;
    H.hands[from] = h.filter(c => !L.includes(c)); P.tb = L; P.last = from; P.msg = `${nmOf(from)}: ${L.map(label).join(" ")}`;
    if (!H.hands[from].length) { P.fin.push(from); P.msg += ` · 다 냈어요! (${P.fin.length}등)`; }
    const rest = P.ord.filter(live); if (rest.length <= 1) { P.fin.push(...rest); P.ph = "end"; } else advance(from); }
  else if (d.t === "pass" && P.ph === "play" && from === P.turn && P.tb.length) { P.passed.push(from); P.msg = `${nmOf(from)} 패스`; advance(from); }
  else return;
  sync(); pushS();
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn(); if (P.ph === "wait") { $("st").textContent = waitText(2, 6); idle(); return; }
  const h = myHand().sort((a, b) => pw(a) - pw(b) || a - b), mine = P.ph === "play" && P.turn === me, n = P.ord.length;
  sel = sel.filter(c => h.includes(c));
  $("st").textContent = P.ph === "end" ? (P.fin.includes(me) ? `결과: 나는 ${rankName(P.fin.indexOf(me), n)}!` : `🎉 대통령: ${pn(P.fin[0])}`) : (P.msg ? P.msg + " · " : "") + (mine ? (P.tb.length ? `내 차례! ${P.tb.length}장으로 ${RK[cr(P.tb[0])]}보다 센 숫자를 내거나 패스` : "내 차례! 같은 숫자 1~4장을 골라 내요") : !P.ord.includes(me) ? `구경 중 · ${pn(P.turn)} 차례` : `${pn(P.turn)} 차례`);
  $("tbl").innerHTML = seats(id => P.fin.includes(id) ? rankName(P.fin.indexOf(id), n) : `${P.cnt[id]}장${P.passed.includes(id) ? " · 패스" : ""}`)
    + `<div class="tb">${P.ph === "play" && P.tb.length ? P.tb.map(c => cardHtml(c, "bg")).join("") + `<small>낸 사람: ${esc(pn(P.last))}</small>` : P.ph === "play" ? '<small>바닥이 비었어요 · 아무 카드나 낼 수 있어요</small>' : ""}</div><p class="note center">세기: ${PWN} (오른쪽일수록 세요)</p>`;
  $("hand").innerHTML = handBox(h, mine ? () => true : null); bindHand(c => toggle(c, 4));
  $("acts").innerHTML = mine ? `<button class="btn" id="pl" type="button"${okPlay(sel) ? "" : " disabled"}>🃏 내기 (${sel.length}장)</button>` + (P.tb.length ? '<button class="btn ghost" id="ps" type="button">🙅 패스</button>' : "") : "";
  if (mine) { $("pl").onclick = () => { act({ t: "play", cs: sel }); sel = []; }; if ($("ps")) $("ps").onclick = () => { sel = []; act({ t: "pass" }); }; }
}
render();
''')

# ── 세븐(7 늘어놓기, 2~6명): 카드를 모두 나누고 7 네 장은 처음부터 바닥에. 바닥 카드 바로 옆 숫자(같은 무늬)만 이어 놓을 수 있어요.
#   패스는 3번까지, 4번째로 패스하면 탈락(카드를 모두 바닥에 내려놓음). 먼저 다 낸 사람이 1등.
card("net-sevens.html", "세븐 7 늘어놓기 (같이 하기)", "7️⃣", 200, "net-sevens-v1",
     "카드를 모두 나눠 갖고, 7 네 장은 처음부터 바닥에 놓아요. 내 차례에는 바닥에 있는 카드 바로 옆 숫자(같은 무늬)를 한 장 이어 놓아요. 예: ♥7이 있으면 ♥6이나 ♥8. 낼 카드가 없거나 내기 싫으면 '패스'(한 판에 3번까지). 4번째 패스를 하면 탈락하고 카드를 모두 바닥에 내려놓아요. 카드를 먼저 다 낸 사람이 1등!",
     r'''
function initState() { return { ph: "wait", rno: 0, ord: [], cnt: {}, turn: null, tb: [], pass: {}, fin: [], dead: [], rank: null, msg: "" }; }
const live = id => !P.fin.includes(id) && !P.dead.includes(id);
const canPut = c => !P.tb.includes(c) && ((cr(c) > 0 && P.tb.includes(c - 1)) || (cr(c) < 12 && P.tb.includes(c + 1)));
function endChk() { const L = P.ord.filter(live); if (L.length <= 1) { P.rank = [...P.fin, ...L, ...P.dead.slice().reverse()]; P.ph = "end"; return true; } return false; }
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") { const ps = canStart(2, 6); if (!ps) return; const dk = deck52(); H.hands = {}; ps.forEach(id => H.hands[id] = []); dk.forEach((c, i) => H.hands[ps[i % ps.length]].push(c));
    ps.forEach(id => H.hands[id] = H.hands[id].filter(c => cr(c) !== 6));
    Object.assign(P, { ph: "play", rno: P.rno + 1, ord: ps, tb: [6, 19, 32, 45], pass: Object.fromEntries(ps.map(id => [id, 0])), fin: [], dead: [], rank: null, msg: "7은 모두 바닥에 놓았어요" }); P.turn = ps[(P.rno - 1) % ps.length];
    ps.forEach(id => { if (!H.hands[id].length) P.fin.push(id); }); if (!endChk() && !live(P.turn)) P.turn = nextIn(ps, P.turn, live); }
  else if (d.t === "put" && P.ph === "play" && from === P.turn) { const c = +d.c, h = H.hands[from]; if (!h.includes(c) || !canPut(c)) return;
    H.hands[from] = h.filter(x => x !== c); P.tb.push(c); P.msg = `${nmOf(from)}: ${label(c)}`; if (!H.hands[from].length) { P.fin.push(from); P.msg += ` · 다 냈어요! (${P.fin.length}등)`; }
    if (!endChk()) P.turn = nextIn(P.ord, from, live); }
  else if (d.t === "pass" && P.ph === "play" && from === P.turn) {
    if (P.pass[from] < 3) { P.pass[from]++; P.msg = `${nmOf(from)} 패스 (${P.pass[from]}/3)`; }
    else { P.tb.push(...H.hands[from]); H.hands[from] = []; P.dead.push(from); P.msg = `${nmOf(from)}: 패스를 다 써서 탈락! 카드를 모두 바닥에 놓았어요`; }
    if (!endChk()) P.turn = nextIn(P.ord, from, live); }
  else return;
  sync(); pushS();
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn(); if (P.ph === "wait") { $("st").textContent = waitText(2, 6); idle(); return; }
  const h = myHand().sort((a, b) => a - b), mine = P.ph === "play" && P.turn === me, place = id => P.rank ? P.rank.indexOf(id) + 1 : 0;
  $("st").textContent = P.ph === "end" ? (place(me) === 1 ? "🎉 1등이에요!" : P.rank ? `🎉 ${pn(P.rank[0])} 1등!${place(me) ? ` · 나는 ${place(me)}등` : ""}` : "끝!") : (P.msg ? P.msg + " · " : "") + (mine ? (h.some(canPut) ? "내 차례! 밝게 보이는 카드를 이어 놓아요" : "낼 카드가 없어요. 패스를 눌러요") : !P.ord.includes(me) ? `구경 중 · ${pn(P.turn)} 차례` : `${pn(P.turn)} 차례`);
  $("tbl").innerHTML = seats(id => P.ph === "end" ? `${place(id)}등${P.dead.includes(id) ? " 💀" : ""}` : P.fin.includes(id) ? `🏁 ${P.fin.indexOf(id) + 1}등` : P.dead.includes(id) ? "💀 탈락" : `${P.cnt[id]}장 · 패스 ${P.pass[id]}/3`)
    + "<div>" + SU.map((s, k) => `<div class="sv"><b class="${k === 1 || k === 2 ? "rdt" : ""}" style="${k === 1 || k === 2 ? "color:#d6453a" : ""}">${s}</b>${Array.from({ length: 13 }, (_, r) => { const c = k * 13 + r; return P.tb.includes(c) ? `<span class="${isRed(c) ? "rd" : ""}">${RK[r]}</span>` : '<span class="e"></span>'; }).join("")}</div>`).join("") + "</div>";
  $("hand").innerHTML = handBox(h, mine ? canPut : null); bindHand(c => act({ t: "put", c }));
  const left = P.ph === "play" && P.ord.includes(me) ? 3 - P.pass[me] : 0;
  $("acts").innerHTML = mine ? `<button class="btn ghost" id="ps" type="button">${left > 0 ? `🙅 패스 (남은 ${left}번)` : "💀 포기 (카드를 모두 내려놓기)"}</button>` : "";
  if (mine) $("ps").onclick = () => { if (left > 0 || confirm("패스를 다 썼어요. 탈락할까요?")) act({ t: "pass" }); };
}
render();
''')

# ── 포커(5장 바꾸기, 2~6명): 5장씩 받고, 한 번 최대 3장까지 바꿔요. 모두 바꾸면 카드를 공개하고 족보가 가장 높은 사람이 +1점.
#   족보: 하이 카드 < 원 페어 < 투 페어 < 트리플 < 스트레이트 < 플러시 < 풀 하우스 < 포카드 < 스트레이트 플러시 < 로열 스트레이트 플러시. A가 가장 높고, A-2-3-4-5도 스트레이트.
card("net-poker.html", "포커 5장 바꾸기 (같이 하기)", "♠️", 330, "net-poker-v1",
     "카드를 5장씩 받아요. 바꾸고 싶은 카드를 최대 3장까지 눌러 고르고 '바꾸기'(바꿀 게 없으면 '그대로')를 눌러요. 모두 바꾸면 카드를 공개하고 족보가 가장 높은 사람이 이겨요(+1점). 족보: 원 페어 < 투 페어 < 트리플 < 스트레이트 < 플러시 < 풀 하우스 < 포카드 < 스트레이트 플러시. 돈이 아니라 점수 놀이예요.",
     r'''
const HN = ["하이 카드", "원 페어", "투 페어", "트리플", "스트레이트", "플러시", "풀 하우스", "포카드", "스트레이트 플러시", "로열 스트레이트 플러시"];
function evalH(h) { const rs = h.map(c => (cr(c) + 12) % 13).sort((a, b) => b - a), su = h.map(cs), fl = su.every(s => s === su[0]);
  const cnt = {}; rs.forEach(r => cnt[r] = (cnt[r] || 0) + 1); const grp = Object.entries(cnt).map(([r, n]) => [n, +r]).sort((a, b) => b[0] - a[0] || b[1] - a[1]), ks = grp.map(g => g[1]);
  const u = [...new Set(rs)]; let st = -1; if (u.length === 5) { if (u[0] - u[4] === 4) st = u[0]; else if (u[0] === 12 && u[1] === 3) st = 3; }
  if (st >= 0 && fl) return [st === 12 ? 9 : 8, st]; if (grp[0][0] === 4) return [7, ...ks]; if (grp[0][0] === 3 && grp[1][0] === 2) return [6, ...ks]; if (fl) return [5, ...rs];
  if (st >= 0) return [4, st]; if (grp[0][0] === 3) return [3, ...ks]; if (grp[0][0] === 2 && grp[1][0] === 2) return [2, ...ks]; if (grp[0][0] === 2) return [1, ...ks]; return [0, ...rs]; }
const cmpH = (a, b) => { for (let i = 0; i < Math.max(a.length, b.length); i++) { const x = (a[i] || 0) - (b[i] || 0); if (x) return x; } return 0; };
function initState() { return { ph: "wait", rno: 0, ord: [], done: [], sw: {}, show: null, tot: {}, msg: "" }; }
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") { const ps = canStart(2, 6); if (!ps) return; H.dk = deck52(); H.hands = {}; ps.forEach(id => H.hands[id] = H.dk.splice(0, 5));
    Object.assign(P, { ph: "play", rno: P.rno + 1, ord: ps, done: [], sw: {}, show: null, msg: "" }); }
  else if (d.t === "swap" && P.ph === "play" && P.ord.includes(from) && !P.done.includes(from) && Array.isArray(d.cs)) { const h = H.hands[from], L = [...new Set(d.cs.map(Number))].filter(c => h.includes(c)); if (L.length > 3) return;
    H.hands[from] = h.map(c => L.includes(c) ? H.dk.pop() : c); P.done.push(from); P.sw[from] = L.length; P.msg = `${nmOf(from)}: ${L.length ? L.length + "장 바꿨어요" : "그대로"}`;
    if (P.ord.every(id => P.done.includes(id))) { const ev = Object.fromEntries(P.ord.map(id => [id, evalH(H.hands[id])])), best = P.ord.reduce((b, id) => cmpH(ev[id], ev[b]) > 0 ? id : b, P.ord[0]);
      const win = P.ord.filter(id => cmpH(ev[id], ev[best]) === 0); win.forEach(id => P.tot[id] = (P.tot[id] || 0) + 1);
      P.show = { hands: Object.fromEntries(P.ord.map(id => [id, H.hands[id].slice()])), ev: Object.fromEntries(P.ord.map(id => [id, ev[id][0]])), win }; P.ph = "end"; } }
  else return;
  pushS();
}
const pkSort = h => h.sort((a, b) => (cr(b) + 12) % 13 - (cr(a) + 12) % 13 || a - b);
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn(); if (P.ph === "wait") { $("st").textContent = waitText(2, 6); idle(); return; }
  if (P.ph === "end" && P.show) { const S = P.show;
    $("st").textContent = S.win.includes(me) ? (S.win.length > 1 ? "🤝 공동 1등!" : "🎉 내가 이겼어요!") : `🎉 ${S.win.map(pn).join(", ")} 승리!`;
    $("tbl").innerHTML = P.ord.map(id => `<div class="bjr"><div class="li"><span>${S.win.includes(id) ? "🏆 " : ""}${esc(pn(id))}</span><b>${HN[S.ev[id]]}</b></div><div class="hand sm">${pkSort(S.hands[id].slice()).map(c => cardHtml(c)).join("")}</div></div>`).join("") + totHtml();
    $("hand").innerHTML = ""; $("acts").innerHTML = ""; return; }
  const h = pkSort(myHand()), inG = P.ord.includes(me), wait = inG && !P.done.includes(me), now = h.length === 5 ? HN[evalH(h)[0]] : "";
  sel = sel.filter(c => h.includes(c));
  $("st").textContent = !inG ? `구경 중 · 바꾸기 ${P.done.length}/${P.ord.length}` : wait ? `바꿀 카드를 골라요 (최대 3장) · 지금: ${now}` : `지금 족보: ${now} · 다른 사람을 기다려요 (${P.done.length}/${P.ord.length})`;
  $("tbl").innerHTML = seats(id => P.done.includes(id) ? `✅ ${P.sw[id]}장 바꿈` : "고르는 중…");
  $("hand").innerHTML = handBox(h, wait ? () => true : null); bindHand(c => toggle(c, 3));
  $("acts").innerHTML = wait ? `<button class="btn" id="sw" type="button">${sel.length ? `🔄 ${sel.length}장 바꾸기` : "✋ 그대로 (안 바꾸기)"}</button>` : "";
  if (wait) $("sw").onclick = () => { act({ t: "swap", cs: sel }); sel = []; };
}
render();
''')

# ── 훌라(2~5명): 7장씩 받고, 차례마다 ① 더미나 버린 카드에서 한 장 가져오기 ② (할 수 있으면) 등록·붙이기 ③ 한 장 버리기.
#   등록: 같은 숫자 3~4장, 같은 무늬 이어진 숫자 3장 이상(A는 1로만), 7은 한 장도 등록 가능. 붙이기: 바닥에 등록된 카드(누구 것이든)에 이어 붙이기.
#   손의 카드를 먼저 모두 없애면 승리. 다른 사람은 남은 카드 점수(A=1, 숫자 그대로, J·Q·K=10)만큼 잃고 이긴 사람이 그만큼 얻어요.
#   그때까지 한 번도 등록하지 않다가 한 차례에 모두 내리면 '훌라!' — 점수 두 배.
card("net-hula.html", "훌라 (같이 하기)", "🃏", 10, "net-hula-v1",
     "7장씩 받고 시작해요. 내 차례에는 ① 더미나 버린 카드에서 한 장 가져오고 ② 할 수 있으면 등록·붙이기를 하고 ③ 한 장을 버리면 끝나요. 등록: 같은 숫자 3~4장, 또는 같은 무늬로 이어진 숫자 3장 이상(A는 1로만 써요). 7은 한 장만으로도 등록할 수 있어요. 붙이기: 바닥에 등록된 카드(누구 것이든)에 맞는 카드를 이어 붙여요. 손의 카드를 먼저 모두 없애면 이겨요! 다른 사람은 남은 카드 점수(A=1, J·Q·K=10)만큼 잃어요. 한 번도 등록하지 않다가 한 차례에 모두 내리면 '훌라!'로 점수가 두 배예요.",
     r'''
const pt = c => cr(c) >= 10 ? 10 : cr(c) + 1;
const isSet = (l, n) => l.length >= n && l.length <= 4 && l.every(c => cr(c) === cr(l[0]));
const isRun = (l, n) => { if (l.length < n || !l.every(c => cs(c) === cs(l[0]))) return false; const r = l.map(cr).sort((a, b) => a - b); return r.every((x, i) => !i || x === r[i - 1] + 1); };
const okMeld = (l, s7) => isSet(l, 3) || isRun(l, 3) || (l.length === 1 && cr(l[0]) === 6) || (!!s7 && (isSet(l, 1) || isRun(l, 1)));
const srt = l => l.slice().sort((a, b) => a - b);
function initState() { return { ph: "wait", rno: 0, ord: [], cnt: {}, turn: null, step: "draw", top: null, deckN: 0, melds: [], res: null, tot: {}, reg: {}, msg: "" }; }
function winBy(from, hula) { const pen = {}; let sum = 0; P.ord.forEach(id => { if (id === from) return; let s = H.hands[id].reduce((a, c) => a + pt(c), 0); if (hula) s *= 2; pen[id] = s; sum += s; P.tot[id] = (P.tot[id] || 0) - s; });
  P.tot[from] = (P.tot[from] || 0) + sum; P.res = { w: from, hula, pen, hands: Object.fromEntries(P.ord.map(id => [id, srt(H.hands[id])])) }; P.ph = "end";
  P.msg = hula ? `🎊 ${nmOf(from)} 훌라!! (점수 두 배)` : `🎉 ${nmOf(from)} 승리! 카드를 모두 내렸어요`; }
function takeDeck() { if (!H.dk.length && H.pile.length > 1) { const t = H.pile.pop(); H.dk = shuf(H.pile); H.pile = [t]; } return H.dk.length ? H.dk.pop() : null; }
function afterMove(from) { if (!H.hands[from].length) winBy(from, !H.rb); }
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") { const ps = canStart(2, 5); if (!ps) return; H.dk = deck52(); H.hands = {}; ps.forEach(id => H.hands[id] = H.dk.splice(0, 7)); H.pile = [H.dk.pop()];
    Object.assign(P, { ph: "play", rno: P.rno + 1, ord: ps, step: "draw", top: H.pile[0], melds: [], res: null, reg: {}, msg: "" }); P.turn = ps[(P.rno - 1) % ps.length]; }
  else if (P.ph !== "play" || from !== P.turn) return;
  else if (d.t === "deck" && P.step === "draw") { const c = takeDeck();
    if (c === null) { const w = P.ord.reduce((b, id) => H.hands[id].reduce((a, x) => a + pt(x), 0) < H.hands[b].reduce((a, x) => a + pt(x), 0) ? id : b, P.ord[0]); winBy(w, false); P.msg = `카드가 다 떨어졌어요. 남은 점수가 가장 적은 ${nmOf(w)} 승리!`; }
    else { H.hands[from].push(c); H.rb = !!P.reg[from]; P.step = "act"; P.msg = `${nmOf(from)}: 더미에서 한 장 가져옴`; } }
  else if (d.t === "pile" && P.step === "draw" && H.pile.length) { const c = H.pile.pop(); H.hands[from].push(c); P.top = H.pile.length ? H.pile[H.pile.length - 1] : null; H.rb = !!P.reg[from]; P.step = "act"; P.msg = `${nmOf(from)}: 버린 카드 ${label(c)} 가져옴`; }
  else if (d.t === "meld" && P.step === "act" && Array.isArray(d.cs)) { const L = [...new Set(d.cs.map(Number))], h = H.hands[from]; if (!L.every(c => h.includes(c)) || !okMeld(L, false)) return;
    H.hands[from] = h.filter(c => !L.includes(c)); P.melds.push({ o: from, cs: srt(L), s7: L.length === 1 }); P.reg[from] = true; P.msg = `${nmOf(from)}: ${L.map(label).join(" ")} 등록`; afterMove(from); }
  else if (d.t === "attach" && P.step === "act") { const c = +d.c, m = P.melds[+d.m], h = H.hands[from]; if (!m || !h.includes(c) || !okMeld([...m.cs, c], m.s7)) return;
    H.hands[from] = h.filter(x => x !== c); m.cs = srt([...m.cs, c]); P.reg[from] = true; P.msg = `${nmOf(from)}: ${label(c)} 붙이기`; afterMove(from); }
  else if (d.t === "discard" && P.step === "act") { const c = +d.c, h = H.hands[from]; if (!h.includes(c)) return; H.hands[from] = h.filter(x => x !== c); H.pile.push(c); P.top = c; P.msg = `${nmOf(from)}: ${label(c)} 버림`;
    if (!H.hands[from].length) winBy(from, !H.rb); else { P.turn = nextIn(P.ord, from, () => true); P.step = "draw"; } }
  else return;
  sync(); P.deckN = H.dk.length; pushS();
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn(); if (P.ph === "wait") { $("st").textContent = waitText(2, 5); idle(); return; }
  const h = myHand().sort((a, b) => a - b), mine = P.ph === "play" && P.turn === me, doing = mine && P.step === "act", R = P.res;
  sel = sel.filter(c => h.includes(c));
  $("st").textContent = P.ph === "end" ? (R && R.w === me ? (R.hula ? "🎊 훌라!! 내가 이겼어요 (점수 두 배)" : "🎉 내가 이겼어요!") : P.msg) : (P.msg ? P.msg + " · " : "") + (mine ? (P.step === "draw" ? "내 차례! 카드를 한 장 가져와요" : "등록·붙이기를 하고, 한 장을 버리면 차례가 끝나요") : !P.ord.includes(me) ? `구경 중 · ${pn(P.turn)} 차례` : `${pn(P.turn)} 차례`);
  $("tbl").innerHTML = seats(id => P.ph === "end" && R ? (id === R.w ? "🏆 승리" : `-${R.pen[id]}점`) : `${P.cnt[id]}장${P.reg[id] ? " · 등록" : ""}`)
    + (P.ph === "play" ? `<div class="pile"><div>${cardHtml(-1)}<small>더미 ${P.deckN}장</small></div><div>${P.top !== null ? cardHtml(P.top) : cardHtml(-1, "e")}<small>버린 카드</small></div></div>` : "")
    + (P.melds.length ? '<p class="lb">📋 등록된 카드</p>' + P.melds.map((m, i) => `<div class="meld"><small>${esc(pn(m.o))}</small><span class="hand sm">${m.cs.map(c => cardHtml(c)).join("")}</span>${doing && sel.length === 1 && okMeld([...m.cs, sel[0]], m.s7) ? `<button class="btn sm" type="button" data-m="${i}">붙이기</button>` : ""}</div>`).join("") : "")
    + (P.ph === "end" && R ? '<p class="lb">🂠 남은 카드</p>' + P.ord.filter(id => id !== R.w).map(id => `<div class="meld"><small>${esc(pn(id))}</small><span class="hand sm">${R.hands[id].map(c => cardHtml(c)).join("")}</span></div>`).join("") : "") + totHtml();
  $("tbl").querySelectorAll("[data-m]").forEach(b => b.onclick = () => { const c = sel[0]; sel = []; act({ t: "attach", c, m: +b.dataset.m }); });
  $("hand").innerHTML = handBox(h, doing ? () => true : null); bindHand(c => toggle(c, 0));
  $("acts").innerHTML = mine && P.step === "draw" ? '<button class="btn" id="dd" type="button">🂠 더미에서 한 장</button>' + (P.top !== null ? `<button class="btn ghost" id="dp" type="button">♻️ 버린 카드 ${label(P.top)} 가져오기</button>` : "")
    : doing ? `<button class="btn" id="rg" type="button"${okMeld(sel, false) ? "" : " disabled"}>📥 등록 (${sel.length}장)</button><button class="btn ghost" id="dc" type="button"${sel.length === 1 ? "" : " disabled"}>🗑️ 고른 1장 버리기</button>` : "";
  if ($("dd")) $("dd").onclick = () => act({ t: "deck" }); if ($("dp")) $("dp").onclick = () => act({ t: "pile" });
  if ($("rg")) $("rg").onclick = () => { const cs_ = sel; sel = []; act({ t: "meld", cs: cs_ }); };
  if ($("dc")) $("dc").onclick = () => { const c = sel[0]; sel = []; act({ t: "discard", c }); };
}
render();
''')
