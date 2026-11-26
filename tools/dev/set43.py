# 명화 작가 퀴즈(art-quiz.html) + 명화 작가별 모음(art-gallery.html) 생성기. 원본 자료는 art_data.py.
#   실행: py set43.py → py ship.py '[["art-quiz.html","🖼️","명화 작가 퀴즈","…","quiz","culture"],["art-gallery.html","🎨","명화 작가별 모음","…","life","culture"]]'
#   퀴즈는 6가지 유형을 자동으로 만든다(같은 씨앗이라 다시 돌려도 같은 결과):
#     ① 작품 → 작가  ② 작가 → 작품(보기는 다른 작가의 작품)  ③ 작가 → 나라  ④ 작가 → 화풍·사조  ⑤ 작품 → 소장처  ⑥ 작품 3점 → 작가
#   등급은 작품의 유명 정도(1·2·3)가 그대로 초급·중급·고급. 그림 이미지는 쓰지 않는다(저작권·오프라인 용량 문제 없음).
import sys, json, random, os
sys.path.insert(0, ".")
from art_data import ARTISTS, ERAS, WEST_ERAS, KOREA_ERAS, EAST_ERAS, SET_OF, HO, HO_EASY, PERIOD, KOREA_TRIVIA, EAST_TRIVIA
from art_wiki import WIKI, NO_IMAGE, COMMONS_Q, tokens as _tokens
from mkquiz import make as make_quiz
from mkpage import make as make_page
H = "out/"
R = random.Random(20261123)

ALLA = {a[0]: dict(id=a[0], name=a[1], en=a[2], years=a[3], country=a[4], style=a[5], era=a[6], bio=a[7], works=[dict(t=w[0], y=w[1], place=w[2], fame=w[3], kind=w[4]) for w in a[8]]) for a in ARTISTS}
for a in ALLA.values():
    a["set"] = SET_OF[a["id"]]; a["ho"] = HO.get(a["id"]); a["period"] = PERIOD.get(a["id"])
    for w in a["works"]: w["artist"] = a["id"]
A, ORDER = ALLA, [a[0] for a in ARTISTS]
ALLW = [w for a in A.values() for w in a["works"]]
NO_COUNTRY = {"bruegel", "vaneyck", "rubens", "elgreco", "chagall", "kandinsky", "whistler", "bosch"}   # 나라를 한 곳으로 말하기 애매한 작가는 '나라' 문제에서 뺀다
COUNTRIES = ["이탈리아", "프랑스", "네덜란드", "스페인", "독일", "영국", "노르웨이", "오스트리아", "일본", "한국(조선)", "멕시코", "미국", "벨기에"]
STYLES = sorted({a["style"] for a in A.values() if a["style"]})
PLACES = sorted({w["place"] for w in ALLW if w["place"] and " 등" not in w["place"]})
J = {"설치": "설치 작품", "그림": "그림", "조각": "조각", "벽화": "벽화", "판화": "판화", "드로잉": "드로잉", "서화": "서화"}

# 같은 제목을 다른 작가도 남긴 작품: 이 작가들은 그 작품 문제의 오답(보기)에 넣지 않아요(정답이 둘이 되지 않게)
AMBIG = {"키스": {"munch"}, "해바라기": {"monet"}, "그네": {"renoir"}, "꿈": {"picasso"}, "피에타": {"titian", "delacroix", "vangogh"}, "바쿠스": {"titian", "rubens", "velazquez", "leonardo"},
         "최후의 심판": {"bosch", "rubens"}, "최후의 만찬": {"dali", "rubens"}, "성모 승천": {"rubens", "elgreco"}, "십자가에서 내려지심": {"rembrandt"}, "삼미신": {"raphael", "botticelli"},
         "세례자 성 요한": {"caravaggio", "raphael"}, "의심하는 도마": {"rembrandt"}, "샘": {"courbet"}, "마라의 죽음": {"munch"}, "풀밭 위의 점심 식사": {"monet", "picasso"},
         "아들을 잡아먹는 사투르누스": {"rubens"}, "생 라자르 역": {"manet"}, "카드놀이 하는 사람들": {"caravaggio"}, "거울을 보는 비너스": {"rubens"}, "씨 뿌리는 사람": {"vangogh"}}
# 흔한 제목(여러 화가가 같은 제목으로 그린 것): 다른 화가 문제의 오답 보기와 소장처 문제에 쓰지 않아요
NODIST = {"자화상", "묵란도", "달마도", "새우", "까치", "황소", "초충도"}
AMBIG.update({"자화상": {"gangsehwang", "gohuidong", "kimhongdo"}, "묵란도": {"kimjeonghui", "johuiryong"}, "초충도": {"simsajeong"}})
CONFL = [{"추상미술", "단색화"}, {"산수화", "진경산수화", "남종화", "문인화", "수묵화", "선종화"}, {"추상미술", "추상표현주의"}, {"인상주의", "후기 인상주의", "신인상주의"}]   # 서로 비슷해서 한 문제의 보기에 같이 두지 않는 화풍
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
    famous = [x for x in diff if min(w["fame"] for w in A[x]["works"]) == 1]
    if len(famous) < k: famous = diff
    n_same = {1: 0, 2: 1, 3: 2}[lv]
    out = R.sample(same, min(n_same, len(same)))
    pool = famous if lv == 1 else diff
    rest = [x for x in pool if x not in out]
    if len(rest) < k - len(out): rest = [x for x in same + diff if x not in out]
    out += R.sample(rest, k - len(out))
    return [A[x]["name"] for x in out]

def info(a, w):
    s = f"{a['name']}({a['years']}·{a['country']})의 {J[w['kind']]}이에요. "
    s += f"{w['y']}에 그렸어요." if w["kind"] in ("그림", "벽화", "서화") else f"{w['y']}에 만들었어요."
    if w["place"]: s += f" {w['place']}에서 볼 수 있어요."
    return s


SETS = {"west": dict(file="art-quiz", eras=WEST_ERAS, countries=COUNTRIES),
        "korea": dict(file="korean-art-quiz", eras=KOREA_ERAS),
        "east": dict(file="eastern-art-quiz", eras=EAST_ERAS, countries=["중국", "일본", "한국(조선)", "인도"])}
def use(sid):
    """보기(오답)를 고를 작가 범위를 한 묶음으로 좁혀요."""
    global A, ORDER, ALLW, STYLES, PLACES, COUNTRIES
    A = {k: v for k, v in ALLA.items() if v["set"] == sid}; ORDER = [x for x in ORDER_ALL if x in A]
    ALLW = [w for a in A.values() for w in a["works"]]
    STYLES = sorted({a["style"] for a in A.values() if a["style"]})
    PLACES = sorted({w["place"] for w in ALLW if w["place"] and " 등" not in w["place"]})
    COUNTRIES = SETS[sid].get("countries")
def gen(sid):
    """묶음 하나(서양·우리나라·동양)의 문제를 만들어요. 보기(오답)도 같은 묶음 안에서만 골라요."""
    global data, level, seen
    use(sid)
    data, level, seen = [], {}, set()
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
            others = [x for x in others if any(z["t"] not in NODIST for z in A[x]["works"])]
            same = [x for x in others if A[x]["era"] == a["era"]]
            sel = R.sample(same, min({1: 0, 2: 1, 3: 2}[lv], len(same)))
            sel += R.sample([x for x in others if x not in sel], 3 - len(sel))
            wrong = [R.choice(sorted([z for z in A[x]["works"] if z["t"] not in NODIST], key=lambda z: z["fame"])[:2])["t"] for x in sel]
            add(f"다음 중 ‘{a['name']}’의 작품은?" if w is picks[0] else f"‘{a['name']}’의 작품으로 알려진 것은?", w["t"], wrong, a["era"], info(a, w), lv)

    # ③ 작가 → 나라
    for a in A.values():
        if not COUNTRIES or a["id"] in NO_COUNTRY: continue
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
        if not w["place"] or " 등" in w["place"] or w["t"] in NODIST: continue
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


    if sid in ("korea", "east"):   # ⑦ 호(號) ↔ 화가 (호가 있는 우리나라 화가만)
        hos = [A[x]["ho"] for x in ORDER if A[x]["ho"]]
        hoa = [x for x in ORDER if A[x]["ho"]]
        for a in A.values():
            if not a["ho"]: continue
            lv = 1 if a["id"] in HO_EASY else (2 if min(w["fame"] for w in a["works"]) == 1 else 3)
            ex = f"{a['name']}({a['years']})의 호는 '{a['ho']}'예요. {a['bio']}"
            add(f"호(號)가 ‘{a['ho']}’인 화가는 누구일까요?", a["name"], [A[x]["name"] for x in R.sample([y for y in hoa if y != a["id"]], 3)], a["era"], ex, lv)
            add(f"화가 ‘{a['name']}’의 호(號)는 무엇일까요?", a["ho"], R.sample([h for h in hos if h != a["ho"]], 3), a["era"], ex, min(3, lv + 1))
    if sid == "korea":   # ⑧ 작품 → 만든 때(10년 단위), ⑨ 화가 → 살았던 때
        import re as _re
        def dec(y):
            m = _re.fullmatch(r"(\d{3})\d(?:경|~\d{4}경?)?|(\d{3})0년대", y)
            return (m.group(1) or m.group(2)) + "0년대" if m else None
        decs = [f"{d}0년대" for d in range(190, 201)]
        for a in A.values():
            for w in a["works"]:
                d = dec(w["y"])
                if not d or (w["y"][:4].isdigit() and "~" in w["y"] and w["y"][:3] != w["y"].split("~")[1][:3]): continue
                k = decs.index(d); near = [x for x in decs if x != d and abs(decs.index(x) - k) <= 3]
                add(f"{a['name']}의 ‘{w['t']}’은(는) 언제 만들어졌을까요?", d, R.sample(near, 3), a["era"], info(a, w), min(3, w["fame"] + 1))
        for a in A.values():
            if a["years"].endswith("~"): continue   # 살아 있는 화가는 빼요
            lv = min(3, min(w["fame"] for w in a["works"]) + 1)
            others = [A[x]["years"] for x in ORDER if x != a["id"] and A[x]["years"][:4] != a["years"][:4]]
            add(f"화가 ‘{a['name']}’이(가) 태어나고 세상을 떠난 해는?", a["years"], R.sample(others, 3), a["era"], f"{a['name']}({a['years']}) — {a['bio']}", lv)
    if sid == "east":   # ⑦ 화가 → 시대(왕조)
        pers = sorted(set(PERIOD.values()))
        for a in A.values():
            lv = min(3, min(w["fame"] for w in a["works"]) + 1)
            same = [p for p in pers if p != a["period"] and p.split()[0] == a["period"].split()[0]]
            other = [p for p in pers if p != a["period"] and p not in same]
            wrong = R.sample(same, min({1: 0, 2: 1, 3: 2}[lv], len(same))); wrong += R.sample(other, 3 - len(wrong))
            add(f"‘{a['name']}’은(는) 어느 시대의 화가일까요?", a["period"], wrong, a["era"], f"{a['name']}({a['en']}, {a['years']}) — {a['bio']}", lv)
    for q, ans, wrong, ex, lv in {"korea": KOREA_TRIVIA, "east": EAST_TRIVIA}.get(sid, []):
        add(q, ans, wrong, "상식", ex, lv)   # 직접 쓴 상식 문제
    return data, level
ORDER_ALL = ORDER
# 묶음마다 문제와 등급 파일(qlevel/<퀴즈>.json: 문제 → 1·2·3)
os.makedirs("qlevel", exist_ok=True)
QUIZ = {}
for sid in SETS:
    d, lvl = gen(sid); QUIZ[sid] = d
    if sid != "west":   # 우리나라·동양 묶음은 작품이 적어 '유명 정도'만으로는 초급이 모자라요 → 쉬운 순서(등급, 만든 순서)로 30%·32%·나머지로 나눠요
        rank = sorted(range(len(d)), key=lambda n: (lvl[d[n][0]], n)); c1, c2 = round(len(d) * .30), round(len(d) * .62)
        for r, n in enumerate(rank): lvl[d[n][0]] = 1 if r < c1 else 2 if r < c2 else 3
    json.dump(lvl, open(f"qlevel/{SETS[sid]['file']}.json", "w", encoding="utf-8"), ensure_ascii=False)
    cnt = {1: 0, 2: 0, 3: 0}
    for v in lvl.values(): cnt[v] += 1
    print(SETS[sid]["file"], "문제", len(d), "초급/중급/고급", cnt[1], cnt[2], cnt[3])
A, ORDER, ALLW = ALLA, ORDER_ALL, [w for a in ALLA.values() for w in a["works"]]
# ───────── 그림 모드(온라인·내장) 자료: 저작권이 끝난 작가의 작품 중 위키백과 대응이 있는 것만
alltitles = {w["t"] for w in ALLW}
missing = [t for t in WIKI if t not in alltitles]; assert not missing, "WIKI 대응표의 제목이 art_data 에 없어요: " + str(missing)
W, QI, G = {}, [], {}
for sid in SETS:
    use(sid)
    for a in A.values():
        tk = _tokens(a["id"], a["en"], a["name"])
        for w in sorted(a["works"], key=lambda z: z["fame"]):
            if w["t"] not in WIKI: continue
            cc = a["id"] in NO_IMAGE   # 저작권이 남은 화가: CC BY·CC BY-SA로 공개된 커먼즈 파일(file:)만, 저작자·라이선스를 붙여 보여 줘요(2026-11-26 사용자 결정)
            if cc and not all(k.startswith("file:") for k in WIKI[w["t"]]): continue
            W[w["t"]] = {"k": WIKI[w["t"]], "a": a["id"], "t": tk, "kd": w["kind"], **({"cc": 1} if cc else {})}
            G.setdefault(a["id"], w["t"])
            QI.append(["이 그림의 작가는 누구일까요?", a["name"], pick_artists(a, w["fame"], ban=AMBIG.get(w["t"], ())), a["era"], w["fame"], w["t"], f"‘{w['t']}’ — " + info(a, w), [w["y"], w["place"] or "", J[w["kind"]], a["name"], a["years"], a["country"]], sid])
A, ORDER, ALLW = ALLA, ORDER_ALL, [w for a in ALLA.values() for w in a["works"]]
# 저작권이 남은 화가(NO_IMAGE)는 앱 안에 그림을 띄우지 않고, 위키백과 검색 링크(앱 밖에서 열림)만 둬요: 작품 제목·화가 이름 → 화가 이름
LINK = {}
for a in A.values():
    if a["id"] not in NO_IMAGE: continue
    LINK[a["name"]] = a["name"]
    for w in a["works"]:
        if w["t"] not in W: LINK[w["t"]] = a["name"]   # 앱 안에 보여 줄 수 있는(CC BY 공개) 그림은 링크 대신 그림으로
# 커먼즈 검색은 영어 이름으로 해요: 한국어 제목+이름(예 '론도 김환기')은 결과가 0건이라 링크가 쓸모없었어요(2026-11-26 사용자 지적)
# art_commons.json(art_commons_check.py 가 센 커먼즈 파일 수): 결과가 더 많은 이름으로 찾고, 0건인 화가(장욱진 등)는 🖼️ 단추를 빼요
try: _CH = json.load(open("art_commons.json", encoding="utf-8"))
except Exception: _CH = {}
LINK_EN = {}
for a in A.values():
    if a["id"] not in NO_IMAGE: continue
    c = _CH.get(a["name"]); en = a.get("en") or a["name"]
    if not c: LINK_EN[a["name"]] = en; continue
    he, hk = c.get("hits_en"), c.get("hits_ko")
    if he == 0 and hk == 0: LINK_EN[a["name"]] = ""; continue
    LINK_EN[a["name"]] = a["name"] if (hk or 0) > (he or 0) and he is not None else en
# 작품 줄: 커먼즈에 그 작품 파일이 있는 것만 검색어(COMMONS_Q), 없으면 "" → 🖼️ 단추 없음(2026-11-26 전수 조사)
for t0, w0 in LINK.items():
    if t0 != w0: LINK_EN[t0] = COMMONS_Q.get(t0, "")
_bad = [t0 for t0 in COMMONS_Q if t0 not in LINK]
if _bad: print("⚠ COMMONS_Q 에 있지만 링크 작품이 아닌 제목:", _bad)
DATA = {"W": W, "Q": QI, "G": G, "N": {a["name"]: a["id"] for a in A.values()}, "L": LINK, "E": LINK_EN}
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

QTITLE = {"west": ("art-quiz.html", "명화 작가 퀴즈", "🖼️", 20, "세계(서양) 명화의 작가와 작품, 시대·화풍을 맞혀 보세요. 우리나라 근현대 화가는 <a href=\"korean-art-quiz.html\">🖌️ 한국 근현대 화가 퀴즈</a>, 조선·중국·일본 그림은 <a href=\"eastern-art-quiz.html\">🏯 동양화 퀴즈</a>에 있어요."),
          "korea": ("korean-art-quiz.html", "한국 근현대 화가 퀴즈", "🖌️", 8, "고희동·나혜석부터 이중섭·박수근·김환기·천경자, 백남준·박서보·김창열까지, 우리나라 근대·현대 화가와 작품·호(號)·이야기를 맞혀 보세요. 조선 화가는 <a href=\"eastern-art-quiz.html\">🏯 동양화 퀴즈</a>에 있어요."),
          "east": ("eastern-art-quiz.html", "동양화 퀴즈", "🏯", 150, "조선(안견·정선·김홍도·신윤복·김정희…)과 중국(고개지·곽희·장택단·황공망…), 일본(셋슈·소타쓰·호쿠사이·히로시게…)의 그림과 화가, 호(號)·시대, 동양화 용어를 맞혀 보세요. 우리나라 근현대 화가는 <a href=\"korean-art-quiz.html\">🖌️ 한국 근현대 화가 퀴즈</a>에 있어요.")}
for sid, (fn, title, emo, hue, desc) in QTITLE.items():
    make_quiz(H + fn, title, emo, hue, fn[:-5] + "-best-v1", desc + " 모든 화가와 대표작은 <a href=\"art-gallery.html\">🎨 명화 작가별 모음</a>에서 볼 수 있어요.", QUIZ[sid], label=title)

# ───────── 명화 작가별 모음 화면
AR = [dict(id=a["id"], n=a["name"], e=a["en"], y=a["years"], c=a["country"], s=a["style"] or "", g=a["era"], b=a["bio"], k=a["set"], h=a["ho"] or "", p=a["period"] or "",
           l=min(w["fame"] for w in a["works"]), w=[[w["t"], w["y"], w["place"] or "", w["fame"], w["kind"]] for w in a["works"]]) for a in A.values()]
CSS = '''.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:.9rem}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:700}
.ar{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:6px}.ar h2{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}.ar .en{font-family:var(--font-body);font-size:.85rem;color:var(--muted)}
.ar .meta{display:flex;gap:6px;flex-wrap:wrap;font-size:.85rem;color:var(--muted)}.ar .tag{background:var(--soft);border-radius:999px;padding:2px 10px;color:var(--fg)}.ar .bio{font-size:.95rem;line-height:1.55}
.ar ul{margin:2px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:4px}.ar li{font-size:.95rem;line-height:1.4}.ar li small{display:block;color:var(--muted);font-size:.8rem}.ar li .st{color:#d89b00}
.era{font-family:var(--font-display);font-size:1.15rem;margin:8px 0 0;color:var(--accent)}#cnt{text-align:center}'''
BODY = '''  <div class="card"><div class="chips" id="sets"></div><div class="chips" id="eras"></div><div class="chips" id="lvs"></div><p class="muted" id="lvp"></p><input type="text" id="q" placeholder="작가·작품·나라·화풍·호 찾기 (예: 모네, 별, 단원, 우키요에)" aria-label="찾기"><p class="muted" id="cnt"></p><a class="btn" id="goq" href="art-quiz.html" style="text-align:center;text-decoration:none">🖼️ 명화 작가 퀴즈 풀기</a></div>
  <div id="list"></div>'''
JS = '''const AR = ''' + json.dumps(AR, ensure_ascii=False) + ''', SETS = ''' + json.dumps({"west": WEST_ERAS, "korea": KOREA_ERAS, "east": EAST_ERAS}, ensure_ascii=False) + ''';
// 묶음: 전체 / 서양 명화 / 한국 근현대 / 동양화(조선·중국·일본). 묶음마다 시대 단추와 '퀴즈 풀기' 단추가 바뀌어요
const SETN = [["all", "전체"], ["west", "🌍 서양 명화"], ["korea", "🖌️ 한국 근현대"], ["east", "🏯 동양화(조선·중국·일본)"]], QZ = { all: ["art-quiz.html", "🖼️ 명화 작가 퀴즈 풀기"], west: ["art-quiz.html", "🖼️ 명화 작가 퀴즈 풀기"], korea: ["korean-art-quiz.html", "🖌️ 한국 근현대 화가 퀴즈 풀기"], east: ["eastern-art-quiz.html", "🏯 동양화 퀴즈 풀기"] };
let set = ld(KEY + "-set") || "all"; if (!QZ[set]) set = "all";
const ERAS_OF = () => ["전체"].concat(set === "all" ? Object.values(SETS).flat() : SETS[set]);
let era = ld(KEY + "-era") || "전체", lvf = +ld(KEY + "-lv") || 0; if (!(lvf >= 0 && lvf <= 3)) lvf = 0;
const LVN = ["모든 난이도", "🌱 초급", "🌿 중급", "🌳 고급"], LVD = ["", "누구나 아는 대표작(★)이 있는 작가예요.", "알려진 작품이 있는 작가예요.", "마니아가 좋아하는 작가예요."];
const norm = s => String(s).toLowerCase().replace(/\\s+/g, "");
function render() {
  const q = norm($("q").value), box = $("list"); let n = 0, w = 0, html = "", last = "";
  AR.forEach(a => {
    if (set !== "all" && a.k !== set) return;
    if (era !== "전체" && a.g !== era) return;
    if (lvf && a.l !== lvf) return;
    if (q && !norm([a.n, a.e, a.c, a.s, a.g, a.b, a.h, a.p, ...a.w.map(x => x[0])].join(" ")).includes(q)) return;
    if (a.g !== last) { last = a.g; html += `<p class="era">${esc(a.g)}</p>`; }
    n++; w += a.w.length;
    html += `<article class="ar"><h2>${esc(a.n)} <span class="en">${esc(a.e)}</span></h2><div class="meta"><span>${esc(a.y)}</span><span>· ${esc(a.p || a.c)}</span>${a.h ? `<span>· 호 ${esc(a.h)}</span>` : ""}${a.s ? `<span class="tag">${esc(a.s)}</span>` : ""}</div><p class="bio">${esc(a.b)}</p><ul>${a.w.map(x => `<li>${x[3] === 1 ? '<span class="st" aria-label="대표작">★</span> ' : ""}<b>${esc(x[0])}</b><small>${esc(x[1])} · ${esc(x[4])}${x[2] ? " · " + esc(x[2]) : ""}</small></li>`).join("")}</ul></article>`;
  });
  box.innerHTML = html || '<p class="muted center">찾는 작가가 없어요</p>';
  $("lvs").innerHTML = LVN.map((t, k) => `<button type="button" class="chip${k === lvf ? " on" : ""}" data-l="${k}">${t}${k ? ` <small>${AR.filter(a => a.l === k && (set === "all" || a.k === set)).length}</small>` : ""}</button>`).join(""); $("lvp").textContent = LVD[lvf];
  $("cnt").textContent = n ? `작가 ${n}명 · 작품 ${w}점 (★ = 누구나 아는 대표작)` : "";
}
function drawSets() {
  if (!ERAS_OF().includes(era)) era = "전체";
  $("sets").innerHTML = SETN.map(([k, t]) => `<button type="button" class="chip${k === set ? " on" : ""}" data-s="${k}">${t}</button>`).join("");
  $("eras").innerHTML = ERAS_OF().map(e => `<button type="button" class="chip${e === era ? " on" : ""}" data-e="${esc(e)}">${esc(e)}</button>`).join("");
  $("goq").href = QZ[set][0]; $("goq").textContent = QZ[set][1];
}
drawSets();
$("sets").addEventListener("click", ev => { const b = ev.target.closest("[data-s]"); if (!b) return; set = b.dataset.s; sv(KEY + "-set", set); drawSets(); render(); });
$("eras").addEventListener("click", ev => { const b = ev.target.closest("[data-e]"); if (!b) return; era = b.dataset.e; sv(KEY + "-era", era); $("eras").querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c === b)); render(); });
$("lvs").addEventListener("click", ev => { const b = ev.target.closest("[data-l]"); if (!b) return; lvf = +b.dataset.l; sv(KEY + "-lv", lvf); render(); });
$("q").addEventListener("input", render); render();'''
make_page(H + "art-gallery.html", "명화 작가별 모음", "🎨", 20, "art-gallery-v1",
          "서양 명화·한국 근현대 화가·동양화(조선·중국·일본)를 한곳에 모았어요. 그림 이미지는 담지 않고 작가와 대표작의 이름·연도·소장처만 정리했어요. 소장처와 제작 연도는 여러 자료와 달라질 수 있어요. 오래된 작품은 '경'(대략)으로 적었어요.",
          BODY, JS, CSS)
for _f in ("art-quiz.html", "korean-art-quiz.html", "eastern-art-quiz.html", "art-gallery.html"): hook(H + _f)
