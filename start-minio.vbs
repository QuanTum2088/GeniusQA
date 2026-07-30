Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c D:\GeniusQA\minio\bin\minio.exe server D:\GeniusQA\minio\data --console-address "":9001""", 0, False
