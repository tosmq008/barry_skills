# Python 性能优化指南

## 性能分析工具

### 1. cProfile - CPU分析

```python
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """性能分析装饰器"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # 输出统计
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
        print(stream.getvalue())

        return result
    return wrapper

# 命令行使用
# python -m cProfile -s cumtime script.py
# python -m cProfile -o output.prof script.py

# 分析结果
# python -c "import pstats; p = pstats.Stats('output.prof'); p.sort_stats('cumulative').print_stats(20)"
```

### 2. line_profiler - 行级分析

```python
# 安装: pip install line_profiler

# 使用 @profile 装饰器标记函数
@profile
def slow_function():
    result = []
    for i in range(10000):
        result.append(i ** 2)
    return result

# 运行: kernprof -l -v script.py
```

### 3. memory_profiler - 内存分析

```python
# 安装: pip install memory_profiler

from memory_profiler import profile

@profile
def memory_intensive():
    data = [i ** 2 for i in range(1000000)]
    return sum(data)

# 运行: python -m memory_profiler script.py
```

### 4. py-spy - 采样分析

```bash
# 安装: pip install py-spy

# 实时查看
py-spy top --pid <PID>

# 生成火焰图
py-spy record -o profile.svg --pid <PID>

# 分析脚本
py-spy record -o profile.svg -- python script.py
```

---

## 代码级优化

### 1. 数据结构选择

```python
# 查找操作：使用 set/dict 而非 list
# 差: O(n)
items = [1, 2, 3, 4, 5]
if 3 in items:  # 线性查找
    pass

# 好: O(1)
items = {1, 2, 3, 4, 5}
if 3 in items:  # 哈希查找
    pass

# 频繁插入/删除：使用 deque 而非 list
from collections import deque

# 差: O(n) 头部插入
items = []
items.insert(0, item)

# 好: O(1) 头部插入
items = deque()
items.appendleft(item)

# 计数：使用 Counter
from collections import Counter

# 差
counts = {}
for item in items:
    counts[item] = counts.get(item, 0) + 1

# 好
counts = Counter(items)

# 默认值：使用 defaultdict
from collections import defaultdict

# 差
groups = {}
for item in items:
    if item.category not in groups:
        groups[item.category] = []
    groups[item.category].append(item)

# 好
groups = defaultdict(list)
for item in items:
    groups[item.category].append(item)
```

### 2. 循环优化

```python
# 列表推导式比 for 循环快
# 差
result = []
for i in range(1000):
    result.append(i ** 2)

# 好
result = [i ** 2 for i in range(1000)]

# 使用生成器处理大数据
# 差: 一次性加载所有数据
def process_all(items):
    return [expensive_operation(item) for item in items]

# 好: 惰性求值
def process_lazy(items):
    for item in items:
        yield expensive_operation(item)

# 避免在循环中重复计算
# 差
for i in range(len(items)):
    if items[i] > len(items) / 2:  # len() 每次都计算
        pass

# 好
length = len(items)
threshold = length / 2
for i in range(length):
    if items[i] > threshold:
        pass

# 使用 enumerate 而非 range(len())
# 差
for i in range(len(items)):
    print(i, items[i])

# 好
for i, item in enumerate(items):
    print(i, item)
```

### 3. 字符串操作

```python
# 字符串拼接：使用 join 而非 +
# 差: O(n²)
result = ""
for s in strings:
    result += s

# 好: O(n)
result = "".join(strings)

# 格式化：使用 f-string
# 差
message = "Hello, " + name + "! You have " + str(count) + " messages."

# 好
message = f"Hello, {name}! You have {count} messages."

# 大量字符串操作：使用 StringIO
from io import StringIO

buffer = StringIO()
for line in lines:
    buffer.write(line)
    buffer.write("\n")
result = buffer.getvalue()
```

### 4. 函数调用优化

```python
# 避免不必要的函数调用
# 差
def get_value():
    return expensive_computation()

for i in range(1000):
    value = get_value()  # 每次都调用

# 好
value = expensive_computation()
for i in range(1000):
    # 使用缓存的值
    pass

# 使用局部变量
# 差
import math
for i in range(10000):
    result = math.sqrt(i)  # 每次都查找 math.sqrt

# 好
from math import sqrt
for i in range(10000):
    result = sqrt(i)  # 直接调用

# 或者
sqrt = math.sqrt  # 局部引用
for i in range(10000):
    result = sqrt(i)
```

---

## 内存优化

### 1. 使用 __slots__

```python
# 普通类：每个实例有 __dict__
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 使用 __slots__：减少内存占用
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

# 内存对比
import sys
p1 = Point(1, 2)  # 普通类: ~152 bytes
p2 = Point(1, 2)  # __slots__: ~56 bytes
```

### 2. 生成器和迭代器

```python
# 差: 一次性加载所有数据到内存
def read_large_file(path):
    with open(path) as f:
        return f.readlines()  # 全部加载

# 好: 逐行读取
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# 使用生成器表达式
# 差
squares = [x ** 2 for x in range(1000000)]  # 列表占用大量内存

# 好
squares = (x ** 2 for x in range(1000000))  # 生成器几乎不占内存
```

### 3. 对象池

```python
from typing import TypeVar, Generic, List, Callable

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """对象池：复用对象减少内存分配"""

    def __init__(self, factory: Callable[[], T], initial_size: int = 10):
        self.factory = factory
        self._pool: List[T] = [factory() for _ in range(initial_size)]

    def acquire(self) -> T:
        """获取对象"""
        if self._pool:
            return self._pool.pop()
        return self.factory()

    def release(self, obj: T) -> None:
        """归还对象"""
        self._pool.append(obj)

# 使用示例
class Buffer:
    def __init__(self, size: int = 1024):
        self.data = bytearray(size)

    def reset(self):
        self.data[:] = b'\x00' * len(self.data)

buffer_pool = ObjectPool(lambda: Buffer(4096), initial_size=10)

# 获取缓冲区
buf = buffer_pool.acquire()
# 使用缓冲区...
buf.reset()
# 归还缓冲区
buffer_pool.release(buf)
```

### 4. 弱引用

```python
import weakref
from typing import Dict, Any

class Cache:
    """使用弱引用的缓存：允许对象被垃圾回收"""

    def __init__(self):
        self._cache: Dict[str, weakref.ref] = {}

    def get(self, key: str) -> Any:
        ref = self._cache.get(key)
        if ref is None:
            return None
        obj = ref()
        if obj is None:
            # 对象已被回收
            del self._cache[key]
            return None
        return obj

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = weakref.ref(value)
```

---

## 数据库优化

### 1. 避免 N+1 查询

```python
# 差: N+1 查询
users = session.query(User).all()
for user in users:
    print(user.orders)  # 每个用户触发一次查询

# 好: 预加载
from sqlalchemy.orm import joinedload, selectinload

# joinedload: 使用 JOIN
users = session.query(User).options(joinedload(User.orders)).all()

# selectinload: 使用 IN 查询
users = session.query(User).options(selectinload(User.orders)).all()
```

### 2. 批量操作

```python
# 差: 逐条插入
for item in items:
    session.add(Item(**item))
    session.commit()

# 好: 批量插入
session.bulk_insert_mappings(Item, items)
session.commit()

# 或使用 executemany
from sqlalchemy import insert

session.execute(
    insert(Item),
    items
)
session.commit()
```

### 3. 只查询需要的字段

```python
# 差: 查询所有字段
users = session.query(User).all()

# 好: 只查询需要的字段
from sqlalchemy import select

stmt = select(User.id, User.name).where(User.active == True)
results = session.execute(stmt).all()
```

### 4. 使用索引

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, index=True)

    # 复合索引
    __table_args__ = (
        Index('idx_name_created', 'name', 'created_at'),
    )
```

---

## 异步优化

### 1. 并发请求

```python
import asyncio
import aiohttp

# 差: 串行请求
async def fetch_all_serial(urls):
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as response:
                results.append(await response.json())
    return results

# 好: 并发请求
async def fetch_all_concurrent(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_one(session, url):
    async with session.get(url) as response:
        return await response.json()
```

### 2. 限制并发数

```python
import asyncio

async def fetch_with_limit(urls, max_concurrent=10):
    """限制并发数的批量请求"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(url):
        async with semaphore:
            return await fetch_one(url)

    tasks = [fetch_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### 3. 连接池

```python
import aiohttp

# 创建带连接池的会话
connector = aiohttp.TCPConnector(
    limit=100,           # 总连接数限制
    limit_per_host=10,   # 每个主机连接数限制
    ttl_dns_cache=300,   # DNS缓存时间
)

async with aiohttp.ClientSession(connector=connector) as session:
    # 复用连接
    pass
```

---

## 计算优化

### 1. NumPy 向量化

```python
import numpy as np

# 差: Python 循环
def calculate_distances_slow(points):
    n = len(points)
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            dist = ((points[i][0] - points[j][0]) ** 2 +
                    (points[i][1] - points[j][1]) ** 2) ** 0.5
            distances.append(dist)
    return distances

# 好: NumPy 向量化
def calculate_distances_fast(points):
    points = np.array(points)
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff ** 2, axis=-1))
    return distances[np.triu_indices(len(points), k=1)]
```

### 2. 使用 Cython

```python
# example.pyx
cdef int fibonacci(int n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def py_fibonacci(n):
    return fibonacci(n)

# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("example.pyx")
)

# 编译: python setup.py build_ext --inplace
```

### 3. 使用 Numba JIT

```python
from numba import jit, prange
import numpy as np

@jit(nopython=True)
def sum_squares(arr):
    """JIT编译的求和"""
    total = 0.0
    for i in range(len(arr)):
        total += arr[i] ** 2
    return total

@jit(nopython=True, parallel=True)
def parallel_sum(arr):
    """并行JIT"""
    total = 0.0
    for i in prange(len(arr)):
        total += arr[i]
    return total
```

---

## 性能测试

### 1. timeit 基准测试

```python
import timeit

# 简单计时
result = timeit.timeit(
    'sum(range(1000))',
    number=10000
)
print(f"Average time: {result / 10000:.6f} seconds")

# 比较两种实现
def method1():
    return [x ** 2 for x in range(1000)]

def method2():
    return list(map(lambda x: x ** 2, range(1000)))

t1 = timeit.timeit(method1, number=1000)
t2 = timeit.timeit(method2, number=1000)
print(f"Method 1: {t1:.4f}s, Method 2: {t2:.4f}s")
```

### 2. pytest-benchmark

```python
# pip install pytest-benchmark

def test_performance(benchmark):
    """使用 pytest-benchmark"""
    result = benchmark(expensive_function, arg1, arg2)
    assert result is not None

# 运行: pytest --benchmark-only
```

### 3. 自定义性能测试框架

```python
import time
from dataclasses import dataclass
from typing import Callable, List
from statistics import mean, stdev

@dataclass
class BenchmarkResult:
    name: str
    iterations: int
    total_time: float
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float

    def __str__(self):
        return (
            f"{self.name}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Mean: {self.mean_time*1000:.3f}ms\n"
            f"  Std Dev: {self.std_dev*1000:.3f}ms\n"
            f"  Min: {self.min_time*1000:.3f}ms\n"
            f"  Max: {self.max_time*1000:.3f}ms"
        )

def benchmark(
    func: Callable,
    *args,
    iterations: int = 100,
    warmup: int = 10,
    **kwargs
) -> BenchmarkResult:
    """运行基准测试"""
    # 预热
    for _ in range(warmup):
        func(*args, **kwargs)

    # 测试
    times: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult(
        name=func.__name__,
        iterations=iterations,
        total_time=sum(times),
        mean_time=mean(times),
        std_dev=stdev(times) if len(times) > 1 else 0,
        min_time=min(times),
        max_time=max(times)
    )

# 使用
result = benchmark(my_function, arg1, arg2, iterations=1000)
print(result)
```

---

## 性能优化清单

| 类别 | 检查项 | 优化方法 |
|------|--------|----------|
| 数据结构 | 查找操作使用 list | 改用 set/dict |
| 数据结构 | 频繁头部操作 | 改用 deque |
| 循环 | for 循环构建列表 | 改用列表推导式 |
| 循环 | 循环内重复计算 | 提取到循环外 |
| 字符串 | 循环内字符串拼接 | 改用 join |
| 内存 | 大量小对象 | 使用 __slots__ |
| 内存 | 一次性加载大文件 | 使用生成器 |
| 数据库 | N+1 查询 | 使用预加载 |
| 数据库 | 逐条插入 | 批量插入 |
| 异步 | 串行请求 | 并发请求 |
| 计算 | Python 循环计算 | NumPy 向量化 |
