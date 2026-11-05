#!/usr/bin/env python3
"""게임 고유번호 관리. 번호는 game_numbers.json(파일 이름 → 번호)에 저장하고, 한 번 정한 번호는 바꾸지 않아요.
새 게임(시작 화면 GAMES, 같이 하기 set30.py GAMES)은 다음 번호를 받아요.
시작 화면(index.html)에는 /*NUM*/ … /*/NUM*/ 사이에 번호표와 같이 하기 게임 목록을 적어 넣어요(번호로 검색하려고).
사용: py gamenum.py  (ship.py와 set30.py가 자동으로 불러요)"""
import os, re, json
DEV = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(DEV, "..", ".."))
JP = os.path.join(DEV, "game_numbers.json")

def index_games():
    s = open(os.path.join(REPO, "index.html"), encoding="utf-8").read()
    m = re.search(r'const GAMES = \[\n(.*?)\n\];', s, re.S)
    return [json.loads(row.rstrip(",")) for row in m.group(1).split("\n") if row.strip().startswith("[")]

def net_games():
    s = open(os.path.join(DEV, "set30.py"), encoding="utf-8").read()
    m = re.search(r'^GAMES = (\[.*?\]\])\n', s, re.S | re.M)
    return json.loads(m.group(1))

def ensure():
    nums = json.load(open(JP, encoding="utf-8")) if os.path.exists(JP) else {}
    nxt = max(nums.values(), default=0) + 1
    for row in index_games() + net_games():
        if row[0] not in nums: nums[row[0]] = nxt; nxt += 1
    json.dump(nums, open(JP, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=False)
    p = os.path.join(REPO, "index.html"); s = open(p, encoding="utf-8").read()
    net = [[g[0], g[1], g[2], nums[g[0]]] for g in net_games()]
    block = "/*NUM*/const NUM = " + json.dumps(nums, ensure_ascii=False, separators=(",", ":")) + ", NETG = " + json.dumps(net, ensure_ascii=False, separators=(",", ":")) + ";/*/NUM*/"
    s2 = re.sub(r'/\*NUM\*/.*?/\*/NUM\*/', lambda m: block, s, flags=re.S) if "/*NUM*/" in s else s.replace("const GROUPS = [", block + "\nconst GROUPS = [", 1)
    if s2 != s: open(p, "w", encoding="utf-8").write(s2)
    return nums

if __name__ == "__main__":
    n = ensure(); print("게임 번호", len(n), "개 (마지막", max(n.values()), "번)")
