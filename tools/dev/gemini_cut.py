# 월별 화투 그림 시트(어두운 배경에 같은 달 카드 4장)를 카드 48장으로 잘라 cards-gemini/NN.webp 로 만든다 (결정 D15·D16)
# 원본: tools/dev/gemini_src/<월>월 <이름>.png (예: "1월 송학.png"). 카드 4장 = 왼쪽부터 번호 (월-1)*4 + 0~3
# 실행: tools\dev 에서 py gemini_cut.py   (월마다 카드 4장을 찾았는지 알려 준다)
import os, re, glob, sys
from PIL import Image, ImageDraw
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gemini_src")
OUT = os.path.join(HERE, "..", "..", "cards-gemini")
os.makedirs(OUT, exist_ok=True)
TW, TH = 200, 322   # 카드 한 장 크기(px), 높이/폭 = 1.61 (화면 CSS 의 .art-gm 비율과 같아야 함)
CARD_Y0, CARD_H = 219, 695  # 시트 안 카드의 위쪽 y 와 높이(2월 시트에서 잰 값, 모든 시트가 같은 배치)

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
    # 시트 배치가 모두 같다: 카드 4장은 같은 높이 줄에 있고 폭 431px. 가로 위치만 찾고 세로는 밝은 카드 종이가 가장 많은 줄(2월 등 기준)에 맞춘다.
    a = np.array(im.convert("RGB")).astype(int)
    mask = a.sum(2) > 480
    hh = mask.shape[0]
    rs = [x for x in runs(mask.sum(0), hh * 0.1, 6) if x[1] - x[0] > 60]
    return [(x0, CARD_Y0, x1 + 1, CARD_Y0 + CARD_H) for x0, x1 in rs]

def rounded(t, rad):
    w, h = t.size
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=rad * 4, fill=255)
    t.putalpha(m.resize((w, h), Image.LANCZOS))
    return t

files = {}
for p in glob.glob(os.path.join(SRC, "*월 *.png")):
    m = re.match(r"(\d+)월 ", os.path.basename(p))
    if m: files[int(m.group(1))] = p
bad = []
for mon in range(1, 13):
    if mon not in files: bad.append("%d월 그림 없음" % mon); continue
    im = Image.open(files[mon]); boxes = find_cards(im)
    if len(boxes) != 4: bad.append("%d월: 카드 %d장만 찾았어요 %s" % (mon, len(boxes), boxes)); continue
    for k, b in enumerate(boxes):
        t = im.convert("RGBA").crop(b).resize((TW, TH), Image.LANCZOS)
        rounded(t, round(TW * 0.07)).save(os.path.join(OUT, "%02d.webp" % ((mon - 1) * 4 + k)), quality=90, method=6)
    ws = [b[2] - b[0] for b in boxes]; hs = [b[3] - b[1] for b in boxes]
    print("%d월: 카드 %s x %s (비율 %.2f)" % (mon, ws, hs, sum(hs) / sum(ws)))
print("문제:", bad or "없음", "| 파일", len(glob.glob(os.path.join(OUT, "*.webp"))), "장")
