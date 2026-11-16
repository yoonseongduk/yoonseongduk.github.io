// 폭탄 뒤 손패가 남아 있어도 「더미 뒤집기」가 뜨고 눌러지는지. 사용: py -m http.server 8765 후 node gs_bflip.js
const { chromium } = require('playwright'); let bad = 0; const ok = (c, m) => { console.log((c ? 'OK  ' : 'FAIL ') + m); if (!c) bad++; };
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 360, height: 780 } })).newPage();
  await p.goto('http://localhost:8765/go-stop.html'); await p.waitForTimeout(600);
  await p.evaluate(() => { clearTimeout(timer); S = GS.newGame(5, 0, 2); S.hands[0] = [0, 1, 2, 40, 44]; S.field = [3, 8, 12]; S.deck = [20, 21, 22, 23, 24, 25, 26, 27]; S.cap = [[], []]; S.turn = 0; S.phase = 'hand'; S.pend = null; S.ctx = null; msg = ''; render(); });
  ok(!(await p.$('#bflip')), '폭탄 전에는 손패가 있으면 「더미 뒤집기」가 없다');
  await p.click('#hand .gc[data-id="0"]'); await p.waitForTimeout(150); await p.click('#bq1'); await p.waitForTimeout(300);
  await p.evaluate(() => { clearTimeout(timer); S.turn = 0; S.phase = 'hand'; S.pend = null; S.ctx = null; render(); });
  ok(await p.evaluate(() => S.hands[0].length === 2 && S.btok[0] === 2), '폭탄 뒤 손패 2장이 남고 뒤집기 보너스 2번');
  ok(!!(await p.$('#bflip')) && /보너스 2번/.test(await p.$eval('#bflip', e => e.textContent)), '손패가 남아 있어도 「더미 뒤집기 (폭탄 보너스 2번 남음)」 버튼이 뜬다');
  await p.click('#bflip'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => S.btok[0] === 1 && S.hands[0].length === 2), '누르면 패를 내지 않고 더미만 뒤집고 보너스가 1번 남는다');
  await b.close(); console.log(bad ? bad + '개 실패' : '모두 통과'); process.exit(bad ? 1 : 0);
})();
