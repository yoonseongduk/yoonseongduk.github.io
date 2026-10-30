import sys
sys.path.insert(0, ".")
from mkpage import make

# ---------------- 제비뽑기 ----------------
make("out/lots.html", "제비뽑기", "🎟️", 150, "lots-v1",
     "인원수만큼 제비(카드)를 만들고 한 사람씩 하나를 골라 뒤집어요. 당첨은 몇 개로 할지 정할 수 있어요. 뒤집은 카드는 다시 바꿀 수 없어요. 한 판이 끝나면 '다시 뽑기'를 누르세요.",
     r'''  <section class="card" id="setup">
    <div class="step"><h2>인원(카드 수)</h2><div><button id="nMinus" type="button" aria-label="줄이기">−</button><b id="n">6</b><button id="nPlus" type="button" aria-label="늘리기">＋</button></div></div>
    <div class="step"><h2>당첨 수</h2><div><button id="wMinus" type="button" aria-label="줄이기">−</button><b id="w">1</b><button id="wPlus" type="button" aria-label="늘리기">＋</button></div></div>
    <input type="text" id="winText" maxlength="12" aria-label="당첨 문구" placeholder="당첨 문구">
    <input type="text" id="loseText" maxlength="12" aria-label="꽝 문구" placeholder="꽝 문구">
    <button class="btn" id="make" type="button">제비 만들기</button>
  </section>
  <section id="play" hidden>
    <div class="grid" id="grid"></div>
    <div class="res" id="res" style="margin-top:12px"></div>
    <div class="row" style="margin-top:12px"><button class="btn ghost" id="openAll" type="button">모두 공개</button><button class="btn" id="again" type="button">다시 뽑기</button></div>
    <button class="btn ghost" id="back" type="button" style="margin-top:8px;width:100%">설정 바꾸기</button>
  </section>''',
     r'''let cfg = ld(KEY) || { n: 6, w: 1, win: "당첨 🎉", lose: "꽝" }, deck = [], opened = new Set();
cfg.n = clamp(cfg.n, 2, 20); cfg.w = clamp(cfg.w, 1, cfg.n - 1);
// 카드 n장 중 w장이 당첨(1)이 되도록 섞는다
const deal = (n, w) => shuf(Array.from({ length: n }, (_, i) => (i < w ? 1 : 0)));
function drawSetup() { $("n").textContent = cfg.n; $("w").textContent = cfg.w; $("winText").value = cfg.win; $("loseText").value = cfg.lose; }
function begin() { cfg.win = $("winText").value.trim() || "당첨 🎉"; cfg.lose = $("loseText").value.trim() || "꽝"; sv(KEY, cfg); deck = deal(cfg.n, cfg.w); opened = new Set(); $("setup").hidden = true; $("play").hidden = false; render(); }
function render() {
  $("grid").style.gridTemplateColumns = `repeat(${cfg.n > 9 ? 4 : 3}, 1fr)`;
  $("grid").innerHTML = deck.map((v, i) => `<button type="button" class="tk ${opened.has(i) ? (v ? "win" : "lose") : ""}" data-i="${i}" ${opened.has(i) ? "disabled" : ""} aria-label="${i + 1}번 카드">${opened.has(i) ? esc(v ? cfg.win : cfg.lose) : (i + 1)}</button>`).join("");
  const left = deck.filter((v, i) => v && !opened.has(i)).length;
  $("res").innerHTML = opened.size === deck.length ? `<b>모두 열었어요!</b><p class="muted">${deck.length}장 중 당첨 ${cfg.w}장</p>` : `<b>${opened.size} / ${deck.length}장 열었어요</b><p class="muted">남은 당첨 카드 ${left}장</p>`;
}
$("grid").addEventListener("click", e => { const t = e.target.closest("[data-i]"); if (t && !t.disabled) { opened.add(+t.dataset.i); render(); try { navigator.vibrate && navigator.vibrate(deck[+t.dataset.i] ? [60, 40, 60] : 30); } catch (x) {} } });
$("nMinus").onclick = () => { if (cfg.n > 2) { cfg.n--; cfg.w = Math.min(cfg.w, cfg.n - 1); drawSetup(); } }; $("nPlus").onclick = () => { if (cfg.n < 20) { cfg.n++; drawSetup(); } };
$("wMinus").onclick = () => { if (cfg.w > 1) { cfg.w--; drawSetup(); } }; $("wPlus").onclick = () => { if (cfg.w < cfg.n - 1) { cfg.w++; drawSetup(); } };
$("make").onclick = begin; $("again").onclick = begin; $("openAll").onclick = () => { deck.forEach((_, i) => opened.add(i)); render(); }; $("back").onclick = () => { $("play").hidden = true; $("setup").hidden = false; drawSetup(); };
drawSetup();''',
     css=".grid{display:grid;gap:10px}.tk{aspect-ratio:1.1;border:2px dashed var(--line);border-radius:16px;background:var(--surface);font-family:var(--font-display);font-size:1.6rem;padding:4px;overflow-wrap:anywhere;line-height:1.2}.tk.win{background:var(--accent);color:var(--accent-fg);border:2px solid var(--accent);font-size:1.3rem}.tk.lose{background:var(--soft);color:var(--muted);border:2px solid var(--line);font-size:1.2rem}.tk:active{transform:scale(.96)}")

# ---------------- 팀 나누기 ----------------
make("out/team-split.html", "팀 나누기", "👥", 195, "teamsplit-v1",
     "이름을 한 줄에 하나씩(또는 쉼표로) 적고 팀 수를 정하면 공평하게 섞어서 나눠 줘요. 팀 인원은 최대 1명까지만 차이 나요. 다시 섞기를 누르면 새로 나눠요.",
     r'''  <section class="card">
    <h2>참가자 이름</h2>
    <textarea id="names" placeholder="예)&#10;아빠&#10;엄마&#10;첫째&#10;둘째" aria-label="참가자 이름"></textarea>
    <p class="muted" id="count"></p>
    <div class="step"><h2>팀 수</h2><div><button id="minus" type="button" aria-label="줄이기">−</button><b id="k">2</b><button id="plus" type="button" aria-label="늘리기">＋</button></div></div>
    <button class="btn" id="go" type="button">팀 나누기</button>
  </section>
  <div id="out"></div>''',
     r'''let cfg = ld(KEY) || { names: "", k: 2 };
const parse = s => s.split(/[\n,]+/).map(x => x.trim()).filter(Boolean);
// 섞은 뒤 한 명씩 돌려 가며 나눠 주면 팀 인원이 최대 1명 차이로 나뉜다
function split(names, k) { const t = Array.from({ length: k }, () => []); shuf(names).forEach((n, i) => t[i % k].push(n)); return t; }
const COLORS = ["#e8453c", "#2f7fe0", "#e2a800", "#2fa05a", "#9b59d6", "#e0752b"];
function show() {
  const names = parse($("names").value); $("count").textContent = names.length ? `${names.length}명` : "이름을 적어 주세요."; $("k").textContent = cfg.k;
  cfg.names = $("names").value; sv(KEY, cfg);
}
function go() {
  const names = parse($("names").value); if (names.length < cfg.k) { $("out").innerHTML = `<div class="res"><b>이름이 모자라요</b><p class="muted">팀 수(${cfg.k})보다 이름이 적어요.</p></div>`; return; }
  const teams = split(names, cfg.k);
  $("out").innerHTML = `<div class="teams">${teams.map((t, i) => `<div class="team" style="border-top:6px solid ${COLORS[i]}"><h2 style="color:${COLORS[i]}">${i + 1}팀 <span class="muted">(${t.length}명)</span></h2><p>${t.map(esc).join("<br>")}</p></div>`).join("")}</div><button class="btn ghost" id="re" type="button" style="margin-top:12px;width:100%">🔀 다시 섞기</button>`;
  $("re").onclick = go;
}
$("names").value = cfg.names; $("names").addEventListener("input", show);
$("minus").onclick = () => { if (cfg.k > 2) { cfg.k--; show(); } }; $("plus").onclick = () => { if (cfg.k < 6) { cfg.k++; show(); } }; $("go").onclick = go; show();''',
     css=".teams{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.team{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px;font-size:1.05rem}.team h2{margin-bottom:6px}.team p{user-select:text;-webkit-user-select:text}")

# ---------------- 주사위 ----------------
make("out/dice-roller.html", "주사위 굴리기", "🎲", 20, "dice-v1",
     "주사위 개수(1~6개)를 고르고 굴려 보세요. 눈의 합계도 알려 줘요. 보드게임이나 내기, 순서 정하기에 쓰세요.",
     r'''  <div class="card"><div class="step"><h2>주사위 개수</h2><div><button id="minus" type="button" aria-label="줄이기">−</button><b id="cnt">2</b><button id="plus" type="button" aria-label="늘리기">＋</button></div></div></div>
  <div class="table" id="table" aria-live="polite"></div>
  <div class="res"><small class="muted">합계</small><div class="big" id="sum">-</div></div>
  <button class="btn" id="roll" type="button">주사위 굴리기</button>
  <div class="card"><h2>최근 기록</h2><p class="muted" id="hist">아직 굴리지 않았어요.</p></div>''',
     r'''const FACES = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"];
let n = clamp(ld(KEY) || 2, 1, 6), vals = [], rolling = false, hist = [];
const rollDie = () => 1 + Math.floor(Math.random() * 6);
function render() { $("cnt").textContent = n; $("table").innerHTML = (vals.length ? vals : Array.from({ length: n }, () => 0)).map(v => `<span class="die ${rolling ? "shake" : ""}">${v ? FACES[v - 1] : "🎲"}</span>`).join(""); $("sum").textContent = vals.length && !rolling ? vals.reduce((a, b) => a + b, 0) : "-"; $("hist").textContent = hist.length ? hist.map(h => h.join("+") + "=" + h.reduce((a, b) => a + b, 0)).join("  ·  ") : "아직 굴리지 않았어요."; }
function roll() {
  if (rolling) return; rolling = true; $("roll").disabled = true; let k = 0;
  const tick = setInterval(() => { vals = Array.from({ length: n }, rollDie); render(); if (++k >= 9) { clearInterval(tick); rolling = false; $("roll").disabled = false; hist.unshift(vals.slice()); hist = hist.slice(0, 6); render(); try { navigator.vibrate && navigator.vibrate(40); } catch (e) {} } }, 70);
}
$("roll").onclick = roll; $("minus").onclick = () => { if (n > 1) { n--; sv(KEY, n); vals = []; render(); } }; $("plus").onclick = () => { if (n < 6) { n++; sv(KEY, n); vals = []; render(); } }; render();''',
     css=".table{display:flex;flex-wrap:wrap;gap:8px 12px;justify-content:center;padding:18px 8px;background:var(--surface);border:1px solid var(--line);border-radius:20px;min-height:130px;align-items:center}.die{font-size:4.6rem;line-height:1;color:var(--fg)}.die.shake{animation:sh .14s infinite}@keyframes sh{0%{transform:rotate(-8deg)}50%{transform:rotate(8deg) translateY(-4px)}100%{transform:rotate(-8deg)}}")

# ---------------- 동전 던지기 ----------------
make("out/coin-flip.html", "동전 던지기", "🪙", 48, "coin-v1",
     "동전을 눌러서 던지세요. 앞면과 뒷면은 매번 50%씩이에요. 간단한 내기나 선택을 정할 때 쓰세요.",
     r'''  <div class="stats"><div class="stat"><small>앞면</small><b id="f">0</b></div><div class="stat"><small>뒷면</small><b id="b">0</b></div><div class="stat"><small>연속</small><b id="s">-</b></div></div>
  <div class="stage"><button class="coin" id="coin" type="button" aria-label="동전 던지기"><span class="face front">앞</span><span class="face back">뒤</span></button></div>
  <div class="res"><div class="big" id="msg" aria-live="polite">동전을 눌러 던지세요</div></div>
  <button class="btn ghost" id="reset" type="button">기록 지우기</button>''',
     r'''let st = ld(KEY) || { f: 0, b: 0, last: "", run: 0 }, flipping = false, turns = 0;
const flip = () => (Math.random() < .5 ? "front" : "back");
function show() { $("f").textContent = st.f; $("b").textContent = st.b; $("s").textContent = st.run > 1 ? (st.last === "front" ? "앞" : "뒤") + " ×" + st.run : "-"; }
function toss() {
  if (flipping) return; flipping = true; const r = flip(); turns += 5 + (r === "back" ? 0.5 : 0) - (turns % 1); const c = $("coin");
  c.style.transform = `rotateY(${turns * 360}deg)`; $("msg").textContent = "던지는 중…";
  setTimeout(() => { flipping = false; st[r === "front" ? "f" : "b"]++; st.run = st.last === r ? st.run + 1 : 1; st.last = r; sv(KEY, st); $("msg").textContent = r === "front" ? "앞면!" : "뒷면!"; show(); }, 1000);
}
$("coin").onclick = toss; $("reset").onclick = () => { st = { f: 0, b: 0, last: "", run: 0 }; sv(KEY, st); $("msg").textContent = "기록을 지웠어요"; show(); }; show();''',
     css=".stage{display:grid;place-items:center;padding:20px 0;perspective:700px}.coin{position:relative;width:170px;height:170px;border-radius:50%;border:0;padding:0;background:none;transform-style:preserve-3d;transition:transform 1s cubic-bezier(.2,.7,.3,1)}.face{position:absolute;inset:0;border-radius:50%;display:grid;place-items:center;font-family:var(--font-display);font-size:4rem;color:#6b4a00;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:radial-gradient(circle at 35% 30%,#ffe58a,#e2a800);border:6px solid #c68a00}.face.back{transform:rotateY(180deg)}")
