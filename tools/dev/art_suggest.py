#!/usr/bin/env python3
"""art_fetch.py --dry-run 에서 걸러진 작품의 위키백과 항목 이름을 검색으로 찾아 후보를 보여 줘요(자동으로 고치지 않고, 사람이 보고 art_wiki.py 를 고쳐요).
   사용: py art_suggest.py            (걸러진 작품 모두)    py art_suggest.py 사춘기 씨름    (이 작품만)
   각 후보: 위키백과 제목 · 한 줄 설명 · 검증 결과(✓ 통과 / ✗ 이유). 같은 작가의 '다른 작품'이 뽑힐 수 있으니 제목을 꼭 눈으로 확인하세요."""
import os, sys, json, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art_data import ARTISTS
from art_wiki import WIKI, NO_IMAGE, tokens
import art_fetch as F

def search(lang, q, n=5):
    d = F.get(f"https://{lang}.wikipedia.org/w/rest.php/v1/search/page?q={urllib.parse.quote(q)}&limit={n}")
    return [(p.get("key"), p.get("title"), p.get("description") or "") for p in (d or {}).get("pages", [])]

def main():
    only = set(a for a in sys.argv[1:] if not a.startswith("-"))
    for a in ARTISTS:
        aid, name, en = a[0], a[1], a[2]
        if aid in NO_IMAGE: continue
        for w in a[8]:
            t = w[0]
            if t not in WIKI or (only and t not in only): continue
            info, why = F.check(WIKI[t], tokens(aid, en, name))
            if info and not only: continue
            print(f"\n■ {t} ({name}) — 지금 대응 {WIKI[t]} → {'✓ 통과' if info else '✗ ' + why}")
            first = WIKI[t][0]; lang, key = first.split(":", 1)
            base = key.split("_(")[0].replace("_", " ")
            qs = [(lang, f"{base} {en}")] if lang == "en" else [("ko", f"{t} {name}"), ("ko", t)]
            if lang == "en": qs.append(("en", base))
            seen = set()
            for lg, q in qs:
                for k, ti, desc in search(lg, q):
                    if (lg, k) in seen: continue
                    seen.add((lg, k)); i2, w2 = F.check([f"{lg}:{k}"], tokens(aid, en, name))
                    print(f"   · {lg}:{k}  |  {desc[:60]}  |  {'✓ ' + i2['l'] if i2 else '✗ ' + w2}")
if __name__ == "__main__": main()
