@echo off
chcp 65001 >nul
title 네이버 지역 순위 체크

:MENU
cls
echo.
echo ████████████████████████████████████████████████████████
echo █                                                      █
echo █    🏥 함소아한의원 네이버 지역 순위 체크 시스템         █
echo █                                                      █
echo ████████████████████████████████████████████████████████
echo.
echo    📋 메뉴를 선택하세요:
echo.
echo    1. ⚡ 순위 빠르게 확인하기
echo    2. 📊 상세 일일 리포트 보기
echo    3. 📈 Excel 리포트 열기
echo    4. 🔄 새로운 순위 데이터 수집
echo    5. 🌐 웹서버로 다른 사람과 공유
echo    6. 📧 이메일로 리포트 받기 (준비중)
echo    7. ❌ 종료
echo.
set /p choice=    선택 (1-7): 

if "%choice%"=="1" goto QUICK_CHECK
if "%choice%"=="2" goto DAILY_REPORT
if "%choice%"=="3" goto OPEN_EXCEL
if "%choice%"=="4" goto COLLECT_DATA
if "%choice%"=="5" goto WEB_SERVER
if "%choice%"=="6" goto EMAIL_REPORT
if "%choice%"=="7" goto EXIT
goto MENU

:QUICK_CHECK
cls
echo 📊 빠른 순위 확인 중...
echo.
python show_ranks.py
echo.
pause
goto MENU

:DAILY_REPORT
cls
echo 📋 상세 일일 리포트 생성 중...
echo.
python daily_summary.py
echo.
pause
goto MENU

:OPEN_EXCEL
cls
echo 📈 Excel 리포트를 열고 있습니다...
if exist "report_local_rank.xlsx" (
    start "" "report_local_rank.xlsx"
    echo ✅ Excel 파일이 열렸습니다!
) else (
    echo ❌ Excel 파일이 없습니다. 먼저 데이터를 수집해주세요.
)
echo.
pause
goto MENU

:COLLECT_DATA
cls
echo 🔄 새로운 순위 데이터 수집 중... (약 2-3분 소요)
echo.
python main.py
echo.
echo 📊 Excel 리포트 생성 중...
python make_report.py
echo.
echo ✅ 데이터 수집 완료!
pause
goto MENU

:WEB_SERVER
cls
echo 🌐 웹서버를 시작합니다...
echo.
echo 📍 다른 사람들이 접속할 수 있는 주소를 표시합니다
echo 🚨 이 창을 닫으면 웹서버가 중단됩니다
echo.
python smart_web_server.py
pause
goto MENU

:EMAIL_REPORT
cls
echo 📧 이메일 기능은 준비 중입니다.
echo    IT팀에 문의해주세요.
echo.
pause
goto MENU

:EXIT
cls
echo 👋 프로그램을 종료합니다.
echo    감사합니다!
timeout /t 2 >nul
exit
