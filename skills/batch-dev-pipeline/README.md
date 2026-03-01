# Batch Dev Pipeline

批量 Idea → 软件流水线。将多个 idea 自动化为可运行的软件项目。

## Quick Start

```bash
# 1. 准备 ideas 文件（参考 templates/ideas-example.yaml）
cp templates/ideas-example.yaml my-ideas.yaml
# 编辑 my-ideas.yaml，填入你的 idea

# 2. 启动批量流水线
python3 scripts/batch-orchestrator.py start my-ideas.yaml \
    --workspace ./workspace \
    --adaptive-dev ~/.local/bin/adaptive-dev

# 3. 查看进度
python3 scripts/batch-orchestrator.py status --workspace ./workspace

# 4. 停止（如需要）
python3 scripts/batch-orchestrator.py stop --workspace ./workspace
```

## Prerequisites

- Python 3.8+
- PyYAML: `pip install pyyaml`
- Claude CLI (`claude` command available)
- adaptive-dev-engine skill installed (`~/.local/bin/adaptive-dev`)

## Ideas YAML Format

```yaml
version: "1.0"
defaults:
  max_sessions: 50        # 每个项目最大 session 数
  target_health: 80       # 健康分数目标

ideas:
  - id: "my-app"          # 唯一 ID（用作目录名）
    name: "My App"        # 显示名称
    requirement: |        # 需求描述（传给 adaptive-dev）
      详细的应用需求描述...
    priority: 1           # 优先级（小 = 高）
    tags: ["fullstack"]   # 标签（可选）
    max_sessions: 30      # 覆盖默认值（可选）
```

## Commands

| Command | Description |
|---------|-------------|
| `start <ideas.yaml>` | 启动批量流水线 |
| `status` | 查看所有项目状态 |
| `stop` | 停止流水线 |

## Status Output

```
============================================================
Batch Pipeline Status: RUNNING
Ideas: 1/3 completed, 0 failed
Current: calculator-api
============================================================
  [x] todo-app:       health=82/100  sessions=12  status=completed
  [>] calculator-api:  health=45/100  sessions=5   status=running
        breakdown: req=18 code=12 test=5 run=5 qual=5
  [ ] weather-app:     health=0/100   sessions=0   status=pending
============================================================
```

## How It Works

1. **Load**: 解析 ideas.yaml，按优先级排序
2. **Isolate**: 为每个 idea 创建独立项目目录
3. **Dispatch**: 调用 `adaptive-dev start` 启动 SDLC
4. **Poll**: 每 30 秒检查 state.json 健康分数
5. **Complete**: health ≥ 80 → 成功，超过 max_sessions → 失败
6. **Next**: 继续下一个 idea

## Resume

如果 batch-orchestrator 被中断，重新运行 `start` 命令会：
- 跳过已完成的 idea
- 恢复当前正在执行的 idea
- 继续处理剩余 idea

## File Structure

```
skills/batch-dev-pipeline/
├── SKILL.md                    # Skill 定义
├── README.md                   # 本文件
├── scripts/
│   ├── batch-orchestrator.py   # 批量调度守护进程
│   └── batch-status.sh         # 状态查看脚本
├── templates/
│   └── ideas-example.yaml      # 示例 ideas 文件
└── references/
    ├── batch-protocol.md       # 批量处理协议
    └── project-isolation.md    # 项目隔离策略
```
