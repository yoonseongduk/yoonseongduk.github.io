#!/usr/bin/env python3
"""끝말잇기 낱말 목록(data/words-ko.txt)을 라이선스가 분명한 국립국어원 사전(우리말샘·한국어기초사전, CC BY-SA 2.0 KR)에서 다시 만든다.
사용(본인 PC에서, 한국 사이트에 접속해 사전 파일을 내려받은 뒤):
  1) 우리말샘(https://opendict.korean.go.kr) → 회원가입·로그인 → '사전 내려받기'에서 JSON 또는 XML 전체 파일을 받아 한 폴더에 풀어요.
     (한국어기초사전 https://krdict.korean.go.kr 의 내려받기 파일도 같은 방식으로 쓸 수 있어요)
  2) py tools\\dev\\build_words_from_opendict.py 폴더경로            → data/words-ko.new.txt 를 만들고 지금 목록과 비교해 보여 줘요
     py tools\\dev\\build_words_from_opendict.py 폴더경로 --apply    → 비교가 만족스러우면 data/words-ko.txt 를 바꿔요(이전 파일은 words-ko.old.txt 로 보관)
  옵션: --pos 명사,대명사,수사   (기본값; 낱말의 품사가 이 중 하나인 것만. 품사가 없는 자료는 '~다'로 끝나는 말을 빼요)
형식: 한 줄에 한 낱말, 한글 2~7글자(지금 목록과 같음). '-'·'^'·숫자 표시는 지워요.
※ 이 도구는 실제 내려받은 파일로는 아직 시험하지 못했어요(이 환경에서 사이트 접속 불가). 파일 모양이 달라 낱말이 적게 나오면 알려 주세요.
※ 라이선스: 결과물은 CC BY-SA 2.0 KR(저작자표시·동일조건변경허락)이에요. 적용하면 licenses.html 의 끝말잇기 항목과 data/words-ko-LICENSE.txt 를 함께 고쳐요(--apply 가 LICENSE 파일은 만들어 줘요)."""
import os, re, sys, json, glob
DEV = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(DEV, "..", ".."))
HANGUL = re.compile(r"^[가-힣]{2,7}$")
BAD_POS = re.compile(r"동사|형용사|보조|어미|접사|조사|관형사|부사|감탄사|구$|속담|관용")

def norm(w):
    return re.sub(r"[-^0-9\s·]", "", w or "")

def from_json(obj, out):
    """JSON 안을 훑어서 word(낱말)와 같은 항목의 pos(품사)를 찾아요. 우리말샘·한국어기초사전 모양을 모두 받아요."""
    def walk(x, skip):                       # skip=True: 이미 항목으로 센 wordinfo 안쪽(낱말만 있고 품사가 없어서 다시 세면 품사 걸러내기를 피해 가요)
        if isinstance(x, dict):
            w = None; pos = None
            wi = x.get("wordinfo")
            if isinstance(wi, dict) and isinstance(wi.get("word"), str): w = wi["word"]
            elif isinstance(x.get("word"), str): w = x["word"]
            elif isinstance(x.get("writtenForm"), str): w = x["writtenForm"]
            si = x.get("senseinfo")
            if isinstance(si, dict) and isinstance(si.get("pos"), str): pos = si["pos"]
            elif isinstance(x.get("pos"), str): pos = x["pos"]
            elif isinstance(x.get("partOfSpeech"), str): pos = x["partOfSpeech"]
            if isinstance(si, list):
                for s in si:
                    if isinstance(s, dict) and isinstance(s.get("pos"), str): pos = s["pos"]; break
            if w and not skip: out.append((w, pos))
            for k, v in x.items(): walk(v, k == "wordinfo")
        elif isinstance(x, list):
            for v in x: walk(v, False)
    walk(obj, False)

def from_xml_text(t, out):
    for m in re.finditer(r"<item>(.*?)</item>", t, re.S):
        it = m.group(1); w = re.search(r"<word>(.*?)</word>", it, re.S); p = re.search(r"<pos>(.*?)</pos>", it, re.S)
        if w: out.append((re.sub(r"<!\[CDATA\[|\]\]>", "", w.group(1)), re.sub(r"<!\[CDATA\[|\]\]>", "", p.group(1)) if p else None))

def main(a):
    if not a or a[0].startswith("-"): print(__doc__); return 1
    src = a[0]; apply = "--apply" in a
    pos_ok = set((a[a.index("--pos") + 1] if "--pos" in a else "명사,대명사,수사").split(","))
    files = [src] if os.path.isfile(src) else sorted(glob.glob(os.path.join(src, "**", "*.json"), recursive=True) + glob.glob(os.path.join(src, "**", "*.xml"), recursive=True))
    if not files: print("JSON/XML 파일을 못 찾았어요:", src); return 1
    raw = []
    for f in files:
        t = open(f, encoding="utf-8", errors="ignore").read()
        if f.lower().endswith(".json"):
            try: from_json(json.loads(t), raw)
            except Exception as e: print("건너뜀(JSON 오류)", f, e)
        else: from_xml_text(t, raw)
    words = set(); nopos = 0
    for w, pos in raw:
        w = norm(w)
        if not HANGUL.match(w): continue
        if pos:
            if not any(p in pos for p in pos_ok) or BAD_POS.search(pos): continue
        else:
            nopos += 1
            if w.endswith("다"): continue
        words.add(w)
    out = sorted(words)
    new = os.path.join(REPO, "data", "words-ko.new.txt"); open(new, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    cur = os.path.join(REPO, "data", "words-ko.txt"); old = set(l.strip() for l in open(cur, encoding="utf-8")) if os.path.exists(cur) else set()
    print(f"읽은 파일 {len(files)}개 · 항목 {len(raw):,}개 → 한글 2~7글자 낱말 {len(out):,}개 (품사 없는 항목 {nopos:,}개)")
    print(f"지금 목록 {len(old):,}개와 겹침 {len(old & words):,}개 · 새 목록에만 {len(words - old):,}개 · 지금 목록에만 {len(old - words):,}개")
    if old: print(f"→ 지금 목록의 {100*len(old & words)/len(old):.0f}%를 새 목록이 담고 있어요(낮으면 파일 모양·품사 옵션을 확인하세요)")
    if apply:
        if os.path.exists(cur): os.replace(cur, os.path.join(REPO, "data", "words-ko.old.txt"))
        os.replace(new, cur)
        open(os.path.join(REPO, "data", "words-ko-LICENSE.txt"), "w", encoding="utf-8").write("끝말잇기 낱말 목록(data/words-ko.txt) 출처·라이선스\n\n국립국어원 우리말샘(https://opendict.korean.go.kr) 또는 한국어기초사전(https://krdict.korean.go.kr)의 표제어에서 한글 2~7글자 명사만 골라 만든 목록이에요.\n라이선스: 크리에이티브 커먼즈 저작자표시-동일조건변경허락 2.0 대한민국(CC BY-SA 2.0 KR) — https://creativecommons.org/licenses/by-sa/2.0/kr/\n이 목록 파일도 같은 라이선스로 이용할 수 있어요. (생성 도구: tools/dev/build_words_from_opendict.py)\n")
        print("data/words-ko.txt 를 바꿨어요. 이어서: licenses.html 끝말잇기 항목 고치기 → py tools\\make-sw.py → 커밋")
    else: print("확인만 했어요. 적용하려면 --apply 를 붙이세요.")
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
