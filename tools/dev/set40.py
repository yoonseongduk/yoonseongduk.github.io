import sys
sys.path.insert(0, ".")
from mkpage import make
from set33 import duo        # set33(→set32→set31→set30)를 불러오면 같이 하기 게임이 모두 다시 만들어져요(윷놀이 net-yut 는 아래에서 새로 덮어써요)

# ───────── 윷놀이(일반 규칙): 시작 화면 yut-nori.html(컴퓨터와 1:1) + 같이 하기 net-yut.html(2명).
#   규칙 엔진은 yut-core.js(순수 함수, 시험 tools/dev/yut_test.js). 말 4개씩, 29칸 말판, 지름길(5·10·가운데), 업기, 빽도, 잡기, 윷·모·잡기는 한 번 더.
#   이 파일이 예전 윷놀이(set14b.py 의 yut-nori, set33.py 의 net-yut: 20칸 원형·말 2개)를 대신해요. 두 쪽 모두 아래 SHARED 를 같이 써요.

SHARED = r'''
const Y = window.YutCore, YCOL = ["#3b6fd6", "#d6453a"];
// 말판 그리기. sides = [{s: 편 상태, c: 색}], hl = 도착할 수 있는 칸 목록(눌러서 고르기)
function yBoard(sides, hl) {
  const X = Y.XY, hs = new Set(hl || []);
  const L = (a, b) => `<line x1="${X[a][0]}" y1="${X[a][1]}" x2="${X[b][0]}" y2="${X[b][1]}" class="yl"/>`;
  let h = `<polygon points="${[0, 5, 10, 15].map(i => X[i].join(",")).join(" ")}" class="yl"/>` + L(5, 22) + L(22, 15) + L(10, 22) + L(22, 0);
  for (let n = 0; n < 29; n++) {
    const big = Y.CORNER[n], r = big ? 17 : 11, on = hs.has(n) ? " hl" : "";
    h += `<circle cx="${X[n][0]}" cy="${X[n][1]}" r="${r}" class="yc${big ? " big" : ""}${on}" data-to="${n}"/>`;
    h += n === 0 ? `<text x="${X[n][0]}" y="${X[n][1] - 1}" class="yn s" text-anchor="middle">출발</text><text x="${X[n][0]}" y="${X[n][1] + 8}" class="yn s" text-anchor="middle">도착</text>` : `<text x="${X[n][0]}" y="${X[n][1] + 3}" class="yn" text-anchor="middle">${n === 22 ? "중앙" : n}</text>`;
  }
  sides.forEach((sd, i) => sd.s.stacks.forEach(st => { const [x, y] = X[st.at];
    h += `<g class="yt" data-to="${st.at}"><circle cx="${x}" cy="${y}" r="14" fill="${sd.c}" stroke="#fff" stroke-width="2.5"/>${st.n > 1 ? `<text x="${x}" y="${y + 5}" text-anchor="middle" class="ytn">${st.n}</text>` : ""}</g>`; }));
  return `<svg class="yb" viewBox="0 0 320 320" role="img" aria-label="윷놀이 말판">${h}</svg>`;
}
const yNode = n => n === 0 ? "출발점" : n === 22 ? "가운데(22번)" : (n === 5 || n === 10 || n === 15 ? n + "번(모서리)" : n + "번 칸");
const yTo = t => t === Y.END ? "도착! 🏁" : t === Y.HOME ? "출발 전으로 돌아가요" : yNode(t);
function yOpt(m, sd) { // 움직임 하나를 글로: "3번 칸의 말 2개(업은 말) → 8번 칸 · 잡기!"
  const from = m.from < 0 ? "출발 전 말 1개" : yNode(sd.stacks[m.from].at) + "의 말 " + m.n + "개" + (m.n > 1 ? "(업은 말)" : "");
  return from + " → " + yTo(m.to) + (m.cap ? " · 잡기! (" + m.cap + "개)" : "") + (m.stack ? " · 업기" : "");
}
function ySticks(t) { return t ? t.flat.map((f, i) => `<span class="${f ? "sf" : "sr"}${i === 0 ? " mk" : ""}">${f ? "▬" : "◖"}</span>`).join("") : "🥢🥢🥢🥢"; }
function yPanel(sd, mark) { return `${mark} 출발 전 ${sd.w} · 도착 ${sd.done}/4` + (sd.stacks.length ? " · 판 위 " + sd.stacks.map(s => yNode(s.at) + (s.n > 1 ? " ×" + s.n : "")).join(", ") : ""); }
const yRules = () => `<details open><summary>📘 윷놀이 규칙 (일반 규칙)</summary><div class="note" style="margin-top:6px">
  <b>목표</b>: 내 말 <b>4개</b>를 먼저 모두 한 바퀴 돌려 <b>도착</b>시키면 이겨요.<br>
  <b>윷 던지기</b>: 가락 4개의 평평한 면(▬)이 몇 개인지 봐요.
  <table class="tbl"><tbody><tr><td>평평한 면 1개</td><td><b>도</b> 1칸 (표시된 ✖ 가락이 평평하면 <b>빽도</b>: 뒤로 1칸)</td></tr><tr><td>2개</td><td><b>개</b> 2칸</td></tr><tr><td>3개</td><td><b>걸</b> 3칸</td></tr><tr><td>4개</td><td><b>윷</b> 4칸 · 한 번 더</td></tr><tr><td>0개(모두 둥글어요)</td><td><b>모</b> 5칸 · 한 번 더</td></tr></tbody></table>
  <b>말판</b>: 바깥 길을 반시계 방향으로 출발점(0)에서 시작해 19번 칸을 지나면 도착이에요. 말은 던진 칸 수만큼 움직여요. 도착은 출발점을 정확히 밟거나 지나가면 돼요.<br>
  <b>🔀 지름길</b>: 모서리 <b>5번</b>이나 <b>10번</b>에 <b>서 있다가</b> 다음에 움직이면 안쪽 길로 들어가요. 그냥 지나가기만 하면 바깥 길이에요.<br>
  &nbsp;&nbsp;• 5번에서 시작: 20→21→<b>가운데(22)</b>→23→24→15번으로 나와 바깥 길(15 이후)을 이어 가요.<br>
  &nbsp;&nbsp;• 10번에서 시작: 25→26→<b>가운데(22)</b>→27→28→바로 도착! (가장 빨라요)<br>
  &nbsp;&nbsp;• 가운데(22)에 서 있다가 움직이면 27→28→도착 쪽으로 나가요.<br>
  <b>🤝 업기</b>: 내 말이 있는 칸에 내 다른 말이 도착하면 한 덩어리가 돼서 <b>함께 움직여요</b>(숫자로 표시). 이동할 때도, 잡힐 때도 같이예요.<br>
  <b>⚔️ 잡기</b>: 상대 말이 있는 칸에 서면 그 칸의 상대 말을 <b>모두 잡아</b> 출발 전으로 돌려보내요. 잡으면 <b>한 번 더</b> 던져요.<br>
  <b>↩️ 빽도</b>: 뒤로 한 칸(온 길을 따라). 출발 전 말은 움직일 수 없고, 1번 칸의 말은 출발 전으로 돌아가요. 움직일 말이 없으면 차례가 넘어가요.<br>
  <b>한 번 더</b>: 윷·모가 나오거나 상대 말을 잡았을 때예요.<br>
  <b>이 앱의 약속</b>: 던진 결과는 <b>바로 사용</b>해요(모아 두지 않아요). 움직일 수 있는 말이 하나뿐이면 자동으로 움직여요.</div></details>`;
'''

CSS = r'''
.yb{width:100%;max-width:360px;margin:0 auto;display:block;touch-action:manipulation}.yb .yl{fill:none;stroke:var(--line);stroke-width:4;stroke-linejoin:round}
.yb .yc{fill:var(--surface);stroke:var(--fg);stroke-width:1.6}.yb .yc.big{fill:color-mix(in srgb,var(--accent) 20%,var(--surface));stroke-width:2.4}.yb .yc.hl{fill:color-mix(in srgb,#2e9d5b 40%,var(--surface));stroke:#2e9d5b;stroke-width:4;cursor:pointer;animation:ypulse .8s infinite alternate}
@keyframes ypulse{to{stroke-width:2}}
.yb .yn{font-size:9px;fill:var(--muted);pointer-events:none;font-family:var(--font-body)}.yb .yn.s{font-size:7.5px}.yb .yt{pointer-events:none}.yb .ytn{font-size:15px;font-weight:800;fill:#fff;pointer-events:none}
.sticks{font-size:2rem;display:flex;justify-content:center;gap:10px;min-height:1.4em}.sticks .sf{color:#c78a3b}.sticks .sr{color:#8a5a22}.sticks .mk{outline:2px dashed #d6453a;outline-offset:2px;border-radius:4px}
.pcsb{display:grid;gap:6px}.pcsb button{text-align:left;line-height:1.35}
.tbl{width:100%;border-collapse:collapse;font-size:.85rem;margin:4px 0}.tbl td{padding:3px 4px;border-bottom:1px solid var(--line)}
details summary{cursor:pointer;font-weight:700}.note{font-size:.85rem;color:var(--muted);line-height:1.6}
@media(prefers-reduced-motion:reduce){.yb .yc.hl{animation:none}}
'''

# ── 혼자 하기(컴퓨터와): 시작 화면 윷놀이
SOLO_BODY = r'''  <div class="stats" style="grid-template-columns:repeat(4,1fr)"><div class="stat"><small>나 도착</small><b id="d1">0/4</b></div><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">나</b></div><div class="stat"><small>컴퓨터</small><b id="d2">0/4</b></div><div class="stat"><small>승리</small><b id="wins">0</b></div></div>
  <div id="brd"></div>
  <div class="card center"><div class="sticks" id="sticks">🥢🥢🥢🥢</div><p class="big" id="res" style="font-size:2rem;min-height:1.3em"></p><p class="muted" id="msg" style="min-height:2.6em">윷을 던져 보세요!</p><p class="note" id="pnl"></p></div>
  <div class="pcsb" id="pick" hidden></div>
  <div class="row"><button class="btn" id="throw" type="button">🥢 윷 던지기</button></div>
  <div class="card res" id="fin" hidden></div>
  <div class="card" id="rules"></div>'''
SOLO_JS = SHARED + r'''
let S, turn, roll, opts, over, busy, wins = ld(KEY) || 0, lastT = null;
const who = w => w ? "컴퓨터" : "나";
function newGame() { S = [Y.newSide(), Y.newSide()]; turn = 0; roll = null; opts = []; over = false; busy = false; lastT = null; $("fin").hidden = true; $("res").textContent = ""; $("msg").textContent = "윷을 던져 보세요!"; render(); }
function render() {
  const hl = roll !== null && turn === 0 ? [...new Set(opts.filter(m => typeof m.to === "number").map(m => m.to))] : [];
  $("brd").innerHTML = yBoard([{ s: S[0], c: YCOL[0] }, { s: S[1], c: YCOL[1] }], hl);
  $("sticks").innerHTML = ySticks(lastT); $("d1").textContent = S[0].done + "/4"; $("d2").textContent = S[1].done + "/4"; $("wins").textContent = wins; $("turn").textContent = over ? "-" : who(turn);
  $("pnl").innerHTML = "🔵 나: " + esc(yPanel(S[0], "").trim()) + "<br>🔴 컴퓨터: " + esc(yPanel(S[1], "").trim());
  const pk = roll !== null && turn === 0 && !over;
  $("pick").hidden = !pk; $("pick").innerHTML = pk ? opts.map((m, k) => `<button class="btn ghost sm" type="button" data-k="${k}">${esc(yOpt(m, S[0]))}</button>`).join("") : "";
  $("throw").disabled = over || busy || turn !== 0 || roll !== null;
}
function say(t) { $("msg").textContent = t; }
function doThrow(w) {
  const t = Y.toss(); lastT = t; roll = t.n; $("res").textContent = t.name + (t.n >= 4 ? "!" : ""); opts = Y.options(S[w], S[1 - w], roll);
  if (!opts.length) { say(`${who(w)}: ${t.name}! 움직일 수 있는 말이 없어서 차례가 넘어가요`); roll = null; turn = 1 - w; render(); if (turn === 1) cpuLater(); return; }
  if (w === 0 && opts.length > 1) { say(`${t.name}! 움직일 말을 골라요 (아래 버튼이나 초록 칸을 눌러요)`); render(); return; }
  resolve(w, w === 0 ? 0 : Y.aiPick(S[w], S[1 - w], roll));
}
function resolve(w, k) {
  const mv = opts[k], text = yOpt(mv, S[w]), res = Y.apply(S[w], S[1 - w], mv, roll); roll = null; opts = [];
  let m = `${who(w)}: ${text}`; if (res.cap) m = `${m} → 상대 말을 잡았어요!`; if (res.fin) m += ` (${res.fin}개 도착)`;
  if (Y.won(S[w])) { over = true; render(); say(m); return win(w); }
  if (res.extra) { m += " · 한 번 더 던져요!"; } else turn = 1 - w;
  say(m); render(); if (turn === 1) cpuLater();
}
function cpuLater() { busy = true; render(); setTimeout(() => { busy = false; if (!over) doThrow(1); }, 900); }
function win(w) {
  if (w === 0) { wins++; sv(KEY, wins); $("wins").textContent = wins; }
  $("fin").innerHTML = `<h2>${w === 0 ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"}</h2><p class="note">${w === 0 ? "말 4개를 먼저 모두 도착시켰어요." : "컴퓨터가 말 4개를 먼저 도착시켰어요. 다시 도전해요!"}</p><button class="btn" id="again" type="button">🥢 한 판 더</button>`; $("fin").hidden = false; $("again").onclick = newGame; render();
}
$("throw").onclick = () => { if (turn !== 0 || over || busy || roll !== null) return; doThrow(0); };
$("pick").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && roll !== null && turn === 0 && !over) resolve(0, +b.dataset.k); });
$("brd").addEventListener("click", e => { const c = e.target.closest("[data-to]"); if (!c || roll === null || turn !== 0 || over) return; const k = opts.findIndex(m => m.to === +c.dataset.to); if (k >= 0) resolve(0, k); });
$("rules").innerHTML = yRules();
newGame();
'''
make("out/yut-nori.html", "윷놀이", "🥢", 38, "yutnori-best-v1",
     "컴퓨터와 <b>일반 규칙 윷놀이</b>를 해요. 말 4개를 먼저 모두 도착시키면 이겨요. 지름길(5번·10번·가운데), 업기, 빽도, 잡기가 모두 있어요. 규칙은 화면 맨 아래에 있어요.",
     SOLO_BODY, SOLO_JS, CSS)

# ── 같이 하기(2명): 방장이 🔵, 들어온 사람이 🔴. 던진 결과는 바로 사용. 방장이 판정해 모두에게 보내요.
duo("net-yut.html", "윷놀이 (같이 하기)", "🪵", 25, "net-yut-v1",
    "일반 규칙 윷놀이예요. 말 4개를 먼저 모두 도착시키면 이겨요. 지름길(5번·10번·가운데), 업기, 빽도, 잡기가 있고 윷·모·잡기는 한 번 더 던져요. 던지고 나면 움직일 말을 골라요(초록 칸을 눌러도 돼요). 규칙은 화면 맨 아래에 있어요.",
    '<p class="center" id="st"></p><div id="brd"></div><div class="center"><div class="sticks" id="sticks">🥢🥢🥢🥢</div><p class="big center" id="res" style="font-size:1.8rem;min-height:1.3em"></p></div><p class="center note" id="pnl"></p><div class="pcsb" id="pick" hidden></div><button class="btn" id="th" type="button" hidden>🥢 윷 던지기</button><div id="rules"></div>',
    SHARED + r'''
function newRound() { return { ph: "play", s: { [P.a]: Y.newSide(), [P.b]: Y.newSide() }, turn: P.first, roll: null, msg: "", tf: null, tn: "" }; }
const mk = id => id === P.a ? "🔵" : "🔴", colOf = id => id === P.a ? YCOL[0] : YCOL[1];
function optsOf(id, r) { return Y.options(P.s[id], P.s[oppOf(id)], r); }
function resolveNet(from, r, k) {
  const o = oppOf(from), ops = optsOf(from, r), mv = ops[k]; if (!mv) return false;
  const text = yOpt(mv, P.s[from]), res = Y.apply(P.s[from], P.s[o], mv, r); P.roll = null;
  P.msg = `${nameOf(from)}: ${text}` + (res.cap ? " → 상대 말을 잡았어요!" : "") + (res.fin ? ` (${res.fin}개 도착)` : "");
  if (Y.won(P.s[from])) finish(from); else if (res.extra) P.msg += " · 한 번 더 던져요!"; else P.turn = o;
  return true;
}
function onAct(from, d) {
  if (P.ph === "end" && d.t === "again") { round(true); pushS(); return; }
  if (P.ph !== "play" || from !== P.turn) return;
  const o = oppOf(from);
  if (d.t === "throw" && P.roll === null) {
    const t = Y.toss(); P.tf = t.flat; P.tn = t.name; const ops = optsOf(from, t.n);
    if (!ops.length) { P.msg = `${nameOf(from)}: ${t.name}! 움직일 수 있는 말이 없어서 차례가 넘어가요`; P.turn = o; }
    else if (ops.length === 1) resolveNet(from, t.n, 0);
    else { P.roll = t.n; P.msg = `${nameOf(from)}: ${t.name}! 움직일 말을 골라요`; }
  } else if (d.t === "move" && P.roll !== null) { if (!resolveNet(from, P.roll, +d.k)) return; }
  else return;
  pushS();
}
function changed(was) {}
function render() {
  if (!P || !P.s) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("brd").innerHTML = ""; $("th").hidden = true; $("pick").hidden = true; $("pnl").textContent = ""; if (!$("rules").firstChild) $("rules").innerHTML = yRules(); if (P) common(); return; }
  const pl = amPlayer(), can = P.ph === "play" && P.turn === me, mine = can && P.roll !== null, ops = mine ? optsOf(me, P.roll) : [];
  $("st").textContent = P.ph === "end" ? endText() : (P.msg ? P.msg + " · " : "") + (!pl ? `구경 중 · ${mk(P.turn)} ${nm(P.turn)} 차례` : can ? (P.roll !== null ? `${Y.NAMES[P.roll]}! 움직일 말을 골라요` : "내 차례! 윷을 던져요") : "상대 차례예요…");
  $("brd").innerHTML = yBoard([{ s: P.s[P.a], c: YCOL[0] }, { s: P.s[P.b], c: YCOL[1] }], [...new Set(ops.filter(m => typeof m.to === "number").map(m => m.to))]);
  $("sticks").innerHTML = ySticks(P.tf ? { flat: P.tf } : null); $("res").textContent = P.tn || "";
  $("pnl").innerHTML = [P.a, P.b].map(id => esc(mk(id) + " " + nm(id) + ": " + yPanel(P.s[id], "").trim())).join("<br>");
  $("th").hidden = !(can && P.roll === null); $("pick").hidden = !mine;
  $("pick").innerHTML = mine ? ops.map((m, k) => `<button class="btn ghost sm" type="button" data-k="${k}">${esc(yOpt(m, P.s[me]))}</button>`).join("") : "";
  if (!$("rules").firstChild) $("rules").innerHTML = yRules(); common();
}
$("th").onclick = () => act({ t: "throw" });
$("pick").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) act({ t: "move", k: +b.dataset.k }); });
$("brd").addEventListener("click", e => { const c = e.target.closest("[data-to]"); if (!c || !P || !P.s || P.turn !== me || P.roll === null) return; const k = optsOf(me, P.roll).findIndex(m => m.to === +c.dataset.to); if (k >= 0) act({ t: "move", k }); });
render();
''', CSS)

# 규칙 엔진(yut-core.js)을 화면 스크립트보다 먼저 읽는다
for fn in ("out/yut-nori.html", "out/net-yut.html"):
    s = open(fn, encoding="utf-8").read(); i = s.index("<script>\n")
    s = s[:i] + '<script src="yut-core.js"></script>\n' + s[i:]; assert "yut-core.js" in s
    open(fn, "w", encoding="utf-8").write(s)
