// 화투 그림 48장을 한 장에 모아 캡처하고 모두 불러와지는지 확인한다: node art_gallery.js  (저장소 루트를 py -m http.server 8765 로 먼저 띄운다)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 900, height: 900 } }); const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('requestfailed', r => errs.push('실패 ' + r.url()));
  await p.goto('http://localhost:8765/licenses.html');
  await p.addScriptTag({ url: 'http://localhost:8765/gostop-core.js' }); await p.addScriptTag({ url: 'http://localhost:8765/gostop-art.js' });
  await p.evaluate(() => { let h = ''; for (let i = 0; i < 48; i++) { const t = GoStop.info(i); h += `<div style="text-align:center;font:11px sans-serif;color:#222"><div style="height:130px">${GoStopArt.img(i).replace('<img ', '<img style="height:130px" ')}</div>${i}: ${t.month}월 ${t.type}${t.sub ? '/' + t.sub : ''}${t.pi === 2 ? ' 쌍피' : ''}</div>`; } document.body.innerHTML = '<div style="background:#eee;padding:8px;display:grid;grid-template-columns:repeat(12,1fr);gap:6px">' + h + '</div>'; });
  await p.waitForTimeout(1500);
  const bad = await p.evaluate(() => [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src));
  console.log('그림 ' + (48 - bad.length) + '/48 불러옴', bad.length ? '실패: ' + bad.join(',') : '', errs.join('|'));
  await p.screenshot({ path: 'art_gallery.png', fullPage: true }); await b.close(); process.exit(bad.length || errs.length ? 1 : 0);
})();
