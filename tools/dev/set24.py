import sys
sys.path.insert(0, ".")
from mkpage import make
BODY = '''  <div class="card" id="intro"><p>질문에 얼마나 공감하는지 고르면 <b>16가지 성격 유형</b> 중 나와 가까운 유형을 알려 줘요. 네 가지 선호 축(에너지 방향·정보 인식·판단 방식·생활 양식)을 따로 측정하고, 결과에는 <b>선호 강도, 인지 기능 순서, 소통·스트레스·성장 팁</b>까지 담았어요.</p><p class="muted">공식 MBTI® 검사가 아니에요. 심리 유형론을 참고해 직접 만든 비슷한 방식의 테스트예요.</p><div class="modes"><button class="btn" id="startQ" type="button">빠른 검사 · 28문항 · 약 3분</button><button class="btn" id="startF" type="button">정밀 검사 · 60문항 · 약 7분</button></div><div id="last"></div></div>
  <div class="card" id="quiz" hidden><div class="step"><span class="muted" id="qn">1 / 28</span><span class="muted" id="axis"></span></div><div class="bar"><i id="prog"></i></div><p class="q" id="qt"></p><div class="ans" id="ans"></div><button class="btn ghost" id="back" type="button">← 이전 문항</button></div>
  <div id="result" hidden></div>'''
CSS = '''.bar{height:8px;border-radius:99px;background:var(--soft);overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--accent);transition:width .2s}.q{font-family:var(--font-display);font-size:1.35rem;line-height:1.5;min-height:4.2em;display:flex;align-items:center}.ans{display:grid;gap:8px}.ans button{background:var(--surface);border:2px solid var(--line);border-radius:14px;padding:12px;font-weight:700;text-align:left}.ans button.on{border-color:var(--accent);background:var(--soft)}.rt{font-family:var(--font-display);font-size:3rem;letter-spacing:.06em;color:var(--accent);line-height:1.1}.rn{font-family:var(--font-display);font-size:1.4rem}.ax{display:grid;gap:10px}.ax .r{display:grid;gap:4px}.ax .l{display:flex;justify-content:space-between;font-size:.88rem;font-weight:700}.ax .t{height:12px;background:var(--soft);border-radius:99px;position:relative;overflow:hidden}.ax .t i{position:absolute;top:0;bottom:0;background:var(--accent);border-radius:99px}.tags{display:flex;flex-wrap:wrap;gap:6px}.tags span{background:var(--soft);border-radius:999px;padding:3px 10px;font-size:.88rem}.sec{display:grid;gap:4px}.sec b{font-size:.95rem}.sec ul{margin:0;padding-left:20px}.modes{display:grid;gap:8px;margin:10px 0}.fn{display:grid;gap:6px}.fn div{display:flex;gap:10px;align-items:flex-start;background:var(--soft);border-radius:12px;padding:8px 10px}.fn b.k{min-width:2.4em;font-family:var(--font-display);font-size:1.15rem;color:var(--accent)}.fn small{display:block;color:var(--muted)}.hist{margin:0;padding-left:18px}.warn{background:var(--soft);border-radius:12px;padding:8px 10px}'''
JS = r'''
const QBASE = [
 ["처음 보는 사람과도 금방 이야기를 시작한다.", "EI", 1], ["사람들과 함께 있으면 에너지가 생긴다.", "EI", 1], ["쉬는 날에는 혼자 조용히 보내는 것이 더 좋다.", "EI", -1], ["모임에서 말을 많이 하는 편이다.", "EI", 1], ["생각을 충분히 정리한 뒤에 말하는 편이다.", "EI", -1], ["전화나 메시지보다 직접 만나서 이야기하는 것이 편하다.", "EI", 1], ["많은 사람 앞에 나서는 일이 부담스럽다.", "EI", -1],
 ["상상이나 가능성을 이야기하는 것이 재미있다.", "SN", -1], ["눈에 보이는 사실과 직접 겪은 경험을 더 믿는다.", "SN", 1], ["새로운 방법보다 검증된 방법이 마음 편하다.", "SN", 1], ["대화할 때 비유나 은유를 자주 쓴다.", "SN", -1], ["일할 때 세부 사항을 꼼꼼히 챙기는 편이다.", "SN", 1], ["어떤 일을 보면 미래의 가능성부터 떠올린다.", "SN", -1], ["설명서는 순서대로 따라 하는 편이다.", "SN", 1],
 ["결정할 때 논리와 원칙을 먼저 따진다.", "TF", 1], ["다른 사람의 기분이 상할까 봐 말을 고르는 편이다.", "TF", -1], ["친구가 고민을 말하면 해결책부터 알려 준다.", "TF", 1], ["공정함이 배려보다 더 중요하다고 생각한다.", "TF", 1], ["영화나 이야기에 쉽게 감정 이입한다.", "TF", -1], ["논쟁에서 이기는 것보다 분위기를 지키고 싶다.", "TF", -1], ["감정보다 사실을 보고 판단하려고 한다.", "TF", 1],
 ["여행을 가기 전에 일정을 미리 짜 둔다.", "JP", 1], ["일이 닥쳐서야 몰아서 하는 편이다.", "JP", -1], ["책상이나 방이 정돈되어 있어야 마음이 편하다.", "JP", 1], ["계획이 갑자기 바뀌어도 크게 스트레스받지 않는다.", "JP", -1], ["할 일을 목록으로 적고 하나씩 지우는 것이 좋다.", "JP", 1], ["그때그때 기분에 따라 움직이는 편이다.", "JP", -1], ["마감보다 일찍 끝내 두려고 한다.", "JP", 1]
];
const QMORE = [
 ["하루 일정이 사람들과의 약속으로 가득 차 있어도 괜찮다.", "EI", 1], ["혼자 있는 시간이 없으면 쉽게 지친다.", "EI", -1], ["새로운 모임에 가면 먼저 다가가 인사를 건넨다.", "EI", 1], ["깊은 이야기는 소수의 가까운 사람과만 나누고 싶다.", "EI", -1], ["생각하기 전에 말이 먼저 나오는 편이다.", "EI", 1], ["여럿이 있는 자리에서는 듣는 쪽이 더 편하다.", "EI", -1], ["주말에 약속이 없으면 허전하다.", "EI", 1], ["나를 잘 모르는 사람 앞에서는 말수가 적어진다.", "EI", -1],
 ["지금 눈앞의 일에 집중하는 것이 잘 맞는다.", "SN", 1], ["'만약에 ~라면' 같은 상상을 자주 한다.", "SN", -1], ["구체적인 예시가 있어야 이해가 잘 된다.", "SN", 1], ["여러 일 사이의 숨은 연결고리와 패턴을 찾는 것이 재미있다.", "SN", -1], ["말할 때 사실과 숫자를 정확하게 말하려 한다.", "SN", 1], ["한 가지 일을 하다가도 다른 아이디어가 자꾸 떠오른다.", "SN", -1], ["손에 잡히는 현실적인 결과물이 나올 때 보람을 느낀다.", "SN", 1], ["이미 있는 방식을 바꿔 보고 싶은 마음이 자주 든다.", "SN", -1],
 ["누군가를 평가할 때 감정보다 기준을 먼저 본다.", "TF", 1], ["상대가 속상해 보이면 내 일정이 바빠도 먼저 들어 준다.", "TF", -1], ["비판이 필요하면 돌려 말하지 않고 정확히 말한다.", "TF", 1], ["결정이 누군가에게 상처가 될지 먼저 생각한다.", "TF", -1], ["토론에서 감정이 섞이면 이해가 잘 안 된다.", "TF", 1], ["다른 사람의 표정이나 말투 변화를 금방 알아챈다.", "TF", -1], ["옳고 그름이 분명할 때는 사정을 봐주기 어렵다.", "TF", 1], ["내 가치관에 어긋나는 일은 이득이 있어도 하고 싶지 않다.", "TF", -1],
 ["약속 시간에 늦지 않으려고 여유 있게 출발한다.", "JP", 1], ["정해진 일정보다 즉흥적인 선택이 더 즐겁다.", "JP", -1], ["결정을 내리고 나면 마음이 편해진다.", "JP", 1], ["선택지를 열어 두고 마지막까지 더 알아보고 싶다.", "JP", -1], ["물건은 항상 제자리에 두는 편이다.", "JP", 1], ["마감 직전의 긴장감이 오히려 집중이 잘 된다.", "JP", -1], ["일을 시작하기 전에 순서와 방법을 정리한다.", "JP", 1], ["계획을 세워도 상황에 맞게 자주 바꾼다.", "JP", -1]
];
function mix(list) { const g = { EI: [], SN: [], TF: [], JP: [] }; list.forEach(q => g[q[1]].push(q)); const out = []; for (let i = 0; i < 15; i++) for (const k of ["EI", "SN", "TF", "JP"]) if (g[k][i]) out.push(g[k][i]); return out; }
let Q = [], mode = "q";
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

const FN = { Ni: ["내향 직관", "흐름 뒤의 큰 그림과 의미를 한 번에 꿰뚫어 보는 힘"], Ne: ["외향 직관", "여러 가능성과 아이디어를 넓게 펼쳐 연결하는 힘"], Si: ["내향 감각", "지난 경험과 기억을 바탕으로 안정과 정확함을 지키는 힘"], Se: ["외향 감각", "지금 이 순간의 현실을 생생하게 느끼고 바로 행동하는 힘"], Ti: ["내향 사고", "스스로 납득되는 논리 체계를 세우고 원리를 따지는 힘"], Te: ["외향 사고", "목표·효율·체계로 일을 정리하고 성과를 내는 힘"], Fi: ["내향 감정", "내 안의 가치와 진정성을 기준으로 판단하는 힘"], Fe: ["외향 감정", "주변 사람의 감정을 읽고 조화를 만드는 힘"] };
const ST = { ISTJ: "Si Te Fi Ne", ISFJ: "Si Fe Ti Ne", INFJ: "Ni Fe Ti Se", INTJ: "Ni Te Fi Se", ISTP: "Ti Se Ni Fe", ISFP: "Fi Se Ni Te", INFP: "Fi Ne Si Te", INTP: "Ti Ne Si Fe", ESTP: "Se Ti Fe Ni", ESFP: "Se Fi Te Ni", ENFP: "Ne Fi Te Si", ENTP: "Ne Ti Fe Si", ESTJ: "Te Si Ne Fi", ESFJ: "Fe Si Ne Ti", ENFJ: "Fe Ni Se Ti", ENTJ: "Te Ni Se Fi" };
const ROLE = ["주기능 · 가장 자연스럽고 편한 힘", "부기능 · 주기능을 받쳐 주는 힘", "3차 기능 · 성장하며 키워 가는 힘", "열등 기능 · 서툴고 스트레스 때 흔들리는 부분"];
const X = {
 ISTJ: ["핵심만 정확하게, 순서대로 말하는 편이에요. 모호한 표현이나 말 바꾸기를 불편해해요.", "갑작스러운 변경과 규칙 무시가 쌓이면 예민해지고, 최악의 상황을 상상하며 걱정이 커져요.", "새로운 방식도 작게 시험해 보세요. 감정 표현을 말로 꺼내면 관계가 훨씬 편해져요."],
 ISFJ: ["부드럽고 배려 있게 말하며, 거절이나 불만은 속으로 삼키는 경우가 많아요.", "도움을 당연하게 여기는 환경에서 지치고, 혼자 참다가 한꺼번에 서운함이 터질 수 있어요.", "'아니요'라고 말하는 연습과 나를 위한 시간을 일정에 넣어 보세요."],
 INFJ: ["깊은 대화를 좋아하고 의미를 담아 말해요. 얕은 수다가 길어지면 에너지가 빠져요.", "오해받는다고 느끼면 마음의 문을 닫고, 지나치게 완벽한 이상과 현실의 차이에 지쳐요.", "생각을 혼자만 품지 말고 말로 나누세요. 이상을 작은 실행 단계로 쪼개면 도움이 돼요."],
 INTJ: ["결론과 근거를 간결하게 말해요. 돌려 말하기나 감정적인 설득은 비효율로 느끼기 쉬워요.", "통제할 수 없는 상황이나 능력을 의심받는 일이 이어지면 차갑고 비판적으로 변해요.", "팀원의 감정과 속도도 중요한 정보로 다뤄 보세요. 계획에 '유연한 예비 칸'을 넣으면 좋아요."],
 ISTP: ["말수가 적고 필요한 말만 해요. 직접 보여 주거나 해 보이는 방식으로 소통해요.", "간섭과 감정적인 요구가 몰리면 잠수 타듯 거리를 두고, 가끔 충동적으로 폭발해요.", "속마음을 한 문장이라도 말로 전해 보세요. 장기 계획을 하나만 정해도 안정감이 생겨요."],
 ISFP: ["조용하고 따뜻하게 말하며, 갈등은 피하려는 편이에요. 행동과 분위기로 마음을 표현해요.", "강요와 비판을 받으면 위축되고, 한계를 넘으면 갑자기 냉정하고 날카로워져요.", "하고 싶은 것을 먼저 입 밖에 내 보세요. 작은 목표를 세우면 재능이 더 빛나요."],
 INFP: ["진심을 담아 말하고 상대의 속마음에 관심이 많아요. 비판은 개인적으로 받아들이기 쉬워요.", "가치가 무시되거나 현실의 압박이 커지면 자책하고 고립되며, 사소한 실수를 크게 확대해요.", "이상을 작은 행동으로 옮겨 보세요. '충분히 괜찮다'는 기준을 정해 두면 마음이 가벼워져요."],
 INTP: ["정확한 개념과 논리를 따져 말해요. 감정이 담긴 질문에 정답을 주려다 어색해지곤 해요.", "논리를 무시당하거나 감정 요구가 쌓이면 말이 없어지고, 갑자기 예민해져 비꼬기도 해요.", "생각을 끝까지 다듬기 전에 공유해 보세요. 마감을 정해 두면 실행력이 올라가요."],
 ESTP: ["직설적이고 유머러스하며 분위기를 빠르게 읽어요. 길고 이론적인 설명은 지루해해요.", "오래 갇혀 있거나 통제받으면 답답해하고, 불안해지면 자극적인 선택으로 도망치기 쉬워요.", "결정 전에 '이후 한 달'을 한 번 상상해 보세요. 장기 목표를 나누어 놀이처럼 진행하면 좋아요."],
 ESFP: ["표현이 풍부하고 따뜻하게 말해요. 무거운 비판이나 장시간의 심각한 이야기에는 쉽게 지쳐요.", "혼자 남거나 비난받으면 불안이 커지고, 재미있는 일로 도망치며 문제를 미루기 쉬워요.", "중요한 일의 순서를 적어 두세요. 감정을 나눌 한 사람을 정해 두면 안정돼요."],
 ENFP: ["열정적으로 떠올리고 이야기를 이어 가요. 말이 앞서 약속이 늘어나는 점을 조심하세요.", "틀에 갇히거나 인정받지 못하면 의욕이 꺼지고, 세부 사항 앞에서 압도돼 예민해져요.", "아이디어 중 하나만 끝까지 마무리해 보세요. 루틴을 최소한으로 만들면 에너지가 오래 가요."],
 ENTP: ["재치 있게 반대 의견을 던지며 토론으로 생각을 굳혀요. 상대는 공격으로 느낄 수 있어요.", "느리고 반복적인 일이 이어지면 짜증이 나고, 감정 문제가 터지면 서툴러 회피해요.", "토론과 진심을 구분해서 전하세요. 시작한 일의 '끝 조건'을 먼저 정하면 완성률이 올라가요."],
 ESTJ: ["분명하고 단호하게 지시와 기준을 말해요. 의견 차이를 불복종으로 받아들이면 갈등이 생겨요.", "질서가 무너지고 책임을 안 지는 모습에 날이 서며, 감정 문제 앞에서 당황하다 퉁명스러워져요.", "결과만큼 과정과 사람의 마음도 칭찬해 보세요. 다른 방식의 장점을 하나씩 인정하면 팀이 편해져요."],
 ESFJ: ["다정하게 말을 걸고 분위기를 살펴요. 비판이나 무관심을 개인적인 거절로 느끼기 쉬워요.", "인정받지 못하거나 갈등이 오래 가면 속상해하고, 지나친 눈치와 간섭으로 번질 수 있어요.", "모두를 만족시키지 않아도 괜찮아요. 내 감정과 요구도 같은 무게로 말해 보세요."],
 ENFJ: ["공감하며 상대에게 맞춰 말하고 동기를 북돋아요. 반대 의견도 부드럽게 말하려다 모호해질 수 있어요.", "관계가 틀어지거나 도움이 거절당하면 크게 상처받고, 지나치게 떠안아 지쳐요.", "남의 성장만큼 내 몫의 휴식을 챙기세요. 상대가 스스로 선택하도록 기다리는 연습이 좋아요."],
 ENTJ: ["목표와 계획을 선명하게 제시하고 빠른 결정을 요구해요. 단호함이 압박으로 느껴질 수 있어요.", "비효율과 느린 결정에 인내심이 바닥나고, 통제를 잃으면 감정이 갑자기 터지기도 해요.", "의견을 먼저 묻고 들을 시간을 주세요. 사람의 감정을 '프로젝트 변수'로 인정해 보세요."]
};
const HK = KEY + '-h';
let idx = 0, ans = [], res = ld(KEY), hist = ld(HK) || [];
function showQ() {
  const [t, a] = Q[idx]; $("qn").textContent = `${idx + 1} / ${Q.length}`; $("qt").textContent = t; $("prog").style.width = (idx / Q.length * 100) + "%"; $("axis").textContent = AX[a][2] + " · " + AX[a][3];
  $("ans").innerHTML = OPTS.map((o, i) => `<button type="button" data-v="${i}" class="${ans[idx] === i ? "on" : ""}">${o}</button>`).join(""); $("back").hidden = idx === 0;
}
function finish() {
  const s = {}; for (const k of Object.keys(AX)) s[k] = 0; Q.forEach(([, a, d], i) => { s[a] += (ans[i] - 2) * d; });
  let code = ""; const pct = {}; for (const k of Object.keys(AX)) { const n = Q.filter(q => q[1] === k).length, p = Math.round(50 + s[k] / (n * 2) * 50); code += s[k] > 0 ? AX[k][0] : AX[k][1]; pct[k] = p; }
  res = { code, pct, n: Q.length, d: new Date().toISOString().slice(0, 10) }; sv(KEY, res);
  hist = [{ code, n: Q.length, d: res.d }].concat(hist).slice(0, 8); sv(HK, hist); showResult(res);
}
function level(p) { const d = Math.abs(p - 50) * 2; return d < 12 ? "거의 비슷" : d < 30 ? "약한 선호" : d < 60 ? "뚜렷한 선호" : "매우 뚜렷한 선호"; }
function showResult(r) {
  const [nm, sum, st, wk, mt, jobs, tip] = T[r.code], li = k => `<li>${esc(k)}</li>`, ks = Object.keys(AX);
  const bars = ks.map((k, i) => { const p = r.pct[k], L = AX[k], side = r.code[i] === L[0] ? L[0] + " " + L[2] : L[1] + " " + L[3]; return `<div class="r"><div class="l"><span>${L[2]}(${L[0]}) ${p}%</span><span>${100 - p}% ${L[3]}(${L[1]})</span></div><div class="t"><i style="left:0;width:${p}%"></i></div><div class="muted" style="font-size:.85rem">→ ${side} · ${level(p)}</div></div>`; }).join("");
  const edge = ks.filter(k => Math.abs(r.pct[k] - 50) * 2 < 16);
  let warn = "";
  if (edge.length) { const alt = r.code.split("").map((c, i) => edge.includes(ks[i]) ? (c === AX[ks[i]][0] ? AX[ks[i]][1] : AX[ks[i]][0]) : c).join(""); warn = `<div class="warn"><b>⚖️ 경계에 있는 축</b><br>${edge.map(k => AX[k][2] + "/" + AX[k][3]).join(", ")} 축은 양쪽 점수가 거의 비슷해요. 상황에 따라 <b>${alt}</b>(${esc((T[alt] || [""])[0])})의 모습도 자주 보일 수 있어요.</div>`; }
  const fns = ST[r.code].split(" "), fn = fns.map((f, i) => `<div><b class="k">${f}</b><span><b>${FN[f][0]}</b> · ${ROLE[i].split(" · ")[0]}<small>${FN[f][1]} (${ROLE[i].split(" · ")[1]})</small></span></div>`).join("");
  const [cm, ss, gr] = X[r.code];
  $("intro").hidden = true; $("quiz").hidden = true; $("result").hidden = false;
  $("result").innerHTML = `<div class="card" style="text-align:center"><div class="muted">나의 성격 유형 · ${r.n || 28}문항 검사</div><div class="rt">${r.code}</div><div class="rn">${esc(nm)}</div><p>${esc(sum)}</p></div>`
    + `<div class="card"><b>📊 성향 비율과 선호 강도</b><div class="ax">${bars}</div>${warn}<p class="muted" style="margin:6px 0 0">비율은 '정답'이 아니라 내 응답의 경향이에요. 50%에 가까울수록 두 방향을 상황에 따라 번갈아 써요.</p></div>`
    + `<div class="card"><b>🧠 마음이 일하는 순서 (인지 기능)</b><p class="muted" style="margin:4px 0 8px">심리학자 융의 유형론에서 말하는 여덟 가지 힘 중 이 유형이 주로 쓰는 네 가지를 순서대로 보여 줘요.</p><div class="fn">${fn}</div></div>`
    + `<div class="card"><div class="sec"><b>💪 강점</b><ul>${st.map(li).join("")}</ul></div><div class="sec"><b>⚠️ 조심할 점</b><ul>${wk.map(li).join("")}</ul></div><div class="sec"><b>🗣️ 소통 스타일</b><p>${esc(cm)}</p></div><div class="sec"><b>😰 스트레스를 받으면</b><p>${esc(ss)}</p></div><div class="sec"><b>🌱 성장 팁</b><p>${esc(gr)}</p></div></div>`
    + `<div class="card"><div class="sec"><b>💞 잘 맞는 유형(일반적으로)</b><div class="tags">${mt.map(m => `<span>${m} · ${T[m][0]}</span>`).join("")}</div></div><div class="sec"><b>🎯 어울리는 일·활동</b><div class="tags">${jobs.map(j => `<span>${esc(j)}</span>`).join("")}</div></div><div class="sec"><b>💬 한마디</b><p>${esc(tip)}</p></div></div>`
    + `<button class="btn" id="copy" type="button">📋 결과 복사하기</button> <button class="btn ghost" id="again" type="button">다시 테스트하기</button><p class="muted">이 테스트는 심리 유형론을 참고해 직접 만든 자기보고식 검사예요. 공식 MBTI® 검사와 달라 결과가 다를 수 있고, 진단이나 채용·진로 결정의 근거로 쓰기엔 적절하지 않아요. 유형은 '선호하는 경향'일 뿐 능력이나 한계를 뜻하지 않으며, 같은 사람도 시기와 기분에 따라 달라질 수 있어요. (MBTI®는 해당 권리자의 상표예요.)</p>`;
  $("copy").onclick = () => { const t = `나의 성격 유형: ${r.code} (${nm})\n` + ks.map(k => `${AX[k][2]}(${AX[k][0]}) ${r.pct[k]}% : ${100 - r.pct[k]}% ${AX[k][3]}(${AX[k][1]})`).join("\n") + `\n인지 기능: ${ST[r.code]}`; try { navigator.clipboard.writeText(t).then(() => { $("copy").textContent = "✅ 복사했어요"; }, () => { $("copy").textContent = "복사에 실패했어요"; }); } catch (e) { $("copy").textContent = "복사에 실패했어요"; } };
  $("again").onclick = () => { $("result").hidden = true; $("intro").hidden = false; idx = 0; ans = []; renderLast(); };
}
function renderLast() {
  const h = hist.filter(x => T[x.code]);
  $("last").innerHTML = h.length ? `<hr style="border:0;border-top:1px solid var(--line);margin:12px 0"><p class="muted">지난 결과 <button type="button" class="btn ghost" id="seeLast" style="padding:6px 12px;font-size:.9rem;margin-left:6px">최근 결과 다시 보기</button></p><ul class="hist muted">${h.map(x => `<li><b>${x.code}</b> ${esc(T[x.code][0])} · ${x.d} · ${x.n || 28}문항</li>`).join("")}</ul>` : "";
  const b = $("seeLast"); if (b && res && T[res.code]) b.onclick = () => showResult(res);
}
function begin(m) { mode = m; Q = mix(m === "f" ? QBASE.concat(QMORE) : QBASE); idx = 0; ans = []; $("intro").hidden = true; $("quiz").hidden = false; showQ(); }
$("startQ").onclick = () => begin("q");
$("startF").onclick = () => begin("f");
$("ans").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (!b) return; ans[idx] = +b.dataset.v; if (idx < Q.length - 1) { idx++; showQ(); } else { $("prog").style.width = "100%"; finish(); } });
$("back").onclick = () => { if (idx > 0) { idx--; showQ(); } };
renderLast();
'''
make("out/personality-16.html", "성격 유형 테스트", "🧩", 270, "personality16-v1",
     "28개(빠른)·60개(정밀) 질문으로 알아보는 16가지 성격 유형 테스트로, 선호 강도·인지 기능·소통/스트레스/성장 팁까지 보여 줘요. 재미로만 봐 주세요. 공식 MBTI® 검사가 아니고, 결과는 이 폰에만 저장돼요.", BODY, JS, CSS)
