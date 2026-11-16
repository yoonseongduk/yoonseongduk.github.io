// 흔들기 배수·쌍피 국진이 화면(점수판·획득 패·결과표)에 반영되는지 확인. 사용: py -m http.server 8765 (저장소 루트) 후 node gs_shake.js
const { chromium } = require('playwright');
let bad = 0; const ok = (c, m) => { console.log((c ? 'OK  ' : 'FAIL ') + m); if (!c) bad++; };
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 360, height: 780 } })).newPage();
  await p.goto('http://localhost:8765/go-stop.html'); await p.waitForTimeout(600);
  await p.evaluate(() => {
    clearTimeout(timer); S = GS.newGame(5, 0, 2); S.turn = 0; S.phase = 'hand'; S.pend = null; S.ctx = null;
    S.cap = [[0, 4, 8, 12, 16, 20, 24, 28, 29, 32, 36, 40, 1, 2], [3]]; S.shake[0] = 1; S.gukjin[0] = 'pi'; msg = ''; render();
  });
  const bar = await p.$eval('#bar .bs', e => e.innerText); // 첫 칸 = 컴퓨터? 내 칸을 따로 찾는다
  const mine = await p.evaluate(() => [...document.querySelectorAll('#bar .bs')].map(e => e.innerText).join(' | '));
  ok(/×2=24점/.test(mine), '점수판에 흔들기 반영 점수(12점 ×2=24점)가 보인다: ' + mine.replace(/\n/g, ' '));
  const cap = await p.$eval('#cap', e => e.innerText);
  ok(/흔들기 ×2 = 24점/.test(cap), '획득 패 아래 점수 줄에 흔들기 배수가 보인다');
  const rows = await p.evaluate(() => [...document.querySelectorAll('#cap .cl')].map(e => e.textContent + ':' + e.nextElementSibling.querySelectorAll('.gc').length));
  ok(rows.join(',').includes('열끗:'), '획득 패 행: ' + rows.join(' '));
  const inPi = await p.evaluate(() => [...document.querySelectorAll('#cap .cl')].filter(e => e.textContent === '피').map(e => [...e.nextElementSibling.parentElement.children].slice(0).length)[0]);
  const pi32 = await p.evaluate(() => { const cl = [...document.querySelectorAll('#cap .cl')].find(e => e.textContent === '피'); const cells = []; let n = cl.nextElementSibling; while (n && !n.classList.contains('cl')) { cells.push(n); n = n.nextElementSibling; } return cells.map(c => [...c.querySelectorAll('.gc')].map(g => g.dataset.id)); });
  ok(pi32.some(a => a.includes('32')), '쌍피로 쓴 9월 열끗(32)이 피 줄에 있다: ' + JSON.stringify(pi32));
  await p.evaluate(() => { S.phase = 'gostop'; S.pend = { type: 'gostop', score: 12 }; render(); });
  ok(/배수 반영 24점/.test(await p.$eval('#bgo', e => e.textContent)), '고 버튼에 배수 반영 점수가 보인다');
  await p.evaluate(() => { GS.act(S, { t: 'stop' }); finish(); });
  const res = await p.$eval('#result', e => e.innerText);
  ok(/흔들기\s*×2/.test(res) && /96점/.test(res), '결과표에 흔들기 ×2와 합계 96점이 보인다: ' + res.replace(/\n/g, ' ').slice(0, 160));
  await b.close(); console.log(bad ? bad + '개 실패' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
