#!/bin/bash
# POC: 验证 Claude CLI 自动化调度可行性

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_FILE="$PROJECT_DIR/.dev-state/state.json"
LOG_FILE="$PROJECT_DIR/.dev-state/daemon.log"
MAX_ITERATIONS=5
ITERATION=0

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查状态
get_status() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status', 'unknown'))"
    else
        echo "no_state"
    fi
}

# 主循环
log "========== POC 守护进程启动 =========="
log "项目目录: $PROJECT_DIR"
log "状态文件: $STATE_FILE"

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    log "--- 迭代 #$ITERATION ---"
    
    STATUS=$(get_status)
    log "当前状态: $STATUS"
    
    case $STATUS in
        "ready"|"continue")
            log "调用 Claude CLI..."
            
            # 核心调用命令
            PROMPT="你是一个自动化开发助手。请读取 .dev-state/state.json 文件，执行下一个 pending 状态的任务（创建对应的文件），然后更新 state.json：
1. 将该任务的 status 改为 completed
2. 将 current_task 加 1
3. 如果所有任务完成，将 status 改为 completed，否则改为 continue
4. 更新 last_update 为当前时间

只执行一个任务就停止。"

            # 执行 Claude CLI (非交互模式)
            cd "$PROJECT_DIR"
            
            # 使用 timeout 防止卡死，--max-turns 限制轮次
            if timeout 120 claude -p "$PROMPT" \
                --dangerously-skip-permissions \
                --max-turns 10 \
                --output-format text \
                2>&1 | tee -a "$LOG_FILE"; then
                log "Claude CLI 执行完成"
            else
                EXIT_CODE=$?
                log "Claude CLI 退出，代码: $EXIT_CODE"
                if [ $EXIT_CODE -eq 124 ]; then
                    log "执行超时"
                fi
            fi
            
            # 等待一下再检查状态
            sleep 2
            ;;
            
        "completed")
            log "所有任务已完成！"
            log "========== POC 验证成功 =========="
            exit 0
            ;;
            
        "error")
            log "遇到错误，停止执行"
            exit 1
            ;;
            
        *)
            log "未知状态: $STATUS"
            exit 1
            ;;
    esac
    
    log "等待 3 秒后继续..."
    sleep 3
done

log "达到最大迭代次数 ($MAX_ITERATIONS)，停止"
log "最终状态: $(get_status)"
