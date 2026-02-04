# Python 并发编程指南

## 并发模型选择

### 选择决策树

```
                    ┌─────────────────┐
                    │   任务类型？     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ IO密集型 │    │ CPU密集型│    │  混合型  │
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────────┐
        │ asyncio │    │ multi-  │    │ asyncio +   │
        │         │    │ process │    │ ProcessPool │
        └─────────┘    └─────────┘    └─────────────┘
```

### 模型对比

| 模型 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| asyncio | IO密集型（网络、文件） | 低开销、高并发 | 需要异步库支持 |
| threading | IO密集型、简单并发 | 简单易用 | GIL限制、线程安全 |
| multiprocessing | CPU密集型 | 真正并行 | 进程开销大、IPC复杂 |
| concurrent.futures | 通用并发 | API简洁 | 灵活性较低 |

---

## asyncio 异步编程

### 基础用法

```python
import asyncio
from typing import List, Any

async def fetch_data(url: str) -> dict:
    """异步获取数据"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_items(items: List[str]) -> List[dict]:
    """并发处理多个项目"""
    tasks = [fetch_data(item) for item in items]
    return await asyncio.gather(*tasks)

# 运行异步函数
async def main():
    urls = ["http://api.example.com/1", "http://api.example.com/2"]
    results = await process_items(urls)
    return results

# Python 3.10+
asyncio.run(main())
```

### 并发控制

```python
import asyncio
from contextlib import asynccontextmanager

class AsyncRateLimiter:
    """异步速率限制器"""

    def __init__(self, rate: int, period: float = 1.0):
        self.rate = rate
        self.period = period
        self.semaphore = asyncio.Semaphore(rate)
        self._tokens = rate
        self._updated_at = asyncio.get_event_loop().time()

    async def acquire(self) -> None:
        await self.semaphore.acquire()
        # 令牌桶算法
        now = asyncio.get_event_loop().time()
        elapsed = now - self._updated_at
        self._tokens = min(self.rate, self._tokens + elapsed * self.rate / self.period)
        self._updated_at = now

        if self._tokens < 1:
            await asyncio.sleep((1 - self._tokens) * self.period / self.rate)

    def release(self) -> None:
        self.semaphore.release()

    @asynccontextmanager
    async def limit(self):
        await self.acquire()
        try:
            yield
        finally:
            self.release()

# 使用示例
rate_limiter = AsyncRateLimiter(rate=10, period=1.0)  # 每秒10个请求

async def rate_limited_fetch(url: str) -> dict:
    async with rate_limiter.limit():
        return await fetch_data(url)
```

### 超时控制

```python
import asyncio
from typing import TypeVar, Callable, Awaitable

T = TypeVar('T')

async def with_timeout(
    coro: Awaitable[T],
    timeout: float,
    default: T = None
) -> T:
    """带超时的异步调用"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return default

async def with_retry(
    func: Callable[..., Awaitable[T]],
    *args,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    **kwargs
) -> T:
    """带重试的异步调用"""
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff

    raise last_exception

# 使用示例
result = await with_timeout(fetch_data(url), timeout=5.0, default={})
result = await with_retry(fetch_data, url, max_retries=3)
```

### 异步上下文管理器

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class AsyncDatabasePool:
    """异步数据库连接池"""

    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool = None

    async def initialize(self) -> None:
        self._pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size
        )

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator:
        async with self._pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn

# 使用示例
pool = AsyncDatabasePool("postgresql://localhost/db")
await pool.initialize()

async with pool.transaction() as conn:
    await conn.execute("INSERT INTO users ...")
    await conn.execute("UPDATE accounts ...")
```

---

## threading 多线程

### 线程安全的数据结构

```python
import threading
from queue import Queue, Empty
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class ThreadSafeCounter:
    """线程安全计数器"""

    def __init__(self, initial: int = 0):
        self._value = initial
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        with self._lock:
            self._value -= amount
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

class ThreadSafeDict(Generic[T]):
    """线程安全字典"""

    def __init__(self):
        self._dict: dict[str, T] = {}
        self._lock = threading.RLock()

    def get(self, key: str, default: T = None) -> Optional[T]:
        with self._lock:
            return self._dict.get(key, default)

    def set(self, key: str, value: T) -> None:
        with self._lock:
            self._dict[key] = value

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._dict:
                del self._dict[key]
                return True
            return False

    def get_or_create(self, key: str, factory: callable) -> T:
        with self._lock:
            if key not in self._dict:
                self._dict[key] = factory()
            return self._dict[key]
```

### 生产者-消费者模式

```python
import threading
from queue import Queue
from typing import Callable, Any, List

class WorkerPool:
    """工作线程池"""

    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.task_queue: Queue = Queue()
        self.result_queue: Queue = Queue()
        self.workers: List[threading.Thread] = []
        self._shutdown = threading.Event()

    def start(self) -> None:
        """启动工作线程"""
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)

    def _worker_loop(self) -> None:
        """工作线程主循环"""
        while not self._shutdown.is_set():
            try:
                task_id, func, args, kwargs = self.task_queue.get(timeout=0.1)
                try:
                    result = func(*args, **kwargs)
                    self.result_queue.put((task_id, result, None))
                except Exception as e:
                    self.result_queue.put((task_id, None, e))
                finally:
                    self.task_queue.task_done()
            except Empty:
                continue

    def submit(self, func: Callable, *args, **kwargs) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())
        self.task_queue.put((task_id, func, args, kwargs))
        return task_id

    def shutdown(self, wait: bool = True) -> None:
        """关闭线程池"""
        self._shutdown.set()
        if wait:
            self.task_queue.join()
            for worker in self.workers:
                worker.join()

# 使用示例
pool = WorkerPool(num_workers=4)
pool.start()

task_ids = []
for item in items:
    task_id = pool.submit(process_item, item)
    task_ids.append(task_id)

pool.shutdown(wait=True)
```

### 读写锁

```python
import threading
from contextlib import contextmanager

class ReadWriteLock:
    """读写锁：允许多个读者或单个写者"""

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    @contextmanager
    def read_lock(self):
        """获取读锁"""
        with self._read_ready:
            self._readers += 1
        try:
            yield
        finally:
            with self._read_ready:
                self._readers -= 1
                if self._readers == 0:
                    self._read_ready.notify_all()

    @contextmanager
    def write_lock(self):
        """获取写锁"""
        with self._read_ready:
            while self._readers > 0:
                self._read_ready.wait()
            yield

# 使用示例
class CachedData:
    def __init__(self):
        self._data = {}
        self._lock = ReadWriteLock()

    def get(self, key: str) -> Any:
        with self._lock.read_lock():
            return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        with self._lock.write_lock():
            self._data[key] = value
```

---

## multiprocessing 多进程

### 进程池

```python
from multiprocessing import Pool, cpu_count
from typing import List, Callable, Any
import functools

def cpu_bound_task(data: Any) -> Any:
    """CPU密集型任务"""
    # 复杂计算
    return result

def parallel_process(
    func: Callable,
    items: List[Any],
    num_processes: int = None
) -> List[Any]:
    """并行处理"""
    if num_processes is None:
        num_processes = cpu_count()

    with Pool(processes=num_processes) as pool:
        results = pool.map(func, items)
    return results

# 带进度的并行处理
from tqdm import tqdm

def parallel_process_with_progress(
    func: Callable,
    items: List[Any],
    num_processes: int = None,
    desc: str = "Processing"
) -> List[Any]:
    """带进度条的并行处理"""
    if num_processes is None:
        num_processes = cpu_count()

    with Pool(processes=num_processes) as pool:
        results = list(tqdm(
            pool.imap(func, items),
            total=len(items),
            desc=desc
        ))
    return results
```

### 进程间通信

```python
from multiprocessing import Process, Queue, Pipe
from typing import Any

class ProcessWorker:
    """进程工作器"""

    def __init__(self, task_queue: Queue, result_queue: Queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.process = None

    def start(self) -> None:
        self.process = Process(target=self._run)
        self.process.start()

    def _run(self) -> None:
        while True:
            task = self.task_queue.get()
            if task is None:  # 毒丸
                break
            task_id, func, args = task
            try:
                result = func(*args)
                self.result_queue.put((task_id, result, None))
            except Exception as e:
                self.result_queue.put((task_id, None, e))

    def stop(self) -> None:
        self.task_queue.put(None)
        self.process.join()

# 使用共享内存
from multiprocessing import Value, Array

class SharedCounter:
    """共享内存计数器"""

    def __init__(self, initial: int = 0):
        self._value = Value('i', initial)

    def increment(self) -> int:
        with self._value.get_lock():
            self._value.value += 1
            return self._value.value

    @property
    def value(self) -> int:
        return self._value.value
```

---

## concurrent.futures

### ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Dict

def parallel_io_tasks(
    func: Callable,
    items: List[Any],
    max_workers: int = 10
) -> Dict[Any, Any]:
    """并行执行IO任务"""
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_item = {
            executor.submit(func, item): item
            for item in items
        }

        # 获取结果
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                results[item] = future.result()
            except Exception as e:
                results[item] = e

    return results

# 带超时的执行
def parallel_with_timeout(
    func: Callable,
    items: List[Any],
    timeout: float = 30.0,
    max_workers: int = 10
) -> List[Any]:
    """带超时的并行执行"""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, item) for item in items]

        for future in futures:
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except TimeoutError:
                results.append(None)
            except Exception as e:
                results.append(e)

    return results
```

### ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor
from typing import List, Callable, Any

def parallel_cpu_tasks(
    func: Callable,
    items: List[Any],
    max_workers: int = None
) -> List[Any]:
    """并行执行CPU密集型任务"""
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, items))
    return results

# 混合使用
async def hybrid_parallel(
    io_func: Callable,
    cpu_func: Callable,
    io_items: List[Any],
    cpu_items: List[Any]
) -> tuple:
    """混合并行：IO用线程，CPU用进程"""
    loop = asyncio.get_event_loop()

    # IO任务用线程池
    with ThreadPoolExecutor() as thread_pool:
        io_futures = [
            loop.run_in_executor(thread_pool, io_func, item)
            for item in io_items
        ]

    # CPU任务用进程池
    with ProcessPoolExecutor() as process_pool:
        cpu_futures = [
            loop.run_in_executor(process_pool, cpu_func, item)
            for item in cpu_items
        ]

    io_results = await asyncio.gather(*io_futures)
    cpu_results = await asyncio.gather(*cpu_futures)

    return io_results, cpu_results
```

---

## 异步与同步混合

### 在异步代码中运行同步函数

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# 全局线程池
_thread_pool = ThreadPoolExecutor(max_workers=10)

async def run_sync(func: Callable, *args, **kwargs) -> Any:
    """在线程池中运行同步函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _thread_pool,
        partial(func, *args, **kwargs)
    )

# 使用示例
def blocking_io_operation(path: str) -> str:
    """阻塞的IO操作"""
    with open(path) as f:
        return f.read()

async def async_read_file(path: str) -> str:
    """异步读取文件"""
    return await run_sync(blocking_io_operation, path)
```

### 在同步代码中运行异步函数

```python
import asyncio
from typing import TypeVar, Callable, Awaitable

T = TypeVar('T')

def run_async(coro: Awaitable[T]) -> T:
    """在同步代码中运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)

# 或使用 asyncio.run (Python 3.7+)
def sync_wrapper(async_func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """将异步函数包装为同步函数"""
    def wrapper(*args, **kwargs) -> T:
        return asyncio.run(async_func(*args, **kwargs))
    return wrapper

# 使用示例
@sync_wrapper
async def async_fetch(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# 可以同步调用
result = async_fetch("http://api.example.com")
```

---

## 最佳实践

### 1. 避免死锁

```python
import threading
from contextlib import contextmanager

class LockManager:
    """锁管理器：按顺序获取锁避免死锁"""

    def __init__(self):
        self._locks: dict[str, threading.Lock] = {}
        self._lock_order: list[str] = []

    def register(self, name: str) -> None:
        self._locks[name] = threading.Lock()
        self._lock_order.append(name)

    @contextmanager
    def acquire_multiple(self, *names: str):
        """按固定顺序获取多个锁"""
        # 按注册顺序排序
        sorted_names = sorted(names, key=lambda n: self._lock_order.index(n))

        acquired = []
        try:
            for name in sorted_names:
                self._locks[name].acquire()
                acquired.append(name)
            yield
        finally:
            for name in reversed(acquired):
                self._locks[name].release()
```

### 2. 优雅关闭

```python
import asyncio
import signal
from typing import Set

class GracefulShutdown:
    """优雅关闭管理器"""

    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._tasks: Set[asyncio.Task] = set()

    def setup_signals(self) -> None:
        """设置信号处理"""
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(
                sig,
                self._shutdown_event.set
            )

    def register_task(self, task: asyncio.Task) -> None:
        """注册任务"""
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def wait_for_shutdown(self) -> None:
        """等待关闭信号"""
        await self._shutdown_event.wait()

    async def shutdown(self, timeout: float = 30.0) -> None:
        """执行关闭"""
        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        # 等待任务完成
        if self._tasks:
            await asyncio.wait(self._tasks, timeout=timeout)

# 使用示例
async def main():
    shutdown = GracefulShutdown()
    shutdown.setup_signals()

    # 启动后台任务
    task = asyncio.create_task(background_worker())
    shutdown.register_task(task)

    # 等待关闭
    await shutdown.wait_for_shutdown()
    await shutdown.shutdown()
```

### 3. 资源池化

```python
import asyncio
from typing import TypeVar, Generic, Callable, Awaitable
from contextlib import asynccontextmanager

T = TypeVar('T')

class AsyncPool(Generic[T]):
    """通用异步资源池"""

    def __init__(
        self,
        factory: Callable[[], Awaitable[T]],
        max_size: int = 10,
        min_size: int = 1
    ):
        self.factory = factory
        self.max_size = max_size
        self.min_size = min_size
        self._pool: asyncio.Queue[T] = asyncio.Queue(maxsize=max_size)
        self._size = 0
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化最小数量的资源"""
        for _ in range(self.min_size):
            resource = await self.factory()
            await self._pool.put(resource)
            self._size += 1

    @asynccontextmanager
    async def acquire(self):
        """获取资源"""
        resource = None
        try:
            # 尝试从池中获取
            try:
                resource = self._pool.get_nowait()
            except asyncio.QueueEmpty:
                # 池为空，创建新资源
                async with self._lock:
                    if self._size < self.max_size:
                        resource = await self.factory()
                        self._size += 1
                    else:
                        # 等待可用资源
                        resource = await self._pool.get()

            yield resource
        finally:
            if resource is not None:
                await self._pool.put(resource)
```
