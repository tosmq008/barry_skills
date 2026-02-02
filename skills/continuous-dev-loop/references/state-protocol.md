# 状态文件协议

## state.json 完整结构

```json
{
  "version": "1.0.0",
  
  "project": {
    "name": "项目名称",
    "description": "项目描述",
    "created_at": "2024-01-31T10:00:00Z"
  },
  
  "status": "running",
  
  "phase": "development",
  
  "current_task": {
    "id": "TASK_003",
    "name": "实现用户登录 API",
    "skill": "rapid-prototype-workflow",
    "phase_task_id": "3.3",
    "started_at": "2024-01-31T10:30:00Z",
    "retry_count": 0,
    "max_retries": 3
  },
  
  "task_queue": [
    {
      "id": "TASK_004",
      "name": "实现用户注册 API",
      "skill": "rapid-prototype-workflow",
      "phase_task_id": "3.4",
      "priority": 1,
      "dependencies": ["TASK_003"]
    }
  ],
  
  "completed_tasks": [
    {
      "id": "TASK_001",
      "name": "创建 PRD 文档",
      "completed_at": "2024-01-31T10:15:00Z",
      "duration_seconds": 300
    }
  ],
  
  "progress": {
    "total_tasks": 32,
    "completed": 15,
    "failed": 1,
    "skipped": 0
  },
  
  "session": {
    "id": "sess_20240131_001",
    "started_at": "2024-01-31T10:00:00Z",
    "turns_used": 45,
    "max_turns": 50
  },
  
  "last_heartbeat": "2024-01-31T10:35:00Z",
  
  "exit_reason": null,
  
  "errors": [
    {
      "timestamp": "2024-01-31T10:20:00Z",
      "task_id": "TASK_002",
      "error": "API 调用失败",
      "resolved": true
    }
  ],
  
  "metrics": {
    "total_sessions": 5,
    "total_turns": 230,
    "total_duration_seconds": 7200,
    "avg_task_duration_seconds": 450
  }
}
```

## 字段说明

### status 状态值

| 值 | 说明 | AI 动作 | 守护进程动作 |
|----|------|---------|--------------|
| `ready` | 准备开始 | 开始执行第一个任务 | 启动会话 |
| `running` | 正在执行 | 继续执行 | 等待 |
| `continue` | 需要继续 | 从 current_task 继续 | 启动新会话 |
| `paused` | 暂停 | 等待 | 等待人工恢复 |
| `completed` | 全部完成 | 无 | 停止 |
| `error` | 发生错误 | 无 | 告警并等待 |

### exit_reason 退出原因

| 值 | 说明 | 守护进程动作 |
|----|------|--------------|
| `turns_limit` | 达到轮次限制 | 立即重启 |
| `task_done` | 当前任务完成 | 立即重启 |
| `all_done` | 所有任务完成 | 停止 |
| `blocked` | 任务阻塞 | 跳过并继续 |
| `error` | 发生错误 | 重试或告警 |
| `rate_limit` | 触发限流 | 等待后重试 |
| `user_stop` | 用户停止 | 停止 |

### phase 阶段值

| 值 | 说明 | 调用的 Skill |
|----|------|--------------|
| `development` | 开发阶段 | rapid-prototype-workflow |
| `testing` | 测试阶段 | test-expert |
| `bugfix` | 修复阶段 | test-report-followup |
| `regression` | 回归阶段 | test-expert |

## AI 更新规则

### 心跳更新

每完成一个子步骤，更新 `last_heartbeat`:

```python
import json
from datetime import datetime

with open('.dev-state/state.json', 'r') as f:
    state = json.load(f)

state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state['session']['turns_used'] += 1

with open('.dev-state/state.json', 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
```

### 任务完成更新

```python
# 1. 将当前任务移到 completed_tasks
completed_task = state['current_task'].copy()
completed_task['completed_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state['completed_tasks'].append(completed_task)

# 2. 更新进度
state['progress']['completed'] += 1

# 3. 设置下一个任务
if state['task_queue']:
    state['current_task'] = state['task_queue'].pop(0)
    state['status'] = 'continue'
    state['exit_reason'] = 'task_done'
else:
    state['current_task'] = None
    state['status'] = 'completed'
    state['exit_reason'] = 'all_done'
```

### 错误记录

```python
state['errors'].append({
    'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'task_id': state['current_task']['id'],
    'error': str(error),
    'resolved': False
})

state['current_task']['retry_count'] += 1

if state['current_task']['retry_count'] >= state['current_task']['max_retries']:
    state['progress']['failed'] += 1
    state['status'] = 'continue'
    state['exit_reason'] = 'blocked'
```
