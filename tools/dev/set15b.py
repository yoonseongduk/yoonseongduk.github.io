import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 할 일 목록 ----------
make(H+"todo-list.html", "오늘 할 일", "✅", 150, "todo-v1",
 "할 일을 적고 <b>+</b>를 누르세요. 끝낸 일은 <b>동그라미를 눌러 체크</b>해요. 얼마나 했는지 진행 막대로 보여 줘요. 폰을 꺼도 목록이 저장돼요. 끝낸 일은 한꺼번에 지울 수도 있어요.",
 r'''  <div class="card"><div class="row2"><input type="text" id="t" placeholder="할 일을 적어요 (예: 숙제하기)" maxlength="40"><button class="btn" id="add" type="button" style="padding:0 18px">＋</button></div><div class="bar"><i id="bar"></i></div><p class="muted center" id="prog"></p></div>
  <div class="chips" id="flt"></div>
  <div class="card"><div id="list"></div></div>
  <button class="btn ghost" id="clear" type="button">✔ 끝낸 일 지우기</button>''',
 r'''let items = ld(KEY) || [{ t: "책 읽기 20분", d: false }, { t: "방 정리하기", d: false }], flt = "all";
const save = () => sv(KEY, items);
function render() {
  const done = items.filter(x => x.d).length; $("bar").style.width = (items.length ? done / items.length * 100 : 0) + "%"; $("prog").textContent = items.length ? `${items.length}개 중 ${done}개 완료${done === items.length ? " 🎉 모두 끝!" : ""}` : "할 일이 없어요";
  $("flt").innerHTML = [["all", "전체"], ["todo", "할 일"], ["done", "끝낸 일"]].map(([k, n]) => `<button type="button" class="chip${flt === k ? " on" : ""}" data-f="${k}">${n}</button>`).join("");
  $("list").innerHTML = items.map((x, k) => ({ x, k })).filter(({ x }) => flt === "all" || (flt === "done") === x.d).map(({ x, k }) => `<div class="ti${x.d ? " done" : ""}"><button type="button" class="ck" data-c="${k}" aria-label="완료 체크">${x.d ? "✔" : ""}</button><span>${esc(x.t)}</span><button type="button" class="del" data-d="${k}" aria-label="삭제">✕</button></div>`).join("") || '<p class="muted center">비어 있어요</p>';
}
function add() { const t = $("t").value.trim(); if (!t) return; items.push({ t, d: false }); $("t").value = ""; save(); render(); }
$("add").onclick = add; $("t").addEventListener("keydown", e => { if (e.key === "Enter" && !e.isComposing) add(); });
$("list").addEventListener("click", e => { const c = e.target.closest("[data-c]"), d = e.target.closest("[data-d]"); if (c) items[+c.dataset.c].d = !items[+c.dataset.c].d; else if (d) items.splice(+d.dataset.d, 1); else return; save(); render(); });
$("flt").addEventListener("click", e => { const b = e.target.closest("[data-f]"); if (b) { flt = b.dataset.f; render(); } }); $("clear").onclick = () => { items = items.filter(x => !x.d); save(); render(); }; render();''',
 css=".row2{display:flex;gap:8px}.row2 input{flex:1}.bar{height:10px;border-radius:5px;background:var(--line);overflow:hidden;margin-top:10px}.bar i{display:block;height:100%;width:0;background:var(--ok);transition:width .3s}.chips{display:flex;gap:6px}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.9rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}.ti{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--line)}.ti span{flex:1;overflow-wrap:anywhere}.ti.done span{text-decoration:line-through;color:var(--muted)}.ck{width:30px;height:30px;border-radius:50%;border:2px solid var(--accent);background:var(--surface);padding:0;color:#fff;font-size:1rem}.ti.done .ck{background:var(--ok);border-color:var(--ok)}.del{width:30px;height:30px;border-radius:50%;border:0;background:transparent;color:var(--muted)}")

# ---------- 물 마시기 ----------
make(H+"water-tracker.html", "물 마시기 기록", "💧", 200, "water-v1",
 "물을 한 컵 마실 때마다 <b>💧 컵 추가</b>를 눌러요. 하루 목표 컵 수를 채우면 파란 물이 가득 차요! 최근 7일 기록도 막대로 볼 수 있어요. (1컵 = 200mL)",
 r'''  <div class="card center"><div class="cupwrap"><div class="cup"><i id="fill"></i><b id="cnt">0</b></div></div><p class="muted" id="ml"></p></div>
  <div class="row"><button class="btn ghost" id="minus" type="button">− 취소</button><button class="btn" id="plus" type="button">💧 컵 추가</button></div>
  <div class="card"><div class="step"><span>하루 목표</span><div><button type="button" id="gm">−</button><b id="goal">8</b><span>컵</span><button type="button" id="gp">＋</button></div></div></div>
  <div class="card"><b>📅 최근 7일</b><div class="hist" id="hist"></div></div>''',
 r'''const key = d => d.toISOString().slice(0, 10), todayKey = () => key(new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000));
let st = ld(KEY) || { goal: 8, log: {} };
const save = () => sv(KEY, st), n = () => st.log[todayKey()] || 0;
function render() {
  const c = n(); $("cnt").textContent = c; $("fill").style.height = Math.min(100, c / st.goal * 100) + "%"; $("ml").textContent = `${c * 200}mL · 목표 ${st.goal * 200}mL ${c >= st.goal ? "🎉 달성!" : "(" + (st.goal - c) + "컵 남음)"}`; $("goal").textContent = st.goal;
  const days = Array.from({ length: 7 }, (_, k) => { const d = new Date(); d.setDate(d.getDate() - (6 - k)); const kk = key(new Date(d.getTime() - d.getTimezoneOffset() * 60000)); return { l: "일월화수목금토"[d.getDay()], v: st.log[kk] || 0 }; });
  $("hist").innerHTML = days.map(d => `<div class="hb"><div class="b"><i class="${d.v >= st.goal ? "ok" : ""}" style="height:${Math.min(100, d.v / Math.max(st.goal, 1) * 100)}%"></i></div><small>${d.l}</small><b>${d.v}</b></div>`).join("");
}
$("plus").onclick = () => { st.log[todayKey()] = n() + 1; save(); render(); if (navigator.vibrate) navigator.vibrate(30); }; $("minus").onclick = () => { if (n() > 0) { st.log[todayKey()] = n() - 1; save(); render(); } };
$("gm").onclick = () => { st.goal = Math.max(1, st.goal - 1); save(); render(); }; $("gp").onclick = () => { st.goal = Math.min(20, st.goal + 1); save(); render(); }; render();''',
 css=".cupwrap{display:flex;justify-content:center}.cup{position:relative;width:130px;height:170px;border:4px solid var(--fg);border-top:0;border-radius:0 0 28px 28px;overflow:hidden;background:var(--surface)}.cup i{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(#5db7f0,#2f8fe0);transition:height .4s}.cup b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-weight:400;font-size:3rem;color:var(--fg);text-shadow:0 0 6px var(--surface)}.hist{display:flex;gap:8px;align-items:flex-end;height:130px;margin-top:10px}.hb{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;height:100%}.hb .b{flex:1;width:70%;background:var(--soft);border-radius:6px;display:flex;align-items:flex-end;overflow:hidden}.hb .b i{display:block;width:100%;background:#8cc8f2}.hb .b i.ok{background:var(--ok)}.hb small{color:var(--muted)}.step button{width:38px;height:38px;border-radius:50%;border:1px solid var(--line);background:var(--soft);font-size:1.3rem;padding:0}")

# ---------- 용돈 기입장 ----------
make(H+"allowance-book.html", "용돈 기입장", "💰", 95, "allowance-v1",
 "받은 돈과 쓴 돈을 적어 두면 <b>지금 얼마가 남았는지</b> 계산해 줘요. 날짜와 내용, 금액을 적고 <b>들어온 돈 / 나간 돈</b> 중에 골라 추가하세요. 이번 달에 얼마를 썼는지도 보여 줘요. 폰에 저장돼요.",
 r'''  <div class="stats"><div class="stat"><small>남은 돈</small><b id="bal">0</b></div><div class="stat"><small>이번 달 쓴 돈</small><b id="spent">0</b></div><div class="stat"><small>이번 달 받은 돈</small><b id="got">0</b></div></div>
  <div class="card"><input type="date" id="d"><input type="text" id="m" placeholder="내용 (예: 문구점, 용돈)" maxlength="20"><input type="number" id="a" inputmode="numeric" placeholder="금액 (원)"><div class="row"><button class="btn" id="in" type="button" style="background:var(--ok)">＋ 들어온 돈</button><button class="btn" id="out" type="button" style="background:var(--bad)">− 나간 돈</button></div></div>
  <div class="card"><b>📒 기록</b><div id="list"></div></div>''',
 r'''let rows = ld(KEY) || [];
const won = n => Math.abs(n).toLocaleString("ko-KR") + "원", ymd = () => { const t = new Date(); return new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 10); };
$("d").value = ymd();
function render() {
  const bal = rows.reduce((s, r) => s + r.v, 0), mon = ymd().slice(0, 7), thisM = rows.filter(r => r.d.startsWith(mon));
  $("bal").textContent = (bal < 0 ? "-" : "") + won(bal); $("spent").textContent = won(thisM.filter(r => r.v < 0).reduce((s, r) => s + r.v, 0)); $("got").textContent = won(thisM.filter(r => r.v > 0).reduce((s, r) => s + r.v, 0));
  $("list").innerHTML = rows.length ? [...rows].map((r, k) => ({ r, k })).sort((x, y) => y.r.d.localeCompare(x.r.d) || y.k - x.k).map(({ r, k }) => `<div class="ar"><div><b>${esc(r.m || "(내용 없음)")}</b><br><small class="muted">${r.d}</small></div><span class="${r.v > 0 ? "plus" : "minus"}">${r.v > 0 ? "+" : "−"}${won(r.v)}</span><button type="button" data-d="${k}" aria-label="삭제">✕</button></div>`).join("") : '<p class="muted center">아직 기록이 없어요</p>';
}
function add(sign) { const a = parseInt($("a").value); if (!(a > 0)) return; rows.push({ d: $("d").value || ymd(), m: $("m").value.trim(), v: sign * a }); sv(KEY, rows); $("m").value = ""; $("a").value = ""; render(); }
$("in").onclick = () => add(1); $("out").onclick = () => add(-1); $("list").addEventListener("click", e => { const d = e.target.closest("[data-d]"); if (d) { rows.splice(+d.dataset.d, 1); sv(KEY, rows); render(); } }); render();''',
 css=".card input{margin:4px 0}.stat b{font-size:1.05rem!important}.ar{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}.ar>div{flex:1;min-width:0}.ar .plus{color:var(--ok);font-weight:700}.ar .minus{color:var(--bad);font-weight:700}.ar button{width:30px;height:30px;border-radius:50%;border:1px solid var(--line);background:var(--soft);padding:0}")

# ---------- 스톱워치 & 타이머 ----------
make(H+"stopwatch-timer.html", "스톱워치·타이머", "⏱️", 215, "stopwatch-v1",
 "<b>스톱워치</b>는 시작/멈춤/구간 기록을, <b>타이머</b>는 라면 3분처럼 정해진 시간이 지나면 <b>소리와 진동</b>으로 알려 줘요. 위의 프리셋 버튼을 누르거나 직접 시간을 정할 수 있어요.",
 r'''  <div class="seg" id="tab" style="--n:2"><button type="button" data-t="sw" class="on">⏱ 스톱워치</button><button type="button" data-t="tm">⏳ 타이머</button></div>
  <div class="card center"><p class="big" id="clock" style="font-size:clamp(2.6rem,15vw,4rem);font-variant-numeric:tabular-nums">00:00.00</p></div>
  <div id="swp"><div class="row"><button class="btn ghost" id="lap" type="button">구간 기록</button><button class="btn" id="ss" type="button">시작</button></div><button class="btn ghost" id="swreset" type="button" style="margin-top:8px;width:100%">초기화</button><ol class="laps" id="laps"></ol></div>
  <div id="tmp" hidden><div class="chips" id="pre"></div><div class="row3"><label>분<input type="number" id="mm" min="0" max="180" value="3" inputmode="numeric"></label><label>초<input type="number" id="ss2" min="0" max="59" value="0" inputmode="numeric"></label></div><div class="row"><button class="btn ghost" id="tmreset" type="button">초기화</button><button class="btn" id="tms" type="button">시작</button></div></div>''',
 r'''let mode = "sw", run = false, t0 = 0, acc = 0, laps = [], raf = 0, total = 180000, tempo = 1, tmRun = false, endAt = 0, left = 180000;
const fmt = ms => { ms = Math.max(0, ms); const m = Math.floor(ms / 60000), s = Math.floor(ms / 1000) % 60, c = Math.floor(ms % 1000 / 10); return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(c).padStart(2, "0")}`; };
function beep() { try { const a = new (window.AudioContext || window.webkitAudioContext)(); for (let k = 0; k < 4; k++) { const o = a.createOscillator(), g = a.createGain(); o.connect(g); g.connect(a.destination); o.frequency.value = 880; g.gain.value = .25; o.start(a.currentTime + k * .35); o.stop(a.currentTime + k * .35 + .2); } } catch (e) {} if (navigator.vibrate) navigator.vibrate([300, 150, 300, 150, 300]); }
function loop() { if (mode === "sw") { const t = acc + (run ? (performance.now() - t0) * tempo : 0); $("clock").textContent = fmt(t); } else { if (tmRun) { left = endAt - performance.now() * tempo; if (left <= 0) { left = 0; tmRun = false; $("tms").textContent = "시작"; beep(); $("clock").classList.add("blink"); } } $("clock").textContent = fmt(left); } raf = requestAnimationFrame(loop); }
$("ss").onclick = () => { if (run) { acc += (performance.now() - t0) * tempo; run = false; $("ss").textContent = "계속"; } else { t0 = performance.now(); run = true; $("ss").textContent = "멈춤"; } };
$("lap").onclick = () => { const t = acc + (run ? (performance.now() - t0) * tempo : 0); if (t > 0) { laps.push(t); $("laps").innerHTML = laps.map((x, k) => `<li>구간 ${k + 1}: <b>${fmt(x)}</b> <small>(+${fmt(x - (laps[k - 1] || 0))})</small></li>`).reverse().join(""); } };
$("swreset").onclick = () => { run = false; acc = 0; laps = []; $("ss").textContent = "시작"; $("laps").innerHTML = ""; };
function setTotal() { total = ((+$("mm").value || 0) * 60 + (+$("ss2").value || 0)) * 1000; left = total; $("clock").classList.remove("blink"); }
$("pre").innerHTML = [["라면 3분", 3, 0], ["계란 7분", 7, 0], ["5분", 5, 0], ["10분", 10, 0], ["30분", 30, 0], ["양치 2분", 2, 0]].map(([n, m, s]) => `<button type="button" class="chip" data-m="${m}" data-s="${s}">${n}</button>`).join("");
$("pre").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (b) { $("mm").value = b.dataset.m; $("ss2").value = b.dataset.s; tmRun = false; $("tms").textContent = "시작"; setTotal(); } });
$("mm").oninput = $("ss2").oninput = () => { if (!tmRun) setTotal(); };
$("tms").onclick = () => { if (tmRun) { tmRun = false; $("tms").textContent = "계속"; } else { if (left <= 0) setTotal(); if (left <= 0) return; $("clock").classList.remove("blink"); endAt = performance.now() * tempo + left; tmRun = true; $("tms").textContent = "멈춤"; } };
$("tmreset").onclick = () => { tmRun = false; $("tms").textContent = "시작"; setTotal(); };
$("tab").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (!b) return; mode = b.dataset.t; document.querySelectorAll("#tab button").forEach(x => x.classList.toggle("on", x === b)); $("swp").hidden = mode !== "sw"; $("tmp").hidden = mode !== "tm"; $("clock").classList.remove("blink"); });
setTotal(); raf = requestAnimationFrame(loop);''',
 css=".blink{animation:bl .5s infinite alternate;color:var(--bad)}@keyframes bl{to{opacity:.25}}.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:.92rem}.row3{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:8px 0}.row3 label{display:flex;flex-direction:column;gap:2px;font-size:.85rem;color:var(--muted)}.laps{list-style:none;padding:0;margin:12px 0 0;display:flex;flex-direction:column;gap:6px}.laps li{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:6px 10px}")

# ---------- 오늘 뭐 먹지 ----------
MENU = {"한식": "김치찌개 된장찌개 비빔밥 불고기 삼겹살 갈비찜 제육볶음 순두부찌개 칼국수 냉면 삼계탕 떡국 잡채 닭갈비 김밥 부대찌개 감자탕 보쌈 설렁탕 청국장".split(), "중식": "짜장면 짬뽕 탕수육 볶음밥 마파두부 깐풍기 양장피 유산슬 울면 마라탕".split(), "일식": "초밥 라멘 우동 돈가스 규동 가라아게 오므라이스 소바 타코야키 카레".split(), "양식": "피자 파스타 스테이크 햄버거 리조또 샐러드 샌드위치 오믈렛 치킨 핫도그".split(), "분식": "떡볶이 순대 튀김 어묵 라볶이 김말이 쫄면 오뎅탕 치즈볼 주먹밥".split(), "간식": "아이스크림 과일 요거트 핫케이크 와플 도넛 쿠키 팝콘 호떡 붕어빵".split()}
make(H+"menu-picker.html", "오늘 뭐 먹지?", "🍽️", 18, "menu-picker-v1",
 "메뉴를 고르기 힘들 때 눌러 보세요! <b>종류를 고르고 '뭐 먹지?'</b>를 누르면 오늘의 메뉴가 두근두근 정해져요. 마음에 안 들면 다시 뽑을 수 있어요. <b>먹기 싫은 메뉴는 ✕로 빼 둘</b> 수도 있어요.",
 r'''  <div class="chips" id="cats"></div>
  <div class="card center" style="min-height:150px;justify-content:center"><p class="muted" id="cat">메뉴 종류를 고르세요</p><p class="big" id="pick" style="font-size:clamp(2.2rem,12vw,3.2rem)">🍽️</p></div>
  <button class="btn" id="go" type="button">🎲 뭐 먹지?</button>
  <div class="card"><b>메뉴 목록</b> <small class="muted">(✕를 눌러 제외)</small><div class="menu" id="menu"></div></div>''',
 r'''const MENU = ''' + json.dumps(MENU, ensure_ascii=False) + r''';
let cat = "전체", ban = new Set(ld(KEY) || []), busy = false, tempo = 1;
const pool = () => (cat === "전체" ? Object.values(MENU).flat() : MENU[cat]).filter(m => !ban.has(m));
function render() { $("cats").innerHTML = ["전체", ...Object.keys(MENU)].map(c => `<button type="button" class="chip${c === cat ? " on" : ""}" data-c="${c}">${c}</button>`).join(""); const list = cat === "전체" ? Object.values(MENU).flat() : MENU[cat]; $("menu").innerHTML = list.map(m => `<button type="button" class="mn${ban.has(m) ? " off" : ""}" data-m="${esc(m)}">${esc(m)}${ban.has(m) ? " ↩" : " ✕"}</button>`).join(""); }
async function go() { if (busy) return; const p = pool(); if (!p.length) { $("pick").textContent = "메뉴가 없어요"; return; } busy = true; $("cat").textContent = "두구두구…"; for (let k = 0; k < 14; k++) { $("pick").textContent = p[ri(0, p.length - 1)]; await new Promise(r => setTimeout(r, (60 + k * 22) * tempo)); } const w = p[ri(0, p.length - 1)]; $("pick").textContent = w; $("cat").textContent = "오늘의 메뉴는!"; if (navigator.vibrate) navigator.vibrate(120); busy = false; }
$("cats").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b) { cat = b.dataset.c; render(); } }); $("menu").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (!b) return; const m = b.dataset.m; ban.has(m) ? ban.delete(m) : ban.add(m); sv(KEY, [...ban]); render(); }); $("go").onclick = go; render();''',
 css=".chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.92rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}.menu{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.mn{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:5px 11px;font-size:.88rem}.mn.off{opacity:.4;text-decoration:line-through}")

# ---------- 오늘의 운세 ----------
make(H+"daily-fortune.html", "오늘의 운세", "🔮", 285, "fortune-v1",
 "<b>생일</b>을 넣으면 오늘의 운세를 알려 줘요! 같은 날 같은 생일이면 <b>하루 동안은 같은 결과</b>가 나와요. 행운의 색과 숫자, 오늘의 한마디도 있어요. 재미로만 봐 주세요 😊",
 r'''  <div class="card"><label class="muted" for="bd">내 생일</label><input type="date" id="bd"><button class="btn" id="go" type="button">🔮 오늘의 운세 보기</button></div>
  <div class="res" id="out" hidden></div>''',
 r'''const COLORS = ["빨강", "주황", "노랑", "초록", "파랑", "보라", "분홍", "하늘색", "하양", "검정"], ITEMS = ["연필", "손수건", "열쇠고리", "초콜릿", "우산", "책", "양말", "물병", "이어폰", "스티커"], WORDS = ["작은 친절이 큰 행운이 돼요.", "오늘은 새로운 도전을 해 봐도 좋아요.", "급할수록 천천히, 한 번 더 확인하세요.", "좋아하는 사람에게 먼저 인사해 보세요.", "하고 싶은 말은 부드럽게 말하면 통해요.", "가까운 사람과 맛있는 걸 나눠 먹어요.", "책 한 쪽이 오늘의 행운을 불러와요.", "웃음이 가장 좋은 부적이에요.", "정리정돈하면 기분이 좋아져요.", "오늘 배운 것은 내일 더 큰 힘이 돼요."], ADV = ["물을 자주 마시면 좋은 하루!", "일찍 자면 내일이 가뿐해요.", "준비물을 미리 챙기세요.", "친구에게 고맙다고 말해 보세요.", "가벼운 산책이 행운을 불러요."];
function hash(s) { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
function rng(seed) { let a = seed; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const stars = n => "★".repeat(n) + "☆".repeat(5 - n), ymd = () => { const t = new Date(); return new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 10); };
function show() { const b = $("bd").value; if (!b) { $("out").hidden = false; $("out").innerHTML = "<b>생일을 골라 주세요</b>"; return; } sv(KEY, b); const r = rng(hash(b + ymd())), pick = a => a[Math.floor(r() * a.length)], n = () => 1 + Math.floor(r() * 5);
  const total = Math.max(2, n()), money = n(), health = n(), study = n(); $("out").hidden = false;
  $("out").innerHTML = `<b>✨ 오늘의 운세 (${ymd()})</b><div class="fr"><span>종합</span><b>${stars(total)}</b></div><div class="fr"><span>금전</span><b>${stars(money)}</b></div><div class="fr"><span>건강</span><b>${stars(health)}</b></div><div class="fr"><span>공부</span><b>${stars(study)}</b></div><p class="muted" style="margin-top:8px">행운의 색 <span class="lk">${pick(COLORS)}</span> · 행운의 숫자 <span class="lk">${1 + Math.floor(r() * 45)}</span> · 행운의 물건 <span class="lk">${pick(ITEMS)}</span></p><p>💬 ${pick(WORDS)}</p><p class="muted">${pick(ADV)}</p>`; }
const saved = ld(KEY); if (saved) $("bd").value = saved; $("go").onclick = show; if (saved) show();''',
 css=".card input{margin:6px 0 12px}.lk{font-weight:700;color:var(--fg)}.fr{display:flex;justify-content:space-between;padding:6px 4px;border-bottom:1px solid var(--line)}.fr b{color:#e0a100;letter-spacing:.1em;font-weight:400}")
