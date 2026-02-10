---
name: adaptive-dev-engine
description: "自适应持续开发引擎。读取 health-check.py 产出的健康度评分，按最弱维度优先策略调度 Agent，持续迭代直到健康度 >= 80。"
license: MIT
compatibility: "Requires health-check.py daemon. Orchestrates product-expert, tech-manager, python-expert, frontend-expert, test-expert, test-report-followup."
metadata:
  category: automation
  phase: orchestration
  version: "2.0.0"
---

# Adaptive Dev Engine

你正在被外部守护进程循环调用，实现持续开发。健康度评分由独立脚本 `health-check.py` 计算并写入 `state.json`，**AI 不重新评估健康度**。

## Agent 一览

| Agent | 职责 | 调用方式 |
|-------|------|----------|
| `product-expert` | 需求分析、PRD 创建 | Skill tool |
| `tech-manager` | 技术方案、架构、前后端联调 | Skill tool |
| `python-expert` | Python 后端开发 | Skill tool |
| `frontend-expert` | 前端开发 | Skill tool |
| `test-expert` | 测试设计与执行 | Skill tool |
| `test-report-followup` | Bug 修复跟进、收尾优化 | Skill tool |

---

## 执行流程

### Step 1: 读取健康度

从 `.dev-state/state.json` 读取 `health.score` 和 `health.breakdown`。该评分由 `health-check.py` 守护进程独立计算，AI 直接使用，不做二次评估。

### Step 2: 识别最弱维度

从 `health.breakdown` 中找出得分最低的维度，作为本轮优先改进目标。

维度列表：`requirements`、`code`、`runnable`、`tests`、`quality`

### Step 3: 决策调度

找到比率最低的维度（score / max_score），按 70% 达标线决定调度：

| 最弱维度 | 调度 Agent |
|----------|-----------|
| `requirements`（比率 < 70%） | `product-expert` |
| `code`（比率 < 70%，score < 10） | `tech-manager`（架构设计） |
| `code`（比率 < 70%，score >= 10） | `python-expert` + `frontend-expert`（并行开发） |
| `runnable`（比率 < 70%） | `tech-manager`（启动/部署问题） |
| `tests`（比率 < 70%） | `test-expert` |
| `quality`（比率 < 70%） | `python-expert` + `frontend-expert`（并行改善） |
| 所有维度 >= 70% | `test-report-followup`（收尾打磨） |
| `score >= 80` | **完成** — 生成交付报告 |

### Step 4: 执行调度

- **单 Agent**: 使用 Skill tool 直接调度。
- **并行 Agent**: 在单条消息中发送多个 Task tool 调用，设置 `run_in_background: true`。

### Step 5: 更新状态

Agent 完成后更新 `.dev-state/state.json`：
- 将完成的 Agent 追加到 `action_history`
- 设置 `status` 为 `running` / `continue` / `completed`
- 更新 `last_heartbeat`

详细字段规范见 `references/state-protocol.md`。

---

## 状态更新规则

- Agent 完成 → 追加 `action_history` 条目（type、agents、health_delta、result、completed_at）
- 健康度达标 → `status: "completed"`，`exit_reason: "usable_reached"`
- 轮次耗尽 → `status: "continue"`，`exit_reason: "turns_limit"`
- 遇到阻塞 → 记录到顶层 `blockers` 数组，跳过继续

完整协议见 `references/state-protocol.md`。

---

## 轮次限制

在 `MAX_TURNS - 5` 时保存断点：
- 将当前进度写入 `current_action.checkpoint`（step、progress、next_action、pending_agents）
- 设置 `status: "continue"`，`exit_reason: "turns_limit"`
- 守护进程会启动新会话继续执行

---

## 重要规则

1. **不重新评估健康度** — 直接使用 `state.json` 中的评分，由 `health-check.py` 负责计算
2. **最弱维度优先** — 每轮只聚焦得分最低的维度，不要分散精力
3. **优先并行调度** — 前后端可并行，测试与修复可并行
4. **健康度 >= 80 即完成** — 不过度优化，达标即交付
5. **遇到阻塞记录并跳过** — 不卡死在单个问题上，记录后继续
6. **每步更新状态** — 保证中断后可恢复
7. **合理假设并记录** — 遇到不确定时做出假设，写入状态文件
8. **主动管理上下文** — 工具调用多时执行 `/compact`，避免上下文耗尽
9. **失败快速跳过** — 同一操作失败 3 次，记录 blocker 并转向下一任务

---

## 异常恢复策略

守护进程会自动分类 Agent 退出原因并采取对应恢复措施：

| 退出类型 | 检测方式 | 恢复策略 |
|----------|----------|----------|
| `context_exhausted` | 日志含 context/token limit | 自动重启新会话（新上下文） |
| `rate_limit` | 日志含 429/rate limit | 指数退避等待后重试 |
| `network_error` | 日志含 ECONNREFUSED/timeout | 等待 30s 后重试，不计入错误 |
| `tool_error` | 日志含 tool execution failed | 计入错误，重试（prompt 含错误上下文） |
| `permission_error` | 日志含 permission denied/401 | 告警，计入错误，可能需人工介入 |
| `session_timeout` | 会话超时 | 自动重启（不计入错误） |
| `unknown_crash` | 无法识别 | 计入错误，标准重试（启用 GIT_ROLLBACK 时回滚） |

**AI 侧主动防御：**
- 上下文过长时主动执行 `/compact` 释放空间
- 工具/命令连续失败 3 次以上，记录为 blocker 并跳过
- 每次退出前确保 checkpoint 已保存

---

## References

| 文档 | 用途 |
|------|------|
| `references/health-assessment.md` | 健康度评估详细指南 |
| `references/decision-engine.md` | 决策引擎规则 |
| `references/agent-orchestration.md` | 多 Agent 编排指南 |
| `references/state-protocol.md` | 状态协议详解 |
| `references/recovery-scenarios.md` | 中断恢复场景 |
