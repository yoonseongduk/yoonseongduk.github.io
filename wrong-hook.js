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
  function wrong(it) { const a = load(), k = a.findIndex(x => x.id === it.id); if (k >= 0) { a[k].n = (a[k].n || 1) + 1; a[k].s = 0; a[k].d = Date.now(); a[k].o = it.o || a[k].o; if (it.m) a[k].m = it.m; } else a.push({ ...it, n: 1, s: 0, d: Date.now() }); save(a); }
  window.WrongNotes = {
    load, save, mastered,
    add(it) { wrong({ id: idOf(it.f || file, it.q, it.a), f: it.f || file, t: it.t || title, q: it.q, a: it.a, o: it.o || null, k: it.k || "mc" }); badge(); },
    fix(f, q, a) { right(idOf(f, q, a)); right(idOf(f, q, a)); badge(); }
  };
  function badge() {
    const main = document.querySelector("main"); if (!main || file === "wrong-notes.html") return; let p = document.getElementById("wnLink");
    if (!p) { p = document.createElement("p"); p.id = "wnLink"; p.className = "muted"; p.style.textAlign = "center"; main.appendChild(p); }
    // 이 퀴즈에서 틀린 문제가 있으면 그 문제만 바로 보는 링크(wrong-notes.html?f=파일), 전체 노트 링크도 함께
    const all = load(), mine = all.filter(x => x.f === file).length, ls = "color:inherit;font-weight:700";
    p.innerHTML = mine ? `<a href="wrong-notes.html?f=${encodeURIComponent(file)}" style="${ls}">📕 이 퀴즈 오답 ${mine}문제 보기</a> · <a href="wrong-notes.html" style="color:inherit">전체 오답 노트(${all.length})</a>`
      : `<a href="wrong-notes.html" style="${ls}">📕 오답 노트${all.length ? " (" + all.length + "문제)" : ""}</a> — 틀린 문제를 모아서 복습해요`;
  }
  const text = el => el ? el.textContent.replace(/\s+/g, " ").trim() : "";
  let snap = null;
  // 눌리기 직전(캡처 단계)에 문제와 보기를 저장해 둔다 — 정답이 공개되기 전 모습
  document.addEventListener("click", e => {
    const b = e.target.closest(".opt"); if (!b || b.disabled) { snap = null; return; }
    const qEl = document.getElementById("q"); if (!qEl) { snap = null; return; }
    const c = qEl.cloneNode(true); c.querySelectorAll(".note,.eg,.hanja").forEach(x => x.remove());
    // 그림·소리·단추 같은 꾸밈(svg·img·audio·button이 든 덩어리)과 맨 앞의 퀴즈 이름 표시는 글자만 남기는 노트에서 뺀다(예전엔 "오케스트라 퀴즈도감 4번…💡 힌트…"처럼 뒤섞여 기록됐다)
    [...c.children].forEach(ch => { if (ch.matches("button,svg,img,audio,figure,canvas") || ch.querySelector("button,svg,img,audio,figure,canvas")) ch.remove(); else if (ch.tagName === "SMALL") { if ([title, text(h1)].includes(text(ch))) ch.remove(); else ch.after(" "); } });   // 분류 표시(<small>)는 문제 글과 붙지 않게 띄어 쓴다
    c.querySelectorAll("button,svg,img,audio,canvas").forEach(x => x.remove());
    let qt = text(c); try { const ex = typeof window.fgWrongText === "function" ? window.fgWrongText() : null; if (ex) qt = ex; } catch (er) {}   // 그림·소리 문제는 글로 풀어 쓴 문제로 바꿔 기록(화면 쪽 스크립트가 fgWrongText를 정의)
    let mm = null; try { mm = typeof window.fgWrongMedia === "function" ? window.fgWrongMedia() : null; } catch (er) {}   // 그림·소리·배치도 문제의 다시 보기 정보
    snap = { m: mm, q: qt, o: [...document.querySelectorAll(".opt")].map(text), picked: text(b) };
  }, true);
  document.addEventListener("click", e => {
    const b = e.target.closest(".opt"); if (!b || !snap) return; const s = snap; snap = null;
    const okEl = document.querySelector(".opt.ok"); if (!okEl) return; const a = text(okEl), id = idOf(file, s.q, a);
    if (b.classList.contains("bad")) wrong({ id, f: file, t: title, q: s.q, a, o: s.o, k: "mc", m: s.m || undefined }); else if (b.classList.contains("ok")) right(id);
    badge();
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", badge); else badge();
})();
