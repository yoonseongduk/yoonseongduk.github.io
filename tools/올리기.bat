@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ===== 가족 게임 올리기 =====
echo [1/5] 사이트의 최신 내용을 먼저 받아 옵니다...
git pull
if errorlevel 1 goto fail
echo [2/5] 폰 저장 목록(sw.js)을 새로 만듭니다...
python tools\make-sw.py
if errorlevel 1 goto nopy
echo [3/5] 바뀐 파일 목록:
git status --short
set /p MSG=변경 내용을 짧게 적어 주세요 (예: 속담 퀴즈 문제 추가): 
if "%MSG%"=="" set MSG=게임 수정
echo [4/5] 저장(커밋)합니다...
git add -A
git commit -m "%MSG%"
echo [5/5] 사이트에 올립니다...
git push
if errorlevel 1 goto fail
echo.
echo 완료! 1~2분 뒤 사이트에 반영되고, 폰은 인터넷이 될 때 앱을 열면 새 버전을 받아요.
pause
exit /b 0
:nopy
echo.
echo 파이썬(python)이 없거나 실행에 실패했어요. https://www.python.org 에서 설치한 뒤 다시 해 보세요.
pause
exit /b 1
:fail
echo.
echo 중간에 오류가 났어요. 위의 빨간 글씨나 메시지를 캡처해서 알려 주세요.
pause
exit /b 1
