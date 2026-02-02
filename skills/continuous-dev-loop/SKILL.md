---
name: continuous-dev-loop
description: "Instructions for Claude to work in continuous 7x24 development mode. Prioritizes reading existing project documents and continuing from checkpoint. Falls back to requirement description only when project is empty."
license: MIT
compatibility: "Works with external daemon script. Integrates with rapid-prototype-workflow, test-expert, test-report-followup skills."
metadata:
  category: automation
  phase: orchestration
  version: "3.3.0"
allowed-tools: bash read_file write_file
---

# Continuous Dev Loop

你正在被外部守护进程循环调用，实现 7×24 持续开发。

## 第一步：检查项目现有文档（必须先执行）

```bash
# 1. 检查 PRD 文档
ls docs/prd/*.md 2>/dev/null && echo "=== 有PRD文档 ===" || echo "=== 无PRD文档 ==="

# 2. 检查其他需求文档
ls -la PRD.md README.md requirements.md 需求.md 2>/dev/null

# 3. 检查代码目录
ls -la client/ admin/ website/ src/ 2>/dev/null

# 4. 读取状态文件
cat .dev-state/state.json
```

## 第二步：根据检查结果决定行动

### 情况 A：有 docs/prd/ 目录且有文档
**从断点继续，不要重新创建 PRD**

1. 读取 state.json 的 checkpoint
2. 确定当前阶段和进度
3. 继续执行下一步

### 情况 B：有 PRD.md / README.md / 需求文档
**基于现有文档继续，不要重新创建**

1. 读取现有文档了解项目需求
2. 检查已完成的工作
3. 从当前进度继续

### 情况 C：项目为空，只有 .dev-state/requirement.txt
**从需求描述开始，创建 PRD**

1. 读取 .dev-state/requirement.txt
2. 使用 rapid-prototype-workflow 从 Phase 1 开始
3. 创建 8 个 PRD 文档

## 状态更新规则

每完成一步，**立即更新** state.json：

```python
import json
from datetime import datetime, timezone

with open('.dev-state/state.json', 'r') as f:
    state = json.load(f)

state['last_heartbeat'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
state['current_task']['checkpoint'] = {
    'phase': '当前阶段',
    'step': '已完成步骤',
    'next': '下一步骤'
}

with open('.dev-state/state.json', 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
```

## 轮次限制处理

接近限制时（约 40 轮），保存断点退出：

```python
state['status'] = 'continue'
state['exit_reason'] = 'turns_limit'
```

## 阶段流转

| 阶段 | Skill | 完成条件 |
|------|-------|----------|
| development | rapid-prototype-workflow | 代码实现完成 |
| testing | test-expert | 测试通过 |
| bugfix | test-report-followup | Bug 修复完成 |
| regression | test-expert | 回归通过 |

## 重要规则

1. **优先读取现有文档**，不要盲目重新创建
2. **从断点继续**，不要重复已完成的工作
3. **使用绝对路径**
4. **每完成一步更新 checkpoint**
5. **遇到不确定的地方，做出合理假设并记录**
