# 오케스트라 퀴즈(orchestra-quiz.html) + 오케스트라 악기 도감(orchestra-gallery.html) 생성기. 원본 자료는 orch_data.py, 그림은 orch_svg.py.
#   실행: py set45.py → py ship.py '[["orchestra-quiz.html","🎻","오케스트라 퀴즈","…","quiz","culture"],["orchestra-gallery.html","🎷","오케스트라 악기 도감","…","life","culture"]]' → py qlevel.py orchestra-quiz
#   문제 유형: ① 도감 그림 → 이름 ② 이름 → 악기군 ③ 설명 → 악기 ④ 같은 악기군 짝 ⑤ 높낮이 비교 ⑥ 오케스트라 지식 ⑦ 곡 속의 악기 ⑧ 무대 배치도(번호 자리)
#   그림은 직접 그린 SVG(기본)이고, 🌐 사진은 사용자가 켠 경우에만 위키백과의 공개 도메인·CC0 사진을 불러와요(orch-mode.js). 그림 파일은 저장소에 두지 않아요.
import sys, json, random, os, re
sys.path.insert(0, ".")
from orch_data import INSTR, GENERAL, PIECES, SEATS, FAMILIES
from orch_specs import SPECS
from orch_svg import ICONS, icon, seating, size_compare, STR_SIZES
from mkquiz import make as make_quiz
from mkpage import make as make_page
H = "out/"; R = random.Random(20261125)
I = {x[0]: dict(id=x[0], n=k + 1, name=x[1], en=x[2], fam=x[3], how=x[4], rng=x[5], desc=x[6], use=x[7], fame=x[8], wiki=x[9], tok=x[10]) for k, x in enumerate(INSTR)}
ORDER = [x[0] for x in INSTR]
BY_FAM = {f: [i for i in ORDER if I[i]["fam"] == f] for f in FAMILIES}
CORE = ["현악기", "목관악기", "금관악기", "타악기"]   # 악기군 문제는 분류가 분명한 네 악기군만 쓴다(하프·피아노 등은 책마다 분류가 달라서 뺀다)
CLUE = {
 "violin": "현악기 중 가장 작고 가장 높은 소리를 내는 악기는?", "viola": "바이올린보다 조금 크고 가운데 소리를 맡는 현악기는?", "cello": "바닥에 세워 무릎 사이에 끼고 연주하는 현악기는?", "doublebass": "현악기 중 가장 크고 가장 낮은 소리를 내는 악기는?",
 "harp": "줄이 40개 넘게 걸려 있고 발로 페달을 밟아 음높이를 바꾸는 악기는?", "flute": "금속으로 만들지만 목관악기로 분류하고, 리드 없이 바람을 불어 소리 내는 악기는?", "piccolo": "플루트의 절반쯤 크기로 아주 높은 소리를 내는 목관악기는?",
 "oboe": "연주 전에 튜닝 기준 음(라)을 내 주는, 겹리드를 쓰는 목관악기는?", "englishhorn": "이름과 달리 호른이 아니라 오보에 계열에 속하는 악기는?", "clarinet": "홑리드를 입에 물고 부는 목관악기로 '피터와 늑대'의 고양이를 맡은 악기는?",
 "bassoon": "긴 관을 반으로 접은 모양의 낮은 목관악기로 '피터와 늑대'의 할아버지를 맡은 악기는?", "contrabassoon": "오케스트라에서 가장 낮은 소리를 내는 목관악기는?",
 "trumpet": "금관악기 중 가장 높고 밝은 소리를 내고 팡파르에 자주 쓰는 악기는?", "horn": "관을 동그랗게 감았고 오른손을 나팔 안에 넣어 소리를 다듬는 금관악기는?", "trombone": "슬라이드를 밀고 당겨 음높이를 바꾸는 금관악기는?", "tuba": "금관악기 중 가장 크고 가장 낮은 소리를 내는 악기는?",
 "timpani": "페달로 음높이를 바꿀 수 있는, 구리 솥 모양의 북은?", "snaredrum": "아래쪽에 줄(스네어)이 있어 '차르르' 소리가 나는 북은?", "bassdrum": "오케스트라에서 가장 큰 북으로 깊고 낮게 울리는 악기는?", "cymbals": "둥근 금속 판 두 장을 마주쳐 '쨍' 소리를 내는 악기는?",
 "triangle": "삼각형 쇠막대를 쇠채로 쳐서 맑은 소리를 내는 악기는?", "xylophone": "나무 판을 채로 쳐서 통통 튀는 소리를 내는 악기는?", "glockenspiel": "금속 판을 채로 쳐서 종소리처럼 맑은 소리를 내는 악기는?", "gong": "크고 둥근 금속 판을 큰 채로 쳐서 길게 울리게 하는 악기는?",
 "tambourine": "둥근 틀에 작은 금속판이 달려 흔들거나 쳐서 '짤랑' 소리를 내는 악기는?", "castanets": "작은 나무 조개 두 짝을 부딪쳐 '딱딱' 소리를 내고 스페인 춤에 쓰는 악기는?",
 "piano": "건반을 누르면 해머가 줄을 치는 악기로, 협주곡의 독주 악기로 자주 나오는 악기는?", "celesta": "작은 피아노처럼 생겼지만 종소리 같은 소리가 나고 '요정의 춤'에 쓰인 악기는?", "organ": "수많은 파이프에 공기를 보내 소리를 내는 건반악기로, 성당에서 자주 보는 악기는?",
}
ALT_KO = {"violin": "바이올린", "viola": "비올라", "cello": "첼로", "doublebass": "콘트라베이스", "harp": "하프", "flute": "플루트", "piccolo": "피콜로", "oboe": "오보에", "englishhorn": "잉글리시 호른", "clarinet": "클라리넷", "bassoon": "바순", "contrabassoon": "콘트라바순", "trumpet": "트럼펫", "horn": "호른", "trombone": "트롬본", "tuba": "튜바", "timpani": "팀파니", "snaredrum": "스네어 드럼", "bassdrum": "베이스 드럼", "cymbals": "심벌즈", "triangle": "트라이앵글", "xylophone": "실로폰", "glockenspiel": "글로켄슈필", "gong": "징", "tambourine": "탬버린", "castanets": "캐스터네츠", "piano": "피아노", "celesta": "첼레스타", "organ": "파이프 오르간"}
ALT_DE = {"violin": "Violine", "viola": "Bratsche", "cello": "Violoncello", "doublebass": "Kontrabass", "harp": "Harfe", "flute": "Querflöte", "piccolo": "Piccoloflöte", "oboe": "Oboe", "englishhorn": "Englischhorn", "clarinet": "Klarinette", "bassoon": "Fagott", "contrabassoon": "Kontrafagott", "trumpet": "Trompete", "horn": "Waldhorn", "trombone": "Posaune", "tuba": "Tuba", "timpani": "Pauke", "snaredrum": "Kleine Trommel", "bassdrum": "Große Trommel", "cymbals": "Becken (Musikinstrument)", "xylophone": "Xylophon", "gong": "Gong", "tambourine": "Tamburin", "castanets": "Kastagnetten", "piano": "Klavier", "celesta": "Celesta", "organ": "Orgel"}
assert set(CLUE) == set(ORDER), set(ORDER) ^ set(CLUE)
data, level, seen, IMG, INFO, SHOW = [], {}, set(), {}, {}, {}
def add(q, ans, wrong, cat, expl, lv):
    if q in seen: return False
    wrong = [w for w in dict.fromkeys(wrong) if w != ans][:3]
    assert len(wrong) == 3, (q, ans, wrong)
    seen.add(q); data.append([q, ans, wrong, cat, expl]); level[q] = lv; return True
def names(ids): return [I[i]["name"] for i in ids]
def others(i, lv, k=3):
    """오답 악기 k개: 쉬운 문제는 다른 악기군에서, 어려운 문제는 같은 악기군에서 더 골라요."""
    a = I[i]; same = [x for x in ORDER if x != i and I[x]["fam"] == a["fam"]]; diff = [x for x in ORDER if x != i and I[x]["fam"] != a["fam"]]
    n_same = {1: 0, 2: 1, 3: 2}[lv]; out = R.sample(same, min(n_same, len(same))); out += R.sample([x for x in diff if x not in out], k - len(out)); return names(out)

# ① 도감 그림 → 이름 / ③ 설명 → 악기
for i in ORDER:
    a = I[i]; lv = a["fame"]
    q1 = f"도감 {a['n']}번 악기(그림)의 이름은 무엇일까요?"
    if add(q1, a["name"], others(i, max(lv, 2) if a["fam"] == "현악기" else lv), a["fam"], f"{a['name']}({a['en']})은 {a['fam']}예요. {a['desc']}", lv): IMG[q1] = ["i", i]; INFO[q1] = i
    q3 = CLUE[i];
    if add(q3, a["name"], others(i, lv), a["fam"], f"{a['name']} — {a['desc']}", lv): INFO[q3] = i
# ② 이름 → 악기군(분류가 분명한 악기만)
for i in ORDER:
    a = I[i]
    if a["fam"] not in CORE: continue
    q2 = f"‘{a['name']}’은(는) 어느 악기군에 속할까요?"
    if add(q2, a["fam"], [f for f in CORE if f != a["fam"]], a["fam"], f"{a['name']}은(는) {a['fam']}예요. {a['how']}.", a["fame"]): SHOW[q2] = i; INFO[q2] = i
# ④ 같은 악기군 짝: ‘X’와 같은 악기군인 것은?
for i in ORDER:
    a = I[i]
    if a["fam"] not in CORE: continue
    mates = [x for x in BY_FAM[a["fam"]] if x != i]; m = R.choice(mates); wrong = [x for x in ORDER if I[x]["fam"] != a["fam"] and I[x]["fam"] in CORE]
    q4 = f"‘{a['name']}’과(와) 같은 악기군에 속하는 악기는?"
    if add(q4, I[m]["name"], names(R.sample(wrong, 3)), a["fam"], f"{a['name']}과(와) {I[m]['name']}은(는) 모두 {a['fam']}예요.", max(1, min(3, a["fame"]))): SHOW[q4] = i; INFO[q4] = m
# ⑤ 높낮이 비교(같은 악기군 안에서 분명한 것만)
for q, ans, ws, fam, ex, lv in [
    ("현악기 중 가장 낮은 소리를 내는 악기는?", "콘트라베이스", ["바이올린", "비올라", "첼로"], "현악기", "콘트라베이스가 현악기 중 가장 크고 가장 낮아요.", 1),
    ("현악기 중 가장 높은 소리를 내는 악기는?", "바이올린", ["비올라", "첼로", "콘트라베이스"], "현악기", "바이올린이 현악기 중 가장 작고 가장 높아요.", 1),
    ("금관악기 중 가장 낮은 소리를 내는 악기는?", "튜바", ["트럼펫", "호른", "트롬본"], "금관악기", "튜바가 금관악기 중 가장 크고 가장 낮아요.", 1),
    ("금관악기 중 가장 높은 소리를 내는 악기는?", "트럼펫", ["튜바", "트롬본", "호른"], "금관악기", "트럼펫이 오케스트라 금관악기 중 가장 높은 소리를 내요.", 2),
    ("다음 목관악기 중 가장 높은 소리를 내는 악기는?", "피콜로", ["플루트", "오보에", "클라리넷"], "목관악기", "피콜로는 플루트의 절반 크기라 한 옥타브 높은 소리를 내요.", 2),
    ("다음 목관악기 중 가장 낮은 소리를 내는 악기는?", "콘트라바순", ["바순", "클라리넷", "오보에"], "목관악기", "콘트라바순은 바순보다 한 옥타브 낮은 가장 낮은 목관악기예요.", 3),
    ("다음 목관악기 중 가장 낮은 소리를 내는 악기는?", "바순", ["플루트", "오보에", "클라리넷"], "목관악기", "바순은 목관악기 중 낮은 소리를 맡아요.", 2),
]: add(q, ans, ws, fam, ex, lv)
# ⑥ 오케스트라 지식, ⑦ 곡 속의 악기
for q, a, w, ex, lv in GENERAL: add(q, a, w, "오케스트라", ex, lv)
for q, a, w, ex, lv in PIECES: add(q, a, w, "곡 속 악기", ex, lv)
# 연주 용어·기초 지식(직접 쓴 사실)
for q, a, w, ex, lv in [
    ("바이올린 활에 송진을 바르는 이유는?", "활이 현에 잘 걸려 소리가 나게 하려고", ["활이 썩지 않게 하려고", "소리를 작게 하려고", "활을 무겁게 하려고"], "송진을 바르면 마찰이 생겨 활털이 현을 붙잡았다 놓으며 소리를 내요.", 3),
    ("오보에·클라리넷·바순의 소리를 내는 얇은 조각 '리드'는 보통 무엇으로 만들까요?", "갈대", ["금속", "고무", "종이"], "갈대를 얇게 깎아 만든 리드가 떨리면서 소리를 내요.", 3),
    ("금관악기의 소리는 무엇이 떨려서 나는 걸까요?", "연주자의 입술", ["악기의 금속 판", "목구멍", "나팔 안의 줄"], "입술을 마우스피스에 대고 떨면 그 진동이 관 속에서 울려 소리가 나요.", 2),
    ("현악기의 음높이는 줄의 무엇에 따라 달라질까요?", "길이·굵기·팽팽함", ["색깔", "무게만", "나이"], "줄이 짧고 가늘고 팽팽할수록 높은 소리가 나요.", 3),
    ("연주 전에 악기끼리 음높이를 서로 맞추는 일을 무엇이라고 할까요?", "튜닝(조율)", ["리허설", "앙코르", "카덴차"], "튜닝은 모든 악기가 같은 기준 음에 맞추는 일이에요.", 1),
    ("현을 활 대신 손가락으로 뜯어 연주하는 방법은?", "피치카토", ["아르코", "트레몰로", "스타카토"], "'피치카토'는 뜯어서 연주하는 방법이고 '아르코'는 다시 활로 켠다는 뜻이에요.", 3),
    ("같은 음을 아주 빠르게 되풀이해 떨리는 효과를 내는 연주법은?", "트레몰로", ["피치카토", "레가토", "크레셴도"], "트레몰로는 '떨림'이라는 뜻이에요.", 3),
    ("음을 짧게 끊어서 연주하라는 뜻의 말은?", "스타카토", ["레가토", "아다지오", "포르테"], "스타카토는 '끊어서', 레가토는 '부드럽게 이어서'라는 뜻이에요.", 2),
    ("음을 끊지 않고 부드럽게 이어서 연주하라는 뜻의 말은?", "레가토", ["스타카토", "프레스토", "포르테"], "레가토는 '이어서'라는 뜻이에요.", 2),
    ("음악 빠르기 말 '프레스토(Presto)'의 뜻은?", "매우 빠르게", ["매우 느리게", "보통 빠르기로", "점점 세게"], "프레스토는 알레그로보다 더 빠른 빠르기예요.", 3),
    ("음악 빠르기 말 '안단테(Andante)'의 뜻은?", "걸어가는 빠르기로", ["아주 빠르게", "아주 느리게", "점점 빠르게"], "안단테는 '걷는 듯한 빠르기'라는 뜻이에요.", 2),
    ("지휘자가 연주자들에게 신호를 줄 때 손에 쥐는 가는 막대는?", "지휘봉", ["활", "채", "악보대"], "지휘봉으로 박자와 신호를 크고 분명하게 보여 줘요.", 1),
    ("팀파니를 연주할 때 쓰는 도구는?", "말렛(북채)", ["활", "리드", "마우스피스"], "끝이 둥근 북채로 가죽을 쳐서 소리를 내요.", 2),
]: add(q, a, w, "오케스트라", ex, lv)

# 더 많은 기초·용어·곡 이야기(직접 쓴 사실)
for q, a, w, ex, lv, cat in [
    ("활로 현을 켜서 소리를 내는 악기들이 모인 악기군은?", "현악기", ["목관악기", "금관악기", "타악기"], "바이올린·비올라·첼로·콘트라베이스가 현악기예요.", 1, "오케스트라"),
    ("트럼펫·호른·트롬본·튜바는 어느 악기군일까요?", "금관악기", ["현악기", "목관악기", "타악기"], "금속으로 만든 관에 입술을 떨어 불어 소리를 내서 금관악기라고 해요.", 1, "오케스트라"),
    ("플루트·오보에·클라리넷·바순은 어느 악기군일까요?", "목관악기", ["현악기", "금관악기", "타악기"], "관에 바람을 불어 소리를 내고, 전통적으로 나무로 만들어 목관악기라고 해요.", 1, "오케스트라"),
    ("팀파니·심벌즈·트라이앵글은 어느 악기군일까요?", "타악기", ["현악기", "목관악기", "금관악기"], "치거나 흔들거나 부딪쳐서 소리를 내는 악기가 타악기예요.", 1, "오케스트라"),
    ("연주 중 지휘자는 보통 누구를 마주 보고 서 있을까요?", "연주자(단원)들", ["관객", "무대 뒤 벽", "객석 맨 뒤"], "지휘자는 관객에게 등을 보이고 연주자들을 마주 보며 신호를 줘요.", 1, "오케스트라"),
    ("연주회 시작 때 보통 가장 마지막에 입장하는 사람은?", "지휘자", ["악장", "팀파니 연주자", "하프 연주자"], "단원들이 입장하고 악장이 튜닝을 마친 뒤 지휘자가 들어와요.", 2, "오케스트라"),
    ("'오케스트라'라는 말은 원래 무엇을 가리켰을까요?", "고대 그리스 극장에서 합창단이 서던 자리", ["왕궁의 연회장", "교회의 오르간 방", "악기를 파는 가게"], "오케스트라는 그리스어로 '춤추는 자리'라는 뜻에서 왔어요.", 3, "오케스트라"),
    ("교향곡은 보통 몇 개의 악장으로 이뤄질까요?", "4개", ["2개", "6개", "8개"], "빠르게-느리게-춤곡풍-빠르게의 네 악장이 가장 흔해요.", 2, "오케스트라"),
    ("협주곡은 보통 몇 개의 악장으로 이뤄질까요?", "3개", ["1개", "5개", "7개"], "빠르게-느리게-빠르게의 세 악장이 가장 흔해요.", 3, "오케스트라"),
    ("교향곡 네 악장 중 보통 둘째 악장의 빠르기는?", "느린 악장", ["가장 빠른 악장", "행진곡풍", "연주하지 않는 악장"], "대개 첫 악장은 빠르고, 둘째 악장은 느리고 노래하듯 흘러요.", 3, "오케스트라"),
    ("현악 사중주에서 제1바이올린이 주로 맡는 역할은?", "주요 선율", ["가장 낮은 반주", "박자만 치기", "쉬는 역할"], "가장 높은 소리를 내서 주요 선율을 자주 맡아요.", 3, "오케스트라"),
    ("클라리넷과 오보에의 가장 큰 차이는?", "클라리넷은 홑리드, 오보에는 겹리드", ["둘 다 금속으로 만든다", "클라리넷은 활로 켠다", "오보에는 리드가 없다"], "리드가 한 장이냐 두 장이냐에 따라 소리가 달라져요.", 3, "오케스트라"),
    ("다음 중 리드 없이 소리를 내는 악기는?", "플루트", ["오보에", "클라리넷", "바순"], "플루트는 취구에 바람을 불어 넣어 소리를 내요.", 2, "오케스트라"),
    ("'피콜로'는 이탈리아어로 어떤 뜻일까요?", "작은", ["큰", "빠른", "맑은"], "플루트의 절반 정도 크기라서 '작은 (플루트)'라고 불러요.", 3, "오케스트라"),
    ("악기 이름에 붙는 '콘트라'(콘트라베이스·콘트라바순)는 대체로 어떤 뜻일까요?", "한 옥타브 낮은", ["한 옥타브 높은", "두 배 빠른", "조금 작은"], "원래 악기보다 낮은 음역을 가졌다는 뜻이에요.", 3, "오케스트라"),
    ("'오보에(hautbois)'는 프랑스어로 어떤 뜻에서 왔을까요?", "높은 나무(높은 소리 나는 목관)", ["작은 새", "두 개의 입술", "얇은 막대"], "'높은 소리의 나무 악기'라는 뜻에서 왔어요.", 3, "오케스트라"),
    ("'첼레스타(celesta)'라는 이름은 어떤 뜻에서 왔을까요?", "하늘의, 천상의", ["작은 종", "건반 있는 하프", "은빛 줄"], "천상의 소리 같다고 해서 붙은 이름이에요.", 3, "오케스트라"),
    ("트롬본 슬라이드의 기본 위치는 몇 가지일까요?", "7가지", ["3가지", "5가지", "12가지"], "슬라이드를 바깥으로 밀수록 낮은 소리가 나고, 기본 위치가 일곱 가지예요.", 3, "오케스트라"),
    ("'튜티(tutti)'의 뜻은?", "모두 함께", ["혼자", "아주 여리게", "조금 느리게"], "오케스트라 단원이 모두 함께 연주하는 것을 말해요.", 3, "오케스트라"),
    ("여러 사람이 함께 소리를 맞춰 연주하는 것을 무엇이라고 할까요?", "합주(앙상블)", ["독주", "카덴차", "서곡"], "혼자 하면 독주(솔로), 여럿이 함께 하면 합주예요.", 1, "오케스트라"),
    ("'소나타'라는 말은 원래 어떤 곡을 가리켰을까요?", "악기로 연주하는 곡", ["노래로 부르는 곡", "춤추는 곡", "행진하는 곡"], "소리 낸다는 뜻에서 왔고, 노래하는 곡(칸타타)과 대비되는 이름이었어요.", 3, "오케스트라"),
    ("베토벤 교향곡 중 합창과 독창이 함께하는 곡은 몇 번일까요?", "9번", ["3번", "5번", "6번"], "9번 '합창'의 마지막 악장에서 노래가 함께해요.", 2, "곡 속 악기"),
    ("비발디 '사계'는 몇 개의 협주곡으로 이뤄져 있을까요?", "4개", ["2개", "3개", "12개"], "봄·여름·가을·겨울이 각각 하나의 협주곡이에요.", 2, "곡 속 악기"),
    ("'동물의 사육제'를 작곡한 사람은?", "카미유 생상스", ["안토닌 드보르자크", "클로드 드뷔시", "요하네스 브람스"], "여러 동물을 악기로 재미있게 표현한 곡이에요.", 2, "곡 속 악기"),
    ("'피터와 늑대'를 작곡한 사람은?", "세르게이 프로코피예프", ["표트르 일리치 차이콥스키", "에드바르 그리그", "모리스 라벨"], "악기마다 등장인물을 맡아 이야기를 들려주는 곡이에요.", 2, "곡 속 악기"),
    ("'볼레로'를 작곡한 사람은?", "모리스 라벨", ["카미유 생상스", "클로드 드뷔시", "에드바르 그리그"], "작은북의 같은 리듬 위에서 악기들이 차례로 선율을 이어받는 곡이에요.", 2, "곡 속 악기"),
    ("'청소년을 위한 관현악 입문'을 작곡한 사람은?", "벤저민 브리튼", ["카미유 생상스", "세르게이 프로코피예프", "클로드 드뷔시"], "오케스트라 악기와 악기군을 차례로 소개하는 곡이에요.", 3, "곡 속 악기"),
]: add(q, a, w, cat, ex, lv)
# ⑧ 무대 배치도(일반적인 배치)
for n, name, where in SEATS:
    q = f"배치도에서 주황색으로 표시된 {n}번 자리에는 보통 누가 앉을까요? (일반적인 배치)"
    wrong = [x[1] for x in SEATS if x[0] != n]; lv = 1 if n == 10 else (2 if n in (1, 4, 6) else 3)
    if add(q, name, R.sample(wrong, 3), "무대 배치", f"{n}번 자리는 {where}에 앉는 {name}의 자리가 일반적이에요. 오케스트라마다 조금씩 다를 수 있어요.", lv): IMG[q] = ["s", n]

os.makedirs("qlevel", exist_ok=True); json.dump(level, open("qlevel/orchestra-quiz.json", "w", encoding="utf-8"), ensure_ascii=False)
cnt = {1: 0, 2: 0, 3: 0}
for v in level.values(): cnt[v] += 1
print("퀴즈 문제", len(data), "초급/중급/고급", cnt[1], cnt[2], cnt[3])
make_quiz(H + "orchestra-quiz.html", "오케스트라 퀴즈", "🎻", 20, "orchestra-quiz-best-v1",
          "오케스트라 악기와 연주 이야기를 맞혀 보세요. 모든 악기는 <a href=\"orchestra-gallery.html\">🎷 오케스트라 악기 도감</a>에서 볼 수 있어요.", data, label="오케스트라 퀴즈")

# ───────── 모드 스크립트 orch-mode.js (그림·사진·정답 카드·힌트)
INFOS = {i: {"n": a["n"], "name": a["name"], "en": a["en"], "fam": a["fam"], "how": a["how"], "rng": a["rng"], "desc": a["desc"], "use": a["use"], "wiki": a["wiki"], "tok": a["tok"], "ko": ALT_KO.get(i), "de": ALT_DE.get(i), "spec": SPECS[i]} for i, a in I.items()}
DATA = {"I": INFOS, "SVG": {i: icon(i) for i in ORDER}, "SEAT": {str(n): seating(n) for n, _, _ in SEATS}, "IMG": IMG, "INFO": INFO, "SHOW": SHOW, "CMP": {i: size_compare(i, False) for i, _, _ in STR_SIZES}, "CMPN": {i: size_compare(i, True) for i, _, _ in STR_SIZES}}
tpl = open("orch_mode_tpl.js", encoding="utf-8").read(); assert "/*DATA*/null" in tpl
open("../../orch-mode.js", "w", encoding="utf-8").write(tpl.replace("/*DATA*/null", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))))
def hook(path):
    t = open(path, encoding="utf-8").read()
    if 'src="orch-mode.js"' not in t:
        t = t.replace("</body>", '<script src="online.js"></script>\n<script src="orch-mode.js" defer></script>\n</body>', 1); open(path, "w", encoding="utf-8").write(t)
hook(H + "orchestra-quiz.html")
def hook_gal():
    pass

# ───────── 악기 도감 화면
CSS = re.search(r"CSS = '''(.*?)'''", open("set43.py", encoding="utf-8").read(), re.S).group(1) + '''
.ar .cmp svg{width:100%;max-width:340px;height:auto;display:block;margin-top:4px}.ar .cmp small{color:var(--muted);font-size:.78rem}.ar .ic{width:72px;height:72px;flex:none;border-radius:12px;overflow:hidden;background:#f6efe0}.ar .ic img{width:72px;height:72px;object-fit:cover;display:block}.ar .cr{color:var(--muted);font-size:.74rem;line-height:1.4}.ar .top{display:flex;gap:12px;align-items:center}.ar .top h2{margin:0}.ar dl{margin:4px 0 0;display:grid;grid-template-columns:5.4em 1fr;gap:2px 8px;font-size:.92rem}.ar dt{color:var(--muted)}.ar dd{margin:0}'''
BODY = '''  <div class="card"><div class="chips" id="eras"></div><div class="chips" id="lvs"></div><p class="muted" id="lvp"></p><input type="text" id="q" placeholder="악기 이름·악기군·소리 찾기 (예: 바이올린, 금관, 낮은)" aria-label="찾기"><p class="muted" id="cnt"></p><a class="btn" id="goq" href="orchestra-quiz.html" style="text-align:center;text-decoration:none">🎻 오케스트라 퀴즈 풀기</a></div>
  <div id="list"></div>'''
AR = [dict(id=a["id"], n=a["n"], nm=a["name"], e=a["en"], f=a["fam"], h=a["how"], r=a["rng"], d=a["desc"], u=a["use"], l=a["fame"], sp=SPECS[a["id"]], svg=ICONS[a["id"]] and icon(a["id"]), cmp=(size_compare(a["id"], True) if a["id"] in {x[0] for x in STR_SIZES} else "")) for a in I.values()]
JS = '''const AR = ''' + json.dumps(AR, ensure_ascii=False) + ''', FAMS = ''' + json.dumps(["전체"] + FAMILIES, ensure_ascii=False) + ''';
let fam = ld(KEY + "-fam") || "전체", lvf = +ld(KEY + "-lv") || 0; if (!(lvf >= 0 && lvf <= 3)) lvf = 0;
const LVN = ["모든 난이도", "🌱 초급", "🌿 중급", "🌳 고급"], LVD = ["", "누구나 아는 악기예요.", "알려진 악기예요.", "마니아가 좋아하는 악기예요."];
const norm = s => String(s).toLowerCase().replace(/\\s+/g, "");
function render() {
  const q = norm($("q").value), box = $("list"); let n = 0, html = "", last = "";
  AR.forEach(a => {
    if (fam !== "전체" && a.f !== fam) return;
    if (lvf && a.l !== lvf) return;
    if (q && !norm([a.nm, a.e, a.f, a.h, a.r, a.d, a.u, ...(a.sp || []).map(x => x[1])].join(" ")).includes(q)) return;
    if (a.f !== last) { last = a.f; html += `<p class="era">${esc(a.f)}</p>`; }
    n++;
    html += `<article class="ar" data-id="${a.id}"><div class="top"><div class="ic">${a.svg}</div><div><h2>${a.l === 1 ? '<span class="st" aria-label="대표 악기">★</span> ' : ""}${esc(a.nm)} <span class="en">${esc(a.e)}</span></h2><div class="meta"><span>도감 ${a.n}번</span><span class="tag">${esc(a.f)}</span></div></div></div><p class="bio">${esc(a.d)}</p><dl><dt>소리 높이</dt><dd>${esc(a.r)} 소리</dd><dt>연주 방법</dt><dd>${esc(a.h)}</dd><dt>쓰임</dt><dd>${esc(a.u)}</dd>${(a.sp || []).map(x => `<dt>${esc(x[0])}</dt><dd>${esc(x[1])}</dd>`).join("")}</dl>${a.cmp ? `<div class="cmp"><small>크기 비교 (주황 색이 이 악기)</small>${a.cmp}</div>` : ""}</article>`;
  });
  box.innerHTML = html || '<p class="muted center">찾는 악기가 없어요</p>';
  $("lvs").innerHTML = LVN.map((t, k) => `<button type="button" class="chip${k === lvf ? " on" : ""}" data-l="${k}">${t}${k ? ` <small>${AR.filter(a => a.l === k).length}</small>` : ""}</button>`).join(""); $("lvp").textContent = LVD[lvf];
  $("cnt").textContent = n ? `악기 ${n}개 (★ = 누구나 아는 대표 악기, 소리 높이는 같은 악기군 안에서의 비교예요)` : "";
}
$("eras").innerHTML = FAMS.map(e => `<button type="button" class="chip${e === fam ? " on" : ""}" data-e="${esc(e)}">${esc(e)}</button>`).join("");
$("eras").addEventListener("click", ev => { const b = ev.target.closest("[data-e]"); if (!b) return; fam = b.dataset.e; sv(KEY + "-fam", fam); $("eras").querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c === b)); render(); });
$("lvs").addEventListener("click", ev => { const b = ev.target.closest("[data-l]"); if (!b) return; lvf = +b.dataset.l; sv(KEY + "-lv", lvf); render(); });
$("q").addEventListener("input", render); render();'''
make_page(H + "orchestra-gallery.html", "오케스트라 악기 도감", "🎷", 20, "orchestra-gallery-v1",
          "오케스트라에서 만나는 악기를 그림과 함께 정리했어요. 그림은 직접 그린 단순한 그림이에요. 소리 높이는 같은 악기군 안에서의 비교예요.", BODY, JS, CSS)

hook(H + "orchestra-gallery.html")
