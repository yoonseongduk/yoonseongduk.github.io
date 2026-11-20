#!/usr/bin/env python3
"""기능 색인(기능_색인.md) 점검: 표의 `구현 위치`에 적힌 파일·폴더가 실제로 있는지, 시작 화면 게임 수 확인.
사용: py featcheck.py"""
import os, re, sys, glob
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")) + os.sep
t = open(R + "기능_색인.md", encoding="utf-8").read()
bad = 0; ids = []; n = 0
for line in t.splitlines():
    if not re.match(r"^\| [CG]-", line): continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    ids.append(cells[0])
    where = cells[3] if cells[0].startswith("C-") else cells[4]   # 1부는 4번째 칸, 2부는 5번째 칸이 구현 위치
    cand = re.findall(r"`([^`]+)`", where) + re.findall(r"[\w\-./]+\.(?:html|js|py|json|svg|webp|txt|css)\b", where)
    for p in cand:
        p = p.split("(")[0].strip()
        if "~" in p or "*" in p: continue
        if re.search(r"[가-힣]", p.replace("올리기.bat", "")) and not p.endswith(".bat"): continue
        if not re.search(r"[/.]", p): continue
        n += 1
        if not glob.glob(R + p.replace("\\", "/")) and not os.path.exists(R + p): bad += 1; print("❌ 없는 위치:", cells[0], p)

# 시작 화면의 모든 게임(번호)이 2부에 1줄 이상 있는지
import json
nums = json.load(open(R + "tools/dev/game_numbers.json", encoding="utf-8")); idx = open(R + "index.html", encoding="utf-8").read()
have = {int(i.split("-")[1]) for i in ids if i.startswith("G-")}
miss = [f for f, n in nums.items() if n not in have and f'"{f}"' in idx and not f.startswith("net-")]
if miss: bad += 1; print("❌ 2부에 없는 게임:", miss)
dup = {i for i in ids if ids.count(i) > 1}
if dup: bad += 1; print("❌ 중복 ID:", sorted(dup))
print(f"기능 {len(ids)}개 / 확인한 위치 {n}곳 / 문제 {bad}건")
sys.exit(1 if bad else 0)
