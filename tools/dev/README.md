# tools/dev — 생성기와 데이터 원본

게임·퀴즈 HTML을 만드는 파이썬 스크립트와 데이터예요. 자세한 설명은 저장소 루트의 `CLAUDE.md` §3을 보세요.

```
cd tools\dev
py set21.py                       # 일본어/한국사/사자성어 퀴즈 생성 (결과: out\*.html)
py ship.py "[[\"jlpt-quiz.html\",\"🇯🇵\",\"일본어 단어 퀴즈\",\"설명\",\"quiz\"]]"   # 저장소로 복사·등록·sw.js 갱신
```
- `out\` 폴더는 임시 결과물이라 git에 올리지 않아요.
- 검증용 Node 스크립트(`qv.js`, `all.js`, `gl.js`, `idx.js`)는 `npm i playwright` 후 사용해요.
