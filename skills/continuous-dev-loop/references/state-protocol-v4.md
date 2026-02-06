# 状态文件协议 v4.0

## state.json 完整结构

```json
{
  "version": "4.0.0",

  "project": {
    "name": "项目名称",
    "path": "/absolute/path/to/project",
    "type": "fullstack",
    "created_at": "2024-01-31T10:00:00Z"
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
    "last_assessed": "2024-01-31T10:30:00Z",
    "history": [
      {"timestamp": "2024-01-31T09:00:00Z", "score": 0},
      {"timestamp": "2024-01-31T10:00:00Z", "score": 45},
      {"timestamp": "2024-01-31T10:30:00Z", "score": 65}
    ]
  },

  "problems": [
    {
      "id": "P001",
      "type": "TEST_FAIL",
      "priority": "P2",
      "description": "test_user_login 失败",
      "location": "tests/test_auth.py:45",
      "detected_at": "2024-01-31T10:30:00Z",
      "resolved": false
    }
  ],

  "status": "running",
  "exit_reason": null,

  "current_action": {
    "id": "A005",
    "type": "fix_tests",
    "description": "修复登录测试失败",
    "skill": "test-report-followup",
    "started_at": "2024-01-31T10:35:00Z",
    "checkpoint": {
      "step": "分析失败原因",
      "progress": "30%",
      "context": "正在检查 mock 配置"
    },
    "retry_count": 0,
    "max_retries": 3
  },

  "action_queue": [
    {
      "id": "A006",
      "type": "add_tests",
      "description": "补充用户注册测试",
      "skill": "test-expert",
      "priority": 2,
      "dependencies": ["A005"]
    }
  ],

  "action_history": [
    {
      "id": "A001",
      "type": "create_requirements",
      "completed_at": "2024-01-31T09:30:00Z",
      "result": "success",
      "health_delta": "+18",
      "duration_seconds": 1800
    },
    {
      "id": "A002",
      "type": "implement_core",
      "completed_at": "2024-01-31T10:00:00Z",
      "result": "success",
      "health_delta": "+20",
      "duration_seconds": 1800
    }
  ],

  "blockers": [],

  "sessions": {
    "count": 5,
    "total_turns": 230,
    "current_session": {
      "id": "sess_005",
      "started_at": "2024-01-31T10:30:00Z",
      "turns_used": 15
    }
  },

  "last_heartbeat": "2024-01-31T10:40:00Z",

  "errors": [],

  "metrics": {
    "total_duration_seconds": 6000,
    "avg_action_duration_seconds": 1500,
    "health_improvement_rate": 10.8
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
| `usable_state_reached` | 达到可用状态 | 停止 |
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

### problems[].type 问题类型

| 类型 | 说明 | 默认优先级 |
|------|------|------------|
| `BLOCKER` | 阻塞问题 | P0 |
| `MISSING` | 功能缺失 | P1 |
| `TEST_FAIL` | 测试失败 | P2 |
| `QUALITY` | 质量问题 | P3 |
| `DOC_MISS` | 文档缺失 | P4 |

### current_action.type 行动类型

| 类型 | 说明 | 常用 Skill |
|------|------|------------|
| `create_requirements` | 创建需求文档 | product-expert |
| `implement_core` | 实现核心功能 | python-expert |
| `implement_feature` | 实现具体功能 | python-expert |
| `add_tests` | 添加测试 | test-expert |
| `fix_tests` | 修复测试 | test-report-followup |
| `fix_blocker` | 修复阻塞问题 | python-expert |
| `improve_quality` | 提升代码质量 | python-expert |
| `polish` | 收尾优化 | test-expert |
| `complete` | 完成并生成报告 | - |

---

## AI 更新规则

### 心跳更新（每个子步骤）

```python
import json
from datetime import datetime

def update_heartbeat():
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    state['sessions']['current_session']['turns_used'] += 1

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 健康度更新（每次评估后）

```python
def update_health(new_breakdown):
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    old_score = state['health']['score']
    new_score = sum(new_breakdown.values())

    state['health']['breakdown'] = new_breakdown
    state['health']['score'] = new_score
    state['health']['usable'] = new_score >= 80
    state['health']['last_assessed'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    state['health']['history'].append({
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'score': new_score
    })

    # 检查是否达到可用状态
    if state['health']['usable']:
        state['status'] = 'completed'
        state['exit_reason'] = 'usable_state_reached'

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return new_score - old_score  # 返回提升值
```

### 行动完成更新

```python
def complete_action(result, health_delta):
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    # 1. 记录完成的行动
    completed = state['current_action'].copy()
    completed['completed_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    completed['result'] = result
    completed['health_delta'] = health_delta
    state['action_history'].append(completed)

    # 2. 设置下一个行动
    if state['action_queue']:
        state['current_action'] = state['action_queue'].pop(0)
        state['status'] = 'continue'
        state['exit_reason'] = 'action_done'
    else:
        state['current_action'] = None
        # 重新评估健康度决定下一步

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### 问题记录

```python
def record_problem(problem_type, description, location=None):
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    problem_id = f"P{len(state['problems']) + 1:03d}"
    priority_map = {
        'BLOCKER': 'P0',
        'MISSING': 'P1',
        'TEST_FAIL': 'P2',
        'QUALITY': 'P3',
        'DOC_MISS': 'P4'
    }

    state['problems'].append({
        'id': problem_id,
        'type': problem_type,
        'priority': priority_map.get(problem_type, 'P3'),
        'description': description,
        'location': location,
        'detected_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'resolved': False
    })

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return problem_id
```

### 断点保存（轮次限制前）

```python
def save_checkpoint(step, progress, context, next_action=None):
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

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

---

## 状态文件初始化

```python
def init_state(project_name, project_path, requirement=None):
    state = {
        "version": "4.0.0",
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
            "last_assessed": None,
            "history": []
        },
        "problems": [],
        "status": "ready",
        "exit_reason": None,
        "current_action": None,
        "action_queue": [],
        "action_history": [],
        "blockers": [],
        "sessions": {
            "count": 0,
            "total_turns": 0,
            "current_session": None
        },
        "last_heartbeat": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "errors": [],
        "metrics": {
            "total_duration_seconds": 0,
            "avg_action_duration_seconds": 0,
            "health_improvement_rate": 0
        }
    }

    os.makedirs('.dev-state', exist_ok=True)

    if requirement:
        with open('.dev-state/requirement.txt', 'w') as f:
            f.write(requirement)

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state
```
