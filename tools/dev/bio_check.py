# 생물 사진 확인 화면(bio-check.html) 만들기 — 2026-11-28 사용자 요청: 생물 퀴즈 사진을 한 번에 확인.
#   bio_wiki.json(사진 있는 이름)·bio_reject.json(사진 없는 이름)으로 out/bio-check.html 을 만들고 ship.py 로 올려요(시작 화면 카드 없음, 주소로만 열기).
#   사진은 '사진 보기'를 누르면 사진마다 커먼즈 파일 주소(Special:FilePath, 폭 320)를 그림으로 바로 띄워요(API를 쓰지 않아 요청 제한(429)에 안 걸림,
#   화면에 보이는 것만 차례로 받음, 저장 안 함). 2026-11-28: 50장씩 API로 묻던 방식이 429로 막혀 사진이 안 떴음.
#   시작 화면에는 '생물 퀴즈' 묶음의 모드(merged.json)로 들어가 있어 '생물 사진'으로 검색돼요.
#   사진마다 ❌ 이상해요 → 📋 목록 복사로 개발자에게 전달 → bio_build.py 의 EXCLUDE 등으로 고침.
import json, mkpage
M = json.load(open("bio_wiki.json", encoding="utf-8")); RJ = json.load(open("bio_reject.json", encoding="utf-8"))
QN = {"animal-quiz.html": "동물", "sea-quiz.html": "바다 생물", "insect-quiz.html": "곤충", "plant-quiz.html": "식물", "dino-quiz.html": "공룡"}
items = [[QN[f], n, v[0], v[1]] for f, m in M.items() for n, v in m.items()]
nophoto = [[QN[f], n] for f, ns in RJ.items() for n in ns]
body = """
<div class="card"><p class="muted" style="margin:0 0 8px">생물 퀴즈에서 정답 뒤에 나오는 사진을 한 번에 확인해요. 사진은 위키미디어 커먼즈에서 불러오고 폰에 저장하지 않아요.</p>
<button class="btn" id="load" type="button" style="width:100%">📷 사진 보기 (인터넷)</button>
<div id="qs" class="chips" style="display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 0"></div>
<p class="muted" id="st" style="margin:8px 0 0"></p></div>
<div id="grid" class="grid"></div>
<div class="card"><b>❌ 이상하다고 표시한 사진 <span id="bc">0</span>개</b><p class="muted" id="bl" style="margin:6px 0">없음</p>
<button class="btn" id="copy" type="button" style="width:100%">📋 목록 복사(개발자에게 보내기)</button>
<button class="btn ghost" id="clr" type="button" style="width:100%;margin-top:6px">표시 모두 지우기</button></div>
<div class="card"><b>📭 사진이 없는 이름</b><p class="muted" style="margin:6px 0">그 생물만 찍힌 사진을 찾지 못했거나(다른 동물·뼈·다른 종 사진), 새끼 이름·여러 종을 묶은 이름이라 뺐어요. 꼭 보고 싶은 생물은 이름을 알려 주세요.</p><div id="np"></div></div>
"""
css = """.fgzoom{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.92);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:12px;cursor:zoom-out}
.fgzoom img{max-width:100%;max-height:calc(100% - 48px);object-fit:contain}
.fgzoom p{color:#fff;margin:8px 0 0;font-size:.9rem;text-align:center}
.fgzoom .fgzx{position:absolute;top:10px;right:10px;width:44px;height:44px;border-radius:50%;border:0;background:rgba(255,255,255,.2);color:#fff;font-size:1.3rem;cursor:pointer}
.it img{cursor:zoom-in}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0}
.it{border:1px solid var(--line,rgba(127,127,127,.3));border-radius:12px;padding:6px;background:var(--card,transparent);font-size:.82rem;min-width:0}
.it .ph{height:120px;display:flex;align-items:center;justify-content:center;background:rgba(127,127,127,.12);border-radius:8px;overflow:hidden}
.it img{max-width:100%;max-height:120px;object-fit:contain}
.it b{display:block;margin:4px 0 0}.it .s{opacity:.7;font-size:.72rem;word-break:break-all}
.it a{color:inherit}.it button{margin-top:4px;width:100%;font:inherit;font-size:.78rem;padding:5px;border-radius:8px;border:1px solid rgba(127,127,127,.45);background:transparent;color:inherit;cursor:pointer}
.it.bad{outline:3px solid #d33}.it.bad button{background:#d33;color:#fff;border-color:#d33}
.chip{font:inherit;font-size:.85rem;padding:5px 10px;border-radius:999px;border:1px solid rgba(127,127,127,.45);background:transparent;color:inherit;cursor:pointer}.chip.on{background:var(--accent,#2a7);color:#fff;border-color:transparent}
#np span{display:inline-block;margin:2px 4px 2px 0;padding:2px 8px;border-radius:999px;background:rgba(127,127,127,.15);font-size:.8rem}"""
js = r"""
/* 사진 크게 보기(2026-11-28 사용자 요청): 사진을 누르면 화면 전체에 크게. 작은 그림을 먼저 보이고 큰 그림(폭 1280)을 받으면 바꿔요. 화면·✕를 누르거나 뒤로 가기로 닫혀요. */
function fgZoom(small, file, cap) {
  var o = document.createElement("div"); o.className = "fgzoom"; o.setAttribute("role", "dialog"); o.setAttribute("aria-label", "사진 크게 보기");
  o.innerHTML = '<button type="button" class="fgzx" aria-label="닫기">✕</button><img alt=""><p></p>';
  var im = o.querySelector("img"); im.src = small; im.alt = cap || ""; o.querySelector("p").textContent = cap || "";
  if (file) { var big = new Image(); big.referrerPolicy = "no-referrer"; big.onload = function () { im.src = big.src; }; big.src = "https://commons.wikimedia.org/wiki/Special:FilePath/" + encodeURIComponent(file) + "?width=1280"; }
  var closed = false;
  function close(fromBack) { if (closed) return; closed = true; o.remove(); window.removeEventListener("popstate", onPop); if (!fromBack) try { history.back(); } catch (e) {} }
  function onPop() { close(true); }
  o.addEventListener("click", function () { close(false); });
  document.body.appendChild(o);
  try { history.pushState({ fgzoom: 1 }, ""); } catch (e) {}
  window.addEventListener("popstate", onPop);
}
const IT = /*IT*/[]/*/IT*/, NP = /*NP*/[]/*/NP*/, BK = "bio-check-v1";
let bad = ld(BK) || {}, cat = "전체", on = false;
const src = f => "https://commons.wikimedia.org/wiki/Special:FilePath/" + encodeURIComponent(f) + "?width=320";
const QS = ["전체", ...new Set(IT.map(x => x[0]))];
const k = x => x[0] + "|" + x[1];
function draw() {
  $("qs").innerHTML = QS.map(q => `<button class="chip ${q === cat ? "on" : ""}" type="button" data-q="${esc(q)}">${esc(q)} ${q === "전체" ? IT.length : IT.filter(x => x[0] === q).length}</button>`).join("");
  $("grid").innerHTML = IT.filter(x => cat === "전체" || x[0] === cat).map(x => { const b = bad[k(x)];
    return `<div class="it ${b ? "bad" : ""}"><div class="ph">${on ? `<img data-f="${esc(x[2])}" src="${esc(src(x[2]))}" alt="${esc(x[1])}" loading="lazy" referrerpolicy="no-referrer" onerror="this.replaceWith('사진 못 받음')">` : "📷"}</div><b>${esc(x[1])}</b><span class="s">${esc(x[0])} · <a href="https://commons.wikimedia.org/wiki/File:${encodeURIComponent(x[2])}" target="_blank" rel="noopener">원본</a></span><button type="button" data-b="${esc(k(x))}">${b ? "❌ 이상해요 (취소)" : "❌ 이상해요"}</button></div>`; }).join("");
  const L = Object.keys(bad); $("bc").textContent = L.length; $("bl").textContent = L.length ? L.map(s => s.replace("|", ": ")).join(", ") : "없음";
  $("np").innerHTML = QS.slice(1).map(q => `<p style="margin:6px 0 2px"><b>${esc(q)}</b></p>` + NP.filter(x => x[0] === q).map(x => `<span>${esc(x[1])}</span>`).join("")).join("");
}
$("qs").addEventListener("click", e => { const b = e.target.closest("[data-q]"); if (b) { cat = b.dataset.q; draw(); } });
$("grid").addEventListener("click", e => { const im = e.target.closest(".it img"); if (im) { const x = IT.find(x => im.dataset.f === x[2]); return fgZoom(im.src, im.dataset.f, x ? x[1] + " · " + x[0] : ""); } const b = e.target.closest("[data-b]"); if (!b) return; if (bad[b.dataset.b]) delete bad[b.dataset.b]; else bad[b.dataset.b] = 1; sv(BK, bad); draw(); });
$("clr").onclick = () => { if (confirm("표시를 모두 지울까요?")) { bad = {}; sv(BK, bad); draw(); } };
$("copy").onclick = () => { const t = "[생물 사진 이상] " + (Object.keys(bad).map(s => s.replace("|", ": ")).join(", ") || "없음"); (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(() => alert("복사했어요. 대화창에 붙여 넣어 보내 주세요."), () => prompt("아래 글을 복사해 주세요", t)); };
$("load").onclick = () => { on = true; draw(); $("st").textContent = "사진은 화면을 내리면 차례로 나와요. 이상한 사진은 ❌를 눌러 표시해 주세요."; $("load").hidden = true; };
draw();
"""
js = js.replace("/*IT*/[]/*/IT*/", json.dumps(items, ensure_ascii=False)).replace("/*NP*/[]/*/NP*/", json.dumps(nophoto, ensure_ascii=False))
mkpage.make("out/bio-check.html", "생물 사진 모아 보기", "📷", 150, "bio-check-v1", "생물 퀴즈 사진을 한 번에 보고, 이상한 사진을 표시해 개발자에게 보내요.", body, js, css)
print("사진 있음", len(items), "· 사진 없음", len(nophoto))
