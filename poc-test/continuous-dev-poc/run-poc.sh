#!/bin/bash
# 简化 POC: 在系统终端运行此脚本
# 用法: cd poc-test/continuous-dev-poc && ./run-poc.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "POC: continuous-dev 测试"
echo "=========================================="

# 清理测试目录
rm -rf test-project
mkdir -p test-project
cd test-project

CONTINUOUS_DEV="$SCRIPT_DIR/../../skills/continuous-dev-loop/scripts/continuous-dev"

echo ""
echo "Step 1: 启动..."
"$CONTINUOUS_DEV" start "POC项目"

echo ""
echo "Step 2: 等待 10 秒让会话启动..."
sleep 10

echo ""
echo "Step 3: 查看状态..."
"$CONTINUOUS_DEV" status

echo ""
echo "Step 4: 查看日志..."
echo "--- daemon.log ---"
tail -30 .dev-state/logs/daemon.log 2>/dev/null || echo "(无日志)"

echo ""
echo "Step 5: 停止..."
"$CONTINUOUS_DEV" stop

echo ""
echo "Step 6: 检查会话日志..."
if ls .dev-state/logs/session-*.log 1>/dev/null 2>&1; then
    echo "✅ 会话日志存在"
    echo "--- 最新会话日志 ---"
    tail -50 "$(ls -t .dev-state/logs/session-*.log | head -1)"
else
    echo "⚠️  无会话日志"
fi

echo ""
echo "=========================================="
echo "POC 完成"
echo "=========================================="
