# 智能决策引擎

## 决策流程

```
健康度评估 → 问题识别 → 优先级排序 → Agent选择 → 并行策略 → 执行
```

---

## 核心决策算法

```python
def decide_next_action(health_score, problems=None):
    """
    根据健康度和问题列表决定下一步行动

    Returns:
        {
            'action': str,           # 行动类型
            'agents': list,          # 需要调度的 Agent
            'parallel': bool,        # 是否并行执行
            'priority': str,         # 优先级 P0-P4
            'expected_delta': str    # 预期健康度提升
        }
    """

    # 1. 优先处理阻塞问题
    if problems:
        blockers = [p for p in problems if p.get('priority') == 'P0']
        if blockers:
            return {
                'action': 'fix_blocker',
                'agents': [get_agent_for_problem(blockers[0])],
                'parallel': False,
                'priority': 'P0',
                'expected_delta': '+5-10'
            }

    # 2. 根据健康度决定主要行动
    if health_score < 20:
        return {
            'action': 'create_requirements',
            'agents': ['product-expert'],
            'parallel': False,
            'priority': 'P1',
            'expected_delta': '+15-20'
        }

    elif health_score < 40:
        return {
            'action': 'design_and_setup',
            'agents': ['tech-manager'],
            'parallel': False,
            'priority': 'P1',
            'expected_delta': '+15-20'
        }

    elif health_score < 60:
        return {
            'action': 'parallel_development',
            'agents': ['python-expert', 'frontend-expert'],
            'parallel': True,  # 前后端并行
            'priority': 'P1',
            'expected_delta': '+15-25'
        }

    elif health_score < 75:
        return {
            'action': 'test_and_fix',
            'agents': ['test-expert', 'python-expert'],
            'parallel': True,  # 边测边修
            'priority': 'P2',
            'expected_delta': '+10-15'
        }

    elif health_score < 80:
        return {
            'action': 'polish_and_verify',
            'agents': ['test-report-followup'],
            'parallel': False,
            'priority': 'P2',
            'expected_delta': '+5-10'
        }

    else:
        return {
            'action': 'complete',
            'agents': [],
            'parallel': False,
            'priority': 'P4',
            'expected_delta': '0'
        }
```

---

## 问题识别与分类

### 问题类型

| 类型 | 代码 | 描述 | 默认优先级 |
|------|------|------|------------|
| 阻塞问题 | `BLOCKER` | 项目无法运行 | P0 |
| 功能缺失 | `MISSING` | 核心功能未实现 | P1 |
| 测试失败 | `TEST_FAIL` | 测试用例失败 | P2 |
| 质量问题 | `QUALITY` | 代码质量差 | P3 |
| 文档缺失 | `DOC_MISS` | 缺少必要文档 | P4 |

### 问题检测

```python
def detect_problems():
    """检测项目中的问题"""
    problems = []

    # 1. 检测阻塞问题
    if not can_start_project():
        problems.append({
            'type': 'BLOCKER',
            'priority': 'P0',
            'description': '项目无法启动',
            'scope': 'backend'
        })

    # 2. 检测测试失败
    failed_tests = get_failed_tests()
    for test in failed_tests:
        problems.append({
            'type': 'TEST_FAIL',
            'priority': 'P2',
            'description': f'测试失败: {test}',
            'scope': detect_scope(test)
        })

    # 3. 检测代码质量问题
    lint_errors = run_linter()
    if lint_errors > 10:
        problems.append({
            'type': 'QUALITY',
            'priority': 'P3',
            'description': f'{lint_errors} 个代码规范问题',
            'scope': 'all'
        })

    return problems
```

---

## Agent 选择策略

### 按问题类型选择

```python
def get_agent_for_problem(problem):
    """根据问题类型选择合适的 Agent"""

    agent_map = {
        'BLOCKER': {
            'backend': 'python-expert',
            'frontend': 'frontend-expert',
            'all': 'tech-manager'
        },
        'MISSING': {
            'backend': 'python-expert',
            'frontend': 'frontend-expert',
            'all': 'tech-manager'
        },
        'TEST_FAIL': {
            'backend': 'python-expert',
            'frontend': 'frontend-expert',
            'all': 'test-report-followup'
        },
        'QUALITY': {
            'backend': 'python-expert',
            'frontend': 'frontend-expert',
            'all': 'tech-manager'
        },
        'DOC_MISS': {
            'all': 'product-expert'
        }
    }

    problem_type = problem.get('type', 'MISSING')
    scope = problem.get('scope', 'all')

    return agent_map.get(problem_type, {}).get(scope, 'tech-manager')
```

### 按任务类型选择

| 任务类型 | 首选 Agent | 备选 | 可并行 |
|----------|------------|------|--------|
| 需求分析 | product-expert | - | 否 |
| 技术设计 | tech-manager | - | 否 |
| 后端开发 | python-expert | - | 是 |
| 前端开发 | frontend-expert | - | 是 |
| 全栈开发 | tech-manager | python-expert + frontend-expert | 是 |
| 测试执行 | test-expert | - | 否 |
| Bug修复 | test-report-followup | python-expert | 是 |

---

## 并行执行策略

### 可并行的场景

```python
PARALLEL_SCENARIOS = {
    # 前后端并行开发
    'parallel_development': {
        'agents': ['python-expert', 'frontend-expert'],
        'condition': lambda h: 40 <= h < 60,
        'description': '前后端并行开发'
    },

    # 测试与修复并行
    'test_and_fix': {
        'agents': ['test-expert', 'python-expert'],
        'condition': lambda h: 60 <= h < 75,
        'description': '边测试边修复'
    },

    # 多Bug并行修复
    'parallel_bugfix': {
        'agents': ['python-expert', 'frontend-expert', 'test-expert'],
        'condition': lambda problems: len(problems) >= 3,
        'description': '多Bug并行修复'
    }
}
```

### 并行执行约束

```python
MAX_PARALLEL_AGENTS = 3  # 最大并行数

def should_parallelize(agents, problems):
    """判断是否应该并行执行"""

    # 1. Agent 数量限制
    if len(agents) > MAX_PARALLEL_AGENTS:
        return False

    # 2. 检查依赖关系
    if has_dependencies(agents):
        return False

    # 3. 检查资源冲突
    if has_file_conflicts(agents):
        return False

    return True
```

---

## 决策日志

每次决策都应记录：

```python
def log_decision(health_score, problems, decision):
    """记录决策日志"""

    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'health_score': health_score,
        'problems_count': len(problems) if problems else 0,
        'decision': {
            'action': decision['action'],
            'agents': decision['agents'],
            'parallel': decision['parallel'],
            'priority': decision['priority']
        },
        'reason': generate_reason(health_score, problems, decision)
    }

    # 追加到状态文件
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    if 'decision_log' not in state:
        state['decision_log'] = []

    state['decision_log'].append(log_entry)

    # 只保留最近 20 条
    state['decision_log'] = state['decision_log'][-20:]

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2)

def generate_reason(health_score, problems, decision):
    """生成决策原因说明"""

    if decision['action'] == 'fix_blocker':
        return f"检测到 P0 阻塞问题，优先修复"

    if health_score < 20:
        return f"健康度 {health_score} < 20，需要先建立需求"

    if health_score < 40:
        return f"健康度 {health_score} < 40，需要技术设计和架构"

    if health_score < 60:
        return f"健康度 {health_score} < 60，进入并行开发阶段"

    if health_score < 75:
        return f"健康度 {health_score} < 75，需要测试和修复"

    if health_score < 80:
        return f"健康度 {health_score} < 80，进行收尾优化"

    return f"健康度 {health_score} >= 80，项目达到可用状态"
```

---

## 自适应调整

### 行动失败时的调整

```python
def adjust_on_failure(action, failure_reason, retry_count):
    """行动失败时调整策略"""

    if retry_count >= 3:
        # 重试 3 次后跳过
        return {
            'action': 'skip_and_continue',
            'record_blocker': True
        }

    adjustments = {
        'agent_error': {
            'action': 'try_alternative_agent',
            'fallback': get_fallback_agent(action['agents'][0])
        },
        'task_too_complex': {
            'action': 'split_task',
            'strategy': 'divide_into_subtasks'
        },
        'dependency_missing': {
            'action': 'resolve_dependency_first',
            'priority': 'P0'
        },
        'timeout': {
            'action': 'retry_with_smaller_scope',
            'reduce_scope': True
        }
    }

    return adjustments.get(failure_reason, {
        'action': 'retry',
        'delay': 60
    })
```

### 进度停滞时的调整

```python
def adjust_on_stagnation(health_history):
    """健康度长时间不提升时调整"""

    if len(health_history) < 3:
        return None

    recent = health_history[-3:]

    # 检查是否停滞
    if recent[-1] <= recent[0]:
        return {
            'action': 'change_strategy',
            'options': [
                'try_different_approach',
                'skip_current_task',
                'request_human_review'
            ],
            'reason': f"健康度停滞在 {recent[-1]}，连续 3 次无提升"
        }

    return None
```

---

## 完整决策流程示例

```python
def execute_decision_cycle():
    """执行一个完整的决策周期"""

    # 1. 评估健康度
    health = assess_health()
    print(f"当前健康度: {health['total']}/100")

    # 2. 检测问题
    problems = detect_problems()
    print(f"检测到 {len(problems)} 个问题")

    # 3. 做出决策
    decision = decide_next_action(health['total'], problems)
    print(f"决策: {decision['action']}")
    print(f"调度 Agent: {decision['agents']}")
    print(f"并行执行: {decision['parallel']}")

    # 4. 记录决策
    log_decision(health['total'], problems, decision)

    # 5. 检查是否完成
    if decision['action'] == 'complete':
        print("✅ 项目达到可用状态！")
        return True

    # 6. 执行决策
    if decision['parallel'] and len(decision['agents']) > 1:
        print(f"并行启动 {len(decision['agents'])} 个 Agent...")
        # 使用 Task tool 并行调度
    else:
        print(f"启动 {decision['agents'][0]}...")
        # 使用 Skill tool 调度

    return False
```
