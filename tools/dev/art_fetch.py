#!/usr/bin/env python3
"""명화 그림 내장용 받기 도구 — 인터넷이 되는 PC에서 한 번 실행하면 art-img/ 에 그림과 목록(index.json)이 만들어져요.
   사용: cd tools\\dev → py art_fetch.py            (모두 받기, 이미 받은 것은 건너뜀)
         py art_fetch.py --dry-run                   (받지 않고 검증만: 어느 작품이 통과하는지 보고)
         py art_fetch.py --only 모나리자 --refresh     (한 작품만 다시)
   검증(통과한 것만 저장): ① 위키백과 항목 설명에 작가 이름이 있다 ② 그림 파일이 위키미디어 커먼즈에 있고 라이선스 표시가 공개 도메인(PD)·CC0 이다.
   저작권이 남아 있을 수 있는 작가(art_wiki.NO_IMAGE)는 처음부터 제외. 끝나면 `py set43.py`·`py ship.py ...`(art-quiz·art-gallery)·`py ..\\make-sw.py` 후 올리면 앱에서 '📦 내장 그림'이 켜져요.
   테스트용: 환경 변수 ART_MOCK=http://localhost:포트 를 주면 위키 주소 대신 그 서버(/en /ko /commons /upload)를 써요."""
import os, re, sys, json, time, zlib, unicodedata, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art_data import ARTISTS
from art_wiki import WIKI, NO_IMAGE, tokens
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "art-img")
UA = "FamilyGamesArtFetch/1.0 (educational family quiz; public-domain paintings only)"
MOCK = os.environ.get("ART_MOCK", "").rstrip("/")
PD = re.compile(r"public domain|^pd\b|^pd-|cc0|cc-zero", re.I)
norm = lambda s: "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower()

def url_for(u):
    if not MOCK: return u
    for host, pre in (("https://en.wikipedia.org", "/en"), ("https://ko.wikipedia.org", "/ko"), ("https://commons.wikimedia.org", "/commons"), ("https://upload.wikimedia.org", "/upload")):
        if u.startswith(host): return MOCK + pre + u[len(host):]
    return u
def get(u, binary=False, tries=2):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url_for(u), headers={"User-Agent": UA}), timeout=25) as r:
                data = r.read(); return data if binary else json.loads(data.decode("utf-8"))
        except Exception as e:
            err = e; time.sleep(1.5)
    return None
def file_of(u):
    m = re.search(r"/commons/(?:thumb/)?[0-9a-f]/[0-9a-f]{2}/([^/]+)", u or ""); return urllib.parse.unquote(m.group(1)) if m else None

def check(keys, toks):
    """작품 하나 검증. 통과하면 (정보 dict, None), 아니면 (None, 이유)."""
    why = "후보 항목 없음"
    for k in keys:
        lang, title = k.split(":", 1)
        s = get(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"), safe="()"))
        if not s or s.get("type") != "standard": why = "항목을 못 찾음"; continue
        th = (s.get("thumbnail") or {}).get("source", "")
        if not th.startswith("https://upload.wikimedia.org/"): why = "대표 그림 없음"; continue
        text = norm((s.get("description") or "") + " " + (s.get("extract") or ""))
        if not any(norm(t) in text for t in toks): why = "항목 설명에 작가 이름이 없음(다른 항목일 수 있음)"; continue
        f = file_of(th)
        if not f: why = "그림 파일 이름을 못 읽음"; continue
        c = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata&titles=" + urllib.parse.quote("File:" + f))
        pages = (c or {}).get("query", {}).get("pages", {}); p = next(iter(pages.values()), {}) if pages else {}
        md = ((p.get("imageinfo") or [{}])[0]).get("extmetadata", {}); lic = (md.get("LicenseShortName") or {}).get("value", "")
        if not lic or not PD.search(lic): why = f"공개 도메인 표시가 아님({lic or '라이선스 정보 없음'})"; continue
        page = ((s.get("content_urls") or {}).get("desktop") or {}).get("page") or f"https://{lang}.wikipedia.org/wiki/" + urllib.parse.quote(title)
        return {"src": th, "p": page, "t": s.get("title") or title, "l": lic, "file": f}, None
    return None, why

def main():
    args = sys.argv[1:]; dry = "--dry-run" in args; refresh = "--refresh" in args; only = args[args.index("--only") + 1] if "--only" in args else None
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    os.makedirs(OUT, exist_ok=True)
    idx_path = os.path.join(OUT, "index.json"); idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else {}
    works = [(a[0], a[1], a[2], w[0]) for a in ARTISTS if a[0] not in NO_IMAGE for w in a[8] if w[0] in WIKI]
    if only: works = [x for x in works if x[3] == only]
    if limit: works = works[:limit]
    ok = skip = 0; fails = []
    for n, (aid, name, en, title) in enumerate(works, 1):
        if not refresh and title in idx and os.path.exists(os.path.join(OUT, idx[title]["f"])): skip += 1; continue
        info, why = check(WIKI[title], tokens(aid, en, name))
        if not info: fails.append((title, why)); print(f"[{n}/{len(works)}] ✗ {title}: {why}"); continue
        if dry: ok += 1; print(f"[{n}/{len(works)}] ✓ {title} ← {info['t']} ({info['l']})"); continue
        data = get(info["src"], binary=True)
        if not data or len(data) < 2000 or len(data) > 600_000: fails.append((title, "그림 내려받기 실패 또는 크기 이상")); print(f"[{n}/{len(works)}] ✗ {title}: 내려받기 실패"); continue
        ext = os.path.splitext(info["file"])[1].lower() or ".jpg"; ext = ext if ext in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"
        fn = f"{aid}-{zlib.crc32(title.encode('utf-8')) % 100000:05d}{ext}"
        open(os.path.join(OUT, fn), "wb").write(data)
        idx[title] = {"f": fn, "p": info["p"], "t": info["t"], "l": info["l"], "src": info["file"]}; ok += 1
        print(f"[{n}/{len(works)}] ✓ {title} ← {info['t']} ({info['l']}, {len(data)//1024}KB)"); time.sleep(0.4)
    if not dry:
        json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        open(os.path.join(OUT, "LICENSE.txt"), "w", encoding="utf-8").write(
            "이 폴더의 그림은 위키백과 항목의 대표 그림(위키미디어 커먼즈)이며, 파일마다 공개 도메인(저작권 만료)·CC0 표시를 확인한 것만 담았어요.\n"
            "작품 이름·그림 출처 주소·라이선스 표시·원본 파일 이름은 index.json 에 있어요. 권리자께서 삭제를 요청하시면 확인 후 바로 지워요.\n")
    print(f"\n통과 {ok} · 이미 있어 건너뜀 {skip} · 걸러짐 {len(fails)} (전체 {len(works)}){' · 검증만(dry-run)' if dry else ''}")
    if fails:
        from collections import Counter
        for k, v in Counter(w for _, w in fails).most_common(): print("  ·", k, v)
    return 0

if __name__ == "__main__": sys.exit(main())
