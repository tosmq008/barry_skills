#!/bin/bash
# 持续开发守护进程 v2.0
# 支持多 Skill 协调、限流保护、中断恢复

# 注意: 不使用 set -e，守护进程需要持续运行并自行处理错误

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(pwd)"

# 加载配置
source "$SCRIPT_DIR/config.env" 2>/dev/null || true

# 默认配置
STATE_DIR="${STATE_DIR:-.dev-state}"
STATE_FILE="${STATE_DIR}/state.json"
LOG_DIR="${STATE_DIR}/logs"
CHECKPOINT_DIR="${STATE_DIR}/checkpoints"

MAX_TURNS="${MAX_TURNS:-50}"
MAX_PARALLEL_SESSIONS="${MAX_PARALLEL_SESSIONS:-3}"
MIN_SESSION_INTERVAL="${MIN_SESSION_INTERVAL:-60}"
MAX_SESSION_INTERVAL="${MAX_SESSION_INTERVAL:-120}"
RATE_LIMIT_WAIT="${RATE_LIMIT_WAIT:-300}"
RATE_LIMIT_BACKOFF="${RATE_LIMIT_BACKOFF:-1.5}"
MAX_RETRIES="${MAX_RETRIES:-3}"
MAX_CONSECUTIVE_ERRORS="${MAX_CONSECUTIVE_ERRORS:-5}"
HEARTBEAT_TIMEOUT="${HEARTBEAT_TIMEOUT:-600}"

# 运行时变量
CONSECUTIVE_ERRORS=0
RATE_LIMIT_COUNT=0
ACTIVE_SESSIONS=0

# ============================================
# 工具函数
# ============================================

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/daemon.log"
}

get_json() {
    python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d$1)" 2>/dev/null
}

set_json() {
    python3 << EOF
import json
with open('$STATE_FILE', 'r') as f:
    d = json.load(f)
$1
with open('$STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
EOF
}

update_heartbeat() {
    local ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    set_json "d['last_heartbeat']='$ts'"
}

save_checkpoint() {
    local ts=$(date +%Y%m%d_%H%M%S)
    cp "$STATE_FILE" "$CHECKPOINT_DIR/checkpoint-$ts.json"
    cp "$STATE_FILE" "$CHECKPOINT_DIR/latest.json"
    log "INFO" "保存断点: checkpoint-$ts.json"
}

random_interval() {
    echo $(( MIN_SESSION_INTERVAL + RANDOM % (MAX_SESSION_INTERVAL - MIN_SESSION_INTERVAL + 1) ))
}

send_alert() {
    local level="$1"
    local message="$2"
    log "$level" "ALERT: $message"
    
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -s -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"[$level] $message\"}" > /dev/null 2>&1 || true
    fi
}

cleanup_old_logs() {
    # 保留最近 7 天的日志和 checkpoint
    local days_to_keep=7
    
    # 清理旧的会话日志
    find "$LOG_DIR" -name "session-*.log" -mtime +$days_to_keep -delete 2>/dev/null || true
    
    # 清理旧的 checkpoint (保留 latest)
    find "$CHECKPOINT_DIR" -name "checkpoint-*.json" -mtime +$days_to_keep -delete 2>/dev/null || true
    
    log "DEBUG" "已清理 ${days_to_keep} 天前的日志和断点"
}

# ============================================
# Skill 映射
# ============================================

get_skill_for_phase() {
    local phase="$1"
    case "$phase" in
        "development") echo "rapid-prototype-workflow" ;;
        "testing")     echo "test-expert" ;;
        "bugfix")      echo "test-report-followup" ;;
        "regression")  echo "test-expert" ;;
        *)             echo "rapid-prototype-workflow" ;;
    esac
}

get_prompt_for_phase() {
    local phase="$1"
    local skill=$(get_skill_for_phase "$phase")
    local task_name=$(get_json "['current_task']['name']" 2>/dev/null || echo "继续任务")
    local checkpoint=$(get_json "['current_task']['checkpoint']" 2>/dev/null || echo "null")
    local project_name=$(get_json "['project']['name']" 2>/dev/null || echo "项目")
    
    cat << EOF
你是持续开发助手，正在执行 7×24 自动化开发任务。

## 项目信息
- 项目名称: $project_name
- 项目目录: $PROJECT_DIR
- 状态文件: $PROJECT_DIR/$STATE_FILE

## 当前状态
- 当前阶段: $phase
- 当前任务: $task_name
- 断点信息: $checkpoint

## 使用的 Skill
请使用 **$skill** skill 执行任务。
如果项目中有 .claude/skills/$skill/SKILL.md，请先阅读该文件了解 skill 规范。

## 执行要求
1. **首先**读取 $PROJECT_DIR/$STATE_FILE 获取完整状态
2. **从断点继续**，不要重复已完成的工作
3. 每完成一个步骤，**立即更新** state.json:
   - last_heartbeat: 当前 UTC 时间 (格式: YYYY-MM-DDTHH:MM:SSZ)
   - current_task.checkpoint: 当前进度详情 (包含 step, file, context)
4. 任务完成时:
   - 更新 progress 中对应阶段的 completed 计数
   - 设置下一个任务到 current_task
   - 设置 status="continue", exit_reason="task_done"
5. 达到轮次限制前 (约 ${MAX_TURNS} 轮的 80%):
   - 保存详细断点信息到 checkpoint
   - 设置 status="continue", exit_reason="turns_limit"
   - 主动结束会话

## 阶段流转规则
- development 完成 → 设置 workflow.current_phase="testing"
- testing 有 Bug → 设置 workflow.current_phase="bugfix"
- testing 无 Bug → 设置 status="completed"
- bugfix 完成 → 设置 workflow.current_phase="regression"
- regression 通过 → 设置 status="completed"
- regression 有新 Bug → 设置 workflow.current_phase="bugfix", iteration++

## 重要提醒
- 所有文件路径使用绝对路径: $PROJECT_DIR/...
- 状态更新必须写入文件，不能只在内存中
- 遇到错误时记录到 state.json 的 errors 数组

请开始执行。
EOF
}

# ============================================
# Claude CLI 调用
# ============================================

run_claude_session() {
    local phase=$(get_json "['workflow']['current_phase']" 2>/dev/null || echo "development")
    local skill=$(get_skill_for_phase "$phase")
    local prompt=$(get_prompt_for_phase "$phase")
    
    log "INFO" "启动会话 - 阶段: $phase, Skill: $skill"
    
    # 更新状态
    set_json "d['status']='running'"
    update_heartbeat
    
    # 更新会话计数
    set_json "d['sessions']['total_count'] = d['sessions'].get('total_count', 0) + 1"
    
    # 构建命令
    local cmd="claude --print --dangerously-skip-permissions --max-turns $MAX_TURNS"
    
    # 执行 - 使用独立日志文件
    local session_id="session-$(date +%Y%m%d_%H%M%S)"
    local output_file="$LOG_DIR/${session_id}.log"
    
    # 写入会话头
    echo "=========================================" > "$output_file"
    echo "会话ID: $session_id" >> "$output_file"
    echo "阶段: $phase" >> "$output_file"
    echo "Skill: $skill" >> "$output_file"
    echo "开始时间: $(date)" >> "$output_file"
    echo "=========================================" >> "$output_file"
    echo "" >> "$output_file"
    
    local start_time=$(date +%s)
    
    if $cmd "$prompt" >> "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "INFO" "会话正常结束, 耗时: ${duration}s"
        CONSECUTIVE_ERRORS=0
        RATE_LIMIT_COUNT=0
        return 0
    else
        local exit_code=$?
        log "WARN" "会话异常退出, 代码: $exit_code"
        
        # 检查是否是限流
        if grep -qi "rate.limit\|too.many.requests\|429" "$output_file" 2>/dev/null; then
            RATE_LIMIT_COUNT=$((RATE_LIMIT_COUNT + 1))
            log "WARN" "检测到限流 (第 $RATE_LIMIT_COUNT 次)"
            set_json "d['exit_reason']='rate_limit'"
            return 2
        fi
        
        CONSECUTIVE_ERRORS=$((CONSECUTIVE_ERRORS + 1))
        return $exit_code
    fi
}

# ============================================
# 限流处理
# ============================================

handle_rate_limit() {
    # 使用 Python 计算，避免 bc 依赖
    local wait_time=$(python3 -c "print(int(min($RATE_LIMIT_WAIT * ($RATE_LIMIT_BACKOFF ** $RATE_LIMIT_COUNT), 1800)))" 2>/dev/null || echo $RATE_LIMIT_WAIT)
    
    log "WARN" "限流处理: 等待 ${wait_time} 秒 (第 $RATE_LIMIT_COUNT 次)"
    set_json "d['rate_limit']['consecutive_limits']=$RATE_LIMIT_COUNT"
    
    sleep $wait_time
}

# ============================================
# 主循环
# ============================================

main_loop() {
    log "INFO" "=========================================="
    log "INFO" "守护进程启动 v2.0"
    log "INFO" "项目目录: $PROJECT_DIR"
    log "INFO" "最大轮次: $MAX_TURNS"
    log "INFO" "会话间隔: ${MIN_SESSION_INTERVAL}-${MAX_SESSION_INTERVAL}s"
    log "INFO" "=========================================="
    
    local loop_count=0
    
    while true; do
        loop_count=$((loop_count + 1))
        
        # 每 100 次循环清理一次旧日志
        if [ $((loop_count % 100)) -eq 0 ]; then
            cleanup_old_logs
        fi
        # 检查状态文件
        if [ ! -f "$STATE_FILE" ]; then
            log "ERROR" "状态文件不存在"
            sleep 60
            continue
        fi
        
        local status=$(get_json "['status']" 2>/dev/null || echo "unknown")
        local exit_reason=$(get_json "['exit_reason']" 2>/dev/null || echo "")
        
        log "DEBUG" "状态: $status, 退出原因: $exit_reason"
        
        case "$status" in
            "ready"|"continue")
                # 检查限流
                if [ "$exit_reason" = "rate_limit" ]; then
                    handle_rate_limit
                fi
                
                # 保存断点
                save_checkpoint
                
                # 运行会话
                run_claude_session
                local result=$?
                
                if [ $result -eq 2 ]; then
                    # 限流，等待后重试
                    handle_rate_limit
                fi
                
                # 随机间隔，防止限流
                local interval=$(random_interval)
                log "INFO" "等待 ${interval} 秒后继续..."
                sleep $interval
                ;;
                
            "running")
                # 检查心跳 - 使用 Python 处理时间，兼容 macOS/Linux
                local last_hb=$(get_json "['last_heartbeat']" 2>/dev/null)
                if [ -n "$last_hb" ]; then
                    local age=$(python3 -c "
from datetime import datetime, timezone
try:
    hb = datetime.fromisoformat('$last_hb'.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    print(int((now - hb).total_seconds()))
except:
    print(0)
" 2>/dev/null || echo 0)
                    
                    if [ "$age" -gt "$HEARTBEAT_TIMEOUT" ]; then
                        log "WARN" "心跳超时 (${age}s > ${HEARTBEAT_TIMEOUT}s), 尝试恢复"
                        set_json "d['status']='continue'; d['exit_reason']='heartbeat_timeout'"
                    fi
                fi
                sleep 30
                ;;
                
            "paused")
                log "INFO" "状态: paused, 等待手动恢复"
                sleep 60
                ;;
                
            "completed")
                log "INFO" "=========================================="
                log "INFO" "所有任务完成！"
                log "INFO" "=========================================="
                send_alert "INFO" "持续开发完成"
                exit 0
                ;;
                
            "error")
                if [ $CONSECUTIVE_ERRORS -ge $MAX_CONSECUTIVE_ERRORS ]; then
                    log "ERROR" "连续错误过多 ($CONSECUTIVE_ERRORS), 停止"
                    send_alert "ERROR" "连续错误过多，已停止"
                    exit 1
                fi
                
                log "WARN" "错误状态，尝试恢复..."
                set_json "d['status']='continue'"
                sleep 60
                ;;
                
            *)
                log "WARN" "未知状态: $status"
                sleep 30
                ;;
        esac
        
        # 连续错误检查
        if [ $CONSECUTIVE_ERRORS -ge $MAX_CONSECUTIVE_ERRORS ]; then
            log "ERROR" "连续错误过多，停止"
            send_alert "ERROR" "连续错误过多"
            exit 1
        fi
    done
}

# ============================================
# 入口
# ============================================

# 环境检查
check_environment() {
    # 检查 Python3
    if ! command -v python3 &> /dev/null; then
        echo "ERROR: python3 未安装"
        exit 1
    fi
    
    # 检查 Claude CLI
    if ! command -v claude &> /dev/null; then
        echo "ERROR: claude CLI 未安装"
        exit 1
    fi
    
    # 检查状态文件
    if [ ! -f "$STATE_FILE" ]; then
        echo "ERROR: 状态文件不存在: $STATE_FILE"
        echo "请先运行 init.sh 初始化项目"
        exit 1
    fi
}

# 创建目录
mkdir -p "$LOG_DIR" "$CHECKPOINT_DIR"

# 环境检查
check_environment

# 信号处理
trap 'log "INFO" "收到终止信号"; save_checkpoint; exit 0' SIGTERM SIGINT

# 启动
main_loop
