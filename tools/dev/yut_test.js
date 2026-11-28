// 윷놀이 엔진(yut-core.js) 시험: node yut_test.js
const Y = require("../../yut-core.js"); let bad = 0;
const ok = (c, m) => { if (!c) { bad++; console.log("❌", m); } };
const st = (at, lane, n, trail) => ({ at, lane: lane || "o", n: n || 1, trail: trail || [[at, lane || "o"]] });
// 길: 지름길은 그 칸에서 시작할 때만
ok(Y.advance(st(5), 1).at === 20, "5에서 시작 → 20");
ok(Y.advance(st(3, "o", 1, [[3, "o"]]), 3).at === 6, "5를 그냥 지나가면 바깥길 6");
ok(Y.advance(st(10), 1).at === 25, "10에서 시작 → 25");
ok(Y.advance(st(8, "o", 1, [[8, "o"]]), 3).at === 11, "10을 지나가면 11");
let r = Y.advance(st(5), 3); ok(r.at === 22, "5→20→21→22 (가운데)");
r = Y.advance(st(5), 5); ok(r.at === 24, "㉮ 5칸 = 24");
r = Y.advance(st(5), 6); ok(r.at === 15 && r.lane === "o", "㉮ 6칸 = 15 (바깥길로)");
r = Y.advance(st(5), 11); ok(r.at === 0, "㉮ 11칸 = 출발·도착 칸에 멈춤"); ok(Y.advance(st(5), 12).end, "㉮ 12칸 = 도착");
r = Y.advance(st(10), 5); ok(r.at === 28, "㉯ 5칸 = 28"); ok(Y.advance(st(10), 6).at === 0, "㉯ 6칸 = 출발·도착 칸에 멈춤"); ok(Y.advance(st(10), 7).end, "㉯ 7칸 = 도착");
r = Y.advance(st(22, "a"), 1); ok(r.at === 27, "가운데에서 시작하면 27");
r = Y.advance(st(22, "a", 1, [[20, "a"], [21, "a"], [22, "a"]]), 3); ok(r.at === 0 && !r.end, "가운데에서 걸(3칸) = 출발·도착 칸에 남음"); ok(Y.advance(st(22, "a", 1, [[20, "a"], [21, "a"], [22, "a"]]), 4).end, "가운데에서 윷(4칸) = 도착");
r = Y.advance(st(20, "a", 1, [[20, "a"]]), 3); ok(r.at === 23, "㉮ 20에서 3칸 = 23 (가운데를 지나 계속)");
r = Y.advance(st(26, "b", 1, [[25, "b"], [26, "b"]]), 3); ok(r.at === 28, "㉯ 26에서 3칸 = 28");
ok(Y.advance(st(19), 1).at === 0, "19에서 도(1칸) = 출발·도착 칸에 남음"); ok(Y.advance(st(19), 2).end && Y.advance(st(19), 3).end, "19에서 2칸 이상 = 도착");
ok(Y.advance(st(0, "o", 1, [[19, "o"], [0, "o"]]), 1).end, "출발·도착 칸의 말은 도(1칸)로도 도착"); r = Y.advance(st(0, "o", 1, [[19, "o"], [0, "o"]]), -1); ok(r.at === 19, "출발·도착 칸의 말 빽도 → 19");
ok(Y.advance(null, 1).at === 1 && Y.advance(null, 5).at === 5, "출발 전 말: 1칸=1, 5칸=5");
// 빽도
r = Y.advance(st(2, "o", 1, [[1, "o"], [2, "o"]]), -1); ok(r.at === 1, "빽도 2→1");
ok(Y.advance(st(1, "o", 1, [[1, "o"]]), -1).home, "1에서 빽도 → 출발 전");
r = Y.advance(st(21, "a", 1, [[20, "a"], [21, "a"]]), -1); ok(r.at === 20 && r.lane === "a", "지름길에서 빽도 21→20");
r = Y.advance(st(15, "o", 1, [[20, "a"], [21, "a"], [22, "a"], [23, "a"], [24, "a"], [15, "o"]]), -1); ok(r.at === 24, "지름길로 온 15에서 빽도 → 24");
r = Y.advance(null, -1); ok(r && r.at === 0 && r.trail.length === 1, "출발 전 말 빽도 → 출발·도착 칸에 놓기(2026-11-28)");
ok(Y.advance({ at: 0, lane: "o", n: 1, trail: [[0, "o"]] }, 2).end, "출발 전에서 빽도로 놓은 말은 다음에 움직이면 도착");
ok(Y.advance({ at: 0, lane: "o", n: 1, trail: [[0, "o"]] }, -1).home, "그 말이 또 빽도면 출발 전으로");
{ const me = { w: 4, done: 0, stacks: [{ at: 2, lane: "o", n: 1, trail: [[1, "o"], [2, "o"]] }] }, op = { w: 3, done: 0, stacks: [{ at: 0, lane: "o", n: 1, trail: [[19, "o"], [0, "o"]] }] };
  const os = Y.options(me, op, -1); ok(os.some(m => m.from === -1 && m.to === 0 && m.cap === 1) && os.some(m => m.from === 0 && m.to === 1), "빽도 선택지: 판 위 말 뒤로 + 새 말 출발·도착 칸(상대 말 잡기 포함)");
  Y.apply(me, op, os.find(m => m.from === -1), -1); ok(me.w === 3 && me.stacks.some(x => x.at === 0) && op.w === 4, "새 말을 놓으면 출발 전 3, 상대 말은 잡혀 출발 전으로"); }
{ const me = { w: 0, done: 4, stacks: [] }; ok(Y.options(me, { w: 4, done: 0, stacks: [] }, -1).length === 0, "출발 전 말도 판 위 말도 없으면 빽도 선택지 없음"); }
// 윷가락 확률(통계)
const cnt = {}; for (let i = 0; i < 160000; i++) { const t = Y.toss(); cnt[t.n] = (cnt[t.n] || 0) + 1; }
const p = n => cnt[n] / 160000; ok(Math.abs(p(-1) - 1 / 16) < .01 && Math.abs(p(1) - 3 / 16) < .01 && Math.abs(p(2) - 6 / 16) < .01 && Math.abs(p(3) - 4 / 16) < .01 && Math.abs(p(4) - 1 / 16) < .01 && Math.abs(p(5) - 1 / 16) < .01, "확률 " + JSON.stringify(cnt));
// 잡기·업기
let a = Y.newSide(), b = Y.newSide(); a.w = 3; a.stacks.push(st(3)); b.w = 3; b.stacks.push(st(5));
let o = Y.options(a, b, 2).find(m => m.from === 0); ok(o.to === 5 && o.cap === 1, "3→5 잡기 옵션");
let res = Y.apply(a, b, o, 2); ok(res.cap === 1 && res.extra && b.w === 4 && b.stacks.length === 0, "잡으면 상대 말 출발 전, 한 번 더");
a.w = 2; a.stacks.push(st(2, "o", 1, [[1, "o"], [2, "o"]]));
o = Y.options(a, b, 3).find(m => m.from === 1); ok(o.to === 5 && o.stack, "같은 편 위로 → 업기");
res = Y.apply(a, b, o, 3); ok(res.stack && a.stacks.length === 1 && a.stacks[0].n === 2, "업으면 한 덩어리");
o = Y.options(a, b, 1).find(m => m.from === 0); res = Y.apply(a, b, o, 1); ok(a.stacks[0].at === 20 && a.stacks[0].n === 2, "업은 말은 함께 움직임(5→20)");
// 출발·도착 칸에 남은 말: 업기·잡기·도착 처리
a = Y.newSide(); b = Y.newSide(); a.w = 2; a.stacks.push(st(0, "o", 1, [[19, "o"], [0, "o"]])); b.w = 3; b.stacks.push(st(27, "b", 1, [[27, "b"]]));
o = Y.options(b, a, 2).find(m => m.from === 0); ok(o && o.to === 0 && o.cap === 1, "출발·도착 칸에 서 있는 말은 정확히 서면 잡을 수 있다");
let fin = Y.options(a, b, 1).find(m => m.from === 0); res = Y.apply(a, b, fin, 1); ok(res.fin === 1 && a.done === 1 && a.stacks.length === 0, "출발·도착 칸의 말이 움직이면 도착");
// 무작위 대국 3000판: 말 수 보존, 끝남, 모든 칸 방문
const seen = new Set(); let maxTurns = 0;
for (let g = 0; g < 3000; g++) {
  const S = [Y.newSide(), Y.newSide()]; let t = 0, turns = 0;
  while (!Y.won(S[0]) && !Y.won(S[1])) {
    if (++turns > 4000) { ok(false, "끝나지 않는 판"); break; }
    let more = true;
    while (more) {
      const roll = Y.toss().n, ops = Y.options(S[t], S[1 - t], roll); more = roll >= 4;
      if (ops.length) { const k = g % 2 && t === 1 ? Y.aiPick(S[t], S[1 - t], roll) : Math.floor(Math.random() * ops.length); const rr = Y.apply(S[t], S[1 - t], ops[k], roll); more = rr.extra; }
      S[t].stacks.forEach(s => seen.add(s.at));
      ok(Y.count(S[0]) === 4 && Y.count(S[1]) === 4, "말 수 보존");
      if (Y.won(S[t])) break;
    }
    if (!Y.won(S[t])) t = 1 - t;
  }
  maxTurns = Math.max(maxTurns, turns);
}
// ── 3·4명 대결(같이 하기): 상대가 여러 편이어도 말 수가 보존되고, 서로 다른 편이 한 칸을 같이 쓰지 않고, 잡기는 그 칸의 모든 상대 말을 잡는지
let multiMax = 0, capMulti = 0;
for (let g = 0; g < 600; g++) {
  const N = 3 + g % 2, S = Array.from({ length: N }, () => Y.newSide()); let t = 0, turns = 0;
  while (!S.some(Y.won) && turns < 4000) {
    let more = true;
    while (more && !S.some(Y.won)) {
      const roll = Y.toss().n, opp = S.filter((x, i) => i !== t), ops = Y.options(S[t], opp, roll); more = roll >= 4; turns++;
      if (ops.length) { const k = (g + t) % 3 === 0 ? Y.aiPick(S[t], opp, roll) : Math.floor(Math.random() * ops.length), before = opp.reduce((a, x) => a + x.w, 0), expectCap = ops[k].cap, rr = Y.apply(S[t], opp, ops[k], roll);
        ok(rr.cap === expectCap, "options의 잡기 수와 apply의 잡기 수가 같아야 함"); ok(opp.reduce((a, x) => a + x.w, 0) === before + rr.cap, "잡힌 말은 모두 출발 전으로"); if (rr.cap && opp.filter(x => true).length > 1) capMulti++; more = rr.extra; }
      S.forEach(x => ok(Y.count(x) === 4, "말 수 보존(" + N + "명)"));
      const owner = {}; S.forEach((x, i) => x.stacks.forEach(st => { if (st.at !== 0) { ok(owner[st.at] === undefined || owner[st.at] === i, "서로 다른 편이 같은 칸을 같이 씀 " + st.at); owner[st.at] = i; } }));
    }
    t = (t + 1) % N;
  }
  ok(S.some(Y.won), "3·4명 판이 끝나지 않음"); multiMax = Math.max(multiMax, turns);
}
ok(capMulti > 0, "여러 상대가 있는 판에서 잡기가 한 번도 안 나옴");
for (let n = 1; n <= 28; n++) ok(seen.has(n), "방문 못 한 칸 " + n);
console.log(bad ? "실패 " + bad + "건" : "✅ 윷놀이 엔진 시험 통과 (2명 3000판 + 3·4명 600판, 가장 긴 판 " + maxTurns + "/" + multiMax + "차례)");
process.exit(bad ? 1 : 0);
