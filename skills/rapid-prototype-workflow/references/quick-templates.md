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
