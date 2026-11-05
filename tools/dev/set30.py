import sys, re
sys.path.insert(0, ".")
from mkpage import make
from set29 import QR_JS, CODEC_JS, CSS as LINK_CSS

# ───────── 같이 하기 (폰 여러 대 연결 + 게임 함께 열기)
# 연결은 이 화면에서 한 번만 해요. 게임은 화면 안(iframe)에 불러오고, 게임끼리 주고받는 말은 이 화면이 전달해요(방장이 가운데서 나눠 줌).
#   같이 하기 ↔ 게임 약속(postMessage):
#     게임→  {fg:"ready"} 준비됐어요 / {fg:"send", to:"host"|"*"|기기id, d} 보내기 / {fg:"h", h} 화면 높이
#     →게임  {fg:"init", me:{id,name}, isHost, players:[{id,name}]} / {fg:"roster", players} / {fg:"msg", from, d}
#   기기끼리(데이터 채널): hi·room·ping·pong·name·buzz·bye(연결 관리), load(게임 바꾸기), g(게임 말 전달 {to, from, d})
# [파일, 이모지, 제목, 설명, 묶음] — 묶음은 HUB_GROUPS. 고유번호는 gamenum.py가 붙여요(game_numbers.json)
HUB_GROUPS = [["board", "♟️", "판 게임"], ["hide", "🙈", "숨기고 겨루기"], ["dice", "🎲", "주사위·숫자"], ["hand", "✊", "눈치·손"], ["party", "🎉", "여러 명 파티"]]
GAMES = [["net-tictactoe.html", "⭕❌", "틱택토", "2명 대결 · 나머지는 구경", "board"],
         ["net-ship-hunt.html", "🚢", "함선 찾기", "2명 · 서로 함선을 숨기고 한 발씩 쏘기", "hide"],
         ["net-omok.html", "⚫⚪", "오목", "2명 · 15×15 판에 5개를 먼저 잇기", "board"],
         ["net-four.html", "🔴🟡", "사목 (4개 잇기)", "2명 · 위에서 떨어뜨려 4개 잇기", "board"],
         ["net-baseball.html", "⚾", "숫자 야구 대결", "2명 · 서로 비밀 숫자를 정하고 먼저 맞히기", "hide"],
         ["net-bingo.html", "🔢", "빙고 대결", "2명 · 각자 판으로 번갈아 부르고 먼저 5줄", "hide"],
         ["net-flip.html", "⚫⚪", "뒤집기 보드", "2명 · 끼워서 뒤집고 돌 많은 쪽이 승리", "board"],
         ["net-dots.html", "🟦", "점 잇기 상자", "2명 · 선을 그어 네모를 더 많이 차지", "board"],
         ["net-mancala.html", "🫘", "칼라하 (콩 옮기기)", "2명 · 콩을 뿌려 창고에 모으기", "board"],
         ["net-hex.html", "🔷", "헥스", "2명 · 육각 판에서 두 변을 먼저 잇기", "board"],
         ["net-31.html", "🔢", "31 게임", "2명 · 1~3개씩 외치고 31을 말하면 짐", "dice"],
         ["net-pig.html", "🎲", "피그 주사위", "2명 · 굴릴까 저금할까, 먼저 100점", "dice"],
         ["net-memory.html", "🃏", "카드 짝 대결", "2명 · 번갈아 짝 맞추기", "hide"],
         ["net-rps.html", "✊", "가위바위보 대결", "2명 · 몰래 고르고 동시에 공개, 3승 먼저", "hand"],
         ["net-highcard.html", "🂡", "하이카드 대결", "2명 · 카드 10장으로 몰래 한 장씩", "hide"],
         ["net-buzzer.html", "🔔", "퀴즈 버저", "여러 명 · 방장이 문제를 내면 먼저 누른 사람이 답해요", "party"],
         ["net-mafia.html", "🕵️", "역할 뽑기 (마피아)", "여러 명 · 각자 폰에 비밀 역할", "party"],
         ["net-react.html", "⚡", "반응 대결", "여러 명 · 초록색이 되면 누구보다 빨리", "hand"],
         ["net-bomb.html", "💣", "폭탄 돌리기", "여러 명 · 폰끼리 폭탄을 넘기다 펑!", "party"],
         ["net-lots.html", "🎟️", "제비뽑기", "여러 명 · 각자 폰에서 한 장씩 뽑기", "party"],
         ["net-onecard.html", "🃏", "원카드", "2명 · 같은 무늬·숫자 내기, 먼저 다 없애기", "hide"],
         ["net-checkers.html", "♛", "체커 (서양 장기)", "2명 · 뛰어넘어 잡기, 끝줄에 가면 왕", "board"],
         ["net-yut.html", "🪵", "윷놀이", "2명 · 윷을 던져 말 2개를 먼저 돌리기", "dice"],
         ["net-yacht.html", "🎲", "주사위 족보", "2~6명 · 차례대로 굴려 12개 족보 채우기", "dice"],
         ["net-wordtrick.html", "🤫", "제시어 추리", "여러 명 · 한 명만 제시어를 몰라요", "party"]]

import gamenum, json as _json
NUMS = gamenum.ensure()
_IG = re.findall(r'\{ id: "(\w+)", n: "([^"]+)", e: "([^"]+)"', open(gamenum.REPO + "/index.html", encoding="utf-8").read())
RACE_GROUPS = [[g, e, n] for g, n, e in _IG if g in ("brain", "quiz", "react", "board", "arcade")]
RACE = [[r[0], r[1], r[2], r[4], NUMS[r[0]]] for r in gamenum.index_games() if r[4] in [g[0] for g in RACE_GROUPS]]
HUB_CSS = LINK_CSS + '''
.gm{display:flex;align-items:center;gap:12px;width:100%;text-align:left;background:var(--soft);border:1px solid var(--line);border-radius:14px;padding:12px}
.gm .e{font-size:1.8rem}.gm b{display:block;font-family:var(--font-display);font-weight:400;font-size:1.25rem}
#gf{width:100%;border:0;display:block;min-height:200px;background:transparent}
.bar{display:flex;justify-content:space-between;align-items:center;gap:8px}.no{font-size:.72rem;color:var(--muted);font-weight:700;margin-left:4px}
.gh{font-family:var(--font-display);font-size:1.1rem;margin-top:6px}
.grp{border:1px solid var(--line);border-radius:14px;background:var(--surface)}.grp>summary{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:12px 14px;cursor:pointer;font-family:var(--font-display);font-size:1.15rem;list-style:none}.grp>summary::-webkit-details-marker{display:none}
.grp>summary::after{content:"▾";color:var(--muted);font-size:1rem;transition:transform .15s}.grp[open]>summary::after{transform:rotate(180deg)}.grp>summary .note{margin-left:auto}.grp .gl{display:grid;gap:8px;padding:0 10px 10px}input[type=search]{width:100%;background:var(--soft);color:var(--fg);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:inherit}
#rf{width:100%;border:0;display:block;min-height:300px;background:var(--bg)}.rwrap{position:relative}
#rcover{position:absolute;inset:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);display:flex;align-items:center;justify-content:center;text-align:center;font-family:var(--font-display);font-size:1.4rem;padding:16px;border-radius:12px}
#rcover.cd{font-size:5rem}.timer{font-family:var(--font-display);font-size:1.5rem;font-variant-numeric:tabular-nums}
.mirs{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}.mir{flex:none;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--surface);cursor:pointer}
.mir .mh{font-size:.78rem;font-weight:700;padding:3px 6px;white-space:nowrap;max-width:150px;overflow:hidden;text-overflow:ellipsis}.mir .mv{width:150px;height:250px;overflow:hidden;position:relative}
.mir iframe{width:360px;height:600px;border:0;transform:scale(.4166);transform-origin:0 0;pointer-events:none}.mir.big .mh{max-width:none}.mir.big .mv{width:300px;height:500px}.mir.big iframe{transform:scale(.8333)}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 11px;font-weight:700;font-size:.88rem}.chip.on{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.kick{border:1px solid var(--line);background:var(--surface);color:var(--bad);border-radius:999px;padding:2px 8px;font-size:.75rem;font-weight:700}
.tag{display:inline-block;border-radius:999px;padding:1px 8px;font-size:.75rem;font-weight:700;background:var(--soft);margin-left:4px}.mini{display:inline-flex;gap:4px;margin-left:6px}.mini button{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:2px 8px;font-size:.78rem}'''

HUB_BODY = '''  <div class="card"><div style="display:grid;gap:4px"><label class="lb" for="nm">이 기기 이름</label><input type="text" id="nm" maxlength="10"><div class="chips" id="nmc"></div></div></div>
  <div class="card" id="start">
    <p>QR로 <b>한 번만</b> 연결하면, 방장이 고른 게임이 모든 폰에서 함께 열려요. 게임을 바꿔도 다시 연결할 필요가 없어요.</p>
    <p class="note">폰(또는 PC)을 <b>같은 와이파이</b>나 한 폰의 <b>핫스팟</b>에 연결한 뒤 시작하세요.</p>
    <div class="row"><button class="btn" id="bh" type="button">📡 방 만들기</button><button class="btn ghost" id="bg" type="button">🔗 참가하기</button></div>
    <label class="note" style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="gst"> 🙋 손님으로 참가 (게임만 하고, 가족·친구 명단은 주고받지 않아요)</label>
  </div>
  <div class="card" id="hostbox" hidden>
    <b id="hstep">① 참가할 폰으로 이 QR을 찍어요</b>
    <canvas class="qr" id="qo" aria-label="초대 QR 코드"></canvas>
    <p class="note">참가할 폰의 <b>카메라 앱</b>으로 찍거나, 그 폰에서 이 화면을 열고 "참가하기 → 📷 QR 찍기"를 눌러요.</p>
    <b>② 참가한 폰에 뜬 답장 QR을 찍어요</b>
    <button class="btn" id="hscan" type="button">📷 답장 QR 찍기</button>
    <details><summary class="note">QR을 못 찍을 때 (PC 등): 코드로 주고받기</summary><div style="display:grid;gap:8px;margin-top:8px">
      <label class="lb" for="oc">초대 코드 (복사해서 상대에게 보내기)</label><textarea class="code" id="oc" readonly></textarea><button class="btn ghost sm" id="ocp" type="button">📋 초대 코드 복사</button>
      <label class="lb" for="ai">상대가 보낸 답장 코드 붙여넣기</label><textarea class="code" id="ai"></textarea><button class="btn ghost sm" id="ago" type="button">연결하기</button></div></details>
    <p class="note" id="hmsg"></p>
    <button class="btn ghost sm" id="hdone" type="button" hidden>그만 받고 게임 고르기</button>
  </div>
  <div class="card" id="guestbox" hidden>
    <div id="gjoin" style="display:grid;gap:10px"><b>방 만든 폰의 QR을 찍어요</b>
      <button class="btn" id="gscan" type="button">📷 QR 찍기</button>
      <details><summary class="note">QR을 못 찍을 때 (PC 등): 코드로 주고받기</summary><div style="display:grid;gap:8px;margin-top:8px">
        <label class="lb" for="oi">받은 초대 코드 붙여넣기</label><textarea class="code" id="oi"></textarea><button class="btn ghost sm" id="ogo" type="button">참가하기</button></div></details></div>
    <div id="gans" hidden style="display:grid;gap:10px"><b>방 만든 폰에서 이 답장 QR을 찍어 주세요</b>
      <canvas class="qr" id="qa" aria-label="답장 QR 코드"></canvas>
      <details><summary class="note">코드로 보내기 (PC 등)</summary><div style="display:grid;gap:8px;margin-top:8px"><textarea class="code" id="ac" readonly></textarea><button class="btn ghost sm" id="acp" type="button">📋 답장 코드 복사</button></div></details></div>
    <p class="note" id="gmsg"></p><button class="btn ghost sm" id="gre" type="button" hidden>🔄 처음부터 다시</button>
  </div>
  <details class="card" id="room" hidden open><summary class="bar"><b id="rsum">📶 연결된 기기</b></summary><div id="list" style="margin-top:6px"></div>
    <div class="row"><button class="btn ghost sm" id="buzz" type="button">📳 신호 보내기</button><button class="btn ghost sm" id="more" type="button" hidden>➕ 한 명 더 연결</button></div>
    <button class="btn ghost sm" id="pplb" type="button">📋 명단 주고받기 (가족·친구 이름)</button><button class="btn ghost sm" id="leave" type="button" style="color:var(--bad)">🔌 연결 끊기</button><div id="ppl"></div>
    <p class="note" id="rmsg" style="color:var(--bad)"></p><p class="note">연결된 동안은 화면이 꺼지지 않게 해요. 앱을 닫거나 화면이 오래 꺼지면 연결이 끊겨요.</p></details>
  <div class="card" id="pick" hidden><b>🎮 같이 할 게임 고르기</b><p class="note">묶음을 눌러 펼쳐요.</p><input type="search" id="gq" placeholder="게임 이름이나 번호(예: 225)로 찾기" autocomplete="off" aria-label="같이 하기 게임 찾기"><div id="glist" style="display:grid;gap:8px"></div>
    <details id="racebox" class="card" style="border-color:var(--accent)"><summary><b>🏁 동시 도전</b> <span class="note">혼자 하는 게임을 다 같이 동시에</span></summary>
      <p class="note" style="margin:6px 0">모두 각자 폰에서 같은 게임을 동시에 시작해요. 컴퓨터와 하는 게임은 각자 컴퓨터와 겨루고, 퍼즐·퀴즈는 <b>같은 문제</b>로 누가 먼저(또는 잘) 하는지 겨뤄요. 다른 사람 화면이 위에 작게 보여요.</p>
      <input type="search" id="rq" placeholder="게임 이름이나 번호(예: 12)로 찾기" autocomplete="off" aria-label="동시 도전 게임 찾기"><div id="rlist" style="display:grid;gap:8px;margin-top:8px"></div></details></div>
  <div class="card" id="wait" hidden><p class="center">방장이 게임을 고르고 있어요… 🎲</p></div>
  <div class="card" id="rstage" hidden><div class="bar"><b id="rname"></b><span class="timer" id="rtime">0:00.0</span></div>
    <div class="mirs" id="mirs"></div>
    <div id="rhost" class="row" hidden><button class="btn sm" id="rgo" type="button">▶ 시작</button><button class="btn ghost sm" id="ragain" type="button">🔁 새 문제로 다시</button></div>
    <div class="rwrap"><div id="rcover">준비 중…</div><iframe id="rf" title="동시 도전 게임"></iframe></div>
    <div class="row" id="rbtn"><button class="btn sm" id="rok" type="button">🏆 성공 · 이겼어요</button><button class="btn ghost sm" id="rno" type="button">😢 실패 · 졌어요</button></div>
    <div id="rres"></div><button class="btn ghost sm" id="rhome" type="button" hidden>🏠 다른 게임 고르기</button></div>
  <div class="card" id="stage" hidden><div class="bar"><b id="gname"></b><button class="btn ghost sm" id="home" type="button" hidden>🏠 게임 바꾸기</button></div><iframe id="gf" title="게임 화면" scrolling="no"></iframe></div>
  <div id="scan" hidden><p>QR 코드를 화면 가운데에 비춰 주세요</p><video id="vid" playsinline muted></video><button class="btn" id="scx" type="button">닫기</button></div>
  <div id="flash" hidden></div>'''

HUB_JS = QR_JS + CODEC_JS + r'''
const GAMES = ''' + _json.dumps(GAMES, ensure_ascii=False) + r''', HUB_GROUPS = ''' + _json.dumps(HUB_GROUPS, ensure_ascii=False) + r''';
const NUMS = ''' + _json.dumps({k: v for k, v in NUMS.items()}, ensure_ascii=False) + r''', RACE = ''' + _json.dumps(RACE, ensure_ascii=False) + r''', RACE_GROUPS = ''' + _json.dumps(RACE_GROUPS, ensure_ascii=False) + r''';
// ───── 상태 ─────
let S = Object.assign({ name: "" }, ld(KEY) || {});
if (!S.name) { const old = ld("link-test-v1"), mine = window.FAMILY && FAMILY.me ? FAMILY.me.get() : ""; S.name = mine || (old && old.name) || "기기" + ri(100, 999); sv(KEY, S); }
$("nm").value = S.name;
// 손님: 게임만 함께 하고 명단은 주고받지 않아요(이번 연결에서만, 저장 안 함)
let asGuest = false;
$("gst").onchange = () => { asGuest = $("gst").checked; };
function setName(v) { S.name = String(v || "").trim().slice(0, 10) || S.name; $("nm").value = S.name; sv(KEY, S); if (role === "guest") gsend({ t: "name", name: S.name, gst: asGuest }); else if (role === "host") roster(); nameChips(); }
$("nm").onchange = () => setName($("nm").value);
// ───── 가족·친구 명단 (공용 FAMILY·FRIENDS): 이름만 주고받고, 받은 쪽이 "추가"를 눌러야 저장돼요
const famL = () => window.FAMILY ? FAMILY.get() : [], frL = () => window.FRIENDS ? FRIENDS.get() : [];
const groupOf = n => famL().includes(n) ? "가족" : frL().includes(n) ? "친구" : "";
function nameChips() { const ns = [...famL(), ...frL()]; $("nmc").innerHTML = ns.slice(0, 20).map(n => `<button type="button" class="chip${n === S.name ? " on" : ""}" data-n="${esc(n)}">${esc(n)}</button>`).join(""); $("nmc").querySelectorAll("[data-n]").forEach(b => b.onclick = () => setName(b.dataset.n)); }
function addPeople(fam, fr) { if (!window.FAMILY) return; const F = famL(), R = frL(); fam.forEach(n => { if (!F.includes(n) && !R.includes(n) && F.length < 12) F.push(n); }); fr.forEach(n => { if (!F.includes(n) && !R.includes(n) && R.length < 30) R.push(n); }); FAMILY.set(F); FRIENDS.set(R); nameChips(); renderRoom(); }
const cleanNames = a => Array.isArray(a) ? [...new Set(a.filter(x => typeof x === "string").map(x => x.trim().slice(0, 8)).filter(Boolean))].slice(0, 30) : [];
let pplIn = { from: [], fam: [], fr: [] };
function gotPpl(m) {
  if (asGuest) return;
  const known = new Set([...famL(), ...frL()]), fam = cleanNames(m.fam).filter(n => !known.has(n)), fr = cleanNames(m.fr).filter(n => !known.has(n) && !fam.includes(n));
  if (!pplIn.from.includes(m.from)) pplIn.from.push(String(m.from || "").slice(0, 10));
  fam.forEach(n => { if (!pplIn.fam.includes(n)) pplIn.fam.push(n); }); fr.forEach(n => { if (!pplIn.fr.includes(n) && !pplIn.fam.includes(n)) pplIn.fr.push(n); });
  renderPpl();
}
function renderPpl() {
  const p = pplIn; if (!p.from.length) { $("ppl").innerHTML = ""; return; }
  $("ppl").innerHTML = `<div class="card" style="border-color:var(--accent);margin-top:8px"><b>📋 ${p.from.map(esc).join(", ")} 님이 명단을 보냈어요</b>`
    + (p.fam.length || p.fr.length ? `${p.fam.length ? `<div>👨‍👩‍👧 가족: ${p.fam.map(esc).join(", ")}</div>` : ""}${p.fr.length ? `<div>🧑‍🤝‍🧑 친구: ${p.fr.map(esc).join(", ")}</div>` : ""}<div class="row"><button class="btn sm" id="pplok" type="button">✅ 내 명단에 추가</button><button class="btn ghost sm" id="pplno" type="button">건너뛰기</button></div>`
      : '<div class="note">내 명단에 이미 다 있어요. 새로 추가할 이름이 없어요.</div><button class="btn ghost sm" id="pplno" type="button">닫기</button>') + "</div>";
  if ($("pplok")) $("pplok").onclick = () => { addPeople(p.fam, p.fr); pplIn = { from: [], fam: [], fr: [] }; renderPpl(); flash("✅ 명단에 추가했어요"); };
  $("pplno").onclick = () => { pplIn = { from: [], fam: [], fr: [] }; renderPpl(); };
}
$("pplb").onclick = () => { if (asGuest) return; const m = { t: "ppl", from: S.name, fam: famL(), fr: frL() }; if (!m.fam.length && !m.fr.length) { alert("보낼 가족·친구 명단이 아직 없어요. 시작 화면의 '가족 명단'에서 이름을 추가하거나, 아래 연결된 기기 옆의 가족/친구 버튼을 눌러 등록해 주세요."); return; }
  if (!confirm(`연결된 모든 기기에 내 가족 ${m.fam.length}명 · 친구 ${m.fr.length}명의 이름을 보낼까요? (이름만 보내요. 받는 쪽이 '추가'를 눌러야 저장돼요)`)) return;
  if (role === "host") peers.forEach(x => { if (!x.gst) send(x, m); }); else gsend(m); flash("📋 보냈어요"); };
$("list").addEventListener("click", e => { const kb = e.target.closest("[data-kick]"); if (kb && role === "host") { const p = peers.find(x => x.id === kb.dataset.kick); if (p && confirm(`${p.name}의 연결을 끊을까요?`)) { send(p, { t: "bye" }); setTimeout(() => { try { p.pc.close(); } catch (x) {} drop(p); }, 150); } return; }
  const g = e.target.closest("[data-gstp]"); if (g && role === "host") { const p = peers.find(x => x.id === g.dataset.gstp); if (p) { p.gst = true; roster(); } return; }
  const b = e.target.closest("[data-addf],[data-addr]"); if (!b) return; const n = String(b.dataset.addf || b.dataset.addr).slice(0, 8); if (b.dataset.addf) addPeople([n], []); else addPeople([], [n]); });
nameChips();
let role = null, myId = "host", pend = null, upl = null, roomList = [], game = null, gameReady = false, gq = [];
const peers = [];
const bc = ("BroadcastChannel" in window) ? new BroadcastChannel("fg-link") : null;
const note = (id, t) => { $(id).textContent = t; };
function copy(id) { const el = $(id); el.select(); try { navigator.clipboard.writeText(el.value).catch(() => document.execCommand("copy")); } catch (e) { try { document.execCommand("copy"); } catch (e2) {} } }
const canScan = () => "BarcodeDetector" in window && navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
async function scanQR(onCode) {
  if (!canScan()) { alert("이 브라우저는 화면 안에서 QR을 찍을 수 없어요. 폰의 카메라 앱으로 찍거나 아래 '코드로 주고받기'를 써 주세요."); return; }
  let st; try { st = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false }); } catch (e) { alert("카메라를 열 수 없어요. 카메라 권한을 허용해 주세요."); return; }
  const det = new BarcodeDetector({ formats: ["qr_code"] }), v = $("vid"); v.srcObject = st; $("scan").hidden = false; try { await v.play(); } catch (e) {}
  let done = false; const end = () => { done = true; st.getTracks().forEach(t => t.stop()); v.srcObject = null; $("scan").hidden = true; };
  $("scx").onclick = end;
  const loop = async () => { if (done) return; try { const r = await det.detect(v); for (const x of r) { const c = pickCode(x.rawValue); if (c) { end(); try { navigator.vibrate && navigator.vibrate(80); } catch (e) {} onCode(c); return; } } } catch (e) {} setTimeout(loop, 200); };
  loop();
}
function flash(t) { $("flash").textContent = t; $("flash").hidden = false; try { navigator.vibrate && navigator.vibrate([200, 100, 200]); } catch (e) {} setTimeout(() => { $("flash").hidden = true; }, 900); }
let wakeL = null;
async function wake() { try { if (role && "wakeLock" in navigator && document.visibilityState === "visible" && !wakeL) { wakeL = await navigator.wakeLock.request("screen"); wakeL.addEventListener("release", () => { wakeL = null; }); } } catch (e) {} }
document.addEventListener("visibilitychange", wake);
const openPeers = () => peers.filter(p => p.open);

// ───── 방 만들기 (방장) ─────
async function hostStart() {
  role = "host"; $("start").hidden = true; $("room").hidden = false; $("hscan").hidden = !canScan();
  if (bc) bc.onmessage = e => { const c = pickCode(e.data); if (c) takeAnswer(c); };
  setInterval(() => peers.forEach(p => { if (p.dc.readyState === "open") p.dc.send(JSON.stringify({ t: "ping", ts: performance.now() })); }), 2000);
  await newOffer(); roster(); showPick(); wake();
}
async function newOffer() {
  $("more").hidden = true; $("hostbox").hidden = false; $("hdone").hidden = !openPeers().length; note("hmsg", "초대 QR을 만드는 중…"); pend = null; $("oc").value = ""; $("qo").hidden = true;
  const pc = newPc(), dc = pc.createDataChannel("fg"), p = { id: mkId(), name: "연결 중…", pc, dc, rtt: null };
  try { await pc.setLocalDescription(await pc.createOffer()); await gathered(pc); p.code = pack("o", pc.localDescription.sdp); } catch (e) { note("hmsg", "⚠️ " + e.message); return; }
  p.ref = p.code.split("~")[2].slice(0, 4); pend = p;
  dc.onopen = () => { p.open = true; send(p, { t: "hi", id: p.id }); send(p, { t: "load", game }); if (R) send(p, { t: "race", R }); note("hmsg", ""); $("hostbox").hidden = true; $("more").hidden = false; flash("✅ 연결됐어요!"); roster(); };
  dc.onclose = () => drop(p);
  dc.onmessage = e => { let m; try { m = JSON.parse(e.data); } catch (x) { return; } hostMsg(p, m); };
  // 잠깐 끊김(disconnected)은 기다려요. 완전히 끊긴 경우(failed·closed·나가기)만 정리해요.
  pc.onconnectionstatechange = () => { const s = pc.connectionState; p.weak = s === "disconnected"; if (!p.open && s === "connecting") note("hmsg", "연결하는 중… 상대 기기와 신호를 맞추고 있어요.");
    if (s === "failed" && !p.open && !p.gone) { drop(p); newOffer().then(() => note("hmsg", "⚠️ 연결에 실패했어요. 새 초대 QR을 만들었어요. 참가할 기기에서 이 QR로 처음부터 다시 해 주세요.")); return; }
    if (s === "failed" || s === "closed") drop(p); else roster(); };
  QR.draw($("qo"), linkOf("j", p.code)); $("qo").hidden = false; $("oc").value = p.code; $("ai").value = ""; $("hstep").textContent = `① 참가할 폰으로 이 QR을 찍어요 (${openPeers().length + 1}번째 손님)`;
  note("hmsg", "");
}
async function takeAnswer(code) {
  const c = unpack(code); if (!c || c.t !== "a") return note("hmsg", "⚠️ 답장 코드가 아니에요. 참가한 폰에 뜬 '답장' QR을 찍어 주세요.");
  if (!pend) return; if (c.ref !== pend.ref) return note("hmsg", "⚠️ 지금 화면의 초대 QR로 만든 답장이 아니에요. 참가할 폰에서 위 QR을 다시 찍어 주세요.");
  const p = pend; pend = null; note("hmsg", "답장을 받았어요. 연결하는 중…");
  try { await p.pc.setRemoteDescription(unsdp(c)); } catch (e) { pend = p; return note("hmsg", "⚠️ 코드를 읽지 못했어요: " + e.message); }
  peers.push(p); roster();
  setTimeout(() => { if (!p.open && !p.gone) note("hmsg", "⚠️ 아직 연결이 안 돼요. 두 기기가 같은 와이파이인지 확인해 주세요. 조금 더 기다리거나, 안 되면 참가할 기기에서 '처음부터 다시'를 눌러 주세요."); }, 40000);
}
function drop(p) { if (p.gone) return; p.gone = true; p.open = false; const i = peers.indexOf(p); if (i >= 0) peers.splice(i, 1); roster(); }
const send = (p, m) => { if (p.dc.readyState === "open") p.dc.send(JSON.stringify(m)); };
const bcast = (m, except) => peers.forEach(p => { if (p !== except) send(p, m); });
function hostMsg(p, m) {
  if (m.t === "pong") { p.rtt = Math.round(performance.now() - m.ts); renderRoom(); }
  else if (m.t === "name") { if (m.gst) p.gst = true; const n0 = String(m.name || "").slice(0, 10) || "손님", used = [S.name, ...peers.filter(x => x !== p).map(x => x.name)]; let n = n0, k = 2; while (used.includes(n)) n = n0 + "-" + k++; p.name = n; roster(); }
  else if (m.t === "buzz") { flash("📳 " + p.name); bcast({ t: "buzz", from: p.name }, p); }
  else if (m.t === "bye") { try { p.pc.close(); } catch (e) {} drop(p); }
  else if (m.t === "g") route(p.id, m.to, m.d);
  else if (m.t === "rres" && R && m.rno === R.rno && R.ph === "run" && !R.res[p.id]) { R.res[p.id] = { ok: !!m.ok, ms: Math.max(0, +m.ms || 0) }; raceCheck(); pushR(); }
  else if (m.t === "snap") { gotSnap(p.id, m); const f = Object.assign({}, m, { from: p.id }); peers.forEach(x => { if (x !== p) send(x, f); }); }
  else if (m.t === "ppl" && !p.gst) { const f = { t: "ppl", from: p.name, fam: m.fam, fr: m.fr }; gotPpl(f); peers.forEach(x => { if (x !== p && !x.gst) send(x, f); }); }
}
// 게임 말 나눠 주기: to = "host"(방장 게임) / "*"(보낸 사람 빼고 모두) / 기기 id
function route(from, to, d) {
  if ((to === "host" || to === "*") && from !== "host") toFrame(from, d);
  if (to === "*") peers.forEach(p => { if (p.id !== from) send(p, { t: "g", from, d }); });
  else if (to !== "host") { const p = peers.find(x => x.id === to); if (p) send(p, { t: "g", from, d }); }
}
// 게임에 넘길 참가자 목록: 연결된 기기만(신호 약한 기기도 포함해 판이 깨지지 않게)
const players = () => roomList.filter(p => p.ok || p.weak).map(p => ({ id: p.id, name: p.nm }));
function roster() {
  if (role !== "host") return;
  roomList = [{ id: "host", nm: S.name, name: S.name + " (방장)", rtt: 0, ok: true }, ...peers.map(p => ({ id: p.id, nm: p.name, name: p.name, rtt: p.rtt, ok: !!p.open && !p.weak, weak: !!p.weak, gst: !!p.gst }))];
  bcast({ t: "room", list: roomList }); renderRoom(); toFrameRoster(); if (R) { const was = R.ph; raceCheck(); if (R.ph !== was) pushR(); else renderRace(); }
  note("rmsg", peers.some(p => p.weak) ? "⚠️ 신호가 약해진 기기가 있어요. 그 폰의 화면을 켜 두면 잠시 뒤 다시 붙어요. 1분 넘게 안 붙으면 ➕ 한 명 더 연결로 다시 들어오게 해 주세요." : "");
}

// ───── 참가하기 (손님) ─────
function guestStart() { role = "guest"; myId = null; $("start").hidden = true; $("guestbox").hidden = false; $("gscan").hidden = !canScan(); }
async function join(code) {
  const c = unpack(code); if (!c || c.t !== "o") return note("gmsg", "⚠️ 초대 코드가 아니에요. 방 만든 폰의 '초대' QR을 찍어 주세요.");
  guestStart(); note("gmsg", "답장 QR을 만드는 중…");
  const pc = newPc(); upl = { pc, dc: null };
  pc.ondatachannel = e => { const dc = upl.dc = e.channel;
    dc.onopen = () => { wake(); $("pplb").hidden = asGuest; gsend({ t: "name", name: S.name, gst: asGuest }); $("guestbox").hidden = true; $("room").hidden = false; $("wait").hidden = !!game; flash("✅ 연결됐어요!"); };
    dc.onmessage = e2 => { let m; try { m = JSON.parse(e2.data); } catch (x) { return; } guestMsg(m); };
    dc.onclose = () => { $("guestbox").hidden = false; $("gjoin").hidden = true; $("gans").hidden = true; $("gre").hidden = false; note("gmsg", "⚠️ 방과 연결이 끊겼어요. '처음부터 다시'를 누르고, 방 만든 폰에서 '➕ 한 명 더 연결'로 다시 들어와 주세요."); roomList = []; renderRoom(); loadGame(null); $("wait").hidden = true; };
  };
  pc.onconnectionstatechange = () => { const s = pc.connectionState; if (s === "failed") { note("gmsg", "⚠️ 연결이 안 돼요. 두 기기가 같은 와이파이인지 확인한 뒤, 방 만든 기기의 새 초대 QR로 처음부터 다시 해 주세요."); $("gre").hidden = false; } note("rmsg", s === "disconnected" ? "⚠️ 방장과 신호가 약해요. 잠시 기다리면 다시 붙어요." : ""); };
  // 손님은 방장 주소 없이 시작해 방장이 먼저 두드리기를 기다려요(답장을 늦게 옮겨도 먼저 포기하지 않게). 15초 뒤에도 안 붙으면 직접 시도해요.
  setTimeout(() => { if (!(upl.dc && upl.dc.readyState === "open")) c.c.forEach(([a, p], i) => pc.addIceCandidate({ candidate: `candidate:${i + 1} 1 udp ${2122260223 - i} ${a} ${p} typ host generation 0`, sdpMid: "0", sdpMLineIndex: 0 }).catch(() => {})); }, 15000);
  try { await pc.setRemoteDescription(unsdp(Object.assign({}, c, { c: [] }))); await pc.setLocalDescription(await pc.createAnswer()); await gathered(pc); const a = pack("a", pc.localDescription.sdp, c.u.slice(0, 4)); QR.draw($("qa"), linkOf("r", a)); $("ac").value = a; } catch (e) { return note("gmsg", "⚠️ " + e.message); }
  $("gjoin").hidden = true; $("gans").hidden = false; note("gmsg", "방 만든 폰이 이 QR을 찍으면(또는 답장 코드를 붙여 넣으면) 자동으로 연결돼요. 시간이 좀 걸려도 괜찮아요. 이 화면을 켜 둔 채 기다려 주세요.");
}
const gsend = m => { if (upl && upl.dc && upl.dc.readyState === "open") upl.dc.send(JSON.stringify(m)); };
function guestMsg(m) {
  if (m.t === "ping") gsend({ t: "pong", ts: m.ts });
  else if (m.t === "hi") myId = m.id;
  else if (m.t === "room") { roomList = m.list; renderRoom(); toFrameRoster(); renderRace(); }
  else if (m.t === "buzz") flash("📳 " + m.from);
  else if (m.t === "load") { loadGame(m.game); $("wait").hidden = !!m.game; }
  else if (m.t === "g") toFrame(m.from, m.d);
  else if (m.t === "race") onRace(m.R);
  else if (m.t === "snap") gotSnap(m.from, m);
  else if (m.t === "ppl") gotPpl(m);
  else if (m.t === "bye") { try { upl.pc.close(); } catch (e) {} if (upl.dc && upl.dc.onclose) upl.dc.onclose(); }
}
addEventListener("pagehide", () => { if (role === "guest") gsend({ t: "bye" }); else if (role === "host") bcast({ t: "bye" }); });

// ───── 게임 불러오기 · 게임과 말 주고받기 ─────
const frameWin = () => $("gf").contentWindow;
function loadGame(f) {
  const g = GAMES.find(x => x[0] === f) || null; if (game === (g && g[0])) return;
  game = g ? g[0] : null; gameReady = false; gq = [];
  $("stage").hidden = !g; $("gf").style.height = "200px"; $("gf").src = g ? g[0] : "about:blank"; $("gname").textContent = g ? g[1] + " " + g[2] : "";
  $("home").hidden = role !== "host"; if (role === "host") $("pick").hidden = !!g;
  if (g) { $("room").open = false; $("hostbox").hidden = true; }
}
const gmBtn = (f, e, t, d, n, kind) => `<button type="button" class="gm" data-${kind}="${f}"><span class="e">${e}</span><span><b>${esc(t)}<span class="no">#${n}</span></b><span class="note">${esc(d)}</span></span></button>`;
// 묶음은 접어 두고(처음엔 모두 접힘) 누르면 펼쳐요. 찾기 글자가 있으면 맞는 게임이 있는 묶음만 펼쳐서 보여 줘요. 펼친 묶음은 다시 그려도 그대로.
const openG = new Set();
const findHit = (q, title, num) => { if (!q) return true; const qn = /^#?\d+$/.test(q) ? +q.replace("#", "") : 0; return qn ? num === qn : title.toLowerCase().includes(q); };
function groupsHtml(groups, items, q, kind) {
  return groups.map(([k, e, n]) => { const rs = items(k); if (!rs.length) return ""; const key = kind + k, open = q || openG.has(key);
    return `<details class="grp" data-key="${key}"${open ? " open" : ""}><summary><span>${e} ${n}</span><span class="note">${rs.length}개</span></summary><div class="gl">${rs.join("")}</div></details>`; }).join("");
}
function bindGroups(el, q) { el.querySelectorAll("details.grp").forEach(d => d.addEventListener("toggle", () => { if (q()) return; d.open ? openG.add(d.dataset.key) : openG.delete(d.dataset.key); })); }
function showPick() {
  $("pick").hidden = !!game || !!R;
  const q = $("gq").value.trim().toLowerCase();
  $("glist").innerHTML = groupsHtml(HUB_GROUPS, k => GAMES.filter(g => g[4] === k && findHit(q, g[2], NUMS[g[0]])).map(g => gmBtn(g[0], g[1], g[2], g[3], NUMS[g[0]] || "", "g")), q, "g") || '<p class="note">찾는 게임이 없어요.</p>';
  $("glist").querySelectorAll("[data-g]").forEach(b => b.onclick = () => pickGame(b.dataset.g)); bindGroups($("glist"), () => $("gq").value.trim()); raceList();
}
function raceList() {
  const q = $("rq").value.trim().toLowerCase();
  $("rlist").innerHTML = groupsHtml(RACE_GROUPS, k => RACE.filter(r => r[3] === k && findHit(q, r[2], r[4])).map(r => gmBtn(r[0], r[1], r[2], "", r[4], "r")), q, "r") || '<p class="note">찾는 게임이 없어요.</p>';
  $("rlist").querySelectorAll("[data-r]").forEach(b => b.onclick = () => raceStart(b.dataset.r)); bindGroups($("rlist"), () => $("rq").value.trim());
}
$("gq").addEventListener("input", showPick);
$("rq").addEventListener("input", raceList);
function pickGame(f) { if (role !== "host") return; if (R) { R = null; bcast({ t: "race", R: null }); onRace(null); } loadGame(f); bcast({ t: "load", game: f }); }
const postF = m => { try { frameWin().postMessage(m, "*"); } catch (e) {} };
function toFrame(from, d) { const m = { fg: "msg", from, d }; if (gameReady) postF(m); else gq.push(m); }
function toFrameRoster() { if (gameReady) postF({ fg: "roster", players: players() }); }
addEventListener("message", e => {
  if (!game || e.source !== frameWin()) return; const m = e.data || {};
  if (m.fg === "ready") { gameReady = true; postF({ fg: "init", me: { id: role === "host" ? "host" : myId, name: S.name }, isHost: role === "host", players: players() }); gq.forEach(postF); gq = []; }
  else if (m.fg === "h") $("gf").style.height = Math.max(200, +m.h || 0) + "px";
  else if (m.fg === "send") { if (role === "host") route("host", m.to, m.d); else if (m.to === "host") gsend({ t: "g", to: "host", d: m.d }); else gsend({ t: "g", to: m.to, d: m.d }); }
});
// ───── 🏁 동시 도전: 기존 게임 페이지를 그대로 불러와 모두 동시에 시작 ─────
// 같은 문제가 나오게 모든 폰에 같은 씨앗(seed)의 Math.random을 넣고, 저장 기록은 이 판에서만 쓰는 임시 저장소로 바꿔요(평소 기록·오답 노트가 섞이지 않게).
// 1.5초마다 내 화면(main)을 찍어 다른 기기에 보내고, 받은 화면은 작은 창(mirror)에 보여 줘요. 그림판(canvas)은 작은 사진으로 바꿔 보내요.
let R = null, rCount = 0, rLoaded = 0, rRun = 0, rT0 = 0, rTick = null, rSnap = null, lastSnap = "", cssSent = 0, myRes = null, mirrors = {};
const fmtT = ms => { const t = Math.max(0, ms) / 1000, m = Math.floor(t / 60), x = (t % 60).toFixed(1); return m + ":" + (x < 10 ? "0" : "") + x; };
const raceGame = f => RACE.find(r => r[0] === f);
const raceShim = seed => `<script>(function(){var s=${seed}>>>0;Math.random=function(){s=(s+0x6D2B79F5)>>>0;var t=s;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296};var m={},P=Storage.prototype,own=Object.prototype.hasOwnProperty;P.getItem=function(k){k=String(k);return own.call(m,k)?m[k]:null};P.setItem=function(k,v){m[String(k)]=String(v)};P.removeItem=function(k){delete m[String(k)]};P.clear=function(){m={}};P.key=function(i){return Object.keys(m)[i]||null};try{Object.defineProperty(P,"length",{get:function(){return Object.keys(m).length},configurable:true})}catch(e){}window.__RACE=1})();<\/script>`;
function raceStart(f) { if (role !== "host") return; loadGame(null); bcast({ t: "load", game: null }); R = { rno: ++rCount, f,   // 판 번호는 계속 늘어나요(게임을 바꿔도 1로 돌아가지 않게: 예전 판의 화면·결과가 섞이지 않도록)
     seed: Math.floor(Math.random() * 2147483647), ph: "ready", res: {} }; pushR(); }
function pushR() { bcast({ t: "race", R }); onRace(R); }
function raceParts() { return roomList.filter(p => p.ok || p.weak).map(p => p.id); }
function raceCheck() { if (R && R.ph === "run" && raceParts().every(id => R.res[id])) R.ph = "done"; }
function onRace(r) {
  R = r; clearInterval(rTick); if (!r) { $("rstage").hidden = true; $("rf").srcdoc = ""; clearInterval(rSnap); rLoaded = rRun = 0; cssSent = 0; rT0 = 0; if (role === "host") showPick(); else $("wait").hidden = !!game; return; }
  $("pick").hidden = true; $("wait").hidden = true; $("rstage").hidden = false; $("room").open = false; $("hostbox").hidden = true;
  if (rLoaded !== r.rno) { rLoaded = r.rno; rRun = 0; rT0 = 0; myRes = null; $("rtime").textContent = "0:00.0"; lastSnap = ""; mirrors = {}; $("mirs").innerHTML = ""; const g = raceGame(r.f); $("rname").textContent = g ? `${g[1]} ${g[2]} #${g[4]}` : r.f;
    $("rcover").hidden = false; $("rcover").className = ""; $("rcover").textContent = "게임을 불러오는 중…";
    fetch(r.f).then(x => x.text()).then(t => { if (rLoaded !== r.rno) return; const base = location.href.split("#")[0].replace(/[^/]*$/, "");
      $("rf").srcdoc = t.replace(/<head>/i, `<head><base href="${base}">` + raceShim(r.seed)); if (!rRun) $("rcover").textContent = role === "host" ? "모두 준비되면 ▶ 시작을 눌러요" : "방장이 시작하면 3초 뒤 시작해요"; })
      .catch(() => { $("rcover").textContent = "⚠️ 게임을 불러오지 못했어요"; }); }
  if (r.ph === "run" && rRun !== r.rno) { rRun = r.rno; let n = 3; $("rcover").hidden = false; $("rcover").className = "cd"; $("rcover").textContent = n;
    const cd = setInterval(() => { n--; if (n > 0) { $("rcover").textContent = n; return; } clearInterval(cd); $("rcover").hidden = true; rT0 = performance.now(); clearInterval(rTick); rTick = setInterval(() => { if (!myRes) $("rtime").textContent = fmtT(performance.now() - rT0); }, 100); renderRace(); clearInterval(rSnap); rSnap = setInterval(snapMine, 1500); snapMine(); }, 1000); }
  if (r.ph === "run" && rT0 && !myRes) rTick = setInterval(() => { $("rtime").textContent = fmtT(performance.now() - rT0); }, 100);
  renderRace();
}
function renderRace() {
  const r = R; if (!r) return; const host = role === "host", me2 = host ? "host" : myId, nmOf = id => (roomList.find(p => p.id === id) || {}).nm || "?";
  $("rhost").hidden = !host; $("rgo").hidden = r.ph !== "ready"; $("ragain").hidden = r.ph === "ready"; $("rhome").hidden = !host;
  $("rbtn").hidden = r.ph !== "run" || !!r.res[me2] || !rT0;
  if (r.res[me2]) $("rtime").textContent = fmtT(r.res[me2].ms);
  const ids = raceParts(), order = ids.slice().sort((a, b) => { const x = r.res[a], y = r.res[b]; const k = v => !v ? 2 : v.ok ? 0 : 1; return k(x) - k(y) || ((x && x.ms) || 0) - ((y && y.ms) || 0); });
  let rank = 0; $("rres").innerHTML = r.ph === "ready" ? "" : `<div class="lb">${r.ph === "done" ? "🏁 결과" : "진행 상황"}</div>` + order.map(id => { const v = r.res[id]; if (v && v.ok) rank++;
    return `<div class="li"><span>${v && v.ok ? ["🥇", "🥈", "🥉"][rank - 1] || rank + "등" : v ? "😢" : "⏳"} ${esc(nmOf(id))}${id === me2 ? " (나)" : ""}</span><b>${v ? (v.ok ? "성공 " : "실패 ") + fmtT(v.ms) : "하는 중…"}</b></div>`; }).join("");
  Object.keys(mirrors).forEach(id => { const h = mirrors[id].el.querySelector(".mh"), v = r.res[id]; h.textContent = nmOf(id) + (v ? (v.ok ? " 🏆 " : " 😢 ") + fmtT(v.ms) : ""); });
}
function raceResult(ok) { if (!R || R.ph !== "run" || myRes || !rT0) return; myRes = { ok, ms: Math.round(performance.now() - rT0) }; clearInterval(rTick); snapMine();
  if (role === "host") { R.res.host = myRes; raceCheck(); pushR(); } else gsend({ t: "rres", rno: R.rno, ok, ms: myRes.ms }); renderRace(); }
function snapMine() {
  if (!R) return; let d; try { d = $("rf").contentDocument; } catch (e) { return; } if (!d || !d.body) return;
  const m = d.querySelector("main") || d.body, c = m.cloneNode(true); c.querySelectorAll("script").forEach(x => x.remove());
  const src = m.querySelectorAll("canvas"); c.querySelectorAll("canvas").forEach((cv, i) => { try { const s0 = src[i], w = Math.min(240, s0.width || 240), h = Math.round((s0.height || 1) * w / (s0.width || 1)), t = document.createElement("canvas"); t.width = w; t.height = h; t.getContext("2d").drawImage(s0, 0, 0, w, h); const img = d.createElement("img"); img.src = t.toDataURL("image/jpeg", .6); img.style.cssText = "width:100%;display:block"; cv.replaceWith(img); } catch (e) {} });
  let html = c.innerHTML; if (html.length > 150000) html = html.replace(/<img[^>]*>/g, ""); if (html === lastSnap) return; lastSnap = html;
  const msg = { t: "snap", rno: R.rno, html, css: cssSent === R.rno ? null : [...d.querySelectorAll("style,link[rel=stylesheet]")].map(x => x.outerHTML).join("") }; cssSent = R.rno;
  if (role === "host") bcast(Object.assign({ from: "host" }, msg)); else gsend(msg);
}
// 작은 화면 문서의 body 닫는 태그는 <\/ 로 써요. 그대로 쓰면 ship.py가 그 자리에 등록 코드를 끼워 넣어서 코드가 깨져요.
function gotSnap(from, m) {
  if (!R || m.rno !== R.rno || from === (role === "host" ? "host" : myId)) return; let mr = mirrors[from];
  if (!mr) { const el = document.createElement("div"); el.className = "mir"; el.innerHTML = '<div class="mh"></div><div class="mv"><iframe title="다른 사람 화면" tabindex="-1"></iframe></div>'; el.onclick = () => el.classList.toggle("big"); $("mirs").appendChild(el); mr = mirrors[from] = { el, css: "", html: "", ready: false }; }
  if (m.css) mr.css = m.css; mr.html = m.html; const fr = mr.el.querySelector("iframe");
  if (!mr.ready) { if (!mr.css) return; const base = location.href.split("#")[0].replace(/[^/]*$/, ""); fr.onload = () => { mr.ready = true; try { fr.contentDocument.querySelector("main").innerHTML = mr.html; } catch (e) {} }; fr.srcdoc = `<!doctype html><html><head><base href="${base}">${mr.css}<style>html,body{overflow:hidden}</style></head><body><main></main><\/body><\/html>`; }
  else { try { fr.contentDocument.querySelector("main").innerHTML = mr.html; } catch (e) {} }
  renderRace();
}
setInterval(() => { if (!R) return; try { const d = $("rf").contentDocument, m = d && (d.querySelector("main") || d.body); if (m) $("rf").style.height = Math.max(300, Math.ceil(m.getBoundingClientRect().bottom + 16)) + "px"; } catch (e) {} }, 600);
$("rok").onclick = () => raceResult(true); $("rno").onclick = () => raceResult(false);
$("rgo").onclick = () => { if (R && R.ph === "ready") { R.ph = "run"; pushR(); } };
$("ragain").onclick = () => { if (R && (R.ph === "done" || confirm("지금 판을 그만두고 새 문제로 다시 할까요?"))) raceStart(R.f); };
$("rhome").onclick = () => { if (R && R.ph === "run" && !confirm("동시 도전을 끝내고 다른 게임을 고를까요?")) return; R = null; bcast({ t: "race", R: null }); onRace(null); };
function renderRoom() {
  $("leave").textContent = role === "host" ? "🔌 방 닫기 (모두 연결 끊기)" : "🔌 연결 끊기 (방에서 나가기)";
  const n = roomList.filter(p => p.ok || p.weak).length; $("rsum").textContent = `📶 연결된 기기 ${n}대`;
  $("list").innerHTML = roomList.length ? roomList.map(p => `<div class="li"><span><span class="dot ${p.ok ? "ok" : "bad"}"></span>${esc(p.name)}${(p.id === myId && role === "guest") || (p.id === "host" && role === "host") ? " (나)" : p.gst ? '<span class="tag">🙋 손님</span>' : groupOf(p.nm) ? `<span class="tag">${groupOf(p.nm)}</span>` : window.FAMILY && p.ok && p.nm && !asGuest ? `<span class="mini"><button type="button" data-addf="${esc(p.nm)}">+가족</button><button type="button" data-addr="${esc(p.nm)}">+친구</button>${role === "host" ? `<button type="button" data-gstp="${p.id}">손님</button>` : ""}</span>` : ""}</span><span class="note">${role === "host" && p.id !== "host" ? `<button type="button" class="kick" data-kick="${p.id}">끊기</button> ` : ""}${p.id === "host" ? "" : p.weak ? "⚠️ 신호 약함 · 다시 붙는 중" : !p.ok ? "연결 중…" : p.rtt == null ? "…" : p.rtt + " ms"}</span></div>`).join("") : '<p class="note">연결된 기기가 없어요.</p>';
}

$("bh").onclick = hostStart;
$("bg").onclick = guestStart;
$("gscan").onclick = () => scanQR(join);
$("ogo").onclick = () => { const c = pickCode($("oi").value); c ? join(c) : note("gmsg", "⚠️ 초대 코드를 붙여 넣어 주세요."); };
$("hscan").onclick = () => scanQR(takeAnswer);
$("ago").onclick = () => { const c = pickCode($("ai").value); c ? takeAnswer(c) : note("hmsg", "⚠️ 답장 코드를 붙여 넣어 주세요."); };
$("ocp").onclick = () => copy("oc");
$("acp").onclick = () => copy("ac");
$("more").onclick = () => { $("room").open = true; newOffer(); };
$("hdone").onclick = () => { $("hostbox").hidden = true; $("more").hidden = false; };
$("gre").onclick = () => { location.href = location.href.split("#")[0]; };
$("home").onclick = () => { if (!confirm("지금 게임을 끝내고 다른 게임을 고를까요? (연결은 그대로예요)")) return; loadGame(null); bcast({ t: "load", game: null }); showPick(); };
// 🔌 연결 끊기: 방장은 방 닫기(모두 끊김), 손님은 방에서 나가기. 끊고 나면 처음 화면으로.
function leave() {
  if (role === "host") { if (!confirm("방을 닫을까요? 연결된 모든 기기의 연결이 끊겨요.")) return; bcast({ t: "bye" }); }
  else if (role === "guest") { if (!confirm("방에서 나갈까요? (방장 폰과의 연결이 끊겨요)")) return; gsend({ t: "bye" }); }
  role = null; setTimeout(() => { peers.forEach(p => { try { p.pc.close(); } catch (e) {} }); try { upl && upl.pc.close(); } catch (e) {} location.href = location.href.split("#")[0]; }, 200);
}
$("leave").onclick = leave;
window.fgLeaveCheck = () => !role || confirm("처음 화면으로 가면 같이 하기 연결이 끊겨요. 갈까요?");   // 🏠 처음으로 버튼(공용 스크립트)을 누를 때
$("buzz").onclick = () => { if (role === "host") bcast({ t: "buzz", from: S.name }); else gsend({ t: "buzz" }); flash("📳 보냈어요"); };

// 카메라 앱으로 QR을 찍어 이 화면이 열렸을 때: #j=초대(참가하기) / #r=답장(방 만든 화면으로 전달)
(() => {
  const h = location.hash, k = h.slice(1, 3), c = pickCode(h.slice(3)); if (!c) return;
  try { history.replaceState(null, "", location.href.split("#")[0]); } catch (e) {}
  if (k === "j=") join(c);
  else if (k === "r=") { guestStart(); $("gjoin").hidden = true; if (bc) bc.postMessage(c); note("gmsg", "✅ 답장을 방 만든 화면으로 보냈어요. 이 창을 닫고 방 만든 화면으로 돌아가 주세요. (자동으로 연결되지 않으면 방 만든 화면에서 '📷 답장 QR 찍기'를 써 주세요)"); }
})();
if (!("RTCPeerConnection" in window)) { $("start").innerHTML = '<p>⚠️ 이 브라우저는 기기끼리 연결하는 기능(WebRTC)을 지원하지 않아요. 크롬이나 삼성 인터넷 최신 버전에서 열어 주세요.</p>'; }
'''

make("out/play-together.html", "같이 하기", "👫", 205, "play-together-v1",
     "폰(또는 PC) 여러 대를 QR로 한 번만 연결하면, 방장이 고른 게임이 모든 기기에서 함께 열려요. 인터넷 서버를 거치지 않고 같은 와이파이(또는 핫스팟) 안에서 기기끼리 바로 주고받아요. 화면이 꺼지거나 앱을 닫으면 연결이 끊겨요. QR코드는 (주)덴소웨이브의 등록상표예요.",
     HUB_BODY, HUB_JS, HUB_CSS)

# ───────── 같이 하기 안에서 여는 게임들 (공통: NET)
NET_JS = r'''
// 같이 하기 화면과 말 주고받기. 혼자 열면 안내만 보여요.
const NET = (() => {
  const inHub = window.parent !== window, cb = { init: [], msg: [], roster: [] }; let info = null;
  const post = m => { try { window.parent.postMessage(m, "*"); } catch (e) {} };
  addEventListener("message", e => { if (e.source !== window.parent) return; const m = e.data || {};
    if (m.fg === "init") { info = m; cb.init.forEach(f => f(m)); } else if (m.fg === "roster" && info) { info.players = m.players; cb.roster.forEach(f => f(m.players)); } else if (m.fg === "msg") cb.msg.forEach(f => f(m.from, m.d)); });
  // 높이는 내용(main) 기준으로 재요. 문서 전체 높이는 화면 칸보다 작아지지 않아서, 짧은 게임으로 바꿔도 줄지 않거든요.
  const fit = () => { const m = document.querySelector("main"); post({ fg: "h", h: Math.ceil((m ? m.getBoundingClientRect().bottom : document.body.scrollHeight) + 12) }); };
  if (inHub) { document.documentElement.classList.add("inhub"); try { new ResizeObserver(fit).observe(document.body); } catch (e) { setInterval(fit, 500); } addEventListener("load", () => post({ fg: "ready" })); }
  return { inHub, get info() { return info; }, on: (k, f) => cb[k].push(f), send: (to, d) => post({ fg: "send", to, d }) };
})();
const nameOf = id => { const p = (NET.info && NET.info.players || []).find(x => x.id === id); return p ? p.name : "?"; };
if (!NET.inHub) document.addEventListener("DOMContentLoaded", () => { document.querySelector("main").insertAdjacentHTML("afterbegin", '<div class="card"><p>이 게임은 <b>👫 같이 하기</b> 화면 안에서 폰 여러 대를 연결해 해요.</p><a class="btn" style="text-align:center;text-decoration:none" href="play-together.html">같이 하기 열기</a></div>'); });
'''
NET_CSS = '''.inhub body{padding:4px 0 8px;background:transparent}.inhub h1{display:none}.inhub main{max-width:none}
.note{font-size:.85rem;color:var(--muted)}.btn.sm{padding:9px 14px;font-size:1rem}'''

# ── 틱택토: 방장 ⭕, 처음 들어온 기기 ❌, 나머지는 구경. 방장이 판정해 모두에게 보내요.
make("out/net-tictactoe.html", "틱택토 (같이 하기)", "⭕", 205, "net-tictactoe-v1",
     "가로, 세로, 대각선으로 3개를 먼저 이으면 이겨요. 방장이 ⭕, 처음 들어온 기기가 ❌이고 나머지는 구경해요. 판이 끝날 때마다 먼저 두는 쪽이 바뀌어요.",
     '''  <div class="card"><p class="center" id="gst"></p><div class="ttt" id="board"></div><p class="center note" id="score"></p><button class="btn ghost sm" id="again" type="button" hidden>새 판</button></div>''',
     NET_JS + r'''
const LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
const judge = b => { for (const l of LINES) if (b[l[0]] && b[l[0]] === b[l[1]] && b[l[0]] === b[l[2]]) return { w: b[l[0]], line: l }; return b.every(Boolean) ? { w: "D", line: [] } : null; };
let G = null, me = null, isHost = false;
function fresh() { G.b = Array(9).fill(""); G.win = null; G.line = []; G.turn = G.first; }
function pickX(ps) { const ids = ps.map(p => p.id); if (G.x && ids.includes(G.x)) return; const nx = ps.find(p => p.id !== "host"); G.x = nx ? nx.id : null; G.sc = { O: 0, X: 0, D: 0 }; fresh(); }
function push() { if (!isHost) return; G.nO = nameOf("host"); G.nX = G.x ? nameOf(G.x) : ""; NET.send("*", { t: "state", G }); render(); }
function move(i, mk) { if (!G.x || G.win || G.b[i] || G.turn !== mk || !(i >= 0 && i < 9)) return; G.b[i] = mk; const j = judge(G.b); if (j) { G.win = j.w; G.line = j.line; G.sc[j.w]++; } else G.turn = mk === "O" ? "X" : "O"; push(); }
function again() { G.first = G.first === "O" ? "X" : "O"; fresh(); push(); }
NET.on("init", m => { me = m.me.id; isHost = m.isHost; if (isHost) { G = { first: "O", x: null, sc: { O: 0, X: 0, D: 0 } }; fresh(); pickX(m.players); push(); } else NET.send("host", { t: "hello" }); render(); });
NET.on("roster", ps => { if (isHost && G) { pickX(ps); push(); } else render(); });
NET.on("msg", (from, d) => {
  if (isHost) { if (d.t === "hello") push(); else if (d.t === "move" && from === G.x) move(+d.i, "X"); else if (d.t === "again" && from === G.x && G.win) again(); }
  else if (d.t === "state") { G = d.G; render(); }
});
const myMark = () => !G ? null : isHost ? "O" : G.x === me ? "X" : null;
function render() {
  if (!G) { $("gst").textContent = "연결을 기다리는 중…"; return; } const mk = myMark();
  $("board").innerHTML = G.b.map((v, i) => `<button type="button" data-i="${i}" class="${G.line.includes(i) ? "w" : ""}" aria-label="${i + 1}번 칸">${v === "O" ? "⭕" : v === "X" ? "❌" : ""}</button>`).join("");
  $("gst").textContent = !G.x ? "상대가 들어오면 시작해요" : G.win === "D" ? "비겼어요!" : G.win ? `${G.win === "O" ? "⭕ " + G.nO : "❌ " + G.nX} 승리! 🎉` : !mk ? `구경 중 · ${G.turn === "O" ? "⭕ " + G.nO : "❌ " + G.nX} 차례` : G.turn === mk ? `내 차례예요 (${mk === "O" ? "⭕" : "❌"})` : "상대 차례예요…";
  $("score").textContent = G.x ? `⭕ ${G.nO} ${G.sc.O} : ${G.sc.X} ${G.nX} ❌ · 무승부 ${G.sc.D}` : "";
  $("again").hidden = !mk || !G.win;
  $("board").querySelectorAll("[data-i]").forEach(b => b.onclick = () => { if (!mk || G.turn !== mk || G.win) return; if (isHost) move(+b.dataset.i, "O"); else NET.send("host", { t: "move", i: +b.dataset.i }); });
}
$("again").onclick = () => { if (isHost) again(); else NET.send("host", { t: "again" }); };
render();
''', LINK_CSS + NET_CSS)

# ── 함선 찾기: 6×6 바다에 함선 3·2·2·1칸(시작 화면의 함선 찾기와 같은 규칙), 한 발씩 번갈아.
#   함선 위치는 각자 폰에만 보여요. 방장 폰이 판정을 위해 두 사람의 위치를 받아 두지만 화면에는 내 것만 그려요(끝나면 모두 공개).
make("out/net-ship-hunt.html", "함선 찾기 (같이 하기)", "🚢", 205, "net-ship-hunt-v1",
     "6×6 바다에 함선 4척(3·2·2·1칸)을 숨기고, 상대 바다를 한 발씩 번갈아 쏴요. 💥 명중, 🌊 빗나감, 함선 칸을 모두 맞히면 침몰! 상대 함선을 먼저 모두 침몰시키면 이겨요. 방장과 처음 들어온 기기가 대결하고 나머지는 구경해요.",
     '''  <div class="card"><p class="center" id="sst"></p>
    <div id="opp" hidden><div class="lb" id="oppl"></div><div class="sea" id="os"></div></div>
    <div><div class="lb" id="myl">내 바다</div><div class="sea" id="ms"></div></div>
    <div class="row" id="place"><button class="btn ghost sm" id="shuf" type="button">🔀 다시 배치</button><button class="btn sm" id="rdy" type="button">✅ 준비 완료</button></div>
    <p class="center note" id="sc"></p><button class="btn ghost sm" id="again" type="button" hidden>새 판</button></div>''',
     NET_JS + r'''
const N = 6, SHIPS = [3, 2, 2, 1];
function randomFleet() {
  for (let tries = 0; tries < 500; tries++) {
    const used = new Set(), out = []; let ok = true;
    for (const len of SHIPS) { let placed = false;
      for (let k = 0; k < 100 && !placed; k++) { const h = Math.random() < .5, r = ri(0, h ? N - 1 : N - len), c = ri(0, h ? N - len : N - 1), cells = Array.from({ length: len }, (_, i) => h ? r * N + c + i : (r + i) * N + c);
        const near = cells.some(x => { const y = Math.floor(x / N), z = x % N; for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) { const yy = y + dy, zz = z + dz; if (yy >= 0 && zz >= 0 && yy < N && zz < N && used.has(yy * N + zz)) return true; } return false; });
        if (!near) { cells.forEach(x => used.add(x)); out.push(cells); placed = true; } }
      if (!placed) { ok = false; break; } }
    if (ok) return out;
  }
  return [[0, 1, 2], [12, 13], [24, 25], [35]];
}
const validFleet = f => Array.isArray(f) && f.length === SHIPS.length && f.map(s => s.length).sort().join() === [...SHIPS].sort().join() && new Set(f.flat()).size === f.flat().length && f.flat().every(x => Number.isInteger(x) && x >= 0 && x < N * N);
let me = null, isHost = false, P = null, fleet = randomFleet(), sent = false;
const F = {};   // 방장만: 두 사람의 함선 위치 (판정용)
// 공개 상태 P: { ph: 대기·배치·대결·끝("wait"|"place"|"play"|"end"), a, b: 두 선수 id, ready, turn, shots: {선수: {칸: 1 명중 | 0 빗나감}}, sunk: {선수: [그 선수의 침몰한 함선]}, sc, reveal }
function newRound(keepScore) { const sc = keepScore && P ? P.sc : {}; P = { ph: P && P.b ? "place" : "wait", a: P ? P.a : "host", b: P ? P.b : null, ready: {}, turn: null, shots: {}, sunk: {}, sc, reveal: null }; Object.keys(F).forEach(k => delete F[k]); if (P.b) P.ph = "place"; }
function pickB(ps) { const ids = ps.map(p => p.id); if (P.b && ids.includes(P.b)) return false; const nx = ps.find(p => p.id !== "host"); P.b = nx ? nx.id : null; P.sc = {}; newRound(false); return true; }
function pushS() { if (!isHost) return; P.na = nameOf(P.a); P.nb = P.b ? nameOf(P.b) : ""; NET.send("*", { t: "state", P }); render(); }
function takeFleet(from, f) { if (P.ph !== "place" || (from !== P.a && from !== P.b) || !validFleet(f)) return; F[from] = f; P.ready[from] = 1; if (P.ready[P.a] && P.ready[P.b]) { P.ph = "play"; P.turn = Math.random() < .5 ? P.a : P.b; P.shots = { [P.a]: {}, [P.b]: {} }; P.sunk = { [P.a]: [], [P.b]: [] }; } pushS(); }
function shoot(from, c) {
  if (P.ph !== "play" || P.turn !== from || !(c >= 0 && c < N * N) || P.shots[from][c] !== undefined) return;
  const opp = from === P.a ? P.b : P.a, ship = F[opp].find(s => s.includes(c)); P.shots[from][c] = ship ? 1 : 0;
  if (ship && ship.every(x => P.shots[from][x] === 1)) P.sunk[opp].push(ship);
  if (P.sunk[opp].length === F[opp].length) { P.ph = "end"; P.win = from; P.sc[from] = (P.sc[from] || 0) + 1; P.reveal = { [P.a]: F[P.a], [P.b]: F[P.b] }; }
  else P.turn = opp;
  pushS();
}
NET.on("init", m => { me = m.me.id; isHost = m.isHost; if (isHost) { P = null; newRound(false); pickB(m.players); pushS(); } else NET.send("host", { t: "hello" }); render(); });
NET.on("roster", ps => { if (isHost && P) { if (pickB(ps)) { sent = false; } pushS(); } else render(); });
NET.on("msg", (from, d) => {
  if (isHost) { if (d.t === "hello") pushS(); else if (d.t === "fleet") takeFleet(from, d.f); else if (d.t === "unready" && P.ph === "place") { delete P.ready[from]; delete F[from]; pushS(); } else if (d.t === "shot") shoot(from, +d.c); else if (d.t === "again" && P.ph === "end" && (from === P.a || from === P.b)) { newRound(true); pushS(); } }
  else if (d.t === "state") { const was = P && P.ph; P = d.P; if (P.ph === "place" && was !== "place") sent = false; render(); }
});
const toHost = d => { if (isHost) NET_local(d); else NET.send("host", d); };
function NET_local(d) { if (d.t === "fleet") takeFleet("host", d.f); else if (d.t === "unready" && P.ph === "place") { delete P.ready.host; delete F.host; pushS(); } else if (d.t === "shot") shoot("host", +d.c); else if (d.t === "again" && P.ph === "end") { newRound(true); pushS(); } }
const amPlayer = () => P && (me === P.a || me === P.b);
const oppOf = id => id === P.a ? P.b : P.a;
// 칸 그리기: ships = 보이는 함선, shots = 이 바다에 떨어진 포탄, sunk = 침몰한 함선, click = 누를 수 있는지
function sea(el, ships, shots, sunk, click) {
  const shipAt = new Set((ships || []).flat()), sunkAt = new Set((sunk || []).flat());
  el.innerHTML = Array.from({ length: N * N }, (_, i) => { const s = shots ? shots[i] : undefined, on = shipAt.has(i), sk = sunkAt.has(i);
    return `<button type="button" data-c="${i}" class="${on ? "ship" : ""}${sk ? " sunk" : ""}"${click && s === undefined ? "" : " disabled"} aria-label="${Math.floor(i / N) + 1}행 ${i % N + 1}열">${s === 1 ? (sk ? "🔥" : "💥") : s === 0 ? "🌊" : on ? "🚢" : ""}</button>`; }).join("");
  if (click) el.querySelectorAll("[data-c]:not([disabled])").forEach(b => b.onclick = () => toHost({ t: "shot", c: +b.dataset.c }));
}
function render() {
  if (!P) { $("sst").textContent = "연결을 기다리는 중…"; $("place").hidden = true; return; }
  const pl = amPlayer(), opp = pl ? oppOf(me) : null, nm = id => id === me ? "나" : (id === P.a ? P.na : P.nb);
  $("place").hidden = !(pl && P.ph === "place"); $("again").hidden = !(pl && P.ph === "end");
  $("rdy").textContent = P.ready[me] ? "↩ 다시 고르기" : "✅ 준비 완료"; $("shuf").disabled = !!P.ready[me];
  if (P.ph === "wait") $("sst").textContent = "상대가 들어오면 시작해요";
  else if (P.ph === "place") $("sst").textContent = !pl ? `${P.na}·${P.nb} 님이 함선을 숨기는 중…` : P.ready[me] ? (P.ready[opp] ? "곧 시작해요!" : "준비 완료! 상대를 기다려요…") : `함선을 숨겨요. 마음에 들면 준비 완료!${P.ready[opp] ? " (상대는 준비됐어요)" : ""}`;
  else if (P.ph === "play") $("sst").textContent = !pl ? `구경 중 · ${nm(P.turn)} 차례` : P.turn === me ? "🎯 내 차례! 상대 바다를 눌러 쏘세요" : "상대가 조준하는 중…";
  else $("sst").textContent = P.win === me ? "🎉 이겼어요! 상대 함선을 모두 침몰시켰어요" : pl ? "😢 졌어요… 다음 판에 다시!" : `🎉 ${nm(P.win)} 승리!`;
  const end = P.ph === "end", rv = P.reveal || {};
  if (pl) {
    $("opp").hidden = P.ph === "place" || P.ph === "wait"; $("oppl").textContent = `상대 바다 (${nm(opp)}) · 남은 함선 ${SHIPS.length - ((P.sunk[opp] || []).length)}척`;
    if (!$("opp").hidden) sea($("os"), end ? rv[opp] : P.sunk[opp], P.shots[me], P.sunk[opp], P.ph === "play" && P.turn === me);
    $("myl").textContent = `내 바다 · 남은 함선 ${SHIPS.length - ((P.sunk[me] || []).length)}척`;
    sea($("ms"), fleet, P.shots[opp], P.sunk[me], false);
  } else {
    $("opp").hidden = P.ph !== "play" && !end; $("oppl").textContent = `${P.na}의 바다`; $("myl").textContent = P.nb ? `${P.nb}의 바다` : "";
    if (!$("opp").hidden) { sea($("os"), end ? rv[P.a] : P.sunk[P.a], P.shots[P.b], P.sunk[P.a], false); sea($("ms"), end ? rv[P.b] : P.sunk[P.b], P.shots[P.a], P.sunk[P.b], false); } else $("ms").innerHTML = "";
  }
  const sa = P.sc[P.a] || 0, sb = P.sc[P.b] || 0; $("sc").textContent = P.b ? `${P.na} ${sa} : ${sb} ${P.nb}` : "";
}
$("shuf").onclick = () => { if (P && P.ready[me]) return; fleet = randomFleet(); render(); };
$("rdy").onclick = () => { if (!amPlayer() || P.ph !== "place") return; if (P.ready[me]) toHost({ t: "unready" }); else toHost({ t: "fleet", f: fleet }); };
$("again").onclick = () => { fleet = randomFleet(); toHost({ t: "again" }); };
render();
''', LINK_CSS + NET_CSS + '''
.sea{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;width:min(100%,320px);margin:4px auto 0}
.sea button{aspect-ratio:1;border-radius:8px;border:1px solid var(--line);background:color-mix(in srgb,#3b82f6 14%,var(--surface));font-size:1.2rem;line-height:1;padding:0}
.sea button:not([disabled]){background:color-mix(in srgb,#3b82f6 26%,var(--surface))}.sea button.ship{background:color-mix(in srgb,var(--muted) 30%,var(--surface))}
.sea button.sunk{background:color-mix(in srgb,var(--bad) 30%,var(--surface))}.sea button[disabled]{cursor:default}''')
