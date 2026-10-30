import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"
SENT = ["나는 오늘 학교에 갔어요", "우리 가족은 주말에 공원에서 놀았어요", "엄마가 맛있는 김치찌개를 끓여 주셨어요", "하늘에 하얀 구름이 둥실 떠 있어요", "동생이 마당에서 강아지와 함께 뛰어놀아요", "할머니께서 시장에서 사과를 사 오셨어요", "비가 오는 날에는 우산을 써야 해요", "나는 친구와 함께 도서관에서 책을 읽었어요", "봄에는 예쁜 꽃이 많이 피어요", "아빠는 매일 아침 일찍 일어나세요", "우리 반 친구들은 운동장에서 축구를 해요", "겨울에는 눈이 내려서 눈사람을 만들 수 있어요", "바닷가에서 조개를 줍고 모래성을 쌓았어요", "선생님께서 숙제를 내 주셨어요", "토끼는 당근을 좋아하고 호랑이는 고기를 좋아해요", "주말에 가족과 함께 영화를 보러 갔어요", "나는 저녁에 샤워를 하고 일찍 잠자리에 들어요", "내일은 소풍을 가는 날이라서 설레요", "세종대왕께서 한글을 만드셨어요", "여름 방학에는 시원한 수박을 먹어요", "버스를 타고 할머니 댁에 갔어요", "우리나라의 수도는 서울이에요", "달은 지구 둘레를 돌고 있어요", "책상 위에 필통과 공책이 놓여 있어요", "오늘 저녁 메뉴는 불고기와 잡채예요", "교실에서는 큰 소리로 떠들면 안 돼요", "강아지가 꼬리를 흔들며 달려와요", "생일 케이크에 초를 꽂고 노래를 불렀어요", "나는 커서 멋진 과학자가 되고 싶어요", "지하철에서는 어른께 자리를 양보해요"]
make(H+"sentence-order.html", "문장 순서 맞추기", "🧩", 62, "sentence-order-best-v1",
 "뒤죽박죽 섞인 <b>낱말 조각을 순서대로 눌러서</b> 올바른 문장을 만들어 보세요. 잘못 눌렀다면 아래 문장에서 조각을 눌러 빼거나, ⌫ 버튼으로 하나씩 지울 수 있어요.",
 r'''  <div class="stats"><div class="stat"><small>문제</small><b id="no">1/10</b></div><div class="stat"><small>맞힌 수</small><b id="score">0</b></div><div class="stat"><small>최고</small><b id="best">0</b></div></div>
  <div class="card"><small class="muted">내가 만든 문장</small><div class="line" id="line"></div></div>
  <div class="bank" id="bank"></div>
  <div class="row"><button class="btn ghost" id="undo" type="button">⌫ 하나 지우기</button><button class="btn" id="check" type="button">확인</button></div>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <button class="btn" id="next" type="button" hidden>다음 문제</button>
  <div class="res" id="res" hidden></div>''',
 r'''const S = ''' + json.dumps(SENT, ensure_ascii=False) + r''';
let qs = [], i = 0, score = 0, best = ld(KEY) || 0, picked = [], words = [], locked = false;
function newRound() { qs = shuf(S).slice(0, 10); i = 0; score = 0; $("res").hidden = true; show(); }
function show() { const s = qs[i]; locked = false; picked = []; words = s.split(" "); let order; do { order = shuf(words.map((w, k) => k)); } while (order.every((v, k) => v === k) && words.length > 1); bank = order; $("msg").textContent = ""; $("next").hidden = true; $("check").hidden = false; $("undo").disabled = false; render(); $("no").textContent = (i + 1) + "/10"; $("score").textContent = score; $("best").textContent = best; }
let bank = [];
function render() {
  $("line").innerHTML = picked.length ? picked.map((k, n) => `<button type="button" class="w on" data-p="${n}">${esc(words[k])}</button>`).join("") : '<span class="muted">아래 조각을 순서대로 눌러 보세요</span>';
  $("bank").innerHTML = bank.map(k => `<button type="button" class="w" data-k="${k}" ${picked.includes(k) ? "disabled" : ""}>${esc(words[k])}</button>`).join("");
}
function check() {
  if (locked) return; if (picked.length < words.length) { $("msg").textContent = "조각을 모두 놓아 주세요"; $("msg").style.color = ""; return; }
  locked = true; const ok = picked.map(k => words[k]).join(" ") === qs[i]; if (ok) score++;
  $("msg").textContent = ok ? "⭕ 정답!" : "❌ 정답: " + qs[i]; $("msg").style.color = ok ? "var(--ok)" : "var(--bad)"; $("score").textContent = score; $("check").hidden = true; $("undo").disabled = true; $("next").textContent = i === 9 ? "결과 보기" : "다음 문제"; $("next").hidden = false;
}
function finish() { let note = ""; if (score > best) { best = score; sv(KEY, best); note = " 🏆 최고 기록이에요!"; } $("next").hidden = true; $("line").textContent = "끝!"; $("bank").innerHTML = ""; $("res").innerHTML = `<b>10문제 중 ${score}개 정답</b><p class="muted">${note}</p><button class="btn" id="again" type="button" style="margin-top:10px;width:100%">다시 하기</button>`; $("res").hidden = false; $("best").textContent = best; $("again").onclick = newRound; }
$("bank").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b && !locked) { picked.push(+b.dataset.k); render(); } });
$("line").addEventListener("click", e => { const b = e.target.closest("[data-p]"); if (b && !locked) { picked.splice(+b.dataset.p, 1); render(); } });
$("undo").onclick = () => { if (!locked) { picked.pop(); render(); } }; $("check").onclick = check; $("next").onclick = () => { if (i === 9) finish(); else { i++; show(); } }; newRound();''',
 css=".line{min-height:56px;display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}.bank{display:flex;flex-wrap:wrap;gap:8px}.w{padding:9px 12px;border-radius:12px;border:2px solid var(--line);background:var(--surface);font-weight:700;font-size:1.02rem}.w.on{border-color:var(--accent);background:var(--soft)}.w:disabled{opacity:.3}")

# ---------- 팬케이크 뒤집기 ----------
make(H+"pancake-flip.html", "팬케이크 뒤집기", "🥞", 32, "pancake-best-v1",
 "팬케이크 접시에 크기가 다른 팬케이크가 쌓여 있어요. 숫자를 눌러서 <b>그 위치부터 위쪽 전부를 뒤집을 수</b> 있어요. 가장 작은 것이 위, 가장 큰 것이 맨 아래가 되도록 <b>적은 횟수</b>로 정렬해 보세요.",
 r'''  <div class="seg" id="lv" style="--n:3"><button type="button" data-n="4" class="on">4장<small>쉬움</small></button><button type="button" data-n="5">5장<small>보통</small></button><button type="button" data-n="6">6장<small>어려움</small></button></div>
  <div class="stats"><div class="stat"><small>뒤집은 횟수</small><b id="moves">0</b></div><div class="stat"><small>기준(좋은 기록)</small><b id="par">0</b></div><div class="stat"><small>최소 기록</small><b id="best">-</b></div></div>
  <div class="stack" id="stack"></div>
  <p class="center muted">누른 팬케이크와 그 위의 팬케이크가 한꺼번에 뒤집혀요 (위 ↔ 아래)</p>
  <div class="res" id="res" hidden></div>
  <button class="btn ghost" id="again" type="button">새 판</button>''',
 r'''let n = 4, st = [], moves = 0, par = 0, done = false, best = ld(KEY) || {};
function solveMin(a) {                              // 너비 우선 탐색으로 최소 뒤집기 횟수
  const key = x => x.join(""), goal = key([...a].sort((p, q) => p - q)), seen = new Set([key(a)]); let cur = [a], d = 0;
  while (cur.length) { if (cur.some(x => key(x) === goal)) return d; const nx = []; for (const x of cur) for (let k = 2; k <= x.length; k++) { const y = [...x.slice(0, k).reverse(), ...x.slice(k)]; if (!seen.has(key(y))) { seen.add(key(y)); nx.push(y); } } cur = nx; d++; }
  return d;
}
function newGame() { do { st = shuf(Array.from({ length: n }, (_, k) => k + 1)); } while (st.every((v, k) => v === k + 1)); par = solveMin(st); moves = 0; done = false; $("res").hidden = true; render(); }
function render() {
  $("stack").innerHTML = st.map((v, k) => `<button type="button" class="pk" data-k="${k}" style="width:${28 + v * (66 / n)}%"><b>${v}</b></button>`).join("");
  $("moves").textContent = moves; $("par").textContent = par; $("best").textContent = best[n] || "-";
}
function flip(k) {
  if (done || k < 1) return; st = [...st.slice(0, k + 1).reverse(), ...st.slice(k + 1)]; moves++; render();
  if (st.every((v, q) => v === q + 1)) { done = true; const nb = !best[n] || moves < best[n]; if (nb) { best[n] = moves; sv(KEY, best); } $("res").innerHTML = `<b>🎉 정렬 완료! ${moves}번</b><p class="muted">${moves <= par ? "최소 횟수로 끝냈어요! 완벽해요 ⭐" : "최소 " + par + "번이면 가능해요"}</p>`; $("res").hidden = false; render(); }
}
$("stack").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) flip(+b.dataset.k); });
$("lv").addEventListener("click", e => { const b = e.target.closest("[data-n]"); if (!b) return; document.querySelectorAll("#lv button").forEach(x => x.classList.toggle("on", x === b)); n = +b.dataset.n; newGame(); });
$("again").onclick = newGame; newGame();''',
 css=".stack{display:flex;flex-direction:column;align-items:center;gap:4px;padding:10px;background:var(--surface);border:1px solid var(--line);border-radius:16px}.pk{height:40px;border:0;border-radius:20px;background:linear-gradient(#e7b05b,#c98a30);color:#4a2c05;font-family:var(--font-display);font-size:1.1rem;padding:0;box-shadow:0 2px 0 rgba(0,0,0,.2)}.pk b{font-weight:400}")

# ---------- 한붓그리기 ----------
make(H+"one-stroke.html", "한붓그리기", "✏️", 258, "onestroke-best-v1",
 "연필을 떼지 않고 <b>모든 선을 한 번씩만 지나가도록</b> 그려 보세요. 점을 눌러 시작하고, 이어진 다음 점을 눌러 선을 따라가요. 같은 선을 두 번 지나갈 수는 없어요. 어떤 점에서 시작해도 돼요!",
 r'''  <div class="stats"><div class="stat"><small>단계</small><b id="lv">1/8</b></div><div class="stat"><small>남은 선</small><b id="left">0</b></div><div class="stat"><small>완료</small><b id="cleared">0</b></div></div>
  <svg class="os" id="svg" viewBox="0 0 300 300" aria-label="한붓그리기 판"></svg>
  <p class="center" id="msg" style="min-height:1.5em;font-weight:700"></p>
  <div class="row"><button class="btn ghost" id="reset" type="button">처음부터</button><button class="btn" id="next" type="button" hidden>다음 단계</button></div>''',
 r'''// 각 단계: 점 좌표와 선 목록 (모두 한붓그리기가 가능하도록 만들었어요: 홀수점이 0개 또는 2개)
const LV = [
 { p: [[150, 40], [60, 230], [240, 230]], e: [[0, 1], [1, 2], [2, 0]] },
 { p: [[60, 60], [240, 60], [240, 240], [60, 240]], e: [[0, 1], [1, 2], [2, 3], [3, 0]] },
 { p: [[60, 60], [240, 60], [240, 240], [60, 240]], e: [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]] },
 { p: [[150, 40], [60, 130], [240, 130], [60, 240], [240, 240]], e: [[0, 1], [0, 2], [1, 2], [1, 3], [2, 4], [3, 4]] },
 { p: [[150, 40], [40, 120], [260, 120], [80, 250], [220, 250]], e: [[0, 1], [1, 3], [3, 4], [4, 2], [2, 0], [0, 3], [0, 4]] },
 { p: [[60, 60], [150, 60], [240, 60], [60, 150], [150, 150], [240, 150]], e: [[0, 1], [1, 2], [3, 4], [4, 5], [0, 3], [1, 4], [2, 5]] },
 { p: [[150, 150], [150, 40], [260, 150], [150, 260], [40, 150]], e: [[0, 2], [0, 4], [1, 2], [2, 3], [3, 4], [4, 1]] },
 { p: [[150, 40], [250, 110], [215, 230], [85, 230], [50, 110]], e: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [0, 2], [2, 4], [4, 1], [1, 3], [3, 0]] }];
let lv = 0, used = [], cur = -1, cleared = ld(KEY) || 0, history = [];
function load(l) { lv = l; used = LV[l].e.map(() => false); cur = -1; history = []; $("msg").textContent = ""; $("next").hidden = true; render(); }
const edgeIdx = (a, b) => LV[lv].e.findIndex(([x, y], k) => !used[k] && ((x === a && y === b) || (x === b && y === a)));
function render() {
  const { p, e } = LV[lv]; let h = "";
  e.forEach(([a, b], k) => { h += `<line x1="${p[a][0]}" y1="${p[a][1]}" x2="${p[b][0]}" y2="${p[b][1]}" class="${used[k] ? "u" : ""}"/>`; });
  p.forEach(([x, y], k) => { const can = cur < 0 || edgeIdx(cur, k) >= 0; h += `<circle cx="${x}" cy="${y}" r="16" class="n${k === cur ? " cur" : ""}${cur >= 0 && k !== cur && can ? " can" : ""}" data-k="${k}"/>`; });
  $("svg").innerHTML = h; $("lv").textContent = (lv + 1) + "/" + LV.length; $("left").textContent = used.filter(x => !x).length; $("cleared").textContent = cleared;
}
function tap(k) {
  if (used.every(x => x)) return; if (cur < 0) { cur = k; history = [k]; return render(); }
  const ei = edgeIdx(cur, k); if (ei < 0) { if (k === cur) { cur = history.length > 1 ? cur : -1; } return render(); }
  used[ei] = true; cur = k; history.push(k); render();
  if (used.every(x => x)) { cleared = Math.max(cleared, lv + 1); sv(KEY, cleared); $("cleared").textContent = cleared; $("msg").textContent = "🎉 성공! 모든 선을 한 번씩 지났어요"; $("msg").style.color = "var(--ok)"; if (lv < LV.length - 1) $("next").hidden = false; else $("msg").textContent += " 마지막 단계까지 끝!"; }
  else if (!LV[lv].e.some(([a, b], q) => !used[q] && (a === cur || b === cur))) { $("msg").textContent = "더 갈 선이 없어요. 처음부터 다시 해 보세요"; $("msg").style.color = "var(--bad)"; }
}
$("svg").addEventListener("click", e => { const c = e.target.closest("[data-k]"); if (c) tap(+c.dataset.k); });
$("reset").onclick = () => load(lv); $("next").onclick = () => load(lv + 1); load(0);''',
 css=".os{width:100%;max-width:380px;margin:0 auto;display:block;background:var(--surface);border:1px solid var(--line);border-radius:16px;touch-action:manipulation}.os line{stroke:var(--muted);stroke-width:6;stroke-linecap:round}.os line.u{stroke:var(--accent)}.os circle.n{fill:var(--surface);stroke:var(--fg);stroke-width:4;cursor:pointer}.os circle.cur{fill:var(--accent)}.os circle.can{stroke:var(--accent)}")
