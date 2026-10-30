import sys, json
sys.path.insert(0, ".")
from mkpage import make

# ---------------- 하이로우 ----------------
make("out/high-low.html", "하이로우", "🂡", 340, "highlow-v1",
     "지금 카드보다 <b>다음 카드가 더 높을지, 더 낮을지</b> 맞혀 보세요. 숫자 순서는 A(가장 낮음) < 2 < … < 10 < J < Q < K(가장 높음)예요. 같은 숫자가 나오면 '같아요!'로 비기고 연승은 그대로예요. 틀리면 끝! 52장을 모두 맞히면 완벽해요.",
     r'''  <div class="stats"><div class="stat"><small>연승</small><b id="st">0</b></div><div class="stat"><small>최고 연승</small><b id="bs">0</b></div><div class="stat"><small>남은 카드</small><b id="left">51</b></div></div>
  <div class="felt"><div class="pc" id="cur"></div></div>
  <p class="center big" id="msg" style="font-size:1.4rem" aria-live="polite">다음 카드는?</p>
  <div class="row"><button class="btn" id="hi" type="button">⬆️ 더 높음</button><button class="btn" id="lo" type="button" style="background:#2f7fe0">⬇️ 더 낮음</button></div>
  <div class="card"><h2>지금까지 나온 카드</h2><div class="hist" id="hist"></div></div>
  <button class="btn ghost" id="again" type="button" hidden>다시 하기</button>''',
     r'''const RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"], SUITS = ["♠", "♥", "♦", "♣"];
let deck, cur, streak, best = ld(KEY) || 0, over, hist;
const newDeck = () => shuf(SUITS.flatMap(s => RANKS.map((r, i) => ({ r, s, v: i + 1 }))));
const red = c => c.s === "♥" || c.s === "♦", cardHtml = (c, small) => `<span class="pcard ${red(c) ? "r" : ""} ${small ? "sm" : ""}">${c.r}<small>${c.s}</small></span>`;
// 비교: 숫자 값만 본다. 같으면 'tie'
const judge = (a, b, guess) => (b.v === a.v ? "tie" : (b.v > a.v) === (guess === "hi") ? "win" : "lose");
function start() { deck = newDeck(); cur = deck.pop(); hist = [cur]; streak = 0; over = false; $("again").hidden = true; $("msg").textContent = "다음 카드는?"; render(); }
function guess(g) {
  if (over) return; const next = deck.pop(), r = judge(cur, next, g); hist.push(next);
  if (r === "tie") { cur = next; $("msg").textContent = "같은 숫자예요! 비겼어요 🤝"; }
  else if (r === "win") { streak++; if (streak > best) { best = streak; sv(KEY, best); } cur = next; $("msg").textContent = "🎉 맞았어요!"; }
  else { over = true; cur = next; $("msg").textContent = `😢 틀렸어요! ${streak}연승으로 끝났어요`; $("again").hidden = false; }
  if (!over && !deck.length) { over = true; $("msg").textContent = "🏆 52장을 모두 맞혔어요! 완벽해요!"; $("again").hidden = false; }
  render();
}
function render() { $("cur").innerHTML = cardHtml(cur); $("st").textContent = streak; $("bs").textContent = best; $("left").textContent = deck.length; $("hist").innerHTML = hist.slice(-12).map(c => cardHtml(c, true)).join(""); $("hi").disabled = $("lo").disabled = over; }
$("hi").onclick = () => guess("hi"); $("lo").onclick = () => guess("lo"); $("again").onclick = start; start();''',
     css=".felt{background:#2d7a4a;border-radius:20px;padding:24px;display:grid;place-items:center}.pcard{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;width:120px;height:170px;border-radius:12px;background:#fff;color:#1b1b1b;font-family:var(--font-display);font-size:3.2rem;line-height:1.1;box-shadow:0 4px 8px rgba(0,0,0,.35)}.pcard small{font-size:2.6rem}.pcard.r{color:#d6332b}.pcard.sm{width:38px;height:54px;font-size:1.05rem;border-radius:6px;box-shadow:none;border:1px solid var(--line)}.pcard.sm small{font-size:.9rem}.hist{display:flex;gap:5px;flex-wrap:wrap}")

# ---------------- 로또 번호 뽑기 ----------------
make("out/lotto-picker.html", "로또 번호 뽑기", "🎱", 45, "lotto-v1",
     "1부터 45까지 서로 다른 6개의 번호와 보너스 번호 1개를 무작위로 뽑아요. 재미로 보는 번호이고, 당첨을 보장하지 않아요. 복권은 건전하게, 무리하지 않는 범위에서 즐기세요.",
     r'''  <div class="card"><div class="step"><h2>게임 수</h2><div><button id="minus" type="button" aria-label="줄이기">−</button><b id="n">5</b><button id="plus" type="button" aria-label="늘리기">＋</button></div></div></div>
  <div id="out"></div>
  <div class="row"><button class="btn" id="go" type="button">번호 뽑기</button><button class="btn ghost" id="copy" type="button">📋 복사하기</button></div>
  <p class="center muted" id="note"></p>''',
     r'''let n = clamp(ld(KEY) || 5, 1, 5), sets = [];
// 1~45 중 서로 다른 7개를 뽑아 앞의 6개는 작은 순서로 정렬하고, 마지막 하나를 보너스로 쓴다
function pick() { const a = shuf(Array.from({ length: 45 }, (_, i) => i + 1)).slice(0, 7); return { main: a.slice(0, 6).sort((x, y) => x - y), bonus: a[6] }; }
const color = v => (v <= 10 ? "#f5b800" : v <= 20 ? "#3fa7e0" : v <= 30 ? "#e8453c" : v <= 40 ? "#8d96a5" : "#5ab030");
const ball = (v, bonus) => `<span class="lb ${bonus ? "bonus" : ""}" style="background:${color(v)}">${v}</span>`;
function render() { $("n").textContent = n; $("out").innerHTML = sets.map((s, i) => `<div class="lrow"><b>${"ABCDE"[i]}</b>${s.main.map(v => ball(v)).join("")}<span class="plus">+</span>${ball(s.bonus, true)}</div>`).join("") || `<div class="res"><p class="muted">"번호 뽑기"를 눌러 보세요</p></div>`; }
function go() { sets = Array.from({ length: n }, pick); render(); $("note").textContent = ""; try { navigator.vibrate && navigator.vibrate(30); } catch (e) {} }
$("go").onclick = go;
$("copy").onclick = async () => { if (!sets.length) return; const t = sets.map((s, i) => `${"ABCDE"[i]}: ${s.main.join(", ")} + ${s.bonus}`).join("\n"); try { await navigator.clipboard.writeText(t); $("note").textContent = "복사했어요!"; } catch (e) { $("note").textContent = "복사가 안 돼요. 번호를 직접 적어 두세요."; } };
$("minus").onclick = () => { if (n > 1) { n--; sv(KEY, n); render(); } }; $("plus").onclick = () => { if (n < 5) { n++; sv(KEY, n); render(); } }; go();''',
     css=".lrow{display:flex;align-items:center;gap:6px;justify-content:center;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:10px 6px;margin-bottom:8px}.lrow>b{font-family:var(--font-display);width:1.4em;color:var(--muted)}.lb{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;color:#fff;font-family:var(--font-display);font-size:1.15rem;text-shadow:0 1px 1px rgba(0,0,0,.3);flex:none}.lb.bonus{box-shadow:0 0 0 3px var(--surface),0 0 0 5px var(--muted)}.plus{color:var(--muted);font-weight:700}@media(max-width:360px){.lb{width:32px;height:32px;font-size:1rem}.lrow{gap:4px}}")

# ---------------- 뽀모도로 타이머 ----------------
make("out/pomodoro.html", "뽀모도로 타이머", "🍅", 8, "pomodoro-v1",
     "집중하는 시간과 쉬는 시간을 번갈아 타이머로 알려 줘요. 집중이 끝나면 쉬는 시간이 자동으로 시작돼요. 시작 버튼을 눌러야 소리가 나요. 화면을 켜 두면 가장 정확해요.",
     r'''  <div class="seg" id="pre" role="radiogroup" aria-label="시간 설정"></div>
  <div class="dial"><svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="52" class="bg"/><circle cx="60" cy="60" r="52" class="fg" id="ring"/></svg><div class="inner"><div class="mode" id="mode">집중</div><div class="time" id="time">25:00</div><div class="muted" id="cnt"></div></div></div>
  <div class="row"><button class="btn" id="go" type="button">시작</button><button class="btn ghost" id="reset" type="button">처음으로</button></div>''',
     r'''const PRE = { a: { f: 25, b: 5, label: "25 / 5", hint: "기본" }, b: { f: 50, b: 10, label: "50 / 10", hint: "길게" }, c: { f: 15, b: 3, label: "15 / 3", hint: "짧게" } };
let pre = (ld(KEY) in PRE) ? ld(KEY) : "a", mode = "f", left = PRE[pre].f * 60, running = false, endAt = 0, timer = 0, done = 0, audio = null, tempo = 1;
const fmt = s => String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(Math.floor(s % 60)).padStart(2, "0");
function beep() { try { audio = audio || new (window.AudioContext || window.webkitAudioContext)(); [660, 880, 660].forEach((f, k) => { const o = audio.createOscillator(), g = audio.createGain(); o.frequency.value = f; g.gain.setValueAtTime(.2, audio.currentTime + k * .22); g.gain.exponentialRampToValueAtTime(.001, audio.currentTime + k * .22 + .2); o.connect(g); g.connect(audio.destination); o.start(audio.currentTime + k * .22); o.stop(audio.currentTime + k * .22 + .2); }); navigator.vibrate && navigator.vibrate([200, 100, 200]); } catch (e) {} }
const total = () => PRE[pre][mode] * 60;
function tick() { left = Math.max(0, Math.ceil((endAt - Date.now()) / 1000 / tempo)); if (left <= 0) return next(); draw(); }
function next() { beep(); if (mode === "f") done++; mode = mode === "f" ? "b" : "f"; left = total(); endAt = Date.now() + left * 1000 * tempo; draw(); }
function toggle() {
  if (running) { running = false; clearInterval(timer); } else { try { audio = audio || new (window.AudioContext || window.webkitAudioContext)(); audio.resume(); } catch (e) {} running = true; endAt = Date.now() + left * 1000 * tempo; timer = setInterval(tick, 250); }
  draw();
}
function reset() { running = false; clearInterval(timer); mode = "f"; left = total(); draw(); }
function draw() {
  $("time").textContent = fmt(left); $("mode").textContent = mode === "f" ? "🍅 집중" : "☕ 휴식"; $("ring").style.strokeDashoffset = 326.7 * (1 - left / total()); $("ring").style.stroke = mode === "f" ? "var(--accent)" : "#2fa05a";
  $("cnt").textContent = done ? `오늘 ${done}번 집중했어요` : ""; $("go").textContent = running ? "일시정지" : (left < total() ? "계속" : "시작"); document.title = running ? fmt(left) + " · 뽀모도로" : "뽀모도로 타이머";
  $("pre").style.setProperty("--n", 3); $("pre").innerHTML = Object.keys(PRE).map(k => `<button type="button" class="${k === pre ? "on" : ""}" data-p="${k}" role="radio" aria-checked="${k === pre}" ${running ? "disabled" : ""}>${PRE[k].label}<small>${PRE[k].hint} (분)</small></button>`).join("");
}
$("pre").addEventListener("click", e => { const b = e.target.closest("[data-p]"); if (b && !b.disabled) { pre = b.dataset.p; sv(KEY, pre); reset(); } });
$("go").onclick = toggle; $("reset").onclick = reset; draw();''',
     css=".dial{position:relative;width:min(300px,100%);margin:0 auto}.dial svg{width:100%;transform:rotate(-90deg)}.dial circle{fill:none;stroke-width:8}.dial .bg{stroke:var(--line)}.dial .fg{stroke-linecap:round;stroke-dasharray:326.7;stroke-dashoffset:0;transition:stroke-dashoffset .3s linear}.inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px}.mode{font-family:var(--font-display);font-size:1.4rem}.time{font-family:var(--font-display);font-size:clamp(3.2rem,18vw,4.4rem);font-variant-numeric:tabular-nums;line-height:1}")

# ---------------- 더치페이 계산기 ----------------
make("out/split-bill.html", "더치페이 계산기", "🧾", 170, "splitbill-v1",
     "총 금액을 인원수로 나눠서 한 사람당 낼 금액을 알려 줘요. 팁이나 봉사료를 더할 수 있고, 걷기 편하게 100원 단위 등으로 올려서 계산할 수도 있어요. 올림하면 조금 남는데, 그 금액도 알려 줘요.",
     r'''  <div class="card">
    <h2>총 금액 (원)</h2>
    <input type="number" id="total" inputmode="numeric" min="0" placeholder="예) 87000" aria-label="총 금액">
    <div class="step"><h2>인원</h2><div><button id="minus" type="button" aria-label="줄이기">−</button><b id="n">3</b><button id="plus" type="button" aria-label="늘리기">＋</button></div></div>
    <h2>팁·봉사료</h2><div class="seg" id="tip" style="--n:4"></div>
    <h2>올림 단위</h2><div class="seg" id="round" style="--n:4"></div>
  </div>
  <div class="res"><small class="muted">한 사람이 낼 금액</small><div class="big" id="each">-</div><p class="muted" id="detail"></p></div>''',
     r'''let cfg = ld(KEY) || { n: 3, tip: 0, round: 100, total: "" };
cfg.n = clamp(cfg.n, 2, 30);
const TIPS = [0, 5, 10, 15], ROUNDS = [1, 10, 100, 1000];
const won = v => v.toLocaleString("ko-KR") + "원";
// 계산: (총액 + 팁)을 인원수로 나눈 값을 올림 단위로 올린다. 올림 때문에 더 걷히는 금액은 '남는 돈'
function calc(total, n, tipPct, unit) {
  const withTip = Math.round(total * (1 + tipPct / 100)), raw = withTip / n, each = Math.ceil(raw / unit) * unit, collected = each * n;
  return { withTip, each, collected, extra: collected - withTip };
}
function render() {
  const t = Math.max(0, parseInt($("total").value || "0", 10) || 0); $("n").textContent = cfg.n; cfg.total = $("total").value; sv(KEY, cfg);
  $("tip").innerHTML = TIPS.map(v => `<button type="button" class="${v === cfg.tip ? "on" : ""}" data-t="${v}" role="radio" aria-checked="${v === cfg.tip}">${v ? v + "%" : "없음"}</button>`).join("");
  $("round").innerHTML = ROUNDS.map(v => `<button type="button" class="${v === cfg.round ? "on" : ""}" data-r="${v}" role="radio" aria-checked="${v === cfg.round}">${v === 1 ? "그대로" : v + "원"}</button>`).join("");
  if (!t) { $("each").textContent = "-"; $("detail").textContent = "총 금액을 입력해 주세요."; return; }
  const r = calc(t, cfg.n, cfg.tip, cfg.round); $("each").textContent = won(r.each);
  $("detail").innerHTML = `${cfg.tip ? `팁 포함 합계 ${won(r.withTip)}<br>` : ""}${cfg.n}명이 낼 총액 ${won(r.collected)}${r.extra ? `<br>올림 때문에 ${won(r.extra)}이(가) 남아요` : ""}`;
}
$("total").value = cfg.total; $("total").addEventListener("input", render);
$("minus").onclick = () => { if (cfg.n > 2) { cfg.n--; render(); } }; $("plus").onclick = () => { if (cfg.n < 30) { cfg.n++; render(); } };
$("tip").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (b) { cfg.tip = +b.dataset.t; render(); } }); $("round").addEventListener("click", e => { const b = e.target.closest("[data-r]"); if (b) { cfg.round = +b.dataset.r; render(); } }); render();''')
