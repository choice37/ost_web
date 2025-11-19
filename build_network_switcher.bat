@echo off
chcp 65001
echo ================================================
echo IP 전환 프로그램 실행 파일 빌드 (ip_ch.exe)
echo ================================================
echo.

echo [1/3] PyInstaller 설치 확인 중...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
) else (
    echo ✓ PyInstaller가 이미 설치되어 있습니다.
)
echo.

echo [2/3] 이전 빌드 파일 정리 중...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"
echo ✓ 정리 완료
echo.

echo [3/3] 실행 파일 생성 중...
pyinstaller --onefile ^
    --windowed ^
    --name "ip_ch" ^
    --icon=NONE ^
    --hidden-import=tkinter ^
    --hidden-import=json ^
    --hidden-import=subprocess ^
    network_switcher.py

if errorlevel 1 (
    echo.
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✓ 빌드 완료!
echo ================================================
echo.
echo 실행 파일 위치: dist\ip_ch.exe
echo.
echo 사용 방법:
echo 1. dist\ip_ch.exe 파일을 우클릭
echo 2. "관리자 권한으로 실행" 선택
echo.
echo ※ 이 실행 파일을 실행하면 관리자 권한이 필요합니다.
echo.

pause

