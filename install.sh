#!/bin/bash
# 安装所有依赖包

echo "=================================="
echo "安装 LinkedIn 招聘系统依赖包"
echo "=================================="

cd ~/Desktop/linkedin_recruiter

echo ""
echo "正在安装依赖..."
pip3 install -r requirements.txt

echo ""
echo "=================================="
echo "安装完成！"
echo "=================================="
echo ""
echo "下一步："
echo "1. 运行测试: python3 test_oauth.py"
echo "2. 快速运行: python3 quick_run.py"
echo ""
