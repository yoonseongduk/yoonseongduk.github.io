// 블랙잭 포인트 판돈 검사 (py -m http.server 8765 를 띄운 뒤: node blackjack.js)
const { chromium } = require("./node_modules/playwright");
let bad = 0; const ok = (c, m) => { console.log((c ? "[통과] " : "[실패] ") + m); if (!c) bad++; };
const seed = (p, total) => p.evaluate(t => { const d = new Date(), y = d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  localStorage.setItem("fg-points-v1", JSON.stringify({ v: 1, p: { "(이 폰)": { total: t, day: y, lastDay: y, streak: 1, today: {}, bonus: {}, seen: ["blackjack.html"], log: [] } } })); }, total);
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 360, height: 800 } }), errs = [];
  p.on("pageerror", e => errs.push(String(e).slice(0, 120)));
  await p.goto("http://localhost:8765/blackjack.html"); await seed(p, 100); await p.reload(); await p.waitForTimeout(500);
  const pts = () => p.evaluate(() => fgPerson.points()), txt = id => p.$eval("#" + id, e => e.textContent);
  ok(await txt("chips") === "100", '내 포인트가 판돈 잔액으로 보인다 (100)');
  ok(await p.$eval('[data-b="500"]', e => e.disabled) && !(await p.$eval('[data-b="100"]', e => e.disabled)), '가진 포인트보다 큰 판돈 버튼은 막힌다(500 막힘, 100 가능)');
  await p.fill("#betin", "37"); await p.dispatchEvent("#betin", "change"); ok(await txt("bet") === "37", '판돈을 1p 단위로 직접 정할 수 있다 (37)');
  await p.fill("#betin", "999"); await p.dispatchEvent("#betin", "change"); ok(await txt("bet") === "100", '가진 것보다 크게 쓰면 내 포인트(100)까지로 맞춘다');
  await p.fill("#betin", "20"); await p.dispatchEvent("#betin", "change");
  // 한 판: 딜 → 판돈이 바로 빠진다
  await p.click('[data-a="deal"]'); await p.waitForTimeout(200);
  const st = await p.evaluate(() => state);
  if (st === "play") ok(await pts() === 80, '딜하면 판돈 20p가 먼저 빠진다 (100→80)');
  for (let i = 0; i < 12 && await p.evaluate(() => state) === "play"; i++) { await p.click('[data-a="stand"]'); await p.waitForTimeout(100); }
  ok(await p.evaluate(() => state) === "over", '한 판이 끝난다');
  const g1 = await p.evaluate(() => ({ g: fgPerson.game(), h: fgPerson.history(), pts: fgPerson.points() }));
  ok(g1.pts - 100 === g1.g.earned && g1.g.earned === g1.h.reduce((t, x) => t + x.p, 0), '내 포인트 변화(' + (g1.pts - 100) + ') = 오늘 손익 = 이력 합계');
  ok(g1.h.every(x => /블랙잭/.test(x.w)) && g1.h[0].p === -20, '이력은 판돈·정산만 있다 (자동 플레이·이김 점수는 없음): ' + g1.h.map(x => x.p + " " + x.w).join(" / "));
  // 여러 판: 하루 횟수 제한이 없다
  let rounds = 1;
  for (let r = 0; r < 14; r++) {
    if (await pts() < 5) break;
    await p.click('[data-a="again"]'); await p.fill("#betin", "5"); await p.dispatchEvent("#betin", "change"); await p.click('[data-a="deal"]');
    for (let i = 0; i < 12 && await p.evaluate(() => state) === "play"; i++) { await p.click('[data-a="stand"]'); await p.waitForTimeout(60); }
    rounds++;
  }
  const g2 = await p.evaluate(() => ({ g: fgPerson.game(), n: fgPerson.history().length, pts: fgPerson.points() }));
  ok(rounds >= 10 && g2.n >= rounds + 0, rounds + '판을 이어서 해도 횟수 제한이 없다 (이력 ' + g2.n + '건)');
  ok(g2.pts - 100 === g2.g.earned, '여러 판 뒤에도 내 포인트 변화 = 오늘 손익 (' + g2.g.earned + 'p)');
  // 올인
  await p.click('[data-a="again"]'); const have = await pts();
  if (have > 0) { await p.click('[data-b="all"]'); ok(await txt("bet") === String(have), '올인: 판돈이 내 포인트 전부(' + have + ')가 된다'); await p.click('[data-a="deal"]'); ok(await pts() === 0, '올인 딜: 내 포인트가 0이 된다'); }
  // 포인트 0이면 못 한다
  await seed(p, 0); await p.reload(); await p.waitForTimeout(500);
  ok(await p.$eval('[data-a="deal"]', e => e.disabled) && /할 수 없어요/.test(await p.$eval('[data-a="deal"]', e => e.textContent)), '포인트가 0이면 딜을 할 수 없다');
  ok(await p.$eval("#betin", e => e.disabled), '포인트가 0이면 판돈 입력도 막힌다');
  // 카드를 정해 놓고 정산 확인: deck 의 끝에서부터 뽑는다(내 첫 장, 내 둘째 장, 딜러 첫 장, 딜러 둘째 장)
  const rig = (cards) => p.evaluate(cs => { const pad = Array.from({ length: 14 }, () => ({ r: "2", s: "♣" })); deck = [...pad, ...cs.slice().reverse().map(x => ({ r: x[0], s: x[1] }))]; }, cards);
  const round = async (label, cards, bet, expectPts, extra) => {
    await seed(p, 100); await p.reload(); await p.waitForTimeout(300); await p.fill("#betin", String(bet)); await p.dispatchEvent("#betin", "change"); await rig(cards);
    await p.click('[data-a="deal"]'); await p.waitForTimeout(100);
    if (extra === "double") { await p.click('[data-a="dbl"]'); } else if (await p.evaluate(() => state) === "play") { await p.click('[data-a="stand"]'); }
    await p.waitForTimeout(150); ok(await pts() === expectPts, label + ': 내 포인트 ' + (await pts()) + ' (기대 ' + expectPts + ')');
  };
  await round("이김(19 vs 17, 판돈 20)", [["10", "♠"], ["9", "♥"], ["10", "♦"], ["7", "♣"]], 20, 120);          // 100-20+40
  await round("짐(17 vs 19, 판돈 20)", [["10", "♠"], ["7", "♥"], ["10", "♦"], ["9", "♣"]], 20, 80);            // 100-20
  await round("비김(18 vs 18, 판돈 20)", [["10", "♠"], ["8", "♥"], ["10", "♦"], ["8", "♣"]], 20, 100);         // 판돈 돌려받음
  await round("블랙잭(판돈 20, 판돈의 2.5배=50 받음)", [["A", "♠"], ["K", "♥"], ["10", "♦"], ["7", "♣"]], 20, 130);   // 100-20+50
  await round("딜러 블랙잭(판돈 20)", [["10", "♠"], ["9", "♥"], ["A", "♦"], ["K", "♣"]], 20, 80);
  await round("올인 이김(판돈 100)", [["10", "♠"], ["9", "♥"], ["10", "♦"], ["7", "♣"]], 100, 200);
  await round("더블 이김(5+6, 더블 뒤 21 vs 17, 판돈 20)", [["5", "♠"], ["6", "♥"], ["10", "♦"], ["7", "♣"], ["10", "♣"]], 20, 140, "double"); // 100-20-20+80
  // 가족 포인트 화면
  await seed(p, 100); await p.reload(); await p.waitForTimeout(400); await p.click('[data-a="deal"]'); await p.waitForTimeout(200);
  await p.goto("http://localhost:8765/family-points.html"); await p.waitForTimeout(600);
  const fp = await p.$eval("#log", e => e.innerText); ok(/블랙잭/.test(fp) && /판돈/.test(fp), '가족 포인트 화면에 블랙잭 판돈 손익이 보인다: ' + fp.replace(/\n/g, " | "));
  ok(errs.length === 0, '오류 없음 ' + errs.join("|"));
  await b.close(); console.log(bad ? "실패 " + bad + "건" : "모두 통과"); process.exit(bad ? 1 : 0);
})();
