import sys
sys.path.insert(0, ".")
from mkpage import make
from set30 import NET_JS, NET_CSS, LINK_CSS   # set30을 불러오면 같이 하기·틱택토·함선 찾기도 함께 다시 만들어져요

# ───────── 같이 하기 게임: 두 사람 대결 공통 (오목·사목·숫자 야구·빙고). 목록은 set30.py의 GAMES.
# 방장(a)과 처음 들어온 기기(b)가 대결, 나머지는 구경. 방장 게임이 판정하고 공개 상태 P를 모두에게 보내요.
# 숨겨야 하는 것(비밀 숫자·빙고 판)은 방장만 H에 들고, 끝나면 P.reveal로 공개해요.
# 게임마다 newRound()(새 판 상태), onAct(from, d)(행동 처리), render()(그리기)를 만들어요. 판마다 먼저 하는 사람(P.first)이 바뀌어요.
DUO_JS = NET_JS + r'''
let me = null, isHost = false, P = null;
const H = {};
const amPlayer = () => !!P && (me === P.a || me === P.b);
const oppOf = id => id === P.a ? P.b : P.a;
const nm = id => id === me ? "나" : id === P.a ? P.na : P.nb;
function round(keep) {
  const a = P ? P.a : "host", b = P ? P.b : null, opt = P ? P.opt : {}, sc = keep && P ? P.sc : {}, first = keep && P && b ? (P.first === a ? b : a) : a;
  Object.keys(H).forEach(k => delete H[k]); P = { a, b, opt, sc, first, win: null, ph: "wait" }; if (b) Object.assign(P, newRound());
}
function pickB(ps) { if (P.b && ps.some(p => p.id === P.b)) return false; const nx = ps.find(p => p.id !== "host"); P.b = nx ? nx.id : null; round(false); return true; }
function pushS() { if (!isHost) return; P.na = nameOf(P.a); P.nb = P.b ? nameOf(P.b) : ""; NET.send("*", { t: "state", P }); render(); }
function finish(w) { P.ph = "end"; P.win = w; P.sc[w] = (P.sc[w] || 0) + 1; }
const act = d => { if (isHost) { if (P && (P.a === "host" || P.b === "host")) onAct("host", d); } else NET.send("host", d); };
NET.on("init", m => { me = m.me.id; isHost = m.isHost; if (isHost) { round(false); pickB(m.players); pushS(); } else NET.send("host", { t: "hello" }); render(); });
NET.on("roster", ps => { if (isHost && P) { pickB(ps); pushS(); } else render(); });
NET.on("msg", (from, d) => { if (isHost) { if (d.t === "hello") pushS(); else if (P && (from === P.a || from === P.b)) onAct(from, d); } else if (d.t === "state") { const was = P && P.ph; P = d.P; changed(was); render(); } });
const scoreLine = () => P && P.b ? `${P.na} ${P.sc[P.a] || 0} : ${P.sc[P.b] || 0} ${P.nb}${P.sc.D ? " · 무승부 " + P.sc.D : ""}` : "";
const endText = () => P.win === "D" ? "비겼어요!" : P.win === me ? "🎉 이겼어요!" : amPlayer() ? "😢 졌어요… 다음 판에 다시!" : `🎉 ${nm(P.win)} 승리!`;
function common() { $("again").hidden = !(amPlayer() && P.ph === "end"); $("sc").textContent = scoreLine(); }
$("again").onclick = () => act({ t: "again" });
'''
AGAIN = '''<p class="center note" id="sc"></p><button class="btn ghost sm" id="again" type="button" hidden>새 판</button>'''
LINE_FIND = r'''
// 같은 돌이 k개 이상 이어졌는지: 이어진 칸 목록(없으면 null)
function lineAt(g, i, W, Hh, k) { const v = g[i], y0 = Math.floor(i / W), x0 = i % W;
  for (const [dx, dy] of [[1, 0], [0, 1], [1, 1], [1, -1]]) { const cells = [i];
    for (const s of [1, -1]) { let x = x0 + dx * s, y = y0 + dy * s; while (x >= 0 && y >= 0 && x < W && y < Hh && g[y * W + x] === v) { cells.push(y * W + x); x += dx * s; y += dy * s; } }
    if (cells.length >= k) return cells; }
  return null; }
'''

# ── 오목: 15×15, 5개 이상 이으면 승리(시작 화면의 오목과 같은 규칙). 먼저 하는 사람이 흑.
#   칸이 작아서 한 번 누르면 미리 보기, 같은 곳을 한 번 더 누르거나 "여기 두기"로 놓아요.
make("out/net-omok.html", "오목 (같이 하기)", "⚫", 35, "net-omok-v1",
     "가로, 세로, 대각선으로 내 돌 5개를 먼저 이으면 이겨요. 먼저 하는 사람이 흑이고, 판마다 순서가 바뀌어요. 칸을 한 번 누르면 미리 보기, 같은 곳을 한 번 더 누르거나 '여기 두기'를 누르면 놓아져요.",
     '''  <div class="card"><p class="center" id="st"></p><canvas id="cv" style="width:100%;max-width:400px;aspect-ratio:1;margin:0 auto;display:block;border-radius:10px;touch-action:manipulation"></canvas>
    <button class="btn sm" id="put" type="button" hidden>✅ 여기 두기</button>''' + AGAIN + '</div>',
     DUO_JS + LINE_FIND + r'''
const N = 15, cv = $("cv"), ctx = cv.getContext("2d"); let sel = -1;
function newRound() { return { ph: "play", g: Array(N * N).fill(0), turn: P.first, last: -1, line: [] }; }
function onAct(from, d) {
  if (d.t === "put" && P.ph === "play" && from === P.turn) { const i = +d.i; if (!(i >= 0 && i < N * N) || P.g[i]) return; P.g[i] = from === P.first ? 1 : 2; P.last = i;
    const w = lineAt(P.g, i, N, N, 5); if (w) { P.line = w; finish(from); } else if (P.g.every(Boolean)) finish("D"); else P.turn = oppOf(from); pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
const canPlay = () => P && P.ph === "play" && P.turn === me;
const colorOf = id => id === P.first ? 1 : 2;
function geo() { const w = cv.clientWidth || 300, dpr = devicePixelRatio || 1; if (cv.width !== Math.round(w * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(w * dpr); } return { w, dpr, gap: w / (N + 1) }; }
function draw() {
  const { w, dpr, gap } = geo(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.fillStyle = "#e3b872"; ctx.fillRect(0, 0, w, w); ctx.strokeStyle = "#5a4020"; ctx.lineWidth = 1;
  for (let k = 1; k <= N; k++) { ctx.beginPath(); ctx.moveTo(gap, k * gap); ctx.lineTo(N * gap, k * gap); ctx.moveTo(k * gap, gap); ctx.lineTo(k * gap, N * gap); ctx.stroke(); }
  [[3, 3], [3, 11], [7, 7], [11, 3], [11, 11]].forEach(([x, y]) => { ctx.beginPath(); ctx.arc((x + 1) * gap, (y + 1) * gap, 2.5, 0, 7); ctx.fillStyle = "#5a4020"; ctx.fill(); });
  if (!P || !P.g) return;
  const xy = i => [(i % N + 1) * gap, (Math.floor(i / N) + 1) * gap];
  const stone = (i, v, a) => { const [x, y] = xy(i); ctx.globalAlpha = a; ctx.beginPath(); ctx.arc(x, y, gap * .45, 0, 7); ctx.fillStyle = v === 1 ? "#111" : "#fafafa"; ctx.fill(); ctx.strokeStyle = "#333"; ctx.stroke(); ctx.globalAlpha = 1; };
  const dot = (i, c) => { const [x, y] = xy(i); ctx.beginPath(); ctx.arc(x, y, gap * .16, 0, 7); ctx.fillStyle = c; ctx.fill(); };
  P.g.forEach((v, i) => { if (v) stone(i, v, 1); });
  if (sel >= 0 && !P.g[sel] && canPlay()) stone(sel, colorOf(me), .5);
  if (P.last >= 0) dot(P.last, "#e53935"); (P.line || []).forEach(i => dot(i, "#2e7d32"));
}
cv.onclick = e => { if (!canPlay()) return; const r = cv.getBoundingClientRect(), { gap } = geo(), x = Math.round((e.clientX - r.left) / gap) - 1, y = Math.round((e.clientY - r.top) / gap) - 1;
  if (x < 0 || y < 0 || x >= N || y >= N) return; const i = y * N + x; if (P.g[i]) return; if (sel === i) return put(); sel = i; render(); };
function put() { if (sel < 0 || !canPlay()) return; const i = sel; sel = -1; act({ t: "put", i }); render(); }
$("put").onclick = put;
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; draw(); return; }
  const pl = amPlayer(), stoneName = id => (id === P.first ? "⚫ " : "⚪ ") + nm(id);
  $("st").textContent = P.ph === "wait" ? "상대가 들어오면 시작해요" : P.ph === "end" ? endText() : !pl ? `구경 중 · ${stoneName(P.turn)} 차례` : P.turn === me ? `내 차례예요 (${colorOf(me) === 1 ? "⚫ 흑" : "⚪ 백"}) · 놓을 곳을 눌러요` : "상대 차례예요…";
  if (!canPlay()) sel = -1; $("put").hidden = !(sel >= 0); common(); draw();
}
addEventListener("resize", () => draw());
render();
''', LINK_CSS + NET_CSS)

# ── 사목: 7열×6줄, 위에서 떨어뜨려 4개 잇기(시작 화면의 사목과 같은 규칙). 먼저 하는 사람이 🔴.
make("out/net-four.html", "사목 (같이 하기)", "🔴", 210, "net-four-v1",
     "열을 눌러 내 돌을 위에서 떨어뜨려요. 가로, 세로, 대각선으로 같은 색 4개를 먼저 이으면 이겨요. 먼저 하는 사람이 🔴이고, 판마다 순서가 바뀌어요.",
     '''  <div class="card"><p class="center" id="st"></p><div class="c4" id="bd"></div>''' + AGAIN + '</div>',
     DUO_JS + LINE_FIND + r'''
const R = 6, C = 7;
function newRound() { return { ph: "play", g: Array(R * C).fill(0), turn: P.first, last: -1, line: [] }; }
function onAct(from, d) {
  if (d.t === "drop" && P.ph === "play" && from === P.turn) { const c = +d.c; if (!(c >= 0 && c < C)) return; let i = -1; for (let r = R - 1; r >= 0; r--) if (!P.g[r * C + c]) { i = r * C + c; break; } if (i < 0) return;
    P.g[i] = from === P.first ? 1 : 2; P.last = i; const w = lineAt(P.g, i, C, R, 4); if (w) { P.line = w; finish(from); } else if (P.g.every(Boolean)) finish("D"); else P.turn = oppOf(from); pushS(); }
  else if (d.t === "again" && P.ph === "end") { round(true); pushS(); }
}
function changed(was) {}
const mine = () => P.first === me ? "🔴" : "🟡";
function render() {
  if (!P || !P.g) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("bd").innerHTML = ""; if (P) common(); return; }
  const pl = amPlayer(), can = P.ph === "play" && P.turn === me, chip = id => (id === P.first ? "🔴 " : "🟡 ") + nm(id);
  $("st").textContent = P.ph === "end" ? endText() : !pl ? `구경 중 · ${chip(P.turn)} 차례` : can ? `내 차례예요 (${mine()}) · 열을 눌러요` : "상대 차례예요…";
  $("bd").innerHTML = P.g.map((v, i) => `<button type="button" data-c="${i % C}" class="${(P.line || []).includes(i) ? "w" : ""}${i === P.last ? " last" : ""}"${can ? "" : " disabled"} aria-label="${i % C + 1}열">${v === 1 ? "🔴" : v === 2 ? "🟡" : ""}</button>`).join("");
  if (can) $("bd").querySelectorAll("[data-c]").forEach(b => b.onclick = () => act({ t: "drop", c: +b.dataset.c }));
  common();
}
render();
''', LINK_CSS + NET_CSS + '''
.c4{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;width:min(100%,340px);margin:0 auto;background:#2856b8;padding:6px;border-radius:12px}
.c4 button{aspect-ratio:1;border-radius:50%;border:0;background:var(--surface);font-size:1.4rem;line-height:1;padding:0}.c4 button.w{box-shadow:0 0 0 3px #2fd27a inset}.c4 button.last{outline:2px solid #fff}.c4 button[disabled]{cursor:default}''')

# ── 숫자 야구 대결: 각자 서로 다른 숫자로 된 비밀 숫자(3 또는 4자리, 방장이 고름)를 정하고, 번갈아 상대 숫자를 맞혀요.
#   S 숫자·자리 모두 맞음, B 숫자만 맞음. 먼저 하는 사람이 맞히면 상대에게 마지막 한 번(같은 횟수)을 줘서, 둘 다 맞히면 무승부.
make("out/net-baseball.html", "숫자 야구 대결 (같이 하기)", "⚾", 140, "net-baseball-v1",
     "각자 서로 다른 숫자로 된 비밀 숫자를 정하고, 번갈아 상대 숫자를 맞혀요. S(스트라이크)는 숫자와 자리가 모두 맞음, B(볼)는 숫자는 있지만 자리가 다름이에요. 먼저 하는 사람이 맞히면 상대에게도 같은 횟수가 되도록 마지막 한 번의 기회가 있어서, 둘 다 맞히면 무승부예요.",
     '''  <div class="card"><p class="center" id="st"></p>
    <div class="seg" id="lenb" style="--n:2" hidden><button type="button" data-n="3">3자리</button><button type="button" data-n="4">4자리</button></div>
    <p class="center" id="mysec"></p>
    <div id="kpw" hidden><div class="slots" id="slots"></div><div class="kp" id="kp"></div><div class="row" id="kpb"></div></div>
    <div class="g2h"><div><div class="lb" id="h1l"></div><div id="h1"></div></div><div><div class="lb" id="h2l"></div><div id="h2"></div></div></div>''' + AGAIN + '</div>',
     DUO_JS + r'''
const okNum = (s, n) => typeof s === "string" && s.length === n && /^\d+$/.test(s) && new Set(s).size === n;
const sb = (g, s) => { let S = 0, B = 0; [...g].forEach((c, i) => { if (s[i] === c) S++; else if (s.includes(c)) B++; }); return [S, B]; };
const L = () => (P && P.opt && P.opt.len) || 3;
let secret = "", buf = "";
function newRound() { return { ph: "set", ready: {}, hist: { [P.a]: [], [P.b]: [] }, turn: null, fin: null, reveal: null }; }
function onAct(from, d) {
  const n = L();
  if (d.t === "len" && from === P.a && P.ph === "set" && !Object.keys(P.ready).length && (d.n === 3 || d.n === 4)) { P.opt.len = d.n; Object.assign(P, newRound()); }
  else if (d.t === "secret" && P.ph === "set" && okNum(d.s, n)) { H[from] = d.s; P.ready[from] = 1; if (P.ready[P.a] && P.ready[P.b]) { P.ph = "play"; P.turn = P.first; } }
  else if (d.t === "unready" && P.ph === "set") { delete P.ready[from]; delete H[from]; }
  else if (d.t === "guess" && P.ph === "play" && from === P.turn && okNum(d.g, n)) {
    const opp = oppOf(from), [S, B] = sb(d.g, H[opp]); P.hist[from].push([d.g, S, B]);
    if (S === n) { if (from === P.first && !P.fin) { P.fin = from; P.turn = opp; } else finish(P.fin ? "D" : from); }
    else if (P.fin) finish(P.fin); else P.turn = opp;
    if (P.ph === "end") P.reveal = { [P.a]: H[P.a], [P.b]: H[P.b] };
  }
  else if (d.t === "again" && P.ph === "end") round(true);
  else return;
  pushS();
}
function changed(was) { if (P.ph === "set" && was !== "set") { secret = ""; buf = ""; } }
const res = ([g, S, B]) => `<div class="li"><b>${g}</b><span>${S === 0 && B === 0 ? "아웃" : (S ? S + "S " : "") + (B ? B + "B" : "")}${S === L() ? " 🎯" : ""}</span></div>`;
function keypad(onOk, okLabel, extra) {
  const n = L();
  $("slots").innerHTML = Array.from({ length: n }, (_, i) => `<span>${buf[i] || ""}</span>`).join("");
  $("kp").innerHTML = "1234567890".split("").map(c => `<button type="button" data-k="${c}"${buf.includes(c) || buf.length >= n ? " disabled" : ""}>${c}</button>`).join("") + '<button type="button" data-k="x" aria-label="지우기">⌫</button>';
  $("kp").querySelectorAll("[data-k]").forEach(b => b.onclick = () => { buf = b.dataset.k === "x" ? buf.slice(0, -1) : buf + b.dataset.k; render(); });
  $("kpb").innerHTML = (extra || "") + `<button class="btn sm" id="kok" type="button"${buf.length === n ? "" : " disabled"}>${okLabel}</button>`;
  $("kok").onclick = () => { const v = buf; buf = ""; onOk(v); };
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; $("kpw").hidden = true; return; }
  const pl = amPlayer(), n = L(), opp = pl ? oppOf(me) : null;
  $("lenb").hidden = !(isHost && pl && P.ph === "set" && !Object.keys(P.ready || {}).length);
  $("lenb").querySelectorAll("button").forEach(b => { b.classList.toggle("on", +b.dataset.n === n); b.onclick = () => { buf = ""; act({ t: "len", n: +b.dataset.n }); }; });
  $("kpw").hidden = true; $("mysec").textContent = "";
  if (P.ph === "wait") $("st").textContent = "상대가 들어오면 시작해요";
  else if (P.ph === "set") {
    $("st").textContent = !pl ? `${P.na}·${P.nb} 님이 비밀 숫자를 정하는 중… (${n}자리)` : P.ready[me] ? (P.ready[opp] ? "곧 시작해요!" : "정했어요! 상대를 기다려요…") : `내 비밀 숫자를 정해요 (${n}자리, 서로 다른 숫자)${P.ready[opp] ? " · 상대는 정했어요" : ""}`;
    if (pl && !P.ready[me]) { $("kpw").hidden = false; keypad(v => { secret = v; act({ t: "secret", s: v }); }, "✅ 이 숫자로 정하기", '<button class="btn ghost sm" id="rnd" type="button">🎲 아무거나</button>'); $("rnd").onclick = () => { buf = shuf("0123456789".split("")).slice(0, n).join(""); render(); }; }
    if (pl && P.ready[me]) { $("mysec").innerHTML = `내 비밀 숫자: <b>${secret}</b> <button class="btn ghost sm" id="unr" type="button">↩ 다시 정하기</button>`; $("unr").onclick = () => act({ t: "unready" }); }
  } else if (P.ph === "play") {
    const can = P.turn === me;
    $("st").textContent = !pl ? `구경 중 · ${nm(P.turn)} 차례` : can ? (P.fin ? "🎯 상대가 맞혔어요! 마지막 기회예요" : "🎯 내 차례! 상대 숫자를 맞혀 보세요") : "상대가 맞히는 중…";
    if (pl) $("mysec").innerHTML = `내 비밀 숫자: <b>${secret}</b>`;
    if (pl && can) { $("kpw").hidden = false; keypad(v => act({ t: "guess", g: v }), "던지기 ⚾"); }
  } else { const rv = P.reveal || {}; $("st").textContent = endText(); $("mysec").innerHTML = `${esc(nm(P.a))}: <b>${rv[P.a] || "?"}</b> · ${esc(nm(P.b))}: <b>${rv[P.b] || "?"}</b>`; }
  const show = P.ph === "play" || P.ph === "end", x = pl ? me : P.a, y = pl ? opp : P.b;
  $("h1l").textContent = show ? (pl ? "내가 던진 공 (상대 숫자)" : `${nm(x)}가 던진 공`) : ""; $("h2l").textContent = show ? (pl ? "상대가 던진 공 (내 숫자)" : `${nm(y)}가 던진 공`) : "";
  $("h1").innerHTML = show ? ((P.hist[x] || []).slice().reverse().map(res).join("") || '<p class="note">아직 없어요</p>') : "";
  $("h2").innerHTML = show ? ((P.hist[y] || []).slice().reverse().map(res).join("") || '<p class="note">아직 없어요</p>') : "";
  common();
}
render();
''', LINK_CSS + NET_CSS + '''
.slots{display:flex;justify-content:center;gap:8px;margin-bottom:8px}.slots span{width:46px;height:54px;border-radius:12px;border:2px solid var(--line);display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:1.8rem}
.kp{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:8px}.kp button{padding:12px 0;border-radius:12px;border:1px solid var(--line);background:var(--soft);font-family:var(--font-display);font-size:1.4rem}.kp button[disabled]{opacity:.35}
.g2h{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}.g2h .li{font-variant-numeric:tabular-nums}''')

# ── 빙고 대결: 각자 1~25가 섞인 5×5 판, 번갈아 숫자를 불러 두 판에 모두 표시. 가로·세로·대각선 한 줄이 1줄, 먼저 5줄이면 승리(같이 5줄이면 무승부).
make("out/net-bingo.html", "빙고 대결 (같이 하기)", "🔢", 280, "net-bingo-v1",
     "1~25가 섞인 내 판을 정하고, 번갈아 내 판에서 숫자를 하나씩 불러요. 불린 숫자는 두 사람 판에 모두 표시돼요. 가로, 세로, 대각선 한 줄이 다 차면 1줄! 먼저 5줄을 만들면 이기고, 같은 숫자로 둘 다 5줄이 되면 무승부예요.",
     '''  <div class="card"><p class="center" id="st"></p><p class="center big" id="lastc" hidden></p>
    <div class="stats" id="lines"></div><div class="bg" id="bd"></div>
    <div class="row" id="place"><button class="btn ghost sm" id="shuf" type="button">🔀 다시 섞기</button><button class="btn sm" id="rdy" type="button">✅ 이 판으로 하기</button></div>
    <div id="oppw" hidden><div class="lb" id="oppl"></div><div class="bg small" id="obd"></div></div>''' + AGAIN + '</div>',
     DUO_JS + r'''
const okBoard = b => Array.isArray(b) && b.length === 25 && [...b].sort((x, y) => x - y).every((v, i) => v === i + 1);
const LN = []; for (let i = 0; i < 5; i++) { LN.push([0, 1, 2, 3, 4].map(j => i * 5 + j), [0, 1, 2, 3, 4].map(j => j * 5 + i)); } LN.push([0, 6, 12, 18, 24], [4, 8, 12, 16, 20]);
const linesOf = (b, called) => LN.filter(l => l.every(i => called.includes(b[i]))).length;
const fresh = () => shuf(Array.from({ length: 25 }, (_, i) => i + 1));
let board = fresh();
function newRound() { return { ph: "set", ready: {}, called: [], turn: null, lines: {}, last: null, reveal: null }; }
function onAct(from, d) {
  if (d.t === "board" && P.ph === "set" && okBoard(d.b)) { H[from] = d.b; P.ready[from] = 1; if (P.ready[P.a] && P.ready[P.b]) { P.ph = "play"; P.turn = P.first; P.lines = { [P.a]: 0, [P.b]: 0 }; } }
  else if (d.t === "unready" && P.ph === "set") { delete P.ready[from]; delete H[from]; }
  else if (d.t === "call" && P.ph === "play" && from === P.turn) { const n = +d.n; if (!(n >= 1 && n <= 25) || P.called.includes(n)) return; P.called.push(n); P.last = n;
    const la = linesOf(H[P.a], P.called), lb = linesOf(H[P.b], P.called); P.lines = { [P.a]: la, [P.b]: lb };
    if (la >= 5 || lb >= 5) { finish(la >= 5 && lb >= 5 ? "D" : la >= 5 ? P.a : P.b); P.reveal = { [P.a]: H[P.a], [P.b]: H[P.b] }; } else P.turn = oppOf(from); }
  else if (d.t === "again" && P.ph === "end") round(true);
  else return;
  pushS();
}
function changed(was) { if (P.ph === "set" && was !== "set") board = fresh(); }
function grid(el, b, click) {
  const called = P.called || [], done = new Set(LN.filter(l => l.every(i => called.includes(b[i]))).flat());
  el.innerHTML = b.map((v, i) => { const on = called.includes(v); return `<button type="button" data-n="${v}" class="${on ? "on" : ""}${done.has(i) ? " ln" : ""}${v === P.last ? " last" : ""}"${click && !on ? "" : " disabled"}>${v}</button>`; }).join("");
  if (click) el.querySelectorAll("[data-n]:not([disabled])").forEach(x => x.onclick = () => act({ t: "call", n: +x.dataset.n }));
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; $("place").hidden = true; return; }
  const pl = amPlayer(), opp = pl ? oppOf(me) : null, called = P.called || [], rd = P.ready || {};
  $("place").hidden = !(pl && P.ph === "set"); $("rdy").textContent = rd[me] ? "↩ 다시 고르기" : "✅ 이 판으로 하기"; $("shuf").disabled = !!rd[me];
  $("lastc").hidden = !P.last; $("lastc").textContent = P.last ? `📣 ${P.last}` : "";
  if (P.ph === "wait") $("st").textContent = "상대가 들어오면 시작해요";
  else if (P.ph === "set") $("st").textContent = !pl ? `${P.na}·${P.nb} 님이 판을 고르는 중…` : rd[me] ? (rd[opp] ? "곧 시작해요!" : "준비 완료! 상대를 기다려요…") : `내 빙고 판이에요. 마음에 들면 시작!${rd[opp] ? " (상대는 준비됐어요)" : ""}`;
  else if (P.ph === "play") $("st").textContent = !pl ? `구경 중 · ${nm(P.turn)} 차례 · 부른 숫자 ${called.length}개` : P.turn === me ? "📣 내 차례! 내 판에서 부를 숫자를 눌러요" : "상대가 숫자를 고르는 중…";
  else $("st").textContent = endText();
  const ls = P.lines || {}; $("lines").innerHTML = P.ph === "play" || P.ph === "end" ? [P.a, P.b].map(id => `<div class="stat"><small>${esc(nm(id))}</small><b>${ls[id] || 0}줄</b></div>`).join("") + `<div class="stat"><small>부른 숫자</small><b>${called.length}</b></div>` : "";
  const rv = P.reveal || {};
  if (pl) grid($("bd"), P.ph === "end" && rv[me] ? rv[me] : board, P.ph === "play" && P.turn === me);
  else if (P.ph === "end") grid($("bd"), rv[P.a], false);
  else $("bd").innerHTML = called.length ? `<p class="note center" style="grid-column:1/-1">부른 숫자: ${called.join(", ")}</p>` : "";
  $("oppw").hidden = P.ph !== "end"; if (P.ph === "end") { const o = pl ? opp : P.b; $("oppl").textContent = `${nm(o)}의 판`; grid($("obd"), rv[o], false); }
  common();
}
$("shuf").onclick = () => { if (P && P.ready && P.ready[me]) return; board = fresh(); render(); };
$("rdy").onclick = () => { if (!amPlayer() || P.ph !== "set") return; act(P.ready[me] ? { t: "unready" } : { t: "board", b: board }); };
render();
''', LINK_CSS + NET_CSS + '''
.bg{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;width:min(100%,320px);margin:0 auto}.bg.small{width:min(100%,220px)}
.bg button{aspect-ratio:1;border-radius:10px;border:1px solid var(--line);background:var(--soft);font-family:var(--font-display);font-size:1.3rem;padding:0}.bg.small button{font-size:.95rem;border-radius:7px}
.bg button.on{background:color-mix(in srgb,var(--accent) 35%,var(--surface))}.bg button.ln{background:color-mix(in srgb,var(--ok) 40%,var(--surface))}.bg button.last{outline:3px solid var(--bad)}.bg button[disabled]{cursor:default}
.stats .stat b{font-size:1.2rem}''')
