// 백업 알림 검사: node bk.js  (저장소 루트를 http://localhost:8765 로 먼저 띄워 둔다: py -m http.server 8765)
const { chromium } = require('playwright');
const U = 'http://localhost:8765/', DAY = 86400000; let bad = 0;
const ok = (c, m) => { console.log((c ? '[통과] ' : '[실패] ') + m); if (!c) bad++; };
(async () => {
  const b = await chromium.launch();
  const mk = async (init, arg) => { const c = await b.newContext({ viewport: { width: 360, height: 800 } }); const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e))); await p.addInitScript(init, arg); p.errs = errs; return p; };
  // 1) 백업 화면: 처음 상태
  let p = await mk(() => { if (!localStorage.getItem('__seed')) { localStorage.setItem('__seed', '1'); localStorage.setItem('allowance-v1', '[1,2]'); } });
  await p.goto(U + 'backup.html'); await p.waitForSelector('#stat-h');
  ok((await p.textContent('#stat-h')).includes('❗'), '처음에는 ❗ 백업한 적 없음');
  ok(await p.$eval('#every button[data-d="30"]', e => e.classList.contains('on')), '기본 주기는 한 달');
  // 2) 주기 변경 저장
  await p.click('#every button[data-d="14"]'); ok(await p.evaluate(() => localStorage.getItem('fg-backup-every')) === '14', '2주 선택이 저장됨');
  // 3) 백업(파일 저장) 후 상태
  await p.evaluate(() => { document.getElementById('dl').click(); }); await p.waitForTimeout(300);
  ok((await p.textContent('#stat-h')).includes('✅') && (await p.textContent('#stat-h')).includes('오늘'), '저장 후 ✅ 오늘');
  ok((await p.textContent('#stat-c')).includes('바뀐 기록이 없어요'), '저장 직후 바뀐 기록 없음');
  // 4) 기록을 바꾸고 다시 열기
  await p.evaluate(() => localStorage.setItem('allowance-v1', '[1,2,3,4]')); await p.reload(); await p.waitForSelector('#stat-c');
  ok((await p.textContent('#stat-c')).includes('1종'), '기록을 바꾸면 바뀐 기록 1종');
  // 5) 백업 파일에 메타 키가 안 들어감
  const keys = await p.evaluate(() => Object.keys(snapshot().data));
  ok(!keys.some(k => k.startsWith('fg-')) && keys.includes('allowance-v1'), '백업 파일에 fg-* 키가 없고 기록은 있음');
  ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '360px 가로 넘침 없음');
  ok(p.errs.length === 0, '오류 없음 ' + p.errs.join('|'));
  // 6) 시작 화면 알림 조건
  const home = async (st) => { const q = await mk((st) => { if (!localStorage.getItem('__seed')) { localStorage.setItem('__seed', '1'); for (const k in st) localStorage.setItem(k, st[k]); } }, st); await q.goto(U + 'index.html'); await q.waitForTimeout(700); const shown = await q.evaluate(() => [...document.querySelectorAll('div')].some(d => d.textContent.includes('기록 백업을 해 둘까요'))); const txt = shown ? await q.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.includes('기록 백업을 해 둘까요')).pop().textContent) : ''; const e = q.errs.length; await q.context().close(); return { shown, txt, e }; };
  const now = Date.now(), old = now - 40 * DAY, base = { 'allowance-v1': '[1,2,3]', 'fg-first-seen': String(old - DAY), 'fg-backup-last': String(old) };
  let r = await home({ ...base, 'fg-backup-sig': JSON.stringify({ 'allowance-v1': 7, '__seed': 1 }) }); ok(!r.shown, '40일 지났어도 바뀐 기록이 없으면 알림 없음');
  r = await home({ ...base, 'fg-backup-sig': JSON.stringify({ 'allowance-v1': 1, '__seed': 1 }) }); ok(r.shown && r.txt.includes('바뀐 기록 1종'), '바뀐 기록이 있으면 알림(바뀐 기록 1종)');
  r = await home({ ...base, 'fg-backup-sig': JSON.stringify({ 'allowance-v1': 1, '__seed': 1 }), 'fg-backup-every': '0' }); ok(!r.shown, '끄기면 알림 없음');
  r = await home({ ...base, 'fg-backup-sig': JSON.stringify({ 'allowance-v1': 1, '__seed': 1 }), 'fg-backup-every': '90' }); ok(!r.shown, '석 달 주기면 40일에는 알림 없음');
  r = await home({ ...base, 'fg-backup-sig': JSON.stringify({ 'allowance-v1': 1, '__seed': 1 }), 'fg-backup-every': '14' }); ok(r.shown, '2주 주기면 40일에 알림');
  r = await home({ ...base }); ok(r.shown, '요약이 없는 예전 백업은 기간만 보고 알림(기존 동작 유지)');
  r = await home({ 'allowance-v1': '[1]', 'fg-first-seen': String(now - 8 * DAY) }); ok(r.shown && r.txt.includes('아직 백업이 없어요'), '백업이 한 번도 없고 8일 지나면 알림');
  r = await home({ 'allowance-v1': '[1]', 'fg-first-seen': String(now - 8 * DAY), 'fg-backup-every': '0' }); ok(!r.shown, '백업 없어도 끄기면 알림 없음');
  await b.close(); console.log(bad ? '실패 ' + bad + '건' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
