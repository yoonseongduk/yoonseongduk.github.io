// 화투 그림 48장을 한 장에 모아 캡처한다: node art_gallery.js  (저장소 루트를 py -m http.server 8765 로 먼저 띄운다)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 900, height: 700 } }); const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://localhost:8765/gallery_blank.html').catch(() => {});
  await p.setContent('<meta charset=utf-8><body style="margin:8px;background:#f5efe6;font-family:sans-serif"><div id=g style="display:grid;grid-template-columns:repeat(12,1fr);gap:6px"></div>');
  await p.addScriptTag({ url: 'http://localhost:8765/gostop-core.js' }).catch(() => {}); await p.addScriptTag({ url: 'http://localhost:8765/gostop-art.js' }).catch(() => {});
  const r = await p.evaluate(() => { if (!window.GoStop || !window.GoStopArt) return 'no-lib'; let h = ''; for (let i = 0; i < 48; i++) { const t = GoStop.info(i); h += `<div style="background:${t.type==='gwang'?'#fff1b8':t.type==='yeol'?'#ffe9d6':t.type==='ddi'?'#fff':'#eef0f2'};border:1.5px solid #999;border-radius:8px;padding:2px;text-align:center;font-size:10px"><div style="width:100%;aspect-ratio:1">${GoStopArt.svg(i)}</div>${t.month}월 ${t.type}${t.sub?'/'+t.sub:''}</div>`; } document.getElementById('g').innerHTML = h; return 'ok'; });
  console.log(r, errs.join('|')); await p.screenshot({ path: 'art_gallery.png', fullPage: true }); await b.close();
})();
