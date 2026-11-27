# 비슷한 게임 합치기 적용기(merged.json). ship.py 가 자동으로 실행해요(여러 번 돌려도 같아요).
#   ① index.html 시작 화면에서 합쳐지는 게임 카드를 빼고(빼기 전 카드는 merged_cards.json 에 보관 → 되돌릴 때 사용),
#      남는 게임 설명 끝에 "🔀 … 모드도 있어요"를 붙이고, /*MERGED*/ 칸에 옛 파일→새 파일·옛 이름·옛 번호를 넣어요
#      (즐겨찾기·최근 목록이 새 게임으로 이어지고, 옛 이름·번호로 검색해도 찾아져요).
#   ② home.js 의 /*MODES*/ 칸에 모드 묶음을 넣어요 → 각 화면 제목 아래에 모드 단추가 나와요.
import json, os, re
R = "../../"
cfg = json.load(open("merged.json", encoding="utf-8"))
groups = cfg["groups"]
merged = {f: g[0][0] for g in groups for f, _ in g[1:]}
nums = json.load(open("game_numbers.json", encoding="utf-8"))
P = "merged_cards.json"
keep = json.load(open(P, encoding="utf-8")) if os.path.exists(P) else {}
idx = open(R + "index.html", encoding="utf-8").read()
gi = idx.index("const GAMES = [")
head, body = idx[:gi], idx[gi:]
end = body.index("\n];") if "\n];" in body else body.index("];")
games, tail = body[:end], body[end:]
lines = games.split("\n")
out = []
for ln in lines:
    m = re.match(r'\s*\["([^"]+\.html)",', ln)
    if m and m.group(1) in merged:
        f = m.group(1)
        if f not in keep: keep[f] = ln.strip().rstrip(",")
        continue
    out.append(ln)
games = "\n".join(out)
games = re.sub(r",(\s*)$", r"\1", games)   # 마지막 줄 쉼표 정리
# 남는 게임 설명에 모드 안내 붙이기
for g in groups:
    main, others = g[0][0], [l for _, l in g[1:]]
    note = " 🔀 " + "·".join(others) + " 모드도 있어요."
    def fix(m):
        desc = m.group(2)
        if "🔀" in desc: desc = desc[:desc.index(" 🔀")]
        return m.group(1) + desc + note + m.group(3)
    games = re.sub(r'(\["' + re.escape(main) + r'", "[^"]*", "[^"]*", ")([^"]*)(")', fix, games, count=1)
alias = []
for f, to in merged.items():
    t = re.search(r'"[^"]*", "[^"]*", "([^"]*)"', keep.get(f, ""))
    alias.append([t.group(1) if t else f, nums.get(f, 0), to])
block = "/*MERGED*/const MERGED = " + json.dumps(merged, ensure_ascii=False) + ", MALIAS = " + json.dumps(alias, ensure_ascii=False) + ";/*/MERGED*/"
idx = head + games + tail
if "/*MERGED*/" in idx: idx = re.sub(r"/\*MERGED\*/.*?/\*/MERGED\*/", lambda m: block, idx, flags=re.S)
else: idx = idx.replace("/*ADDED*/", block + "\n/*ADDED*/", 1)
open(R + "index.html", "w", encoding="utf-8").write(idx)
json.dump(keep, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# home.js 모드 묶음
hj = open(R + "home.js", encoding="utf-8").read()
mb = "/*MODES*/var MODES = " + json.dumps(groups, ensure_ascii=False) + ";/*/MODES*/"
hj = re.sub(r"/\*MODES\*/.*?/\*/MODES\*/", lambda m: mb, hj, flags=re.S)
open(R + "home.js", "w", encoding="utf-8").write(hj)
print("합친 게임:", len(merged), "개 → 시작 화면에서 빠짐, 모드 묶음", len(groups), "개")
