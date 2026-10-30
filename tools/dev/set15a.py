import sys, json
sys.path.insert(0, ".")
from mkpage import make
H = "out/"

# ---------- 만 나이 계산기 ----------
make(H+"age-calc.html", "나이 계산기", "🎂", 330, "agecalc-v1",
 "생년월일을 고르면 <b>만 나이</b>, 태어난 지 며칠인지, <b>다음 생일까지 남은 날</b>, 띠와 별자리를 알려 줘요. 가족 생일을 모두 넣어서 비교해 볼 수도 있어요.",
 r'''  <div class="card"><label class="muted" for="bd">생년월일</label><input type="date" id="bd"><div class="row"><button class="btn" id="calc" type="button">계산하기</button><button class="btn ghost" id="save" type="button">가족에 추가</button></div></div>
  <div class="res" id="out" hidden></div>
  <div class="card"><b>👨‍👩‍👧 가족 목록</b><div id="fam"></div></div>''',
 r'''const ANIMALS = "쥐 소 호랑이 토끼 용 뱀 말 양 원숭이 닭 개 돼지".split(" "), DAYS = "일월화수목금토".split("");
const SIGNS = [[1, 20, "물병자리"], [2, 19, "물고기자리"], [3, 21, "양자리"], [4, 20, "황소자리"], [5, 21, "쌍둥이자리"], [6, 22, "게자리"], [7, 23, "사자자리"], [8, 23, "처녀자리"], [9, 24, "천칭자리"], [10, 24, "전갈자리"], [11, 23, "사수자리"], [12, 22, "염소자리"]];
let fam = ld(KEY) || [];
const sign = (m, d) => { let s = "염소자리"; for (const [mm, dd, n] of SIGNS) if (m > mm || (m === mm && d >= dd)) s = n; return s; };
function info(str) {
  const b = new Date(str + "T00:00:00"), t = new Date(); t.setHours(0, 0, 0, 0); if (isNaN(b) || b > t) return null;
  let age = t.getFullYear() - b.getFullYear(); if (t.getMonth() < b.getMonth() || (t.getMonth() === b.getMonth() && t.getDate() < b.getDate())) age--;
  let nx = new Date(t.getFullYear(), b.getMonth(), b.getDate()); if (nx < t) nx = new Date(t.getFullYear() + 1, b.getMonth(), b.getDate()); const days = Math.round((t - b) / 864e5), left = Math.round((nx - t) / 864e5);
  return { age, days, left, animal: ANIMALS[(b.getFullYear() - 4) % 12], sign: sign(b.getMonth() + 1, b.getDate()), dow: DAYS[b.getDay()], yearAge: t.getFullYear() - b.getFullYear() };
}
function show() { const v = $("bd").value, i = v && info(v); if (!i) { $("out").hidden = false; $("out").innerHTML = "<b>생년월일을 올바르게 골라 주세요</b>"; return; } $("out").hidden = false; $("out").innerHTML = `<b>만 ${i.age}세</b><p class="muted">연 나이 ${i.yearAge}세 · 태어난 지 ${i.days.toLocaleString()}일째<br>다음 생일까지 ${i.left === 0 ? "오늘이 생일! 🎉" : i.left + "일"} · ${i.animal}띠 · ${i.sign} · ${i.dow}요일 출생</p>`; }
function render() { $("fam").innerHTML = fam.length ? fam.map((f, k) => { const i = info(f.d); return i ? `<div class="fr"><input type="text" value="${esc(f.n)}" data-n="${k}" maxlength="8"><span>만 ${i.age}세 · 생일 ${i.left === 0 ? "오늘!" : "D-" + i.left}</span><button type="button" data-d="${k}" aria-label="삭제">✕</button></div>` : ""; }).join("") : '<p class="muted">저장된 가족이 없어요</p>'; }
$("calc").onclick = show; $("save").onclick = () => { const v = $("bd").value; if (!v || !info(v)) return show(); fam.push({ n: "가족" + (fam.length + 1), d: v }); sv(KEY, fam); render(); };
$("fam").addEventListener("input", e => { const k = e.target.dataset.n; if (k !== undefined) { fam[+k].n = e.target.value; sv(KEY, fam); } });
$("fam").addEventListener("click", e => { const d = e.target.closest("[data-d]"); if (d) { fam.splice(+d.dataset.d, 1); sv(KEY, fam); render(); } }); render();''',
 css=".fr{display:flex;align-items:center;gap:8px;margin-top:8px}.fr input{width:84px}.fr span{flex:1;font-size:.9rem;color:var(--muted)}.fr button{width:34px;height:34px;border-radius:50%;border:1px solid var(--line);background:var(--soft);padding:0}")

# ---------- D-day ----------
make(H+"dday-counter.html", "디데이 계산기", "📆", 15, "dday-v1",
 "시험, 소풍, 생일 같은 <b>기다리는 날</b>을 등록하면 D-day를 보여 줘요. 이미 지난 날은 <b>D+몇 일</b>로 알려 줘요. 아래에서 <b>두 날짜 사이가 며칠</b>인지도 계산할 수 있어요.",
 r'''  <div class="card"><b>➕ 날 등록</b><input type="text" id="t" placeholder="이름 (예: 소풍)" maxlength="14"><input type="date" id="d"><button class="btn" id="add" type="button">등록</button></div>
  <div class="card"><b>⏳ 내 디데이</b><div id="list"></div></div>
  <div class="card"><b>📏 두 날짜 사이</b><div class="row"><input type="date" id="a"><input type="date" id="b"></div><p class="center big" id="diff" style="font-size:1.6rem">-</p></div>''',
 r'''let items = ld(KEY) || [{ t: "새해", d: new Date().getFullYear() + 1 + "-01-01" }];
const today = () => { const t = new Date(); t.setHours(0, 0, 0, 0); return t; }, days = (d) => Math.round((new Date(d + "T00:00:00") - today()) / 864e5), lab = n => n === 0 ? "D-DAY 🎉" : n > 0 ? "D-" + n : "D+" + (-n);
function render() { items.sort((x, y) => Math.abs(days(x.d)) - Math.abs(days(y.d))); $("list").innerHTML = items.length ? items.map((it, k) => `<div class="dd"><div><b>${esc(it.t)}</b><br><small class="muted">${it.d}</small></div><span class="${days(it.d) < 0 ? "past" : ""}">${lab(days(it.d))}</span><button type="button" data-d="${k}" aria-label="삭제">✕</button></div>`).join("") : '<p class="muted">등록된 날이 없어요</p>'; calc(); }
function calc() { const a = $("a").value, b = $("b").value; $("diff").textContent = a && b ? Math.abs(Math.round((new Date(b) - new Date(a)) / 864e5)) + "일 차이" : "-"; }
$("add").onclick = () => { const t = $("t").value.trim(), d = $("d").value; if (!t || !d) return; items.push({ t, d }); sv(KEY, items); $("t").value = ""; render(); };
$("list").addEventListener("click", e => { const d = e.target.closest("[data-d]"); if (d) { items.splice(+d.dataset.d, 1); sv(KEY, items); render(); } }); $("a").oninput = $("b").oninput = calc; render();''',
 css=".card input{margin:4px 0}.dd{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--line)}.dd>div{flex:1}.dd span{font-family:var(--font-display);font-size:1.5rem;color:var(--accent)}.dd span.past{color:var(--muted)}.dd button{width:34px;height:34px;border-radius:50%;border:1px solid var(--line);background:var(--soft);padding:0}")

# ---------- 단위 변환 ----------
make(H+"unit-convert.html", "단위 변환기", "📐", 195, "unitconvert-v1",
 "길이, 무게, 넓이, 부피, 온도를 서로 바꿔 줘요. <b>숫자를 입력하면 모든 단위로 한꺼번에</b> 계산돼요. 집 넓이를 말할 때 쓰는 <b>평</b>과 ㎡도 바꿀 수 있어요.",
 r'''  <div class="chips" id="cats"></div>
  <div class="card"><label class="muted" for="v">바꿀 값</label><div class="row"><input type="number" id="v" inputmode="decimal" value="1"><select id="u"></select></div></div>
  <div class="card"><div id="out"></div></div>''',
 r'''const CAT = { "길이": { "mm": .001, "cm": .01, "m": 1, "km": 1000, "인치(in)": .0254, "피트(ft)": .3048, "야드(yd)": .9144, "마일(mi)": 1609.344, "자": .30303 },
  "무게": { "mg": 1e-6, "g": .001, "kg": 1, "톤(t)": 1000, "온스(oz)": .0283495, "파운드(lb)": .45359237, "근(600g)": .6, "돈(3.75g)": .00375 },
  "넓이": { "㎠": 1e-4, "㎡": 1, "평": 3.305785, "ha(헥타르)": 1e4, "㎢": 1e6, "에이커": 4046.856 },
  "부피": { "mL": .001, "L": 1, "㎥": 1000, "컵(200mL)": .2, "큰술(15mL)": .015, "작은술(5mL)": .005, "갤런(US)": 3.785412, "되(1.8L)": 1.8, "말(18L)": 18 },
  "온도": null };
let cat = "길이", base = ld(KEY) || {};
function chips() { $("cats").innerHTML = Object.keys(CAT).map(c => `<button type="button" class="chip${c === cat ? " on" : ""}" data-c="${c}">${c}</button>`).join(""); const us = cat === "온도" ? ["섭씨(℃)", "화씨(℉)", "켈빈(K)"] : Object.keys(CAT[cat]); $("u").innerHTML = us.map(u => `<option>${u}</option>`).join(""); }
const fmt = n => { if (!isFinite(n)) return "-"; const a = Math.abs(n); return (a !== 0 && (a < 1e-4 || a >= 1e9) ? n.toExponential(4) : +n.toPrecision(7)).toLocaleString("ko-KR", { maximumFractionDigits: 8 }); };
function calc() {
  const v = parseFloat($("v").value), u = $("u").value; if (isNaN(v)) { $("out").innerHTML = '<p class="muted">숫자를 입력해 주세요</p>'; return; }
  let rows; if (cat === "온도") { const c = u.startsWith("섭씨") ? v : u.startsWith("화씨") ? (v - 32) * 5 / 9 : v - 273.15; rows = [["섭씨(℃)", c], ["화씨(℉)", c * 9 / 5 + 32], ["켈빈(K)", c + 273.15]]; } else { const m = v * CAT[cat][u]; rows = Object.entries(CAT[cat]).map(([k, f]) => [k, m / f]); }
  $("out").innerHTML = rows.map(([k, x]) => `<div class="ur${k === u ? " me" : ""}"><span>${k}</span><b>${fmt(x)}</b></div>`).join("");
}
$("cats").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b) { cat = b.dataset.c; chips(); calc(); } }); $("v").oninput = $("u").onchange = calc; chips(); calc();''',
 css=".chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.95rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}.row{grid-template-columns:1fr 1fr}select{width:100%;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:11px 12px;font:inherit}.ur{display:flex;justify-content:space-between;padding:7px 4px;border-bottom:1px solid var(--line)}.ur.me{background:var(--soft);border-radius:8px}.ur b{font-weight:700;font-variant-numeric:tabular-nums}")

# ---------- BMI ----------
make(H+"bmi-calc.html", "BMI 계산기", "⚖️", 140, "bmi-v1",
 "<b>키와 몸무게</b>를 넣으면 체질량지수(BMI)와 비만도를 알려 줘요. 한국 기준(저체중 18.5 미만, 정상 18.5~22.9, 과체중 23~24.9, 비만 25 이상)을 써요. 성장기 어린이는 나이에 따라 기준이 달라서, 참고만 해 주세요.",
 r'''  <div class="card"><label class="muted">키 (cm)</label><input type="number" id="h" inputmode="decimal" placeholder="예: 170"><label class="muted">몸무게 (kg)</label><input type="number" id="w" inputmode="decimal" placeholder="예: 65"><button class="btn" id="go" type="button">계산하기</button></div>
  <div class="res" id="out" hidden></div>''',
 r'''const last = ld(KEY); if (last) { $("h").value = last[0]; $("w").value = last[1]; }
function calc() { const h = parseFloat($("h").value), w = parseFloat($("w").value); if (!(h > 50 && h < 250 && w > 5 && w < 300)) { $("out").hidden = false; $("out").innerHTML = "<b>키와 몸무게를 올바르게 넣어 주세요</b>"; return; } sv(KEY, [h, w]);
  const m = h / 100, bmi = w / (m * m), lo = 18.5 * m * m, hi = 22.9 * m * m; const cat = bmi < 18.5 ? ["저체중", "#2f6fdf"] : bmi < 23 ? ["정상", "#1f9d62"] : bmi < 25 ? ["과체중", "#d9a400"] : ["비만", "#d6453a"];
  const pos = Math.max(0, Math.min(100, (bmi - 14) / (34 - 14) * 100)); $("out").hidden = false;
  $("out").innerHTML = `<b style="color:${cat[1]}">BMI ${bmi.toFixed(1)} · ${cat[0]}</b><div class="gauge"><i style="left:${pos}%"></i></div><div class="gl"><span>저체중</span><span>정상</span><span>과체중</span><span>비만</span></div><p class="muted">정상 체중 범위: ${lo.toFixed(1)}kg ~ ${hi.toFixed(1)}kg</p>`; }
$("go").onclick = calc; if (last) calc();''',
 css=".card input{margin:4px 0 10px}.gauge{position:relative;height:14px;border-radius:7px;margin:14px 0 4px;background:linear-gradient(90deg,#2f6fdf 0 22.5%,#1f9d62 22.5% 44.5%,#d9a400 44.5% 55%,#d6453a 55%)}.gauge i{position:absolute;top:-5px;width:6px;height:24px;margin-left:-3px;background:var(--fg);border-radius:3px}.gl{display:flex;justify-content:space-between;font-size:.75rem;color:var(--muted)}")

# ---------- 할인 계산기 ----------
make(H+"discount-calc.html", "할인 계산기", "🏷️", 48, "discount-v1",
 "물건의 <b>원래 가격과 할인율</b>을 넣으면 얼마에 살 수 있는지 계산해 줘요. 쿠폰으로 <b>한 번 더 할인</b>을 받는 경우, 여러 개를 사는 경우도 계산돼요.",
 r'''  <div class="card"><label class="muted">원래 가격 (원)</label><input type="number" id="p" inputmode="numeric" placeholder="예: 30000"><label class="muted">할인율 (%)</label><input type="number" id="d1" inputmode="decimal" placeholder="예: 20"><label class="muted">추가 할인율 (%) — 쿠폰 등</label><input type="number" id="d2" inputmode="decimal" placeholder="없으면 비워 두세요"><label class="muted">개수</label><input type="number" id="n" inputmode="numeric" value="1" min="1"></div>
  <div class="res" id="out"></div>''',
 r'''const won = n => Math.round(n).toLocaleString("ko-KR") + "원";
function calc() { const p = parseFloat($("p").value), d1 = parseFloat($("d1").value) || 0, d2 = parseFloat($("d2").value) || 0, n = Math.max(1, parseInt($("n").value) || 1);
  if (!(p > 0)) { $("out").innerHTML = '<p class="muted">가격을 입력해 주세요</p>'; return; }
  const a = p * (1 - d1 / 100), f = a * (1 - d2 / 100), total = f * n, saved = (p - f) * n, eff = (1 - f / p) * 100;
  $("out").innerHTML = `<b>${won(f)}</b><p class="muted">1개 가격 · 원래 ${won(p)}${d2 ? ` → 1차 할인 후 ${won(a)}` : ""}</p><div class="kv"><span>개수 ${n}개 합계</span><b>${won(total)}</b></div><div class="kv"><span>아낀 돈</span><b style="color:var(--ok)">${won(saved)}</b></div><div class="kv"><span>실제 총 할인율</span><b>${eff.toFixed(1)}%</b></div>${d2 ? `<p class="muted">💡 ${d1}%와 ${d2}%를 더한 ${d1 + d2}%가 아니라 <b>${eff.toFixed(1)}%</b>예요 (할인 위에 또 할인)</p>` : ""}`; }
["p", "d1", "d2", "n"].forEach(k => { $(k).oninput = calc; }); calc();''',
 css=".card input{margin:4px 0 10px}.kv{display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid var(--line);margin-top:6px}.kv b{font-family:var(--font-body);font-weight:700;font-size:1.05rem}")

# ---------- 점수판 ----------
make(H+"scoreboard.html", "가족 점수판", "📊", 270, "scoreboard-v1",
 "보드게임, 윷놀이, 퀴즈 대회… <b>모든 놀이의 점수</b>를 여기에 적어요. 이름을 고치고 +1, +5, -1 버튼으로 점수를 바꾸면 <b>1등이 자동으로 표시</b>돼요. 닫아도 점수가 저장돼요.",
 r'''  <div class="card"><div id="board"></div><div class="row"><button class="btn ghost" id="add" type="button">+ 사람 추가</button><button class="btn ghost" id="reset" type="button">점수만 0으로</button></div></div>
  <div class="card"><b>📝 기록</b><div id="log" class="muted"></div></div>''',
 r'''let st = ld(KEY) || { p: [{ n: "아빠", s: 0 }, { n: "엄마", s: 0 }, { n: "나", s: 0 }, { n: "동생", s: 0 }], log: [] };
const save = () => sv(KEY, st);
function render() { const mx = Math.max(...st.p.map(x => x.s)); $("board").innerHTML = st.p.map((x, k) => `<div class="sr${x.s === mx && mx > 0 ? " top" : ""}"><span class="rk">${x.s === mx && mx > 0 ? "👑" : ""}</span><input type="text" value="${esc(x.n)}" data-n="${k}" maxlength="8"><button data-k="${k}" data-v="-1" type="button">−1</button><b>${x.s}</b><button data-k="${k}" data-v="1" type="button">+1</button><button data-k="${k}" data-v="5" type="button">+5</button></div>`).join(""); $("log").innerHTML = st.log.slice(-8).reverse().map(l => `<div>${esc(l)}</div>`).join("") || "아직 기록이 없어요"; }
$("board").addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (!b) return; const p = st.p[+b.dataset.k], v = +b.dataset.v; p.s += v; st.log.push(`${p.n} ${v > 0 ? "+" : ""}${v} → ${p.s}점`); st.log = st.log.slice(-40); save(); render(); });
$("board").addEventListener("input", e => { const k = e.target.dataset.n; if (k !== undefined) { st.p[+k].n = e.target.value; save(); } });
$("add").onclick = () => { if (st.p.length < 10) { st.p.push({ n: "참가자" + (st.p.length + 1), s: 0 }); save(); render(); } }; $("reset").onclick = () => { st.p.forEach(x => { x.s = 0; }); st.log = []; save(); render(); }; render();''',
 css=".sr{display:flex;align-items:center;gap:6px;padding:6px 0}.sr .rk{width:22px;text-align:center}.sr input{flex:1;min-width:0;padding:8px 10px}.sr button{min-width:38px;height:38px;border-radius:10px;border:1px solid var(--line);background:var(--soft);font-weight:700;padding:0 4px}.sr b{min-width:2.4ch;text-align:center;font-family:var(--font-display);font-weight:400;font-size:1.5rem}.sr.top b{color:var(--accent)}")
