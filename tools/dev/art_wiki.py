# 명화 그림 모드(온라인·내장)용 위키백과 항목 대응표. 작품 제목(art_data.py) → 위키백과 항목 후보(앞에서부터 시도).
#   "en:" 영어판, "ko:" 한국어판. 후보가 틀려도 안전: 런타임(online.js)·art_fetch.py 가 ① 항목 설명에 작가 이름이 있는지 ② 그림이 공개 도메인인지 확인하고, 아니면 그림 없이 글로만 보여 줘요.
#   저작권이 남아 있을 수 있는 작가(사후 70년이 안 지났거나 확실하지 않은 작가)는 NO_IMAGE 에 넣어 그림을 아예 쓰지 않아요.
NO_IMAGE = {"matisse", "picasso", "dali", "magritte", "chagall", "warhol", "pollock", "kahlo", "hopper"}
WIKI = {
 # (2026-11-23 실제 위키백과로 검증: 사진 저작권이 남은 천지창조·다비드 상·피에타, 그림첩으로 연결되던 한국 풍속화, 대표 그림이 없는 항목은 대응에서 뺌 → 그림 없이 글로만)
 "모나리자": ["en:Mona_Lisa"], "최후의 만찬": ["en:The_Last_Supper_(Leonardo)"], "암굴의 성모": ["en:Virgin_of_the_Rocks"], "흰 담비를 안은 여인": ["en:Lady_with_an_Ermine"],
 "비트루비우스적 인간": ["en:Vitruvian_Man"],
 "최후의 심판": ["en:The_Last_Judgment_(Michelangelo)"], "도니 톤도": ["en:Doni_Tondo"],
 "아테네 학당": ["en:The_School_of_Athens"], "시스티나 성모": ["en:Sistine_Madonna"], "의자의 성모": ["en:Madonna_della_seggiola"], "그리스도의 변모": ["en:Transfiguration_(Raphael)"],
 "비너스의 탄생": ["en:The_Birth_of_Venus"], "프리마베라(봄)": ["en:Primavera_(Botticelli)"], "비너스와 마르스": ["en:Venus_and_Mars_(Botticelli)"],
 "우르비노의 비너스": ["en:Venus_of_Urbino"], "성모 승천": ["en:Assumption_of_the_Virgin_(Titian)"],
 "아르놀피니 부부의 초상": ["en:Arnolfini_Portrait"], "겐트 제단화": ["en:Ghent_Altarpiece"],
 "대사들": ["en:The_Ambassadors_(Holbein)"],
 "모피 외투를 입은 자화상": ["en:Self-Portrait_(Dürer,_Munich)"], "기도하는 손": ["en:Praying_Hands_(Dürer)"], "멜랑콜리아 I": ["en:Melencolia_I"], "코뿔소": ["en:Dürer's_Rhinoceros"],
 "쾌락의 정원": ["en:The_Garden_of_Earthly_Delights"], "건초 수레(세폭 제단화)": ["en:The_Haywain_Triptych"],
 "바벨탑": ["en:The_Tower_of_Babel_(Bruegel)"], "눈 속의 사냥꾼": ["en:The_Hunters_in_the_Snow"], "농민의 결혼식": ["en:The_Peasant_Wedding"], "아이들의 놀이": ["en:Children's_Games_(Bruegel)"],
 "성 마태의 소명": ["en:The_Calling_of_St_Matthew_(Caravaggio)"], "바쿠스": ["en:Bacchus_(Caravaggio)"], "의심하는 도마": ["en:The_Incredulity_of_Saint_Thomas_(Caravaggio)"], "과일 바구니": ["en:Basket_of_Fruit_(Caravaggio)"],
 "야경": ["en:The_Night_Watch"], "니콜라스 튈프 박사의 해부학 강의": ["en:The_Anatomy_Lesson_of_Dr._Nicolaes_Tulp"], "돌아온 탕자": ["en:The_Return_of_the_Prodigal_Son_(Rembrandt)"], "유대인 신부": ["en:The_Jewish_Bride"],
 "진주 귀걸이를 한 소녀": ["en:Girl_with_a_Pearl_Earring"], "우유를 따르는 하녀": ["en:The_Milkmaid_(Vermeer)"], "델프트 풍경": ["en:View_of_Delft"], "레이스를 짜는 여인": ["en:The_Lacemaker_(Vermeer)"],
 "회화의 기술": ["en:The_Art_of_Painting"], "편지를 읽는 푸른 옷의 여인": ["en:Woman_in_Blue_Reading_a_Letter"],
 "시녀들": ["en:Las_Meninas"], "브레다의 항복": ["en:The_Surrender_of_Breda"], "교황 인노첸시오 10세의 초상": ["en:Portrait_of_Innocent_X"], "거울을 보는 비너스": ["en:Rokeby_Venus"],
 "오르가스 백작의 매장": ["en:The_Burial_of_the_Count_of_Orgaz"], "톨레도 풍경": ["en:View_of_Toledo"],
 "십자가에서 내려지심": ["en:The_Descent_from_the_Cross_(Rubens,_1612–1614)"], "삼미신": ["en:The_Three_Graces_(Rubens,_Madrid)"],
 "웃는 기사": ["en:The_Laughing_Cavalier"], "키테라 섬의 순례": ["en:The_Embarkation_for_Cythera"], "그네": ["en:The_Swing_(Fragonard)"],
 "1808년 5월 3일": ["en:The_Third_of_May_1808"], "옷을 벗은 마하": ["en:The_Nude_Maja"], "아들을 잡아먹는 사투르누스": ["en:Saturn_Devouring_His_Son"], "카를로스 4세의 가족": ["en:The_Family_of_Charles_IV"],
 "나폴레옹 1세의 대관식": ["en:The_Coronation_of_Napoleon"], "마라의 죽음": ["en:The_Death_of_Marat"], "호라티우스 형제의 맹세": ["en:Oath_of_the_Horatii"], 
 "그랑드 오달리스크": ["en:La_Grande_Odalisque"], "샘": ["en:The_Source_(Ingres)", "en:The_Source_(painting)"], "터키탕": ["en:The_Turkish_Bath"],
 "민중을 이끄는 자유의 여신": ["en:Liberty_Leading_the_People"], "사르다나팔루스의 죽음": ["en:The_Death_of_Sardanapalus"], "키오스 섬의 학살": ["en:The_Massacre_at_Chios"],
 "메두사호의 뗏목": ["en:The_Raft_of_the_Medusa"],
 "비, 증기, 속도": ["en:Rain,_Steam_and_Speed_–_The_Great_Western_Railway"], "전함 테메레르": ["en:The_Fighting_Temeraire"], "노예선": ["en:The_Slave_Ship"],
 "건초 마차": ["en:The_Hay_Wain"], "안개 바다 위의 방랑자": ["en:Wanderer_above_the_Sea_of_Fog"], "바닷가의 수도사": ["en:Monk_by_the_Sea"],
 "오르낭의 매장": ["en:A_Burial_at_Ornans"], "화가의 아틀리에": ["en:The_Painter's_Studio"], "안녕하세요, 쿠르베 씨": ["en:Bonjour,_Monsieur_Courbet"],
 "이삭 줍는 사람들": ["en:The_Gleaners"], "만종": ["en:The_Angelus_(painting)", "en:The_Angelus_(Millet)"], "씨 뿌리는 사람": ["en:The_Sower_(Millet)"],
 "풀밭 위의 점심 식사": ["en:Le_Déjeuner_sur_l'herbe"], "올랭피아": ["en:Olympia_(Manet)"], "폴리베르제르의 바": ["en:A_Bar_at_the_Folies-Bergère"], "피리 부는 소년": ["en:The_Fifer"],
 "인상, 해돋이": ["en:Impression,_Sunrise"], "수련": ["en:Water_Lilies"], "루앙 대성당 연작": ["en:Rouen_Cathedral_(Monet_series)", "en:Rouen_Cathedral_(Monet)"], "건초더미 연작": ["en:Haystacks_(Monet)"],
 "양산을 든 여인": ["en:Woman_with_a_Parasol_–_Madame_Monet_and_Her_Son"], "생 라자르 역": ["en:Gare_Saint-Lazare_(Monet_series)"],
 "물랭 드 라 갈레트의 무도회": ["en:Bal_du_moulin_de_la_Galette"], "보트 놀이 일행의 오찬": ["en:Luncheon_of_the_Boating_Party"], "피아노 치는 소녀들": ["en:Girls_at_the_Piano"],
 "압생트": ["en:L'Absinthe"], "발레 수업": ["en:The_Dance_Class"],
 "카드놀이 하는 사람들": ["en:The_Card_Players"], 
 "별이 빛나는 밤": ["en:The_Starry_Night"], "해바라기": ["en:Sunflowers_(series_of_paintings_by_Vincent_van_Gogh)", "en:Sunflowers_(Van_Gogh_series)"], "밤의 카페 테라스": ["en:Café_Terrace_at_Night"],
 "감자 먹는 사람들": ["en:The_Potato_Eaters"], "아를의 침실": ["en:Bedroom_in_Arles"], "까마귀가 나는 밀밭": ["en:Wheatfield_with_Crows"], "귀에 붕대를 감은 자화상": ["en:Self-Portrait_with_Bandaged_Ear"],
 "론 강의 별이 빛나는 밤": ["en:Starry_Night_Over_the_Rhône"], "닥터 가셰의 초상": ["en:Portrait_of_Dr._Gachet"],
 "우리는 어디서 왔는가, 우리는 무엇인가, 우리는 어디로 가는가": ["en:Where_Do_We_Come_From?_What_Are_We?_Where_Are_We_Going?"], "황색 그리스도": ["en:The_Yellow_Christ"], "설교 후의 환상": ["en:Vision_After_the_Sermon"],
 "그랑드 자트 섬의 일요일 오후": ["en:A_Sunday_Afternoon_on_the_Island_of_La_Grande_Jatte"], "아니에르에서의 물놀이": ["en:Bathers_at_Asnières"],
 "물랭 루주의 라 굴뤼": ["en:Moulin_Rouge:_La_Goulue"],
 "잠자는 집시": ["en:The_Sleeping_Gypsy"], "꿈": ["en:The_Dream_(Rousseau)"], "열대 폭풍 속의 호랑이": ["en:Surprised!"],
 "키스": ["en:The_Kiss_(Klimt)"], "유디트 I": ["en:Judith_and_the_Head_of_Holofernes_(Klimt)"], "아델레 블로흐바우어 1세의 초상": ["en:Portrait_of_Adele_Bloch-Bauer_I"], "아테나 팔라스": ["en:Pallas_Athena_(Klimt)"],
 "절규": ["en:The_Scream"], "사춘기": ["en:Puberty_(Munch)"], "병든 아이": ["en:The_Sick_Child_(Munch)"],
 "죽음과 소녀": ["en:Death_and_the_Maiden_(Schiele)"],
 "구성 VII": ["en:Composition_VII"], "빨강, 파랑, 노랑의 구성": ["en:Composition_with_Red_Blue_and_Yellow"], "브로드웨이 부기우기": ["en:Broadway_Boogie_Woogie"],
 "회색과 검정의 배열 1번(화가의 어머니)": ["en:Whistler's_Mother"], "마담 X": ["en:Portrait_of_Madame_X"],
 "가나가와 해변의 높은 파도": ["en:The_Great_Wave_off_Kanagawa"], "맑은 날의 남풍(붉은 후지)": ["en:Fine_Wind,_Clear_Morning"],
 
 "인왕제색도": ["ko:인왕제색도"], "금강전도": ["ko:금강전도"], "몽유도원도": ["ko:몽유도원도"], 
}
# 작가 이름 토큰이 너무 흔한 단어면 따로 지정(예: David 는 다비드 상과 헷갈려요)
TOKEN_OVERRIDE = {"rembrandt": ["rembrandt"], "david": ["jacques-louis david"], "turner": ["j. m. w. turner", "joseph mallord william turner", "turner"], "constable": ["john constable", "constable"], "hals": ["frans hals"],
                  "manet": ["édouard manet", "edouard manet", "manet"], "monet": ["claude monet", "monet"]}

EXTRA_TOKENS = {"raphael": ["raphael", "raffaello"], "titian": ["titian", "tiziano"], "bruegel": ["bruegel", "brueghel"], "elgreco": ["el greco", "greco"], "vaneyck": ["van eyck"],
                "lautrec": ["lautrec", "toulouse-lautrec"], "friedrich": ["friedrich"], "michelangelo": ["michelangelo"], "leonardo": ["leonardo"], "holbein": ["holbein"], "durer": ["durer", "dürer"],
                "velazquez": ["velazquez", "velázquez"], "kimhongdo": ["김홍도", "단원"], "sinyunbok": ["신윤복", "혜원"], "jeongseon": ["정선", "겸재"], "angyeon": ["안견"], "kimjeonghui": ["김정희", "추사"]}
def tokens(aid, en, name):
    """위키백과 항목 설명에 하나 이상 들어 있어야 하는 작가 이름(영문·한글). online.js 의 확인과 같은 규칙."""
    if aid in TOKEN_OVERRIDE: t = list(TOKEN_OVERRIDE[aid])
    else:
        w = en.split(); t = [en] + ([w[-1]] if len(w[-1]) >= 4 else [])
    t += EXTRA_TOKENS.get(aid, []); t.append(name)
    return list(dict.fromkeys(t))
