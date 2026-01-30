# API Design Conventions

## RESTful API Standards

### URL Naming

```
# 资源命名使用复数名词
GET    /api/v1/users           # 获取用户列表
GET    /api/v1/users/{id}      # 获取单个用户
POST   /api/v1/users           # 创建用户
PUT    /api/v1/users/{id}      # 更新用户
DELETE /api/v1/users/{id}      # 删除用户

# 嵌套资源
GET    /api/v1/users/{userId}/orders    # 获取用户的订单
POST   /api/v1/users/{userId}/orders    # 为用户创建订单

# 操作类接口使用动词
POST   /api/v1/orders/{id}/submit       # 提交订单
POST   /api/v1/orders/{id}/cancel       # 取消订单
```

### HTTP Methods

| Method | 用途 | 幂等性 | 安全性 |
|--------|------|--------|--------|
| GET | 查询资源 | 是 | 是 |
| POST | 创建资源 | 否 | 否 |
| PUT | 全量更新 | 是 | 否 |
| PATCH | 部分更新 | 否 | 否 |
| DELETE | 删除资源 | 是 | 否 |

### HTTP Status Codes

```
# 成功响应
200 OK              - 请求成功
201 Created         - 资源创建成功
204 No Content      - 删除成功，无返回内容

# 客户端错误
400 Bad Request     - 请求参数错误
401 Unauthorized    - 未认证
403 Forbidden       - 无权限
404 Not Found       - 资源不存在
409 Conflict        - 资源冲突
422 Unprocessable   - 业务校验失败

# 服务端错误
500 Internal Error  - 服务器内部错误
502 Bad Gateway     - 网关错误
503 Service Unavailable - 服务不可用
```

## Request/Response Format

### Standard Response Structure

```json
{
  "code": "SUCCESS",
  "message": "操作成功",
  "data": {
    // 业务数据
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "traceId": "abc123"
}
```

### Pagination Response

```json
{
  "code": "SUCCESS",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

### Error Response

```json
{
  "code": "VALIDATION_ERROR",
  "message": "参数校验失败",
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "traceId": "abc123"
}
```

## API Contract Template

```yaml
# API Contract: User Management

endpoint: /api/v1/users
version: v1
module: client-backend

# Create User
POST /api/v1/users:
  description: 创建新用户
  auth: required
  request:
    headers:
      Content-Type: application/json
      Authorization: Bearer {token}
    body:
      username:
        type: string
        required: true
        minLength: 3
        maxLength: 50
      email:
        type: string
        required: true
        format: email
      password:
        type: string
        required: true
        minLength: 8
  response:
    201:
      description: 创建成功
      body:
        code: SUCCESS
        data:
          id: number
          username: string
          email: string
          createdAt: datetime
    400:
      description: 参数错误
    409:
      description: 用户名或邮箱已存在

# Get User
GET /api/v1/users/{id}:
  description: 获取用户详情
  auth: required
  params:
    id:
      type: number
      required: true
  response:
    200:
      description: 成功
    404:
      description: 用户不存在
```

## Frontend-Backend Contract Workflow

### Step 1: Define Contract

```typescript
// shared/contracts/user.contract.ts

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  createdAt: string;
}

export interface ApiResponse<T> {
  code: string;
  message: string;
  data: T;
}
```

### Step 2: Backend Implementation

```java
@PostMapping("/users")
public ResponseEntity<ApiResponse<UserResponse>> createUser(
    @Valid @RequestBody CreateUserRequest request) {
    User user = userService.create(request);
    return ResponseEntity.status(201)
        .body(ApiResponse.success(UserResponse.from(user)));
}
```

### Step 3: Frontend Implementation

```typescript
// api/modules/user.api.ts
export const userApi = {
  create: (data: CreateUserRequest): Promise<ApiResponse<UserResponse>> => {
    return httpClient.post('/api/v1/users', data);
  }
};

// services/user.service.ts
export class UserService {
  async createUser(data: CreateUserRequest): Promise<UserResponse> {
    const response = await userApi.create(data);
    return response.data;
  }
}
```

## Error Code Standards

```typescript
// shared/constants/error-codes.ts

export const ErrorCodes = {
  // 通用错误 (1xxxx)
  SUCCESS: '10000',
  UNKNOWN_ERROR: '10001',
  VALIDATION_ERROR: '10002',
  
  // 认证错误 (2xxxx)
  UNAUTHORIZED: '20001',
  TOKEN_EXPIRED: '20002',
  FORBIDDEN: '20003',
  
  // 用户模块 (3xxxx)
  USER_NOT_FOUND: '30001',
  USER_ALREADY_EXISTS: '30002',
  INVALID_PASSWORD: '30003',
  
  // 订单模块 (4xxxx)
  ORDER_NOT_FOUND: '40001',
  ORDER_CANNOT_CANCEL: '40002',
} as const;
```

## Versioning Strategy

```
# URL版本控制
/api/v1/users
/api/v2/users

# Header版本控制
Accept: application/vnd.api+json; version=1

# 版本兼容规则
- v1 保持向后兼容
- 破坏性变更发布新版本
- 旧版本保留至少6个月
```
