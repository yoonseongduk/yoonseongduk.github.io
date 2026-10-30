import sys
sys.path.insert(0, ".")
from mkpage import make
BODY = '''  <div class="card" id="intro"><p>질문에 얼마나 공감하는지 고르면 <b>16가지 성격 유형</b> 중 나와 가까운 유형을 알려 줘요. 28문항, 약 3분 걸려요.</p><p class="muted">공식 MBTI® 검사가 아니에요. 재미로 만든 비슷한 방식의 테스트예요.</p><button class="btn" id="start" type="button">시작하기</button><div id="last"></div></div>
  <div class="card" id="quiz" hidden><div class="step"><span class="muted" id="qn">1 / 28</span><span class="muted" id="axis"></span></div><div class="bar"><i id="prog"></i></div><p class="q" id="qt"></p><div class="ans" id="ans"></div><button class="btn ghost" id="back" type="button">← 이전 문항</button></div>
  <div id="result" hidden></div>'''
CSS = '''.bar{height:8px;border-radius:99px;background:var(--soft);overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--accent);transition:width .2s}.q{font-family:var(--font-display);font-size:1.35rem;line-height:1.5;min-height:4.2em;display:flex;align-items:center}.ans{display:grid;gap:8px}.ans button{background:var(--surface);border:2px solid var(--line);border-radius:14px;padding:12px;font-weight:700;text-align:left}.ans button.on{border-color:var(--accent);background:var(--soft)}.rt{font-family:var(--font-display);font-size:3rem;letter-spacing:.06em;color:var(--accent);line-height:1.1}.rn{font-family:var(--font-display);font-size:1.4rem}.ax{display:grid;gap:10px}.ax .r{display:grid;gap:4px}.ax .l{display:flex;justify-content:space-between;font-size:.88rem;font-weight:700}.ax .t{height:12px;background:var(--soft);border-radius:99px;position:relative;overflow:hidden}.ax .t i{position:absolute;top:0;bottom:0;background:var(--accent);border-radius:99px}.tags{display:flex;flex-wrap:wrap;gap:6px}.tags span{background:var(--soft);border-radius:999px;padding:3px 10px;font-size:.88rem}.sec{display:grid;gap:4px}.sec b{font-size:.95rem}.sec ul{margin:0;padding-left:20px}'''
JS = r'''
const Q = [
 ["처음 보는 사람과도 금방 이야기를 시작한다.", "EI", 1], ["사람들과 함께 있으면 에너지가 생긴다.", "EI", 1], ["쉬는 날에는 혼자 조용히 보내는 것이 더 좋다.", "EI", -1], ["모임에서 말을 많이 하는 편이다.", "EI", 1], ["생각을 충분히 정리한 뒤에 말하는 편이다.", "EI", -1], ["전화나 메시지보다 직접 만나서 이야기하는 것이 편하다.", "EI", 1], ["많은 사람 앞에 나서는 일이 부담스럽다.", "EI", -1],
 ["상상이나 가능성을 이야기하는 것이 재미있다.", "SN", -1], ["눈에 보이는 사실과 직접 겪은 경험을 더 믿는다.", "SN", 1], ["새로운 방법보다 검증된 방법이 마음 편하다.", "SN", 1], ["대화할 때 비유나 은유를 자주 쓴다.", "SN", -1], ["일할 때 세부 사항을 꼼꼼히 챙기는 편이다.", "SN", 1], ["어떤 일을 보면 미래의 가능성부터 떠올린다.", "SN", -1], ["설명서는 순서대로 따라 하는 편이다.", "SN", 1],
 ["결정할 때 논리와 원칙을 먼저 따진다.", "TF", 1], ["다른 사람의 기분이 상할까 봐 말을 고르는 편이다.", "TF", -1], ["친구가 고민을 말하면 해결책부터 알려 준다.", "TF", 1], ["공정함이 배려보다 더 중요하다고 생각한다.", "TF", 1], ["영화나 이야기에 쉽게 감정 이입한다.", "TF", -1], ["논쟁에서 이기는 것보다 분위기를 지키고 싶다.", "TF", -1], ["감정보다 사실을 보고 판단하려고 한다.", "TF", 1],
 ["여행을 가기 전에 일정을 미리 짜 둔다.", "JP", 1], ["일이 닥쳐서야 몰아서 하는 편이다.", "JP", -1], ["책상이나 방이 정돈되어 있어야 마음이 편하다.", "JP", 1], ["계획이 갑자기 바뀌어도 크게 스트레스받지 않는다.", "JP", -1], ["할 일을 목록으로 적고 하나씩 지우는 것이 좋다.", "JP", 1], ["그때그때 기분에 따라 움직이는 편이다.", "JP", -1], ["마감보다 일찍 끝내 두려고 한다.", "JP", 1]
];
const AX = { EI: ["E", "I", "외향", "내향"], SN: ["S", "N", "현실", "직관"], TF: ["T", "F", "사고", "감정"], JP: ["J", "P", "계획", "탐색"] };
const OPTS = ["전혀 그렇지 않다", "그렇지 않은 편이다", "보통이다", "그런 편이다", "매우 그렇다"];
const T = {
 ISTJ: ["현실주의 관리자", "책임감이 강하고 약속을 지키는 믿음직한 사람이에요. 규칙과 순서를 중시하고 맡은 일을 끝까지 해내요.", ["성실하고 꼼꼼해요", "약속을 잘 지켜요", "침착하게 일을 처리해요"], ["융통성이 부족할 수 있어요", "감정 표현이 서툴 수 있어요"], ["ESFP", "ESTP"], ["회계·행정 같은 정리 업무", "공무·법률", "품질 관리"], "가끔은 계획 밖의 즐거움도 허락해 보세요."],
 ISFJ: ["따뜻한 수호자", "조용하지만 주변 사람을 세심하게 챙기는 다정한 사람이에요. 헌신적이고 기억력이 좋아요.", ["배려심이 깊어요", "책임감이 강해요", "세심하게 살펴요"], ["거절을 어려워할 수 있어요", "자신을 뒤로 미룰 수 있어요"], ["ESFP", "ESTP"], ["교육·간호·상담", "돌봄과 서비스", "사무 지원"], "나를 위한 시간도 꼭 챙기세요."],
 INFJ: ["통찰력 있는 조언가", "사람의 마음을 깊이 이해하고 의미 있는 일을 추구하는 사람이에요. 조용하지만 신념이 단단해요.", ["공감 능력이 뛰어나요", "멀리 내다봐요", "신념이 확고해요"], ["완벽주의로 지칠 수 있어요", "속마음을 감추기 쉬워요"], ["ENFP", "ENTP"], ["상담·교육", "글쓰기·기획", "사회 활동"], "지치기 전에 쉬어 가세요."],
 INTJ: ["치밀한 전략가", "장기적인 계획을 세우고 효율적으로 목표를 이루는 사람이에요. 독립적이고 분석적이에요.", ["계획력이 뛰어나요", "독립적이에요", "문제를 구조적으로 풀어요"], ["고집이 셀 수 있어요", "감정 표현이 적을 수 있어요"], ["ENFP", "ENTP"], ["연구·개발", "전략 기획", "설계·분석"], "다른 사람의 감정에도 귀를 기울여 보세요."],
 ISTP: ["만능 해결사", "조용히 관찰하다가 필요할 때 손쉽게 문제를 해결하는 사람이에요. 도구와 기계를 잘 다뤄요.", ["침착해요", "손재주가 좋아요", "실용적이에요"], ["속마음을 잘 말하지 않아요", "장기 계획이 약할 수 있어요"], ["ESFJ", "ESTJ"], ["기술·정비", "운동·공예", "응급 상황 대처"], "마음을 표현하는 연습을 해 보세요."],
 ISFP: ["온화한 예술가", "감수성이 풍부하고 자유를 사랑하는 사람이에요. 조용히 자기만의 방식으로 아름다움을 만들어요.", ["감성이 풍부해요", "부드럽고 친절해요", "현재를 즐겨요"], ["갈등을 피하려 해요", "계획이 느슨할 수 있어요"], ["ENFJ", "ESFJ"], ["디자인·예술", "요리·미용", "동물·자연 관련"], "자신의 생각을 조금 더 말해 보세요."],
 INFP: ["이상주의 몽상가", "가치와 진심을 중시하는 따뜻한 상상가예요. 이야기와 창작을 좋아하고 사람의 내면에 관심이 많아요.", ["상상력이 풍부해요", "진정성 있어요", "깊이 공감해요"], ["현실적 결정이 어려울 수 있어요", "상처를 오래 간직해요"], ["ENFJ", "ENTJ"], ["글쓰기·창작", "상담·심리", "예술 분야"], "작은 목표부터 하나씩 실행해 보세요."],
 INTP: ["호기심 많은 탐구자", "원리를 파고드는 것을 좋아하는 생각 많은 사람이에요. 논리적이고 독창적이에요.", ["분석력이 뛰어나요", "호기심이 많아요", "독창적이에요"], ["일상 관리가 서툴 수 있어요", "실행이 미뤄지기 쉬워요"], ["ENTJ", "ESTJ"], ["연구·프로그래밍", "수학·과학", "철학·이론"], "아이디어를 작게라도 실행해 보세요."],
 ESTP: ["대담한 모험가", "활동적이고 순발력이 뛰어난 행동파예요. 현장에서 빠르게 판단하고 즐기며 살아요.", ["행동력이 좋아요", "상황 판단이 빨라요", "에너지가 넘쳐요"], ["충동적일 수 있어요", "장기 계획이 약할 수 있어요"], ["ISFJ", "ISTJ"], ["영업·스포츠", "응급·구조", "이벤트 기획"], "결정 전에 한 번만 더 생각해 보세요."],
 ESFP: ["분위기 메이커", "사람들과 어울리는 것을 좋아하는 유쾌한 사람이에요. 지금 이 순간을 즐기며 주변을 밝게 해요.", ["유쾌하고 친화력이 좋아요", "표현력이 풍부해요", "낙천적이에요"], ["계획이 느슨할 수 있어요", "지루한 일을 싫어해요"], ["ISTJ", "ISFJ"], ["공연·방송", "서비스·여행", "행사 진행"], "중요한 일은 미리 챙겨 두세요."],
 ENFP: ["열정적인 아이디어뱅크", "호기심과 열정이 넘치고 사람을 좋아하는 사람이에요. 새로운 아이디어로 분위기를 띄워요.", ["창의적이에요", "사교적이고 따뜻해요", "열정이 넘쳐요"], ["집중력이 흩어질 수 있어요", "마무리가 약할 수 있어요"], ["INFJ", "INTJ"], ["기획·마케팅", "교육·상담", "창작 분야"], "시작한 일은 끝까지 마무리해 보세요."],
 ENTP: ["재치 있는 토론가", "새로운 생각을 던지고 토론을 즐기는 사람이에요. 재치와 아이디어가 풍부해요.", ["아이디어가 넘쳐요", "말솜씨가 좋아요", "도전을 즐겨요"], ["논쟁을 즐기다 상대가 지칠 수 있어요", "꾸준함이 부족할 수 있어요"], ["INFJ", "INTJ"], ["창업·기획", "광고·미디어", "법률·정책"], "상대의 감정도 헤아려 보세요."],
 ESTJ: ["믿음직한 현장 지휘관", "체계적이고 책임감 있게 사람과 일을 이끄는 사람이에요. 규칙과 효율을 중시해요.", ["조직력이 뛰어나요", "결단력이 있어요", "책임감이 강해요"], ["융통성이 부족할 수 있어요", "자기 방식을 고집할 수 있어요"], ["ISTP", "ISFP"], ["관리·운영", "공무·군·경", "경영"], "다양한 의견에 귀를 열어 보세요."],
 ESFJ: ["사교적인 돌봄이", "주변 사람을 챙기고 화합을 이끄는 다정한 사람이에요. 분위기를 따뜻하게 만들어요.", ["친절하고 협력적이에요", "책임감이 강해요", "사람을 잘 챙겨요"], ["남의 시선에 민감해요", "비판에 상처받기 쉬워요"], ["ISTP", "ISFP"], ["교육·의료", "서비스·행사", "사회복지"], "내 마음의 소리도 들어 보세요."],
 ENFJ: ["사람을 이끄는 리더", "사람들의 성장을 돕고 이끄는 따뜻한 리더예요. 공감 능력과 책임감이 뛰어나요.", ["공감과 소통이 뛰어나요", "사람을 이끌어요", "헌신적이에요"], ["남을 너무 신경 쓸 수 있어요", "스트레스를 안으로 쌓아요"], ["INFP", "ISFP"], ["교육·코칭", "홍보·기획", "공동체 활동"], "스스로를 돌보는 시간을 가지세요."],
 ENTJ: ["대담한 통솔자", "목표를 세우고 사람과 자원을 모아 이루어 내는 타고난 리더예요. 단호하고 효율적이에요.", ["추진력이 강해요", "전략적이에요", "자신감이 있어요"], ["밀어붙이다 상대를 지치게 할 수 있어요", "감정을 놓칠 수 있어요"], ["INFP", "INTP"], ["경영·창업", "프로젝트 관리", "정책·법률"], "함께 가는 사람들의 속도도 살펴보세요."]
};
let idx = 0, ans = [], res = ld(KEY);
function showQ() {
  const [t, a] = Q[idx]; $("qn").textContent = `${idx + 1} / ${Q.length}`; $("qt").textContent = t; $("prog").style.width = (idx / Q.length * 100) + "%"; $("axis").textContent = AX[a][2] + " · " + AX[a][3];
  $("ans").innerHTML = OPTS.map((o, i) => `<button type="button" data-v="${i}" class="${ans[idx] === i ? "on" : ""}">${o}</button>`).join(""); $("back").hidden = idx === 0;
}
function finish() {
  const s = {}; for (const k of Object.keys(AX)) s[k] = 0; Q.forEach(([, a, d], i) => { s[a] += (ans[i] - 2) * d; });
  let code = ""; const pct = {}; for (const k of Object.keys(AX)) { const n = Q.filter(q => q[1] === k).length, p = Math.round(50 + s[k] / (n * 2) * 50); code += s[k] > 0 ? AX[k][0] : s[k] < 0 ? AX[k][1] : AX[k][1]; pct[k] = p; }
  res = { code, pct, d: new Date().toISOString().slice(0, 10) }; sv(KEY, res); showResult(res);
}
function showResult(r) {
  const [nm, sum, st, wk, mt, jobs, tip] = T[r.code], li = k => `<li>${esc(k)}</li>`;
  const bars = Object.keys(AX).map(k => { const p = r.pct[k], L = AX[k]; return `<div class="r"><div class="l"><span>${L[2]}(${L[0]}) ${p}%</span><span>${100 - p}% ${L[3]}(${L[1]})</span></div><div class="t"><i style="left:0;width:${p}%"></i></div></div>`; }).join("");
  $("intro").hidden = true; $("quiz").hidden = true; $("result").hidden = false;
  $("result").innerHTML = `<div class="card" style="text-align:center"><div class="muted">나의 성격 유형</div><div class="rt">${r.code}</div><div class="rn">${esc(nm)}</div><p>${esc(sum)}</p></div>`
    + `<div class="card"><b>📊 성향 비율</b><div class="ax">${bars}</div></div>`
    + `<div class="card"><div class="sec"><b>💪 강점</b><ul>${st.map(li).join("")}</ul></div><div class="sec"><b>⚠️ 조심할 점</b><ul>${wk.map(li).join("")}</ul></div><div class="sec"><b>💞 잘 맞는 유형(일반적으로)</b><div class="tags">${mt.map(m => `<span>${m} · ${T[m][0]}</span>`).join("")}</div></div><div class="sec"><b>🎯 어울리는 일·활동</b><div class="tags">${jobs.map(j => `<span>${esc(j)}</span>`).join("")}</div></div><div class="sec"><b>💬 한마디</b><p>${esc(tip)}</p></div></div>`
    + `<button class="btn" id="again" type="button">다시 테스트하기</button><p class="muted">재미로 보는 간단한 테스트예요. 공식 MBTI® 검사와는 달라서 결과가 다를 수 있고, 사람의 성격은 이 유형 하나로 정해지지 않아요. (MBTI®는 해당 권리자의 상표예요.)</p>`;
  $("again").onclick = () => { $("result").hidden = true; $("intro").hidden = false; idx = 0; ans = []; renderLast(); };
}
function renderLast() { $("last").innerHTML = res && T[res.code] ? `<hr style="border:0;border-top:1px solid var(--line);margin:12px 0"><p class="muted">지난 결과: <b>${res.code}</b> (${esc(T[res.code][0])}) · ${res.d} <button type="button" class="btn ghost" id="seeLast" style="padding:6px 12px;font-size:.9rem;margin-left:6px">다시 보기</button></p>` : ""; const b = $("seeLast"); if (b) b.onclick = () => showResult(res); }
$("start").onclick = () => { idx = 0; ans = []; $("intro").hidden = true; $("quiz").hidden = false; showQ(); };
$("ans").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (!b) return; ans[idx] = +b.dataset.v; if (idx < Q.length - 1) { idx++; showQ(); } else { $("prog").style.width = "100%"; finish(); } });
$("back").onclick = () => { if (idx > 0) { idx--; showQ(); } };
renderLast();
'''
make("out/personality-16.html", "성격 유형 테스트", "🧩", 270, "personality16-v1",
     "28개 질문으로 알아보는 16가지 성격 유형 테스트예요. 재미로만 봐 주세요. 공식 MBTI® 검사가 아니고, 결과는 이 폰에만 저장돼요.", BODY, JS, CSS)
