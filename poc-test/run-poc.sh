#!/bin/bash
# POC 测试脚本 - 请在系统终端中运行
# 使用方法: cd /Users/yinlianbang/work_ai/barry_skills/poc-test && ./run-poc.sh

echo "=========================================="
echo "Claude CLI POC 测试"
echo "=========================================="

rm -f result.txt 2>/dev/null

WORK_DIR="$(pwd)"
echo "工作目录: $WORK_DIR"
echo ""

# 方式1: prompt 作为位置参数放最后
echo "执行 Claude CLI..."
claude --print --dangerously-skip-permissions --max-turns 5 "请创建文件 ${WORK_DIR}/result.txt，内容为 POC_SUCCESS"

echo ""
echo "=========================================="
if [ -f "result.txt" ]; then
    echo "✅ 成功！内容: $(cat result.txt)"
else
    echo "❌ 文件未创建"
fi
echo "=========================================="
