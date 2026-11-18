# 가족 순위표 화면 (family-ranking.html) — 대표 게임 10개의 사람별 최고 기록을 비교한다.
# 기록은 person.js 가 "키"(이 폰 주인) / "키::이름"(다른 사람)으로 저장해 둔 것을 그대로 읽는다(RAWPAGE 화면).
# 새 게임을 넣으려면 아래 BOARDS 에 한 줄 추가하고 `py set37.py` → `py ship.py ...` 를 다시 실행한다.
import sys
sys.path.insert(0, ".")
from mkpage import make

CSS = '''.li{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--line)}.li:last-child{border-bottom:0}
.note{font-size:.85rem;color:var(--muted)}.me{font-weight:700;color:var(--accent)}.sub{font-size:.85rem;color:var(--muted);margin-top:6px}
.gt{display:flex;justify-content:space-between;align-items:center;gap:8px}.gt a{font-size:.85rem;color:var(--accent)}.rk{display:inline-block;min-width:1.6em}
'''

BODY = '''  <div class="card"><b>🏅 종합 (1등 횟수)</b><div id="total"></div><div class="note" id="tnote"></div></div>
  <div id="boards"></div>
  <p class="muted">이 폰에 저장된 기록만 비교해요. 가족이 한 폰을 같이 쓰면서 위쪽 칩에서 이름을 골라 하면 사람별로 쌓여요. 기록이 두 사람 이상일 때만 1등으로 세요.</p>
'''

JS = r'''
// 게임별 기록 정의: k=저장 키, sub=[[세부 키, 이름]](없으면 숫자 하나), low=낮을수록 좋음, f=값 표시 함수
const BOARDS = [
  { f: "reaction-test.html",  e: "⚡", t: "반응 속도",   k: "reaction-best-v1",    sub: [["avg", "5번 평균"], ["one", "한 번 최고"]], low: true, fmt: v => v + "ms" },
  { f: "typing-test.html",    e: "⌨️", t: "타자 속도",   k: "typing-best-v1",      fmt: v => v + "타" },
  { f: "quick-math.html",     e: "🧮", t: "암산 (60초)", k: "quickmath-best-v1",   sub: [["add", "덧셈·뺄셈"], ["times", "구구단"], ["mul", "곱셈"]], fmt: v => v + "문제" },
  { f: "times-table.html",    e: "✖️", t: "구구단 (60초)", k: "timestable-best-v1", fmt: v => v + "개" },
  { f: "click-speed.html",    e: "👆", t: "클릭 속도",   k: "clickspeed-best-v1",  sub: [["5", "5초"], ["10", "10초"], ["30", "30초"]], fmt: v => v + " CPS" },
  { f: "number-memory.html",  e: "🔢", t: "숫자 기억",   k: "numbermemory-best-v1", fmt: v => v + "단계" },
  { f: "reverse-memory.html", e: "🔁", t: "거꾸로 기억", k: "reversememory-best-v1", fmt: v => v + "단계" },
  { f: "pattern-memory.html", e: "🧩", t: "패턴 기억",   k: "patternmem-best-v1",  fmt: v => v + "단계" },
  { f: "aim-trainer.html",    e: "🎯", t: "조준 연습 (30초)", k: "aim-best-v1",    sub: [["big", "큰 과녁"], ["mid", "보통"], ["small", "작은 과녁"]], fmt: v => v + "명중" },
  { f: "stroop-color.html",   e: "🎨", t: "글자 색 맞히기", k: "stroop-best-v1",   fmt: v => v + "점" },
  { f: "number-tap.html",     e: "👇", t: "숫자 순서 터치", k: "numtap-best-v1",   sub: [["3", "3단계"], ["4", "4단계"], ["5", "5단계"]], low: true, fmt: v => (v / 1000).toFixed(2) + "초" },
];
const FP = window.fgPerson, MEDAL = ["🥇", "🥈", "🥉"];
const rawGet = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
const jsonGet = k => { try { return JSON.parse(rawGet(k)); } catch (e) { return null; } };
const ownerName = () => FP.owner() || "(이 폰)";
// 이름 모으기: 가족 명단 + 포인트 기록 + 이 폰 주인 + 저장소에 "키::이름"으로 남은 이름
function allNames() {
  const fam = jsonGet("family-members-v1"), pts = (jsonGet(FP.pointsKey) || {}).p || {}, set = new Set([ownerName()]);
  (Array.isArray(fam) ? fam : []).forEach(n => typeof n === "string" && n && set.add(n));
  Object.keys(pts).forEach(n => n && set.add(n));
  try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i) || ""; const j = k.indexOf("::"); if (j > 0 && BOARDS.some(b => b.k === k.slice(0, j))) set.add(k.slice(j + 2)); } } catch (e) {}
  return [...set];
}
// 한 사람의 기록 읽기(이 폰 주인은 "키", 다른 사람은 "키::이름")
function readVal(b, name, sub) {
  const key = name === ownerName() ? b.k : b.k + "::" + name;
  let v = jsonGet(key);
  if (v && typeof v === "object" && sub != null) v = v[sub];
  v = Number(v);
  return v > 0 ? v : null;
}
function render() {
  const names = allNames(), cur = FP.player() || ownerName(), wins = {};
  names.forEach(n => wins[n] = 0);
  let html = "";
  BOARDS.forEach(b => {
    const subs = b.sub || [[null, ""]];
    let rowsHtml = "", any = false;
    subs.forEach(([sk, sl]) => {
      const rows = names.map(n => ({ n, v: readVal(b, n, sk) })).filter(r => r.v != null).sort((x, y) => b.low ? x.v - y.v : y.v - x.v);
      if (rows.length) any = true;
      if (rows.length >= 2) { const best = rows[0].v; rows.filter(r => r.v === best).forEach(r => wins[r.n]++); }
      rowsHtml += (sl ? `<div class="sub">${esc(sl)}</div>` : "") + (rows.length ? rows.map((r, i) => `<div class="li${r.n === cur ? " me" : ""}"><span><span class="rk">${MEDAL[i] || (i + 1)}</span> ${esc(r.n)}</span><b>${esc(b.fmt(r.v))}</b></div>`).join("") : `<div class="note">아직 기록이 없어요</div>`);
    });
    html += `<div class="card"><div class="gt"><b>${b.e} ${esc(b.t)}</b><a href="${b.f}">하러 가기 ›</a></div>${rowsHtml}</div>`;
  });
  $("boards").innerHTML = html;
  const tot = names.map(n => ({ n, w: wins[n] })).sort((a, b) => b.w - a.w);
  $("total").innerHTML = tot.map((r, i) => `<div class="li${r.n === cur ? " me" : ""}"><span><span class="rk">${i === 0 && r.w > 0 ? "🥇" : i + 1}</span> ${esc(r.n)}</span><b>${r.w}번</b></div>`).join("");
  $("tnote").textContent = tot.every(r => r.w === 0) ? "두 사람 이상이 같은 게임을 하면 1등이 정해져요. 위쪽 칩에서 '누가 하나요?'를 골라 보세요." : "";
}
render();
addEventListener("pageshow", render);
'''

make("out/family-ranking.html", "가족 순위표", "🏅", 30, "fg-ranking-v1",
     "게임별로 가족 중 누가 가장 잘했는지 최고 기록을 비교해요. 이 폰에 저장된 기록만 보여요.", BODY, JS, CSS)
