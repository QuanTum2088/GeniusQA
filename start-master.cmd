@echo off
chcp 65001 >nul
title GeniusQA Master Startup
echo ================================================
echo  GeniusQA Master Startup - Additional Services
echo ================================================
echo.

:: ========== Step 1: Check MySQL ==========
echo [1/4] Checking MySQL service...
sc query MySQL84 | find "RUNNING" >nul 2>&1 && echo   MySQL84 is running || echo   MySQL84 not running

:: ========== Step 2: Check Redis ==========
echo [2/4] Checking Redis service...
sc query Redis | find "RUNNING" >nul 2>&1 && echo   Redis is running || echo   Redis not running

:: ========== Step 3: Start MinIO ==========
echo [3/4] Starting MinIO (port 9000)...
powershell -WindowStyle Hidden -Command "Start-Process -FilePath 'D:\GeniusQA\minio\bin\minio.exe' -ArgumentList 'server','D:\GeniusQA\minio\data','--console-address',':9001','--quiet' -WindowStyle Hidden -RedirectStandardOutput 'D:\GeniusQA\logs\minio.log' -RedirectStandardError 'D:\GeniusQA\logs\minio.err.log'"

:: ========== Step 4: Start Playwright MCP ==========
echo [4/4] Starting Playwright MCP (port 8080)...
powershell -WindowStyle Hidden -Command "Start-Process -FilePath 'D:\Node.js\node.exe' -ArgumentList 'D:\GeniusQA\backend\.venv\Lib\site-packages\playwright-mcp\node_modules\@playwright\mcp\cli.js','--host','0.0.0.0','--port','8080','--headless','--allowed-hosts','*','--allow-unrestricted-file-access' -WindowStyle Hidden -RedirectStandardOutput 'D:\GeniusQA\logs\playwright-mcp.log' -RedirectStandardError 'D:\GeniusQA\logs\playwright-mcp.err.log'"

echo.
echo ================================================
echo  Additional services started!
echo  Backend is managed by Windows Scheduled Task (GeniusQA-Backend)
echo  Access: http://192.168.1.4
echo ================================================
exit
