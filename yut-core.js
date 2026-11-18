/* 윷놀이 규칙 엔진(일반 규칙) — 화면과 무관한 순수 함수라서 node로도 시험해요(tools/dev/yut_test.js).
   말판: 29칸. 바깥 20칸(0 = 출발·도착, 5·10·15 = 모서리) + 지름길 9칸.
     칸 번호: 0 출발 → 1~4 → 5(오른쪽 위 모서리) → 6~9 → 10(왼쪽 위) → 11~14 → 15(왼쪽 아래) → 16~19 → 도착.
     지름길 ㉮: 5에서 시작하면 20·21 → 22(가운데) → 23·24 → 15 로 가서 바깥길을 이어 가요.
     지름길 ㉯: 10에서 시작하면 25·26 → 22(가운데) → 27·28 → 도착.
     가운데(22)에서 시작하면 27·28 → 도착(가장 빨리 나가는 길). 지름길은 "그 칸에서 움직이기 시작할 때"만 들어가요(그냥 지나가면 바깥길).
   윷가락 4개: 평평한 면 수 1=도(1칸) 2=개(2) 3=걸(3) 4=윷(4) 0=모(5). 도인데 표시된 가락이 평평하면 빽도(뒤로 1칸).
   말은 한 편에 4개. 같은 편 말이 한 칸에 모이면 업기(함께 움직임). 상대 말이 있는 칸에 서면 잡기(상대 말들은 출발 전으로, 한 번 더 던짐). 윷·모도 한 번 더.
   4개를 모두 도착시키면 이겨요. 도착은 출발점(0)을 지나거나 정확히 서는 것 모두 인정.
   편 상태 side = { w: 출발 전 말 수, done: 도착한 말 수, stacks: [{ at, lane, n, trail }] }  (JSON 가능). lane: "o" 바깥길, "a" 지름길 ㉮, "b" 지름길 ㉯. */
(function (root) {
  "use strict";
  var END = "end", HOME = "home";
  var NAMES = { "-1": "빽도", 1: "도", 2: "개", 3: "걸", 4: "윷", 5: "모" };
  function lerp(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; }
  var A = [270, 270], B = [270, 50], C = [50, 50], D = [50, 270], O = [160, 160], XY = [], k;
  for (k = 0; k < 5; k++) { XY[k] = lerp(A, B, k / 5); XY[5 + k] = lerp(B, C, k / 5); XY[10 + k] = lerp(C, D, k / 5); XY[15 + k] = lerp(D, A, k / 5); }
  XY[20] = lerp(B, O, 1 / 3); XY[21] = lerp(B, O, 2 / 3); XY[22] = O; XY[23] = lerp(O, D, 1 / 3); XY[24] = lerp(O, D, 2 / 3);
  XY[25] = lerp(C, O, 1 / 3); XY[26] = lerp(C, O, 2 / 3); XY[27] = lerp(O, A, 1 / 3); XY[28] = lerp(O, A, 2 / 3);
  var CORNER = { 0: 1, 5: 1, 10: 1, 15: 1, 22: 1 };

  // 한 칸 앞으로. first = 이번 움직임의 첫 걸음(이때만 지름길로 들어가요). 반환: [칸, 길] 또는 END
  function succ(n, lane, first) {
    if (first) { if (n === 5) return [20, "a"]; if (n === 10) return [25, "b"]; if (n === 22) return [27, "b"]; }
    if (lane === "a") { if (n === 20) return [21, "a"]; if (n === 21) return [22, "a"]; if (n === 22) return [23, "a"]; if (n === 23) return [24, "a"]; if (n === 24) return [15, "o"]; }
    if (lane === "b") { if (n === 25) return [26, "b"]; if (n === 26) return [22, "b"]; if (n === 22) return [27, "b"]; if (n === 27) return [28, "b"]; if (n === 28) return END; }
    if (n === 19) return END;
    return [n + 1, "o"];
  }
  // st(없으면 출발 전 말 1개)를 steps칸 움직인 결과. 반환: {end} | {home}(빽도로 출발 전으로) | {at, lane, trail} | null(못 움직임)
  function advance(st, steps) {
    var trail = st ? st.trail.slice() : [], at = st ? st.at : 0, lane = st ? st.lane : "o", i, nx;
    if (steps < 0) {
      if (!st) return null;
      trail.pop(); if (!trail.length) return { home: true };
      var t = trail[trail.length - 1]; return { at: t[0], lane: t[1], trail: trail };
    }
    for (i = 0; i < steps; i++) {
      nx = (!st && i === 0) ? [1, "o"] : succ(at, lane, i === 0);
      if (nx === END) return { end: true };
      at = nx[0]; lane = nx[1]; trail.push([at, lane]);
    }
    return { at: at, lane: lane, trail: trail };
  }
  function newSide() { return { w: 4, done: 0, stacks: [] }; }
  function count(s) { return s.w + s.done + s.stacks.reduce(function (a, x) { return a + x.n; }, 0); }
  // 윷가락 던지기. rnd() = 0~1. 반환 {n, name, flat[4]}  (flat[0]이 표시된 가락)
  function toss(rnd) {
    rnd = rnd || Math.random; var flat = [0, 0, 0, 0].map(function () { return rnd() < .5; }), c = flat.filter(Boolean).length;
    var n = c === 0 ? 5 : c === 1 && flat[0] ? -1 : c;
    return { n: n, name: NAMES[n], flat: flat };
  }
  // 이번 던지기(roll)로 할 수 있는 움직임 목록. 각 {from(-1 = 출발 전 말, 그 밖에는 stacks 번호), to(칸 번호 | "end" | "home"), n(움직이는 말 수), cap(잡는 말 수), stack(업는지)}
  function options(me, opp, roll) {
    var out = [];
    function add(from, st) {
      var r = advance(st, roll); if (!r) return;
      var n = st ? st.n : 1, m = { from: from, n: n, to: r.end ? END : r.home ? HOME : r.at, cap: 0, stack: false };
      if (!r.end && !r.home) { opp.stacks.forEach(function (o) { if (o.at === r.at) m.cap += o.n; }); me.stacks.forEach(function (s, i) { if (s.at === r.at && i !== from) m.stack = true; }); }
      out.push(m);
    }
    if (roll > 0 && me.w > 0) add(-1, null);
    me.stacks.forEach(function (s, i) { add(i, s); });
    return out;
  }
  // 움직임을 실제로 적용(me, opp 를 고쳐요). 반환 {cap, fin, stack, home, extra} — extra: 한 번 더 던지기(윷·모·잡기)
  function apply(me, opp, mv, roll) {
    var st = mv.from < 0 ? null : me.stacks[mv.from], n = st ? st.n : 1, res = { cap: 0, fin: 0, stack: false, home: false, extra: false }, r, j, same;
    r = advance(st, roll);
    if (st) me.stacks.splice(mv.from, 1); else me.w--;
    if (r.home) { me.w += n; res.home = true; return res; }
    if (r.end) { me.done += n; res.fin = n; res.extra = roll >= 4; return res; }
    for (j = opp.stacks.length - 1; j >= 0; j--) if (opp.stacks[j].at === r.at) { res.cap += opp.stacks[j].n; opp.w += opp.stacks[j].n; opp.stacks.splice(j, 1); }
    same = me.stacks.filter(function (s) { return s.at === r.at; })[0];
    if (same) { same.n += n; same.lane = r.lane; same.trail = r.trail; res.stack = true; } else me.stacks.push({ at: r.at, lane: r.lane, n: n, trail: r.trail });
    res.extra = roll >= 4 || res.cap > 0;
    return res;
  }
  var won = function (s) { return s.done >= 4; };
  // 컴퓨터가 고르는 움직임(options 의 번호). 도착 > 잡기 > 지름길·업기 > 앞으로 나가기, 잡힐 곳은 피해요
  function aiPick(me, opp, roll) {
    var ops = options(me, opp, roll); if (!ops.length) return -1;
    var best = -1, bs = -1e9;
    ops.forEach(function (m, i) {
      var s = Math.random() * 2 - 1;
      if (m.to === END) s += 40 * m.n; else if (m.to === HOME) s -= 30 * m.n;
      else {
        s += 60 * m.cap + (m.stack ? 6 : 0) + (m.to === 5 || m.to === 10 || m.to === 22 ? 7 : 0) + (m.to >= 20 ? 4 : 0);
        s += 0.4 * (m.to === 0 ? 0 : (m.to >= 20 ? m.to - 10 : m.to)) * m.n;
        var danger = 0; // 이 칸에 서면 상대가 다음에 잡을 수 있나(상대 말이 1~5칸 뒤에 있나)
        opp.stacks.forEach(function (o) { for (var k = 1; k <= 5; k++) { var r = advance(o, k); if (r && r.at === m.to) danger = 1; } });
        if (opp.w > 0) for (var q = 1; q <= 5; q++) { var r2 = advance(null, q); if (r2 && r2.at === m.to) danger = Math.max(danger, 0.5); }
        s -= 14 * danger * m.n;
      }
      if (m.from < 0 && m.to !== END) s += 1.5; // 출발 전 말도 적당히 내보내요
      if (s > bs) { bs = s; best = i; }
    });
    return best;
  }
  var api = { NAMES: NAMES, XY: XY, CORNER: CORNER, END: END, HOME: HOME, succ: succ, advance: advance, newSide: newSide, count: count, toss: toss, options: options, apply: apply, won: won, aiPick: aiPick };
  root.YutCore = api; if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
