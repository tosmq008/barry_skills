# Adaptive Dev Engine

自适应持续开发引擎 - 智能分析任何项目状态，动态调度多 Agent 并行执行，持续迭代直到达到可用状态。

## 核心特性

- **双引擎架构**: 支持独立的 `CLI 守护进程模式`，或者与环境集成的 `IDE 原生模式`。
- **健康度评分系统**: 0-100 分量化项目状态，≥80 分即可用
- **智能决策引擎**: 根据健康度和问题类型动态决定下一步行动
- **多 Agent 调度或角色扮演**: 在 CLI 模式下作为上游控制器调度子进程；在 IDE 模式下直接读取各专家规则自我迭代。
- **无间断自动循环**: 支持在 IDE 对话框内进行 `YOLO / Autoloop` 的零打扰闭环。
- **自动断点恢复**: 支持轮次限制、进程崩溃、限流等场景的自动恢复

## 可调度的角色 (专家体系)

| Agent 角色 | 职责 |
|-------|------|
| `product-expert` | 产品设计、PRD、UI原型 |
| `tech-manager` | 技术协调、系统架构联调 |
| `python-expert` | Python/后端底层架构开发 |
| `frontend-expert` | 前端组件、UI实现开发 |
| `test-expert` | 编写/执行 E2E、集成、单元覆盖率 |
| `test-report-followup` | Bug修复跟进、收尾质量提升 |

## 快速开始

### 【模式 A】IDE 原生无间断模式 (推荐用于现代大模型工作台)

1. 在 IDE 的对话框中，输入以下 Slash Command：
   `/adaptive-dev`
2. AI 会自动进入**死循环状态**（不会每一小步都来麻烦你，会自动分析健康度 -> `执行方案` -> `分析最新健康度` -> `执行下一项`... ）。
3. 任何时刻如果你觉得 AI 做得差不多了，系统强制其输出最新状态，你可以直接回复“继续” 或重新跑 `/adaptive-dev` 衔接。

**防撞车警告**:
使用 IDE 原生触发开发前，如果你的项目根目录有 CLI 生成的 `.dev-state/daemon.pid`，说明外置 Bash 脚本还在跑。请务必先停止它（保证不会多机同时写同一个 json）。

---

### 【模式 B】旧版 CLI 守护进程模式

适用于非大模型 IDE 环境。它由一个死循环守护 Bash 处理上下文切分并交还给 Claude CLI。

**macOS / Linux**
```bash
cp scripts/adaptive-dev ~/.local/bin/
chmod +x ~/.local/bin/adaptive-dev

adaptive-dev start "一个待办事项App，支持增删改查"
adaptive-dev logs
adaptive-dev stop
```

**Windows (PowerShell)**
```powershell
Copy-Item scripts\adaptive-dev.ps1 $env:USERPROFILE\.local\bin\
.\adaptive-dev.ps1 start "一个待办事项App，支持增删改查"
```

## 健康度与决策流程

```
健康度评估表：
0-20  (PRD完整性)
0-25  (功能实现程度)
0-20  (可运行性/部署情况) 
0-20  (测试用例覆盖比率)
0-15  (代码质量及Lint警告)
```

**可用状态: 总分 ≥ 80**

```
自适应流向：
极弱 requirements   → product-expert 
较弱 code           → tech-manager 或 python-expert + frontend-expert 
弱 runnable         → 修复启动框架 
低 tests 取值       → test-expert 
极差 quality        → linter 自动修改 
```

## 目录结构

```
adaptive-dev-engine/
├── SKILL.md                      # 主 Skill 调度与多代理定义
├── README.md                     # 本文件
├── scripts/
│   ├── adaptive-dev              # 守护进程脚本 (Bash - CLI Mode)
│   ├── adaptive-dev.ps1          # 守护进程脚本 (PowerShell - CLI Mode)
│   ├── health-check.py           # 独立的评分算法 (共用)
│   └── init-state.py             # IDE Mode 无容错初始化状态脚本
└── references/
    ├── decision-engine.md        # 智能决策引擎
    ├── state-protocol.md         # 状态协议详解
    └── ...                       # 其他参考规则
```

## 与其他 Skill 的关系

本 Skill 作为最高编排层，会在运行时自动引用子专家 Skill 的指令执行实际操作。这种模块化解耦可以在不修改核心循环的情况下单独升级某个专家引擎的能力。

## License

MIT
