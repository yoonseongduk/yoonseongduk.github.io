#!/usr/bin/env python3
"""획순 데이터가 없는 글자(data/stroke-missing.json)의 번호 위치를 '글자 분해'로 추정해요.
  1) cjkvi-ids 의 글자 분해식(IDS)으로 글자를 부품으로 나눠요  (https://github.com/cjkvi/cjkvi-ids)
  2) 부품마다 Make Me a Hanzi 의 획 좌표를 가져와 부품 자리(왼쪽/위쪽 …)에 맞게 옮겨 붙여요
  3) 총 획수가 data/hanja.json 의 '총 N획' 과 같은 글자만 채택해요
  결과: tools/dev/auto_raw.json  → (snap_auto.js 로 글꼴 모양에 맞춰 보정) → data/stroke-auto.json
사용법: python build_stroke_auto.py [graphics.txt] [ids.txt]   (없으면 내려받아요)"""
import json, re, sys, os, urllib.request
gp = sys.argv[1] if len(sys.argv) > 1 else "graphics.txt"; ip = sys.argv[2] if len(sys.argv) > 2 else "ids.txt"
if not os.path.exists(gp): urllib.request.urlretrieve("https://raw.githubusercontent.com/skishore/makemeahanzi/master/graphics.txt", gp)
if not os.path.exists(ip): urllib.request.urlretrieve("https://raw.githubusercontent.com/cjkvi/cjkvi-ids/master/ids.txt", ip)
G = {}
for l in open(gp, encoding="utf-8"):
    j = json.loads(l); G[j["character"]] = [[((x) / 1024, (900 - y) / 1024) for x, y in m] for m in j["medians"]]
IDS = {}
for l in open(ip, encoding="utf-8"):
    if l.startswith("#") or not l.strip(): continue
    c = l.rstrip("\n").split("\t")
    if len(c) < 3: continue
    cands = c[2:]
    pick = next((x for x in cands if "[K]" in x), None) or next((x for x in cands if "[" not in x), None) or cands[0]
    IDS[c[1]] = re.sub(r"\[[A-Z]+\]", "", pick)
ARITY = {"⿰": 2, "⿱": 2, "⿴": 2, "⿵": 2, "⿶": 2, "⿷": 2, "⿸": 2, "⿹": 2, "⿺": 2, "⿻": 2, "⿲": 3, "⿳": 3}
NARROW_L = set("氵亻忄扌彳礻衤犭阝⺖⺘𧾷糸饣讠")
SHORT_T = set("艹宀冖亠⺾𠂉人𠆢")
def parse(s, i=0):
    ch = s[i]
    if ch in ARITY:
        kids = []; j = i + 1
        for _ in range(ARITY[ch]):
            k, j = parse(s, j); kids.append(k)
        return (ch, kids), j
    return ch, i + 1
def bbox(strokes):
    xs = [p[0] for s in strokes for p in s]; ys = [p[1] for s in strokes for p in s]
    return min(xs), min(ys), max(xs), max(ys)
def place(strokes, box):
    x0, y0, x1, y1 = bbox(strokes); bx0, by0, bx1, by1 = box
    sw, sh = x1 - x0, y1 - y0; bw, bh = bx1 - bx0, by1 - by0
    out = []
    for s in strokes:
        o = []
        for x, y in s:
            nx = bx0 + (x - x0) / sw * bw if sw > .04 else (bx0 + bx1) / 2 + (x - (x0 + x1) / 2) * min(1, bw / .12)
            ny = by0 + (y - y0) / sh * bh if sh > .04 else (by0 + by1) / 2 + (y - (y0 + y1) / 2) * min(1, bh / .12)
            o.append((nx, ny))
        out.append(o)
    return out
def leaf(ch, depth=0):
    if ch in G: return [list(s) for s in G[ch]]
    if depth < 6 and ch in IDS and IDS[ch] != ch:
        t, _ = parse(IDS[ch]); return strokes_of(t, (0.08, 0.08, 0.92, 0.92), depth + 1)
    return None
def strokes_of(node, box, depth=0):
    if isinstance(node, str):
        s = leaf(node, depth)
        return place(s, box) if s else None
    op, kids = node; x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    names = [k if isinstance(k, str) else None for k in kids]
    if op == "⿰": r = .38 if names[0] in NARROW_L else .5; bx = [(x0, y0, x0 + w * r, y1), (x0 + w * r, y0, x1, y1)]
    elif op == "⿱": r = .34 if names[0] in SHORT_T else .5; bx = [(x0, y0, x1, y0 + h * r), (x0, y0 + h * r, x1, y1)]
    elif op == "⿲": bx = [(x0, y0, x0 + w / 3, y1), (x0 + w / 3, y0, x0 + 2 * w / 3, y1), (x0 + 2 * w / 3, y0, x1, y1)]
    elif op == "⿳": bx = [(x0, y0, x1, y0 + h / 3), (x0, y0 + h / 3, x1, y0 + 2 * h / 3), (x0, y0 + 2 * h / 3, x1, y1)]
    elif op == "⿴": bx = [(x0, y0, x1, y1), (x0 + w * .22, y0 + h * .22, x1 - w * .22, y1 - h * .22)]
    elif op == "⿵": bx = [(x0, y0, x1, y1), (x0 + w * .2, y0 + h * .28, x1 - w * .2, y1)]
    elif op == "⿶": bx = [(x0, y0, x1, y1), (x0 + w * .2, y0, x1 - w * .2, y1 - h * .28)]
    elif op == "⿷": bx = [(x0, y0, x1, y1), (x0 + w * .28, y0 + h * .2, x1, y1 - h * .2)]
    elif op == "⿸": bx = [(x0, y0, x1, y1), (x0 + w * .28, y0 + h * .28, x1, y1)]
    elif op == "⿹": bx = [(x0, y0, x1, y1), (x0, y0 + h * .28, x1 - w * .28, y1)]
    elif op == "⿺": bx = [(x0, y0, x1, y1), (x0 + w * .28, y0, x1, y1 - h * .28)]
    else: bx = [(x0, y0, x1, y1)] * len(kids)              # ⿻ 겹침
    parts = [strokes_of(k, b, depth) for k, b in zip(kids, bx)]
    if any(p is None for p in parts): return None
    if op in ("⿶", "⿺"): parts = [parts[1], parts[0]]      # 안쪽 먼저, 바깥(받침) 나중
    return [s for p in parts for s in p]
h = json.load(open("../../data/hanja.json", encoding="utf-8")); total = {}
for c, k, g, info in h:
    m = re.search(r"총 (\d+)획", info); total[c] = int(m.group(1)) if m else None
miss = json.load(open("../../data/stroke-missing.json", encoding="utf-8"))
ok = {}; bad = []; BB = {}
for c in miss:
    ids = IDS.get(c)
    if not ids or ids == c: bad.append((c, "분해식 없음")); continue
    try: t, _ = parse(ids)
    except Exception: bad.append((c, "분해식 해석 실패")); continue
    s = strokes_of(t, (0.07, 0.07, 0.93, 0.93))
    if not s: bad.append((c, "부품 자료 없음 " + ids)); continue
    if total.get(c) and len(s) != total[c]: bad.append((c, "획수 다름 %d≠%d %s" % (len(s), total[c], ids))); continue
    ok[c] = [[round(st[0][0] * 300, 1), round(st[0][1] * 300, 1)] for st in s]
    bb = bbox(s); BB[c] = [round(v * 300, 1) for v in bb]
json.dump(BB, open("auto_bbox.json", "w", encoding="utf-8"), separators=(",", ":"))
json.dump(ok, open("auto_raw.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("채택", len(ok), "/", len(miss), " 제외", len(bad))
for c, why in bad: print(" ", c, why)
