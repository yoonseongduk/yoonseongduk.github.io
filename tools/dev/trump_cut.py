# 트럼프카드 그림 시트(무늬별 13장, 조커·뒷면)를 카드로 잘라 cards-trump/ 에 webp 로 만든다 (결정 D19)
# 원본: tools/dev/gemini_src/트럼프 <무늬>.png, "트럼프 표지 · 조커 · 뒷면.png"
# 결과: cards-trump/{s,h,d,c}{A,2..10,J,Q,K}.webp, joker-c.webp(컬러), joker-b.webp(흑백), back.webp
# 실행: tools\dev 에서 py trump_cut.py
import os, glob, sys
from PIL import Image, ImageDraw
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gemini_src")
OUT = os.path.join(HERE, "..", "..", "cards-trump")
os.makedirs(OUT, exist_ok=True)
TW, TH = 200, 280          # 한 장 크기(px)
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = {"스페이드": "s", "하트": "h", "다이아몬드": "d", "클로버": "c"}

def runs(v, th, gap=6, minlen=0):
    r, s = [], None
    for i, x in enumerate(v):
        if x > th and s is None: s = i
        if x <= th and s is not None: r.append([s, i - 1]); s = None
    if s is not None: r.append([s, len(v) - 1])
    out = []
    for a in r:
        if out and a[0] - out[-1][1] <= gap: out[-1][1] = a[1]
        else: out.append(a)
    return [x for x in out if x[1] - x[0] >= minlen]

def row_bands(im):
    a = np.array(im.convert("RGB")).astype(int)
    return runs((a.sum(2) > 480).sum(1), 250, 6, 200)      # 카드 줄의 세로 위치

CW, CH, GAP, X0 = 352, 496, 48, 84                         # 카드 폭·높이, 카드 사이 간격, 첫 카드 x (모든 무늬 시트가 같은 배치)

def suit_boxes(im):
    bands = row_bands(im)
    if len(bands) != 2: return []
    out = []
    for (y0, y1), n in zip(bands, (7, 6)):
        out += [(X0 + i * (CW + GAP), y0, X0 + i * (CW + GAP) + CW, y0 + CH) for i in range(n)]
    return out

def joker_boxes(im):
    a = np.array(im.convert("RGB")).astype(int)
    mask = a.sum(2) > 150                                  # 어두운 배경과 구별(카드 속이 어두워도 테두리·종이는 밝다)
    sub = mask[:, 1500:]
    ys = np.where(sub.sum(1) > 200)[0]; y0 = ys.min() if len(ys) else 0
    cols = runs(sub[y0:y0 + CH].sum(0), CH * 0.5, 10, 100)
    return [(1500 + x0, y0, 1500 + x1 + 1, y0 + CH) for x0, x1 in cols]

def rounded(t, rad):
    w, h = t.size
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=rad * 4, fill=255)
    t.putalpha(m.resize((w, h), Image.LANCZOS))
    return t

def save(im, b, name):
    t = rounded(im.convert("RGBA").crop(b).resize((TW, TH), Image.LANCZOS), round(TW * 0.06))
    t.save(os.path.join(OUT, name + ".webp"), quality=90, method=6)

bad = []
for p in glob.glob(os.path.join(SRC, "트럼프 *.png")):
    base = os.path.basename(p)[len("트럼프 "):-4]
    im = Image.open(p)
    if base in SUITS:
        boxes = suit_boxes(im)
        if len(boxes) != 13: bad.append("%s: 카드 %d장(13장이어야 해요)" % (base, len(boxes))); continue
        for r, b in zip(RANKS, boxes): save(im, b, SUITS[base] + r)
        ws = [b[2] - b[0] for b in boxes]; hs = [b[3] - b[1] for b in boxes]
        print("%s: 폭 %d~%d 높이 %d~%d (비율 %.2f)" % (base, min(ws), max(ws), min(hs), max(hs), sum(hs) / sum(ws)))
    else:
        boxes = joker_boxes(im)
        if len(boxes) != 3: bad.append("%s: 카드 %d장(3장이어야 해요) %s" % (base, len(boxes), boxes)); continue
        for nm, b in zip(["joker-c", "joker-b", "back"], boxes): save(im, b, nm)
        print("조커·뒷면:", [(b[2] - b[0], b[3] - b[1]) for b in boxes])
print("문제:", bad or "없음", "| 파일", len(glob.glob(os.path.join(OUT, "*.webp"))), "장")
