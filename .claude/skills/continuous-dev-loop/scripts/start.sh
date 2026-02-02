#!/bin/bash
# 启动持续开发守护进程 v2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.env" 2>/dev/null || true

STATE_DIR="${STATE_DIR:-.dev-state}"
PID_FILE="${STATE_DIR}/daemon.pid"
LOG_FILE="${STATE_DIR}/logs/daemon.log"

echo "=========================================="
echo "启动持续开发守护进程"
echo "=========================================="

# 检查状态目录
if [ ! -d "$STATE_DIR" ]; then
    echo "❌ 状态目录不存在，请先运行 init.sh"
    exit 1
fi

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  守护进程已在运行 (PID: $OLD_PID)"
        echo "如需重启，请先运行 ./scripts/stop.sh"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

# 确保日志目录存在
mkdir -p "$STATE_DIR/logs" "$STATE_DIR/checkpoints"

# 启动守护进程
echo "启动守护进程..."
nohup "$SCRIPT_DIR/daemon.sh" >> "$LOG_FILE" 2>&1 &
DAEMON_PID=$!
echo $DAEMON_PID > "$PID_FILE"

sleep 3

if ps -p $DAEMON_PID > /dev/null 2>&1; then
    echo ""
    echo "✅ 守护进程已启动"
    echo "   PID: $DAEMON_PID"
    echo ""
    echo "常用命令:"
    echo "  查看状态: ./scripts/status.sh"
    echo "  查看日志: tail -f $LOG_FILE"
    echo "  暂停:     ./scripts/pause.sh"
    echo "  停止:     ./scripts/stop.sh"
else
    echo "❌ 启动失败，请检查日志"
    tail -20 "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
