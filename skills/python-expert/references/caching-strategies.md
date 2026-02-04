# Python 缓存策略指南

## 缓存层次

```
┌─────────────────────────────────────────────────────────────┐
│                      缓存层次架构                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    L1: 进程内缓存                     │   │
│  │  特点: 最快、容量小、进程隔离                          │   │
│  │  实现: lru_cache、dict、TTLCache                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    L2: 分布式缓存                     │   │
│  │  特点: 较快、容量大、跨进程共享                        │   │
│  │  实现: Redis、Memcached                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    L3: 持久化存储                     │   │
│  │  特点: 较慢、容量最大、持久化                          │   │
│  │  实现: Database、File System                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 进程内缓存

### functools.lru_cache

```python
from functools import lru_cache, cache
from typing import Optional

# 基础用法
@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """缓存计算结果"""
    return sum(i ** 2 for i in range(n))

# Python 3.9+ 无限缓存
@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 清除缓存
expensive_computation.cache_clear()

# 查看缓存统计
print(expensive_computation.cache_info())
# CacheInfo(hits=10, misses=5, maxsize=128, currsize=5)
```

### 自定义 TTL 缓存

```python
import time
from typing import TypeVar, Generic, Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from threading import Lock

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    """缓存条目"""
    value: T
    expires_at: float
    created_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class TTLCache(Generic[T]):
    """带TTL的缓存"""

    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry[T]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired:
                del self._cache[key]
                return None
            return entry.value

    def set(self, key: str, value: T, ttl: float = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl

        with self._lock:
            # 检查容量
            if len(self._cache) >= self.max_size:
                self._evict_expired()
                if len(self._cache) >= self.max_size:
                    self._evict_oldest()

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=time.time() + ttl
            )

    def delete(self, key: str) -> bool:
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()

    def _evict_expired(self) -> None:
        """清除过期条目"""
        now = time.time()
        expired_keys = [
            k for k, v in self._cache.items()
            if v.expires_at < now
        ]
        for key in expired_keys:
            del self._cache[key]

    def _evict_oldest(self) -> None:
        """清除最旧的条目"""
        if not self._cache:
            return
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]

# 使用示例
cache = TTLCache[dict](default_ttl=3600, max_size=1000)
cache.set("user:123", {"name": "John"})
user = cache.get("user:123")
```

### 缓存装饰器

```python
from functools import wraps
from typing import Callable, TypeVar, Optional
import hashlib
import json

T = TypeVar('T')

def cached(
    ttl: float = 300.0,
    key_prefix: str = "",
    key_builder: Optional[Callable[..., str]] = None,
    cache_none: bool = False
):
    """通用缓存装饰器"""
    cache = TTLCache(default_ttl=ttl)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_data = json.dumps({
                    "func": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }, sort_keys=True, default=str)
                cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

            # 尝试获取缓存
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 写入缓存
            if result is not None or cache_none:
                cache.set(cache_key, result)

            return result

        # 暴露缓存操作
        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        return wrapper

    return decorator

# 使用示例
@cached(ttl=3600, key_prefix="user")
def get_user(user_id: str) -> dict:
    return fetch_from_database(user_id)

# 清除缓存
get_user.cache_clear()
```

---

## 分布式缓存 (Redis)

### Redis 客户端封装

```python
import redis.asyncio as redis
from typing import Optional, Any, Union
import json
import pickle

class RedisCache:
    """Redis缓存客户端"""

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        prefix: str = "",
        default_ttl: int = 3600
    ):
        self.url = url
        self.prefix = prefix
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """连接Redis"""
        self._client = redis.from_url(
            self.url,
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self) -> None:
        """关闭连接"""
        if self._client:
            await self._client.close()

    def _make_key(self, key: str) -> str:
        """生成完整键名"""
        return f"{self.prefix}:{key}" if self.prefix else key

    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        full_key = self._make_key(key)
        value = await self._client.get(full_key)
        if value is None:
            return None
        return json.loads(value)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """设置值"""
        full_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        serialized = json.dumps(value, default=str)

        return await self._client.set(
            full_key,
            serialized,
            ex=ttl,
            nx=nx,
            xx=xx
        )

    async def delete(self, *keys: str) -> int:
        """删除键"""
        full_keys = [self._make_key(k) for k in keys]
        return await self._client.delete(*full_keys)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        full_key = self._make_key(key)
        return await self._client.exists(full_key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间"""
        full_key = self._make_key(key)
        return await self._client.expire(full_key, ttl)

    async def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        full_key = self._make_key(key)
        return await self._client.ttl(full_key)

    async def incr(self, key: str, amount: int = 1) -> int:
        """递增"""
        full_key = self._make_key(key)
        return await self._client.incrby(full_key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """递减"""
        full_key = self._make_key(key)
        return await self._client.decrby(full_key, amount)
```

### 缓存模式实现

```python
from typing import TypeVar, Callable, Awaitable, Optional
from functools import wraps

T = TypeVar('T')

class CachePatterns:
    """缓存模式实现"""

    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def cache_aside(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[T]],
        ttl: int = 3600
    ) -> T:
        """Cache-Aside模式：先查缓存，未命中则查数据库并写入缓存"""
        # 1. 查缓存
        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        # 2. 查数据库
        value = await fetch_func()

        # 3. 写入缓存
        if value is not None:
            await self.cache.set(key, value, ttl=ttl)

        return value

    async def write_through(
        self,
        key: str,
        value: T,
        persist_func: Callable[[T], Awaitable[None]],
        ttl: int = 3600
    ) -> None:
        """Write-Through模式：同时写入缓存和数据库"""
        # 1. 写入数据库
        await persist_func(value)

        # 2. 写入缓存
        await self.cache.set(key, value, ttl=ttl)

    async def write_behind(
        self,
        key: str,
        value: T,
        persist_func: Callable[[T], Awaitable[None]],
        ttl: int = 3600
    ) -> None:
        """Write-Behind模式：先写缓存，异步写数据库"""
        # 1. 写入缓存
        await self.cache.set(key, value, ttl=ttl)

        # 2. 异步写入数据库（实际应用中应使用消息队列）
        asyncio.create_task(persist_func(value))

    async def refresh_ahead(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[T]],
        ttl: int = 3600,
        refresh_threshold: float = 0.8
    ) -> T:
        """Refresh-Ahead模式：在过期前主动刷新"""
        # 1. 查缓存
        cached = await self.cache.get(key)
        remaining_ttl = await self.cache.ttl(key)

        if cached is not None:
            # 检查是否需要刷新
            if remaining_ttl < ttl * (1 - refresh_threshold):
                # 异步刷新
                asyncio.create_task(self._refresh(key, fetch_func, ttl))
            return cached

        # 2. 缓存未命中
        value = await fetch_func()
        if value is not None:
            await self.cache.set(key, value, ttl=ttl)
        return value

    async def _refresh(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[T]],
        ttl: int
    ) -> None:
        """刷新缓存"""
        value = await fetch_func()
        if value is not None:
            await self.cache.set(key, value, ttl=ttl)
```

### 分布式锁

```python
import uuid
import asyncio
from contextlib import asynccontextmanager

class DistributedLock:
    """Redis分布式锁"""

    def __init__(
        self,
        cache: RedisCache,
        name: str,
        timeout: int = 10,
        retry_interval: float = 0.1
    ):
        self.cache = cache
        self.name = f"lock:{name}"
        self.timeout = timeout
        self.retry_interval = retry_interval
        self._token = str(uuid.uuid4())

    async def acquire(self, blocking: bool = True) -> bool:
        """获取锁"""
        while True:
            # 尝试获取锁
            acquired = await self.cache._client.set(
                self.name,
                self._token,
                ex=self.timeout,
                nx=True
            )

            if acquired:
                return True

            if not blocking:
                return False

            await asyncio.sleep(self.retry_interval)

    async def release(self) -> bool:
        """释放锁"""
        # 使用Lua脚本确保原子性
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = await self.cache._client.eval(
            script,
            1,
            self.name,
            self._token
        )
        return result == 1

    async def extend(self, additional_time: int) -> bool:
        """延长锁时间"""
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        result = await self.cache._client.eval(
            script,
            1,
            self.name,
            self._token,
            additional_time
        )
        return result == 1

    @asynccontextmanager
    async def lock(self):
        """上下文管理器"""
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError(f"Failed to acquire lock: {self.name}")
        try:
            yield
        finally:
            await self.release()

# 使用示例
async def update_inventory(product_id: str, quantity: int):
    lock = DistributedLock(cache, f"inventory:{product_id}")

    async with lock.lock():
        # 临界区代码
        current = await get_inventory(product_id)
        await set_inventory(product_id, current - quantity)
```

---

## 缓存策略

### 缓存穿透防护

```python
class CachePenetrationProtection:
    """缓存穿透防护"""

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.null_value = "__NULL__"
        self.null_ttl = 60  # 空值缓存时间较短

    async def get_with_protection(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[Optional[T]]],
        ttl: int = 3600
    ) -> Optional[T]:
        """带穿透防护的获取"""
        # 1. 查缓存
        cached = await self.cache.get(key)

        if cached == self.null_value:
            # 缓存了空值，直接返回None
            return None

        if cached is not None:
            return cached

        # 2. 查数据库
        value = await fetch_func()

        # 3. 写入缓存
        if value is not None:
            await self.cache.set(key, value, ttl=ttl)
        else:
            # 缓存空值，防止穿透
            await self.cache.set(key, self.null_value, ttl=self.null_ttl)

        return value
```

### 缓存击穿防护

```python
import asyncio
from typing import Dict

class CacheBreakdownProtection:
    """缓存击穿防护：使用互斥锁"""

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self._locks: Dict[str, asyncio.Lock] = {}

    def _get_lock(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get_with_mutex(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[T]],
        ttl: int = 3600
    ) -> T:
        """带互斥锁的获取"""
        # 1. 查缓存
        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        # 2. 获取锁
        lock = self._get_lock(key)
        async with lock:
            # 双重检查
            cached = await self.cache.get(key)
            if cached is not None:
                return cached

            # 3. 查数据库
            value = await fetch_func()

            # 4. 写入缓存
            if value is not None:
                await self.cache.set(key, value, ttl=ttl)

            return value
```

### 缓存雪崩防护

```python
import random

class CacheAvalancheProtection:
    """缓存雪崩防护：随机过期时间"""

    def __init__(self, cache: RedisCache):
        self.cache = cache

    def _randomize_ttl(self, base_ttl: int, variance: float = 0.1) -> int:
        """随机化TTL"""
        delta = int(base_ttl * variance)
        return base_ttl + random.randint(-delta, delta)

    async def set_with_jitter(
        self,
        key: str,
        value: Any,
        base_ttl: int = 3600,
        variance: float = 0.1
    ) -> None:
        """带抖动的设置"""
        ttl = self._randomize_ttl(base_ttl, variance)
        await self.cache.set(key, value, ttl=ttl)

    async def batch_set_with_jitter(
        self,
        items: Dict[str, Any],
        base_ttl: int = 3600,
        variance: float = 0.1
    ) -> None:
        """批量设置，每个键有不同的过期时间"""
        for key, value in items.items():
            ttl = self._randomize_ttl(base_ttl, variance)
            await self.cache.set(key, value, ttl=ttl)
```

---

## 多级缓存

```python
from typing import List, Optional, Any

class MultiLevelCache:
    """多级缓存"""

    def __init__(self):
        self.levels: List[CacheLevel] = []

    def add_level(self, cache: Any, ttl: int) -> None:
        """添加缓存层级"""
        self.levels.append(CacheLevel(cache, ttl))

    async def get(self, key: str) -> Optional[Any]:
        """从多级缓存获取"""
        for i, level in enumerate(self.levels):
            value = await level.get(key)
            if value is not None:
                # 回填上层缓存
                for j in range(i):
                    await self.levels[j].set(key, value)
                return value
        return None

    async def set(self, key: str, value: Any) -> None:
        """设置到所有层级"""
        for level in self.levels:
            await level.set(key, value)

    async def delete(self, key: str) -> None:
        """从所有层级删除"""
        for level in self.levels:
            await level.delete(key)

class CacheLevel:
    """缓存层级"""

    def __init__(self, cache: Any, ttl: int):
        self.cache = cache
        self.ttl = ttl

    async def get(self, key: str) -> Optional[Any]:
        if hasattr(self.cache, 'get'):
            if asyncio.iscoroutinefunction(self.cache.get):
                return await self.cache.get(key)
            return self.cache.get(key)
        return None

    async def set(self, key: str, value: Any) -> None:
        if hasattr(self.cache, 'set'):
            if asyncio.iscoroutinefunction(self.cache.set):
                await self.cache.set(key, value, ttl=self.ttl)
            else:
                self.cache.set(key, value)

    async def delete(self, key: str) -> None:
        if hasattr(self.cache, 'delete'):
            if asyncio.iscoroutinefunction(self.cache.delete):
                await self.cache.delete(key)
            else:
                self.cache.delete(key)

# 使用示例
multi_cache = MultiLevelCache()
multi_cache.add_level(TTLCache(default_ttl=60), ttl=60)      # L1: 进程内
multi_cache.add_level(redis_cache, ttl=3600)                  # L2: Redis

value = await multi_cache.get("user:123")
```

---

## 缓存最佳实践

### 1. 键命名规范

```python
class CacheKeyBuilder:
    """缓存键构建器"""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix

    def build(self, *parts: str) -> str:
        """构建缓存键"""
        key_parts = [self.prefix] if self.prefix else []
        key_parts.extend(parts)
        return ":".join(key_parts)

    def user(self, user_id: str) -> str:
        return self.build("user", user_id)

    def user_profile(self, user_id: str) -> str:
        return self.build("user", user_id, "profile")

    def user_orders(self, user_id: str, page: int = 1) -> str:
        return self.build("user", user_id, "orders", f"page:{page}")

    def product(self, product_id: str) -> str:
        return self.build("product", product_id)

    def search(self, query: str, page: int = 1) -> str:
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return self.build("search", query_hash, f"page:{page}")

# 使用
keys = CacheKeyBuilder(prefix="myapp")
key = keys.user_profile("123")  # "myapp:user:123:profile"
```

### 2. 缓存预热

```python
class CacheWarmer:
    """缓存预热器"""

    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def warm_users(self, user_ids: List[str]) -> None:
        """预热用户缓存"""
        for user_id in user_ids:
            user = await fetch_user_from_db(user_id)
            if user:
                await self.cache.set(f"user:{user_id}", user)

    async def warm_hot_data(self) -> None:
        """预热热点数据"""
        # 获取热点数据列表
        hot_items = await get_hot_items()

        # 并发预热
        tasks = [
            self._warm_item(item)
            for item in hot_items
        ]
        await asyncio.gather(*tasks)

    async def _warm_item(self, item: dict) -> None:
        """预热单个项目"""
        key = f"item:{item['id']}"
        await self.cache.set(key, item)
```

### 3. 缓存监控

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    def to_dict(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.2%}",
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }

class MonitoredCache:
    """带监控的缓存"""

    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.stats = CacheStats()

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.cache.get(key)
            if value is not None:
                self.stats.hits += 1
            else:
                self.stats.misses += 1
            return value
        except Exception:
            self.stats.errors += 1
            raise

    async def set(self, key: str, value: Any, **kwargs) -> None:
        try:
            await self.cache.set(key, value, **kwargs)
            self.stats.sets += 1
        except Exception:
            self.stats.errors += 1
            raise

    async def delete(self, key: str) -> None:
        try:
            await self.cache.delete(key)
            self.stats.deletes += 1
        except Exception:
            self.stats.errors += 1
            raise

    def get_stats(self) -> dict:
        return self.stats.to_dict()
```
