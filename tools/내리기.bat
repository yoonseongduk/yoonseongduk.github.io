@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ===== 가족 게임 내리기 (작업 시작 전 최신 받기) =====
echo [1/2] 공개 사이트(코드)의 최신 내용을 받습니다...
git pull
if errorlevel 1 goto fail
echo [2/2] 비공개 작업 문서(design, 작업상태)의 최신 내용을 받습니다...
if not exist .git-private goto skip
git --git-dir=.git-private --work-tree=. pull --no-rebase --no-edit origin main
if errorlevel 1 goto fail
echo.
echo 완료! 두 저장소 모두 최신입니다. 이제 작업을 시작하세요.
pause
exit /b 0
:skip
echo .git-private가 없어 비공개 문서는 건너뜁니다. (비공개_동기화.md의 최초 설정 참고)
pause
exit /b 0
:fail
echo.
echo 오류가 났어요. 고치던 파일이 있으면 먼저 올리기.bat으로 저장한 뒤 다시 해 보세요. 위의 메시지를 캡처해서 알려 주세요.
pause
exit /b 1
