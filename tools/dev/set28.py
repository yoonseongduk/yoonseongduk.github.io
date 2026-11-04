import sys
sys.path.insert(0, ".")
from mkpage import make
RX = open("/tmp/rx.js", encoding="utf-8").read()
COM = r"""
const pad = n => String(n).padStart(2, "0");
const ymd = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const todayS = () => ymd(new Date());
const dnum = s => { const [y, m, d] = s.split("-").map(Number); return Math.round(Date.UTC(y, m - 1, d) / 86400000); };
const addDays = (s, n) => { const [y, m, d] = s.split("-").map(Number); return ymd(new Date(y, m - 1, d + n)); };
const WD = ["일", "월", "화", "수", "목", "금", "토"];
const wdOf = s => WD[new Date(s + "T00:00:00").getDay()];
"""
CSS = '''.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-weight:700}.chip.on{background:var(--fg);color:var(--bg);border-color:var(--fg)}.dots{display:flex;gap:6px;justify-content:center}.dots i{width:10px;height:10px;border-radius:50%;background:var(--line)}.dots i.on{background:var(--accent)}.dots i.ok{background:var(--ok)}
.hz{font-size:5.5rem;line-height:1.1;text-align:center;font-family:"Noto Serif KR","Noto Serif CJK KR","Batang",serif}.hd{text-align:center;font-weight:700;font-size:1.15rem}.sec h3{margin:0;font-size:.95rem}.sec p{margin:2px 0 0}.sec ul{margin:4px 0 0;padding-left:20px}.tags{display:flex;flex-wrap:wrap;gap:6px}.tags span{background:color-mix(in srgb,var(--fg) 10%,var(--surface));border-radius:999px;padding:3px 10px;font-size:.9rem}.sec{display:grid;gap:4px}
.nav{display:grid;grid-template-columns:1fr 1fr;gap:8px}.opts{display:grid;gap:8px}.opt{background:var(--surface);border:2px solid var(--line);border-radius:14px;padding:12px;font-weight:700;text-align:center;font-size:1.1rem}.opt.good{border-color:var(--ok);background:color-mix(in srgb,var(--ok) 20%,var(--surface))}.opt.bad{border-color:var(--bad);background:color-mix(in srgb,var(--bad) 20%,var(--surface))}.opts.big .opt{font-family:"Noto Serif KR","Noto Serif CJK KR","Batang",serif;font-size:2rem}.note{font-size:.85rem;color:var(--muted)}.num{font-family:var(--font-display);font-size:2.2rem;color:var(--accent);text-align:center}a.btn{display:block;text-align:center;text-decoration:none}'''
BODY = '''  <div class="chips" id="cats"></div>
  <div class="card center"><b id="ttl"></b><div class="dots" id="dots"></div><div class="note" id="streak"></div></div>
  <div class="card" id="view"></div>
  <div class="nav" id="nav"></div>'''
JS = COM + r'''
''' + RX + r'''
const GR = ["6급", "5급", "4급", "3급", "2급", "1급"];
let S = Object.assign({ cat: "6급", done: {}, days: {} }, ld(KEY) || {});
let ALL = [], DET = {}, pool = [], set = [], step = 0, off = 0, qs = [], qi = 0, right = 0, locked = false;
const save = () => sv(KEY, S);
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function seeded(arr, seed) { const r = rng(seed), a = [...arr]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const hash = s => { let h = 7; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; };
const dkey = () => todayS() + "|" + S.cat + "|" + off;
function pick() {
  pool = ALL.filter(d => d[2] === S.cat); const order = seeded(pool, hash("hz" + S.cat)), n = order.length, base = ((dnum(todayS()) + off) * 3) % n;
  set = [0, 1, 2].map(k => order[(base + k) % n]);
}
const dt = () => { const d = new Date(); return `${d.getMonth() + 1}월 ${d.getDate()}일 (${wdOf(todayS())})`; };
function streak() { let n = 0, d = todayS(); if (!S.days[d]) d = addDays(d, -1); while (S.days[d]) { n++; d = addDays(d, -1); } return n; }
function head() {
  $("ttl").textContent = `📅 오늘의 한자 · ${dt()}${off ? ` · 추가 ${off}` : ""}`;
  $("dots").innerHTML = set.map((_, i) => `<i class="${step > i ? "ok" : step === i ? "on" : ""}"></i>`).join("") + `<i class="${step === 3 ? "on" : step > 3 ? "ok" : ""}" style="border-radius:3px"></i>`;
  const n = streak(), dn = S.done[dkey()];
  $("streak").textContent = `${n ? "🔥 " + n + "일 연속 공부 중 · " : ""}${dn !== undefined ? "이 묶음은 오늘 공부했어요 ✅ (퀴즈 " + dn + "/3)" : "한자 3개를 보고 짧은 퀴즈로 마무리해요"}`;
}
function card(d) {
  const e = DET[d[0]] || {};
  let h = `<div class="hz">${esc(d[0])}</div><div class="hd">${esc(d[1])} · ${esc(d[2])}</div><p class="note center">${esc(rinfo(d[3]))}</p>`;
  h += e.o ? `<div class="sec"><h3>🌱 글자의 유래</h3><p>${esc(e.o)}</p><p class="note">※ 한자의 유래는 학설에 따라 다를 수 있어요.</p></div>` : `<div class="sec"><h3>🌱 글자의 유래</h3><p class="note">이 글자의 유래 설명은 아직 준비 중이에요.</p></div>`;
  if (e.w) h += `<div class="sec"><h3>📝 이렇게 써요 (한자어)</h3><ul>${e.w.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div>`;
  if (e.i) h += `<div class="sec"><h3>📜 사자성어 속 쓰임</h3><ul>${e.i.map(x => `<li><b>${esc(x[0])}</b> (${esc(x[1])}) — ${esc(x[2])}</li>`).join("")}</ul></div>`;
  if (e.r) h += `<div class="sec"><h3>🧩 같은 부수 ${esc(rname(e.r[0]))} 한자</h3><div class="tags">${e.r[1].map(x => `<span>${esc(x[0])} ${esc(x[1])}</span>`).join("")}</div></div>`;
  return h;
}
function makeQs() {
  const others = d => shuf(pool.filter(x => x[0] !== d[0]));
  qs = shuf(set).map((d, i) => { const t = i % 2; const o = others(d).slice(0, 3); return t === 0 ? { d, type: "hun", opts: shuf([d, ...o]) } : { d, type: "char", opts: shuf([d, ...o]) }; });
  qi = 0; right = 0; locked = false;
}
function render() {
  head();
  if (step < 3) { $("view").innerHTML = card(set[step]); $("nav").innerHTML = `<button class="btn ghost" id="bk" type="button"${step ? "" : " disabled"}>◀ 이전</button><button class="btn" id="nx" type="button">${step < 2 ? "다음 한자 ▶" : "퀴즈 풀기 ▶"}</button>`;
    $("bk").onclick = () => { step--; render(); window.scrollTo(0, 0); }; $("nx").onclick = () => { step++; if (step === 3) makeQs(); render(); window.scrollTo(0, 0); }; return; }
  if (step === 3) { const q = qs[qi], big = q.type === "hun";
    $("view").innerHTML = `<div class="note center">퀴즈 ${qi + 1}/3</div>${q.type === "hun" ? `<div class="hz">${esc(q.d[0])}</div><p class="center"><b>이 한자의 뜻과 음은?</b></p>` : `<div class="hd" style="font-size:1.6rem">${esc(q.d[1])}</div><p class="center"><b>이 뜻과 음의 한자는?</b></p>`}<div class="opts${big ? "" : " big"}" id="op">${q.opts.map((o, i) => `<button type="button" class="opt" data-i="${i}">${esc(q.type === "hun" ? o[1] : o[0])}</button>`).join("")}</div><div class="note center" id="fb"></div>`;
    $("nav").innerHTML = `<button class="btn" id="nx2" type="button" hidden style="grid-column:1/-1">${qi < 2 ? "다음 문제 ▶" : "결과 보기 ▶"}</button>`;
    $("op").onclick = e => { const b = e.target.closest("[data-i]"); if (!b || locked) return; locked = true; const o = q.opts[+b.dataset.i], ok = o[0] === q.d[0]; if (ok) right++; document.querySelectorAll("#op .opt").forEach((x, i) => { if (q.opts[i][0] === q.d[0]) x.classList.add("good"); else if (x === b) x.classList.add("bad"); });
      $("fb").textContent = ok ? "⭕ 정답!" : `❌ 정답은 ${q.d[0]} (${q.d[1]})`; $("nx2").hidden = false; };
    $("nx2").onclick = () => { locked = false; if (qi < 2) { qi++; render(); } else { S.done[dkey()] = right; S.days[todayS()] = 1; save(); step = 4; render(); } };
    return; }
  const msg = right === 3 ? "🎉 모두 맞혔어요!" : right >= 2 ? "👍 잘했어요!" : "💪 내일 또 만나요!";
  $("view").innerHTML = `<div class="center"><div class="num">${right} / 3</div><b>${msg}</b></div><div class="sec"><h3>오늘 공부한 한자</h3><div class="tags">${set.map(d => `<span>${esc(d[0])} ${esc(d[1])}</span>`).join("")}</div></div><p class="note center">${streak()}일 연속 공부 중이에요 🔥</p>`;
  $("nav").innerHTML = `<button class="btn" id="more" type="button">➕ 3개 더 공부하기</button><button class="btn ghost" id="again" type="button">↩ 처음부터 다시 보기</button><a class="btn ghost" href="hanja-write.html" style="grid-column:1/-1">✍️ 한자 쓰기에서 연습하기</a><a class="btn ghost" href="hanja-quiz.html" style="grid-column:1/-1">📖 한자 급수 퀴즈 풀기</a>`;
  $("more").onclick = () => { off++; step = 0; pick(); render(); window.scrollTo(0, 0); }; $("again").onclick = () => { step = 0; render(); window.scrollTo(0, 0); };
}
function cats() { $("cats").innerHTML = GR.map(c => `<button type="button" class="chip${c === S.cat ? " on" : ""}" data-c="${c}">${c}</button>`).join(""); }
$("cats").onclick = e => { const b = e.target.closest("[data-c]"); if (!b) return; S.cat = b.dataset.c; off = 0; step = 0; save(); cats(); pick(); render(); };
Promise.all([fetch("data/hanja.json").then(r => r.json()), fetch("data/hanja-detail.json").then(r => r.json()).catch(() => ({}))]).then(([a, d]) => { ALL = a; DET = d; cats(); pick(); render(); }).catch(() => { $("view").innerHTML = '<p class="muted">한자 자료를 불러오지 못했어요. 인터넷에 한 번 연결한 뒤 다시 열어 주세요.</p>'; });
'''
make("out/hanja-today.html", "오늘의 한자", "📅", 30, "hanja-today-v1",
 "급수를 고르면 날마다 한자 3개가 정해져요. 유래와 쓰임을 보고 짧은 퀴즈로 마무리해요. 같은 날에는 같은 한자가 나오고, 공부 기록은 이 폰에만 저장돼요.",
 BODY, JS, CSS)
