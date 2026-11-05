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

def quiz_counts():
    """퀴즈마다 문제 수(시작 화면 카드·같이 하기 목록에 표시). 문제 목록 const D가 있으면 그 개수, 특별한 퀴즈는 따로 세요."""
    out = {}
    for r in index_games():
        if r[4] != "quiz": continue
        h = open(os.path.join(REPO, r[0]), encoding="utf-8").read()
        try:
            if "const D = [" in h:
                i = h.index("const D = ["); j = i + re.search(r"\];\r?\n", h[i:]).start(); out[r[0]] = f"{len(json.loads(h[i + 10:j + 1])):,}문제"
            elif r[0] == "capital-quiz.html":
                i = h.index("const FL = {"); out[r[0]] = f"{h[i:h.index('};', i)].count(':'):,}개 나라"
            elif r[0] == "chosung-quiz.html":
                i = h.index("const WORDS = {"); blk = h[i:h.index("};", i)]; out[r[0]] = f"{sum(len(v.split()) for v in re.findall(r':\s*\"([^\"]+)\"', blk)):,}낱말"
            elif r[0] in ("hanja-write.html", "hanja-today.html"):
                out[r[0]] = f"한자 {len(json.load(open(os.path.join(REPO, 'data/hanja.json'), encoding='utf-8'))):,}자"
            elif r[0] == "word-chain.html":
                n = sum(1 for _ in open(os.path.join(REPO, "data/words-ko.txt"), encoding="utf-8")); out[r[0]] = f"사전 {n // 10000}만 낱말"
        except Exception as e:
            print("문제 수 세기 실패", r[0], e)
    return out

def ensure():
    nums = json.load(open(JP, encoding="utf-8")) if os.path.exists(JP) else {}
    nxt = max(nums.values(), default=0) + 1
    for row in index_games() + net_games():
        if row[0] not in nums: nums[row[0]] = nxt; nxt += 1
    json.dump(nums, open(JP, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=False)
    p = os.path.join(REPO, "index.html"); s = open(p, encoding="utf-8").read()
    net = [[g[0], g[1], g[2], nums[g[0]]] for g in net_games()]
    # BUZZ: 같이 하기 퀴즈 버저로도 할 수 있는 퀴즈(문제 목록 const D가 들어 있는 퀴즈) — 시작 화면 카드에 🔔 표시
    buzz = [r[0] for r in index_games() if r[4] == "quiz" and "const D = [" in open(os.path.join(REPO, r[0]), encoding="utf-8").read()]
    qc = quiz_counts()
    block = "/*NUM*/const QCNT = " + json.dumps(qc, ensure_ascii=False, separators=(",", ":")) + ", NUM = " + json.dumps(nums, ensure_ascii=False, separators=(",", ":")) + ", NETG = " + json.dumps(net, ensure_ascii=False, separators=(",", ":")) + ", BUZZ = " + json.dumps(buzz, ensure_ascii=False, separators=(",", ":")) + ";/*/NUM*/"
    s2 = re.sub(r'/\*NUM\*/.*?/\*/NUM\*/', lambda m: block, s, flags=re.S) if "/*NUM*/" in s else s.replace("const GROUPS = [", block + "\nconst GROUPS = [", 1)
    if s2 != s: open(p, "w", encoding="utf-8").write(s2)
    return nums

if __name__ == "__main__":
    n = ensure(); print("게임 번호", len(n), "개 (마지막", max(n.values()), "번)")
