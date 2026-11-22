/* 같이 하기 가짜 허브: 한 화면에 iframe 여러 개(= 폰 여러 대)를 열고, 진짜 허브처럼 말을 전달해 줘요.
   사용: const {openHub} = require('./hubsim.js'); const hub = await openHub(browser, 'net-yut.html', 4, {base:'http://localhost:8791/'});
   hub.frames[i] = i번째 폰의 Playwright Frame(0번이 방장), hub.drop(i) = i번째 폰이 나감, hub.page. 서버는 저장소 폴더에서 `python3 -m http.server 8791` 로 먼저 띄워요. */
const NAMES = ['방장', '철수', '영희', '민수', '지수', '하나'], IDS = ['host', 'p1', 'p2', 'p3', 'p4', 'p5'];
async function openHub(browser, file, n, opt = {}) {
  const base = opt.base || 'http://localhost:8791/', page = await browser.newPage({ viewport: opt.viewport || { width: 1600, height: 900 } });
  const html = `<body style="margin:0;display:flex;flex-wrap:wrap;gap:6px;background:#222"><script>
  const players = ${JSON.stringify(NAMES.slice(0, n).map((nm, i) => ({ id: IDS[i], name: nm })))}, frames = [], alive = players.map(() => true);
  const post = (k, m) => { try { frames[k].contentWindow.postMessage(m, '*'); } catch (e) {} };
  const live = () => players.filter((p, k) => alive[k]);
  window.drop = k => { alive[k] = false; frames[k].style.opacity = .3; players.forEach((p, j) => { if (alive[j]) post(j, { fg: 'roster', players: live() }); }); };
  addEventListener('message', e => { const i = frames.findIndex(f => f.contentWindow === e.source); if (i < 0 || !alive[i]) return; const m = e.data || {};
    if (m.fg === 'ready') post(i, { fg: 'init', me: players[i], isHost: i === 0, players: live() });
    else if (m.fg === 'h') frames[i].style.height = Math.min(m.h, 2400) + 'px';
    else if (m.fg === 'send') { const dst = m.to === '*' ? players.map((p, k) => k).filter(k => k !== i) : m.to === 'host' ? [0] : [players.findIndex(p => p.id === m.to)];
      dst.forEach(k => { if (k >= 0 && alive[k]) post(k, { fg: 'msg', from: players[i].id, d: m.d }); }); } });
  players.forEach((p, k) => { const f = document.createElement('iframe'); f.src = ${JSON.stringify(base + file)}; f.style.cssText = 'width:${opt.w || 360}px;height:700px;border:0;background:#fff'; f.name = 'p' + k; document.body.appendChild(f); frames.push(f); });
  </script></body>`;
  await page.setContent(html); const frs = []; const t0 = Date.now();
  while (frs.length < n && Date.now() - t0 < 15000) { await page.waitForTimeout(200); frs.length = 0; for (let k = 0; k < n; k++) { const f = page.frames().find(x => x.name() === 'p' + k); if (f) frs.push(f); } }
  await page.waitForTimeout(800);
  return { page, frames: frs, drop: k => page.evaluate(k => window.drop(k), k) };
}
module.exports = { openHub };
