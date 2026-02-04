# Python 设计原则指南

## SOLID 原则

### 1. 单一职责原则 (Single Responsibility Principle)

**定义：** 一个类应该只有一个引起它变化的原因。

**反例：**
```python
# 违反SRP：一个类做了太多事情
class UserManager:
    def create_user(self, data: dict) -> User:
        # 创建用户
        pass

    def send_welcome_email(self, user: User) -> None:
        # 发送邮件
        pass

    def generate_report(self, users: list[User]) -> str:
        # 生成报告
        pass

    def export_to_csv(self, users: list[User]) -> bytes:
        # 导出CSV
        pass
```

**正例：**
```python
# 遵循SRP：每个类只负责一件事
class UserService:
    """用户业务逻辑"""
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, data: CreateUserRequest) -> User:
        user = User.create(**data.dict())
        self.repository.save(user)
        return user

class EmailService:
    """邮件服务"""
    def send_welcome_email(self, user: User) -> None:
        # 发送邮件逻辑
        pass

class ReportGenerator:
    """报告生成器"""
    def generate_user_report(self, users: list[User]) -> str:
        # 生成报告逻辑
        pass

class DataExporter:
    """数据导出器"""
    def export_to_csv(self, data: list[dict]) -> bytes:
        # 导出逻辑
        pass
```

---

### 2. 开闭原则 (Open/Closed Principle)

**定义：** 软件实体应该对扩展开放，对修改关闭。

**反例：**
```python
# 违反OCP：添加新支付方式需要修改现有代码
class PaymentProcessor:
    def process(self, payment_type: str, amount: float) -> bool:
        if payment_type == "credit_card":
            return self._process_credit_card(amount)
        elif payment_type == "wechat":
            return self._process_wechat(amount)
        elif payment_type == "alipay":
            return self._process_alipay(amount)
        # 添加新支付方式需要修改这里
        else:
            raise ValueError(f"Unknown payment type: {payment_type}")
```

**正例：**
```python
# 遵循OCP：通过抽象和多态扩展
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    """支付策略抽象基类"""
    @abstractmethod
    def process(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def process(self, amount: float) -> bool:
        # 信用卡支付逻辑
        return True

class WechatPayment(PaymentStrategy):
    def process(self, amount: float) -> bool:
        # 微信支付逻辑
        return True

class AlipayPayment(PaymentStrategy):
    def process(self, amount: float) -> bool:
        # 支付宝支付逻辑
        return True

# 添加新支付方式只需创建新类
class ApplePayPayment(PaymentStrategy):
    def process(self, amount: float) -> bool:
        # Apple Pay支付逻辑
        return True

class PaymentProcessor:
    """支付处理器：对扩展开放，对修改关闭"""
    def process(self, strategy: PaymentStrategy, amount: float) -> bool:
        return strategy.process(amount)
```

---

### 3. 里氏替换原则 (Liskov Substitution Principle)

**定义：** 子类对象应该能够替换父类对象而不影响程序的正确性。

**反例：**
```python
# 违反LSP：子类改变了父类的行为契约
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value

    def area(self) -> float:
        return self._width * self._height

class Square(Rectangle):
    """正方形：违反LSP，因为设置宽度会同时改变高度"""
    @Rectangle.width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._height = value  # 违反了父类的契约

    @Rectangle.height.setter
    def height(self, value: float) -> None:
        self._width = value
        self._height = value

# 使用时会出问题
def test_rectangle(rect: Rectangle):
    rect.width = 5
    rect.height = 4
    assert rect.area() == 20  # Square会失败！
```

**正例：**
```python
# 遵循LSP：使用组合或重新设计继承关系
from abc import ABC, abstractmethod

class Shape(ABC):
    """形状抽象基类"""
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side ** 2

# 现在两者都可以正确替换Shape
def calculate_total_area(shapes: list[Shape]) -> float:
    return sum(shape.area() for shape in shapes)
```

---

### 4. 接口隔离原则 (Interface Segregation Principle)

**定义：** 客户端不应该被迫依赖它不使用的接口。

**反例：**
```python
# 违反ISP：一个大接口包含太多方法
from abc import ABC, abstractmethod

class Worker(ABC):
    @abstractmethod
    def work(self) -> None:
        pass

    @abstractmethod
    def eat(self) -> None:
        pass

    @abstractmethod
    def sleep(self) -> None:
        pass

class Robot(Worker):
    def work(self) -> None:
        print("Working...")

    def eat(self) -> None:
        # 机器人不需要吃饭，但被迫实现
        raise NotImplementedError("Robots don't eat")

    def sleep(self) -> None:
        # 机器人不需要睡觉，但被迫实现
        raise NotImplementedError("Robots don't sleep")
```

**正例：**
```python
# 遵循ISP：拆分为多个小接口
from abc import ABC, abstractmethod
from typing import Protocol

class Workable(Protocol):
    def work(self) -> None: ...

class Eatable(Protocol):
    def eat(self) -> None: ...

class Sleepable(Protocol):
    def sleep(self) -> None: ...

class Human:
    """人类：实现所有接口"""
    def work(self) -> None:
        print("Working...")

    def eat(self) -> None:
        print("Eating...")

    def sleep(self) -> None:
        print("Sleeping...")

class Robot:
    """机器人：只实现需要的接口"""
    def work(self) -> None:
        print("Working...")

# 使用时只依赖需要的接口
def assign_work(worker: Workable) -> None:
    worker.work()

def schedule_lunch(eater: Eatable) -> None:
    eater.eat()
```

---

### 5. 依赖倒置原则 (Dependency Inversion Principle)

**定义：** 高层模块不应该依赖低层模块，两者都应该依赖抽象。

**反例：**
```python
# 违反DIP：高层模块直接依赖低层模块
class MySQLDatabase:
    def query(self, sql: str) -> list:
        # MySQL查询实现
        pass

class UserService:
    def __init__(self):
        # 直接依赖具体实现
        self.db = MySQLDatabase()

    def get_users(self) -> list:
        return self.db.query("SELECT * FROM users")
```

**正例：**
```python
# 遵循DIP：依赖抽象而非具体实现
from abc import ABC, abstractmethod
from typing import Protocol

class Database(Protocol):
    """数据库抽象接口"""
    def query(self, sql: str) -> list: ...

class MySQLDatabase:
    def query(self, sql: str) -> list:
        # MySQL实现
        pass

class PostgreSQLDatabase:
    def query(self, sql: str) -> list:
        # PostgreSQL实现
        pass

class UserService:
    def __init__(self, db: Database):
        # 依赖抽象，通过构造函数注入
        self.db = db

    def get_users(self) -> list:
        return self.db.query("SELECT * FROM users")

# 使用时注入具体实现
mysql_db = MySQLDatabase()
user_service = UserService(mysql_db)

# 轻松切换实现
postgres_db = PostgreSQLDatabase()
user_service = UserService(postgres_db)
```

---

## 常用设计模式

### 1. 工厂模式 (Factory Pattern)

```python
from abc import ABC, abstractmethod
from typing import Type

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> bool:
        pass

class EmailNotification(Notification):
    def send(self, message: str) -> bool:
        print(f"Sending email: {message}")
        return True

class SMSNotification(Notification):
    def send(self, message: str) -> bool:
        print(f"Sending SMS: {message}")
        return True

class PushNotification(Notification):
    def send(self, message: str) -> bool:
        print(f"Sending push: {message}")
        return True

class NotificationFactory:
    """通知工厂"""
    _creators: dict[str, Type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }

    @classmethod
    def create(cls, notification_type: str) -> Notification:
        creator = cls._creators.get(notification_type)
        if not creator:
            raise ValueError(f"Unknown notification type: {notification_type}")
        return creator()

    @classmethod
    def register(cls, name: str, creator: Type[Notification]) -> None:
        """注册新的通知类型"""
        cls._creators[name] = creator

# 使用
notification = NotificationFactory.create("email")
notification.send("Hello!")
```

---

### 2. 单例模式 (Singleton Pattern)

```python
from threading import Lock
from typing import TypeVar, Type

T = TypeVar('T')

class Singleton:
    """线程安全的单例基类"""
    _instances: dict[Type, object] = {}
    _lock: Lock = Lock()

    def __new__(cls: Type[T]) -> T:
        if cls not in cls._instances:
            with cls._lock:
                # 双重检查锁定
                if cls not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class DatabaseConnection(Singleton):
    """数据库连接单例"""
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._connection = None
            self._initialized = True

    def connect(self, url: str) -> None:
        if self._connection is None:
            self._connection = create_connection(url)

# 使用装饰器实现单例
def singleton(cls: Type[T]) -> Type[T]:
    """单例装饰器"""
    instances: dict[Type, object] = {}
    lock = Lock()

    def get_instance(*args, **kwargs) -> T:
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class ConfigManager:
    def __init__(self):
        self.config = {}
```

---

### 3. 策略模式 (Strategy Pattern)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

class PricingStrategy(ABC):
    """定价策略抽象"""
    @abstractmethod
    def calculate(self, base_price: float) -> float:
        pass

class RegularPricing(PricingStrategy):
    def calculate(self, base_price: float) -> float:
        return base_price

class MemberPricing(PricingStrategy):
    def __init__(self, discount: float = 0.1):
        self.discount = discount

    def calculate(self, base_price: float) -> float:
        return base_price * (1 - self.discount)

class VIPPricing(PricingStrategy):
    def __init__(self, discount: float = 0.2):
        self.discount = discount

    def calculate(self, base_price: float) -> float:
        return base_price * (1 - self.discount)

@dataclass
class Order:
    """订单：使用策略模式计算价格"""
    base_price: float
    pricing_strategy: PricingStrategy

    def get_final_price(self) -> float:
        return self.pricing_strategy.calculate(self.base_price)

# 使用
regular_order = Order(100, RegularPricing())
print(regular_order.get_final_price())  # 100

vip_order = Order(100, VIPPricing())
print(vip_order.get_final_price())  # 80
```

---

### 4. 观察者模式 (Observer Pattern)

```python
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field

class Observer(ABC):
    """观察者抽象"""
    @abstractmethod
    def update(self, event: str, data: Any) -> None:
        pass

class Subject:
    """被观察者"""
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        for observer in self._observers:
            observer.update(event, data)

# 使用事件总线实现
@dataclass
class EventBus:
    """事件总线"""
    _subscribers: dict[str, list[Callable]] = field(default_factory=dict)

    def subscribe(self, event: str, handler: Callable) -> None:
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._subscribers:
            self._subscribers[event].remove(handler)

    def publish(self, event: str, data: Any = None) -> None:
        if event in self._subscribers:
            for handler in self._subscribers[event]:
                handler(data)

# 使用
event_bus = EventBus()

def on_user_created(user: dict):
    print(f"User created: {user['name']}")

def send_welcome_email(user: dict):
    print(f"Sending welcome email to {user['email']}")

event_bus.subscribe("user.created", on_user_created)
event_bus.subscribe("user.created", send_welcome_email)

event_bus.publish("user.created", {"name": "John", "email": "john@example.com"})
```

---

### 5. 装饰器模式 (Decorator Pattern)

```python
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, TypeVar
import time
import logging

T = TypeVar('T')

# 函数装饰器
def retry(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

def log_execution(logger: logging.Logger = None):
    """日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {e}")
                raise
        return wrapper
    return decorator

# 类装饰器模式
class DataSource(ABC):
    @abstractmethod
    def read(self) -> str:
        pass

    @abstractmethod
    def write(self, data: str) -> None:
        pass

class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename

    def read(self) -> str:
        with open(self.filename) as f:
            return f.read()

    def write(self, data: str) -> None:
        with open(self.filename, 'w') as f:
            f.write(data)

class DataSourceDecorator(DataSource):
    """数据源装饰器基类"""
    def __init__(self, source: DataSource):
        self._source = source

    def read(self) -> str:
        return self._source.read()

    def write(self, data: str) -> None:
        self._source.write(data)

class EncryptionDecorator(DataSourceDecorator):
    """加密装饰器"""
    def read(self) -> str:
        data = super().read()
        return self._decrypt(data)

    def write(self, data: str) -> None:
        encrypted = self._encrypt(data)
        super().write(encrypted)

    def _encrypt(self, data: str) -> str:
        # 加密逻辑
        return data

    def _decrypt(self, data: str) -> str:
        # 解密逻辑
        return data

class CompressionDecorator(DataSourceDecorator):
    """压缩装饰器"""
    def read(self) -> str:
        data = super().read()
        return self._decompress(data)

    def write(self, data: str) -> None:
        compressed = self._compress(data)
        super().write(compressed)

    def _compress(self, data: str) -> str:
        # 压缩逻辑
        return data

    def _decompress(self, data: str) -> str:
        # 解压逻辑
        return data

# 使用：组合多个装饰器
source = FileDataSource("data.txt")
encrypted_source = EncryptionDecorator(source)
compressed_encrypted_source = CompressionDecorator(encrypted_source)
```

---

## Python 特有的设计技巧

### 1. 使用 Protocol 定义接口

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool: ...
    def __eq__(self, other: object) -> bool: ...

def sort_items(items: list[Comparable]) -> list[Comparable]:
    return sorted(items)

# 任何实现了 __lt__ 和 __eq__ 的类都可以使用
class Product:
    def __init__(self, price: float):
        self.price = price

    def __lt__(self, other: 'Product') -> bool:
        return self.price < other.price

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False
        return self.price == other.price

products = [Product(100), Product(50), Product(75)]
sorted_products = sort_items(products)  # 类型检查通过
```

### 2. 使用 dataclass 简化数据类

```python
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """初始化后的验证"""
        if not self.email or '@' not in self.email:
            raise ValueError("Invalid email")

@dataclass(frozen=True)
class Point:
    """不可变数据类"""
    x: float
    y: float

    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
```

### 3. 使用上下文管理器管理资源

```python
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

@contextmanager
def transaction(connection) -> Generator[None, None, None]:
    """事务上下文管理器"""
    try:
        yield
        connection.commit()
    except Exception:
        connection.rollback()
        raise

@asynccontextmanager
async def async_transaction(connection) -> AsyncGenerator[None, None]:
    """异步事务上下文管理器"""
    try:
        yield
        await connection.commit()
    except Exception:
        await connection.rollback()
        raise

# 使用
with transaction(conn):
    conn.execute("INSERT INTO users ...")
    conn.execute("UPDATE accounts ...")

async with async_transaction(async_conn):
    await async_conn.execute("INSERT INTO users ...")
```

### 4. 使用描述符实现属性验证

```python
from typing import Any, Optional

class Validator:
    """验证器描述符基类"""
    def __init__(self, name: str = None):
        self.name = name

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: type = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj: Any, value: Any) -> None:
        self.validate(value)
        obj.__dict__[self.name] = value

    def validate(self, value: Any) -> None:
        pass

class PositiveNumber(Validator):
    """正数验证器"""
    def validate(self, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")

class NonEmptyString(Validator):
    """非空字符串验证器"""
    def validate(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string")
        if not value.strip():
            raise ValueError(f"{self.name} cannot be empty")

class Product:
    name = NonEmptyString()
    price = PositiveNumber()
    quantity = PositiveNumber()

    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

# 使用
product = Product("iPhone", 999.99, 10)  # OK
product = Product("", 999.99, 10)  # ValueError: name cannot be empty
product = Product("iPhone", -100, 10)  # ValueError: price must be positive
```
