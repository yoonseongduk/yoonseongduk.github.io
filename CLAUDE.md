# 가족 미니 게임 — 작업 인수인계 문서 (CLAUDE.md)

이 파일은 Claude Code가 이 폴더에서 시작할 때 **자동으로 읽는** 안내서예요. (클라우드에서 하던 작업을 PC에서 이어 가기 위한 기억 노트)
`cloud.md`는 이 파일을 가리키는 짧은 안내만 있어요.

## 0. 한눈에 보기
- 사이트: https://yoonseongduk.github.io/ (GitHub Pages, 저장소 `yoonseongduk/yoonseongduk.github.io`, 브랜치 `main`)
- 내용: 폰에서 하는 **단일 HTML 파일 미니 게임·퀴즈·도구 약 210개**. 앱처럼 설치(PWA)되고 **오프라인**에서도 돼요.
- 사용자는 **초보자(한국어)**. 설명은 **한국어로, 자세하고 쉽게**. 결과는 짧게 보고하고 마지막에 "크레딧 잔액은 제가 볼 수 없어요"를 덧붙여 왔어요(필수 아님).
- 사용자 PC 폴더: `E:\03_data001\개인\돈벌기\핸드폰_어플_모음\가족게임` (git clone 완료). 폰은 삼성 갤럭시(삼성 인터넷/크롬).
- 실제 폰 테스트는 못 해요. "PC 브라우저에서 폰 크기(360px)로 확인했다"까지만 말하고 폰에서 확인했다고 주장하지 마세요.

## 1. 폴더 구조
| 경로 | 설명 |
|---|---|
| `index.html` | 시작 화면. `GAMES` 배열에 `[파일, 이모지, 제목, 설명, 그룹]` 한 줄씩. 그룹: brain, quiz, react, board, arcade, together, life |
| `*.html` | 게임 하나 = 파일 하나. 빌드 도구 없음, 외부 라이브러리 없음 |
| `sw.js` | 서비스 워커(오프라인 저장). **직접 고치지 말고** `py tools\make-sw.py`로 생성 |
| `manifest.webmanifest`, `icon-*.png` | 앱 설치용 |
| `fonts/` | 도현체·Noto Sans KR 자체 포함(OFL). `fonts/fonts.css` |
| `data/` | `hanja.json`(한자 3,500), `hanja-detail.json`(한자 자세히), `words-ko.txt`(끝말잇기 사전 33만) |
| `wrong-hook.js` | 퀴즈 오답을 자동 수집하는 공통 스크립트(퀴즈 페이지 44개+에 삽입됨) |
| `wrong-notes.html` | 오답 노트 화면(집중 복습) |
| `licenses.html` | 출처·저작권 안내(시작 화면 하단 링크) |
| `tools/make-sw.py` | sw.js 생성기. 버전 = 파일 내용 해시(CRLF 정규화) |
| `tools/올리기.bat` | PC에서 고친 뒤 pull→sw 생성→커밋→push (변경 없으면 "올릴 변경 내용이 없어요") |
| `tools/dev/` | **게임·퀴즈 생성기와 데이터 원본**(아래 §3) |

## 2. 가장 중요한 규칙 (어기지 말 것)
1. **저작권/상표**: 사용자는 저작권 문제를 매우 신경 써요. 상표와 겹치는 이름은 일반 이름으로 바꿨어요(파일명 포함).
   - 예: 테트리스→`block-stack.html`(블록 쌓기, 새 8모양·폭탄·연쇄·콤보 규칙), 워들→`word-guess-en`, 오셀로→`flip-board`, 사이먼→`color-sequence`, 커넥트4→`four-in-row`, 퐁→`table-tennis`, 플래피→`wing-bird`, 우주침략자→`alien-defense`, 전함→`ship-hunt`, 라이츠아웃→`light-off`, 플러드잇→`color-fill`, 요트→`dice-combo`, 2048→`number-merge`, 지뢰찾기→`mine-puzzle`, 라이어게임→`word-trick`(역할 "모르쇠").
   - MBTI는 상표 → 화면 이름은 **"성격 유형 테스트"**(`personality-16.html`), 직접 쓴 문항·해설, "공식 MBTI® 검사가 아님" 문구 유지.
   - 새 게임을 만들 때 유명 게임/브랜드 이름을 제목·파일명에 쓰지 마세요.
   - 외부 데이터는 출처를 `licenses.html`에 적어요(한국어문회 한자 자료, acidsound/korean_wordlist, 글꼴 OFL 등). 새 데이터를 쓰면 라이선스부터 확인하고 적으세요.
2. **오프라인/PWA**: 모든 `.html`·`data/*`·루트 `*.js`는 sw.js가 미리 저장해요. 새 파일을 추가/수정하면 반드시 `py tools\make-sw.py`(올리기.bat이 자동 실행). 외부 URL(CDN, 구글 폰트) 사용 금지. 글꼴은 `fonts/fonts.css`.
3. **모든 페이지 공통 형식**: 단일 파일, 모바일 우선(360px에서 가로 넘침 금지, 16px 여백), 라이트/다크 대응(`:root` 색 토큰 + `@media (prefers-color-scheme: dark)`), `[hidden]{display:none!important}`, localStorage는 try/catch로 감싸기, 페이지 안에 `<link rel="manifest">`와 sw 등록 스크립트 포함(`tools/dev/ship.py`가 자동 삽입).
4. **전역 이름 충돌**: 페이지 최상위 `const/let/function` 이름이 `window` 속성(top, open, stop, name, status, frame, info …)이나 아케이드 엔진 전역과 겹치면 오류가 나요. `tools/dev/gl.js`로 검사하세요.
5. **내 커밋은 `git add -A` 금지**: 바꾼 파일만 골라 add. 커밋 메시지는 한국어, 한 줄 요약.
6. 사실 정확성: 퀴즈(한국사·사자성어·일본어·순우리말 등)는 직접 쓴 내용이라 틀릴 수 있어요. 애매한 문제는 빼는 쪽으로. 사용자가 틀림을 알려 주면 바로 고치기.
7. 사용자가 이미 "알아서 진행"을 허락했어요: 만들기 → 검증 → 등록 → 커밋/푸시 → 간단히 보고. 단, **이름 변경·삭제처럼 바깥에 영향이 큰 일**은 요청이 있을 때만.

## 3. 만드는 방법 (tools/dev)
- 한 번 `cd tools\dev` 후 실행(경로는 상대경로라 PC에서도 돼요). 결과 HTML은 `tools/dev/out/`에 만들어지고, `ship.py`가 저장소로 복사 + 필요한 머리글/등록 삽입 + `index.html` 등록 + `sw.js` 갱신까지 해요.
- 새 게임: `mkpage.py`(`make(path,title,emoji,hue,key,help,body,js,css)`), 퀴즈: `mkquiz.py`(`make(..., data=[[질문,정답,[오답3],분류,해설],...])`), 아케이드: `mkarcade.py`(canvas 엔진: reset/update/draw/pointer/key).
- 등록: `py ship.py "[[\"파일.html\",\"이모지\",\"제목\",\"설명\",\"quiz\"]]"` (JSON). 이미 등록된 파일을 다시 ship하면 카드는 그대로, 파일만 갱신.
- 대표 생성 스크립트와 데이터:
  | 대상 | 스크립트 | 데이터 |
  |---|---|---|
  | 일본어 단어 퀴즈(2,511문제) | `set21.py` | `jlpt_data.py`, `jlpt_more1~5.py` |
  | 한국사 퀴즈(1,574문제) | `set21.py` | `kh_all5.json`(=`kh_*.py` 합친 것) |
  | 한자 사자성어 퀴즈(3,312) + 사자성어 퀴즈(560) | `set21.py` + `idiom_merge.py` | `idiom_data.txt`(한글\|한자\|뜻\|풀이\|예문) |
  | 순우리말 퀴즈(1,317) | `set22.py` | `pk1~6.txt` |
  | 음양력·시간 도구 | `set23.py` | `data/lunar_data.js`, `jq24.js` 등 |
  | 성격 유형 테스트 | `set24.py` | (스크립트 안에 문항·해설) |
  | 오답 노트, 한자 쓰기 | `set19.py`, `set20.py` | |
  | 한자 자세히 보기 | `hd1~4.txt`, `hd_rows.json` → `data/hanja-detail.json` | (생성 코드는 대화 중 일회성; 형식은 JSON 참고) |
- 데이터 추가 요령(예: 사자성어): `idiom_more*.txt` 식으로 새 줄을 쓰고 → 중복(한글/한자/뜻) 제거 후 `idiom_data.txt`에 추가 → `py idiom_merge.py` → `py set21.py` → `py ship.py ...` → 검증 → 푸시. **`sed '/.../d'`로 줄 지울 때 `\|`를 쓰면 모든 줄이 지워지니 주의**(파이썬 필터 권장).
- 검증 도구(Node + Playwright 필요): `qv.js 페이지명...`(퀴즈 보기·정답 검사), `all.js`(모든 페이지 360px 오류·가로 넘침), `gl.js`(전역 이름 충돌), `idx.js`(시작 화면). PC에서 쓰려면 `npm i playwright` + `npx playwright install chromium`.

## 4. 주요 기능 메모
- **오답 노트**: 퀴즈 `.opt` 클릭을 `wrong-hook.js`가 가로채 기록(localStorage `wrongnotes-v1`). 연속 2번 맞히면 졸업. 한자 쓰기 오답은 4지선다로 바꿔 복습.
- **업데이트 흐름**: 폰 앱을 열면 예전 파일로 먼저 뜨고 뒤에서 새 파일을 받아요 → 앱을 완전히 닫았다 열면 반영. 시작 화면에 "새 버전 확인" 카드가 있고 오프라인이면 자동으로 건너뛰어요.
- **오늘의 운세(`daily-fortune.html`)**: 생일(양력/음력, 윤달), 태어난 시(시진)로 결과가 달라지고 "자세히 보기" 화면이 있어요. 음력 변환표(1901~2049, 한국천문연구원 자료 기반 `korean-lunar-calendar` MIT)와 절기표(1925~2077, 천문 계산 `ephem`으로 분 단위 사전 계산)를 내장. 사주는 연·월·일·시 간지 + 오행 분포(년주·월주는 절기 기준). 성별은 쓰지 않음(의미 없음).
- **음양력·시간 도구(`calendar-tools.html`)**: 오늘/음양력 변환+음력 명절/24절기/12시진/날짜 계산.
- **한자 급수 퀴즈**: 정답 후 "📖 이 한자 자세히 보기" → `data/hanja-detail.json`(6급 300자는 유래·한자어 예 직접 작성, 나머지는 사자성어 속 쓰임·같은 부수 한자만).

## 5. 앞으로 할 만한 일 (사용자가 원하면)
- 한자 자세히 보기: 5급(200자)부터 유래·사용 예 추가(`hd*.txt` 형식: `한자|유래|예1|예2|예3`).
- 퀴즈 문제 더 늘리기(한국사 1,000+ 달성, 일본어 2,500+, 사자성어 560, 순우리말 1,317은 사용자가 계속 "더 늘려 달라" 요청해 옴). 늘릴 때는 새로 쓴 문제 중 애매한 것은 걸러서 넣기.
- 24절기 전체를 사주에 활용, 1954~61년 표준시(+8:30)·서머타임 반영(현재 미반영).
- 성격 유형 테스트: 가족 비교 기능 제안해 둔 상태.
- 사용자가 최근 지적한 사항은 모두 반영됨(아이콘 중복 방지, 블록 퍼즐 놓는 위치, 쓰기 화면 스크롤 없는 진행 등).

## 6. PC 환경 준비 (처음 한 번)
1. Claude Code 설치(https://claude.com/claude-code) 후 이 폴더에서 `claude` 실행 → 이 문서를 자동으로 읽어요.
2. Python 3는 `py`로 실행(`python`은 가짜 연결일 수 있음). Git은 이미 설치·이름/이메일 설정 완료(`yoonseongduk`).
3. 작업 뒤 올리기: `tools\올리기.bat` 더블클릭 → 변경 메모 입력 → "완료!". Claude Code가 직접 커밋/푸시하게 할 수도 있어요(푸시 시 GitHub 로그인 창이 뜰 수 있음).
4. Windows 줄바꿈(CRLF) 경고(`LF will be replaced by CRLF`)는 무시해도 돼요.
