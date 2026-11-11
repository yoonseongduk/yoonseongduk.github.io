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
console.log(bad ? `실패 ${bad}건` : `모두 통과 (${n}개 검사)`); process.exit(bad ? 1 : 0);
