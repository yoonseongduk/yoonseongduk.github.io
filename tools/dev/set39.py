import sys, re
sys.path.insert(0, ".")
from set34 import party, CARD_JS, CARD_CSS   # set34(→set33→set32→set31→set30)를 불러오면 앞의 같이 하기 게임도 모두 다시 만들어져요

# ───────── 같이 하기 게임 6차: 맞고·고스톱(화투) 2~3명. 목록은 set30.py 의 GAMES(묶음 "card").
#   규칙 엔진은 시작 화면 맞고와 같은 gostop-core.js(순수 함수)이고, 방장만 전체 판(손패·더미)을 들고 있어요.
#   모두에게 보내는 공개 상태 P.v = 바닥·가져온 패·더미 장수·점수·단계(손패는 빼요). 각자에게는 privTo 로 내 손패만 보내요(CARD_JS 의 H.hands).
#   P.ord = 자리 순서(참가자 id), 엔진의 자리 번호 p = P.ord 의 위치. 사람끼리만 하고 컴퓨터는 없어요(컴퓨터와 하려면 시작 화면의 맞고).
#   화면 CSS 는 시작 화면 맞고(set36.py)의 CSS 를 그대로 가져와요(.pile 만 .gpile 로 바꿔 카드 게임 공통 CSS 와 겹치지 않게).

_src = open("set36.py", encoding="utf-8").read()
_i = _src.index("CSS = r'''") + len("CSS = r'''"); GCSS = _src[_i:_src.index("'''", _i)]
GCSS = GCSS.replace("main{gap:8px}\n", "").replace(".pile{", ".gpile{").replace(".pile b{", ".gpile b{")
assert ".gpile" in GCSS and ".gc{" in GCSS

BODY = '<p class="center" id="st"></p><div class="bar" id="bar"></div><div id="tbl"></div><div class="hand" id="hand"></div><div class="acts" id="acts"></div><button class="btn" id="go" type="button" hidden>▶ 시작하기</button>'

JS = r'''
const GS = window.GoStop, GTAG = { gwang: "광", yeol: "열", pi: "피" };
try { const st0 = JSON.parse(localStorage.getItem("go-stop-stats-v1")), a0 = st0 && st0.artSet && (st0.art === "gemini" || st0.art === "minhwa") ? st0.art : "old"; GoStopArt.mode(a0); document.body.classList.toggle("art-gm", a0 === "gemini"); } catch (e) { GoStopArt.mode("old"); }
let SS = null; // 엔진의 전체 판(방장만 가짐)
function initState() { return { ph: "wait", rno: 0, ord: [], cnt: {}, turn: null, msg: "", tot: {}, v: null }; }
const seatOf = id => P.ord.indexOf(id), sname = p => nmOf(P.ord[p]);
function gface(id) { const i = GS.info(id); return { i, tag: i.type === "ddi" ? "띠" : i.pi === 2 ? "쌍피" : GTAG[i.type] }; }
const glab = id => { const i = GS.info(id), f = gface(id); return i.month + "월 " + (i.type === "gwang" ? "光" : i.type === "ddi" ? ({ red: "홍단", blue: "청단", cho: "초단", plain: "띠" })[i.sub] : f.tag); };
function gcard(id, o) { o = o || {}; const f = gface(id), cls = "gc t-" + f.i.type + (f.i.type === "ddi" ? " d-" + f.i.sub : "") + (o.cls ? " " + o.cls : ""); return `<button type="button" class="${cls}" data-id="${id}" ${o.on ? "" : "disabled"} aria-label="${glab(id)}">${GoStopArt.img(id)}<span class="g">${f.i.month} ${f.tag}</span></button>`; }

// ── 방장: 판 진행
function viewOf() { const S = SS; return { field: S.field.slice(), cap: S.cap.map(c => c.slice()), dn: S.deck.length, phase: S.phase, pend: S.pend ? JSON.parse(JSON.stringify(S.pend)) : null, turn: S.turn, go: S.goCount.slice(), shake: S.shake.slice(), bomb: S.bomb.slice(), btok: S.btok.slice(), gk: S.gukjin.slice(), last: S.last || null, hn: S.hands.map(h => h.length), sc: S.hands.map((_, p) => GS.scoreOf(S, p).total), thr: GS.threshold(S), res: S.phase === "end" ? S.result : null }; }
function refresh() { H.hands = {}; P.ord.forEach((id, p) => H.hands[id] = SS.hands[p].slice()); P.v = viewOf(); P.turn = SS.phase === "end" ? null : P.ord[SS.turn]; }
function describe(l) {
  const who = sname(l.who), bomb = l.sp.includes("폭탄");
  let t = l.hand === null ? `${who}: 패를 내지 않고 더미만 뒤집어` : bomb ? `${who}: 💣 ${GS.month(l.hand)}월 패 3장을 한꺼번에 내고` : `${who}: ${glab(l.hand)}를 내고`;
  t += (l.flip != null ? ` ${glab(l.flip)}를 뒤집어` : "") + (l.got.length ? ` → ${l.got.map(glab).join(", ")} 가져감` : " → 가져온 패 없음");
  if (l.steal.length) t += ` · 상대 피 ${l.steal.length}장 빼앗음`; if (l.sp.length) t += " ✨" + l.sp.join("·");
  return t;
}
function mkAct(d) {
  switch (d.t) {
    case "play": case "pick": return { t: d.t, id: +d.id };
    case "shake": case "bomb": return { t: d.t, yes: !!d.yes };
    case "gukjin": return { t: "gukjin", as: d.as === "pi" ? "pi" : "yeol" };
    case "go": case "stop": case "flip": return { t: d.t };
  }
  return null;
}
function finishGame() {
  const r = SS.result; P.ph = "end";
  if (r.draw) { P.msg = "🤝 나가리! 아무도 " + P.v.thr + "점을 못 냈어요"; return; }
  const w = P.ord[r.winner]; P.tot[w] = (P.tot[w] || 0) + r.points; r.per.forEach(x => { const id = P.ord[x.who]; P.tot[id] = (P.tot[id] || 0) - x.pay; });
  P.msg = "🏆 " + sname(r.winner) + " 승리! " + r.points + "점";
}
function onAct(from, d) {
  if (d.t === "start" && from === "host" && P.ph !== "play") {
    const ps = canStart(2, 3); if (!ps) return; const first = P.rno % ps.length;
    SS = GS.newGame((Math.random() * 2147483647) | 0, ps.length === 3 ? first : (first ? 1 : 0), ps.length); H.ltn = 0;
    Object.assign(P, { ph: "play", rno: P.rno + 1, ord: ps }); refresh(); P.msg = "패를 나눴어요. " + sname(SS.turn) + "부터 시작해요.";
  } else if (P.ph === "play" && SS && from === P.ord[SS.turn]) {
    const a = mkAct(d); if (!a) return; const who = SS.turn, before = SS.cap.map(c => c.slice());
    try { GS.act(SS, a); } catch (e) { return; }
    if (SS.last && SS.turnNo !== H.ltn) { SS.last.stealFrom = {}; SS.cap.forEach((c, p) => { const lost = before[p].filter(id => !c.includes(id) && SS.last.steal.includes(id)).length; if (lost) SS.last.stealFrom[p] = lost; }); H.ltn = SS.turnNo; P.msg = describe(SS.last) + (a.t === "gukjin" ? " · 9월 열끗을 " + (a.as === "pi" ? "쌍피" : "열끗") + "으로 써요" : ""); }
    if (a.t === "go" || a.t === "stop") P.msg = sname(who) + (a.t === "go" ? ": 고! 🔥" : ": 스톱!");
    refresh(); if (SS.phase === "end") finishGame();
  } else return;
  sync(); pushS();
}

// ── 화면(모두)
function capTable(V, order, myS) {
  const L = V.last, nw = new Set(L ? L.got.concat(L.steal) : []), n = V.hn.length;
  const cell = (p, k) => { const gp = id => id === GS.RULES.gukjin && V.gk[p] === "pi"; const ids = V.cap[p].filter(id => (gp(id) ? "pi" : GS.info(id).type) === k).sort((a, b) => a - b); let c = ids.length; if (k === "pi") c = ids.reduce((s, x) => s + (gp(x) ? 2 : GS.info(x).pi), 0); return `<span class="n">${c}</span>` + ids.map(id => gcard(id, { cls: nw.has(id) ? "new" : "" })).join(""); };
  const mulOf = p => Math.pow(GS.RULES.shakeMult, V.shake[p] || 0) * Math.pow(GS.RULES.bombMult, V.bomb[p] || 0);
  const sc = p => { const t = GS.score(V.cap[p], V.gk[p]), m = mulOf(p); return (t.parts.map(x => x.n + " " + x.p + "점").join(" · ") + (m > 1 && t.total ? " · ×" + m + " = " + t.total * m + "점" : "")) || "&nbsp;"; };
  const fresh = p => L && L.who === p && (L.got.length + L.steal.length) ? `<em>방금 +${L.got.length + L.steal.length}</em>` : "", fresh2 = p => L && L.stealFrom && L.stealFrom[p] ? `<em>피 -${L.stealFrom[p]}</em>` : "";
  let h = `<div></div>` + order.map(p => `<div class="ch">${p === myS ? "🙂" : "👤"} ${esc(sname(p))} ${fresh(p)}${fresh2(p)}</div>`).join("");
  [["光", "gwang"], ["열끗", "yeol"], ["띠", "ddi"], ["피", "pi"]].forEach(r => { h += `<div class="cl">${r[0]}</div>` + order.map(p => `<div class="cc">${cell(p, r[1])}</div>`).join(""); });
  return `<div class="card tight"><div class="cap" style="grid-template-columns:2.1em repeat(${n},minmax(0,1fr))">${h}<div></div>${order.map(p => `<div class="pt">${sc(p)}</div>`).join("")}</div></div>`;
}
function barHtml(V, order, myS) {
  return order.map(p => { const mm = Math.pow(GS.RULES.shakeMult, V.shake[p] || 0) * Math.pow(GS.RULES.bombMult, V.bomb[p] || 0), tt = V.sc[p];
    const sp = (mm > 1 && tt ? " · ×" + mm + "=" + tt * mm + "점" : "") + (V.shake[p] ? " · 🎲×" + V.shake[p] : "") + (V.bomb[p] ? " · 💣×" + V.bomb[p] : "");
    return `<div class="bs${P.ph === "play" && V.turn === p ? " on" : ""}"><span class="bn">${p === myS ? "🙂" : "👤"} ${esc(sname(p))}</span><span class="bp">${tt}점</span><span class="bm">손패 ${V.hn[p]}장${V.go[p] ? " · 고 " + V.go[p] + "번" : ""}${sp}</span></div>`; }).join("");
}
function guideText(V, myS, mine) {
  const w = sname(V.turn);
  if (P.ph === "end") return "🏁 한 판이 끝났어요. 방장이 「새 판 시작」을 눌러요";
  if (!mine) return V.phase === "gostop" ? `⏳ ${w}: 고·스톱을 정하는 중이에요` : V.phase === "pick" ? `⏳ ${w}: 가져갈 패를 고르는 중이에요` : (V.phase === "shake" || V.phase === "bomb" || V.phase === "gukjin") ? `⏳ ${w}: 선택하는 중이에요` : `⏳ ${w} 차례예요`;
  if (V.phase === "shake") return "👉 흔들기를 할까요? " + V.pend.month + "월 패를 3장 들고 있어요 (이기면 점수 ×2)";
  if (V.phase === "bomb") return "👉 폭탄을 낼까요? " + V.pend.month + "월 패 3장 + 바닥 1장 (점수 ×2, 상대 피 1장씩)";
  if (V.phase === "gukjin") return "👉 9월 열끗(국진)을 얻었어요. 열끗과 쌍피 중 어떻게 쓸까요? (한 번 고르면 바꿀 수 없어요)";
  if (V.phase === "pick") return "👉 같은 달 패가 2장이에요. 가져갈 패를 하나 골라요 (반짝이는 바닥 패)";
  if (V.phase === "gostop") return "👉 " + V.pend.score + "점이에요! 「고」(계속)나 「스톱」(끝내기)을 골라요";
  if (V.hn[myS] === 0 || V.btok[myS] > 0) return "👉 내 차례예요. " + (V.hn[myS] === 0 ? "손패가 없어요. 「더미 뒤집기」를 눌러요" : "손패를 내거나 「더미 뒤집기」를 눌러요 (폭탄 보너스 " + V.btok[myS] + "번 남음)");
  return "👉 내 차례예요. 손패에서 한 장을 골라 내요";
}
function resultHtml(V) {
  const r = V.res; if (!r) return "";
  if (r.draw) return `<div class="card res"><h2>🤝 나가리</h2><div class="note">아무도 ${V.thr}점을 못 냈어요.</div></div>`;
  const common = r.common.filter(x => !/^고/.test(x));
  return `<div class="card res"><h2>🏆 ${esc(sname(r.winner))} 승리!</h2><table class="tbl"><tbody>${r.parts.map(x => `<tr><td>${x.n}</td><td>${x.p}점</td></tr>`).join("")}${r.go ? `<tr><td>고 ${r.go}번</td><td>${r.go >= 3 ? "×" + Math.pow(2, r.go - 2) : "+" + r.go + "점"}</td></tr>` : ""}${common.map(x => `<tr><td>${x}</td><td></td></tr>`).join("")}`
    + r.per.map(x => `<tr><td>낼 점수 · ${esc(sname(x.who))}${x.mult.length ? " · " + x.mult.join("·") : ""}</td><td>${x.pay}점</td></tr>`).join("") + `<tr><td><b>합계 · ${esc(sname(r.winner))} 받는 점수</b></td><td><b>${r.points}점</b></td></tr></tbody></table><div class="note">졌을 때 낼 점수는 놀이용 점수예요(포인트와 무관).</div></div>`;
}
function render() {
  if (!P) { $("st").textContent = "연결을 기다리는 중…"; return; }
  goBtn();
  if (P.ph === "wait" || !P.v) { $("st").textContent = waitText(2, 3); $("bar").innerHTML = ""; idle(); return; }
  const V = P.v, n = V.hn.length, myS = seatOf(me), mine = P.ph === "play" && myS >= 0 && V.turn === myS;
  const order = []; if (myS >= 0) { for (let k = 1; k < n; k++) order.push((myS + k) % n); order.push(myS); } else for (let p = 0; p < n; p++) order.push(p);
  $("bar").style.gridTemplateColumns = "repeat(" + n + ",1fr)"; $("bar").className = "bar" + (n === 3 ? " b3" : ""); $("bar").innerHTML = barHtml(V, order, myS);
  $("st").textContent = P.msg || "";
  const pk = P.ph === "play" && V.phase === "pick" && mine ? V.pend.ids : [], hh = myHand().sort((a, b) => a - b), canPlay = mine && V.phase === "hand" && hh.length > 0;
  const nl = Math.min(4, Math.ceil(V.dn / 6));
  $("tbl").innerHTML = capTable(V, order, myS)
    + `<div class="card tight"><div class="board"><div class="field" id="field" aria-label="바닥">${V.field.slice().sort((a, b) => a - b).map(id => gcard(id, { on: pk.includes(id), cls: pk.includes(id) ? "pick" : "" })).join("")}</div><div class="gpile"><div class="stk" aria-hidden="true">${"<i></i>".repeat(Math.max(nl, V.dn ? 1 : 0))}</div><b>${V.dn}</b>더미</div></div></div>`
    + `<div class="next${mine ? "" : " cpu"}">${esc(guideText(V, myS, mine))}</div>` + resultHtml(V) + totHtml();
  $("hand").innerHTML = hh.map(id => gcard(id, { on: canPlay, cls: canPlay && V.field.some(x => GS.month(x) === GS.month(id)) ? "can match" : (canPlay ? "can" : "") })).join("");
  let a = "";
  if (mine && P.ph === "play") {
    if (V.phase === "gostop") a = `<button class="btn" id="bgo" type="button">🔥 고! (지금 ${V.pend.score}점)</button><button class="btn ghost" id="bstop" type="button">✋ 스톱</button>`;
    else if (V.phase === "shake") a = `<button class="btn" id="bq1" type="button">🎲 흔들기 (점수 ×2)</button><button class="btn ghost" id="bq0" type="button">그냥 내기</button>`;
    else if (V.phase === "bomb") a = `<button class="btn" id="bq1" type="button">💣 폭탄! (3장 한꺼번에)</button><button class="btn ghost" id="bq0" type="button">한 장만 내기</button>`;
    else if (V.phase === "gukjin") a = `<button class="btn" id="bq1" type="button">🍶 쌍피로 쓰기 (피 2장)</button><button class="btn ghost" id="bq0" type="button">열끗으로 쓰기</button>`;
    else if (V.phase === "hand" && (V.hn[myS] === 0 || V.btok[myS] > 0)) a = `<button class="btn" id="bflip" type="button">🃏 더미 뒤집기${V.btok[myS] > 0 ? " (폭탄 보너스 " + V.btok[myS] + "번 남음)" : ""}</button>`;
  }
  $("acts").innerHTML = a;
  if ($("bgo")) { $("bgo").onclick = () => act({ t: "go" }); $("bstop").onclick = () => act({ t: "stop" }); }
  if ($("bq1")) { const ph = V.phase; $("bq1").onclick = () => act(ph === "gukjin" ? { t: "gukjin", as: "pi" } : { t: ph, yes: true }); $("bq0").onclick = () => act(ph === "gukjin" ? { t: "gukjin", as: "yeol" } : { t: ph, yes: false }); }
  if ($("bflip")) $("bflip").onclick = () => act({ t: "flip" });
}
$("hand").addEventListener("click", e => { const b = e.target.closest("button.gc"); if (!b || b.disabled || !P || P.ph !== "play") return; act({ t: "play", id: +b.dataset.id }); });
$("tbl").addEventListener("click", e => { const b = e.target.closest(".field button.gc"); if (!b || b.disabled || !P || P.ph !== "play") return; act({ t: "pick", id: +b.dataset.id }); });
render();
'''

party("net-gostop.html", "맞고·고스톱 (같이 하기)", "🎴", 12, "net-gostop-v1",
      "화투로 하는 2~3명 대결이에요. 2명이면 맞고(기준 7점), 3명이면 고스톱(기준 3점)이에요. 방장이 ▶ 시작하기를 누르면 패를 나눠요. 내 차례에 손패를 한 장 내면 같은 달 바닥 패를 가져가고, 더미에서 한 장 더 뒤집어요. 기준 점수가 되면 「고」(계속)나 「스톱」(끝내기)을 골라요. 흔들기·폭탄·쌍피 선택·피박·광박·고박도 시작 화면의 맞고와 같아요. 내 손패는 내 폰에만 보여요. 점수는 놀이용이고 포인트는 주지 않아요.",
      BODY, CARD_JS + JS, CARD_CSS + GCSS)
# 규칙 엔진(gostop-core.js)과 그림(gostop-art.js)을 화면 스크립트보다 먼저 읽는다
p = "out/net-gostop.html"; s = open(p, encoding="utf-8").read()
i = s.index("<script>\n")
s = s[:i] + '<script src="gostop-core.js"></script>\n<script src="gostop-art.js"></script>\n' + s[i:]
assert "gostop-core.js" in s and "gostop-art.js" in s
open(p, "w", encoding="utf-8").write(s)
