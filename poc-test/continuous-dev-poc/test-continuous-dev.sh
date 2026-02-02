#!/bin/bash
# POC 测试: continuous-dev 持续运行验证
# 测试目标: 验证守护进程能否正确循环调用 Claude CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/test-project"
CONTINUOUS_DEV="$SCRIPT_DIR/../../skills/continuous-dev-loop/scripts/continuous-dev"

echo "=========================================="
echo "POC: continuous-dev 持续运行测试"
echo "=========================================="
echo ""

# 清理
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "1. 测试初始化..."
"$CONTINUOUS_DEV" start "POC测试项目"

sleep 3

echo ""
echo "2. 检查状态..."
"$CONTINUOUS_DEV" status

echo ""
echo "3. 检查状态文件..."
if [ -f ".dev-state/state.json" ]; then
    echo "✅ state.json 已创建"
    cat .dev-state/state.json
else
    echo "❌ state.json 未创建"
    exit 1
fi

echo ""
echo "4. 检查守护进程..."
if [ -f ".dev-state/daemon.pid" ]; then
    PID=$(cat .dev-state/daemon.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ 守护进程运行中 (PID: $PID)"
    else
        echo "❌ 守护进程未运行"
    fi
else
    echo "❌ PID 文件不存在"
fi

echo ""
echo "5. 等待第一次会话 (最多 30 秒)..."
for i in {1..30}; do
    if [ -f ".dev-state/logs/daemon.log" ] && grep -q "启动会话" ".dev-state/logs/daemon.log" 2>/dev/null; then
        echo "✅ 会话已启动"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

echo ""
echo "6. 查看日志..."
if [ -f ".dev-state/logs/daemon.log" ]; then
    echo "--- daemon.log ---"
    tail -20 .dev-state/logs/daemon.log
fi

echo ""
echo "7. 停止守护进程..."
"$CONTINUOUS_DEV" stop

echo ""
echo "8. 检查会话日志..."
SESSION_LOG=$(ls -t .dev-state/logs/session-*.log 2>/dev/null | head -1)
if [ -n "$SESSION_LOG" ]; then
    echo "✅ 会话日志已创建: $SESSION_LOG"
    echo "--- 会话日志前 50 行 ---"
    head -50 "$SESSION_LOG"
else
    echo "⚠️  无会话日志 (可能会话未完成)"
fi

echo ""
echo "=========================================="
echo "POC 测试完成"
echo "=========================================="
