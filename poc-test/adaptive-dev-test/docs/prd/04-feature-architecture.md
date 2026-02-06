# 功能架构设计 - 待办事项管理系统

## 1. 产品架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        待办事项管理系统架构                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐                                          │
│  │     Client端         │                                          │
│  │    (用户侧Web)       │                                          │
│  ├──────────────────────┤                                          │
│  │ • 任务管理           │                                          │
│  │ • 列表管理           │                                          │
│  │ • 标签管理           │                                          │
│  │ • 搜索筛选           │                                          │
│  │ • 数据统计           │                                          │
│  │ • 个人中心           │                                          │
│  │ • 设置               │                                          │
│  └──────────────────────┘                                          │
│           │                                                         │
│           │ RESTful API                                            │
│           ▼                                                         │
│  ┌──────────────────────┐                                          │
│  │     Backend API      │                                          │
│  │   (Python/FastAPI)   │                                          │
│  ├──────────────────────┤                                          │
│  │ • 用户认证           │                                          │
│  │ • 任务CRUD           │                                          │
│  │ • 列表CRUD           │                                          │
│  │ • 标签CRUD           │                                          │
│  │ • 搜索服务           │                                          │
│  │ • 统计服务           │                                          │
│  └──────────────────────┘                                          │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────────┐                                          │
│  │      Database        │                                          │
│  │      (SQLite)        │                                          │
│  ├──────────────────────┤                                          │
│  │ • users              │                                          │
│  │ • tasks              │                                          │
│  │ • lists              │                                          │
│  │ • tags               │                                          │
│  │ • task_tags          │                                          │
│  └──────────────────────┘                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. 功能模块划分

### 2.1 核心功能模块

| 模块 | 功能 | 优先级 | MVP |
|------|------|--------|-----|
| **用户认证** | 注册、登录、登出、密码重置 | P0 | ✅ |
| **任务管理** | 任务增删改查、状态变更、优先级设置 | P0 | ✅ |
| **列表管理** | 列表增删改查、任务分组 | P0 | ✅ |
| **标签管理** | 标签增删改查、任务标记 | P1 | ✅ |
| **搜索筛选** | 关键词搜索、条件筛选 | P1 | ✅ |
| **数据统计** | 完成率、任务数统计 | P2 | ✅ |
| **个人中心** | 个人信息、偏好设置 | P2 | ✅ |

### 2.2 功能详细说明

#### 2.2.1 用户认证模块

**功能清单:**
- 用户注册（邮箱 + 密码）
- 用户登录（JWT Token）
- 用户登出
- 密码修改
- 个人信息编辑

**数据模型:**
```python
User {
    id: int
    email: string (unique)
    username: string
    password_hash: string
    avatar_url: string (optional)
    created_at: datetime
    updated_at: datetime
}
```

**API端点:**
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/me` - 更新用户信息
- `PUT /api/auth/password` - 修改密码

---

#### 2.2.2 任务管理模块

**功能清单:**
- 创建任务
- 查看任务列表
- 查看任务详情
- 编辑任务
- 删除任务
- 标记任务状态（待办/进行中/已完成）
- 设置任务优先级（高/中/低）
- 设置截止日期
- 任务排序（手动拖拽）

**数据模型:**
```python
Task {
    id: int
    user_id: int (外键)
    list_id: int (外键, nullable)
    title: string
    description: text (optional)
    status: enum ('todo', 'in_progress', 'completed')
    priority: enum ('high', 'medium', 'low', 'none')
    due_date: date (optional)
    completed_at: datetime (optional)
    order: int (排序字段)
    created_at: datetime
    updated_at: datetime
}
```

**API端点:**
- `POST /api/tasks` - 创建任务
- `GET /api/tasks` - 获取任务列表（支持筛选）
- `GET /api/tasks/{id}` - 获取任务详情
- `PUT /api/tasks/{id}` - 更新任务
- `DELETE /api/tasks/{id}` - 删除任务
- `PATCH /api/tasks/{id}/status` - 更新任务状态
- `PATCH /api/tasks/{id}/priority` - 更新任务优先级
- `POST /api/tasks/reorder` - 批量更新任务顺序

---

#### 2.2.3 列表管理模块

**功能清单:**
- 创建列表
- 查看列表
- 编辑列表
- 删除列表
- 列表排序

**数据模型:**
```python
List {
    id: int
    user_id: int (外键)
    name: string
    color: string (optional, hex color)
    icon: string (optional, emoji or icon name)
    order: int
    created_at: datetime
    updated_at: datetime
}
```

**默认列表:**
- 收件箱（Inbox）- 默认列表，不可删除
- 今天（Today）- 虚拟列表，显示今日任务
- 即将到来（Upcoming）- 虚拟列表，显示未来7天任务

**API端点:**
- `POST /api/lists` - 创建列表
- `GET /api/lists` - 获取列表
- `GET /api/lists/{id}` - 获取列表详情
- `PUT /api/lists/{id}` - 更新列表
- `DELETE /api/lists/{id}` - 删除列表
- `POST /api/lists/reorder` - 批量更新列表顺序

---

#### 2.2.4 标签管理模块

**功能清单:**
- 创建标签
- 查看标签
- 编辑标签
- 删除标签
- 为任务添加标签
- 从任务移除标签

**数据模型:**
```python
Tag {
    id: int
    user_id: int (外键)
    name: string
    color: string (hex color)
    created_at: datetime
    updated_at: datetime
}

TaskTag {
    task_id: int (外键)
    tag_id: int (外键)
    created_at: datetime
}
```

**API端点:**
- `POST /api/tags` - 创建标签
- `GET /api/tags` - 获取标签列表
- `PUT /api/tags/{id}` - 更新标签
- `DELETE /api/tags/{id}` - 删除标签
- `POST /api/tasks/{task_id}/tags` - 为任务添加标签
- `DELETE /api/tasks/{task_id}/tags/{tag_id}` - 移除任务标签

---

#### 2.2.5 搜索筛选模块

**功能清单:**
- 关键词搜索（任务标题、描述）
- 按状态筛选
- 按优先级筛选
- 按列表筛选
- 按标签筛选
- 按截止日期筛选
- 组合筛选

**API端点:**
- `GET /api/tasks/search?q={keyword}` - 关键词搜索
- `GET /api/tasks?status={status}&priority={priority}&list_id={list_id}&tag_id={tag_id}&due_date={date}` - 组合筛选

---

#### 2.2.6 数据统计模块

**功能清单:**
- 任务总数统计
- 完成任务数统计
- 完成率计算
- 按状态分组统计
- 按优先级分组统计
- 按列表分组统计
- 趋势图（最近7天/30天完成情况）

**API端点:**
- `GET /api/stats/overview` - 总览统计
- `GET /api/stats/by-status` - 按状态统计
- `GET /api/stats/by-priority` - 按优先级统计
- `GET /api/stats/by-list` - 按列表统计
- `GET /api/stats/trend?days={days}` - 趋势统计

---

## 3. 信息架构

### 3.1 导航结构

```
待办事项管理系统
├── 侧边栏
│   ├── 收件箱 (Inbox)
│   ├── 今天 (Today)
│   ├── 即将到来 (Upcoming)
│   ├── ─────────────
│   ├── 我的列表
│   │   ├── 列表1
│   │   ├── 列表2
│   │   └── + 新建列表
│   ├── ─────────────
│   ├── 标签
│   │   ├── #标签1
│   │   ├── #标签2
│   │   └── + 新建标签
│   └── ─────────────
│   └── 设置
├── 主内容区
│   ├── 顶部栏
│   │   ├── 页面标题
│   │   ├── 搜索框
│   │   └── 用户头像
│   ├── 任务列表
│   │   ├── 筛选器
│   │   ├── 排序选项
│   │   └── 任务项
│   └── + 快速添加按钮
└── 详情面板（可折叠）
    ├── 任务详情
    ├── 编辑表单
    └── 操作按钮
```

### 3.2 页面层级

| 层级 | 页面 | 路由 | 说明 |
|------|------|------|------|
| L1 | 登录页 | `/login` | 未登录用户入口 |
| L1 | 注册页 | `/register` | 新用户注册 |
| L2 | 首页（收件箱） | `/` | 默认显示收件箱 |
| L2 | 今天 | `/today` | 今日任务 |
| L2 | 即将到来 | `/upcoming` | 未来任务 |
| L2 | 列表详情 | `/lists/{id}` | 特定列表的任务 |
| L2 | 标签详情 | `/tags/{id}` | 特定标签的任务 |
| L2 | 搜索结果 | `/search?q={keyword}` | 搜索结果页 |
| L2 | 统计页 | `/stats` | 数据统计 |
| L2 | 设置页 | `/settings` | 用户设置 |

---

## 4. 数据流设计

### 4.1 任务创建流程

```
用户输入任务标题
    ↓
点击"添加"按钮
    ↓
前端验证（标题不为空）
    ↓
发送 POST /api/tasks
    ↓
后端验证（用户认证、数据格式）
    ↓
写入数据库
    ↓
返回任务对象
    ↓
前端更新任务列表
    ↓
显示成功提示
```

### 4.2 任务状态变更流程

```
用户点击任务复选框
    ↓
前端乐观更新（立即显示变更）
    ↓
发送 PATCH /api/tasks/{id}/status
    ↓
后端更新状态
    ↓
返回更新后的任务
    ↓
前端确认更新成功
    ↓
（如失败则回滚）
```

### 4.3 数据同步策略

**实时同步:**
- 任务增删改 - 立即同步
- 状态变更 - 立即同步

**定时同步:**
- 统计数据 - 每5分钟更新一次

**缓存策略:**
- 列表和标签 - 本地缓存，变更时更新
- 任务列表 - 按页缓存，滚动加载

---

## 5. 状态管理

### 5.1 前端状态

```typescript
AppState {
  auth: {
    user: User | null
    token: string | null
    isAuthenticated: boolean
  }
  tasks: {
    items: Task[]
    loading: boolean
    error: string | null
    filters: {
      status: string[]
      priority: string[]
      listId: number | null
      tagId: number | null
    }
  }
  lists: {
    items: List[]
    loading: boolean
  }
  tags: {
    items: Tag[]
    loading: boolean
  }
  ui: {
    sidebarCollapsed: boolean
    detailPanelOpen: boolean
    selectedTaskId: number | null
  }
}
```

---

## 6. 错误处理

### 6.1 错误类型

| 错误类型 | HTTP状态码 | 处理方式 |
|----------|-----------|----------|
| 认证失败 | 401 | 跳转登录页 |
| 权限不足 | 403 | 提示无权限 |
| 资源不存在 | 404 | 提示资源不存在 |
| 参数错误 | 400 | 提示具体错误信息 |
| 服务器错误 | 500 | 提示稍后重试 |
| 网络错误 | - | 提示网络异常，重试 |

### 6.2 错误提示

**Toast提示:**
- 成功操作 - 绿色提示，2秒后自动消失
- 错误操作 - 红色提示，需手动关闭
- 警告信息 - 黄色提示，3秒后自动消失

---

## 7. 性能优化

### 7.1 前端优化

- **懒加载** - 任务列表分页加载
- **虚拟滚动** - 大量任务时使用虚拟列表
- **防抖节流** - 搜索输入防抖，滚动加载节流
- **乐观更新** - 状态变更立即反馈
- **缓存策略** - 列表和标签本地缓存

### 7.2 后端优化

- **数据库索引** - user_id, list_id, status, due_date
- **查询优化** - 使用JOIN减少查询次数
- **分页查询** - 限制单次返回数据量
- **缓存** - 统计数据缓存

---

## 8. 安全设计

### 8.1 认证授权

- **JWT Token** - 用户认证
- **Token过期** - 7天过期，需重新登录
- **权限校验** - 每个API请求校验用户权限

### 8.2 数据安全

- **密码加密** - bcrypt加密存储
- **SQL注入防护** - 使用ORM参数化查询
- **XSS防护** - 前端输入转义
- **CSRF防护** - Token验证

---

## 9. 扩展性设计

### 9.1 预留扩展点

**V2.0 扩展:**
- 子任务 - task表增加parent_id字段
- 任务提醒 - 增加reminders表
- 任务评论 - 增加comments表
- 任务附件 - 增加attachments表

**V3.0 扩展:**
- 团队协作 - 增加teams, team_members表
- 任务分配 - task表增加assignee_id字段
- 权限管理 - 增加permissions表

### 9.2 API版本管理

- 使用URL版本号: `/api/v1/tasks`
- 保持向后兼容
- 废弃API提前通知

---

**文档版本**: v1.0
**创建日期**: 2026-02-06
**最后更新**: 2026-02-06
**文档状态**: 待评审
