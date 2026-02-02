# 快速原型开发规范

> 适用于 Codex、Claude Code、Trae、Kiro 等 AI 编程助手

本规范定义了使用 AI 编程助手进行快速原型开发的标准流程和要求。

---

## 适用场景

**必须使用本规范：**
- 构建 MVP 或概念验证项目
- 快速验证商业想法
- 需要快速反馈的实验性功能
- 上市时间紧迫的项目

**禁止使用本规范：**
- 构建生产级系统
- 安全/性能是关键要求
- 需要长期可维护性
- 大型团队协作项目

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React + Vite + Tailwind CSS | 快速构建，热更新，美观样式 |
| 后端 | Python + FastAPI | 轻量、快速开发 |
| 数据库 | SQLite | 零配置，单文件，便携 |
| 包管理 | uv | 极速Python依赖管理 |
| ORM | SQLModel | FastAPI原生支持，简洁 |

---

## 工程结构

```
project/
├── docs/
│   ├── prd/                           # 产品需求文档（必须）
│   │   ├── 01-project-brief.md        # 项目简介
│   │   ├── 02-feature-architecture.md # 功能架构图
│   │   ├── 03-role-definition.md      # 系统角色定义
│   │   ├── 04-module-design.md        # 功能模块划分
│   │   ├── 05-page-list.md            # 交互页面清单
│   │   ├── 06-page-navigation.md      # 页面跳转关系
│   │   ├── 07-page-interaction.md     # 页面交互操作
│   │   └── 08-visual-style.md         # 视觉风格规范
│   ├── ui/
│   │   └── [project-name].pen         # UI 设计稿（必须）
│   ├── api/
│   │   └── api-spec.md                # API 接口文档（必须）
│   └── test/
│       ├── test-plan.md               # 测试方案（必须）
│       └── test-cases.md              # 测试用例（必须）
├── client/
│   ├── frontend/                      # 用户前端
│   └── backend/
│       └── src/                       # 后端代码必须在 src/ 包下
├── admin/
│   ├── frontend/                      # 管理后台前端
│   └── backend/
│       └── src/                       # 后端代码必须在 src/ 包下
├── shared/
│   └── db/
│       └── data.db                    # 共享SQLite数据库
├── logs/                              # 日志目录
├── start.sh                           # 一键启动脚本 (Mac/Linux)
├── start.bat                          # 一键启动脚本 (Windows)
├── stop.sh                            # 停止脚本 (Mac/Linux)
├── stop.bat                           # 停止脚本 (Windows)
└── README.md
```

### 模块职责

| 模块 | 职责 | 优先级 |
|------|------|--------|
| client-frontend | 用户界面、核心交互 | P0 - 必须 |
| client-backend | 用户API、业务逻辑 | P0 - 必须 |
| admin-frontend | 数据管理、配置界面 | P0 - 必须 |
| admin-backend | 管理API、数据操作 | P0 - 必须 |

**Note:** Admin模块必须实现，与Client侧同等重要。

---

## 基础系统模块

### Client 侧 (C侧)

| 模块 | 功能 |
|------|------|
| 个人中心 | 基本信息、修改密码、退出登录 |
| 消息中心 | 消息列表、未读标记 |
| 系统设置 | 关于我们、意见反馈 |

### Admin 侧 (管理侧)

| 模块 | 功能 |
|------|------|
| 系统配置 | 基础配置、参数配置 |
| 用户管理 | 用户列表、用户状态 |
| 管理员管理 | 管理员列表、重置密码 |

---

## 开发流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. 需求    │ →  │  2. UI      │ →  │  3. 实现    │ →  │  4. 测试    │
│  分析      │    │  设计       │    │  开发       │    │  发布       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
    (30min)          (2-4hrs)         (1-2 days)         (4-8hrs)
```

---

## Phase 1: 需求分析 (30 minutes)

### 1.1 项目简介

必须回答以下问题：
- 解决什么问题？
- 目标用户是谁？
- 核心功能是什么？（最多5个）
- 成功标准是什么？

### 1.2 功能架构图

PRD 必须包含完整的功能架构图：
- 必须列出所有功能模块
- 每个模块必须细化到具体功能点
- 区分 C侧 和 Admin侧
- 标注功能优先级 (P0/P1/P2)

### 1.3 需求实现方案 (必须)

**必须完成以下设计工作：**

1. **系统角色定义** - 明确所有角色及权限范围
2. **功能模块划分** - 按模块划分功能，包含描述、角色、优先级
3. **交互页面清单** - 列出所有页面，包含编号、名称、入口、角色
4. **页面跳转关系** - 定义页面间跳转关系和流程图
5. **页面交互操作** - 定义每个页面的操作和组件
6. **视觉风格差异** - 区分 Client 和 Admin 的视觉风格

### 1.4 输出文档清单

| 序号 | 文档名称 | 路径 |
|------|----------|------|
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

## Phase 2: UI 设计 (2-4 hours)

### 2.1 全生命周期覆盖要求

**UI 设计稿必须覆盖用户完整使用旅程：**

- 入口阶段：启动页、引导页、登录、注册、忘记密码
- 核心功能阶段：首页、列表、详情、搜索、筛选
- 交互操作阶段：表单、确认页、结果页
- 个人中心阶段：个人中心、编辑、密码、消息、设置
- **异常状态（必须）**：空状态、加载状态、错误状态、404、无权限
- **弹窗/浮层（必须）**：确认弹窗、提示、操作菜单、Toast

### 2.2 设计稿规范

- 文件格式：`.pen`
- 文件命名：`[工程名称].pen`
- 存储路径：`docs/ui/[工程名称].pen`
- 所有 UI 设计稿必须通过设计工具读取和修改

### 2.3 UI 5轮迭代审查 (必须)

| Round | 角色 | Focus |
|-------|------|-------|
| 1 | 商业分析师 | 价值主张、转化路径 |
| 2 | 领域产品经理 | 业务流程、行业实践 |
| 3 | 资深产品经理 | 用户习惯、交互体验 |
| 4 | UED设计专家 | 视觉层次、设计一致性 |
| 5 | 小白用户 | 易用性、直观性 |

### 2.4 设计交付清单

**Client Side - 必须完整覆盖：**

| 阶段 | 页面 |
|------|------|
| 入口 | 启动页、引导页、登录、注册、忘记密码 |
| 首页 | 首页(有数据)、首页(空状态)、首页(加载中) |
| 核心 | 列表页、详情页、搜索页、筛选页 |
| 操作 | 表单页、确认页、结果页(成功/失败) |
| 个人 | 个人中心、编辑资料、修改密码 |
| 消息 | 消息列表、消息详情、空消息 |
| 设置 | 系统设置、关于我们、意见反馈 |
| 异常 | 空状态、加载中、网络错误、404 |
| 组件 | 弹窗、Toast、ActionSheet |

**Admin Side - 必须完整覆盖：**

| 阶段 | 页面 |
|------|------|
| 入口 | 登录页 |
| 首页 | Dashboard(数据概览) |
| 列表 | 数据列表(有数据/空/加载中) |
| 表单 | 新增表单、编辑表单 |
| 详情 | 数据详情页 |
| 配置 | 系统配置页 |
| 组件 | 确认弹窗、操作反馈 |

### 2.5 UI Style Guide

```css
/* 简约配色 */
--primary: #3b82f6;      /* 蓝色主色 */
--secondary: #64748b;    /* 灰色辅助 */
--background: #f8fafc;   /* 浅灰背景 */
--surface: #ffffff;      /* 白色卡片 */
--text-primary: #1e293b; /* 深色文字 */
--text-secondary: #64748b;/* 浅色文字 */

/* 间距 */
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */

/* 圆角 */
--radius-sm: 0.375rem;   /* 6px */
--radius-md: 0.5rem;     /* 8px */
--radius-lg: 0.75rem;    /* 12px */
```

---

## Phase 3: 实现开发 (1-2 days)

### 3.1 实现顺序

1. Setup project (30min) - 初始化 client + admin 结构
2. Client Side First (1 day) - Frontend + Backend
3. Admin Side (0.5-1 day) - Frontend + Backend
4. Integration (2-4hrs) - 连接所有模块

### 3.2 编码规范

**必须遵守：**
- 后端代码必须放在 `src/` 包下
- 所有 Python 导入必须使用绝对路径（如 `from src.database import`）
- 使用 uv 作为包管理器
- 使用 SQLite + SQLModel
- 必须使用 Tailwind CSS 构建简约美观的界面
- 必须使用现成组件库 (Headless UI, Radix UI)
- 必须保持代码简洁，避免过度封装
- **界面实现必须严格按照 UI 设计稿进行还原**
- **实现过程中如发现 UI 设计稿缺失内容，必须先补全设计稿，再执行界面实现**

**禁止事项：**
- 禁止使用过于花哨的动画
- 禁止堆砌太多颜色
- 禁止忽视移动端适配
- 禁止使用默认的丑陋样式
- 禁止过度设计架构
- **禁止脱离设计稿自行发挥界面样式**
- **禁止在设计稿缺失时直接实现界面**

### 3.3 后端初始化

```bash
# 初始化后端
cd client/backend
uv init
uv add fastapi uvicorn sqlmodel aiosqlite python-multipart

# 创建 src 包
mkdir -p src
touch src/__init__.py src/main.py src/models.py src/routes.py src/database.py

# 运行
uv run uvicorn src.main:app --reload --port 8000
```

### 3.4 一键启动脚本 (必须)

项目根目录必须包含跨平台的一键启动脚本：
- `start.sh` / `start.bat` - 启动脚本
- `stop.sh` / `stop.bat` - 停止脚本
- 端口变量在脚本顶部，易于修改
- 前端从环境变量读取后端地址

### 3.5 API 文档生成 (必须)

```python
app = FastAPI(
    title="[项目名称] API",
    description="[项目描述]",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc
    openapi_url="/openapi.json"
)
```

**每个接口必须包含：**
- summary（接口标题）
- description（接口描述）
- tags（标签分组）
- response_model（响应模型）
- responses（状态码说明）

**每个参数必须包含：**
- description（参数描述）
- example（示例值）

---

## Phase 4: 测试发布 (4-8 hours)

### 4.1 测试方案设计 (必须)

| 测试类型 | 适用性 |
|----------|--------|
| 单元测试 | ✅ 核心逻辑必须 |
| 集成测试 | ✅ API层必须 |
| 功能测试 | ✅ 必须 |
| 黑盒测试 | ✅ 主要方式 |
| E2E测试 | ⚠️ 核心流程 |
| 性能测试 | ❌ 不包含 |
| 安全测试 | ❌ 不包含 |

### 4.2 测试用例独立性 (必须)

**核心原则：每个测试用例必须完全独立**

- 每个用例使用独立的测试数据
- 测试数据在用例执行前创建，执行后清理
- 不依赖其他用例产生的数据
- 测试必须能任意次数重复执行

### 4.3 功能测试清单

```markdown
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

## Edge Cases
- [ ] Empty states handled
- [ ] Invalid input rejected
- [ ] Network errors handled gracefully

## UI 还原验收测试 (必须)
- [ ] 页面布局与设计稿一致
- [ ] 颜色、字体、间距与设计稿一致
- [ ] 组件样式与设计稿一致
- [ ] 响应式布局与设计稿一致
- [ ] 交互动效与设计稿一致
- [ ] 空状态/加载状态/错误状态与设计稿一致

## 用例独立性检查
- [ ] 所有测试用例可独立执行
- [ ] 用例间无数据依赖
- [ ] 用例执行顺序不影响结果
```

### 4.4 发布前检查项

- [ ] 核心功能必须正常工作
- [ ] 必须无阻塞性Bug
- [ ] 必须有基本错误处理
- [ ] 必须能收集用户反馈

---

## 迭代周期

发布后快速迭代：

```
Feedback → Fix/Improve → Test → Ship → Repeat
  (1hr)      (2-4hrs)    (1hr)  (30min)
```

---

## UI 优化工作流

```
1. 创建设计稿
   ↓
2. 生成初始设计
   ↓
3. 优化美观度
   ↓
4. 更新设计稿
   ↓
5. 实现代码 (React + Tailwind)
   ↓
6. 视觉微调 (间距、颜色、动效)
   ↓
7. 响应式适配检查
```

---

## 快速参考命令

```bash
# 初始化新项目
mkdir my-project && cd my-project

# 初始化前端
npm create vite@latest client/frontend -- --template react-ts
cd client/frontend && npm install -D tailwindcss postcss autoprefixer

# 初始化后端
mkdir -p client/backend/src && cd client/backend
uv init && uv add fastapi uvicorn sqlmodel aiosqlite

# 一键启动
./start.sh
```

---

## 何时升级到企业级工作流

当以下情况出现时，应升级到企业级开发流程：
- 原型已验证，需要生产级质量
- 用户量增长
- 安全/性能成为关键要求
- 团队扩展
