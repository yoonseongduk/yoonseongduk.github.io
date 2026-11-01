import sys
sys.path.insert(0, ".")
from mkpage import make

CSS0 = '''select,input[type=date],input[type=time]{width:100%;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:inherit;min-width:0}
.f{display:grid;gap:4px}.f>label,.lb{font-size:.88rem;color:var(--muted);font-weight:700}.g2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}.g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.li{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}.li:last-child{border-bottom:0}.x{background:none;border:0;color:var(--muted);font-size:1.15rem;padding:4px 8px}
.tag{display:inline-block;border-radius:999px;padding:2px 10px;font-size:.82rem;font-weight:700;background:var(--soft)}.tag.ok{background:color-mix(in srgb,var(--ok) 22%,var(--surface))}.tag.bad{background:color-mix(in srgb,var(--bad) 22%,var(--surface))}.tag.wn{background:color-mix(in srgb,#e0a100 25%,var(--surface))}
.btn.sm{padding:7px 14px;font-size:.95rem}.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-weight:700;font-size:.92rem}.chip.on{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.num{font-family:var(--font-display);font-size:1.9rem;color:var(--accent);line-height:1.2}.note{font-size:.85rem;color:var(--muted)}'''
COM = r'''
const pad = n => String(n).padStart(2, "0");
const ymd = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const todayS = () => ymd(new Date());
const dnum = s => { const [y, m, d] = s.split("-").map(Number); return Math.round(Date.UTC(y, m - 1, d) / 86400000); };
const addDays = (s, n) => { const [y, m, d] = s.split("-").map(Number); return ymd(new Date(y, m - 1, d + n)); };
const WD = ["일", "월", "화", "수", "목", "금", "토"];
const wdOf = s => WD[new Date(s + "T00:00:00").getDay()];
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
'''
def mk(fn, title, emoji, hue, key, help_, body, js, css=""):
    make("out/" + fn, title, emoji, hue, key, help_, body, COM + js, CSS0 + css)

# ───────── 1. 기초대사량·하루 칼로리
mk("bmr-calc.html", "대사량·칼로리 계산기", "🔥", 15, "bmr-calc-v1",
 "기초대사량(가만히 있어도 쓰는 열량)과 하루에 필요한 칼로리를 추정해요. 몸 상태와 질환에 따라 달라서 참고용이에요. 입력값은 이 폰에만 저장돼요.",
 '''  <div class="card"><div class="seg" id="sex" style="--n:2"><button type="button" data-v="m" class="on">남성</button><button type="button" data-v="f">여성</button></div>
    <div class="g3"><div class="f"><label for="age">나이(세)</label><input type="number" id="age" inputmode="numeric" min="10" max="100" value="40"></div><div class="f"><label for="h">키(cm)</label><input type="number" id="h" inputmode="decimal" min="100" max="230" value="170"></div><div class="f"><label for="w">몸무게(kg)</label><input type="number" id="w" inputmode="decimal" min="25" max="250" value="65"></div></div>
    <div class="f"><label for="act">활동량</label><select id="act"><option value="1.2">거의 앉아서 생활 (운동 거의 안 함)</option><option value="1.375" selected>가벼운 활동 (주 1~3회 운동)</option><option value="1.55">보통 활동 (주 3~5회 운동)</option><option value="1.725">활동 많음 (주 6~7회 운동)</option><option value="1.9">매우 많음 (육체노동·선수)</option></select></div>
    <div class="f"><label>목표</label><div class="seg" id="goal" style="--n:3"><button type="button" data-v="-500">감량</button><button type="button" data-v="0" class="on">유지</button><button type="button" data-v="300">증량</button></div></div></div>
  <div class="card" id="out"></div>''',
 r'''
let S = Object.assign({ sex: "m", age: 40, h: 170, w: 65, act: "1.375", goal: "0" }, ld(KEY) || {});
function setSeg(id, v) { document.querySelectorAll("#" + id + " button").forEach(b => b.classList.toggle("on", b.dataset.v === String(v))); }
function calc() {
  const a = +$("age").value, h = +$("h").value, w = +$("w").value;
  if (!(a > 0 && h > 0 && w > 0)) { $("out").innerHTML = '<p class="muted">나이·키·몸무게를 입력해 주세요.</p>'; return; }
  S = { sex: S.sex, age: a, h, w, act: $("act").value, goal: S.goal }; sv(KEY, S);
  const bmr = 10 * w + 6.25 * h - 5 * a + (S.sex === "m" ? 5 : -161), tdee = bmr * +S.act, goal = +S.goal, tgt = Math.round(tdee + goal);
  const floor = S.sex === "m" ? 1500 : 1200, low = tgt < floor;
  const rows = [["탄수화물", .5, 4], ["단백질", .25, 4], ["지방", .25, 9]].map(([n, r, k]) => `<tr><td>${n}</td><td>${Math.round(tgt * r / k)} g</td><td class="muted">${Math.round(tgt * r)} kcal · ${r * 100}%</td></tr>`).join("");
  $("out").innerHTML = `<div class="center"><div class="note">기초대사량 (BMR)</div><div class="num">${Math.round(bmr).toLocaleString()} kcal</div><div class="note">하루 총 소비 열량 (활동 반영)</div><div class="num">${Math.round(tdee).toLocaleString()} kcal</div></div>
    <div class="center" style="background:var(--soft);border-radius:12px;padding:10px"><div class="note">하루 섭취 목표 (${goal < 0 ? "체중 감량" : goal > 0 ? "체중 증량" : "체중 유지"})</div><div class="num">${tgt.toLocaleString()} kcal</div>${goal < 0 ? `<div class="note">한 달에 약 2kg(주 0.5kg) 감량 속도예요</div>` : goal > 0 ? `<div class="note">근력 운동과 함께하면 좋아요</div>` : ""}</div>
    ${low ? `<p class="note" style="color:var(--bad)">⚠️ 목표가 ${floor.toLocaleString()}kcal보다 낮아요. 너무 적게 먹으면 근육이 줄고 건강을 해칠 수 있어요. 활동량을 늘리는 쪽을 권해요.</p>` : ""}
    <div><b>🍚 영양소 배분 예시</b><table style="width:100%;border-collapse:collapse;margin-top:4px"><tbody>${rows}</tbody></table></div>
    <p class="note">미플린-세인트 지오 공식으로 추정한 값이에요. 근육량·질환·임신·약 복용에 따라 실제와 다를 수 있고 의학적 진단이 아니에요. 몸 상태가 걱정되면 의사나 영양사와 상의하세요.</p>`;
}
setSeg("sex", S.sex); setSeg("goal", S.goal); $("age").value = S.age; $("h").value = S.h; $("w").value = S.w; $("act").value = S.act;
$("sex").onclick = e => { const b = e.target.closest("[data-v]"); if (!b) return; S.sex = b.dataset.v; setSeg("sex", S.sex); calc(); };
$("goal").onclick = e => { const b = e.target.closest("[data-v]"); if (!b) return; S.goal = b.dataset.v; setSeg("goal", S.goal); calc(); };
["age", "h", "w", "act"].forEach(i => $(i).addEventListener("input", calc)); calc();
''')

# ───────── 2. 걸음·운동 칼로리
mk("exercise-kcal.html", "걸음·운동 칼로리", "🏃", 150, "exercise-kcal-v1",
 "걸음 수나 운동 종류와 시간으로 소모한 칼로리를 계산해요. 운동 강도 지수(MET)로 계산한 추정치예요. 입력값은 이 폰에만 저장돼요.",
 '''  <div class="card"><div class="g2"><div class="f"><label for="w">몸무게(kg)</label><input type="number" id="w" inputmode="decimal" min="25" max="250" value="65"></div><div class="f"><label for="h">키(cm)</label><input type="number" id="h" inputmode="decimal" min="100" max="230" value="170"></div></div>
    <div class="seg" id="tab" style="--n:2"><button type="button" data-v="step" class="on">걸음 수</button><button type="button" data-v="sport">운동 종류</button></div>
    <div id="pStep"><div class="f"><label for="steps">걸음 수</label><input type="number" id="steps" inputmode="numeric" min="0" value="8000"></div></div>
    <div id="pSport" hidden><div class="f"><label for="sp">운동</label><select id="sp"></select></div><div class="f" style="margin-top:8px"><label for="min">운동 시간(분)</label><input type="number" id="min" inputmode="numeric" min="1" value="30"></div></div></div>
  <div class="card" id="out"></div>''',
 r'''
const SP = [["걷기 · 천천히 (3.2km/h)", 2.8], ["걷기 · 보통 (4.8km/h)", 3.5], ["걷기 · 빠르게 (5.6km/h)", 4.3], ["달리기 · 8km/h", 8.3], ["달리기 · 10km/h", 9.8], ["달리기 · 12km/h", 11.8], ["자전거 · 보통", 6.8], ["수영 · 보통", 6], ["등산", 6.5], ["계단 오르기", 8.8], ["줄넘기", 11.8], ["에어로빅·댄스", 6.5], ["요가·스트레칭", 2.5], ["근력 운동 · 가볍게", 3.5], ["근력 운동 · 강하게", 6], ["배드민턴·탁구", 4.5], ["축구·농구", 7], ["집안일·청소", 3.3]];
const FOOD = [["밥 한 공기", 300], ["라면 1봉지", 500], ["치킨 한 조각", 250], ["콜라 1캔", 100], ["케이크 한 조각", 350], ["바나나 1개", 90]];
let S = Object.assign({ w: 65, h: 170, tab: "step", steps: 8000, sp: 1, min: 30 }, ld(KEY) || {});
$("sp").innerHTML = SP.map((x, i) => `<option value="${i}">${x[0]}</option>`).join("");
function setTab(v) { document.querySelectorAll("#tab button").forEach(b => b.classList.toggle("on", b.dataset.v === v)); $("pStep").hidden = v !== "step"; $("pSport").hidden = v !== "sport"; }
function calc() {
  const w = +$("w").value, h = +$("h").value; S = { w, h, tab: S.tab, steps: +$("steps").value, sp: +$("sp").value, min: +$("min").value }; sv(KEY, S);
  if (!(w > 0)) { $("out").innerHTML = '<p class="muted">몸무게를 입력해 주세요.</p>'; return; }
  let kcal = 0, lines = "";
  if (S.tab === "step") {
    if (!(S.steps >= 0) || !(h > 0)) { $("out").innerHTML = '<p class="muted">걸음 수와 키를 입력해 주세요.</p>'; return; }
    const stride = h * .415 / 100, km = S.steps * stride / 1000, hr = km / 4.8; kcal = 3.5 * w * hr * 1.05;
    lines = `<div class="note">걸음 수 ${S.steps.toLocaleString()}걸음 · 보폭 약 ${(stride * 100).toFixed(0)}cm</div><div>이동 거리 <b>${km.toFixed(2)} km</b> · 걸은 시간 약 <b>${Math.round(hr * 60)}분</b> (보통 걸음 기준)</div>`;
  } else {
    if (!(S.min > 0)) { $("out").innerHTML = '<p class="muted">운동 시간을 입력해 주세요.</p>'; return; }
    const m = SP[S.sp][1]; kcal = m * w * (S.min / 60) * 1.05; lines = `<div class="note">${SP[S.sp][0]} · ${S.min}분 · 강도 ${m} MET</div>`;
  }
  const walkMin = k => Math.round(k / (3.5 * w * 1.05 / 60));
  $("out").innerHTML = `<div class="center"><div class="note">소모 열량</div><div class="num">${Math.round(kcal).toLocaleString()} kcal</div></div>${lines}
    <div><b>🍽️ 이만큼이면 이런 음식과 비슷해요</b><div class="note">${FOOD.map(([n, k]) => `${n} ${k}kcal → 걷기 ${walkMin(k)}분`).join("<br>")}</div></div>
    <p class="note">MET 값은 신체 활동 연구 자료를 참고한 평균치예요. 실제 소모량은 체력·속도·지형에 따라 달라요. 의학적 처방이 아니에요.</p>`;
}
$("w").value = S.w; $("h").value = S.h; $("steps").value = S.steps; $("sp").value = S.sp; $("min").value = S.min; setTab(S.tab);
$("tab").onclick = e => { const b = e.target.closest("[data-v]"); if (!b) return; S.tab = b.dataset.v; setTab(S.tab); calc(); };
["w", "h", "steps", "sp", "min"].forEach(i => $(i).addEventListener("input", calc)); calc();
''')

# ───────── 3. 집안일 당번표
mk("chore-rota.html", "집안일 당번표", "🧹", 95, "chore-rota-v1",
 "가족 이름과 집안일을 넣으면 매주 돌아가며 당번이 바뀌어요. 한 일은 체크해 두면 누가 얼마나 했는지 알 수 있어요. 이 폰에만 저장돼요.",
 '''  <div class="seg" id="tab" style="--n:3"><button type="button" data-v="0" class="on">이번 주</button><button type="button" data-v="1">다음 주</button><button type="button" data-v="s">설정</button></div>
  <div id="view"></div>''',
 r'''
let S = Object.assign({ members: ["엄마", "아빠", "첫째"], chores: ["설거지", "청소기", "쓰레기 버리기", "빨래 개기"], off: 0, done: {}, cnt: {} }, ld(KEY) || {});
let tab = "0";
const wk = () => Math.floor((dnum(todayS()) + 3) / 7);
function weekLabel(w) { const mon = dnum("1970-01-01") + w * 7 - 3; const d = new Date(mon * 86400000); const e = new Date((mon + 6) * 86400000); return `${d.getUTCMonth() + 1}/${d.getUTCDate()}(월) ~ ${e.getUTCMonth() + 1}/${e.getUTCDate()}(일)`; }
const who = (w, k) => S.members.length ? S.members[(((k + w + S.off) % S.members.length) + S.members.length) % S.members.length] : "-";
function save() { sv(KEY, S); }
function render() {
  document.querySelectorAll("#tab button").forEach(b => b.classList.toggle("on", b.dataset.v === tab));
  if (tab === "s") {
    $("view").innerHTML = `<div class="card"><b>👨‍👩‍👧 가족</b>${S.members.map((m, i) => `<div class="li"><span>${esc(m)}</span><button class="x" data-dm="${i}" type="button" aria-label="삭제">✕</button></div>`).join("")}<div class="g2" style="grid-template-columns:1fr auto"><input type="text" id="nm" maxlength="8" placeholder="이름 추가"><button class="btn sm" id="am" type="button">추가</button></div></div>
      <div class="card"><b>🧽 집안일</b>${S.chores.map((m, i) => `<div class="li"><span>${esc(m)}</span><button class="x" data-dc="${i}" type="button" aria-label="삭제">✕</button></div>`).join("")}<div class="g2" style="grid-template-columns:1fr auto"><input type="text" id="nc" maxlength="14" placeholder="집안일 추가"><button class="btn sm" id="ac" type="button">추가</button></div></div>
      <div class="card"><b>🔄 이번 주 당번 한 칸 밀기</b><p class="note">누구에게 어떤 일이 걸릴지 바꾸고 싶을 때 눌러요.</p><button class="btn ghost" id="shift" type="button">한 칸 밀기</button></div>`;
    $("am").onclick = () => { const v = $("nm").value.trim(); if (v) { S.members.push(v); save(); render(); } };
    $("ac").onclick = () => { const v = $("nc").value.trim(); if (v) { S.chores.push(v); save(); render(); } };
    $("shift").onclick = () => { S.off++; save(); $("shift").textContent = "✅ 밀었어요"; };
    $("view").querySelectorAll("[data-dm]").forEach(b => b.onclick = () => { S.members.splice(+b.dataset.dm, 1); save(); render(); });
    $("view").querySelectorAll("[data-dc]").forEach(b => b.onclick = () => { S.chores.splice(+b.dataset.dc, 1); save(); render(); });
    return;
  }
  const w = wk() + +tab;
  if (!S.members.length || !S.chores.length) { $("view").innerHTML = '<div class="card"><p class="muted">설정에서 가족과 집안일을 먼저 추가해 주세요.</p></div>'; return; }
  const rows = S.chores.map((c, k) => { const p = who(w, k), key = w + "|" + c, d = !!S.done[key]; return `<div class="li"><span><b>${esc(c)}</b><br><span class="note">당번: ${esc(p)}</span></span>${tab === "0" ? `<button type="button" class="chip${d ? " on" : ""}" data-k="${esc(key)}" data-p="${esc(p)}">${d ? "✅ 했어요" : "아직"}</button>` : ""}</div>`; }).join("");
  const tot = Object.keys(S.cnt).filter(n => S.members.includes(n)).map(n => `<span class="tag">${esc(n)} ${S.cnt[n]}번</span>`).join(" ");
  const dn = tab === "0" ? S.chores.filter(c => S.done[w + "|" + c]).length : 0;
  $("view").innerHTML = `<div class="card"><div class="note">${weekLabel(w)}</div>${rows}${tab === "0" ? `<div class="note">이번 주 ${dn}/${S.chores.length} 완료${dn === S.chores.length ? " 🎉 모두 끝!" : ""}</div>` : ""}</div>${tot ? `<div class="card"><b>📊 지금까지 한 횟수</b><div class="chips">${tot}</div></div>` : ""}`;
  $("view").querySelectorAll("[data-k]").forEach(b => b.onclick = () => { const k = b.dataset.k, p = b.dataset.p; if (S.done[k]) { delete S.done[k]; S.cnt[p] = Math.max(0, (S.cnt[p] || 1) - 1); } else { S.done[k] = 1; S.cnt[p] = (S.cnt[p] || 0) + 1; } save(); render(); });
}
$("tab").onclick = e => { const b = e.target.closest("[data-v]"); if (b) { tab = b.dataset.v; render(); } };
render();
''')

# (순서 정하기·팀 나누기는 order-picker/team-split/ladder-game/lots 로 이미 있어 만들지 않음)

# ───────── 5. 혈압·혈당 기록장
mk("health-log.html", "혈압·혈당 기록장", "🩺", 355, "health-log-v1",
 "혈압과 혈당 수치를 기록하고 추이를 봐요. 분류는 참고용이며 진단이 아니에요. 걱정되는 수치나 증상이 있으면 병원에 문의하세요. 기록은 이 폰에만 저장돼요.",
 '''  <div class="card"><div class="f"><label for="who">기록하는 사람</label><div style="display:grid;grid-template-columns:1fr auto;gap:8px"><select id="who"></select><button class="btn ghost sm" id="addw" type="button">＋ 사람 추가</button></div></div><div id="addbox" hidden style="display:none"></div></div>
  <div class="seg" id="tab" style="--n:2"><button type="button" data-v="bp" class="on">혈압</button><button type="button" data-v="bs">혈당</button></div>
  <div class="card" id="form"></div>
  <div class="card" id="sum"></div>
  <div class="card" id="list"></div>''',
 r'''
let S = Object.assign({ people: ["나"], cur: "나", bp: [], bs: [] }, ld(KEY) || {});
let tab = "bp";
const save = () => sv(KEY, S);
function nowParts() { const d = new Date(); return [ymd(d), pad(d.getHours()) + ":" + pad(d.getMinutes())]; }
function bpCls(s, d) {
  if (s >= 180 || d >= 120) return ["매우 높음", "bad", "🚨 수치가 매우 높아요. 증상이 있으면 바로 119나 병원에 연락하세요."];
  if (s >= 140 || d >= 90) return ["고혈압 범위", "bad", "높은 편이에요. 반복해서 나오면 병원 상담을 권해요."];
  if (s >= 130 || d >= 80) return ["고혈압 전단계", "wn", ""];
  if (s >= 120) return ["주의", "wn", ""];
  if (s < 90 || d < 60) return ["낮은 편", "wn", "어지러우면 앉거나 누워 쉬세요."];
  return ["정상", "ok", ""];
}
function bsCls(v, t) {
  if (v < 70) return ["저혈당 주의", "bad", "🚨 식은땀·떨림이 있으면 당분을 먹고, 계속되면 병원에 연락하세요."];
  if (v >= 300) return ["매우 높음", "bad", "🚨 수치가 매우 높아요. 병원에 연락하세요."];
  if (t === "fast") return v >= 126 ? ["당뇨 범위", "bad", ""] : v >= 100 ? ["공복혈당 주의", "wn", ""] : ["정상", "ok", ""];
  if (t === "after") return v >= 200 ? ["높음", "bad", ""] : v >= 140 ? ["주의", "wn", ""] : ["정상", "ok", ""];
  return v >= 200 ? ["높음", "bad", ""] : v >= 140 ? ["주의", "wn", ""] : ["정상 범위", "ok", ""];
}
const BT = { fast: "공복", after: "식후 2시간", bed: "취침 전", etc: "기타" };
function form() {
  const [d, t] = nowParts();
  const dt = `<div class="g2"><div class="f"><label for="fd">날짜</label><input type="date" id="fd" value="${d}"></div><div class="f"><label for="ft">시간</label><input type="time" id="ft" value="${t}"></div></div>`;
  $("form").innerHTML = tab === "bp" ? dt + `<div class="g3"><div class="f"><label for="a">수축기(높은)</label><input type="number" id="a" inputmode="numeric" placeholder="120"></div><div class="f"><label for="b">이완기(낮은)</label><input type="number" id="b" inputmode="numeric" placeholder="80"></div><div class="f"><label for="c">맥박</label><input type="number" id="c" inputmode="numeric" placeholder="70"></div></div><button class="btn" id="save" type="button">기록하기</button>`
    : dt + `<div class="g2"><div class="f"><label for="a">혈당(mg/dL)</label><input type="number" id="a" inputmode="numeric" placeholder="95"></div><div class="f"><label for="k">측정 시점</label><select id="k"><option value="fast">공복</option><option value="after">식후 2시간</option><option value="bed">취침 전</option><option value="etc">기타</option></select></div></div><button class="btn" id="save" type="button">기록하기</button>`;
  $("save").onclick = () => {
    const a = +$("a").value, o = { id: uid(), p: S.cur, d: $("fd").value || d, t: $("ft").value || t };
    if (!(a > 0)) { $("a").focus(); return; }
    if (tab === "bp") { const b = +$("b").value; if (!(b > 0)) { $("b").focus(); return; } o.s = a; o.dd = b; o.hr = +$("c").value || 0; S.bp.push(o); } else { o.v = a; o.k = $("k").value; S.bs.push(o); }
    save(); render();
  };
}
function chart(arr, get, lo, hi) {
  if (arr.length < 2) return "";
  const W = 300, H = 90, vs = arr.map(get), mn = Math.min(...vs, lo) - 5, mx = Math.max(...vs, hi) + 5;
  const X = i => 8 + i * (W - 16) / (arr.length - 1), Y = v => H - 6 - (v - mn) / (mx - mn) * (H - 12);
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="추이 그래프"><rect x="0" y="${Y(hi)}" width="${W}" height="${Math.max(0, Y(lo) - Y(hi))}" fill="var(--ok)" opacity=".12"/><polyline fill="none" stroke="var(--accent)" stroke-width="2" points="${arr.map((x, i) => X(i) + "," + Y(get(x))).join(" ")}"/>${arr.map((x, i) => `<circle cx="${X(i)}" cy="${Y(get(x))}" r="3" fill="var(--accent)"/>`).join("")}</svg>`;
}
function render() {
  $("who").innerHTML = S.people.map(p => `<option${p === S.cur ? " selected" : ""}>${esc(p)}</option>`).join("");
  document.querySelectorAll("#tab button").forEach(b => b.classList.toggle("on", b.dataset.v === tab));
  form();
  const all = (tab === "bp" ? S.bp : S.bs).filter(x => x.p === S.cur).sort((a, b) => (a.d + a.t).localeCompare(b.d + b.t)), last = all.slice(-14);
  $("list").hidden = !all.length; if (!all.length) { $("sum").innerHTML = '<p class="muted">아직 기록이 없어요. 위에서 첫 기록을 남겨 보세요.</p>'; $("list").innerHTML = ""; return; }
  const l = all[all.length - 1], w7 = all.filter(x => dnum(x.d) >= dnum(todayS()) - 6), avg = f => w7.length ? Math.round(w7.reduce((a, x) => a + f(x), 0) / w7.length) : 0;
  const c = tab === "bp" ? bpCls(l.s, l.dd) : bsCls(l.v, l.k);
  $("sum").innerHTML = `<div class="note">가장 최근 (${l.d} ${l.t})</div><div class="num">${tab === "bp" ? `${l.s} / ${l.dd}${l.hr ? ` <span class="note">맥박 ${l.hr}</span>` : ""}` : `${l.v} mg/dL <span class="note">${BT[l.k]}</span>`}</div><div><span class="tag ${c[1]}">${c[0]}</span></div>${c[2] ? `<p class="note" style="color:var(--bad)">${c[2]}</p>` : ""}
    ${w7.length ? `<div class="note">최근 7일 평균 (${w7.length}회): <b>${tab === "bp" ? avg(x => x.s) + " / " + avg(x => x.dd) : avg(x => x.v) + " mg/dL"}</b></div>` : ""}
    ${chart(last, tab === "bp" ? x => x.s : x => x.v, tab === "bp" ? 90 : 70, tab === "bp" ? 120 : 100)}<div class="note">초록 띠는 대략 정상 범위예요 · 최근 ${last.length}회</div>
    <p class="note">참고용 분류예요. 같은 수치도 사람과 상황에 따라 의미가 달라서, 진단과 치료는 의사와 상의하세요.</p>`;
  $("list").innerHTML = `<b>📋 기록</b>` + all.slice().reverse().slice(0, 40).map(x => { const cc = tab === "bp" ? bpCls(x.s, x.dd) : bsCls(x.v, x.k); return `<div class="li"><span>${x.d.slice(5).replace("-", "/")} ${x.t}<br><b>${tab === "bp" ? x.s + "/" + x.dd : x.v}</b> ${tab === "bs" ? `<span class="note">${BT[x.k]}</span>` : ""} <span class="tag ${cc[1]}">${cc[0]}</span></span><button class="x" data-id="${x.id}" type="button" aria-label="삭제">✕</button></div>`; }).join("") + `<button class="btn ghost sm" id="cp" type="button" style="margin-top:8px">📋 기록 복사(병원 상담용)</button>`;
  $("list").querySelectorAll("[data-id]").forEach(b => b.onclick = () => { const k = tab === "bp" ? "bp" : "bs"; S[k] = S[k].filter(x => x.id !== b.dataset.id); save(); render(); });
  $("cp").onclick = () => { const t = `[${S.cur}] ${tab === "bp" ? "혈압" : "혈당"} 기록\n` + all.map(x => `${x.d} ${x.t} ${tab === "bp" ? x.s + "/" + x.dd + (x.hr ? " 맥박" + x.hr : "") : x.v + " (" + BT[x.k] + ")"}`).join("\n"); try { navigator.clipboard.writeText(t).then(() => { $("cp").textContent = "✅ 복사했어요"; }, () => { $("cp").textContent = "복사 실패"; }); } catch (e) { $("cp").textContent = "복사 실패"; } };
}
$("tab").onclick = e => { const b = e.target.closest("[data-v]"); if (b) { tab = b.dataset.v; render(); } };
$("who").onchange = () => { S.cur = $("who").value; save(); render(); };
$("addw").onclick = () => { const n = (window.prompt("추가할 사람 이름") || "").trim().slice(0, 8); if (n && !S.people.includes(n)) { S.people.push(n); S.cur = n; save(); render(); } };
render();
''')

# ───────── 6. 약 복용 체크표
mk("med-check.html", "약 복용 체크표", "💊", 200, "med-check-v1",
 "약 이름과 먹는 시간을 등록하고 먹을 때마다 체크해요. 지난 7일간 잘 챙겼는지도 볼 수 있어요. 복용 방법은 의사·약사의 안내를 따르세요. 이 폰에만 저장돼요.",
 '''  <div class="card"><div class="g2" style="grid-template-columns:auto 1fr auto;align-items:center"><button class="x" id="prev" type="button" aria-label="전날">◀</button><b class="center" id="dl"></b><button class="x" id="next" type="button" aria-label="다음날">▶</button></div></div>
  <div class="card" id="today"></div>
  <div class="card" id="wk"></div>
  <details class="card"><summary><b>➕ 약 등록·관리</b></summary><div id="mgr" style="display:grid;gap:10px;margin-top:10px"></div></details>''',
 r'''
const SL = [["m", "아침"], ["n", "점심"], ["e", "저녁"], ["b", "자기 전"]];
let S = Object.assign({ meds: [], log: {} }, ld(KEY) || {});
let day = todayS();
const save = () => sv(KEY, S);
function due(d) { const a = []; S.meds.forEach(m => { if ((m.since || "0000") > d) return; SL.forEach(([k]) => { if (m.t.includes(k)) a.push(m.id + "|" + k); }); }); return a; }
function render() {
  $("dl").textContent = `${day.slice(5).replace("-", "/")} (${wdOf(day)})${day === todayS() ? " · 오늘" : ""}`; $("next").disabled = day >= todayS();
  const lg = S.log[day] || {}, items = due(day);
  $("today").innerHTML = S.meds.length ? SL.map(([k, nm]) => { const ms = S.meds.filter(m => m.t.includes(k) && (m.since || "0000") <= day); if (!ms.length) return ""; return `<div><div class="lb">${nm}</div>${ms.map(m => { const key = m.id + "|" + k, on = lg[key]; return `<div class="li"><span><b>${esc(m.n)}</b>${m.memo ? `<br><span class="note">${esc(m.memo)}</span>` : ""}</span><button type="button" class="chip${on ? " on" : ""}" data-k="${key}">${on ? "✅ 먹었어요" : "아직"}</button></div>`; }).join("")}</div>`; }).join("") + `<div class="note">${items.filter(k => lg[k]).length}/${items.length} 복용</div>` : '<p class="muted">아래 "약 등록·관리"에서 약을 먼저 등록해 주세요.</p>';
  const days = Array.from({ length: 7 }, (_, i) => addDays(todayS(), i - 6));
  $("wk").innerHTML = `<b>📅 최근 7일</b><div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center">${days.map(d => { const it = due(d), done = it.filter(k => (S.log[d] || {})[k]).length, p = it.length ? done / it.length : null; return `<div><div class="note">${wdOf(d)}</div><div style="font-size:1.3rem">${p === null ? "·" : p === 1 ? "🟢" : p > 0 ? "🟡" : (d === todayS() ? "⚪" : "🔴")}</div><div class="note">${it.length ? done + "/" + it.length : ""}</div></div>`; }).join("")}</div><div class="note">🟢 모두 복용 · 🟡 일부 · 🔴 안 먹음</div>`;
  $("mgr").innerHTML = S.meds.map(m => `<div class="li"><span><b>${esc(m.n)}</b> <span class="note">${SL.filter(([k]) => m.t.includes(k)).map(x => x[1]).join("·")}</span></span><button class="x" data-dm="${m.id}" type="button" aria-label="삭제">✕</button></div>`).join("")
    + `<div class="f"><label for="mn">약 이름</label><input type="text" id="mn" maxlength="20" placeholder="예: 혈압약"></div><div class="f"><label>먹는 시간</label><div class="chips" id="mt">${SL.map(([k, n]) => `<button type="button" class="chip" data-t="${k}">${n}</button>`).join("")}</div></div><div class="f"><label for="mm">메모(선택)</label><input type="text" id="mm" maxlength="30" placeholder="예: 식후 30분"></div><button class="btn sm" id="am" type="button">등록하기</button>`;
  $("mt").onclick = e => { const b = e.target.closest("[data-t]"); if (b) b.classList.toggle("on"); };
  $("am").onclick = () => { const n = $("mn").value.trim(), t = [...document.querySelectorAll("#mt .on")].map(b => b.dataset.t); if (!n || !t.length) { (n ? $("mt") : $("mn")).focus && (n ? 0 : $("mn").focus()); return; } S.meds.push({ id: uid(), n, t, memo: $("mm").value.trim(), since: todayS() }); save(); render(); };
  $("mgr").querySelectorAll("[data-dm]").forEach(b => b.onclick = () => { if (confirm("이 약을 삭제할까요?")) { S.meds = S.meds.filter(m => m.id !== b.dataset.dm); save(); render(); } });
  $("today").querySelectorAll("[data-k]").forEach(b => b.onclick = () => { const l = S.log[day] || (S.log[day] = {}); if (l[b.dataset.k]) delete l[b.dataset.k]; else l[b.dataset.k] = 1; save(); render(); });
}
$("prev").onclick = () => { day = addDays(day, -1); render(); };
$("next").onclick = () => { if (day < todayS()) { day = addDays(day, 1); render(); } };
render();
''')

# ───────── 7. 감정 기록 일기
mk("mood-diary.html", "감정 기록 일기", "🌈", 330, "mood-diary-v1",
 "오늘 기분을 이모지로 남기고 한 줄 메모를 적어요. 한 달 달력과 통계로 내 마음의 흐름을 볼 수 있어요. 이 폰에만 저장돼요.",
 '''  <div class="card"><div class="lb" id="dt"></div><div class="chips" id="moods" style="justify-content:space-between"></div><div class="lb">오늘 한 일 (여러 개 선택)</div><div class="chips" id="acts"></div><textarea id="memo" rows="3" maxlength="200" placeholder="오늘 한 줄 메모 (선택)"></textarea><button class="btn" id="save" type="button">기록하기</button></div>
  <div class="card"><div style="display:grid;grid-template-columns:auto 1fr auto;align-items:center"><button class="x" id="pm" type="button" aria-label="이전 달">◀</button><b class="center" id="ml"></b><button class="x" id="nm" type="button" aria-label="다음 달">▶</button></div><div id="cal"></div></div>
  <div class="card" id="stat"></div>''',
 r'''
const MOODS = [[5, "😄", "아주 좋음"], [4, "🙂", "좋음"], [3, "😐", "보통"], [2, "😟", "별로"], [1, "😢", "힘듦"]];
const ACTS = ["가족", "친구", "운동", "일·공부", "휴식", "취미", "외출", "맛집", "독서", "잠 푹"];
let S = ld(KEY) || { e: {} };
let sel = todayS(), vm = new Date(), curM = null, curA = [];
const save = () => sv(KEY, S);
$("acts").innerHTML = ACTS.map(a => `<button type="button" class="chip" data-a="${a}">${a}</button>`).join("");
$("moods").innerHTML = MOODS.map(([v, e, n]) => `<button type="button" class="chip" data-m="${v}" style="font-size:1.5rem;padding:6px 10px" aria-label="${n}" title="${n}">${e}</button>`).join("");
function load(d) { sel = d; const x = S.e[d]; curM = x ? x.m : null; curA = x ? [...x.a] : []; $("memo").value = x ? x.t : ""; paint(); }
function paint() {
  $("dt").textContent = `기분 기록 · ${sel.replace(/-/g, ".")} (${wdOf(sel)})${sel === todayS() ? " · 오늘" : ""}`;
  document.querySelectorAll("#moods .chip").forEach(b => b.classList.toggle("on", +b.dataset.m === curM));
  document.querySelectorAll("#acts .chip").forEach(b => b.classList.toggle("on", curA.includes(b.dataset.a)));
  $("save").textContent = S.e[sel] ? "수정하기" : "기록하기";
}
$("moods").onclick = e => { const b = e.target.closest("[data-m]"); if (b) { curM = +b.dataset.m; paint(); } };
$("acts").onclick = e => { const b = e.target.closest("[data-a]"); if (!b) return; const a = b.dataset.a; curA = curA.includes(a) ? curA.filter(x => x !== a) : [...curA, a]; paint(); };
$("save").onclick = () => { if (!curM) { $("moods").scrollIntoView({ block: "center" }); return; } S.e[sel] = { m: curM, a: curA, t: $("memo").value.trim() }; save(); cal(); stat(); paint(); $("save").textContent = "✅ 저장했어요"; };
function cal() {
  const y = vm.getFullYear(), m = vm.getMonth(), first = new Date(y, m, 1).getDay(), n = new Date(y, m + 1, 0).getDate();
  $("ml").textContent = `${y}년 ${m + 1}월`;
  let h = '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center;margin-top:8px">' + WD.map(w => `<div class="note">${w}</div>`).join("") + "<div></div>".repeat(first);
  for (let d = 1; d <= n; d++) { const k = `${y}-${pad(m + 1)}-${pad(d)}`, x = S.e[k], mo = x ? MOODS.find(z => z[0] === x.m)[1] : ""; h += `<button type="button" data-d="${k}" style="border:1px solid ${k === sel ? "var(--accent)" : "var(--line)"};background:var(--surface);border-radius:8px;padding:2px 0;min-height:44px;line-height:1.2"><div class="note">${d}</div><div>${mo}</div></button>`; }
  $("cal").innerHTML = h + "</div>"; $("cal").querySelectorAll("[data-d]").forEach(b => b.onclick = () => { load(b.dataset.d); });
}
function stat() {
  const pre = `${vm.getFullYear()}-${pad(vm.getMonth() + 1)}`, ks = Object.keys(S.e).filter(k => k.startsWith(pre)), xs = ks.map(k => S.e[k]);
  if (!xs.length) { $("stat").innerHTML = '<p class="muted">이 달의 기록이 아직 없어요.</p>'; return; }
  const avg = xs.reduce((a, x) => a + x.m, 0) / xs.length, cnt = MOODS.map(([v, e]) => `${e} ${xs.filter(x => x.m === v).length}`).join(" &nbsp; ");
  const at = {}; xs.forEach(x => x.a.forEach(a => { (at[a] = at[a] || []).push(x.m); }));
  const top = Object.entries(at).filter(([, v]) => v.length >= 2).map(([a, v]) => [a, v.reduce((p, q) => p + q, 0) / v.length, v.length]).sort((a, b) => b[1] - a[1]).slice(0, 3);
  $("stat").innerHTML = `<b>📊 이번 달 마음 통계</b><div>기록한 날 <b>${xs.length}일</b> · 평균 기분 <b>${avg.toFixed(1)}</b> / 5</div><div>${cnt}</div>${top.length ? `<div class="note">기분이 좋았던 날 자주 한 일: ${top.map(t => `<b>${t[0]}</b>(평균 ${t[1].toFixed(1)}, ${t[2]}번)`).join(", ")}</div>` : ""}`;
}
$("pm").onclick = () => { vm = new Date(vm.getFullYear(), vm.getMonth() - 1, 1); cal(); stat(); };
$("nm").onclick = () => { vm = new Date(vm.getFullYear(), vm.getMonth() + 1, 1); cal(); stat(); };
load(todayS()); cal(); stat();
''')

# ───────── 8. 냉장고 유통기한 기록
mk("fridge-date.html", "냉장고 유통기한", "🧊", 190, "fridge-date-v1",
 "냉장고 속 음식의 유통기한을 적어 두면 임박한 순서대로 알려 줘요. 기한이 지난 음식은 상태를 꼭 확인하고 의심되면 버리세요. 이 폰에만 저장돼요.",
 '''  <div class="card"><div class="f"><label for="n">음식 이름</label><input type="text" id="n" maxlength="20" placeholder="예: 우유, 두부"></div>
    <div class="g2"><div class="f"><label for="d">유통기한(소비기한)</label><input type="date" id="d"></div><div class="f"><label for="pl">보관 장소</label><select id="pl"><option value="fr">냉장</option><option value="fz">냉동</option><option value="rm">실온</option></select></div></div>
    <div class="f"><label>오늘부터 며칠 뒤로 입력</label><div class="chips"><button type="button" class="chip" data-p="3">3일</button><button type="button" class="chip" data-p="7">1주</button><button type="button" class="chip" data-p="14">2주</button><button type="button" class="chip" data-p="30">1달</button><button type="button" class="chip" data-p="90">3달</button><button type="button" class="chip" data-p="180">6달</button></div></div>
    <button class="btn" id="add" type="button">➕ 추가하기</button></div>
  <div class="seg" id="flt" style="--n:4"><button type="button" data-v="all" class="on">전체</button><button type="button" data-v="fr">냉장</button><button type="button" data-v="fz">냉동</button><button type="button" data-v="rm">실온</button></div>
  <div class="card" id="list"></div>''',
 r'''
const PL = { fr: "냉장", fz: "냉동", rm: "실온" };
let S = ld(KEY) || { items: [] }, flt = "all";
const save = () => sv(KEY, S);
$("d").value = addDays(todayS(), 7);
document.querySelector(".chips").onclick = e => { const b = e.target.closest("[data-p]"); if (b) $("d").value = addDays(todayS(), +b.dataset.p); };
$("add").onclick = () => { const n = $("n").value.trim(); if (!n) { $("n").focus(); return; } if (!$("d").value) { $("d").focus(); return; } S.items.push({ id: uid(), n, d: $("d").value, p: $("pl").value }); save(); $("n").value = ""; render(); };
$("flt").onclick = e => { const b = e.target.closest("[data-v]"); if (!b) return; flt = b.dataset.v; document.querySelectorAll("#flt button").forEach(x => x.classList.toggle("on", x === b)); render(); };
function render() {
  const t = dnum(todayS()), arr = S.items.filter(x => flt === "all" || x.p === flt).map(x => ({ ...x, left: dnum(x.d) - t })).sort((a, b) => a.left - b.left);
  const soon = S.items.filter(x => dnum(x.d) - t <= 3 && dnum(x.d) - t >= 0).length, over = S.items.filter(x => dnum(x.d) - t < 0).length;
  const head = S.items.length ? `<div class="note">${over ? `<b style="color:var(--bad)">기한 지남 ${over}개</b> · ` : ""}${soon ? `<b>3일 이내 ${soon}개</b> · ` : ""}전체 ${S.items.length}개</div>` : "";
  $("list").innerHTML = head + (arr.length ? arr.map(x => { const c = x.left < 0 ? "bad" : x.left <= 3 ? "wn" : "ok", lb = x.left < 0 ? `${-x.left}일 지남` : x.left === 0 ? "오늘까지" : `D-${x.left}`; return `<div class="li"><span><b>${esc(x.n)}</b> <span class="tag">${PL[x.p]}</span><br><span class="note">${x.d.replace(/-/g, ".")}</span></span><span style="display:flex;gap:4px;align-items:center"><span class="tag ${c}">${lb}</span><button class="x" data-id="${x.id}" type="button" aria-label="다 먹음 또는 버림">✕</button></span></div>`; }).join("") + `<p class="note">✕ 를 누르면 목록에서 지워요 (다 먹었거나 버렸을 때).</p>` : '<p class="muted">등록된 음식이 없어요.</p>');
  $("list").querySelectorAll("[data-id]").forEach(b => b.onclick = () => { S.items = S.items.filter(x => x.id !== b.dataset.id); save(); render(); });
}
render();
''')
