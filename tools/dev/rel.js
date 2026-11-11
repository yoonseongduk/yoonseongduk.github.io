// 릴리스 노트 표시 검사: node rel.js  (저장소 루트를 py -m http.server 8765 로 먼저 띄운다)
const { chromium } = require('playwright'); const fs = require('fs');
const U = 'http://localhost:8765/'; let bad = 0;
const ok = (c, m) => { console.log((c ? '[통과] ' : '[실패] ') + m); if (!c) bad++; };
(async () => {
  const notes = JSON.parse(fs.readFileSync(__dirname + '/../../data/release-notes.json', 'utf8'));
  ok(Array.isArray(notes) && notes.length > 0 && notes.every(x => x.ver && x.date && x.title && Array.isArray(x.items) && x.items.length), '릴리스 노트 파일 형식이 맞다 (' + notes.length + '건)');
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 360, height: 800 }, serviceWorkers: 'allow' }); const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(U + 'index.html'); await p.waitForFunction(() => document.getElementById('pwaVer') && document.getElementById('pwaVer').textContent.includes('릴리스'), null, { timeout: 15000 }).catch(() => {});
  const ver = await p.textContent('#pwaVer'); ok(ver.includes('릴리스 ' + notes[0].ver), '버전 줄에 현재 릴리스 번호가 보인다: ' + ver);
  ok(await p.$eval('#pwaRel', e => !e.hidden), '업데이트 내용(릴리스 노트)이 보인다');
  await p.click('#pwaRel summary'); const body = await p.textContent('#pwaRelBody'); ok(body.includes(notes[0].title) && body.includes(notes[0].items[0]), '펼치면 최신 릴리스의 제목과 바뀐 점이 있다');
  ok((await p.$$('#pwaRelBody .rv')).length === Math.min(6, notes.length), '최근 6건까지 보인다');
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '360px 가로 넘침 없음');
  ok(errs.length === 0, '오류 없음 ' + errs.join('|'));
  await b.close(); console.log(bad ? '실패 ' + bad + '건' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
