#!/usr/bin/env python3
"""퀴즈 추가 문제: tools/dev/qmore/<퀴즈 파일 이름에서 .html 뺀 것>.txt 의 문제를 그 퀴즈의 문제 목록(D)에 합쳐요.
줄 형식(빈 줄·#로 시작하는 줄은 건너뜀)
  일반 퀴즈      : 문제|정답|오답1|오답2|오답3
  국기·이모지 영어: 그림|정답            (오답은 퀴즈가 다른 정답에서 자동으로 골라요)
  이모지 퀴즈    : 그림|이름|분류
  OX 퀴즈        : 문장|O 또는 X|분류|해설
기존 문제와 같은 문제(첫 칸이 같음)는 넣지 않아요. 정답이 오답에 섞이거나 오답이 겹치면 오류로 멈춰요.
사용: py qmore.py            → 저장소의 퀴즈 파일(.html)에 바로 합쳐요(생성기가 없는 퀴즈도 돼요)
      mkquiz.make()도 이 파일을 읽어 합치므로, 생성기로 다시 만들어도 추가 문제가 남아요."""
import os, re, json, sys
DEV = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.join(DEV, "qmore"); REPO = os.path.abspath(os.path.join(DEV, "..", ".."))

def _lines(name):
    p = os.path.join(DIR, name + ".txt")
    if not os.path.exists(p): return []
    return [l.rstrip("\n").rstrip("\r") for l in open(p, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]

def _row(f, base):
    """f: 칸 목록, base: 원래 문제 하나(모양을 따라 해요)"""
    q, a = f[0].strip(), f[1].strip()
    if isinstance(base[1], str) and re.match(r"^[OX] ", base[1]):                      # OX 퀴즈
        assert a in ("O", "X"), f"OX 답은 O 또는 X: {f}"
        return [q, "O 맞아요" if a == "O" else "X 아니에요", [], f[2].strip() if len(f) > 2 else "", f[3].strip() if len(f) > 3 else ""]
    if len(base) == 2: return [q, a]                                                      # 국기·이모지 영어
    if base[2] is None: return [q, a, None, f[2].strip() if len(f) > 2 else ""]           # 이모지 퀴즈(분류)
    w = [x.strip() for x in f[2:5]]
    assert len(w) == 3 and all(w), f"오답 3개가 필요해요: {f}"
    assert a not in w and len(set(w)) == 3, f"정답이 오답에 있거나 오답이 겹쳐요: {f}"
    r = [q, a, w]
    if len(base) >= 4: r.append(f[5].strip() if len(f) > 5 else (base[3] if isinstance(base[3], str) else ""))
    if len(base) >= 5: r.append(f[6].strip() if len(f) > 6 else "")
    return r

def merge(fname, data):
    """fname: 'xxx-quiz.html', data: 원래 문제 목록 → 추가 문제를 합친 새 목록"""
    name = os.path.basename(fname)[:-5]; ls = _lines(name)
    if not ls or not data: return data
    seen = {r[0] for r in data}; out = list(data)
    for l in ls:
        r = _row(l.split("|"), data[0])
        if r[0] in seen: continue
        seen.add(r[0]); out.append(r)
    return out

def apply_all():
    for t in sorted(os.listdir(DIR)):
        if not t.endswith(".txt"): continue
        f = os.path.join(REPO, t[:-4] + ".html"); h = open(f, encoding="utf-8").read()
        i = h.index("const D = ["); j = i + re.search(r"\];\r?\n", h[i:]).start(); d = json.loads(h[i + 10:j + 1])
        # 원래 문제 목록은 qmore/base/<이름>.json 에 한 번 저장해 두고, 매번 '원래 + 추가 문제'로 새로 만들어요(추가 문제를 고치거나 지워도 반영되게)
        bp = os.path.join(DIR, "base", t[:-4] + ".json"); os.makedirs(os.path.dirname(bp), exist_ok=True)
        if not os.path.exists(bp):
            assert len(merge(f, d)) != len(d) or not _lines(t[:-4]), f"{t}: 이미 합쳐진 것 같아요. git에서 원래 파일을 되돌린 뒤 다시 하세요"
            json.dump(d, open(bp, "w", encoding="utf-8"), ensure_ascii=False)
        base = json.load(open(bp, encoding="utf-8")); nd = merge(f, base)
        if nd != d: open(f, "w", encoding="utf-8").write(h[:i + 10] + json.dumps(nd, ensure_ascii=False) + h[j + 1:])
        print(f"{t[:-4]:<22} {len(base):>4} → {len(nd):>4}")

if __name__ == "__main__":
    apply_all()
