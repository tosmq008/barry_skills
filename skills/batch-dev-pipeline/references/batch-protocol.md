# Batch Processing Protocol

## Overview

批量处理协议定义了 batch-orchestrator 如何管理 N 个 idea 的生命周期。

## State Machines

### Batch Lifecycle

```
ready → running → completed
                → stopped    (用户手动停止)
                → failed     (所有 idea 失败)
```

| Status | Description |
|--------|-------------|
| `ready` | 已加载 ideas.yaml，等待启动 |
| `running` | 正在处理 idea 队列 |
| `completed` | 所有 idea 处理完毕（含失败的） |
| `stopped` | 用户手动停止 |

### Idea Lifecycle

```
pending → running → completed  (health ≥ 80)
                  → failed     (session 超限 / daemon 异常)
                  → skipped    (恢复时跳过已完成的)
```

| Status | Description |
|--------|-------------|
| `pending` | 等待调度 |
| `running` | adaptive-dev 正在执行 |
| `completed` | 健康分数达标 |
| `failed` | 超过 max_sessions 或 daemon 异常退出 |
| `skipped` | 恢复时跳过 |

## Dispatch Protocol

1. 按 `priority` 升序排列 ideas（小 = 高优先级）
2. 逐个 dispatch（PoC 为顺序执行，后续支持并行）
3. 每个 idea 调用 `adaptive-dev start "<requirement>"`
4. 轮询 `.dev-state/state.json` 直到终止条件

## Polling Protocol

- 间隔：30 秒
- 读取：`workspace/<idea.id>/.dev-state/state.json`
- 终止条件：
  - `status == "completed"` → idea 成功
  - `sessions.count >= max_sessions` → idea 失败（超限）
  - daemon PID 不存在且 status 非 running/continue → idea 失败

## Resume Protocol

重启 batch-orchestrator 时：

1. 读取 `batch-state.json`
2. 跳过 `status == "completed"` 的 idea
3. 对 `status == "running"` 的 idea：
   - 检查 adaptive-dev daemon 是否存活
   - 存活 → 继续轮询
   - 不存活 → 重新 dispatch
4. 对 `status == "pending"` 的 idea → 正常 dispatch

## Error Escalation

| 错误类型 | 处理 |
|---------|------|
| adaptive-dev start 失败 | 记录错误，标记 idea 为 failed，继续下一个 |
| idea 超过 max_sessions | 停止 adaptive-dev，标记 failed，继续下一个 |
| daemon 异常退出 | 标记 failed，继续下一个 |
| batch-orchestrator 被 SIGTERM | 停止当前 adaptive-dev，保存状态，退出 |

## State File: batch-state.json

位置：`workspace/batch-state.json`

```json
{
  "version": "0.1.0",
  "status": "running",
  "ideas_file": "/abs/path/ideas.yaml",
  "workspace": "/abs/path/workspace",
  "total_ideas": 3,
  "completed_ideas": 1,
  "failed_ideas": 0,
  "current_idea_id": "calculator-api",
  "progress": { ... },
  "started_at": "ISO8601",
  "last_updated": "ISO8601",
  "daemon_pid": 12345
}
```
