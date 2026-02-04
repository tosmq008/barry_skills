# Python API 设计指南

## RESTful API 设计规范

### URL 设计原则

```
┌─────────────────────────────────────────────────────────────┐
│                    RESTful URL 设计                          │
├─────────────────────────────────────────────────────────────┤
│  资源命名: 使用名词复数，不使用动词                            │
│  ✓ GET /users          ✗ GET /getUsers                      │
│  ✓ POST /orders        ✗ POST /createOrder                  │
├─────────────────────────────────────────────────────────────┤
│  层级关系: 使用嵌套表示从属关系                                │
│  GET /users/{id}/orders     用户的订单列表                    │
│  GET /orders/{id}/items     订单的商品列表                    │
├─────────────────────────────────────────────────────────────┤
│  查询参数: 用于过滤、排序、分页                                │
│  GET /users?status=active&sort=-created_at&page=1           │
└─────────────────────────────────────────────────────────────┘
```

### HTTP 方法语义

| 方法 | 语义 | 幂等性 | 示例 |
|------|------|--------|------|
| GET | 获取资源 | 是 | `GET /users/123` |
| POST | 创建资源 | 否 | `POST /users` |
| PUT | 全量更新 | 是 | `PUT /users/123` |
| PATCH | 部分更新 | 是 | `PATCH /users/123` |
| DELETE | 删除资源 | 是 | `DELETE /users/123` |

### HTTP 状态码规范

```python
# 成功响应
200 OK              # 请求成功
201 Created         # 创建成功
204 No Content      # 删除成功，无返回内容

# 客户端错误
400 Bad Request     # 请求参数错误
401 Unauthorized    # 未认证
403 Forbidden       # 无权限
404 Not Found       # 资源不存在
409 Conflict        # 资源冲突
422 Unprocessable   # 验证失败

# 服务端错误
500 Internal Error  # 服务器内部错误
502 Bad Gateway     # 网关错误
503 Unavailable     # 服务不可用
```

---

## API 版本控制

### 版本策略

```python
# 方式1: URL路径版本 (推荐)
GET /api/v1/users
GET /api/v2/users

# 方式2: 请求头版本
GET /api/users
Header: X-API-Version: 2

# 方式3: 查询参数版本
GET /api/users?version=2
```

### FastAPI 版本实现

```python
from fastapi import FastAPI, APIRouter

# 创建版本路由
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users")
async def get_users_v1():
    return {"version": "v1", "users": []}

@v2_router.get("/users")
async def get_users_v2():
    # v2 返回更丰富的数据结构
    return {"version": "v2", "data": {"users": [], "total": 0}}

app = FastAPI()
app.include_router(v1_router)
app.include_router(v2_router)
```

---

## 请求响应格式设计

### 统一响应格式

```python
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    code: int = 0
    message: str = "success"
    data: List[T] = []
    pagination: dict = {
        "page": 1,
        "page_size": 20,
        "total": 0,
        "total_pages": 0
    }

# 使用示例
@router.get("/users/{user_id}", response_model=ResponseModel[UserResponse])
async def get_user(user_id: str):
    user = await user_service.get(user_id)
    return ResponseModel(data=user)
```

### 错误响应格式

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ErrorDetail(BaseModel):
    """错误详情"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    """错误响应格式"""
    code: int
    message: str
    errors: Optional[List[ErrorDetail]] = None
    trace_id: Optional[str] = None

# 错误响应示例
{
    "code": 422,
    "message": "Validation failed",
    "errors": [
        {"field": "email", "message": "Invalid email format", "code": "INVALID_EMAIL"},
        {"field": "password", "message": "Password too short", "code": "PASSWORD_TOO_SHORT"}
    ],
    "trace_id": "abc-123-def"
}
```

### 请求模型设计

```python
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime

class CreateUserRequest(BaseModel):
    """创建用户请求"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "securepass123"
            }
        }

class UpdateUserRequest(BaseModel):
    """更新用户请求 - 所有字段可选"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = None
    avatar: Optional[str] = None

class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 支持 ORM 模型转换
```

---

## 认证授权设计

### JWT 认证实现

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime
    type: str  # access / refresh

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload.get("sub")
    except JWTError:
        return None
```

### 依赖注入认证

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

# 权限检查装饰器
def require_permission(permission: str):
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    return permission_checker

# 使用示例
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permission("user:delete"))
):
    await user_service.delete(user_id)
    return {"message": "User deleted"}
```

---

## 分页、过滤、排序

### 通用分页参数

```python
from fastapi import Query
from pydantic import BaseModel
from typing import Optional, List, TypeVar, Generic

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Query(1, ge=1, description="页码")
    page_size: int = Query(20, ge=1, le=100, description="每页数量")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    """分页结果"""
    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
```

### 过滤和排序

```python
from enum import Enum
from typing import Optional, List

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class UserFilter(BaseModel):
    """用户过滤条件"""
    status: Optional[str] = None
    role: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search: Optional[str] = None  # 模糊搜索

class UserSort(BaseModel):
    """用户排序"""
    field: str = "created_at"
    order: SortOrder = SortOrder.DESC

# 路由使用
@router.get("/users", response_model=Page[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    user_service: UserService = Depends(get_user_service)
):
    filters = UserFilter(status=status, role=role, search=search)
    sort = UserSort(field=sort_by, order=sort_order)

    users, total = await user_service.list(
        filters=filters,
        sort=sort,
        offset=pagination.offset,
        limit=pagination.limit
    )

    return Page(
        items=users,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )
```

### 游标分页（大数据量）

```python
from typing import Optional
import base64
import json

class CursorPagination:
    """游标分页 - 适合大数据量"""

    @staticmethod
    def encode_cursor(data: dict) -> str:
        return base64.b64encode(json.dumps(data).encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> dict:
        return json.loads(base64.b64decode(cursor.encode()).decode())

@router.get("/posts")
async def list_posts(
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, le=100)
):
    if cursor:
        cursor_data = CursorPagination.decode_cursor(cursor)
        last_id = cursor_data["last_id"]
        posts = await post_service.list_after(last_id, limit)
    else:
        posts = await post_service.list(limit)

    next_cursor = None
    if len(posts) == limit:
        next_cursor = CursorPagination.encode_cursor({"last_id": posts[-1].id})

    return {
        "items": posts,
        "next_cursor": next_cursor
    }
```

---

## 文件上传下载

### 文件上传

```python
from fastapi import UploadFile, File, HTTPException
from typing import List
import aiofiles
import uuid
import os

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file(file: UploadFile) -> None:
    """验证上传文件"""
    # 检查扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type not allowed: {ext}")

    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    await file.seek(0)  # 重置文件指针

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    await validate_file(file)

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # 异步写入文件
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)

    return {"filename": filename, "url": f"/files/{filename}"}

@router.post("/upload/multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        await validate_file(file)
        # 处理每个文件...
        results.append({"filename": file.filename})
    return {"files": results}
```

### 文件下载

```python
from fastapi.responses import FileResponse, StreamingResponse
import aiofiles

@router.get("/files/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(404, "File not found")

    return FileResponse(
        filepath,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.get("/files/{filename}/stream")
async def stream_file(filename: str):
    """流式下载大文件"""
    filepath = os.path.join(UPLOAD_DIR, filename)

    async def file_iterator():
        async with aiofiles.open(filepath, 'rb') as f:
            while chunk := await f.read(8192):
                yield chunk

    return StreamingResponse(
        file_iterator(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

---

## WebSocket 实时通信

### WebSocket 基础实现

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # 从所有房间移除
        for room in self.rooms.values():
            room.discard(user_id)

    async def send_personal(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

    async def broadcast_to_room(self, room: str, message: dict):
        if room in self.rooms:
            for user_id in self.rooms[room]:
                await self.send_personal(user_id, message)

    def join_room(self, user_id: str, room: str):
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(user_id)

    def leave_room(self, user_id: str, room: str):
        if room in self.rooms:
            self.rooms[room].discard(user_id)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

async def handle_message(user_id: str, data: dict):
    """处理 WebSocket 消息"""
    action = data.get("action")

    if action == "join_room":
        manager.join_room(user_id, data["room"])
    elif action == "leave_room":
        manager.leave_room(user_id, data["room"])
    elif action == "send_message":
        await manager.broadcast_to_room(data["room"], {
            "type": "message",
            "from": user_id,
            "content": data["content"]
        })
```

---

## 异常处理中间件

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
import uuid

app = FastAPI()

class APIException(Exception):
    """API 异常基类"""
    def __init__(self, code: int, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details

class BusinessError(APIException):
    """业务错误"""
    pass

class NotFoundError(APIException):
    """资源不存在"""
    def __init__(self, resource: str, id: str):
        super().__init__(404, f"{resource} not found: {id}")

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "trace_id": str(uuid.uuid4())
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Validation failed",
            "errors": errors
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = str(uuid.uuid4())
    # 记录详细错误日志
    logger.error(f"[{trace_id}] Unhandled exception: {exc}\n{traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal server error",
            "trace_id": trace_id
        }
    )
```
