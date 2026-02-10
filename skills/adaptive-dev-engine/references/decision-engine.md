# 智能决策引擎

## 决策流程

```
健康度评估 → 维度比率计算 → 最弱维度识别 → Agent选择 → 并行策略 → 执行
```

---

## 核心决策算法：维度优先决策

不再使用总分区间来决定行动，而是找到**最弱维度**，针对性调度 Agent。

### 维度定义

| 维度 | 满分 | 对应 Agent |
|------|------|-----------|
| requirements（需求完整度） | 20 | product-expert |
| code（代码实现度） | 25 | tech-manager 或 python-expert + frontend-expert |
| runnable（可运行度） | 20 | tech-manager |
| tests（测试覆盖度） | 20 | test-expert |
| quality（代码质量） | 15 | python-expert 或 frontend-expert |

### 决策算法

```python
DIMENSION_MAX = {
    'requirements': 20,
    'code': 25,
    'runnable': 20,
    'tests': 20,
    'quality': 15,
}

DIMENSION_THRESHOLD = 0.70  # 70% 视为该维度达标

def decide_next_action(health):
    """
    基于维度优先的决策算法

    Args:
        health: {
            'score': int,
            'breakdown': {
                'requirements': int,
                'code': int,
                'runnable': int,
                'tests': int,
                'quality': int
            }
        }

    Returns:
        {
            'action': str,
            'agents': list,
            'parallel': bool,
            'reason': str
        }
    """

    # 完成条件：总分 >= 80
    if health['score'] >= 80:
        return {
            'action': 'complete',
            'agents': [],
            'parallel': False,
            'reason': f"总分 {health['score']} >= 80，项目达到可用状态"
        }

    # 计算每个维度的比率
    dimensions = health['breakdown']
    ratios = {}
    for dim, score in dimensions.items():
        max_score = DIMENSION_MAX[dim]
        ratios[dim] = score / max_score

    # 检查是否所有维度都 > 70%
    all_above_threshold = all(r >= DIMENSION_THRESHOLD for r in ratios.values())

    if all_above_threshold:
        return {
            'action': 'polish',
            'agents': ['test-report-followup'],
            'parallel': False,
            'reason': f"所有维度均 >= 70%，进入收尾打磨阶段"
        }

    # 找到最弱维度（比率最低）
    weakest_dim = min(ratios, key=ratios.get)
    weakest_ratio = ratios[weakest_dim]
    weakest_score = dimensions[weakest_dim]

    # 根据最弱维度调度 Agent
    return dispatch_by_weakest(weakest_dim, weakest_score, weakest_ratio)


def dispatch_by_weakest(dim, score, ratio):
    """根据最弱维度选择 Agent"""

    if dim == 'requirements':
        return {
            'action': 'improve_requirements',
            'agents': ['product-expert'],
            'parallel': False,
            'reason': f"需求维度最弱 ({score}/20, {ratio:.0%})，调度 product-expert 完善需求"
        }

    elif dim == 'code':
        if score < 10:
            # 代码量极低，先让 tech-manager 做技术设计和任务拆分
            return {
                'action': 'design_and_plan',
                'agents': ['tech-manager'],
                'parallel': False,
                'reason': f"代码维度最弱且极低 ({score}/25, {ratio:.0%})，先由 tech-manager 做技术设计"
            }
        else:
            # 有一定代码基础，前后端并行开发
            return {
                'action': 'parallel_development',
                'agents': ['python-expert', 'frontend-expert'],
                'parallel': True,
                'reason': f"代码维度最弱 ({score}/25, {ratio:.0%})，前后端并行开发"
            }

    elif dim == 'runnable':
        return {
            'action': 'make_runnable',
            'agents': ['tech-manager'],
            'parallel': False,
            'reason': f"可运行度最弱 ({score}/20, {ratio:.0%})，调度 tech-manager 解决运行问题"
        }

    elif dim == 'tests':
        return {
            'action': 'add_tests',
            'agents': ['test-expert'],
            'parallel': False,
            'reason': f"测试维度最弱 ({score}/20, {ratio:.0%})，调度 test-expert 补充测试"
        }

    elif dim == 'quality':
        # 质量问题根据项目类型选择 Agent
        return {
            'action': 'improve_quality',
            'agents': ['python-expert', 'frontend-expert'],
            'parallel': True,
            'reason': f"质量维度最弱 ({score}/15, {ratio:.0%})，调度开发专家改善代码质量"
        }
```

---

## 问题检测（简化版）

### 问题类型

| 类型 | 描述 | 影响维度 |
|------|------|----------|
| 项目无法启动 | 缺少依赖、配置错误 | runnable |
| 核心功能缺失 | 关键 API/页面未实现 | code |
| 测试失败 | 用例执行不通过 | tests |
| 代码规范差 | lint 错误过多 | quality |
| 需求不清晰 | PRD 缺失或不完整 | requirements |

### 检测逻辑

```python
def detect_problems(health):
    """基于维度分数快速检测问题"""
    problems = []
    dimensions = health['breakdown']

    if dimensions['runnable'] == 0:
        problems.append({
            'type': 'BLOCKER',
            'dimension': 'runnable',
            'description': '项目完全无法运行'
        })

    if dimensions['requirements'] < 5:
        problems.append({
            'type': 'MISSING',
            'dimension': 'requirements',
            'description': '需求文档严重不足'
        })

    if dimensions['code'] < 5:
        problems.append({
            'type': 'MISSING',
            'dimension': 'code',
            'description': '几乎没有代码实现'
        })

    return problems
```

---

## 并行执行策略

### 可并行的场景

```python
PARALLEL_SCENARIOS = {
    # 前后端并行开发（code 维度最弱且 score >= 10）
    'parallel_development': {
        'agents': ['python-expert', 'frontend-expert'],
        'description': '前后端并行开发'
    },

    # 测试与修复并行
    'test_and_fix': {
        'agents': ['test-expert', 'test-report-followup'],
        'description': '边测试边修复'
    },

    # 质量改善并行
    'parallel_quality': {
        'agents': ['python-expert', 'frontend-expert'],
        'description': '前后端并行改善代码质量'
    }
}
```

### 并行执行约束

```python
MAX_PARALLEL_AGENTS = 3  # 最大并行数

def should_parallelize(agents):
    """判断是否应该并行执行"""

    # Agent 数量限制
    if len(agents) > MAX_PARALLEL_AGENTS:
        return False

    # 检查是否操作不同目录（通过 prompt 约束）
    # 并行 Agent 必须操作不同的文件目录
    return True
```

---

## 停滞检测

当健康度连续多个 session 没有提升时，自动切换策略。

```python
def detect_stagnation(health_history):
    """
    检测健康度是否停滞

    Args:
        health_history: 最近 N 次 session 的健康度记录
            [{'score': 45, 'session': 3}, {'score': 46, 'session': 4}, ...]

    Returns:
        None 或 调整建议
    """

    if len(health_history) < 3:
        return None

    recent = health_history[-3:]
    scores = [h['score'] for h in recent]

    # 连续 3 次健康度没有明显提升（提升 < 2 分）
    if scores[-1] - scores[0] < 2:
        # 找到当前最弱维度
        current = recent[-1]
        weakest = min(current['breakdown'], key=lambda d: current['breakdown'][d] / DIMENSION_MAX[d])

        return {
            'stagnant': True,
            'sessions_stuck': 3,
            'stuck_dimension': weakest,
            'suggestion': 'change_strategy',
            'options': [
                f"换一个 Agent 处理 {weakest} 维度",
                f"将 {weakest} 维度的任务拆分为更小的子任务",
                "跳过当前维度，先提升其他维度",
                "请求人工介入审查"
            ],
            'reason': f"健康度停滞在 {scores[-1]}，连续 3 个 session 无明显提升，瓶颈在 {weakest} 维度"
        }

    return None
```

---

## 决策日志

每次决策都应记录到 `.dev-state/state.json`：

```python
def log_decision(health, decision):
    """记录决策日志"""

    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'health_score': health['score'],
        'breakdown': health['breakdown'],
        'ratios': {
            dim: round(score / DIMENSION_MAX[dim], 2)
            for dim, score in health['breakdown'].items()
        },
        'weakest_dimension': min(
            health['breakdown'],
            key=lambda d: health['breakdown'][d] / DIMENSION_MAX[d]
        ),
        'decision': {
            'action': decision['action'],
            'agents': decision['agents'],
            'parallel': decision['parallel'],
            'reason': decision['reason']
        }
    }

    # 追加到 state.json 的 decision_log
    # 只保留最近 20 条
    state['decision_log'] = state.get('decision_log', [])
    state['decision_log'].append(log_entry)
    state['decision_log'] = state['decision_log'][-20:]
```

---

## 完整决策流程示例

```python
def execute_decision_cycle(health, health_history):
    """执行一个完整的决策周期"""

    # 1. 检查停滞
    stagnation = detect_stagnation(health_history)
    if stagnation:
        print(f"警告: {stagnation['reason']}")
        print(f"建议: {stagnation['options']}")
        # 可选择自动切换策略或提示用户

    # 2. 检测阻塞问题
    problems = detect_problems(health)
    if any(p['type'] == 'BLOCKER' for p in problems):
        print("检测到阻塞问题，优先处理")

    # 3. 维度优先决策
    decision = decide_next_action(health)
    print(f"决策: {decision['action']}")
    print(f"原因: {decision['reason']}")
    print(f"调度 Agent: {decision['agents']}")
    print(f"并行执行: {decision['parallel']}")

    # 4. 记录决策
    log_decision(health, decision)

    # 5. 执行
    if decision['action'] == 'complete':
        print("项目达到可用状态！")
        return True

    if decision['parallel'] and len(decision['agents']) > 1:
        # 使用 Task tool 并行调度
        pass
    else:
        # 使用 Skill tool 单 Agent 调度
        pass

    return False
```
