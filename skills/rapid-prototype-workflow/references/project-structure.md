# Project Structure 详细说明

## 三端架构 (Client + Admin + Website)

```
./
├── docs/
│   ├── prd/                           # 产品需求文档（必须）
│   │   ├── 01-project-brief.md
│   │   ├── 02-feature-architecture.md
│   │   ├── 03-role-definition.md
│   │   ├── 04-module-design.md
│   │   ├── 05-page-list.md
│   │   ├── 06-page-navigation.md
│   │   ├── 07-page-interaction.md
│   │   └── 08-visual-style.md
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
├── website/                           # 项目官网（纯静态 HTML）
│   ├── index.html                     # 首页
│   ├── features.html                  # 功能介绍
│   ├── pricing.html                   # 定价页面
│   ├── about.html                     # 关于我们
│   ├── contact.html                   # 联系我们
│   ├── 404.html                       # 404页面
│   ├── css/                           # 样式文件
│   ├── js/                            # 脚本文件
│   └── images/                        # 图片资源
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

---

## Module Responsibilities

| Module | Purpose | Priority |
|--------|---------|----------|
| client-frontend | 用户界面、核心交互 | P0 - 必须 |
| client-backend | 用户API、业务逻辑 | P0 - 必须 |
| admin-frontend | 数据管理、配置界面 | P0 - 必须 |
| admin-backend | 管理API、数据操作 | P0 - 必须 |
| website | 项目官网、产品介绍（静态） | P1 - 推荐 |

**Note:** Admin模块必须实现，与Client侧同等重要。Website为静态官网，用于产品展示和推广。

---

## Website (官网) 模块说明

> ⚠️ **Website 必须先用 MCP Pencil 完成 UI 设计稿，再实现静态 HTML。禁止跳过设计稿直接写代码。**

官网是纯静态 HTML 页面，用于：
- 产品介绍和功能展示
- 下载/使用引导
- 团队/公司介绍
- 联系方式和支持

**技术选型：**
- 纯静态 HTML/CSS/JS，无需构建工具
- 使用 Tailwind CSS CDN 快速样式开发
- **必须使用 `frontend-design` skill 进行 Review 和优化**
- 可部署到 GitHub Pages / Vercel / Netlify

**设计稿要求：**
- Website UI 设计稿与 Client/Admin 一起存放在 `docs/ui/[project].pen`
- 必须覆盖：Landing、功能、定价、关于、联系、页头、页脚、404

**本地预览：**
```bash
cd website
python -m http.server 4000
# 或
npx serve . -p 4000
```

---

## Standard Modules (基础系统模块)

### Client Side (C侧) 基础模块

| 模块 | 功能 |
|------|------|
| 个人中心 | 基本信息、修改密码、退出登录 |
| 消息中心 | 消息列表、未读标记 |
| 系统设置 | 关于我们、意见反馈 |

### Admin Side (管理侧) 基础模块

| 模块 | 功能 |
|------|------|
| 系统配置 | 基础配置、参数配置 |
| 用户管理 | 用户列表、用户状态 |
| 管理员管理 | 管理员列表、重置密码 |

### Website (官网) 标准页面

| 页面 | 功能 |
|------|------|
| 首页 (Landing) | 产品核心价值、CTA按钮 |
| 功能介绍 | 产品功能详细说明 |
| 定价页面 | 价格方案（如有） |
| 关于我们 | 团队/公司介绍 |
| 联系我们 | 联系方式、反馈表单 |
| 下载/开始使用 | 引导用户使用产品 |

---

## Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | React + Vite + Tailwind CSS | 快速构建，热更新，美观样式 |
| Backend | Python + FastAPI | 轻量、快速开发 |
| Database | SQLite | 零配置，单文件，便携 |
| Package Manager | uv | 极速Python依赖管理 |
| ORM | SQLModel | FastAPI原生支持，简洁 |
| UI Design | MCP Pencil + frontend-design | 生成设计 + 优化美观度 |
| Website | 纯静态 HTML + Tailwind CDN | 无需构建，快速部署 |

### Why These Choices?

- **SQLite**: 无需安装数据库服务，单文件存储，开发即生产
- **uv**: 比pip快10-100倍，现代Python包管理
- **FastAPI**: 自动API文档，类型安全，异步支持
- **SQLModel**: 结合SQLAlchemy和Pydantic，代码最少
- **Tailwind CSS**: 原子化CSS，快速构建美观界面
- **frontend-design skill**: 避免AI生成的通用丑陋界面，产出专业级UI
