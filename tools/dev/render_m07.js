// 7월 임시 그림: minhwa.py 가 만든 7월 SVG 4장을 gemini 카드와 같은 크기(200x310) PNG 로 만든다 → gemini_src/m07_0~3.png
const { chromium } = require("./node_modules/playwright"); const fs = require("fs"), path = require("path");
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 200, height: 310 }, deviceScaleFactor: 1 });
  for (let k = 0; k < 4; k++) {
    let svg = fs.readFileSync(path.join(__dirname, "../../cards-minhwa/" + (24 + k) + ".svg"), "utf8").replace('width="100" height="164"', 'width="200" height="310" preserveAspectRatio="none"');
    await p.setContent('<body style="margin:0;background:transparent">' + svg + "</body>");
    await p.screenshot({ path: path.join(__dirname, "gemini_src/m07_" + k + ".png"), omitBackground: true });
  }
  await b.close();
})();
