import sys, json
sys.path.insert(0, ".")
from mkpage import make
_km = json.load(open("keymap.json", encoding="utf-8")); _km.update({"hanja-write-strokefix-v1": "한자 획순 수정", "hanja-write-nums-v1": "한자 쓰기 설정", "hanja-today-v1": "오늘의 한자 학습 기록"})
KM = json.dumps(_km, ensure_ascii=False)
CSS = '''.li{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--line)}.li:last-child{border-bottom:0}.x{background:none;border:0;color:var(--muted);font-size:1.1rem;padding:4px 8px}.btn.sm{padding:8px 14px;font-size:1rem}.lb{font-size:.88rem;color:var(--muted);font-weight:700}.note{font-size:.85rem;color:var(--muted)}.nm{flex:1;min-width:0}.nm input{background:transparent;border:1px solid transparent;font-weight:700;padding:8px 6px}.nm input:focus{border-color:var(--line);background:var(--soft)}.g2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}.ok{color:var(--ok);font-weight:700}.bad{color:var(--bad);font-weight:700}input[type=file]{width:100%;font:inherit}.opt{display:flex;gap:8px;align-items:flex-start;font-size:.95rem}.tbl{width:100%;border-collapse:collapse;font-size:.9rem}.tbl td{padding:4px 2px;border-bottom:1px solid var(--line)}.tbl td:last-child{text-align:right;color:var(--muted)}'''

# ───── 가족 명단
make("out/family-members.html", "가족 명단", "👨‍👩‍👧", 25, "family-members-v1",
 "가족 이름을 한 번만 적어 두면, 당번표·점수판·혈압 기록·팀 나누기·순서 정하기에서 '가족 명단 불러오기' 버튼으로 한 번에 쓸 수 있어요. 이 폰에만 저장돼요.",
 '''  <div class="card"><b>👨‍👩‍👧 우리 가족</b><div id="list"></div><div class="g2" style="grid-template-columns:1fr auto"><input type="text" id="nn" maxlength="8" placeholder="이름 추가 (예: 엄마)"><button class="btn sm" id="add" type="button">추가</button></div><div class="note" id="cnt"></div></div>
  <div class="card"><b>📌 어디에서 쓰나요?</b><div class="note">집안일 당번표 · 가족 점수판 · 혈압·혈당 기록장 · 팀 나누기 · 순서·벌칙 정하기 · 성격 유형 테스트(이름 자동 완성)<br>각 화면의 <b>"👨‍👩‍👧 가족 명단 불러오기"</b> 버튼을 누르면 이 명단이 들어가요.</div></div>''',
 r'''
const MAX = 12;
let L = (window.FAMILY ? FAMILY.get() : (ld("family-members-v1") || []));
const save = () => { if (window.FAMILY) FAMILY.set(L); else sv("family-members-v1", L); };
function render() {
  $("list").innerHTML = L.length ? L.map((n, i) => `<div class="li"><span class="nm"><input type="text" value="${esc(n)}" maxlength="8" data-i="${i}" aria-label="이름"></span><span style="display:flex"><button class="x" data-up="${i}" type="button" aria-label="위로"${i ? "" : " disabled"}>▲</button><button class="x" data-dn="${i}" type="button" aria-label="아래로"${i < L.length - 1 ? "" : " disabled"}>▼</button><button class="x" data-del="${i}" type="button" aria-label="삭제">✕</button></span></div>`).join("") : '<p class="muted">아직 등록된 가족이 없어요. 아래에 이름을 적어 추가해 주세요.</p>';
  $("cnt").textContent = `${L.length}명 / 최대 ${MAX}명`;
}
function addName() { const v = $("nn").value.trim().slice(0, 8); if (!v) { $("nn").focus(); return; } if (L.includes(v)) { $("cnt").innerHTML = '<span class="bad">같은 이름이 이미 있어요</span>'; return; } if (L.length >= MAX) { $("cnt").innerHTML = '<span class="bad">최대 12명까지예요</span>'; return; } L.push(v); save(); $("nn").value = ""; render(); $("nn").focus(); }
$("add").onclick = addName; $("nn").addEventListener("keydown", e => { if (e.key === "Enter") addName(); });
$("list").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; const g = k => b.dataset[k] !== undefined ? +b.dataset[k] : null;
  if (g("del") !== null) { L.splice(g("del"), 1); } else if (g("up") !== null && g("up") > 0) { const i = g("up"); [L[i - 1], L[i]] = [L[i], L[i - 1]]; } else if (g("dn") !== null && g("dn") < L.length - 1) { const i = g("dn"); [L[i + 1], L[i]] = [L[i], L[i + 1]]; } else return; save(); render(); });
$("list").addEventListener("change", e => { const i = +e.target.dataset.i, v = e.target.value.trim().slice(0, 8); if (!v || (L.includes(v) && L[i] !== v)) { e.target.value = L[i]; return; } L[i] = v; save(); render(); });
render();
''' + "\n", CSS)
# script tag for family.js
p = "out/family-members.html"; s = open(p, encoding="utf-8").read(); s = s.replace("</body>", '<script src="family.js"></script>\n</body>', 1)
# family.js must load before page script uses FAMILY -> put in head
s = s.replace("<script>\nconst $ = id", '<script src="family.js"></script>\n<script>\nconst $ = id', 1); s = s.replace('<script src="family.js"></script>\n</body>', "</body>")
open(p, "w", encoding="utf-8").write(s)

# ───── 백업·복원
BODY = '''  <div class="card"><b>💾 백업 파일 만들기</b><div class="note">이 폰에 저장된 모든 기록(약 복용, 혈압·혈당, 용돈, 일기, 점수판, 게임 최고 기록, 오답 노트 등)을 파일 하나로 저장해요.</div><div id="sum"></div>
    <div class="g2"><button class="btn" id="dl" type="button">⬇️ 파일로 저장</button><button class="btn ghost" id="sh" type="button">📤 공유·보내기</button></div><div class="note" id="msg1"></div></div>
  <div class="card"><b>📥 백업에서 복원하기</b><div class="note">새 폰이나 앱을 지운 뒤에 백업 파일을 골라 기록을 되돌려요. 먼저 파일을 고르면 내용을 보여 드려요.</div>
    <input type="file" id="file" accept=".json,application/json"><div id="prev"></div></div>
  <div class="card"><b>❓ 잘 쓰는 방법</b><div class="note">• 한 달에 한 번, 또는 약·혈압처럼 소중한 기록을 많이 쌓았을 때 백업해 두세요.<br>• 저장한 파일은 카카오톡 "나에게 보내기"나 구글 드라이브에 올려 두면 폰을 바꿔도 안전해요.<br>• 백업 파일에는 약 이름·혈압 같은 개인 기록이 들어 있어요. 아무에게나 보내지 마세요.<br>• 앱이 다른 주소(다른 사이트)에서 열리면 기록은 따로 저장돼요. 같은 주소에서 복원하세요.</div></div>'''
JS = r'''
const KM = ''' + KM + r''';
const META = ["fg-first-seen", "fg-backup-last", "fg-backup-snooze"];
const isGame = k => /-best-|-wins-|-stats-/.test(k);
function allKeys() { const o = []; try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (!META.includes(k)) o.push(k); } } catch (e) {} return o.sort(); }
function snapshot() { const d = {}; allKeys().forEach(k => { try { d[k] = localStorage.getItem(k); } catch (e) {} }); return { app: "family-games", v: 1, saved: new Date().toISOString(), data: d }; }
const nameOf = k => KM[k] || (k.replace(/-v\d+$/, "") + " (기타)");
function groups(d) { const life = [], game = []; Object.keys(d).forEach(k => (isGame(k) ? game : life).push(k)); return { life, game }; }
function renderSum() {
  const g = groups(snapshot().data), rows = g.life.map(k => { let n = ""; try { const v = JSON.parse(localStorage.getItem(k)); n = Array.isArray(v) ? v.length + "개" : v && typeof v === "object" ? Object.keys(v).length + "항목" : ""; } catch (e) {} return `<tr><td>${esc(nameOf(k))}</td><td>${n}</td></tr>`; }).join("");
  $("sum").innerHTML = `<table class="tbl"><tbody>${rows || '<tr><td colspan="2" class="muted">저장된 기록이 아직 없어요</td></tr>'}${g.game.length ? `<tr><td>게임 최고 기록</td><td>${g.game.length}개</td></tr>` : ""}</tbody></table>`;
  let last = 0; try { last = +localStorage.getItem("fg-backup-last") || 0; } catch (e) {}
  $("msg1").textContent = last ? "마지막 백업: " + new Date(last).toLocaleDateString("ko-KR") : "아직 백업한 적이 없어요.";
}
function fileObj() { const s = JSON.stringify(snapshot()), d = new Date(), n = `family-games-backup-${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}.json`; return { s, n, blob: new Blob([s], { type: "application/json" }) }; }
function done() { try { localStorage.setItem("fg-backup-last", String(Date.now())); } catch (e) {} renderSum(); }
$("dl").onclick = () => { const f = fileObj(), a = document.createElement("a"); a.href = URL.createObjectURL(f.blob); a.download = f.n; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); done(); $("msg1").innerHTML = '<span class="ok">✅ 파일을 저장했어요.</span> 다운로드 폴더를 확인하세요.'; };
$("sh").onclick = async () => { const f = fileObj(); try { const file = new File([f.blob], f.n, { type: "application/json" }); if (navigator.canShare && navigator.canShare({ files: [file] })) { await navigator.share({ files: [file], title: "가족 게임 백업" }); done(); $("msg1").innerHTML = '<span class="ok">✅ 보냈어요.</span>'; return; } } catch (e) { if (e && e.name === "AbortError") return; } $("msg1").innerHTML = '<span class="bad">이 폰에서는 공유가 안 돼요.</span> "파일로 저장"을 써 주세요.'; };
let loaded = null;
$("file").onchange = async () => {
  const f = $("file").files[0]; $("prev").innerHTML = ""; loaded = null; if (!f) return;
  try { const j = JSON.parse(await f.text()); if (!j || j.app !== "family-games" || !j.data || typeof j.data !== "object") throw 0; const d = {}; Object.keys(j.data).forEach(k => { if (typeof j.data[k] === "string" && k.length < 80 && !META.includes(k)) d[k] = j.data[k]; }); if (!Object.keys(d).length) throw 0; loaded = d;
    const g = groups(d), cur = snapshot().data, same = Object.keys(d).filter(k => k in cur).length;
    $("prev").innerHTML = `<div class="note">백업한 날: <b>${esc(j.saved ? new Date(j.saved).toLocaleString("ko-KR") : "알 수 없음")}</b> · 기록 ${g.life.length}종 + 게임 최고 기록 ${g.game.length}개</div>
      <table class="tbl"><tbody>${g.life.map(k => `<tr><td>${esc(nameOf(k))}</td><td>${k in cur ? "덮어씀" : "새로 들어옴"}</td></tr>`).join("")}</tbody></table>
      <label class="opt"><input type="radio" name="mode" value="over" checked> <span><b>백업 내용으로 덮어쓰기</b><br><span class="note">같은 이름의 기록은 백업 파일 것으로 바뀌어요 (${same}종).</span></span></label>
      <label class="opt"><input type="radio" name="mode" value="fill"> <span><b>지금 기록은 두고 없는 것만 채우기</b><br><span class="note">이미 있는 기록은 그대로 둬요.</span></span></label>
      <button class="btn" id="go" type="button">📥 복원하기</button><div class="note" id="msg2"></div>`;
    $("go").onclick = () => { const mode = document.querySelector('input[name=mode]:checked').value; if (!confirm(mode === "over" ? "지금 기록 중 같은 이름의 것은 백업 파일 내용으로 바뀝니다. 복원할까요?" : "없는 기록만 채울게요. 진행할까요?")) return; let n = 0; Object.keys(loaded).forEach(k => { try { if (mode === "fill" && localStorage.getItem(k) !== null) return; localStorage.setItem(k, loaded[k]); n++; } catch (e) {} }); $("msg2").innerHTML = `<span class="ok">✅ ${n}종의 기록을 복원했어요.</span> 각 화면을 다시 열면 반영돼 있어요.`; renderSum(); };
  } catch (e) { $("prev").innerHTML = '<p class="bad">가족 게임 백업 파일이 아니에요. 다시 확인해 주세요.</p>'; }
};
renderSum();
'''
make("out/backup.html", "기록 백업·복원", "💾", 160, "backup-v1",
 "폰에 저장된 모든 기록을 파일 하나로 백업하고, 새 폰이나 앱을 지운 뒤에 복원해요. 파일은 이 폰 밖으로 자동 전송되지 않아요.",
 BODY, JS, CSS)
