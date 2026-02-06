# CODING.md - 编码规范约定

> 定义快速原型开发的编码规范和最佳实践

---

## 通用原则

| 原则 | 说明 |
|------|------|
| 简洁优先 | 避免过度封装，保持代码简单 |
| 设计驱动 | 界面实现必须严格按照设计稿还原 |
| 不可变性 | 优先使用不可变数据结构 |
| 错误处理 | 所有异步操作必须有错误处理 |
| 类型安全 | 使用 TypeScript / Pydantic 确保类型安全 |

---

## Python 后端规范

### 项目结构

```
backend/
└── src/                    # 所有代码必须在 src/ 包下
    ├── __init__.py
    ├── main.py             # FastAPI 入口
    ├── models.py           # SQLModel 数据模型
    ├── schemas.py          # Pydantic 请求/响应模型
    ├── routes.py           # 路由定义
    ├── database.py         # 数据库配置
    └── utils.py            # 工具函数
```

### 导入规范

```python
# ✅ 正确：使用绝对导入
from src.database import get_session
from src.models import User
from src.schemas import UserCreate

# ❌ 错误：使用相对导入
from .database import get_session
from ..models import User
```

### FastAPI 入口模板

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import init_db
from src.routes import router

app = FastAPI(
    title="项目名称 API",
    description="项目描述",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

@app.on_event("startup")
async def startup():
    init_db()
```

### 数据模型规范

```python
# src/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class UserBase(SQLModel):
    username: str = Field(index=True)
    email: str = Field(unique=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime
```

### API 路由规范

```python
# src/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.database import get_session
from src.models import User, UserCreate, UserRead

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/users", response_model=list[UserRead])
async def get_users(session: Session = Depends(get_session)):
    """获取用户列表"""
    users = session.exec(select(User)).all()
    return users

@router.post("/users", response_model=UserRead)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """创建用户"""
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

### 错误处理

```python
from fastapi import HTTPException

# 标准错误响应
raise HTTPException(status_code=404, detail="User not found")
raise HTTPException(status_code=400, detail="Invalid input")
raise HTTPException(status_code=500, detail="Internal server error")
```

---

## React 前端规范

### 项目结构

```
frontend/
└── src/
    ├── components/         # 可复用组件
    │   ├── ui/             # 基础 UI 组件
    │   └── business/       # 业务组件
    ├── pages/              # 页面组件
    ├── hooks/              # 自定义 Hooks
    ├── services/           # API 服务
    ├── utils/              # 工具函数
    ├── types/              # TypeScript 类型
    ├── App.tsx
    └── main.tsx
```

### 组件规范

```tsx
// ✅ 正确：函数组件 + TypeScript
interface UserCardProps {
  user: User;
  onEdit: (id: number) => void;
}

export function UserCard({ user, onEdit }: UserCardProps) {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold">{user.name}</h3>
      <button onClick={() => onEdit(user.id)}>编辑</button>
    </div>
  );
}

// ❌ 错误：类组件
class UserCard extends React.Component { ... }
```

### 状态管理

```tsx
// 简单状态：useState
const [users, setUsers] = useState<User[]>([]);

// 复杂状态：useReducer
const [state, dispatch] = useReducer(reducer, initialState);

// 全局状态：Context
const UserContext = createContext<UserContextType | null>(null);
```

### API 服务

```tsx
// src/services/api.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchUsers(): Promise<User[]> {
  const response = await fetch(`${API_BASE}/api/users`);
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  return response.json();
}

export async function createUser(data: UserCreate): Promise<User> {
  const response = await fetch(`${API_BASE}/api/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create user');
  }
  return response.json();
}
```

### 自定义 Hooks

```tsx
// src/hooks/useUsers.ts
export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetchUsers()
      .then(setUsers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { users, loading, error };
}
```

---

## Tailwind CSS 规范

### 配色方案

```css
/* 简约配色 */
--primary: #3b82f6;      /* 蓝色主色 */
--secondary: #64748b;    /* 灰色辅助 */
--background: #f8fafc;   /* 浅灰背景 */
--surface: #ffffff;      /* 白色卡片 */
--text-primary: #1e293b; /* 深色文字 */
--text-secondary: #64748b;/* 浅色文字 */
--success: #22c55e;      /* 成功绿色 */
--warning: #f59e0b;      /* 警告黄色 */
--error: #ef4444;        /* 错误红色 */
```

### 间距规范

```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
```

### 常用类组合

```tsx
// 卡片
<div className="p-4 bg-white rounded-lg shadow">

// 按钮 - 主要
<button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">

// 按钮 - 次要
<button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">

// 输入框
<input className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">

// 标题
<h1 className="text-2xl font-bold text-gray-900">
<h2 className="text-xl font-semibold text-gray-800">

// 正文
<p className="text-gray-600">
```

---

## 不可变性原则

### JavaScript/TypeScript

```typescript
// ✅ 正确：创建新对象
function updateUser(user: User, name: string): User {
  return { ...user, name };
}

// ❌ 错误：直接修改
function updateUser(user: User, name: string): User {
  user.name = name;  // 修改了原对象！
  return user;
}

// ✅ 正确：数组操作
const newItems = [...items, newItem];           // 添加
const newItems = items.filter(i => i.id !== id); // 删除
const newItems = items.map(i => i.id === id ? {...i, name} : i); // 更新
```

### Python

```python
# ✅ 正确：使用 Pydantic model_copy
updated_user = user.model_copy(update={"name": new_name})

# ❌ 错误：直接修改
user.name = new_name  # 修改了原对象！
```

---

## 禁止事项

### 代码层面

- ❌ 禁止使用 `any` 类型（TypeScript）
- ❌ 禁止使用 `var` 声明变量
- ❌ 禁止直接修改 props 或 state
- ❌ 禁止在循环中使用 `await`（应使用 `Promise.all`）
- ❌ 禁止硬编码敏感信息（API Key、密码等）

### 样式层面

- ❌ 禁止使用内联样式（除非动态计算）
- ❌ 禁止使用过于花哨的动画
- ❌ 禁止堆砌太多颜色
- ❌ 禁止忽视移动端适配
- ❌ 禁止使用默认的丑陋样式
- ❌ 禁止脱离设计稿自行发挥

---

## 代码质量检查清单

在提交代码前检查：

- [ ] 代码可读性良好，命名清晰
- [ ] 函数小于 50 行
- [ ] 文件小于 800 行
- [ ] 无深层嵌套（> 4 层）
- [ ] 有适当的错误处理
- [ ] 无 console.log 语句
- [ ] 无硬编码值
- [ ] 使用不可变模式
- [ ] 界面与设计稿一致

---

## 相关文档

- [CLAUDE.md](./CLAUDE.md) - AI 编程助手核心约定
- [AGENTS.md](./AGENTS.md) - 多 Agent 协作约定
- [WORKFLOW.md](./WORKFLOW.md) - 开发工作流约定
- [PROJECT.md](./PROJECT.md) - 项目结构约定
