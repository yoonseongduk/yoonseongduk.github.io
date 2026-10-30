const REPO = require('path').resolve(__dirname, '..', '..');
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const errs = []; const dir = REPO + '/';
  const p = await b.newPage({ viewport: { width: 400, height: 900 } }); p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + dir + 'index.html'); await p.waitForTimeout(250);
  console.log('카드 수', await p.locator('a.game').count(), '| 분류 제목', (await p.locator('h2').allInnerTexts()).map(t => t.replace(/\n/g, ' ')).join(' / '));
  const links = await p.evaluate(() => [...document.querySelectorAll('a.game')].map(a => a.getAttribute('href')));
  console.log('링크 파일 모두 존재:', links.every(f => fs.existsSync(dir + f)), '| 중복 없음', new Set(links).size === links.length, '| 저장소의 게임 파일 중 목록에 없는 것:', fs.readdirSync(dir).filter(f => f.endsWith('.html') && f !== 'index.html' && !links.includes(f)).join(', ') || '없음');
  await p.locator('[data-g=arcade]').click(); console.log('아케이드 분류:', await p.locator('a.game').count(), '개 |', (await p.locator('#count').textContent()).trim());
  await p.locator('[data-g=all]').click(); await p.fill('#q', '숫자'); console.log('"숫자" 검색:', (await p.locator('a.game h3').allInnerTexts()).join(', '));
  await p.fill('#q', '없는게임zzz'); console.log('없는 검색어:', (await p.locator('.empty').textContent()).trim());
  await p.fill('#q', ''); for (const w of [400, 320, 700]) { await p.setViewportSize({ width: w, height: 900 }); console.log(w + 'px 가로넘침', (await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth])).join('/')); }
  await p.setViewportSize({ width: 400, height: 1100 }); await p.screenshot({ path: 'index.png' });
  console.log('오류', JSON.stringify(errs)); await b.close();
})();
