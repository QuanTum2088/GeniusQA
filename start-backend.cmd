@echo off
chcp 65001 >nl
echo ========================================
echo  N-Tester Backend - D:\GeniusQA
echo ========================================

set NT_PORTABLE_ROOT=D:\GeniusQA
set LOGS=D:\GeniusQA\logs
if not exist %LOGS% mkdir %LOGS%

echo Starting backend on port 80...
start "NTest-Backend" /MIN "D:\GeniusQA\backend\.venv\Scripts\python.exe" "D:\GeniusQA\backend\run_portable.py"

echo Waiting 8 seconds for startup...
ping -n 8 127.0.0.1 >nul

echo Testing...
for /f %%i in ('powershell -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1/' -TimeoutSec 5 -UseBasicParsing).StatusCode } catch { echo 0 }"') do set RESULT=%%i
if "%RESULT%"=="200" (
    echo [OK] Backend+Frontend is running at http://127.0.0.1
) else (
    echo [INFO] Status code: %RESULT%
)

echo.
echo Backend started. Access: http://192.168.1.4
