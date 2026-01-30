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

This skill enables fast iteration for experimental projects, MVPs, and proof-of-concept development with **24/7 autonomous coding capability**.

## Key Features

- **UI-First**: MCP Pencil + frontend-design 生成美观界面
- **Lightweight Stack**: Python + FastAPI + SQLite
- **Autonomous Mode**: 7x24小时自动化开发，直到完成
- **Self-Correcting**: 自动修复错误，持续迭代

## Technology Stack (Lightweight)

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | React + Vite + Tailwind CSS | 快速构建，热更新，美观样式 |
| Backend | Python + FastAPI | 轻量、快速开发 |
| Database | SQLite | 零配置，单文件，便携 |
| Package Manager | uv | 极速Python依赖管理 |
| ORM | SQLModel | FastAPI原生支持，简洁 |
| UI Design | MCP Pencil + frontend-design | 生成设计 + 优化美观度 |

### Why These Choices?

- **SQLite**: 无需安装数据库服务，单文件存储，开发即生产
- **uv**: 比pip快10-100倍，现代Python包管理
- **FastAPI**: 自动API文档，类型安全，异步支持
- **SQLModel**: 结合SQLAlchemy和Pydantic，代码最少
- **Tailwind CSS**: 原子化CSS，快速构建美观界面
- **frontend-design skill**: 避免AI生成的通用丑陋界面，产出专业级UI

## 适用场景

本 skill 必须用于以下场景：
- 构建 MVP 或概念验证项目
- 快速验证商业想法
- 需要快速反馈的实验性功能
- 上市时间紧迫的项目
- 架构完美性不是首要目标的项目

## 不适用场景

以下场景禁止使用本 skill：
- 构建生产级系统
- 安全/性能是关键要求
- 需要长期可维护性
- 大型团队协作项目

## Project Structure

Rapid prototypes also support dual-side architecture (Client + Admin):

```
project/
├── client/              # 使用侧 (User-facing)
│   ├── frontend/        # 用户前端
│   └── backend/         # 用户后端API
├── admin/               # 管理侧 (Admin)
│   ├── frontend/        # 管理后台前端
│   └── backend/         # 管理后台API
└── shared/              # 共享代码
```

### Module Responsibilities

| Module | Purpose | Priority |
|--------|---------|----------|
| client-frontend | 用户界面、核心交互 | P0 - 必须 |
| client-backend | 用户API、业务逻辑 | P0 - 必须 |
| admin-frontend | 数据管理、配置界面 | P0 - 必须 |
| admin-backend | 管理API、数据操作 | P0 - 必须 |

**Note:** Admin模块必须实现，与Client侧同等重要。

## Standard Modules (基础系统模块)

所有项目必备的基础系统功能模块。

### Client Side (C侧) 基础模块

#### 1. 个人中心 (Personal Center)

| 功能 | 描述 |
|------|------|
| 基本信息 | 头像、昵称展示与编辑 |
| 修改密码 | 密码修改 |
| 退出登录 | 退出当前账号 |

#### 2. 消息中心 (Message Center)

| 功能 | 描述 |
|------|------|
| 消息列表 | 系统通知列表 |
| 未读标记 | 未读数量、标记已读 |

#### 3. 系统设置 (System Settings)

| 功能 | 描述 |
|------|------|
| 关于我们 | 版本信息 |
| 意见反馈 | 用户反馈入口 |

---

### Admin Side (管理侧) 基础模块

#### 1. 系统配置 (System Config)

| 功能 | 描述 |
|------|------|
| 基础配置 | 网站名称、Logo |
| 参数配置 | 系统参数键值对管理 |

#### 2. 用户管理 (User Management)

| 功能 | 描述 |
|------|------|
| 用户列表 | 用户搜索、分页展示 |
| 用户状态 | 启用/禁用用户 |

#### 3. 管理员管理 (Admin Management)

| 功能 | 描述 |
|------|------|
| 管理员列表 | 管理员账号增删改查 |
| 重置密码 | 重置管理员密码 |

## Core Principles

| Principle | Description |
|-----------|-------------|
| UI-First | Design UI before coding using MCP Pencil |
| Speed Over Perfection | Ship fast, iterate faster |
| Function Over Architecture | Make it work, not perfect |
| Strict Testing | Functional correctness is non-negotiable |
| Minimal Documentation | Just enough to understand |
| Client First | 先完成用户侧，再补充管理侧 |

## Workflow Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. Idea    │ →  │  2. UI      │ →  │  3. Auto    │ →  │  4. Test    │
│  Capture    │    │  Design     │    │  Implement  │    │  & Ship     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
    (30min)          (2-4hrs)         (Autonomous)        (Auto-verify)
                                       24/7 Loop
```

## 🚀 Autonomous Development Mode (YOLO Mode)

### What is Autonomous Mode?

让 AI 在循环中持续工作，直到任务完成。你可以睡觉、离开，醒来时代码已经写好。

```
定义目标 → AI 自动迭代 → 独立验证 → 完成或继续
    ↑                                    │
    └────────────────────────────────────┘
              (失败则继续循环)
```

### Setup Autoloop

```bash
# 安装 Autoloop 插件
claude plugin marketplace add yaoshengzhe/autoloop
claude plugin install autoloop@autoloop

# 或使用简单的 shell 循环
```

### Autonomous Loop Commands

```bash
# 使用 Autoloop 启动持续开发（无迭代限制）
/autoloop:autoloop "Build complete user authentication system:

# Requirements
- Login/logout REST endpoints  
- JWT token generation
- Password hashing with bcrypt
- SQLite database storage

# Verification Criteria
- All API endpoints working
- Unit tests passing
- Frontend can login/logout successfully"
```

### Simple Shell Loop (Continuous Mode)

```bash
#!/bin/bash
# loop.sh - 持续运行直到完成

PROMPT_FILE="prompt.md"

while true; do
  echo "========== $(date) =========="
  
  cat "$PROMPT_FILE" | claude -p --dangerously-skip-permissions
  
  # 自动提交进度
  git add . && git commit -m "Auto: $(date +%H:%M:%S)" 2>/dev/null || true
  
  # 检查是否完成
  # if [ -f ".done" ]; then break; fi
done
```

### Prompt Template for Autonomous Mode

```markdown
# prompt.md

## Goal
Build a complete [feature name] for the rapid prototype.

## Current Status
Check existing code and continue from where we left off.

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Verification
Before claiming completion:
1. Run all tests: `pytest` and `npm test`
2. Verify API endpoints work
3. Check frontend renders correctly

## Rules
- Focus on functionality over perfection
- Use SQLite for database
- Use Tailwind CSS for styling
- Commit progress frequently
- If stuck, try a different approach
```

### Safety Guidelines for Autonomous Mode

1. **使用独立项目目录**
   ```bash
   mkdir ~/rapid-projects/my-prototype
   cd ~/rapid-projects/my-prototype
   ```

2. **使用 Git 版本控制（必须）**
   ```bash
   git init
   git add . && git commit -m "Before autonomous mode"
   ```

3. **设置工作边界**
   ```markdown
   # 在 prompt.md 中明确限制
   ## Boundaries
   - Only modify files in this project directory
   - Do not install system-level packages
   - Do not modify any config outside project
   ```

### Autonomous Mode Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    Autonomous Development                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 定义任务 (prompt.md)                                      │
│     └── 明确目标、需求、验证标准                               │
│                                                              │
│  2. 启动循环                                                  │
│     └── /autoloop:autoloop "..."                             │
│                                                              │
│  3. AI 自动工作                                               │
│     ├── 写代码                                                │
│     ├── 运行测试                                              │
│     ├── 修复错误                                              │
│     ├── 提交进度                                              │
│     └── 重复直到完成                                          │
│                                                              │
│  4. 独立验证                                                  │
│     └── 另一个 Agent 验证完成度                               │
│                                                              │
│  5. 完成或继续                                                │
│     ├── 验证通过 → 结束                                       │
│     └── 验证失败 → 继续迭代                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Example: Build Complete Feature Autonomously

```bash
/autoloop:autoloop "Build user management for rapid prototype:

# Tech Stack
- Backend: Python + FastAPI + SQLite + SQLModel
- Frontend: React + Vite + Tailwind CSS
- Package Manager: uv for Python

# Features to Build
1. User registration (email + password)
2. User login with JWT
3. User profile page
4. Admin user list page
5. Admin can disable users

# File Structure
client/backend/src/ - FastAPI backend
client/frontend/src/ - React frontend
admin/backend/src/ - Admin API
admin/frontend/src/ - Admin UI
shared/db/data.db - SQLite database

# Verification (checked by independent agent)
- All API endpoints return correct responses
- Frontend pages render without errors
- User can register → login → view profile
- Admin can view and manage users
- All tests passing

# Style Requirements
- Use Tailwind CSS
- Minimal, clean design
- Consistent spacing and colors

# Completion Signal
When all features are complete and verified, create a file named '.done'"
```

## Phase 1: Idea Capture (30 minutes)

### 1.1 One-Page Brief

Create a simple brief answering:

```markdown
# Project Brief: [Name]

## What problem are we solving?
[1-2 sentences]

## Who is the target user?
[1 sentence]

## What is the core feature?
[Bullet list, max 5 items]

## What does success look like?
[1-2 measurable outcomes]

## Timeline
[Target completion date]
```

### 1.2 功能架构图 (Feature Architecture)

PRD 必须包含完整的功能架构图，覆盖所有功能细节点：

```
┌─────────────────────────────────────────────────────────────────┐
│                        [项目名称] 功能架构图                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    C侧 (用户端)                          │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ 核心功能 │  │ 个人中心 │  │ 消息中心 │  │ 系统设置 │   │   │
│  │  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤   │   │
│  │  │ 功能1   │  │ 基本信息 │  │ 消息列表 │  │ 关于我们 │   │   │
│  │  │ 功能2   │  │ 修改密码 │  │ 未读标记 │  │ 意见反馈 │   │   │
│  │  │ 功能3   │  │ 退出登录 │  │ 标记已读 │  │ 版本信息 │   │   │
│  │  │ ...     │  │         │  │         │  │         │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Admin侧 (管理端)                       │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ 系统配置 │  │ 用户管理 │  │ 管理员   │  │ 业务管理 │   │   │
│  │  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤   │   │
│  │  │ 基础配置 │  │ 用户列表 │  │ 管理员   │  │ 业务功能 │   │   │
│  │  │ 参数配置 │  │ 用户状态 │  │ 列表    │  │ 数据管理 │   │   │
│  │  │         │  │ 用户详情 │  │ 重置密码 │  │ ...     │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**功能架构图要求：**
- 必须列出所有功能模块
- 每个模块必须细化到具体功能点
- 区分 C侧 和 Admin侧
- 标注功能优先级 (P0/P1/P2)

### 1.3 不包含内容
- Technical architecture ❌
- Performance requirements ❌
- Security audit ❌

**Output:** One-page project brief + 功能架构图

## Phase 2: UI Design with MCP Pencil + frontend-design (2-4 hours)

### 2.0 UI 全生命周期覆盖要求

**UI 设计稿必须覆盖用户完整使用旅程，不允许遗漏任何页面状态。**

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI 全生命周期覆盖清单                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 入口阶段                                                     │
│     ├── 启动页/闪屏 (Splash)                                     │
│     ├── 引导页 (Onboarding) - 首次使用                           │
│     ├── 登录页 (Login)                                          │
│     ├── 注册页 (Register)                                       │
│     ├── 忘记密码 (Forgot Password)                              │
│     └── 第三方登录 (业务需要时必须实现)                          │
│                                                                 │
│  2. 核心功能阶段                                                 │
│     ├── 首页/主界面                                              │
│     ├── 核心功能页面 (根据业务)                                   │
│     ├── 详情页                                                   │
│     ├── 列表页                                                   │
│     ├── 搜索页 + 搜索结果                                        │
│     └── 筛选/分类页                                              │
│                                                                 │
│  3. 交互操作阶段                                                 │
│     ├── 表单填写页                                               │
│     ├── 确认页/预览页                                            │
│     ├── 支付页 (业务需要时必须实现)                              │
│     └── 结果页 (成功/失败)                                       │
│                                                                 │
│  4. 个人中心阶段                                                 │
│     ├── 个人中心首页                                             │
│     ├── 个人信息编辑                                             │
│     ├── 修改密码                                                 │
│     ├── 消息中心                                                 │
│     └── 系统设置                                                 │
│                                                                 │
│  5. 异常状态 (必须覆盖)                                          │
│     ├── 空状态 (Empty State) - 无数据                            │
│     ├── 加载状态 (Loading)                                       │
│     ├── 错误状态 (Error) - 网络错误/服务器错误                    │
│     ├── 404 页面                                                 │
│     └── 无权限页面                                               │
│                                                                 │
│  6. 弹窗/浮层 (必须覆盖)                                         │
│     ├── 确认弹窗 (Confirm Dialog)                                │
│     ├── 提示弹窗 (Alert)                                         │
│     ├── 操作菜单 (Action Sheet)                                  │
│     ├── Toast 提示                                               │
│     └── 底部弹窗 (Bottom Sheet)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**UI 设计稿交付清单：**

| 类别 | 必须包含 | 检查项 |
|------|----------|--------|
| 入口流程 | 登录、注册、忘记密码 | ☐ 完整流程 |
| 核心页面 | 首页、列表、详情、搜索 | ☐ 所有主要页面 |
| 个人中心 | 个人中心、编辑、设置 | ☐ 完整模块 |
| 空状态 | 每个列表页的空状态 | ☐ 所有列表 |
| 加载状态 | 骨架屏/Loading | ☐ 统一风格 |
| 错误状态 | 网络错误、服务错误 | ☐ 友好提示 |
| 弹窗组件 | 确认、提示、操作菜单 | ☐ 统一风格 |
| Admin端 | 登录、列表、表单、详情 | ☐ 完整覆盖 |

### 2.1 Design Principles (简约美观)

**UI设计原则：**
- **简约优先**: 去除不必要的元素，保持界面干净
- **留白充足**: 给内容呼吸空间，不要拥挤
- **一致性**: 统一的颜色、字体、间距
- **层次分明**: 通过大小、颜色、位置区分重要性

### 2.2 Generate UI Design

**Step 1: 使用 MCP Pencil 生成初始设计**

**设计稿文件规范：**
- 文件格式：`.pen`
- 文件命名：`[工程名称].pen`
- 存储路径：`docs/ui/[工程名称].pen`
- 所有 UI 设计稿必须通过 MCP Pencil 读取和修改

```
# 项目结构
project/
├── docs/
│   └── ui/
│       └── [project-name].pen    # UI 设计稿文件（必须）
├── client/
├── admin/
└── ...
```

**MCP Pencil 命令：**

```bash
# 1. 创建新设计稿
pencil create --name "[project-name]" --output "docs/ui/[project-name].pen"

# 2. 生成主要页面
pencil generate --file "docs/ui/[project-name].pen" --type screens --description "[feature description]" --style "minimal modern"

# 3. 生成组件库
pencil generate --file "docs/ui/[project-name].pen" --type components --style "clean minimal"

# 4. 生成素材资源
pencil generate --file "docs/ui/[project-name].pen" --type assets --theme "simple line icons"

# 5. 读取设计稿
pencil read --file "docs/ui/[project-name].pen"

# 6. 更新设计稿
pencil update --file "docs/ui/[project-name].pen" --screen "[screen-name]" --changes "[changes]"

# 7. 导出设计规范
pencil export --file "docs/ui/[project-name].pen" --format html|css
```

**设计稿管理规范：**

| 操作 | 命令 | 说明 |
|------|------|------|
| 创建 | `pencil create` | 初始化 .pen 文件 |
| 生成 | `pencil generate` | 生成页面/组件/素材 |
| 读取 | `pencil read` | 读取现有设计稿 |
| 更新 | `pencil update` | 修改现有设计 |
| 导出 | `pencil export` | 导出为代码/规范 |

**必须遵守：**
- 所有 UI 设计必须保存到 `docs/ui/[project-name].pen`
- 后续所有设计修改必须通过 `pencil read` 读取后再修改
- 禁止直接修改 .pen 文件，必须通过 MCP Pencil 命令操作
- 每次 UI Review 后的修改必须更新到 .pen 文件

**Step 2: 使用 frontend-design skill 优化美观度**

```bash
# 激活 frontend-design skill 进行UI优化
/frontend-design

# 优化指令示例
"请使用 frontend-design skill 优化这个页面：
- 使用 Tailwind CSS 实现简约现代风格
- 确保足够的留白和呼吸感
- 使用柔和的颜色搭配
- 添加微妙的阴影和圆角
- 优化排版层次"
```

### 2.3 UI Style Guide (简约风格)

```css
/* 必须使用的简约配色 */
--primary: #3b82f6;      /* 蓝色主色 */
--secondary: #64748b;    /* 灰色辅助 */
--background: #f8fafc;   /* 浅灰背景 */
--surface: #ffffff;      /* 白色卡片 */
--text-primary: #1e293b; /* 深色文字 */
--text-secondary: #64748b;/* 浅色文字 */

/* 必须使用的间距 */
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */

/* 必须使用的圆角 */
--radius-sm: 0.375rem;   /* 6px */
--radius-md: 0.5rem;     /* 8px */
--radius-lg: 0.75rem;    /* 12px */
```

### 2.4 Design Deliverables

**Client Side (用户侧) - 必须完整覆盖：**

| 阶段 | 页面 | 状态 |
|------|------|------|
| 入口 | 启动页、引导页、登录、注册、忘记密码 | ☐ |
| 首页 | 首页(有数据)、首页(空状态)、首页(加载中) | ☐ |
| 核心 | 列表页、详情页、搜索页、筛选页 | ☐ |
| 操作 | 表单页、确认页、结果页(成功/失败) | ☐ |
| 个人 | 个人中心、编辑资料、修改密码 | ☐ |
| 消息 | 消息列表、消息详情、空消息 | ☐ |
| 设置 | 系统设置、关于我们、意见反馈 | ☐ |
| 异常 | 空状态、加载中、网络错误、404 | ☐ |
| 组件 | 弹窗、Toast、ActionSheet | ☐ |

**Admin Side (管理侧) - 必须完整覆盖：**

| 阶段 | 页面 | 状态 |
|------|------|------|
| 入口 | 登录页 | ☐ |
| 首页 | Dashboard(数据概览) | ☐ |
| 列表 | 数据列表(有数据/空/加载中) | ☐ |
| 表单 | 新增表单、编辑表单 | ☐ |
| 详情 | 数据详情页 | ☐ |
| 配置 | 系统配置页 | ☐ |
| 组件 | 确认弹窗、操作反馈 | ☐ |

**Shared 组件库：**
- [ ] Color palette (简约配色)
- [ ] Typography (清晰易读)
- [ ] Icon set (线性图标)
- [ ] Button styles (各状态)
- [ ] Form components (输入框、选择器等)
- [ ] Card components
- [ ] Empty/Loading/Error states

### 2.5 UI Multi-Role Review (5轮迭代审查)

**每轮 Review 基于上一轮的改进结果进行，确保 UI 质量层层提升。**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Round 1    │ →  │  Round 2    │ →  │  Round 3    │ →  │  Round 4    │ →  │  Round 5    │
│  商业分析师  │    │  领域产品   │    │  资深产品   │    │  UED专家    │    │  小白用户   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

#### Round 1: 商业分析师 Review

```markdown
# UI Review - Round 1: 商业分析师视角

## Review Focus
- 界面是否清晰传达产品价值主张？
- 核心功能入口是否突出？
- 用户转化路径是否顺畅？
- 商业目标是否在UI中得到体现？

## 必须检查项
- [ ] 首屏是否传达核心价值？
- [ ] CTA按钮是否明确？
- [ ] 付费/转化入口是否合理？
- [ ] 数据展示是否支持商业决策？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

#### Round 2: 项目专业领域产品经理 Review

```markdown
# UI Review - Round 2: 领域产品经理视角

## Review Focus (基于Round 1改进后)
- 功能是否符合行业最佳实践？
- 业务流程是否完整？
- 专业术语使用是否准确？
- 是否满足目标用户的专业需求？

## 必须检查项
- [ ] 业务流程是否完整闭环？
- [ ] 专业功能是否易于发现？
- [ ] 数据展示是否符合行业习惯？
- [ ] 异常场景是否有合理处理？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

#### Round 3: 中国互联网资深产品经理 Review

```markdown
# UI Review - Round 3: 资深产品经理视角

## Review Focus (基于Round 2改进后)
- 是否符合中国用户使用习惯？
- 交互模式是否主流？
- 是否借鉴了成功产品的设计？
- 用户体验是否流畅？

## 必须检查项
- [ ] 导航结构是否清晰？
- [ ] 操作反馈是否及时？
- [ ] 加载状态是否友好？
- [ ] 是否有适当的引导？
- [ ] 是否考虑了移动端体验？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

#### Round 4: 专业UED设计专家 Review

```markdown
# UI Review - Round 4: UED设计专家视角

## Review Focus (基于Round 3改进后)
- 视觉层次是否清晰？
- 色彩搭配是否和谐？
- 间距和对齐是否规范？
- 组件设计是否一致？

## 必须检查项
- [ ] 视觉层次：主次分明
- [ ] 色彩：配色和谐，对比度合适
- [ ] 排版：字体大小、行高、间距规范
- [ ] 组件：风格统一，状态完整
- [ ] 动效：自然流畅，不过度
- [ ] 响应式：各尺寸适配良好

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

#### Round 5: 小白用户 Review

```markdown
# UI Review - Round 5: 小白用户视角

## Review Focus (基于Round 4改进后)
- 第一次使用能否快速上手？
- 功能是否一目了然？
- 是否有困惑的地方？
- 操作是否简单直观？

## 必须检查项
- [ ] 不看说明能否完成主要任务？
- [ ] 按钮文字是否易懂？
- [ ] 错误提示是否友好？
- [ ] 是否知道下一步该做什么？
- [ ] 整体感觉是否舒适？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

#### Review 执行命令

```bash
# 自动执行5轮UI Review
/autoloop:autoloop "Execute 5-round UI review process:

Round 1 - 商业分析师视角:
Review current UI from business analyst perspective, focus on value proposition and conversion.
Make improvements based on feedback.

Round 2 - 领域产品经理视角:
Review improved UI from domain product manager perspective, focus on business flow completeness.
Make improvements based on feedback.

Round 3 - 资深产品经理视角:
Review improved UI from senior PM perspective, focus on Chinese user habits and UX.
Make improvements based on feedback.

Round 4 - UED设计专家视角:
Review improved UI from UED expert perspective, focus on visual hierarchy and design consistency.
Make improvements based on feedback.

Round 5 - 小白用户视角:
Review improved UI from novice user perspective, focus on ease of use and clarity.
Make final improvements.

Output: Create ui-review-report.md documenting all 5 rounds of feedback and changes."
```

### 2.6 Quick Design Review

必须检查项 (5 minutes):
- [ ] 界面是否简约干净？
- [ ] 留白是否充足？
- [ ] 颜色是否协调统一？
- [ ] 文字层次是否清晰？
- [ ] 核心操作是否突出？
- [ ] 5轮Review是否全部完成？

**全生命周期覆盖检查：**
- [ ] 入口流程完整？(登录/注册/忘记密码)
- [ ] 核心页面完整？(首页/列表/详情/搜索)
- [ ] 个人中心完整？(资料/密码/消息/设置)
- [ ] 空状态全覆盖？(每个列表页)
- [ ] 加载状态统一？(骨架屏/Loading)
- [ ] 错误状态友好？(网络错误/服务错误)
- [ ] 弹窗组件统一？(确认/提示/操作菜单)
- [ ] Admin端完整？(登录/列表/表单/详情)

**Output:** 经过5轮专业Review的简约美观UI设计，覆盖全生命周期

## Phase 3: Quick Implementation (1-2 days)

### 3.1 Implementation Order

```
1. Setup project (30min)
   └── Initialize client + admin structure

2. Client Side First (1 day)
   ├── Client Frontend (4-6hrs)
   │   └── Convert MCP Pencil designs to code
   │   └── Core user interactions
   └── Client Backend (4-6hrs)
       └── User-facing APIs
       └── Core business logic

3. Admin Side (0.5-1 day)
   ├── Admin Frontend (3-4hrs)
   │   └── Data management UI
   │   └── Use admin templates (Ant Design Pro, etc.)
   └── Admin Backend (2-3hrs)
       └── CRUD APIs for management
       └── Can share models with client-backend

4. Integration (2-4hrs)
   └── Connect all modules
   └── Basic error handling
```

### 3.2 Coding Guidelines

**必须遵守：**
- 必须使用 Tailwind CSS 构建简约美观的界面
- 必须使用 frontend-design skill 优化UI细节
- 必须使用现成组件库 (Headless UI, Radix UI)
- 必须保持代码简洁，避免过度封装
- 必须注重视觉细节（间距、对齐、颜色）

**禁止事项：**
- 禁止使用过于花哨的动画
- 禁止堆砌太多颜色
- 禁止忽视移动端适配
- 禁止使用默认的丑陋样式
- 禁止过度设计架构

### 3.3 Minimal Project Structure

```
project/
├── docs/
│   └── ui/
│       └── [project-name].pen  # UI 设计稿（必须）
├── client/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── pages/          # 用户页面
│   │   │   ├── components/     # 用户组件
│   │   │   ├── api/            # API调用
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── backend/
│       ├── src/
│       │   ├── __init__.py
│       │   ├── main.py         # FastAPI入口
│       │   ├── models.py       # SQLModel模型
│       │   ├── routes.py       # API路由
│       │   └── database.py     # SQLite连接
│       ├── data.db             # SQLite数据库文件
│       ├── pyproject.toml      # uv项目配置
│       └── uv.lock             # 依赖锁定
├── admin/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── pages/          # 管理页面
│   │   │   ├── components/     # 管理组件
│   │   │   └── App.tsx
│   │   └── package.json
│   └── backend/
│       ├── src/
│       │   ├── __init__.py
│       │   ├── main.py         # FastAPI入口
│       │   ├── models.py       # 复用或扩展client模型
│       │   └── routes.py       # 管理API路由
│       ├── pyproject.toml
│       └── uv.lock
├── shared/
│   └── db/
│       └── data.db             # 共享SQLite数据库
└── README.md
```

### 3.4 Backend Setup with uv

```bash
# 安装 uv (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 初始化后端项目
cd client/backend
uv init
uv add fastapi uvicorn sqlmodel aiosqlite

# 创建 src 包
mkdir -p src
touch src/__init__.py src/main.py src/models.py src/routes.py src/database.py

# 运行开发服务器
uv run uvicorn src.main:app --reload --port 8000
```

### 3.5 SQLite + SQLModel 示例

```python
# src/database.py
from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

# src/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ItemBase(SQLModel):
    name: str
    description: Optional[str] = None

class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    created_at: datetime

# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import init_db
from src.routes import router

app = FastAPI(title="Rapid Prototype API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router, prefix="/api")
```

### 3.6 API 文档生成约定 (必须)

**所有 API 必须生成完整的接口文档，这是强制要求。**

#### 3.6.1 FastAPI 自动文档配置

```python
# src/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="[项目名称] API",
    description="[项目描述]",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI 文档地址
    redoc_url="/redoc",         # ReDoc 文档地址
    openapi_url="/openapi.json" # OpenAPI JSON Schema
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="[项目名称] API",
        version="1.0.0",
        description="[项目描述]",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### 3.6.2 API 路由文档规范

**每个 API 端点必须包含以下文档元素：**

```python
# src/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户账号，手机号必须唯一",
    responses={
        201: {"description": "用户创建成功"},
        400: {"description": "手机号已存在"},
        422: {"description": "请求参数验证失败"}
    }
)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    创建新用户:
    
    - **phone**: 手机号（必填，唯一）
    - **password**: 密码（必填，最少6位）
    - **nickname**: 昵称（必填）
    """
    pass

@router.get(
    "/",
    response_model=List[UserRead],
    summary="获取用户列表",
    description="分页获取用户列表，支持搜索"
)
def list_users(
    page: int = 1,
    size: int = 20,
    search: str = None,
    session: Session = Depends(get_session)
):
    """
    获取用户列表:
    
    - **page**: 页码，默认1
    - **size**: 每页数量，默认20
    - **search**: 搜索关键词（可选）
    """
    pass
```

#### 3.6.3 数据模型文档规范

**所有 Pydantic/SQLModel 模型必须包含字段描述：**

```python
# src/models/user.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(SQLModel):
    """用户创建请求体"""
    phone: str = Field(..., description="手机号", example="13800001111", min_length=11, max_length=11)
    password: str = Field(..., description="密码", example="123456", min_length=6)
    nickname: str = Field(..., description="昵称", example="张三", max_length=50)

class UserRead(SQLModel):
    """用户响应体"""
    id: int = Field(..., description="用户ID", example=1)
    phone: str = Field(..., description="手机号", example="13800001111")
    nickname: str = Field(..., description="昵称", example="张三")
    avatar: Optional[str] = Field(None, description="头像URL", example="https://example.com/avatar.png")
    is_active: bool = Field(..., description="是否启用", example=True)
    created_at: datetime = Field(..., description="创建时间")

class UserUpdate(SQLModel):
    """用户更新请求体"""
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    avatar: Optional[str] = Field(None, description="头像URL")
```

#### 3.6.4 API 文档必须包含内容

| 内容 | 要求 | 示例 |
|------|------|------|
| 接口标题 | summary 必填 | "创建用户" |
| 接口描述 | description 必填 | "创建新用户账号" |
| 请求参数 | 每个参数必须有描述 | Field(description="手机号") |
| 响应模型 | response_model 必填 | response_model=UserRead |
| 状态码 | responses 必填 | 200/201/400/404/422 |
| 标签分组 | tags 必填 | tags=["用户管理"] |
| 示例值 | example 必填 | example="13800001111" |

#### 3.6.5 API 文档访问地址

```
# 开发环境 API 文档地址（必须可访问）

Client Backend:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

Admin Backend:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json
```

#### 3.6.6 API 文档检查清单

```markdown
# API 文档必须检查项

## 基础配置
- [ ] FastAPI 配置了 title、description、version
- [ ] docs_url 和 redoc_url 已启用
- [ ] openapi_url 可访问

## 每个接口必须包含
- [ ] summary（接口标题）
- [ ] description（接口描述）
- [ ] tags（标签分组）
- [ ] response_model（响应模型）
- [ ] responses（状态码说明）

## 每个参数必须包含
- [ ] description（参数描述）
- [ ] example（示例值）
- [ ] 类型约束（min_length, max_length 等）

## 文档可用性
- [ ] /docs 页面可正常访问
- [ ] /redoc 页面可正常访问
- [ ] 所有接口可在文档中测试
```

**Output:** Working prototype

## Phase 4: Test & Ship (4-8 hours)

### 4.0 测试方案设计 (Test Plan Design)

**在编写测试用例之前，必须先设计测试方案。**

#### 4.0.1 测试方式与方法论

| 测试类型 | 描述 | 快速原型适用 |
|----------|------|--------------|
| 单元测试 (Unit Test) | 测试单个函数/方法的正确性 | ✅ 核心逻辑必须 |
| 集成测试 (Integration Test) | 测试模块间交互 | ✅ API层必须 |
| 功能测试 (Functional Test) | 测试业务功能完整性 | ✅ 必须 |
| 黑盒测试 (Black Box) | 不关心内部实现，只验证输入输出 | ✅ 主要方式 |
| UI自动化测试 (E2E) | 模拟用户操作验证界面 | ⚠️ 核心流程 |
| 性能测试 | 压力、负载测试 | ❌ 不包含 |
| 安全测试 | 渗透、漏洞扫描 | ❌ 不包含 |

#### 4.0.2 测试数据原则

```markdown
# 测试数据原则

1. **独立性原则**
   - 每个测试用例使用独立的测试数据
   - 测试数据在用例执行前创建，执行后清理
   - 不依赖其他用例产生的数据

2. **隔离性原则**
   - 测试环境与生产环境完全隔离
   - 使用独立的测试数据库 (test.db)
   - 每次测试前重置数据库状态

3. **可重复性原则**
   - 测试必须能任意次数重复执行
   - 每次执行结果必须一致
   - 不受执行顺序影响

4. **最小化原则**
   - 只创建测试所需的最少数据
   - 避免复杂的数据依赖关系
   - 测试数据简单明确
```

#### 4.0.3 测试用例独立性要求

**核心原则：每个测试用例必须完全独立，不存在用例间依赖和串联。**

```python
# ✅ 正确示例：独立的测试用例
class TestUserAPI:
    
    def test_create_user(self, db_session):
        """测试创建用户 - 独立用例"""
        # Arrange: 准备测试数据
        user_data = {"phone": "13800001111", "nickname": "测试用户"}
        
        # Act: 执行操作
        response = client.post("/api/users", json=user_data)
        
        # Assert: 验证结果
        assert response.status_code == 201
        assert response.json()["phone"] == "13800001111"
    
    def test_get_user(self, db_session):
        """测试获取用户 - 独立用例，自己创建所需数据"""
        # Arrange: 本用例自己创建测试数据
        user = User(phone="13800002222", nickname="查询测试")
        db_session.add(user)
        db_session.commit()
        
        # Act
        response = client.get(f"/api/users/{user.id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["nickname"] == "查询测试"

# ❌ 错误示例：用例间存在依赖
class TestUserAPIBad:
    created_user_id = None  # 共享状态 - 错误！
    
    def test_create_user(self):
        response = client.post("/api/users", json={...})
        self.created_user_id = response.json()["id"]  # 保存给其他用例用 - 错误！
    
    def test_get_user(self):
        # 依赖上一个用例创建的数据 - 错误！
        response = client.get(f"/api/users/{self.created_user_id}")
```

#### 4.0.4 测试分层策略

```
┌─────────────────────────────────────────────────────────────────┐
│                        测试金字塔                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                         ┌─────────┐                             │
│                         │  E2E    │  ← 少量核心流程              │
│                         │  Tests  │    (UI自动化)                │
│                       ┌─┴─────────┴─┐                           │
│                       │ Integration │  ← API层测试               │
│                       │    Tests    │    (接口测试)              │
│                     ┌─┴─────────────┴─┐                         │
│                     │   Unit Tests    │  ← 大量单元测试          │
│                     │                 │    (函数/方法)           │
│                     └─────────────────┘                         │
│                                                                 │
│  快速原型重点：集成测试 (API) + 功能测试 (核心流程)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.0.5 测试方案模板

```markdown
# 测试方案: [功能名称]

## 1. 测试范围
- 被测功能：[功能描述]
- 测试类型：单元测试 / 集成测试 / 功能测试 / E2E测试

## 2. 测试方法
- [ ] 黑盒测试：验证输入输出
- [ ] 边界值测试：边界条件验证
- [ ] 等价类划分：有效/无效输入

## 3. 测试数据
- 数据来源：测试用例自行创建
- 数据清理：每个用例执行后自动清理
- 隔离方式：独立测试数据库

## 4. 测试环境
- 数据库：SQLite (test.db)
- 后端：本地 FastAPI 测试服务器
- 前端：Jest + React Testing Library

## 5. 通过标准
- 所有测试用例通过
- 代码覆盖率 > 60% (核心逻辑)
- 无阻塞性Bug
```

### 4.1 测试用例设计 (Test Case Design)

**测试用例必须在测试方案确定后设计，每个用例完全独立。**

#### 4.1.1 测试用例设计原则

| 原则 | 描述 |
|------|------|
| 独立性 | 每个用例独立执行，不依赖其他用例 |
| 自包含 | 用例自己准备数据，自己清理数据 |
| 可重复 | 任意次数执行，结果一致 |
| 单一职责 | 一个用例只验证一个场景 |
| 明确断言 | 断言清晰，失败原因明确 |

#### 4.1.2 测试用例模板

```markdown
# 测试用例: TC_[模块]_[编号]

## 基本信息
- 用例ID: TC_USER_001
- 用例名称: 用户注册成功
- 测试类型: 功能测试
- 优先级: P0

## 前置条件
- 测试数据库已初始化
- 手机号 13800001111 未被注册

## 测试步骤
1. 调用注册接口 POST /api/register
2. 传入参数: {"phone": "13800001111", "password": "123456"}

## 预期结果
- 返回状态码 201
- 返回用户ID
- 数据库中存在该用户记录

## 测试数据
- 本用例自行创建，执行后自动清理

## 独立性声明
- 不依赖任何其他用例
- 不为其他用例提供数据
```

#### 4.1.3 各层测试用例示例

**单元测试用例 (Unit Test)**

```python
# tests/unit/test_utils.py
import pytest
from src.utils import hash_password, verify_password

class TestPasswordUtils:
    """密码工具函数单元测试 - 每个用例独立"""
    
    def test_hash_password_returns_hash(self):
        """TC_UNIT_001: 密码哈希返回非空字符串"""
        result = hash_password("123456")
        assert result is not None
        assert len(result) > 0
        assert result != "123456"
    
    def test_verify_password_correct(self):
        """TC_UNIT_002: 正确密码验证通过"""
        hashed = hash_password("123456")
        assert verify_password("123456", hashed) is True
    
    def test_verify_password_incorrect(self):
        """TC_UNIT_003: 错误密码验证失败"""
        hashed = hash_password("123456")
        assert verify_password("wrong", hashed) is False
```

**集成测试用例 (Integration Test / API Test)**

```python
# tests/integration/test_user_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_test_session

client = TestClient(app)

class TestUserAPI:
    """用户API集成测试 - 每个用例独立"""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """每个用例执行前后自动清理数据库"""
        yield
        db_session.rollback()
    
    def test_register_success(self, db_session):
        """TC_API_001: 用户注册成功"""
        # Arrange - 本用例独立准备数据
        user_data = {
            "phone": "13800001111",
            "password": "123456",
            "nickname": "测试用户"
        }
        
        # Act
        response = client.post("/api/register", json=user_data)
        
        # Assert
        assert response.status_code == 201
        assert "id" in response.json()
    
    def test_register_duplicate_phone(self, db_session):
        """TC_API_002: 重复手机号注册失败"""
        # Arrange - 本用例自己创建前置数据
        existing_user = {"phone": "13800002222", "password": "123456", "nickname": "已存在"}
        client.post("/api/register", json=existing_user)
        
        # Act - 再次注册相同手机号
        response = client.post("/api/register", json=existing_user)
        
        # Assert
        assert response.status_code == 400
        assert "已注册" in response.json()["detail"]
    
    def test_login_success(self, db_session):
        """TC_API_003: 用户登录成功"""
        # Arrange - 本用例自己创建测试用户
        user_data = {"phone": "13800003333", "password": "123456", "nickname": "登录测试"}
        client.post("/api/register", json=user_data)
        
        # Act
        response = client.post("/api/login", json={
            "phone": "13800003333",
            "password": "123456"
        })
        
        # Assert
        assert response.status_code == 200
        assert "token" in response.json()
```

**功能测试用例 (Functional Test)**

```python
# tests/functional/test_user_flow.py
class TestUserFunctional:
    """用户功能测试 - 每个用例独立验证完整功能"""
    
    def test_user_can_update_profile(self, db_session):
        """TC_FUNC_001: 用户可以修改个人资料"""
        # Arrange - 创建并登录用户
        user = create_test_user(db_session, phone="13800004444")
        token = login_user(user)
        
        # Act - 修改资料
        response = client.put(
            "/api/user/profile",
            json={"nickname": "新昵称"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["nickname"] == "新昵称"
    
    def test_user_can_change_password(self, db_session):
        """TC_FUNC_002: 用户可以修改密码"""
        # Arrange - 本用例独立创建用户
        user = create_test_user(db_session, phone="13800005555", password="old123")
        token = login_user(user)
        
        # Act
        response = client.put(
            "/api/user/password",
            json={"old_password": "old123", "new_password": "new456"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        # 验证新密码可以登录
        login_response = client.post("/api/login", json={
            "phone": "13800005555",
            "password": "new456"
        })
        assert login_response.status_code == 200
```

**E2E测试用例 (UI自动化)**

```typescript
// tests/e2e/user.spec.ts
import { test, expect } from '@playwright/test';

test.describe('用户流程E2E测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 每个用例前重置测试数据
    await resetTestDatabase();
  });
  
  test('TC_E2E_001: 用户可以完成注册流程', async ({ page }) => {
    // Arrange
    await page.goto('/register');
    
    // Act
    await page.fill('[data-testid="phone"]', '13800006666');
    await page.fill('[data-testid="password"]', '123456');
    await page.fill('[data-testid="nickname"]', 'E2E测试用户');
    await page.click('[data-testid="submit"]');
    
    // Assert
    await expect(page).toHaveURL('/home');
    await expect(page.locator('[data-testid="welcome"]')).toContainText('E2E测试用户');
  });
  
  test('TC_E2E_002: 用户可以完成登录流程', async ({ page }) => {
    // Arrange - 本用例独立创建测试用户
    await createTestUser({ phone: '13800007777', password: '123456' });
    await page.goto('/login');
    
    // Act
    await page.fill('[data-testid="phone"]', '13800007777');
    await page.fill('[data-testid="password"]', '123456');
    await page.click('[data-testid="submit"]');
    
    // Assert
    await expect(page).toHaveURL('/home');
  });
});
```

### 4.2 Functional Testing (Strict!)

Even for rapid prototypes, functional correctness is mandatory:

```markdown
# 必须通过的测试检查项

## Client Side Tests
- [ ] User can complete main task end-to-end
- [ ] All buttons/links work correctly
- [ ] Form submissions work
- [ ] Data saves and loads correctly
- [ ] Error states show appropriate messages

## Admin Side Tests
- [ ] Admin can view data list
- [ ] Admin can create/edit/delete records
- [ ] Data changes reflect in client side
- [ ] Basic permission check works

## Edge Cases
- [ ] Empty states handled
- [ ] Invalid input rejected
- [ ] Network errors handled gracefully

## Cross-Module Tests
- [ ] Client and Admin share data correctly
- [ ] Admin changes visible to users

## 用例独立性检查
- [ ] 所有测试用例可独立执行
- [ ] 用例间无数据依赖
- [ ] 用例执行顺序不影响结果
```

### 4.3 不包含的测试
- Performance/Load testing ❌
- Security penetration testing ❌
- Accessibility audit ❌
- Cross-browser exhaustive testing ❌

### 4.4 Local Run (本地直接运行)

```bash
# Backend (Python) - 直接本地运行
cd client/backend && uv run uvicorn src.main:app --reload --port 8000
cd admin/backend && uv run uvicorn src.main:app --reload --port 8001

# Frontend - 开发模式
cd client/frontend && npm run dev -- --port 3000
cd admin/frontend && npm run dev -- --port 3001

# Frontend - 生产构建后本地预览
cd client/frontend && npm run build && npx serve dist -p 3000
cd admin/frontend && npm run build && npx serve dist -p 3001
```

### 4.5 发布前必须检查项

- [ ] 核心功能必须正常工作
- [ ] 必须无阻塞性Bug
- [ ] 必须有基本错误处理
- [ ] 必须能收集用户反馈

**Output:** Deployed prototype ready for user testing

## Iteration Cycle

After initial ship, iterate quickly:

```
Feedback → Fix/Improve → Test → Ship → Repeat
  (1hr)      (2-4hrs)    (1hr)  (30min)
```

## Comparison: Rapid vs Enterprise Workflow

| Aspect | Rapid Prototype | Enterprise (fullstack-project-workflow) |
|--------|-----------------|----------------------------------------|
| Documentation | 1-page brief | Full PRD, SRS, Tech Design |
| UI Design | MCP Pencil (hours) | Figma + Review (days) |
| Architecture | Minimal, flat | Layered OOP, abstractions |
| Code Quality | Working > Perfect | Clean, maintainable |
| Testing | Functional only | Full suite + Performance |
| Security | Basic only | Full audit |
| Timeline | Days | Weeks/Months |
| Team Size | 1-2 people | Multiple teams |

## When to Graduate to Enterprise Workflow

Transition to `fullstack-project-workflow` when:
- Prototype is validated and needs production quality
- User base is growing
- Security/Performance become critical
- Team is expanding
- Long-term maintenance is needed

## Quick Reference Commands

```bash
# 初始化新项目
mkdir my-project && cd my-project

# 初始化前端 (Vite + React + Tailwind)
npm create vite@latest client/frontend -- --template react-ts
cd client/frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @headlessui/react @heroicons/react axios

# 初始化后端 (Python + FastAPI + SQLite)
cd ../..
mkdir -p client/backend/src
cd client/backend
uv init
uv add fastapi uvicorn sqlmodel aiosqlite python-multipart
touch src/__init__.py src/main.py src/models.py src/routes.py src/database.py

# 运行后端
uv run uvicorn src.main:app --reload --port 8000

# 运行前端
cd ../frontend && npm run dev

# 使用 MCP Pencil 生成UI设计（保存到 docs/ui/）
mkdir -p docs/ui
pencil create --name "my-project" --output "docs/ui/my-project.pen"
pencil generate --file "docs/ui/my-project.pen" --screens "login,dashboard,settings" --style "minimal modern"

# 读取设计稿进行后续修改
pencil read --file "docs/ui/my-project.pen"

# 使用 frontend-design skill 优化
/frontend-design
"优化当前页面，使用Tailwind实现简约现代风格"

# 快速测试
pytest client/backend/tests/
npm run test --prefix client/frontend
```

## UI 优化工作流

```
1. MCP Pencil 创建设计稿 (docs/ui/[project].pen)
   ↓
2. MCP Pencil 生成初始设计
   ↓
3. frontend-design skill 优化美观度
   ↓
4. MCP Pencil 更新设计稿
   ↓
5. 实现代码 (React + Tailwind)
   ↓
6. 视觉微调 (间距、颜色、动效)
   ↓
7. 响应式适配检查
```

## Tailwind 简约组件示例

```tsx
// 简约按钮
<button className="px-4 py-2 bg-blue-500 text-white rounded-lg 
  hover:bg-blue-600 transition-colors shadow-sm">
  提交
</button>

// 简约卡片
<div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
  <h3 className="text-lg font-medium text-gray-900">标题</h3>
  <p className="text-gray-500">描述内容</p>
</div>

// 简约输入框
<input className="w-full px-4 py-2 border border-gray-200 rounded-lg
  focus:ring-2 focus:ring-blue-500 focus:border-transparent
  placeholder-gray-400" />
```

## SQLite 使用注意

```python
# 共享数据库路径配置
import os
DB_PATH = os.environ.get("DB_PATH", "../shared/db/data.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Client和Admin后端共享同一个SQLite文件
# 注意：SQLite不支持高并发写入，适合原型验证
```

## Related Skills

- `frontend-design` - Anthropic官方skill，优化UI美观度，避免AI通用丑陋风格
- `autoloop` - 自动化循环开发插件，实现24/7持续编程
- `prd-template` - Use simplified version for brief
- `dev-task-split` - Use for breaking down implementation
- `fullstack-project-workflow` - Graduate to this for production

## Autonomous Mode Best Practices

### 1. 任务拆分
```
大任务 → 拆分为小任务 → 每个小任务独立循环
```

### 2. 验证标准明确
```markdown
# Good ✅
- All tests passing
- API returns 200 for /api/users
- Login page renders without console errors

# Bad ❌
- Code looks good
- Feature is complete
- Everything works
```

### 3. 持续开发直到完成
```bash
# 第一轮：基础结构
/autoloop:autoloop "Setup project structure and database models"

# 第二轮：后端API
/autoloop:autoloop "Implement all REST APIs"

# 第三轮：前端页面
/autoloop:autoloop "Build all frontend pages"

# 第四轮：集成完善
/autoloop:autoloop "Fix all issues until everything works perfectly"
```

### 4. 监控进度
```bash
# 实时查看日志
tail -f loop/loop.log

# 查看 Git 提交历史
git log --oneline -20

# 检查测试状态
pytest --tb=short
npm test
```
