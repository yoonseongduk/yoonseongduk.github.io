const REPO = require('path').resolve(__dirname, '..', '..');
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); await p.goto('about:blank');
  const files = fs.readdirSync(REPO).filter(f => f.endsWith('.html')); const bad = [];
  for (const f of files) { const s = fs.readFileSync(REPO + '/' + f, 'utf8'); const m = s.match(/<script>([\s\S]*?)<\/script>/); if (!m) continue; const names = new Set(); let depth = 0; for (const line of m[1].split('\n')) { const mm = line.match(/^(?:let|const|var)\s+([A-Za-z_$][\w$]*)/) || line.match(/^function\s+([A-Za-z_$][\w$]*)/); if (mm) names.add(mm[1]); const ml = line.match(/^(?:let|const)\s+([^=;]+?)(?:=|;|$)/); if (ml && ml[1].includes(',')) ml[1].split(',').forEach(x => names.add(x.trim().split(/\s/)[0])); }
    const clash = await p.evaluate(n => n.filter(x => x in window), [...names]); if (clash.length) bad.push(f + ': ' + clash.join(',')); }
  console.log('브라우저 기본 이름과 겹치는 전역 이름:', bad.length ? bad.join(' | ') : '없음 (' + files.length + '개 파일 검사)'); await b.close();
})();
