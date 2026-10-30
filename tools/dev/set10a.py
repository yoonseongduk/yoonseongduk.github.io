import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 행맨 ----------
HW = "elephant:코끼리 giraffe:기린 penguin:펭귄 dolphin:돌고래 monkey:원숭이 rabbit:토끼 tiger:호랑이 turtle:거북이 butterfly:나비 spider:거미 banana:바나나 orange:오렌지 strawberry:딸기 watermelon:수박 cherry:체리 tomato:토마토 potato:감자 carrot:당근 cheese:치즈 chicken:닭고기 sandwich:샌드위치 hamburger:햄버거 chocolate:초콜릿 cookie:쿠키 school:학교 teacher:선생님 student:학생 pencil:연필 notebook:공책 library:도서관 hospital:병원 airport:공항 station:역 bridge:다리 mountain:산 river:강 forest:숲 island:섬 desert:사막 rainbow:무지개 thunder:천둥 summer:여름 winter:겨울 autumn:가을 spring:봄 morning:아침 evening:저녁 friend:친구 family:가족 brother:형제 sister:자매 doctor:의사 farmer:농부 pilot:조종사 singer:가수 painter:화가 computer:컴퓨터 keyboard:키보드 camera:카메라 guitar:기타 piano:피아노 bicycle:자전거 airplane:비행기 rocket:로켓 window:창문 kitchen:부엌 garden:정원 flower:꽃 balloon:풍선 present:선물 holiday:휴일 birthday:생일 happy:행복한 hungry:배고픈 sleepy:졸린 clever:영리한 brave:용감한 quiet:조용한 strong:강한 yellow:노란색 purple:보라색 silver:은색".split()
HW = [x.split(":") for x in HW]
make(H+"hangman.html", "행맨 (영어 단어)", "🔤", 330, "hangman-v1",
 "뜻을 보고 <b>영어 단어의 알파벳</b>을 하나씩 눌러 맞혀 보세요. 틀리면 하트가 줄어요. 하트 6개를 모두 잃기 전에 단어를 완성하세요!",
 r'''  <div class="stats"><div class="stat"><small>남은 하트</small><b id="hp">❤️×6</b></div><div class="stat"><small>연속 성공</small><b id="streak">0</b></div><div class="stat"><small>최고 연속</small><b id="best">0</b></div></div>
  <div class="card center"><small class="muted">뜻</small><p class="big" id="mean"></p><p class="big wd" id="word"></p></div>
  <div class="kb" id="kb"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="next" type="button" hidden>다음 단어</button>''',
 r'''const WORDS = ''' + json.dumps(HW, ensure_ascii=False) + r''';
let word = "", meaning = "", got = new Set(), wrong = 0, over = false, streak = 0, best = ld(KEY) || 0, last = "";
function newWord() { let w; do { w = WORDS[ri(0, WORDS.length - 1)]; } while (w[0] === last); [word, meaning] = w; last = word; got = new Set(); wrong = 0; over = false; $("res").hidden = true; $("next").hidden = true; render(); }
function render() {
  $("mean").textContent = meaning; $("word").textContent = [...word].map(c => (got.has(c) || over) ? c.toUpperCase() : "_").join(" ");
  $("hp").textContent = "❤️".repeat(6 - wrong) + "🖤".repeat(wrong); $("streak").textContent = streak; $("best").textContent = best;
  $("kb").innerHTML = "abcdefghijklmnopqrstuvwxyz".split("").map(c => `<button type="button" class="k${got.has(c) ? (word.includes(c) ? " ok" : " no") : ""}" data-k="${c}" ${got.has(c) || over ? "disabled" : ""}>${c.toUpperCase()}</button>`).join("");
}
function press(c) {
  if (over || got.has(c)) return; got.add(c); if (!word.includes(c)) wrong++;
  const done = [...word].every(x => got.has(x));
  if (done || wrong >= 6) {
    over = true; if (done) { streak++; if (streak > best) { best = streak; sv(KEY, best); } } else streak = 0;
    $("res").innerHTML = done ? `<b>🎉 정답! ${word.toUpperCase()}</b><p class="muted">${meaning}</p>` : `<b>아쉬워요 😢 정답은 ${word.toUpperCase()}</b><p class="muted">${meaning}</p>`; $("res").hidden = false; $("next").hidden = false;
  }
  render();
}
$("kb").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) press(b.dataset.k); });
document.addEventListener("keydown", e => { if (!e.ctrlKey && !e.metaKey && /^[a-z]$/i.test(e.key)) press(e.key.toLowerCase()); });
$("next").onclick = newWord; newWord();''',
 css=".wd{letter-spacing:.08em;word-break:break-all}.kb{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}.k{padding:10px 0;border-radius:10px;border:1px solid var(--line);background:var(--surface);font-weight:700;min-width:0}.k.ok{background:var(--ok);color:#fff;border-color:var(--ok)}.k.no{opacity:.4;text-decoration:line-through}.k:disabled{cursor:default}")

# ---------- 10 만들기 ----------
make(H+"ten-pairs.html", "10 만들기", "🔟", 195, "tenpairs-best-v1",
 "숫자 두 개를 눌러서 <b>합이 10</b>이 되면 둘이 사라져요. 판 위의 숫자를 <b>모두 지우면</b> 성공! 틀리게 누르면 시간이 3초 늘어나요. 빨리 지울수록 좋은 기록이에요.",
 r'''  <div class="seg" id="lv" style="--n:3"><button type="button" data-n="5" class="on">쉬움<small>5×6</small></button><button type="button" data-n="7">보통<small>6×7</small></button><button type="button" data-n="9">어려움<small>7×8</small></button></div>
  <div class="stats"><div class="stat"><small>시간</small><b id="time">0.0</b></div><div class="stat"><small>남은 짝</small><b id="left">0</b></div><div class="stat"><small>최고 기록</small><b id="best">-</b></div></div>
  <div class="tgrid" id="grid"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새로 하기</button>''',
 r'''const SIZE = { 5: [5, 6], 7: [6, 7], 9: [7, 8] };
let lvl = 5, cells = [], sel = -1, t0 = 0, pen = 0, done = false, best = ld(KEY) || {}, tm = 0, tempo = 1;
function newGame() {
  const [c, r] = SIZE[lvl], n = c * r - ((c * r) % 2), pairs = n / 2, arr = [];
  for (let k = 0; k < pairs; k++) { const a = ri(1, 9); arr.push(a, 10 - a); }
  while (arr.length < c * r) arr.push(0);                               // 홀수 칸이면 빈칸 하나
  cells = shuf(arr).map(v => ({ v, gone: v === 0 })); sel = -1; pen = 0; done = false; t0 = Date.now(); $("res").hidden = true;
  $("grid").style.gridTemplateColumns = `repeat(${c}, 1fr)`; render();
}
function render() {
  $("grid").innerHTML = cells.map((x, i) => `<button type="button" class="tc${x.gone ? " gone" : ""}${i === sel ? " sel" : ""}" data-i="${i}" ${x.gone ? "disabled" : ""} aria-label="${x.v}">${x.gone ? "" : x.v}</button>`).join("");
  $("left").textContent = cells.filter(x => !x.gone).length / 2; $("best").textContent = best[lvl] ? best[lvl].toFixed(1) + "초" : "-";
}
function tap(i) {
  if (done || cells[i].gone) return;
  if (sel < 0) { sel = i; return render(); }
  if (sel === i) { sel = -1; return render(); }
  if (cells[sel].v + cells[i].v === 10) { cells[sel].gone = cells[i].gone = true; sel = -1; if (cells.every(x => x.gone)) win(); }
  else { pen += 3; sel = -1; $("grid").classList.add("shake"); setTimeout(() => $("grid").classList.remove("shake"), 250); }
  render();
}
const elapsed = () => (Date.now() - t0) / 1000 + pen;
function win() { done = true; const s = elapsed(), nb = !best[lvl] || s < best[lvl]; if (nb) { best[lvl] = s; sv(KEY, best); } $("res").innerHTML = `<b>🎉 모두 지웠어요! ${s.toFixed(1)}초</b><p class="muted">${nb ? "신기록이에요!" : "최고 기록 " + best[lvl].toFixed(1) + "초"} · 틀린 벌점 ${pen}초</p>`; $("res").hidden = false; }
$("grid").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b) tap(+b.dataset.i); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); lvl = +b.dataset.n; newGame(); });
$("again").onclick = newGame;
tm = setInterval(() => { if (!done) $("time").textContent = elapsed().toFixed(1); }, 100); newGame();''',
 css=".tgrid{display:grid;gap:6px}.tgrid.shake{animation:sh .25s}@keyframes sh{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}.tc{aspect-ratio:1;border-radius:12px;border:2px solid var(--line);background:var(--surface);font-family:var(--font-display);font-size:clamp(1.4rem,7vw,2rem);padding:0;min-width:0}.tc.sel{border-color:var(--accent);background:var(--soft)}.tc.gone{visibility:hidden}")

# ---------- 수열 퀴즈 ----------
make(H+"sequence-quiz.html", "수열 퀴즈", "🔢", 245, "sequence-quiz-best-v1",
 "숫자가 어떤 규칙으로 늘어나는지 찾아서 <b>빈칸에 들어갈 숫자</b>를 골라 보세요. 10문제를 풀면 결과가 나와요.",
 r'''  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card center"><p class="big" id="seq"></p><p class="muted" id="why"></p></div>
  <div class="seg" id="opts" style="--n:2;grid-template-columns:1fr 1fr"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>''',
 r'''let qs = [], i = 0, score = 0, best = ld(KEY) || 0, locked = false;
function makeSeq(level) {
  const t = ri(0, level > 5 ? 6 : 4), a = ri(1, 9); let s = [], why = "";
  if (t === 0) { const d = ri(2, 9); s = Array.from({ length: 6 }, (_, k) => a + d * k); why = `${d}씩 커져요`; }
  else if (t === 1) { const d = ri(2, 6); s = Array.from({ length: 6 }, (_, k) => a + 40 - d * k); why = `${d}씩 작아져요`; }
  else if (t === 2) { const m = ri(2, 3); s = Array.from({ length: 6 }, (_, k) => (a % 3 + 1) * m ** k); why = `${m}배씩 커져요`; }
  else if (t === 3) { s = Array.from({ length: 6 }, (_, k) => (k + 1) ** 2); why = "제곱수(1×1, 2×2, 3×3…)예요"; }
  else if (t === 4) { const d = ri(1, 4); s = Array.from({ length: 6 }, (_, k) => a + (k * (k + 1) / 2) * d); why = "더하는 수가 1씩 커져요"; }
  else if (t === 5) { s = [a, a + 1]; while (s.length < 6) s.push(s[s.length - 1] + s[s.length - 2]); why = "앞의 두 수를 더해요"; }
  else { const d = ri(2, 5), e = ri(1, 3); s = [a]; while (s.length < 6) s.push(s[s.length - 1] + (s.length % 2 ? d : -e)); why = `+${d}, -${e}를 번갈아 해요`; }
  return { s, why };
}
function newRound() {
  qs = Array.from({ length: 10 }, (_, k) => { const { s, why } = makeSeq(k); const hole = ri(3, 5), ans = s[hole], wrong = new Set(); while (wrong.size < 3) { const w = ans + ri(-6, 6); if (w !== ans && w > 0) wrong.add(w); } return { s, why, hole, ans, opts: shuf([ans, ...wrong]) }; });
  i = 0; score = 0; $("res").hidden = true; show();
}
function show() {
  const q = qs[i]; locked = false; $("next").hidden = true; $("why").textContent = "";
  $("seq").textContent = q.s.map((v, k) => k === q.hole ? "?" : v).join(", ");
  $("opts").innerHTML = q.opts.map((o, k) => `<button type="button" data-k="${k}">${o}</button>`).join("");
  $("no").textContent = (i + 1) + "/10"; $("score").textContent = score; $("best").textContent = best;
}
function pick(k) {
  if (locked) return; locked = true; const q = qs[i], ok = q.opts[k] === q.ans; if (ok) score++;
  document.querySelectorAll("#opts button").forEach((b, n) => { b.disabled = true; if (q.opts[n] === q.ans) b.classList.add("on"); });
  $("seq").textContent = q.s.join(", "); $("why").textContent = (ok ? "⭕ " : "❌ ") + q.why; $("score").textContent = score; $("next").textContent = i === 9 ? "결과 보기" : "다음 문제"; $("next").hidden = false;
}
function finish() { let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("seq").textContent = "끝!"; $("opts").innerHTML = ""; $("next").hidden = true; $("res").innerHTML = `<b>10문제 중 ${score}개 정답</b><p class="muted">${score >= 9 ? "수학 천재! 🎓" : score >= 6 ? "잘했어요 👍" : "규칙을 더 찾아봐요 💪"}${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("res").hidden = false; $("best").textContent = best; $("again").onclick = newRound; }
$("opts").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) pick(+b.dataset.k); });
$("next").onclick = () => { if (i === 9) finish(); else { i++; show(); } }; newRound();''',
 css=".seg button{padding:14px 4px;font-family:var(--font-display);font-size:1.5rem;font-weight:400}")
