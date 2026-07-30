@echo off
chcp 65001 >nul
echo Installing missing packages...
D:\Python\python.exe -m pip install jsonpath-ng dictdiffer faker psutil typer jmespath user-agents --no-deps
echo Done. Starting backend...
D:\Python\python.exe D:\GeniusQA\backend\run_portable.py
pause
