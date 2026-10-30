import sys, json, re, csv, ast
sys.path.insert(0, ".")
# 데이터: 한자 3500자를 별도 파일로 (쓰기 퀴즈 전용)
exec(open("set18.py", encoding="utf-8").read().split("print(len(D)")[0].replace('make("out/hanja-quiz.html"', 'make = None #'))
data = [[d[0], d[1], d[3], d[4]] for d in D]
import os
os.makedirs("out/yoonseongduk.github.io/data", exist_ok=True)
json.dump(data, open("out/yoonseongduk.github.io/data/hanja.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
from mkpage import make
print("hanja.json", len(data), os.path.getsize("out/yoonseongduk.github.io/data/hanja.json"))

make("out/hanja-write.html", "한자 쓰기", "✍️", 8, "hanja-write-best-v1",
 "화면의 네모 칸에 <b>손가락으로 한자를 써 보세요</b>. <b>따라 쓰기</b>는 연하게 보이는 한자를 따라 쓰고, <b>보고 쓰기</b>는 뜻과 음만 보고 기억해서 써요. <b>확인</b>을 누르면 쓴 모양과 정답 모양이 얼마나 겹치는지 계산해요 (AI가 아니라 모양 비교예요). 획순은 검사하지 않아요.",
 r'''  <div class="chips" id="cats"></div>
  <div class="seg" id="mode" style="--n:2"><button type="button" data-m="trace" class="on">따라 쓰기<small>연한 글자를 따라</small></button><button type="button" data-m="memo">보고 쓰기<small>뜻과 음만 보고</small></button></div>
  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>성공</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="muted" id="ask"></p><p class="big" id="mean" style="font-size:1.8rem"></p></div>
  <div class="padwrap"><canvas id="pad" width="300" height="300" aria-label="한자를 쓰는 칸"></canvas></div>
  <div class="row3"><button class="btn ghost" id="undo" type="button">↩ 한 획 지우기</button><button class="btn ghost" id="clear" type="button">🧽 모두 지우기</button><button class="btn" id="check" type="button">확인</button></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>''',
 r'''let ALL = [], pool = [], cat = "6급", mode = "trace", qs = [], i = 0, score = 0, best = ld(KEY) || 0, strokes = [], cur = null, done = false, guideCache = null;
const cv = $("pad"), ctx = cv.getContext("2d"), S = 300, G = 60, CELL = S / G, FONT = '"Noto Serif CJK KR","Noto Serif KR","Noto Sans CJK KR","Noto Sans KR","Malgun Gothic","Apple SD Gothic Neo","AppleGothic","Batang","serif"';
fetch("data/hanja.json").then(r => r.json()).then(d => { ALL = d; chips(); start(); }).catch(() => { $("ask").textContent = "한자 자료를 불러오지 못했어요. 인터넷에 한 번 연결한 뒤 다시 열어 주세요."; });
function chips() { $("cats").innerHTML = ["6급", "5급", "4급", "3급", "2급", "1급"].map(c => `<button type="button" class="chip${c === cat ? " on" : ""}" data-c="${c}">${c}</button>`).join(""); }
function start() { pool = ALL.filter(d => d[2] === cat); qs = shuf(pool).slice(0, 10); i = 0; score = 0; $("res").hidden = true; show(); }
function glyphCanvas(ch, scale = 1) { const c = document.createElement("canvas"); c.width = c.height = S; const x = c.getContext("2d"); x.fillStyle = "#000"; x.textAlign = "center"; x.textBaseline = "middle"; x.font = `${Math.round(S * .78 * scale)}px ${FONT}`; x.fillText(ch, S / 2, S / 2 + S * .04); return c; }
function drawStroke(x, pts, w, col) { x.strokeStyle = col; x.fillStyle = col; x.lineWidth = w; x.lineCap = x.lineJoin = "round"; if (pts.length === 1) { x.beginPath(); x.arc(pts[0][0], pts[0][1], w / 2, 0, 7); x.fill(); return; } x.beginPath(); pts.forEach(([a, b], k) => k ? x.lineTo(a, b) : x.moveTo(a, b)); x.stroke(); }
function render(overlay) {
  const d = qs[i], style = getComputedStyle(document.documentElement), fg = style.getPropertyValue("--fg").trim() || "#222", line = style.getPropertyValue("--line").trim() || "#ccc", surf = style.getPropertyValue("--surface").trim() || "#fff", acc = style.getPropertyValue("--accent").trim() || "#c4552b";
  ctx.clearRect(0, 0, S, S); ctx.fillStyle = surf; ctx.fillRect(0, 0, S, S); ctx.strokeStyle = line; ctx.lineWidth = 1; ctx.setLineDash([5, 5]); ctx.strokeRect(.5, .5, S - 1, S - 1); ctx.beginPath(); ctx.moveTo(S / 2, 0); ctx.lineTo(S / 2, S); ctx.moveTo(0, S / 2); ctx.lineTo(S, S / 2); ctx.stroke(); ctx.setLineDash([]);
  if (mode === "trace" || overlay) { ctx.globalAlpha = overlay ? .28 : .16; ctx.drawImage(glyphTinted(d[0], overlay ? "#d6453a" : fg), 0, 0); ctx.globalAlpha = 1; }
  strokes.forEach(s => drawStroke(ctx, s, 15, fg)); if (cur) drawStroke(ctx, cur, 15, fg);
}
function glyphTinted(ch, color) { const g = glyphCanvas(ch), c = document.createElement("canvas"); c.width = c.height = S; const x = c.getContext("2d"); x.drawImage(g, 0, 0); x.globalCompositeOperation = "source-in"; x.fillStyle = color; x.fillRect(0, 0, S, S); return c; }
function show() { const d = qs[i]; strokes = []; cur = null; done = false; $("res").hidden = true; $("next").hidden = true; $("check").hidden = false; $("undo").disabled = $("clear").disabled = false; const [hun, um] = d[1].split(" ").length > 1 ? [d[1].slice(0, d[1].lastIndexOf(" ")), d[1].slice(d[1].lastIndexOf(" ") + 1)] : [d[1], ""];
  $("ask").textContent = mode === "trace" ? "연하게 보이는 한자를 따라 써 보세요" : "이 뜻과 음의 한자를 써 보세요"; $("mean").textContent = d[1]; $("no").textContent = (i + 1) + "/10"; $("score").textContent = score; $("best").textContent = best; render(false); }
// 모양 비교: 60×60 칸으로 줄인 글자 마스크와 내가 쓴 마스크를 겹쳐 본다
function maskOf(canvasLike) { const t = document.createElement("canvas"); t.width = t.height = G; const x = t.getContext("2d"); x.drawImage(canvasLike, 0, 0, G, G); const px = x.getImageData(0, 0, G, G).data, m = new Uint8Array(G * G); for (let k = 0; k < G * G; k++) m[k] = px[k * 4 + 3] > 40 ? 1 : 0; return m; }
function inkCanvas() { const c = document.createElement("canvas"); c.width = c.height = S; const x = c.getContext("2d"); strokes.forEach(s => drawStroke(x, s, 15, "#000")); return c; }
function bbox(m) { let x0 = G, y0 = G, x1 = -1, y1 = -1; for (let k = 0; k < G * G; k++) if (m[k]) { const x = k % G, y = Math.floor(k / G); x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); } return x1 < 0 ? null : [x0, y0, x1, y1]; }
function normalize(u, g) { const bu = bbox(u), bg = bbox(g); if (!bu || !bg) return u; const sw = bg[2] - bg[0] + 1, sh = bg[3] - bg[1] + 1, uw = bu[2] - bu[0] + 1, uh = bu[3] - bu[1] + 1, sc = Math.min(sw / uw, sh / uh), out = new Uint8Array(G * G), cxu = (bu[0] + bu[2]) / 2, cyu = (bu[1] + bu[3]) / 2, cxg = (bg[0] + bg[2]) / 2, cyg = (bg[1] + bg[3]) / 2;
  for (let k = 0; k < G * G; k++) if (u[k]) { const x = k % G, y = Math.floor(k / G), nx = Math.round(cxg + (x - cxu) * sc), ny = Math.round(cyg + (y - cyu) * sc); if (nx >= 0 && nx < G && ny >= 0 && ny < G) out[ny * G + nx] = 1; } return out; }
function dilate(m, r) { const o = new Uint8Array(G * G); for (let k = 0; k < G * G; k++) if (m[k]) { const x = k % G, y = Math.floor(k / G); for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) { const nx = x + dx, ny = y + dy; if (nx >= 0 && nx < G && ny >= 0 && ny < G) o[ny * G + nx] = 1; } } return o; }
function compare(g, u, tol) { const du = dilate(u, tol), dg = dilate(g, tol); let gs = 0, gc = 0, us = 0, uc = 0; const ga = g.reduce((a, b) => a + b, 0), ua = u.reduce((a, b) => a + b, 0); for (let k = 0; k < G * G; k++) { if (g[k]) { gs++; if (du[k]) gc++; } if (u[k]) { us++; if (dg[k]) uc++; } } const cov = gs ? gc / gs : 0, pre = us ? uc / us : 0; return { cov, pre, area: ga ? ua / ga : 0, score: Math.round((cov + pre) / 2 * 100) }; }
function judge(ch, mode) { const g = maskOf(glyphCanvas(ch)); let u = maskOf(inkCanvas()); if (mode === "memo") u = normalize(u, g); const r = compare(g, u, 1); r.ok = (mode === "trace" ? r.cov >= .75 && r.pre >= .72 : r.cov >= .72 && r.pre >= .7) && r.area > .3 && r.area < 2.2; return r; }        // 까맣게 칠하거나 너무 적게 쓰면 실패
function check() {
  if (done) return; if (!strokes.length) { $("res").hidden = false; $("res").innerHTML = "<b>먼저 한자를 써 주세요</b>"; return; }
  done = true; const d = qs[i], r = judge(d[0], mode); render(true); $("check").hidden = true; $("undo").disabled = $("clear").disabled = true; if (r.ok) score++;
  $("res").hidden = false; $("res").innerHTML = `<b>${r.ok ? "⭕ 잘 썼어요!" : "❌ 조금 달라요"}</b><p class="muted">모양이 겹친 정도 ${r.score}% (정답 글자를 덮어서 보여 줘요)<br>${esc(d[0])} = ${esc(d[1])} · ${esc(d[3])}</p>${r.ok ? "" : '<button class="btn ghost" id="self" type="button" style="margin-top:8px;width:100%">그래도 내가 맞게 썼어요 (스스로 채점)</button>'}`;
  if (!r.ok && window.WrongNotes) WrongNotes.add({ f: "hanja-write.html", t: "한자 쓰기", q: "뜻과 음: " + d[1] + " (" + d[2] + ")", a: d[0], k: "write" });
  const s = $("self"); if (s) s.onclick = () => { score++; s.remove(); $("score").textContent = score; $("res").querySelector("b").textContent = "⭕ 스스로 채점: 맞게 썼어요!"; if (window.WrongNotes) WrongNotes.fix("hanja-write.html", "뜻과 음: " + d[1] + " (" + d[2] + ")", d[0]); };
  $("score").textContent = score; $("next").textContent = i === 9 ? "결과 보기" : "다음 문제"; $("next").hidden = false;
}
function finish() { let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("next").hidden = true; $("check").hidden = true; $("res").hidden = false; $("res").innerHTML = `<b>10문제 중 ${score}개 성공</b><p class="muted">${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("best").textContent = best; $("again").onclick = start; }
// 그리기 (손가락/마우스)
function pt(e) { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * S, (e.clientY - r.top) / r.height * S]; }
cv.addEventListener("pointerdown", e => { if (done) return; e.preventDefault(); cv.setPointerCapture(e.pointerId); cur = [pt(e)]; render(false); });
cv.addEventListener("pointermove", e => { if (!cur) return; e.preventDefault(); cur.push(pt(e)); render(false); });
["pointerup", "pointercancel"].forEach(ev => cv.addEventListener(ev, e => { if (!cur) return; strokes.push(cur); cur = null; render(false); }));
$("undo").onclick = () => { if (!done) { strokes.pop(); render(false); } }; $("clear").onclick = () => { if (!done) { strokes = []; render(false); } }; $("check").onclick = check;
$("next").onclick = () => { if (i === 9) finish(); else { i++; show(); } };
$("cats").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b) { cat = b.dataset.c; chips(); start(); } });
$("mode").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (!b) return; document.querySelectorAll("#mode button").forEach(x => x.classList.toggle("on", x === b)); mode = b.dataset.m; if (ALL.length) start(); });
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => ALL.length && render(done));''',
 css=".chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.92rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}.padwrap{display:flex;justify-content:center}#pad{width:100%;max-width:340px;aspect-ratio:1;border:2px solid var(--fg);border-radius:12px;touch-action:none;background:var(--surface)}.row3{display:grid;grid-template-columns:1fr 1fr 1.2fr;gap:8px}.row3 .btn{padding:12px 4px;font-size:1.05rem}")
