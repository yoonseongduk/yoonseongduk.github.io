#!/usr/bin/env python3
"""초성 퀴즈(chosung-quiz.html)의 낱말 목록을 tools/dev/chosung_words.txt(`분류|낱말|등급`, 등급 1=초급 2=중급 3=고급)에서 다시 만들어 끼워 넣어요.
낱말을 늘리려면 chosung_words.txt 에 줄을 추가하고 `py tools\\dev\\chosung_build.py` 를 실행해요(한글 2~6글자, 띄어쓰기 없음, 다른 분류와 같은 낱말 금지)."""
import os, re, json, sys
DEV = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(DEV, "..", ".."))
rows = [l.rstrip("\n").split("|") for l in open(os.path.join(DEV, "chosung_words.txt"), encoding="utf-8") if l.strip() and not l.startswith("#")]
seen = set(); out = []
for r in rows:
    assert len(r) == 3 and re.fullmatch(r"[가-힣]{2,6}", r[1]) and r[2] in ("1", "2", "3"), f"형식 오류: {r}"
    assert r[1] not in seen, f"중복 낱말: {r[1]}"; seen.add(r[1]); out.append([r[0], r[1], int(r[2])])
p = os.path.join(REPO, "chosung-quiz.html"); h = open(p, encoding="utf-8", newline="").read()
data = "/*WORDS*/const W = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";/*/WORDS*/"
if "/*WORDS*/" in h: h = re.sub(r"/\*WORDS\*/.*?/\*/WORDS\*/", lambda m: data, h, count=1, flags=re.S)
else:
    h = re.sub(r"const WORDS = \{.*?\n\};", lambda m: data, h, count=1, flags=re.S)
    h = h.replace("const ALL = Object.entries(WORDS).flatMap(([cat, ws]) => ws.split(\" \").map(w => ({ cat, w, c: cho(w) })));", "const ALL = W.map(([cat, w, l]) => ({ cat, w, c: cho(w), l }));", 1)
open(p, "w", encoding="utf-8", newline="").write(h)
print("낱말", len(out), "개 (초급", sum(1 for x in out if x[2] == 1), "중급", sum(1 for x in out if x[2] == 2), "고급", sum(1 for x in out if x[2] == 3), ") 분류", len({x[0] for x in out}), "개")
