import sys
sys.path.insert(0, ".")
from mkpage import make
from set33 import duo        # set33(→set32→set31→set30)를 불러오면 같이 하기 게임이 모두 다시 만들어져요(윷놀이 net-yut 는 아래에서 새로 덮어써요)

# ───────── 윷놀이(일반 규칙): 시작 화면 yut-nori.html(컴퓨터와 1:1) + 같이 하기 net-yut.html(2명).
#   규칙 엔진은 yut-core.js(순수 함수, 시험 tools/dev/yut_test.js). 말 4개씩, 29칸 말판, 지름길(5·10·가운데), 업기, 빽도, 잡기, 윷·모·잡기는 한 번 더.
#   이 파일이 예전 윷놀이(set14b.py 의 yut-nori, set33.py 의 net-yut: 20칸 원형·말 2개)를 대신해요. 두 쪽 모두 아래 SHARED 를 같이 써요.

SHARED = r'''
const Y = window.YutCore, YCOL = ["#3b6fd6", "#d6453a"];
// 말판 그리기(한지 바탕에 붉은 테두리, 카드 그림과 같은 분위기). sides = [{s: 편 상태, c: 색, nm: 이름}], hl = 도착할 수 있는 칸 목록(눌러서 고르기)
function yBoard(sides, hl) {
  const X = Y.XY, hs = new Set(hl || []);
  const L = (a, b, c) => `<line x1="${X[a][0]}" y1="${X[a][1]}" x2="${X[b][0]}" y2="${X[b][1]}" class="yl${c || ""}"/>`;
  let h = `<defs><radialGradient id="ygB" cx="50%" cy="42%" r="70%"><stop offset="0" stop-color="#FBF3E1"/><stop offset="1" stop-color="#EBD9B0"/></radialGradient></defs>`
    + `<rect x="2" y="2" width="316" height="356" rx="24" fill="#8E1F1F"/><rect x="8" y="8" width="304" height="344" rx="19" fill="url(#ygB)"/><rect x="13" y="13" width="294" height="334" rx="15" fill="none" stroke="#C9A56A" stroke-width="1" stroke-dasharray="2 4"/>`
    + `<polygon points="${[0, 5, 10, 15].map(i => X[i].join(",")).join(" ")}" class="yl"/>` + L(5, 22, " d") + L(22, 15, " d") + L(10, 22, " d") + L(22, 0, " d")
    + `<polygon points="291,150 283,168 299,168" fill="#8E1F1F"/><text x="291" y="184" class="yn s" text-anchor="middle" fill="#8E1F1F">출발</text>`;   // 출발 방향(위쪽으로 올라가요)
  for (let n = 0; n < 29; n++) {
    const big = Y.CORNER[n], r = big ? 18 : 11, on = hs.has(n) ? " hl" : "";
    h += `<circle cx="${X[n][0]}" cy="${X[n][1]}" r="${r}" class="yc${big ? " big" : ""}${n === 0 ? " go" : ""}${on}" data-to="${n}"/>`;
    h += n === 0 ? `<text x="${X[n][0]}" y="${X[n][1] - 2}" class="yn s w" text-anchor="middle">출발</text><text x="${X[n][0]}" y="${X[n][1] + 8}" class="yn s w" text-anchor="middle">도착</text>` : `<text x="${X[n][0]}" y="${X[n][1] + (big ? 4 : 3)}" class="yn${big ? " b" : ""}" text-anchor="middle">${n === 22 ? "중앙" : n}</text>`;
  }
  sides.forEach(sd => sd.s.stacks.forEach(st => { const [x, y] = X[st.at];
    h += `<g class="yt" data-to="${st.at}"><circle cx="${x}" cy="${y}" r="14" fill="${sd.c}" stroke="#fff" stroke-width="2.5"/><circle cx="${x - 4}" cy="${y - 5}" r="5" fill="#fff" opacity=".35"/>${st.n > 1 ? `<text x="${x}" y="${y + 5}" text-anchor="middle" class="ytn">${st.n}</text>` : ""}</g>`; }));
  h += `<line x1="22" y1="296" x2="298" y2="296" stroke="#C9A56A" stroke-width="1.2"/>`;   // 아래 칸: 출발 전 말(대기)과 도착 수
  sides.forEach((sd, i) => { const left = i === 0, w = sd.s.w;
    for (let k = 0; k < 4; k++) { const x = left ? 36 + k * 28 : 284 - k * 28, on = k < w;
      h += `<circle cx="${x}" cy="318" r="11" fill="${on ? sd.c : "none"}" stroke="${on ? "#fff" : sd.c}" stroke-width="${on ? 2.5 : 1.5}" ${on ? "" : 'stroke-dasharray="3 3" opacity=".6"'}/>${on ? `<circle cx="${x - 3}" cy="${y2(318)}" r="4" fill="#fff" opacity=".35"/>` : ""}`; }
    h += `<text x="${left ? 24 : 296}" y="343" class="yn s l" text-anchor="${left ? "start" : "end"}">${esc(sd.nm || "")} · 출발 전 ${w} · 도착 ${sd.s.done}/4</text>`; });
  return `<svg class="yb" viewBox="0 0 320 360" role="img" aria-label="윷놀이 말판">${h}</svg>`;
}
const y2 = v => v - 4;
const yNode = n => n === 0 ? "출발·도착 칸" : n === 22 ? "가운데(22번)" : (n === 5 || n === 10 || n === 15 ? n + "번(모서리)" : n + "번 칸");
const yTo = t => t === Y.END ? "도착! 🏁" : t === 0 ? "출발·도착 칸에 멈춰요 (다음에 움직이면 도착)" : t === Y.HOME ? "출발 전으로 돌아가요" : yNode(t);
function yOpt(m, sd) { // 움직임 하나를 글로: "3번 칸의 말 2개(업은 말) → 8번 칸 · 잡기!"
  const from = m.from < 0 ? "출발 전 말 1개" : yNode(sd.stacks[m.from].at) + "의 말 " + m.n + "개" + (m.n > 1 ? "(업은 말)" : "");
  return from + " → " + yTo(m.to) + (m.cap ? " · 잡기! (" + m.cap + "개)" : "") + (m.stack ? " · 업기" : "");
}
const YIMG = { "-1": "backdo", 1: "do", 2: "gae", 3: "geol", 4: "yut", 5: "mo" };   // 결과 카드 그림: yut-img/yut_*.svg (사용자가 만든 그림)
Object.values(YIMG).forEach(k => { const im = new Image(); im.src = "yut-img/yut_" + k + ".svg"; });   // 던질 때 늦게 뜨지 않게 미리 불러와요
const yCard = n => YIMG[n] ? `<img class="ycard" src="yut-img/yut_${YIMG[n]}.svg" alt="${Y.NAMES[n]}" draggable="false">` : `<img class="yready" src="yut-img/yut_ready.svg" alt="윷가락 네 개" draggable="false">`;
function yPanel(sd, mark) { return `${mark} 출발 전 ${sd.w} · 도착 ${sd.done}/4` + (sd.stacks.length ? " · 판 위 " + sd.stacks.map(s => yNode(s.at) + (s.n > 1 ? " ×" + s.n : "")).join(", ") : ""); }
const yRules = () => `<details open><summary>📘 윷놀이 규칙 (일반 규칙)</summary><div class="note" style="margin-top:6px">
  <b>목표</b>: 내 말 <b>4개</b>를 먼저 모두 한 바퀴 돌려 <b>도착</b>시키면 이겨요.<br>
  <b>윷 던지기</b>: 가락 4개의 평평한 면(▬)이 몇 개인지 봐요.
  <table class="tbl"><tbody><tr><td><img class="yth" src="yut-img/yut_do.svg" alt="도"></td><td>평평한 면 1개</td><td><b>도</b> 1칸</td></tr><tr><td><img class="yth" src="yut-img/yut_gae.svg" alt="개"></td><td>2개</td><td><b>개</b> 2칸</td></tr><tr><td><img class="yth" src="yut-img/yut_geol.svg" alt="걸"></td><td>3개</td><td><b>걸</b> 3칸</td></tr><tr><td><img class="yth" src="yut-img/yut_yut.svg" alt="윷"></td><td>4개</td><td><b>윷</b> 4칸 · 한 번 더</td></tr><tr><td><img class="yth" src="yut-img/yut_mo.svg" alt="모"></td><td>0개(모두 둥글어요)</td><td><b>모</b> 5칸 · 한 번 더</td></tr><tr><td><img class="yth" src="yut-img/yut_backdo.svg" alt="빽도"></td><td>도인데 ✖ 표시 가락이 평평</td><td><b>빽도</b> 뒤로 1칸</td></tr></tbody></table>
  <b>말판</b>: 바깥 길을 반시계 방향으로 출발·도착 칸(0)에서 시작해 한 바퀴 돌아요. 말은 던진 칸 수만큼 움직여요.<br>&nbsp;&nbsp;• <b>출발·도착 칸에 정확히 서면</b> 말은 그 칸에 <b>남아 있어요</b>(상대가 정확히 서면 잡힐 수도 있어요). 다음에 그 말을 움직이면 몇 칸이든 <b>도착</b>이에요.<br>&nbsp;&nbsp;• 그 칸을 <b>넘어가면</b> 바로 도착이에요. (예: 가운데에서 걸=3칸이면 출발·도착 칸에 멈추고, 윷=4칸이면 도착)<br>
  <b>🔀 지름길</b>: 모서리 <b>5번</b>이나 <b>10번</b>에 <b>서 있다가</b> 다음에 움직이면 안쪽 길로 들어가요. 그냥 지나가기만 하면 바깥 길이에요.<br>
  &nbsp;&nbsp;• 5번에서 시작: 20→21→<b>가운데(22)</b>→23→24→15번으로 나와 바깥 길(15 이후)을 이어 가요.<br>
  &nbsp;&nbsp;• 10번에서 시작: 25→26→<b>가운데(22)</b>→27→28→출발·도착 칸 (가장 빨라요)<br>
  &nbsp;&nbsp;• 가운데(22)에 서 있다가 움직이면 27→28→출발·도착 칸 쪽으로 나가요.<br>
  <b>🤝 업기</b>: 내 말이 있는 칸에 내 다른 말이 도착하면 한 덩어리가 돼서 <b>함께 움직여요</b>(숫자로 표시). 이동할 때도, 잡힐 때도 같이예요.<br>
  <b>⚔️ 잡기</b>: 상대 말이 있는 칸에 서면 그 칸의 상대 말을 <b>모두 잡아</b> 출발 전으로 돌려보내요. 잡으면 <b>한 번 더</b> 던져요.<br>
  <b>↩️ 빽도</b>: 뒤로 한 칸(온 길을 따라). 출발 전 말은 움직일 수 없고, 1번 칸의 말은 출발 전으로 돌아가요. 움직일 말이 없으면 차례가 넘어가요.<br>
  <b>한 번 더</b>: 윷·모가 나오거나 상대 말을 잡았을 때예요.<br>
  <b>이 앱의 약속</b>: 던진 결과는 <b>바로 사용</b>해요(모아 두지 않아요). 움직일 수 있는 말이 하나뿐이면 자동으로 움직여요.</div></details>`;
'''

CSS = r'''
.yb{width:100%;max-width:360px;margin:0 auto;display:block;touch-action:manipulation;filter:drop-shadow(0 3px 8px rgba(0,0,0,.28))}
.yb .yl{fill:none;stroke:#C9A56A;stroke-width:8;stroke-linejoin:round;stroke-linecap:round}.yb .yl.d{stroke:#DDC391;stroke-width:5}
.yb .yc{fill:#FFF8E6;stroke:#7A4A1E;stroke-width:2}.yb .yc.big{fill:#F2C14E;stroke:#7A4A1E;stroke-width:3}.yb .yc.go{fill:#C0392B;stroke:#7A1F14}
.yb .yc.hl{fill:#bff0cf;stroke:#1f9d62;stroke-width:4;cursor:pointer;animation:ypulse .8s infinite alternate}
@keyframes ypulse{to{stroke-width:2}}
.yb .yn{font-size:9px;fill:#7A4A1E;pointer-events:none;font-family:var(--font-body)}.yb .yn.b{font-size:11px;font-weight:700}.yb .yn.s{font-size:8px}.yb .yn.w{fill:#fff;font-weight:700}.yb .yn.l{fill:#5b3a1a;font-size:9.5px}
.yb .yt{pointer-events:none}.yb .ytn{font-size:15px;font-weight:800;fill:#fff;pointer-events:none}
.sticks{font-size:2rem;display:flex;justify-content:center;gap:10px;min-height:1.4em}.sticks .sf{color:#c78a3b}.sticks .sr{color:#8a5a22}.sticks .mk{outline:2px dashed #d6453a;outline-offset:2px;border-radius:4px}
.yready{height:130px;width:auto;max-width:100%;filter:drop-shadow(0 4px 6px rgba(0,0,0,.25))}.sticks{min-height:0}.ycard{height:190px;width:auto;max-width:100%;border-radius:14px;box-shadow:0 4px 14px rgba(0,0,0,.35);animation:ythrow .65s cubic-bezier(.2,.9,.3,1.2)}
@keyframes ythrow{0%{transform:translateY(-70px) rotate(-14deg) scale(.55);opacity:0}55%{transform:translateY(8px) rotate(3deg) scale(1.06);opacity:1}100%{transform:none}}
.yth{height:56px;width:auto;border-radius:6px;display:block}
@media(prefers-reduced-motion:reduce){.ycard{animation:none}}
.pcsb{display:grid;gap:6px}.pcsb button{text-align:left;line-height:1.35}
.tbl{width:100%;border-collapse:collapse;font-size:.85rem;margin:4px 0}.tbl td{padding:3px 4px;border-bottom:1px solid var(--line)}
details summary{cursor:pointer;font-weight:700}.note{font-size:.85rem;color:var(--muted);line-height:1.6}
@media(prefers-reduced-motion:reduce){.yb .yc.hl{animation:none}}
'''

# ── 혼자 하기(컴퓨터와): 시작 화면 윷놀이
SOLO_BODY = r'''  <div class="stats" style="grid-template-columns:repeat(4,1fr)"><div class="stat"><small>나 도착</small><b id="d1">0/4</b></div><div class="stat"><small>차례</small><b id="turn" style="font-size:1.1rem">나</b></div><div class="stat"><small>컴퓨터</small><b id="d2">0/4</b></div><div class="stat"><small>승리</small><b id="wins">0</b></div></div>
  <div id="brd"></div>
  <div class="card center"><div class="sticks" id="sticks"><img class="yready" src="yut-img/yut_ready.svg" alt="윷가락 네 개" draggable="false"></div><p class="big" id="res" style="font-size:2rem;min-height:1.3em"></p><p class="muted" id="msg" style="min-height:2.6em">윷을 던져 보세요!</p><p class="note" id="pnl"></p></div>
  <div class="pcsb" id="pick" hidden></div>
  <div class="row"><button class="btn" id="throw" type="button">윷 던지기</button></div>
  <div class="card res" id="fin" hidden></div>
  <div class="card" id="rules"></div>'''
SOLO_JS = SHARED + r'''
let S, turn, roll, opts, over, busy, wins = ld(KEY) || 0, lastT = null;
const who = w => w ? "컴퓨터" : "나";
function newGame() { S = [Y.newSide(), Y.newSide()]; turn = 0; roll = null; opts = []; over = false; busy = false; lastT = null; $("sticks").innerHTML = yCard(0); $("fin").hidden = true; $("res").textContent = ""; $("msg").textContent = "윷을 던져 보세요!"; render(); }
function render() {
  const hl = roll !== null && turn === 0 ? [...new Set(opts.filter(m => typeof m.to === "number").map(m => m.to))] : [];
  $("brd").innerHTML = yBoard([{ s: S[0], c: YCOL[0], nm: "나" }, { s: S[1], c: YCOL[1], nm: "컴퓨터" }], hl);
  $("d1").textContent = S[0].done + "/4"; $("d2").textContent = S[1].done + "/4"; $("wins").textContent = wins; $("turn").textContent = over ? "-" : who(turn);
  $("pnl").innerHTML = "🔵 나: " + esc(yPanel(S[0], "").trim()) + "<br>🔴 컴퓨터: " + esc(yPanel(S[1], "").trim());
  const pk = roll !== null && turn === 0 && !over;
  $("pick").hidden = !pk; $("pick").innerHTML = pk ? opts.map((m, k) => `<button class="btn ghost sm" type="button" data-k="${k}">${esc(yOpt(m, S[0]))}</button>`).join("") : "";
  $("throw").disabled = over || busy || turn !== 0 || roll !== null;
}
function say(t) { $("msg").textContent = t; }
function doThrow(w) {
  const t = Y.toss(); lastT = t; roll = t.n; $("sticks").innerHTML = yCard(t.n); $("res").textContent = t.name + (t.n >= 4 ? "!" : ""); opts = Y.options(S[w], S[1 - w], roll);
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
  $("fin").innerHTML = `<h2>${w === 0 ? "🎉 내가 이겼어요!" : "😢 컴퓨터가 이겼어요"}</h2><p class="note">${w === 0 ? "말 4개를 먼저 모두 도착시켰어요." : "컴퓨터가 말 4개를 먼저 도착시켰어요. 다시 도전해요!"}</p><button class="btn" id="again" type="button">🔁 한 판 더</button>`; $("fin").hidden = false; $("again").onclick = newGame; render();
}
$("throw").onclick = () => { if (turn !== 0 || over || busy || roll !== null) return; doThrow(0); };
$("pick").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && roll !== null && turn === 0 && !over) resolve(0, +b.dataset.k); });
$("brd").addEventListener("click", e => { const c = e.target.closest("[data-to]"); if (!c || roll === null || turn !== 0 || over) return; const k = opts.findIndex(m => m.to === +c.dataset.to); if (k >= 0) resolve(0, k); });
$("rules").innerHTML = yRules();
newGame();
'''
make("out/yut-nori.html", "윷놀이", '<img src="yut-img/yut_icon.svg" alt="" style="height:1.1em;vertical-align:-.15em;border-radius:4px">', 38, "yutnori-best-v1",
     "컴퓨터와 <b>일반 규칙 윷놀이</b>를 해요. 말 4개를 먼저 모두 도착시키면 이겨요. 지름길(5번·10번·가운데), 업기, 빽도, 잡기가 모두 있어요. 규칙은 화면 맨 아래에 있어요.",
     SOLO_BODY, SOLO_JS, CSS)

# ── 같이 하기(2명): 방장이 🔵, 들어온 사람이 🔴. 던진 결과는 바로 사용. 방장이 판정해 모두에게 보내요.
duo("net-yut.html", "윷놀이 (같이 하기)", '<img src="yut-img/yut_icon.svg" alt="" style="height:1.1em;vertical-align:-.15em;border-radius:4px">', 25, "net-yut-v1",
    "일반 규칙 윷놀이예요. 말 4개를 먼저 모두 도착시키면 이겨요. 지름길(5번·10번·가운데), 업기, 빽도, 잡기가 있고 윷·모·잡기는 한 번 더 던져요. 던지고 나면 움직일 말을 골라요(초록 칸을 눌러도 돼요). 규칙은 화면 맨 아래에 있어요.",
    '<p class="center" id="st"></p><div id="brd"></div><div class="center"><div class="sticks" id="sticks"><img class="yready" src="yut-img/yut_ready.svg" alt="윷가락 네 개" draggable="false"></div><p class="big center" id="res" style="font-size:1.8rem;min-height:1.3em"></p></div><p class="center note" id="pnl"></p><div class="pcsb" id="pick" hidden></div><button class="btn" id="th" type="button" hidden>윷 던지기</button><div id="rules"></div>',
    SHARED + r'''
function newRound() { return { ph: "play", s: { [P.a]: Y.newSide(), [P.b]: Y.newSide() }, turn: P.first, roll: null, msg: "", tf: null, tn: "", tr: 0, tk: 0 }; }
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
    const t = Y.toss(); P.tf = t.flat; P.tn = t.name; P.tr = t.n; P.tk = (P.tk || 0) + 1; const ops = optsOf(from, t.n);
    if (!ops.length) { P.msg = `${nameOf(from)}: ${t.name}! 움직일 수 있는 말이 없어서 차례가 넘어가요`; P.turn = o; }
    else if (ops.length === 1) resolveNet(from, t.n, 0);
    else { P.roll = t.n; P.msg = `${nameOf(from)}: ${t.name}! 움직일 말을 골라요`; }
  } else if (d.t === "move" && P.roll !== null) { if (!resolveNet(from, P.roll, +d.k)) return; }
  else return;
  pushS();
}
function changed(was) {}
let shownK = -1;
function render() {
  if (!P || !P.s) { $("st").textContent = !P ? "연결을 기다리는 중…" : "상대가 들어오면 시작해요"; $("brd").innerHTML = ""; $("th").hidden = true; $("pick").hidden = true; $("pnl").textContent = ""; if (!$("rules").firstChild) $("rules").innerHTML = yRules(); if (P) common(); return; }
  const pl = amPlayer(), can = P.ph === "play" && P.turn === me, mine = can && P.roll !== null, ops = mine ? optsOf(me, P.roll) : [];
  $("st").textContent = P.ph === "end" ? endText() : (P.msg ? P.msg + " · " : "") + (!pl ? `구경 중 · ${mk(P.turn)} ${nm(P.turn)} 차례` : can ? (P.roll !== null ? `${Y.NAMES[P.roll]}! 움직일 말을 골라요` : "내 차례! 윷을 던져요") : "상대 차례예요…");
  $("brd").innerHTML = yBoard([{ s: P.s[P.a], c: YCOL[0], nm: nm(P.a) }, { s: P.s[P.b], c: YCOL[1], nm: nm(P.b) }], [...new Set(ops.filter(m => typeof m.to === "number").map(m => m.to))]);
  if (!P.tr) { $("sticks").innerHTML = yCard(0); shownK = -1; } else if (shownK !== P.tk) { $("sticks").innerHTML = yCard(P.tr); shownK = P.tk; }   // 새로 던졌을 때만 다시 그려서 튀어나오는 동작이 한 번만 보이게
  $("res").textContent = P.tn || "";
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
