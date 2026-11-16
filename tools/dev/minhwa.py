# 맞고 화투 48장 — 한국 민화풍 그림을 직접 SVG로 그려 cards-minhwa/ 에 만든다 (결정 D14, 직접 그린 그림이라 저작권 문제 없음)
# 실행: tools\dev 에서 py minhwa.py   → ../../cards-minhwa/00.svg ~ 47.svg  (파일 이름 = 카드 번호, 월 = (번호>>2)+1)
# 좌표는 100x164 칸(카드 비율 1:1.64, 기존 그림과 같음). 색은 오방색 계열.
import math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cards-minhwa")
os.makedirs(OUT, exist_ok=True)

# gostop-core.js 의 MONTHS 와 같은 표
MONTHS = [
    ["gwang", "ddi:red", "pi", "pi"], ["yeol:bird", "ddi:red", "pi", "pi"], ["gwang", "ddi:red", "pi", "pi"], ["yeol:bird", "ddi:cho", "pi", "pi"],
    ["yeol:bridge", "ddi:cho", "pi", "pi"], ["yeol:butterfly", "ddi:blue", "pi", "pi"], ["yeol:boar", "ddi:cho", "pi", "pi"], ["gwang", "yeol:goose", "pi", "pi"],
    ["yeol:cup", "ddi:blue", "pi", "pi"], ["yeol:deer", "ddi:blue", "pi", "pi"], ["gwang", "pi2", "pi", "pi"], ["gwang", "yeol:swallow", "ddi:plain", "pi2"],
]

INK = "#3b2a20"
PAPER = "#f3e7c9"


def f(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")


def tr(g, x, y, s=1.0, r=0.0, flip=False):
    sx = -s if flip else s
    return '<g transform="translate(%s %s) rotate(%s) scale(%s %s)">%s</g>' % (f(x), f(y), f(r), f(sx), f(s), g)


def ell(cx, cy, rx, ry, fill, r=0, stroke=None, sw=0.6):
    st = (' stroke="%s" stroke-width="%s"' % (stroke, sw)) if stroke else ""
    rot = (' transform="rotate(%s %s %s)"' % (f(r), f(cx), f(cy))) if r else ""
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s%s/>' % (f(cx), f(cy), f(rx), f(ry), fill, st, rot)


def circ(cx, cy, r, fill, stroke=None, sw=0.6):
    st = (' stroke="%s" stroke-width="%s"' % (stroke, sw)) if stroke else ""
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (f(cx), f(cy), f(r), fill, st)


def path(d, fill="none", stroke=None, sw=1, cap="round"):
    st = (' stroke="%s" stroke-width="%s" stroke-linecap="%s" stroke-linejoin="round"' % (stroke, sw, cap)) if stroke else ""
    return '<path d="%s" fill="%s"%s/>' % (d, fill, st)


def poly(pts, fill, stroke=None, sw=0.6):
    st = (' stroke="%s" stroke-width="%s" stroke-linejoin="round"' % (stroke, sw)) if stroke else ""
    return '<polygon points="%s" fill="%s"%s/>' % (" ".join("%s,%s" % (f(a), f(b)) for a, b in pts), fill, st)


# ───────── 꽃·잎 조각
def flower5(x, y, r, petal, center="#f0c040", ink=INK):
    s = ""
    for i in range(5):
        a = math.radians(i * 72 - 90)
        s += ell(x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, r * 0.5, r * 0.42, petal, math.degrees(a), ink, 0.35)
    return s + circ(x, y, r * 0.25, center)


def leaf(x, y, l, w, ang, fill="#3f7d4a"):
    # 끝이 뾰족한 잎
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * l, y + math.sin(a) * l
    nx, ny = -math.sin(a) * w, math.cos(a) * w
    mx, my = x + math.cos(a) * l * 0.5, y + math.sin(a) * l * 0.5
    d = "M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" % (f(x), f(y), f(mx + nx), f(my + ny), f(ex), f(ey), f(mx - nx), f(my - ny), f(x), f(y))
    return path(d, fill, INK, 0.4)


def tuft(x, y, s, col="#2f6b3a"):
    t = ""
    for i in range(-4, 5):
        a = math.radians(-90 + i * 17)
        t += path("M%s,%s L%s,%s" % (f(x), f(y), f(x + math.cos(a) * 15 * s), f(y + math.sin(a) * 15 * s)), "none", col, 1.1)
    return t + circ(x, y, 1.4 * s, "#5b3a22")


def maple_leaf(x, y, r, fill, rot=0):
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36 - 90)
        rr = r if i % 2 == 0 else r * 0.5
        if i % 4 == 0 and i > 0:
            rr = r * 0.95
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return poly(pts, fill, INK, 0.45) + path("M%s,%s L%s,%s" % (f(x), f(y), f(x + math.cos(math.radians(rot + 90)) * r * 0.4), f(y + math.sin(math.radians(rot + 90)) * r * 0.4)), "none", INK, 0.5)


# ───────── 새·동물
def bird(x, y, s, body, wing, belly, flip=False, beak="#e8a020", crest=False):
    g = path("M-6,2 L-22,10 L-20,4 L-24,-1 L-8,-3 Z", wing, INK, 0.5)  # 꼬리
    g += ell(0, 0, 11, 7.5, body, -8, INK, 0.5)
    g += ell(1, 3, 8, 4.2, belly, -8)
    g += circ(10, -7, 5.2, body, INK, 0.5)
    g += poly([(14.5, -8), (21, -6.2), (14.5, -5)], beak, INK, 0.4)
    g += circ(11.5, -8.2, 1.1, INK)
    g += path("M-4,-3 Q2,-12 12,-2 Q4,3 -4,-3 Z", wing, INK, 0.5)  # 날개
    if crest:
        g += path("M8,-12 Q6,-18 11,-17", "none", INK, 0.8)
    g += path("M-1,7 L-2,12 M3,7 L3,12", "none", INK, 0.8)
    return tr(g, x, y, s, 0, flip)


def butterfly(x, y, s, a="#e8863a", b="#f3c14a"):
    g = ""
    for sg in (-1, 1):
        g += path("M0,0 Q%s,-16 %s,-6 Q%s,0 0,0 Z" % (f(sg * 8), f(sg * 17), f(sg * 8)), a, INK, 0.5)
        g += path("M0,0 Q%s,10 %s,12 Q%s,4 0,0 Z" % (f(sg * 10), f(sg * 9), f(sg * 3)), b, INK, 0.5)
        g += circ(sg * 10, -6, 1.7, "#fff7d8")
    g += ell(0, 1, 1.3, 6, INK)
    g += path("M0,-4 Q-3,-10 -6,-11 M0,-4 Q3,-10 6,-11", "none", INK, 0.5)
    return tr(g, x, y, s)


def boar(x, y, s):
    g = ell(0, 0, 17, 10, "#6b4a32", 0, INK, 0.6)
    g += path("M-14,-6 Q-8,-14 0,-9 Q8,-14 14,-6", "none", "#3b2a20", 1.1)  # 등 털
    g += circ(18, 1, 8, "#7a553a", INK, 0.6)  # 머리
    g += ell(25, 3, 3.6, 3, "#c9967a", 0, INK, 0.5)  # 코
    g += poly([(22, 5.5), (27, 9), (24, 3.5)], "#fffbe8", INK, 0.35)  # 엄니
    g += poly([(14, -5), (16, -13), (20, -6)], "#6b4a32", INK, 0.5)  # 귀
    g += circ(20, -1, 1.2, INK)
    for lx in (-11, -5, 6, 12):
        g += path("M%s,8 L%s,17" % (lx, lx), "none", INK, 2.2)
    g += path("M-17,-1 Q-24,-6 -22,-11", "none", INK, 1.2)
    return tr(g, x, y, s)


def deer(x, y, s):
    g = ell(0, 0, 16, 8.5, "#bd8650", 0, INK, 0.6)
    for i, (sx, sy) in enumerate([(-8, -3), (-2, 2), (6, -4), (10, 2), (-11, 3)]):
        g += circ(sx, sy, 1.3, "#fff2d0")
    g += path("M12,-4 Q18,-14 20,-22", "none", "#bd8650", 6)
    g += ell(21, -24, 5.2, 4, "#bd8650", -20, INK, 0.6)
    g += circ(23, -25, 0.9, INK)
    g += circ(26, -23, 0.9, INK)
    g += path("M19,-27 L16,-38 M16,-38 L11,-41 M16,-36 L20,-42 M21,-27 L25,-38 M25,-38 L30,-40 M25,-36 L22,-43", "none", "#7a4a22", 1.3)
    for lx in (-11, -6, 7, 12):
        g += path("M%s,7 L%s,24" % (lx, lx + 1), "none", INK, 2)
    return tr(g, x, y, s)


def goose(x, y, s, flip=False):
    g = path("M-22,-2 Q-12,-14 0,-2 Q12,-14 22,-2 Q12,-6 0,2 Q-12,-6 -22,-2 Z", "#3d3a44", INK, 0.5)
    g += ell(0, 1, 4, 2.2, "#3d3a44")
    g += path("M3,0 L10,2", "none", "#e0902a", 1.6)
    g += circ(7, -0.5, 2.6, "#3d3a44")
    return tr(g, x, y, s, 0, flip)


def crane(x, y, s):
    g = path("M-8,0 Q-22,2 -26,12 Q-12,10 -4,6 Z", "#ffffff", INK, 0.5)  # 꼬리 깃
    g += ell(0, 0, 13, 8, "#ffffff", -5, INK, 0.6)
    g += path("M8,-3 Q16,-14 14,-26", "none", "#ffffff", 4.6)
    g += path("M8,-3 Q16,-14 14,-26", "none", INK, 0.6)
    g += circ(15, -28, 3.4, "#ffffff", INK, 0.6)
    g += circ(15.4, -30.6, 1.6, "#d8281e")  # 단정학 머리
    g += path("M17.5,-28 L26,-26", "none", "#f0b020", 1.4)
    g += circ(16, -28.4, 0.7, INK)
    g += path("M-8,-2 Q-2,-18 10,-4 Q2,2 -8,-2 Z", "#f3f3f3", INK, 0.5)
    g += path("M-6,2 Q-2,0 -1,-4", "none", INK, 0.6)
    g += path("M-2,8 L-4,28 M4,8 L4,28", "none", INK, 0.9)
    return tr(g, x, y, s)


def phoenix(x, y, s):
    g = ""
    cols = ["#d8402f", "#f0a830", "#2f6fb0", "#3f9a58"]
    for i, c in enumerate(cols):  # 긴 꼬리 깃
        g += path("M-6,6 C-30,%s -34,%s -26,%s" % (20 + i * 6, 40 + i * 8, 62 + i * 3), "none", c, 3.2 - i * 0.3)
    g += ell(0, 0, 13, 8.5, "#d8402f", -10, INK, 0.6)
    g += path("M-4,-2 Q-14,-16 4,-10 Q10,-6 6,2 Z", "#f0a830", INK, 0.5)
    g += path("M8,-4 Q15,-14 13,-22", "none", "#d8402f", 5)
    g += circ(14, -24, 4.6, "#e65a3a", INK, 0.6)
    g += poly([(18, -25), (25, -22.5), (18, -21.5)], "#f0b020", INK, 0.4)
    g += circ(15.5, -25, 1, INK)
    g += path("M12,-28 Q8,-36 14,-35 M14,-29 Q14,-38 19,-35", "none", "#2f6fb0", 1.6)  # 볏
    g += path("M-2,8 L-4,18 M3,8 L4,18", "none", INK, 1)
    return tr(g, x, y, s)


# ───────── 달마다 바탕 그림 (월별 식물·풍경). 반환: 그림 조각 문자열
def scene(m, k=0):
    s = ""
    if m == 1:  # 소나무
        s += path("M24,150 C34,118 18,96 40,70 C52,56 44,40 56,24", "none", "#6b4423", 6.5)
        s += path("M40,72 C58,70 66,60 78,50", "none", "#6b4423", 3.5)
        s += path("M33,100 C20,96 14,88 8,80", "none", "#6b4423", 3)
        for (a, b, c) in [(56, 26, 1.1), (78, 52, 1.0), (10, 80, 0.95), (45, 70, 0.9), (30, 108, 0.9), (70, 98, 0.8)]:
            s += tuft(a, b, c)
        s += path("M50,140 C60,130 68,130 80,134", "none", "#6b4423", 3)
        s += tuft(80, 134, 0.8)
    elif m == 2:  # 매화
        s += path("M8,150 C26,128 20,100 46,84 C62,74 58,52 76,38 C84,30 88,22 94,20", "none", "#4a3426", 5)
        s += path("M46,84 C38,72 30,70 22,62 M58,60 C66,66 80,66 90,74 M26,118 C36,116 44,122 52,128", "none", "#4a3426", 2.4)
        for (a, b, c) in [(22, 62, 6.5), (90, 74, 6), (76, 38, 7), (46, 84, 7.5), (52, 128, 6), (62, 54, 5.5), (30, 100, 5), (94, 22, 5), (16, 140, 5)]:
            s += flower5(a, b, c, "#f9d8e0" if (a + b) % 2 else "#f4a9bd")
    elif m == 3:  # 벚꽃
        s += path("M96,150 C80,120 90,96 62,78 C46,68 52,48 30,34 C20,28 14,22 8,18", "none", "#4a3426", 5.5)
        s += path("M62,78 C74,70 82,60 92,56 M44,52 C54,50 62,40 70,36", "none", "#4a3426", 2.4)
        pts = [(30, 34, 7), (10, 20, 6), (62, 78, 7.5), (92, 56, 6.5), (70, 36, 6), (50, 60, 6), (82, 104, 6), (42, 44, 5.5), (88, 130, 5.5), (20, 46, 5)]
        for (a, b, c) in pts:
            s += flower5(a, b, c, "#fbc9d8", "#e8788f")
            s += flower5(a + 7, b + 6, c * 0.6, "#f7a8c0", "#e8788f")
    elif m == 4:  # 흑싸리(검붉은 싸리꽃)
        s += path("M6,20 C34,6 70,10 96,30", "none", "#4a3426", 3.2)
        for i, x in enumerate((20, 44, 66, 86)):
            L = 8 + (i % 2) * 3
            for j in range(L):
                w = 5.2 - j * 0.35
                s += ell(x + math.sin(j * 0.8 + i) * 1.8, 18 + j * 7.4, max(w, 1.6), 3.8, "#4b3b69" if j % 2 else "#2f2646", 0, INK, 0.3)
            s += path("M%s,14 L%s,24" % (x, x), "none", "#4a3426", 1.2)
        for (a, b, c) in [(10, 40, 160), (92, 62, 20), (14, 110, 200), (84, 134, 340), (50, 150, 270)]:
            s += leaf(a, b, 16, 4.4, c, "#4c8a55")
    elif m == 5:  # 난초
        for ang, base in [(-100, 20), (-70, 38), (-120, 14), (-60, 50)]:
            pass
        s += path("M30,150 C20,110 28,70 6,40 C26,62 40,96 38,150 Z", "#3d8a50", INK, 0.5)
        s += path("M38,150 C44,100 66,66 94,38 C76,80 60,110 50,150 Z", "#4c9a5c", INK, 0.5)
        s += path("M34,150 C30,120 46,88 56,52 C58,92 52,124 46,150 Z", "#2f7344", INK, 0.5)
        s += path("M62,100 L60,56", "none", "#6a8f44", 2)
        s += flower5(60, 52, 8, "#8c7be0", "#f3e6a0") + flower5(70, 70, 6, "#a090ea", "#f3e6a0")
    elif m == 6:  # 모란
        for ang in (200, 340, 170, 10, 250):
            s += leaf(50, 100, 34, 11, ang, "#2f7344")
        for (a, b, r, c1, c2) in [(50, 70, 24, "#d8405c", "#ec7a90"), (24, 118, 14, "#e46a82", "#f3a0b0"), (80, 122, 13, "#e46a82", "#f3a0b0")]:
            for i in range(8):
                ang = i * 45
                s += ell(a + math.cos(math.radians(ang)) * r * 0.55, b + math.sin(math.radians(ang)) * r * 0.5, r * 0.5, r * 0.4, c1, ang, INK, 0.4)
            for i in range(6):
                ang = i * 60 + 20
                s += ell(a + math.cos(math.radians(ang)) * r * 0.3, b + math.sin(math.radians(ang)) * r * 0.28, r * 0.34, r * 0.26, c2, ang, INK, 0.3)
            s += circ(a, b, r * 0.18, "#f3c844", INK, 0.3)
    elif m == 7:  # 홍싸리
        for x0, ang in [(22, -12), (50, 4), (80, 14)]:
            s += path("M%s,150 C%s,110 %s,70 %s,24" % (x0, x0 + ang, x0 + ang * 2, x0 + ang * 3), "none", "#6a4a2c", 2.2)
            for j in range(14):
                t = j / 13
                px = x0 + ang * 3 * t + math.sin(j) * 5
                py = 148 - t * 120
                s += ell(px - 6, py, 7, 2.6, "#d8566a", -25, INK, 0.3) + ell(px + 6, py + 3, 7, 2.6, "#e8788a", 25, INK, 0.3)
    elif m == 8:  # 공산(보름달·억새)
        s += circ(50, 60, 32, "#f8e8a0", "#d8b858", 1)
        s += poly([(0, 118), (22, 88), (40, 108), (62, 80), (84, 104), (100, 90), (100, 150), (0, 150)], "#4f6b7c", INK, 0.5)
        s += poly([(0, 134), (30, 112), (58, 130), (100, 112), (100, 164), (0, 164)], "#35505e", INK, 0.5)
        for (x, h) in [(14, 40), (30, 30), (70, 36), (86, 44)]:
            s += path("M%s,162 Q%s,%s %s,%s" % (x, x - 3, 162 - h * 0.6, x + 4, 162 - h), "none", "#a08a56", 1.4)
            s += ell(x + 4, 162 - h - 4, 2.4, 7, "#e8d8a8", 12, "#a08a56", 0.4)
    elif m == 9:  # 국화
        for ang in (210, 330, 160, 20):
            s += leaf(50, 128, 30, 9, ang, "#3f7d4a")
        for (a, b, r, c) in [(50, 66, 25, "#f2c42e"), (22, 112, 14, "#fff2c0"), (80, 110, 13, "#f2c42e")]:
            for i in range(20):
                ang = i * 18
                s += ell(a + math.cos(math.radians(ang)) * r * 0.62, b + math.sin(math.radians(ang)) * r * 0.62, r * 0.42, r * 0.13, c, ang, "#8a6a10", 0.3)
            for i in range(14):
                ang = i * 25.7 + 9
                s += ell(a + math.cos(math.radians(ang)) * r * 0.36, b + math.sin(math.radians(ang)) * r * 0.36, r * 0.27, r * 0.1, "#f7dc70" if c != "#fff2c0" else "#ffffff", ang, "#8a6a10", 0.25)
            s += circ(a, b, r * 0.16, "#e0902a")
    elif m == 10:  # 단풍
        s += path("M96,6 C70,24 60,50 34,64 C22,72 14,86 8,104", "none", "#4a3426", 4.5)
        cols = ["#d2412f", "#e58a2b", "#c0302a", "#f0b030"]
        for i, (a, b, r, rot) in enumerate([(78, 24, 16, 10), (58, 52, 15, 40), (36, 76, 14, 0), (88, 62, 13, 25), (18, 98, 12, 55), (70, 90, 14, 70), (46, 112, 12, 15)]):
            s += maple_leaf(a, b, r, cols[i % 4], rot)
    elif m == 11:  # 오동
        s += path("M50,150 L50,64", "none", "#6b4a2c", 4)
        for (a, b, r, rot) in [(30, 112, 26, -20), (72, 108, 25, 20), (50, 134, 22, 0)]:
            s += path("M%s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s %s,%s Z" % (f(a), f(b - r), f(a + r), f(b - r), f(a + r), f(b + r * 0.6), f(a), f(b + r), f(a - r), f(b + r * 0.6), f(a - r), f(b - r), f(a), f(b - r)), "#4a8a56", INK, 0.5)
            s += path("M%s,%s L%s,%s" % (f(a), f(b - r), f(a), f(b + r)), "none", INK, 0.5)
        for (a, b) in [(40, 38), (56, 28), (62, 50), (46, 56), (50, 44)]:
            s += ell(a, b, 5.4, 7, "#9a70c8", 0, INK, 0.4) + ell(a, b + 2.5, 2.6, 3, "#e6d4f4")
    elif m == 12:  # 비·버들
        for x0 in (18, 44, 70, 90):
            s += path("M%s,8 C%s,40 %s,70 %s,%s" % (x0, x0 + 8, x0 - 6, x0 + 2, 120 + (x0 % 3) * 10), "none", "#6a9a4c", 1.6)
            for j in range(9):
                t = (j + 1) / 10
                s += leaf(x0 + math.sin(t * 6) * 3, 8 + t * 108, 7, 1.7, 100 + (j % 2) * 60, "#7ab45a")
        s += path("M4,6 L96,6", "none", "#4a3426", 3)
        for i in range(14):
            x = 6 + (i * 37) % 90
            y = 20 + (i * 53) % 130
            s += path("M%s,%s l-3,9" % (x, y), "none", "#5b8fd0", 0.9)
    return s


def bridge(x, y, s):
    g = path("M-26,10 Q0,-14 26,10", "none", "#8a5a34", 5)
    g += path("M-26,10 L26,10", "none", "#8a5a34", 3)
    for bx in (-16, -8, 0, 8, 16):
        g += path("M%s,%s L%s,%s" % (bx, -8 + abs(bx) * 0.4, bx, 10), "none", "#5b3a22", 1)
    g += path("M-30,14 Q-14,18 0,14 Q14,10 30,14", "none", "#5b8fd0", 1.4)
    return tr(g, x, y, s)


def cup(x, y, s):
    g = path("M-12,-8 L12,-8 Q12,10 0,12 Q-12,10 -12,-8 Z", "#fbf6e8", INK, 0.8)
    g += path("M-10,-2 Q0,2 10,-2 M-8,3 Q0,7 8,3", "none", "#3a62b0", 1)
    g += path("M-3,12 L-5,20 L5,20 L3,12 Z", "#fbf6e8", INK, 0.8)
    g += path("M-6,20 L6,20", "none", INK, 1.2)
    return tr(g, x, y, s)


def umbrella_man(x, y, s):
    g = path("M-26,-6 Q0,-42 26,-6 Z", "#e8a43a", INK, 0.8)
    for rx in (-16, -6, 6, 16):
        g += path("M%s,-6 Q%s,-22 0,-25" % (rx, rx * 0.5), "none", "#8a5a1a", 0.6)
    g += path("M0,-24 L0,40", "none", INK, 1.4)
    g += poly([(-12, 8), (12, 8), (16, 52), (-16, 52)], "#fbf6ec", INK, 0.7)  # 도포
    g += path("M-3,8 L0,30 L3,8", "none", "#2f4f8a", 1.2)
    g += circ(0, 2, 5.5, "#f6dcb8", INK, 0.6)
    g += ell(0, -2, 12, 2.2, "#1c1612", 0, INK, 0.5) + path("M-5,-3 Q0,-14 5,-3 Z", "#1c1612", INK, 0.5)  # 갓
    g += path("M-6,52 L-6,62 M6,52 L6,62", "none", INK, 2)
    return tr(g, x, y, s)


def swallow(x, y, s, flip=False):
    g = path("M-6,0 L-26,-6 L-20,2 L-26,10 Z", "#1e2c52", INK, 0.5)
    g += ell(0, 0, 11, 6, "#1e2c52", -10, INK, 0.5)
    g += ell(2, 2.5, 7, 3.2, "#fffbea")
    g += circ(10, -5, 4.6, "#1e2c52", INK, 0.5)
    g += circ(12, -2.5, 2, "#d8402f")
    g += poly([(13, -6), (19, -4.5), (13, -3.5)], "#e8a020", INK, 0.35)
    g += circ(11, -6.5, 0.9, "#ffffff")
    g += path("M-4,-3 Q-12,-18 8,-12 Q4,-3 -4,-3 Z", "#2c3f72", INK, 0.5)
    return tr(g, x, y, s, 0, flip)


def pavilion(x, y, s):  # 3월 광: 정자 기와지붕
    g = path("M-34,0 Q-26,-2 -22,-12 L22,-12 Q26,-2 34,0 L30,5 L-30,5 Z", "#5b4a3a", INK, 0.8)
    g += path("M-22,-12 Q0,-26 22,-12", "#4a3a2e", INK, 0.8)
    g += poly([(-24, 5), (24, 5), (22, 12), (-22, 12)], "#c8352b", INK, 0.6)
    for px in (-20, 0, 20):
        g += path("M%s,12 L%s,40" % (px, px), "none", "#a83a2a", 3)
    g += poly([(-16, 12), (-4, 12), (-4, 24), (-16, 24)], "#f0e0b0", INK, 0.5)
    g += poly([(4, 12), (16, 12), (16, 24), (4, 24)], "#f0e0b0", INK, 0.5)
    return tr(g, x, y, s)


# ───────── 띠 (리본)
def ribbon(kind):
    col = {"red": "#cf3a30", "blue": "#2f62b4", "cho": "#3f9650", "plain": "#efe3c4"}[kind]
    mark = "#fff3d8" if kind != "plain" else "#8a6a44"
    g = '<g transform="rotate(-4 50 82)">'
    g += path("M36,10 L68,10 L68,150 L52,142 L36,150 Z", col, INK, 1.2)
    if kind == "plain":
        g += path("M40,16 L64,16 M40,144 L64,144", "none", "#8a6a44", 0.8)
        for yy in (40, 70, 100):
            g += path("M46,%s Q52,%s 58,%s" % (yy, yy + 10, yy), "none", "#b09068", 1.3)
    else:
        for yy in (30, 50, 70, 90, 110):  # 글씨 느낌의 줄무늬
            g += path("M44,%s L60,%s M52,%s L52,%s" % (yy, yy, yy - 6, yy + 6), "none", mark, 1.6)
    return g + "</g>"


def mark_double():  # 쌍피 표시
    return circ(84, 148, 8.5, "#d8402f", INK, 0.8) + circ(81, 148, 1.8, "#fff6dc") + circ(87, 148, 1.8, "#fff6dc")


def card(i):
    m, k = (i >> 2) + 1, i & 3
    t = MONTHS[m - 1][k].split(":")
    typ, sub = t[0], (t[1] if len(t) > 1 else "")
    bgc = PAPER
    if typ == "gwang" and m == 8:
        bgc = "#2a3a5c"
    body = scene(m, k)
    extra = ""
    if m == 8 and typ != "gwang":
        body = body  # 억새·산·달
    if typ == "gwang":
        if m == 1:
            extra = circ(76, 30, 15, "#d8402f", "#8a2218", 0.8) + crane(34, 58, 1.2)
        elif m == 3:
            extra = pavilion(50, 30, 0.95)
        elif m == 8:
            extra = ""
        elif m == 11:
            extra = phoenix(52, 72, 1.15)
        elif m == 12:
            body = scene(12)
            extra = umbrella_man(52, 74, 1.15)
    elif typ == "yeol":
        if sub == "bird":
            extra = bird(40, 62, 1.45, "#f2c230", "#8a6a20", "#fff1b0", False) if m == 2 else bird(32, 46, 1.3, "#5a4a78", "#3a2f4f", "#d8d0e8", False)
        elif sub == "bridge":
            extra = bridge(50, 126, 1.5)
        elif sub == "butterfly":
            extra = butterfly(78, 40, 1.5) + butterfly(24, 134, 1.0, "#9a6ad8", "#f0d0ff")
        elif sub == "boar":
            extra = boar(42, 128, 1.25)
        elif sub == "goose":
            extra = goose(30, 34, 1.0) + goose(66, 28, 1.0, True) + goose(50, 48, 0.8)
        elif sub == "cup":
            extra = cup(50, 122, 1.35)
        elif sub == "deer":
            extra = deer(40, 118, 1.15)
        elif sub == "swallow":
            extra = swallow(40, 70, 1.5)
    elif typ == "ddi":
        extra = ribbon(sub)
    elif typ == "pi2":
        extra = mark_double()
    border = ""
    if typ == "gwang":
        border = '<rect x="2.6" y="2.6" width="94.8" height="158.8" rx="6" fill="none" stroke="#e0b020" stroke-width="2.6"/>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 164" width="100" height="164">'
           '<defs><clipPath id="c"><rect x="3" y="3" width="94" height="158" rx="6"/></clipPath></defs>'
           '<rect x="0.8" y="0.8" width="98.4" height="162.4" rx="7" fill="%s" stroke="%s" stroke-width="1.6"/>'
           '<g clip-path="url(#c)">%s%s</g>%s'
           '<rect x="5" y="5" width="90" height="154" rx="4" fill="none" stroke="#b08a54" stroke-width="0.6" opacity=".7"/></svg>') % (bgc, INK, body, extra, border)
    return svg


for i in range(48):
    with open(os.path.join(OUT, "%02d.svg" % i), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(card(i))
print("만든 그림:", len(os.listdir(OUT)), "→", os.path.normpath(OUT))
