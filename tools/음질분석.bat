@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ===== 클래식 음원 음질 분석 (더블클릭 한 번으로 끝까지) =====
echo  * 분석하는 동안 PC가 절전에 들어가지 않게 해 주세요(설정 - 시스템 - 전원).
echo  * 중간에 창을 닫아도 괜찮아요. 다시 더블클릭하면 이미 분석한 곡은 건너뛰고 이어서 해요.
echo.
echo [1/4] 최신 내용을 받아 옵니다...
git pull
if errorlevel 1 goto fail
echo [2/4] 남은 곡의 음질을 분석합니다(곡 수와 서버 속도에 따라 30분~1시간 걸릴 수 있어요)...
cd tools\dev
py music_pick.py --follow
if errorlevel 1 goto fail
echo [3/4] 분석 결과를 앱에 반영합니다...
py classic_publish.py
if errorlevel 1 goto fail
cd /d "%~dp0.."
echo [4/4] 사이트에 올립니다...
git add classic-quiz.html classic-gallery.html classic-mode.js classic-media.js sw.js index.html data/release-notes.json tools/dev/music_pick.json tools/dev/music_pick_scr.json tools/dev/music_pick_state.json tools/dev/music_pick_ia.json
git diff --cached --quiet
if not errorlevel 1 goto nothing
git commit -m "클래식 음질 분석 반영(PC 더블클릭)"
if errorlevel 1 goto fail
git push
if errorlevel 1 goto fail
echo.
echo 완료! 1~2분 뒤 사이트에 반영되고, 폰은 앱을 완전히 닫았다 열면 새 곡 목록을 받아요.
pause
exit /b 0
:nothing
echo.
echo 새로 반영할 내용이 없어요(모든 곡이 이미 분석돼 있어요).
pause
exit /b 0
:fail
echo.
echo 중간에 오류가 났어요. 위의 메시지를 캡처해서 알려 주세요. (다시 더블클릭하면 이어서 해요)
pause
exit /b 1
