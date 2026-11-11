// 사람별 기록·포인트 검사: node pp.js  (저장소 루트를 py -m http.server 8765 로 먼저 띄운다)
const { chromium } = require('playwright');
const U = 'http://localhost:8765/'; let bad = 0;
const ok = (c, m) => { console.log((c ? '[통과] ' : '[실패] ') + m); if (!c) bad++; };
(async () => {
  const b = await chromium.launch();
  const open = async (path, seed) => { const c = await b.newContext({ viewport: { width: 360, height: 800 } }); const p = await c.newPage(); p.errs = []; p.on('pageerror', e => p.errs.push(String(e)));
    await p.addInitScript((s) => { if (!sessionStorage.getItem('__s')) { sessionStorage.setItem('__s', '1'); for (const k in s) localStorage.setItem(k, s[k]); } }, seed || {}); await p.goto(U + path); await p.waitForTimeout(400); return p; };
  const base = { 'family-me-v1': '"아빠"', 'family-members-v1': '["아빠","엄마"]' };
  // 1) 사람별 기록 분리
  let p = await open('click-speed.html', { ...base, 'clickspeed-best-v1': '{"10":5}' });
  ok(await p.evaluate(() => localStorage.getItem('clickspeed-best-v1')) === '{"10":5}', '주인(아빠)은 예전 키 그대로 읽는다');
  await p.evaluate(() => localStorage.setItem('fg-player-v1', '엄마')); await p.reload(); await p.waitForTimeout(300);
  ok(await p.evaluate(() => localStorage.getItem('clickspeed-best-v1')) === null, '엄마로 바꾸면 아빠 기록이 안 보인다');
  await p.evaluate(() => localStorage.setItem('clickspeed-best-v1', '{"10":9}'));
  const raw = await p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith('clickspeed-best')).sort().join(','));
  ok(raw === 'clickspeed-best-v1,clickspeed-best-v1::엄마', '엄마 기록은 "키::엄마"로 따로 저장된다 ' + raw);
  ok(await p.evaluate(() => localStorage.getItem('clickspeed-best-v1')) === '{"10":9}', '엄마 화면에서는 엄마 기록이 읽힌다');
  // 2) 백업 화면은 변환 없이 원본 키를 본다
  await p.goto(U + 'backup.html'); await p.waitForTimeout(400);
  const snap = await p.evaluate(() => snapshot().data);
  ok(snap['clickspeed-best-v1'] === '{"10":5}' && snap['clickspeed-best-v1::엄마'] === '{"10":9}', '백업 파일에 아빠·엄마 기록이 각각 들어간다');
  ok(await p.evaluate(() => nameOf('clickspeed-best-v1::엄마')) === '클릭 속도 테스트 · 엄마', '백업 화면 이름 표시에 사람 이름이 붙는다');
  ok(await p.evaluate(() => (JSON.parse(localStorage.getItem('fg-points-v1') || 'null') === null)), '백업 화면은 포인트를 주지 않는다');
  await p.context().close();
  // 3) 포인트: 기본·처음·연속·최고 기록·이김, 일일 상한
  p = await open('click-speed.html', base);
  ok((await p.$('#fg-who')) !== null && (await p.textContent('#fg-who')).includes('아빠'), '게임 화면 위쪽에 사람 칩이 보인다');
  await p.mouse.click(180, 400); await p.waitForTimeout(11500);
  let pt = await p.evaluate(() => JSON.parse(localStorage.getItem('fg-points-v1')));
  ok(pt && pt.p['아빠'] && pt.p['아빠'].total === 65, '기본 10 + 처음 20 + 연속 5 + (클릭 속도 게임이 첫 기록을 직접 저장해) 최고 기록 30 = 65 (' + (pt && pt.p['아빠'] && pt.p['아빠'].total) + ')');
  await p.evaluate(() => localStorage.setItem('clickspeed-best-v1', '{"10":99}')); await p.waitForTimeout(500);
  pt = await p.evaluate(() => JSON.parse(localStorage.getItem('fg-points-v1')));
  ok(pt.p['아빠'].total === 65, '한 번 연 화면에서 최고 기록 가산은 한 번만 (' + pt.p['아빠'].total + ')');
  await p.evaluate(() => { const d = document.createElement('div'); d.textContent = '🎉 성공했어요!'; document.body.appendChild(d); }); await p.waitForTimeout(500);
  pt = await p.evaluate(() => JSON.parse(localStorage.getItem('fg-points-v1')));
  ok(pt.p['아빠'].total === 85, '이겼어요 글귀가 나오면 +20 (' + pt.p['아빠'].total + ')');
  ok(p.errs.length === 0, '오류 없음 ' + p.errs.join('|'));
  // 4) 칩으로 사람 바꾸기 + 시작 화면 칩
  await p.click('#fg-who'); await p.waitForSelector('#fg-whomenu');
  const items = await p.$$eval('#fg-whomenu button', bs => bs.map(x => x.textContent));
  ok(items.some(t => t.includes('엄마')) && items.some(t => t.includes('포인트 보기')), '메뉴에 가족과 포인트 보기가 있다');
  p.once('dialog', d => d.accept()); await p.click('#fg-whomenu button:has-text("엄마")'); await p.waitForTimeout(800);
  ok(await p.evaluate(() => localStorage.getItem('fg-player-v1')) === '엄마' && (await p.textContent('#fg-who')).includes('엄마'), '칩에서 엄마를 고르면 바뀌고 새로 열린다');
  await p.goto(U + 'index.html'); await p.waitForTimeout(500);
  ok((await p.$('#fg-who')) !== null, '시작 화면에도 칩이 있다');
  await p.goto(U + 'family-points.html'); await p.waitForTimeout(600);
  const rk = await p.textContent('#rank'); ok(rk.includes('아빠') && rk.includes('85p'), '포인트 화면에 순위가 보인다');
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '포인트 화면 360px 가로 넘침 없음');
  await p.context().close();
  // 5) 게임이 아닌 화면은 포인트가 없다 / 소유자 미지정이면 변환 없음
  p = await open('allowance-book.html', {}); await p.mouse.click(100, 300); await p.waitForTimeout(11500);
  ok(await p.evaluate(() => localStorage.getItem('fg-points-v1')) === null, '도구 화면(용돈 기입장)은 포인트를 주지 않는다');
  await p.context().close();
  await b.close(); console.log(bad ? '실패 ' + bad + '건' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
