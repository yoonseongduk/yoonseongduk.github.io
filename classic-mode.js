/* 클래식 듣고 맞히기 — 클래식 작곡가 퀴즈(classic-quiz.html)와 작곡가별 모음(classic-gallery.html) 공용.
   음원은 이 저장소(GitHub)나 서버에 두지 않아요. 사용자가 🌐 온라인 듣기를 허락하면 ① 위키미디어 커먼즈에서 곡 음원을 찾고 ② 파일 이름에 곡 낱말이 있고 ③ 라이선스가 공개 도메인·CC0 표시일 때만 불러와
   처음 듣는 동안 이 폰의 저장 공간(Cache)에 앞부분(약 900KB, 20~30초)을 저장해요. 그다음부터는 인터넷 없이도 들려요. 하나라도 틀리면 그 곡은 음원 없이 글로만 나와요.
   이 파일은 tools/dev/set44.py 가 만들어요(직접 고치지 말고 tools/dev/classic_mode_tpl.js 와 set44.py 를 고치세요). */
(function () {
  "use strict";
  var DATA = {"W":{"토카타와 푸가 d단조":["요한 제바스티안 바흐","1700년대 초","오르간곡","바로크",1,"독일","bach"],"G선상의 아리아":["요한 제바스티안 바흐","1720년대경","관현악곡","바로크",1,"독일","bach"],"브란덴부르크 협주곡":["요한 제바스티안 바흐","1721","협주곡","바로크",2,"독일","bach"],"마태 수난곡":["요한 제바스티안 바흐","1727경","종교 음악","바로크",3,"독일","bach"],"골트베르크 변주곡":["요한 제바스티안 바흐","1741경","피아노 독주곡","바로크",3,"독일","bach"],"평균율 클라비어 곡집":["요한 제바스티안 바흐","1722","피아노 독주곡","바로크",3,"독일","bach"],"메시아":["게오르크 프리드리히 헨델","1741","종교 음악","바로크",1,"독일","handel"],"수상 음악":["게오르크 프리드리히 헨델","1717","관현악곡","바로크",2,"독일","handel"],"왕궁의 불꽃놀이 음악":["게오르크 프리드리히 헨델","1749","관현악곡","바로크",2,"독일","handel"],"울게 하소서":["게오르크 프리드리히 헨델","1711","오페라","바로크",2,"독일","handel"],"사계":["안토니오 비발디","1720년대","협주곡","바로크",1,"이탈리아","vivaldi"],"조화의 영감":["안토니오 비발디","1711","협주곡","바로크",3,"이탈리아","vivaldi"],"캐논 D장조":["요한 파헬벨","1680년대경","실내악","바로크",1,"독일","pachelbel"],"교향곡 94번 '놀람'":["요제프 하이든","1791","교향곡","고전",1,"오스트리아","haydn"],"교향곡 101번 '시계'":["요제프 하이든","1794","교향곡","고전",2,"오스트리아","haydn"],"천지창조":["요제프 하이든","1798","종교 음악","고전",2,"오스트리아","haydn"],"현악 사중주 '황제'":["요제프 하이든","1797","실내악","고전",3,"오스트리아","haydn"],"아이네 클라이네 나흐트무지크":["볼프강 아마데우스 모차르트","1787","관현악곡","고전",1,"오스트리아","mozart"],"터키 행진곡(피아노 소나타 11번 중)":["볼프강 아마데우스 모차르트","1783경","피아노 독주곡","고전",1,"오스트리아","mozart"],"마술피리":["볼프강 아마데우스 모차르트","1791","오페라","고전",1,"오스트리아","mozart"],"피가로의 결혼":["볼프강 아마데우스 모차르트","1786","오페라","고전",1,"오스트리아","mozart"],"교향곡 40번 g단조":["볼프강 아마데우스 모차르트","1788","교향곡","고전",2,"오스트리아","mozart"],"교향곡 41번 '주피터'":["볼프강 아마데우스 모차르트","1788","교향곡","고전",2,"오스트리아","mozart"],"돈 조반니":["볼프강 아마데우스 모차르트","1787","오페라","고전",2,"오스트리아","mozart"],"클라리넷 협주곡 A장조":["볼프강 아마데우스 모차르트","1791","협주곡","고전",3,"오스트리아","mozart"],"교향곡 5번 '운명'":["루트비히 판 베토벤","1808","교향곡","고전",1,"독일","beethoven"],"교향곡 9번 '합창'":["루트비히 판 베토벤","1824","교향곡","고전",1,"독일","beethoven"],"엘리제를 위하여":["루트비히 판 베토벤","1810경","피아노 독주곡","고전",1,"독일","beethoven"],"피아노 소나타 14번 '월광'":["루트비히 판 베토벤","1801","피아노 독주곡","고전",1,"독일","beethoven"],"교향곡 6번 '전원'":["루트비히 판 베토벤","1808","교향곡","고전",2,"독일","beethoven"],"피아노 소나타 8번 '비창'":["루트비히 판 베토벤","1799","피아노 독주곡","고전",2,"독일","beethoven"],"피아노 협주곡 5번 '황제'":["루트비히 판 베토벤","1809","협주곡","고전",2,"독일","beethoven"],"교향곡 3번 '영웅'":["루트비히 판 베토벤","1804","교향곡","고전",2,"독일","beethoven"],"마왕":["프란츠 슈베르트","1815","가곡·성악곡","낭만",2,"오스트리아","schubert"],"아베 마리아(엘렌의 노래 3번)":["프란츠 슈베르트","1825","가곡·성악곡","낭만",1,"오스트리아","schubert"],"피아노 오중주 '송어'":["프란츠 슈베르트","1819","실내악","낭만",2,"오스트리아","schubert"],"교향곡 8번 '미완성'":["프란츠 슈베르트","1822","교향곡","낭만",1,"오스트리아","schubert"],"겨울 나그네":["프란츠 슈베르트","1827","가곡·성악곡","낭만",2,"오스트리아","schubert"],"군대 행진곡 1번":["프란츠 슈베르트","1818경","행진곡·무곡","낭만",3,"오스트리아","schubert"],"윌리엄 텔 서곡":["조아키노 로시니","1829","관현악곡","낭만",1,"이탈리아","rossini"],"세비야의 이발사":["조아키노 로시니","1816","오페라","낭만",1,"이탈리아","rossini"],"한여름 밤의 꿈 서곡":["펠릭스 멘델스존","1826","관현악곡","낭만",2,"독일","mendelssohn"],"결혼 행진곡(한여름 밤의 꿈 중)":["펠릭스 멘델스존","1842","행진곡·무곡","낭만",1,"독일","mendelssohn"],"바이올린 협주곡 e단조":["펠릭스 멘델스존","1844","협주곡","낭만",1,"독일","mendelssohn"],"핑갈의 동굴":["펠릭스 멘델스존","1830","관현악곡","낭만",3,"독일","mendelssohn"],"교향곡 4번 '이탈리아'":["펠릭스 멘델스존","1833","교향곡","낭만",2,"독일","mendelssohn"],"무언가":["펠릭스 멘델스존","1830~1845","피아노 독주곡","낭만",3,"독일","mendelssohn"],"즉흥 환상곡":["프레데리크 쇼팽","1834","피아노 독주곡","낭만",2,"폴란드","chopin"],"녹턴 Op.9-2":["프레데리크 쇼팽","1832","피아노 독주곡","낭만",1,"폴란드","chopin"],"빗방울 전주곡":["프레데리크 쇼팽","1839","피아노 독주곡","낭만",2,"폴란드","chopin"],"영웅 폴로네즈":["프레데리크 쇼팽","1842","피아노 독주곡","낭만",2,"폴란드","chopin"],"이별의 곡(에튀드 Op.10-3)":["프레데리크 쇼팽","1832","피아노 독주곡","낭만",2,"폴란드","chopin"],"혁명 에튀드":["프레데리크 쇼팽","1831","피아노 독주곡","낭만",2,"폴란드","chopin"],"강아지 왈츠":["프레데리크 쇼팽","1847","피아노 독주곡","낭만",1,"폴란드","chopin"],"피아노 협주곡 1번 e단조":["프레데리크 쇼팽","1830","협주곡","낭만",3,"폴란드","chopin"],"트로이메라이":["로베르트 슈만","1838","피아노 독주곡","낭만",1,"독일","schumann"],"어린이 정경":["로베르트 슈만","1838","피아노 독주곡","낭만",2,"독일","schumann"],"시인의 사랑":["로베르트 슈만","1840","가곡·성악곡","낭만",3,"독일","schumann"],"사랑의 꿈 3번":["프란츠 리스트","1850","피아노 독주곡","낭만",2,"헝가리","liszt"],"헝가리 광시곡 2번":["프란츠 리스트","1847","피아노 독주곡","낭만",1,"헝가리","liszt"],"전주곡(레 프렐뤼드)":["프란츠 리스트","1854","관현악곡","낭만",3,"헝가리","liszt"],"라 트라비아타":["주세페 베르디","1853","오페라","낭만",1,"이탈리아","verdi"],"아이다":["주세페 베르디","1871","오페라","낭만",1,"이탈리아","verdi"],"리골레토":["주세페 베르디","1851","오페라","낭만",2,"이탈리아","verdi"],"나부코":["주세페 베르디","1842","오페라","낭만",2,"이탈리아","verdi"],"일 트로바토레":["주세페 베르디","1853","오페라","낭만",3,"이탈리아","verdi"],"발퀴레의 기행":["리하르트 바그너","1856","관현악곡","낭만",1,"독일","wagner"],"로엔그린":["리하르트 바그너","1848","오페라","낭만",2,"독일","wagner"],"트리스탄과 이졸데":["리하르트 바그너","1859","오페라","낭만",2,"독일","wagner"],"탄호이저":["리하르트 바그너","1845","오페라","낭만",3,"독일","wagner"],"아름답고 푸른 도나우":["요한 슈트라우스 2세","1867","행진곡·무곡","낭만",1,"오스트리아","strauss2"],"봄의 소리 왈츠":["요한 슈트라우스 2세","1882","행진곡·무곡","낭만",2,"오스트리아","strauss2"],"박쥐":["요한 슈트라우스 2세","1874","오페라","낭만",2,"오스트리아","strauss2"],"황제 왈츠":["요한 슈트라우스 2세","1889","행진곡·무곡","낭만",3,"오스트리아","strauss2"],"트리치 트라치 폴카":["요한 슈트라우스 2세","1858","행진곡·무곡","낭만",3,"오스트리아","strauss2"],"몰다우":["베드르지흐 스메타나","1874","관현악곡","국민악파",1,"체코","smetana"],"팔려간 신부":["베드르지흐 스메타나","1866","오페라","국민악파",2,"체코","smetana"],"카르멘":["조르주 비제","1875","오페라","낭만",1,"프랑스","bizet"],"아를의 여인":["조르주 비제","1872","관현악곡","낭만",2,"프랑스","bizet"],"진주조개잡이":["조르주 비제","1863","오페라","낭만",3,"프랑스","bizet"],"동물의 사육제":["카미유 생상스","1886","관현악곡","낭만",1,"프랑스","saintsaens"],"백조(동물의 사육제 중)":["카미유 생상스","1886","관현악곡","낭만",1,"프랑스","saintsaens"],"죽음의 무도":["카미유 생상스","1874","관현악곡","낭만",2,"프랑스","saintsaens"],"삼손과 델릴라":["카미유 생상스","1877","오페라","낭만",2,"프랑스","saintsaens"],"교향곡 3번 '오르간'":["카미유 생상스","1886","교향곡","낭만",3,"프랑스","saintsaens"],"헝가리 무곡 5번":["요하네스 브람스","1869","행진곡·무곡","낭만",1,"독일","brahms"],"자장가":["요하네스 브람스","1868","가곡·성악곡","낭만",1,"독일","brahms"],"대학 축전 서곡":["요하네스 브람스","1880","관현악곡","낭만",3,"독일","brahms"],"독일 레퀴엠":["요하네스 브람스","1868","종교 음악","낭만",3,"독일","brahms"],"폴로베츠인의 춤(이고르 공 중)":["알렉산드르 보로딘","1870~1880년대","오페라","국민악파",2,"러시아","borodin"],"중앙아시아의 초원에서":["알렉산드르 보로딘","1880","관현악곡","국민악파",3,"러시아","borodin"],"전람회의 그림":["모데스트 무소륵스키","1874","피아노 독주곡","국민악파",1,"러시아","mussorgsky"],"민둥산의 하룻밤":["모데스트 무소륵스키","1867","관현악곡","국민악파",2,"러시아","mussorgsky"],"백조의 호수":["표트르 일리치 차이콥스키","1876","발레 음악","낭만",1,"러시아","tchaikovsky"],"호두까기 인형":["표트르 일리치 차이콥스키","1892","발레 음악","낭만",1,"러시아","tchaikovsky"],"잠자는 숲속의 미녀":["표트르 일리치 차이콥스키","1889","발레 음악","낭만",2,"러시아","tchaikovsky"],"1812년 서곡":["표트르 일리치 차이콥스키","1880","관현악곡","낭만",2,"러시아","tchaikovsky"],"피아노 협주곡 1번 b♭단조":["표트르 일리치 차이콥스키","1875","협주곡","낭만",1,"러시아","tchaikovsky"],"교향곡 6번 '비창'":["표트르 일리치 차이콥스키","1893","교향곡","낭만",2,"러시아","tchaikovsky"],"바이올린 협주곡 D장조":["표트르 일리치 차이콥스키","1878","협주곡","낭만",2,"러시아","tchaikovsky"],"교향곡 9번 '신세계로부터'":["안토닌 드보르자크","1893","교향곡","국민악파",1,"체코","dvorak"],"유모레스크":["안토닌 드보르자크","1894","피아노 독주곡","국민악파",2,"체코","dvorak"],"슬라브 무곡":["안토닌 드보르자크","1878","행진곡·무곡","국민악파",2,"체코","dvorak"],"첼로 협주곡 b단조":["안토닌 드보르자크","1895","협주곡","국민악파",3,"체코","dvorak"],"왕벌의 비행":["니콜라이 림스키코르사코프","1900","관현악곡","국민악파",1,"러시아","rimsky"],"셰에라자드":["니콜라이 림스키코르사코프","1888","관현악곡","국민악파",1,"러시아","rimsky"],"파반":["가브리엘 포레","1887","관현악곡","낭만",2,"프랑스","faure"],"레퀴엠 d단조":["가브리엘 포레","1888","종교 음악","낭만",2,"프랑스","faure"],"꿈꾼 후에":["가브리엘 포레","1877","가곡·성악곡","낭만",3,"프랑스","faure"],"페르 귄트":["에드바르 그리그","1875","관현악곡","국민악파",1,"노르웨이","grieg"],"아침(페르 귄트 중)":["에드바르 그리그","1875","관현악곡","국민악파",1,"노르웨이","grieg"],"솔베이그의 노래(페르 귄트 중)":["에드바르 그리그","1875","가곡·성악곡","국민악파",2,"노르웨이","grieg"],"피아노 협주곡 a단조":["에드바르 그리그","1868","협주곡","국민악파",2,"노르웨이","grieg"],"홀베르크 모음곡":["에드바르 그리그","1884","관현악곡","국민악파",3,"노르웨이","grieg"],"위풍당당 행진곡":["에드워드 엘가","1901","행진곡·무곡","낭만",1,"영국","elgar"],"사랑의 인사":["에드워드 엘가","1888","관현악곡","낭만",1,"영국","elgar"],"수수께끼 변주곡":["에드워드 엘가","1899","관현악곡","낭만",2,"영국","elgar"],"첼로 협주곡 e단조":["에드워드 엘가","1919","협주곡","낭만",3,"영국","elgar"],"라 보엠":["자코모 푸치니","1896","오페라","낭만",1,"이탈리아","puccini"],"토스카":["자코모 푸치니","1900","오페라","낭만",1,"이탈리아","puccini"],"나비 부인":["자코모 푸치니","1904","오페라","낭만",1,"이탈리아","puccini"],"투란도트":["자코모 푸치니","1920년대(미완)","오페라","낭만",2,"이탈리아","puccini"],"교향곡 1번 '거인'":["구스타프 말러","1888","교향곡","낭만",2,"오스트리아","mahler"],"교향곡 2번 '부활'":["구스타프 말러","1894","교향곡","낭만",2,"오스트리아","mahler"],"대지의 노래":["구스타프 말러","1909","교향곡","낭만",3,"오스트리아","mahler"],"차라투스트라는 이렇게 말했다":["리하르트 슈트라우스","1896","관현악곡","낭만",1,"독일","strauss_r"],"틸 오일렌슈피겔의 유쾌한 장난":["리하르트 슈트라우스","1895","관현악곡","낭만",3,"독일","strauss_r"],"장미의 기사":["리하르트 슈트라우스","1910","오페라","낭만",3,"독일","strauss_r"],"핀란디아":["장 시벨리우스","1899","관현악곡","국민악파",1,"핀란드","sibelius"],"슬픈 왈츠":["장 시벨리우스","1904","관현악곡","국민악파",2,"핀란드","sibelius"],"짐노페디":["에릭 사티","1888","피아노 독주곡","근현대",1,"프랑스","satie"],"그노시엔":["에릭 사티","1890","피아노 독주곡","근현대",2,"프랑스","satie"],"달빛(베르가마스크 모음곡 중)":["클로드 드뷔시","1890","피아노 독주곡","근현대",1,"프랑스","debussy"],"아라베스크 1번":["클로드 드뷔시","1891","피아노 독주곡","근현대",2,"프랑스","debussy"],"목신의 오후 전주곡":["클로드 드뷔시","1894","관현악곡","근현대",2,"프랑스","debussy"],"바다":["클로드 드뷔시","1905","관현악곡","근현대",2,"프랑스","debussy"],"꿈":["클로드 드뷔시","1890","피아노 독주곡","근현대",3,"프랑스","debussy"],"행성":["구스타브 홀스트","1914~1916","관현악곡","근현대",1,"영국","holst"],"피아노 협주곡 2번 c단조":["세르게이 라흐마니노프","1901","협주곡","낭만",1,"러시아","rachmaninoff"],"전주곡 c♯단조":["세르게이 라흐마니노프","1892","피아노 독주곡","낭만",2,"러시아","rachmaninoff"],"파가니니 주제에 의한 광시곡":["세르게이 라흐마니노프","1934","관현악곡","낭만",2,"러시아","rachmaninoff"],"볼레로":["모리스 라벨","1928","관현악곡","근현대",1,"프랑스","ravel"],"죽은 왕녀를 위한 파반느":["모리스 라벨","1899","피아노 독주곡","근현대",1,"프랑스","ravel"],"물의 유희":["모리스 라벨","1901","피아노 독주곡","근현대",3,"프랑스","ravel"],"라 발스":["모리스 라벨","1920","관현악곡","근현대",3,"프랑스","ravel"],"봄의 제전":["이고르 스트라빈스키","1913","발레 음악","근현대",2,"러시아","stravinsky"],"불새":["이고르 스트라빈스키","1910","발레 음악","근현대",2,"러시아","stravinsky"],"페트루슈카":["이고르 스트라빈스키","1911","발레 음악","근현대",3,"러시아","stravinsky"],"루마니아 민속 무곡":["벨러 버르토크","1915","피아노 독주곡","근현대",3,"헝가리","bartok"],"관현악을 위한 협주곡":["벨러 버르토크","1943","관현악곡","근현대",3,"헝가리","bartok"],"피터와 늑대":["세르게이 프로코피예프","1936","관현악곡","근현대",1,"러시아","prokofiev"],"로미오와 줄리엣":["세르게이 프로코피예프","1935","발레 음악","근현대",2,"러시아","prokofiev"],"랩소디 인 블루":["조지 거슈윈","1924","관현악곡","근현대",1,"미국","gershwin"],"파리의 아메리카인":["조지 거슈윈","1928","관현악곡","근현대",2,"미국","gershwin"],"포기와 베스":["조지 거슈윈","1935","오페라","근현대",3,"미국","gershwin"],"왈츠 2번(재즈 모음곡 2번)":["드미트리 쇼스타코비치","1938","행진곡·무곡","근현대",2,"러시아","shostakovich"],"교향곡 7번 '레닌그라드'":["드미트리 쇼스타코비치","1941","교향곡","근현대",3,"러시아","shostakovich"],"현을 위한 아다지오":["새뮤얼 바버","1936","관현악곡","근현대",2,"미국","barber"]},"C":[["요한 제바스티안 바흐","바로크","bach"],["게오르크 프리드리히 헨델","바로크","handel"],["안토니오 비발디","바로크","vivaldi"],["요한 파헬벨","바로크","pachelbel"],["요제프 하이든","고전","haydn"],["볼프강 아마데우스 모차르트","고전","mozart"],["루트비히 판 베토벤","고전","beethoven"],["프란츠 슈베르트","낭만","schubert"],["조아키노 로시니","낭만","rossini"],["펠릭스 멘델스존","낭만","mendelssohn"],["프레데리크 쇼팽","낭만","chopin"],["로베르트 슈만","낭만","schumann"],["프란츠 리스트","낭만","liszt"],["주세페 베르디","낭만","verdi"],["리하르트 바그너","낭만","wagner"],["요한 슈트라우스 2세","낭만","strauss2"],["베드르지흐 스메타나","국민악파","smetana"],["조르주 비제","낭만","bizet"],["카미유 생상스","낭만","saintsaens"],["요하네스 브람스","낭만","brahms"],["알렉산드르 보로딘","국민악파","borodin"],["모데스트 무소륵스키","국민악파","mussorgsky"],["표트르 일리치 차이콥스키","낭만","tchaikovsky"],["안토닌 드보르자크","국민악파","dvorak"],["니콜라이 림스키코르사코프","국민악파","rimsky"],["가브리엘 포레","낭만","faure"],["에드바르 그리그","국민악파","grieg"],["에드워드 엘가","낭만","elgar"],["자코모 푸치니","낭만","puccini"],["구스타프 말러","낭만","mahler"],["리하르트 슈트라우스","낭만","strauss_r"],["장 시벨리우스","국민악파","sibelius"],["에릭 사티","근현대","satie"],["클로드 드뷔시","근현대","debussy"],["구스타브 홀스트","근현대","holst"],["세르게이 라흐마니노프","낭만","rachmaninoff"],["모리스 라벨","근현대","ravel"],["이고르 스트라빈스키","근현대","stravinsky"],["벨러 버르토크","근현대","bartok"],["세르게이 프로코피예프","근현대","prokofiev"],["조지 거슈윈","근현대","gershwin"],["드미트리 쇼스타코비치","근현대","shostakovich"],["새뮤얼 바버","근현대","barber"]],"AMBIG":{"레퀴엠 d단조":["brahms","verdi"],"자장가":["mozart","schubert"],"죽음의 무도":["liszt"],"아베 마리아(엘렌의 노래 3번)":["bach","gounod"],"전주곡(레 프렐뤼드)":["chopin","debussy","rachmaninoff"],"꿈":["schumann"],"백조(동물의 사육제 중)":["tchaikovsky"]},"P":{"G선상의 아리아":["Wiki naxos 8.550194 01 13.ogg"],"브란덴부르크 협주곡":["ia:Bach__J.S._-_Brandenburg_Concerto_No_2_in_F_Major__BWV_1047_mvmt_/Bach__J.S._-_Brandenburg_Concerto_No_2_in_F_Major__BWV_1047_mvmt.ogg","Bach Brandenburg 4 coda to the 3rd movement.wav"],"골트베르크 변주곡":["ia:MusopenCollectionAsFlac/Bach_GoldbergVariations/JohannSebastianBach-01-GoldbergVariationsBwv.988-Aria.mp3","ia:BachGoldbergVariations/GoldbergVariations.ogg"],"메시아":["Handel Messiah Hallelujah by Oratorio Chorus.ogg"],"수상 음악":["Handel's Water Music - 14. Lentement - Chamber Orchestra - United States Marine Band.opus"],"왕궁의 불꽃놀이 음악":["ia:HandelMusicForTheRoyalFireworks2011/09TheRejoicing.ogg","Paul Ayres - Handel's Music for the Royal Fireworks, HWV 351 - IV. La Réjouissance.ogg"],"캐논 D장조":["Kevin MacLeod - Canon in D Major.ogg","Pachelbel's Canon.ogg"],"교향곡 94번 '놀람'":["Haydn; Symphony No. 94 \"Surprise\", 2. Andante.ogg","Haydn; Symphony No. 94 \"Surprise\", 4. Finale (Allegro molto).ogg"],"아이네 클라이네 나흐트무지크":["ia:mozart-kv-525-string-serenade-no.-13-eine-kleine-nachtmusik/Mozart - KV 525 - String Serenade No. 13 Eine Kleine Nachtmusik.flac","ia:MozartEineKleineNachtmusik_102/MozartALittleNightMusic.ogg"],"마술피리":["ia:MusopenCollectionAsFlac/Mozart_MagicFluteOverture/WolfgangAmadeusMozart-MagicFluteOverture.mp3","W. A. Mozart - Die Zauberflöte - 18. Der Hölle Rache kocht in meinem Herzen (Ferenc Fricsay, 1953).ogg"],"피가로의 결혼":["ia:MusopenCollectionAsFlac/Mozart_MarriageOfFigaro/WolfgangAmadeusMozart-MarriageOfFigaro.mp3","Mozart, The Marriage of Figaro (overture).ogg"],"교향곡 40번 g단조":["ia:MusopenCollectionAsFlac/Mozart_SymphonyNo.40inGMinor/WolfgangAmadeusMozart-SymphonyNo.40InGMinorK.550-01-MoltoAllegro.mp3","Mozart - Symphony No. 40 in G minor, K550 - I. Molto allegro (Musopen Symphony).flac"],"교향곡 9번 '합창'":["PMLP01607-Symphony No.9, Op.125 (Beethoven, Ludwig van), IV Presto.ogg"],"피아노 소나타 14번 '월광'":["ia:BeethovenPianoSonataNo.14moonlight/BeethovenPianoSonata14.ogg"],"교향곡 6번 '전원'":["Ludwig van Beethoven - symphony no. 6 in f major 'pastoral', op. 68 - iii. allegro.ogg","Ludwig van Beethoven - symphony no. 6 in f major 'pastoral', op. 68 - i. allegro non troppo.ogg"],"피아노 소나타 8번 '비창'":["Beethoven, Sonata No. 8 in C Minor Pathetique, Op. 13 - III. Rondo - Allegro.ogg"],"교향곡 3번 '영웅'":["ia:MusopenCollectionAsFlac/Beethoven_SymphonyNo.3Eroica/LudwigVanBeethoven-SymphonyNo.3InEFlatMajorEroicaOp.55-01-AllegroConBrio.mp3","Beethoven - Symphony No. 3 in E flat major, Op. 55 'Eroica' - III. Scherzo. Allegro vivace (Musopen Symphony).flac"],"아베 마리아(엘렌의 노래 3번)":["Franz Schubert - Ellens dritter Gesang.oga"],"교향곡 8번 '미완성'":["ia:schubert-8-i-blomstedt-leipzig-2021_202611/schubert 8-i (blomstedt-leipzig 2021).mp3","ia:SchubertSymphonyNo.8unfinished_347/01_schubertNo.8M1.ogg"],"한여름 밤의 꿈 서곡":["A Midsummer Night's Dream Op. 61 Overture (Mendelssohn) European Archive.ogg"],"결혼 행진곡(한여름 밤의 꿈 중)":["A Midsummer Night's Dream Op. 61 Wedding March (Mendelssohn) European Archive.ogg"],"녹턴 Op.9-2":["ia:musopen-chopin/Nocturne Op. 9 no. 2 in E flat major.mp3"],"즉흥 환상곡":["ia:musopen-chopin/Fantasie Impromptu Op. 66.mp3"],"영웅 폴로네즈":["ia:musopen-chopin/PolonaiseOp.53InAFlatMajorheroic.mp3","ia:FredericChopinPolonaiseNo.6InAFlatMajorOp.53/FredericChopinPolonaiseNo.6InAFlatMajorOp.53.ogg"],"혁명 에튀드":["Chopin - 12 Études, Op. 10 - No. 12 in C minor 'Revolutionary' (Edward Neeman).flac"],"강아지 왈츠":["ia:musopen-chopin/Waltz Op. 64 no. 1 in D flat major.mp3"],"헝가리 광시곡 2번":["Jaan Patterson - 01 - Hungarian Rhapsody No2 S2442 Franz Liszt.ogg"],"아이다":["Triumphal March from Aida.ogg","Aida-Trompeten.ogg"],"몰다우":["ia:MusopenCollectionAsFlac/Smetana_Vltava/BedichSmetana-MVlast-Vltava.mp3","Smetana, Má vlast - Vltava - The Moldau.ogg"],"카르멘":["Bizet - Carmen - Toreador Song (French, Musopen).ogg"],"전람회의 그림":["ia:modest-mussorgsky-pictures-at-an-exhibition-promenade/Modest_Mussorgsky_-_pictures_at_an_exhibition_-_promenade_-_allegro_giusto,_nel_modo_russico_senza_allegrezza,_ma.ogg","Modest Mussorgsky - pictures at an exhibition - promenade - allegro giusto, nel modo russico senza allegrezza, ma.ogg"],"백조의 호수":["Tchaikovsky - Swan Lake Op.20 - Act II Concl.ogg","Tchaikovsky - Swan Lake Op.20 - Act III Concl, Allegro.ogg"],"교향곡 6번 '비창'":["Tchaikovsky, Theme from Symphony No. 6 In B Minor, Op. 74, 'Pathetique' - I. Adagio, Allegro Non Troppo.ogg","Tchaikovsky, Symphony No. 6 in B minor, Op. 74, 'Pathetique' - II. Allegro con gracia.ogg"],"교향곡 9번 '신세계로부터'":["Antonin Dvorak - symphony no. 9 in e minor 'from the new world', op. 95 - iii. molto vivace.ogg","ia:DvorakSymphonyNo.9/04_dvorakSym9Mvmt4.ogg"],"왕벌의 비행":["Rimsky-Korsakov - flight of the bumblebee.oga"],"셰에라자드":["Rimsky-Korsakov. Scheherazade, Symphonic Suite, Op. 35 - 01 The Sea And Sinbads Ship.ogg","Rimsky-Korsakov. Scheherazade, Symphonic Suite, Op. 35 - 02 The Story Of The Kalandar Prince.ogg"],"페르 귄트":["ia:MusopenCollectionAsFlac/Greig_PeerGynt/EdvardGrieg-PeerGyntSuiteNo.1Op.46-04-InTheHallOfTheMountainKing.mp3","Grieg - Peer Gynt Suite No. 1, Op. 46 - II. The Death of Aase (Musopen Symphony).flac"],"아침(페르 귄트 중)":["ia:MusopenCollectionAsFlac/Greig_PeerGynt/EdvardGrieg-PeerGyntSuiteNo.1Op.46-01-Morning.mp3","Henrik Ibsen, Edvard Grieg - Morgenstemning (Morning Mood).ogg"],"피아노 협주곡 a단조":["ia:GriegPianoConcertoMvt1/Grieg_Piano_Concerto_mvt1.ogg","Edvard Grieg - piano concerto in a minor, op. 16 - iii. allegro moderato molto.ogg"],"위풍당당 행진곡":["ELGAR Pomp and Circumstance in D, Opus 39, No. 1 - United States Marine Band.mp3"],"차라투스트라는 이렇게 말했다":["Also Sprach Zarathustra - Einleitung.ogg","Richard Strauss - Also Sprach Zarathustra.ogg"],"짐노페디":["Satie Gymnopèdie n.1 DariaBaiocchi.wav","Gymnopedie No. 1 (ISRC USUAN1100787).mp3"],"그노시엔":["Jaan Patterson - 05 - Gnossiennes No1 ric Alfred Leslie Satie.ogg"],"행성":["Holst The Planets Jupiter.ogg"],"피아노 협주곡 2번 c단조":["ia:RachmaninoffPianoConcertoNo.2/01_Moderato.mp3","Sergei Rachmaninoff - piano concerto no. 2 in c minor, op. 18 - ii. adagio sostenuto.ogg"],"볼레로":["Bolero-Maurice Ravel-ORTF National Orchestra-Georges Tzipine-23 March 1965.ogg","Bolero-Maurice Ravel-Paris Orchestra-Charles Munch-1956.ogg"],"죽은 왕녀를 위한 파반느":["Maurice Ravel - Pavane pour une infante défunte.ogg"],"랩소디 인 블루":["US Marine Band Rhapsody in Blue.oga"],"빗방울 전주곡":["ia:musopen-chopin/Prelude Op. 28 no. 15.mp3"],"교향곡 5번 '운명'":["Ludwig van Beethoven - symphony no. 5 in c minor, op. 67 - i. allegro con brio.ogg","Ludwig van Beethoven - symphony no. 5 in c minor, op. 67 - ii. andante con moto.ogg"],"라 트라비아타":["ICBSA Verdi - La traviata, Sempre libera.ogg","ICBSA Verdi - La traviata, Preludio parte 1.ogg"],"전주곡 c♯단조":["Prélude en Do dièse mineur de Rachmaninov op. 3 (Morceaux de fantaisie).ogg"],"토카타와 푸가 d단조":["Bach, Toccata und Fuge d-moll BWV 565, Norbert Schenk.mp3","Toccata et Fugue BWV565.ogg"],"사계":["Vivaldi - Four Seasons 1 Spring mvt 1 Allegro - John Harrison violin.oga","Vivaldi - Four Seasons 4 Winter Air Force Strings - United States Air Force Band.mp3"],"터키 행진곡(피아노 소나타 11번 중)":["Mozart - Piano Sonata No. 11 in A major - III. Allegro (Turkish March).ogg"],"엘리제를 위하여":["FurElise.ogg","Fur Elise.ogg"],"마왕":["Schubert's Erlkönig, D.328 - Michael Jackson.ogg"],"윌리엄 텔 서곡":["Guillaume Tell - Overture - (Rossini, Gioacchino) by Fritz Reiner (conductor).mp3","Gioachino Rossini, William Tell Overture (military band version, 2000).ogg"],"바이올린 협주곡 e단조":["Hankyung Arte Philharmonic - Mendelssohn's Violin Concerto in E minor, Op. 64, MWV O 14 - I. Allegro molto appassionato.ogg","Hankyung Arte Philharmonic - Mendelssohn's Violin Concerto in E minor, Op. 64, MWV O 14 - III. Allegretto non troppo-Allegro molto vivace.ogg"],"발퀴레의 기행":["Ride of the Valkyries.ogg"],"아름답고 푸른 도나우":["Strauss, An der schönen blauen Donau.ogg","\"An der schönen, blauen Donau\", performed by the US Marine Band.mp3"],"백조(동물의 사육제 중)":["Camille Saint-Saëns - Le Cygne (No. 13) - Matilda Colliard and Stefano Ligoratti.ogg","20091104 Alisa Weilerstein and Jason Yoder - Saint Saëns' The Swan.ogg"],"헝가리 무곡 5번":["Ungarischer Tanz Nr. 5 in fis-Moll, Klavier zu 4 Händen.oga"],"호두까기 인형":["Tchaikovsky - Dance of the Sugar Plum Fairy - The Nutcracker.ogg","Tchaikovsky - Nutcracker Suite - Russian Dance - Philip Milman - Lud and Schlatts Musical Emporium.wav"],"피아노 협주곡 1번 b♭단조":["Tchaikovsky, Concerto No.1 in B-flat minor Op.23, I. Allegro.ogg"],"유모레스크":["Dvořák - Humoresque Op. 101 No. 7.ogg"],"슬라브 무곡":["Slavonic Dance No. 2 - Strolling Strings - United States Air Force Band.mp3"],"사랑의 인사":["Edward Elgar - Salut d'amour, Op. 12 - Emanuel Salvador and Pau Casan (2011).ogg"],"달빛(베르가마스크 모음곡 중)":["Clair de lune (Claude Debussy) Suite bergamasque.ogg"],"아라베스크 1번":["Claude Debussy - Première Arabesque - Patrizia Prati.ogg"]},"O":{"Guillaume Tell - Overture - (Rossini, Gioacchino) by Fritz Reiner (conductor).mp3":515,"PMLP01607-Symphony No.9, Op.125 (Beethoven, Ludwig van), IV Presto.ogg":400}};   // W: {곡: [작곡가, 연도, 갈래, 시대, 유명도, 나라, 작곡가id]}, C: [[작곡가, 시대, id]], AMBIG, P: {곡: [음질 선별을 통과한 커먼즈 파일 이름들]}
  var AS = "classic-autosave-v1", LM = "classic-limit-v1", BADK = "classic-badaudio-v1", FS = "classic-fullsave-v1", MK = "classic-listen-mode-v1", WK = "classic-wrong-v1", SAVED = "classic-saved-v1", CACHE = "fg-classic-saved-v1", KEEP = 900000, FULLMAX = 40000000, LIMIT = [15, 30, 60].indexOf(+lsGet2("classic-limit-v1")) >= 0 ? +lsGet2("classic-limit-v1") : 30;
  function lsGet2(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  var mode = "off", saved = null;   // mode: off | mix | only
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var shuffle = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i], a2 = a[j]; a[i] = a2; a[j] = t; } return a; };
  var CONSENT = "🌐 온라인 듣기를 켜요.\n\n· 인터넷에서 저작권이 끝난(공개 도메인·CC0) 클래식 녹음만 찾아서 들려줘요.\n· 찾고 들을 때 이 기기의 인터넷 주소가 위키미디어 또는 인터넷 아카이브 서버에 전달돼요(이 앱은 개인 정보를 보내지 않아요).\n· 들은 곡의 앞부분(약 1MB 이하)은 이 폰에 저장해서, 다음부터는 인터넷 없이도 들을 수 있어요(설정에서 지울 수 있어요).\n· 조건에 맞는 녹음이 없으면 그 곡은 글로만 나와요.\n\n켤까요?";
  var online = function () { return !!window.fgOnline && fgOnline.enabled && fgOnline.on() && navigator.onLine !== false; };
  var badList = function () { try { var a = JSON.parse(lsGet(BADK) || "[]"); return Array.isArray(a) ? a : []; } catch (e) { return []; } };
  var isBad = function (name) { return badList().indexOf(name) >= 0; };
  var savedCount = function () { return saved ? Object.keys(saved).length : 0; };
  var credit = function (e) { return '🎧 음원: <a href="' + esc(e.page) + '" target="_blank" rel="noopener noreferrer">' + esc(e.label || '위키미디어 커먼즈') + ' 「' + esc(e.title) + "」</a>" + (e.artist && !/no machine-readable/i.test(e.artist) ? " · 녹음: " + esc(e.artist) : "") + " (" + (e.licenseUrl ? '<a href="' + esc(e.licenseUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(e.license) + "</a>" : esc(e.license)) + ")"; };
  var inCache = function (cb) { return "caches" in window ? caches.open(CACHE).then(cb).catch(function () { return null; }) : Promise.resolve(null); };

  // ── 음원 하나 얻기: ① 폰에 저장된 것 → ② 온라인에서 찾기 (통과하면 {src, page, title, license, kind}, 아니면 null)
  var blobUrls = {};
  function fromSaved(t) {
    var e = saved && saved[t]; if (!e || isBad(e.title)) return Promise.resolve(null);
    if (blobUrls[t]) return Promise.resolve({ src: blobUrls[t], page: e.page, title: e.title, license: e.license, kind: "saved", label: e.label, artist: e.artist, licenseUrl: e.licenseUrl, remote: e.src });
    return inCache(function (c) { return c.match(e.src); }).then(function (r) { return r ? r.blob() : null; }).then(function (b) {
      if (!b) return null; blobUrls[t] = URL.createObjectURL(b); return { src: blobUrls[t], page: e.page, title: e.title, license: e.license, kind: "saved", label: e.label, artist: e.artist, licenseUrl: e.licenseUrl, remote: e.src };
    }).catch(function () { return null; });
  }
  // 소리가 실제로 나올 수 있는지 잠깐 확인(메타데이터만 받아 봐요). 9초 안에 안 되면 다음 후보(다른 서버)로 넘어가요
  function playable(src) {
    return new Promise(function (ok) {
      var a = new Audio(), done = false, t = setTimeout(function () { f(false); }, 9000);
      function f(v) { if (done) return; done = true; clearTimeout(t); try { a.removeAttribute("src"); a.load(); } catch (e) {} ok(v); }
      a.preload = "metadata"; a.addEventListener("loadedmetadata", function () { f(true); }); a.addEventListener("error", function () { f(false); }); a.src = src;
    });
  }
  function fromOnline(t) {
    var names = DATA.P[t]; if (!names || !online()) return Promise.resolve(null);
    return fgOnline.audioFiles(names, 80000000, true).then(function (list) {
      list = (list || []).filter(function (x) { return !isBad(x.title); }); var k = 0;
      function next() {
        if (k >= list.length) return null; var r = list[k++];
        return playable(r.src).then(function (okp) { return okp ? r : next(); });
      }
      return next().then(function (r) { r = r || list[0]; return r ? { src: r.src, page: r.page, title: r.title, license: r.license, label: r.label, artist: r.artist, licenseUrl: r.licenseUrl, size: r.size, kind: "online", remote: r.src } : null; });
    });
  }
  function getAudio(t) { return fromSaved(t).then(function (r) { return r || fromOnline(t); }); }
  var hasAudioCandidate = function (t) { return !!DATA.P[t] && (!!(saved && saved[t]) || online()); };
  var candidates = function () { return Object.keys(DATA.W).filter(hasAudioCandidate); };

  // 처음 들을 때 앞부분만 폰에 저장(mp3·ogg 계열은 앞 900KB, 작은 파일은 통째로, 큰 wav·flac 은 저장하지 않고 들을 때마다 불러와요)
  function saveOne(t, r) {
    if (lsGet(AS) !== "1" || r.kind !== "online" || (saved && saved[t]) || !("caches" in window)) return;
    if (DATA.O && DATA.O[r.title]) return;   // 곡 중간부터 듣는 녹음은 앞부분만 저장하면 들을 부분이 없어서 저장하지 않아요   // 저장은 사용자가 고른 경우에만
    storeOne(t, r);
  }
  function storeOne(t, r) {   // 저장에 성공하면 true(약속), 저장할 수 없는 파일이면 false
    var ext = (r.title.match(/\.(\w+)$/) || [, ""])[1].toLowerCase(), full = lsGet(FS) === "1" && r.size && r.size <= FULLMAX, small = full || (r.size && r.size <= 2000000), lossy = /^(ogg|oga|opus|mp3)$/.test(ext);
    if (!small && !lossy) return Promise.resolve(false);
    return fetch(r.src, { credentials: "omit", referrerPolicy: "no-referrer", headers: small ? {} : { Range: "bytes=0-" + (KEEP - 1) } }).then(function (resp) {
      if (!resp.ok) throw 0; return resp.blob().then(function (b) { return { b: b, type: resp.headers.get("content-type") || "audio/ogg" }; });
    }).then(function (x) {
      if (!x.b.size || x.b.size < 20000) throw 0;
      return inCache(function (c) { return c.put(r.src, new Response(x.b, { status: 200, headers: { "Content-Type": x.type } })); }).then(function () {
        saved = saved || {}; saved[t] = { src: r.src, page: r.page, title: r.title, license: r.license, label: r.label, artist: r.artist, licenseUrl: r.licenseUrl }; lsSet(SAVED, JSON.stringify(saved)); if (bar && !dl.running) drawBar(); return true;
      });
    }).catch(function (e) { if (e && e.name === "QuotaExceededError") dl.full = true; return false; });
  }

  // ── 📥 모든 곡 저장하기(그림의 '📥 그림 저장하기'와 같은 방식, 2026-11-24 사용자 요청): 듣기 가능한 곡을 한 번에 이 폰에 저장해요.
  //    저장하는 범위는 '전곡 저장' 설정을 따라요(꺼짐 = 곡마다 앞부분 약 0.9MB). 검증(공개 도메인·CC0 표시)을 통과한 녹음만 저장해요.
  var dl = { running: false, cancel: false, msg: "", full: false };
  function pmap(items, fn, limit) { var k = 0; function w() { if (k >= items.length) return Promise.resolve(); var it = items[k++]; return Promise.resolve(fn(it)).then(w); } var ws = []; for (var i = 0; i < Math.min(limit, items.length); i++) ws.push(w()); return Promise.all(ws); }
  function saveAll() {
    if (dl.running) { dl.cancel = true; dl.msg = "멈추는 중…"; drawBar(); return; }
    if (!(window.fgOnline && fgOnline.ask(CONSENT)) || !("caches" in window)) return;
    if (navigator.onLine === false) { dl.msg = "지금은 인터넷이 없어서 저장할 수 없어요."; drawBar(); return; }
    var todo = Object.keys(DATA.P).filter(function (t) { return !(saved && saved[t]); });
    if (!todo.length) { dl.msg = "저장할 곡이 없어요(모두 저장됨)."; drawBar(); return; }
    var full = lsGet(FS) === "1", mb = full ? "수백 MB까지(곡 전체)" : "약 " + Math.round(todo.length * 0.9) + "MB(곡마다 앞부분)";
    try { if (!window.confirm("음원 " + todo.length + "곡, " + mb + "을 이 폰에 저장해요. 와이파이에서 몇 분 걸릴 수 있어요.\n저작권이 끝난 녹음만 저장하고, 찾지 못한 곡은 건너뛰어요.\n\n저장할까요?")) return; } catch (e) {}
    var okc = 0, bad = 0; dl.running = true; dl.cancel = false; dl.full = false; drawBar();
    pmap(todo, function (t) {
      if (dl.cancel || dl.full) return null;
      return fromOnline(t).then(function (r) { return r ? storeOne(t, r) : false; }).catch(function () { return false; }).then(function (ok) {
        if (ok) okc++; else bad++;
        dl.msg = "저장 중… " + (okc + bad) + "/" + todo.length + " (저장 " + okc + "곡, 건너뜀 " + bad + ")"; drawBar();
      });
    }, 2).then(function () {
      dl.running = false;
      dl.msg = (dl.cancel ? "멈췄어요. " : dl.full ? "폰 저장 공간이 모자라 멈췄어요. " : "끝났어요. ") + "저장 " + okc + "곡" + (bad ? ", 건너뜀 " + bad + "곡(검증을 통과한 녹음을 찾지 못했거나 불러오지 못한 곡)" : "") + ".";
      dl.cancel = false; drawBar();
    });
  }
  function clearSaved() {
    try { if (!window.confirm("이 폰에 저장한 음원 " + savedCount() + "곡을 지울까요? (다시 들으면 또 저장돼요)")) return; } catch (e) {}
    try { if ("caches" in window) caches.delete(CACHE); } catch (e) {}
    try { localStorage.removeItem(SAVED); } catch (e) {} saved = null; blobUrls = {}; stopAudio(); if (bar) drawBar();
  }

  // ── 소리 재생(한 번에 하나, 앞 LIMIT초만)
  var cur = null;
  function stopAudio() { if (cur) { try { cur.pause(); } catch (e) {} } }
  function player(r, lim) {
    stopAudio(); var a = new Audio(r.src); a.preload = "auto"; a._lim = lim === undefined ? LIMIT : lim; cur = a;
    var st = (DATA.O && DATA.O[r.title]) || 0; a._st = st;   // 곡다운 부분부터(긴 악장 녹음)
    if (st) a.addEventListener("loadedmetadata", function () { if (a.currentTime < st) try { a.currentTime = st; } catch (e) {} }, { once: true });
    a.addEventListener("timeupdate", function () { if (a.currentTime - a._st >= a._lim) { a.pause(); a.dispatchEvent(new Event("ended")); } });
    return a;
  }

  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}.amode button.sm{padding:6px 10px;font-size:.85rem}" +
      ".amode small{color:var(--muted,#666)}.aplay{display:flex;flex-direction:column;align-items:center;gap:6px;margin:0 0 10px}.aplay button{border:0;border-radius:999px;background:var(--accent,#c4552b);color:var(--accent-fg,#fff);font-size:1.15rem;font-weight:700;padding:14px 26px;min-width:200px}" +
      ".aplay small{color:var(--muted,#666)}.acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".row2{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}.ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}" +
      ".cbtn,.gplay{margin-left:6px;border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:2px 10px;font-size:.8rem}a.cbtn{display:inline-block;text-decoration:none}.ytrow{margin-top:8px;font-weight:400;font-family:var(--font-body,inherit);display:flex;gap:6px;align-items:center;flex-wrap:wrap}.ytrow small{color:var(--muted,#666);font-size:.8rem}.ytrow .cbtn{margin-left:0}.gplay.on,.cbtn.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent}";
    document.head.appendChild(st);
  }
  function askSave() {
    if (lsGet(AS) !== null || !(window.fgOnline && fgOnline.on())) return; var yes = false;
    try { yes = window.confirm("📥 들은 곡의 앞부분(약 1MB 이하)을 이 폰에 저장할까요?\n\n· 저장하면 다음부터 인터넷 없이도 들을 수 있어요.\n· 저장하지 않으면 들을 때마다 인터넷이 필요해요.\n· 나중에 언제든 바꾸거나 지울 수 있어요.\n\n[확인] 저장해요   [취소] 저장하지 않고 듣기만 해요"); } catch (e) {}
    lsSet(AS, yes ? "1" : "0");
  }
  var bar;
  function drawBar() {
    var n = savedCount(), on = online(), can = on || n > 0;
    var h = '<b>🎧 듣고 맞히기</b><div class="row">' +
      '<button type="button" data-m="off" class="' + (mode === "off" ? "on" : "") + '">📴 글로만</button>' +
      '<button type="button" data-m="mix" class="' + (mode === "mix" ? "on" : "") + '">🔀 섞어서(한 판 최대 3개)</button>' +
      '<button type="button" data-m="only" class="' + (mode === "only" ? "on" : "") + '">🎧 듣기 문제만</button></div>';
    h += "<small>" + (mode === "off" ? "듣기 문제를 풀려면 아래에서 골라요. 처음 한 번은 인터넷이 필요하고, 들은 곡은 이 폰에 저장돼서 다음부터는 인터넷 없이도 들려요." :
      (on ? "인터넷에서 저작권이 끝난 녹음을 찾아 들려줘요(위키미디어·인터넷 아카이브 서버에 이 기기의 주소가 전달돼요). 선택한 시간(" + LIMIT + "초) 동안 들려요." : (n ? "지금은 인터넷이 없어서 이 폰에 저장된 음원(" + n + "곡)만 나와요." : "지금은 인터넷이 없고 저장된 음원도 없어서 글로만 나와요."))) + " · 저장된 음원 " + n + " / 듣기 가능 " + Object.keys(DATA.P).length + "곡 · <a href=\"offline-media.html\">📊 저장 현황</a></small>";
    h += '<div class="row"><small>듣기 시간:</small>' + [15, 30, 60].map(function (s) { return '<button type="button" class="sm' + (LIMIT === s ? " on" : "") + '" data-m="lim" data-s="' + s + '">' + s + "초</button>"; }).join("") + "<small>(모음 화면과 정답 뒤에는 끝까지 들어요)</small></div>";
    h += '<div class="row"><button type="button" class="sm" data-m="fullsave">📦 전곡 저장: ' + (lsGet(FS) === "1" ? "켜짐" : "꺼짐") + "</button><small>켜면 곡 전체를 저장해요(한 곡 수 MB~수십 MB, 와이파이 권장). 끄면 앞부분만 저장해요.</small></div>";
    h += '<div class="row"><button type="button" class="sm" data-m="auto">💾 들은 곡 자동 저장: ' + (lsGet(AS) === "1" ? "켜짐" : "꺼짐") + "</button>" + (n && !dl.running ? '<button type="button" class="sm" data-m="clear">🗑️ 저장한 음원 지우기</button>' : "") + "</div>";
    if (window.fgOnline && fgOnline.enabled) {
      var left = Object.keys(DATA.P).length - n;
      h += '<div class="row">' + ("caches" in window ? '<button type="button" class="sm" data-m="saveall"' + (!dl.running && !left ? " disabled" : "") + ">" + (dl.running ? "⏹ 멈추기" : !left ? "✅ 모두 저장됨" : n ? "📥 남은 곡 저장하기 (" + left + "곡)" : "📥 모든 곡 저장하기(오프라인용)") + "</button>" : "") +
        "<small>" + esc(dl.msg || "한 번에 저장해 두면 인터넷 없이도 듣기 문제를 풀 수 있어요.") + "</small></div>";
    }
    if (isQuiz && wrongList.length && mode !== "off") h += '<div class="row"><button type="button" class="sm" id="clsreview" data-m="review">' + reviewLabel() + "</button><small>틀린 곡만 다시 들어요.</small></div>";
    bar.innerHTML = h;
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "clsmode";
    var hh = document.querySelector("h1"); if (hh) hh.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return; var m = b.dataset.m;
      if (m === "review") startReview(); else if (m === "saveall") saveAll(); else if (m === "clear") clearSaved(); else if (m === "auto") { lsSet(AS, lsGet(AS) === "1" ? "0" : "1"); drawBar(); }
      else if (m === "lim") { LIMIT = +b.dataset.s; lsSet(LM, String(LIMIT)); drawBar(); }
      else if (m === "fullsave") { if (lsGet(FS) === "1") lsSet(FS, "0"); else { var ok = false; try { ok = window.confirm("📦 곡 전체를 이 폰에 저장할까요?\n\n· 한 곡이 수 MB~수십 MB(길게는 80MB)까지 있어요. 폰 저장 공간과 데이터를 많이 써요.\n· 와이파이에서 쓰는 걸 권해요.\n· 이미 저장한 앞부분은 그대로 두고, 앞으로 저장하는 곡부터 전체를 저장해요.\n· 언제든 끄거나 '저장한 음원 지우기'로 지울 수 있어요."); } catch (x) {} if (ok) lsSet(FS, "1"); } drawBar(); }
      else {
        if (m !== "off" && !online() && !savedCount()) { try { window.alert("지금은 인터넷이 없어요. 인터넷이 켜진 곳에서 한 번 들어 보면 이 폰에 저장돼요."); } catch (x) {} }
        if (m !== "off" && window.fgOnline && !fgOnline.on() && !fgOnline.ask(CONSENT) && !savedCount()) return;
        askSave(); mode = m; lsSet(MK, mode); drawBar(); stopAudio(); start();
      }
    });
    drawBar();
  }

  // ── 문제 만들기: 곡 → 작곡가 또는 곡 → 제목
  function wrongComposers(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []), mine = w[6], era = w[3], lvl = w[4];
    var pool = DATA.C.filter(function (c) { return c[2] !== mine && ban.indexOf(c[2]) < 0; });
    var same = shuffle(pool.filter(function (c) { return c[1] === era; })), diff = shuffle(pool.filter(function (c) { return c[1] !== era; }));
    var n = lvl === 1 ? 0 : lvl === 2 ? 1 : 2, out = same.slice(0, n); diff.concat(same.slice(n)).forEach(function (c) { if (out.length < 3 && out.indexOf(c) < 0) out.push(c); });
    return out.slice(0, 3).map(function (c) { return c[0]; });
  }
  function wrongTitles(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []);
    return shuffle(Object.keys(DATA.W).filter(function (x) { var v = DATA.W[x]; return x !== t && v[6] !== w[6] && ban.indexOf(v[6]) < 0 && v[4] <= 2 && (DATA.AMBIG[x] || []).indexOf(w[6]) < 0; })).slice(0, 3);
  }
  // 오답 노트(wrong-hook.js)용: 소리 문제는 글만으로도 풀 수 있는 문제로 바꿔 기록하고, 소리 듣기 정보(m)도 함께 남겨요
  window.fgWrongText = function () {
    var c = typeof qs !== "undefined" && qs && qs[i]; if (!c || !c.d.aud) return null; var w = DATA.W[c.d.tt];
    return c.d.kind === "t" ? "🎧 소리 문제 — " + w[0] + "(" + w[5] + ")의 " + w[2] + ", " + w[1] + "에 만들었어요. 이 곡의 제목은 무엇일까요?" : "🎧 소리 문제 — ‘" + c.d.tt + "’의 작곡가는 누구일까요?";
  };
  window.fgWrongMedia = function () { var c = typeof qs !== "undefined" && qs && qs[i]; return c && c.d.aud ? { k: "c", t: c.d.tt } : null; };
  function mkItem(t, kind, r) {
    var w = DATA.W[t], d;
    if (kind === "t") d = ["이 곡의 제목은 무엇일까요?", t, wrongTitles(t), w[3], w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    else d = ["이 곡의 작곡가는 누구일까요?", w[0], wrongComposers(t), w[3], "‘" + t + "’ — " + w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    d.tt = t; d.aud = r; d.kind = kind; return d;
  }
  function pmap(items, fn, limit) { var out = new Array(items.length), k = 0; function w() { if (k >= items.length) return Promise.resolve(); var n = k++; return Promise.resolve(fn(items[n], n)).then(function (r) { out[n] = r; return w(); }); } var ws = []; for (var q = 0; q < Math.min(limit, items.length); q++) ws.push(w()); return Promise.all(ws).then(function () { return out; }); }
  var roundId = 0;
  function mix() {
    var id = ++roundId, want = mode === "only" ? 10 : 3, first = i === 0 && !locked;
    var pool = shuffle(candidates().filter(function (t) { var w = DATA.W[t]; return (!lv || w[4] === lv) && (cat === "전체" || w[3] === cat); })).slice(0, want + (mode === "only" ? 8 : 3));
    if (!pool.length) return;
    pmap(pool, function (t) { return getAudio(t).then(function (r) { return r ? { t: t, r: r } : null; }); }, 2).then(function (all) {
      var ok = all.filter(Boolean); if (id !== roundId || !ok.length || !qs || qs.length < 2) return;
      var slots = []; for (var k = first ? 0 : i + 1; k < qs.length; k++) slots.push(k);
      slots = (first ? [0].concat(shuffle(slots.slice(1))) : shuffle(slots)).slice(0, Math.min(want, ok.length));
      slots.forEach(function (pos, n) { var d = mkItem(ok[n].t, Math.random() < 0.5 ? "t" : "c", ok[n].r); qs[pos] = { d: d, opts: options(d) }; });
      if (first && slots.indexOf(0) >= 0) show();
    });
  }
  var hintUsed = false;
  function decorateQ() {
    var c = qs && qs[i]; stopAudio(); hintUsed = false; if (!c || !c.d.aud) return;
    var q = document.getElementById("q"), box = document.createElement("div"), r = c.d.aud; box.className = "aplay";
    box.innerHTML = '<button type="button">▶ 소리 듣기</button><small>눌러서 듣고, 몇 번이든 다시 들을 수 있어요(' + LIMIT + "초, 정답을 고르면 끝까지 들을 수 있어요).</small>";
    var btn = box.querySelector("button"), a = null;
    function bind() {
      a = player(r); a.addEventListener("ended", function () { btn.textContent = "🔁 다시 듣기"; });
      a.addEventListener("error", function () { btn.textContent = "소리를 불러오지 못했어요"; btn.disabled = true; });
    }
    btn.addEventListener("click", function () {
      if (!a) { bind(); saveOne(c.d.tt, r); }
      if (!a.paused && !a.ended) { a.pause(); btn.textContent = "▶ 이어서 듣기"; return; }
      if (a.ended || a.currentTime >= a._lim) a.currentTime = 0; stopAudioExcept(a); var p = a.play(); if (p && p.catch) p.catch(function () { btn.textContent = "소리를 불러오지 못했어요"; }); btn.textContent = "⏸ 멈추기";
    });
    q.insertBefore(box, q.firstChild);
    var m = DATA.W[c.d.tt], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
    var hbtn = hb.querySelector("button"), out = hb.querySelector("div"), lvl = 0;
    hbtn.addEventListener("click", function () { if (locked) return; hintUsed = true; lvl++; out.hidden = false; out.textContent = lvl === 1 ? "시대: " + m[3] + (c.d.kind === "c" ? " · 갈래: " + m[2] : "") : "시대: " + m[3] + " · 갈래: " + m[2] + " · 작곡가의 나라: " + m[5]; if (lvl >= 2) hbtn.disabled = true; else hbtn.textContent = "💡 힌트 한 번 더"; });
    q.appendChild(hb);
  }
  function stopAudioExcept(a) { if (cur && cur !== a) { try { cur.pause(); } catch (e) {} } cur = a; }
  function addCard() {
    var c = qs && qs[i]; if (!c || !c.d.aud) return; var m = DATA.W[c.d.tt], q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><b>‘' + esc(c.d.tt) + "’</b><span>" + esc(m[0]) + " (" + esc(m[5]) + ")</span><span>" + esc(m[3]) + " · " + esc(m[2]) + " · " + esc(m[1]) + '</span></div><div class="row2"><button type="button" class="cbtn" id="clsfull">▶ 끝까지 듣기</button><button type="button" class="cbtn" id="clsbad">🔇 음질이 나빠요</button></div><small id="clsmsg" class="note"></small><span class="note">' + credit(c.d.aud) + "</span>");
    var fb = document.getElementById("clsfull"), bb = document.getElementById("clsbad"), msg = document.getElementById("clsmsg"), r = c.d.aud, remote = r.remote || r.src;
    fb.addEventListener("click", function () {
      if (cur && cur._full && !cur.paused) { cur.pause(); fb.textContent = "▶ 이어서 듣기"; return; }
      if (cur && cur._full && cur.paused && !cur.ended) { cur.play(); fb.textContent = "⏸ 멈추기"; return; }
      if (r.kind === "saved" && !online()) { msg.textContent = "저장된 건 앞부분만 있어요. 인터넷이 켜지면 끝까지 들을 수 있어요."; }
      var src = (r.kind === "saved" && !online()) ? r.src : remote; var a = player({ src: src }, Infinity); a._full = true; a.addEventListener("ended", function () { fb.textContent = "🔁 다시 듣기"; }); a.addEventListener("error", function () { msg.textContent = "끝까지 불러오지 못했어요. 잠시 뒤 다시 눌러 보세요."; fb.textContent = "▶ 끝까지 듣기"; });
      var p = a.play(); if (p && p.catch) p.catch(function () {}); fb.textContent = "⏸ 멈추기";
    });
    bb.addEventListener("click", function () {
      var a = badList(); if (a.indexOf(r.title) < 0) a.push(r.title); lsSet(BADK, JSON.stringify(a.slice(-100)));
      if (saved && saved[c.d.tt]) { delete saved[c.d.tt]; lsSet(SAVED, JSON.stringify(saved)); delete blobUrls[c.d.tt]; }
      bb.disabled = true; msg.textContent = "알려 줘서 고마워요. 이 녹음은 이제 쓰지 않고 다른 녹음으로 바꿔요(없으면 이 곡은 글로만 나와요)."; if (ytOk() && !document.getElementById("clsyt")) msg.insertAdjacentHTML("afterend", '<div class="row2" id="clsyt">' + ytLink(c.d.tt).replace("🎧 유튜브에서 듣기", "🎧 유튜브에서 좋은 연주로 듣기") + "</div>");
    });
  }
  // ── 틀린 곡 복습
  var wrongList = [];
  function loadWrong() { try { var a = JSON.parse(lsGet(WK) || "[]"); wrongList = Array.isArray(a) ? a.filter(function (t) { return DATA.W[t]; }) : []; } catch (e) { wrongList = []; } }
  var reviewLabel = function () { return "🔁 틀린 곡 복습 (" + wrongList.length + ")"; };
  function record(c, ok) {
    if (!c || !c.d.tt) return; var k = wrongList.indexOf(c.d.tt);
    if (ok) { if (k >= 0) wrongList.splice(k, 1); } else { if (k >= 0) wrongList.splice(k, 1); wrongList.push(c.d.tt); }
    lsSet(WK, JSON.stringify(wrongList.slice(-60))); var b = document.getElementById("clsreview"); if (b) b.textContent = reviewLabel();
  }
  function startReview() {
    var ts = shuffle(wrongList.filter(hasAudioCandidate)).slice(0, 10); if (!ts.length) return;
    start(); roundId++;
    pmap(ts, getAudio, 2).then(function (rs) {
      var items = []; ts.forEach(function (t, n) { if (rs[n]) { var d = mkItem(t, Math.random() < 0.5 ? "t" : "c", rs[n]); items.push({ d: d, opts: options(d) }); } });
      if (!items.length) return; qs = items; i = 0; score = 0; show();
    });
  }

  // ── 🎧 유튜브에서 듣기: 곡 이름으로 유튜브 검색 결과를 앱 밖(새 창·유튜브 앱)에서 열어요. 앱 안에서 재생하거나 소리를 받아 오지 않아요(유튜브 약관).
  //    정답을 고른 뒤에만 보여서 정답이 미리 드러나지 않아요. 온라인 기능을 끈 판(fgOnline.enabled=false)에서는 보이지 않아요.
  var ytOk = function () { return !!window.fgOnline && fgOnline.enabled; };
  var TITLES = Object.keys(DATA.W).sort(function (a, b) { return b.length - a.length; });
  function ytUrl(t) { var w = DATA.W[t], q = (w ? w[0] + " " : "") + String(t).replace(/[‘’'"“”]/g, ""); return "https://www.youtube.com/results?search_query=" + encodeURIComponent(q); }
  function ytLink(t) { return '<a class="cbtn yt" href="' + esc(ytUrl(t)) + '" target="_blank" rel="noopener noreferrer">🎧 유튜브에서 듣기</a>'; }
  function songOf(d) { if (!d) return null; if (d.tt && DATA.W[d.tt]) return d.tt; var s = [d[0], d[1], d[4]].join(" "); for (var k = 0; k < TITLES.length; k++) if (s.indexOf(TITLES[k]) >= 0) return TITLES[k]; return null; }
  function addYt() {
    if (!ytOk()) return; var c = qs && qs[i], t = c && songOf(c.d), q = document.getElementById("q"); if (!t || !q || q.querySelector(".yt")) return;
    q.insertAdjacentHTML("beforeend", '<div class="row2 ytrow">' + ytLink(t) + '<small>‘' + esc(t) + "’ 연주를 유튜브에서 찾아요(앱 밖에서 열려요)</small></div>");
  }

  // ── 모음: 곡 옆에 ▶ 듣기 단추(눌렀을 때 허락·검색·재생)
  function decorateGal() {
    var list = document.getElementById("list"); if (!list) return;
    list.querySelectorAll("li").forEach(function (li) {
      if (li.dataset.cls) return; li.dataset.cls = "1"; var b = li.querySelector("b"); if (!b) return;
      if (ytOk() && DATA.W[b.textContent]) b.insertAdjacentHTML("afterend", DATA.P[b.textContent] ? ytLink(b.textContent).replace("🎧 유튜브에서 듣기", "🎧 유튜브") : ytLink(b.textContent).replace("🎧 유튜브에서 듣기", "🎧 유튜브에서 듣기(앱 안 소리 없음)"));
      if (!DATA.P[b.textContent]) return;
      var btn = document.createElement("button"); btn.type = "button"; btn.className = "gplay"; btn.textContent = "▶ 듣기"; btn.dataset.t = b.textContent; b.insertAdjacentElement("afterend", btn);
    });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".gplay"); if (!b) return;
    var t = b.dataset.t, on = b.classList.contains("on"); document.querySelectorAll(".gplay.on").forEach(function (x) { x.classList.remove("on"); x.textContent = "▶ 듣기"; }); stopAudio();
    if (on) return;
    if (!(saved && saved[t]) && window.fgOnline && !fgOnline.on() && !fgOnline.ask(CONSENT)) return;
    askSave(); b.textContent = "⏳ 찾는 중…";
    getAudio(t).then(function (r) {
      if (!r) { b.textContent = "음원 없음"; b.disabled = true; if (ytOk() && !b.nextElementSibling?.classList?.contains("yt")) b.insertAdjacentHTML("afterend", ytLink(t).replace("🎧 유튜브에서 듣기", "🎧 유튜브에서 듣기")); return; }
      var a = player(r, Infinity); b.classList.add("on"); b.textContent = "⏹ 멈추기"; saveOne(t, r);
      a.addEventListener("ended", function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; });
      a.addEventListener("error", function () { b.classList.remove("on"); b.textContent = "불러오지 못함"; });
      var p = a.play(); if (p && p.catch) p.catch(function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; });
    });
  });

  function boot() {
    loadWrong();
    try { saved = JSON.parse(lsGet(SAVED) || "null"); if (!saved || typeof saved !== "object" || !Object.keys(saved).length) saved = null; } catch (e) { saved = null; }
    if (isQuiz) {
      buildBar();
      var oS = start, oShow = show, oPick = pick;
      start = function () { oS(); if (mode !== "off") mix(); };
      show = function () { oShow(); decorateQ(); };
      pick = function (k) { if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k); if (c && c.d.aud) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } record(c, ok); addCard(); } addYt(); };
      var m = lsGet(MK); if ((m === "mix" || m === "only") && (savedCount() || online())) { mode = m; drawBar(); start(); }
    } else if (isGal) {
      injectCss();
      new MutationObserver(decorateGal).observe(document.getElementById("list"), { childList: true }); decorateGal();
    }
  }
  addEventListener("online", function () { if (bar) drawBar(); }); addEventListener("offline", function () { if (bar) drawBar(); });
  addEventListener("pagehide", stopAudio);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
