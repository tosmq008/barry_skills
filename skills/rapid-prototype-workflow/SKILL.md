---
name: rapid-prototype-workflow
description: "This skill manages rapid prototyping projects with 24/7 autonomous development capability. It supports MVP development using UI-first workflow with MCP Pencil, Python/FastAPI backend, SQLite database, and autonomous loop mode for continuous coding until completion. The skill enables hands-off development where AI iterates automatically."
license: MIT
compatibility: "Requires MCP Pencil for UI generation. Backend uses Python with uv. Supports Autoloop/YOLO mode for autonomous development."
metadata:
  category: rapid-development
  phase: prototyping
  version: "2.0.0"
allowed-tools: bash cat read_file write_file mcp
---

# Rapid Prototype Workflow Skill

快速原型开发工作流，支持三端架构 (Client + Admin + Website)，24/7 自动化开发。

## When to Use

**适用：** MVP、概念验证、快速验证商业想法、上市时间紧迫的项目
**不适用：** 生产级系统、安全/性能关键、长期可维护性要求、大型团队协作

## Project Structure (三端架构)

```
./
├── docs/
│   ├── prd/                    # PRD 文档（8个必须）
│   ├── ui/[project].pen        # UI 设计稿（必须）
│   ├── api/api-spec.md         # API 文档（必须）
│   └── test/                   # 测试文档（必须）
├── client/
│   ├── frontend/               # 用户前端 (React + Vite)
│   └── backend/src/            # 用户后端 (FastAPI)
├── admin/
│   ├── frontend/               # 管理前端
│   └── backend/src/            # 管理后端
├── website/                    # 官网（纯静态 HTML）
│   ├── index.html, features.html, pricing.html
│   ├── about.html, contact.html, 404.html
│   └── css/, js/, images/
├── shared/db/data.db           # 共享 SQLite
└── start.sh / stop.sh          # 一键启动脚本
```

> 📄 详细结构说明: `references/project-structure.md`

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Python + FastAPI + SQLModel |
| Database | SQLite (零配置) |
| Package Manager | uv (极速) |
| UI Design | MCP Pencil + frontend-design skill |
| Website | 纯静态 HTML + Tailwind CDN |

---

## Workflow (4 Phases)

### Phase 1: Idea Capture (30min) - 必须输出 8 个 PRD 文档

> ⚠️ **执行前必须读取 `references/prd-templates.md` 获取完整 PRD 模板**

| 文档 | 路径 |
|------|------|
| 项目简介 | `docs/prd/01-project-brief.md` |
| 功能架构图 | `docs/prd/02-feature-architecture.md` |
| 系统角色定义 | `docs/prd/03-role-definition.md` |
| 功能模块划分 | `docs/prd/04-module-design.md` |
| 交互页面清单 | `docs/prd/05-page-list.md` |
| 页面跳转关系 | `docs/prd/06-page-navigation.md` |
| 页面交互操作 | `docs/prd/07-page-interaction.md` |
| 视觉风格规范 | `docs/prd/08-visual-style.md` |

**必须包含：**
- 功能架构图覆盖 Client + Admin + Website 三端
- 系统角色及权限矩阵
- 所有页面编号和跳转关系
- Client 与 Admin 视觉差异定义

---

### Phase 2: UI Design (2-4hrs) - 必须完成 5 轮 Review

> ⚠️ **执行前必须读取 `references/ui-review-templates.md` 获取完整审查模板和交付清单**

**Step 1: 创建设计稿**
```bash
pencil create --name "[project]" --output "docs/ui/[project].pen"
pencil generate --file "docs/ui/[project].pen" --type screens --style "minimal modern"
```

**Step 2: 5 轮迭代审查（必须全部完成）**

| Round | 角色 | Focus |
|-------|------|-------|
| 1 | 商业分析师 | 价值主张、转化路径 |
| 2 | 领域产品经理 | 业务流程、行业实践 |
| 3 | 资深产品经理 | 用户习惯、交互体验 |
| 4 | UED设计专家 | 视觉层次、设计一致性 |
| 5 | 小白用户 | 易用性、直观性 |

**Step 3: 必须覆盖的页面状态**

- **Client:** 启动页、登录、注册、忘记密码、首页(有数据/空/加载中)、列表、详情、搜索、表单、结果页、个人中心、消息、设置、空状态、错误状态、弹窗组件
- **Admin:** 登录、Dashboard、数据列表、新增/编辑表单、详情、配置、弹窗
- **Website:** Landing(Hero+功能+CTA)、功能介绍、定价、关于我们、联系我们、页头导航、页脚、404

> ⚠️ **Website 官网也必须先完成 UI 设计稿，再进行静态页面实现。设计稿同样存放在 `docs/ui/[project].pen` 中。**

---

### Phase 3: Implementation (1-2 days)

> ⚠️ **执行前必须读取：**
> - `references/quick-templates.md` 获取代码模板和 Website HTML 模板
> - `references/startup-scripts.md` 获取启动脚本模板
> - `references/project-structure.md` 获取完整项目结构说明

**执行顺序：**
1. Setup project (30min)
2. Client Side First (1 day)
3. Admin Side (0.5-1 day)
4. Website (2-4hrs) - 纯静态 HTML
5. Integration (2-4hrs)

**必须遵守的代码规范：**
- 后端代码必须放在 `src/` 包下
- Python 导入使用绝对路径 (`from src.database import`)
- 使用 uv 作为包管理器
- 使用 SQLite + SQLModel
- 使用 Tailwind CSS
- **界面实现必须严格按照 UI 设计稿还原**
- **禁止脱离设计稿自行发挥界面样式**
- **设计稿缺失时必须先补全设计稿，再实现界面**

**Quick Start:**
```bash
# Client Backend
cd client/backend && uv init && uv add fastapi uvicorn sqlmodel aiosqlite
mkdir -p src && touch src/__init__.py src/main.py src/models.py src/routes.py src/database.py
uv run uvicorn src.main:app --reload --port 8000

# Client Frontend
npm create vite@latest client/frontend -- --template react-ts
cd client/frontend && npm install -D tailwindcss postcss autoprefixer && npm run dev -- --port 3000

# Website (纯静态)
cd website && python -m http.server 4000
```

**Website 官网要求：**
- **必须先用 MCP Pencil 完成 UI 设计稿，再实现静态页面**
- 纯静态 HTML + Tailwind CSS CDN，无需构建工具
- **必须使用 `frontend-design` skill 进行 Review 和优化**
- 本地预览: `cd website && python -m http.server 4000`
- **禁止跳过设计稿直接写 HTML 代码**

---

### Phase 4: Test & Ship (4-8hrs)

> ⚠️ **执行前必须读取 `references/test-templates.md` 获取完整测试模板**

**测试类型：**
| 类型 | 适用 |
|------|------|
| 单元测试 | ✅ 核心逻辑必须 |
| 集成测试 | ✅ API层必须 |
| 功能测试 | ✅ 必须 |
| E2E测试 | ⚠️ 核心流程 |
| 性能/安全测试 | ❌ 不包含 |

**测试用例独立性要求（必须）：**
- 每个用例使用独立的测试数据
- 测试数据在用例执行前创建，执行后清理
- 不依赖其他用例产生的数据

**发布前检查项：**
- [ ] 核心功能正常工作
- [ ] 无阻塞性 Bug
- [ ] 基本错误处理
- [ ] UI 与设计稿一致

---

## Standard Modules (基础系统模块)

### Client Side
| 模块 | 功能 |
|------|------|
| 个人中心 | 基本信息、修改密码、退出登录 |
| 消息中心 | 消息列表、未读标记 |
| 系统设置 | 关于我们、意见反馈 |

### Admin Side
| 模块 | 功能 |
|------|------|
| 系统配置 | 基础配置、参数配置 |
| 用户管理 | 用户列表、用户状态 |
| 管理员管理 | 管理员列表、重置密码 |

### Website
| 页面 | 功能 |
|------|------|
| 首页 (Landing) | 产品核心价值、CTA按钮 |
| 功能介绍 | 产品功能详细说明 |
| 定价页面 | 价格方案（如有） |
| 关于我们 | 团队/公司介绍 |
| 联系我们 | 联系方式、反馈表单 |

---

## Autonomous Mode (持续开发模式)

> ⚠️ **执行前必须读取 `references/autonomous-mode.md` 获取完整指南**

### 核心机制：状态文件驱动

```
.dev-state/
├── current-phase.txt      # 当前阶段 (1-4)
├── current-task.txt       # 当前任务
├── completed-tasks.txt    # 已完成任务
└── dev-log.txt            # 开发日志
```

### 启动持续开发

用户指令：
```
使用 rapid-prototype-workflow 进行持续开发：
项目名称: [名称]
项目需求: [描述]
```

### AI 必须遵守的规则

**规则 1: 每次对话开始检查状态**
- 检查 `.dev-state/` 是否存在
- 存在则从断点继续，不存在则初始化

**规则 2: 任务粒度控制**
- 单任务 < 10 分钟
- 每完成一个任务立即更新状态文件

**规则 3: 上下文长度自我监控**
- 执行超过 5 个任务时，保存状态并提示用户开新会话
- 提示格式：`⚠️ 建议开启新会话继续开发。请发送 '继续开发' 恢复。`

**规则 4: 阻塞任务处理**
- 遇到阻塞记录到 `blocked-tasks.txt` 并跳过
- 不要卡在单个任务上

### 继续开发指令

用户发送以下任意指令时从断点继续：
- `继续开发`
- `恢复开发`
- `继续 rapid-prototype-workflow`

### 任务清单 (32 个任务)

| Phase | 任务数 | 内容 |
|-------|--------|------|
| 1. PRD | 8 | 8 个 PRD 文档 |
| 2. UI | 8 | 3 端设计稿 + 5 轮 Review |
| 3. Code | 10 | 三端代码实现 |
| 4. Test | 6 | 测试和发布 |

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| UI-First | 先用 MCP Pencil 设计 UI，再写代码 |
| Speed Over Perfection | 快速交付，快速迭代 |
| Design-Driven | 界面实现必须严格按照设计稿还原 |
| Client First | 先完成用户侧，再补充管理侧 |
| frontend-design Required | Website 官网必须使用 frontend-design skill 优化 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/workflow-phases.md` | ⭐ 工作流速查卡（一页纸概览） |
| `references/project-structure.md` | 项目结构详细说明 |
| `references/prd-templates.md` | PRD 文档模板 |
| `references/ui-review-templates.md` | UI 5轮审查模板 |
| `references/quick-templates.md` | 代码模板 + Website HTML |
| `references/startup-scripts.md` | 启动脚本模板 |
| `references/test-templates.md` | 测试模板 |
| `references/autonomous-mode.md` | 持续开发模式指南 |

## Related Skills

- `frontend-design` - UI 优化（**Website 官网必须使用**）
- `prd-template` - PRD 模板
- `dev-task-split` - 任务拆分
- `fullstack-project-workflow` - 企业级项目工作流（原型验证后升级）
