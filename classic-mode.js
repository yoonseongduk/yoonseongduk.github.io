/* 클래식 듣고 맞히기 — 클래식 작곡가 퀴즈(classic-quiz.html)와 작곡가별 모음(classic-gallery.html) 공용.
   음원은 앱 안의 classic-audio/ (tools/dev/music_fetch.py 가 PC에서 위키미디어 커먼즈의 공개 도메인·CC0 녹음을 받아 20초 조각으로 잘라 둠)만 써요. 인터넷이 필요 없어요.
   이 파일은 tools/dev/set44.py 가 만들어요(직접 고치지 말고 tools/dev/classic_mode_tpl.js 와 set44.py 를 고치세요). */
(function () {
  "use strict";
  var DATA = {"W":{"토카타와 푸가 d단조":["요한 제바스티안 바흐","1700년대 초","오르간곡","바로크",1,"독일","bach"],"G선상의 아리아":["요한 제바스티안 바흐","1720년대경","관현악곡","바로크",1,"독일","bach"],"브란덴부르크 협주곡":["요한 제바스티안 바흐","1721","협주곡","바로크",2,"독일","bach"],"마태 수난곡":["요한 제바스티안 바흐","1727경","종교 음악","바로크",3,"독일","bach"],"골트베르크 변주곡":["요한 제바스티안 바흐","1741경","피아노 독주곡","바로크",3,"독일","bach"],"평균율 클라비어 곡집":["요한 제바스티안 바흐","1722","피아노 독주곡","바로크",3,"독일","bach"],"메시아":["게오르크 프리드리히 헨델","1741","종교 음악","바로크",1,"독일","handel"],"수상 음악":["게오르크 프리드리히 헨델","1717","관현악곡","바로크",2,"독일","handel"],"왕궁의 불꽃놀이 음악":["게오르크 프리드리히 헨델","1749","관현악곡","바로크",2,"독일","handel"],"울게 하소서":["게오르크 프리드리히 헨델","1711","오페라","바로크",2,"독일","handel"],"사계":["안토니오 비발디","1720년대","협주곡","바로크",1,"이탈리아","vivaldi"],"조화의 영감":["안토니오 비발디","1711","협주곡","바로크",3,"이탈리아","vivaldi"],"캐논 D장조":["요한 파헬벨","1680년대경","실내악","바로크",1,"독일","pachelbel"],"교향곡 94번 '놀람'":["요제프 하이든","1791","교향곡","고전",1,"오스트리아","haydn"],"교향곡 101번 '시계'":["요제프 하이든","1794","교향곡","고전",2,"오스트리아","haydn"],"천지창조":["요제프 하이든","1798","종교 음악","고전",2,"오스트리아","haydn"],"현악 사중주 '황제'":["요제프 하이든","1797","실내악","고전",3,"오스트리아","haydn"],"아이네 클라이네 나흐트무지크":["볼프강 아마데우스 모차르트","1787","관현악곡","고전",1,"오스트리아","mozart"],"터키 행진곡(피아노 소나타 11번 중)":["볼프강 아마데우스 모차르트","1783경","피아노 독주곡","고전",1,"오스트리아","mozart"],"마술피리":["볼프강 아마데우스 모차르트","1791","오페라","고전",1,"오스트리아","mozart"],"피가로의 결혼":["볼프강 아마데우스 모차르트","1786","오페라","고전",1,"오스트리아","mozart"],"교향곡 40번 g단조":["볼프강 아마데우스 모차르트","1788","교향곡","고전",2,"오스트리아","mozart"],"교향곡 41번 '주피터'":["볼프강 아마데우스 모차르트","1788","교향곡","고전",2,"오스트리아","mozart"],"돈 조반니":["볼프강 아마데우스 모차르트","1787","오페라","고전",2,"오스트리아","mozart"],"클라리넷 협주곡 A장조":["볼프강 아마데우스 모차르트","1791","협주곡","고전",3,"오스트리아","mozart"],"교향곡 5번 '운명'":["루트비히 판 베토벤","1808","교향곡","고전",1,"독일","beethoven"],"교향곡 9번 '합창'":["루트비히 판 베토벤","1824","교향곡","고전",1,"독일","beethoven"],"엘리제를 위하여":["루트비히 판 베토벤","1810경","피아노 독주곡","고전",1,"독일","beethoven"],"피아노 소나타 14번 '월광'":["루트비히 판 베토벤","1801","피아노 독주곡","고전",1,"독일","beethoven"],"교향곡 6번 '전원'":["루트비히 판 베토벤","1808","교향곡","고전",2,"독일","beethoven"],"피아노 소나타 8번 '비창'":["루트비히 판 베토벤","1799","피아노 독주곡","고전",2,"독일","beethoven"],"피아노 협주곡 5번 '황제'":["루트비히 판 베토벤","1809","협주곡","고전",2,"독일","beethoven"],"교향곡 3번 '영웅'":["루트비히 판 베토벤","1804","교향곡","고전",2,"독일","beethoven"],"마왕":["프란츠 슈베르트","1815","가곡·성악곡","낭만",2,"오스트리아","schubert"],"아베 마리아(엘렌의 노래 3번)":["프란츠 슈베르트","1825","가곡·성악곡","낭만",1,"오스트리아","schubert"],"피아노 오중주 '송어'":["프란츠 슈베르트","1819","실내악","낭만",2,"오스트리아","schubert"],"교향곡 8번 '미완성'":["프란츠 슈베르트","1822","교향곡","낭만",1,"오스트리아","schubert"],"겨울 나그네":["프란츠 슈베르트","1827","가곡·성악곡","낭만",2,"오스트리아","schubert"],"군대 행진곡 1번":["프란츠 슈베르트","1818경","행진곡·무곡","낭만",3,"오스트리아","schubert"],"윌리엄 텔 서곡":["조아키노 로시니","1829","관현악곡","낭만",1,"이탈리아","rossini"],"세비야의 이발사":["조아키노 로시니","1816","오페라","낭만",1,"이탈리아","rossini"],"한여름 밤의 꿈 서곡":["펠릭스 멘델스존","1826","관현악곡","낭만",2,"독일","mendelssohn"],"결혼 행진곡(한여름 밤의 꿈 중)":["펠릭스 멘델스존","1842","행진곡·무곡","낭만",1,"독일","mendelssohn"],"바이올린 협주곡 e단조":["펠릭스 멘델스존","1844","협주곡","낭만",1,"독일","mendelssohn"],"핑갈의 동굴":["펠릭스 멘델스존","1830","관현악곡","낭만",3,"독일","mendelssohn"],"교향곡 4번 '이탈리아'":["펠릭스 멘델스존","1833","교향곡","낭만",2,"독일","mendelssohn"],"무언가":["펠릭스 멘델스존","1830~1845","피아노 독주곡","낭만",3,"독일","mendelssohn"],"즉흥 환상곡":["프레데리크 쇼팽","1834","피아노 독주곡","낭만",2,"폴란드","chopin"],"녹턴 Op.9-2":["프레데리크 쇼팽","1832","피아노 독주곡","낭만",1,"폴란드","chopin"],"빗방울 전주곡":["프레데리크 쇼팽","1839","피아노 독주곡","낭만",2,"폴란드","chopin"],"영웅 폴로네즈":["프레데리크 쇼팽","1842","피아노 독주곡","낭만",2,"폴란드","chopin"],"이별의 곡(에튀드 Op.10-3)":["프레데리크 쇼팽","1832","피아노 독주곡","낭만",2,"폴란드","chopin"],"혁명 에튀드":["프레데리크 쇼팽","1831","피아노 독주곡","낭만",2,"폴란드","chopin"],"강아지 왈츠":["프레데리크 쇼팽","1847","피아노 독주곡","낭만",1,"폴란드","chopin"],"피아노 협주곡 1번 e단조":["프레데리크 쇼팽","1830","협주곡","낭만",3,"폴란드","chopin"],"트로이메라이":["로베르트 슈만","1838","피아노 독주곡","낭만",1,"독일","schumann"],"어린이 정경":["로베르트 슈만","1838","피아노 독주곡","낭만",2,"독일","schumann"],"시인의 사랑":["로베르트 슈만","1840","가곡·성악곡","낭만",3,"독일","schumann"],"사랑의 꿈 3번":["프란츠 리스트","1850","피아노 독주곡","낭만",2,"헝가리","liszt"],"헝가리 광시곡 2번":["프란츠 리스트","1847","피아노 독주곡","낭만",1,"헝가리","liszt"],"전주곡(레 프렐뤼드)":["프란츠 리스트","1854","관현악곡","낭만",3,"헝가리","liszt"],"라 트라비아타":["주세페 베르디","1853","오페라","낭만",1,"이탈리아","verdi"],"아이다":["주세페 베르디","1871","오페라","낭만",1,"이탈리아","verdi"],"리골레토":["주세페 베르디","1851","오페라","낭만",2,"이탈리아","verdi"],"나부코":["주세페 베르디","1842","오페라","낭만",2,"이탈리아","verdi"],"일 트로바토레":["주세페 베르디","1853","오페라","낭만",3,"이탈리아","verdi"],"발퀴레의 기행":["리하르트 바그너","1856","관현악곡","낭만",1,"독일","wagner"],"로엔그린":["리하르트 바그너","1848","오페라","낭만",2,"독일","wagner"],"트리스탄과 이졸데":["리하르트 바그너","1859","오페라","낭만",2,"독일","wagner"],"탄호이저":["리하르트 바그너","1845","오페라","낭만",3,"독일","wagner"],"아름답고 푸른 도나우":["요한 슈트라우스 2세","1867","행진곡·무곡","낭만",1,"오스트리아","strauss2"],"봄의 소리 왈츠":["요한 슈트라우스 2세","1882","행진곡·무곡","낭만",2,"오스트리아","strauss2"],"박쥐":["요한 슈트라우스 2세","1874","오페라","낭만",2,"오스트리아","strauss2"],"황제 왈츠":["요한 슈트라우스 2세","1889","행진곡·무곡","낭만",3,"오스트리아","strauss2"],"트리치 트라치 폴카":["요한 슈트라우스 2세","1858","행진곡·무곡","낭만",3,"오스트리아","strauss2"],"몰다우":["베드르지흐 스메타나","1874","관현악곡","국민악파",1,"체코","smetana"],"팔려간 신부":["베드르지흐 스메타나","1866","오페라","국민악파",2,"체코","smetana"],"카르멘":["조르주 비제","1875","오페라","낭만",1,"프랑스","bizet"],"아를의 여인":["조르주 비제","1872","관현악곡","낭만",2,"프랑스","bizet"],"진주조개잡이":["조르주 비제","1863","오페라","낭만",3,"프랑스","bizet"],"동물의 사육제":["카미유 생상스","1886","관현악곡","낭만",1,"프랑스","saintsaens"],"백조(동물의 사육제 중)":["카미유 생상스","1886","관현악곡","낭만",1,"프랑스","saintsaens"],"죽음의 무도":["카미유 생상스","1874","관현악곡","낭만",2,"프랑스","saintsaens"],"삼손과 델릴라":["카미유 생상스","1877","오페라","낭만",2,"프랑스","saintsaens"],"교향곡 3번 '오르간'":["카미유 생상스","1886","교향곡","낭만",3,"프랑스","saintsaens"],"헝가리 무곡 5번":["요하네스 브람스","1869","행진곡·무곡","낭만",1,"독일","brahms"],"자장가":["요하네스 브람스","1868","가곡·성악곡","낭만",1,"독일","brahms"],"대학 축전 서곡":["요하네스 브람스","1880","관현악곡","낭만",3,"독일","brahms"],"독일 레퀴엠":["요하네스 브람스","1868","종교 음악","낭만",3,"독일","brahms"],"폴로베츠인의 춤(이고르 공 중)":["알렉산드르 보로딘","1870~1880년대","오페라","국민악파",2,"러시아","borodin"],"중앙아시아의 초원에서":["알렉산드르 보로딘","1880","관현악곡","국민악파",3,"러시아","borodin"],"전람회의 그림":["모데스트 무소륵스키","1874","피아노 독주곡","국민악파",1,"러시아","mussorgsky"],"민둥산의 하룻밤":["모데스트 무소륵스키","1867","관현악곡","국민악파",2,"러시아","mussorgsky"],"백조의 호수":["표트르 일리치 차이콥스키","1876","발레 음악","낭만",1,"러시아","tchaikovsky"],"호두까기 인형":["표트르 일리치 차이콥스키","1892","발레 음악","낭만",1,"러시아","tchaikovsky"],"잠자는 숲속의 미녀":["표트르 일리치 차이콥스키","1889","발레 음악","낭만",2,"러시아","tchaikovsky"],"1812년 서곡":["표트르 일리치 차이콥스키","1880","관현악곡","낭만",2,"러시아","tchaikovsky"],"피아노 협주곡 1번 b♭단조":["표트르 일리치 차이콥스키","1875","협주곡","낭만",1,"러시아","tchaikovsky"],"교향곡 6번 '비창'":["표트르 일리치 차이콥스키","1893","교향곡","낭만",2,"러시아","tchaikovsky"],"바이올린 협주곡 D장조":["표트르 일리치 차이콥스키","1878","협주곡","낭만",2,"러시아","tchaikovsky"],"교향곡 9번 '신세계로부터'":["안토닌 드보르자크","1893","교향곡","국민악파",1,"체코","dvorak"],"유모레스크":["안토닌 드보르자크","1894","피아노 독주곡","국민악파",2,"체코","dvorak"],"슬라브 무곡":["안토닌 드보르자크","1878","행진곡·무곡","국민악파",2,"체코","dvorak"],"첼로 협주곡 b단조":["안토닌 드보르자크","1895","협주곡","국민악파",3,"체코","dvorak"],"왕벌의 비행":["니콜라이 림스키코르사코프","1900","관현악곡","국민악파",1,"러시아","rimsky"],"셰에라자드":["니콜라이 림스키코르사코프","1888","관현악곡","국민악파",1,"러시아","rimsky"],"파반":["가브리엘 포레","1887","관현악곡","낭만",2,"프랑스","faure"],"레퀴엠 d단조":["가브리엘 포레","1888","종교 음악","낭만",2,"프랑스","faure"],"꿈꾼 후에":["가브리엘 포레","1877","가곡·성악곡","낭만",3,"프랑스","faure"],"페르 귄트":["에드바르 그리그","1875","관현악곡","국민악파",1,"노르웨이","grieg"],"아침(페르 귄트 중)":["에드바르 그리그","1875","관현악곡","국민악파",1,"노르웨이","grieg"],"솔베이그의 노래(페르 귄트 중)":["에드바르 그리그","1875","가곡·성악곡","국민악파",2,"노르웨이","grieg"],"피아노 협주곡 a단조":["에드바르 그리그","1868","협주곡","국민악파",2,"노르웨이","grieg"],"홀베르크 모음곡":["에드바르 그리그","1884","관현악곡","국민악파",3,"노르웨이","grieg"],"위풍당당 행진곡":["에드워드 엘가","1901","행진곡·무곡","낭만",1,"영국","elgar"],"사랑의 인사":["에드워드 엘가","1888","관현악곡","낭만",1,"영국","elgar"],"수수께끼 변주곡":["에드워드 엘가","1899","관현악곡","낭만",2,"영국","elgar"],"첼로 협주곡 e단조":["에드워드 엘가","1919","협주곡","낭만",3,"영국","elgar"],"라 보엠":["자코모 푸치니","1896","오페라","낭만",1,"이탈리아","puccini"],"토스카":["자코모 푸치니","1900","오페라","낭만",1,"이탈리아","puccini"],"나비 부인":["자코모 푸치니","1904","오페라","낭만",1,"이탈리아","puccini"],"투란도트":["자코모 푸치니","1920년대(미완)","오페라","낭만",2,"이탈리아","puccini"],"교향곡 1번 '거인'":["구스타프 말러","1888","교향곡","낭만",2,"오스트리아","mahler"],"교향곡 2번 '부활'":["구스타프 말러","1894","교향곡","낭만",2,"오스트리아","mahler"],"대지의 노래":["구스타프 말러","1909","교향곡","낭만",3,"오스트리아","mahler"],"차라투스트라는 이렇게 말했다":["리하르트 슈트라우스","1896","관현악곡","낭만",1,"독일","strauss_r"],"틸 오일렌슈피겔의 유쾌한 장난":["리하르트 슈트라우스","1895","관현악곡","낭만",3,"독일","strauss_r"],"장미의 기사":["리하르트 슈트라우스","1910","오페라","낭만",3,"독일","strauss_r"],"핀란디아":["장 시벨리우스","1899","관현악곡","국민악파",1,"핀란드","sibelius"],"슬픈 왈츠":["장 시벨리우스","1904","관현악곡","국민악파",2,"핀란드","sibelius"],"짐노페디":["에릭 사티","1888","피아노 독주곡","근현대",1,"프랑스","satie"],"그노시엔":["에릭 사티","1890","피아노 독주곡","근현대",2,"프랑스","satie"],"달빛(베르가마스크 모음곡 중)":["클로드 드뷔시","1890","피아노 독주곡","근현대",1,"프랑스","debussy"],"아라베스크 1번":["클로드 드뷔시","1891","피아노 독주곡","근현대",2,"프랑스","debussy"],"목신의 오후 전주곡":["클로드 드뷔시","1894","관현악곡","근현대",2,"프랑스","debussy"],"바다":["클로드 드뷔시","1905","관현악곡","근현대",2,"프랑스","debussy"],"꿈":["클로드 드뷔시","1890","피아노 독주곡","근현대",3,"프랑스","debussy"],"행성":["구스타브 홀스트","1914~1916","관현악곡","근현대",1,"영국","holst"],"피아노 협주곡 2번 c단조":["세르게이 라흐마니노프","1901","협주곡","낭만",1,"러시아","rachmaninoff"],"전주곡 c♯단조":["세르게이 라흐마니노프","1892","피아노 독주곡","낭만",2,"러시아","rachmaninoff"],"파가니니 주제에 의한 광시곡":["세르게이 라흐마니노프","1934","관현악곡","낭만",2,"러시아","rachmaninoff"],"볼레로":["모리스 라벨","1928","관현악곡","근현대",1,"프랑스","ravel"],"죽은 왕녀를 위한 파반느":["모리스 라벨","1899","피아노 독주곡","근현대",1,"프랑스","ravel"],"물의 유희":["모리스 라벨","1901","피아노 독주곡","근현대",3,"프랑스","ravel"],"라 발스":["모리스 라벨","1920","관현악곡","근현대",3,"프랑스","ravel"],"봄의 제전":["이고르 스트라빈스키","1913","발레 음악","근현대",2,"러시아","stravinsky"],"불새":["이고르 스트라빈스키","1910","발레 음악","근현대",2,"러시아","stravinsky"],"페트루슈카":["이고르 스트라빈스키","1911","발레 음악","근현대",3,"러시아","stravinsky"],"루마니아 민속 무곡":["벨러 버르토크","1915","피아노 독주곡","근현대",3,"헝가리","bartok"],"관현악을 위한 협주곡":["벨러 버르토크","1943","관현악곡","근현대",3,"헝가리","bartok"],"피터와 늑대":["세르게이 프로코피예프","1936","관현악곡","근현대",1,"러시아","prokofiev"],"로미오와 줄리엣":["세르게이 프로코피예프","1935","발레 음악","근현대",2,"러시아","prokofiev"],"랩소디 인 블루":["조지 거슈윈","1924","피아노 독주곡","근현대",1,"미국","gershwin"],"파리의 아메리카인":["조지 거슈윈","1928","관현악곡","근현대",2,"미국","gershwin"],"포기와 베스":["조지 거슈윈","1935","오페라","근현대",3,"미국","gershwin"],"왈츠 2번(재즈 모음곡 2번)":["드미트리 쇼스타코비치","1938","행진곡·무곡","근현대",2,"러시아","shostakovich"],"교향곡 7번 '레닌그라드'":["드미트리 쇼스타코비치","1941","교향곡","근현대",3,"러시아","shostakovich"],"현을 위한 아다지오":["새뮤얼 바버","1936","관현악곡","근현대",2,"미국","barber"]},"C":[["요한 제바스티안 바흐","바로크","bach"],["게오르크 프리드리히 헨델","바로크","handel"],["안토니오 비발디","바로크","vivaldi"],["요한 파헬벨","바로크","pachelbel"],["요제프 하이든","고전","haydn"],["볼프강 아마데우스 모차르트","고전","mozart"],["루트비히 판 베토벤","고전","beethoven"],["프란츠 슈베르트","낭만","schubert"],["조아키노 로시니","낭만","rossini"],["펠릭스 멘델스존","낭만","mendelssohn"],["프레데리크 쇼팽","낭만","chopin"],["로베르트 슈만","낭만","schumann"],["프란츠 리스트","낭만","liszt"],["주세페 베르디","낭만","verdi"],["리하르트 바그너","낭만","wagner"],["요한 슈트라우스 2세","낭만","strauss2"],["베드르지흐 스메타나","국민악파","smetana"],["조르주 비제","낭만","bizet"],["카미유 생상스","낭만","saintsaens"],["요하네스 브람스","낭만","brahms"],["알렉산드르 보로딘","국민악파","borodin"],["모데스트 무소륵스키","국민악파","mussorgsky"],["표트르 일리치 차이콥스키","낭만","tchaikovsky"],["안토닌 드보르자크","국민악파","dvorak"],["니콜라이 림스키코르사코프","국민악파","rimsky"],["가브리엘 포레","낭만","faure"],["에드바르 그리그","국민악파","grieg"],["에드워드 엘가","낭만","elgar"],["자코모 푸치니","낭만","puccini"],["구스타프 말러","낭만","mahler"],["리하르트 슈트라우스","낭만","strauss_r"],["장 시벨리우스","국민악파","sibelius"],["에릭 사티","근현대","satie"],["클로드 드뷔시","근현대","debussy"],["구스타브 홀스트","근현대","holst"],["세르게이 라흐마니노프","낭만","rachmaninoff"],["모리스 라벨","근현대","ravel"],["이고르 스트라빈스키","근현대","stravinsky"],["벨러 버르토크","근현대","bartok"],["세르게이 프로코피예프","근현대","prokofiev"],["조지 거슈윈","근현대","gershwin"],["드미트리 쇼스타코비치","근현대","shostakovich"],["새뮤얼 바버","근현대","barber"]],"AMBIG":{"레퀴엠 d단조":["brahms","verdi"],"자장가":["mozart","schubert"],"죽음의 무도":["liszt"],"아베 마리아(엘렌의 노래 3번)":["bach","gounod"],"전주곡(레 프렐뤼드)":["chopin","debussy","rachmaninoff"],"꿈":["schumann"],"백조(동물의 사육제 중)":["tchaikovsky"]}};   // W: {곡: [작곡가, 연도, 갈래, 시대, 유명도, 나라, 작곡가id]}, C: [[작곡가, 시대, id]], AMBIG
  var MK = "classic-listen-mode-v1", WK = "classic-wrong-v1";
  var isQuiz = !!document.getElementById("opts") && typeof start === "function", isGal = !!document.getElementById("list") && !isQuiz;
  var idx = null, mode = "off";   // off | mix | only
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var shuffle = function (a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; };
  var has = function (t) { return !!(idx && idx[t] && DATA.W[t]); };
  var audioTitles = function () { return Object.keys(DATA.W).filter(has); };
  var credit = function (e) { return '🎧 음원: <a href="' + esc(e.p) + '" target="_blank" rel="noopener noreferrer">위키미디어 커먼즈 「' + esc(e.t) + "」</a> (" + esc(e.l) + ")"; };

  // ── 소리 재생(한 번에 하나만)
  var cur = null;
  function player(title) {
    if (cur) { try { cur.pause(); } catch (e) {} }
    var a = new Audio("classic-audio/" + idx[title].f); a.preload = "auto"; cur = a; return a;
  }
  function stopAudio() { if (cur) { try { cur.pause(); } catch (e) {} } }

  function injectCss() {
    var st = document.createElement("style");
    st.textContent = ".amode{background:var(--surface,#fff);border:1px solid var(--line,#ccc);border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px}.amode .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".amode button{border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:8px 12px;font-size:.92rem}.amode button.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent;font-weight:700}" +
      ".amode small{color:var(--muted,#666)}.aplay{display:flex;flex-direction:column;align-items:center;gap:6px;margin:0 0 10px}.aplay button{border:0;border-radius:999px;background:var(--accent,#c4552b);color:var(--accent-fg,#fff);font-size:1.15rem;font-weight:700;padding:14px 26px;min-width:200px}" +
      ".aplay small{color:var(--muted,#666)}.acard{margin-top:10px;padding:10px 12px;border:1px solid var(--line,#ccc);border-radius:12px;text-align:left;display:flex;flex-direction:column;gap:2px}.acard b{font-size:1.05rem}.acard span{font-size:.88rem;color:var(--muted,#666)}" +
      ".ahint{margin-top:8px;font-size:.9rem;text-align:center}.ahint button{border:1px dashed var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:6px 12px;font-size:.88rem}.ahint div{margin-top:6px;color:var(--muted,#666)}" +
      ".gplay{margin-left:6px;border:1px solid var(--line,#ccc);background:transparent;color:var(--fg,#222);border-radius:999px;padding:2px 10px;font-size:.8rem}.gplay.on{background:var(--accent,#c4552b);color:var(--accent-fg,#fff);border-color:transparent}";
    document.head.appendChild(st);
  }
  var bar;
  function drawBar() {
    var n = audioTitles().length;
    var h = '<b>🎧 듣고 맞히기</b><div class="row">' +
      '<button type="button" data-m="off" class="' + (mode === "off" ? "on" : "") + '">📴 글로만</button>' +
      '<button type="button" data-m="mix" class="' + (mode === "mix" ? "on" : "") + '"' + (n ? "" : " disabled") + ">🔀 섞어서(한 판 최대 3개)</button>" +
      '<button type="button" data-m="only" class="' + (mode === "only" ? "on" : "") + '"' + (n ? "" : " disabled") + ">🎧 듣기 문제만</button></div>";
    h += "<small>" + (n ? "인터넷 없이 앱에 들어 있는 짧은 음원(약 20초)으로 곡을 맞혀요. 소리가 나오니 주변을 확인하세요. 듣기 문제 " + n + "곡." : "음원을 아직 준비 중이에요.") + "</small>";
    if (isQuiz && wrongList.length && mode !== "off") h += '<div class="row"><button type="button" id="clsreview" data-m="review">' + reviewLabel() + "</button><small>틀린 곡만 다시 들어요. 맞히면 목록에서 빠져요.</small></div>";
    bar.innerHTML = h;
  }
  function buildBar() {
    injectCss(); bar = document.createElement("div"); bar.className = "amode"; bar.id = "clsmode";
    var hh = document.querySelector("h1"); if (hh) hh.insertAdjacentElement("afterend", bar); else document.body.insertBefore(bar, document.body.firstChild);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.disabled) return;
      if (b.dataset.m === "review") startReview(); else { mode = b.dataset.m; lsSet(MK, mode); drawBar(); stopAudio(); start(); }
    });
    drawBar();
  }

  // ── 문제 만들기: 곡 → 작곡가 또는 곡 → 제목(같은 곡이 둘 다 나오지 않게 번갈아)
  var composers = function () { return DATA.C; };
  function wrongComposers(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []), mine = w[6], era = w[3], lvl = w[4];
    var pool = composers().filter(function (c) { return c[2] !== mine && ban.indexOf(c[2]) < 0; });
    var same = shuffle(pool.filter(function (c) { return c[1] === era; })), diff = shuffle(pool.filter(function (c) { return c[1] !== era; }));
    var n = lvl === 1 ? 0 : lvl === 2 ? 1 : 2, out = same.slice(0, n); diff.concat(same.slice(n)).some(function (c) { if (out.length >= 3) return true; if (out.indexOf(c) < 0) out.push(c); return false; });
    return out.slice(0, 3).map(function (c) { return c[0]; });
  }
  function wrongTitles(t) {
    var w = DATA.W[t], ban = (DATA.AMBIG[t] || []);
    var pool = Object.keys(DATA.W).filter(function (x) { var v = DATA.W[x]; return x !== t && v[6] !== w[6] && ban.indexOf(v[6]) < 0 && v[4] <= 2 && (DATA.AMBIG[x] || []).indexOf(w[6]) < 0; });
    return shuffle(pool).slice(0, 3);
  }
  function mkItem(t, kind) {
    var w = DATA.W[t], d;
    if (kind === "t") d = ["이 곡의 제목은 무엇일까요?", t, wrongTitles(t), w[3], w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    else d = ["이 곡의 작곡가는 누구일까요?", w[0], wrongComposers(t), w[3], "‘" + t + "’ — " + w[0] + "(" + w[5] + ")의 " + w[2] + "이에요. " + w[1] + "에 만들었어요."];
    d.tt = t; d.aud = idx[t]; d.kind = kind; return d;
  }
  var roundId = 0;
  function mix() {
    var id = ++roundId, want = mode === "only" ? 10 : 3, first = i === 0 && !locked;
    var pool = shuffle(audioTitles().filter(function (t) { var w = DATA.W[t]; return (!lv || w[4] === lv) && (cat === "전체" || w[3] === cat); })).slice(0, want);
    if (!pool.length || !qs || qs.length < 2) return;
    var slots = []; for (var k = first ? 0 : i + 1; k < qs.length; k++) slots.push(k);
    slots = (first ? [0].concat(shuffle(slots.slice(1))) : shuffle(slots)).slice(0, pool.length);
    slots.forEach(function (pos, n) { var d = mkItem(pool[n], Math.random() < 0.5 ? "t" : "c"); qs[pos] = { d: d, opts: options(d) }; });
    if (first && slots.indexOf(0) >= 0) show();
  }
  var hintUsed = false;
  function decorateQ() {
    var c = qs && qs[i]; stopAudio(); hintUsed = false; if (!c || !c.d.aud) return;
    var q = document.getElementById("q"), box = document.createElement("div"); box.className = "aplay";
    box.innerHTML = '<button type="button">▶ 소리 듣기</button><small>눌러서 듣고, 몇 번이든 다시 들을 수 있어요(약 20초).</small>';
    var btn = box.querySelector("button"), a = player(c.d.tt);
    a.addEventListener("ended", function () { btn.textContent = "🔁 다시 듣기"; });
    a.addEventListener("error", function () { btn.textContent = "소리를 불러오지 못했어요"; btn.disabled = true; });
    btn.addEventListener("click", function () { if (!a.paused && !a.ended) { a.pause(); btn.textContent = "▶ 이어서 듣기"; } else { if (a.ended) a.currentTime = 0; var p = a.play(); if (p && p.catch) p.catch(function () {}); btn.textContent = "⏸ 멈추기"; } });
    q.insertBefore(box, q.firstChild);
    // 힌트: 시대·나라 → 갈래 (쓰면 맞혀도 0.5점)
    var m = DATA.W[c.d.tt], hb = document.createElement("div"); hb.className = "ahint"; hb.innerHTML = '<button type="button">💡 힌트 (쓰면 맞혀도 0.5점)</button><div hidden></div>';
    var hbtn = hb.querySelector("button"), out = hb.querySelector("div"), lvl = 0;
    hbtn.addEventListener("click", function () { if (locked) return; hintUsed = true; lvl++; out.hidden = false; out.textContent = lvl === 1 ? "시대: " + m[3] + (c.d.kind === "c" ? " · 갈래: " + m[2] : "") : "시대: " + m[3] + " · 갈래: " + m[2] + " · 작곡가의 나라: " + m[5]; if (lvl >= 2) hbtn.disabled = true; else hbtn.textContent = "💡 힌트 한 번 더"; });
    q.appendChild(hb);
  }
  function addCard() {
    var c = qs && qs[i]; if (!c || !c.d.aud) return; var m = DATA.W[c.d.tt], q = document.getElementById("q");
    var n = q.querySelector(".note"); if (n) n.remove(); var h = q.querySelector(".ahint"); if (h) h.remove();
    q.insertAdjacentHTML("beforeend", '<div class="acard"><b>‘' + esc(c.d.tt) + "’</b><span>" + esc(m[0]) + " (" + esc(m[5]) + ")</span><span>" + esc(m[3]) + " · " + esc(m[2]) + " · " + esc(m[1]) + '</span></div><span class="note">' + credit(c.d.aud) + "</span>");
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
    var ts = shuffle(wrongList.filter(has)).slice(0, 10); if (!ts.length) return;
    start(); roundId++;
    qs = ts.map(function (t) { var d = mkItem(t, Math.random() < 0.5 ? "t" : "c"); return { d: d, opts: options(d) }; }); i = 0; score = 0; show();
  }

  // ── 모음: 곡 옆에 ▶ 단추
  function decorateGal() {
    var list = document.getElementById("list"); if (!list || !idx) return;
    list.querySelectorAll("li").forEach(function (li) {
      if (li.dataset.cls) return; li.dataset.cls = "1"; var b = li.querySelector("b"); if (!b) return; var t = b.textContent; if (!has(t)) return;
      var btn = document.createElement("button"); btn.type = "button"; btn.className = "gplay"; btn.textContent = "▶ 듣기"; btn.dataset.t = t; b.insertAdjacentElement("afterend", btn);
    });
  }
  var playing = null;
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".gplay"); if (!b) return;
    var t = b.dataset.t, on = b.classList.contains("on"); document.querySelectorAll(".gplay.on").forEach(function (x) { x.classList.remove("on"); x.textContent = "▶ 듣기"; }); stopAudio();
    if (on) return; var a = player(t); b.classList.add("on"); b.textContent = "⏹ 멈추기";
    a.addEventListener("ended", function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; }); a.play().catch(function () { b.classList.remove("on"); b.textContent = "▶ 듣기"; });
  });

  function boot() {
    loadWrong();
    fetch("classic-audio/index.json").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (j) {
      idx = j && typeof j === "object" && Object.keys(j).length ? j : null;
      if (isQuiz) {
        buildBar();
        var oS = start, oShow = show, oPick = pick;
        start = function () { oS(); if (mode !== "off") mix(); };
        show = function () { oShow(); decorateQ(); };
        pick = function (k) { if (locked) return; var c = qs && qs[i], ok = c && c.opts[k] === c.d[1], hu = hintUsed; oPick(k); if (c && c.d.aud) { if (ok && hu) { score -= 0.5; document.getElementById("score").textContent = score; } record(c, ok); addCard(); } };
        var m = lsGet(MK); if (idx && (m === "mix" || m === "only")) { mode = m; drawBar(); start(); }
      } else if (isGal) {
        new MutationObserver(decorateGal).observe(document.getElementById("list"), { childList: true }); decorateGal();
      }
    });
  }
  addEventListener("pagehide", stopAudio);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
