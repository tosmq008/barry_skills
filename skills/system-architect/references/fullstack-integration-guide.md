# 前后端综合集成指南

## 1. 接口契约管理

### 1.1 契约定义规范

**OpenAPI/Swagger 规范：**
- 所有API必须先定义OpenAPI规范
- 规范文件作为前后端开发的唯一契约
- 契约变更需要前后端共同评审

**契约文件结构：**
```yaml
openapi: 3.0.3
info:
  title: [项目名] API
  version: 1.0.0
paths:
  /api/v1/users:
    get:
      summary: 获取用户列表
      parameters: [...]
      responses:
        '200':
          content:
            application/json:
              schema: { $ref: '#/components/schemas/UserList' }
components:
  schemas:
    User:
      type: object
      properties:
        id: { type: integer }
        name: { type: string }
```

### 1.2 Mock 服务策略

| 方案 | 适用场景 | 工具 |
|------|----------|------|
| 前端Mock | 前端独立开发 | MSW / Mock.js |
| Mock Server | 团队共享Mock | Prism / json-server |
| 契约Mock | 基于OpenAPI自动生成 | Swagger Mock |

## 2. 认证鉴权集成

### 2.1 JWT 认证流程

```
1. 用户登录 → 后端验证 → 返回 AccessToken + RefreshToken
2. 前端存储Token → 请求携带 Authorization: Bearer <token>
3. 后端验证Token → 解析用户信息 → 权限检查
4. Token过期 → 前端用RefreshToken换新Token → 重试请求
5. RefreshToken过期 → 跳转登录页
```

### 2.2 权限控制集成

**前端权限控制：**
- 路由级：路由守卫检查权限
- 页面级：权限指令控制元素显隐
- 按钮级：权限函数控制操作

**后端权限控制：**
- 接口级：中间件/装饰器检查权限
- 数据级：查询条件过滤数据范围
- 字段级：响应过滤敏感字段

### 2.3 权限数据同步

```
后端返回权限数据:
{
  "roles": ["admin"],
  "permissions": ["user:read", "user:write", "order:read"],
  "menus": [...]
}

前端存储并使用:
- 路由表动态生成
- 菜单动态渲染
- 按钮权限判断
```

## 3. 数据交互规范

### 3.1 请求规范

**请求头标准：**
```
Content-Type: application/json
Authorization: Bearer <token>
X-Request-ID: <uuid>
X-Client-Version: 1.0.0
Accept-Language: zh-CN
```

### 3.2 响应规范

**成功响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "meta": { "total": 100, "page": 1, "page_size": 20 }
}
```

**错误响应：**
```json
{
  "code": 40001,
  "message": "参数校验失败",
  "errors": [
    { "field": "email", "message": "格式不正确" }
  ]
}
```

### 3.3 特殊数据处理

| 数据类型 | 前端处理 | 后端处理 | 约定 |
|----------|----------|----------|------|
| 时间 | dayjs本地化展示 | UTC存储/ISO8601返回 | ISO 8601 |
| 金额 | 分→元展示 | 分为单位存储 | 整数分 |
| 枚举 | 前端映射文案 | 返回枚举值 | 统一枚举字典 |
| 文件 | FormData上传 | 流式接收 | multipart |
| 大数字 | BigInt/字符串 | 字符串返回 | 避免精度丢失 |

## 4. 错误处理规范

### 4.1 错误码体系

| 范围 | 类别 | 前端处理策略 |
|------|------|--------------|
| 0 | 成功 | 正常处理 |
| 400xx | 客户端错误 | 表单提示/参数修正 |
| 401xx | 认证错误 | 刷新Token/跳转登录 |
| 403xx | 权限错误 | 权限提示/申请权限 |
| 404xx | 资源不存在 | 404页面/友好提示 |
| 409xx | 冲突错误 | 提示冲突/刷新重试 |
| 429xx | 限流 | 提示稍后重试 |
| 500xx | 服务器错误 | 通用错误提示 |

### 4.2 前端统一错误处理

```typescript
// 请求拦截器统一处理
const errorHandler = (error) => {
  const { status, data } = error.response
  switch (status) {
    case 401: refreshToken() or redirectToLogin()
    case 403: showPermissionDenied()
    case 429: showRateLimitMessage()
    case 500: showServerError()
  }
}
```

## 5. 联调流程规范

### 5.1 联调前准备

- [ ] API契约文档已确认
- [ ] 后端接口已部署到开发环境
- [ ] 前端Mock已切换为真实API
- [ ] 测试数据已准备
- [ ] CORS配置已完成

### 5.2 联调检查清单

- [ ] 所有接口路径正确
- [ ] 请求参数格式匹配
- [ ] 响应数据结构一致
- [ ] 错误码处理完整
- [ ] 认证Token传递正确
- [ ] 分页/排序/筛选正常
- [ ] 文件上传/下载正常
- [ ] 并发请求处理正确
- [ ] 超时/重试机制生效
- [ ] 跨域配置正确

## 6. 输出物清单

- OpenAPI/Swagger契约文件
- 认证鉴权集成方案
- 数据交互规范文档
- 错误码字典
- 联调检查清单
