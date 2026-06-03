#!/bin/bash
# 快速启动脚本（带代理）

# 如果你有代理服务（例如 Clash、V2Ray 等），修改下面的代理地址
# 常见代理端口：
# - Clash: 7890
# - V2Ray: 10809
# - 其他代理软件请查看其配置

PROXY_URL="http://127.0.0.1:7890"

echo "正在启动 Gemini Web2API 服务（带代理）..."
echo "代理地址: $PROXY_URL"
echo ""
echo "如果代理地址不正确，请编辑此脚本修改 PROXY_URL 变量"
echo ""

# 启动服务
py gemini_web2api.py --proxy $PROXY_URL
