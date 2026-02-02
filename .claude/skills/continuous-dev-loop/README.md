# Continuous Dev Loop - 7×24 持续自动化开发

通过外部守护脚本 + Claude Code CLI 实现近乎无人值守的持续开发，自动协调开发、测试、修复、回归等多个阶段。

## 特性

- ✅ **7×24 持续运行** - 守护进程自动重启会话
- ✅ **中断恢复** - 任何情况下都能从断点继续
- ✅ **限流保护** - 随机间隔 + 指数退避，防止 API 限流
- ✅ **多 Skill 协调** - 自动调用开发、测试、修复等 Skill
- ✅ **状态持久化** - 所有进度保存到文件

---

## 快速开始

### 前置条件

- Claude Code CLI 已安装并登录 (`claude --version`)
- Python 3.x
- Bash/Zsh

### 1. 复制脚本到项目

```bash
# 方式1: 复制整个 scripts 目录
cp -r /path/to/skills/continuous-dev-loop/scripts /your/project/

# 方式2: 如果在同一仓库
ln -s ../skills/continuous-dev-loop/scripts ./scripts
```

### 2. 初始化项目

```bash
cd /your/project
./scripts/init.sh "项目名称" "项目描述"
```

初始化后会创建:
```
.dev-state/
├── state.json        # 主状态文件
├── sessions/         # 会话状态
├── checkpoints/      # 断点快照
└── logs/             # 运行日志
```

### 3. 启动持续开发

```bash
./scripts/start.sh
```

### 4. 监控运行状态

```bash
# 查看状态摘要
./scripts/status.sh

# 实时查看日志
tail -f .dev-state/logs/daemon.log

# 持续监控
watch -n 10 ./scripts/status.sh
```

### 5. 控制命令

```bash
# 暂停 (完成当前会话后暂停)
./scripts/pause.sh

# 恢复
./scripts/resume.sh

# 停止
./scripts/stop.sh
```

---

## 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         完整工作流                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Phase 1              Phase 2              Phase 3             │
│   开发阶段      ───▶   测试阶段      ───▶   修复阶段            │
│                                                                 │
│   rapid-prototype      test-expert          test-report         │
│   -workflow                                 -followup           │
│                                                                 │
│   • PRD 文档           • 测试方案           • 解析报告          │
│   • UI 设计            • 测试用例           • 分派任务          │
│   • 代码实现           • 测试执行           • 执行修复          │
│                        • 测试报告                               │
│                              │                    │             │
│                              ▼                    ▼             │
│                         有 Bug?            Phase 4              │
│                              │             回归测试             │
│                             Yes                                 │
│                              │             test-expert          │
│                              └──────────▶                       │
│                                            • 验证修复           │
│                                            • 回归用例           │
│                                                  │              │
│                                                  ▼              │
│                                            全部通过?            │
│                                             │      │            │
│                                            Yes    No            │
│                                             │      │            │
│                                             ▼      └──▶ bugfix  │
│                                          ✅ 完成                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 配置说明

编辑 `scripts/config.env`:

```bash
# 会话控制
MAX_TURNS=50                    # 单次会话最大轮次

# 限流保护 (重要!)
MIN_SESSION_INTERVAL=60         # 最小会话间隔 (秒)
MAX_SESSION_INTERVAL=120        # 最大会话间隔 (秒)
RATE_LIMIT_WAIT=300             # 限流后等待时间 (秒)

# 错误处理
MAX_RETRIES=3                   # 单任务最大重试
MAX_CONSECUTIVE_ERRORS=5        # 连续错误上限

# 心跳超时
HEARTBEAT_TIMEOUT=600           # 心跳超时判定 (秒)

# 告警 (可选)
ALERT_WEBHOOK=""                # Slack/钉钉 webhook
```

---

## 状态说明

### 运行状态 (status)

| 状态 | 说明 | 守护进程动作 |
|------|------|--------------|
| `ready` | 准备开始 | 启动会话 |
| `running` | 正在执行 | 监控心跳 |
| `continue` | 需要继续 | 启动新会话 |
| `paused` | 已暂停 | 等待恢复 |
| `completed` | 全部完成 | 退出 |
| `error` | 发生错误 | 尝试恢复 |

### 退出原因 (exit_reason)

| 原因 | 说明 |
|------|------|
| `turns_limit` | 达到轮次限制，正常退出 |
| `task_done` | 当前任务完成 |
| `all_done` | 所有任务完成 |
| `rate_limit` | 触发 API 限流 |
| `heartbeat_timeout` | 心跳超时 |
| `user_pause` | 用户暂停 |

---

## 中断恢复

系统支持从以下场景恢复:

| 场景 | 自动恢复 |
|------|----------|
| 达到轮次限制 | ✅ 自动继续 |
| 网络中断 | ✅ 心跳超时后恢复 |
| API 限流 | ✅ 等待后重试 |
| 进程崩溃 | ✅ 从 checkpoint 恢复 |
| 系统重启 | ✅ 重新启动后继续 |
| 任务阻塞 | ✅ 跳过并继续 |

---

## 日志文件

```
.dev-state/logs/
├── daemon.log              # 守护进程日志
├── session-20240131_100000.log  # 会话日志
├── session-20240131_103000.log
└── ...
```

查看日志:
```bash
# 守护进程日志
tail -f .dev-state/logs/daemon.log

# 最新会话日志
ls -t .dev-state/logs/session-*.log | head -1 | xargs tail -f
```

---

## 常见问题

### Q: 如何查看当前进度?

```bash
./scripts/status.sh
```

### Q: 如何跳过当前任务?

```bash
# 编辑状态文件，增加 retry_count 到 3 以上
python3 -c "
import json
with open('.dev-state/state.json', 'r') as f:
    d = json.load(f)
d['current_task']['retry_count'] = 99
d['status'] = 'continue'
with open('.dev-state/state.json', 'w') as f:
    json.dump(d, f, indent=2)
"
```

### Q: 如何从特定阶段开始?

```bash
# 修改当前阶段
python3 -c "
import json
with open('.dev-state/state.json', 'r') as f:
    d = json.load(f)
d['workflow']['current_phase'] = 'testing'  # 或 bugfix, regression
d['status'] = 'continue'
with open('.dev-state/state.json', 'w') as f:
    json.dump(d, f, indent=2)
"
```

### Q: 遇到限流怎么办?

系统会自动处理，等待时间会指数增长。如果频繁限流，可以增加配置:

```bash
# config.env
MIN_SESSION_INTERVAL=120
MAX_SESSION_INTERVAL=180
RATE_LIMIT_WAIT=600
```

### Q: 如何完全重置?

```bash
./scripts/stop.sh
rm -rf .dev-state
./scripts/init.sh "项目名称" "项目描述"
./scripts/start.sh
```

---

## 目录结构

```
skills/continuous-dev-loop/
├── SKILL.md                    # Skill 定义
├── README.md                   # 使用说明 (本文件)
├── scripts/
│   ├── config.env              # 配置文件
│   ├── daemon.sh               # 守护进程 (核心)
│   ├── init.sh                 # 初始化
│   ├── start.sh                # 启动
│   ├── stop.sh                 # 停止
│   ├── pause.sh                # 暂停
│   ├── resume.sh               # 恢复
│   └── status.sh               # 状态查询
└── references/
    ├── state-protocol.md       # 状态文件协议
    ├── skill-integration.md    # Skill 集成指南
    ├── recovery-scenarios.md   # 恢复场景详解
    └── troubleshooting.md      # 问题排查
```

---

## 相关 Skill

| Skill | 用途 |
|-------|------|
| rapid-prototype-workflow | 快速原型开发 |
| test-expert | 测试专家 |
| test-report-followup | 测试报告跟进 |
| dev-task-split | 开发任务拆分 |
| bug-fix-task-split | Bug 修复任务拆分 |
