// 맞고 화면 검사: node gs_ui.js  (저장소 루트를 py -m http.server 8765 로 먼저 띄운다)
const { chromium } = require('playwright');
const U = 'http://localhost:8765/'; let bad = 0;
const ok = (c, m) => { console.log((c ? '[통과] ' : '[실패] ') + m); if (!c) bad++; };
(async () => {
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 360, height: 800 } }); const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.addInitScript(() => { if (!sessionStorage.getItem('s')) { sessionStorage.setItem('s', '1'); localStorage.setItem('family-me-v1', '"아빠"'); } });
  await p.goto(U + 'go-stop.html'); await p.waitForTimeout(600);
  ok((await p.$$('#hand .gc')).length === 10, '손패 10장이 보인다');
  ok((await p.$$eval('#field .gc', e => e.length)) === 8, '바닥 8장이 보인다');
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '360px 가로 넘침 없음(시작)');
  await p.screenshot({ path: 'gs_shot1.png', fullPage: false });
  ok((await p.$$eval('#hand .gc.best', e => e.length)) === 1, '내 차례에 추천 패(⭐)가 1장 표시된다');
  ok((await p.$$eval('#hand .gc.match, #hand .gc.best', e => e.length)) >= 1, '짝이 맞는 패 표시가 있다');
  ok(await p.evaluate(async () => { const r = await Promise.all(GoStopArt.all().map(u => fetch(u).then(x => x.ok))); return r.length === 48 && r.every(Boolean); }), '화투 그림 48장이 모두 불러와진다');
  await p.click('#hintOn'); ok((await p.$$eval('#hand .gc.best, #hand .gc.match', e => e.length)) === 0, '힌트를 끄면 표시가 사라진다'); await p.click('#hintOn');
  let sawNew = false; const sawGuide = new Set(), sawStep = new Set();
  let turns = 0, shot = false;
  for (let i = 0; i < 600; i++) {
    const end = await p.$eval('#result', e => !e.hidden); if (end) break;
    if (!sawNew && await p.$('#cap .gc.new')) sawNew = true;
    sawGuide.add(await p.$eval('#next', e => e.innerText)); sawStep.add(await p.$eval('#next .steps .on', e => e.innerText).catch(() => 'none'));
    if (await p.$('#bstop')) { await p.click(i % 2 ? '#bstop' : '#bgo').catch(() => {}); await p.waitForTimeout(300); continue; }
    if (await p.$('#bq1')) { await p.click(i % 2 ? '#bq1' : '#bq0').catch(() => {}); await p.waitForTimeout(300); continue; }
    if (await p.$('#bflip')) { await p.click('#bflip').catch(() => {}); await p.waitForTimeout(300); continue; }
    const pick = await p.$('#field .gc.pick'); if (pick) { await pick.click(); await p.waitForTimeout(300); continue; }
    const can = await p.$('#hand .gc.can');
    if (can) { await can.click(); turns++; await p.waitForTimeout(250); if (turns === 3 && !shot) { shot = true; await p.screenshot({ path: 'gs_shot2.png', fullPage: false }); } continue; }
    await p.waitForTimeout(300);
  }
  ok(sawNew, '방금 가져온 패가 주황 테두리(new)로 표시된다');
  ok(sawStep.size >= 2 && [...sawStep].some(t => /손패 내기/.test(t)) && [...sawStep].some(t => /컴퓨터 차례/.test(t)), '진행하는 동안 남은 단계의 현재 칸이 바뀐다: ' + [...sawStep].join(' / '));
  const stepsAt = await p.evaluate(() => { const old = S, r = {}; const t = (k, o) => { S = Object.assign({}, old, o); r[k] = stepNo(); }; const h1 = [[1], ...old.hands.slice(1)]; t('hand', { phase: 'hand', turn: 0, pend: null, hands: h1 }); t('shake', { phase: 'shake', turn: 0, pend: { month: 1 }, hands: h1 }); t('flipOnly', { phase: 'hand', turn: 0, pend: null, hands: [[], ...old.hands.slice(1)] }); t('gukjin', { phase: 'gukjin', turn: 0, pend: { type: 'gukjin' } }); t('pickHand', { phase: 'pick', turn: 0, pend: { stage: 'hand', ids: [] } }); t('pickFlip', { phase: 'pick', turn: 0, pend: { stage: 'flip', ids: [] } }); t('gostop', { phase: 'gostop', turn: 0, pend: { score: 7 } }); t('cpu', { phase: 'hand', turn: 1, pend: null }); t('end', { phase: 'end' }); S = old; return r; });
  ok(JSON.stringify(Object.entries(stepsAt).sort()) === JSON.stringify(Object.entries({ hand: 0, shake: 0, flipOnly: 2, pickHand: 1, pickFlip: 3, gukjin: 4, gostop: 5, cpu: 6, end: 7 }).sort()), '상황별 현재 단계 번호가 맞다: ' + JSON.stringify(stepsAt));
  ok(sawGuide.size >= 3 && [...sawGuide].some(t => /내 차례예요/.test(t)) && [...sawGuide].some(t => /컴퓨터 차례예요/.test(t)), '다음에 할 일 안내가 상황마다 바뀐다: ' + [...sawGuide].map(t => t.split('\n')[0].slice(0, 22)).join(' / '));
  ok(await p.$eval('#result', e => !e.hidden), '한 판이 끝까지 진행되어 결과가 나온다 (내가 낸 횟수 ' + turns + ')');
  const txt = await p.$eval('#result', e => e.innerText); ok(/승리|아쉬워요|나가리/.test(txt), '결과 문구가 보인다: ' + txt.split('\n')[0]);
  await p.screenshot({ path: 'gs_shot3.png', fullPage: true });
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '360px 가로 넘침 없음(결과)');
  ok(await p.evaluate(() => { const s = JSON.parse(localStorage.getItem('go-stop-stats-v1')); return !!s && s.w + s.l + s.d === 1; }), '전적이 저장된다');
  const before = await p.evaluate(() => fgPerson.points()); await p.evaluate(() => fgPerson.grant(14, '맞고 승리')); const after = await p.evaluate(() => fgPerson.points());
  ok(after - before === 14, '맞고 승리 포인트 +14 연결 (' + before + '→' + after + ')');
  await p.evaluate(() => fgPerson.grant(99, '맞고 승리')); ok((await p.evaluate(() => fgPerson.points())) - after === 99, '맞고는 한 판 포인트 상한이 없다(+99)');
  await p.evaluate(() => { for (let i = 0; i < 5; i++) fgPerson.grant(7, '맞고 승리'); }); ok((await p.evaluate(() => fgPerson.points())) - after === 99 + 35, '맞고는 하루 횟수 제한이 없다(연속 5번 +35)');
  await p.waitForTimeout(300); const gt = await p.$eval('#fg-gpt', e => e.textContent), wt = await p.$eval('#fg-who', e => e.textContent);
  ok(/제한 없음/.test(gt) && /\d+p/.test(gt), '이 게임 포인트 표시(제한 없음): ' + gt); ok(/⭐ \d+p/.test(wt), '내 포인트 칩: ' + wt);
  await p.click('#again'); await p.waitForTimeout(500); ok((await p.$$('#hand .gc')).length === 10 && await p.$eval('#result', e => e.hidden), '한 판 더: 새 판이 시작된다');
  // ── 3인 고스톱: 인원을 바꾸면 새 판이 3인으로 시작하고, 컴퓨터 두 명과 끝까지 진행된다
  await p.selectOption('#modeSel', '3'); await p.waitForTimeout(600);
  ok((await p.$$('#hand .gc')).length === 7 && (await p.$$eval('#field .gc', e => e.length)) === 6, '3인: 손패 7장·바닥 6장으로 시작한다');
  ok((await p.$$eval('#bar .bs', e => e.length)) === 3 && (await p.$$eval('#cap .ch', e => e.length)) === 3, '3인: 점수판과 획득 패 표가 3명으로 보인다 (컴퓨터1·컴퓨터2·나)');
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '3인 360px 가로 넘침 없음(시작)');
  await p.screenshot({ path: 'gs_shot4.png', fullPage: false });
  ok(await p.evaluate(() => JSON.parse(localStorage.getItem('go-stop-stats-v1')).mode === 3), '인원 선택(3인)이 저장된다');
  const saw3 = { shake: 0, bomb: 0, gukjin: 0, flip: 0, who: new Set() }; let t3 = 0;
  for (let i = 0; i < 900; i++) {
    if (await p.$eval('#result', e => !e.hidden)) break;
    saw3.who.add(await p.$eval('#bar .bs.on .bn', e => e.textContent.trim()).catch(() => ''));
    if (await p.$('#bstop')) { await p.click(i % 2 ? '#bstop' : '#bgo').catch(() => {}); await p.waitForTimeout(250); continue; }
    if (await p.$('#bq1')) { const t = await p.$eval('#bq1', e => e.textContent); if (/흔들기/.test(t)) saw3.shake++; else if (/폭탄/.test(t)) saw3.bomb++; else saw3.gukjin++; await p.click('#bq1').catch(() => {}); await p.waitForTimeout(250); continue; }
    if (await p.$('#bflip')) { saw3.flip++; await p.click('#bflip').catch(() => {}); await p.waitForTimeout(250); continue; }
    const pk = await p.$('#field .gc.pick'); if (pk) { await pk.click(); await p.waitForTimeout(250); continue; }
    const cn = await p.$('#hand .gc.can'); if (cn) { await cn.click(); t3++; await p.waitForTimeout(200); continue; }
    await p.waitForTimeout(250);
  }
  ok(await p.$eval('#result', e => !e.hidden), '3인 한 판이 끝까지 진행되어 결과가 나온다 (내가 낸 횟수 ' + t3 + ', 흔들기 ' + saw3.shake + '·폭탄 ' + saw3.bomb + '·국진 ' + saw3.gukjin + '·더미 뒤집기 ' + saw3.flip + ')');
  ok([...saw3.who].some(t => /컴퓨터1/.test(t)) && [...saw3.who].some(t => /컴퓨터2/.test(t)), '3인: 컴퓨터1·컴퓨터2가 차례대로 둔다');
  const txt3 = await p.$eval('#result', e => e.innerText); ok(/승리|아쉬워요|나가리/.test(txt3) && (/나가리/.test(txt3) || /가 낼 점수/.test(txt3)), '3인 결과: 진 사람마다 낼 점수와 합계가 보인다: ' + txt3.split(String.fromCharCode(10)).slice(0, 4).join(' / '));
  await p.screenshot({ path: 'gs_shot5.png', fullPage: false });
  // ── 선택 질문 화면(흔들기·폭탄·손패 없는 차례): 상황을 직접 만들어 버튼이 뜨고 눌러지는지 확인
  const setup = (hand, field, deck) => p.evaluate(([h, f, d]) => { clearTimeout(timer); S = GS.newGame(5, 0, 3); S.hands[0] = h.slice(); S.field = f.slice(); S.deck = d.slice(); S.cap = [[], [], []]; S.turn = 0; S.phase = 'hand'; S.pend = null; S.ctx = null; msg = ''; lastTurnNo = S.turnNo; render(); }, [hand, field, deck]);
  await setup([0, 1, 2, 40, 41, 44, 45], [8, 12], [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]);
  await p.click('#hand .gc[data-id="0"]'); await p.waitForTimeout(150);
  ok(/흔들기/.test(await p.$eval('#bq1', e => e.textContent)) && /흔들기를 할까요/.test(await p.$eval('#next', e => e.innerText)), '손패 같은 달 3장(바닥에 없음): 「흔들기」 버튼과 안내가 뜬다');
  ok((await p.$eval('#next .steps .on', e => e.innerText)).includes('손패 내기'), '흔들기 질문 중에는 ① 손패 내기 단계가 강조된다');
  await p.click('#bq1'); await p.waitForTimeout(250);
  ok(await p.evaluate(() => S.shake[0] === 1 && S.last && S.last.sp.includes('흔들기')) && /흔들기/.test(await p.$eval('#msg', e => e.textContent)), '흔들기를 누르면 적용되고 안내 메시지에 표시된다');
  ok(await p.$eval('#bar .bs:last-child .bm', e => /🎲×1/.test(e.textContent)), '점수판에 내 흔들기(🎲×1)가 표시된다');
  await setup([0, 1, 2, 40, 41, 44, 45], [3, 8], [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]);
  await p.click('#hand .gc[data-id="0"]'); await p.waitForTimeout(150);
  ok(/폭탄/.test(await p.$eval('#bq1', e => e.textContent)) && /폭탄을 낼까요/.test(await p.$eval('#next', e => e.innerText)), '손패 3장 + 바닥 1장: 「폭탄」 버튼과 안내가 뜬다');
  await p.click('#bq1'); await p.waitForTimeout(250);
  ok(await p.evaluate(() => S.bomb[0] === 1 && S.hands[0].length === 4) && /폭탄/.test(await p.$eval('#msg', e => e.textContent)), '폭탄을 누르면 3장이 한꺼번에 나가고 메시지에 표시된다');
  await setup([], [8], [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]);
  ok((await p.$$('#hand .gc')).length === 0 && !!(await p.$('#bflip')) && /더미 뒤집기/.test(await p.$eval('#next', e => e.innerText)), '손패가 없으면 「더미 뒤집기」 버튼과 안내가 뜬다');
  ok((await p.$eval('#next .steps .on', e => e.innerText)).includes('더미 뒤집기'), '손패 없는 차례에는 ③ 더미 뒤집기 단계가 강조된다');
  await p.click('#bflip'); await p.waitForTimeout(250);
  ok(await p.evaluate(() => S.last && S.last.hand === null && S.deck.length < 14) && /더미만 뒤집어/.test(await p.$eval('#msg', e => e.textContent)), '「더미 뒤집기」를 누르면 더미만 뒤집고 메시지가 나온다');
  await p.evaluate(() => clearTimeout(timer));
  await p.selectOption('#modeSel', '2'); await p.waitForTimeout(500); ok((await p.$$('#hand .gc')).length === 10, '2인으로 되돌리면 손패 10장으로 시작한다');
  ok(errs.length === 0, '오류 없음 ' + errs.join(' | ').slice(0, 200));
  await b.close(); console.log(bad ? '실패 ' + bad + '건' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
