# 노노그램 그림을 프로그램으로 대량 생성한다(몬스터·문양·눈송이). 결과는 nonogram_gen.json 에 저장하고 nonogram_pics.py 가 화면에 넣는다.
# 사용: python3 nonogram_gen.py            → 목표 개수만큼 만들어 data/nonogram-gen.json 저장(같은 씨앗이면 항상 같은 결과)
#       python3 nonogram_gen.py --verify   → 저장된 그림이 모두 "추측 없이 풀리는지" 다시 검사
# 통과 기준: 줄 단위 논리(각 줄에서 확실한 칸 채우기)만으로 끝까지 풀리는 퍼즐 = 정답이 하나뿐이고 추측이 필요 없는 퍼즐.
import sys, json, random, functools, itertools, os

PALC = "royg bcknps".replace(" ", "")  # 색 글자(w 흰색은 눈에만 써요)

@functools.lru_cache(maxsize=None)
def arrangements(n, clue):  # 한 줄(길이 n)에 단서 clue 를 놓는 모든 방법(비트 튜플)
    ks = [] if clue == (0,) else list(clue)
    out = []
    def rec(i, k, cur):
        if k == len(ks):
            out.append(tuple(cur + [0] * (n - len(cur)))); return
        need = sum(ks[k:]) + len(ks) - k - 1
        for s in range(i, n - need + 1):
            rec(s + ks[k] + 1, k + 1, cur + [0] * (s - len(cur)) + [1] * ks[k])
    rec(0, 0, [])
    return [o for o in out if len(o) == n]

def runs(line):
    r, c = [], 0
    for v in line:
        if v: c += 1
        elif c: r.append(c); c = 0
    if c: r.append(c)
    return tuple(r) or (0,)

def line_solvable(g):  # g: 0/1 격자. 줄 논리만으로 끝까지 풀리면 True
    n = len(g)
    rc = [runs(r) for r in g]; cc = [runs([g[y][x] for y in range(n)]) for x in range(n)]
    st = [[-1] * n for _ in range(n)]   # -1 모름, 0 빈칸, 1 칠함
    changed = True
    while changed:
        changed = False
        for horizontal in (True, False):
            for i in range(n):
                clue = rc[i] if horizontal else cc[i]
                cur = st[i] if horizontal else [st[y][i] for y in range(n)]
                if -1 not in cur: continue
                ok = [a for a in arrangements(n, clue) if all(c == -1 or c == a[k] for k, c in enumerate(cur))]
                if not ok: return False
                for k in range(n):
                    if cur[k] == -1:
                        v = ok[0][k]
                        if all(a[k] == v for a in ok):
                            if horizontal: st[i][k] = v
                            else: st[k][i] = v
                            changed = True
    return all(st[y][x] != -1 for y in range(n) for x in range(n))

# ── 모양 만들기 ─────────────────────────────────────────
def components(g):  # 칠한 칸 덩어리 수(8방향 이웃). 몬스터는 한 덩어리여야 그림처럼 보여요
    n = len(g); seen = set(); cnt = 0
    for y in range(n):
        for x in range(n):
            if g[y][x] and (y, x) not in seen:
                cnt += 1; stack = [(y, x)]; seen.add((y, x))
                while stack:
                    cy, cx = stack.pop()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < n and 0 <= nx < n and g[ny][nx] and (ny, nx) not in seen: seen.add((ny, nx)); stack.append((ny, nx))
    return cnt

def blob_monster(n, rnd):  # 좌우 대칭 몬스터: 무작위 점을 뭉쳐 몸을 만들고 눈·무늬를 넣는다
    half = (n + 1) // 2
    for _ in range(40):
        g = [[1 if rnd.random() < 0.62 else 0 for _ in range(n)] for _ in range(n)]
        for y in range(n):                       # 왼쪽을 오른쪽에 거울처럼 복사
            for x in range(half): g[y][n - 1 - x] = g[y][x]
        for _ in range(2):                       # 이웃 다수결로 매끈한 덩어리로
            h = [r[:] for r in g]
            for y in range(n):
                for x in range(n):
                    s = sum(g[yy][xx] for yy in range(max(0, y - 1), min(n, y + 2)) for xx in range(max(0, x - 1), min(n, x + 2)))
                    h[y][x] = 1 if s >= 5 else 0
            g = h
            for y in range(n):
                for x in range(half): g[y][n - 1 - x] = g[y][x]
        tot = sum(map(sum, g))
        rows = sum(1 for r in g if any(r)); cols = sum(1 for x in range(n) if any(g[y][x] for y in range(n)))
        if 0.38 * n * n <= tot <= 0.78 * n * n and rows >= n - 1 and cols >= n - 1 and components(g) == 1: return g
    return None

def mandala(n, rnd):  # 위아래·좌우 대칭 문양
    q = (n + 1) // 2
    for _ in range(40):
        quarter = [[1 if rnd.random() < 0.55 else 0 for _ in range(q)] for _ in range(q)]
        g = [[0] * n for _ in range(n)]
        for y in range(q):
            for x in range(q):
                for yy, xx in ((y, x), (y, n - 1 - x), (n - 1 - y, x), (n - 1 - y, n - 1 - x)): g[yy][xx] = quarter[y][x]
        tot = sum(map(sum, g))
        if 0.4 * n * n <= tot <= 0.75 * n * n and all(any(r) for r in g): return g
    return None

def snowflake(n, rnd):  # 대각선 대칭 + 좌우 대칭(눈송이 같은 문양)
    q = (n + 1) // 2
    for _ in range(40):
        t = [[0] * q for _ in range(q)]
        for y in range(q):
            for x in range(y, q):
                t[y][x] = t[x][y] = 1 if rnd.random() < 0.55 else 0
        g = [[0] * n for _ in range(n)]
        for y in range(q):
            for x in range(q):
                for yy, xx in ((y, x), (y, n - 1 - x), (n - 1 - y, x), (n - 1 - y, n - 1 - x)): g[yy][xx] = t[y][x]
        tot = sum(map(sum, g))
        if 0.4 * n * n <= tot <= 0.75 * n * n and all(any(r) for r in g): return g
    return None

def colorize(g, kind, rnd):  # 0/1 격자 → 색 글자 줄. 몬스터는 눈·포인트 색을 더한다
    n = len(g)
    body = rnd.choice("royg" + "bcns" + "ps")
    acc = rnd.choice([c for c in "royggbckpn" if c != body])
    rows = [["." if not v else body for v in r] for r in g]
    cells = [(y, x) for y in range(n) for x in range(n) if g[y][x]]
    if kind == "blob":
        up = [(y, x) for (y, x) in cells if y < n // 2 and x < n // 2 and x > 0]
        if up:
            y, x = rnd.choice(up); eye = rnd.choice("kk" + "w")
            rows[y][x] = eye
            if g[y][n - 1 - x]: rows[y][n - 1 - x] = eye
        for (y, x) in cells:
            if x < (n + 1) // 2 and rnd.random() < 0.14 and rows[y][x] == body:
                rows[y][x] = acc
                if g[y][n - 1 - x]: rows[y][n - 1 - x] = acc
    else:
        for (y, x) in cells:
            if (x + y) % 2 == 0 and rnd.random() < 0.28 and rows[y][x] == body: rows[y][x] = acc
        for (y, x) in cells:
            if y < (n + 1) // 2 and x < (n + 1) // 2 and rnd.random() < 0.12 and rows[y][x] == body:
                for yy, xx in ((y, x), (y, n - 1 - x), (n - 1 - y, x), (n - 1 - y, n - 1 - x)):
                    if g[yy][xx]: rows[yy][xx] = acc
    return ["".join(r) for r in rows]

ADJ = ["졸린", "화난", "웃는", "수줍은", "용감한", "배고픈", "반짝이는", "작은", "큰", "씩씩한", "엉뚱한", "느긋한", "장난꾸러기", "똑똑한", "착한", "신나는", "조용한", "빠른", "포근한", "씽씽", "깜찍한", "듬직한", "아기", "꼬마", "슈퍼", "비밀의", "행운의", "춤추는", "노래하는", "달리는"]
NOUN_BLOB = [("도깨비", "👹"), ("외계인", "👽"), ("몬스터", "👾"), ("로봇", "🤖"), ("유령", "👻"), ("문어", "🐙"), ("용", "🐲"), ("공룡", "🦖"), ("고슴도치", "🦔"), ("올빼미", "🦉"), ("곰돌이", "🐻"), ("토끼", "🐰"), ("여우", "🦊"), ("거북이", "🐢"), ("부엉이", "🦉"), ("개구리", "🐸")]
NOUN_PAT = [("문양", "🔷"), ("무늬", "🔶"), ("장식", "💠"), ("보석", "💎"), ("타일", "🟦"), ("만화경", "🔮"), ("방석", "🧶"), ("수놓은 천", "🧵")]
NOUN_SNOW = [("눈송이", "❄️"), ("눈꽃", "❄️"), ("별빛", "✨"), ("결정", "💠")]

def gen(target):  # target = {5: 개수, 8: …}
    out = {}
    rnd = random.Random(20261120)
    seen = set(); used_names = set()
    for n, want in target.items():
        lst = []; tries = 0
        while len(lst) < want and tries < want * 400:
            tries += 1
            kind = rnd.choices(["blob", "mandala", "snow"], weights=[5, 3, 2])[0]
            g = {"blob": blob_monster, "mandala": mandala, "snow": snowflake}[kind](n, rnd)
            if g is None: continue
            key = json.dumps(g)
            if key in seen or not line_solvable(g): continue
            seen.add(key)
            rows = colorize(g, "blob" if kind == "blob" else "pat", rnd)
            pool = NOUN_BLOB if kind == "blob" else NOUN_PAT if kind == "mandala" else NOUN_SNOW
            for _ in range(200):
                noun, emo = rnd.choice(pool); name = rnd.choice(ADJ) + " " + noun
                if name not in used_names: break
            else: name = f"{noun} {len(used_names) + 1}"
            used_names.add(name); lst.append({"n": name, "e": emo, "g": rows})
        out[str(n)] = lst
        print(f"{n}×{n}: {len(lst)}개 만듦 (시도 {tries}번)", flush=True)
    return out

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "nonogram-gen.json")
    if "--verify" in sys.argv:
        data = json.load(open(path, encoding="utf-8")); bad = 0
        for n, lst in data.items():
            for p in lst:
                g = [[0 if c == "." else 1 for c in r] for r in p["g"]]
                if len(g) != int(n) or any(len(r) != int(n) for r in g) or not line_solvable(g): bad += 1; print("❌", n, p["n"])
        print("검사 끝: 문제", bad, "개 /", sum(len(v) for v in data.values()), "개"); sys.exit(1 if bad else 0)
    tgt = {5: 45, 8: 260, 10: 320, 15: 320}
    if "--small" in sys.argv: tgt = {5: 5, 8: 8, 10: 8, 15: 8}
    data = gen(tgt)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("저장:", path, sum(len(v) for v in data.values()), "개")
