"""저작권이 남은 화가(NO_IMAGE)마다 위키미디어 커먼즈에 관련 파일이 있는지 세어 art_commons.json 에 적어요.
명화 모음의 🖼️(커먼즈에서 그림 찾아보기) 단추는 파일이 1개 이상인 화가에게만 붙여요(set43.py 가 읽음).
2026-11-26: 장욱진처럼 커먼즈에 파일이 하나도 없는 화가는 단추를 눌러도 '결과 없음'만 나와서 만들었어요.
검색은 영어 이름·한국어 이름을 따옴표로 묶어(정확히 그 이름) 셉니다. 파일을 받지는 않아요(숫자만).
실행: py art_commons_check.py   (화가를 늘리거나 커먼즈에 파일이 새로 올라왔을 것 같을 때 다시 실행)"""
import json, time, urllib.request, urllib.parse
from art_data import ARTISTS
from art_wiki import NO_IMAGE

UA = "family-games-art-check/1.0"

def hits(q):
    u = "https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&format=json&srlimit=1&srsearch=" + urllib.parse.quote(q)
    for n in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30) as r:
                return json.load(r)["query"]["searchinfo"]["totalhits"]
        except Exception:
            time.sleep(5 + 5 * n)
    return None

out = {}
for a in ARTISTS:
    aid, ko, en = a[0], a[1], a[2]
    if aid not in NO_IMAGE: continue
    h_en = hits(f'"{en}"') if en else 0; time.sleep(1.5)
    h_ko = hits(f'"{ko}"'); time.sleep(1.5)
    out[ko] = {"en": en, "hits_en": h_en, "hits_ko": h_ko}
    print(ko, en, h_en, h_ko, flush=True)
json.dump(out, open("art_commons.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("화가", len(out), "/ 커먼즈 파일 없음:", [k for k, v in out.items() if not (v["hits_en"] or v["hits_ko"])])
