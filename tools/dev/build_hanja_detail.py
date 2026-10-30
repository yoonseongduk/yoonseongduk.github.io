"""data/hanja-detail.json 만들기: 한자별 유래·한자어 예(hd*.txt) + 사자성어 속 쓰임 + 같은 부수 한자.
사용: cd tools/dev 이동 후  py build_hanja_detail.py
새 급수를 추가하려면 hd6.txt 처럼 같은 형식(한자|유래|예1|예2|예3)의 파일을 만들고 아래 FILES에 이름을 더하세요."""
import json, re, os, glob, unicodedata as ud
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILES = ["hd5.txt", "hd6.txt", "hd7.txt", "hd8.txt", "hd9.txt", "hd10.txt"]            # 6급 300자는 hd_rows.json(= hd1~4 정리본)
rows = json.load(open("hd_rows.json", encoding="utf-8"))
rows["文"] = ["사람 가슴에 무늬를 새긴 모양에서 '글월, 무늬'", "文章(문장)=글", "文字(문자)=글자", "人文(인문)=사람의 학문"]
for f in FILES:
    if not os.path.exists(f): continue
    for l in open(f, encoding="utf-8").read().split("\n"):
        if not l.strip(): continue
        p = l.split("|"); assert len(p) >= 2, (f, l[:30]); rows[p[0]] = p[1:]   # 한자|유래|예1|예2|예3 (예는 0~3개)
d = json.load(open(REPO + "/data/hanja.json", encoding="utf-8"))
dset = {x[0] for x in d}; norm = {ud.normalize("NFKC", c): c for c in dset}
fixed = {}
for c, v in rows.items():
    k = c if c in dset else norm.get(ud.normalize("NFKC", c))
    if k is None: print("데이터에 없는 글자:", c); continue
    fixed[k] = v
idi = [l.split("|") for l in open("idiom_data.txt", encoding="utf-8").read().split("\n") if l.strip()]
byc = {}
for r in idi:
    for c in set(r[1]): byc.setdefault(ud.normalize("NFKC", c), []).append([r[0], r[1], r[2]])
rad = {}
for x in d:
    m = re.search(r"부수 (\S+)", x[3])
    if m: rad.setdefault(m.group(1), []).append(x)
out = {}
for x in d:
    c = x[0]; e = {}
    if c in fixed: e["o"] = fixed[c][0]; e["w"] = fixed[c][1:]
    ids = byc.get(ud.normalize("NFKC", c), [])[:4]
    if ids: e["i"] = ids
    m = re.search(r"부수 (\S+)", x[3])
    if m:
        sib = sorted([y for y in rad[m.group(1)] if y[0] != c], key=lambda y: -int(y[2][0]))[:8]
        if sib: e["r"] = [m.group(1), [[y[0], y[1]] for y in sib]]
    out[c] = e
json.dump(out, open(REPO + "/data/hanja-detail.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("한자", len(out), "자, 유래·예 있는 글자", sum(1 for v in out.values() if "o" in v))
