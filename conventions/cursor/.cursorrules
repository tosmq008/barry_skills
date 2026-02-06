# CLAUDE.md - AI 编程助手核心约定

> 适用于 Claude Code、Codex、Cursor、Trae、Kiro 等 AI 编程工具

本文档定义了 AI 编程助手在项目中工作的核心规则和约定。

---

## 项目上下文

```yaml
项目类型: 快速原型开发
技术栈:
  前端: React + Vite + Tailwind CSS
  后端: Python + FastAPI + SQLModel
  数据库: SQLite
  包管理: uv (Python) / npm (Node)
架构: 三端架构 (Client + Admin + Website)
```

---

## 核心原则

| 原则 | 说明 |
|------|------|
| UI-First | 先用 MCP Pencil 设计 UI，再写代码 |
| Design-Driven | 界面实现必须严格按照设计稿还原 |
| Speed > Perfect | 快速交付，快速迭代 |
| Client First | 先完成用户侧，再补充管理侧 |
| 状态驱动 | 使用 `.dev-state/` 实现断点续传 |

---

## Development Guidelines

### File Writing Strategy (CRITICAL)

由于 AI 上下文窗口限制，写入文件时必须遵循以下原则：

- **禁止一次性写入大文件** - 容易导致内容截断或丢失
- **分批追加写入** - 每次写入 100-200 行，逐步构建完整文件
- **先创建骨架，再填充内容** - 先写入文件结构，再分批补充各部分
- **写入后立即验证** - 每次写入后读取确认内容完整

---

## 工作模式

### 1. 每次对话开始时

```bash
# 必须先检查项目状态
ls docs/prd/*.md 2>/dev/null    # 检查 PRD 文档
cat .dev-state/state.json       # 检查开发状态
ls -la client/ admin/ website/  # 检查代码目录
```

**决策逻辑：**
- 有 `docs/prd/` → 从断点继续，不重新创建 PRD
- 有 `PRD.md` / `README.md` → 基于现有文档继续
- 项目为空 → 从 Phase 1 开始创建 PRD

### 2. 任务执行规则

- **任务粒度**: 单任务 < 10 分钟
- **状态更新**: 每完成一个任务立即更新状态文件
- **上下文监控**: 执行超过 5 个任务时，保存状态并提示开新会话

### 3. 阻塞处理

遇到阻塞时：
1. 记录到 `.dev-state/blocked-tasks.txt`
2. 跳过当前任务，继续执行后续任务
3. 不要卡在单个任务上

---

## 状态文件协议

```
.dev-state/
├── state.json           # 主状态文件 (JSON)
├── task-registry.json   # 全局任务注册表 (CRITICAL)
├── current-phase.txt    # 当前阶段 (1-4)
├── current-task.txt     # 当前任务
├── completed-tasks.txt  # 已完成任务列表
├── blocked-tasks.txt    # 阻塞任务及原因
└── dev-log.txt          # 开发日志
```

### state.json 格式

```json
{
  "status": "running",
  "last_heartbeat": "2024-01-31T10:00:00Z",
  "current_task": {
    "phase": "3",
    "step": "3.5",
    "checkpoint": {
      "phase": "代码实现",
      "step": "实现 Client Frontend 核心页面",
      "next": "实现 Admin Backend"
    }
  }
}
```

### task-registry.json 格式 (全局任务汇总)

```json
{
  "project": "项目名称",
  "created_at": "2024-01-31T08:00:00Z",
  "updated_at": "2024-01-31T14:30:00Z",
  "summary": {
    "total": 32,
    "completed": 20,
    "in_progress": 1,
    "pending": 10,
    "blocked": 1
  },
  "tasks": [
    {
      "id": "1.1",
      "phase": "1",
      "name": "编写项目简介",
      "status": "completed",
      "agent": "product-expert",
      "started_at": "2024-01-31T08:00:00Z",
      "completed_at": "2024-01-31T08:15:00Z",
      "output": "docs/prd/01-project-brief.md"
    },
    {
      "id": "3.5",
      "phase": "3",
      "name": "实现 Client Frontend 核心页面",
      "status": "in_progress",
      "agent": "frontend-expert",
      "started_at": "2024-01-31T14:00:00Z",
      "completed_at": null,
      "output": null,
      "subtasks": [
        { "name": "登录页", "status": "completed" },
        { "name": "首页", "status": "in_progress" },
        { "name": "列表页", "status": "pending" }
      ]
    },
    {
      "id": "3.3",
      "phase": "3",
      "name": "实现支付接口",
      "status": "blocked",
      "agent": "python-expert",
      "blocked_reason": "缺少支付网关配置",
      "blocked_at": "2024-01-31T12:00:00Z"
    }
  ]
}
```

### 任务状态持久化规则 (CRITICAL)

1. **任务开始时**: 立即更新 `task-registry.json`，设置 `status: "in_progress"`
2. **任务完成时**: 立即更新 `status: "completed"` 和 `completed_at`
3. **任务阻塞时**: 设置 `status: "blocked"` 并记录 `blocked_reason`
4. **子任务进度**: 对于大任务，使用 `subtasks` 数组跟踪细粒度进度
5. **中断恢复**: 新会话启动时，读取 `task-registry.json` 找到 `in_progress` 任务继续

### 中断恢复流程

```bash
# 新会话启动时的检查顺序
1. cat .dev-state/task-registry.json  # 读取全局任务汇总
2. 找到 status="in_progress" 的任务  # 定位中断点
3. 检查该任务的 subtasks 进度        # 确定具体断点
4. 从断点继续执行                    # 不重复已完成工作
```

---

## UI 设计规范 (MCP Pencil)

### 设计稿存储路径

```
docs/ui/
├── [project-name].pen      # 主设计稿文件 (包含所有端)
├── client/                 # Client 端设计稿 (可选拆分)
│   └── client.pen
├── admin/                  # Admin 端设计稿 (可选拆分)
│   └── admin.pen
└── website/                # Website 设计稿 (可选拆分)
    └── website.pen
```

### MCP Pencil 工具使用规范

**必须使用 Pencil MCP 工具操作 .pen 文件，禁止使用 Read/Grep 等工具直接读取。**

| 工具 | 用途 | 使用时机 |
|------|------|----------|
| `get_editor_state()` | 获取当前编辑器状态 | 每次设计任务开始时 |
| `open_document(path)` | 打开设计稿文件 | 打开已有 .pen 文件 |
| `open_document("new")` | 创建新设计稿 | 项目初始化时 |
| `get_guidelines(topic)` | 获取设计指南 | 设计前获取规范 |
| `get_style_guide_tags()` | 获取风格标签 | 选择设计风格时 |
| `get_style_guide(tags)` | 获取风格指南 | 应用设计风格时 |
| `batch_get(patterns)` | 查询设计节点 | 读取设计稿内容 |
| `batch_design(operations)` | 批量设计操作 | 创建/修改设计元素 |
| `get_screenshot(nodeId)` | 获取节点截图 | 验证设计效果 |

### 设计工作流

```
1. get_editor_state()           # 检查当前状态
2. open_document() / new        # 打开或创建设计稿
3. get_guidelines("landing-page" | "design-system")  # 获取设计指南
4. get_style_guide_tags()       # 获取可用风格标签
5. get_style_guide(tags)        # 选择并应用风格
6. batch_design(operations)     # 执行设计操作 (每次 ≤25 个操作)
7. get_screenshot(nodeId)       # 验证设计效果
8. 重复 6-7 直到完成
```

### 设计稿命名规范

| 端 | 文件名 | 示例 |
|---|--------|------|
| 统一设计稿 | `[project-name].pen` | `todo-app.pen` |
| Client 端 | `client.pen` 或 `[project]-client.pen` | `todo-client.pen` |
| Admin 端 | `admin.pen` 或 `[project]-admin.pen` | `todo-admin.pen` |
| Website | `website.pen` 或 `[project]-website.pen` | `todo-website.pen` |

### 设计稿内容要求

**每个 .pen 文件必须包含：**

1. **页面结构** - 所有页面的 Frame 布局
2. **组件库** - 可复用的 UI 组件 (reusable: true)
3. **状态变体** - 空状态、加载中、错误状态
4. **响应式** - 移动端和桌面端适配

**Client 端必须覆盖：**
- 入口流程：启动页、引导页、登录、注册、忘记密码
- 首页：有数据、空状态、加载中
- 核心页面：列表、详情、搜索、筛选
- 操作页面：表单、确认、结果
- 个人中心：资料、设置、消息
- 异常状态：空、加载、错误、404

**Admin 端必须覆盖：**
- 登录页、Dashboard
- 数据列表（有数据/空/加载中）
- 表单（新增/编辑）、详情页
- 系统配置、确认弹窗

**Website 必须覆盖：**
- Landing (Hero + 功能 + CTA)
- 功能介绍、定价、关于、联系
- 页头、页脚、404

---

## 文档要求

### 必须输出的文档

| 序号 | 文档 | 路径 |
|------|------|------|
| 1 | 项目简介 | `docs/prd/01-project-brief.md` |
| 2 | 功能架构图 | `docs/prd/02-feature-architecture.md` |
| 3 | 系统角色定义 | `docs/prd/03-role-definition.md` |
| 4 | 功能模块划分 | `docs/prd/04-module-design.md` |
| 5 | 交互页面清单 | `docs/prd/05-page-list.md` |
| 6 | 页面跳转关系 | `docs/prd/06-page-navigation.md` |
| 7 | 页面交互操作 | `docs/prd/07-page-interaction.md` |
| 8 | 视觉风格规范 | `docs/prd/08-visual-style.md` |
| 9 | UI 设计稿 | `docs/ui/[project].pen` |
| 10 | API 接口文档 | `docs/api/api-spec.md` |
| 11 | 测试方案 | `docs/test/test-plan.md` |
| 12 | 测试用例 | `docs/test/test-cases.md` |

---

## 禁止事项

- **禁止** 脱离设计稿自行发挥界面样式
- **禁止** 在设计稿缺失时直接实现界面
- **禁止** 跳过 UI 设计稿直接写代码
- **禁止** 重复已完成的工作
- **禁止** 盲目重新创建已存在的文档
- **禁止** 过度设计架构
- **禁止** 使用默认的丑陋样式

---

## 继续开发指令

当用户发送以下指令时，从断点继续：

```
继续开发
恢复开发
继续 rapid-prototype-workflow
```

### 响应格式

```markdown
📊 **开发状态恢复**

当前阶段: Phase 3 - 代码实现
当前任务: 3.5 实现 Client Frontend 核心页面
已完成: 20/32 任务 (62.5%)
阻塞任务: 1 个

继续执行任务 3.5...
```

---

## 上下文预警

当感知到上下文过长时，输出：

```markdown
⚠️ 建议开启新会话继续开发。当前进度已保存到 .dev-state/，
请发送 '继续开发' 指令恢复。
```

---

## 相关文档

- [AGENTS.md](./AGENTS.md) - OpenAI Codex CLI 约定
- [KIRO.md](./KIRO.md) - AWS Kiro 约定
- [WORKFLOW.md](./WORKFLOW.md) - 开发工作流约定
- [PROJECT.md](./PROJECT.md) - 项目结构约定
- [CODING.md](./CODING.md) - 编码规范约定
