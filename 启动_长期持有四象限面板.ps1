$ErrorActionPreference = "Stop"

$scriptDir = "G:\Codex\个人\investment\static\long-hold-quadrant"
$pythonScript = Join-Path $scriptDir "build_quadrant_data.py"

Write-Host "正在生成最新数据..." -ForegroundColor Cyan
python $pythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "数据生成失败，请检查 Python 脚本或 Excel 路径。" -ForegroundColor Red
    exit 1
}

Write-Host "数据生成成功。正在启动本地服务器..." -ForegroundColor Green
Set-Location $scriptDir

# 随机选一个端口或固定 8081
$port = 8081
$url = "http://localhost:$port"

Write-Host "========================================="
Write-Host "面板已启动！请在浏览器中打开: $url" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 停止服务器"
Write-Host "========================================="

Start-Process $url

# 使用 python 内置的 http.server
python -m http.server $port
