# 智能决策引擎

## 决策流程

```
项目分析 → 健康度评估 → 问题识别 → 行动选择 → 执行 → 验证 → 循环
```

---

## 问题识别与优先级

### 问题类型定义

| 类型 | 代码 | 描述 | 影响 |
|------|------|------|------|
| 阻塞问题 | BLOCKER | 项目无法运行 | 必须立即解决 |
| 功能缺失 | MISSING | 核心功能未实现 | 影响可用性 |
| 测试失败 | TEST_FAIL | 测试用例失败 | 影响质量 |
| 质量问题 | QUALITY | 代码质量差 | 影响维护 |
| 文档缺失 | DOC_MISS | 缺少必要文档 | 影响理解 |

### 优先级矩阵

```
紧急度 ↑
    │
    │  P0: BLOCKER     P1: MISSING (核心)
    │  立即处理         优先处理
    │
    │  P2: TEST_FAIL   P3: QUALITY
    │  尽快处理         计划处理
    │
    │  P4: DOC_MISS    P5: 优化建议
    │  有空处理         可选处理
    │
    └────────────────────────────→ 影响范围
```

---

## 行动选择算法

```python
def select_next_action(health_score, problems):
    """
    根据健康度和问题列表选择下一步行动
    """

    # 1. 优先处理阻塞问题
    blockers = [p for p in problems if p['type'] == 'BLOCKER']
    if blockers:
        return {
            'action': 'fix_blocker',
            'target': blockers[0],
            'skill': 'python-expert',  # 或根据问题类型选择
            'priority': 'P0'
        }

    # 2. 根据健康度决定主要行动
    if health_score < 20:
        return {
            'action': 'create_requirements',
            'skill': 'product-expert',
            'expected_delta': '+15-20'
        }

    elif health_score < 40:
        return {
            'action': 'implement_core',
            'skill': 'python-expert',
            'expected_delta': '+15-20'
        }

    elif health_score < 60:
        # 检查是功能缺失还是测试不足
        missing = [p for p in problems if p['type'] == 'MISSING']
        if missing:
            return {
                'action': 'implement_feature',
                'target': missing[0],
                'skill': 'python-expert',
                'expected_delta': '+10-15'
            }
        else:
            return {
                'action': 'add_tests',
                'skill': 'test-expert',
                'expected_delta': '+10-15'
            }

    elif health_score < 80:
        # 检查具体短板
        test_fails = [p for p in problems if p['type'] == 'TEST_FAIL']
        if test_fails:
            return {
                'action': 'fix_tests',
                'target': test_fails,
                'skill': 'test-report-followup',
                'expected_delta': '+5-10'
            }

        quality_issues = [p for p in problems if p['type'] == 'QUALITY']
        if quality_issues:
            return {
                'action': 'improve_quality',
                'target': quality_issues,
                'skill': 'python-expert',
                'expected_delta': '+5-10'
            }

        return {
            'action': 'polish',
            'skill': 'test-expert',
            'expected_delta': '+5-10'
        }

    else:
        # 已达可用状态
        return {
            'action': 'complete',
            'generate_report': True
        }
```

---

## Skill 选择策略

### 按行动类型选择

| 行动 | 首选 Skill | 备选 | 选择条件 |
|------|------------|------|----------|
| 需求分析 | product-expert | prd-template | 复杂需求用 product-expert |
| 技术设计 | tech-plan-template | - | - |
| 前端开发 | frontend-expert | - | React/Vue 项目 |
| 后端开发 | python-expert | - | Python/FastAPI 项目 |
| 全栈原型 | rapid-prototype-workflow | - | 新项目快速启动 |
| 测试设计 | test-expert | - | - |
| Bug 修复 | test-report-followup | - | 有测试报告时 |
| 代码审查 | code-reviewer | - | 质量问题 |

### 按项目类型选择

```python
def select_skill_by_project(project_type, action):
    """根据项目类型选择合适的 Skill"""

    skill_map = {
        'python_backend': {
            'implement': 'python-expert',
            'test': 'test-expert',
            'fix': 'test-report-followup'
        },
        'react_frontend': {
            'implement': 'frontend-expert',
            'test': 'test-expert',
            'fix': 'test-report-followup'
        },
        'fullstack': {
            'implement': 'tech-manager',  # 协调前后端
            'test': 'test-expert',
            'fix': 'test-report-followup'
        },
        'prototype': {
            'implement': 'rapid-prototype-workflow',
            'test': 'test-expert',
            'fix': 'test-report-followup'
        }
    }

    return skill_map.get(project_type, {}).get(action, 'python-expert')
```

---

## 行动执行模板

### 模板 1: 实现功能

```markdown
## 当前行动: 实现功能

### 目标
{feature_description}

### 使用 Skill
{skill_name}

### 执行步骤
1. 分析需求文档中的功能描述
2. 设计实现方案
3. 编写代码
4. 添加基础测试
5. 验证功能正常

### 完成标准
- [ ] 功能按需求实现
- [ ] 基础测试通过
- [ ] 无阻塞错误

### 预期健康度提升
{expected_delta}
```

### 模板 2: 修复问题

```markdown
## 当前行动: 修复问题

### 问题描述
{problem_description}

### 问题类型
{problem_type} (优先级: {priority})

### 使用 Skill
{skill_name}

### 执行步骤
1. 定位问题根因
2. 设计修复方案
3. 实施修复
4. 验证修复有效
5. 确保无回归

### 完成标准
- [ ] 问题已修复
- [ ] 相关测试通过
- [ ] 无新问题引入

### 预期健康度提升
{expected_delta}
```

### 模板 3: 补充测试

```markdown
## 当前行动: 补充测试

### 测试目标
{test_target}

### 当前覆盖率
{current_coverage}%

### 使用 Skill
test-expert

### 执行步骤
1. 分析未覆盖的代码路径
2. 设计测试用例
3. 编写测试代码
4. 运行测试验证
5. 检查覆盖率提升

### 完成标准
- [ ] 新增测试用例 >= {min_cases}
- [ ] 所有测试通过
- [ ] 覆盖率提升 >= {min_delta}%

### 预期健康度提升
{expected_delta}
```

---

## 决策日志

每次决策都应记录：

```json
{
  "decision_log": [
    {
      "timestamp": "2024-01-31T10:00:00Z",
      "health_score": 45,
      "problems_found": [
        {"type": "MISSING", "desc": "用户登录功能未实现"},
        {"type": "TEST_FAIL", "desc": "2个测试失败"}
      ],
      "decision": {
        "action": "implement_feature",
        "target": "用户登录功能",
        "skill": "python-expert",
        "reason": "功能缺失优先于测试失败"
      }
    }
  ]
}
```

---

## 自适应调整

### 行动失败时的调整

```python
def adjust_on_failure(action, failure_reason):
    """行动失败时调整策略"""

    adjustments = {
        'skill_not_suitable': {
            'action': 'try_alternative_skill',
            'fallback': get_alternative_skill(action['skill'])
        },
        'task_too_complex': {
            'action': 'split_task',
            'strategy': 'divide_and_conquer'
        },
        'dependency_missing': {
            'action': 'resolve_dependency',
            'priority': 'P0'
        },
        'unknown_error': {
            'action': 'record_and_skip',
            'notify': True
        }
    }

    return adjustments.get(failure_reason, adjustments['unknown_error'])
```

### 进度停滞时的调整

```python
def adjust_on_stagnation(health_history):
    """健康度长时间不提升时调整"""

    # 检查最近 3 次评估
    recent = health_history[-3:]
    if len(recent) < 3:
        return None

    # 如果健康度没有提升
    if recent[-1]['score'] <= recent[0]['score']:
        return {
            'action': 'change_strategy',
            'options': [
                'try_different_skill',
                'skip_current_problem',
                'request_human_help'
            ]
        }

    return None
```
