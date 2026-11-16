# Gemini 로 만든 월별 화투 그림(한 장에 같은 달 카드 4장)을 카드로 잘라 cards-gemini/NN.png 로 만든다 (결정 D15)
# 원본: tools/dev/gemini_src/01월.png ~ 12월.png (.jfif/.jpg 도 됨). 카드 4장 = 왼쪽부터 번호 (월-1)*4 + 0~3
# 실행: tools\dev 에서 py gemini_cut.py   (있는 달만 만들고, 없는 달·이상한 달은 알려 준다)
import os, glob, sys
from PIL import Image, ImageDraw
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gemini_src")
OUT = os.path.join(HERE, "..", "..", "cards-gemini")
os.makedirs(OUT, exist_ok=True)
TW, TH = 200, 310  # 카드 한 장 크기(px), 높이/폭 = 1.55 (화면 CSS 의 .art-gm 비율과 같아야 함)
H = {}

def runs(v, th, gap):
    r, s = [], None
    for i, x in enumerate(v):
        if x > th and s is None: s = i
        if x <= th and s is not None: r.append([s, i - 1]); s = None
    if s is not None: r.append([s, len(v) - 1])
    out = []
    for a in r:
        if out and a[0] - out[-1][1] <= gap: out[-1][1] = a[1]
        else: out.append(a)
    return out

def find_cards(im):
    a = np.array(im.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = ((r - b) > 14) | (a.sum(2) < 330)       # 카드 속(누런 종이·진한 선·색 그림). 회색 배경·그림자는 제외
    hh = mask.shape[0]
    cols = mask.sum(0)
    rs = [x for x in runs(cols, hh * 0.08, 8) if x[1] - x[0] > 40]
    boxes = []
    for x0, x1 in rs:
        rows = np.where(mask[:, x0:x1 + 1].sum(1) > (x1 - x0) * 0.3)[0]
        boxes.append((x0, rows.min(), x1 + 1, rows.max() + 1))
    return boxes

def rounded(t, rad):
    w, h = t.size
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=rad * 4, fill=255)
    t.putalpha(m.resize((w, h), Image.LANCZOS))
    return t

def src_for(mon):
    for e in ("png", "jfif", "jpg", "jpeg", "webp"):
        for fmt in ("%02d월.%s", "%d월.%s"):
            p = os.path.join(SRC, fmt % (mon, e))
            if os.path.exists(p): return p

made, bad = [], []
seen = {}
for mon in range(1, 13):
    p = src_for(mon)
    if not p: continue
    h = open(p, "rb").read()
    if h in seen: bad.append("%d월: %d월과 같은 파일이에요" % (mon, seen[h])); continue
    seen[h] = mon
    im = Image.open(p)
    boxes = find_cards(im)
    if len(boxes) != 4: bad.append("%d월: 카드 %d장만 찾았어요(4장이어야 해요) %s" % (mon, len(boxes), boxes)); continue
    ws = [b[2] - b[0] for b in boxes]; hs = [b[3] - b[1] for b in boxes]
    for k, b in enumerate(boxes):
        t = im.convert("RGBA").crop(b)
        t = t.resize((TW, TH), Image.LANCZOS)   # 월마다 비율이 1.50~1.58 로 조금씩 달라서 모두 같은 비율로 맞춘다
        rounded(t, round(TW * 0.07)).save(os.path.join(OUT, "%02d.webp" % ((mon - 1) * 4 + k)), quality=88, method=6)
    made.append(mon)
    print("%d월: 카드 폭 %s 높이 %s (비율 %.2f)" % (mon, ws, hs, sum(hs) / sum(ws)))

# ── 월별 그림이 없는 달은 한 장짜리 모음 그림(all.png, 15칸)에서 자르고, 거기에도 없는 7월은 minhwa 그림(m07_*.png)으로 채운다.
SHEET = os.path.join(SRC, "all.png")
GX, DX, RY, CW, CH = [32, 533, 1032], [0, 89, 178, 268], [45, 192, 337, 478, 621], 79, 108
CELL = {6: (1, 2), 8: (2, 0), 9: (2, 1), 10: (2, 2), 11: (2, 3), 12: (2, 4)}   # 월 → (묶음, 줄)
sheet = Image.open(SHEET).convert("RGB") if os.path.exists(SHEET) else None
def sheet_card(g, r, c):
    a = np.array(sheet).astype(int); dk = a.sum(2) < 250
    x0, y0 = GX[g] + DX[c], RY[r]
    xs, ys = slice(max(x0 - 6, 0), x0 + CW + 6), slice(max(y0 - 6, 0), y0 + CH + 6)
    d = dk[ys, xs]
    cols = np.where(d[: CH + 4].sum(0) > CH * 0.5)[0]
    rows = np.where(d[:, 8: CW - 6].sum(1) > CW * 0.5)[0]; rows = rows[rows < CH + 8]
    b = (xs.start + cols.min(), ys.start + rows.min(), xs.start + cols.max() + 1, ys.start + rows.max() + 1)
    return sheet.crop(b).convert("RGBA").resize((TW, TH), Image.LANCZOS)
for mon in range(1, 13):
    if mon in made: continue
    for k in range(4):
        i = (mon - 1) * 4 + k
        if mon == 7:
            pth = os.path.join(SRC, "m07_%d.png" % k)
            if not os.path.exists(pth): bad.append("7월 임시 그림 없음: node render_m07.js 를 먼저 실행"); break
            t = Image.open(pth).convert("RGBA").resize((TW, TH), Image.LANCZOS)
        elif mon in CELL and sheet is not None:
            cc = 2 if (mon == 11 and k == 3) else k    # 11월 4번째엔 쌍피 점이 잘못 붙어 3번째(피) 그림을 쓴다
            t = rounded(sheet_card(*CELL[mon], cc), round(TW * 0.07))
        else:
            bad.append("%d월 그림 없음" % mon); break
        t.save(os.path.join(OUT, "%02d.webp" % i), quality=88, method=6)
    else:
        print("%d월: %s" % (mon, "임시(minhwa)" if mon == 7 else "all.png 에서 자름(해상도 낮음)"))
print("월별 그림:", made, "| 문제:", bad or "없음", "| 파일", len(os.listdir(OUT)), "장")
