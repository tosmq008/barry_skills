# 状态协议详解

## state.json 完整结构

```json
{
  "version": "1.0.0",

  "project": {
    "name": "my-project",
    "path": "/Users/user/projects/my-project",
    "type": "fullstack",
    "created_at": "2024-01-31T08:00:00Z"
  },

  "health": {
    "score": 65,
    "breakdown": {
      "requirements": 18,
      "code": 20,
      "tests": 12,
      "runnable": 10,
      "quality": 5
    },
    "usable": false,
    "target": 80,
    "assessed_at": "2024-01-31T10:30:00Z",
    "history": [
      {"timestamp": "2024-01-31T09:00:00Z", "score": 0},
      {"timestamp": "2024-01-31T09:30:00Z", "score": 18},
      {"timestamp": "2024-01-31T10:00:00Z", "score": 45},
      {"timestamp": "2024-01-31T10:30:00Z", "score": 65}
    ]
  },

  "status": "running",
  "exit_reason": null,

  "current_action": {
    "type": "parallel_development",
    "description": "前后端并行开发",
    "agents": ["python-expert", "frontend-expert"],
    "started_at": "2024-01-31T10:30:00Z",
    "checkpoint": null
  },

  "agent_coordination": {
    "active_agents": [
      {
        "agent": "python-expert",
        "task_id": "T001",
        "task": "backend_development",
        "status": "running",
        "started_at": "2024-01-31T10:30:00Z",
        "progress": "60%"
      }
    ],
    "completed_agents": [],
    "pending_sync": false
  },

  "action_history": [
    {
      "type": "create_requirements",
      "agents": ["product-expert"],
      "health_delta": "+18",
      "completed_at": "2024-01-31T09:30:00Z",
      "result": "success"
    }
  ],

  "decision_log": [
    {
      "timestamp": "2024-01-31T10:30:00Z",
      "health_score": 45,
      "decision": {
        "action": "parallel_development",
        "agents": ["python-expert", "frontend-expert"],
        "parallel": true
      },
      "reason": "健康度 45 < 60，进入并行开发阶段"
    }
  ],

  "blockers": [],
  "errors": [],

  "sessions": {
    "count": 5,
    "total_turns": 230,
    "current_session": {
      "id": "sess_005",
      "started_at": "2024-01-31T10:00:00Z",
      "turns_used": 25
    }
  },

  "last_heartbeat": "2024-01-31T10:35:00Z",

  "metrics": {
    "total_duration_seconds": 9000,
    "avg_health_delta_per_session": 13,
    "parallel_executions": 2
  }
}
```

---

## 字段说明

### status 状态值

| 值 | 说明 | AI 动作 | 守护进程动作 |
|----|------|---------|--------------|
| `ready` | 准备开始 | 执行健康度分析 | 启动会话 |
| `running` | 正在执行 | 继续当前行动 | 等待 |
| `continue` | 需要继续 | 从 checkpoint 继续 | 启动新会话 |
| `paused` | 暂停 | 等待 | 等待人工恢复 |
| `completed` | 达到可用状态 | 生成报告 | 停止 |
| `blocked` | 遇到阻塞 | 等待 | 告警并等待 |

### exit_reason 退出原因

| 值 | 说明 | 守护进程动作 |
|----|------|--------------|
| `turns_limit` | 达到轮次限制 | 立即重启 |
| `action_done` | 当前行动完成 | 立即重启 |
| `usable_reached` | 达到可用状态 | 停止 |
| `blocked` | 行动阻塞 | 跳过并继续 |
| `error` | 发生错误 | 重试或告警 |
| `rate_limit` | 触发限流 | 等待后重试 |
| `user_stop` | 用户停止 | 停止 |
| `heartbeat_timeout` | 心跳超时 | 强制重启 |

### health.breakdown 健康度分解

| 字段 | 范围 | 说明 |
|------|------|------|
| `requirements` | 0-20 | 需求清晰度 |
| `code` | 0-25 | 代码完整度 |
| `tests` | 0-20 | 测试覆盖度 |
| `runnable` | 0-20 | 可运行性 |
| `quality` | 0-15 | 代码质量 |

### current_action.type 行动类型

| 类型 | 说明 | 常用 Agent |
|------|------|------------|
| `create_requirements` | 创建需求文档 | product-expert |
| `design_and_setup` | 技术设计 | tech-manager |
| `parallel_development` | 并行开发 | python-expert + frontend-expert |
| `test_and_fix` | 测试修复 | test-expert + python-expert |
| `polish_and_verify` | 收尾优化 | test-report-followup |
| `complete` | 完成 | - |

---

## 状态更新 API

### 初始化状态

```python
import json
import os
from datetime import datetime
from pathlib import Path

def init_state(project_name, project_path, requirement=None):
    """初始化状态文件"""

    state = {
        "version": "1.0.0",
        "project": {
            "name": project_name,
            "path": project_path,
            "type": "unknown",
            "created_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        },
        "health": {
            "score": 0,
            "breakdown": {
                "requirements": 0,
                "code": 0,
                "tests": 0,
                "runnable": 0,
                "quality": 0
            },
            "usable": False,
            "target": 80,
            "assessed_at": None,
            "history": []
        },
        "status": "ready",
        "exit_reason": None,
        "current_action": None,
        "agent_coordination": {
            "active_agents": [],
            "completed_agents": [],
            "pending_sync": False
        },
        "action_history": [],
        "decision_log": [],
        "blockers": [],
        "errors": [],
        "sessions": {
            "count": 0,
            "total_turns": 0,
            "current_session": None
        },
        "last_heartbeat": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "metrics": {
            "total_duration_seconds": 0,
            "avg_health_delta_per_session": 0,
            "parallel_executions": 0
        }
    }

    # 创建目录
    state_dir = Path(project_path) / '.dev-state'
    state_dir.mkdir(exist_ok=True)

    # 保存需求
    if requirement:
        with open(state_dir / 'requirement.txt', 'w') as f:
            f.write(requirement)

    # 保存状态
    with open(state_dir / 'state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state
```

### 更新心跳

```python
def update_heartbeat():
    """更新心跳时间"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    if state['sessions']['current_session']:
        state['sessions']['current_session']['turns_used'] += 1

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 更新健康度

```python
def update_health(breakdown):
    """更新健康度评分"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    total = sum(breakdown.values())
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    state['health']['breakdown'] = breakdown
    state['health']['score'] = total
    state['health']['usable'] = total >= 80
    state['health']['assessed_at'] = now
    state['health']['history'].append({
        'timestamp': now,
        'score': total
    })

    # 检查是否达到可用状态
    if state['health']['usable']:
        state['status'] = 'completed'
        state['exit_reason'] = 'usable_reached'

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return total
```

### 设置当前行动

```python
def set_current_action(action_type, agents, description=None):
    """设置当前行动"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    state['current_action'] = {
        'type': action_type,
        'description': description or action_type,
        'agents': agents,
        'started_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'checkpoint': None
    }

    # 添加到 active_agents
    for agent in agents:
        state['agent_coordination']['active_agents'].append({
            'agent': agent,
            'task_id': f"T{len(state['action_history']) + 1:03d}",
            'task': action_type,
            'status': 'running',
            'started_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'progress': '0%'
        })

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 完成行动

```python
def complete_action(result, health_delta):
    """完成当前行动"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    if state['current_action']:
        # 记录到历史
        state['action_history'].append({
            'type': state['current_action']['type'],
            'agents': state['current_action']['agents'],
            'health_delta': health_delta,
            'completed_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'result': result
        })

        # 清空当前行动
        state['current_action'] = None

    # 移动 active_agents 到 completed_agents
    state['agent_coordination']['completed_agents'].extend(
        state['agent_coordination']['active_agents']
    )
    state['agent_coordination']['active_agents'] = []

    # 设置继续状态
    state['status'] = 'continue'
    state['exit_reason'] = 'action_done'

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 保存断点

```python
def save_checkpoint(step, progress, context, next_action=None):
    """保存断点（轮次限制前调用）"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    if state['current_action']:
        state['current_action']['checkpoint'] = {
            'step': step,
            'progress': progress,
            'context': context,
            'next_action': next_action,
            'saved_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

    state['status'] = 'continue'
    state['exit_reason'] = 'turns_limit'

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 记录决策

```python
def log_decision(health_score, decision, reason):
    """记录决策日志"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    state['decision_log'].append({
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'health_score': health_score,
        'decision': decision,
        'reason': reason
    })

    # 只保留最近 20 条
    state['decision_log'] = state['decision_log'][-20:]

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 记录错误

```python
def log_error(error_type, message, agent=None):
    """记录错误"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    state['errors'].append({
        'type': error_type,
        'message': message,
        'agent': agent,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    })

    # 只保留最近 50 条
    state['errors'] = state['errors'][-50:]

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

---

## 状态文件位置

```
project/
└── .dev-state/
    ├── state.json          # 主状态文件
    ├── requirement.txt     # 原始需求（如有）
    ├── locks/              # 文件锁目录
    │   └── *.lock
    ├── logs/               # 会话日志
    │   └── session-*.log
    └── checkpoints/        # 断点备份
        └── checkpoint-*.json
```

---

## 状态恢复

### 从断点恢复

```python
def restore_from_checkpoint():
    """从断点恢复"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    if state['current_action'] and state['current_action'].get('checkpoint'):
        checkpoint = state['current_action']['checkpoint']
        print(f"从断点恢复: {checkpoint['step']}")
        print(f"进度: {checkpoint['progress']}")
        print(f"上下文: {checkpoint['context']}")

        if checkpoint.get('next_action'):
            print(f"下一步: {checkpoint['next_action']}")

        return checkpoint

    return None
```

### 状态一致性检查

```python
def validate_state():
    """验证状态文件一致性"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    issues = []

    # 检查必要字段
    required_fields = ['version', 'project', 'health', 'status']
    for field in required_fields:
        if field not in state:
            issues.append(f"缺少必要字段: {field}")

    # 检查健康度范围
    if state.get('health', {}).get('score', 0) > 100:
        issues.append("健康度超过 100")

    # 检查状态一致性
    if state.get('status') == 'completed' and not state.get('health', {}).get('usable'):
        issues.append("状态为 completed 但 usable 为 false")

    return issues
```
