Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c D:\Node.js\node.exe D:\GeniusQA\backend\.venv\Lib\site-packages\playwright-mcp\node_modules\@playwright\mcp\cli.js --host 0.0.0.0 --port 8080 --headless --allowed-hosts * --allow-unrestricted-file-access", 0, False
