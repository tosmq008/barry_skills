# 中断恢复场景详解

## 场景 1: 正常轮次限制退出

**触发条件:** turns_used >= max_turns

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "turns_limit",
  "current_task": {
    "checkpoint": {
      "step": "coding",
      "file": "src/auth.py",
      "line": 45
    }
  }
}
```

**恢复策略:**
- 守护进程等待 60-120 秒后重启
- 新会话从 checkpoint 继续

---

## 场景 2: 任务完成退出

**触发条件:** 当前任务执行完毕

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "task_done",
  "current_task": {
    "id": "NEXT_TASK_ID",
    "name": "下一个任务"
  }
}
```

**恢复策略:**
- 守护进程立即启动新会话
- 执行下一个任务

---

## 场景 3: API 限流

**触发条件:** 收到 429 Rate Limit 响应

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "rate_limit",
  "rate_limit": {
    "consecutive_limits": 2,
    "backoff_until": "2024-01-31T11:00:00Z"
  }
}
```

**恢复策略:**
- 等待 RATE_LIMIT_WAIT * (BACKOFF ^ consecutive_limits) 秒
- 最长等待 30 分钟
- 重试最多 3 次

---

## 场景 4: 网络中断

**触发条件:** 网络断开导致 API 调用失败

**检测方式:** 心跳超时 (HEARTBEAT_TIMEOUT 秒无更新)

**状态:**
```json
{
  "status": "running",
  "last_heartbeat": "2024-01-31T10:00:00Z"  // 超过 10 分钟前
}
```

**恢复策略:**
- 守护进程检测到心跳超时
- 设置 status="continue", exit_reason="heartbeat_timeout"
- 从最近的 checkpoint 恢复

---

## 场景 5: 进程崩溃

**触发条件:** Claude CLI 进程意外终止

**检测方式:** 
- 会话日志中断
- 状态仍为 "running" 但进程不存在

**恢复策略:**
- 守护进程检测到异常
- 从 checkpoints/latest.json 恢复状态
- 重启会话

---

## 场景 6: 系统重启

**触发条件:** 机器重启

**检测方式:**
- daemon.pid 存在但进程不在
- 状态可能为 "running"

**恢复策略:**
```bash
# 启动时检查
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ! ps -p "$PID" > /dev/null 2>&1; then
        # 进程不存在，清理并恢复
        rm -f "$PID_FILE"
        # 从 checkpoint 恢复
        cp checkpoints/latest.json state.json
        # 设置继续状态
        set_json "d['status']='continue'"
    fi
fi
```

---

## 场景 7: 任务阻塞

**触发条件:** 任务重试 3 次仍失败

**状态:**
```json
{
  "status": "continue",
  "exit_reason": "blocked",
  "current_task": {
    "retry_count": 3,
    "id": "BLOCKED_TASK"
  },
  "progress": {
    "development": {"failed": 1}
  }
}
```

**恢复策略:**
- 记录失败任务
- 跳过此任务
- 继续下一个任务
- 发送告警通知

---

## 场景 8: 用户暂停

**触发条件:** 用户执行 pause.sh

**状态:**
```json
{
  "status": "paused",
  "exit_reason": "user_pause"
}
```

**恢复策略:**
- 守护进程等待
- 用户执行 resume.sh 后继续

---

## 场景 9: 阶段流转

**触发条件:** 当前阶段所有任务完成

**状态变化:**
```json
// Before
{
  "workflow": {
    "current_phase": "development",
    "phase_status": {
      "development": "in_progress"
    }
  }
}

// After
{
  "workflow": {
    "current_phase": "testing",
    "phase_status": {
      "development": "completed",
      "testing": "in_progress"
    }
  }
}
```

**恢复策略:**
- 自动切换到下一阶段
- 使用对应的 Skill

---

## 场景 10: 全部完成

**触发条件:** 所有阶段完成，无遗留问题

**状态:**
```json
{
  "status": "completed",
  "exit_reason": "all_done",
  "workflow": {
    "phase_status": {
      "development": "completed",
      "testing": "completed",
      "bugfix": "completed",
      "regression": "completed"
    }
  }
}
```

**恢复策略:**
- 守护进程正常退出
- 发送完成通知

---

## Checkpoint 文件格式

```json
{
  "timestamp": "2024-01-31T10:30:00Z",
  "state_snapshot": { /* 完整 state.json 内容 */ },
  "session_info": {
    "id": "sess_001",
    "turns_used": 45,
    "duration_seconds": 1800
  },
  "recovery_hint": "从 src/auth.py:45 继续实现 login 接口"
}
```

## 恢复优先级

1. **最新 checkpoint** - checkpoints/latest.json
2. **状态文件** - state.json
3. **会话日志** - 解析最后的操作
4. **重新开始** - 从当前任务头开始
