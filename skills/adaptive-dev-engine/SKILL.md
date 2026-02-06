---
name: adaptive-dev-engine
description: "自适应持续开发引擎。智能分析任何项目状态，动态调度多 Agent 并行执行，持续迭代直到达到可用状态。支持新项目从零开始、已有项目继续开发、Bug修复、性能优化等任意场景。"
license: MIT
compatibility: "Works with external daemon script. Orchestrates product-expert, tech-manager, python-expert, frontend-expert, test-expert, test-report-followup."
metadata:
  category: automation
  phase: orchestration
  version: "1.0.0"
---

# Adaptive Dev Engine - 自适应持续开发引擎

你正在被外部守护进程循环调用，实现 7×24 持续开发。

## 核心理念

```
任何项目状态 → 健康度分析 → 智能决策 → 多Agent并行 → 达到可用状态
```

**可用状态定义：健康度 ≥ 80 分**

---

## 可调度的专业 Agent

| Agent | 职责 | 适用场景 | 调用方式 |
|-------|------|----------|----------|
| `product-expert` | 产品设计、PRD、UI原型 | 需求不清、产品设计 | Skill tool |
| `tech-manager` | 技术协调、前后端联调 | 全栈开发、接口对接 | Skill tool |
| `python-expert` | Python后端开发 | API、数据库、业务逻辑 | Skill tool |
| `frontend-expert` | 前端开发 | React/Vue、UI实现 | Skill tool |
| `test-expert` | 测试设计与执行 | 测试方案、用例、执行 | Skill tool |
| `test-report-followup` | Bug修复跟进 | 测试报告解析、修复验证 | Skill tool |

---

## 执行流程

### Step 1: 项目健康度分析（每次会话必须先执行）

```bash
echo "=========================================="
echo "项目健康度分析"
echo "=========================================="

# 1. 基础结构
echo "=== 1. 项目结构 ==="
ls -la 2>/dev/null | head -20
for dir in docs src client admin website app backend frontend; do
    [ -d "$dir" ] && echo "  ✓ $dir/"
done

# 2. 需求文档
echo ""
echo "=== 2. 需求文档 ==="
prd_count=$(ls docs/prd/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "  PRD文档数: $prd_count"
[ -f "PRD.md" ] && echo "  ✓ PRD.md"
[ -f "README.md" ] && echo "  ✓ README.md"
[ -f "requirements.md" ] && echo "  ✓ requirements.md"

# 3. 代码文件
echo ""
echo "=== 3. 代码状态 ==="
py_count=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" 2>/dev/null | wc -l | tr -d ' ')
ts_count=$(find . -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
js_count=$(find . -name "*.js" -o -name "*.jsx" -not -path "./node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
echo "  Python: $py_count 文件"
echo "  TypeScript: $ts_count 文件"
echo "  JavaScript: $js_count 文件"

# 4. 测试文件
echo ""
echo "=== 4. 测试状态 ==="
test_count=$(find . -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.spec.ts" 2>/dev/null | wc -l | tr -d ' ')
echo "  测试文件数: $test_count"

# 5. 依赖配置
echo ""
echo "=== 5. 项目配置 ==="
[ -f "pyproject.toml" ] && echo "  ✓ pyproject.toml (Python)"
[ -f "package.json" ] && echo "  ✓ package.json (Node)"
[ -f "requirements.txt" ] && echo "  ✓ requirements.txt"
[ -f "start.sh" ] && echo "  ✓ start.sh (启动脚本)"

# 6. 状态文件
echo ""
echo "=== 6. 开发状态 ==="
if [ -f ".dev-state/state.json" ]; then
    echo "  ✓ 有状态文件"
    cat .dev-state/state.json
else
    echo "  ✗ 无状态文件 (首次运行)"
fi

# 7. 实际运行检测
echo ""
echo "=== 7. 运行检测 ==="
if [ -f "start.sh" ]; then
    echo "  尝试启动项目..."
    timeout 15 ./start.sh &>/dev/null &
    START_PID=$!
    sleep 8

    # 检测后端
    if curl -s http://localhost:8000/health &>/dev/null || curl -s http://localhost:8000/ &>/dev/null; then
        echo "  ✓ 后端可运行 (port 8000)"
    elif curl -s http://localhost:3000/ &>/dev/null; then
        echo "  ✓ 前端可运行 (port 3000)"
    else
        echo "  ✗ 无法访问服务"
    fi

    # 清理
    kill $START_PID 2>/dev/null
    pkill -f "uvicorn|npm|node" 2>/dev/null
else
    # 尝试直接运行
    if [ -f "src/main.py" ]; then
        echo "  检测到 src/main.py，可尝试 uvicorn 启动"
    elif [ -f "app/main.py" ]; then
        echo "  检测到 app/main.py，可尝试 uvicorn 启动"
    elif [ -f "package.json" ]; then
        echo "  检测到 package.json，可尝试 npm 启动"
    else
        echo "  ✗ 无启动入口"
    fi
fi

echo ""
echo "=========================================="
```

### Step 2: 计算健康度评分

根据分析结果，计算 5 个维度的评分：

| 维度 | 分值 | 评分标准 |
|------|------|----------|
| **需求清晰度** | 0-20 | 0:无需求 / 10:有描述 / 15:有PRD / 20:PRD完整(≥4个) |
| **代码完整度** | 0-25 | 0:无代码 / 10:骨架 / 15:部分功能 / 20:基本完整 / 25:功能完整 |
| **测试覆盖度** | 0-20 | 0:无测试 / 5:少量 / 10:基础 / 15:较好 / 20:充分 |
| **可运行性** | 0-20 | 0:无法运行 / 10:部分可运行 / 15:基本可运行 / 20:完全可运行 |
| **代码质量** | 0-15 | 0:问题多 / 5:一般 / 10:较好 / 15:优秀 |

**评分后更新状态文件：**

```python
import json
from datetime import datetime

def update_health_score(breakdown):
    """更新健康度评分"""
    state_file = '.dev-state/state.json'

    with open(state_file, 'r') as f:
        state = json.load(f)

    total = sum(breakdown.values())
    state['health'] = {
        'score': total,
        'breakdown': breakdown,
        'usable': total >= 80,
        'assessed_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return total

# 示例
breakdown = {
    'requirements': 15,  # 有PRD文档
    'code': 20,          # 基本完整
    'tests': 10,         # 基础测试
    'runnable': 15,      # 基本可运行
    'quality': 10        # 较好
}
score = update_health_score(breakdown)
print(f"健康度: {score}/100, 可用: {score >= 80}")
```

### Step 3: 智能决策与 Agent 调度

根据健康度决定调度哪些 Agent：

```
┌─────────────────────────────────────────────────────────────────┐
│                        健康度决策树                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  健康度 < 20 (空项目/需求不清)                                   │
│  └─→ 调度: product-expert                                       │
│      └─→ 任务: 需求分析、PRD创建                                 │
│                                                                 │
│  健康度 20-40 (有需求/无代码)                                    │
│  └─→ 调度: tech-manager                                         │
│      └─→ 任务: 技术方案、架构设计、启动开发                       │
│                                                                 │
│  健康度 40-60 (有代码/功能不全)                                  │
│  └─→ 并行调度: python-expert + frontend-expert                  │
│      └─→ 任务: 前后端并行开发                                    │
│                                                                 │
│  健康度 60-75 (功能完整/测试不足)                                │
│  └─→ 调度: test-expert                                          │
│      └─→ 并行: python-expert/frontend-expert (边测边修)          │
│                                                                 │
│  健康度 75-80 (接近可用/有小问题)                                │
│  └─→ 调度: test-report-followup                                 │
│      └─→ 任务: 收尾优化、回归验证                                │
│                                                                 │
│  健康度 ≥ 80 (可用状态)                                         │
│  └─→ 完成！生成交付报告                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: 执行 Agent 调度

#### 单 Agent 调度（使用 Skill tool）

```
调度单个 Agent 时，使用 Skill tool:

示例: 调度 product-expert 进行需求分析
→ Skill(skill="product-expert", args="分析项目需求，创建完整的 PRD 文档")

示例: 调度 python-expert 实现后端
→ Skill(skill="python-expert", args="实现用户认证 API，包含登录、注册、token刷新")

示例: 调度 test-expert 执行测试
→ Skill(skill="test-expert", args="执行完整测试，生成测试报告")
```

#### 并行 Agent 调度（使用 Task tool）

**重要**: 要实现并行执行，必须在**单个消息**中发送多个 Task 调用。

```
并行调度前后端开发示例:

在一个消息中同时发送两个 Task 调用:

Task 1:
  - subagent_type: "general-purpose"
  - description: "python-expert 后端开发"
  - prompt: "使用 python-expert skill 实现后端 API..."
  - run_in_background: true

Task 2:
  - subagent_type: "general-purpose"
  - description: "frontend-expert 前端开发"
  - prompt: "使用 frontend-expert skill 实现前端页面..."
  - run_in_background: true

两个 Task 会并行执行，完成后会收到通知。
```

**并行调度的完整 prompt 模板:**

```python
# Task 1: 后端开发
backend_prompt = """
使用 python-expert skill 实现以下后端功能:

## 任务
{backend_tasks}

## 要求
1. 按照 API 规范实现
2. 包含基础测试
3. 完成后更新 .dev-state/state.json

## 状态更新
完成后执行:
```python
import json
with open('.dev-state/state.json', 'r') as f:
    state = json.load(f)
state['agent_coordination']['completed_agents'].append({
    'agent': 'python-expert',
    'task': 'backend_development',
    'status': 'completed'
})
with open('.dev-state/state.json', 'w') as f:
    json.dump(state, f, indent=2)
```
"""

# Task 2: 前端开发
frontend_prompt = """
使用 frontend-expert skill 实现以下前端功能:

## 任务
{frontend_tasks}

## API 接口
{api_spec}

## 要求
1. 按照 UI 设计稿实现
2. 对接后端 API
3. 完成后更新 .dev-state/state.json
"""
```

#### 等待并行 Agent 完成

```
并行 Agent 启动后，会收到类似通知:
"Agent xxx is working in the background. You will be notified when it completes."

可以:
1. 继续执行其他任务
2. 使用 Read tool 查看 output_file 检查进度
3. 等待完成通知后汇总结果
```

### Step 5: 汇总结果与状态更新

每个 Agent 完成后，汇总结果并重新评估健康度：

```python
def aggregate_results():
    """汇总 Agent 执行结果"""
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    completed = state.get('agent_coordination', {}).get('completed_agents', [])

    # 计算健康度提升
    health_delta = 0
    for agent in completed:
        if agent['status'] == 'completed':
            # 根据任务类型估算提升
            delta_map = {
                'prd_creation': 15,
                'backend_development': 10,
                'frontend_development': 10,
                'test_execution': 10,
                'bug_fix': 5
            }
            health_delta += delta_map.get(agent['task'], 5)

    # 更新健康度
    state['health']['score'] = min(100, state['health']['score'] + health_delta)
    state['health']['usable'] = state['health']['score'] >= 80

    # 清空已完成的 Agent
    state['agent_coordination']['completed_agents'] = []

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return state['health']['score']
```

### Step 6: 可用状态验证

当健康度 ≥ 80 时，执行最终验证：

```bash
#!/bin/bash
echo "=========================================="
echo "可用状态验证"
echo "=========================================="

PASS=0
FAIL=0

# 1. 可运行性检查
echo "1. 检查可运行性..."
if [ -f "start.sh" ]; then
    timeout 30 ./start.sh &
    PID=$!
    sleep 10

    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ 后端可运行"
        ((PASS++))
    else
        echo "   ❌ 后端无法启动"
        ((FAIL++))
    fi

    kill $PID 2>/dev/null
    pkill -f "uvicorn\|npm" 2>/dev/null
else
    echo "   ⚠️ 无启动脚本"
fi

# 2. 测试检查
echo "2. 检查测试..."
if command -v pytest &>/dev/null && [ -d "tests" ]; then
    if pytest --tb=no -q 2>/dev/null; then
        echo "   ✅ 测试通过"
        ((PASS++))
    else
        echo "   ❌ 测试失败"
        ((FAIL++))
    fi
else
    echo "   ⚠️ 无测试或 pytest"
fi

# 3. 代码质量
echo "3. 检查代码质量..."
if command -v ruff &>/dev/null; then
    if ruff check . --quiet 2>/dev/null; then
        echo "   ✅ 代码规范"
        ((PASS++))
    else
        echo "   ⚠️ 有代码问题"
    fi
fi

echo ""
echo "=========================================="
echo "验证结果: $PASS 通过, $FAIL 失败"
echo "=========================================="

if [ $FAIL -eq 0 ]; then
    echo "✅ 项目达到可用状态！"
    exit 0
else
    echo "⚠️ 项目需要继续优化"
    exit 1
fi
```

### Step 7: 生成交付报告

```python
def generate_delivery_report():
    """生成交付报告"""
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    report = f"""# 项目交付报告

## 基本信息
- 项目名称: {state['project']['name']}
- 完成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
- 总会话数: {state['sessions']['count']}
- 最终健康度: {state['health']['score']}/100

## 健康度明细
- 需求清晰度: {state['health']['breakdown']['requirements']}/20
- 代码完整度: {state['health']['breakdown']['code']}/25
- 测试覆盖度: {state['health']['breakdown']['tests']}/20
- 可运行性: {state['health']['breakdown']['runnable']}/20
- 代码质量: {state['health']['breakdown']['quality']}/15

## 调度统计
- Agent 调度次数: {len(state.get('action_history', []))}
- 并行执行次数: {sum(1 for a in state.get('action_history', []) if a.get('parallel'))}

## 完成的工作
"""
    for action in state.get('action_history', []):
        report += f"- [{action.get('completed_at', 'N/A')}] {action.get('type', 'unknown')}: {action.get('result', 'N/A')}\n"

    report += """
## 启动方式
```bash
./start.sh
```

## 后续建议
- 持续补充测试用例
- 完善错误处理
- 添加监控和日志
"""

    with open('docs/DELIVERY_REPORT.md', 'w') as f:
        f.write(report)

    return report
```

---

## 状态文件结构

```json
{
  "version": "1.0.0",
  "project": {
    "name": "项目名称",
    "path": "/absolute/path",
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
    "assessed_at": "2024-01-31T10:00:00Z"
  },
  "status": "running",
  "exit_reason": null,
  "current_action": {
    "type": "parallel_development",
    "agents": ["python-expert", "frontend-expert"],
    "started_at": "2024-01-31T10:30:00Z"
  },
  "agent_coordination": {
    "active_agents": [
      {"agent": "python-expert", "status": "running", "progress": "60%"},
      {"agent": "frontend-expert", "status": "running", "progress": "40%"}
    ],
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

---

## 轮次限制处理

接近限制时（约 40 轮），保存断点：

```python
def save_checkpoint_and_exit():
    """保存断点并退出"""
    with open('.dev-state/state.json', 'r') as f:
        state = json.load(f)

    state['status'] = 'continue'
    state['exit_reason'] = 'turns_limit'
    state['current_action']['checkpoint'] = {
        'step': '当前执行步骤',
        'progress': '进度百分比',
        'next_action': '下次继续的行动',
        'pending_agents': ['未完成的agent列表']
    }
    state['last_heartbeat'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    with open('.dev-state/state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
```

---

## 重要规则

1. **每次会话先分析健康度** - 不要盲目执行，先了解项目状态
2. **优先使用并行调度** - 前后端可并行，测试修复可并行
3. **健康度 ≥ 80 即可用** - 不要过度优化，达标即可
4. **遇到阻塞记录并跳过** - 不要卡死在单个问题上
5. **每完成一步更新状态** - 保证可恢复
6. **Sub Agent 完成后汇总** - 统一更新健康度
7. **合理假设并记录** - 遇到不确定时做出假设

---

## References

| 文档 | 用途 |
|------|------|
| `references/health-assessment.md` | 健康度评估详细指南 |
| `references/decision-engine.md` | 智能决策引擎 |
| `references/agent-orchestration.md` | 多Agent编排指南 |
| `references/state-protocol.md` | 状态协议详解 |
| `references/recovery-scenarios.md` | 中断恢复场景 |
