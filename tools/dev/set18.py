import sys, csv, ast, collections, re
sys.path.insert(0, ".")
from mkquiz import make
rows = list(csv.DictReader(open("hj/hanja.csv", encoding="utf-8")))
GROUP = {"8급": "6급", "7급Ⅱ": "6급", "7급": "6급", "6급Ⅱ": "6급", "6급": "6급", "5급Ⅱ": "5급", "5급": "5급", "4급Ⅱ": "4급", "4급": "4급", "3급Ⅱ": "3급", "3급": "3급", "2급": "2급", "1급": "1급"}
ORDER = ["6급", "5급", "4급", "3급", "2급", "1급"]
def ans(m):
    prs = ast.literal_eval(m); out = []
    for hun, um in prs:
        clean = lambda t: re.sub(r"\[[^\]]*\]", "", t).strip()
        out.append("·".join(clean(h) for h in hun[:2]) + " " + "·".join(clean(u) for u in um[:1]))
    return " / ".join(out[:2])
D = []; seen = set()
for r in rows:
    g = GROUP.get(r["level"])
    if not g or r["hanja"] in seen: continue
    seen.add(r["hanja"])
    D.append([r["hanja"], ans(r["meaning"]), [], g, f'{r["level"]} · 부수 {r["radical"]} · 총 {r["total_strokes"]}획'])
D.sort(key=lambda x: ORDER.index(x[3]))
print(len(D), collections.Counter(d[3] for d in D))
print(max(len(d[1]) for d in D), [d for d in D if len(d[1]) > 14][:5])
make("out/hanja-quiz.html", "한자 급수 퀴즈", "🈶", 8, "hanja-grade-quiz-best-v1",
     "한자를 보고 <b>뜻(훈)과 소리(음)</b>를 맞혀 보세요. 위의 <b>6급~1급</b> 버튼으로 급수를 고를 수 있어요. 한자 3,500자(한국어문회 배정한자 8급~1급)가 들어 있고, 6급은 8급~6급 한자 300자예요. 자료: 사단법인 한국어문회 배정한자.",
     D, label="이 한자의 뜻과 음은?", qsize="clamp(4rem,24vw,6rem)")
