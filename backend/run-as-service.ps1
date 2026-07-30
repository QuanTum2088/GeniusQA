# GeniusQA 后端 PowerShell 守护进程
$env:MYSQL_DATABASE_URI = "mysql+aiomysql://root:86340365@localhost:3306/geniusqa?charset=utf8mb4"
$env:MYSQL_DATABASE_URI_SYNC = "mysql+pymysql://root:86340365@localhost:3306/geniusqa?charset=utf8mb4"
$env:REDIS_URI = "redis://localhost:6379/4"
$env:CELERY_BROKER_URL = "redis://localhost:6379/5"
$env:CELERY_RESULT_BACKEND = "redis://localhost:6379/5"
$env:SECRET_KEY = "change-me-in-production"

while ($true) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 启动后端..."
    try {
        & "D:\GeniusQA\backend\.venv\Scripts\python.exe" "D:\GeniusQA\backend\run_portable.py"
    } catch {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 错误: $_"
    }
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 后端退出，5秒后重启..."
    Start-Sleep 5
}