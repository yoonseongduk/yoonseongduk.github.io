# 생물 퀴즈 사진 대응표 만들기(2026-11-28 사용자 요청: 생물 이름이 정답이면 사진과 연결).
#   퀴즈 5개(동물·바다 생물·곤충·식물·공룡)의 정답 중 '위키백과 항목이 실제 생물(분류군)'인 것만 골라
#   bio_wiki.json = {퀴즈 파일: {정답: 위키백과 항목 이름}} 을 만들어요. 그림 파일은 받지 않아요(이름만 확인).
#   확인: ① 한국어 위키백과에 항목이 있고(넘겨주기 따라감) 동음이의 문서가 아님 ② 자유 라이선스 대표 사진이 있음
#        ③ 위키데이터에 학명(P225)이 있거나 분류군(Q16521)·화석 분류군(Q23038290)·단형 분류군(Q310890)
#   사진 라이선스(공개 도메인·CC0·CC BY·CC BY-SA)는 폰이 보여 줄 때 online.js 가 다시 확인해요.
#   실행: py bio_build.py  →  py bio_apply.py (화면에 넣기, qlevel.py 가 자동 실행)
import json, re, time, urllib.error, urllib.parse, urllib.request
R = "../../"
QUIZ = ["animal-quiz.html", "sea-quiz.html", "insect-quiz.html", "plant-quiz.html", "dino-quiz.html"]
UA = {"User-Agent": "family-games-bio-check/1.0 (offline quiz data check)"}
TAXON = {"Q16521", "Q23038290", "Q310890", "Q55983715"}   # 분류군·화석 분류군·단형 분류군·흔히 부르는 생물 이름(돌고래·캥거루처럼 학명 하나에 딱 맞지 않는 이름)
# 동음이의 문서(해마·코스모스·불가사리)는 아래 꼬리말을 붙인 항목을 차례로 찾아봐요
SUFFIX = [" (동물)", " (식물)", " (생물)", " (어류)", " (물고기)", " (곤충)", " (극피동물)", " (속)", " (공룡)", " (조류)", " (새)"]
import os
CACHE = "bio_cache.json"   # 물어본 결과 저장(다시 돌릴 때 위키 서버에 또 묻지 않게, 저장소에는 안 올림)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
PACE = 6   # 요청 사이 쉬는 초. 위키 서버는 요청이 몰리면 429(요청 제한)를 줘요(CLAUDE.md §8: 한 번에 하나씩, 간격을 두고)
def get(url):
    if url in cache: return cache[url]
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: d = json.load(r)
            cache[url] = d; json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); time.sleep(PACE); return d
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503): raise
            wait = int(e.headers.get("Retry-After") or 60); print("  요청 제한(429) → %d초 기다려요" % wait, flush=True); time.sleep(min(max(wait, 30), 300))
    raise SystemExit("요청 제한이 계속돼요. 지금까지 받은 결과는 bio_cache.json 에 있으니 나중에 다시 실행하면 이어서 해요.")
def answers(f):
    s = open(R + f, encoding="utf-8").read(); D = json.loads(re.search(r"const D = (\[.*?\]);\r?\n", s, re.S).group(1))
    out = []
    for d in D:
        a = str(d[1]).strip()
        if 1 < len(a) <= 14 and not re.search(r"[0-9A-Za-z%·,()~/]|\s\S+\s", a) and a not in out: out.append(a)
    return out
DIS = set()   # 동음이의 문서였던 이름(이 이름에만 꼬리말을 붙여 다시 찾아요)
def ko_pages(names):
    res = {}
    for k in range(0, len(names), 50):
        part = names[k:k + 50]
        q = get("https://ko.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1, "prop": "pageprops", "ppprop": "wikibase_item|page_image_free|disambiguation", "titles": "|".join(part)}))["query"]
        alias = {}
        for x in q.get("normalized", []) + q.get("redirects", []): alias[x["to"]] = alias.get(x["from"], x["from"])
        for p in q.get("pages", {}).values():
            pp = p.get("pageprops", {}); t = p.get("title")
            if "disambiguation" in pp:
                src = t
                while src in alias: src = alias[src]
                DIS.add(src)
            if "missing" in p or "disambiguation" in pp or not pp.get("wikibase_item") or not pp.get("page_image_free"): continue
            src = t
            while src in alias: src = alias[src]
            for n in part:
                if n == src or alias.get(t) == n or n == t: res[n] = (t, pp["wikibase_item"], pp["page_image_free"])
    return res
def claims(qids):
    res = {}; qids = sorted(set(q for q in qids if q))
    for k in range(0, len(qids), 50):
        d = get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "props": "claims", "ids": "|".join(qids[k:k + 50])}))
        for q, e in d.get("entities", {}).items(): res[q] = e.get("claims", {})
    return res
ids = lambda c, p: {x["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for x in c.get(p, [])}
def taxa(qids):
    cl = claims(qids); ok = {q for q, c in cl.items() if "P225" in c or ids(c, "P31") & TAXON}
    rest = {q: ids(c, "P279") for q, c in cl.items() if q not in ok and ids(c, "P279")}   # 미역처럼 '~의 한 종류'(P279)로만 적힌 항목: 위 단계가 분류군이면 통과
    if rest:
        up = claims(set().union(*rest.values()))
        ok |= {q for q, ps in rest.items() if any("P225" in up.get(x, {}) or ids(up.get(x, {}), "P31") & TAXON for x in ps)}
    return ok
# 빼는 이름: 새끼·애벌레 이름인데 어른 항목으로 넘어가는 것(사진이 정답과 달라 보임), 생물이 아닌 말, 잘못 이어지는 것(2026-11-28 확인)
EXCLUDE = {"병아리", "망아지", "학배기", "송충이", "렙토세팔루스", "여러해살이", "덩굴", "딱정벌레류", "일본강치", "수각류", "육식 공룡"}   # 수각류·육식 공룡: 여러 공룡을 묶은 이름이라 그림이 섞여 나옴(2026-11-28 사용자 지적)
# 사진 고르기(2026-11-28 사용자 지적: '오리' 문서 사진이 청둥오리, '악어' 사진에 다른 동물도 나옴).
#   여러 종을 묶은 문서는 한 종의 사진을, 어떤 문서는 다른 동물이 함께 찍힌 사진을 대표로 써요. 그래서 위키미디어 커먼즈의
#   '찍힌 것(depicts, P180)' 기록으로 확인해요: ① 그 생물(위키데이터 항목)이 찍혀 있다고 적혀 있고 ② 다른 생물은 함께 적혀 있지 않은 사진만 써요.
#   후보는 한국어 위키백과 대표 사진 → 위키데이터 대표 사진(P18) 순서. 기록이 없는 사진은 확인할 수 없어 쓰지 않아요(정확성 우선).
def depicts(files):
    res = {}; files = sorted(set(files))
    for k in range(0, len(files), 50):
        d = get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "sites": "commonswiki", "props": "info|claims", "titles": "|".join("File:" + f.replace("_", " ") for f in files[k:k + 50])}))
        for e in d.get("entities", {}).values():
            t = e.get("title", "").replace("File:", "").replace(" ", "_")
            st = e.get("statements") or e.get("claims") or {}
            if t and isinstance(st, dict): res[t] = {x["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for x in st.get("P180", []) if isinstance(x["mainsnak"].get("datavalue", {}).get("value"), dict)}
    return res
def is_org(c): return "P225" in c or bool(ids(c, "P31") & TAXON)
# 뼈·화석 사진은 빼요(2026-11-28 사용자 지적: 스테고사우루스가 뼈만 나옴). 파일 이름 또는 찍힌 것(뼈대 Q7881·화석 Q40614·두개골 Q13147)으로 확인
BONE_Q = {"Q7881", "Q40614", "Q13147"}
BONE_RE = re.compile(r"skelet|squelet|skull|cr[aâ]ne|sch[aä]del|fossil|museum|mus[eé]e|holotype|specimen|mount|bones?\b|cast\b|replica|exhibit", re.I)
def restore_search(sci):   # 공룡: 커먼즈에서 복원도(살아 있을 때 모습) 그림 찾기
    if not sci: return []
    d = get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "format": "json", "list": "search", "srnamespace": 6, "srlimit": 15, "srsearch": sci + " life restoration filetype:bitmap"}))
    return [r["title"].replace("File:", "").replace(" ", "_") for r in d.get("query", {}).get("search", []) if sci.split()[0].lower() in r["title"].lower()]
# 사진 직접 지정(사용자가 확인 화면에서 이상하다고 알려 준 것을 커먼즈 설명을 읽고 바꾼 것): 이름 → 커먼즈 파일 이름
PIN = {
    "하드로사우루스": "Hadrosaurus_TD.png",
    # 2026-11-28 사용자 확인 화면 지적(부분만 나옴·이상함) → 커먼즈 설명을 읽고 몸 전체가 나온 것으로
    "감자": "Solanales_-_Solanum_tuberosum_-_3.jpg",
    "국화": "Chrysanthemum_×_morifolium_flowers.jpg",   # 옛: 08NOV(설명 없음, 사용자: 이상함) → 국화꽃 여러 송이(CC BY-SA 4.0)   # 옛: 싹이 튼 감자 → 감자 덩이줄기들(CC BY-SA 4.0), 문제 "땅속에서 자라는 채소는?"
    "코끼리": "178_Male_African_bush_elephant_in_Etosha_National_Park_Photo_by_Giles_Laurent.jpg",   # 옛: 숲속 코끼리(나무에 가림)
    "진주조개": "Pinctada_fucata_(Japanese_pearl_oyster)_(Japan).jpg",   # 옛: 양식장 조개 일부
    "개미": "Red_forest_ant_(Formica_rufa)_on_an_alfalfa_flower_(Medicago_sativa).jpg",   # 옛: 얼굴 옆모습만
    "전기가오리": "Naturalis_Biodiversity_Center_-_RMNH.ART.52_-_Narke_japonica_(Temminck_and_Schlegel)_-_Kawahara_Keiga_-_1823_-_1829_-_Siebold_Collection_-_pencil_drawing_-_water_colour.jpeg",   # 옛: Narke_japonica.jpg(이상함) → 시볼트 일본 동물지 원화(공개 도메인, 몸 전체)   # 2026-11-28 사용자 지적: 공룡 전체 그림이 아님(옛 그림은 작은 복원도 모음) → 몸 전체 복원도(CC BY 4.0)
}
REJECT = {}   # 사진이 맞지 않아 뺀 이름(화면에 보고)
out = {}
for f in QUIZ:
    names = answers(f); pg = ko_pages(names)
    miss = [n for n in names if n not in pg and n in DIS]; alt = ko_pages([n + x for n in miss for x in SUFFIX]) if miss else {}
    for n in miss:
        for x in SUFFIX:
            if n + x in alt: pg[n] = alt[n + x]; break
    tx = taxa([v[1] for v in pg.values()])
    keep = [n for n in names if n in pg and pg[n][1] in tx and n not in EXCLUDE]
    CL = claims([pg[n][1] for n in keep])
    cand = {n: [pg[n][2].replace(" ", "_")] + [x["mainsnak"].get("datavalue", {}).get("value", "").replace(" ", "_") for x in CL.get(pg[n][1], {}).get("P18", []) if isinstance(x["mainsnak"].get("datavalue", {}).get("value"), str)] for n in keep}
    if f == "dino-quiz.html":   # 공룡은 복원도를 먼저(대표 사진은 대부분 뼈 화석)
        for n in keep:
            sci = next((x["mainsnak"].get("datavalue", {}).get("value", "") for x in CL.get(pg[n][1], {}).get("P225", []) if isinstance(x["mainsnak"].get("datavalue", {}).get("value"), str)), "")
            cand[n] = restore_search(sci) + cand[n]
    DP = depicts([x for v in cand.values() for x in v])
    other = claims({q for v in DP.values() for q in v if q})
    out[f] = {}
    for n in keep:
        q = pg[n][1]; pick = None
        for x in dict.fromkeys(cand[n]):
            dp = DP.get(x, set())
            if q in dp and not (dp & BONE_Q) and not BONE_RE.search(x) and not any(o != q and is_org(other.get(o, {})) for o in dp): pick = x; break
        if n in PIN: pick = PIN[n]
        if pick: out[f][n] = [pick, pg[n][0]]
        else: REJECT.setdefault(f, []).append(n)
    print(f, "사진 확인 통과", len(out[f]), "/", len(keep))
print("찍힌 것 기록으로 확인되지 않아 뺀 이름:", json.dumps(REJECT, ensure_ascii=False, indent=0))
json.dump(REJECT, open("bio_reject.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)   # 사진이 없는 이름(확인 화면 bio-check.html 에 보여 줌)
json.dump(out, open("bio_wiki.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
