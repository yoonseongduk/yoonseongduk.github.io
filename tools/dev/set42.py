# 신고한 퀴즈 문제 화면 (quiz-flags.html) — 퀴즈에서 🚩로 신고한 문제를 모아 보고, 복사해서 개발자(Claude)에게 전달한다.
# 저장: quiz-flags-v1 = {퀴즈 파일: {문제: {a: 정답, p: 내가 고른 답, t: 시각}}} (퀴즈 공통 틀의 FLAG 패치가 씀, tools/dev/qlevel.py)
import sys
sys.path.insert(0, ".")
from mkpage import make

CSS = '''.it{padding:10px 0;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:4px}.it:last-child{border-bottom:0}
.it b{overflow-wrap:anywhere}.it .note{font-size:.85rem;color:var(--muted);overflow-wrap:anywhere}.rm{align-self:flex-start;background:transparent;border:1px solid var(--line);border-radius:999px;padding:3px 12px;font-size:.85rem}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:8px}'''

BODY = '''  <div class="card"><b id="sum">🚩 신고한 문제</b>
    <p class="muted">퀴즈에서 보기를 고른 뒤 나오는 "🚩 문제가 이상해요" 단추로 신고한 문제예요. 이 폰에만 저장되고, 신고한 문제는 이 폰에서 다시 나오지 않아요. 아래 복사 단추로 글을 복사해서 개발자에게 전달해 주세요.</p>
    <div class="row2"><button class="btn" id="copy" type="button">📋 전체 복사</button><button class="btn ghost" id="clear" type="button">🗑️ 모두 지우기</button></div>
    <div class="muted" id="msg" role="status"></div></div>
  <div id="list"></div>
'''

JS = r'''
// KEY·$·esc 는 공통 틀(mkpage)에 있어요
const fld = () => { try { const v = JSON.parse(localStorage.getItem(KEY)); return v && typeof v === "object" ? v : {}; } catch (e) { return {}; } };
const fsv = v => { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} };
const nm = f => f.replace(/\.html$/, "");
const day = t => { const d = new Date(t); return (d.getMonth() + 1) + "/" + d.getDate(); };
function rows() { const a = []; const all = fld(); Object.keys(all).forEach(f => Object.keys(all[f]).forEach(q => a.push({ f, q, ...all[f][q] }))); return a.sort((x, y) => y.t - x.t); }
function render() {
  const r = rows(); $("sum").textContent = "🚩 신고한 문제 " + r.length + "개";
  const g = {}; r.forEach(x => (g[x.f] = g[x.f] || []).push(x));
  $("list").innerHTML = r.length ? Object.keys(g).map(f => `<section class="card"><b>${esc(nm(f))} (${g[f].length})</b>${g[f].map(x => `<div class="it"><b>${esc(x.q)}</b><span class="note">정답으로 저장된 답: ${esc(x.a)} · 내가 고른 답: ${esc(x.p || "-")} · ${day(x.t)}</span><button class="rm" type="button" data-f="${esc(f)}" data-q="${esc(x.q)}">신고 취소</button></div>`).join("")}</section>`).join("") : `<div class="card muted">아직 신고한 문제가 없어요. 퀴즈에서 이상한 문제를 만나면 🚩를 눌러 주세요.</div>`;
}
function text() { const r = rows(); return "[퀴즈 문제 신고] 총 " + r.length + "개\n" + r.map(x => `${x.f} | ${x.q} | 정답: ${x.a} | 고른 답: ${x.p || "-"} | ${day(x.t)}`).join("\n"); }
$("list").addEventListener("click", e => { const b = e.target.closest(".rm"); if (!b) return; const all = fld(); if (all[b.dataset.f]) { delete all[b.dataset.f][b.dataset.q]; if (!Object.keys(all[b.dataset.f]).length) delete all[b.dataset.f]; fsv(all); } render(); });
$("copy").onclick = async () => {
  const t = text();
  try { await navigator.clipboard.writeText(t); $("msg").textContent = "복사했어요! 개발자에게 붙여넣어 주세요."; }
  catch (e) { const ta = document.createElement("textarea"); ta.value = t; document.body.appendChild(ta); ta.select(); try { document.execCommand("copy"); $("msg").textContent = "복사했어요! 개발자에게 붙여넣어 주세요."; } catch (e2) { $("msg").textContent = "복사가 안 돼요. 아래 글을 직접 선택해 복사해 주세요: " + t; } ta.remove(); }
};
$("clear").onclick = () => { if (confirm("신고한 문제를 모두 지울까요? (지우면 그 문제가 다시 나와요)")) { fsv({}); render(); $("msg").textContent = "모두 지웠어요."; } };
render();
'''
make("out/quiz-flags.html", "신고한 퀴즈 문제", "🚩", 0, "quiz-flags-v1", "문제가 이상할 때 신고하고 모아서 전달해요.", BODY, JS, CSS)
