---
name: batch-dev-pipeline
description: "批量 Idea → 软件流水线。读取 N 个 idea 从 YAML 文件，为每个 idea 创建隔离项目目录，通过 adaptive-dev-engine 完成完整 SDLC（需求→架构→编码→测试→交付），监控所有项目的健康分数。"
license: MIT
compatibility: "Requires adaptive-dev-engine skill, Python 3.8+, PyYAML, claude CLI"
metadata:
  category: automation
  phase: orchestration
  version: "0.1.0"
  author: barry
allowed-tools: bash read_file write_file grep glob
---

# Batch Dev Pipeline

批量 Idea → 软件 流水线编排器。

## When to Use

**适用场景：**
- 有多个 idea 需要批量实现为可运行软件
- 需要每个 idea 独立走完完整 SDLC 流程
- 需要统一监控多个项目的开发进度

**不适用：**
- 单个项目开发（直接用 adaptive-dev-engine）
- 需要项目间共享状态的场景（PoC 不支持）

## Architecture

```
ideas.yaml → batch-orchestrator → workspace/<idea>/adaptive-dev → SDLC
```

- **外层**: batch-orchestrator.py 管理 idea 队列和项目隔离
- **内层**: adaptive-dev-engine 处理每个 idea 的完整 SDLC

## Workflow

### 1. Prepare ideas.yaml

```yaml
version: "1.0"
defaults:
  max_sessions: 50
ideas:
  - id: "my-app"
    name: "My App"
    requirement: |
      应用描述...
    priority: 1
```

### 2. Start batch pipeline

```bash
python3 batch-orchestrator.py start ideas.yaml --workspace ./workspace
```

### 3. Monitor progress

```bash
# 查看状态
python3 batch-orchestrator.py status --workspace ./workspace

# 或使用 shell 脚本
bash batch-status.sh ./workspace
```

### 4. Stop (if needed)

```bash
python3 batch-orchestrator.py stop --workspace ./workspace
```

## Dispatch Logic

1. 按 priority 升序排列 ideas
2. 逐个 dispatch（顺序执行）
3. 每个 idea: `adaptive-dev start "<requirement>"`
4. 轮询 state.json 直到 completed/failed
5. 记录结果，继续下一个

## Output

```
workspace/
├── batch-state.json          # 批量状态
├── batch-orchestrator.log    # 日志
├── <idea-1>/                 # 项目 1（完整代码 + 文档）
├── <idea-2>/                 # 项目 2
└── <idea-N>/                 # 项目 N
```

## References

| Document | Purpose |
|----------|---------|
| `references/batch-protocol.md` | 批量处理协议和状态机 |
| `references/project-isolation.md` | 项目隔离策略 |

## Related Skills

- `adaptive-dev-engine` - 单项目 SDLC 编排（内层引擎）
- `continuous-dev-loop` - 7x24 持续开发循环
- `orchestrator` - 通用编排调度器
