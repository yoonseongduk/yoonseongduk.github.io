#!/usr/bin/env python3
"""릴리스 노트를 data/release-notes.json 맨 위에 추가한다(새 버전 확인 카드의 '업데이트 내용'에 보여요).
사용: py tools/release.py "제목" "바뀐 점 1" "바뀐 점 2" ...
번호는 오늘 날짜-순번(예: 2026.11.11-5)으로 자동 정해요. 올리기 전에 한 번 실행하면 돼요(올리기.bat 이 sw.js 도 다시 만들어요)."""
import sys, os, json, datetime
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")) + os.sep
P = R + "data/release-notes.json"
if len(sys.argv) < 3: sys.exit("사용: py tools/release.py \"제목\" \"바뀐 점 1\" [\"바뀐 점 2\" ...]")
kst = datetime.timezone(datetime.timedelta(hours=9)); today = datetime.datetime.now(kst).strftime("%Y-%m-%d")
notes = json.load(open(P, encoding="utf-8"))
n = sum(1 for x in notes if x["date"] == today) + 1
e = {"ver": today.replace("-", ".") + "-" + str(n), "date": today, "title": sys.argv[1], "items": sys.argv[2:]}
notes.insert(0, e); notes = notes[:30]
open(P, "w", encoding="utf-8", newline="\n").write("[\n" + ",\n".join("  " + json.dumps(x, ensure_ascii=False) for x in notes) + "\n]\n")
print("릴리스 추가:", e["ver"], e["title"])
