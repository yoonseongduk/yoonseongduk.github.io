const REPO = require('path').resolve(__dirname, '..', '..');
const { chromium } = require('playwright'); const fs=require('fs');
(async () => { const b = await chromium.launch(); const files=fs.readdirSync(REPO).filter(f=>f.endsWith('.html')); const bad=[]; let ovf=[];
 for (const f of files) { const p = await b.newPage({ viewport: { width: 360, height: 800 } }); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); await p.goto(`file://${REPO}/${f}`); await p.waitForTimeout(120); if(errs.length) bad.push(f+': '+errs[0]); if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)) ovf.push(f); await p.close(); }
 console.log('검사', files.length, '| 오류 있는 페이지:', bad.length?bad.join(' ; '):'없음', '| 가로 넘침(360px):', ovf.length?ovf.join(', '):'없음'); await b.close(); })();
