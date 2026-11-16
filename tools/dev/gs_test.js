// 맞고 규칙 엔진 시험: node gs_test.js  (브라우저 필요 없음)
const G = require('../../gostop-core.js'); let bad = 0, n = 0;
const ok = (c, m) => { n++; if (!c) { bad++; console.log('[실패] ' + m); } else if (process.env.V) console.log('[통과] ' + m); };
const eq = (a, b, m) => ok(JSON.stringify(a) === JSON.stringify(b), m + ' (기대 ' + JSON.stringify(b) + ', 실제 ' + JSON.stringify(a) + ')');
const sort = a => a.slice().sort((x, y) => x - y);
// 1) 덱 구성
const all = [...Array(48).keys()].map(G.info), cnt = t => all.filter(i => i.type === t).length;
eq([cnt('gwang'), cnt('yeol'), cnt('ddi'), cnt('pi')], [5, 9, 10, 24], '광5·열끗9·띠10·피24장');
eq(all.filter(i => i.type === 'pi').reduce((s, i) => s + i.pi, 0), 26, '피 점수 합(쌍피 2장 포함) 26');
eq(['red', 'blue', 'cho'].map(s => all.filter(i => i.sub === s).length), [3, 3, 3], '홍단·청단·초단 각 3장');
eq([4, 12, 29].map(id => G.info(id).type), ['yeol', 'yeol', 'yeol'], '고도리 3장은 열끗');
eq(G.info(44).type + G.info(44).month, 'gwang12', '44번은 12월 광(비광)');
// 2) 점수
const S = ids => G.score(ids).total;
eq(S([0, 8, 28]), 3, '광 3장(비광 없음) 3점'); eq(S([0, 8, 44]), 2, '비광 포함 3광 2점');
eq(S([0, 8, 28, 40]), 4, '광 4장 4점'); eq(S([0, 8, 28, 40, 44]), 15, '5광 15점');
eq(S([4, 12, 29]), 5, '고도리 5점');
eq(S([4, 12, 29, 16, 24]), 6, '고도리 5점 + 열끗 5장 1점');
eq(S([1, 5, 9]), 3, '홍단 3점'); eq(S([13, 17, 25]), 3, '초단(4·5·7월) 3점'); eq(S([21, 33, 37]), 3, '청단(6·9·10월) 3점');
eq(S([2, 3, 6, 7, 10, 11, 14, 15, 18, 19]), 1, '피 10장 1점'); eq(S([2, 3, 6, 7, 10, 11, 14, 15, 18, 19, 22]), 2, '피 11장 2점');
eq(S([2, 3, 6, 7, 10, 11, 14, 15, 41]), 1, '쌍피(11월)는 2장으로 쳐서 피 10장분 1점');
eq(S([1, 5, 9, 4, 12]), 3, '홍단만 3점(새 2장은 점수 아님)');
// 3) 한 턴 규칙: 필요한 칸만 채워 만든 판 (hands[1] 은 비지 않게 한 장 둔다)
const mk = o => ({ seed: 0, hands: [o.h || [], o.h2 || [47]], field: o.f || [], deck: o.d || [], cap: [o.c0 || [], o.c1 || []], turn: 0, phase: 'hand', pend: null, ctx: null, goCount: [0, 0], lastGo: [0, 0], winner: -1, result: null, last: null, turnNo: 0 });
let s = mk({ h: [16, 40], f: [0], d: [17], c1: [2, 3] }); G.act(s, { t: 'play', id: 16 });
eq(sort(s.cap[0]), [2, 16, 17], '쪽: 낸 패+뒤집은 패+상대 피 1장'); ok(s.last.sp.includes('쪽'), '쪽 표시'); eq(s.cap[1], [3], '쪽: 상대 피가 1장 줄어듦');
s = mk({ h: [16, 40], f: [18], d: [17] }); G.act(s, { t: 'play', id: 16 });
eq(sort(s.field), [16, 17, 18], '뻑: 3장이 바닥에 묶임'); eq(s.cap[0], [], '뻑: 가져가는 것 없음'); ok(s.last.sp.includes('뻑'), '뻑 표시');
s = mk({ h: [22, 40], f: [20, 21], d: [23], c1: [2] }); G.act(s, { t: 'play', id: 22 }); eq(s.phase, 'pick', '바닥에 같은 월 2장이면 고르기'); G.act(s, { t: 'pick', id: 20 });
eq(sort(s.cap[0]), [2, 20, 21, 22, 23], '따닥: 4장 모두 + 상대 피 1장'); ok(s.last.sp.includes('따닥'), '따닥 표시');
s = mk({ h: [17, 40], f: [16, 0], d: [1], c1: [2] }); G.act(s, { t: 'play', id: 17 });
ok(s.last.sp.includes('싹쓸이') && s.field.length === 0, '싹쓸이: 바닥을 비우면 표시'); ok(s.cap[0].includes(2), '싹쓸이: 상대 피 1장 받음');
s = mk({ h: [19, 40], f: [16, 17, 18], d: [8] }); G.act(s, { t: 'play', id: 19 });
eq(sort(s.cap[0]).slice(0, 4), [16, 17, 18, 19], '뻑 먹기: 묶인 3장 + 내 패 4장'); ok(s.last.sp.includes('뻑 먹기'), '뻑 먹기 표시');
s = mk({ h: [22, 40], f: [20, 21, 0], d: [4] }); G.act(s, { t: 'play', id: 22 }); G.act(s, { t: 'pick', id: 21 });
ok(s.cap[0].includes(22) && s.cap[0].includes(21) && s.field.includes(20), '2장 중 하나를 고르면 나머지는 바닥에 남음');
s = mk({ h: [16, 40], f: [], d: [0] }); G.act(s, { t: 'play', id: 16 }); ok(s.field.includes(16) && s.field.includes(0) && s.turn === 1, '짝이 없으면 바닥에 놓고 차례가 넘어감');
// 4) 고/스톱·정산
const c7 = [0, 8, 28, 40, 1, 5, 9]; // 광 4장(4점) + 홍단(3점) = 7점
let t = mk({ h: [24, 46], f: [], d: [26], c0: c7.slice(), h2: [47, 45] }); G.act(t, { t: 'play', id: 24 });
eq(t.phase, 'gostop', '7점이 되면 고/스톱을 묻는다'); G.act(t, { t: 'go' }); eq([t.turn, t.phase, t.goCount[0], t.lastGo[0]], [1, 'hand', 1, 7], '고를 하면 상대 차례, 고 횟수·기준점 기록');
let w = mk({ h: [24, 46], f: [], d: [26], c0: c7.slice(), c1: [2, 3] }); G.act(w, { t: 'play', id: 24 }); G.act(w, { t: 'stop' });
eq([w.phase, w.result.winner, w.result.score], ['end', 0, 7], '스톱하면 판 끝'); ok(w.result.mult.includes('광박') && !w.result.mult.includes('피박'), '광박 ×2(상대 광 없음), 피 점수는 없어 피박 아님'); eq(w.result.points, 14, '정산 7점 ×2(광박)');
let x = mk({ h: [24, 46], f: [], d: [26], c0: c7.slice(), c1: [2, 3] }); x.goCount[0] = 3; G.act(x, { t: 'play', id: 24 }); G.act(x, { t: 'stop' });
eq(x.result.points, (7 + 2) * 2 * 2, '3고: (점수+2)×2, 광박 ×2');
let y = mk({ h: [24, 46], f: [], d: [26], c0: [0, 8, 28, 40, 1, 5, 9] }); y.lastGo[0] = 7; G.act(y, { t: 'play', id: 24 });
eq(y.phase, 'hand', '고 뒤에는 점수가 오르지 않으면 다시 묻지 않는다');
let z = mk({ h: [24], f: [], d: [26], c0: c7.slice(), h2: [] }); G.act(z, { t: 'play', id: 24 }); eq(z.phase, 'end', '마지막 턴에 7점이면 바로 끝(스톱)');
// 4-2) 2단계 규칙(D28): 3인·흔들기·폭탄·국진 선택·멍박·고박·손패 없는 차례
const mkn = o => { const n = o.hands.length; return { seed: 0, hands: o.hands, field: o.f || [], deck: o.d || [], cap: o.cap || Array.from({ length: n }, () => []), turn: o.turn || 0, phase: 'hand', pend: null, ctx: null,
  goCount: Array(n).fill(0), lastGo: Array(n).fill(0), winner: -1, result: null, last: null, turnNo: 0 }; };
const g3 = G.newGame(7, 0, 3);
eq([g3.hands.map(h => h.length), g3.field.length, g3.deck.length, G.threshold(g3)], [[7, 7, 7], 6, 21, 3], '3인: 손패 7·바닥 6·더미 21, 기준 3점');
eq([G.newGame(7, 0).hands.map(h => h.length), G.threshold(G.newGame(7, 0))], [[10, 10], 7], '2인(맞고)은 그대로: 손패 10, 기준 7점');
// 3인 스틸: 쪽이면 상대 둘에게서 피 1장씩
let q = mkn({ hands: [[16, 40], [47], [46]], f: [0], d: [17], cap: [[], [2, 3], [6, 7]] }); G.act(q, { t: 'play', id: 16 });
eq([q.cap[0].length, q.cap[0].filter(id => G.info(id).type === 'pi').length, q.cap[1].length, q.cap[2].length], [4, 2, 1, 1], '3인 쪽: 낸 패·뒤집은 패 + 상대 두 사람에게서 피 1장씩(받은 피 2장)');
eq(q.turn, 1, '3인: 차례는 0→1→2 순서로 넘어간다');
// 흔들기: 같은 달 3장 + 바닥에 없음 → 묻고, 하면 ×2
let sk = mkn({ hands: [[0, 1, 2, 40], [47], [46]], f: [8], d: [9] }); G.act(sk, { t: 'play', id: 0 });
eq([sk.phase, sk.pend.type], ['shake', 'shake'], '손패 같은 달 3장(바닥에 없음)이면 흔들기를 묻는다'); G.act(sk, { t: 'shake', yes: true });
ok(sk.shake[0] === 1 && sk.last.sp.includes('흔들기'), '흔들기를 하면 횟수·표시가 남는다');
let sk3 = mkn({ hands: [[0, 1, 2, 40], [47], [46]], f: [8], d: [9] }); G.act(sk3, { t: 'play', id: 0 }); G.act(sk3, { t: 'shake', yes: false });
ok(sk3.shake[0] === 0 && sk3.declined[0].includes(1), '흔들기를 안 하면 횟수가 늘지 않고 같은 달을 다시 묻지 않는다');
let sw = mkn({ hands: [[16, 40], [47], [46]], cap: [[0, 8, 28, 40, 1, 5, 9], [2], [3]], f: [], d: [26] }); sw.shake = [1, 0, 0]; sw.bomb = [0, 0, 0]; G.act(sw, { t: 'play', id: 16 }); G.act(sw, { t: 'stop' });
ok(sw.result.common.includes('흔들기'), '정산에 흔들기 표시'); eq(sw.result.points, 7 * 2 * 2 * 2, '흔들기 ×2, 광박 ×2씩 두 사람(3점 기준 3인) 몫 합산: 7점 ×2(흔들기) ×2(광박) × 진 사람 2명 = 56');
// 폭탄: 손패 3장 + 바닥 1장 → 4장 한 번에, 상대 피 1장씩, ×2
let bm = mkn({ hands: [[0, 1, 2, 40], [47], [46]], f: [3, 8], d: [9, 20, 21, 22], cap: [[], [10], [14]] }); G.act(bm, { t: 'play', id: 0 });
eq(bm.phase, 'bomb', '손패 같은 달 3장 + 바닥 1장이면 폭탄을 묻는다'); G.act(bm, { t: 'bomb', yes: true });
ok([0, 1, 2, 3].every(id => bm.cap[0].includes(id)) && bm.hands[0].join() === '40' && bm.bomb[0] === 1 && bm.last.sp.includes('폭탄'), '폭탄: 4장을 가져오고 손패에서 3장이 한꺼번에 나간다');
ok(bm.cap[0].includes(10) && bm.cap[0].includes(14) && bm.cap[1].length === 0 && bm.cap[2].length === 0, '폭탄: 상대 두 사람에게서 피 1장씩');
ok(bm.btok[0] === 2, '폭탄을 내면 패 없이 뒤집기만 하는 차례(btok)를 2번 받는다');
{ const d0 = bm.deck.length, h0 = bm.hands[0].length; bm.turn = 0; bm.phase = 'hand'; bm.pend = null; bm.ctx = null; G.act(bm, { t: 'flip' }); ok(bm.btok[0] === 1 && bm.hands[0].length === h0 && bm.deck.length < d0, '손패가 남아 있어도 폭탄 보너스로 패를 내지 않고 더미만 뒤집을 수 있다'); }
let bm3 = mkn({ hands: [[40], [47], [46]], f: [8], d: [9, 10] }); let thr3 = false; try { G.act(bm3, { t: "flip" }); } catch (e) { thr3 = true; } ok(thr3, '폭탄 보너스가 없고 손패가 있으면 뒤집기만은 안 된다');
let bm2 = mkn({ hands: [[0, 1, 2, 40], [47], [46]], f: [3, 8], d: [9] }); G.act(bm2, { t: 'play', id: 0 }); G.act(bm2, { t: 'bomb', yes: false }); ok(bm2.bomb[0] === 0 && bm2.hands[0].length === 3, '폭탄을 안 하면 한 장만 낸다');
// 손패 없는 차례
let fo = mkn({ hands: [[], [47], [46]], f: [8], d: [16] }); G.act(fo, { t: 'flip' }); ok(fo.last.hand === null && fo.field.length === 2 && fo.turn === 1, '손패가 없으면 더미만 뒤집고 차례가 넘어간다');
let fo2 = mkn({ hands: [[16], [47], [46]], f: [8], d: [9] }); let thrown = false; try { G.act(fo2, { t: 'flip' }); } catch (e) { thrown = true; } ok(thrown, '손패가 남아 있으면 flip 은 못 한다');
// 국진(9월 열끗) 선택
let gk = mkn({ hands: [[33, 40], [47], [46]], f: [32], d: [0] }); G.act(gk, { t: 'play', id: 33 });
eq([gk.phase, gk.pend.type], ['gukjin', 'gukjin'], '9월 열끗(국진)을 얻으면 선택을 묻는다'); G.act(gk, { t: 'gukjin', as: 'pi' });
eq([gk.gukjin[0], gk.turn, G.score([32], 'pi').n.pi, G.score([32], 'yeol').n.yeol], ['pi', 1, 2, 1], '쌍피를 고르면 피 2장으로 계산, 열끗이면 열끗 1장');
// 멍박: 이긴 사람의 열끗 7장 이상
const yeol7 = [4, 12, 16, 20, 24, 29, 32];
let mb = mkn({ hands: [[8], [47]], cap: [yeol7.slice(), [2]], f: [], d: [26] }); G.act(mb, { t: 'play', id: 8 }); eq(mb.phase, 'gostop', '열끗 7장(고도리 포함)이면 7점 이상: 고·스톱을 묻는다'); G.act(mb, { t: 'stop' });
ok(mb.result.mult.includes('멍박'), '멍박: 이긴 사람 열끗 7장 이상이면 진 사람 ×2');
// 고박: 2인은 ×2, 3인은 고박한 사람이 진 사람 몫을 모두 부담
let gb = mkn({ hands: [[24, 46], [47, 45]], cap: [c7.slice(), [2, 3]], d: [26] }); gb.goCount = [0, 1]; G.act(gb, { t: 'play', id: 24 }); G.act(gb, { t: 'stop' });
ok(gb.result.mult.includes('고박'), '2인 고박 표시'); eq(gb.result.points, 7 * 2 * 2, '2인 고박: 광박 ×2, 고박 ×2 = 28');
let g3b = mkn({ hands: [[24, 46], [47, 45], [44, 43]], cap: [c7.slice(), [2, 3], [6, 7]], d: [26] }); g3b.goCount = [0, 1, 0]; G.act(g3b, { t: 'play', id: 24 }); G.act(g3b, { t: 'stop' });
eq(g3b.result.per.map(x => x.pay), [14 + 14, 0].reverse().reverse(), '3인 고박(독박): 고를 외친 사람이 진 두 사람 몫(14+14)을 모두 부담');
ok(g3b.result.per[0].mult.includes('고박(독박)') && g3b.result.points === 28, '독박 표시와 이긴 사람이 받는 합계 28');
// 5) 시뮬레이션: 컴퓨터끼리 많이 두어 보고 카드 48장이 항상 보존되는지, 끝까지 가는지
let games = 0, draws = 0, wins = [0, 0], sp = {}, maxPts = 0;
const total = s => [...s.hands[0], ...s.hands[1], ...s.field, ...s.deck, ...s.cap[0], ...s.cap[1]];
for (let seed = 1; seed <= 3000; seed++) {
  const st = G.newGame(seed, seed % 2); let k = 0;
  try {
    while (st.phase !== 'end' && k++ < 400) {
      G.act(st, G.aiStep(st));
      if (st.last && st.last.sp && st.last.turnNo !== st.turnNo) { st.last.sp.forEach(q => sp[q] = (sp[q] || 0) + 1); st.last.turnNo = st.turnNo; }
      if (!st.ctx && new Set(total(st)).size !== 48) { bad++; console.log('[실패] 카드 보존 깨짐 seed=' + seed); break; }
    }
  } catch (e) { bad++; console.log('[실패] 예외 seed=' + seed + ' ' + e.message); break; }
  if (st.phase !== 'end') { bad++; console.log('[실패] 끝나지 않음 seed=' + seed); break; }
  games++; if (st.result.draw) draws++; else { wins[st.result.winner]++; maxPts = Math.max(maxPts, st.result.points); }
}
console.log(`시뮬레이션 ${games}판: 나가리 ${draws}, 승 ${wins.join('/')}, 최대 ${maxPts}점, 특수 ${JSON.stringify(sp)}`);
ok(games === 3000, '3000판 모두 끝까지 진행'); ok(draws < games * 0.6, '나가리가 너무 많지 않음');
// 5-2) 3인 시뮬레이션: 카드 보존·끝까지 진행·정산 합계
{
  const tot3 = s => [...s.hands.flat(), ...s.field, ...s.deck, ...s.cap.flat()];
  let g3n = 0, d3 = 0, w3 = [0, 0, 0], sp3 = {}, flips = 0, maxP = 0, gob = 0, badSum = 0, shortDeck = 0;
  for (let seed = 1; seed <= 3000; seed++) {
    const st = G.newGame(seed, seed % 3, 3); let k = 0;
    try {
      while (st.phase !== 'end' && k++ < 600) {
        const a = G.aiStep(st); if (a.t === 'flip') flips++;
        G.act(st, a);
        if (st.last && st.last.turnNo !== st.turnNo && !st.ctx && st.last.sp) { st.last.sp.forEach(q => sp3[q] = (sp3[q] || 0) + 1); st.last.turnNo = st.turnNo; }
        if (!st.ctx && new Set(tot3(st)).size !== 48) { bad++; console.log('[실패] 3인 카드 보존 깨짐 seed=' + seed); break; }
      }
    } catch (e) { bad++; console.log('[실패] 3인 예외 seed=' + seed + ' ' + e.message); break; }
    if (st.phase !== 'end') { bad++; console.log('[실패] 3인 끝나지 않음 seed=' + seed); break; }
    g3n++; if (st.result.draw) d3++; else {
      w3[st.result.winner]++; maxP = Math.max(maxP, st.result.points);
      const sum = st.result.per.reduce((t, x) => t + x.pay, 0); if (sum !== st.result.points || st.result.per.length !== 2) badSum++;
      if (st.result.per.some(x => x.mult.includes('고박(독박)'))) gob++;
    }
  }
  console.log(`3인 시뮬레이션 ${g3n}판: 나가리 ${d3}, 승 ${w3.join('/')}, 최대 ${maxP}점, 손패 없는 차례 ${flips}번, 독박 ${gob}번, 특수 ${JSON.stringify(sp3)}`);
  ok(g3n === 3000, '3인 3000판 모두 끝까지 진행'); ok(badSum === 0, '3인 정산: 진 사람이 낼 몫의 합 = 이긴 사람이 받는 점수'); ok(d3 < g3n * 0.6, '3인 나가리가 너무 많지 않음');
  ok(flips > 0 && (sp3['폭탄'] || 0) > 0 && (sp3['흔들기'] || 0) > 0, '3인에서도 폭탄·흔들기·손패 없는 차례가 실제로 나온다');
}
console.log(bad ? `실패 ${bad}건` : `모두 통과 (${n}개 검사)`); process.exit(bad ? 1 : 0);
