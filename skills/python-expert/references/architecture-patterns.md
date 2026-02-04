# Python 架构模式指南

## 分层架构 (Layered Architecture)

### 标准四层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation)                      │
│  职责: 处理HTTP请求、参数验证、响应序列化、错误处理              │
│  组件: Controllers, Routers, Schemas, Middleware             │
├─────────────────────────────────────────────────────────────┤
│                    应用层 (Application)                       │
│  职责: 用例编排、事务管理、跨领域协调                           │
│  组件: Services, Use Cases, DTOs                             │
├─────────────────────────────────────────────────────────────┤
│                    领域层 (Domain)                            │
│  职责: 核心业务逻辑、业务规则、领域模型                         │
│  组件: Entities, Value Objects, Domain Services, Events      │
├─────────────────────────────────────────────────────────────┤
│                    基础设施层 (Infrastructure)                 │
│  职责: 技术实现、外部服务集成、持久化                           │
│  组件: Repositories, External APIs, Database, Cache          │
└─────────────────────────────────────────────────────────────┘
```

### 层间依赖规则

```python
# 依赖方向：上层 → 下层
# 表现层 → 应用层 → 领域层 ← 基础设施层

# 正确：上层依赖下层
from domain.entities import User
from application.services import UserService

# 错误：下层依赖上层
# from presentation.schemas import UserResponse  # 领域层不应导入表现层
```

---

## 目录结构模板

### 小型项目结构

```
project/
├── main.py                 # 应用入口
├── config.py               # 配置
├── models.py               # 数据模型
├── schemas.py              # 请求/响应模型
├── services.py             # 业务逻辑
├── repositories.py         # 数据访问
├── routes.py               # 路由定义
└── utils.py                # 工具函数
```

### 中型项目结构

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py             # 应用入口
│   ├── config.py           # 配置管理
│   ├── dependencies.py     # 依赖注入
│   │
│   ├── api/                # API层
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   └── orders.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── logging.py
│   │
│   ├── schemas/            # 请求/响应模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   │
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   │
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   │
│   ├── repositories/       # 数据访问
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   └── order_repository.py
│   │
│   └── core/               # 核心模块
│       ├── __init__.py
│       ├── exceptions.py
│       ├── logging.py
│       └── security.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_users.py
│   └── test_orders.py
│
├── alembic/                # 数据库迁移
├── pyproject.toml
└── README.md
```

### 大型项目结构（领域驱动）

```
project/
├── src/
│   ├── __init__.py
│   │
│   ├── shared/                     # 共享内核
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entity.py           # 实体基类
│   │   │   ├── value_object.py     # 值对象基类
│   │   │   └── events.py           # 领域事件基类
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── cache.py
│   │   │   └── message_bus.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   │
│   ├── user/                       # 用户领域
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── email.py
│   │   │   │   └── password.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_domain_service.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_events.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── user_repository.py  # 接口定义
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_service.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   └── create_user.py
│   │   │   └── queries/
│   │   │       ├── __init__.py
│   │   │       └── get_user.py
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── sql_user_repository.py  # 具体实现
│   │   └── presentation/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── schemas.py
│   │
│   ├── order/                      # 订单领域
│   │   └── ...                     # 类似结构
│   │
│   └── main.py                     # 应用入口
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── pyproject.toml
```

---

## 仓储模式 (Repository Pattern)

### 仓储接口定义

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """仓储抽象基类"""

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """根据ID获取实体"""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """获取所有实体"""
        pass

    @abstractmethod
    async def add(self, entity: T) -> T:
        """添加实体"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """更新实体"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """删除实体"""
        pass

class UserRepository(Repository['User']):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional['User']:
        """根据邮箱获取用户"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        pass
```

### 仓储实现

```python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy用户仓储实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        row = result.scalar_one_or_none()
        return User.from_orm(row) if row else None

    async def get_all(self) -> List[User]:
        result = await self.session.execute(select(UserModel))
        return [User.from_orm(row) for row in result.scalars().all()]

    async def add(self, entity: User) -> User:
        model = UserModel(**entity.dict())
        self.session.add(model)
        await self.session.flush()
        return User.from_orm(model)

    async def update(self, entity: User) -> User:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == entity.id)
        )
        model = result.scalar_one()
        for key, value in entity.dict(exclude={'id'}).items():
            setattr(model, key, value)
        await self.session.flush()
        return User.from_orm(model)

    async def delete(self, id: str) -> bool:
        result = await self.session.execute(
            sql_delete(UserModel).where(UserModel.id == id)
        )
        return result.rowcount > 0

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        row = result.scalar_one_or_none()
        return User.from_orm(row) if row else None

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email).limit(1)
        )
        return result.scalar_one_or_none() is not None
```

---

## 工作单元模式 (Unit of Work)

```python
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class UnitOfWork(ABC):
    """工作单元抽象"""

    @abstractmethod
    async def __aenter__(self) -> 'UnitOfWork':
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @property
    @abstractmethod
    def users(self) -> UserRepository:
        pass

    @property
    @abstractmethod
    def orders(self) -> OrderRepository:
        pass

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy工作单元实现"""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session = None

    async def __aenter__(self) -> 'SQLAlchemyUnitOfWork':
        self._session = self.session_factory()
        self._users = SQLAlchemyUserRepository(self._session)
        self._orders = SQLAlchemyOrderRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    @property
    def users(self) -> UserRepository:
        return self._users

    @property
    def orders(self) -> OrderRepository:
        return self._orders

# 使用示例
async def create_order_with_user(uow: UnitOfWork, user_data: dict, order_data: dict):
    async with uow:
        # 创建用户
        user = User(**user_data)
        await uow.users.add(user)

        # 创建订单
        order = Order(user_id=user.id, **order_data)
        await uow.orders.add(order)

        # 提交事务
        await uow.commit()
```

---

## 依赖注入 (Dependency Injection)

### 简单容器实现

```python
from typing import TypeVar, Type, Callable, Dict, Any
from functools import wraps

T = TypeVar('T')

class Container:
    """依赖注入容器"""

    def __init__(self):
        self._services: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(
        self,
        interface: Type[T],
        factory: Callable[..., T],
        singleton: bool = False
    ) -> None:
        """注册服务"""
        if singleton:
            self._services[interface] = lambda: self._get_singleton(interface, factory)
        else:
            self._services[interface] = factory

    def _get_singleton(self, interface: Type[T], factory: Callable[..., T]) -> T:
        if interface not in self._singletons:
            self._singletons[interface] = factory()
        return self._singletons[interface]

    def resolve(self, interface: Type[T]) -> T:
        """解析服务"""
        if interface not in self._services:
            raise ValueError(f"Service not registered: {interface}")
        return self._services[interface]()

    def inject(self, func: Callable) -> Callable:
        """注入装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数参数类型注解
            hints = func.__annotations__
            for name, hint in hints.items():
                if name not in kwargs and hint in self._services:
                    kwargs[name] = self.resolve(hint)
            return func(*args, **kwargs)
        return wrapper

# 使用示例
container = Container()

# 注册服务
container.register(Database, lambda: PostgresDatabase(config.DATABASE_URL), singleton=True)
container.register(UserRepository, lambda: SQLUserRepository(container.resolve(Database)))
container.register(UserService, lambda: UserService(container.resolve(UserRepository)))

# 解析服务
user_service = container.resolve(UserService)
```

### FastAPI 依赖注入

```python
from fastapi import Depends, FastAPI
from typing import AsyncGenerator

app = FastAPI()

# 数据库会话依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# 仓储依赖
async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return SQLAlchemyUserRepository(db)

# 服务依赖
async def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    cache: CacheClient = Depends(get_cache)
) -> UserService:
    return UserService(repository, cache)

# 在路由中使用
@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

---

## CQRS 模式 (Command Query Responsibility Segregation)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic

# 命令基类
@dataclass
class Command(ABC):
    """命令基类"""
    pass

# 查询基类
@dataclass
class Query(ABC):
    """查询基类"""
    pass

T = TypeVar('T')

# 命令处理器
class CommandHandler(ABC, Generic[T]):
    @abstractmethod
    async def handle(self, command: T) -> None:
        pass

# 查询处理器
class QueryHandler(ABC, Generic[T]):
    @abstractmethod
    async def handle(self, query: T) -> Any:
        pass

# 具体命令
@dataclass
class CreateUserCommand(Command):
    email: str
    name: str
    password: str

@dataclass
class UpdateUserCommand(Command):
    user_id: str
    name: str

# 具体查询
@dataclass
class GetUserQuery(Query):
    user_id: str

@dataclass
class ListUsersQuery(Query):
    page: int = 1
    page_size: int = 20

# 命令处理器实现
class CreateUserCommandHandler(CommandHandler[CreateUserCommand]):
    def __init__(self, repository: UserRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    async def handle(self, command: CreateUserCommand) -> None:
        user = User.create(
            email=command.email,
            name=command.name,
            password_hash=hash_password(command.password)
        )
        await self.repository.add(user)
        await self.event_bus.publish(UserCreatedEvent(user_id=user.id))

# 查询处理器实现
class GetUserQueryHandler(QueryHandler[GetUserQuery]):
    def __init__(self, read_db: ReadDatabase):
        self.read_db = read_db

    async def handle(self, query: GetUserQuery) -> UserDTO:
        # 从读库查询，可以是优化过的视图或缓存
        return await self.read_db.get_user(query.user_id)

# 消息总线
class MessageBus:
    def __init__(self):
        self._command_handlers: dict[type, CommandHandler] = {}
        self._query_handlers: dict[type, QueryHandler] = {}

    def register_command_handler(
        self,
        command_type: type,
        handler: CommandHandler
    ) -> None:
        self._command_handlers[command_type] = handler

    def register_query_handler(
        self,
        query_type: type,
        handler: QueryHandler
    ) -> None:
        self._query_handlers[query_type] = handler

    async def execute_command(self, command: Command) -> None:
        handler = self._command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for command: {type(command)}")
        await handler.handle(command)

    async def execute_query(self, query: Query) -> Any:
        handler = self._query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for query: {type(query)}")
        return await handler.handle(query)
```

---

## 事件驱动架构 (Event-Driven Architecture)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Dict, Any
from uuid import uuid4
import asyncio

@dataclass
class DomainEvent(ABC):
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserCreatedEvent(DomainEvent):
    user_id: str = ""
    email: str = ""

@dataclass
class OrderPlacedEvent(DomainEvent):
    order_id: str = ""
    user_id: str = ""
    total_amount: float = 0.0

class EventHandler(ABC):
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        pass

class EventBus:
    """事件总线"""

    def __init__(self):
        self._handlers: Dict[type, List[EventHandler]] = {}
        self._async_handlers: Dict[type, List[Callable]] = {}

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_async(self, event_type: type, handler: Callable) -> None:
        """订阅异步处理器"""
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """发布事件"""
        event_type = type(event)

        # 同步处理器
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            await handler.handle(event)

        # 异步处理器（并发执行）
        async_handlers = self._async_handlers.get(event_type, [])
        if async_handlers:
            await asyncio.gather(
                *[handler(event) for handler in async_handlers],
                return_exceptions=True
            )

# 事件处理器示例
class SendWelcomeEmailHandler(EventHandler):
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def handle(self, event: UserCreatedEvent) -> None:
        await self.email_service.send_welcome_email(event.email)

class UpdateUserStatsHandler(EventHandler):
    def __init__(self, stats_service: StatsService):
        self.stats_service = stats_service

    async def handle(self, event: UserCreatedEvent) -> None:
        await self.stats_service.increment_user_count()

# 配置事件总线
event_bus = EventBus()
event_bus.subscribe(UserCreatedEvent, SendWelcomeEmailHandler(email_service))
event_bus.subscribe(UserCreatedEvent, UpdateUserStatsHandler(stats_service))

# 发布事件
await event_bus.publish(UserCreatedEvent(user_id="123", email="user@example.com"))
```

---

## 插件架构 (Plugin Architecture)

```python
from abc import ABC, abstractmethod
from typing import Dict, Type, List
from importlib import import_module
from pathlib import Path

class Plugin(ABC):
    """插件基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @abstractmethod
    def initialize(self, app: 'Application') -> None:
        """初始化插件"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭插件"""
        pass

class PluginManager:
    """插件管理器"""

    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}

    def register(self, plugin_class: Type[Plugin]) -> None:
        """注册插件类"""
        name = plugin_class.__name__
        self._plugin_classes[name] = plugin_class

    def discover(self, plugin_dir: str) -> None:
        """自动发现插件"""
        plugin_path = Path(plugin_dir)
        for file in plugin_path.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module_name = f"plugins.{file.stem}"
            module = import_module(module_name)

            # 查找Plugin子类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Plugin)
                    and attr is not Plugin
                ):
                    self.register(attr)

    def load(self, name: str, app: 'Application') -> Plugin:
        """加载插件"""
        if name in self._plugins:
            return self._plugins[name]

        if name not in self._plugin_classes:
            raise ValueError(f"Plugin not found: {name}")

        plugin = self._plugin_classes[name]()
        plugin.initialize(app)
        self._plugins[name] = plugin
        return plugin

    def load_all(self, app: 'Application') -> List[Plugin]:
        """加载所有插件"""
        return [self.load(name, app) for name in self._plugin_classes]

    def unload(self, name: str) -> None:
        """卸载插件"""
        if name in self._plugins:
            self._plugins[name].shutdown()
            del self._plugins[name]

    def unload_all(self) -> None:
        """卸载所有插件"""
        for name in list(self._plugins.keys()):
            self.unload(name)

# 插件示例
class LoggingPlugin(Plugin):
    @property
    def name(self) -> str:
        return "logging"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, app: 'Application') -> None:
        app.add_middleware(LoggingMiddleware())

    def shutdown(self) -> None:
        pass

class MetricsPlugin(Plugin):
    @property
    def name(self) -> str:
        return "metrics"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, app: 'Application') -> None:
        app.add_route("/metrics", self.metrics_endpoint)

    def shutdown(self) -> None:
        pass

    async def metrics_endpoint(self, request):
        return {"status": "ok"}
```

---

## 模块化设计原则

### 1. 高内聚

```python
# 好的设计：相关功能放在一起
class UserModule:
    """用户模块：包含所有用户相关功能"""

    def __init__(self):
        self.repository = UserRepository()
        self.service = UserService(self.repository)
        self.validator = UserValidator()

    def create_user(self, data: dict) -> User:
        self.validator.validate(data)
        return self.service.create(data)

    def get_user(self, user_id: str) -> User:
        return self.service.get(user_id)
```

### 2. 低耦合

```python
# 通过接口解耦
from typing import Protocol

class NotificationSender(Protocol):
    def send(self, recipient: str, message: str) -> bool: ...

class UserService:
    def __init__(self, notification: NotificationSender):
        # 依赖抽象，不依赖具体实现
        self.notification = notification

    def create_user(self, data: dict) -> User:
        user = User(**data)
        # 不关心具体是邮件还是短信
        self.notification.send(user.email, "Welcome!")
        return user
```

### 3. 接口隔离

```python
# 拆分大接口为小接口
class Readable(Protocol):
    def read(self, id: str) -> Any: ...

class Writable(Protocol):
    def write(self, data: Any) -> None: ...

class Deletable(Protocol):
    def delete(self, id: str) -> bool: ...

# 只依赖需要的接口
class ReportGenerator:
    def __init__(self, data_source: Readable):
        # 只需要读取能力
        self.data_source = data_source

    def generate(self, id: str) -> str:
        data = self.data_source.read(id)
        return format_report(data)
```
