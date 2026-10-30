import sys
sys.path.insert(0, ".")
from mkpage import make
lunar = open("data/lunar_data.js").read() + open("data/lunar_funcs.js").read()
jq = open("data/jq24.js").read()
BODY = '''  <div class="seg" id="tabs" style="--n:5"><button type="button" data-t="today" class="on">오늘</button><button type="button" data-t="conv">음양력</button><button type="button" data-t="term">24절기</button><button type="button" data-t="sijin">시진</button><button type="button" data-t="calc">날짜</button></div>
  <section id="p-today" class="pane"></section>
  <section id="p-conv" class="pane" hidden>
    <div class="card"><div class="seg" id="cmode" style="--n:2"><button type="button" data-m="s" class="on">양력 → 음력</button><button type="button" data-m="l">음력 → 양력</button></div>
      <div id="cs"><label class="muted" for="cd">양력 날짜</label><input type="date" id="cd"></div>
      <div id="cl" hidden><label class="muted">음력 날짜</label><div class="cr"><input type="number" id="ly" min="1901" max="2049" placeholder="년" style="width:96px"><select id="lm"></select><select id="ld"></select><label class="muted lp"><input type="checkbox" id="lp"> 윤달</label></div></div>
      <button class="btn" id="cgo" type="button">변환하기</button></div>
    <div class="res" id="cout" hidden></div>
    <div class="card"><div class="step"><b>🎎 음력 명절 (양력 날짜)</b><div><button type="button" id="hy-" aria-label="이전 해">‹</button><b id="hy">2026</b><button type="button" id="hy+" aria-label="다음 해">›</button></div></div><div id="hol"></div></div>
  </section>
  <section id="p-term" class="pane" hidden><div class="card"><div class="step"><b>🌾 24절기</b><div><button type="button" id="ty-" aria-label="이전 해">‹</button><b id="ty">2026</b><button type="button" id="ty+" aria-label="다음 해">›</button></div></div><p class="muted">한국 표준시 기준이에요. 음력 날짜도 함께 보여 줘요.</p><div id="tl"></div></div></section>
  <section id="p-sijin" class="pane" hidden>
    <div class="card"><label class="muted" for="tt">시각 → 시진 알아보기</label><input type="time" id="tt"><div id="tr" class="muted"></div></div>
    <div class="card"><b>🕰 12시진 (자시~해시)</b><div id="sl"></div></div></section>
  <section id="p-calc" class="pane" hidden>
    <div class="card"><b>📅 D-day · 날짜 사이 일수</b><label class="muted" for="d1">기준 날짜</label><input type="date" id="d1"><label class="muted" for="d2">비교 날짜</label><input type="date" id="d2"><div id="dr" class="muted"></div></div>
    <div class="card"><b>➕ 며칠 뒤·전 날짜</b><label class="muted" for="d3">기준 날짜</label><input type="date" id="d3"><label class="muted" for="dn">일수 (뒤는 +, 전은 −)</label><input type="number" id="dn" value="100"><div id="dr2" class="muted"></div></div>
  </section>'''
CSS = '''.pane{display:flex;flex-direction:column;gap:12px}.pane[hidden]{display:none}.cr{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:6px 0}.cr select,.cr input,input[type=time]{background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:inherit}input[type=date],input[type=time]{margin:6px 0 10px}.lp{display:flex;align-items:center;gap:6px}.lp input{width:auto;margin:0}.kv{display:flex;justify-content:space-between;gap:10px;padding:7px 2px;border-bottom:1px solid var(--line)}.kv:last-child{border:0}.kv span:first-child{color:var(--muted);flex:none}.kv b{text-align:right;font-weight:700}.row2{padding:8px 4px;border-bottom:1px solid var(--line)}.row2:last-child{border:0}.row2 .h{display:flex;justify-content:space-between;gap:8px;font-weight:700}.row2 .s{color:var(--muted);font-size:.86rem}.row2.now{background:var(--soft);border-radius:10px;border-bottom-color:transparent}.big2{font-family:var(--font-display);font-size:1.6rem;line-height:1.3}.tag{display:inline-block;background:var(--soft);border-radius:999px;padding:2px 10px;font-size:.82rem;font-weight:700;margin-left:6px}'''
JS = lunar + jq + r'''
const STEM = "갑을병정무기경신임계", BRANCH = "자축인묘진사오미신유술해", SH = "甲乙丙丁戊己庚辛壬癸", BH = "子丑寅卯辰巳午未申酉戌亥", ANI = "쥐소호랑이토끼용뱀말양원숭이닭개돼지".match(/호랑이|원숭이|돼지|쥐|소|토끼|용|뱀|말|양|닭|개/g), WD = "일월화수목금토";
const TERMS = [["소한", "작은 추위, 겨울 추위가 본격적으로 시작돼요"], ["대한", "큰 추위, 한 해 중 가장 추운 때예요"], ["입춘", "봄이 시작되는 때예요"], ["우수", "눈이 녹아 비가 되는 때예요"], ["경칩", "겨울잠 자던 개구리가 깨어나요"], ["춘분", "낮과 밤의 길이가 같아져요"], ["청명", "하늘이 맑고 따뜻해 농사 준비를 해요"], ["곡우", "봄비가 내려 곡식을 키워 줘요"], ["입하", "여름이 시작되는 때예요"], ["소만", "만물이 점차 자라 가득 차기 시작해요"], ["망종", "보리를 거두고 모를 심기 좋은 때예요"], ["하지", "낮이 가장 긴 날이에요"], ["소서", "작은 더위, 장마가 시작돼요"], ["대서", "큰 더위, 가장 더운 때예요"], ["입추", "가을이 시작되는 때예요"], ["처서", "더위가 물러가는 때예요"], ["백로", "풀잎에 흰 이슬이 맺혀요"], ["추분", "낮과 밤의 길이가 같아져요"], ["한로", "찬 이슬이 맺혀 쌀쌀해져요"], ["상강", "서리가 내리기 시작해요"], ["입동", "겨울이 시작되는 때예요"], ["소설", "첫눈이 내리는 때예요"], ["대설", "눈이 많이 내리는 때예요"], ["동지", "밤이 가장 긴 날이에요. 팥죽을 먹어요"]];
const SIJIN = [["자시", "子", "쥐", "23:30~01:30", "야반(夜半)", "하루가 시작되는 한밤중"], ["축시", "丑", "소", "01:30~03:30", "계명(鷄鳴)", "닭이 울기 시작하는 때"], ["인시", "寅", "호랑이", "03:30~05:30", "평단(平旦)", "새벽, 동이 트는 때"], ["묘시", "卯", "토끼", "05:30~07:30", "일출(日出)", "해가 뜨는 때"], ["진시", "辰", "용", "07:30~09:30", "식시(食時)", "아침밥을 먹는 때"], ["사시", "巳", "뱀", "09:30~11:30", "우중(隅中)", "해가 높이 오르는 오전"], ["오시", "午", "말", "11:30~13:30", "일중(日中)", "해가 하늘 한가운데 있는 한낮"], ["미시", "未", "양", "13:30~15:30", "일질(日昳)", "해가 기울기 시작하는 때"], ["신시", "申", "원숭이", "15:30~17:30", "포시(晡時)", "저녁밥을 먹는 때"], ["유시", "酉", "닭", "17:30~19:30", "일입(日入)", "해가 지는 때"], ["술시", "戌", "개", "19:30~21:30", "황혼(黃昏)", "어두워지는 저녁"], ["해시", "亥", "돼지", "21:30~23:30", "인정(人定)", "사람들이 잠자리에 드는 때"]];
const p2 = n => String(n).padStart(2, "0"), dnum = (y, m, d) => Math.round(Date.UTC(y, m - 1, d) / 864e5), wd = (y, m, d) => WD[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
const dayIdx = (y, m, d) => ((dnum(y, m, d) - dnum(1900, 1, 1) + 10) % 60 + 60) % 60, gzTxt = i => STEM[i % 10] + BRANCH[i % 12] + "(" + SH[i % 10] + BH[i % 12] + ")";
const termDate = (y, k) => { const t = new Date(Date.UTC(y, 0, 1) + JQ[y - 1925][k] * 6e4); return { y: t.getUTCFullYear(), m: t.getUTCMonth() + 1, d: t.getUTCDate(), hh: t.getUTCHours(), mm: t.getUTCMinutes() }; };
const fmtT = t => `${t.m}월 ${t.d}일(${wd(t.y, t.m, t.d)}) ${p2(t.hh)}:${p2(t.mm)}`;
const lunTxt = l => l ? `음력 ${l.y}년 ${l.leap ? "윤" : ""}${l.m}월 ${l.d}일` : "(음력 범위 밖)", lunShort = l => l ? `${l.leap ? "윤" : ""}${l.m}.${l.d}` : "-";
function yearGz(y, m, d, hh) { if (y < 1926 || y > 2076) return null; const t = Date.UTC(y, m - 1, d, hh), ip = Date.UTC(y, 0, 1) + JQ[y - 1925][2] * 6e4, ys = t < ip ? y - 1 : y; return ((ys - 4) % 60 + 60) % 60; }
function monthGz(y, m, d, hh) { if (y < 1926 || y > 2076) return null; const t = Date.UTC(y, m - 1, d, hh), ys = yearGz(y, m, d, hh) % 10; let k = 0, best = Date.UTC(y - 1, 11, 31) - 1e12; for (let j = 0; j < 24; j += 2) { const tt = Date.UTC(y, 0, 1) + JQ[y - 1925][j] * 6e4; if (tt <= t) { k = j; best = tt; } } const br = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0][k / 2]; if (best < Date.UTC(y - 1, 11, 31) - 1e11) { const tt = Date.UTC(y - 1, 0, 1) + JQ[y - 1 - 1925][22] * 6e4; k = 22; } const off = ((k === 22 && Date.UTC(y, m - 1, d, hh) < Date.UTC(y, 0, 1) + JQ[y - 1925][0] * 6e4 ? 0 : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0][k / 2]) - 2 + 12) % 12, ysT = (yearGz(y, m, d, hh)) % 10; return ((ysT % 5) * 2 + 2 + off) % 10 + 0 * ys + 10 * 0, ((((ysT % 5) * 2 + 2 + off) % 10) * 6 + 0, 0); }
'''
JS += r'''
function pillars(y, m, d, hh) {
  if (y < 1926 || y > 2076) return null; const t = Date.UTC(y, m - 1, d, hh), y0 = yy => Date.UTC(yy, 0, 1), ip = y0(y) + JQ[y - 1925][2] * 6e4, ys = t < ip ? y - 1 : y, ystem = ((ys - 4) % 10 + 10) % 10, ybr = ((ys - 4) % 12 + 12) % 12;
  const list = [[y - 1, 22], ...[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22].map(k => [y, k])].map(([yy, k]) => ({ k, t: y0(yy) + JQ[yy - 1925][k] * 6e4 })); let cur = list[0]; for (const x of list) if (x.t <= t) cur = x;
  const BR = { 0: 1, 2: 2, 4: 3, 6: 4, 8: 5, 10: 6, 12: 7, 14: 8, 16: 9, 18: 10, 20: 11, 22: 0 }, mbr = BR[cur.k], off = (mbr - 2 + 12) % 12, mstem = ((ystem % 5) * 2 + 2 + off) % 10;
  return { y: ystem + "," + ybr, ys: ystem, yb: ybr, ms: mstem, mb: mbr };
}
const pTxt = (s, b) => STEM[s] + BRANCH[b] + "(" + SH[s] + BH[b] + ")";
const $$ = s => [...document.querySelectorAll(s)], kv = (a, b) => `<div class="kv"><span>${a}</span><b>${b}</b></div>`;
function sijinOf(h, m) { const x = (h * 60 + m + 30) % 1440; return Math.floor(x / 120); }
function termNow(now) { const y = now.y, tN = Date.UTC(y, now.m - 1, now.d, now.hh, now.mm); let list = []; for (const yy of [y - 1, y, y + 1]) if (yy >= 1925 && yy <= 2077) for (let k = 0; k < 24; k++) list.push({ y: yy, k, t: Date.UTC(yy, 0, 1) + JQ[yy - 1925][k] * 6e4 }); let cur = null, nxt = null; for (const x of list) { if (x.t <= tN) cur = x; else { nxt = x; break; } } return { cur, nxt, tN }; }
const clock = () => { const n = new Date(); return { y: n.getFullYear(), m: n.getMonth() + 1, d: n.getDate(), hh: n.getHours(), mm: n.getMinutes(), ss: n.getSeconds() }; };
function renderToday() {
  const n = clock(), l = n.y >= 1901 && n.y <= 2049 ? toLunar(n.y, n.m, n.d) : null, pl = pillars(n.y, n.m, n.d, n.hh), di = dayIdx(n.y, n.m, n.d), si = sijinOf(n.hh, n.mm), tn = termNow(n);
  const sinfo = SIJIN[si], nx = tn.nxt ? termDate(tn.nxt.y, tn.nxt.k) : null, dd = nx ? dnum(nx.y, nx.m, nx.d) - dnum(n.y, n.m, n.d) : 0;
  let zones = ""; try { zones = [["서울", "Asia/Seoul"], ["도쿄", "Asia/Tokyo"], ["베이징", "Asia/Shanghai"], ["런던", "Europe/London"], ["뉴욕", "America/New_York"], ["로스앤젤레스", "America/Los_Angeles"]].map(([c, z]) => kv(c, new Intl.DateTimeFormat("ko-KR", { timeZone: z, month: "numeric", day: "numeric", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date()))).join(""); } catch (e) { zones = '<p class="muted">이 폰에서는 세계 시각을 볼 수 없어요.</p>'; }
  $("p-today").innerHTML = `<div class="card"><div class="big2">${n.y}년 ${n.m}월 ${n.d}일 (${wd(n.y, n.m, n.d)})</div><div class="big2" style="font-size:1.25rem;color:var(--accent)">${lunTxt(l)}</div>`
    + kv("지금 시각", `${p2(n.hh)}:${p2(n.mm)}:${p2(n.ss)}`) + kv("지금 시진", `${sinfo[0]} (${sinfo[1]}) · ${sinfo[2]}띠 시간`) + kv("일진(날의 간지)", gzTxt(di))
    + (pl ? kv("연·월 간지", `${pTxt(pl.ys, pl.yb)}년 ${pTxt(pl.ms, pl.mb)}월`) + kv("올해의 띠", ANI[pl.yb] + "띠") : "")
    + (tn.cur ? kv("지금 절기", `${TERMS[tn.cur.k][0]} (${termDate(tn.cur.y, tn.cur.k).m}월 ${termDate(tn.cur.y, tn.cur.k).d}일 시작)`) : "") + (nx ? kv("다음 절기", `${TERMS[tn.nxt.k][0]} · ${nx.m}월 ${nx.d}일 (D-${dd})`) : "") + `</div>`
    + (tn.cur ? `<div class="card"><b>🌾 ${TERMS[tn.cur.k][0]}</b><p class="muted">${TERMS[tn.cur.k][1]}.</p></div>` : "") + `<div class="card"><b>🌏 세계 시각</b>${zones}</div>`;
}
function convert() {
  const mode = $("cmode").querySelector(".on").dataset.m; let s, l, err = "";
  if (mode === "s") { const v = $("cd").value; if (!v) { err = "양력 날짜를 골라 주세요"; } else { const [y, m, d] = v.split("-").map(Number); if (y < 1901 || y > 2049) err = "1901~2049년만 변환할 수 있어요"; else { s = { y, m, d }; l = toLunar(y, m, d); } } }
  else { const y = +$("ly").value, m = +$("lm").value, d = +$("ld").value, lp = $("lp").checked; if (!y) err = "음력 년도를 입력해 주세요"; else { s = toSolar(y, m, d, lp); if (!s) err = `음력 ${y}년 ${lp ? "윤" : ""}${m}월 ${d}일은 없는 날짜예요 (1901~2049년, 윤달·그믐 날짜를 확인해 주세요)`; else l = { y, m, d, leap: lp }; } }
  const o = $("cout"); o.hidden = false; if (err) { o.innerHTML = `<b>${esc(err)}</b>`; return; }
  const di = dayIdx(s.y, s.m, s.d), pl = pillars(s.y, s.m, s.d, 12);
  o.innerHTML = `<b>변환 결과</b><div style="text-align:left;margin-top:8px">` + kv("양력", `${s.y}년 ${s.m}월 ${s.d}일 (${wd(s.y, s.m, s.d)})`) + kv("음력", lunTxt(l).replace("음력 ", "")) + kv("일진", gzTxt(di)) + (pl ? kv("연·월 간지", `${pTxt(pl.ys, pl.yb)}년 ${pTxt(pl.ms, pl.mb)}월`) + kv("띠", ANI[pl.yb] + "띠") : "") + `</div>`;
}
const HOL = [["설날", 1, 1], ["정월 대보름", 1, 15], ["한식", 0, 0], ["부처님오신날", 4, 8], ["단오", 5, 5], ["칠석", 7, 7], ["백중", 7, 15], ["추석", 8, 15], ["중양절", 9, 9], ["동지(24절기)", -1, 0]];
function renderHol() {
  const y = +$("hy").textContent; let h = "";
  for (const [nm, m, d] of HOL) {
    if (m === 0) { const t = termDate(y - 1, 23); const dt = new Date(Date.UTC(t.y, t.m - 1, t.d) + 105 * 864e5); h += `<div class="row2"><div class="h"><span>🌿 한식</span><span>${dt.getUTCMonth() + 1}월 ${dt.getUTCDate()}일 (${WD[dt.getUTCDay()]})</span></div><div class="s">전년 동지부터 105일째 되는 날</div></div>`; continue; }
    if (m === -1) { const t = termDate(y, 23); h += `<div class="row2"><div class="h"><span>🥣 동지</span><span>${t.m}월 ${t.d}일 (${wd(t.y, t.m, t.d)})</span></div><div class="s">24절기 · 양력 기준 절기</div></div>`; continue; }
    const s = toSolar(y, m, d, false); h += s ? `<div class="row2"><div class="h"><span>${nm}</span><span>${s.m}월 ${s.d}일 (${wd(s.y, s.m, s.d)})</span></div><div class="s">음력 ${m}월 ${d}일</div></div>` : "";
  }
  $("hol").innerHTML = h || '<p class="muted">1901~2049년만 볼 수 있어요.</p>';
}
function renderTerms() {
  const y = +$("ty").textContent, n = clock(); let h = "";
  for (let k = 0; k < 24; k++) { const t = termDate(y, k), l = y >= 1901 && y <= 2049 ? toLunar(t.y, t.m, t.d) : null, nowIs = n.y === y && t.m === n.m && t.d === n.d; h += `<div class="row2${nowIs ? " now" : ""}"><div class="h"><span>${TERMS[k][0]}${k % 2 === 0 ? '<span class="tag">절(節)</span>' : '<span class="tag">중기</span>'}</span><span>${fmtT(t)}</span></div><div class="s">${lunShort(l) !== "-" ? "음력 " + lunShort(l) + " · " : ""}${TERMS[k][1]}</div></div>`; }
  $("tl").innerHTML = y >= 1926 && y <= 2076 ? h : '<p class="muted">1926~2076년만 볼 수 있어요.</p>';
}
function renderSijin() {
  const n = clock(), si = sijinOf(n.hh, n.mm);
  $("sl").innerHTML = SIJIN.map((s, i) => `<div class="row2${i === si ? " now" : ""}"><div class="h"><span>${s[0]} ${s[1]} · ${s[2]}${i === si ? '<span class="tag">지금</span>' : ""}</span><span>${s[3]}</span></div><div class="s">${s[4]} · ${s[5]}</div></div>`).join("");
}
function renderTime() { const v = $("tt").value; if (!v) { $("tr").textContent = ""; return; } const [h, m] = v.split(":").map(Number), s = SIJIN[sijinOf(h, m)]; $("tr").innerHTML = `${p2(h)}:${p2(m)}은 <b style="color:var(--fg)">${s[0]} (${s[1]}시)</b> · ${s[2]}띠 시간이에요. (${s[3]}, ${s[4]})`; }
function renderCalc() {
  const a = $("d1").value, b = $("d2").value; if (a && b) { const [y1, m1, d1] = a.split("-").map(Number), [y2, m2, d2] = b.split("-").map(Number), n = dnum(y2, m2, d2) - dnum(y1, m1, d1); $("dr").innerHTML = `<b style="color:var(--fg)">${n === 0 ? "같은 날이에요" : Math.abs(n) + "일 " + (n > 0 ? "뒤 (D-" + n + ")" : "전 (D+" + Math.abs(n) + ")")}</b><br>약 ${Math.floor(Math.abs(n) / 7)}주 ${Math.abs(n) % 7}일 · ${wd(y1, m1, d1)}요일 → ${wd(y2, m2, d2)}요일`; } else $("dr").textContent = "두 날짜를 모두 골라 주세요.";
  const c = $("d3").value, k = +$("dn").value; if (c && !isNaN(k)) { const [y, m, d] = c.split("-").map(Number), t = new Date(Date.UTC(y, m - 1, d) + k * 864e5), l = t.getUTCFullYear() >= 1901 && t.getUTCFullYear() <= 2049 ? toLunar(t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate()) : null; $("dr2").innerHTML = `<b style="color:var(--fg)">${t.getUTCFullYear()}년 ${t.getUTCMonth() + 1}월 ${t.getUTCDate()}일 (${WD[t.getUTCDay()]})</b>${l ? "<br>" + lunTxt(l) : ""}`; } else $("dr2").textContent = "";
}
$("tabs").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (!b) return; $$("#tabs button").forEach(x => x.classList.toggle("on", x === b)); $$(".pane").forEach(p => p.hidden = p.id !== "p-" + b.dataset.t); sv(KEY, b.dataset.t); if (b.dataset.t === "today") renderToday(); if (b.dataset.t === "sijin") renderSijin(); });
$("cmode").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (!b) return; $$("#cmode button").forEach(x => x.classList.toggle("on", x === b)); $("cs").hidden = b.dataset.m !== "s"; $("cl").hidden = b.dataset.m !== "l"; });
$("lm").innerHTML = Array.from({ length: 12 }, (_, i) => `<option value="${i + 1}">${i + 1}월</option>`).join(""); $("ld").innerHTML = Array.from({ length: 30 }, (_, i) => `<option value="${i + 1}">${i + 1}일</option>`).join("");
const nowY = clock().y; $("hy").textContent = Math.min(2049, Math.max(1901, nowY)); $("ty").textContent = Math.min(2076, Math.max(1926, nowY));
$("hy-").onclick = () => { $("hy").textContent = Math.max(1901, +$("hy").textContent - 1); renderHol(); }; $("hy+").onclick = () => { $("hy").textContent = Math.min(2049, +$("hy").textContent + 1); renderHol(); };
$("ty-").onclick = () => { $("ty").textContent = Math.max(1926, +$("ty").textContent - 1); renderTerms(); }; $("ty+").onclick = () => { $("ty").textContent = Math.min(2076, +$("ty").textContent + 1); renderTerms(); };
$("cgo").onclick = convert; $("tt").oninput = renderTime; ["d1", "d2", "d3", "dn"].forEach(i => $(i).oninput = renderCalc);
{ const n = clock(), iso = `${n.y}-${p2(n.m)}-${p2(n.d)}`; $("cd").value = iso; $("d1").value = iso; $("d3").value = iso; $("tt").value = `${p2(n.hh)}:${p2(n.mm)}`; $("ly").value = n.y; }
renderToday(); renderHol(); renderTerms(); renderSijin(); renderTime(); renderCalc(); setInterval(() => { if (!$("p-today").hidden) renderToday(); }, 1000);
const lt = ld(KEY); if (lt && lt !== "today") { const b = document.querySelector(`#tabs [data-t="${lt}"]`); if (b) b.click(); }
'''
# remove the junk monthGz / yearGz helper (unused) to keep code clean
import re
i = JS.index("function yearGz"); j = JS.index("function pillars")
JS = JS[:i] + JS[j:]
make("out/calendar-tools.html", "음양력·시간 도구", "🗓️", 200, "calendar-tools-v1",
     "양력과 음력을 서로 바꾸고, 24절기와 12시진(자시~해시), 날짜 계산을 한곳에서 볼 수 있어요. 한국 표준시 기준이며 음력은 1901~2049년, 절기는 1926~2076년을 지원해요.",
     BODY, JS, CSS)
