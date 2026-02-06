# 角色权限设计 - 待办事项管理系统

## 1. 角色定义

### 1.1 MVP阶段角色（单用户模式）

| 角色 | 定义 | 数量 | 说明 |
|------|------|------|------|
| **注册用户** | 已注册并登录的用户 | 多个 | MVP阶段唯一角色 |
| **游客** | 未登录用户 | - | 只能访问登录/注册页 |

**MVP阶段说明:**
- 暂不支持团队协作
- 每个用户只能管理自己的任务
- 用户之间数据完全隔离

### 1.2 未来版本角色规划（V3.0）

| 角色 | 定义 | 权限范围 | 典型场景 |
|------|------|----------|----------|
| **团队所有者** | 创建团队的用户 | 全部权限 | 团队管理 |
| **团队管理员** | 被授权的管理员 | 管理权限 | 协助管理 |
| **团队成员** | 普通团队成员 | 基础权限 | 日常使用 |
| **访客** | 被邀请的外部用户 | 只读权限 | 查看任务 |

---

## 2. 权限矩阵（MVP阶段）

### 2.1 功能权限

| 功能模块 | 注册用户 | 游客 | 说明 |
|----------|---------|------|------|
| **用户认证** | | | |
| 注册 | ❌ | ✅ | 游客可注册 |
| 登录 | ❌ | ✅ | 游客可登录 |
| 登出 | ✅ | ❌ | 用户可登出 |
| 修改密码 | ✅ | ❌ | 用户可修改密码 |
| 修改个人信息 | ✅ | ❌ | 用户可修改信息 |
| **任务管理** | | | |
| 创建任务 | ✅ | ❌ | 只能创建自己的任务 |
| 查看任务 | ✅ (自己的) | ❌ | 只能查看自己的任务 |
| 编辑任务 | ✅ (自己的) | ❌ | 只能编辑自己的任务 |
| 删除任务 | ✅ (自己的) | ❌ | 只能删除自己的任务 |
| 变更任务状态 | ✅ (自己的) | ❌ | 只能变更自己的任务 |
| **列表管理** | | | |
| 创建列表 | ✅ | ❌ | 只能创建自己的列表 |
| 查看列表 | ✅ (自己的) | ❌ | 只能查看自己的列表 |
| 编辑列表 | ✅ (自己的) | ❌ | 只能编辑自己的列表 |
| 删除列表 | ✅ (自己的) | ❌ | 只能删除自己的列表（除默认列表） |
| **标签管理** | | | |
| 创建标签 | ✅ | ❌ | 只能创建自己的标签 |
| 查看标签 | ✅ (自己的) | ❌ | 只能查看自己的标签 |
| 编辑标签 | ✅ (自己的) | ❌ | 只能编辑自己的标签 |
| 删除标签 | ✅ (自己的) | ❌ | 只能删除自己的标签 |
| **搜索筛选** | | | |
| 搜索任务 | ✅ (自己的) | ❌ | 只能搜索自己的任务 |
| 筛选任务 | ✅ (自己的) | ❌ | 只能筛选自己的任务 |
| **数据统计** | | | |
| 查看统计 | ✅ (自己的) | ❌ | 只能查看自己的统计 |

**图例**: ✅ 允许 | ❌ 禁止

---

## 3. 数据隔离策略

### 3.1 用户数据隔离

**原则**: 每个用户只能访问自己的数据

**实现方式:**
```python
# 所有查询都必须带上 user_id 过滤
tasks = db.query(Task).filter(Task.user_id == current_user.id).all()

# 创建资源时自动关联当前用户
task = Task(
    title=data.title,
    user_id=current_user.id  # 自动关联
)
```

### 3.2 权限校验流程

```
用户请求 API
    ↓
验证 JWT Token
    ↓
提取 user_id
    ↓
查询资源（带 user_id 过滤）
    ↓
检查资源是否属于当前用户
    ↓
允许操作 / 拒绝访问
```

### 3.3 API权限校验示例

```python
# 获取任务详情
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询任务，必须属于当前用户
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  # 权限校验
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

# 更新任务
@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询任务，必须属于当前用户
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  # 权限校验
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 更新任务
    for key, value in data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    return task
```

---

## 4. 路由权限配置

### 4.1 公开路由（无需认证）

| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/health` | GET | 健康检查 |

### 4.2 受保护路由（需要认证）

| 路由 | 方法 | 权限要求 |
|------|------|----------|
| `/api/auth/me` | GET | 已登录 |
| `/api/auth/me` | PUT | 已登录 |
| `/api/auth/password` | PUT | 已登录 |
| `/api/tasks/*` | ALL | 已登录 + 资源所有者 |
| `/api/lists/*` | ALL | 已登录 + 资源所有者 |
| `/api/tags/*` | ALL | 已登录 + 资源所有者 |
| `/api/stats/*` | GET | 已登录 |

---

## 5. 未来版本权限设计（V3.0）

### 5.1 团队协作权限矩阵

| 功能 | 团队所有者 | 团队管理员 | 团队成员 | 访客 |
|------|-----------|-----------|---------|------|
| **团队管理** | | | | |
| 创建团队 | ✅ | ❌ | ❌ | ❌ |
| 解散团队 | ✅ | ❌ | ❌ | ❌ |
| 编辑团队信息 | ✅ | ✅ | ❌ | ❌ |
| **成员管理** | | | | |
| 邀请成员 | ✅ | ✅ | ❌ | ❌ |
| 移除成员 | ✅ | ✅ | ❌ | ❌ |
| 设置管理员 | ✅ | ❌ | ❌ | ❌ |
| **任务管理** | | | | |
| 创建任务 | ✅ | ✅ | ✅ | ❌ |
| 查看任务 | ✅ | ✅ | ✅ | ✅ |
| 编辑任务 | ✅ | ✅ | ✅ (自己的) | ❌ |
| 删除任务 | ✅ | ✅ | ✅ (自己的) | ❌ |
| 分配任务 | ✅ | ✅ | ✅ | ❌ |
| **列表管理** | | | | |
| 创建列表 | ✅ | ✅ | ✅ | ❌ |
| 编辑列表 | ✅ | ✅ | ✅ (自己的) | ❌ |
| 删除列表 | ✅ | ✅ | ✅ (自己的) | ❌ |
| 共享列表 | ✅ | ✅ | ✅ | ❌ |

### 5.2 资源权限级别

| 权限级别 | 说明 | 可执行操作 |
|----------|------|-----------|
| **所有者** | 资源创建者 | 全部操作 |
| **编辑者** | 被授权编辑 | 查看、编辑 |
| **查看者** | 被授权查看 | 仅查看 |
| **无权限** | 未授权 | 无法访问 |

### 5.3 列表共享权限

```python
ListPermission {
    id: int
    list_id: int
    user_id: int
    permission: enum ('owner', 'editor', 'viewer')
    created_at: datetime
}
```

**权限继承:**
- 列表的权限会继承到列表下的所有任务
- 用户对列表有编辑权限，则对列表下的任务也有编辑权限

---

## 6. 权限校验中间件

### 6.1 认证中间件

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

### 6.2 资源所有权校验

```python
async def verify_task_ownership(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Task:
    """校验任务所有权"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task

# 使用示例
@router.put("/tasks/{task_id}")
async def update_task(
    data: TaskUpdate,
    task: Task = Depends(verify_task_ownership)  # 自动校验所有权
):
    # 更新任务
    for key, value in data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    return task
```

---

## 7. 安全最佳实践

### 7.1 密码安全

- ✅ 使用 bcrypt 加密存储
- ✅ 密码最小长度 8 位
- ✅ 密码必须包含字母和数字
- ✅ 登录失败次数限制（5次后锁定10分钟）

### 7.2 Token安全

- ✅ JWT Token 有效期 7 天
- ✅ Token 存储在 HTTP-only Cookie（如使用Cookie）
- ✅ 或存储在 localStorage（需注意XSS风险）
- ✅ Token 刷新机制（可选）

### 7.3 API安全

- ✅ 所有API使用HTTPS
- ✅ CORS配置限制来源
- ✅ 请求频率限制（Rate Limiting）
- ✅ SQL注入防护（使用ORM）
- ✅ XSS防护（输入转义）

---

## 8. 错误处理

### 8.1 权限错误响应

| 错误场景 | HTTP状态码 | 错误信息 |
|----------|-----------|----------|
| 未登录 | 401 | "Authentication required" |
| Token无效 | 401 | "Invalid authentication credentials" |
| Token过期 | 401 | "Token expired" |
| 无权限访问 | 403 | "Access denied" |
| 资源不存在 | 404 | "Resource not found or access denied" |

### 8.2 错误响应格式

```json
{
  "detail": "Access denied",
  "error_code": "PERMISSION_DENIED",
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## 9. 审计日志（未来版本）

### 9.1 日志记录

**记录内容:**
- 用户操作（创建、编辑、删除）
- 操作时间
- 操作IP
- 操作结果

**日志用途:**
- 安全审计
- 问题排查
- 用户行为分析

---

**文档版本**: v1.0
**创建日期**: 2026-02-06
**最后更新**: 2026-02-06
**文档状态**: 待评审
