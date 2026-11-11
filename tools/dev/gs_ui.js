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
  await p.screenshot({ path: 'gs_shot1.png', fullPage: true });
  let turns = 0, shot = false;
  for (let i = 0; i < 600; i++) {
    const end = await p.$eval('#result', e => !e.hidden); if (end) break;
    if (await p.$('#bstop')) { await p.click(i % 2 ? '#bstop' : '#bgo').catch(() => {}); await p.waitForTimeout(300); continue; }
    const pick = await p.$('#field .gc.pick'); if (pick) { await pick.click(); await p.waitForTimeout(300); continue; }
    const can = await p.$('#hand .gc.can');
    if (can) { await can.click(); turns++; await p.waitForTimeout(250); if (turns === 3 && !shot) { shot = true; await p.screenshot({ path: 'gs_shot2.png', fullPage: true }); } continue; }
    await p.waitForTimeout(300);
  }
  ok(await p.$eval('#result', e => !e.hidden), '한 판이 끝까지 진행되어 결과가 나온다 (내가 낸 횟수 ' + turns + ')');
  const txt = await p.$eval('#result', e => e.innerText); ok(/승리|아쉬워요|나가리/.test(txt), '결과 문구가 보인다: ' + txt.split('\n')[0]);
  await p.screenshot({ path: 'gs_shot3.png', fullPage: true });
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '360px 가로 넘침 없음(결과)');
  ok(await p.evaluate(() => { const s = JSON.parse(localStorage.getItem('go-stop-stats-v1')); return !!s && s.w + s.l + s.d === 1; }), '전적이 저장된다');
  const before = await p.evaluate(() => fgPerson.points()); await p.evaluate(() => fgPerson.grant(14, '맞고 승리')); const after = await p.evaluate(() => fgPerson.points());
  ok(after - before === 14, '맞고 승리 포인트 +14 연결 (' + before + '→' + after + ')');
  await p.evaluate(() => fgPerson.grant(99, '맞고 승리')); ok((await p.evaluate(() => fgPerson.points())) - after === 50, '한 판 최대 50p');
  await p.click('#again'); await p.waitForTimeout(500); ok((await p.$$('#hand .gc')).length === 10 && await p.$eval('#result', e => e.hidden), '한 판 더: 새 판이 시작된다');
  ok(errs.length === 0, '오류 없음 ' + errs.join(' | ').slice(0, 200));
  await b.close(); console.log(bad ? '실패 ' + bad + '건' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
