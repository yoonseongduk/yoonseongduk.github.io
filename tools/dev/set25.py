import sys
sys.path.insert(0, ".")
from mkpage import make
BODY = '''  <div class="card"><b>⚙️ 계산 설정</b>
    <label class="muted" for="ref">기준일 (재직 중인 곳은 이 날짜까지 계산해요)</label><input type="date" id="ref">
    <label class="opt"><input type="checkbox" id="inc" checked> 퇴사일 당일도 근무일로 포함</label>
    <label class="opt"><input type="checkbox" id="mrg" checked> 기간이 겹치면 한 번만 계산 (중복 근무 제외)</label></div>
  <div id="list"></div>
  <button class="btn" id="add" type="button">➕ 경력 추가</button>
  <div class="card" id="res"></div>'''
CSS = '''.opt{display:flex;gap:8px;align-items:center;margin-top:8px;font-size:.95rem}input[type=date]{width:100%;box-sizing:border-box;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:inherit}.job{display:grid;gap:8px;margin-bottom:12px}.job .row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}.job input{min-width:0;max-width:100%;box-sizing:border-box}.job>*{min-width:0}.job .row3{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center}.job .top{display:flex;gap:8px}.job .top input{flex:1;width:auto}.dur{font-family:var(--font-display);font-size:1.15rem;color:var(--accent)}.big{font-family:var(--font-display);font-size:1.9rem;color:var(--accent);line-height:1.2;text-align:center}.tbl{width:100%;border-collapse:collapse;font-size:.92rem}.tbl td{padding:5px 2px;border-bottom:1px solid var(--line)}.tbl td:last-child{text-align:right}.bad{color:var(--bad)}.btn.sm{padding:6px 12px;font-size:.9rem}label.mini{display:flex;gap:6px;align-items:center;font-size:.9rem}.pc{width:72px!important;padding:8px!important}'''
JS = r'''
const DAY = 86400000;
const toD = s => { if (!s) return null; const [y, m, d] = s.split("-").map(Number); return Date.UTC(y, m - 1, d) / DAY; };
const fmt = n => { const t = new Date(n * DAY); return `${t.getUTCFullYear()}.${String(t.getUTCMonth() + 1).padStart(2, "0")}.${String(t.getUTCDate()).padStart(2, "0")}`; };
const dim = (y, m) => new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
function ymd(a, b) {
  const A = new Date(a * DAY), B = new Date(b * DAY);
  let y = B.getUTCFullYear() - A.getUTCFullYear(), m = B.getUTCMonth() - A.getUTCMonth(), d = B.getUTCDate() - A.getUTCDate();
  if (d < 0) { m--; const pm = B.getUTCMonth() - 1; d += pm < 0 ? dim(B.getUTCFullYear() - 1, 11) : dim(B.getUTCFullYear(), pm); }
  if (m < 0) { y--; m += 12; }
  return { y, m, d };
}
const norm = o => { let { y, m, d } = o; m += Math.floor(d / 30); d %= 30; y += Math.floor(m / 12); m %= 12; return { y, m, d }; };
const add = (a, b) => ({ y: a.y + b.y, m: a.m + b.m, d: a.d + b.d });
const txt = o => `${o.y ? o.y + "년 " : ""}${o.m ? o.m + "개월 " : ""}${o.d || (!o.y && !o.m) ? o.d + "일" : ""}`.trim();
const today = () => { const t = new Date(); return Date.UTC(t.getFullYear(), t.getMonth(), t.getDate()) / DAY; };
const iso = n => new Date(n * DAY).toISOString().slice(0, 10);
let st = ld(KEY) || { ref: "", inc: true, mrg: true, jobs: [{ n: "", s: "", e: "", cur: false, p: 100 }] };
if (!st.ref) st.ref = iso(today());
function save() { sv(KEY, st); }
function render() {
  $("ref").value = st.ref; $("inc").checked = st.inc; $("mrg").checked = st.mrg;
  $("list").innerHTML = st.jobs.map((j, i) => `<div class="card job" data-i="${i}"><div class="top"><input type="text" data-f="n" maxlength="20" placeholder="회사·기관 이름 (예: ○○회사)" value="${esc(j.n)}"><button type="button" class="btn ghost sm" data-del="${i}">삭제</button></div>
    <div class="row"><div><label class="muted">입사일</label><input type="date" data-f="s" value="${esc(j.s)}"></div><div><label class="muted">퇴사일</label><input type="date" data-f="e" value="${esc(j.e)}"${j.cur ? " disabled" : ""}></div></div>
    <div class="row3"><label class="mini"><input type="checkbox" data-f="cur"${j.cur ? " checked" : ""}> 현재 재직 중</label><label class="mini">인정 비율 <input type="number" class="pc" data-f="p" min="0" max="100" value="${j.p}"> %</label></div>
    <div class="dur" data-d="${i}"></div></div>`).join("");
  calc();
}
function range(j) {
  const s = toD(j.s); if (s == null) return null;
  const e0 = j.cur ? toD(st.ref) : toD(j.e); if (e0 == null) return null;
  const e = e0 + (st.inc ? 1 : 0); return { s, e };
}
function calc() {
  const items = [];
  st.jobs.forEach((j, i) => {
    const el = document.querySelector(`[data-d="${i}"]`), r = range(j);
    if (!r) { if (el) el.textContent = ""; return; }
    if (r.e <= r.s) { if (el) el.innerHTML = `<span class="bad">날짜를 확인해 주세요 (퇴사일이 입사일보다 빨라요)</span>`; return; }
    const o = norm(ymd(r.s, r.e)); if (el) el.textContent = `${txt(o)} · ${r.e - r.s}일`;
    items.push({ ...r, o, name: j.n || `경력 ${i + 1}`, p: clamp(+j.p || 0, 0, 100) });
  });
  if (!items.length) { $("res").innerHTML = `<p class="muted">입사일과 퇴사일을 입력하면 계산 결과가 나와요.</p>`; return; }
  let segs = items.map(x => ({ s: x.s, e: x.e })).sort((a, b) => a.s - b.s), merged = [];
  for (const s of segs) { const l = merged[merged.length - 1]; if (l && s.s <= l.e) l.e = Math.max(l.e, s.e); else merged.push({ ...s }); }
  const base = st.mrg ? merged : items;
  let tot = { y: 0, m: 0, d: 0 }, days = 0;
  base.forEach(x => { tot = add(tot, ymd(x.s, x.e)); days += x.e - x.s; });
  tot = norm(tot);
  const overlap = items.reduce((a, x) => a + (x.e - x.s), 0) - merged.reduce((a, x) => a + (x.e - x.s), 0);
  let h = `<div class="muted" style="text-align:center">총 경력${st.mrg ? " (중복 제외)" : " (단순 합산)"}</div><div class="big">${txt(tot)}</div><div class="muted" style="text-align:center">총 ${days.toLocaleString()}일 · 약 ${(days / 365.25).toFixed(1)}년</div>`;
  h += `<table class="tbl" style="margin-top:10px">` + items.map(x => `<tr><td>${esc(x.name)}${x.p < 100 ? ` <span class="muted">(${x.p}%)</span>` : ""}</td><td>${fmt(x.s)} ~ ${fmt(x.e - (st.inc ? 1 : 0))}</td><td>${txt(x.o)}</td></tr>`).join("") + `</table>`;
  if (overlap > 0) h += `<p class="muted">겹치는 기간 ${overlap}일${st.mrg ? "은 한 번만 계산했어요." : "이 있지만 단순 합산이라 그대로 더했어요."}</p>`;
  if (merged.length > 1) { const gaps = []; for (let k = 1; k < merged.length; k++) gaps.push({ s: merged[k - 1].e, e: merged[k].s }); h += `<div class="sec" style="margin-top:6px"><b>⏳ 공백 기간</b><table class="tbl">` + gaps.map(g => `<tr><td>${fmt(g.s)} ~ ${fmt(g.e - 1)}</td><td>${txt(norm(ymd(g.s, g.e)))} (${g.e - g.s}일)</td></tr>`).join("") + `</table></div>`; }
  if (items.some(x => x.p < 100)) { const wd = Math.round(items.reduce((a, x) => a + (x.e - x.s) * x.p / 100, 0)), y = Math.floor(wd / 365), r = wd - y * 365, m = Math.floor(r / 30); h += `<p><b>인정 비율 반영</b> (겹침 제외 없이 합산): 약 <b>${txt({ y, m, d: r % 30 })}</b> (${wd}일)</p>`; }
  h += `<button class="btn sm" id="cp" type="button">📋 결과 복사</button><p class="muted">일반적인 방식(해당 월은 달력대로, 일수 합산 시 30일=1개월, 12개월=1년)으로 계산해요. 기관마다 인정 기준이 다를 수 있으니 제출 전에는 해당 기관 기준을 꼭 확인하세요.</p>`;
  $("res").innerHTML = h;
  $("cp").onclick = () => { const t = "총 경력: " + txt(tot) + ` (${days}일)\n` + items.map(x => `${x.name} ${fmt(x.s)}~${fmt(x.e - (st.inc ? 1 : 0))} ${txt(x.o)}`).join("\n"); try { navigator.clipboard.writeText(t).then(() => { $("cp").textContent = "✅ 복사했어요"; }, () => { $("cp").textContent = "복사 실패"; }); } catch (e) { $("cp").textContent = "복사 실패"; } };
}
$("ref").onchange = () => { st.ref = $("ref").value || iso(today()); save(); calc(); };
$("inc").onchange = () => { st.inc = $("inc").checked; save(); calc(); };
$("mrg").onchange = () => { st.mrg = $("mrg").checked; save(); calc(); };
$("add").onclick = () => { st.jobs.push({ n: "", s: "", e: "", cur: false, p: 100 }); save(); render(); };
$("list").addEventListener("input", e => { const f = e.target.dataset.f, i = +e.target.closest("[data-i]").dataset.i; if (!f) return; const j = st.jobs[i]; if (f === "cur") { j.cur = e.target.checked; save(); render(); return; } j[f] = f === "p" ? e.target.value : e.target.value; save(); calc(); });
$("list").addEventListener("click", e => { const b = e.target.closest("[data-del]"); if (!b) return; st.jobs.splice(+b.dataset.del, 1); if (!st.jobs.length) st.jobs.push({ n: "", s: "", e: "", cur: false, p: 100 }); save(); render(); });
render();
'''
make("out/career-calc.html", "경력 계산기", "💼", 215, "career-calc-v1",
     "이력서·경력증명서에 쓰는 총 경력을 계산해요. 여러 직장의 근무 기간을 합산하고, 겹치는 기간과 공백 기간도 알려 줘요. 입력한 내용은 이 폰에만 저장돼요.", BODY, JS, CSS)
