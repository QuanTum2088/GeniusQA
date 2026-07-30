@echo off
chcp 65001 >nul
echo Installing all missing packages for backend...
echo.

D:\Python\python.exe -m pip install ply apscheduler dictdiffer psutil typer jmespath user-agents ua-parser xmltodict paramiko langchain langchain-openai langgraph langchain-mcp-adapters openai anthropic browser-use faker 2>&1

echo.
echo Installing AI/ML packages done.
echo Starting backend...
D:\Python\python.exe D:\GeniusQA\backend\run_portable.py
pause