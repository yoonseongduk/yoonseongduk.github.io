# 노노그램 그림 퍼즐의 원본 데이터 + 검사 + nonogram.html 에 넣기.
# 사용: python3 nonogram_pics.py          → 정답이 하나뿐인지·모양이 맞는지 검사하고 nonogram.html 의 그림 목록을 갱신해요.
#       python3 nonogram_pics.py --montage 파일.png → 모든 그림을 한 장으로 그려 봐요(눈으로 확인용).
# 그림 한 줄 = 글자 n개. '.' 은 빈칸, 나머지는 색깔 글자: r 빨강 o 주황 y 노랑 g 초록 b 파랑 c 하늘 k 검정 w 흰색 s 회색 n 갈색 p 분홍
# 새 그림을 넣으면 정답이 하나뿐인지 꼭 이 검사로 확인하세요(여러 개면 사람이 푼 그림이 달라질 수 있어요).
import sys, json, re, itertools

PICS = {
 5: [
  ("하트", "❤️", [".r.r.", "rrrrr", "rrrrr", ".rrr.", "..r.."]),
  ("집", "🏠", ["..r..", ".rrr.", "rrrrr", "yyyyy", "yynyy"]),
  ("나무", "🌳", ["..g..", ".ggg.", "ggggg", "..n..", "..n.."]),
  ("별", "⭐", ["..y..", "yyyyy", ".yyy.", ".yyy.", "yy.yy"]),
  ("웃는 얼굴", "😊", [".yyy.", "ykyky", "yyyyy", "ykkky", ".yyy."]),
  ("꽃", "🌸", [".ppp.", "ppypp", ".ppp.", "..g..", "..g.."]),
 ],
 8: [
  ("하트", "❤️", [".rr..rr.", "rrrrrrrr", "rrrrrrrr", "rrrrrrrr", ".rrrrrr.", "..rrrr..", "...rr...", "........"]),
  ("집", "🏠", ["...rr...", "..rrrr..", ".rrrrrr.", "rrrrrrrr", ".yyyyyy.", ".ycyynn.", ".yyyynn.", ".yyyynn."]),
  ("나무", "🌳", ["...gg...", "..gggg..", ".gggggg.", "gggggggg", ".gggggg.", "...nn...", "...nn...", "...nn..."]),
  ("물고기", "🐟", ["........", "..bbbb..", ".bbbbbb.", "b.bbkbb.", "bbbbbbbb", "b.bbbbb.", "..bbbb..", "........"]),
  ("아이스크림", "🍦", ["..pppp..", ".pppppp.", "pppppppp", "oooooooo", ".oooooo.", "..oooo..", "...oo...", "...oo..."]),
  ("해", "☀️", ["...yy...", ".y.yy.y.", "..yyyy..", "yyyyyyyy", "yyyyyyyy", "..yyyy..", ".y.yy.y.", "...yy..."]),
 ],
 10: [
  ("하트", "❤️", ["..........", ".rrr..rrr.", "rrrrrrrrrr", "rrrrrrrrrr", "rrrrrrrrrr", ".rrrrrrrr.", "..rrrrrr..", "...rrrr...", "....rr....", ".........."]),
  ("집", "🏠", ["....rr....", "...rrrr...", "..rrrrrr..", ".rrrrrrrr.", "rrrrrrrrrr", ".yyyyyyyy.", ".yccyyccy.", ".yccyyccy.", ".yyyynnyy.", ".yyyynnyy."]),
  ("나무", "🌳", ["....gg....", "...gggg...", "..gggggg..", ".gggggggg.", "...gggg...", "..gggggg..", ".gggggggg.", "....nn....", "....nn....", "....nn...."]),
  ("고양이", "🐱", ["ss......ss", "sss....sss", "ssssssssss", "ssksssskss", "ssssssssss", "ssssppssss", "ssskssksss", ".ssssssss.", "..ssssss..", ".........."]),
  ("곰", "🐻", ["nn......nn", "nnn....nnn", ".nnnnnnnn.", "nnnnnnnnnn", "nnknnnnknn", "nnnnnnnnnn", "nnnwwwwnnn", "nnnwkkwnnn", ".nnnnnnnn.", "..nnnnnn.."]),
  ("꽃", "🌷", ["....pp....", "..pppppp..", ".pppyyppp.", ".pppyyppp.", "..pppppp..", "....pp....", ".....g....", "..gg.g....", "...ggg....", ".....g...."]),
  ("돛단배", "⛵", ["....w.....", "....ww....", "....www...", "....wwww..", "....wwwww.", "....n.....", ".nnnnnnnn.", "..nnnnnn..", "bbbbbbbbbb", "bbbbbbbbbb"]),
 ],
}
PAL = {"r": "#e5484d", "o": "#f2994a", "y": "#f5c518", "g": "#3fa34d", "b": "#3b82c4", "c": "#7fd0e8", "k": "#23272f", "w": "#f6f1e4", "s": "#9aa3b2", "n": "#8a5a34", "p": "#f48fb1"}

def runs(line):
    r, c = [], 0
    for v in line:
        if v: c += 1
        elif c: r.append(c); c = 0
    if c: r.append(c)
    return r or [0]

def line_options(n, clue):  # clue 에 맞는 한 줄(0/1 n개)의 모든 경우
    ks = [] if clue == [0] else clue
    out = []
    def rec(i, k, cur):
        if k == len(ks):
            out.append(tuple(cur + [0] * (n - len(cur)))); return
        need = sum(ks[k:]) + len(ks) - k - 1
        for s in range(i, n - need + 1):
            rec(s + ks[k] + 1, k + 1, cur + [0] * (s - len(cur)) + [1] * ks[k])
    rec(0, 0, [])
    return [o for o in out if len(o) == n]

def feasible(col, ks, n):  # 위에서부터 채운 열(col)이 단서(ks)로 끝낼 수 있는 상태인가
    r = [x for x in runs(col) if x] if any(col) else []
    open_ = bool(col) and col[-1] == 1
    done = r[:-1] if open_ else r
    k = len(done)
    if k > len(ks) or done != ks[:k]: return False
    rem = n - len(col)
    if open_:
        if k >= len(ks) or r[-1] > ks[k]: return False
        need = (ks[k] - r[-1]) + sum(ks[k + 1:]) + (len(ks) - k - 1)
    else:
        rest = ks[k:]; need = sum(rest) + max(0, len(rest) - 1)
    return need <= rem

def count_solutions(grid, limit=2):  # 행 단위 탐색 + 열 단서 가지치기
    n = len(grid); g = [[1 if ch != "." else 0 for ch in r] for r in grid]
    rc = [runs(r) for r in g]; cc = [runs([g[y][x] for y in range(n)]) for x in range(n)]
    kc = [[] if c == [0] else c for c in cc]
    rows = [line_options(n, c) for c in rc]; cnt = [0]
    def rec(y, chosen):
        if cnt[0] >= limit: return
        if y == n:
            if all(runs([chosen[i][x] for i in range(n)]) == cc[x] for x in range(n)): cnt[0] += 1
            return
        for opt in rows[y]:
            ch = chosen + [opt]
            if all(feasible([ch[i][x] for i in range(len(ch))], kc[x], n) for x in range(n)): rec(y + 1, ch)
    rec(0, [])
    return cnt[0]

def check():
    bad = 0
    for n, lst in PICS.items():
        for name, emo, rows in lst:
            if len(rows) != n or any(len(r) != n for r in rows): print(f"❌ 크기 오류: {n}×{n} {name}"); bad += 1; continue
            if any(ch != "." and ch not in PAL for r in rows for ch in r): print(f"❌ 색 글자 오류: {name}"); bad += 1; continue
            c = count_solutions(rows)
            print(("✅" if c == 1 else "⚠️ 정답이 여러 개") + f" {n}×{n} {name} (정답 {'1개' if c == 1 else '2개 이상'})")
            if c != 1: bad += 1
    return bad

def inject():
    data = {str(n): [{"n": nm, "e": e, "g": rows} for nm, e, rows in lst] for n, lst in PICS.items()}
    p = "../../nonogram.html"; s = open(p, encoding="utf-8").read()
    new = "/*PICS*/const PICS = " + json.dumps(data, ensure_ascii=False) + ", PAL = " + json.dumps(PAL) + ";/*/PICS*/"
    if "/*PICS*/" in s: s = re.sub(r"/\*PICS\*/.*?/\*/PICS\*/", lambda m: new, s, flags=re.S)
    else: raise SystemExit("nonogram.html 에 /*PICS*/ 표시가 없어요")
    open(p, "w", encoding="utf-8").write(s); print("nonogram.html 그림 목록 갱신:", sum(len(v) for v in PICS.values()), "개")

def montage(path):
    from PIL import Image
    items = [(n, nm, rows) for n, lst in PICS.items() for nm, _, rows in lst]
    cols, box, pad = 6, 150, 14; W = cols * (box + pad) + pad; H = ((len(items) + cols - 1) // cols) * (box + pad) + pad
    im = Image.new("RGB", (W, H), (30, 30, 36))
    for i, (n, nm, rows) in enumerate(items):
        ox, oy, c = pad + (i % cols) * (box + pad), pad + (i // cols) * (box + pad), box // n
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch == ".": continue
                col = tuple(int(PAL[ch][k:k + 2], 16) for k in (1, 3, 5))
                for dy in range(c):
                    for dx in range(c): im.putpixel((ox + x * c + dx, oy + y * c + dy), col)
    im.save(path)

if __name__ == "__main__":
    if "--montage" in sys.argv: montage(sys.argv[sys.argv.index("--montage") + 1]); sys.exit(0)
    bad = check()
    if bad: print(f"\n문제 {bad}개 — 고친 뒤 다시 실행하세요"); sys.exit(1)
    inject()
