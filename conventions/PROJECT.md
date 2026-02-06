# PROJECT.md - 项目结构约定

> 定义快速原型开发的标准项目结构

---

## 三端架构总览

```
./
├── docs/                              # 文档目录
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
├── client/                            # 用户端
│   ├── frontend/                      # 用户前端 (React + Vite)
│   │   ├── src/
│   │   │   ├── components/            # 组件
│   │   │   ├── pages/                 # 页面
│   │   │   ├── hooks/                 # 自定义 Hooks
│   │   │   ├── services/              # API 服务
│   │   │   ├── utils/                 # 工具函数
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── backend/                       # 用户后端 (FastAPI)
│       ├── src/                       # 后端代码必须在 src/ 包下
│       │   ├── __init__.py
│       │   ├── main.py                # 入口文件
│       │   ├── models.py              # 数据模型
│       │   ├── routes.py              # 路由定义
│       │   ├── database.py            # 数据库配置
│       │   └── schemas.py             # Pydantic 模型
│       ├── pyproject.toml
│       └── uv.lock
├── admin/                             # 管理端
│   ├── frontend/                      # 管理前端
│   │   └── (同 client/frontend 结构)
│   └── backend/                       # 管理后端
│       └── src/                       # 后端代码必须在 src/ 包下
│           └── (同 client/backend/src 结构)
├── website/                           # 项目官网（纯静态 HTML）
│   ├── index.html                     # 首页 (Landing)
│   ├── features.html                  # 功能介绍
│   ├── pricing.html                   # 定价页面
│   ├── about.html                     # 关于我们
│   ├── contact.html                   # 联系我们
│   ├── 404.html                       # 404 页面
│   ├── css/                           # 样式文件
│   │   └── style.css
│   ├── js/                            # 脚本文件
│   │   └── main.js
│   └── images/                        # 图片资源
├── shared/                            # 共享资源
│   └── db/
│       └── data.db                    # 共享 SQLite 数据库
├── logs/                              # 日志目录
├── .dev-state/                        # 开发状态（自动生成）
│   ├── state.json                     # 主状态文件
│   ├── current-phase.txt              # 当前阶段
│   ├── current-task.txt               # 当前任务
│   ├── completed-tasks.txt            # 已完成任务
│   ├── blocked-tasks.txt              # 阻塞任务
│   └── dev-log.txt                    # 开发日志
├── start.sh                           # 一键启动脚本 (Mac/Linux)
├── start.bat                          # 一键启动脚本 (Windows)
├── stop.sh                            # 停止脚本 (Mac/Linux)
├── stop.bat                           # 停止脚本 (Windows)
└── README.md                          # 项目说明
```

---

## 模块职责

| 模块 | 职责 | 优先级 |
|------|------|--------|
| client-frontend | 用户界面、核心交互 | P0 - 必须 |
| client-backend | 用户 API、业务逻辑 | P0 - 必须 |
| admin-frontend | 数据管理、配置界面 | P0 - 必须 |
| admin-backend | 管理 API、数据操作 | P0 - 必须 |
| website | 项目官网、产品介绍（静态） | P1 - 推荐 |

**Note:** Admin 模块必须实现，与 Client 侧同等重要。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Frontend | React + Vite + Tailwind CSS | 快速构建，热更新，美观样式 |
| Backend | Python + FastAPI | 轻量、快速开发 |
| Database | SQLite | 零配置，单文件，便携 |
| Package Manager | uv | 极速 Python 依赖管理 |
| ORM | SQLModel | FastAPI 原生支持，简洁 |
| UI Design | MCP Pencil + frontend-design | 生成设计 + 优化美观度 |
| Website | 纯静态 HTML + Tailwind CDN | 无需构建，快速部署 |

---

## 端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| Client Frontend | 3000 | 用户前端 |
| Client Backend | 8000 | 用户 API |
| Admin Frontend | 3001 | 管理前端 |
| Admin Backend | 8001 | 管理 API |
| Website | 4000 | 官网静态页面 |

---

## 基础系统模块

### Client Side (C侧)

| 模块 | 功能 |
|------|------|
| 个人中心 | 基本信息、修改密码、退出登录 |
| 消息中心 | 消息列表、未读标记 |
| 系统设置 | 关于我们、意见反馈 |

### Admin Side (管理侧)

| 模块 | 功能 |
|------|------|
| 系统配置 | 基础配置、参数配置 |
| 用户管理 | 用户列表、用户状态 |
| 管理员管理 | 管理员列表、重置密码 |

### Website (官网)

| 页面 | 功能 |
|------|------|
| 首页 (Landing) | 产品核心价值、CTA 按钮 |
| 功能介绍 | 产品功能详细说明 |
| 定价页面 | 价格方案（如有） |
| 关于我们 | 团队/公司介绍 |
| 联系我们 | 联系方式、反馈表单 |
| 下载/开始使用 | 引导用户使用产品 |

---

## 快速初始化命令

### Client Backend

```bash
cd client/backend
uv init
uv add fastapi uvicorn sqlmodel aiosqlite python-multipart
mkdir -p src
touch src/__init__.py src/main.py src/models.py src/routes.py src/database.py
uv run uvicorn src.main:app --reload --port 8000
```

### Client Frontend

```bash
npm create vite@latest client/frontend -- --template react-ts
cd client/frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm run dev -- --port 3000
```

### Admin (同上，端口 8001/3001)

### Website

```bash
cd website
python -m http.server 4000
# 或
npx serve . -p 4000
```

---

## 启动脚本模板

### start.sh (Mac/Linux)

```bash
#!/bin/bash

# 端口配置
CLIENT_FRONTEND_PORT=3000
CLIENT_BACKEND_PORT=8000
ADMIN_FRONTEND_PORT=3001
ADMIN_BACKEND_PORT=8001
WEBSITE_PORT=4000

# 启动 Client Backend
cd client/backend && uv run uvicorn src.main:app --reload --port $CLIENT_BACKEND_PORT &

# 启动 Client Frontend
cd client/frontend && npm run dev -- --port $CLIENT_FRONTEND_PORT &

# 启动 Admin Backend
cd admin/backend && uv run uvicorn src.main:app --reload --port $ADMIN_BACKEND_PORT &

# 启动 Admin Frontend
cd admin/frontend && npm run dev -- --port $ADMIN_FRONTEND_PORT &

# 启动 Website
cd website && python -m http.server $WEBSITE_PORT &

echo "All services started!"
echo "Client: http://localhost:$CLIENT_FRONTEND_PORT"
echo "Admin: http://localhost:$ADMIN_FRONTEND_PORT"
echo "Website: http://localhost:$WEBSITE_PORT"
echo "API Docs: http://localhost:$CLIENT_BACKEND_PORT/docs"
```

### stop.sh (Mac/Linux)

```bash
#!/bin/bash

# 停止所有服务
pkill -f "uvicorn src.main:app"
pkill -f "vite"
pkill -f "http.server"

echo "All services stopped!"
```

---

## 数据库配置

### 共享 SQLite 数据库

```python
# client/backend/src/database.py
from sqlmodel import SQLModel, create_engine, Session
import os

# 使用共享数据库
DB_PATH = os.path.join(os.path.dirname(__file__), "../../../shared/db/data.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

---

## 相关文档

- [CLAUDE.md](./CLAUDE.md) - AI 编程助手核心约定
- [AGENTS.md](./AGENTS.md) - 多 Agent 协作约定
- [WORKFLOW.md](./WORKFLOW.md) - 开发工作流约定
- [CODING.md](./CODING.md) - 编码规范约定
