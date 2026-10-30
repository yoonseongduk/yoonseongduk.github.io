import sys, random, re, glob
sys.path.insert(0, ".")
import mkquiz
random.seed(11)
DROP = set("되 말 요 자 굴 벌판 파도 소슬바람 수달 김치 감자 고구마 호박 단오 약과 강정 홍시 두부 간장 한복 농악 옹기 고무신 배추 호두 고명 양념 밑반찬 수정과 식혜 미숫가루 조청 대문 장터 고무줄놀이 송편 숭늉 사립문 장독대 툇마루 이웃사촌 붙임성 도마".split())
rows = []; seen_w = set(); seen_m = set()
for f in sorted(glob.glob("pk[1-6].txt")):
    for l in open(f, encoding="utf-8").read().split("\n"):
        if not l.strip(): continue
        p = l.split("|"); assert len(p) == 4, (f, l)
        w, cat, m, ex = p
        if w in DROP or m == "-" or w in seen_w or m in seen_m: continue
        if "모양" in m[-4:] or "소리" in m[-4:] or w.endswith(("하다",)) is False and re.search(r"(모양|소리)$", m): cat = "소리·모양"
        seen_w.add(w); seen_m.add(m); rows.append((w, cat, m, ex))
print(len(rows))
by = {}
for r in rows: by.setdefault(r[1], []).append(r)
def pick(pool, ans, key):
    c = list({x[key] for x in pool if x[key] != ans}); return random.sample(c, 3)
data = []
for w, cat, m, ex in rows:
    pool = by[cat] if len(by[cat]) >= 8 else rows
    note = f"{w} = {m}" + (f" · 예문: {ex.replace('{','').replace('}','')}" if ex != "-" else "")
    data.append([f"‘{w}’의 뜻은?", m, pick(pool, m, 2), cat, note])
    data.append([f"‘{m}’을(를) 뜻하는 순우리말은?", w, pick(pool, w, 0), cat, note])
    mt = re.search(r"\{([^}]+)\}", ex)
    if ex != "-" and mt and mt.group(1) == w:
        data.append([ex.replace(mt.group(0), "（　　）") + f"  (뜻: {m})", w, pick(pool, w, 0), cat, note])
print(len(data))
mkquiz.make("out/purekorean-quiz.html", "순우리말 퀴즈", "🌾", 130, "purekorean-quiz-best-v1",
    "예쁜 순우리말의 뜻을 맞히고, 뜻에 맞는 낱말과 빈칸에 알맞은 낱말을 골라요. 위쪽 버튼으로 분야를 고를 수 있어요.", data, "", qsize="clamp(1.35rem,6.4vw,1.9rem)")
