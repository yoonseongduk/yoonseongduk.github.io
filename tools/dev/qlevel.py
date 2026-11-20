#!/usr/bin/env python3
"""퀴즈 등급(초급·중급·고급) 붙이기.
 - 퀴즈 HTML(공통 틀을 쓰는 것)에 등급 단추와 `const LV = "1223…"`(문제마다 1·2·3, D와 같은 순서)을 넣어요. 여러 번 돌려도 같아요.
 - 문제별 등급을 정하는 순서: ① 규칙(한자 급수·일본어 N급·한자 사자성어) ② qmore/<이름>.txt 안의 `## 초급`·`## 중급`·`## 고급` 구역
   ③ qlevel/<이름>.json({문제: 등급}) ④ 없으면 2(중급).
 - qlevel/<이름>.json 은 `py qlevel.py import 이름 목록파일 번호등급파일` 로 만들어요(목록파일: 번호|문제|정답 줄, 번호등급파일: `번호 등급` 줄).
 - 사용: py qlevel.py          → 모든 퀴즈에 적용
        py qlevel.py 이름...   → 그 퀴즈만 (예: job-quiz)
        py qlevel.py check     → 등급별 문제 수 표"""
import os, re, json, sys
DEV = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(DEV, "..", ".."))
QL = os.path.join(DEV, "qlevel"); QM = os.path.join(DEV, "qmore")
MARK = "/*LEVEL*/"
SECT = {"초급": 1, "중급": 2, "고급": 3}

def quiz_files():
    out = []
    for f in sorted(os.listdir(REPO)):
        if not f.endswith("-quiz.html"): continue
        h = open(os.path.join(REPO, f), encoding="utf-8").read()
        if "function options(d)" in h and "ROUND = 10" in h and "const D = [" in h: out.append(f[:-5])
    return out

def read_d(h):
    h = re.sub(r'const LV = "[123]*";\n', "", h)
    i = h.index("const D = ["); j = i + re.search(r"\];\r?\n", h[i:]).start()
    return json.loads(h[i + 10:j + 1]), i, j + 2

def section_levels(name):
    p = os.path.join(QM, name + ".txt"); m = {}; cur = 0
    if not os.path.exists(p): return m
    for l in open(p, encoding="utf-8"):
        l = l.rstrip("\r\n")
        mm = re.match(r"^##\s*(초급|중급|고급)", l)
        if mm: cur = SECT[mm.group(1)]; continue
        if not l.strip() or l.lstrip().startswith("#") or not cur: continue
        m.setdefault(l.split("|")[0].strip(), cur)
    return m

def idiom_levels():
    """한자 사자성어 퀴즈용: 사자성어 퀴즈(idiom-quiz)의 등급을 한자 4글자로 찾아요"""
    h = open(os.path.join(REPO, "idiom-quiz.html"), encoding="utf-8").read(); d = read_d(h)[0]; lv = levels_for("idiom-quiz", d, h)
    return {re.match(r"^(\S+)", r[4]).group(1): int(lv[n]) for n, r in enumerate(d) if len(r) > 4 and r[4]}

def levels_for(name, D, h=None):
    if name == "hanja-quiz":
        return "".join("1" if r[3] in ("6급", "5급") else "2" if r[3] in ("4급", "3급") else "3" for r in D)
    if name == "jlpt-quiz":
        return "".join("1" if r[3] in ("N5", "N4") else "2" if r[3] == "N3" else "3" for r in D)
    if name == "hanja-idiom-quiz":
        im = idiom_levels(); out = []
        for r in D:
            m = re.match(r"^([一-鿿]{4})", r[4] or "")
            out.append(str(im.get(m.group(1), 2)) if m else "2")
        return "".join(out)
    jp = os.path.join(QL, name + ".json"); jm = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
    sm = section_levels(name)
    return "".join(str(sm.get(r[0], jm.get(r[0], 2))) for r in D)

# ── 화면(공통 틀) 고치기
HTML_ADD = '''  <div class="chips" id="lvs" role="group" aria-label="등급"></div>
  <p class="muted" id="lvp"></p>
'''
JS_ADD = r'''/*LEVEL*/
const LVN = ["전체", "🌱 초급", "🌿 중급", "🌳 고급"], LVM = [1, 1, 1.5, 2], LVK = KEY.split("-best-").join("-lv-") === KEY ? KEY + "-lv" : KEY.split("-best-").join("-lv-");
let lv = +ld(LVK) || 0; if (!(lv >= 0 && lv <= 3)) lv = 0;
const lvOf = n => +(typeof LV === "string" && LV[n] || 2), lvCnt = l => D.filter((d, n) => lvOf(n) === l).length, bestKey = () => lv ? KEY + "-L" + lv : KEY;
best = ld(bestKey()) || 0;
function renderLv() {
  if (lv && lvCnt(lv) < 4) lv = 0;
  window.FG_MULT = LVM[lv]; window.FG_LV = lv ? LVN[lv].slice(3) : "";
  $("lvs").innerHTML = LVN.map((n, k) => `<button class="chip ${k === lv ? "on" : ""}" type="button" data-l="${k}" aria-pressed="${k === lv}">${n}${k ? `<small> ${lvCnt(k)}</small>` : ""}</button>`).join("");
  $("lvp").textContent = lv ? `${LVN[lv].slice(3)} 문제예요. 포인트가 ×${LVM[lv]}배로 쌓여요.` : "초급 ×1 · 중급 ×1.5 · 고급 ×2 포인트 (전체는 ×1)";
}
$("lvs").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b) { lv = +b.dataset.l; sv(LVK, lv); best = ld(bestKey()) || 0; start(); } });
'''

def patch_html(h):
    if MARK in h: return h
    a = '  <div class="chips" id="cats" role="group" aria-label="분류" hidden></div>\n'
    assert a in h, "분류 줄을 못 찾음"
    h = h.replace(a, HTML_ADD + a, 1)
    a = "let cat = \"전체\", qs = [], i = 0, score = 0, best = ld(KEY) || 0, locked = false;\n"
    assert a in h, "상태 줄을 못 찾음"
    h = h.replace(a, a + JS_ADD, 1)
    a = 'const pool = D.filter(d => cat === "전체" || d[3] === cat);'
    assert a in h, "pool 줄을 못 찾음"
    h = h.replace(a, 'renderLv(); const pool = D.filter((d, n) => (!lv || lvOf(n) === lv) && (cat === "전체" || d[3] === cat));', 1)
    a = "sv(KEY, best); note"
    assert a in h, "최고 기록 줄을 못 찾음"
    h = h.replace(a, "sv(bestKey(), best); note", 1)
    return h

# ── 🚩 문제 오류 신고(공통 틀): 신고한 문제는 localStorage "quiz-flags-v1" = {퀴즈 파일: {문제: {a: 정답, p: 내가 고른 답, t: 시각}}} 에 저장하고, quiz-flags.html 에서 모아 보고 복사해요
FMARK = "/*FLAG*/"
FLAG_CSS = ".flagb{margin-top:8px;background:transparent;border:1px dashed var(--line);border-radius:999px;padding:4px 12px;font-family:var(--font-body);font-size:.85rem;color:var(--muted)}.flagb.on{border-style:solid;border-color:var(--bad);color:var(--bad)}\n"
FLAG_JS = r'''/*FLAG*/
const FLK = "quiz-flags-v1", FLF = (location.pathname.split("/").pop() || "quiz-quiz.html");
const flAll = () => { const v = ld(FLK); return v && typeof v === "object" ? v : {}; }, isFlag = q => !!(flAll()[FLF] || {})[q];
function toggleFlag(d, picked) { const all = flAll(), m = all[FLF] || (all[FLF] = {}); if (m[d[0]]) delete m[d[0]]; else m[d[0]] = { a: String(d[1]), p: String(picked || ""), t: Date.now() }; if (!Object.keys(m).length) delete all[FLF]; sv(FLK, all); }
function showFlag(d, picked) { $("q").insertAdjacentHTML("beforeend", `<button class="flagb ${isFlag(d[0]) ? "on" : ""}" type="button" data-flag="1">${isFlag(d[0]) ? "🚩 신고했어요 (누르면 취소)" : "🚩 문제가 이상해요"}</button>`); $("q").querySelector("[data-flag]").onclick = e => { toggleFlag(d, picked); e.target.classList.toggle("on", isFlag(d[0])); e.target.textContent = isFlag(d[0]) ? "🚩 신고했어요 (누르면 취소)" : "🚩 문제가 이상해요"; }; }
'''

def patch_flag(h):
    if FMARK in h: return h
    a = "/*LEVEL*/"
    assert a in h, "등급 패치가 먼저 필요해요"
    h = h.replace(a, FLAG_JS + a, 1)
    a = '  $("score").textContent = score; $("next").textContent = i === qs.length - 1 ? "결과 보기" : "다음 문제"; $("next").hidden = false;\n}'
    assert h.count(a) == 1, "pick 끝 줄을 못 찾음"
    h = h.replace(a, "  showFlag(d, opts[k]);\n" + a, 1)
    a = '(!lv || lvOf(n) === lv) && (cat === "전체" || d[3] === cat));'
    assert a in h, "pool 줄을 못 찾음"
    h = h.replace(a, '(!lv || lvOf(n) === lv) && !isFlag(d[0]) && (cat === "전체" || d[3] === cat));', 1)   # 신고한 문제는 이 폰에서 다시 안 나와요
    h = h.replace("</style>", FLAG_CSS + "</style>", 1)
    return h

def apply_one(path):
    name = os.path.basename(path)[:-5]
    if not name.endswith("-quiz"): return None
    h = open(path, encoding="utf-8", newline="").read(); crlf = "\r\n" in h; h = h.replace("\r\n", "\n")
    if "function options(d)" not in h or "ROUND = 10" not in h: return None
    h = patch_flag(patch_html(h))
    h = re.sub(r'const LV = "[123]*";\n', "", h)
    D, i, j = read_d(h)
    lv = levels_for(name, D)
    h = h[:j] + '\nconst LV = "' + lv + '";' + h[j:]
    if crlf: h = h.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(h)
    return [lv.count(c) for c in "123"]

def import_idx(name, listfile, idxfile):
    q = {}
    for l in open(listfile, encoding="utf-8"):
        p = l.rstrip("\n").split("|")
        if len(p) >= 2 and p[0].isdigit(): q[int(p[0])] = p[1]
    out = {}
    for l in open(idxfile, encoding="utf-8"):
        p = l.split()
        if len(p) >= 2 and p[0].isdigit() and p[1] in "123" and int(p[0]) in q: out[q[int(p[0])]] = int(p[1])
    os.makedirs(QL, exist_ok=True); json.dump(out, open(os.path.join(QL, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(name, "등급", len(out), "/", len(q))

def main(a_):
    a = a_
    if a and a[0] == "import": return import_idx(a[1], a[2], a[3])
    names = quiz_files() if not a or a[0] == "check" else [x if x.endswith("-quiz") else x + "-quiz" for x in a]
    for n in names:
        c = apply_one(os.path.join(REPO, n + ".html"))
        if c: print(f"{n:24} 초급 {c[0]:4} 중급 {c[1]:4} 고급 {c[2]:4} 합계 {sum(c)}")
    if not a_ or a_[0] == "check":                      # 공통 틀이 아닌 퀴즈(속담·상식·세계 수도)도 함께
        import qlevel_custom; qlevel_custom.apply_all()

if __name__ == "__main__": main(sys.argv[1:])
