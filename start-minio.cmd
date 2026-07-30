@echo off
powershell -WindowStyle Hidden -Command "Start-Process -FilePath 'D:\GeniusQA\minio\bin\minio.exe' -ArgumentList 'server','D:\GeniusQA\minio\data','--console-address',':9001','--quiet' -WindowStyle Hidden"
