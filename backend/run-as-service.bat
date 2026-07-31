@echo off
:: GeniusQA Backend Service - auto restart on crash
chcp 65001 >nul
title GeniusQA Backend Service

set NT_PORTABLE_ROOT=D:\GeniusQA
set FRONTEND_DIST=D:\GeniusQA\frontend\dist

:: ==== Database ====
set MYSQL_DATABASE_URI=mysql+aiomysql://root:86340365@localhost:3306/geniusqa?charset=utf8mb4
set MYSQL_DATABASE_URI_SYNC=mysql+pymysql://root:86340365@localhost:3306/geniusqa?charset=utf8mb4

:: ==== Redis ====
set REDIS_URI=redis://localhost:6379/4
set CELERY_BROKER_URL=redis://localhost:6379/5
set CELERY_RESULT_BACKEND=redis://localhost:6379/5

:: ==== Security ====
set SECRET_KEY=change-me-in-production

:: ==== Watchdog Loop ====
:start
echo [%date% %time%] Starting backend on port 8100...
"D:\GeniusQA\backend\.venv\Scripts\python.exe" "D:\GeniusQA\backend\run_portable.py" > "D:\GeniusQA\logs\backend.log" 2>&1
echo [%date% %time%] Backend exited, restart in 5s...
timeout /t 5 /nobreak >nul
goto start
