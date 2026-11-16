/* 맞고(2인)·고스톱(3인) 규칙 엔진 — 화면과 무관한 순수 함수라서 node로도 시험해요(tools/dev/gs_test.js).
   화투 48장은 직접 정한 번호(0~47)로만 다루고 그림은 화면(go-stop.html)이 그려요. 규칙은 design 결정 D8(1단계)·D28(2단계).
   카드 번호: 월 = (번호 >> 2) + 1, 월 안의 순서 = 번호 & 3. 플레이어 번호: 0 = 나, 1·2 = 컴퓨터. 인원은 state.hands.length 로 안다(2 또는 3).
   진행: act(state, {t:"play",id}) → 필요하면 {t:"shake",yes}(흔들기)·{t:"bomb",yes}(폭탄)·{t:"pick",id}(짝 고르기)·{t:"gukjin",as}(국진 선택)
         → 점수가 기준(2인 7점, 3인 3점) 이상이면 {t:"go"} 또는 {t:"stop"}. 손패가 없는 차례(폭탄 뒤)는 {t:"flip"}.
   state 는 일반 객체(JSON 가능)이고 act 가 그대로 고쳐요. 규칙의 숫자는 아래 RULES 한 곳에서 고쳐요. */
(function (root) {
  "use strict";
  var MONTHS = [
    ["gwang", "ddi:red", "pi", "pi"], ["yeol:bird", "ddi:red", "pi", "pi"], ["gwang", "ddi:red", "pi", "pi"], ["yeol:bird", "ddi:cho", "pi", "pi"],
    ["yeol:bridge", "ddi:cho", "pi", "pi"], ["yeol:butterfly", "ddi:blue", "pi", "pi"], ["yeol:boar", "ddi:cho", "pi", "pi"], ["gwang", "yeol:goose", "pi", "pi"],
    ["yeol:cup", "ddi:blue", "pi", "pi"], ["yeol:deer", "ddi:blue", "pi", "pi"], ["gwang", "pi2", "pi", "pi"], ["gwang", "yeol:swallow", "ddi:plain", "pi2"]
  ];
  var NAMES = ["", "송학", "매조", "벚꽃", "흑싸리", "난초", "모란", "홍싸리", "공산", "국화", "단풍", "오동", "비"];
  var THRESHOLD = 7; // 맞고(2인)의 고·스톱 기준 점수(이전 단계와 같은 값, 호환용)
  // ── 규칙 숫자(D28): 사람 수별 설정과 배수
  var RULES = {
    2: { hand: 10, field: 8, threshold: 7 },   // 맞고
    3: { hand: 7, field: 6, threshold: 3 },    // 고스톱
    shakeMult: 2, bombMult: 2,                 // 흔들기·폭탄 한 번마다 곱하는 수
    myungbak: 7,                               // 멍박: 이긴 사람의 열끗이 이 장수 이상이면 진 사람 ×2
    gukjin: 32                                 // 국진(9월 열끗) 카드 번호
  };

  function info(id) {
    var m = (id >> 2) + 1, p = MONTHS[m - 1][id & 3].split(":"), t = p[0];
    return { id: id, month: m, type: t === "pi2" ? "pi" : t, sub: p[1] || "", pi: t === "pi2" ? 2 : t === "pi" ? 1 : 0, name: NAMES[m] };
  }
  function month(id) { return (id >> 2) + 1; }
  function rng(seed) { var a = seed >>> 0; return function () { a = (a + 0x6D2B79F5) >>> 0; var t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function shuffled(r) { var a = [], i, j, x; for (i = 0; i < 48; i++) a.push(i); for (i = 47; i > 0; i--) { j = Math.floor(r() * (i + 1)); x = a[i]; a[i] = a[j]; a[j] = x; } return a; }
  function countMonth(a) { var c = {}; a.forEach(function (id) { c[month(id)] = (c[month(id)] || 0) + 1; }); return c; }
  function maxCount(a) { var c = countMonth(a), m = 0; Object.keys(c).forEach(function (k) { if (c[k] > m) m = c[k]; }); return m; }

  function np(state) { return state.hands.length; }
  function nextP(state, p) { return (p + 1) % np(state); }
  function thr(state) { return (RULES[np(state)] || RULES[2]).threshold; }
  function others(state, p) { var o = [], i; for (i = 1; i < np(state); i++) o.push((p + i) % np(state)); return o; } // p 다음 차례부터 순서대로
  function allEmpty(state) { init(state); return state.hands.every(function (h, i) { return h.length === 0 && !state.btok[i]; }); } // 폭탄으로 받은 「뒤집기만」 차례(btok)가 남아 있으면 아직 안 끝남
  function zeros(n) { var a = [], i; for (i = 0; i < n; i++) a.push(0); return a; }
  function init(state) { // 시험용으로 손으로 만든 판에도 새 칸이 있도록 채운다
    var n = np(state), i;
    if (!state.shake) state.shake = zeros(n); if (!state.bomb) state.bomb = zeros(n);
    if (!state.btok) state.btok = zeros(n);
    if (!state.shaken) { state.shaken = []; for (i = 0; i < n; i++) state.shaken.push([]); }
    if (!state.declined) { state.declined = []; for (i = 0; i < n; i++) state.declined.push([]); }
    if (!state.gukjin) { state.gukjin = []; for (i = 0; i < n; i++) state.gukjin.push(null); }
  }

  // 새 판: 2인 = 손패 10장씩·바닥 8장, 3인 = 손패 7장씩·바닥 6장. 바닥에 같은 월이 3장 이상이거나 손패에 같은 월이 4장이면 다시 섞는다.
  // first: 먼저 시작하는 사람(2인은 0/1, 3인은 0~2)
  function newGame(seed, first, n) {
    n = n === 3 ? 3 : 2; var R = RULES[n], r = rng(seed), d, hands, field, tries = 0, i;
    do {
      d = shuffled(r); hands = []; for (i = 0; i < n; i++) hands.push(d.slice(i * R.hand, (i + 1) * R.hand)); field = d.slice(n * R.hand, n * R.hand + R.field); tries++;
    } while ((maxCount(field) >= 3 || hands.some(function (h) { return maxCount(h) >= 4; })) && tries < 50);
    var st = { seed: seed, n: n, hands: hands, field: field, deck: d.slice(n * R.hand + R.field), cap: [], turn: n === 2 ? (first ? 1 : 0) : ((first || 0) % 3), phase: "hand", pend: null, ctx: null,
      goCount: zeros(n), lastGo: zeros(n), winner: -1, result: null, last: null, turnNo: 0 };
    for (i = 0; i < n; i++) st.cap.push([]);
    init(st); return st;
  }

  // ── 점수. gk: 국진(9월 열끗)을 어떻게 쓰는지("pi" 면 쌍피로 계산, 그 밖에는 열끗)
  function score(cap, gk) {
    var g = [], y = [], d = [], p = 0, parts = [], total = 0, i, inf;
    for (i = 0; i < cap.length; i++) {
      if (cap[i] === RULES.gukjin && gk === "pi") { p += 2; continue; }
      inf = info(cap[i]); if (inf.type === "gwang") g.push(cap[i]); else if (inf.type === "yeol") y.push(cap[i]); else if (inf.type === "ddi") d.push(cap[i]); else p += inf.pi;
    }
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
  function scoreOf(state, p) { init(state); return score(state.cap[p], state.gukjin[p]); }

  // ── 결과 정산: 이긴 사람의 점수 + 고 점수(1고 +1, 2고 +2), 3고부터 2배씩, 흔들기·폭탄 ×2씩.
  //    진 사람마다 광박·피박·멍박 ×2, 고박(2인 ×2 / 3인은 고박한 사람이 다른 진 사람 몫까지 모두 부담).
  function settle(state, winner) {
    init(state);
    var w = scoreOf(state, winner), g = state.goCount[winner], base = w.total, common = [], n = np(state), per = [], total = 0, loserBest = 0, i;
    base += Math.min(g, 2); if (g >= 3) { base *= Math.pow(2, g - 2); common.push("고 " + g + "번"); }
    if (state.shake[winner]) { base *= Math.pow(RULES.shakeMult, state.shake[winner]); common.push("흔들기" + (state.shake[winner] > 1 ? " ×" + state.shake[winner] : "")); }
    if (state.bomb[winner]) { base *= Math.pow(RULES.bombMult, state.bomb[winner]); common.push("폭탄" + (state.bomb[winner] > 1 ? " ×" + state.bomb[winner] : "")); }
    others(state, winner).forEach(function (l) {
      var ls = scoreOf(state, l), pts = base, m = [], gobak = state.goCount[l] > 0;
      if (w.n.gwang >= 3 && ls.n.gwang === 0) { pts *= 2; m.push("광박"); }
      if (w.parts.some(function (x) { return /^피/.test(x.n); }) && ls.n.pi <= 5) { pts *= 2; m.push("피박"); }
      if (w.n.yeol >= RULES.myungbak) { pts *= 2; m.push("멍박"); }
      if (gobak && n === 2) { pts *= 2; m.push("고박"); }
      loserBest = Math.max(loserBest, ls.total);
      per.push({ who: l, pts: pts, mult: m, gobak: gobak && n === 3, score: ls.total, pay: pts });
    });
    if (n === 3) { // 독박: 고를 외친 사람이 있으면 그 사람이 진 사람들의 몫을 모두 낸다(둘 다 고를 외쳤으면 각자 자기 몫)
      var gb = per.filter(function (x) { return x.gobak; });
      if (gb.length === 1) { var sum = per.reduce(function (s, x) { return s + x.pts; }, 0); per.forEach(function (x) { x.pay = x === gb[0] ? sum : 0; }); gb[0].mult.push("고박(독박)"); }
      else if (gb.length === 2) gb.forEach(function (x) { x.mult.push("고박"); });
    }
    per.forEach(function (x) { total += x.pay; });
    state.winner = winner; state.phase = "end";
    state.result = { winner: winner, score: w.total, parts: w.parts, go: g, mult: common.concat(n === 2 ? per[0].mult : []), common: common, per: per, points: total, loserScore: loserBest };
  }
  function finishNoStop(state) { // 손패가 끝났을 때: 고를 외친 사람 중 기준 점수 이상인 가장 높은 사람이 승리, 없으면 나가리
    var best = -1, bs = 0;
    state.hands.forEach(function (_, p) { var s = scoreOf(state, p).total; if (state.goCount[p] > 0 && s >= thr(state) && s > bs) { best = p; bs = s; } });
    if (best >= 0) settle(state, best); else { state.winner = -2; state.phase = "end"; state.result = { winner: -2, score: 0, parts: [], go: 0, mult: [], common: [], per: [], points: 0, loserScore: 0, draw: true }; }
  }

  // ── 한 턴의 처리
  function remove(a, id) { var i = a.indexOf(id); if (i >= 0) a.splice(i, 1); }
  function sameMonth(state, id) { return state.field.filter(function (x) { return month(x) === month(id); }); }
  function take(state, ids) { var c = state.ctx; ids.forEach(function (id) { remove(state.field, id); state.cap[state.turn].push(id); c.got.push(id); }); }
  function steal(state, why) { // 상대마다 피 1장씩(1점짜리 먼저)
    if (why) state.ctx.sp.push(why);
    others(state, state.turn).forEach(function (o) {
      var opp = state.cap[o], pick = -1, i;
      for (i = 0; i < opp.length; i++) if (info(opp[i]).type === "pi" && info(opp[i]).pi === 1) { pick = i; break; }
      if (pick < 0) for (i = 0; i < opp.length; i++) if (info(opp[i]).type === "pi") { pick = i; break; }
      if (pick >= 0) { var id = opp.splice(pick, 1)[0]; state.cap[state.turn].push(id); state.ctx.steal.push(id); }
    });
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
    if (c.hk === "flip") return flipResolve(state); // 손패 없이 더미만 뒤집는 차례
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
    return flipResolve(state); // three·bomb: 이미 가져옴
  }
  function endTurn(state) {
    var c = state.ctx, me = state.turn;
    if (state.field.length === 0 && c.got.length > 0) steal(state, "싹쓸이");
    state.last = { who: me, hand: c.hand, flip: c.flip, got: c.got.slice(), sp: c.sp.slice(), steal: c.steal.slice() };
    init(state);
    if (c.got.indexOf(RULES.gukjin) >= 0 && !state.gukjin[me]) { state.phase = "gukjin"; state.pend = { type: "gukjin" }; return; } // 9월 열끗을 열끗/쌍피 중 고른다
    return afterTurn(state);
  }
  function afterTurn(state) {
    var me = state.turn;
    state.ctx = null; state.pend = null; state.turnNo++;
    var s = scoreOf(state, me).total, over = allEmpty(state);
    if (s >= thr(state) && s > state.lastGo[me]) {
      if (over) return settle(state, me);
      state.phase = "gostop"; state.pend = { type: "gostop", score: s }; return;
    }
    if (over) return finishNoStop(state);
    state.turn = nextP(state, me); state.phase = "hand";
  }

  // 손패의 카드 한 장을 낸다(흔들기·폭탄을 이미 정했거나 해당 없을 때). sp: 이번 차례에 미리 붙일 표시(흔들기)
  function doPlay(state, id, sp) {
    var me = state.turn, c, m;
    remove(state.hands[me], id); m = sameMonth(state, id);
    c = state.ctx = { hand: id, hk: "none", hm: -1, flip: null, got: [], sp: sp || [], steal: [] };
    if (m.length === 0) { state.field.push(id); c.hk = "none"; return doFlip(state); }
    if (m.length === 1) { c.hk = "one"; c.hm = m[0]; return doFlip(state); }
    if (m.length === 2) { c.hk = "two"; state.phase = "pick"; state.pend = { type: "pick", stage: "hand", ids: m.slice() }; return; }
    c.hk = "three"; take(state, [id].concat(m)); steal(state, "뻑 먹기"); return doFlip(state);
  }

  function act(state, a) {
    var me = state.turn, c, m, mm;
    init(state);
    if (a.t === "play") {
      if (state.phase !== "hand" || state.hands[me].indexOf(a.id) < 0) throw new Error("지금은 낼 수 없는 카드");
      mm = month(a.id); var inHand = state.hands[me].filter(function (x) { return month(x) === mm; }).length, onField = sameMonth(state, a.id).length;
      if (inHand >= 3 && state.declined[me].indexOf(mm) < 0 && state.shaken[me].indexOf(mm) < 0) { // 폭탄(바닥에 1장) 또는 흔들기(바닥에 없음)를 할 수 있는 경우 먼저 묻는다
        if (onField === 1) { state.phase = "bomb"; state.pend = { type: "bomb", id: a.id, month: mm }; return; }
        if (onField === 0) { state.phase = "shake"; state.pend = { type: "shake", id: a.id, month: mm }; return; }
      }
      return doPlay(state, a.id, []);
    }
    if (a.t === "shake") {
      if (state.phase !== "shake") throw new Error("흔들기를 고를 때가 아님");
      var sid = state.pend.id, smm = state.pend.month; state.pend = null; state.phase = "hand";
      if (a.yes) { state.shaken[me].push(smm); state.shake[me]++; return doPlay(state, sid, ["흔들기"]); }
      state.declined[me].push(smm); return doPlay(state, sid, []);
    }
    if (a.t === "bomb") {
      if (state.phase !== "bomb") throw new Error("폭탄을 고를 때가 아님");
      var bid = state.pend.id, bmm = state.pend.month; state.pend = null; state.phase = "hand";
      if (!a.yes) { state.declined[me].push(bmm); return doPlay(state, bid, []); }
      var three = state.hands[me].filter(function (x) { return month(x) === bmm; }), fcard = sameMonth(state, bid)[0];
      state.bomb[me]++; state.btok[me] += 2; three.forEach(function (x) { remove(state.hands[me], x); });
      c = state.ctx = { hand: bid, hk: "bomb", hm: fcard, flip: null, got: [], sp: [], steal: [], bombCards: three.slice() };
      take(state, three.concat([fcard])); steal(state, "폭탄"); return doFlip(state);
    }
    if (a.t === "flip") { // 더미만 뒤집는 차례: 손패가 없거나, 폭탄으로 받은 뒤집기 차례(btok)가 남아 있을 때
      if (state.phase !== "hand" || (state.hands[me].length > 0 && !state.btok[me])) throw new Error("손패가 남아 있으면 패를 내야 함");
      if (state.btok[me] > 0) state.btok[me]--;
      state.ctx = { hand: null, hk: "flip", hm: -1, flip: null, got: [], sp: [], steal: [] }; return doFlip(state);
    }
    if (a.t === "pick") {
      if (state.phase !== "pick" || state.pend.ids.indexOf(a.id) < 0) throw new Error("고를 수 없는 카드");
      c = state.ctx; var stage = state.pend.stage; state.pend = null;
      if (stage === "hand") { c.hm = a.id; state.phase = "hand"; return doFlip(state); }
      state.phase = "hand"; take(state, [c.flip, a.id]); return endTurn(state);
    }
    if (a.t === "gukjin") {
      if (state.phase !== "gukjin") throw new Error("국진을 고를 때가 아님");
      state.gukjin[me] = a.as === "pi" ? "pi" : "yeol"; return afterTurn(state);
    }
    if (a.t === "go" || a.t === "stop") {
      if (state.phase !== "gostop") throw new Error("고/스톱을 고를 때가 아님");
      if (a.t === "stop") return settle(state, me);
      state.goCount[me]++; state.lastGo[me] = state.pend.score; state.pend = null;
      if (allEmpty(state)) return finishNoStop(state);
      state.turn = nextP(state, me); state.phase = "hand"; return;
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
      var m = sameMonth(state, id), v = value(id), g, inHand = state.hands[me].filter(function (x) { return month(x) === month(id); }).length;
      if (m.length === 0) g = -v * 0.7;
      else if (m.length === 1) g = v + value(m[0]) + 2;
      else if (m.length === 2) g = v + Math.max(value(m[0]), value(m[1])) + 1.5;
      else g = 20 + v;
      if (inHand >= 3 && m.length === 1) g += 30;       // 폭탄
      else if (inHand >= 3 && m.length === 0) g += 4;   // 흔들기
      if (g > best) { best = g; pick = id; }
    });
    return pick;
  }
  function aiPick(state) { var ids = state.pend.ids; return ids.slice().sort(function (a, b) { return value(b) - value(a); })[0]; }
  function aiGo(state) { // true면 고, false면 스톱
    var me = state.turn, mine = scoreOf(state, me).total, opp = 0, left = state.hands[me].length, many = np(state) === 3;
    others(state, me).forEach(function (o) { opp = Math.max(opp, scoreOf(state, o).total); });
    if (many) { if (mine >= 7 || opp >= 3 || left <= 1) return false; return left >= 3 && opp <= 1; }
    if (mine >= 10 || opp >= 4 || left <= 2) return false;
    return left >= 4 || opp <= 1;
  }
  function aiGukjin(state) { // 국진을 열끗/쌍피 중 점수가 더 높은 쪽으로(같으면 피박을 피하려고 쌍피)
    var me = state.turn, a = score(state.cap[me], "yeol").total, b = score(state.cap[me], "pi").total;
    return b >= a ? "pi" : "yeol";
  }
  function aiStep(state) { // 컴퓨터가 지금 해야 할 행동 하나를 돌려준다
    if (state.phase === "hand") return state.hands[state.turn].length === 0 ? { t: "flip" } : { t: "play", id: aiPlay(state) };
    if (state.phase === "pick") return { t: "pick", id: aiPick(state) };
    if (state.phase === "gostop") return { t: aiGo(state) ? "go" : "stop" };
    if (state.phase === "shake") return { t: "shake", yes: true };
    if (state.phase === "bomb") return { t: "bomb", yes: true };
    if (state.phase === "gukjin") return { t: "gukjin", as: aiGukjin(state) };
    return null;
  }

  var api = { MONTHS: MONTHS, NAMES: NAMES, RULES: RULES, THRESHOLD: THRESHOLD, threshold: thr, info: info, month: month, newGame: newGame, act: act, score: score, scoreOf: scoreOf, settle: settle, value: value, aiStep: aiStep, aiPlay: aiPlay, aiPick: aiPick, aiGo: aiGo, aiGukjin: aiGukjin, rng: rng, sameMonth: sameMonth, others: others, count: np };
  root.GoStop = api; if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
