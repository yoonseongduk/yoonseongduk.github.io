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
                if n == src or alias.get(t) == n or n == t: res[n] = (t, pp["wikibase_item"])
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
EXCLUDE = {"병아리", "망아지", "학배기", "송충이", "렙토세팔루스", "여러해살이", "덩굴", "딱정벌레류", "일본강치"}
out = {}
for f in QUIZ:
    names = answers(f); pg = ko_pages(names)
    miss = [n for n in names if n not in pg and n in DIS]; alt = ko_pages([n + x for n in miss for x in SUFFIX]) if miss else {}
    for n in miss:
        for x in SUFFIX:
            if n + x in alt: pg[n] = alt[n + x]; break
    tx = taxa([v[1] for v in pg.values()])
    out[f] = {n: pg[n][0] for n in names if n in pg and pg[n][1] in tx and n not in EXCLUDE}
    print(f, "정답 후보", len(names), "→ 생물 항목", len(out[f]), "· 빠진 예:", [n for n in names if n not in out[f]][:12])
json.dump(out, open("bio_wiki.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
