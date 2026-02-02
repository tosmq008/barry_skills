# Workflow Quick Reference Card

快速原型开发工作流速查卡 - 一页纸概览

---

## 4 阶段总览

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Phase 1    │ →  │   Phase 2    │ →  │   Phase 3    │ →  │   Phase 4    │
│  Idea (30m)  │    │  UI (2-4h)   │    │  Code (1-2d) │    │  Ship (4-8h) │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
     ↓                    ↓                    ↓                    ↓
  8个PRD文档          5轮UI审查           三端代码实现          测试+发布
```

---

## Phase 1: Idea Capture (30min)

**输出：** 8 个 PRD 文档 → `docs/prd/`

| # | 文档 | 核心内容 |
|---|------|----------|
| 1 | 项目简介 | 问题、用户、核心功能 |
| 2 | 功能架构图 | Client + Admin + Website 三端 |
| 3 | 系统角色 | 角色定义 + 权限矩阵 |
| 4 | 模块划分 | 功能点 + 优先级 |
| 5 | 页面清单 | 页面编号 + 入口 |
| 6 | 跳转关系 | 页面间跳转流程 |
| 7 | 交互操作 | 每页操作 + 组件 |
| 8 | 视觉风格 | Client vs Admin 差异 |

📄 **详细模板:** `prd-templates.md`

---

## Phase 2: UI Design (2-4hrs)

**输出：** UI 设计稿 → `docs/ui/[project].pen`

**5 轮审查：**
```
Round 1 (商业分析师) → Round 2 (领域PM) → Round 3 (资深PM) → Round 4 (UED) → Round 5 (小白用户)
```

**必须覆盖页面：**
- **Client:** 入口流程 + 核心功能 + 个人中心 + 异常状态 + 弹窗组件
- **Admin:** 登录 + Dashboard + 列表 + 表单 + 详情 + 配置
- **Website:** Landing + 功能 + 定价 + 关于 + 联系 + 404 (**也必须先设计稿**)

📄 **详细清单:** `ui-review-templates.md`

---

## Phase 3: Implementation (1-2 days)

**执行顺序：**
```
Setup (30m) → Client (1d) → Admin (0.5d) → Website (2-4h) → Integration (2-4h)
```

**技术栈：**
| 层 | 技术 |
|----|------|
| Frontend | React + Vite + Tailwind |
| Backend | Python + FastAPI + SQLModel |
| Database | SQLite (共享) |
| Website | 纯静态 HTML + Tailwind CDN |

**端口分配：**
| 服务 | 端口 |
|------|------|
| Client Frontend | 3000 |
| Client Backend | 8000 |
| Admin Frontend | 3001 |
| Admin Backend | 8001 |
| Website | 4000 |

**核心规则：**
- ✅ 后端代码放 `src/` 包下
- ✅ 界面严格按设计稿还原
- ✅ **Website 也必须先完成 UI 设计稿，再写 HTML**
- ✅ Website 必须用 `frontend-design` skill 优化
- ❌ 禁止脱离设计稿自行发挥
- ❌ 禁止跳过设计稿直接写代码

📄 **代码模板:** `quick-templates.md`
📄 **启动脚本:** `startup-scripts.md`

---

## Phase 4: Test & Ship (4-8hrs)

**测试范围：**
| 类型 | 必须？ |
|------|--------|
| 单元测试 | ✅ 核心逻辑 |
| 集成测试 | ✅ API 层 |
| 功能测试 | ✅ 必须 |
| E2E 测试 | ⚠️ 核心流程 |
| 性能/安全 | ❌ 不包含 |

**发布检查：**
- [ ] 核心功能正常
- [ ] 无阻塞性 Bug
- [ ] UI 与设计稿一致
- [ ] 基本错误处理

📄 **测试模板:** `test-templates.md`

---

## 快速命令

```bash
# Client Backend
cd client/backend && uv init && uv add fastapi uvicorn sqlmodel
uv run uvicorn src.main:app --reload --port 8000

# Client Frontend
npm create vite@latest client/frontend -- --template react-ts
cd client/frontend && npm run dev -- --port 3000

# Admin (同上，端口 8001/3001)

# Website
cd website && python -m http.server 4000
```

---

## 核心原则

| 原则 | 说明 |
|------|------|
| UI-First | 先设计 UI，再写代码 |
| Design-Driven | 界面必须还原设计稿 |
| Client First | 先 Client，后 Admin |
| Speed > Perfect | 快速交付，快速迭代 |
| frontend-design | Website 必须用此 skill 优化 |
