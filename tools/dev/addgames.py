#!/usr/bin/env python3
"""시작 화면(index.html)의 GAMES 목록 끝에 새 게임을 추가한다. 사용법: addgames.py '<JSON 목록: [파일,아이콘,제목,설명,분류]>' [새 분류 JSON]"""
import os
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import sys, json, re
p = REPO + "/index.html"
s = open(p, encoding='utf-8').read()
games = json.loads(sys.argv[1])
if len(sys.argv) > 2:                                   # 새 분류가 필요하면 GROUPS 앞쪽에 넣는다 (생활은 맨 뒤)
    for g in json.loads(sys.argv[2]):
        if f'id: "{g["id"]}"' not in s:
            row = f'  {{ id: "{g["id"]}", n: "{g["n"]}", e: "{g["e"]}", h: {g["h"]} }},\n'
            s = s.replace('  { id: "life"', row + '  { id: "life"', 1)
m = re.search(r'const GAMES = \[\n(.*?)\n\];', s, re.S); assert m
body = m.group(1)
add = ''
for f, e, t, d, g in games:
    if f'"{f}"' in body: continue
    add += f',\n  ["{f}", "{e}", "{t}", "{d}", "{g}"]'
s = s.replace(m.group(0), 'const GAMES = [\n' + body + add + '\n];', 1)
open(p, 'w', encoding='utf-8').write(s)
print('추가된 게임', add.count('["'))
