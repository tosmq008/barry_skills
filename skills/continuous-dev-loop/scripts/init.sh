#!/bin/bash
# 初始化持续开发状态 v2.0

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(pwd)"

source "$SCRIPT_DIR/config.env" 2>/dev/null || true

STATE_DIR="${STATE_DIR:-.dev-state}"
PROJECT_NAME="${1:-未命名项目}"
PROJECT_DESC="${2:-}"

echo "=========================================="
echo "初始化持续开发环境 v2.0"
echo "=========================================="
echo "项目目录: $PROJECT_DIR"
echo "项目名称: $PROJECT_NAME"
echo ""

# 创建目录结构
mkdir -p "$STATE_DIR"/{sessions,checkpoints,logs}

# 生成初始状态
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$STATE_DIR/state.json" << EOF
{
  "version": "2.0.0",
  "project": {
    "name": "$PROJECT_NAME",
    "description": "$PROJECT_DESC",
    "created_at": "$TIMESTAMP"
  },
  "workflow": {
    "current_phase": "development",
    "phase_status": {
      "development": "pending",
      "testing": "pending",
      "bugfix": "pending",
      "regression": "pending"
    },
    "iteration": 1
  },
  "status": "ready",
  "exit_reason": null,
  "current_task": {
    "id": "INIT",
    "phase": "development",
    "skill": "rapid-prototype-workflow",
    "name": "开始开发",
    "sub_task": "1.1",
    "started_at": null,
    "checkpoint": null,
    "retry_count": 0
  },
  "task_queue": [],
  "completed_tasks": [],
  "progress": {
    "development": {"total": 0, "completed": 0, "failed": 0},
    "testing": {"total": 0, "completed": 0, "failed": 0},
    "bugfix": {"total": 0, "completed": 0, "failed": 0},
    "regression": {"total": 0, "completed": 0, "failed": 0}
  },
  "sessions": {
    "active": [],
    "total_count": 0,
    "total_turns": 0
  },
  "rate_limit": {
    "last_call": null,
    "consecutive_limits": 0,
    "backoff_until": null
  },
  "last_heartbeat": "$TIMESTAMP",
  "last_checkpoint": null,
  "errors": []
}
EOF

# 初始化日志
echo "[$TIMESTAMP] 项目初始化: $PROJECT_NAME" > "$STATE_DIR/logs/daemon.log"

# 复制配置
if [ ! -f "scripts/config.env" ]; then
    mkdir -p scripts
    cp "$SCRIPT_DIR/config.env" scripts/ 2>/dev/null || true
fi

echo "✅ 初始化完成"
echo ""
echo "目录结构:"
echo "  $STATE_DIR/"
echo "  ├── state.json        # 主状态文件"
echo "  ├── sessions/         # 会话状态"
echo "  ├── checkpoints/      # 断点快照"
echo "  └── logs/             # 运行日志"
echo ""
echo "下一步: ./scripts/start.sh"
