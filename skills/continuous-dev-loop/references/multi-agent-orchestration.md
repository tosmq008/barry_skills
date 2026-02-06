# 多 Agent 编排引擎

## 可调度的专业 Agent

| Agent | 职责 | 适用场景 |
|-------|------|----------|
| `product-expert` | 产品设计、PRD、UI原型 | 需求不清、产品设计阶段 |
| `tech-manager` | 技术协调、前后端联调 | 全栈开发、接口对接 |
| `python-expert` | Python后端开发 | API、数据库、业务逻辑 |
| `frontend-expert` | 前端开发 | React/Vue、UI实现 |
| `test-expert` | 测试设计与执行 | 测试方案、用例、执行 |
| `test-report-followup` | Bug修复跟进 | 测试报告解析、修复验证 |

---

## 调度策略

### 策略 1: 按健康度阶段调度

```python
def get_agents_by_health(health_score):
    """根据健康度选择需要调度的 Agent"""

    if health_score < 20:
        # 需求阶段：产品专家主导
        return {
            'primary': 'product-expert',
            'parallel': []
        }

    elif health_score < 40:
        # 设计+开发启动阶段
        return {
            'primary': 'tech-manager',
            'parallel': ['product-expert']  # 并行完善需求
        }

    elif health_score < 60:
        # 核心开发阶段：前后端并行
        return {
            'primary': 'tech-manager',
            'parallel': ['python-expert', 'frontend-expert']
        }

    elif health_score < 75:
        # 测试阶段：测试+修复并行
        return {
            'primary': 'test-expert',
            'parallel': ['python-expert', 'frontend-expert']  # 边测边修
        }

    elif health_score < 80:
        # 收尾阶段：全面验证
        return {
            'primary': 'test-report-followup',
            'parallel': ['test-expert']
        }

    else:
        # 已达可用状态
        return {
            'primary': None,
            'parallel': []
        }
```

### 策略 2: 按任务类型调度

```python
def get_agents_by_task(task_type, project_type):
    """根据任务类型选择 Agent 组合"""

    dispatch_map = {
        # 需求相关任务
        'requirement_analysis': {
            'agents': ['product-expert'],
            'parallel': False
        },
        'prd_creation': {
            'agents': ['product-expert'],
            'parallel': False
        },

        # 全栈开发任务
        'fullstack_feature': {
            'agents': ['tech-manager'],  # tech-manager 内部会调度前后端
            'parallel': False
        },
        'api_frontend_integration': {
            'agents': ['python-expert', 'frontend-expert'],
            'parallel': True  # 前后端并行开发
        },

        # 纯后端任务
        'backend_api': {
            'agents': ['python-expert'],
            'parallel': False
        },
        'database_design': {
            'agents': ['python-expert'],
            'parallel': False
        },

        # 纯前端任务
        'frontend_ui': {
            'agents': ['frontend-expert'],
            'parallel': False
        },
        'frontend_component': {
            'agents': ['frontend-expert'],
            'parallel': False
        },

        # 测试任务
        'test_design': {
            'agents': ['test-expert'],
            'parallel': False
        },
        'test_execution': {
            'agents': ['test-expert'],
            'parallel': False
        },
        'full_test_cycle': {
            'agents': ['test-expert'],
            'parallel': False,
            'followup': 'test-report-followup'  # 测试后自动跟进
        },

        # Bug 修复任务
        'bug_fix_backend': {
            'agents': ['python-expert', 'test-expert'],
            'parallel': True  # 修复和验证并行
        },
        'bug_fix_frontend': {
            'agents': ['frontend-expert', 'test-expert'],
            'parallel': True
        },
        'bug_fix_fullstack': {
            'agents': ['test-report-followup'],  # 统一协调
            'parallel': False
        }
    }

    return dispatch_map.get(task_type, {
        'agents': ['python-expert'],
        'parallel': False
    })
```

### 策略 3: 按问题优先级调度

```python
def get_agents_by_problems(problems):
    """根据问题列表智能调度多个 Agent 并行处理"""

    # 按类型分组问题
    backend_problems = [p for p in problems if p['scope'] == 'backend']
    frontend_problems = [p for p in problems if p['scope'] == 'frontend']
    test_problems = [p for p in problems if p['scope'] == 'test']

    agents_to_dispatch = []

    # 有后端问题 → 调度 python-expert
    if backend_problems:
        agents_to_dispatch.append({
            'agent': 'python-expert',
            'tasks': backend_problems,
            'priority': min(p['priority'] for p in backend_problems)
        })

    # 有前端问题 → 调度 frontend-expert
    if frontend_problems:
        agents_to_dispatch.append({
            'agent': 'frontend-expert',
            'tasks': frontend_problems,
            'priority': min(p['priority'] for p in frontend_problems)
        })

    # 有测试问题 → 调度 test-expert
    if test_problems:
        agents_to_dispatch.append({
            'agent': 'test-expert',
            'tasks': test_problems,
            'priority': min(p['priority'] for p in test_problems)
        })

    # 按优先级排序
    agents_to_dispatch.sort(key=lambda x: x['priority'])

    return agents_to_dispatch
```

---

## 并行执行模式

### 模式 1: 前后端并行开发

```
┌─────────────────────────────────────────────────────┐
│                   tech-manager                       │
│                   (协调者)                           │
└─────────────────────┬───────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  python-expert  │     │ frontend-expert │
│   (后端 API)    │     │   (前端 UI)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
              ┌─────────────┐
              │   联调验证   │
              └─────────────┘
```

**调度代码:**
```python
# 使用 Task tool 并行启动
parallel_tasks = [
    {
        'agent': 'python-expert',
        'prompt': f'''
实现以下后端 API:
{backend_tasks}

完成后更新状态文件。
''',
        'run_in_background': True
    },
    {
        'agent': 'frontend-expert',
        'prompt': f'''
实现以下前端功能:
{frontend_tasks}

API 接口文档: {api_spec}
完成后更新状态文件。
''',
        'run_in_background': True
    }
]
```

### 模式 2: 测试与修复并行

```
┌─────────────────────────────────────────────────────┐
│               test-report-followup                   │
│                   (协调者)                           │
└─────────────────────┬───────────────────────────────┘
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ python-  │   │ frontend-│   │  test-   │
│  expert  │   │  expert  │   │  expert  │
│(修后端)  │   │(修前端)  │   │(回归测试)│
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┴──────────────┘
                    ▼
              ┌─────────────┐
              │  验证通过?  │
              └─────────────┘
```

### 模式 3: 多模块并行开发

```
┌─────────────────────────────────────────────────────┐
│                  continuous-dev-loop                 │
│                     (主控)                           │
└─────────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
┌────────┐      ┌────────┐       ┌────────┐
│模块 A  │      │模块 B  │       │模块 C  │
│python- │      │python- │       │frontend│
│expert  │      │expert  │       │-expert │
└────────┘      └────────┘       └────────┘
```

---

## 调度执行流程

### 完整调度流程

```python
def execute_with_agents(health_score, problems, current_task):
    """
    智能调度多 Agent 执行任务
    """

    # 1. 确定调度策略
    if current_task:
        # 有明确任务，按任务类型调度
        dispatch = get_agents_by_task(current_task['type'], project_type)
    elif problems:
        # 有问题待解决，按问题调度
        dispatch = get_agents_by_problems(problems)
    else:
        # 按健康度阶段调度
        dispatch = get_agents_by_health(health_score)

    # 2. 准备 Agent 任务
    agent_tasks = prepare_agent_tasks(dispatch, problems, current_task)

    # 3. 执行调度
    if dispatch.get('parallel', False) and len(agent_tasks) > 1:
        # 并行执行
        results = execute_parallel(agent_tasks)
    else:
        # 串行执行
        results = execute_sequential(agent_tasks)

    # 4. 汇总结果
    return aggregate_results(results)


def execute_parallel(agent_tasks):
    """
    并行执行多个 Agent 任务
    使用 Task tool 的并行能力
    """

    # 构建并行调用
    # 注意：在实际执行时，这会转换为多个 Task tool 调用
    parallel_calls = []

    for task in agent_tasks:
        parallel_calls.append({
            'tool': 'Task',
            'params': {
                'subagent_type': 'general-purpose',
                'description': f"{task['agent']} 执行任务",
                'prompt': f'''
使用 {task['agent']} skill 执行以下任务:

## 任务描述
{task['description']}

## 具体内容
{task['details']}

## 完成标准
{task['acceptance_criteria']}

## 状态更新
完成后更新 .dev-state/state.json
''',
                'run_in_background': True
            }
        })

    return parallel_calls
```

---

## Agent 协作协议

### 状态同步

所有 Agent 通过 `.dev-state/state.json` 同步状态：

```json
{
  "agent_coordination": {
    "active_agents": [
      {
        "agent": "python-expert",
        "task_id": "T001",
        "status": "running",
        "started_at": "2024-01-31T10:00:00Z",
        "progress": "60%"
      },
      {
        "agent": "frontend-expert",
        "task_id": "T002",
        "status": "running",
        "started_at": "2024-01-31T10:00:00Z",
        "progress": "40%"
      }
    ],
    "completed_agents": [],
    "pending_sync": false,
    "sync_point": null
  }
}
```

### 依赖等待

```python
def check_dependencies(task):
    """检查任务依赖是否满足"""

    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    completed = [a['task_id'] for a in state['agent_coordination']['completed_agents']]

    for dep in task.get('dependencies', []):
        if dep not in completed:
            return False, f"等待 {dep} 完成"

    return True, None
```

### 冲突避免

```python
def acquire_file_lock(agent_name, file_path):
    """获取文件锁，避免多 Agent 同时修改"""

    lock_file = f".dev-state/locks/{file_path.replace('/', '_')}.lock"

    if os.path.exists(lock_file):
        with open(lock_file, 'r') as f:
            lock_info = json.load(f)
        if lock_info['agent'] != agent_name:
            return False, f"文件被 {lock_info['agent']} 锁定"

    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    with open(lock_file, 'w') as f:
        json.dump({
            'agent': agent_name,
            'locked_at': datetime.utcnow().isoformat()
        }, f)

    return True, None
```

---

## 典型调度场景

### 场景 1: 新功能开发 (健康度 40-60)

```
输入: 需要实现用户管理模块

调度决策:
1. 主控: tech-manager
2. 并行 Agent:
   - python-expert: 实现用户 CRUD API
   - frontend-expert: 实现用户管理界面

执行流程:
1. tech-manager 分析需求，拆分前后端任务
2. 并行启动 python-expert 和 frontend-expert
3. 等待两者完成
4. tech-manager 执行联调验证
5. 更新健康度
```

### 场景 2: Bug 修复 (有测试报告)

```
输入: 测试报告显示 5 个 Bug (3后端 + 2前端)

调度决策:
1. 主控: test-report-followup
2. 并行 Agent:
   - python-expert: 修复 3 个后端 Bug
   - frontend-expert: 修复 2 个前端 Bug
   - test-expert: 准备回归测试

执行流程:
1. test-report-followup 解析报告，分派任务
2. 并行启动修复 Agent
3. 修复完成后，test-expert 执行回归
4. 验证所有 Bug 已修复
5. 更新健康度
```

### 场景 3: 快速原型 (健康度 < 20)

```
输入: 空项目 + 需求描述

调度决策:
1. 主控: product-expert
2. 后续: tech-manager → 并行开发

执行流程:
1. product-expert 创建 PRD 和 UI 设计
2. tech-manager 接管，创建技术方案
3. 并行启动前后端开发
4. 测试验证
5. 达到可用状态
```

### 场景 4: 测试补充 (健康度 60-75)

```
输入: 功能完整但测试覆盖不足

调度决策:
1. 主控: test-expert
2. 并行: python-expert (边测边修)

执行流程:
1. test-expert 设计测试方案
2. 执行测试，发现问题
3. 并行调度 python-expert 修复
4. 回归验证
5. 更新健康度
```

---

## 效率优化

### 并行度控制

```python
MAX_PARALLEL_AGENTS = 3  # 最大并行 Agent 数

def optimize_parallelism(tasks):
    """优化并行度，避免资源竞争"""

    # 按依赖关系分组
    independent_tasks = [t for t in tasks if not t.get('dependencies')]
    dependent_tasks = [t for t in tasks if t.get('dependencies')]

    # 独立任务可并行，但不超过最大并行度
    parallel_batch = independent_tasks[:MAX_PARALLEL_AGENTS]
    sequential_queue = independent_tasks[MAX_PARALLEL_AGENTS:] + dependent_tasks

    return parallel_batch, sequential_queue
```

### 任务合并

```python
def merge_similar_tasks(tasks):
    """合并相似任务，减少 Agent 调度开销"""

    # 按 Agent 类型分组
    by_agent = {}
    for task in tasks:
        agent = task['agent']
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(task)

    # 合并同一 Agent 的多个小任务
    merged = []
    for agent, agent_tasks in by_agent.items():
        if len(agent_tasks) > 1:
            merged.append({
                'agent': agent,
                'tasks': agent_tasks,
                'description': f"批量执行 {len(agent_tasks)} 个任务"
            })
        else:
            merged.append(agent_tasks[0])

    return merged
```

### 结果缓存

```python
def cache_agent_result(agent, task_hash, result):
    """缓存 Agent 执行结果，避免重复执行"""

    cache_dir = '.dev-state/cache'
    os.makedirs(cache_dir, exist_ok=True)

    cache_file = f"{cache_dir}/{agent}_{task_hash}.json"
    with open(cache_file, 'w') as f:
        json.dump({
            'result': result,
            'cached_at': datetime.utcnow().isoformat(),
            'ttl_hours': 24
        }, f)
```
