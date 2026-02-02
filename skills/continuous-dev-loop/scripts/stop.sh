#!/bin/bash
# 停止持续开发守护进程

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.env" 2>/dev/null || true

STATE_DIR="${STATE_DIR:-.dev-state}"
PID_FILE="${STATE_DIR}/daemon.pid"

echo "=========================================="
echo "停止持续开发守护进程"
echo "=========================================="

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  守护进程未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "停止守护进程 (PID: $PID)..."
    kill "$PID" 2>/dev/null
    
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "强制终止..."
        kill -9 "$PID" 2>/dev/null
    fi
    
    echo "✅ 守护进程已停止"
else
    echo "⚠️  进程 $PID 不存在"
fi

rm -f "$PID_FILE"
