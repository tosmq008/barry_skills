---
name: python-expert
description: "Python技术专家，以资深工程师视角进行开发任务。从需求理解、模型设计、架构分层、复用性、扩展性、稳定性、高性能等维度全面考量。精通多线程并发、缓存策略、设计模式、RESTful API设计、数据库建模，确保代码质量和系统可靠性。适用于Python项目的架构设计、API开发、数据库设计、代码实现、性能优化和代码审查。"
license: MIT
compatibility: "适用于Python 3.8+项目。支持asyncio、threading、multiprocessing并发模型。兼容主流框架如FastAPI、Django、Flask等。"
metadata:
  category: development
  phase: implementation
  version: "1.0.0"
  author: python-expert
allowed-tools: bash read_file write_file grep glob
---

# Python Expert Skill

作为Python技术专家，以资深工程师的视角进行开发任务，从需求理解到代码实现，全面考虑复用性、扩展性、稳定性和高性能。

## When to Use

**适用场景：**
- Python项目架构设计与实现
- 复杂业务逻辑的模块化设计
- 高性能Python应用开发
- 多线程/异步并发编程
- 缓存策略设计与实现
- RESTful API设计与开发
- 数据库模型设计与优化
- 前后端数据交互设计
- 代码重构与优化
- 代码审查与质量把控

**不适用：**
- 简单的脚本编写（无架构需求）
- 非Python语言项目
- 纯运维部署任务

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Python技术专家工作流程                          │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: 需求分析          Phase 2: 模型设计                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 需求理解与澄清  │  ──▶  │ 领域模型设计    │                  │
│  │ 边界条件识别    │       │ 数据结构设计    │                  │
│  │ 非功能需求分析  │       │ 接口契约定义    │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 3: 架构设计          Phase 4: 代码实现                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 分层架构设计    │  ──▶  │ 核心逻辑实现    │                  │
│  │ 模块划分        │       │ 并发处理实现    │                  │
│  │ 依赖关系设计    │       │ 缓存策略实现    │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 5: 质量保障          Phase 6: 性能优化                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 单元测试编写    │  ──▶  │ 性能瓶颈分析    │                  │
│  │ 代码审查        │       │ 优化方案实施    │                  │
│  │ 异常处理完善    │       │ 基准测试验证    │                  │
│  └─────────────────┘       └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 需求分析 (Requirement Analysis)

### 1.1 需求理解与澄清

**必须明确的内容：**

| 维度 | 关键问题 | 输出 |
|------|----------|------|
| 功能需求 | 系统需要做什么？ | 功能清单 |
| 输入输出 | 数据从哪来？到哪去？ | 数据流图 |
| 业务规则 | 有哪些约束和规则？ | 规则列表 |
| 用户场景 | 谁在什么情况下使用？ | 用例描述 |

### 1.2 边界条件识别

**必须考虑的边界：**
- 空值/None处理
- 边界值（最大/最小/零）
- 异常输入（类型错误、格式错误）
- 并发访问场景
- 资源限制（内存、连接数、文件句柄）

### 1.3 非功能需求分析

| 维度 | 指标 | 考量点 |
|------|------|--------|
| 性能 | 响应时间、吞吐量 | 是否需要异步/并发 |
| 可靠性 | 错误率、恢复时间 | 重试机制、降级策略 |
| 可扩展性 | 数据量增长、功能扩展 | 模块化、插件化设计 |
| 可维护性 | 代码复杂度、文档 | 清晰的分层和命名 |

---

## Phase 2: 模型设计 (Model Design)

> ⚠️ **执行前必须读取 `references/design-principles.md` 获取设计原则指南**

### 2.1 领域模型设计

**设计步骤：**
1. 识别核心实体（Entity）
2. 定义值对象（Value Object）
3. 确定聚合根（Aggregate Root）
4. 设计领域服务（Domain Service）

**示例结构：**
```python
# 实体基类
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic
from datetime import datetime

T = TypeVar('T')

@dataclass
class Entity(ABC, Generic[T]):
    """实体基类，具有唯一标识"""
    id: T
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

# 值对象示例
@dataclass(frozen=True)
class Money:
    """值对象：金额，不可变"""
    amount: Decimal
    currency: str = "CNY"

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

### 2.2 数据结构设计

**选择原则：**

| 场景 | 推荐结构 | 原因 |
|------|----------|------|
| 频繁查找 | dict/set | O(1)查找 |
| 有序数据 | list/deque | 保持顺序 |
| 优先级处理 | heapq | O(log n)操作 |
| 缓存场景 | OrderedDict/lru_cache | LRU淘汰 |
| 树形结构 | 自定义类/嵌套dict | 层级关系 |

### 2.3 接口契约定义

**使用Protocol定义接口：**
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Repository(Protocol[T]):
    """仓储接口协议"""
    def get(self, id: str) -> T | None: ...
    def save(self, entity: T) -> None: ...
    def delete(self, id: str) -> bool: ...
    def list(self, **filters) -> list[T]: ...
```

---

## Phase 3: 架构设计 (Architecture Design)

> ⚠️ **执行前必须读取 `references/architecture-patterns.md` 获取架构模式指南**

### 3.1 分层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Python分层架构                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    API层 (api/)                      │   │
│  │  路由定义 | 请求验证 | 响应序列化 | 错误处理          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   服务层 (services/)                 │   │
│  │  业务逻辑 | 事务管理 | 跨模块协调 | 缓存管理          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   仓储层 (repositories/)             │   │
│  │  数据访问 | 查询封装 | 持久化 | 数据映射              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   领域层 (domain/)                   │   │
│  │  实体定义 | 值对象 | 领域服务 | 业务规则              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   基础层 (infrastructure/)           │   │
│  │  数据库连接 | 缓存客户端 | 消息队列 | 外部API         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 模块划分原则

**高内聚低耦合：**
- 单一职责：每个模块只做一件事
- 接口隔离：依赖抽象而非具体实现
- 依赖倒置：高层模块不依赖低层模块

**推荐目录结构：**
```
project/
├── api/                    # API层
│   ├── __init__.py
│   ├── routes/            # 路由定义
│   ├── schemas/           # 请求/响应模型
│   └── dependencies.py    # 依赖注入
├── services/              # 服务层
│   ├── __init__.py
│   └── user_service.py
├── repositories/          # 仓储层
│   ├── __init__.py
│   ├── base.py           # 基础仓储
│   └── user_repository.py
├── domain/               # 领域层
│   ├── __init__.py
│   ├── entities/         # 实体
│   ├── value_objects/    # 值对象
│   └── services/         # 领域服务
├── infrastructure/       # 基础设施层
│   ├── __init__.py
│   ├── database.py       # 数据库连接
│   ├── cache.py          # 缓存客户端
│   └── external/         # 外部服务
├── core/                 # 核心配置
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── exceptions.py     # 异常定义
│   └── logging.py        # 日志配置
└── utils/                # 工具函数
    ├── __init__.py
    └── helpers.py
```

### 3.3 依赖注入设计

```python
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

class Container:
    """简单的依赖注入容器"""
    _instances: dict[type, object] = {}
    _factories: dict[type, Callable] = {}

    @classmethod
    def register(cls, interface: type[T], factory: Callable[[], T]) -> None:
        cls._factories[interface] = factory

    @classmethod
    def resolve(cls, interface: type[T]) -> T:
        if interface not in cls._instances:
            if interface not in cls._factories:
                raise ValueError(f"No factory registered for {interface}")
            cls._instances[interface] = cls._factories[interface]()
        return cls._instances[interface]

# 使用示例
Container.register(UserRepository, lambda: SQLUserRepository(db_session))
Container.register(UserService, lambda: UserService(Container.resolve(UserRepository)))
```

---

## Phase 4: 代码实现 (Code Implementation)

### 4.1 核心逻辑实现

> ⚠️ **执行前必须读取 `references/design-principles.md` 获取SOLID原则指南**

**编码规范：**
- 使用类型注解（Type Hints）
- 遵循PEP 8风格指南
- 编写清晰的docstring
- 合理使用设计模式

**示例：服务层实现**
```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class UserService:
    """用户服务：处理用户相关业务逻辑"""
    repository: UserRepository
    cache: CacheClient
    event_bus: EventBus

    async def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息，优先从缓存读取"""
        # 1. 尝试从缓存获取
        cached = await self.cache.get(f"user:{user_id}")
        if cached:
            return User.from_dict(cached)

        # 2. 从数据库获取
        user = await self.repository.get(user_id)
        if user:
            # 3. 写入缓存
            await self.cache.set(
                f"user:{user_id}",
                user.to_dict(),
                ttl=3600
            )
        return user

    async def create_user(self, data: CreateUserRequest) -> User:
        """创建用户"""
        # 1. 业务验证
        if await self.repository.exists_by_email(data.email):
            raise BusinessError("EMAIL_EXISTS", "邮箱已被注册")

        # 2. 创建实体
        user = User.create(
            email=data.email,
            name=data.name,
            password_hash=hash_password(data.password)
        )

        # 3. 持久化
        await self.repository.save(user)

        # 4. 发布事件
        await self.event_bus.publish(UserCreatedEvent(user_id=user.id))

        return user
```

### 4.2 并发处理实现

> ⚠️ **执行前必须读取 `references/concurrency-guide.md` 获取并发编程指南**

**选择并发模型：**

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| IO密集型 | asyncio | 协程切换开销小 |
| CPU密集型 | multiprocessing | 绑定GIL |
| 混合场景 | ThreadPoolExecutor + asyncio | 灵活组合 |
| 简单并行 | concurrent.futures | API简洁 |

**异步编程示例：**
```python
import asyncio
from typing import List
from contextlib import asynccontextmanager

class AsyncBatchProcessor:
    """异步批处理器"""

    def __init__(self, max_concurrency: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def process_item(self, item: Any) -> Any:
        """处理单个项目，受信号量限制"""
        async with self.semaphore:
            return await self._do_process(item)

    async def process_batch(self, items: List[Any]) -> List[Any]:
        """批量处理，并发执行"""
        tasks = [self.process_item(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _do_process(self, item: Any) -> Any:
        """实际处理逻辑，子类实现"""
        raise NotImplementedError
```

### 4.3 缓存策略实现

> ⚠️ **执行前必须读取 `references/caching-strategies.md` 获取缓存策略指南**

**缓存装饰器：**
```python
from functools import wraps
from typing import Callable, Optional
import hashlib
import json

def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{args}:{kwargs}"
                cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

            # 尝试获取缓存
            cache = get_cache_client()
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return json.loads(cached_value)

            # 执行函数
            result = await func(*args, **kwargs)

            # 写入缓存
            await cache.set(cache_key, json.dumps(result), ex=ttl)

            return result
        return wrapper
    return decorator

# 使用示例
@cached(ttl=3600, key_prefix="user")
async def get_user_profile(user_id: str) -> dict:
    return await fetch_user_from_db(user_id)
```

---

## Phase 5: 质量保障 (Quality Assurance)

> ⚠️ **执行前必须读取 `references/code-review-checklist.md` 获取代码审查清单**

### 5.1 单元测试编写

**测试原则：**
- 每个公共方法都有测试
- 覆盖正常路径和异常路径
- 使用mock隔离外部依赖
- 测试命名清晰表达意图

**测试示例：**
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestUserService:
    """用户服务测试"""

    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return UserService(
            repository=AsyncMock(spec=UserRepository),
            cache=AsyncMock(spec=CacheClient),
            event_bus=AsyncMock(spec=EventBus)
        )

    @pytest.mark.asyncio
    async def test_get_user_from_cache(self, service):
        """测试从缓存获取用户"""
        # Arrange
        user_data = {"id": "123", "name": "Test"}
        service.cache.get.return_value = user_data

        # Act
        result = await service.get_user("123")

        # Assert
        assert result.id == "123"
        service.repository.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_cache_miss(self, service):
        """测试缓存未命中时从数据库获取"""
        # Arrange
        service.cache.get.return_value = None
        service.repository.get.return_value = User(id="123", name="Test")

        # Act
        result = await service.get_user("123")

        # Assert
        assert result.id == "123"
        service.cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self, service):
        """测试创建用户时邮箱已存在"""
        # Arrange
        service.repository.exists_by_email.return_value = True

        # Act & Assert
        with pytest.raises(BusinessError) as exc:
            await service.create_user(CreateUserRequest(
                email="test@example.com",
                name="Test",
                password="password123"
            ))
        assert exc.value.code == "EMAIL_EXISTS"
```

### 5.2 代码审查要点

**审查清单：**

| 类别 | 检查项 |
|------|--------|
| 正确性 | 逻辑是否正确？边界条件是否处理？ |
| 安全性 | 是否有注入风险？敏感数据是否保护？ |
| 性能 | 是否有N+1查询？是否需要缓存？ |
| 可读性 | 命名是否清晰？复杂逻辑是否有注释？ |
| 可维护性 | 是否遵循SOLID原则？是否易于测试？ |
| 异常处理 | 异常是否被正确捕获和处理？ |

### 5.3 异常处理完善

**异常层次设计：**
```python
class BaseError(Exception):
    """基础异常类"""
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

class BusinessError(BaseError):
    """业务异常：可预期的业务错误"""
    pass

class ValidationError(BaseError):
    """验证异常：输入验证失败"""
    pass

class InfrastructureError(BaseError):
    """基础设施异常：外部服务错误"""
    pass

# 全局异常处理
async def error_handler(request, exc):
    if isinstance(exc, BusinessError):
        return JSONResponse(
            status_code=400,
            content={"code": exc.code, "message": exc.message}
        )
    elif isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=422,
            content={"code": exc.code, "message": exc.message, "details": exc.details}
        )
    else:
        # 记录未知异常
        logger.exception("Unexpected error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"code": "INTERNAL_ERROR", "message": "服务器内部错误"}
        )
```

---

## Phase 6: 性能优化 (Performance Optimization)

> ⚠️ **执行前必须读取 `references/performance-optimization.md` 获取性能优化指南**

### 6.1 性能瓶颈分析

**分析工具：**

| 工具 | 用途 | 命令 |
|------|------|------|
| cProfile | CPU分析 | `python -m cProfile -s cumtime script.py` |
| memory_profiler | 内存分析 | `@profile` 装饰器 |
| line_profiler | 行级分析 | `@profile` 装饰器 |
| py-spy | 采样分析 | `py-spy top --pid PID` |

**常见瓶颈：**
- 数据库N+1查询
- 同步阻塞IO
- 大量小对象创建
- 不必要的序列化/反序列化
- 锁竞争

### 6.2 优化方案实施

**数据库优化：**
```python
# 避免N+1查询：使用预加载
users = await session.execute(
    select(User)
    .options(selectinload(User.orders))
    .where(User.active == True)
)

# 批量操作
await session.execute(
    insert(User),
    [{"name": name} for name in names]
)
```

**内存优化：**
```python
# 使用生成器处理大数据
def process_large_file(filepath: str):
    with open(filepath) as f:
        for line in f:
            yield process_line(line)

# 使用__slots__减少内存
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

**并发优化：**
```python
# 使用连接池
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)

# 批量并发请求
async def fetch_all(urls: list[str]) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### 6.3 基准测试验证

**性能测试框架：**
```python
import pytest
import time
from statistics import mean, stdev

class TestPerformance:
    """性能测试"""

    @pytest.mark.benchmark
    def test_user_query_performance(self, benchmark):
        """测试用户查询性能"""
        result = benchmark(lambda: sync_get_user("123"))

        # 断言性能指标
        assert benchmark.stats['mean'] < 0.1  # 平均响应时间 < 100ms
        assert benchmark.stats['max'] < 0.5   # 最大响应时间 < 500ms

    @pytest.mark.asyncio
    async def test_batch_processing_throughput(self):
        """测试批处理吞吐量"""
        items = list(range(1000))

        start = time.perf_counter()
        await processor.process_batch(items)
        elapsed = time.perf_counter() - start

        throughput = len(items) / elapsed
        assert throughput > 100  # 吞吐量 > 100 items/s
```

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 技术设计文档 | `docs/technical-design.md` | 架构和设计决策 |
| API文档 | `docs/api.md` | 接口定义和示例 |
| 代码审查报告 | `docs/code-review.md` | 审查结果和建议 |
| 性能测试报告 | `docs/performance-report.md` | 性能指标和优化 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/design-principles.md` | SOLID原则和设计模式 |
| `references/architecture-patterns.md` | 架构模式和最佳实践 |
| `references/concurrency-guide.md` | 并发编程指南 |
| `references/caching-strategies.md` | 缓存策略指南 |
| `references/performance-optimization.md` | 性能优化指南 |
| `references/code-review-checklist.md` | 代码审查清单 |
| `references/api-design-guide.md` | API设计与前后端交互 |
| `references/database-design-guide.md` | 数据库设计指南 |

---

## Related Skills

- `test-expert` - 测试专家（系统测试）
- `tech-plan-template` - 技术方案模板
- `development-workflow` - 开发工作流
- `quant-architect` - 量化架构师（高性能系统）
