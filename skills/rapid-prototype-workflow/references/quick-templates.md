# Quick Templates for Rapid Prototyping

## Technology Stack

| Component | Choice | Install |
|-----------|--------|---------|
| Frontend | React + Vite | `npm create vite@latest` |
| Backend | Python + FastAPI | `uv add fastapi uvicorn` |
| Database | SQLite | 内置，无需安装 |
| ORM | SQLModel | `uv add sqlmodel` |
| Package Manager | uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

## One-Page Project Brief Template

```markdown
# Project Brief: [项目名称]

**Date:** [日期]
**Owner:** [负责人]
**Target:** [目标完成日期]

## 问题
[用1-2句话描述要解决的问题]

## 用户
[目标用户是谁？]

## 核心功能
- [ ] 功能1
- [ ] 功能2
- [ ] 功能3
(最多5个)

## 成功标准
- [可衡量的结果1]
- [可衡量的结果2]

## 不做什么
- [明确排除的功能]
```

## MCP Pencil Design Prompts

### 生成主界面

```
Generate a modern [app type] interface with:
- Main dashboard showing [key metrics]
- Navigation for [main sections]
- Style: [minimal/corporate/playful]
- Colors: [primary color preference]
```

### 生成表单页面

```
Generate a form page for [purpose] with:
- Fields: [list fields]
- Validation indicators
- Submit and cancel buttons
- Mobile responsive
```

### 生成列表页面

```
Generate a data list page showing:
- Items with [key attributes]
- Search and filter options
- Pagination
- Action buttons per item
```

### 生成资源素材

```
Generate icon set for [app type]:
- Navigation icons
- Action icons
- Status icons
- Style: [outline/filled/duotone]
- Size: 24px base
```

## Minimal API Contract

```yaml
# API: [Feature Name]

# Create
POST /api/[resource]
  body: { field1, field2 }
  response: { id, field1, field2, createdAt }

# Read List
GET /api/[resource]
  query: { page, limit, search }
  response: { items: [], total }

# Read One
GET /api/[resource]/:id
  response: { id, field1, field2 }

# Update
PUT /api/[resource]/:id
  body: { field1, field2 }
  response: { id, field1, field2, updatedAt }

# Delete
DELETE /api/[resource]/:id
  response: { success: true }
```

## Quick Test Checklist

```markdown
# Functional Test: [Feature Name]

## Happy Path
- [ ] 用户可以 [主要操作1]
- [ ] 用户可以 [主要操作2]
- [ ] 数据正确保存
- [ ] 数据正确显示

## Error Handling
- [ ] 空数据显示提示
- [ ] 无效输入显示错误
- [ ] 网络错误有提示

## Quick Smoke Test
- [ ] 页面加载正常
- [ ] 主流程可走通
- [ ] 无控制台错误
```

## Deploy Checklist

```markdown
# Deploy: [Version]

## Pre-Deploy
- [ ] 所有测试通过
- [ ] 环境变量配置
- [ ] 数据库迁移准备

## Deploy
- [ ] 后端部署
- [ ] 前端部署
- [ ] 验证主流程

## Post-Deploy
- [ ] 监控正常
- [ ] 通知相关人员
```

## Project Structure Templates

### Python + FastAPI + SQLite Backend

```bash
# 初始化项目
mkdir -p client/backend/src
cd client/backend

# 使用 uv 初始化
uv init
uv add fastapi uvicorn sqlmodel aiosqlite python-multipart

# 创建基础文件
touch src/__init__.py src/main.py src/models.py src/routes.py src/database.py
```

### Backend 代码模板

```python
# src/database.py
from sqlmodel import SQLModel, create_engine, Session
import os

DB_PATH = os.environ.get("DB_PATH", "./data.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

```python
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
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    created_at: datetime
```

```python
# src/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.database import get_session
from src.models import Item, ItemCreate, ItemRead

router = APIRouter()

@router.get("/items", response_model=list[ItemRead])
def list_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@router.post("/items", response_model=ItemRead)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = Item.from_orm(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
```

```python
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

@app.get("/health")
def health():
    return {"status": "ok"}
```

### React + Vite Frontend

```bash
npm create vite@latest client/frontend -- --template react-ts
cd client/frontend
npm install axios antd @ant-design/icons
```

---

## Standard Module Templates (基础模块模板)

### 用户模型 (User Model)

```python
# src/models/user.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(max_length=20, unique=True)
    password_hash: str
    nickname: str = Field(max_length=50)
    avatar: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
```

### 消息模型 (Message Model)

```python
# src/models/message.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=100)
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 系统配置模型 (Admin)

```python
# admin/backend/src/models/config.py
from sqlmodel import SQLModel, Field
from typing import Optional

class SystemConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, max_length=100)
    value: str
    description: Optional[str] = None
```

### 管理员模型 (Admin)

```python
# admin/backend/src/models/admin.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    password_hash: str
    name: str = Field(max_length=50)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
```


---

## API 文档规范模板

### FastAPI 配置示例

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

### API 路由文档规范示例

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

### 数据模型文档规范示例

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

### API 文档检查清单

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

---

## Tailwind CSS 简约组件示例

### 简约按钮

```tsx
// Primary Button
<button className="px-4 py-2 bg-blue-500 text-white rounded-lg 
  hover:bg-blue-600 transition-colors shadow-sm">
  提交
</button>

// Secondary Button
<button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg 
  hover:bg-gray-200 transition-colors">
  取消
</button>

// Danger Button
<button className="px-4 py-2 bg-red-500 text-white rounded-lg 
  hover:bg-red-600 transition-colors">
  删除
</button>
```

### 简约卡片

```tsx
<div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
  <h3 className="text-lg font-medium text-gray-900">标题</h3>
  <p className="text-gray-500">描述内容</p>
</div>
```

### 简约输入框

```tsx
<input 
  className="w-full px-4 py-2 border border-gray-200 rounded-lg
    focus:ring-2 focus:ring-blue-500 focus:border-transparent
    placeholder-gray-400" 
  placeholder="请输入..."
/>
```

### 简约列表项

```tsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm">
  <div className="flex items-center space-x-3">
    <div className="w-10 h-10 bg-gray-100 rounded-full"></div>
    <div>
      <p className="font-medium text-gray-900">标题</p>
      <p className="text-sm text-gray-500">描述</p>
    </div>
  </div>
  <button className="text-blue-500 hover:text-blue-600">查看</button>
</div>
```

### 简约表单

```tsx
<form className="space-y-4">
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">
      用户名
    </label>
    <input 
      className="w-full px-4 py-2 border border-gray-200 rounded-lg
        focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    />
  </div>
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">
      密码
    </label>
    <input 
      type="password"
      className="w-full px-4 py-2 border border-gray-200 rounded-lg
        focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    />
  </div>
  <button className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg 
    hover:bg-blue-600 transition-colors">
    登录
  </button>
</form>
```

### 空状态组件

```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
    <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
    </svg>
  </div>
  <p className="text-gray-500 mb-4">暂无数据</p>
  <button className="px-4 py-2 bg-blue-500 text-white rounded-lg">
    添加数据
  </button>
</div>
```

### 加载状态组件

```tsx
// Loading Spinner
<div className="flex items-center justify-center py-12">
  <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
</div>

// Skeleton Loading
<div className="animate-pulse space-y-4">
  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
  <div className="h-4 bg-gray-200 rounded w-5/6"></div>
</div>
```

---

## SQLite 使用注意

```python
# 共享数据库路径配置
import os
DB_PATH = os.environ.get("DB_PATH", "../shared/db/data.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Client和Admin后端共享同一个SQLite文件
# 注意：SQLite不支持高并发写入，适合原型验证
```


---

## Website (官网) 纯静态 HTML 模板

> ⚠️ **重要：Website 必须先用 MCP Pencil 完成 UI 设计稿，再实现静态 HTML。禁止跳过设计稿直接写代码。**

### 设计稿要求

Website 的 UI 设计稿与 Client/Admin 一起存放在 `docs/ui/[project].pen` 中，必须包含：
- Landing Page (Hero + 功能亮点 + CTA)
- 功能介绍页
- 定价页面
- 关于我们
- 联系我们
- 页头导航（响应式）
- 页脚
- 404 页面

### 目录结构

```
website/
├── index.html          # 首页
├── features.html       # 功能介绍
├── pricing.html        # 定价页面
├── about.html          # 关于我们
├── contact.html        # 联系我们
├── 404.html            # 404页面
├── css/
│   └── style.css       # 自定义样式
├── js/
│   └── main.js         # 脚本文件（如需要）
└── images/             # 图片资源
```

### 基础 HTML 模板

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>产品名称 - 一句话价值主张</title>
  <meta name="description" content="产品描述">
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-white text-gray-900">
  <!-- 页头导航 -->
  <header class="bg-white border-b sticky top-0 z-50">
    <nav class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
      <a href="/" class="text-xl font-bold">Logo</a>
      <div class="flex items-center gap-8">
        <a href="/" class="text-gray-600 hover:text-gray-900">首页</a>
        <a href="features.html" class="text-gray-600 hover:text-gray-900">功能</a>
        <a href="pricing.html" class="text-gray-600 hover:text-gray-900">定价</a>
        <a href="about.html" class="text-gray-600 hover:text-gray-900">关于</a>
        <a href="contact.html" class="text-gray-600 hover:text-gray-900">联系</a>
        <a href="#" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          开始使用
        </a>
      </div>
    </nav>
  </header>

  <!-- Hero 区域 -->
  <section class="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
    <div class="max-w-6xl mx-auto px-4 text-center">
      <h1 class="text-5xl font-bold text-gray-900 mb-6">
        产品核心价值主张
      </h1>
      <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        用一两句话描述产品能为用户解决什么问题
      </p>
      <div class="flex gap-4 justify-center">
        <a href="#" class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
          立即开始
        </a>
        <a href="features.html" class="px-8 py-3 bg-white text-gray-700 rounded-lg hover:bg-gray-50 font-medium border">
          了解更多
        </a>
      </div>
    </div>
  </section>

  <!-- 功能亮点 -->
  <section class="py-20">
    <div class="max-w-6xl mx-auto px-4">
      <h2 class="text-3xl font-bold text-center mb-12">核心功能</h2>
      <div class="grid grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <span class="text-2xl">🚀</span>
          </div>
          <h3 class="text-lg font-semibold mb-2">功能一</h3>
          <p class="text-gray-600">功能描述文字</p>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <span class="text-2xl">⚡</span>
          </div>
          <h3 class="text-lg font-semibold mb-2">功能二</h3>
          <p class="text-gray-600">功能描述文字</p>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <span class="text-2xl">🎯</span>
          </div>
          <h3 class="text-lg font-semibold mb-2">功能三</h3>
          <p class="text-gray-600">功能描述文字</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA 区域 -->
  <section class="bg-blue-600 py-16">
    <div class="max-w-4xl mx-auto px-4 text-center">
      <h2 class="text-3xl font-bold text-white mb-4">准备好开始了吗？</h2>
      <p class="text-blue-100 mb-8">立即体验，开启高效之旅</p>
      <a href="#" class="px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 font-medium">
        免费试用
      </a>
    </div>
  </section>

  <!-- 页脚 -->
  <footer class="bg-gray-900 text-gray-400 py-12">
    <div class="max-w-6xl mx-auto px-4">
      <div class="grid grid-cols-4 gap-8 mb-8">
        <div>
          <h4 class="text-white font-semibold mb-4">产品</h4>
          <ul class="space-y-2">
            <li><a href="features.html" class="hover:text-white">功能介绍</a></li>
            <li><a href="pricing.html" class="hover:text-white">定价</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-4">公司</h4>
          <ul class="space-y-2">
            <li><a href="about.html" class="hover:text-white">关于我们</a></li>
            <li><a href="contact.html" class="hover:text-white">联系我们</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-4">支持</h4>
          <ul class="space-y-2">
            <li><a href="#" class="hover:text-white">文档</a></li>
            <li><a href="#" class="hover:text-white">常见问题</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-4">关注我们</h4>
        </div>
      </div>
      <div class="border-t border-gray-800 pt-8 text-center text-sm">
        © 2024 产品名称. All rights reserved.
      </div>
    </div>
  </footer>
</body>
</html>
```

### 使用 frontend-design skill 优化官网 (必须)

**官网页面必须使用 `frontend-design` skill 进行 Review 和优化：**

```bash
# 激活 frontend-design skill 优化官网
/frontend-design

# 优化指令示例
"请使用 frontend-design skill 优化官网页面：
- 检查视觉层次和排版
- 优化色彩搭配和对比度
- 确保 CTA 按钮突出
- 检查响应式适配
- 优化首屏加载体验
- 确保移动端导航可用"
```

### 本地预览

```bash
# 使用 Python 简单服务器
cd website
python -m http.server 4000

# 或使用 npx serve
npx serve . -p 4000

# 访问 http://localhost:4000
```

### 官网 Review 检查清单

```markdown
# 官网页面 Review 检查项 (使用 frontend-design skill)

## 视觉设计
- [ ] Hero 区域视觉冲击力足够
- [ ] CTA 按钮颜色突出、位置明显
- [ ] 色彩搭配和谐统一
- [ ] 字体层次清晰
- [ ] 间距和留白充足

## 内容结构
- [ ] 首屏传达核心价值主张
- [ ] 功能介绍清晰易懂
- [ ] 联系方式易于找到

## 响应式
- [ ] 移动端适配良好
- [ ] 导航在小屏幕可用
- [ ] 图片自适应

## SEO
- [ ] 每页有独立 title
- [ ] meta description 已设置
- [ ] 图片有 alt 属性
```
