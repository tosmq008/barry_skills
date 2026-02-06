# 多 Agent 编排指南

## Agent 概览

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| `product-expert` | 产品设计 | 需求描述 | PRD、UI设计 |
| `tech-manager` | 技术协调 | PRD | 技术方案、任务分配 |
| `python-expert` | 后端开发 | 技术方案 | API、数据库、业务逻辑 |
| `frontend-expert` | 前端开发 | UI设计、API文档 | 前端代码 |
| `test-expert` | 测试执行 | 代码、PRD | 测试报告 |
| `test-report-followup` | Bug修复 | 测试报告 | 修复代码 |

---

## 调度方式

### 方式 1: Skill Tool 调度（单 Agent）

```
适用: 单个 Agent 独立执行任务

调用方式:
Skill tool → skill="agent-name"

示例:
Skill(skill="product-expert")
→ 执行产品设计任务
```

### 方式 2: Task Tool 调度（并行 Agent）

```
适用: 多个 Agent 并行执行

调用方式:
在单个消息中发送多个 Task tool 调用

示例:
Task(subagent_type="general-purpose", prompt="使用 python-expert...", run_in_background=True)
Task(subagent_type="general-purpose", prompt="使用 frontend-expert...", run_in_background=True)
→ 两个 Agent 并行执行
```

---

## 并行执行模式

### 模式 1: 前后端并行开发

```
场景: 健康度 40-60，需要实现功能

┌─────────────────────────────────────────┐
│           adaptive-dev-engine            │
│              (主控)                      │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│ python-expert │       │frontend-expert│
│  (后端 API)   │       │  (前端 UI)    │
│               │       │               │
│ - 数据模型    │       │ - 页面组件    │
│ - API 接口    │       │ - 状态管理    │
│ - 业务逻辑    │       │ - API 对接    │
└───────┬───────┘       └───────┬───────┘
        │                       │
        └───────────┬───────────┘
                    ▼
            ┌─────────────┐
            │  联调验证    │
            │ tech-manager │
            └─────────────┘
```

**调度代码:**
```python
# 并行启动前后端开发
# 在单个消息中发送两个 Task 调用

backend_task = Task(
    subagent_type="general-purpose",
    description="python-expert 后端开发",
    prompt=f"""
使用 python-expert skill 实现后端功能。

## 任务列表
{backend_tasks}

## API 规范
- RESTful 风格
- 统一响应格式
- 错误处理

## 完成后
更新 .dev-state/state.json:
```python
import json
with open('.dev-state/state.json', 'r') as f:
    state = json.load(f)
state['agent_coordination']['completed_agents'].append({{
    'agent': 'python-expert',
    'task': 'backend_development',
    'status': 'completed'
}})
with open('.dev-state/state.json', 'w') as f:
    json.dump(state, f, indent=2)
```
""",
    run_in_background=True
)

frontend_task = Task(
    subagent_type="general-purpose",
    description="frontend-expert 前端开发",
    prompt=f"""
使用 frontend-expert skill 实现前端功能。

## 任务列表
{frontend_tasks}

## API 接口文档
{api_spec}

## UI 设计稿
{ui_design}

## 完成后
更新 .dev-state/state.json
""",
    run_in_background=True
)
```

### 模式 2: 测试与修复并行

```
场景: 健康度 60-75，需要测试和修复

┌─────────────────────────────────────────┐
│           adaptive-dev-engine            │
│              (主控)                      │
└───────────────────┬─────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│  test-  │   │ python- │   │frontend-│
│  expert │   │  expert │   │ expert  │
│(测试)   │   │(修后端) │   │(修前端) │
└────┬────┘   └────┬────┘   └────┬────┘
     │             │             │
     └─────────────┴─────────────┘
                   ▼
           ┌─────────────┐
           │  回归验证    │
           └─────────────┘
```

### 模式 3: 多 Bug 并行修复

```
场景: 测试报告有多个 Bug，分属不同模块

┌─────────────────────────────────────────┐
│         test-report-followup             │
│           (Bug 分派)                     │
└───────────────────┬─────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ Bug #1  │   │ Bug #2  │   │ Bug #3  │
│ python- │   │ python- │   │frontend-│
│ expert  │   │ expert  │   │ expert  │
│(用户API)│   │(订单API)│   │(登录页) │
└─────────┘   └─────────┘   └─────────┘
```

---

## Agent 协调协议

### 状态同步

所有 Agent 通过 `.dev-state/state.json` 同步状态：

```json
{
  "agent_coordination": {
    "active_agents": [
      {
        "agent": "python-expert",
        "task_id": "T001",
        "task": "backend_development",
        "status": "running",
        "started_at": "2024-01-31T10:00:00Z",
        "progress": "60%",
        "current_file": "src/routes/user.py"
      },
      {
        "agent": "frontend-expert",
        "task_id": "T002",
        "task": "frontend_development",
        "status": "running",
        "started_at": "2024-01-31T10:00:00Z",
        "progress": "40%",
        "current_file": "src/pages/Login.tsx"
      }
    ],
    "completed_agents": [
      {
        "agent": "product-expert",
        "task_id": "T000",
        "task": "prd_creation",
        "status": "completed",
        "completed_at": "2024-01-31T09:30:00Z",
        "result": "success",
        "outputs": ["docs/prd/01-project-brief.md", "docs/prd/02-feature-architecture.md"]
      }
    ],
    "pending_sync": false,
    "last_sync": "2024-01-31T10:30:00Z"
  }
}
```

### Agent 状态更新

每个 Agent 在执行过程中应定期更新状态：

```python
def update_agent_status(agent_name, status, progress=None, current_file=None):
    """更新 Agent 执行状态"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    # 找到对应的 Agent
    for agent in state['agent_coordination']['active_agents']:
        if agent['agent'] == agent_name:
            agent['status'] = status
            if progress:
                agent['progress'] = progress
            if current_file:
                agent['current_file'] = current_file
            break

    state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

### Agent 完成通知

Agent 完成任务后，移动到 completed_agents：

```python
def mark_agent_completed(agent_name, result, outputs=None):
    """标记 Agent 完成"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    # 从 active 移到 completed
    for i, agent in enumerate(state['agent_coordination']['active_agents']):
        if agent['agent'] == agent_name:
            completed_agent = state['agent_coordination']['active_agents'].pop(i)
            completed_agent['status'] = 'completed'
            completed_agent['completed_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            completed_agent['result'] = result
            if outputs:
                completed_agent['outputs'] = outputs
            state['agent_coordination']['completed_agents'].append(completed_agent)
            break

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

---

## 依赖管理

### 任务依赖定义

```python
TASK_DEPENDENCIES = {
    'backend_development': [],  # 无依赖，可立即开始
    'frontend_development': ['api_spec'],  # 依赖 API 文档
    'test_execution': ['backend_development', 'frontend_development'],  # 依赖开发完成
    'bug_fix': ['test_execution'],  # 依赖测试报告
}
```

### 依赖检查

```python
def check_dependencies(task_type):
    """检查任务依赖是否满足"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    completed_tasks = [
        a['task'] for a in state['agent_coordination']['completed_agents']
    ]

    dependencies = TASK_DEPENDENCIES.get(task_type, [])

    for dep in dependencies:
        if dep not in completed_tasks:
            return False, f"等待 {dep} 完成"

    return True, None
```

---

## 冲突避免

### 文件锁机制

```python
import os
import json
from pathlib import Path

LOCK_DIR = '.dev-state/locks'

def acquire_file_lock(agent_name, file_path):
    """获取文件锁"""

    Path(LOCK_DIR).mkdir(parents=True, exist_ok=True)

    lock_file = Path(LOCK_DIR) / f"{file_path.replace('/', '_')}.lock"

    if lock_file.exists():
        with open(lock_file, 'r') as f:
            lock_info = json.load(f)
        if lock_info['agent'] != agent_name:
            return False, f"文件被 {lock_info['agent']} 锁定"

    with open(lock_file, 'w') as f:
        json.dump({
            'agent': agent_name,
            'file': file_path,
            'locked_at': datetime.utcnow().isoformat()
        }, f)

    return True, None

def release_file_lock(agent_name, file_path):
    """释放文件锁"""

    lock_file = Path(LOCK_DIR) / f"{file_path.replace('/', '_')}.lock"

    if lock_file.exists():
        with open(lock_file, 'r') as f:
            lock_info = json.load(f)
        if lock_info['agent'] == agent_name:
            lock_file.unlink()
            return True

    return False
```

### 目录分离

为避免冲突，不同 Agent 应操作不同目录：

| Agent | 主要操作目录 |
|-------|-------------|
| python-expert | `src/`, `backend/`, `app/` |
| frontend-expert | `client/`, `frontend/`, `web/` |
| test-expert | `tests/`, `docs/test/` |
| product-expert | `docs/prd/`, `docs/ui/` |

---

## 结果汇总

### 汇总所有 Agent 结果

```python
def aggregate_agent_results():
    """汇总所有完成的 Agent 结果"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    completed = state['agent_coordination']['completed_agents']

    # 统计结果
    summary = {
        'total_agents': len(completed),
        'success': len([a for a in completed if a['result'] == 'success']),
        'failed': len([a for a in completed if a['result'] == 'failed']),
        'outputs': []
    }

    for agent in completed:
        if agent.get('outputs'):
            summary['outputs'].extend(agent['outputs'])

    # 估算健康度提升
    health_delta = 0
    delta_map = {
        'prd_creation': 15,
        'backend_development': 12,
        'frontend_development': 12,
        'test_execution': 10,
        'bug_fix': 5
    }

    for agent in completed:
        if agent['result'] == 'success':
            health_delta += delta_map.get(agent['task'], 5)

    summary['estimated_health_delta'] = health_delta

    return summary
```

### 更新健康度

```python
def update_health_after_agents():
    """Agent 完成后更新健康度"""

    summary = aggregate_agent_results()

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    # 更新健康度
    old_score = state['health']['score']
    new_score = min(100, old_score + summary['estimated_health_delta'])

    state['health']['score'] = new_score
    state['health']['usable'] = new_score >= 80

    # 记录到历史
    state['action_history'].append({
        'type': 'agent_batch_complete',
        'agents': [a['agent'] for a in state['agent_coordination']['completed_agents']],
        'health_delta': f"+{new_score - old_score}",
        'completed_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    })

    # 清空已完成的 Agent
    state['agent_coordination']['completed_agents'] = []

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return new_score
```

---

## 错误处理

### Agent 执行失败

```python
def handle_agent_failure(agent_name, error):
    """处理 Agent 执行失败"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    # 记录错误
    if 'errors' not in state:
        state['errors'] = []

    state['errors'].append({
        'agent': agent_name,
        'error': str(error),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    })

    # 从 active 移除
    state['agent_coordination']['active_agents'] = [
        a for a in state['agent_coordination']['active_agents']
        if a['agent'] != agent_name
    ]

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    # 决定是否重试
    retry_count = len([e for e in state['errors'] if e['agent'] == agent_name])

    if retry_count < 3:
        return {'action': 'retry', 'delay': 60}
    else:
        return {'action': 'skip', 'record_blocker': True}
```

### 超时处理

```python
AGENT_TIMEOUT = 1800  # 30 分钟

def check_agent_timeout():
    """检查 Agent 是否超时"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    now = datetime.utcnow()
    timeout_agents = []

    for agent in state['agent_coordination']['active_agents']:
        started = datetime.fromisoformat(agent['started_at'].replace('Z', ''))
        if (now - started).total_seconds() > AGENT_TIMEOUT:
            timeout_agents.append(agent['agent'])

    return timeout_agents
```
