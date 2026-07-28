@echo off
chcp 65001 >nul
title N-Tester 源码部署向导
color 0B

echo =========================================
echo   N-Tester 源码部署向导
echo   项目: C:\Users\Administrator\NTester-Source
echo =========================================
echo.
echo [1/4] 激活虚拟环境...
set VENV=C:\Users\Administrator\NTester-Source\backend\.venv
if not exist "%VENV%\Scripts\python.exe" (
    echo [ERROR] 虚拟环境不存在，请先运行: python -m venv %VENV%
    pause
    exit /b 1
)
echo [OK] 虚拟环境已就绪
echo.

echo [2/4] 安装后端依赖（这步可能需要 5-10 分钟，请耐心等待）...
set PIP=%VENV%\Scripts\pip.exe
%PIP% install -i https://mirrors.aliyun.com/pypi/simple ^
    SQLAlchemy==2.0.3 loguru==0.6.0 python-dotenv==1.2.1 ^
    aiomysql==0.3.2 PyMySQL==1.0.2 alembic==1.13.1 ^
    redis==5.0.4 celery==5.2.7 ^
    requests==2.32.5 httpx==0.28.1 aiofiles==25.1.0 ^
    python-jose[cryptography]==3.3.0 passlib==1.7.4 ^
    bcrypt==4.2.0 cryptography==40.0.2 PyJWT==2.11.0 ^
    python-multipart==0.0.20 python-dateutil==2.9.0 ^
    croniter Pillow openpyxl python-docx paramiko ^
    jinja2 email-validator pyyaml --timeout 300
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 部分安装失败，继续尝试启动...
)
echo.

echo [3/4] 启动后端服务...
set NT_PORTABLE_ROOT=C:\Users\Administrator\NTester-Source
cd /d C:\Users\Administrator\NTester-Source
if not exist logs mkdir logs
start "NTest-Backend" /MIN cmd /c ""%VENV%\Scripts\python.exe" "C:\Users\Administrator\NTester-Source\backend\run_portable.py" > "C:\Users\Administrator\NTester-Source\logs\backend_out.log" 2>&1"
echo.
echo 后端启动中，等待 8 秒...
ping -n 8 127.0.0.1 >nul
echo.

echo [4/4] 验证服务...
for /f %%i in ('powershell -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8100/api/v1/projects/?page=1' -TimeoutSec 5 -UseBasicParsing).StatusCode } catch { echo 0 }"') do set STATUS=%%i
if "%STATUS%"=="422" (
    echo =========================================
    echo   [OK] 后端启动成功! (8100 端口)
    echo.
    echo   访问地址: http://localhost:8100
    echo   局域网:   http://192.168.1.4:8100
    echo   前端:     待后续 Nginx 配置
    echo =========================================
) else (
    echo [FAIL] 后端启动失败，错误日志:
    type "C:\Users\Administrator\NTester-Source\logs\backend_out.log"
)
echo.
echo 更多 Python 依赖安装: 打开 cmd 执行:
echo   %PIP% install -i https://mirrors.aliyun.com/pypi/simple -r C:\Users\Administrator\NTester-Source\backend\requirements-windows.utf8.txt
echo.
pause
