# Python 数据库设计指南

## 数据库模型设计

### SQLAlchemy 模型基础

```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    """软删除混入类"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

def generate_uuid():
    return str(uuid.uuid4())

class BaseModel(Base, TimestampMixin):
    """模型基类"""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

### 实体关系设计

```python
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship

# 一对多关系
class User(BaseModel):
    __tablename__ = 'users'

    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # 一对多：一个用户有多个订单
    orders = relationship("Order", back_populates="user", lazy="selectin")

class Order(BaseModel):
    __tablename__ = 'orders'

    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    total_amount = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')

    # 多对一
    user = relationship("User", back_populates="orders")
    # 一对多
    items = relationship("OrderItem", back_populates="order", lazy="selectin")

# 多对多关系
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id'), primary_key=True),
    Column('role_id', String(36), ForeignKey('roles.id'), primary_key=True)
)

class Role(BaseModel):
    __tablename__ = 'roles'

    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", secondary=user_roles, back_populates="roles")

# 在 User 中添加
# roles = relationship("Role", secondary=user_roles, back_populates="users")
```

---

## 索引设计

### 索引类型与使用场景

| 索引类型 | 使用场景 | 示例 |
|----------|----------|------|
| 单列索引 | 单字段查询 | `WHERE email = ?` |
| 复合索引 | 多字段组合查询 | `WHERE status = ? AND created_at > ?` |
| 唯一索引 | 唯一性约束 | `email UNIQUE` |
| 全文索引 | 文本搜索 | `MATCH(content) AGAINST(?)` |

### 索引设计原则

```python
from sqlalchemy import Index

class Order(BaseModel):
    __tablename__ = 'orders'

    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=func.now())
    total_amount = Column(Integer)

    __table_args__ = (
        # 单列索引：外键查询
        Index('idx_orders_user_id', 'user_id'),

        # 复合索引：状态+时间查询（注意顺序：高选择性字段在前）
        Index('idx_orders_status_created', 'status', 'created_at'),

        # 覆盖索引：避免回表
        Index('idx_orders_user_status', 'user_id', 'status', 'total_amount'),
    )

# 索引设计检查清单
# 1. WHERE 条件字段是否有索引
# 2. JOIN 字段是否有索引
# 3. ORDER BY 字段是否在索引中
# 4. 复合索引顺序是否正确（最左前缀原则）
# 5. 是否有冗余索引
```

---

## 查询优化

### 避免 N+1 查询

```python
from sqlalchemy.orm import selectinload, joinedload, subqueryload

# 问题：N+1 查询
users = session.query(User).all()
for user in users:
    print(user.orders)  # 每个用户触发一次查询

# 解决方案1：selectinload（推荐，使用 IN 查询）
users = session.query(User).options(
    selectinload(User.orders)
).all()

# 解决方案2：joinedload（使用 JOIN，适合一对一）
users = session.query(User).options(
    joinedload(User.profile)
).all()

# 多层预加载
users = session.query(User).options(
    selectinload(User.orders).selectinload(Order.items)
).all()
```

### 只查询需要的字段

```python
from sqlalchemy import select

# 差：查询所有字段
users = session.query(User).all()

# 好：只查询需要的字段
stmt = select(User.id, User.name, User.email).where(User.is_active == True)
results = session.execute(stmt).all()

# 使用 load_only
from sqlalchemy.orm import load_only

users = session.query(User).options(
    load_only(User.id, User.name, User.email)
).all()
```

### 批量操作

```python
# 批量插入
from sqlalchemy import insert

users_data = [{"name": f"User{i}", "email": f"user{i}@example.com"} for i in range(1000)]

# 方式1：bulk_insert_mappings
session.bulk_insert_mappings(User, users_data)

# 方式2：execute insert
session.execute(insert(User), users_data)

# 批量更新
from sqlalchemy import update

session.execute(
    update(User).where(User.status == 'inactive').values(is_deleted=True)
)

# 批量删除
from sqlalchemy import delete

session.execute(
    delete(Order).where(Order.created_at < datetime(2020, 1, 1))
)

session.commit()
```

---

## 事务管理

### 事务基础

```python
from sqlalchemy.orm import Session
from contextlib import contextmanager

@contextmanager
def transaction(session: Session):
    """事务上下文管理器"""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

# 使用示例
with transaction(session) as tx:
    user = User(name="John", email="john@example.com")
    tx.add(user)
    order = Order(user_id=user.id, total_amount=100)
    tx.add(order)
```

### 异步事务

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager

engine = create_async_engine("postgresql+asyncpg://localhost/db")
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 使用
async with get_session() as session:
    user = User(name="John")
    session.add(user)
```

### 嵌套事务（Savepoint）

```python
async def transfer_money(from_id: str, to_id: str, amount: int):
    async with get_session() as session:
        # 扣款
        from_account = await session.get(Account, from_id)
        from_account.balance -= amount

        # 使用 savepoint
        async with session.begin_nested():
            # 入账
            to_account = await session.get(Account, to_id)
            to_account.balance += amount

            # 如果这里失败，只回滚到 savepoint
            await notify_transfer(from_id, to_id, amount)
```

---

## 数据库迁移

### Alembic 配置

```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config
from app.models import Base

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy."
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 检测字段类型变化
            compare_server_default=True  # 检测默认值变化
        )

        with context.begin_transaction():
            context.run_migrations()
```

### 迁移脚本示例

```python
# alembic/versions/xxx_add_user_phone.py
"""add user phone column

Revision ID: abc123
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    op.create_index('idx_users_phone', 'users', ['phone'])

def downgrade():
    op.drop_index('idx_users_phone', 'users')
    op.drop_column('users', 'phone')

# 数据迁移
def upgrade():
    # 添加新列
    op.add_column('users', sa.Column('full_name', sa.String(200)))

    # 数据迁移
    op.execute("""
        UPDATE users SET full_name = first_name || ' ' || last_name
    """)

    # 删除旧列
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

### 常用命令

```bash
# 生成迁移
alembic revision --autogenerate -m "add user phone"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1

# 查看历史
alembic history

# 查看当前版本
alembic current
```

---

## 连接池管理

### 连接池配置

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 超出 pool_size 后最多创建的连接数
    pool_timeout=30,        # 获取连接超时时间
    pool_recycle=1800,      # 连接回收时间（秒）
    pool_pre_ping=True,     # 使用前检测连接是否有效
)

# 异步连接池
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
)
```

### 连接池监控

```python
from sqlalchemy import event

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """连接被取出时"""
    logger.debug(f"Connection checked out: {connection_record}")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """连接归还时"""
    logger.debug(f"Connection checked in: {connection_record}")

def get_pool_status():
    """获取连接池状态"""
    return {
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "checked_in": engine.pool.checkedin(),
    }
```

---

## 读写分离

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from contextlib import contextmanager

class DatabaseRouter:
    """数据库路由：读写分离"""

    def __init__(self, master_url: str, slave_urls: list[str]):
        self.master = create_engine(master_url)
        self.slaves = [create_engine(url) for url in slave_urls]
        self._slave_index = 0

    def get_master(self):
        return self.master

    def get_slave(self):
        # 轮询选择从库
        slave = self.slaves[self._slave_index]
        self._slave_index = (self._slave_index + 1) % len(self.slaves)
        return slave

router = DatabaseRouter(
    master_url="postgresql://master/db",
    slave_urls=["postgresql://slave1/db", "postgresql://slave2/db"]
)

@contextmanager
def read_session():
    """只读会话"""
    session = Session(router.get_slave())
    try:
        yield session
    finally:
        session.close()

@contextmanager
def write_session():
    """写入会话"""
    session = Session(router.get_master())
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

---

## 数据库设计规范

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写复数，下划线分隔 | `users`, `order_items` |
| 字段名 | 小写，下划线分隔 | `user_id`, `created_at` |
| 主键 | `id` 或 `表名_id` | `id`, `user_id` |
| 外键 | `关联表单数_id` | `user_id`, `order_id` |
| 索引 | `idx_表名_字段名` | `idx_users_email` |
| 唯一索引 | `uk_表名_字段名` | `uk_users_email` |

### 字段设计规范

```python
class User(BaseModel):
    __tablename__ = 'users'

    # 主键：使用 UUID 或自增 ID
    id = Column(String(36), primary_key=True, default=generate_uuid)

    # 字符串：指定合理长度
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    # 状态字段：使用枚举或短字符串
    status = Column(String(20), default='active')

    # 金额：使用整数存储分，避免浮点精度问题
    balance = Column(Integer, default=0)  # 单位：分

    # 时间：使用 DateTime，带时区
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 布尔值：明确默认值
    is_active = Column(Boolean, default=True, nullable=False)

    # JSON 字段：存储灵活数据
    metadata = Column(JSON, default=dict)
```

### 设计检查清单

- [ ] 表名和字段名符合命名规范
- [ ] 主键设计合理（UUID/自增）
- [ ] 外键有索引
- [ ] 常用查询字段有索引
- [ ] 字段类型和长度合理
- [ ] 必要字段设置 NOT NULL
- [ ] 有默认值的字段设置 DEFAULT
- [ ] 时间字段使用 DateTime
- [ ] 金额字段使用整数（分）
- [ ] 软删除字段（如需要）
