# 맞고(고스톱 2인) 화면 — 규칙은 gostop-core.js, 화면은 여기서만 만든다 (결정 D8)
import sys
sys.path.insert(0, ".")
from mkpage import make

CSS = r'''
.note{font-size:.85rem;color:var(--muted)}
.gc{--cw:56px;width:var(--cw);height:calc(var(--cw)*1.4);flex:none;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:2px 1px;border-radius:8px;border:1.5px solid #b9b2a4;background:#fffdf6;color:#1c2233;font:inherit;line-height:1.1;position:relative}
.gc .m{align-self:flex-start;font-weight:800;font-size:calc(var(--cw)*.22);padding-left:3px}
.gc .e{font-size:calc(var(--cw)*.46);line-height:1}
.gc .g{font-size:calc(var(--cw)*.2);font-weight:700;white-space:nowrap}
.t-gwang{background:#fff1b8;border-color:#c59a1c}.t-yeol{background:#ffe9d6;border-color:#d58a4b}.t-pi{background:#eef0f2;border-color:#aab1ba}
.t-ddi{background:#fff;border-color:#888}.d-red{background:#ffd9d6;border-color:#d6453a}.d-blue{background:#d8e6ff;border-color:#3b6fd6}.d-cho{background:#d9f3dc;border-color:#2f9a4a}.d-plain{background:#eee}
button.gc{cursor:pointer}button.gc:disabled{cursor:default}
.hand .gc.can{box-shadow:0 0 0 2px var(--accent)}.field .gc.pick{box-shadow:0 0 0 3px var(--accent);animation:glow .8s infinite alternate}
@keyframes glow{to{box-shadow:0 0 0 5px var(--accent)}}
.hand{display:flex;flex-wrap:wrap;gap:6px;justify-content:center}
.field{display:flex;flex-wrap:wrap;gap:4px;justify-content:center;min-height:68px}.field .gc{--cw:44px}
.mini{display:flex;flex-wrap:wrap;gap:2px;align-items:center}.mini .gc{--cw:24px;border-width:1px;border-radius:4px;padding:0}.mini .gc .m,.mini .gc .g{display:none}.mini .gc .e{font-size:.8rem}
.grp{display:flex;gap:6px;align-items:center;min-height:28px;font-size:.75rem;color:var(--muted)}.grp b{min-width:2.6em;color:var(--fg)}
.pile{display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:52px;padding:6px;border-radius:10px;background:var(--soft);font-size:.8rem}.pile b{font-family:var(--font-display);font-size:1.3rem;font-weight:400}
.board{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:start}
.who{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.who .sc{font-family:var(--font-display);font-size:1.3rem}
.msg{min-height:2.6em;font-weight:700}.acts{display:flex;gap:8px;flex-wrap:wrap}.acts .btn{flex:1}.parts{font-size:.8rem;color:var(--muted)}
.res h2{margin-bottom:4px}.tbl{width:100%;border-collapse:collapse;font-size:.9rem}.tbl td{padding:3px 2px;border-bottom:1px solid var(--line)}.tbl td:last-child{text-align:right}
details summary{cursor:pointer;font-weight:700}
'''

BODY = '''  <div class="card" id="opp"></div>
  <div class="card"><div class="board"><div class="field" id="field" aria-label="바닥"></div><div class="pile" id="pile"></div></div></div>
  <div class="card" id="me"></div>
  <div class="msg" id="msg" role="status" aria-live="polite"></div>
  <div class="acts" id="acts"></div>
  <div class="hand" id="hand" aria-label="내 손패"></div>
  <div class="card res" id="result" hidden></div>
  <div class="card"><details><summary>📘 규칙 보기</summary><div class="note" style="margin-top:6px">
    • 손패 1장을 내면 같은 달 패가 바닥에 있을 때 짝으로 가져가요. 이어서 더미에서 한 장 뒤집어 같은 방식으로 해요.<br>
    • <b>쪽</b>(낸 패와 뒤집은 패가 같은 달) · <b>따닥</b> · <b>싹쓸이</b> · <b>뻑 먹기</b>는 상대 피를 1장 가져와요. 3장이 묶이는 <b>뻑</b>은 나중에 누가 4장을 가져가요.<br>
    • 점수: 광 3장 3점(비광 포함 2점)·4장 4점·5장 15점, 고도리 5점, 홍단·청단·초단 각 3점, 열끗·띠 5장부터 1점씩, 피 10장부터 1점씩(쌍피는 2장).<br>
    • 7점 이상이면 <b>고</b>(더 하기) 또는 <b>스톱</b>. 고는 1번 +1점, 2번 +2점, 3번부터 2배씩. 광박·피박이면 2배.<br>
    • 포인트는 놀이용이에요. 이기면 점수만큼(최대 50p) 받고, 지면 잃지 않아요.</div></details></div>'''

JS = r'''
const GS = window.GoStop, ME = 0, CPU = 1;
const EM = ["", "🌲", "🌼", "🌸", "🪻", "🌷", "🌺", "🍃", "🌾", "🏵️", "🍁", "🍂", "☔"];
const AN = { bird: "🐦", bridge: "🌉", butterfly: "🦋", boar: "🐗", goose: "🦆", cup: "🍶", deer: "🦌", swallow: "🕊️" };
const DDI = { red: "홍단", blue: "청단", cho: "초단", plain: "띠" };
let S = null, lastWinner = -1, lastTurnNo = 0, msg = "", done = false, timer = 0;
let stats = ld(KEY) || { w: 0, l: 0, d: 0, best: 0 };
function face(id) { const i = GS.info(id); return { i, mid: i.type === "yeol" ? AN[i.sub] : EM[i.month], tag: i.type === "gwang" ? "光" : i.type === "yeol" ? "열끗" : i.type === "ddi" ? DDI[i.sub] : i.pi === 2 ? "쌍피" : "피" }; }
function card(id, o) {
  o = o || {}; const f = face(id), cls = "gc t-" + f.i.type + (f.i.type === "ddi" ? " d-" + f.i.sub : "") + (o.cls ? " " + o.cls : "");
  return `<button type="button" class="${cls}" data-id="${id}" ${o.on ? "" : "disabled"} aria-label="${f.i.month}월 ${f.tag}"><span class="m">${f.i.month}</span><span class="e">${f.mid}</span><span class="g">${f.tag}</span></button>`;
}
function groups(cap) {
  const by = { gwang: [], yeol: [], ddi: [], pi: [] }; cap.forEach(id => by[GS.info(id).type].push(id));
  const row = (n, k) => `<div class="grp"><b>${n} ${k === "pi" ? by.pi.reduce((s, x) => s + GS.info(x).pi, 0) : by[k].length}</b><div class="mini">${by[k].sort((a, b) => a - b).map(id => card(id)).join("")}</div></div>`;
  return row("光", "gwang") + row("열끗", "yeol") + row("띠", "ddi") + row("피", "pi");
}
function side(p, title) {
  const sc = GS.score(S.cap[p]), g = S.goCount[p];
  return `<div class="who"><b>${title}</b><span class="note">${p === CPU ? "손패 " + S.hands[CPU].length + "장 · " : ""}${g ? "고 " + g + "번 · " : ""}<span class="sc">${sc.total}점</span></span></div>${groups(S.cap[p])}<div class="parts">${sc.parts.map(x => x.n + " " + x.p + "점").join(" · ") || "&nbsp;"}</div>`;
}
function render() {
  const pick = S.phase === "pick" && S.turn === ME ? S.pend.ids : [];
  $("opp").innerHTML = side(CPU, "🤖 컴퓨터");
  $("me").innerHTML = side(ME, "🙂 " + (window.fgPerson && fgPerson.player() || "나"));
  $("field").innerHTML = S.field.slice().sort((a, b) => a - b).map(id => card(id, { on: pick.includes(id), cls: pick.includes(id) ? "pick" : "" })).join("");
  $("pile").innerHTML = `<b>${S.deck.length}</b>더미`;
  const my = S.turn === ME && S.phase === "hand";
  $("hand").innerHTML = S.hands[ME].slice().sort((a, b) => a - b).map(id => card(id, { on: my, cls: my ? "can" : "" })).join("");
  $("msg").textContent = pick.length ? "👆 가져올 패를 골라요 (반짝이는 패)" : msg;
  let a = "";
  if (S.phase === "gostop" && S.turn === ME) a = `<button class="btn" id="bgo" type="button">🔥 고! (지금 ${S.pend.score}점)</button><button class="btn ghost" id="bstop" type="button">✋ 스톱</button>`;
  $("acts").innerHTML = a;
  if ($("bgo")) { $("bgo").onclick = () => step({ t: "go" }); $("bstop").onclick = () => step({ t: "stop" }); }
}
function describe(l) {
  const who = l.who === ME ? "나" : "컴퓨터", t = [];
  t.push(`${who}: ${GS.info(l.hand).month}월 패`); if (l.flip != null) t[0] += `, 뒤집은 패 ${GS.info(l.flip).month}월`;
  if (l.sp.length) t.push("✨ " + l.sp.join("·") + "!"); if (l.steal.length) t.push("상대 피 " + l.steal.length + "장 가져옴");
  if (!l.got.length && !l.sp.length) t.push("가져온 패 없음");
  return t.join(" — ");
}
function step(a) {
  clearTimeout(timer);
  const who = S.turn;
  try { GS.act(S, a); } catch (e) { console.error(e); return; }
  if (a.t === "go" || a.t === "stop") msg = (who === ME ? "나" : "컴퓨터") + (a.t === "go" ? ": 고! 🔥" : ": 스톱!");
  if (S.last && S.turnNo !== lastTurnNo) { lastTurnNo = S.turnNo; msg = describe(S.last); }
  render();
  if (S.phase === "end") return finish();
  if (S.turn === CPU) timer = setTimeout(() => step(GS.aiStep(S)), S.phase === "gostop" ? 1100 : 950);
}
$("hand").addEventListener("click", e => { const b = e.target.closest("button.gc"); if (!b || b.disabled || !S || S.phase !== "hand" || S.turn !== ME) return; step({ t: "play", id: +b.dataset.id }); });
$("field").addEventListener("click", e => { const b = e.target.closest("button.gc"); if (!b || b.disabled || !S || S.phase !== "pick" || S.turn !== ME) return; step({ t: "pick", id: +b.dataset.id }); });
function finish() {
  const r = S.result; if (done) return; done = true; let html, add = 0;
  if (r.draw) { stats.d++; html = `<h2>🤝 나가리</h2><div class="note">아무도 7점을 못 냈어요. 다시 해 봐요!</div>`; lastWinner = -1; }
  else if (r.winner === ME) {
    stats.w++; add = Math.min(r.points, 50); stats.best = Math.max(stats.best, r.points); lastWinner = ME;
    if (window.fgPerson && fgPerson.grant) fgPerson.grant(r.points, "맞고 승리");
    html = `<h2>🏆 승리!</h2>`;
  } else { stats.l++; lastWinner = CPU; html = `<h2>😢 아쉬워요</h2><div class="note">컴퓨터가 스톱했어요. 졌을 때는 포인트를 잃지 않아요.</div>`; }
  if (!r.draw) html += `<table class="tbl"><tbody>${r.parts.map(x => `<tr><td>${x.n}</td><td>${x.p}점</td></tr>`).join("")}${r.go ? `<tr><td>고 ${r.go}번</td><td>${r.go >= 3 ? "×" + Math.pow(2, r.go - 2) : "+" + r.go + "점"}</td></tr>` : ""}${r.mult.filter(x => !/^고/.test(x)).map(x => `<tr><td>${x}</td><td>×2</td></tr>`).join("")}<tr><td><b>합계</b></td><td><b>${r.points}점</b></td></tr></tbody></table>${r.winner === ME ? `<div class="ok" style="margin-top:6px">⭐ 포인트 +${add}p (최대 50p)</div>` : ""}`;
  html += `<div class="acts" style="margin-top:8px"><button class="btn" id="again" type="button">🎴 한 판 더</button></div><div class="note">전적: ${stats.w}승 ${stats.l}패 ${stats.d}나가리 · 최고 ${stats.best}점</div>`;
  sv(KEY, stats); $("result").innerHTML = html; $("result").hidden = false; $("again").onclick = start; $("result").scrollIntoView({ behavior: "smooth", block: "nearest" });
}
function start() {
  clearTimeout(timer); done = false; $("result").hidden = true; msg = "패를 나눴어요. 내 차례부터!"; lastTurnNo = 0;
  S = GS.newGame((Math.random() * 2147483647) | 0, lastWinner === CPU ? 1 : 0);
  if (S.turn === CPU) msg = "컴퓨터가 먼저 시작해요.";
  render(); if (S.turn === CPU) timer = setTimeout(() => step(GS.aiStep(S)), 900);
}
start();
'''

make("out/go-stop.html", "맞고 (고스톱)", "🎴", 12, "go-stop-stats-v1",
     "컴퓨터와 둘이서 하는 화투 놀이예요. 이기면 점수만큼 포인트를 받고, 져도 잃지 않아요. 화투 그림은 직접 그린 것이에요.", BODY, JS, CSS)
# 규칙 엔진(gostop-core.js)을 화면 스크립트보다 먼저 읽는다
p = "out/go-stop.html"; s = open(p, encoding="utf-8").read()
s = s.replace("<script>\nconst $ = id", '<script src="gostop-core.js"></script>\n<script>\nconst $ = id', 1)
assert "gostop-core.js" in s
open(p, "w", encoding="utf-8").write(s)
