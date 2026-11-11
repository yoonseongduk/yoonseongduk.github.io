# 맞고(고스톱 2인) 화면 — 규칙은 gostop-core.js, 그림은 gostop-art.js(cards/ 의 공개 그림), 화면은 여기서만 만든다 (결정 D8·D10·D11)
import sys
sys.path.insert(0, ".")
from mkpage import make

CSS = r'''
main{gap:8px}
.note{font-size:.85rem;color:var(--muted)}
.gc{--cw:56px;width:var(--cw);height:calc(var(--cw)*1.64);flex:none;padding:0;border:0;background:transparent;position:relative;border-radius:calc(var(--cw)*.09);font:inherit;color:#1c2233}
.gc img{width:100%;height:100%;display:block;pointer-events:none;-webkit-user-drag:none;filter:drop-shadow(0 1px 1.5px rgba(0,0,0,.4))}
.gc .g{position:absolute;left:1px;top:1px;font-size:max(8px,calc(var(--cw)*.18));font-weight:800;line-height:1.2;padding:0 3px;border-radius:6px;background:rgba(255,255,255,.9);border:1px solid rgba(0,0,0,.3);white-space:nowrap}
.t-gwang .g{background:#ffe27a}.t-yeol .g{background:#ffd2a6}.t-ddi .g{background:#cfe3ff}.d-red .g{background:#ffc9c4}.d-cho .g{background:#ffdcc4}.d-plain .g{background:#e4e4e4}
button.gc{cursor:pointer}button.gc:disabled{cursor:default}
.hand{display:flex;flex-wrap:wrap;gap:8px 6px;justify-content:center;padding-bottom:6px}
.hand .gc.match{outline:3px solid #2e9d5b;outline-offset:1px}.hand .gc.best{outline:3px solid #f0a800;outline-offset:1px}
.hand .gc.match::after,.hand .gc.best::after{position:absolute;left:50%;bottom:-9px;transform:translateX(-50%);font-size:.68rem;font-weight:800;line-height:1.2;padding:0 6px;border-radius:8px;color:#fff;white-space:nowrap}
.hand .gc.match::after{content:"짝";background:#2e9d5b}.hand .gc.best::after{content:"⭐ 추천";background:#d58f00}
.field{display:flex;flex-wrap:wrap;gap:6px 4px;justify-content:center;min-height:76px}.field .gc{--cw:46px}
.field .gc.tgt{outline:2px dashed #2e9d5b;outline-offset:1px}
.field .gc.pick{outline:3px solid var(--accent);outline-offset:1px;animation:glow .8s infinite alternate}
@keyframes glow{to{outline-color:#ff7a1a}}
.cap{display:grid;grid-template-columns:2.1em 1fr 1fr;gap:3px 6px;align-items:start}
.cap .ch{font-weight:700;font-size:.85rem;display:flex;gap:6px;align-items:baseline;flex-wrap:wrap}.cap .ch em{font-style:normal;font-size:.72rem;font-weight:800;color:#ff7a1a}
.cap .cl{font-weight:800;font-size:.85rem;padding-top:6px;color:var(--muted)}
.cap .cc{min-height:26px;display:flex;flex-wrap:wrap;gap:2px;align-content:flex-start;align-items:flex-start;border-left:1px solid var(--line);padding-left:5px}
.cap .cc .n{font-size:.72rem;font-weight:800;color:var(--muted);min-width:1.3em;padding-top:2px}
.cap .pt{font-size:.72rem;color:var(--muted);border-left:1px solid var(--line);padding-left:5px;min-height:1.2em}
.cap .gc{--cw:24px;border-radius:3px}.cap .gc .g{display:none}.cap .gc img{filter:none}
.gc.new{outline:3px solid #ff7a1a;outline-offset:0;z-index:2;animation:pulse .8s ease-in-out 4}
.cap .gc.new{outline-width:2px}
@keyframes pulse{50%{transform:scale(1.35)}}
.pile{display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:50px;padding:6px;border-radius:10px;background:var(--soft);font-size:.8rem}.pile b{font-family:var(--font-display);font-size:1.3rem;font-weight:400}
.board{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:start}
.tight{padding:8px 10px;gap:6px}
.bar{position:sticky;top:0;z-index:20;display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:6px 0;background:var(--bg)}
.bs{border:2px solid var(--line);border-radius:14px;padding:6px 10px;background:var(--surface);display:grid;grid-template-columns:1fr auto;align-items:baseline}.bs.on{border-color:var(--accent)}
.bs .bn{font-weight:700}.bs .bp{font-family:var(--font-display);font-size:1.6rem}.bs .bm{grid-column:1/-1;font-size:.78rem;color:var(--muted)}
.msg{min-height:2.4em;font-weight:700;font-size:.92rem}.acts{display:flex;gap:8px;flex-wrap:wrap}.acts .btn{flex:1}
.hint{display:flex;gap:10px;align-items:center;justify-content:space-between;font-size:.8rem;color:var(--muted)}.hint label{display:flex;gap:4px;align-items:center;cursor:pointer;font-weight:700}
.res h2{margin-bottom:4px}.tbl{width:100%;border-collapse:collapse;font-size:.9rem}.tbl td{padding:3px 2px;border-bottom:1px solid var(--line)}.tbl td:last-child{text-align:right}
details summary{cursor:pointer;font-weight:700}
@media(prefers-reduced-motion:reduce){.gc.new,.field .gc.pick{animation:none}}
'''

BODY = '''  <div class="bar" id="bar"></div>
  <div class="card tight"><div class="cap" id="cap"></div></div>
  <div class="card tight"><div class="board"><div class="field" id="field" aria-label="바닥"></div><div class="pile" id="pile"></div></div></div>
  <div class="msg" id="msg" role="status" aria-live="polite"></div>
  <div class="acts" id="acts"></div>
  <div class="hand" id="hand" aria-label="내 손패"></div>
  <div class="hint"><span>🟢 짝이 맞는 패 · ⭐ 추천 패 · 점선은 바닥의 짝</span><label><input type="checkbox" id="hintOn"> 힌트</label></div>
  <div class="card res" id="result" hidden></div>
  <div class="card"><details><summary>📘 규칙 보기</summary><div class="note" style="margin-top:6px">
    • 손패 1장을 내면 같은 달 패가 바닥에 있을 때 짝으로 가져가요. 이어서 더미에서 한 장 뒤집어 같은 방식으로 해요.<br>
    • <b>쪽</b>(낸 패와 뒤집은 패가 같은 달) · <b>따닥</b> · <b>싹쓸이</b> · <b>뻑 먹기</b>는 상대 피를 1장 가져와요. 3장이 묶이는 <b>뻑</b>은 나중에 누가 4장을 가져가요.<br>
    • 점수: 광 3장 3점(비광 포함 2점)·4장 4점·5장 15점, 고도리 5점, 홍단·청단·초단 각 3점, 열끗·띠 5장부터 1점씩, 피 10장부터 1점씩(쌍피는 2장).<br>
    • 7점 이상이면 <b>고</b>(더 하기) 또는 <b>스톱</b>. 고는 1번 +1점, 2번 +2점, 3번부터 2배씩. 광박·피박이면 2배.<br>
    • 방금 가져온 패는 주황 테두리로 반짝여요. 힌트를 켜면 짝이 맞는 패(초록)와 추천 패(⭐)를 알려 줘요. 포인트는 놀이용이에요. 이기면 점수만큼(최대 50p) 받고, 지면 잃지 않아요.<br>
    • 화투 그림: Louie Mantia·すけじょ, CC BY-SA 4.0 (Wikimedia Commons). 자세한 출처는 licenses.html 에 있어요.</div></details></div>'''

JS = r'''
const GS = window.GoStop, ME = 0, CPU = 1;
const TAG = { gwang: "광", yeol: "열", pi: "피" };
let S = null, lastWinner = -1, lastTurnNo = 0, msg = "", done = false, timer = 0;
let stats = ld(KEY) || { w: 0, l: 0, d: 0, best: 0 };
if (typeof stats.hint !== "boolean") stats.hint = true;
function face(id) { const i = GS.info(id); return { i, tag: i.type === "ddi" ? "띠" : i.pi === 2 ? "쌍피" : TAG[i.type] }; }
const lab = id => { const i = GS.info(id), f = face(id); return i.month + "월 " + (i.type === "gwang" ? "光" : i.type === "ddi" ? ({ red: "홍단", blue: "청단", cho: "초단", plain: "띠" })[i.sub] : f.tag); };
function card(id, o) {
  o = o || {}; const f = face(id), cls = "gc t-" + f.i.type + (f.i.type === "ddi" ? " d-" + f.i.sub : "") + (o.cls ? " " + o.cls : "");
  return `<button type="button" class="${cls}" data-id="${id}" ${o.on ? "" : "disabled"} aria-label="${lab(id)}">${GoStopArt.img(id)}<span class="g">${f.i.month} ${f.tag}</span></button>`;
}
function newSet() { return new Set(S.last ? S.last.got.concat(S.last.steal) : []); }
function capTable() {
  const nw = newSet(), L = S.last, cell = (cap, k) => {
    const ids = cap.filter(id => GS.info(id).type === k).sort((a, b) => a - b), n = k === "pi" ? ids.reduce((s, x) => s + GS.info(x).pi, 0) : ids.length;
    return `<span class="n">${n}</span>` + ids.map(id => card(id, { cls: nw.has(id) ? "new" : "" })).join("");
  };
  const sc = p => GS.score(S.cap[p]).parts.map(x => x.n + " " + x.p + "점").join(" · ") || "&nbsp;";
  const fresh = p => L && L.who === p && (L.got.length + L.steal.length) ? `<em>방금 +${L.got.length + L.steal.length}</em>` : "";
  const fresh2 = p => (L && L.who !== p && L.steal.length) ? `<em>피 -${L.steal.length}</em>` : "";
  let h = `<div></div><div class="ch">🤖 컴퓨터 ${fresh(CPU)}${fresh2(CPU)}</div><div class="ch">🙂 ${esc((window.fgPerson && fgPerson.player()) || "나")} ${fresh(ME)}${fresh2(ME)}</div>`;
  [["光", "gwang"], ["열끗", "yeol"], ["띠", "ddi"], ["피", "pi"]].forEach(r => { h += `<div class="cl">${r[0]}</div><div class="cc">${cell(S.cap[CPU], r[1])}</div><div class="cc">${cell(S.cap[ME], r[1])}</div>`; });
  return h + `<div></div><div class="pt">${sc(CPU)}</div><div class="pt">${sc(ME)}</div>`;
}
function bar() {
  const a = GS.score(S.cap[CPU]).total, b = GS.score(S.cap[ME]).total, on = S.phase !== "end" ? S.turn : -1;
  const nm = (window.fgPerson && fgPerson.player()) || "나";
  return `<div class="bs${on === CPU ? " on" : ""}"><span class="bn">🤖 컴퓨터</span><span class="bp">${a}점</span><span class="bm">손패 ${S.hands[CPU].length}장${S.goCount[CPU] ? " · 고 " + S.goCount[CPU] + "번" : ""}</span></div>` +
    `<div class="bs${on === ME ? " on" : ""}"><span class="bn">🙂 ${esc(nm)}</span><span class="bp">${b}점</span><span class="bm">손패 ${S.hands[ME].length}장${S.goCount[ME] ? " · 고 " + S.goCount[ME] + "번" : ""} · 더미 ${S.deck.length}</span></div>`;
}
function render() {
  const pick = S.phase === "pick" && S.turn === ME ? S.pend.ids : [];
  const my = S.turn === ME && S.phase === "hand", hint = my && stats.hint;
  const mine = S.hands[ME], monthsInHand = new Set(mine.map(GS.month)), best = hint ? GS.aiPlay(S) : -1;
  $("bar").innerHTML = bar();
  $("cap").innerHTML = capTable();
  $("field").innerHTML = S.field.slice().sort((a, b) => a - b).map(id => card(id, { on: pick.includes(id), cls: pick.includes(id) ? "pick" : hint && monthsInHand.has(GS.month(id)) ? "tgt" : "" })).join("");
  $("pile").innerHTML = `<b>${S.deck.length}</b>더미`;
  $("hand").innerHTML = mine.slice().sort((a, b) => a - b).map(id => { const m = hint && S.field.some(x => GS.month(x) === GS.month(id)); return card(id, { on: my, cls: (my ? "can" : "") + (id === best ? " best" : m ? " match" : "") }); }).join("");
  $("msg").textContent = pick.length ? "👆 가져올 패를 골라요 (반짝이는 패)" : msg;
  let a = "";
  if (S.phase === "gostop" && S.turn === ME) a = `<button class="btn" id="bgo" type="button">🔥 고! (지금 ${S.pend.score}점)</button><button class="btn ghost" id="bstop" type="button">✋ 스톱</button>`;
  $("acts").innerHTML = a;
  if ($("bgo")) { $("bgo").onclick = () => step({ t: "go" }); $("bstop").onclick = () => step({ t: "stop" }); }
  $("hintOn").checked = stats.hint;
}
$("hintOn").onchange = e => { stats.hint = e.target.checked; sv(KEY, stats); render(); };
function describe(l) {
  const who = l.who === ME ? "나" : "컴퓨터";
  let t = `${who}: ${lab(l.hand)}를 내고` + (l.flip != null ? ` ${lab(l.flip)}를 뒤집어` : "") + (l.got.length ? ` → ${l.got.map(lab).join(", ")} 가져감` : " → 가져온 패 없음");
  if (l.steal.length) t += ` · 상대 피 ${l.steal.length}장 빼앗음`; if (l.sp.length) t += " ✨" + l.sp.join("·");
  return t;
}
function step(a) {
  clearTimeout(timer);
  const who = S.turn;
  try { GS.act(S, a); } catch (e) { console.error(e); return; }
  if (a.t === "go" || a.t === "stop") msg = (who === ME ? "나" : "컴퓨터") + (a.t === "go" ? ": 고! 🔥" : ": 스톱!");
  if (S.last && S.turnNo !== lastTurnNo) { lastTurnNo = S.turnNo; msg = describe(S.last); }
  render();
  if (S.phase === "end") return finish();
  if (S.turn === CPU) timer = setTimeout(() => step(GS.aiStep(S)), S.phase === "gostop" ? 1100 : 1200);
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
     "컴퓨터와 둘이서 하는 화투 놀이예요. 이기면 점수만큼 포인트를 받고, 져도 잃지 않아요. 화투 그림은 공개된 그림(CC BY-SA 4.0)을 썼어요.", BODY, JS, CSS)
# 규칙 엔진(gostop-core.js)과 그림(gostop-art.js)을 화면 스크립트보다 먼저 읽는다
p = "out/go-stop.html"; s = open(p, encoding="utf-8").read()
s = s.replace("<script>\nconst $ = id", '<script src="gostop-core.js"></script>\n<script src="gostop-art.js"></script>\n<script>\nconst $ = id', 1)
assert "gostop-core.js" in s and "gostop-art.js" in s
open(p, "w", encoding="utf-8").write(s)
