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
    const pick = await p.$('#field .gc.pick'); if (pick) { await pick.click(); await p.waitForTimeout(300); continue; }
    const can = await p.$('#hand .gc.can');
    if (can) { await can.click(); turns++; await p.waitForTimeout(250); if (turns === 3 && !shot) { shot = true; await p.screenshot({ path: 'gs_shot2.png', fullPage: false }); } continue; }
    await p.waitForTimeout(300);
  }
  ok(sawNew, '방금 가져온 패가 주황 테두리(new)로 표시된다');
  ok(sawStep.size >= 2 && [...sawStep].some(t => /손패 내기/.test(t)) && [...sawStep].some(t => /컴퓨터 차례/.test(t)), '진행하는 동안 남은 단계의 현재 칸이 바뀐다: ' + [...sawStep].join(' / '));
  const stepsAt = await p.evaluate(() => { const old = S, r = {}; const t = (k, o) => { S = Object.assign({}, old, o); r[k] = stepNo(); }; t('hand', { phase: 'hand', turn: 0, pend: null }); t('pickHand', { phase: 'pick', turn: 0, pend: { stage: 'hand', ids: [] } }); t('pickFlip', { phase: 'pick', turn: 0, pend: { stage: 'flip', ids: [] } }); t('gostop', { phase: 'gostop', turn: 0, pend: { score: 7 } }); t('cpu', { phase: 'hand', turn: 1, pend: null }); t('end', { phase: 'end' }); S = old; return r; });
  ok(JSON.stringify(stepsAt) === JSON.stringify({ hand: 0, pickHand: 1, pickFlip: 3, gostop: 4, cpu: 5, end: 6 }), '상황별 현재 단계 번호가 맞다: ' + JSON.stringify(stepsAt));
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
  ok(errs.length === 0, '오류 없음 ' + errs.join(' | ').slice(0, 200));
  await b.close(); console.log(bad ? '실패 ' + bad + '건' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
