import sys, json
sys.path.insert(0, ".")
from mkpage import make

# ---------------- 진실 혹은 벌칙 ----------------
truths = ["요즘 가장 웃겼던 일은?", "가장 좋아하는 음식과 싫어하는 음식은?", "어릴 때 가장 무서웠던 것은?", "지금 가장 갖고 싶은 것은?", "살면서 가장 창피했던 순간은?", "우리 가족 중 가장 닮고 싶은 사람은 누구?", "하루 동안 투명인간이 된다면 뭘 하고 싶어?", "가장 최근에 울었던 일은?", "사실은 잘 못하는데 아닌 척하는 것은?", "로또 1등에 당첨되면 제일 먼저 뭘 할래?",
          "요즘 휴대폰에서 가장 많이 쓰는 앱은?", "어렸을 때 가장 좋아했던 만화나 노래는?", "가장 기억에 남는 여행지는?", "오늘 하루 중 가장 기분 좋았던 순간은?", "가장 좋아하는 계절과 그 이유는?", "슈퍼 파워가 하나 생긴다면 어떤 힘을 갖고 싶어?", "지금 여기 있는 사람 중 칭찬하고 싶은 사람과 이유는?", "무인도에 딱 하나만 가져간다면?", "남에게 들은 말 중 가장 기분 좋았던 말은?", "가장 자신 있는 요리는?",
          "올해 꼭 이루고 싶은 목표는?", "처음 학교(또는 직장)에 간 날을 기억해?", "가장 좋아하는 영화나 드라마는?", "잠들기 전에 꼭 하는 일은?", "사실은 잘 모르면서 아는 척했던 적이 있어?"]
dares = ["10초 동안 웃지 않고 버티기", "가장 좋아하는 노래 한 소절 부르기", "동물 흉내 내기 (다른 사람이 맞히면 성공)", "옆 사람 어깨를 10초 동안 주물러 주기", "제자리에서 팔 벌려 뛰기 10번", "표정만으로 기쁨, 슬픔, 화남 연기하기", "가족 한 명을 3가지로 칭찬하기", "눈을 감고 제자리에서 5바퀴 돌기", "아기처럼 말하며 자기소개하기", "가장 좋아하는 광고 따라 하기",
         "성대모사 하나 보여 주기", "한 손으로 코를 잡고 다른 손으로 귀를 잡고 3바퀴 돌기", "다음 차례까지 말끝마다 '~냥'을 붙여 말하기", "'간장 공장 공장장'을 빠르게 3번 말하기", "마이크를 잡은 것처럼 한 곡 부르기", "슬로모션으로 인사하기", "5초 동안 모델 포즈 취하기", "엉덩이로 자기 이름 쓰기", "1분 동안 존댓말만 쓰기", "박수를 20번 치되 웃지 않기",
         "옆 사람의 동작을 10초 동안 따라 하기", "좋아하는 음식을 몸짓으로만 설명하기", "무릎 꿇고 큰절 올리기 (웃으면 한 번 더)", "제일 크게 웃는 소리 내기", "30초 동안 한 발로 서 있기"]
make("out/truth-dare.html", "진실 혹은 벌칙", "🃏", 275, "truthdare-v1",
     "'진실'은 솔직하게 대답하는 질문 카드, '벌칙'은 몸으로 하는 미션 카드예요. 둘러앉아 휴대폰을 돌리며 한 장씩 뽑으세요. 모든 카드를 한 번씩 쓰면 다시 섞여요. 불편한 질문은 '패스'해도 좋아요!",
     r'''  <div class="stats"><div class="stat"><small>진실 카드</small><b id="ct">0</b></div><div class="stat"><small>벌칙 카드</small><b id="cd">0</b></div><div class="stat"><small>뽑은 수</small><b id="cn">0</b></div></div>
  <div class="cardbox" id="cardbox" aria-live="polite"><p class="muted">아래 버튼을 눌러 카드를 뽑으세요</p></div>
  <div class="row"><button class="btn" id="t" type="button">진실 🗣️</button><button class="btn" id="d" type="button" style="background:var(--bad)">벌칙 🎬</button></div>
  <button class="btn ghost" id="r" type="button">아무거나 뽑기 🎲</button>''',
     r'''const TRUTH = %s;
const DARE = %s;
let deck = { t: shuf(TRUTH), d: shuf(DARE) }, used = { t: 0, d: 0, n: 0 };
// 카드를 한 장씩 꺼낸다. 다 쓰면 다시 섞는다 (같은 카드가 연속으로 나오지 않게)
function draw(kind) { if (!deck[kind].length) deck[kind] = shuf(kind === "t" ? TRUTH : DARE); const c = deck[kind].pop(); used[kind]++; used.n++; return c; }
function show(kind) { const c = draw(kind); $("cardbox").className = "cardbox " + kind; $("cardbox").innerHTML = `<small>${kind === "t" ? "🗣️ 진실" : "🎬 벌칙"}</small><div class="big">${esc(c)}</div>`; $("ct").textContent = used.t; $("cd").textContent = used.d; $("cn").textContent = used.n; try { navigator.vibrate && navigator.vibrate(30); } catch (e) {} }
$("t").onclick = () => show("t"); $("d").onclick = () => show("d"); $("r").onclick = () => show(Math.random() < .5 ? "t" : "d");''' % (json.dumps(truths, ensure_ascii=False), json.dumps(dares, ensure_ascii=False)),
     css=".cardbox{min-height:210px;background:var(--surface);border:2px dashed var(--line);border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center;padding:18px}.cardbox.t{border:3px solid var(--accent);background:var(--soft)}.cardbox.d{border:3px solid var(--bad);background:color-mix(in srgb,var(--bad) 10%,var(--surface))}.cardbox small{font-weight:700;color:var(--muted)}.cardbox .big{font-size:clamp(1.4rem,7vw,2rem)}")

# ---------------- 밸런스 게임 ----------------
bal = [["평생 여름만 계속되기", "평생 겨울만 계속되기"], ["평생 라면만 먹기", "평생 치킨만 먹기"], ["하늘을 마음껏 날 수 있기", "투명인간이 될 수 있기"], ["과거로 시간 여행하기", "미래로 시간 여행하기"], ["매일 늦잠 자고 지각하기", "매일 일찍 일어나서 시간이 남기"], ["동물과 대화할 수 있기", "세상의 모든 언어를 할 수 있기"],
       ["한 달 동안 집 안에서만 지내기", "한 달 동안 집 밖에서만 지내기"], ["지금 100만 원 받기", "1년 뒤에 150만 원 받기"], ["잠을 안 자도 괜찮은 몸", "밥을 안 먹어도 괜찮은 몸"], ["아침형 인간", "저녁형 인간"], ["바다로 여행 가기", "산으로 여행 가기"], ["강아지와 함께 살기", "고양이와 함께 살기"],
       ["평생 단 음식만 먹기", "평생 짠 음식만 먹기"], ["키가 10cm 더 커지기", "달리기가 엄청 빨라지기"], ["노래를 아주 잘하기", "춤을 아주 잘하기"], ["만화 속 세상에서 하루 살기", "영화 속 세상에서 하루 살기"], ["친구 100명과 얕게 지내기", "진짜 친한 친구 1명과 깊게 지내기"], ["매일 아이스크림 먹기", "매일 피자 먹기"],
       ["눈 내리는 크리스마스", "햇살 가득한 크리스마스"], ["좋아하는 연예인 만나기", "좋아하는 만화 주인공 만나기"], ["비 오는 날 우산 없이 걷기", "맑은 날 우산 쓰고 걷기"], ["평생 휴대폰 없이 살기", "평생 TV와 컴퓨터 없이 살기"], ["용돈 두 배, 대신 방학 없음", "용돈 그대로, 방학 두 배"], ["하루 종일 말 한마디도 못 하기", "하루 종일 쉬지 않고 말해야 하기"],
       ["여행 가서 비만 오기", "집에 있는데 날씨는 최고"], ["항상 5분 일찍 도착하기", "항상 5분 늦게 도착하지만 맛집 가기"], ["수영장 하나를 통째로 쓰기", "놀이공원 하나를 통째로 쓰기"], ["내 방에 큰 침대", "내 방에 큰 책장"]]
make("out/balance-game.html", "밸런스 게임", "⚖️", 330, "balance-v1",
     "두 가지 중 하나를 골라야 하는 질문이에요. 고른 뒤에는 가족과 '왜 그걸 골랐는지' 서로 이야기해 보세요. 정답은 없어요!",
     r'''  <div class="stats" style="grid-template-columns:repeat(2,1fr)"><div class="stat"><small>답한 질문</small><b id="cnt">0</b></div><div class="stat"><small>A를 고른 비율</small><b id="pa">-</b></div></div>
  <div class="card center"><small class="muted" id="no"></small><h2>둘 중 하나만 고른다면?</h2></div>
  <button class="opt a" id="a" type="button"></button><div class="center big" style="font-size:1.4rem;color:var(--muted)">VS</div><button class="opt b" id="b" type="button"></button>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="next" type="button">다음 질문</button>''',
     r'''const Q = %s;
let st = ld(KEY) || { a: 0, b: 0 }, order = shuf(Q.map((_, i) => i)), pos = 0, chosen = false;
function show() { const q = Q[order[pos]]; chosen = false; $("a").textContent = "🅰️ " + q[0]; $("b").textContent = "🅱️ " + q[1]; $("a").className = "opt a"; $("b").className = "opt b"; $("res").hidden = true; $("no").textContent = `질문 ${pos + 1} / ${Q.length}`; stats(); }
function stats() { $("cnt").textContent = st.a + st.b; $("pa").textContent = st.a + st.b ? Math.round(st.a / (st.a + st.b) * 100) + "%%" : "-"; }
function pick(side) {
  if (chosen) return; chosen = true; st[side]++; sv(KEY, st); $(side).classList.add("picked"); $(side === "a" ? "b" : "a").classList.add("dim");
  $("res").innerHTML = `<b>${side === "a" ? "🅰️" : "🅱️"}를 골랐어요!</b><p class="muted">왜 그걸 골랐는지 서로 이야기해 보세요 💬</p>`; $("res").hidden = false; stats();
}
$("a").onclick = () => pick("a"); $("b").onclick = () => pick("b");
$("next").onclick = () => { pos++; if (pos >= order.length) { order = shuf(order); pos = 0; } show(); }; show();''' % json.dumps(bal, ensure_ascii=False),
     css=".opt{border:3px solid var(--line);background:var(--surface);border-radius:20px;padding:22px 16px;font-family:var(--font-display);font-size:1.35rem;line-height:1.35;min-height:96px;overflow-wrap:anywhere}.opt.a{border-color:#e8453c}.opt.b{border-color:#2f7fe0}.opt.picked{background:var(--accent);color:var(--accent-fg);border-color:var(--accent)}.opt.dim{opacity:.4}")

# ---------------- 음식 월드컵 ----------------
foods = [["🍕", "피자"], ["🍔", "햄버거"], ["🍣", "초밥"], ["🍜", "라면"], ["🍗", "치킨"], ["🥟", "만두"], ["🍝", "파스타"], ["🌮", "타코"], ["🍙", "주먹밥"], ["🍛", "카레"], ["🥩", "스테이크"], ["🍤", "튀김"], ["🍞", "빵"], ["🥗", "샐러드"], ["🍦", "아이스크림"], ["🍩", "도넛"],
         ["🍰", "케이크"], ["🍟", "감자튀김"], ["🌭", "핫도그"], ["🍲", "전골"], ["🍢", "오뎅꼬치"], ["🥞", "팬케이크"], ["🧇", "와플"], ["🍫", "초콜릿"], ["🍪", "쿠키"], ["🍉", "수박"], ["🍓", "딸기"], ["🍖", "갈비"], ["🌯", "부리또"], ["🥪", "샌드위치"], ["🍱", "도시락"], ["🍡", "떡꼬치"]]
make("out/food-worldcup.html", "음식 월드컵", "🏆", 12, "foodcup-v1",
     "두 음식 중 더 먹고 싶은 쪽을 눌러서 16강부터 결승까지 올라가요. 마지막에 남은 음식이 오늘의 메뉴 후보예요! 가족과 같이 하면 의견이 갈려서 더 재미있어요.",
     r'''  <div class="stats" style="grid-template-columns:repeat(2,1fr)"><div class="stat"><small>라운드</small><b id="round">16강</b></div><div class="stat"><small>진행</small><b id="prog">1/8</b></div></div>
  <div class="bar"><i id="bar"></i></div>
  <div class="versus" id="vs"></div>
  <div class="res" id="win" hidden></div>
  <button class="btn" id="again" type="button" hidden>다시 하기</button>''',
     r'''const FOODS = %s;
let list, winners, i, rnd, champion, hist = ld(KEY) || {};
const ROUND = n => (n === 2 ? "결승" : n + "강");
function start() { list = shuf(FOODS).slice(0, 16); winners = []; i = 0; champion = null; $("win").hidden = true; $("again").hidden = true; show(); }
function show() {
  const n = list.length, a = list[i * 2], b = list[i * 2 + 1];
  $("round").textContent = ROUND(n); $("prog").textContent = `${i + 1}/${n / 2}`; $("bar").style.width = ((16 - n + i * 2) / 15 * 100) + "%%";
  $("vs").innerHTML = [a, b].map((f, k) => `<button type="button" class="food" data-k="${k}"><span>${f[0]}</span><b>${esc(f[1])}</b></button>`).join(`<div class="vsmark">VS</div>`).replace('</button><div', '</button><div');
}
function pick(k) {
  winners.push(list[i * 2 + k]); i++;
  if (i * 2 >= list.length) { if (winners.length === 1) return finish(winners[0]); list = winners; winners = []; i = 0; }
  show();
}
function finish(f) { champion = f; hist[f[1]] = (hist[f[1]] || 0) + 1; sv(KEY, hist); $("vs").innerHTML = ""; $("round").textContent = "우승!"; $("prog").textContent = "🎉"; $("bar").style.width = "100%%"; const top = Object.entries(hist).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([n, c]) => `${n} ${c}회`).join(" · ");
  $("win").innerHTML = `<div class="big">${f[0]}</div><b>${esc(f[1])}</b><p class="muted">오늘의 메뉴 우승!${top ? "<br>지금까지 우승: " + esc(top) : ""}</p>`; $("win").hidden = false; $("again").hidden = false; }
$("vs").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) pick(+b.dataset.k); });
$("again").onclick = start; start();''' % json.dumps(foods, ensure_ascii=False),
     css=".bar{height:10px;background:var(--line);border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--accent);transition:width .3s}.versus{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center}.vsmark{font-family:var(--font-display);color:var(--muted);font-size:1.2rem}.food{background:var(--surface);border:3px solid var(--line);border-radius:22px;min-height:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:8px}.food span{font-size:4.2rem;line-height:1}.food b{font-family:var(--font-display);font-weight:400;font-size:1.35rem}.food:active{transform:scale(.96);border-color:var(--accent)}")

# ---------------- 빙고 ----------------
make("out/bingo.html", "빙고", "🔢", 100, "bingo-v1",
     "1~25가 적힌 내 판에서 <b>부르고 싶은 숫자를 눌러요.</b> 불린 숫자는 두 판(내 판, 컴퓨터 판)에 모두 표시돼요. 가로, 세로, 대각선으로 한 줄이 다 차면 빙고 1줄! <b>먼저 5줄</b>을 만들면 이겨요. 컴퓨터가 5줄을 먼저 만들면 져요.",
     r'''  <div class="stats"><div class="stat"><small>내 빙고</small><b id="my">0줄</b></div><div class="stat"><small>방금 부른 수</small><b id="last">-</b></div><div class="stat"><small>컴퓨터 빙고</small><b id="cp">0줄</b></div></div>
  <div class="turn" id="turn" aria-live="polite"></div>
  <div class="board" id="board" role="grid" aria-label="빙고 판"></div>
  <div class="res" id="res" hidden></div>
  <button class="btn" id="new" type="button">새 판</button>''',
     r'''const LINES = []; for (let r = 0; r < 5; r++) { LINES.push([0, 1, 2, 3, 4].map(c => r * 5 + c)); LINES.push([0, 1, 2, 3, 4].map(c => c * 5 + r)); } LINES.push([0, 6, 12, 18, 24], [4, 8, 12, 16, 20]);
let mine, comp, called, over, busy, lastNo, best = ld(KEY) || { w: 0, l: 0, d: 0 };
// 불린 숫자(called)만 보고 완성된 줄의 수를 센다. 판은 칸 번호 → 숫자 배열이다
const lines = (board, called) => LINES.filter(l => l.every(i => called.has(board[i]))).length;
function newGame() { mine = shuf(Array.from({ length: 25 }, (_, i) => i + 1)); comp = shuf(Array.from({ length: 25 }, (_, i) => i + 1)); called = new Set(); over = false; busy = false; lastNo = null; $("res").hidden = true; render(); }
function check() {
  const a = lines(mine, called), b = lines(comp, called);
  if (a >= 5 || b >= 5) { over = true; if (a >= 5 && b >= 5) { best.d++; res("🤝 동시에 5줄! 비겼어요"); } else if (a >= 5) { best.w++; res("🎉 내가 이겼어요!"); } else { best.l++; res("😢 컴퓨터가 먼저 5줄을 만들었어요"); } sv(KEY, best); return true; } return false;
}
function res(t) { $("res").innerHTML = `<b>${t}</b><p class="muted">전적 ${best.w}승 ${best.d}무 ${best.l}패</p>`; $("res").hidden = false; }
function call(n) { called.add(n); lastNo = n; }
// 컴퓨터는 자기 판에서 가장 많이 채워진 줄을 완성시키는 숫자를 고른다
function compPick() {
  const left = [...Array(25).keys()].map(i => i + 1).filter(n => !called.has(n)); let best = -1, pick = [];
  for (const n of left) { let s = 0; for (const l of LINES) if (l.some(i => comp[i] === n)) s += l.filter(i => called.has(comp[i])).length ** 2; if (s > best) { best = s; pick = [n]; } else if (s === best) pick.push(n); }
  if (Math.random() < .3) return left[Math.floor(Math.random() * left.length)];      // 가끔은 아무 숫자나 불러서 사람에게도 기회를 준다
  return pick[Math.floor(Math.random() * pick.length)];
}
function tap(i) {
  if (over || busy || called.has(mine[i])) return; call(mine[i]); render(); if (check()) return render();
  busy = true; render(); setTimeout(() => { call(compPick()); busy = false; check(); render(); }, 700);
}
function render() {
  $("board").innerHTML = mine.map((n, i) => `<button type="button" class="bc ${called.has(n) ? "on" : ""} ${n === lastNo ? "last" : ""}" data-i="${i}" ${called.has(n) || over || busy ? "disabled" : ""}>${n}</button>`).join("");
  $("my").textContent = lines(mine, called) + "줄"; $("cp").textContent = lines(comp, called) + "줄"; $("last").textContent = lastNo ?? "-";
  $("turn").textContent = over ? "게임 끝" : busy ? "컴퓨터가 숫자를 고르는 중…" : "부르고 싶은 숫자를 누르세요";
}
$("board").addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b && !b.disabled) tap(+b.dataset.i); });
$("new").onclick = newGame; newGame();''',
     css=".turn{text-align:center;font-family:var(--font-display);font-size:1.3rem;min-height:1.8em}.board{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;background:var(--line);padding:6px;border-radius:16px}.bc{aspect-ratio:1;border:0;border-radius:10px;background:var(--surface);font-family:var(--font-display);font-size:1.5rem;padding:0}.bc.on{background:var(--accent);color:var(--accent-fg)}.bc.last{box-shadow:0 0 0 3px #ffd23f inset}.bc:disabled{cursor:default}")
