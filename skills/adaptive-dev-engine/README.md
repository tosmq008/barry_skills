# Adaptive Dev Engine

自适应持续开发引擎 - 智能分析任何项目状态，动态调度多 Agent 并行执行，持续迭代直到达到可用状态。

## 核心特性

- **健康度评分系统**: 0-100 分量化项目状态，≥80 分即可用
- **智能决策引擎**: 根据健康度和问题类型动态决定下一步行动
- **多 Agent 并行调度**: 前后端并行开发，测试修复并行执行
- **自动断点恢复**: 支持轮次限制、进程崩溃、限流等场景的自动恢复
- **7×24 持续运行**: 守护进程自动管理会话生命周期

## 可调度的 Agent

| Agent | 职责 |
|-------|------|
| `product-expert` | 产品设计、PRD、UI原型 |
| `tech-manager` | 技术协调、前后端联调 |
| `python-expert` | Python后端开发 |
| `frontend-expert` | 前端开发 |
| `test-expert` | 测试设计与执行 |
| `test-report-followup` | Bug修复跟进 |

## 快速开始

### macOS / Linux

```bash
# 复制脚本到 PATH
cp scripts/adaptive-dev ~/.local/bin/
chmod +x ~/.local/bin/adaptive-dev

# 或创建软链接
ln -s $(pwd)/scripts/adaptive-dev ~/.local/bin/adaptive-dev

# 使用
adaptive-dev start "一个待办事项App，支持增删改查"
adaptive-dev status
adaptive-dev stop
```

### Windows (PowerShell)

```powershell
# 复制脚本到项目目录或 PATH
Copy-Item scripts\adaptive-dev.ps1 $env:USERPROFILE\.local\bin\

# 使用 (在项目目录下运行)
.\adaptive-dev.ps1 start "一个待办事项App，支持增删改查"
.\adaptive-dev.ps1 status
.\adaptive-dev.ps1 stop

# 或者设置别名
Set-Alias adaptive-dev "$env:USERPROFILE\.local\bin\adaptive-dev.ps1"
```

### 命令说明

| 命令 | 说明 |
|------|------|
| `start [需求]` | 启动持续开发 |
| `status` | 查看状态 |
| `logs` | 实时日志 |
| `pause` | 暂停 |
| `stop` | 停止 |
| `reset` | 重置 |

## 健康度评分

| 维度 | 分值 | 说明 |
|------|------|------|
| 需求清晰度 | 0-20 | PRD完整性 |
| 代码完整度 | 0-25 | 功能实现程度 |
| 测试覆盖度 | 0-20 | 测试用例覆盖 |
| 可运行性 | 0-20 | 能否正常启动 |
| 代码质量 | 0-15 | 代码规范程度 |

**可用状态: 总分 ≥ 80**

## 决策流程

```
健康度 < 20  → product-expert (需求分析)
健康度 20-40 → tech-manager (技术设计)
健康度 40-60 → python-expert + frontend-expert (并行开发)
健康度 60-75 → test-expert + 修复 (边测边修)
健康度 75-80 → test-report-followup (收尾优化)
健康度 ≥ 80  → 完成！
```

## 目录结构

```
adaptive-dev-engine/
├── SKILL.md                      # 主 Skill 文件
├── README.md                     # 本文件
├── scripts/
│   ├── adaptive-dev              # 守护进程脚本 (Bash - macOS/Linux)
│   └── adaptive-dev.ps1          # 守护进程脚本 (PowerShell - Windows)
└── references/
    ├── health-assessment.md      # 健康度评估指南
    ├── decision-engine.md        # 智能决策引擎
    ├── agent-orchestration.md    # 多Agent编排指南
    ├── state-protocol.md         # 状态协议详解
    └── recovery-scenarios.md     # 中断恢复场景
```

## 状态文件

运行时会在项目目录创建 `.dev-state/` 目录：

```
.dev-state/
├── state.json          # 主状态文件
├── requirement.txt     # 原始需求
├── logs/               # 会话日志
├── checkpoints/        # 断点备份
└── locks/              # 文件锁
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CLAUDE_MODEL` | claude-sonnet-4-20250514 | 使用的模型 |
| `SKILL_DIR` | `~/.claude/skills/adaptive-dev-engine` | Skill 目录路径 |

## 系统要求

| 平台 | 要求 |
|------|------|
| macOS/Linux | Bash, Python 3, claude CLI |
| Windows | PowerShell 5.1+, Python 3, claude CLI |

## 与其他 Skill 的关系

本 Skill 作为编排层，动态调度以下 Skill：

- `product-expert` - 产品设计
- `tech-manager` - 技术协调
- `python-expert` - 后端开发
- `frontend-expert` - 前端开发
- `test-expert` - 测试执行
- `test-report-followup` - Bug修复

## License

MIT
