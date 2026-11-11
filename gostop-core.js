/* 맞고(2인 고스톱) 규칙 엔진 — 화면과 무관한 순수 함수라서 node로도 시험해요(tools/dev/gs_test.js).
   화투 48장은 직접 정한 번호(0~47)로만 다루고 그림은 화면(go-stop.html)이 그려요. 1단계 규칙은 design 결정 D8.
   카드 번호: 월 = (번호 >> 2) + 1, 월 안의 순서 = 번호 & 3.
   진행: act(state, {t:"play",id}) → 필요하면 {t:"pick",id} → 7점 이상이면 {t:"go"} 또는 {t:"stop"}. state 는 일반 객체(JSON 가능)이고 act 가 그대로 고쳐요. */
(function (root) {
  "use strict";
  var MONTHS = [
    ["gwang", "ddi:red", "pi", "pi"], ["yeol:bird", "ddi:red", "pi", "pi"], ["gwang", "ddi:red", "pi", "pi"], ["yeol:bird", "ddi:cho", "pi", "pi"],
    ["yeol:bridge", "ddi:cho", "pi", "pi"], ["yeol:butterfly", "ddi:blue", "pi", "pi"], ["yeol:boar", "ddi:cho", "pi", "pi"], ["gwang", "yeol:goose", "pi", "pi"],
    ["yeol:cup", "ddi:blue", "pi", "pi"], ["yeol:deer", "ddi:blue", "pi", "pi"], ["gwang", "pi2", "pi", "pi"], ["gwang", "yeol:swallow", "ddi:plain", "pi2"]
  ];
  var NAMES = ["", "송학", "매조", "벚꽃", "흑싸리", "난초", "모란", "홍싸리", "공산", "국화", "단풍", "오동", "비"];
  var THRESHOLD = 7, STEAL = 1;

  function info(id) {
    var m = (id >> 2) + 1, p = MONTHS[m - 1][id & 3].split(":"), t = p[0];
    return { id: id, month: m, type: t === "pi2" ? "pi" : t, sub: p[1] || "", pi: t === "pi2" ? 2 : t === "pi" ? 1 : 0, name: NAMES[m] };
  }
  function month(id) { return (id >> 2) + 1; }
  function rng(seed) { var a = seed >>> 0; return function () { a = (a + 0x6D2B79F5) >>> 0; var t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function shuffled(r) { var a = [], i, j, x; for (i = 0; i < 48; i++) a.push(i); for (i = 47; i > 0; i--) { j = Math.floor(r() * (i + 1)); x = a[i]; a[i] = a[j]; a[j] = x; } return a; }
  function countMonth(a) { var c = {}; a.forEach(function (id) { c[month(id)] = (c[month(id)] || 0) + 1; }); return c; }
  function maxCount(a) { var c = countMonth(a), m = 0; Object.keys(c).forEach(function (k) { if (c[k] > m) m = c[k]; }); return m; }

  // 새 판: 손패 10장씩, 바닥 8장, 더미 20장. 바닥에 같은 월이 3장 이상이거나 손패에 같은 월이 4장이면 다시 섞는다.
  function newGame(seed, first) {
    var r = rng(seed), d, hands, field, tries = 0;
    do {
      d = shuffled(r); hands = [d.slice(0, 10), d.slice(10, 20)]; field = d.slice(20, 28); tries++;
    } while ((maxCount(field) >= 3 || maxCount(hands[0]) >= 4 || maxCount(hands[1]) >= 4) && tries < 50);
    return { seed: seed, hands: hands, field: field, deck: d.slice(28), cap: [[], []], turn: first ? 1 : 0, phase: "hand", pend: null, ctx: null,
      goCount: [0, 0], lastGo: [0, 0], winner: -1, result: null, last: null, turnNo: 0 };
  }

  // ── 점수
  function score(cap) {
    var g = [], y = [], d = [], p = 0, parts = [], total = 0, i, inf;
    for (i = 0; i < cap.length; i++) { inf = info(cap[i]); if (inf.type === "gwang") g.push(cap[i]); else if (inf.type === "yeol") y.push(cap[i]); else if (inf.type === "ddi") d.push(cap[i]); else p += inf.pi; }
    function add(name, pts) { if (pts > 0) { parts.push({ n: name, p: pts }); total += pts; } }
    if (g.length >= 5) add("5광", 15); else if (g.length === 4) add("4광", 4); else if (g.length === 3) add(g.indexOf(44) >= 0 ? "비광 3광" : "3광", g.indexOf(44) >= 0 ? 2 : 3);
    if (y.length >= 5) add("열끗 " + y.length + "장", y.length - 4);
    var godori = [4, 12, 29].every(function (id) { return y.indexOf(id) >= 0; });
    if (godori) add("고도리", 5);
    if (d.length >= 5) add("띠 " + d.length + "장", d.length - 4);
    [["홍단", "red"], ["청단", "blue"], ["초단", "cho"]].forEach(function (s) { if (d.filter(function (id) { return info(id).sub === s[1]; }).length === 3) add(s[0], 3); });
    if (p >= 10) add("피 " + p + "장", p - 9);
    return { total: total, parts: parts, n: { gwang: g.length, yeol: y.length, ddi: d.length, pi: p } };
  }

  // ── 결과 정산: 점수 + 고 점수(1고 +1, 2고 +2), 3고부터 2배씩, 광박·피박 ×2
  function settle(state, winner) {
    var loser = 1 - winner, w = score(state.cap[winner]), l = score(state.cap[loser]), g = state.goCount[winner], pts = w.total, mult = [];
    pts += Math.min(g, 2); if (g >= 3) { pts *= Math.pow(2, g - 2); mult.push("고 " + g + "번"); }
    if (w.n.gwang >= 3 && l.n.gwang === 0) { pts *= 2; mult.push("광박"); }
    if (w.parts.some(function (x) { return /^피/.test(x.n); }) && l.n.pi <= 5) { pts *= 2; mult.push("피박"); }
    state.winner = winner; state.phase = "end";
    state.result = { winner: winner, score: w.total, parts: w.parts, go: g, mult: mult, points: pts, loserScore: l.total };
  }
  function finishNoStop(state) { // 손패가 끝났을 때: 고를 외친 사람이 7점 이상이면 승리, 아니면 나가리
    var best = -1, bs = 0;
    [0, 1].forEach(function (p) { var s = score(state.cap[p]).total; if (state.goCount[p] > 0 && s >= THRESHOLD && s > bs) { best = p; bs = s; } });
    if (best >= 0) settle(state, best); else { state.winner = -2; state.phase = "end"; state.result = { winner: -2, score: 0, parts: [], go: 0, mult: [], points: 0, loserScore: 0, draw: true }; }
  }

  // ── 한 턴의 처리
  function remove(a, id) { var i = a.indexOf(id); if (i >= 0) a.splice(i, 1); }
  function sameMonth(state, id) { return state.field.filter(function (x) { return month(x) === month(id); }); }
  function take(state, ids) { var c = state.ctx; ids.forEach(function (id) { remove(state.field, id); state.cap[state.turn].push(id); c.got.push(id); }); }
  function steal(state, why) {
    var opp = state.cap[1 - state.turn], pick = -1, i;
    for (i = 0; i < opp.length; i++) if (info(opp[i]).type === "pi" && info(opp[i]).pi === 1) { pick = i; break; }
    if (pick < 0) for (i = 0; i < opp.length; i++) if (info(opp[i]).type === "pi") { pick = i; break; }
    state.ctx.sp.push(why);
    if (pick >= 0) { var id = opp.splice(pick, 1)[0]; state.cap[state.turn].push(id); state.ctx.steal.push(id); }
  }
  function flipResolve(state) {
    var c = state.ctx, f = c.flip, m = sameMonth(state, f);
    if (m.length === 0) { state.field.push(f); return endTurn(state); }
    if (m.length === 1) { take(state, [f, m[0]]); return endTurn(state); }
    if (m.length === 2) { state.phase = "pick"; state.pend = { type: "pick", stage: "flip", ids: m.slice() }; return; }
    take(state, [f].concat(m)); steal(state, "뻑 먹기"); return endTurn(state); // 바닥에 묶여 있던 3장 + 뒤집은 1장
  }
  function doFlip(state) {
    var c = state.ctx, h = c.hand; c.flip = state.deck.shift();
    if (c.flip === undefined) { c.flip = null; return endTurn(state); }
    var same = month(c.flip) === month(h);
    if (c.hk === "none") { // 낸 패가 바닥에 놓였고 뒤집은 패가 같은 월 → 쪽
      if (same) { take(state, [h, c.flip]); steal(state, "쪽"); return endTurn(state); }
      return flipResolve(state);
    }
    if (c.hk === "one") {
      if (same) { state.field.push(h); state.field.push(c.flip); c.sp.push("뻑"); return endTurn(state); } // 3장이 바닥에 묶임
      take(state, [h, c.hm]); return flipResolve(state);
    }
    if (c.hk === "two") {
      if (same) { var other = state.field.filter(function (x) { return month(x) === month(h) && x !== c.hm; }); take(state, [h, c.hm, c.flip].concat(other)); steal(state, "따닥"); return endTurn(state); }
      take(state, [h, c.hm]); return flipResolve(state);
    }
    return flipResolve(state); // three: 이미 가져옴
  }
  function endTurn(state) {
    var c = state.ctx, me = state.turn;
    if (state.field.length === 0 && c.got.length > 0) steal(state, "싹쓸이");
    state.last = { who: me, hand: c.hand, flip: c.flip, got: c.got.slice(), sp: c.sp.slice(), steal: c.steal.slice() };
    state.ctx = null; state.pend = null; state.turnNo++;
    var s = score(state.cap[me]).total, over = state.hands[0].length === 0 && state.hands[1].length === 0;
    if (s >= THRESHOLD && s > state.lastGo[me]) {
      if (over) return settle(state, me);
      state.phase = "gostop"; state.pend = { type: "gostop", score: s }; return;
    }
    if (over) return finishNoStop(state);
    state.turn = 1 - me; state.phase = "hand";
  }

  function act(state, a) {
    var me = state.turn, c, m;
    if (a.t === "play") {
      if (state.phase !== "hand" || state.hands[me].indexOf(a.id) < 0) throw new Error("지금은 낼 수 없는 카드");
      remove(state.hands[me], a.id); m = sameMonth(state, a.id);
      c = state.ctx = { hand: a.id, hk: "none", hm: -1, flip: null, got: [], sp: [], steal: [] };
      if (m.length === 0) { state.field.push(a.id); c.hk = "none"; return doFlip(state); }
      if (m.length === 1) { c.hk = "one"; c.hm = m[0]; return doFlip(state); }
      if (m.length === 2) { c.hk = "two"; state.phase = "pick"; state.pend = { type: "pick", stage: "hand", ids: m.slice() }; return; }
      c.hk = "three"; take(state, [a.id].concat(m)); steal(state, "뻑 먹기"); return doFlip(state);
    }
    if (a.t === "pick") {
      if (state.phase !== "pick" || state.pend.ids.indexOf(a.id) < 0) throw new Error("고를 수 없는 카드");
      c = state.ctx; var stage = state.pend.stage; state.pend = null;
      if (stage === "hand") { c.hm = a.id; state.phase = "hand"; return doFlip(state); }
      state.phase = "hand"; take(state, [c.flip, a.id]); return endTurn(state);
    }
    if (a.t === "go" || a.t === "stop") {
      if (state.phase !== "gostop") throw new Error("고/스톱을 고를 때가 아님");
      if (a.t === "stop") return settle(state, me);
      state.goCount[me]++; state.lastGo[me] = state.pend.score; state.pend = null;
      if (state.hands[0].length === 0 && state.hands[1].length === 0) return finishNoStop(state);
      state.turn = 1 - me; state.phase = "hand"; return;
    }
    throw new Error("알 수 없는 행동");
  }

  // ── 컴퓨터(중간 난이도): 가치 높은 패를 가져오고, 아까운 패는 바닥에 내놓지 않는다
  function value(id) {
    var i = info(id);
    if (i.type === "gwang") return id === 44 ? 4 : 6;
    if (i.type === "yeol") return [4, 12, 29].indexOf(id) >= 0 ? 5 : 3.5;
    if (i.type === "ddi") return i.sub === "plain" ? 3 : 4;
    return i.pi === 2 ? 2 : 1;
  }
  function aiPlay(state) {
    var me = state.turn, best = -1e9, pick = state.hands[me][0];
    state.hands[me].forEach(function (id) {
      var m = sameMonth(state, id), v = value(id), g;
      if (m.length === 0) g = -v * 0.7;
      else if (m.length === 1) g = v + value(m[0]) + 2;
      else if (m.length === 2) g = v + Math.max(value(m[0]), value(m[1])) + 1.5;
      else g = 20 + v;
      if (g > best) { best = g; pick = id; }
    });
    return pick;
  }
  function aiPick(state) { var ids = state.pend.ids; return ids.slice().sort(function (a, b) { return value(b) - value(a); })[0]; }
  function aiGo(state) { // true면 고, false면 스톱
    var me = state.turn, mine = score(state.cap[me]).total, opp = score(state.cap[1 - me]).total, left = state.hands[me].length;
    if (mine >= 10 || opp >= 4 || left <= 2) return false;
    return left >= 4 || opp <= 1;
  }
  function aiStep(state) { // 컴퓨터가 지금 해야 할 행동 하나를 돌려준다
    if (state.phase === "hand") return { t: "play", id: aiPlay(state) };
    if (state.phase === "pick") return { t: "pick", id: aiPick(state) };
    if (state.phase === "gostop") return { t: aiGo(state) ? "go" : "stop" };
    return null;
  }

  var api = { MONTHS: MONTHS, NAMES: NAMES, THRESHOLD: THRESHOLD, info: info, month: month, newGame: newGame, act: act, score: score, settle: settle, value: value, aiStep: aiStep, aiPlay: aiPlay, aiPick: aiPick, aiGo: aiGo, rng: rng, sameMonth: sameMonth };
  root.GoStop = api; if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
