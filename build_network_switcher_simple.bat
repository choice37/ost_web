@echo off
chcp 65001
echo ================================================
echo IP 전환 프로그램 실행 파일 생성 (ip_ch.exe)
echo ================================================
echo.

echo [1/2] PyInstaller 설치 확인...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 설치 중...
    pip install pyinstaller
) else (
    echo 이미 설치되어 있습니다.
)
echo.

echo [2/2] 실행 파일 생성 중...
REM 이전 빌드 파일 삭제
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

REM 실행 파일 생성
pyinstaller --onefile --windowed --name "ip_ch" network_switcher.py

echo.
if exist "dist\ip_ch.exe" (
    echo ================================================
    echo ✓ 생성 완료!
    echo ================================================
    echo.
    echo 실행 파일 위치: dist\ip_ch.exe
    echo.
    echo 사용 방법:
    echo 1. dist\ip_ch.exe 파일을 우클릭
    echo 2. "관리자 권한으로 실행" 선택
    echo.
) else (
    echo ❌ 실행 파일 생성 실패!
)

pause

