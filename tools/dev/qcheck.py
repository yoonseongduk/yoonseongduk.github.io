#!/usr/bin/env python3
"""퀴즈 추가 문제 검사(파일을 바꾸지 않아요): py qcheck.py 이름...  (예: job-quiz)
qmore/<이름>.txt 의 줄 형식·중복·정답/오답 겹침을 검사하고, 등급(## 초급·중급·고급 구역 + qlevel/<이름>.json)별 문제 수를 보여 줘요."""
import os, re, json, sys
import qmore, qlevel
for n in sys.argv[1:]:
    n = n if n.endswith("-quiz") else n + "-quiz"; bp = os.path.join(qmore.DIR, "base", n + ".json")
    h = open(os.path.join(qmore.REPO, n + ".html"), encoding="utf-8").read()
    base = json.load(open(bp, encoding="utf-8")) if os.path.exists(bp) else qlevel.read_d(h)[0]
    seen = {r[0] for r in base}; bad = 0; add = []; cur = 0; sec = {}
    for ln, l in enumerate(open(os.path.join(qmore.DIR, n + ".txt"), encoding="utf-8") if os.path.exists(os.path.join(qmore.DIR, n + ".txt")) else [], 1):
        l = l.rstrip("\r\n"); m = re.match(r"^##\s*(초급|중급|고급)", l)
        if m: cur = qlevel.SECT[m.group(1)]; continue
        if not l.strip() or l.lstrip().startswith("#"): continue
        try: r = qmore._row(l.split("|"), base[0])
        except Exception as e: bad += 1; print(f"  ❌ {ln}줄: {e}"); continue
        if r[0] in seen: bad += 1; print(f"  ⚠ {ln}줄 중복 문제: {r[0][:30]}"); continue
        seen.add(r[0]); add.append(r); sec[r[0]] = cur
    jp = os.path.join(qlevel.QL, n + ".json"); jm = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
    allq = list(base) + add; lv = [sec.get(r[0]) or jm.get(r[0]) or 2 for r in allq]
    print(f"{n}: 기존 {len(base)} + 새 문제 {len(add)} = {len(allq)} | 초급 {lv.count(1)} 중급 {lv.count(2)} 고급 {lv.count(3)} | 문제줄 오류 {bad}")
