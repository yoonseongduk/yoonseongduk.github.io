#!/usr/bin/env python3
"""폰에서 '📋 내가 고친 획순 복사'로 복사한 JSON을 data/stroke-fix.json 에 합쳐요.
사용법: 복사한 내용을 아무 파일(예: fix.txt)에 붙여 넣고  python merge_stroke_fix.py fix.txt"""
import json, sys
new = json.load(open(sys.argv[1], encoding="utf-8-sig"))      # 메모장이 붙이는 BOM 표시도 괜찮아요
p = "../../data/stroke-fix.json"
old = json.load(open(p, encoding="utf-8"))
old.update(new)
open(p, "w", encoding="utf-8").write(json.dumps(old, ensure_ascii=False, separators=(",", ":")))
print("합친 글자:", len(new), "/ 전체 수정 글자:", len(old))
