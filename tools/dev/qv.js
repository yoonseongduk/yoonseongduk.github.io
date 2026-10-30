const REPO = require('path').resolve(__dirname, '..', '..');
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
 for (const f of process.argv.slice(2)) {
  const p = await b.newPage({ viewport: { width: 400, height: 900 } }); p.on('pageerror', e => errs.push(f+': '+e.message));
  await p.goto(`file://${REPO}/${f}.html`); await p.waitForTimeout(150);
  const r = await p.evaluate(() => { let bad=0, und=0; for(let t=0;t<300;t++){ start(); for(const q of qs){ const o=q.opts; if(new Set(o).size!==o.length||o.length<4||!o.includes(q.d[1])) bad++; if(o.some(x=>!x||String(x).includes('undefined'))) und++; } } return { n:D.length, 보기오류:bad, undefined:und, 이상한항목:D.filter(d=>!d[0]||!d[1]).length }; });
  for (let k=0;k<10;k++){ const a=await p.evaluate(()=>qs[i].opts.indexOf(qs[i].d[1])); await p.locator(`[data-k="${a}"]`).click(); await p.click('#next'); }
  console.log(f, JSON.stringify(r), '|', (await p.locator('#res b').textContent()).trim(), 'ov', await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)); await p.close(); }
 console.log('오류', JSON.stringify(errs)); await b.close(); })();
