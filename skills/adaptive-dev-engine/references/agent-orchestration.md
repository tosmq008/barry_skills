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

## 冲突避免：Prompt 约束（替代文件锁）

文件锁机制不可靠（子 Agent 不会主动使用），改为在每个 Agent 的 prompt 中**显式声明可操作的目录范围**。

### 目录分离规则

| Agent | 允许修改的目录 | 禁止修改的目录 |
|-------|---------------|---------------|
| product-expert | `docs/prd/`, `docs/ui/` | `src/`, `tests/`, `client/` |
| tech-manager | `docs/tech/`, 项目配置文件 | `src/` 具体实现代码 |
| python-expert | `src/`, `backend/`, `app/`, `server/` | `client/`, `frontend/`, `web/` |
| frontend-expert | `client/`, `frontend/`, `web/` | `src/`, `backend/`, `app/`, `server/` |
| test-expert | `tests/`, `docs/test/` | `src/`, `client/` |
| test-report-followup | 根据 bug 所在模块决定 | 非相关模块 |

### Prompt 约束模板

在调度每个 Agent 时，prompt 中必须包含以下约束：

```
## 文件操作约束（必须遵守）

你只能修改以下目录中的文件：
- {allowed_dirs}

你不能修改以下目录中的文件：
- {forbidden_dirs}

如果你需要修改约束范围外的文件，请在状态文件中记录需求，由主控 Agent 协调处理。
```

**示例 - python-expert 的 prompt：**
```
## 文件操作约束（必须遵守）

你只能修改以下目录中的文件：
- src/
- backend/
- app/
- server/
- requirements.txt / pyproject.toml

你不能修改以下目录中的文件：
- client/
- frontend/
- web/
- docs/prd/
```

---

## 并行执行模式

### 模式 1: 前后端并行开发

```
场景: code 维度最弱且 score >= 10

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
│ 约束: src/    │       │ 约束: client/ │
│ backend/      │       │ frontend/     │
│ app/          │       │ web/          │
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

## 文件操作约束（必须遵守）
你只能修改以下目录中的文件：
- src/
- backend/
- app/
- server/

你不能修改以下目录中的文件：
- client/
- frontend/
- web/

## 完成后
将执行结果写入 .dev-state/agents/python-expert.json
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

## 文件操作约束（必须遵守）
你只能修改以下目录中的文件：
- client/
- frontend/
- web/

你不能修改以下目录中的文件：
- src/
- backend/
- app/
- server/

## API 接口文档
{api_spec}

## 完成后
将执行结果写入 .dev-state/agents/frontend-expert.json
""",
    run_in_background=True
)
```

### 模式 2: 测试与修复并行

```
场景: tests 维度最弱，同时有已知 bug

┌─────────────────────────────────────────┐
│           adaptive-dev-engine            │
│              (主控)                      │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌─────────────────┐
│  test-expert  │       │test-report-     │
│  (新增测试)   │       │followup (修bug) │
│               │       │                 │
│ 约束: tests/  │       │ 约束: 按bug模块 │
└───────┬───────┘       └───────┬─────────┘
        │                       │
        └───────────┬───────────┘
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

## 状态同步：Agent 独立状态文件

每个 Agent 写入自己的独立状态文件，避免多 Agent 竞争写同一个 `state.json`。

### 目录结构

```
.dev-state/
├── state.json                  # 主控读写，Agent 只读
└── agents/                     # 每个 Agent 写自己的文件
    ├── python-expert.json
    ├── frontend-expert.json
    ├── test-expert.json
    └── product-expert.json
```

### Agent 状态文件格式

每个 Agent 完成任务后写入 `.dev-state/agents/{agent-name}.json`：

```json
{
  "agent": "python-expert",
  "task": "backend_development",
  "status": "completed",
  "started_at": "2024-01-31T10:00:00Z",
  "completed_at": "2024-01-31T10:45:00Z",
  "result": "success",
  "outputs": [
    "src/routes/user.py",
    "src/models/user.py"
  ],
  "summary": "完成用户模块 API 开发，包含 CRUD 接口",
  "issues": []
}
```

### 主控汇总逻辑

主控 Agent（adaptive-dev-engine）负责读取所有 Agent 状态文件并汇总：

```python
import json
from pathlib import Path

def aggregate_agent_results():
    """汇总所有 Agent 的执行结果"""

    agents_dir = Path('.dev-state/agents')
    if not agents_dir.exists():
        return {'total_agents': 0, 'results': []}

    results = []
    for agent_file in agents_dir.glob('*.json'):
        with open(agent_file, 'r') as f:
            results.append(json.load(f))

    summary = {
        'total_agents': len(results),
        'success': len([r for r in results if r['result'] == 'success']),
        'failed': len([r for r in results if r['result'] == 'failed']),
        'outputs': [],
        'issues': []
    }

    for r in results:
        summary['outputs'].extend(r.get('outputs', []))
        summary['issues'].extend(r.get('issues', []))

    return summary
```

### Agent Prompt 中的状态写入指令

每个 Agent 的 prompt 末尾应包含：

```
## 完成后（必须执行）

将你的执行结果写入 .dev-state/agents/{agent-name}.json，格式如下：
{
  "agent": "{agent-name}",
  "task": "任务描述",
  "status": "completed" 或 "failed",
  "started_at": "ISO时间",
  "completed_at": "ISO时间",
  "result": "success" 或 "failed",
  "outputs": ["修改的文件列表"],
  "summary": "一句话总结完成了什么",
  "issues": ["遇到的问题，如果有的话"]
}
```

---

## 依赖管理

### 任务依赖定义

```python
TASK_DEPENDENCIES = {
    'backend_development': ['tech_design'],
    'frontend_development': ['tech_design', 'api_spec'],
    'test_execution': ['backend_development', 'frontend_development'],
    'bug_fix': ['test_execution'],
}
```

### 依赖检查

```python
def check_dependencies(task_type):
    """检查任务依赖是否满足"""

    agents_dir = Path('.dev-state/agents')
    completed_tasks = []

    if agents_dir.exists():
        for agent_file in agents_dir.glob('*.json'):
            with open(agent_file, 'r') as f:
                data = json.load(f)
            if data.get('result') == 'success':
                completed_tasks.append(data['task'])

    dependencies = TASK_DEPENDENCIES.get(task_type, [])

    for dep in dependencies:
        if dep not in completed_tasks:
            return False, f"等待 {dep} 完成"

    return True, None
```

---

## 错误处理

### Agent 执行失败

```python
def handle_agent_failure(agent_name, error):
    """处理 Agent 执行失败"""

    # 读取该 Agent 的状态文件
    agent_file = Path(f'.dev-state/agents/{agent_name}.json')

    failure_record = {
        'agent': agent_name,
        'status': 'failed',
        'result': 'failed',
        'error': str(error),
        'completed_at': datetime.utcnow().isoformat()
    }

    with open(agent_file, 'w') as f:
        json.dump(failure_record, f, indent=2, ensure_ascii=False)

    # 检查历史失败次数（从 state.json 的 decision_log 中统计）
    retry_count = count_recent_failures(agent_name)

    if retry_count < 3:
        return {'action': 'retry', 'delay': 60}
    else:
        return {'action': 'skip', 'record_blocker': True}
```

### 超时处理

```python
AGENT_TIMEOUT = 1800  # 30 分钟

def check_agent_timeout(active_agents):
    """
    检查 Agent 是否超时

    Args:
        active_agents: 当前正在运行的 Agent 列表
            [{'agent': 'python-expert', 'started_at': '...'}]
    """

    now = datetime.utcnow()
    timeout_agents = []

    for agent in active_agents:
        started = datetime.fromisoformat(agent['started_at'].replace('Z', ''))
        if (now - started).total_seconds() > AGENT_TIMEOUT:
            timeout_agents.append(agent['agent'])

    return timeout_agents
```

---

## 结果汇总与健康度更新

```python
def update_health_after_agents():
    """Agent 完成后，主控重新评估健康度"""

    summary = aggregate_agent_results()

    if summary['failed'] > 0:
        print(f"警告: {summary['failed']} 个 Agent 执行失败")

    # 重新运行健康度评估（而非简单加分）
    # 健康度应该由实际项目状态决定，而非预估增量
    new_health = assess_health()

    # 记录到历史
    state['health']['history'].append({
        'score': new_health['score'],
        'breakdown': new_health['breakdown'],
        'session': state['sessions']['count'],
        'agents_run': [r['agent'] for r in summary.get('results', [])]
    })

    # 清理 Agent 状态文件（归档到 completed）
    archive_agent_results()

    return new_health
```
