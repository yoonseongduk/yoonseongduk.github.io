import sys, json
sys.path.insert(0, ".")
from mkpage import make
make("out/wrong-notes.html", "오답 노트", "📕", 355, "wrongnotes-ui-v1",
 "퀴즈에서 <b>틀린 문제</b>가 자동으로 여기에 모여요. <b>집중 복습</b>을 누르면 많이 틀린 문제부터 다시 풀어요. 복습에서 <b>두 번 연속 맞히면</b> 노트에서 사라져요 (익힌 문제로 표시). 퀴즈에서 그 문제를 다시 맞혀도 같은 방식으로 세어져요. 기록은 이 폰에만 저장돼요.",
 r'''  <div class="stats"><div class="stat"><small>틀린 문제</small><b id="cnt">0</b></div><div class="stat"><small>익힌 문제</small><b id="mas">0</b></div><div class="stat"><small>퀴즈 종류</small><b id="kinds">0</b></div></div>
  <div class="chips" id="chips"></div>
  <div id="rev" hidden><div class="card center"><p class="muted" id="rt"></p><p class="big" id="rq" style="font-size:1.5rem"></p></div><div class="opts" id="ro"></div><p class="center" id="rm" style="min-height:1.4em;font-weight:700"></p><button class="btn" id="rn" type="button" hidden>다음</button></div>
  <div class="row" id="acts"><button class="btn" id="go" type="button">🔥 집중 복습 (10문제)</button><button class="btn ghost" id="clear" type="button">🗑 모두 지우기</button></div>
  <div class="res" id="sum" hidden></div>
  <div class="card" id="listbox"><b>📋 틀린 문제 목록</b><div id="list"></div></div>''',
 r'''const KEY2 = "wrongnotes-v1", MKEY = "wrongnotes-mastered-v1";
const load = () => { try { return JSON.parse(localStorage.getItem(KEY2)) || []; } catch (e) { return []; } }, save = a => { try { localStorage.setItem(KEY2, JSON.stringify(a)); } catch (e) {} }, mastered = () => { try { return +localStorage.getItem(MKEY) || 0; } catch (e) { return 0; } }, addMastered = () => { try { localStorage.setItem(MKEY, String(mastered() + 1)); } catch (e) {} };
let items = load(), filt = "전체", q = [], qi = 0, good = 0, locked = false, tempo = 1;
const kinds = () => [...new Set(items.map(x => x.t))];
function chips() { const ks = kinds(); $("chips").innerHTML = ["전체", ...ks].map(k => `<button type="button" class="chip${k === filt ? " on" : ""}" data-k="${esc(k)}">${esc(k)} <small>${k === "전체" ? items.length : items.filter(x => x.t === k).length}</small></button>`).join(""); }
const view = () => items.filter(x => filt === "전체" || x.t === filt);
function render() {
  items = load(); if (filt !== "전체" && !items.some(x => x.t === filt)) filt = "전체"; chips(); $("cnt").textContent = items.length; $("mas").textContent = mastered(); $("kinds").textContent = kinds().length;
  const v = view().sort((a, b) => (b.n || 1) - (a.n || 1) || b.d - a.d);
  $("list").innerHTML = v.length ? v.map((x, k) => `<div class="wi"><div class="wh"><span class="muted">${esc(x.t)} · ${x.n || 1}번 틀림</span><button type="button" data-del="${esc(x.id)}" aria-label="삭제">✕</button></div><div class="wq">${esc(x.q)}</div><details><summary>정답 보기</summary><b class="wa">${esc(x.a)}</b>${x.k === "write" ? ' <a href="hanja-write.html">✍️ 쓰기 연습</a>' : ""}</details></div>`).join("") : '<p class="muted center" style="padding:14px 0">🎉 틀린 문제가 없어요! 퀴즈를 풀다 틀리면 여기에 모여요.</p>';
  $("go").disabled = !v.filter(x => x.k !== "write" && x.o).length; $("acts").hidden = false;
}
function startReview() {
  const pool = view().filter(x => x.k !== "write" && x.o && x.o.length >= 2); if (!pool.length) return;
  q = pool.map(x => ({ x, w: (x.n || 1) + Math.random() * 1.5 })).sort((a, b) => b.w - a.w).slice(0, 10).map(o => o.x); q = shuf(q); qi = 0; good = 0; $("sum").hidden = true; $("rev").hidden = false; $("acts").hidden = true; $("listbox").hidden = true; showQ();
}
function showQ() { const x = q[qi]; locked = false; $("rt").textContent = `${x.t} · ${qi + 1}/${q.length}`; $("rq").textContent = x.q; $("rm").textContent = ""; $("rn").hidden = true; $("ro").innerHTML = shuf(x.o).map((o, k) => `<button class="opt" type="button" data-o="${esc(o)}">${esc(o)}</button>`).join(""); }
function pick(b) {
  if (locked) return; locked = true; const x = q[qi], ok = b.dataset.o === x.a, all = load(), k = all.findIndex(y => y.id === x.id);
  document.querySelectorAll("#ro .opt").forEach(o => { o.disabled = true; if (o.dataset.o === x.a) o.classList.add("ok"); else if (o === b) o.classList.add("bad"); });
  if (ok) { good++; if (k >= 0) { all[k].s = (all[k].s || 0) + 1; if (all[k].s >= 2) { all.splice(k, 1); addMastered(); $("rm").textContent = "⭕ 두 번 맞혔어요! 익힌 문제로 옮겼어요 🎉"; } else $("rm").textContent = "⭕ 정답! 한 번 더 맞히면 익힌 문제예요"; } }
  else { if (k >= 0) { all[k].n = (all[k].n || 1) + 1; all[k].s = 0; all[k].d = Date.now(); } $("rm").textContent = "❌ 아쉬워요. 다시 도전해요"; }
  $("rm").style.color = ok ? "var(--ok)" : "var(--bad)"; save(all); $("rn").textContent = qi === q.length - 1 ? "결과 보기" : "다음"; $("rn").hidden = false;
}
function finish() { $("rev").hidden = true; $("acts").hidden = false; $("listbox").hidden = false; render(); $("sum").hidden = false; $("sum").innerHTML = `<b>복습 끝! ${q.length}문제 중 ${good}개 정답</b><p class="muted">${good === q.length ? "완벽해요 🎉" : "틀린 문제는 노트에 남아 있어요. 또 도전해요 💪"}</p>`; }
$("go").onclick = startReview; $("ro").addEventListener("click", e => { const b = e.target.closest("[data-o]"); if (b) pick(b); }); $("rn").onclick = () => { if (qi === q.length - 1) finish(); else { qi++; showQ(); } };
$("chips").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) { filt = b.dataset.k; render(); } });
$("list").addEventListener("click", e => { const d = e.target.closest("[data-del]"); if (d) { save(load().filter(x => x.id !== d.dataset.del)); render(); } });
$("clear").onclick = () => { if (confirm("오답 노트를 모두 지울까요?")) { save([]); render(); } }; render();''',
 css=".chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.88rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}.opts{display:grid;gap:8px}.opt{background:var(--surface);border:2px solid var(--line);border-radius:14px;min-height:54px;padding:8px 12px;font-weight:700;font-size:1rem;text-align:left}.opt.ok{border-color:var(--ok);background:color-mix(in srgb,var(--ok) 16%,var(--surface))}.opt.bad{border-color:var(--bad);background:color-mix(in srgb,var(--bad) 14%,var(--surface))}.wi{padding:10px 0;border-bottom:1px solid var(--line)}.wh{display:flex;justify-content:space-between;align-items:center}.wh button{width:28px;height:28px;border-radius:50%;border:1px solid var(--line);background:var(--soft);padding:0}.wq{margin:4px 0;overflow-wrap:anywhere}details summary{color:var(--accent);cursor:pointer;font-size:.9rem}.wa{color:var(--ok)}")
