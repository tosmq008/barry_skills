#!/bin/bash
# POC 测试脚本 - 管道方式
# 使用方法: cd /Users/yinlianbang/work_ai/barry_skills/poc-test && ./run-poc-pipe.sh

echo "=========================================="
echo "Claude CLI POC 测试 (管道方式)"
echo "=========================================="

rm -f result.txt 2>/dev/null

WORK_DIR="$(pwd)"
echo "工作目录: $WORK_DIR"
echo ""

# 使用管道传入 prompt
echo "请创建文件 ${WORK_DIR}/result.txt，内容为 POC_SUCCESS" | \
  claude --print --dangerously-skip-permissions --max-turns 5

echo ""
echo "=========================================="
if [ -f "result.txt" ]; then
    echo "✅ 成功！内容: $(cat result.txt)"
else
    echo "❌ 文件未创建"
fi
echo "=========================================="
