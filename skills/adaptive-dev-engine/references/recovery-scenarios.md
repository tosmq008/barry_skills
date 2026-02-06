# 中断恢复场景

## 场景概览

| 场景 | 触发条件 | 恢复策略 |
|------|----------|----------|
| 轮次限制 | turns >= max_turns | 从 checkpoint 继续 |
| 任务完成 | 当前任务执行完毕 | 执行下一个任务 |
| API 限流 | 429 Rate Limit | 等待后重试 |
| 心跳超时 | 无心跳更新 | 强制重启 |
| 进程崩溃 | 进程意外终止 | 从 checkpoint 恢复 |
| 用户暂停 | 用户执行 pause | 等待 resume |
| 达到可用 | 健康度 >= 80 | 生成报告并退出 |

---

## 场景 1: 轮次限制退出

**触发条件:** `turns_used >= max_turns` (默认 50)

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "turns_limit",
  "current_action": {
    "type": "parallel_development",
    "checkpoint": {
      "step": "实现用户登录 API",
      "progress": "60%",
      "context": "已完成数据模型，正在实现路由",
      "next_action": "继续实现 login 接口"
    }
  }
}
```

**恢复策略:**
1. 守护进程等待 60-120 秒
2. 启动新会话
3. AI 读取 checkpoint，从断点继续

**AI 恢复代码:**
```python
def resume_from_turns_limit():
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    checkpoint = state['current_action'].get('checkpoint')
    if checkpoint:
        print(f"从断点恢复: {checkpoint['step']}")
        print(f"进度: {checkpoint['progress']}")
        print(f"下一步: {checkpoint.get('next_action', '继续当前任务')}")

        # 继续执行
        return checkpoint['next_action']

    return None
```

---

## 场景 2: 任务完成退出

**触发条件:** 当前任务执行完毕

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "action_done",
  "current_action": null,
  "health": {
    "score": 65,
    "usable": false
  }
}
```

**恢复策略:**
1. 守护进程立即启动新会话
2. AI 重新评估健康度
3. 决定下一步行动

---

## 场景 3: API 限流

**触发条件:** 收到 429 Rate Limit 响应

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "rate_limit",
  "errors": [
    {
      "type": "rate_limit",
      "message": "API rate limit exceeded",
      "timestamp": "2024-01-31T10:30:00Z"
    }
  ]
}
```

**恢复策略:**
1. 守护进程等待 `RATE_LIMIT_WAIT` 秒 (默认 300)
2. 指数退避: `wait * (2 ^ consecutive_limits)`
3. 最长等待 30 分钟
4. 重试最多 3 次

**守护进程代码:**
```bash
handle_rate_limit() {
    local consecutive=$(get_json "['rate_limit_count']" || echo 0)
    local wait=$((RATE_LIMIT_WAIT * (2 ** consecutive)))

    # 最长 30 分钟
    [ $wait -gt 1800 ] && wait=1800

    log "限流等待 ${wait}s (第 $((consecutive+1)) 次)"
    sleep $wait

    # 更新计数
    set_json "d['rate_limit_count'] = $((consecutive+1))"
}
```

---

## 场景 4: 心跳超时

**触发条件:** `last_heartbeat` 超过 `HEARTBEAT_TIMEOUT` (默认 30 分钟)

**状态:**
```json
{
  "status": "running",
  "last_heartbeat": "2024-01-31T10:00:00Z"
}
```

**检测方式:**
```python
def check_heartbeat_timeout():
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    last_hb = state.get('last_heartbeat')
    if not last_hb:
        return False

    hb_time = datetime.fromisoformat(last_hb.replace('Z', ''))
    age = (datetime.utcnow() - hb_time).total_seconds()

    return age > HEARTBEAT_TIMEOUT  # 默认 1800 秒
```

**恢复策略:**
1. 守护进程检测到心跳超时
2. 杀死当前 claude 进程
3. 设置 `status="continue"`, `exit_reason="heartbeat_timeout"`
4. 从最近的 checkpoint 恢复

---

## 场景 5: 进程崩溃

**触发条件:** Claude CLI 进程意外终止

**检测方式:**
- 状态为 `running` 但进程不存在
- 会话日志中断

**恢复策略:**
```bash
check_process_crash() {
    local status=$(get_json "['status']")

    if [ "$status" = "running" ]; then
        # 检查是否有 claude 进程
        if ! pgrep -x "claude" > /dev/null; then
            log "检测到进程崩溃，准备恢复"

            # 设置恢复状态
            set_json "d['status']='continue'; d['exit_reason']='process_crash'"

            # 记录错误
            set_json "d['errors'].append({'type': 'crash', 'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'})"

            return 0  # 需要恢复
        fi
    fi

    return 1  # 不需要恢复
}
```

---

## 场景 6: 用户暂停

**触发条件:** 用户执行 `./adaptive-dev pause`

**状态:**
```json
{
  "status": "paused",
  "exit_reason": "user_pause"
}
```

**恢复策略:**
1. 守护进程进入等待状态
2. 用户执行 `./adaptive-dev start` 恢复
3. 自动设置 `status="continue"`

---

## 场景 7: 达到可用状态

**触发条件:** `health.score >= 80`

**状态:**
```json
{
  "status": "completed",
  "exit_reason": "usable_reached",
  "health": {
    "score": 82,
    "usable": true
  }
}
```

**恢复策略:**
1. AI 生成交付报告
2. 守护进程正常退出
3. 发送完成通知（如配置）

---

## 场景 8: Agent 执行失败

**触发条件:** Sub Agent 执行失败

**状态:**
```json
{
  "agent_coordination": {
    "active_agents": [
      {
        "agent": "python-expert",
        "status": "failed",
        "error": "无法连接数据库"
      }
    ]
  },
  "errors": [
    {
      "type": "agent_failure",
      "agent": "python-expert",
      "message": "无法连接数据库"
    }
  ]
}
```

**恢复策略:**
```python
def handle_agent_failure(agent_name, error):
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    # 统计重试次数
    retry_count = len([
        e for e in state['errors']
        if e.get('agent') == agent_name and e.get('type') == 'agent_failure'
    ])

    if retry_count < 3:
        # 重试
        return {'action': 'retry', 'delay': 60 * retry_count}
    else:
        # 跳过并记录 blocker
        state['blockers'].append({
            'agent': agent_name,
            'error': error,
            'skipped_at': datetime.utcnow().isoformat()
        })
        return {'action': 'skip', 'continue': True}
```

---

## Checkpoint 文件格式

```json
{
  "timestamp": "2024-01-31T10:30:00Z",
  "state_snapshot": {
    "health": {"score": 65},
    "current_action": {"type": "parallel_development"},
    "agent_coordination": {}
  },
  "session_info": {
    "id": "sess_005",
    "turns_used": 45,
    "duration_seconds": 1800
  },
  "recovery_hint": "从 src/routes/user.py 继续实现 login 接口"
}
```

---

## 恢复优先级

1. **最新 checkpoint** - `.dev-state/checkpoints/latest.json`
2. **状态文件** - `.dev-state/state.json`
3. **会话日志** - 解析最后的操作
4. **重新开始** - 从当前任务头开始

---

## 守护进程恢复逻辑

```bash
recover_session() {
    local status=$(get_json "['status']")
    local exit_reason=$(get_json "['exit_reason']")

    case "$exit_reason" in
        turns_limit)
            log "轮次限制，立即重启"
            sleep 60
            start_session
            ;;
        action_done)
            log "任务完成，立即重启"
            start_session
            ;;
        rate_limit)
            handle_rate_limit
            start_session
            ;;
        heartbeat_timeout|process_crash)
            log "异常退出，从 checkpoint 恢复"
            restore_checkpoint
            start_session
            ;;
        usable_reached)
            log "项目完成！"
            generate_report
            exit 0
            ;;
        user_pause)
            log "用户暂停，等待恢复"
            # 不做任何事，等待用户 resume
            ;;
        *)
            log "未知退出原因: $exit_reason"
            sleep 60
            start_session
            ;;
    esac
}
```
