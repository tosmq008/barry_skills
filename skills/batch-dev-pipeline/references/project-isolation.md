# Project Isolation Strategy

## Overview

每个 idea 在独立的项目目录中执行，确保零共享状态。

## Directory Structure

```
workspace/
├── batch-state.json              # 批量状态（orchestrator 管理）
├── batch-orchestrator.log        # orchestrator 日志
├── todo-app/                     # idea-1 独立项目
│   ├── .dev-state/
│   │   ├── state.json            # adaptive-dev 状态
│   │   ├── config.env            # 项目级配置覆盖
│   │   ├── daemon.pid
│   │   ├── logs/
│   │   ├── checkpoints/
│   │   └── agents/
│   ├── docs/prd/                 # 生成的 PRD 文档
│   ├── src/                      # 生成的代码
│   └── ...
├── calculator-api/               # idea-2 独立项目
│   ├── .dev-state/
│   └── ...
└── weather-dashboard/            # idea-3 独立项目
    ├── .dev-state/
    └── ...
```

## Isolation Guarantees

| 维度 | 隔离方式 |
|------|---------|
| 文件系统 | 每个 idea 独立目录 `workspace/<idea.id>/` |
| 状态 | 独立 `.dev-state/state.json` |
| 进程 | 独立 adaptive-dev daemon（独立 PID） |
| 配置 | 独立 `config.env` 覆盖 |
| 日志 | 独立 `.dev-state/logs/` |
| Git | PoC 不初始化 Git（后续可加） |

## Config Override

每个项目的 `.dev-state/config.env` 可覆盖 adaptive-dev 默认配置：

```bash
MAX_TURNS=40                    # 每个 session 最大轮次
MAX_TOTAL_SESSIONS=30           # 该项目最大 session 数
GIT_AUTO_COMMIT=false           # PoC 关闭 Git 自动提交
```

## Project Creation Flow

```python
def create_project(idea):
    1. mkdir workspace/<idea.id>/
    2. mkdir workspace/<idea.id>/.dev-state/
    3. write workspace/<idea.id>/.dev-state/config.env
    4. return project_dir
```

## Cross-Project Communication

**PoC 阶段：无跨项目通信。**

后续可扩展：
- 共享模块库 `workspace/_shared/`
- 跨项目依赖声明
- 公共组件复用
