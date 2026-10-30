import sys, json, random, datetime
sys.path.insert(0, ".")
from mkpage import make
from mkquiz import make as mkq

# ---------------- 요일 맞히기 (요일은 파이썬 달력으로 정확하게 계산해서 넣는다) ----------------
random.seed(20261030)
DAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
special = [(1945, 8, 15, "광복절"), (1950, 6, 25, ""), (1988, 9, 17, "서울 올림픽 개막일"), (2002, 6, 4, "월드컵 한국 첫 경기일"), (2000, 1, 1, ""), (2024, 12, 25, "크리스마스"), (2026, 1, 1, "새해 첫날"), (2026, 5, 5, "어린이날"), (2026, 10, 9, "한글날"), (2025, 3, 1, "삼일절"), (2023, 10, 3, "개천절"), (2030, 1, 1, "")]
items, seen = [], set()
for y, m, d, note in special:
    dt = datetime.date(y, m, d); items.append((dt, note))
while len(items) < 140:
    y = random.randint(1990, 2040); m = random.randint(1, 12); d = random.randint(1, 28)
    if (y, m, d) in seen: continue
    seen.add((y, m, d)); items.append((datetime.date(y, m, d), ""))
data = []
for dt, note in items:
    ans = DAYS[dt.weekday()]; wrong = random.sample([x for x in DAYS if x != ans], 3)
    data.append([f"{dt.year}년 {dt.month}월 {dt.day}일" + (f" ({note})" if note else ""), ans, wrong])
mkq("out/weekday-quiz.html", "요일 맞히기", "📆", 8, "weekday-quiz-best-v1", "그 날짜가 무슨 요일인지 맞혀 보세요. 날짜를 보고 '달력'을 머릿속으로 그려 보는 게임이에요.", data, label="무슨 요일일까요?")

# ---------------- 시계 읽기 ----------------
make("out/clock-quiz.html", "시계 읽기", "🕒", 215, "clockquiz-best-v1",
     "시계 그림을 보고 <b>몇 시 몇 분</b>인지 골라 보세요. 짧은 바늘이 '시', 긴 바늘이 '분'을 가리켜요. 쉬움은 5분 단위, 어려움은 1분 단위예요.",
     r'''  <div class="seg" id="lv" role="radiogroup" aria-label="난이도"></div>
  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="clockbox"><canvas id="cv" width="640" height="640" aria-label="시계 그림"></canvas></div>
  <div class="opts" id="opts"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>''',
     r'''const LV = { easy: { step: 5, label: "쉬움", hint: "5분 단위" }, hard: { step: 1, label: "어려움", hint: "1분 단위" } }, ROUND = 10;
let lv = (ld(KEY + "-lv") in LV) ? ld(KEY + "-lv") : "easy", qs, i, score, locked, best = ld(KEY) || {};
const label = (h, m) => `${h}시 ${m ? m + "분" : "정각"}`;
// 시침과 분침의 각도 (12시 방향이 0도, 시계 방향). 시침은 분이 지난 만큼도 조금 더 간다
const angles = (h, m) => ({ hour: ((h % 12) + m / 60) * 30, min: m * 6 });
function makeQ() {
  const step = LV[lv].step, h = ri(1, 12), m = ri(0, 59 / step | 0) * step, ans = label(h, m), set = new Set([ans]);
  while (set.size < 4) { const t = Math.random(); let hh = h, mm = m; if (t < .35) hh = ri(1, 12); else if (t < .7) mm = ri(0, 59 / step | 0) * step; else { hh = ri(1, 12); mm = ri(0, 59 / step | 0) * step; } set.add(label(hh, mm)); }
  return { h, m, ans, opts: shuf([...set]) };
}
function start() { qs = Array.from({ length: ROUND }, makeQ); i = 0; score = 0; $("res").hidden = true; show(); }
function drawClock(h, m) {
  const c = $("cv").getContext("2d"), R = 300, css = getComputedStyle(document.documentElement), fg = css.getPropertyValue("--fg").trim(), line = css.getPropertyValue("--line").trim(), acc = css.getPropertyValue("--accent").trim(), sf = css.getPropertyValue("--surface").trim();
  c.clearRect(0, 0, 640, 640); c.save(); c.translate(320, 320); c.fillStyle = sf; c.beginPath(); c.arc(0, 0, R, 0, 7); c.fill(); c.lineWidth = 10; c.strokeStyle = fg; c.stroke();
  for (let k = 0; k < 60; k++) { const a = k * 6 * Math.PI / 180, len = k % 5 ? 12 : 28; c.strokeStyle = k % 5 ? line : fg; c.lineWidth = k % 5 ? 3 : 6; c.beginPath(); c.moveTo(Math.sin(a) * (R - 8), -Math.cos(a) * (R - 8)); c.lineTo(Math.sin(a) * (R - 8 - len), -Math.cos(a) * (R - 8 - len)); c.stroke(); }
  c.fillStyle = fg; c.font = "bold 54px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; for (let n = 1; n <= 12; n++) { const a = n * 30 * Math.PI / 180; c.fillText(n, Math.sin(a) * (R - 68), -Math.cos(a) * (R - 68)); }
  const A = angles(h, m); const hand = (deg, len, w, col) => { const a = deg * Math.PI / 180; c.strokeStyle = col; c.lineWidth = w; c.lineCap = "round"; c.beginPath(); c.moveTo(-Math.sin(a) * 20, Math.cos(a) * 20); c.lineTo(Math.sin(a) * len, -Math.cos(a) * len); c.stroke(); };
  hand(A.hour, 150, 16, fg); hand(A.min, 220, 10, acc); c.fillStyle = fg; c.beginPath(); c.arc(0, 0, 14, 0, 7); c.fill(); c.restore();
}
function show() { const q = qs[i]; locked = false; $("next").hidden = true; drawClock(q.h, q.m); $("opts").innerHTML = q.opts.map((o, k) => `<button class="opt" type="button" data-k="${k}">${o}</button>`).join(""); $("no").textContent = (i + 1) + "/" + ROUND; $("score").textContent = score; $("best").textContent = best[lv] || 0; $("lv").style.setProperty("--n", 2); $("lv").innerHTML = Object.keys(LV).map(k => `<button type="button" class="${k === lv ? "on" : ""}" data-l="${k}" role="radio" aria-checked="${k === lv}">${LV[k].label}<small>${LV[k].hint}</small></button>`).join(""); }
function pick(k) { if (locked) return; locked = true; const q = qs[i]; if (q.opts[k] === q.ans) score++; document.querySelectorAll(".opt").forEach((b, n) => { b.disabled = true; if (q.opts[n] === q.ans) b.classList.add("ok"); else if (n === k) b.classList.add("bad"); }); $("score").textContent = score; $("next").textContent = i === ROUND - 1 ? "결과 보기" : "다음 문제"; $("next").hidden = false; }
function finish() { let note = ""; if (score > (best[lv] || 0)) { best[lv] = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("opts").innerHTML = ""; $("next").hidden = true; $("res").innerHTML = `<b>${ROUND}문제 중 ${score}개 정답</b><p class="muted">${score >= 9 ? "시계 박사님! 🎓" : score >= 6 ? "잘했어요 👍" : "조금만 더 연습해 봐요 💪"}${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("res").hidden = false; $("best").textContent = best[lv]; $("again").onclick = start; }
$("opts").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) pick(+b.dataset.k); }); $("next").onclick = () => { if (i === ROUND - 1) finish(); else { i++; show(); } };
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b && b.dataset.l !== lv) { lv = b.dataset.l; sv(KEY + "-lv", lv); start(); } }); start();''',
     css=".clockbox{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:12px;display:grid;place-items:center}.clockbox canvas{width:min(100%,300px);aspect-ratio:1}.opts{display:grid;grid-template-columns:1fr 1fr;gap:10px}.opt{background:var(--surface);border:2px solid var(--line);border-radius:14px;min-height:58px;padding:8px;font-weight:700;font-size:1.1rem}.opt.ok{border-color:var(--ok);background:color-mix(in srgb,var(--ok) 16%,var(--surface))}.opt.bad{border-color:var(--bad);background:color-mix(in srgb,var(--bad) 14%,var(--surface))}.opt:disabled{cursor:default}")

# ---------------- 크기 비교 ----------------
make("out/size-compare.html", "크기 비교", "⚖️", 330, "sizecompare-best-v1",
     "왼쪽과 오른쪽 계산 중 <b>값이 더 큰 쪽</b>을 재빨리 누르세요. 30초 동안 몇 개나 맞히는지 겨뤄요. 틀리면 시간이 2초 줄어요. (컴퓨터: ← → 키)",
     r'''  <div class="bar"><i id="bar"></i></div>
  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">30</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="vs" id="vs"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
     r'''const DUR = 30;
let score = 0, best = ld(KEY) || 0, endAt = 0, timer = 0, state = "idle", cur = null, lock = false, hits = 0, tried = 0;
// 두 식을 만든다. 값이 같으면 다시 만든다. 점수가 오를수록 값이 비슷해진다
function expr() { const t = ri(0, 2); if (t === 0) { const a = ri(2, 9), b = ri(2, 9); return { t: `${a} × ${b}`, v: a * b }; } if (t === 1) { const a = ri(10, 60), b = ri(10, 60); return { t: `${a} + ${b}`, v: a + b }; } const a = ri(40, 99), b = ri(5, 39); return { t: `${a} − ${b}`, v: a - b }; }
function makePair(level) { for (;;) { const x = expr(), y = expr(); const gap = Math.abs(x.v - y.v); if (x.v !== y.v && gap <= Math.max(3, 40 - level * 3)) return [x, y]; } }
const bigger = p => (p[0].v > p[1].v ? 0 : 1);
function nextQ() { cur = makePair(score); lock = false; $("vs").innerHTML = cur.map((e, k) => `<button type="button" class="ex" data-k="${k}">${e.t}</button>`).join(`<span class="vsm">VS</span>`); }
function tick() { const left = Math.max(0, (endAt - Date.now()) / 1000); $("time").textContent = Math.ceil(left); $("bar").style.width = (left / DUR * 100) + "%"; if (!left) finish(); }
function start() { score = 0; hits = 0; tried = 0; state = "play"; $("res").hidden = true; $("start").hidden = true; endAt = Date.now() + DUR * 1000; clearInterval(timer); timer = setInterval(tick, 100); $("score").textContent = 0; nextQ(); tick(); }
function pick(k) {
  if (state !== "play" || lock) return; lock = true; tried++; const ok = k === bigger(cur), btn = document.querySelector(`[data-k="${k}"]`);
  if (ok) { score++; hits++; $("score").textContent = score; btn.classList.add("good"); } else { endAt -= 2000; btn.classList.add("bad"); document.querySelector(`[data-k="${bigger(cur)}"]`).classList.add("good"); }
  setTimeout(() => { if (state === "play") nextQ(); }, ok ? 120 : 380); tick();
}
function finish() { clearInterval(timer); state = "over"; $("time").textContent = 0; $("bar").style.width = "0%"; let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("best").textContent = best; $("vs").innerHTML = ""; $("res").innerHTML = `<b>${score}개 맞혔어요!</b><p class="muted">${tried}번 중 ${hits}번 정답${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; }
$("vs").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) pick(+b.dataset.k); });
document.addEventListener("keydown", e => { if (e.key === "ArrowLeft") pick(0); else if (e.key === "ArrowRight") pick(1); });
$("start").onclick = start; $("best").textContent = best;''',
     css=".bar{height:10px;background:var(--line);border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;width:100%;background:var(--accent)}.vs{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center;min-height:170px}.ex{min-height:160px;border:3px solid var(--line);border-radius:22px;background:var(--surface);font-family:var(--font-display);font-size:clamp(1.8rem,9vw,2.6rem);padding:6px}.ex.good{border-color:var(--ok);background:color-mix(in srgb,var(--ok) 16%,var(--surface))}.ex.bad{border-color:var(--bad);background:color-mix(in srgb,var(--bad) 14%,var(--surface))}.vsm{font-family:var(--font-display);color:var(--muted)}")

# ---------------- 다른 그림 찾기 ----------------
make("out/odd-emoji.html", "다른 그림 찾기", "🔍", 255, "oddemoji-best-v1",
     "같은 그림들 사이에 숨어 있는 <b>모양이 조금 다른 그림 하나</b>를 찾아서 누르세요. 맞히면 다음 단계(그림이 더 많아져요). 30초 안에 최대한 높은 단계까지 가 보세요. 틀리면 시간이 3초 줄어요.",
     r'''  <div class="bar"><i id="bar"></i></div>
  <div class="stats"><div class="stat"><small>남은 시간</small><b id="time">30</b></div><div class="stat"><small>단계</small><b id="stage">1</b></div><div class="stat"><small>최고 단계</small><b id="best">0</b></div></div>
  <div class="grid" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
     r'''const DUR = 30, PAIRS = [["😀", "😃"], ["🌕", "🌖"], ["🔺", "🔻"], ["◀️", "▶️"], ["🟥", "🟧"], ["🐻", "🐼"], ["⭐", "🌟"], ["🍎", "🍅"], ["🐶", "🐕"], ["🕐", "🕑"], ["🌑", "🌘"], ["🔵", "🟣"]];
let stage = 1, odd = 0, endAt = 0, timer = 0, state = "idle", best = ld(KEY) || 0, lock = false;
const size = s => Math.min(6, 2 + Math.floor((s + 2) / 3));                    // 단계가 오르면 칸이 늘어난다 (최대 6×6)
function round() { const n = size(stage), pr = PAIRS[ri(0, PAIRS.length - 1)], flip = Math.random() < .5, [a, b] = flip ? [pr[1], pr[0]] : pr; odd = ri(0, n * n - 1); lock = false;
  $("grid").style.gridTemplateColumns = `repeat(${n}, 1fr)`; $("grid").style.fontSize = (n <= 3 ? 2.8 : n === 4 ? 2.3 : n === 5 ? 1.9 : 1.6) + "rem"; $("grid").innerHTML = Array.from({ length: n * n }, (_, i) => `<button type="button" class="e" data-i="${i}" aria-label="그림 ${i + 1}">${i === odd ? b : a}</button>`).join(""); $("stage").textContent = stage; }
function tick() { const left = Math.max(0, (endAt - Date.now()) / 1000); $("time").textContent = Math.ceil(left); $("bar").style.width = (left / DUR * 100) + "%"; if (!left) finish(); }
function start() { stage = 1; state = "play"; $("res").hidden = true; $("start").hidden = true; $("grid").style.opacity = 1; endAt = Date.now() + DUR * 1000; clearInterval(timer); timer = setInterval(tick, 100); round(); tick(); }
function pick(i, el) { if (state !== "play" || lock) return; if (i === odd) { stage++; round(); } else { lock = true; endAt -= 3000; el.classList.add("bad"); document.querySelector(`[data-i="${odd}"]`).classList.add("ok"); setTimeout(() => { if (state === "play") round(); }, 450); tick(); } }
function finish() { clearInterval(timer); state = "over"; $("time").textContent = 0; $("bar").style.width = "0%"; let note = ""; if (stage > best) { best = stage; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("best").textContent = best; $("res").innerHTML = `<b>${stage}단계까지 갔어요!</b><p class="muted">${stage >= 15 ? "눈이 정말 좋아요 🦅" : stage >= 9 ? "대단해요 👏" : "한 번 더 도전해 볼까요?"}${note}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; }
$("grid").addEventListener("pointerdown", e => { const b = e.target.closest("[data-i]"); if (b) { e.preventDefault(); pick(+b.dataset.i, b); } });
$("start").onclick = start; $("best").textContent = best; round(); $("grid").style.opacity = .5;''',
     css=".bar{height:10px;background:var(--line);border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;width:100%;background:var(--accent)}.grid{display:grid;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:8px;touch-action:manipulation}.e{aspect-ratio:1;border:0;border-radius:10px;background:var(--soft);padding:0;line-height:1;font-family:'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif}.e.bad{outline:4px solid var(--bad)}.e.ok{outline:4px solid var(--ok)}")
