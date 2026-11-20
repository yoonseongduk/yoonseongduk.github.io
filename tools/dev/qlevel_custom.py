#!/usr/bin/env python3
"""공통 틀이 아닌 퀴즈(속담·상식·세계 수도)에 등급(초급·중급·고급)을 붙여요. qlevel.py 가 부릅니다(여러 번 돌려도 같음).
등급 파일: qlevel/<이름>.json = {키: 등급}. 키 = 속담 `앞[정답]뒤`, 상식 `문제 앞 70자`, 수도 `나라 이름`.
시계 읽기·초성 퀴즈는 따로 고쳤어요(각각 clock-quiz.html·chosung-quiz.html 안의 등급 코드)."""
import os, re, json
DEV = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(DEV, "..", "..")); QL = os.path.join(DEV, "qlevel")
MARK = "/*LEVEL*/"
CSS = ".chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.9rem;font-family:inherit;color:inherit;cursor:pointer}.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg)}.chip small{opacity:.7}\n"
JS = r'''/*LEVEL*/
const LVN = ["전체", "🌱 초급", "🌿 중급", "🌳 고급"], LVM = [1, 1, 1.5, 2], LVK = KEY.split("-best-").join("-lv-") === KEY ? KEY + "-lv" : KEY.split("-best-").join("-lv-");
let lv = +ld(LVK) || 0; if (!(lv >= 0 && lv <= 3)) lv = 0;
const lvOf = n => +(typeof LV === "string" && LV[n] || 2), lvCnt = l => @@LIST@@.filter((d, n) => lvOf(n) === l).length, bestKey = () => lv ? KEY + "-L" + lv : KEY;
best = ld(bestKey()) || @@BEST0@@;
function renderLv() {
  if (lv && lvCnt(lv) < 4) lv = 0;
  window.FG_MULT = LVM[lv]; window.FG_LV = lv ? LVN[lv].slice(3) : "";
  $("lvs").innerHTML = LVN.map((n, k) => `<button class="chip ${k === lv ? "on" : ""}" type="button" data-l="${k}" aria-pressed="${k === lv}">${n}${k ? `<small> ${lvCnt(k)}</small>` : ""}</button>`).join("");
  $("lvp").textContent = lv ? `${LVN[lv].slice(3)} 문제예요. 포인트가 ×${LVM[lv]}배로 쌓여요.` : "초급 ×1 · 중급 ×1.5 · 고급 ×2 포인트 (전체는 ×1)";
}
$("lvs").addEventListener("click", e => { const b = e.target.closest("[data-l]"); if (b) { lv = +b.dataset.l; sv(LVK, lv); best = ld(bestKey()) || @@BEST0@@; start(); } });
'''
HTML = '  <div class="chips" id="lvs" role="group" aria-label="등급"></div>\n  <p class="muted" id="lvp"></p>\n'
CFG = {
 "proverb-quiz": dict(list="D", best0="0", html_before='  <div class="stats">', start=('function start() { qs = shuf(D).slice(0, 10)', 'function start() { renderLv(); qs = shuf(D.filter((d, n) => !lv || lvOf(n) === lv)).slice(0, 10)'),
                      fin=('if (score > best) { best = score; sv(KEY, best);', 'if (score > best) { best = score; sv(bestKey(), best);'), key=lambda r: f"{r[0]}[{r[1]}]{r[2]}"),
 "trivia-quiz": dict(list="D", best0="0", html_before='  <div class="chips" id="cats"', start=('const pool = D.filter(d => cat === "전체" || d[0] === cat);', 'renderLv(); const pool = D.filter((d, n) => (!lv || lvOf(n) === lv) && (cat === "전체" || d[0] === cat));'),
                     fin=('sv(KEY, best); note', 'sv(bestKey(), best); note'), key=lambda r: str(r[1])[:70]),
 "capital-quiz": dict(list="C", best0="[0, 0]", html_before='  <div class="seg" id="dir"', start=('qs = shuf(C).slice(0, 10).map(c => {', 'renderLv(); qs = shuf(C.filter((c, n) => !lv || lvOf(n) === lv)).slice(0, 10).map(c => {'),
                      fin=('best[dir] = score; sv(KEY, best);', 'best[dir] = score; sv(bestKey(), best);'), key=None),
}
def read_d(h):
    i = h.index("const D = ["); j = i + re.search(r"\];\r?\n", h[i:]).start(); return json.loads(h[i + 10:j + 1]), j + 2
def apply(name):
    c = CFG[name]; p = os.path.join(REPO, name + ".html"); h = open(p, encoding="utf-8", newline="").read(); crlf = "\r\n" in h; h = h.replace("\r\n", "\n")
    h = re.sub(r'\nconst LV = "[123]*";', "", h)
    if MARK not in h:
        assert c["html_before"] in h, name + " html"; h = h.replace(c["html_before"], HTML + c["html_before"], 1)
        m = re.search(r"^let [^\n]*best = ld\(KEY\)[^\n]*\n", h, re.M); assert m, name + " state"
        js = JS.replace("@@LIST@@", c["list"]).replace("@@BEST0@@", c["best0"])
        h = h[:m.end()] + js + h[m.end():]
        for a, b in (c["start"], c["fin"]): assert a in h, (name, a[:30]); h = h.replace(a, b, 1)
        if ".chip{" not in h: h = h.replace("</style>", CSS + "</style>", 1)
    jp = os.path.join(QL, name + ".json"); jm = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
    if name == "capital-quiz":
        m = re.search(r'const C = "([^"]+)"', h); C = [x.split(":") for x in m.group(1).split(" ")]
        lv = "".join(str(jm.get(x[0], 2)) for x in C)
        e = h.index("\n", h.index("const C = ")); h = h[:e] + '\nconst LV = "' + lv + '";' + h[e:]
    else:
        D, j = read_d(h); lv = "".join(str(jm.get(c["key"](r), 2)) for r in D)
        h = h[:j] + '\nconst LV = "' + lv + '";' + h[j:]
    import qlevel; h = qlevel.patch_guard(h)          # 분류까지 고르면 문제가 0개가 될 수 있는 퀴즈(상식)는 등급을 전체로 되돌려요
    if crlf: h = h.replace("\n", "\r\n")
    open(p, "w", encoding="utf-8", newline="").write(h)
    return [lv.count(x) for x in "123"]
def apply_all():
    for n in CFG:
        if os.path.exists(os.path.join(QL, n + ".json")):
            c = apply(n); print(f"{n:24} 초급 {c[0]:4} 중급 {c[1]:4} 고급 {c[2]:4} 합계 {sum(c)}")
if __name__ == "__main__": apply_all()
