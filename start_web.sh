#!/bin/bash
# LinkedIn 招聘系统 Web 服务启动脚本

echo "=================================="
echo "LinkedIn 招聘系统 - Web 服务"
echo "=================================="
echo ""
echo "正在启动服务..."
echo ""

cd "$(dirname "$0")"

# 启动 Flask 服务器
python3 web_server.py
