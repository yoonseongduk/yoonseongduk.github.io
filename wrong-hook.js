// 퀴즈에서 틀린 문제를 자동으로 오답 노트(wrong-notes.html)에 모아 주는 작은 도우미예요.
(() => {
  const KEY = "wrongnotes-v1", MKEY = "wrongnotes-mastered-v1";
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } };
  const save = a => { try { localStorage.setItem(KEY, JSON.stringify(a.slice(-600))); } catch (e) {} };
  const mastered = () => { try { return +localStorage.getItem(MKEY) || 0; } catch (e) { return 0; } };
  const addMastered = () => { try { localStorage.setItem(MKEY, String(mastered() + 1)); } catch (e) {} };
  const file = location.pathname.split("/").pop() || "index.html";
  const h1 = document.querySelector("h1"), title = h1 ? h1.textContent.replace(/\s+\S+$/, "").trim() || h1.textContent.trim() : file;
  const idOf = (f, q, a) => f + "|" + q + "|" + a;
  function right(id) { const a = load(), k = a.findIndex(x => x.id === id); if (k < 0) return; a[k].s = (a[k].s || 0) + 1; if (a[k].s >= 2) { a.splice(k, 1); addMastered(); } save(a); }
  function wrong(it) { const a = load(), k = a.findIndex(x => x.id === it.id); if (k >= 0) { a[k].n = (a[k].n || 1) + 1; a[k].s = 0; a[k].d = Date.now(); a[k].o = it.o || a[k].o; } else a.push({ ...it, n: 1, s: 0, d: Date.now() }); save(a); }
  window.WrongNotes = {
    load, save, mastered,
    add(it) { wrong({ id: idOf(it.f || file, it.q, it.a), f: it.f || file, t: it.t || title, q: it.q, a: it.a, o: it.o || null, k: it.k || "mc" }); badge(); },
    fix(f, q, a) { right(idOf(f, q, a)); right(idOf(f, q, a)); badge(); }
  };
  function badge() {
    const main = document.querySelector("main"); if (!main) return; let p = document.getElementById("wnLink");
    if (!p) { p = document.createElement("p"); p.id = "wnLink"; p.className = "muted"; p.style.textAlign = "center"; main.appendChild(p); }
    const n = load().length; p.innerHTML = `<a href="wrong-notes.html" style="color:inherit;font-weight:700">📕 오답 노트${n ? " (" + n + "문제)" : ""}</a> — 틀린 문제를 모아서 복습해요`;
  }
  const text = el => el ? el.textContent.replace(/\s+/g, " ").trim() : "";
  let snap = null;
  // 눌리기 직전(캡처 단계)에 문제와 보기를 저장해 둔다 — 정답이 공개되기 전 모습
  document.addEventListener("click", e => {
    const b = e.target.closest(".opt"); if (!b || b.disabled) { snap = null; return; }
    const qEl = document.getElementById("q"); if (!qEl) { snap = null; return; }
    const c = qEl.cloneNode(true); c.querySelectorAll(".note,.eg,.hanja").forEach(x => x.remove());
    snap = { q: text(c), o: [...document.querySelectorAll(".opt")].map(text), picked: text(b) };
  }, true);
  document.addEventListener("click", e => {
    const b = e.target.closest(".opt"); if (!b || !snap) return; const s = snap; snap = null;
    const okEl = document.querySelector(".opt.ok"); if (!okEl) return; const a = text(okEl), id = idOf(file, s.q, a);
    if (b.classList.contains("bad")) wrong({ id, f: file, t: title, q: s.q, a, o: s.o, k: "mc" }); else if (b.classList.contains("ok")) right(id);
    badge();
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", badge); else badge();
})();
