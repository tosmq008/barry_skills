---
name: continuous-dev-loop
description: "自适应持续开发引擎。智能分析任何项目状态，动态调度多 Agent 并行执行，持续迭代直到达到可用状态。支持新项目从零开始、已有项目继续开发、Bug修复、性能优化等任意场景。"
license: MIT
compatibility: "Works with external daemon script. Orchestrates product-expert, tech-manager, python-expert, frontend-expert, test-expert, test-report-followup."
metadata:
  category: automation
  phase: orchestration
  version: "4.0.0"
allowed-tools: bash read_file write_file task
---

# Continuous Dev Loop v4.0 - 自适应持续开发引擎

你正在被外部守护进程循环调用，实现 7×24 持续开发。

## 核心理念

```
任何项目状态 → 智能分析 → 动态调度多Agent → 并行执行 → 达到可用状态
```

---

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

## 第一步：项目健康度分析（必须先执行）

每次会话开始，执行完整的项目健康度分析：

```bash
# 1. 基础结构检查
echo "=== 项目结构 ==="
ls -la
ls -la docs/ src/ client/ admin/ website/ app/ 2>/dev/null

# 2. 文档完整性
echo "=== 文档状态 ==="
ls docs/prd/*.md 2>/dev/null | wc -l
ls docs/api/*.md 2>/dev/null | wc -l
ls docs/test/*.md 2>/dev/null | wc -l

# 3. 代码状态
echo "=== 代码状态 ==="
find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" 2>/dev/null | head -20
git status --short 2>/dev/null | head -20

# 4. 测试状态
echo "=== 测试状态 ==="
ls -la **/test*.py **/*_test.py **/tests/ 2>/dev/null | head -10

# 5. 运行状态
echo "=== 运行状态 ==="
cat package.json 2>/dev/null | grep -A5 '"scripts"'
cat pyproject.toml 2>/dev/null | grep -A5 '\[tool.uv\]'

# 6. 状态文件
echo "=== 持续开发状态 ==="
cat .dev-state/state.json 2>/dev/null || echo "无状态文件"
```

---

## 第二步：计算健康度评分

基于分析结果，计算项目健康度（0-100分）：

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 需求清晰度 | 20% | PRD完整性、需求文档质量 |
| 代码完整度 | 25% | 核心功能实现、代码覆盖 |
| 测试覆盖度 | 20% | 测试用例、通过率 |
| 可运行性 | 20% | 能否启动、无阻塞错误 |
| 代码质量 | 15% | 无明显Bug、代码规范 |

**可用状态定义：健康度 ≥ 80 分**

> 📄 详细评估指南: `references/health-assessment.md`

---

## 第三步：智能调度 Agent

### 按健康度阶段调度

```
健康度 < 20 (空项目/需求不清)
  └─→ 调度: product-expert
      └─→ 任务: 需求分析、PRD创建、UI设计

健康度 20-40 (有需求/无代码)
  └─→ 调度: tech-manager (主控)
      └─→ 并行: product-expert (完善需求)
      └─→ 任务: 技术方案、架构设计

健康度 40-60 (有代码/功能不全)
  └─→ 调度: tech-manager (主控)
      └─→ 并行: python-expert + frontend-expert
      └─→ 任务: 前后端并行开发

健康度 60-75 (功能完整/测试不足)
  └─→ 调度: test-expert (主控)
      └─→ 并行: python-expert + frontend-expert (边测边修)
      └─→ 任务: 测试执行、Bug修复

健康度 75-80 (接近可用/有小问题)
  └─→ 调度: test-report-followup (主控)
      └─→ 并行: test-expert (回归验证)
      └─→ 任务: 收尾优化

健康度 ≥ 80 (可用状态)
  └─→ 完成！生成交付报告
```

### 按任务类型调度

| 任务类型 | 调度 Agent | 并行模式 |
|----------|------------|----------|
| 需求分析 | product-expert | 单独执行 |
| 全栈功能 | tech-manager | 内部协调前后端 |
| 前后端开发 | python-expert + frontend-expert | **并行执行** |
| 测试执行 | test-expert | 单独执行 |
| Bug修复 | test-report-followup | 协调多Agent并行修复 |
| 后端Bug | python-expert + test-expert | **并行执行** |
| 前端Bug | frontend-expert + test-expert | **并行执行** |

### 按问题类型调度

| 问题类型 | 优先级 | 调度 Agent |
|----------|--------|------------|
| 阻塞问题 | P0 | 立即调度对应 expert |
| 功能缺失 | P1 | tech-manager 协调 |
| 测试失败 | P2 | test-report-followup |
| 质量问题 | P3 | python-expert / frontend-expert |
| 文档缺失 | P4 | product-expert |

> 📄 详细调度策略: `references/multi-agent-orchestration.md`

---

## 第四步：并行执行 Sub Agents

### 并行执行模式

**模式 1: 前后端并行开发**

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

**模式 2: 测试与修复并行**

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
└──────────┘   └──────────┘   └──────────┘
```

### 并行调度代码示例

```python
# 使用 Task tool 并行启动多个 Sub Agent
# 在单个消息中发送多个 Task 调用实现并行

# 示例：前后端并行开发
parallel_tasks = [
    {
        'tool': 'Task',
        'subagent_type': 'general-purpose',
        'description': 'python-expert 后端开发',
        'prompt': '''
使用 python-expert skill 实现以下后端功能:
{backend_tasks}

完成后更新 .dev-state/state.json
''',
        'run_in_background': True
    },
    {
        'tool': 'Task',
        'subagent_type': 'general-purpose',
        'description': 'frontend-expert 前端开发',
        'prompt': '''
使用 frontend-expert skill 实现以下前端功能:
{frontend_tasks}

API 接口文档: {api_spec}
完成后更新 .dev-state/state.json
''',
        'run_in_background': True
    }
]
```

---

## 第五步：状态同步与协调

### Agent 协调状态

```json
{
  "agent_coordination": {
    "active_agents": [
      {
        "agent": "python-expert",
        "task_id": "T001",
        "status": "running",
        "progress": "60%"
      },
      {
        "agent": "frontend-expert",
        "task_id": "T002",
        "status": "running",
        "progress": "40%"
      }
    ],
    "completed_agents": [],
    "pending_sync": false
  }
}
```

### 依赖管理

```python
# 检查任务依赖
def check_dependencies(task):
    completed = get_completed_tasks()
    for dep in task.get('dependencies', []):
        if dep not in completed:
            return False, f"等待 {dep} 完成"
    return True, None
```

### 冲突避免

- 同一文件不能被多个 Agent 同时修改
- 使用文件锁机制避免冲突
- 前后端分离开发，减少冲突

---

## 第六步：可用状态验证

### 必须满足（全部通过才算可用）

- [ ] **可运行**: 项目能正常启动，无阻塞错误
- [ ] **核心功能**: 主要功能可正常使用
- [ ] **基础测试**: 核心流程有测试覆盖且通过
- [ ] **无P0/P1 Bug**: 无阻塞性和严重Bug

### 验证流程

```bash
#!/bin/bash
echo "=== 可用状态验证 ==="

# 1. 可运行性
timeout 30 ./start.sh &
sleep 10
curl -s http://localhost:8000/health && echo "✅ 可运行"

# 2. 测试通过
pytest --tb=no -q && echo "✅ 测试通过"

# 3. 代码质量
ruff check . --quiet && echo "✅ 代码规范"

echo "=== 验证完成 ==="
```

---

## 典型调度场景

### 场景 1: 新项目从零开始

```
健康度: 0 → 目标: 80

调度流程:
1. product-expert → 创建 PRD (+18)
2. tech-manager → 技术方案 (+5)
3. python-expert + frontend-expert (并行) → 核心功能 (+30)
4. test-expert → 测试执行 (+15)
5. test-report-followup → Bug修复 (+12)

预计会话: 8-12 次
```

### 场景 2: 有代码有Bug

```
健康度: 55 → 目标: 80

调度流程:
1. test-expert → 执行测试，生成报告
2. test-report-followup → 解析报告，分派任务
3. python-expert + frontend-expert (并行) → 修复Bug
4. test-expert → 回归验证

预计会话: 3-5 次
```

### 场景 3: 功能完整待优化

```
健康度: 72 → 目标: 80

调度流程:
1. test-expert → 补充测试用例 (+5)
2. python-expert → 代码质量优化 (+3)
3. 验证达到可用状态

预计会话: 2-3 次
```

---

## 状态文件结构 (v4.0)

```json
{
  "version": "4.0.0",
  "project": {
    "name": "项目名称",
    "path": "/path/to/project",
    "type": "fullstack"
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
    "target": 80
  },
  "status": "running",
  "current_action": {
    "type": "parallel_development",
    "agents": ["python-expert", "frontend-expert"],
    "started_at": "2024-01-31T10:30:00Z"
  },
  "agent_coordination": {
    "active_agents": [],
    "completed_agents": []
  },
  "action_history": [],
  "sessions": {
    "count": 5,
    "total_turns": 230
  },
  "last_heartbeat": "2024-01-31T10:35:00Z"
}
```

> 📄 完整状态协议: `references/state-protocol-v4.md`

---

## 轮次限制处理

接近限制时（约 40 轮），保存断点并等待 Sub Agent 完成：

```python
# 1. 等待所有 Sub Agent 完成或保存断点
for agent in active_agents:
    if agent['status'] == 'running':
        save_agent_checkpoint(agent)

# 2. 保存主控断点
state['status'] = 'continue'
state['exit_reason'] = 'turns_limit'
state['current_action']['checkpoint'] = {
    'step': '当前步骤',
    'pending_agents': [a['agent'] for a in active_agents],
    'next_action': '下次继续的行动'
}
```

---

## 重要规则

1. **每次会话先分析健康度**，不要盲目执行
2. **优先使用并行调度**，提高执行效率
3. **健康度 ≥ 80 即可用**，不要过度优化
4. **遇到阻塞记录并跳过**，不要卡死
5. **每完成一步更新状态**，保证可恢复
6. **Sub Agent 完成后汇总结果**，统一更新健康度
7. **合理假设并记录**，遇到不确定时

---

## References

| 文档 | 用途 |
|------|------|
| `references/health-assessment.md` | 健康度评估详细指南 |
| `references/decision-engine.md` | 智能决策引擎 |
| `references/multi-agent-orchestration.md` | 多Agent编排指南 |
| `references/state-protocol-v4.md` | 状态协议 v4.0 |
| `references/recovery-scenarios.md` | 中断恢复场景 |

---

## 交付报告模板

当项目达到可用状态时，生成交付报告：

```markdown
# 项目交付报告

## 基本信息
- 项目名称: {name}
- 完成时间: {timestamp}
- 总会话数: {sessions}
- 最终健康度: {score}/100

## 调度统计
- 调度 Agent 次数: {agent_calls}
- 并行执行次数: {parallel_executions}
- 平均健康度提升: {avg_delta}/次

## 健康度明细
- 需求清晰度: {requirements}/20
- 代码完整度: {code}/25
- 测试覆盖度: {tests}/20
- 可运行性: {runnable}/20
- 代码质量: {quality}/15

## 完成的工作
{action_history}

## 启动方式
{startup_instructions}

## 后续建议
{recommendations}
```
