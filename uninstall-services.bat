@echo off
chcp 65001 >nul
title GeniusQA 服务卸载
echo ================================================
echo  卸载 GeniusQA 持久化服务
echo ================================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 需要管理员权限！
    pause
    exit /b 1
)

:: 卸载计划任务
echo [1/4] 删除计划任务...
schtasks /delete /tn "GeniusQA-Backend" /f >nul 2>&1 && echo   ✓ GeniusQA-Backend 已删除 || echo   - 计划任务不存在

:: 卸载 HKLM\Run 项
echo [2/4] 删除 HKLM\Run 注册表项...
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "GeniusQA Master" /f >nul 2>&1 && echo   ✓ GeniusQA Master 已删除 || echo   - 注册表项不存在

:: 恢复 Windows 服务手动启动
echo [3/4] 恢复 MySQL/Redis 为手动启动...
sc config MySQL84 start=demand >nul 2>&1 && echo   ✓ MySQL84 改为手动
sc config Redis start=demand >nul 2>&1 && echo   ✓ Redis 改为手动

:: 停止所有服务
echo [4/4] 停止所有 GeniusQA 服务...
taskkill /f /im minio.exe >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq *Backend*" >nul 2>&1
schtasks /end /tn "GeniusQA-Backend" >nul 2>&1
echo   ✓ 所有服务已停止

echo.
echo 卸载完成！
pause