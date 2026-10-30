import sys, json
sys.path.insert(0, ".")
from mkpage import make

# ---------------- 패턴 기억 ----------------
make("out/pattern-memory.html", "패턴 기억", "🟦", 225, "patternmem-best-v1",
     "칸들이 <b>순서대로 반짝이는 것</b>을 잘 보고, 사라지면 같은 순서로 눌러 보세요. 맞힐 때마다 반짝이는 칸이 하나씩 늘어나요. 한 번 틀리면 끝! 단계가 오르면 판도 커져요.",
     r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lvl">1</b></div><div class="stat"><small>최고 단계</small><b id="best">0</b></div><div class="stat"><small>상태</small><b id="st" style="font-size:1.05rem">준비</b></div></div>
  <div class="pgrid" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="start" type="button">시작</button>''',
     r'''let level = 1, seq = [], pos = 0, state = "idle", best = ld(KEY) || 0, tempo = 1, gen = 0, n = 3;
const sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
const sizeFor = l => (l < 6 ? 3 : l < 13 ? 4 : 5);
function build() { n = sizeFor(level); $("grid").style.gridTemplateColumns = `repeat(${n}, 1fr)`; $("grid").innerHTML = Array.from({ length: n * n }, (_, i) => `<button type="button" class="pc" data-i="${i}" aria-label="칸 ${i + 1}"></button>`).join(""); }
function setStatus(t) { $("st").textContent = t; $("lvl").textContent = level; $("best").textContent = best; $("grid").classList.toggle("lock", state !== "input"); }
async function show() {
  const my = ++gen; state = "show"; pos = 0; build(); setStatus("잘 보세요"); await sleep(700);
  for (const i of seq) { if (my !== gen) return; const el = document.querySelector(`[data-i="${i}"]`); el.classList.add("lit"); await sleep(Math.max(260, 520 - level * 12)); el.classList.remove("lit"); await sleep(170); }
  if (my !== gen) return; state = "input"; setStatus("따라 눌러요");
}
function addStep() { seq.push(ri(0, sizeFor(level) ** 2 - 1)); }
function start() { level = 1; seq = []; $("res").hidden = true; $("start").hidden = true; for (let k = 0; k < 3; k++) addStep(); show(); }
async function press(i) {
  if (state !== "input") return; const el = document.querySelector(`[data-i="${i}"]`);
  if (seq[pos] !== i) { state = "over"; gen++; el.classList.add("bad"); const reached = level - 1; if (reached > best) { best = reached; sv(KEY, best); } setStatus("끝"); $("res").innerHTML = `<b>${reached}단계까지 성공!</b><p class="muted">${reached >= 10 ? "기억력 천재 🧠" : reached >= 5 ? "잘했어요 👍" : "다시 도전해 볼까요?"}</p>`; $("res").hidden = false; $("start").hidden = false; $("start").textContent = "다시 하기"; return; }
  el.classList.add("ok"); setTimeout(() => el.classList.remove("ok"), 160); pos++;
  if (pos === seq.length) { state = "wait"; setStatus("정답! 👍"); await sleep(800); level++; const oldN = n; if (sizeFor(level) !== oldN) seq = seq.map(() => ri(0, sizeFor(level) ** 2 - 1)); addStep(); show(); }
}
$("grid").addEventListener("pointerdown", e => { const c = e.target.closest("[data-i]"); if (c) { e.preventDefault(); press(+c.dataset.i); } });
$("start").onclick = start; build(); setStatus("준비");''',
     css=".pgrid{display:grid;gap:8px;padding:10px;background:var(--surface);border:1px solid var(--line);border-radius:18px;touch-action:manipulation}.pgrid.lock .pc{cursor:default}.pc{aspect-ratio:1;border:0;border-radius:14px;background:var(--soft);padding:0;transition:background .1s,transform .1s}.pc.lit{background:var(--accent);transform:scale(.92);box-shadow:0 0 18px var(--accent)}.pc.ok{background:var(--ok)}.pc.bad{background:var(--bad)}")

# ---------------- 묵찌빠 ----------------
make("out/mukjjippa.html", "묵찌빠", "✊", 10, "mukjjippa-v1",
     "먼저 <b>가위바위보</b>로 공격권을 정해요. 이긴 쪽이 공격이에요. 그다음 <b>묵(✊)·찌(✌️)·빠(✋)</b>를 내서 <b>공격하는 쪽과 같은 손이 나오면 공격하는 쪽이 이겨요!</b> 다른 손이 나오면 가위바위보처럼 이긴 쪽이 공격권을 가져가요.",
     r'''  <div class="stats"><div class="stat"><small>승</small><b id="w">0</b></div><div class="stat"><small>연승</small><b id="s">0</b></div><div class="stat"><small>패</small><b id="l">0</b></div></div>
  <div class="phase" id="phase" aria-live="polite"></div>
  <div class="stage"><div><div class="h" id="mine">❔</div><small>나</small></div><div class="vs">VS</div><div><div class="h" id="cpu">❔</div><small>컴퓨터</small></div></div>
  <div class="res" id="msg"><b>가위바위보로 공격권을 정해요</b></div>
  <div class="picks" id="picks"></div>
  <button class="btn ghost" id="reset" type="button">기록 지우기</button>''',
     r'''const HANDS = [{ e: "✊", rps: "바위", mjp: "묵" }, { e: "✌️", rps: "가위", mjp: "찌" }, { e: "✋", rps: "보", mjp: "빠" }];
let st = ld(KEY) || { w: 0, l: 0, s: 0 }, phase = "rps", att = null, round = 0;
const beats = (a, b) => (a - b + 3) % 3 === 2;                      // 바위(묵) > 가위(찌) > 보(빠) > 바위
// 한 판의 규칙: (단계, 내 손, 컴퓨터 손, 공격권) → 다음 단계와 결과
function rule(phase, me, cpu, att) {
  if (phase === "rps") { if (me === cpu) return { phase: "rps", att: null, text: "비겼어요! 다시 가위바위보" }; const a = beats(me, cpu) ? "me" : "cpu"; return { phase: "mjp", att: a, text: a === "me" ? "내가 이겼어요! 공격권은 나에게 있어요 ⚔️" : "컴퓨터가 이겼어요. 공격권은 컴퓨터에게 있어요 🛡️" }; }
  if (me === cpu) return { phase: "rps", att: null, end: att, text: att === "me" ? "🎉 묵찌빠! 내가 이겼어요" : "😢 묵찌빠! 컴퓨터가 이겼어요" };
  const a = beats(me, cpu) ? "me" : "cpu"; return { phase: "mjp", att: a, text: (a === att ? "공격권을 지켰어요" : "공격권이 넘어갔어요") + (a === "me" ? " (내게 있어요 ⚔️)" : " (컴퓨터에게 있어요 🛡️)") };
}
function play(me) {
  const cpu = ri(0, 2), r = rule(phase, me, cpu, att); round++; $("mine").textContent = HANDS[me].e; $("cpu").textContent = HANDS[cpu].e;
  if (r.end) { if (r.end === "me") { st.w++; st.s++; } else { st.l++; st.s = 0; } sv(KEY, st); }
  phase = r.phase; att = r.att; $("msg").innerHTML = `<b>${r.text}</b>`; render();
}
function render() {
  $("w").textContent = st.w; $("l").textContent = st.l; $("s").textContent = st.s;
  $("phase").innerHTML = phase === "rps" ? "✊✌️✋ 가위바위보로 공격권 정하기" : att === "me" ? "<b style='color:var(--ok)'>⚔️ 내가 공격!</b> 컴퓨터와 같은 손을 내면 이겨요" : "<b style='color:var(--bad)'>🛡️ 컴퓨터가 공격!</b> 컴퓨터와 다른 손을 내세요";
  $("picks").innerHTML = HANDS.map((h, i) => `<button class="pick" type="button" data-p="${i}"><span>${h.e}</span>${phase === "rps" ? h.rps : h.mjp}</button>`).join("");
}
$("picks").addEventListener("click", e => { const b = e.target.closest("[data-p]"); if (b) play(+b.dataset.p); });
$("reset").onclick = () => { st = { w: 0, l: 0, s: 0 }; sv(KEY, st); phase = "rps"; att = null; $("mine").textContent = $("cpu").textContent = "❔"; $("msg").innerHTML = "<b>기록을 지웠어요</b>"; render(); }; render();''',
     css=".phase{text-align:center;font-family:var(--font-display);font-size:1.25rem;min-height:1.8em}.stage{background:var(--surface);border:2px solid var(--line);border-radius:22px;padding:14px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;text-align:center;gap:6px}.stage .h{font-size:clamp(3.4rem,20vw,5rem);line-height:1.1}.stage small{color:var(--muted)}.stage .vs{color:var(--muted);font-family:var(--font-display)}.picks{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.pick{background:var(--surface);border:2px solid var(--line);border-radius:18px;padding:12px 4px;display:flex;flex-direction:column;align-items:center;gap:2px;font-weight:700;font-size:1.1rem}.pick span{font-size:clamp(2.4rem,14vw,3.4rem);line-height:1.1}.pick:active{transform:scale(.96);border-color:var(--accent)}")

# ---------------- 참참참 ----------------
make("out/cham-cham-cham.html", "참참참", "👉", 335, "chamcham-best-v1",
     "'참참참!' 소리에 맞춰 방향을 고르는 게임이에요. <b>공격</b>일 때는 손가락 방향(👈👉)을 골라 컴퓨터의 얼굴 방향과 <b>같으면</b> 내가 1점! <b>수비</b>일 때는 얼굴 방향을 골라 컴퓨터 손가락과 <b>달라야</b> 안 걸려요. 3점을 먼저 따면 이겨요. 방향은 1.5초 안에 골라야 해요!",
     r'''  <div class="stats" style="grid-template-columns:repeat(3,1fr)"><div class="stat"><small>나</small><b id="me">0</b></div><div class="stat"><small>라운드</small><b id="rd">0</b></div><div class="stat"><small>컴퓨터</small><b id="cp">0</b></div></div>
  <div class="stage2" id="stage" aria-live="polite"><div class="role" id="role">준비</div><div class="big" id="big">참참참!</div><div class="sub" id="sub">시작을 눌러 주세요</div></div>
  <div class="bar"><i id="bar"></i></div>
  <div class="row"><button class="dir" id="L" type="button" disabled>◀ 왼쪽</button><button class="dir" id="R" type="button" disabled>오른쪽 ▶</button></div>
  <button class="btn" id="start" type="button">시작</button>''',
     r'''let me = 0, cp = 0, rd = 0, state = "idle", attack = true, tempo = 1, pickTimer = 0, myPick = null, token = 0;
const ARROW = { L: "👈", R: "👉" }, HEAD = { L: "◀️", R: "▶️" }, NAME = { L: "왼쪽", R: "오른쪽" }, sleep = ms => new Promise(r => setTimeout(r, ms * tempo));
// 한 라운드의 결과: 공격하는 쪽의 손가락 방향과 수비하는 쪽의 얼굴 방향이 같으면 공격 성공
const hit = (finger, head) => finger === head;
function ui(role, big, sub) { $("role").textContent = role; $("big").innerHTML = big; $("sub").textContent = sub; $("me").textContent = me; $("cp").textContent = cp; $("rd").textContent = rd; }
async function round() {
  const my = ++token; rd++; attack = rd % 2 === 1; myPick = null; $("L").disabled = $("R").disabled = true; $("bar").style.width = "0%";
  ui(attack ? "⚔️ 공격 차례" : "🛡️ 수비 차례", "참", attack ? "컴퓨터의 얼굴 방향을 맞혀 손가락을 돌려요" : "컴퓨터의 손가락과 다른 쪽으로 얼굴을 돌려요");
  await sleep(550); if (my !== token) return; $("big").textContent = "참 참"; await sleep(550); if (my !== token) return; $("big").textContent = "참 참 참!"; await sleep(450); if (my !== token) return;
  state = "pick"; $("big").textContent = attack ? "👆 손가락!" : "🙂 얼굴!"; $("L").disabled = $("R").disabled = false; const t0 = performance.now(), total = 1500 * tempo;
  const iv = setInterval(() => { $("bar").style.width = Math.min(100, (performance.now() - t0) / total * 100) + "%"; }, 50);
  await new Promise(res => { pickTimer = setTimeout(res, total); window.__early = res; }); clearInterval(iv); if (my !== token) return; state = "reveal"; $("L").disabled = $("R").disabled = true;
  const cpu = Math.random() < .5 ? "L" : "R", mine = myPick, finger = attack ? mine : cpu, head = attack ? cpu : mine; let text, won = null;
  if (!mine) { won = attack ? false : false; text = "시간이 지났어요! 고르지 못했어요 ⏰"; if (!attack) { cp++; text += " (수비 실패)"; } }
  else if (hit(finger, head)) { if (attack) { me++; won = true; text = "🎯 같은 방향! 내가 1점!"; } else { cp++; won = false; text = "😱 걸렸어요! 컴퓨터가 1점"; } }
  else text = attack ? "😅 다른 방향! 컴퓨터가 피했어요" : "😎 잘 피했어요!";
  ui(attack ? "⚔️ 공격 결과" : "🛡️ 수비 결과", `${ARROW[finger] || "❔"} ${HEAD[head] || "❔"}`, `손가락 ${finger ? NAME[finger] : "-"} · 얼굴 ${head ? NAME[head] : "-"}  →  ${text}`);
  await sleep(1400); if (my !== token) return;
  if (me >= 3 || cp >= 3) return end(); round();
}
function end() { state = "idle"; const win = me >= 3, best = ld(KEY) || { w: 0, l: 0 }; best[win ? "w" : "l"]++; sv(KEY, best); ui(win ? "🎉 승리" : "😢 패배", win ? "이겼어요!" : "졌어요", `전적 ${best.w}승 ${best.l}패 · 다시 도전해 보세요`); $("start").hidden = false; $("start").textContent = "다시 하기"; }
function choose(d) { if (state !== "pick" || myPick) return; myPick = d; clearTimeout(pickTimer); if (window.__early) window.__early(); }
function start() { me = 0; cp = 0; rd = 0; $("start").hidden = true; round(); }
$("L").onclick = () => choose("L"); $("R").onclick = () => choose("R"); $("start").onclick = start;
document.addEventListener("keydown", e => { if (e.key === "ArrowLeft") choose("L"); else if (e.key === "ArrowRight") choose("R"); });''',
     css=".stage2{background:var(--surface);border:2px solid var(--line);border-radius:22px;min-height:210px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;text-align:center;padding:14px}.role{font-family:var(--font-display);font-size:1.2rem;color:var(--muted)}.stage2 .big{font-size:clamp(2.2rem,12vw,3.4rem)}.sub{color:var(--muted);font-size:.92rem;padding:0 6px}.bar{height:8px;background:var(--line);border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--accent)}.dir{background:var(--surface);border:3px solid var(--line);border-radius:18px;min-height:72px;font-family:var(--font-display);font-size:1.5rem}.dir:not(:disabled):active{border-color:var(--accent);transform:scale(.97)}.dir:disabled{opacity:.45;cursor:default}")

# ---------------- 한글 단어 찾기 ----------------
themes = {"동물": "토끼 호랑이 사자 코끼리 기린 고래 강아지 고양이 거북이 원숭이 다람쥐 펭귄", "과일": "사과 바나나 딸기 수박 포도 복숭아 참외 오렌지 레몬 자두 감 귤", "음식": "김치 비빔밥 라면 만두 떡볶이 김밥 짜장면 피자 치킨 불고기 냉면 순대",
          "나라": "한국 일본 중국 미국 영국 프랑스 독일 호주 캐나다 인도 태국 브라질", "탈것": "자동차 버스 기차 비행기 자전거 지하철 택시 트럭 오토바이 배 로켓 헬리콥터"}
make("out/word-search.html", "단어 찾기", "🔤", 160, "wordsearch-best-v1",
     "글자판 속에 숨은 단어를 찾아서 <b>손가락으로 쭉 그어</b> 선택하세요. 단어는 가로, 세로, 대각선(↘)으로 숨어 있고, 거꾸로 그어도 돼요. 아래 목록의 단어를 모두 찾으면 끝! 주제를 고를 수 있어요.",
     r'''  <div class="seg" id="th" role="radiogroup" aria-label="주제" style="--n:5"></div>
  <div class="stats" style="grid-template-columns:repeat(2,1fr)"><div class="stat"><small>시간</small><b id="time">0:00</b></div><div class="stat"><small>최고(이 주제)</small><b id="best">-</b></div></div>
  <div class="wgrid" id="grid" aria-label="글자판"></div>
  <div class="words" id="words"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="new" type="button">새 판</button>''',
     r'''const THEMES = %s;
const FILL = "가나다라마바사아자차카타파하고노도로모보소오조초코토포호구누두루무부수우주추쿠투푸후기니디리미비시이지치키티피히거너더러머버서어저처커터퍼허".split("");
const N = 8, DIRS = [[0, 1], [1, 0], [1, 1]];                // 가로, 세로, 대각선(↘)에만 단어를 숨긴다
const fmt = s => Math.floor(s / 60) + ":" + String(s %% 60).padStart(2, "0");
let theme = (ld(KEY + "-th") in THEMES) ? ld(KEY + "-th") : "동물", grid, words, found, placed, t0, timer, done, sel = null, best = ld(KEY) || {};
// 단어를 판에 숨긴다. 겹치는 칸은 같은 글자일 때만 허용한다
function build(list) {
  for (let tries = 0; tries < 50; tries++) {
    const g = Array.from({ length: N }, () => Array(N).fill("")), pl = []; let ok = true;
    for (const w of list) {
      const ch = [...w]; let put = false;
      for (let a = 0; a < 300 && !put; a++) { const [dr, dc] = DIRS[ri(0, 2)], r = ri(0, N - 1), c = ri(0, N - 1), er = r + dr * (ch.length - 1), ec = c + dc * (ch.length - 1);
        if (er >= N || ec >= N) continue; if (!ch.every((x, k) => !g[r + dr * k][c + dc * k] || g[r + dr * k][c + dc * k] === x)) continue;
        ch.forEach((x, k) => { g[r + dr * k][c + dc * k] = x; }); pl.push({ w, r, c, dr, dc }); put = true; }
      if (!put) { ok = false; break; }
    }
    if (ok) { for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (!g[r][c]) g[r][c] = FILL[ri(0, FILL.length - 1)]; return { g, pl }; }
  }
  return null;
}
function newGame() {
  clearInterval(timer); let b = null; while (!b) { words = shuf(THEMES[theme].split(" ").filter(w => [...w].length >= 2 && [...w].length <= 5)).slice(0, 6); b = build(words); } grid = b.g; placed = b.pl; found = new Set(); done = false; t0 = 0; sel = null; $("time").textContent = "0:00"; $("res").hidden = true; render();
}
function startTimer() { if (t0 || done) return; t0 = Date.now(); timer = setInterval(() => { $("time").textContent = fmt(Math.floor((Date.now() - t0) / 1000)); }, 500); }
const lineCells = (r1, c1, r2, c2) => {                       // 시작 칸에서 끝 칸까지, 가장 가까운 8방향의 직선에 놓인 칸들
  const dr = r2 - r1, dc = c2 - c1, len = Math.max(Math.abs(dr), Math.abs(dc)); if (!len) return [[r1, c1]];
  const ang = Math.round(Math.atan2(dr, dc) / (Math.PI / 4)), D = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]][((ang %% 8) + 8) %% 8], out = [];
  for (let k = 0; k <= len; k++) { const r = r1 + D[0] * k, c = c1 + D[1] * k; if (r < 0 || c < 0 || r >= N || c >= N) break; out.push([r, c]); } return out;
};
function commit(cells) {
  const s = cells.map(([r, c]) => grid[r][c]).join(""), rev = [...s].reverse().join(""); const w = words.find(x => !found.has(x) && (x === s || x === rev));
  if (w) { found.add(w); cells.forEach(([r, c]) => { grid[r][c] = grid[r][c]; foundCells.add(r + "," + c); }); if (found.size === words.length) win(); }
  render(); return !!w;
}
let foundCells = new Set();
function win() { done = true; clearInterval(timer); const s = Math.max(1, Math.floor((Date.now() - t0) / 1000)); let t = `${fmt(s)} 만에 모두 찾았어요.`; if (!best[theme] || s < best[theme]) { best[theme] = s; sv(KEY, best); t += " 🏆 최고 기록이에요!"; } $("res").innerHTML = `<b>🎉 모두 찾았어요!</b><p class="muted">${t}</p>`; $("res").hidden = false; }
function render() {
  const selSet = new Set((sel || []).map(([r, c]) => r + "," + c));
  $("grid").innerHTML = grid.map((row, r) => row.map((ch, c) => `<span class="wc ${foundCells.has(r + "," + c) ? "f" : ""} ${selSet.has(r + "," + c) ? "s" : ""}" data-r="${r}" data-c="${c}">${ch}</span>`).join("")).join("");
  $("words").innerHTML = words.map(w => `<span class="wd ${found.has(w) ? "d" : ""}">${w}</span>`).join(""); $("best").textContent = best[theme] ? fmt(best[theme]) : "-";
  $("th").innerHTML = Object.keys(THEMES).map(k => `<button type="button" class="${k === theme ? "on" : ""}" data-t="${k}" role="radio" aria-checked="${k === theme}">${k}</button>`).join("");
}
const cellAt = e => { const el = document.elementFromPoint(e.clientX, e.clientY); return el && el.dataset && el.dataset.r !== undefined ? [+el.dataset.r, +el.dataset.c] : null; };
let start0 = null;
$("grid").addEventListener("pointerdown", e => { if (done) return; const c = cellAt(e); if (c) { e.preventDefault(); startTimer(); start0 = c; sel = [c]; render(); } });
$("grid").addEventListener("pointermove", e => { if (!start0) return; const c = cellAt(e); if (c) { sel = lineCells(start0[0], start0[1], c[0], c[1]); render(); } });
["pointerup", "pointercancel"].forEach(ev => document.addEventListener(ev, () => { if (!start0) return; const s = sel; start0 = null; sel = null; if (s && s.length > 1) commit(s); else render(); }));
$("th").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (b && b.dataset.t !== theme) { theme = b.dataset.t; sv(KEY + "-th", theme); foundCells = new Set(); newGame(); } });
$("new").onclick = () => { foundCells = new Set(); newGame(); }; newGame();''' % json.dumps(themes, ensure_ascii=False),
     css=".wgrid{display:grid;grid-template-columns:repeat(8,1fr);gap:3px;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:8px;touch-action:none}.wc{aspect-ratio:1;display:grid;place-items:center;border-radius:8px;background:var(--soft);font-family:var(--font-display);font-size:clamp(1.1rem,6vw,1.6rem);user-select:none}.wc.s{background:var(--accent);color:var(--accent-fg)}.wc.f{background:color-mix(in srgb,var(--ok) 35%,var(--surface));color:var(--fg)}.words{display:flex;flex-wrap:wrap;gap:8px}.wd{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px 14px;font-weight:700}.wd.d{text-decoration:line-through;color:var(--muted);background:var(--soft)}")
