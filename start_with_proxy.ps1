# 快速启动脚本（带代理）

# 如果你有代理服务（例如 Clash、V2Ray 等），修改下面的代理地址
# 常见代理端口：
# - Clash: 7890
# - V2Ray: 10809
# - 其他代理软件请查看其配置

$PROXY_URL = "http://127.0.0.1:7890"

Write-Host "正在启动 Gemini Web2API 服务（带代理）..."
Write-Host "代理地址: $PROXY_URL"
Write-Host ""
Write-Host "如果代理地址不正确，请编辑此脚本修改 PROXY_URL 变量"
Write-Host ""

# 停止已有服务
$port = 8081
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($process) {
    Write-Host "停止旧服务 (PID: $process)..."
    Stop-Process -Id $process -Force
    Start-Sleep -Seconds 2
}

# 启动新服务
Write-Host "启动服务..."
py gemini_web2api.py --proxy $PROXY_URL
