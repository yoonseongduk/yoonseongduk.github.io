#!/usr/bin/env python3
"""한자 획순 데이터(data/stroke-6.json ~ stroke-1.json) 생성기.
원본: Make Me a Hanzi (https://github.com/skishore/makemeahanzi) 의 graphics.txt
  - graphics.txt 는 Arphic Public License (Arphic PL KaitiM GB / UKai 에서 파생), 사전/코드는 LGPL.
사용법: python build_stroke.py [graphics.txt 경로]   (없으면 GitHub 에서 내려받아요)
출력 형식: {"한자": {"s": ["SVG 경로(좌표÷4, y 위쪽이 +)", ...], "n": [[획 시작 x, y]...]}}
화면 좌표 = (x × S/256, (225 − y) × S/256)  (원본 좌표 1024 칸을 4로 나눠 저장해 용량을 줄임)"""
import json, re, sys, os, unicodedata as u, urllib.request
src = sys.argv[1] if len(sys.argv) > 1 else "graphics.txt"
if not os.path.exists(src):
    print("내려받는 중…"); urllib.request.urlretrieve("https://raw.githubusercontent.com/skishore/makemeahanzi/master/graphics.txt", src)
g = {}
for l in open(src, encoding="utf-8"):
    j = json.loads(l); g[j["character"]] = j
q = lambda p: re.sub(r"-?\d+", lambda m: str(round(int(m.group()) / 4)), p).replace(" Z", "Z")
h = json.load(open("../../data/hanja.json", encoding="utf-8"))
by = {}; miss = []
for c, k, gr, info in h:
    for cand in (c, u.normalize("NFKC", c)):
        if cand in g:
            j = g[cand]; by.setdefault(gr, {})[c] = {"s": [q(s) for s in j["strokes"]], "n": [[round(m[0][0] / 4), round(m[0][1] / 4)] for m in j["medians"]]}
            break
    else: miss.append(c)
for gr, d in by.items():
    f = "../../data/stroke-%s.json" % gr.replace("급", "")
    open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    print(gr, len(d), "자", os.path.getsize(f) // 1024, "KB")
print("획순 데이터가 없는 글자:", len(miss), "자")
