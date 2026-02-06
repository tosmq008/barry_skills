# Adaptive Dev Engine 使用手册

## 目录

1. [简介](#简介)
2. [安装配置](#安装配置)
3. [快速开始](#快速开始)
4. [命令详解](#命令详解)
5. [工作流程](#工作流程)
6. [健康度系统](#健康度系统)
7. [Agent 调度](#agent-调度)
8. [状态管理](#状态管理)
9. [故障排除](#故障排除)
10. [最佳实践](#最佳实践)

---

## 简介

Adaptive Dev Engine（自适应持续开发引擎）是一个智能化的 7×24 持续开发系统。它能够：

- **智能分析**：自动评估任何项目的健康状态
- **动态决策**：根据健康度智能选择下一步行动
- **多 Agent 并行**：调度多个专业 Agent 并行执行任务
- **自动恢复**：支持断点续传、限流保护、崩溃恢复

### 适用场景

| 场景 | 说明 |
|------|------|
| 新项目启动 | 从需求描述开始，自动完成 PRD → 设计 → 开发 → 测试 |
| 已有项目继续 | 分析现有代码，补充缺失部分 |
| Bug 修复 | 持续测试和修复直到通过 |
| 功能迭代 | 基于现有项目添加新功能 |

---

## 安装配置

### 系统要求

| 平台 | 要求 |
|------|------|
| macOS/Linux | Bash, Python 3, claude CLI |
| Windows | PowerShell 5.1+, Python 3, claude CLI |

### 安装步骤

#### macOS / Linux

```bash
# 方式1: 复制到 PATH
cp scripts/adaptive-dev ~/.local/bin/
chmod +x ~/.local/bin/adaptive-dev

# 方式2: 创建软链接
ln -s /path/to/adaptive-dev-engine/scripts/adaptive-dev ~/.local/bin/adaptive-dev

# 验证安装
adaptive-dev help
```

#### Windows (PowerShell)

```powershell
# 复制脚本
Copy-Item scripts\adaptive-dev.ps1 $env:USERPROFILE\.local\bin\

# 设置别名 (可选，添加到 $PROFILE)
Set-Alias adaptive-dev "$env:USERPROFILE\.local\bin\adaptive-dev.ps1"

# 验证安装
.\adaptive-dev.ps1 help
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | 使用的 Claude 模型 |
| `SKILL_DIR` | `~/.claude/skills/adaptive-dev-engine` | Skill 文件目录 |

```bash
# 示例：使用 Opus 模型
CLAUDE_MODEL=claude-opus-4-20250514 adaptive-dev start "我的项目"
```

---

## 快速开始

### 场景1：从零开始新项目

```bash
# 1. 创建项目目录
mkdir my-todo-app && cd my-todo-app

# 2. 启动持续开发（提供需求描述）
adaptive-dev start "一个待办事项App，支持创建、编辑、删除、标记完成任务，数据持久化到SQLite"

# 3. 查看进度
adaptive-dev status

# 4. 查看实时日志
adaptive-dev logs
```

### 场景2：继续已有项目

```bash
# 进入已有项目目录
cd existing-project

# 直接启动（无需提供需求，会自动分析）
adaptive-dev start

# 系统会自动：
# - 分析现有代码结构
# - 评估健康度
# - 决定下一步行动
```

### 场景3：暂停和恢复

```bash
# 暂停开发（当前会话完成后生效）
adaptive-dev pause

# 恢复开发
adaptive-dev start

# 完全停止
adaptive-dev stop
```

---

## 命令详解

### `start [需求描述]`

启动持续开发。

```bash
# 空项目 - 必须提供需求
adaptive-dev start "需求描述"

# 已有项目 - 可省略需求
adaptive-dev start
```

**自动判断逻辑：**
1. 已在运行 → 提示已运行
2. 有状态文件 → 从断点继续
3. 有项目文档/代码 → 基于现有内容继续
4. 空项目 → 需要提供需求描述

### `status`

查看当前状态。

```bash
adaptive-dev status
```

输出示例：
```
==========================================
📊 自适应持续开发状态
==========================================
守护进程: ✅ 运行中 (PID: 12345)

项目: my-todo-app
状态: running

健康度: 65/100 🔄 开发中
  需求: 18/20
  代码: 20/25
  测试: 12/20
  运行: 10/20
  质量: 5/15

会话: 5 次

心跳: 30s 前

最近日志:
[2024-01-31 10:30:00] 启动会话 #5 - 健康度: 65
```

### `logs`

实时查看日志。

```bash
adaptive-dev logs
# 按 Ctrl+C 退出
```

### `pause`

暂停开发（当前会话完成后生效）。

```bash
adaptive-dev pause
```

### `stop`

立即停止守护进程。

```bash
adaptive-dev stop
```

### `reset`

重置所有状态（删除 `.dev-state/` 目录）。

```bash
adaptive-dev reset
```

### `help`

显示帮助信息。

```bash
adaptive-dev help
```

---

## 工作流程

### 整体流程

```
┌─────────────────────────────────────────────────────────────┐
│                     Adaptive Dev Engine                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│   │  分析   │ →  │  评分   │ →  │  决策   │ →  │  执行   │  │
│   │ 项目状态 │    │ 健康度  │    │ 下一步  │    │ Agent   │  │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│        ↑                                            │        │
│        └────────────── 循环迭代 ←───────────────────┘        │
│                                                              │
│                    直到健康度 ≥ 80                           │
└─────────────────────────────────────────────────────────────┘
```

### 单次会话流程

1. **健康度分析** - 扫描项目结构、代码、测试、文档
2. **计算评分** - 5 个维度打分，总分 0-100
3. **智能决策** - 根据分数决定调度哪些 Agent
4. **执行任务** - 调度 Agent 执行具体工作
5. **更新状态** - 保存进度，准备下一轮

---

## 健康度系统

### 评分维度

| 维度 | 分值 | 评分标准 |
|------|------|----------|
| **需求清晰度** | 0-20 | 0:无需求 / 10:有描述 / 15:有PRD / 20:PRD完整 |
| **代码完整度** | 0-25 | 0:无代码 / 10:骨架 / 15:部分功能 / 20:基本完整 / 25:功能完整 |
| **测试覆盖度** | 0-20 | 0:无测试 / 5:少量 / 10:基础 / 15:较好 / 20:充分 |
| **可运行性** | 0-20 | 0:无法运行 / 10:部分可运行 / 15:基本可运行 / 20:完全可运行 |
| **代码质量** | 0-15 | 0:问题多 / 5:一般 / 10:较好 / 15:优秀 |

### 可用状态

**总分 ≥ 80 即为可用状态**，系统会自动停止并生成交付报告。

### 决策规则

```
健康度 < 20  → 调度 product-expert (需求分析)
健康度 20-40 → 调度 tech-manager (技术设计)
健康度 40-60 → 并行调度 python-expert + frontend-expert (开发)
健康度 60-75 → 调度 test-expert + 修复 (边测边修)
健康度 75-80 → 调度 test-report-followup (收尾优化)
健康度 ≥ 80  → 完成！生成交付报告
```

---

## Agent 调度

### 可用 Agent

| Agent | 职责 | 适用场景 |
|-------|------|----------|
| `product-expert` | 产品设计、PRD、UI原型 | 需求不清、产品设计 |
| `tech-manager` | 技术协调、前后端联调 | 全栈开发、接口对接 |
| `python-expert` | Python后端开发 | API、数据库、业务逻辑 |
| `frontend-expert` | 前端开发 | React/Vue、UI实现 |
| `test-expert` | 测试设计与执行 | 测试方案、用例、执行 |
| `test-report-followup` | Bug修复跟进 | 测试报告解析、修复验证 |

### 并行执行

系统会自动识别可并行的任务：

- 前端 + 后端开发可并行
- 测试 + 修复可并行
- 多个独立模块可并行

---

## 状态管理

### 状态目录结构

```
.dev-state/
├── state.json          # 主状态文件
├── requirement.txt     # 原始需求
├── daemon.pid          # 守护进程 PID
├── logs/               # 会话日志
│   ├── daemon.log      # 守护进程日志
│   └── session-*.log   # 各会话日志
├── checkpoints/        # 断点备份
└── locks/              # 文件锁
```

### 状态文件字段

```json
{
  "version": "1.0.0",
  "project": {
    "name": "项目名称",
    "path": "/absolute/path"
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
    "usable": false
  },
  "status": "running",
  "sessions": {
    "count": 5
  },
  "last_heartbeat": "2024-01-31T10:30:00Z"
}
```

### 状态值说明

| status | 说明 |
|--------|------|
| `ready` | 准备就绪，等待启动 |
| `running` | 正在执行 |
| `continue` | 等待下一轮 |
| `paused` | 用户暂停 |
| `completed` | 已完成（健康度 ≥ 80） |

---

## 故障排除

### 常见问题

#### 1. 启动失败：需要 python3

```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3
```

#### 2. 启动失败：需要 claude CLI

```bash
# 安装 claude CLI
npm install -g @anthropic-ai/claude-cli

# 或使用 pip
pip install claude-cli
```

#### 3. 守护进程无响应

```bash
# 检查状态
adaptive-dev status

# 查看日志
adaptive-dev logs

# 强制停止并重启
adaptive-dev stop
adaptive-dev start
```

#### 4. 限流问题

系统会自动处理限流：
- 首次限流等待 5 分钟
- 连续限流指数退避（最长 30 分钟）

#### 5. 心跳超时

如果会话卡住超过 30 分钟，守护进程会自动：
1. 终止当前会话
2. 保存断点
3. 启动新会话

### 日志位置

```bash
# 守护进程日志
cat .dev-state/logs/daemon.log

# 最新会话日志
ls -lt .dev-state/logs/session-*.log | head -1 | xargs cat
```

---

## 最佳实践

### 1. 需求描述要清晰

```bash
# ❌ 不好的需求
adaptive-dev start "做个网站"

# ✅ 好的需求
adaptive-dev start "一个博客系统，支持文章的增删改查、Markdown编辑、标签分类、用户评论，使用FastAPI后端和React前端"
```

### 2. 定期检查进度

```bash
# 查看状态
adaptive-dev status

# 实时日志
adaptive-dev logs
```

### 3. 合理使用暂停

```bash
# 需要人工介入时暂停
adaptive-dev pause

# 修改后继续
adaptive-dev start
```

### 4. 保持 SKILL 文件更新

确保 `SKILL_DIR` 指向最新的 skill 文件：

```bash
export SKILL_DIR="/path/to/adaptive-dev-engine"
```

### 5. 监控资源使用

长时间运行时注意：
- 磁盘空间（日志文件）
- API 配额（Claude API 调用）

---

## 附录

### A. 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MAX_TURNS` | 50 | 单次会话最大轮次 |
| `MIN_INTERVAL` | 60s | 会话间隔最小值 |
| `MAX_INTERVAL` | 120s | 会话间隔最大值 |
| `SESSION_TIMEOUT` | 1800s | 会话超时时间 |
| `HEARTBEAT_TIMEOUT` | 1800s | 心跳超时时间 |
| `MAX_ERRORS` | 5 | 最大连续错误数 |
| `RATE_LIMIT_WAIT` | 300s | 限流等待基础时间 |

### B. 相关文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 主 Skill 定义 |
| [README.md](README.md) | 项目概述 |
| [references/health-assessment.md](references/health-assessment.md) | 健康度评估详解 |
| [references/decision-engine.md](references/decision-engine.md) | 决策引擎详解 |
| [references/agent-orchestration.md](references/agent-orchestration.md) | Agent 编排详解 |
| [references/state-protocol.md](references/state-protocol.md) | 状态协议详解 |
| [references/recovery-scenarios.md](references/recovery-scenarios.md) | 恢复场景详解 |

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2024-01-31 | 初始版本 |

---

**Happy Coding!** 🚀
