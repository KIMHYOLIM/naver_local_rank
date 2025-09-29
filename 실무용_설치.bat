@echo off
chcp 65001 >nul
title 네이버 지역 순위 체크 시스템 - 친구용 설치

echo.
echo ████████████████████████████████████████████████████████
echo █                                                      █
echo █    🏥 네이버 지역 순위 체크 시스템 (친구용)           █
echo █                                                      █
echo ████████████████████████████████████████████████████████
echo.
echo 📋 이 프로그램은 네이버에서 특정 업체의 지역 검색 순위를
echo    자동으로 확인해주는 도구입니다.
echo.
echo 🔧 설치할 내용:
echo    ✅ Python 패키지 설치
echo    ✅ 네이버 API 키 설정  
echo    ✅ 키워드 파일 설정
echo    ✅ 바탕화면 바로가기 생성
echo.

pause

echo 🔍 1단계: Python 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo 📥 Python 다운로드 페이지를 열고 있습니다...
    start https://www.python.org/downloads/
    echo.
    echo 🔧 Python 설치 후 다시 실행해주세요.
    echo    (설치 시 "Add Python to PATH" 체크 필수!)
    pause
    exit /b 1
) else (
    echo ✅ Python이 설치되어 있습니다.
)

echo.
echo 📦 2단계: 필요한 패키지 설치 중...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 패키지 설치에 실패했습니다.
    echo 💡 인터넷 연결을 확인하고 다시 시도해주세요.
    pause
    exit /b 1
) else (
    echo ✅ 패키지 설치 완료!
)

echo.
echo 🔑 3단계: 네이버 API 키 설정
echo.
echo 📝 네이버 개발자 센터에서 API 키를 발급받아야 합니다:
echo    1. https://developers.naver.com/ 접속
echo    2. 로그인 후 "Application 등록"
echo    3. "검색" API 선택
echo    4. Client ID와 Client Secret 복사
echo.
echo 💡 API 키가 없다면 'N'을 입력하고 나중에 설정하세요.
echo.
set /p has_api="API 키가 있습니까? (Y/N): "

if /i "%has_api%"=="Y" (
    echo.
    set /p client_id="Client ID를 입력하세요: "
    set /p client_secret="Client Secret을 입력하세요: "
    
    echo NAVER_CLIENT_ID=!client_id! > .env
    echo NAVER_CLIENT_SECRET=!client_secret! >> .env
    echo ✅ API 키 설정 완료!
) else (
    echo # 네이버 API 키를 입력하세요 > .env
    echo NAVER_CLIENT_ID=여기에_클라이언트_ID_입력 >> .env
    echo NAVER_CLIENT_SECRET=여기에_클라이언트_시크릿_입력 >> .env
    echo ⚠️ 나중에 .env 파일을 수정하여 API 키를 입력하세요.
)

echo.
echo 📋 4단계: 키워드 파일 설정
echo.
echo keywords.csv 파일을 확인하고 원하는 검색어로 수정하세요.
echo 현재는 한의원 예제로 설정되어 있습니다.

echo.
echo 🖥️ 5단계: 바탕화면 바로가기 생성
copy "현업용_간편실행.bat" "%USERPROFILE%\Desktop\순위체크.bat" >nul 2>&1
if %errorlevel% eq 0 (
    echo ✅ 바탕화면에 '순위체크.bat' 바로가기가 생성되었습니다!
) else (
    echo ⚠️ 바로가기 생성에 실패했습니다.
)

echo.
echo 🎉 설치 완료!
echo ════════════════════════════════════════════════════════
echo.
echo 📋 사용 방법:
echo    1. 바탕화면의 '순위체크.bat' 더블클릭
echo    2. 메뉴에서 원하는 기능 선택
echo    3. 첫 실행 시 "4번" 선택하여 데이터 수집
echo.
echo 📊 결과 확인:
echo    - 빠른 확인: 메뉴 1번
echo    - Excel 리포트: 메뉴 3번  
echo    - 웹 대시보드: 메뉴 5번
echo.
echo 🔧 설정 파일:
echo    - keywords.csv: 검색 키워드 설정
echo    - .env: 네이버 API 키 설정
echo.
echo ════════════════════════════════════════════════════════
echo.

pause
