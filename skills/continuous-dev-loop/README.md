# Continuous Dev Loop

7×24 持续自动化开发，自动判断项目状态。

## 使用方式

**统一入口，自动判断：**

```bash
cd /your/project
./continuous-dev start [需求描述]
```

## 自动判断逻辑

| 项目状态 | 行为 |
|----------|------|
| 已在运行 | 提示已运行 |
| 有 `.dev-state/` | 从断点继续 |
| 有 `docs/prd/` 或代码 | 基于现有项目继续 |
| 空项目 | 需要传入需求描述 |

## 示例

### 空项目（需要需求描述）

```bash
cd /empty-project
./continuous-dev start "一个待办事项App，支持增删改查"
```

### 已有项目（自动继续）

```bash
cd /existing-project
./continuous-dev start
```

### 断点继续（自动继续）

```bash
cd /project-with-dev-state
./continuous-dev start
```

## 命令

| 命令 | 说明 |
|------|------|
| `start [requirement]` | 启动（自动判断，也用于恢复暂停） |
| `stop` | 停止守护进程 |
| `pause` | 暂停（完成当前会话后） |
| `status` | 查看状态 |
| `logs` | 实时日志 |
| `reset` | 重置 |

## 安装

```bash
# 复制脚本到项目
cp ~/.claude/skills/continuous-dev-loop/scripts/continuous-dev /your/project/
chmod +x /your/project/continuous-dev
```

## 前置条件

- Claude Code CLI (`claude --version`)
- Python 3.x
- `~/.claude/skills/continuous-dev-loop/` 已安装
- `~/.claude/skills/rapid-prototype-workflow/` 已安装
