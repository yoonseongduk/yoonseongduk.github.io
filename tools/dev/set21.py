import sys, random
sys.path.insert(0, ".")
exec(open("mkquiz.py", encoding="utf-8").read().split("if __name__")[0]) if False else None
import mkquiz
from jlpt_data import J
from jlpt_more1 import J2
from jlpt_more2 import J3
from jlpt_more3 import J4
for _k, _v in J4.items(): J3[_k] = J3.get(_k, "") + "\n" + _v
from jlpt_more4 import J5
for _k, _v in J5.items(): J3[_k] = J3.get(_k, "") + "\n" + _v
from jlpt_more5 import J6
for _k, _v in J6.items(): J3[_k] = J3.get(_k, "") + "\n" + _v
_seen = set(); _J = {}
for lv in ["N5", "N4", "N3", "N2", "N1"]:
    lines = [l for l in J[lv].split("\n") if l.strip()] + [l for l in J2.get(lv, "").split("\n") if l.strip()] + [l for l in J3.get(lv, "").split("\n") if l.strip()]
    out = []; _m = set()
    for l in lines:
        f = l.split("|")
        if f[0] in _seen or f[2] in _m: continue
        _seen.add(f[0]); _m.add(f[2]); out.append(l)
    _J[lv] = "\n".join(out)
J = _J
import json as _j
K = _j.load(open("kh_all5.json", encoding="utf-8"))
random.seed(7)
# JLPT
import re
data = []
HAS_KANJI = re.compile(r"[\u4e00-\u9fff]")
for lv in ["N5", "N4", "N3", "N2", "N1"]:
    ws = []
    for line in J[lv].split("\n"):
        w, r, m, ex, tr = line.split("|")
        if w in {x[0] for x in ws} or any(w == x[0] for l2 in J for x in []): continue
        ws.append((w, r, m, ex, tr))
    ms = [x[2] for x in ws]; fs = [x[0] if x[0] == x[1] else f"{x[0]} ({x[1]})" for x in ws]; rs = sorted({x[1] for x in ws})
    for w, r, m, ex, tr in ws:
        f = w if w == r else f"{w} ({r})"
        note = f"{f} = {m} · 예문: {ex} {tr}"
        pick = lambda pool, ans: random.sample([p for p in pool if p != ans], 3)
        data.append([f + "  — 뜻은?", m, pick(ms, m), lv, note])
        data.append([f"‘{m}’을(를) 일본어로 하면?", f, pick(fs, f), lv, note])
        if HAS_KANJI.search(w) and w != r:
            data.append([f"{w}  — 읽는 법은?", r, pick(rs, r), lv, note])
mkquiz.make("out/jlpt-quiz.html", "일본어 단어 퀴즈", "🇯🇵", 350, "jlpt-quiz-best-v1",
    "JLPT 일본어능력시험 N5(쉬움)~N1(어려움) 수준의 단어를 뜻 맞히기, 일본어 고르기, 읽는 법 맞히기로 풀어요. 위쪽 버튼으로 급수를 골라요.", data, "", qsize="clamp(1.5rem,7vw,2.1rem)")
# 한국사
kd = [[q, a, w, c, n] for q, a, w, c, n in K]
mkquiz.make("out/korean-history-quiz.html", "한국사 퀴즈", "🏯", 30, "korean-history-quiz-best-v1",
    "선사 시대부터 현대까지 시대별로 한국사 문제를 풀어요. 위쪽 버튼으로 시대를 골라요.", kd, "", qsize="clamp(1.3rem,6vw,1.8rem)")
# 한자 사자성어
rows = [l.split("|") for l in open("idiom_data.txt", encoding="utf-8").read().split("\n") if l.strip()]
allh = [r[1] for r in rows]
chars = sorted({c for h in allh for c in h})
hd = []
for ko, h, mean, origin, ex in rows:
    note = f"{h} ({ko}) · {origin}"
    others = [x for x in allh if x != h]
    hd.append([mean, h, random.sample(others, 3), "뜻 보고 한자 고르기", note])
    hd.append([f"‘{ko}’의 한자는?", h, random.sample(others, 3), "한글 보고 한자 고르기", note])
    if len(h) == 4:
        for k in range(4):
            blank = h[:k] + "□" + h[k + 1:]
            wr = random.sample([c for c in chars if c not in h], 3)
            hd.append([f"{blank}  ({mean})", h[k], wr, "빈칸 한자 채우기", f"{h} ({ko}) · {origin}"])
mkquiz.make("out/hanja-idiom-quiz.html", "한자 사자성어 퀴즈", "📜", 20, "hanja-idiom-quiz-best-v1",
    "사자성어의 뜻을 보고 알맞은 한자를 고르거나, 빈칸에 들어갈 한자를 맞혀요.", hd, "", qsize="clamp(1.4rem,7vw,2rem)")
