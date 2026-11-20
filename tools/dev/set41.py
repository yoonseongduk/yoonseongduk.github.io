#!/usr/bin/env python3
"""신조어 퀴즈(newword-quiz.html) 생성: newword_data.txt(## 초급/중급/고급 구역, 줄 `문제|정답|오답1|오답2|오답3|해설|시기 분류(선택)`)를 읽어 퀴즈를 만들고
등급 파일(qlevel/newword-quiz.json)을 써요. 사용: py set41.py → py ship.py '[["newword-quiz.html","💬","신조어 퀴즈","최근 유행어·줄임말의 뜻을 맞혀요.","quiz"]]' (이미 등록돼 있으면 파일만 갱신) → py qlevel.py newword-quiz"""
import json, os, re, mkquiz
SECT = {"초급": 1, "중급": 2, "고급": 3}
data, lv, cur, seen = [], {}, 0, set()
for ln, l in enumerate(open("newword_data.txt", encoding="utf-8"), 1):
    l = l.rstrip("\r\n"); m = re.match(r"^##\s*(초급|중급|고급)", l)
    if m: cur = SECT[m.group(1)]; continue
    if not l.strip() or l.startswith("#"): continue
    p = [x.strip() for x in l.split("|")]
    assert len(p) in (6, 7) and all(p) and cur, f"{ln}줄 형식 오류: {l[:40]}"
    q, a, w, note = p[0], p[1], p[2:5], p[5]; era = p[6] if len(p) == 7 else "신조어"   # 7번째 칸 = 시기 분류(최신 2025~·2023~24·2020~22·오래 쓰는 말)
    assert a not in w and len(set(w)) == 3, f"{ln}줄 보기 겹침"
    if q in seen: continue
    seen.add(q); data.append([q, a, w, era, note]); lv[q] = cur
os.makedirs("out", exist_ok=True); os.makedirs("qlevel", exist_ok=True)
json.dump(lv, open("qlevel/newword-quiz.json", "w", encoding="utf-8"), ensure_ascii=False)
mkquiz.make("out/newword-quiz.html", "신조어 퀴즈", "💬", 285, "newword-quiz-best-v1", "요즘 쓰는 신조어·줄임말의 뜻을 맞혀 보세요.", data)
print({k: list(lv.values()).count(k) for k in (1, 2, 3)})
