// 판마다 포인트가 바로 들어가는지, 이력 패널이 열리는지 검사 (py -m http.server 8765 를 띄운 뒤: node rounds.js)
const { chromium } = require("./node_modules/playwright");
let bad = 0; const ok = (c, m) => { console.log((c ? "[통과] " : "[실패] ") + m); if (!c) bad++; };
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 360, height: 700 } }), errs = [];
  p.on("pageerror", e => errs.push(String(e).slice(0, 120)));
  await p.goto("http://localhost:8765/aim-trainer.html"); await p.waitForTimeout(600);
  await p.evaluate(() => { fgPerson.cfg.minSec = 1; });
  const earned = () => p.evaluate(() => fgPerson.game().earned);
  await p.mouse.click(180, 400); await p.waitForTimeout(2300); ok(await earned() === 10, '1판: 플레이 +10이 바로 반영된다');
  await p.evaluate(() => { const x = document.createElement("button"); x.id = "rs"; x.textContent = "다시 시작"; x.style.cssText = "position:fixed;left:10px;bottom:10px;z-index:9999"; document.body.appendChild(x); });
  await p.click("#rs"); await p.mouse.click(180, 400); await p.waitForTimeout(2300); ok(await earned() === 20, '다시 시작 후 2판: 플레이 +10이 또 들어간다');
  await p.evaluate(() => { const d = document.createElement("p"); d.textContent = "🎉 성공했어요!"; document.body.appendChild(d); }); await p.waitForTimeout(400);
  ok(await earned() === 40, '2판 이김 +20이 바로 반영된다');
  await p.mouse.click(180, 400); await p.waitForTimeout(300);
  await p.evaluate(() => { const d = document.createElement("p"); d.textContent = "🎉 성공했어요! 또"; document.body.appendChild(d); }); await p.waitForTimeout(400);
  ok(await earned() === 70, '끝난 판 다음 탭으로 시작한 3판도 플레이+이김이 들어간다');
  await p.mouse.click(180, 400); await p.waitForTimeout(2300); ok(await earned() === 70, '하루 플레이 3번이 넘으면 더 받지 않는다');
  await p.click("#fg-gpt"); await p.waitForTimeout(200);
  const rows = await p.$$eval("#fg-ghist tr", t => t.map(r => r.innerText.replace(/\s+/g, " ")));
  ok(rows.length === 5, '포인트 칸을 누르면 오늘 이력이 열린다 (' + rows.length + '줄)');
  const before = await p.evaluate(() => fgPerson.points()); await p.waitForTimeout(500);
  ok(await p.evaluate(() => fgPerson.points()) === before && (await p.$$eval("#fg-ghist tr", t => t.length)) === 5, '이력 패널을 열어도 포인트가 늘지 않는다(패널 글자를 이김 글귀로 오인하지 않음)');
  await p.click("#fg-gpt"); ok(!(await p.$("#fg-ghist")), '다시 누르면 닫힌다');
  // ── 실제 5장 포커로 여러 판: 짧게 끝나는 판·진 판도 플레이 점수가 들어가고 이력에 쌓인다
  const q = await b.newPage({ viewport: { width: 360, height: 800 } }); q.on("pageerror", e => errs.push(String(e).slice(0, 120)));
  await q.goto("http://localhost:8765/poker-draw.html"); await q.waitForTimeout(600);
  await q.evaluate(() => { fgPerson.cfg.roundSec = 1; fgPerson.cfg.minSec = 99; });
  const g = () => q.evaluate(() => fgPerson.game());
  for (let h = 1; h <= 4; h++) {
    await q.click("#mh button"); await q.waitForTimeout(1300);            // 카드 하나 고정(입력) 후 1.3초
    await q.click("#act"); await q.waitForTimeout(400);                   // 카드 교체하기 → 이김/짐/비김 글귀
    const gg = await g(); ok(gg.plays === Math.min(h, 3), h + '번째 판 끝: 플레이 ' + gg.plays + '/3번이 그 자리에서 반영된다 (결과: ' + (await q.$eval("#res b", e => e.textContent)) + ')');
    if (h < 4) { await q.click("#act"); await q.waitForTimeout(300); }      // 다음 판
  }
  const hist = await q.evaluate(() => fgPerson.history());
  ok(hist.length >= 3 && hist.every(x => x.p > 0), '이력에 판마다 쌓인다 (' + hist.length + '건: ' + hist.map(x => x.w).join(' / ') + ')');
  await q.click("#fg-gpt"); const panel = await q.$eval("#fg-ghist", e => e.innerText); ok(/플레이 3\/3번/.test(panel) && panel.includes("합계 " + hist.reduce((t, x) => t + x.p, 0) + "p"), '이력 패널의 합계·횟수가 맞다');
  ok(errs.length === 0, '오류 없음 ' + errs.join('|'));
  await b.close(); console.log(bad ? "실패 " + bad + "건" : "모두 통과"); process.exit(bad ? 1 : 0);
})();
