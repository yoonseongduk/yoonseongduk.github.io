# 생물 퀴즈 사진 붙이기: bio_wiki.json(bio_build.py 결과) + bio_photo_tpl.js → 저장소 맨 위 bio-photo.js,
#   그리고 퀴즈 5개 화면 끝에 online.js·bio-photo.js 를 넣어요(여러 번 돌려도 같아요, qlevel.py 가 마지막에 자동 실행).
import json, os, re
R = "../../"
if not os.path.exists("bio_wiki.json"): raise SystemExit("bio_wiki.json 이 없어요. 먼저 py bio_build.py")
M = json.load(open("bio_wiki.json", encoding="utf-8"))
js = open("bio_photo_tpl.js", encoding="utf-8").read()
js = re.sub(r"/\*MAP\*/.*?/\*/MAP\*/", lambda m: "/*MAP*/" + json.dumps(M, ensure_ascii=False, separators=(",", ":")) + "/*/MAP*/", js, flags=re.S)
open(R + "bio-photo.js", "w", encoding="utf-8").write(js)
TAG = '<script src="bio-photo.js"></script>'
for f in M:
    p = R + f; h = open(p, encoding="utf-8", newline="").read()
    if TAG in h: continue
    add = ("" if 'src="online.js"' in h else '<script src="online.js"></script>') + TAG
    i = h.rindex("</body>"); h = h[:i] + add + "\n" + h[i:]
    open(p, "w", encoding="utf-8", newline="").write(h)
print("생물 사진:", {f: len(v) for f, v in M.items()})
