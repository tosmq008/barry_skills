---
name: continuous-dev-loop
description: "7x24 autonomous development with multi-skill orchestration, interruption recovery, and rate limiting protection."
license: MIT
compatibility: "Requires Claude Code CLI. Integrates with rapid-prototype-workflow, test-expert, test-report-followup skills."
metadata:
  category: automation
  phase: orchestration
  version: "2.0.0"
allowed-tools: bash read_file write_file
---

# Continuous Dev Loop Skill

实现 7×24 持续自动化开发，支持多 Skill 协调、中断恢复、限流保护。

## 核心特性

| 特性 | 说明 |
|------|------|
| 中断恢复 | 任何情况下中断都能从断点恢复 |
| 限流保护 | 会话间隔 60-120 秒，最多 3 个并行会话 |
| 多 Skill 协调 | 自动调用开发、测试、修复等 Skill |
| 状态持久化 | 所有状态写入文件，支持跨会话恢复 |

## 工作流阶段

| Phase | 名称 | Skill | 任务 |
|-------|------|-------|------|
| 1 | development | rapid-prototype-workflow | PRD、UI、代码 |
| 2 | testing | test-expert | 测试方案、执行、报告 |
| 3 | bugfix | test-report-followup | 解析报告、修复 |
| 4 | regression | test-expert | 回归验证 |

## 中断场景

| 场景 | 恢复策略 |
|------|----------|
| 轮次限制 | 立即重启继续 |
| 任务完成 | 启动下一任务 |
| 网络中断 | 等待恢复后重启 |
| API 限流 | 等待 5 分钟后重试 |
| 进程崩溃 | 从 checkpoint 恢复 |
| 任务阻塞 | 跳过并记录 |

## 快速开始

```bash
# 初始化
./scripts/init.sh "项目名称" "项目描述"

# 启动
./scripts/start.sh

# 状态
./scripts/status.sh

# 停止
./scripts/stop.sh
```

> 详细文档见 references/ 目录
