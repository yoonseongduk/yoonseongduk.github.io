// auto_raw.json 의 번호 위치를, 쓰기 화면에 보이는 연한 글꼴 글자의 '먹'(획이 있는 곳)에 맞춰 보정해서 data/stroke-auto.json 으로 저장해요.
// 사용법: (저장소 폴더에서 `py -m http.server 8000` 을 켜 둔 상태로) node snap_auto.js
const { chromium } = require("playwright"); const fs = require("fs");
(async () => {
  const raw = JSON.parse(fs.readFileSync("auto_raw.json", "utf8")), bbs = JSON.parse(fs.readFileSync("auto_bbox.json", "utf8")); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 360, height: 740 } });
  await p.goto("http://localhost:" + (process.env.PORT || 8000) + "/hanja-write.html"); await p.waitForFunction(() => typeof ALL !== "undefined" && ALL.length > 3000);
  const out = await p.evaluate(({ raw, bbs }) => {
    const res = {}, R = 30;
    for (const ch of Object.keys(raw)) {
      const c = glyphCanvas(ch), x = c.getContext("2d"), px = x.getImageData(0, 0, S, S).data, ink = (a, b) => a >= 0 && b >= 0 && a < S && b < S && px[(b * S + a) * 4 + 3] > 110;
      let gx0 = S, gy0 = S, gx1 = -1, gy1 = -1; for (let yy = 0; yy < S; yy++) for (let xx = 0; xx < S; xx++) if (px[(yy * S + xx) * 4 + 3] > 110) { if (xx < gx0) gx0 = xx; if (xx > gx1) gx1 = xx; if (yy < gy0) gy0 = yy; if (yy > gy1) gy1 = yy; }
      const [bx0, by0, bx1, by1] = bbs[ch], fit = gx1 > gx0 && bx1 > bx0 && by1 > by0 && gy1 > gy0;
      const pts0 = raw[ch].map(([qx, qy]) => fit ? [gx0 + (qx - bx0) / (bx1 - bx0) * (gx1 - gx0), gy0 + (qy - by0) / (by1 - by0) * (gy1 - gy0)] : [qx, qy]);
      res[ch] = pts0.map(([ax, ay]) => { let best = null, bd = 1e9; const cx = Math.round(ax), cy = Math.round(ay);
        if (ink(cx, cy)) return [cx, cy];
        for (let dy = -R; dy <= R; dy++) for (let dx = -R; dx <= R; dx++) { if (ink(cx + dx, cy + dy)) { const d = dx * dx + dy * dy; if (d < bd) { bd = d; best = [cx + dx, cy + dy]; } } }
        return best || [cx, cy]; });
    }
    return res;
  }, { raw, bbs });
  fs.writeFileSync("../../data/stroke-auto.json", JSON.stringify(out)); console.log("보정한 글자", Object.keys(out).length); await b.close();
})();
