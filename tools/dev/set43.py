# 명화 작가 퀴즈(art-quiz.html) + 명화 작가별 모음(art-gallery.html) 생성기. 원본 자료는 art_data.py.
#   실행: py set43.py → py ship.py '[["art-quiz.html","🖼️","명화 작가 퀴즈","…","quiz","culture"],["art-gallery.html","🎨","명화 작가별 모음","…","life","culture"]]'
#   퀴즈는 6가지 유형을 자동으로 만든다(같은 씨앗이라 다시 돌려도 같은 결과):
#     ① 작품 → 작가  ② 작가 → 작품(보기는 다른 작가의 작품)  ③ 작가 → 나라  ④ 작가 → 화풍·사조  ⑤ 작품 → 소장처  ⑥ 작품 3점 → 작가
#   등급은 작품의 유명 정도(1·2·3)가 그대로 초급·중급·고급. 그림 이미지는 쓰지 않는다(저작권·오프라인 용량 문제 없음).
import sys, json, random, os
sys.path.insert(0, ".")
from art_data import ARTISTS, ERAS
from art_wiki import WIKI, NO_IMAGE, tokens as _tokens
from mkquiz import make as make_quiz
from mkpage import make as make_page
H = "out/"
R = random.Random(20261123)

A = {a[0]: dict(id=a[0], name=a[1], en=a[2], years=a[3], country=a[4], style=a[5], era=a[6], bio=a[7], works=[dict(t=w[0], y=w[1], place=w[2], fame=w[3], kind=w[4]) for w in a[8]]) for a in ARTISTS}
ORDER = [a[0] for a in ARTISTS]
for a in A.values():
    for w in a["works"]: w["artist"] = a["id"]
ALLW = [w for a in A.values() for w in a["works"]]
NO_COUNTRY = {"bruegel", "vaneyck", "rubens", "elgreco", "chagall", "kandinsky", "whistler", "bosch"}   # 나라를 한 곳으로 말하기 애매한 작가는 '나라' 문제에서 뺀다
COUNTRIES = ["이탈리아", "프랑스", "네덜란드", "스페인", "독일", "영국", "노르웨이", "오스트리아", "일본", "한국(조선)", "멕시코", "미국", "벨기에"]
STYLES = sorted({a["style"] for a in A.values() if a["style"]})
PLACES = sorted({w["place"] for w in ALLW if w["place"] and " 등" not in w["place"]})
J = {"그림": "그림", "조각": "조각", "벽화": "벽화", "판화": "판화", "드로잉": "드로잉", "서화": "서화"}

# 같은 제목을 다른 작가도 남긴 작품: 이 작가들은 그 작품 문제의 오답(보기)에 넣지 않아요(정답이 둘이 되지 않게)
AMBIG = {"키스": {"munch"}, "해바라기": {"monet"}, "그네": {"renoir"}, "꿈": {"picasso"}, "피에타": {"titian", "delacroix", "vangogh"}, "바쿠스": {"titian", "rubens", "velazquez", "leonardo"},
         "최후의 심판": {"bosch", "rubens"}, "최후의 만찬": {"dali", "rubens"}, "성모 승천": {"rubens", "elgreco"}, "십자가에서 내려지심": {"rembrandt"}, "삼미신": {"raphael", "botticelli"},
         "세례자 성 요한": {"caravaggio", "raphael"}, "의심하는 도마": {"rembrandt"}, "샘": {"courbet"}, "마라의 죽음": {"munch"}, "풀밭 위의 점심 식사": {"monet", "picasso"},
         "아들을 잡아먹는 사투르누스": {"rubens"}, "생 라자르 역": {"manet"}, "카드놀이 하는 사람들": {"caravaggio"}, "거울을 보는 비너스": {"rubens"}, "씨 뿌리는 사람": {"vangogh"}}
CONFL = [{"산수화", "진경산수화"}, {"추상미술", "추상표현주의"}, {"인상주의", "후기 인상주의", "신인상주의"}]   # 서로 비슷해서 한 문제의 보기에 같이 두지 않는 화풍
data, level, seen = [], {}, set()
def add(q, ans, wrong, era, expl, lv):
    if q in seen: return
    wrong = [w for w in dict.fromkeys(wrong) if w != ans][:3]
    assert len(wrong) == 3, (q, ans, wrong)
    seen.add(q); data.append([q, ans, wrong, era, expl]); level[q] = lv

def pick_artists(a, lv, k=3, ban=()):
    """작가 a 의 오답 작가 k명. 쉬운 문제는 다른 시대에서, 어려운 문제는 같은 시대에서 골라요."""
    same = [x for x in ORDER if x != a["id"] and x not in ban and A[x]["era"] == a["era"]]
    diff = [x for x in ORDER if x != a["id"] and x not in ban and A[x]["era"] != a["era"]]
    famous = [x for x in diff if min(w["fame"] for w in A[x]["works"]) == 1] or diff
    n_same = {1: 0, 2: 1, 3: 2}[lv]
    out = R.sample(same, min(n_same, len(same)))
    pool = famous if lv == 1 else diff
    rest = [x for x in pool if x not in out]
    out += R.sample(rest, k - len(out))
    return [A[x]["name"] for x in out]

def info(a, w):
    s = f"{a['name']}({a['years']}·{a['country']})의 {J[w['kind']]}이에요. "
    s += f"{w['y']}에 그렸어요." if w["kind"] in ("그림", "벽화", "서화") else f"{w['y']}에 만들었어요."
    if w["place"]: s += f" {w['place']}에서 볼 수 있어요."
    return s

# ① 작품 → 작가
for a in A.values():
    for w in a["works"]:
        add(f"‘{w['t']}’의 작가는 누구일까요?", a["name"], pick_artists(a, w["fame"], ban=AMBIG.get(w["t"], ())), a["era"], info(a, w), w["fame"])

# ② 작가 → 작품 (작가마다 가장 유명한 작품 1개 + 작품이 3개 이상이면 다른 작품 1개)
for a in A.values():
    ws = sorted(a["works"], key=lambda w: w["fame"])
    picks = [ws[0]] + ([R.choice(ws[1:])] if len(ws) >= 3 else [])
    for w in picks:
        lv = w["fame"]
        others = [x for x in ORDER if x != a["id"] and not any(a["id"] in AMBIG.get(z["t"], ()) for z in A[x]["works"][:2])]
        same = [x for x in others if A[x]["era"] == a["era"]]
        sel = R.sample(same, min({1: 0, 2: 1, 3: 2}[lv], len(same)))
        sel += R.sample([x for x in others if x not in sel], 3 - len(sel))
        wrong = [R.choice(sorted(A[x]["works"], key=lambda z: z["fame"])[:2])["t"] for x in sel]
        add(f"다음 중 ‘{a['name']}’의 작품은?" if w is picks[0] else f"‘{a['name']}’의 작품으로 알려진 것은?", w["t"], wrong, a["era"], info(a, w), lv)

# ③ 작가 → 나라
for a in A.values():
    if a["id"] in NO_COUNTRY: continue
    lv = min(w["fame"] for w in a["works"])
    wrong = R.sample([c for c in COUNTRIES if c != a["country"]], 3)
    add(f"‘{a['name']}’은(는) 어느 나라의 화가일까요?", a["country"], wrong, a["era"], f"{a['name']}({a['en']}, {a['years']}) — {a['bio']}", lv)

# ④ 작가 → 화풍·사조
for a in A.values():
    if not a["style"]: continue
    lv = min(3, min(w["fame"] for w in a["works"]) + (1 if a["style"] in ("신인상주의", "소박파", "우키요에", "빈 분리파", "진경산수화", "산수화") else 0))
    ban = set().union(*[g for g in CONFL if a["style"] in g]) - {a["style"]}
    wrong = R.sample([s for s in STYLES if s != a["style"] and s not in ban], 3)
    add(f"화가 ‘{a['name']}’과(와) 가장 관련 깊은 화풍(사조)은?", a["style"], wrong, a["era"], f"{a['name']}은(는) '{a['style']}'의 대표적인 작가예요. {a['bio']}", lv)

# ⑤ 작품 → 소장처 (소장처가 한 곳으로 분명한 작품만)
for w in ALLW:
    if not w["place"] or " 등" in w["place"]: continue
    a = A[w["artist"]]; lv = max(2, w["fame"])
    city = lambda p: p[p.rfind("(") + 1:-1] if p.endswith(")") else p      # 같은 도시의 다른 미술관을 보기에 하나 넣어 그럴듯하게
    same = [p for p in PLACES if p != w["place"] and city(p) == city(w["place"])]
    wrong = R.sample(same, min(1, len(same))) if lv >= 2 else []
    wrong += R.sample([p for p in PLACES if p != w["place"] and p not in wrong], 3 - len(wrong))
    add(f"‘{w['t']}’ 작품은 어디에서 볼 수 있을까요?", w["place"], wrong, a["era"], f"{a['name']}의 {J[w['kind']]}이에요. {w['y']} 작품으로 {w['place']}에 있어요.", lv)

# ⑥ 작품 3점 → 작가 (작품이 3점 이상인 작가, 5점 이상이면 한 번 더)
for a in A.values():
    ws = a["works"]
    if len(ws) < 3: continue
    for rep in range(2 if len(ws) >= 5 else 1):
        sel = R.sample(ws, 3); lv = max(1, round(sum(w["fame"] for w in sel) / 3))
        q = "다음 작품들을 모두 남긴 작가는? " + " · ".join(f"‘{w['t']}’" for w in sel)
        add(q, a["name"], pick_artists(a, lv, ban=set().union(*[AMBIG.get(w["t"], set()) for w in sel])), a["era"], f"{a['name']}({a['years']}·{a['country']}) — {a['bio']}", lv)

# 등급 파일(qlevel/art-quiz.json): 문제 → 1·2·3
os.makedirs("qlevel", exist_ok=True)
json.dump(level, open("qlevel/art-quiz.json", "w", encoding="utf-8"), ensure_ascii=False)
cnt = {1: 0, 2: 0, 3: 0}
for v in level.values(): cnt[v] += 1
print("퀴즈 문제", len(data), "초급/중급/고급", cnt[1], cnt[2], cnt[3])
# ───────── 그림 모드(온라인·내장) 자료: 저작권이 끝난 작가의 작품 중 위키백과 대응이 있는 것만
alltitles = {w["t"] for w in ALLW}
missing = [t for t in WIKI if t not in alltitles]; assert not missing, "WIKI 대응표의 제목이 art_data 에 없어요: " + str(missing)
W, QI, G = {}, [], {}
for a in A.values():
    if a["id"] in NO_IMAGE: continue
    tk = _tokens(a["id"], a["en"], a["name"])
    for w in sorted(a["works"], key=lambda z: z["fame"]):
        if w["t"] not in WIKI: continue
        W[w["t"]] = {"k": WIKI[w["t"]], "a": a["id"], "t": tk, "kd": w["kind"]}
        G.setdefault(a["id"], w["t"])
        QI.append(["이 그림의 작가는 누구일까요?", a["name"], pick_artists(a, w["fame"], ban=AMBIG.get(w["t"], ())), a["era"], w["fame"], w["t"], f"‘{w['t']}’ — " + info(a, w), [w["y"], w["place"] or "", J[w["kind"]], a["name"], a["years"], a["country"]]])
DATA = {"W": W, "Q": QI, "G": G, "N": {a["name"]: a["id"] for a in A.values()}}
tpl = open("art_mode_tpl.js", encoding="utf-8").read(); assert "/*DATA*/null" in tpl
open("../../art-mode.js", "w", encoding="utf-8").write(tpl.replace("/*DATA*/null", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))))
# 오답 노트용 작은 모듈(명화 그림 찾기 정보만): wrong-notes.html 이 틀린 그림 문제의 그림을 다시 보여 줄 때 써요
_mt = open("art_media_tpl.js", encoding="utf-8").read(); assert "/*MEDIA*/null" in _mt
open("../../art-media.js", "w", encoding="utf-8").write(_mt.replace("/*MEDIA*/null", json.dumps(W, ensure_ascii=False, separators=(",", ":"))))
print("그림 모드: 작품 대응", len(W), "| 그림 문제", len(QI), "| 대표작 있는 작가", len(G), "| 그림 제외 작가", len(NO_IMAGE))
def hook(path):
    t = open(path, encoding="utf-8").read()
    if 'src="art-mode.js"' not in t:
        t = t.replace("</body>", '<script src="online.js"></script>\n<script src="art-mode.js" defer></script>\n</body>', 1); open(path, "w", encoding="utf-8").write(t)

make_quiz(H + "art-quiz.html", "명화 작가 퀴즈", "🖼️", 20, "art-quiz-best-v1",
          "세계 명화의 작가와 작품, 시대·화풍을 맞혀 보세요. 모든 작가와 대표작은 <a href=\"art-gallery.html\">🎨 명화 작가별 모음</a>에서 볼 수 있어요.", data, label="명화 작가 퀴즈")

# ───────── 명화 작가별 모음 화면
AR = [dict(id=a["id"], n=a["name"], e=a["en"], y=a["years"], c=a["country"], s=a["style"] or "", g=a["era"], b=a["bio"],
           l=min(w["fame"] for w in a["works"]), w=[[w["t"], w["y"], w["place"] or "", w["fame"], w["kind"]] for w in a["works"]]) for a in A.values()]
CSS = '''.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:.9rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}
.ar{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:6px}.ar h2{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}.ar .en{font-family:var(--font-body);font-size:.85rem;color:var(--muted)}
.ar .meta{display:flex;gap:6px;flex-wrap:wrap;font-size:.85rem;color:var(--muted)}.ar .tag{background:var(--soft);border-radius:999px;padding:2px 10px;color:var(--fg)}.ar .bio{font-size:.95rem;line-height:1.55}
.ar ul{margin:2px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:4px}.ar li{font-size:.95rem;line-height:1.4}.ar li small{display:block;color:var(--muted);font-size:.8rem}.ar li .st{color:#d89b00}
.era{font-family:var(--font-display);font-size:1.15rem;margin:8px 0 0;color:var(--accent)}#cnt{text-align:center}'''
BODY = '''  <div class="card"><div class="chips" id="eras"></div><div class="chips" id="lvs"></div><p class="muted" id="lvp"></p><input type="text" id="q" placeholder="작가·작품·나라·화풍 찾기 (예: 모네, 별, 프랑스, 인상주의)" aria-label="찾기"><p class="muted" id="cnt"></p><a class="btn" id="goq" href="art-quiz.html" style="text-align:center;text-decoration:none">🖼️ 명화 작가 퀴즈 풀기</a></div>
  <div id="list"></div>'''
JS = '''const AR = ''' + json.dumps(AR, ensure_ascii=False) + ''', ERAS = ''' + json.dumps(["전체"] + ERAS, ensure_ascii=False) + ''';
let era = ld(KEY + "-era") || "전체", lvf = +ld(KEY + "-lv") || 0; if (!(lvf >= 0 && lvf <= 3)) lvf = 0;
const LVN = ["모든 난이도", "🌱 초급", "🌿 중급", "🌳 고급"], LVD = ["", "누구나 아는 대표작(★)이 있는 작가예요.", "알려진 작품이 있는 작가예요.", "마니아가 좋아하는 작가예요."];
const norm = s => String(s).toLowerCase().replace(/\\s+/g, "");
function render() {
  const q = norm($("q").value), box = $("list"); let n = 0, w = 0, html = "", last = "";
  AR.forEach(a => {
    if (era !== "전체" && a.g !== era) return;
    if (lvf && a.l !== lvf) return;
    if (q && !norm([a.n, a.e, a.c, a.s, a.g, a.b, ...a.w.map(x => x[0])].join(" ")).includes(q)) return;
    if (a.g !== last) { last = a.g; html += `<p class="era">${esc(a.g)}</p>`; }
    n++; w += a.w.length;
    html += `<article class="ar"><h2>${esc(a.n)} <span class="en">${esc(a.e)}</span></h2><div class="meta"><span>${esc(a.y)}</span><span>· ${esc(a.c)}</span>${a.s ? `<span class="tag">${esc(a.s)}</span>` : ""}</div><p class="bio">${esc(a.b)}</p><ul>${a.w.map(x => `<li>${x[3] === 1 ? '<span class="st" aria-label="대표작">★</span> ' : ""}<b>${esc(x[0])}</b><small>${esc(x[1])} · ${esc(x[4])}${x[2] ? " · " + esc(x[2]) : ""}</small></li>`).join("")}</ul></article>`;
  });
  box.innerHTML = html || '<p class="muted center">찾는 작가가 없어요</p>';
  $("lvs").innerHTML = LVN.map((t, k) => `<button type="button" class="chip${k === lvf ? " on" : ""}" data-l="${k}">${t}${k ? ` <small>${AR.filter(a => a.l === k).length}</small>` : ""}</button>`).join(""); $("lvp").textContent = LVD[lvf];
  $("cnt").textContent = n ? `작가 ${n}명 · 작품 ${w}점 (★ = 누구나 아는 대표작)` : "";
}
$("eras").innerHTML = ERAS.map(e => `<button type="button" class="chip${e === era ? " on" : ""}" data-e="${esc(e)}">${esc(e)}</button>`).join("");
$("eras").addEventListener("click", ev => { const b = ev.target.closest("[data-e]"); if (!b) return; era = b.dataset.e; sv(KEY + "-era", era); $("eras").querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c === b)); render(); });
$("lvs").addEventListener("click", ev => { const b = ev.target.closest("[data-l]"); if (!b) return; lvf = +b.dataset.l; sv(KEY + "-lv", lvf); render(); });
$("q").addEventListener("input", render); render();'''
make_page(H + "art-gallery.html", "명화 작가별 모음", "🎨", 20, "art-gallery-v1",
          "그림 이미지는 담지 않고 작가와 대표작의 이름·연도·소장처만 정리했어요. 소장처와 제작 연도는 여러 자료와 달라질 수 있어요. 오래된 작품은 '경'(대략)으로 적었어요.",
          BODY, JS, CSS)
hook(H + "art-quiz.html"); hook(H + "art-gallery.html")
