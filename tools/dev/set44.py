# 클래식 작곡가·곡명 퀴즈(classic-quiz.html) + 작곡가별 모음(classic-gallery.html) 생성기. 원본 자료는 music_data.py.
#   실행: py set44.py → py ship.py '[["classic-quiz.html","🎼","클래식 작곡가 퀴즈","…","quiz","culture"],["classic-gallery.html","🎻","클래식 작곡가별 모음","…","life","culture"]]'
#   퀴즈 유형: ① 곡 → 작곡가 ② 작곡가 → 곡 ③ 작곡가 → 나라 ④ 작곡가 → 시대 ⑤ 곡 → 갈래 ⑥ 곡 3개 → 작곡가
#   등급은 곡의 유명 정도(1·2·3)가 그대로 초급·중급·고급. 같은 씨앗이라 다시 돌려도 같은 결과.
import sys, json, random, os, re
sys.path.insert(0, ".")
from music_data import COMPOSERS, ERAS, GENRES, AMBIG, NO_COUNTRY, NO_ERA
from mkquiz import make as make_quiz
from mkpage import make as make_page
from music_audio import AUDIO
H = "out/"
R = random.Random(20261124)
C = {c[0]: dict(id=c[0], name=c[1], en=c[2], years=c[3], country=c[4], era=c[5], bio=c[6], works=[dict(t=w[0], y=w[1], g=w[2], fame=w[3]) for w in c[7]]) for c in COMPOSERS}
ORDER = [c[0] for c in COMPOSERS]
for c in C.values():
    for w in c["works"]: w["comp"] = c["id"]
ALLW = [w for c in C.values() for w in c["works"]]
titles = [w["t"] for w in ALLW]; assert len(titles) == len(set(titles)), "곡 제목이 겹쳐요: " + str([t for t in titles if titles.count(t) > 1])
COUNTRIES = sorted({c["country"] for c in C.values()})
# 갈래 문제에서 한 보기에 같이 두지 않는 쌍(둘 다 맞을 수 있어서)
GEN_BAN = {"관현악곡": {"행진곡·무곡"}, "교향곡": {"관현악곡"}, "협주곡": {"관현악곡"}, "발레 음악": {"관현악곡"}, "행진곡·무곡": {"관현악곡", "피아노 독주곡"}, "오페라": {"가곡·성악곡"}, "가곡·성악곡": {"오페라", "종교 음악"}, "종교 음악": {"가곡·성악곡"}}
GEN_EXTRA = {"윌리엄 텔 서곡": {"오페라"}, "발퀴레의 기행": {"오페라"}, "왕벌의 비행": {"오페라", "행진곡·무곡"}, "G선상의 아리아": {"가곡·성악곡"}, "백조(동물의 사육제 중)": {"실내악"}, "아베 마리아(엘렌의 노래 3번)": {"종교 음악"}}
data, level, seen = [], {}, set()
def add(q, ans, wrong, era, expl, lv):
    if q in seen: return
    wrong = [w for w in dict.fromkeys(wrong) if w != ans][:3]
    assert len(wrong) == 3, (q, ans, wrong)
    seen.add(q); data.append([q, ans, wrong, era, expl]); level[q] = lv
def pick(a, lv, ban=(), k=3):
    """오답 작곡가 k명. 쉬운 문제는 다른 시대, 어려운 문제는 같은 시대에서 더 골라요."""
    same = [x for x in ORDER if x != a["id"] and x not in ban and C[x]["era"] == a["era"]]
    diff = [x for x in ORDER if x != a["id"] and x not in ban and C[x]["era"] != a["era"]]
    famous = [x for x in diff if min(w["fame"] for w in C[x]["works"]) == 1] or diff
    out = R.sample(same, min({1: 0, 2: 1, 3: 2}[lv], len(same)))
    out += R.sample([x for x in (famous if lv == 1 else diff) if x not in out], k - len(out))
    return [C[x]["name"] for x in out]
def info(a, w): return f"{a['name']}({a['years']}·{a['country']})의 {w['g']}이에요. {w['y']}에 만들었어요."

for a in C.values():                                                    # ① 곡 → 작곡가
    for w in a["works"]:
        add(f"‘{w['t']}’의 작곡가는 누구일까요?", a["name"], pick(a, w["fame"], ban=AMBIG.get(w["t"], ())), a["era"], info(a, w), w["fame"])
for a in C.values():                                                    # ② 작곡가 → 곡
    ws = sorted(a["works"], key=lambda w: w["fame"]); picks = [ws[0]] + ([R.choice(ws[1:])] if len(ws) >= 3 else [])
    for w in picks:
        lv = w["fame"]; others = [x for x in ORDER if x != a["id"] and not any(a["id"] in AMBIG.get(z["t"], ()) for z in C[x]["works"][:2]) and a["id"] not in AMBIG.get(w["t"], ())]
        same = [x for x in others if C[x]["era"] == a["era"]]; sel = R.sample(same, min({1: 0, 2: 1, 3: 2}[lv], len(same)))
        sel += R.sample([x for x in others if x not in sel], 3 - len(sel))
        wrong = [R.choice(sorted(C[x]["works"], key=lambda z: z["fame"])[:2])["t"] for x in sel]
        add(f"다음 중 ‘{a['name']}’의 작품은?" if w is picks[0] else f"‘{a['name']}’의 작품으로 알려진 것은?", w["t"], wrong, a["era"], info(a, w), lv)
for a in C.values():                                                    # ③ 작곡가 → 나라
    if a["id"] in NO_COUNTRY: continue
    lv = min(w["fame"] for w in a["works"])
    add(f"‘{a['name']}’은(는) 어느 나라의 작곡가일까요?", a["country"], R.sample([c for c in COUNTRIES if c != a["country"]], 3), a["era"], f"{a['name']}({a['en']}, {a['years']}) — {a['bio']}", lv)
for a in C.values():                                                    # ④ 작곡가 → 시대
    if a["id"] in NO_ERA: continue
    lv = min(3, min(w["fame"] for w in a["works"]) + (1 if a["era"] in ("국민악파",) else 0))
    add(f"작곡가 ‘{a['name']}’이(가) 속한 음악사 시대는?", a["era"], R.sample([e for e in ERAS if e != a["era"]], 3), a["era"], f"{a['name']}({a['years']}) — {a['bio']}", lv)
for a in C.values():                                                    # ⑤ 곡 → 갈래
    for w in a["works"]:
        ban = set(GEN_BAN.get(w["g"], ())) | GEN_EXTRA.get(w["t"], set())
        add(f"‘{w['t']}’은(는) 어떤 갈래의 음악일까요?", w["g"], R.sample([g for g in GENRES if g != w["g"] and g not in ban], 3), a["era"], f"{a['name']}의 곡이에요. {w['y']}에 만들었어요.", max(2, w["fame"]))
for a in C.values():                                                    # ⑥ 곡 3개 → 작곡가
    ws = a["works"]
    if len(ws) < 3: continue
    for rep in range(2 if len(ws) >= 6 else 1):
        sel = R.sample(ws, 3); lv = max(1, round(sum(w["fame"] for w in sel) / 3))
        add("다음 곡들을 모두 남긴 작곡가는? " + " · ".join(f"‘{w['t']}’" for w in sel), a["name"], pick(a, lv, ban=set().union(*[AMBIG.get(w["t"], set()) for w in sel])), a["era"], f"{a['name']}({a['years']}·{a['country']}) — {a['bio']}", lv)

os.makedirs("qlevel", exist_ok=True)
json.dump(level, open("qlevel/classic-quiz.json", "w", encoding="utf-8"), ensure_ascii=False)
cnt = {1: 0, 2: 0, 3: 0}
for v in level.values(): cnt[v] += 1
print("퀴즈 문제", len(data), "초급/중급/고급", cnt[1], cnt[2], cnt[3])
make_quiz(H + "classic-quiz.html", "클래식 작곡가 퀴즈", "🎼", 280, "classic-quiz-best-v1",
          "클래식 작곡가와 곡, 시대를 맞혀 보세요. 모든 작곡가와 대표곡은 <a href=\"classic-gallery.html\">🎻 클래식 작곡가별 모음</a>에서 볼 수 있어요.", data, label="클래식 작곡가 퀴즈")

# ───────── 작곡가별 모음 화면 (명화 작가별 모음과 같은 모양)
AR = [dict(id=a["id"], n=a["name"], e=a["en"], y=a["years"], c=a["country"], g=a["era"], b=a["bio"], l=min(w["fame"] for w in a["works"]), w=[[w["t"], w["y"], w["g"], w["fame"]] for w in a["works"]]) for a in C.values()]
src = open("set43.py", encoding="utf-8").read()
CSS = re.search(r"CSS = '''(.*?)'''", src, re.S).group(1)
BODY = '''  <div class="card"><div class="chips" id="eras"></div><div class="chips" id="lvs"></div><p class="muted" id="lvp"></p><input type="text" id="q" placeholder="작곡가·곡·나라·갈래 찾기 (예: 모차르트, 운명, 독일, 오페라)" aria-label="찾기"><p class="muted" id="cnt"></p><a class="btn" id="goq" href="classic-quiz.html" style="text-align:center;text-decoration:none">🎼 클래식 작곡가 퀴즈 풀기</a></div>
  <div id="list"></div>'''
JS = '''const AR = ''' + json.dumps(AR, ensure_ascii=False) + ''', ERAS = ''' + json.dumps(["전체"] + ERAS, ensure_ascii=False) + ''';
let era = ld(KEY + "-era") || "전체", lvf = +ld(KEY + "-lv") || 0; if (!(lvf >= 0 && lvf <= 3)) lvf = 0;
const LVN = ["모든 난이도", "🌱 초급", "🌿 중급", "🌳 고급"], LVD = ["", "누구나 아는 대표곡(★)이 있는 작곡가예요.", "알려진 곡이 있는 작곡가예요.", "마니아가 좋아하는 작곡가예요."];
const norm = s => String(s).toLowerCase().replace(/\\s+/g, "");
function render() {
  const q = norm($("q").value), box = $("list"); let n = 0, w = 0, html = "", last = "";
  AR.forEach(a => {
    if (era !== "전체" && a.g !== era) return;
    if (lvf && a.l !== lvf) return;
    if (q && !norm([a.n, a.e, a.c, a.g, a.b, ...a.w.map(x => x[0] + x[2])].join(" ")).includes(q)) return;
    if (a.g !== last) { last = a.g; html += `<p class="era">${esc(a.g)}</p>`; }
    n++; w += a.w.length;
    html += `<article class="ar"><h2>${esc(a.n)} <span class="en">${esc(a.e)}</span></h2><div class="meta"><span>${esc(a.y)}</span><span>· ${esc(a.c)}</span></div><p class="bio">${esc(a.b)}</p><ul>${a.w.map(x => `<li>${x[3] === 1 ? '<span class="st" aria-label="대표곡">★</span> ' : ""}<b>${esc(x[0])}</b><small>${esc(x[1])} · ${esc(x[2])}</small></li>`).join("")}</ul></article>`;
  });
  box.innerHTML = html || '<p class="muted center">찾는 작곡가가 없어요</p>';
  $("lvs").innerHTML = LVN.map((t, k) => `<button type="button" class="chip${k === lvf ? " on" : ""}" data-l="${k}">${t}${k ? ` <small>${AR.filter(a => a.l === k).length}</small>` : ""}</button>`).join(""); $("lvp").textContent = LVD[lvf];
  $("cnt").textContent = n ? `작곡가 ${n}명 · 곡 ${w}개 (★ = 누구나 아는 대표곡)` : "";
}
$("eras").innerHTML = ERAS.map(e => `<button type="button" class="chip${e === era ? " on" : ""}" data-e="${esc(e)}">${esc(e)}</button>`).join("");
$("eras").addEventListener("click", ev => { const b = ev.target.closest("[data-e]"); if (!b) return; era = b.dataset.e; sv(KEY + "-era", era); $("eras").querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c === b)); render(); });
$("lvs").addEventListener("click", ev => { const b = ev.target.closest("[data-l]"); if (!b) return; lvf = +b.dataset.l; sv(KEY + "-lv", lvf); render(); });
$("q").addEventListener("input", render); render();'''
make_page(H + "classic-gallery.html", "클래식 작곡가별 모음", "🎻", 280, "classic-gallery-v1",
          "작곡가와 대표곡의 이름·작곡 연도·갈래를 정리했어요. 작곡 연도는 자료마다 조금 다를 수 있어요(초연·출판 연도와 다를 수 있어요).", BODY, JS, CSS)

# ───────── 듣고 맞히기 모드(classic-mode.js) 만들기 + 두 화면에 끼우기
_pp = os.environ.get("PICK_FILE") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "music_pick.json")
_pk = json.load(open(_pp, encoding="utf-8")) if os.path.exists(_pp) else {}
PICK = {t: [x["f"] for x in v] for t, v in _pk.items() if t in AUDIO}   # 음질 선별을 통과한 곡만(파일 이름 목록, 음원 파일은 저장소에 없음)
W = {w["t"]: [C[w["comp"]]["name"], w["y"], w["g"], C[w["comp"]]["era"], w["fame"], C[w["comp"]]["country"], w["comp"]] for w in ALLW}
DATA = {"W": W, "C": [[c["name"], c["era"], c["id"]] for c in C.values()], "AMBIG": {t: sorted(s) for t, s in AMBIG.items()},
        "P": PICK}
tpl = open("classic_mode_tpl.js", encoding="utf-8").read(); assert "/*DATA*/null" in tpl
open("../../classic-mode.js", "w", encoding="utf-8").write(tpl.replace("/*DATA*/null", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))))
# 오답 노트용 작은 모듈(곡별 음원 이름만): wrong-notes.html 이 틀린 듣기 문제의 소리를 다시 들려줄 때 써요
_mt = open("classic_media_tpl.js", encoding="utf-8").read(); assert "/*MEDIA*/null" in _mt
open("../../classic-media.js", "w", encoding="utf-8").write(_mt.replace("/*MEDIA*/null", json.dumps(DATA["P"], ensure_ascii=False, separators=(",", ":"))))
def hook(path):
    t = open(path, encoding="utf-8").read()
    if 'src="classic-mode.js"' not in t:
        t = t.replace("</body>", '<script src="online.js"></script>\n<script src="classic-mode.js" defer></script>\n</body>', 1); open(path, "w", encoding="utf-8").write(t)
hook(H + "classic-quiz.html"); hook(H + "classic-gallery.html")
print("듣기 모드 자료: 곡", len(W))
