# 性能优化指南

## 1. 延迟优化

### 1.1 网络层优化

**内核旁路技术：**

| 技术 | 延迟改善 | 适用场景 |
|------|----------|----------|
| DPDK | 50-80% | 高频交易 |
| Solarflare | 60-90% | 超低延迟 |
| Kernel Bypass | 40-60% | 通用优化 |

**实施要点：**
- 使用用户态网络栈
- 避免系统调用开销
- 直接访问网卡DMA

### 1.2 内存层优化

**零拷贝技术：**
```cpp
// 避免数据拷贝
void process_message(const char* buffer, size_t len) {
    // 直接处理原始buffer，不做拷贝
    parse_in_place(buffer, len);
}
```

**内存池预分配：**
```cpp
class ObjectPool<T> {
    std::vector<T> pool;
    std::queue<T*> free_list;
public:
    T* allocate() {
        if (free_list.empty()) return nullptr;
        T* obj = free_list.front();
        free_list.pop();
        return obj;
    }
    void deallocate(T* obj) {
        free_list.push(obj);
    }
};
```

### 1.3 CPU层优化

**CPU亲和性设置：**
```cpp
// 绑定线程到指定CPU核心
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(core_id, &cpuset);
pthread_setaffinity_np(thread, sizeof(cpuset), &cpuset);
```

**NUMA优化：**
- 本地内存访问
- 避免跨NUMA节点
- 合理分配线程

---

## 2. 吞吐量优化

### 2.1 批处理

**消息批量处理：**
```python
def process_batch(messages: List[Message]):
    # 批量处理减少系统调用
    batch_size = 100
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i+batch_size]
        process_messages(batch)
```

### 2.2 异步IO

**使用io_uring（Linux 5.1+）：**
- 减少系统调用次数
- 支持批量提交
- 零拷贝支持

**使用epoll：**
```cpp
int epoll_fd = epoll_create1(0);
struct epoll_event events[MAX_EVENTS];
int n = epoll_wait(epoll_fd, events, MAX_EVENTS, timeout);
```

### 2.3 无锁队列

**SPSC队列（单生产者单消费者）：**
```cpp
template<typename T>
class SPSCQueue {
    std::atomic<size_t> head{0};
    std::atomic<size_t> tail{0};
    std::vector<T> buffer;
public:
    bool push(const T& item);
    bool pop(T& item);
};
```

---

## 3. 资源利用优化

### 3.1 内存优化

**避免GC影响：**
- C++/Rust：无GC
- Python：对象池复用
- Java：调优GC参数

**内存对齐：**
```cpp
struct alignas(64) CacheLine {
    // 64字节对齐，避免伪共享
    std::atomic<int> counter;
    char padding[60];
};
```

### 3.2 CPU优化

**SIMD向量化：**
```cpp
// 使用AVX2计算
__m256d a = _mm256_load_pd(data);
__m256d b = _mm256_load_pd(data + 4);
__m256d c = _mm256_add_pd(a, b);
```

**分支预测优化：**
```cpp
// 使用likely/unlikely提示
if (__builtin_expect(condition, 1)) {
    // 高概率执行路径
}
```

---

## 4. 性能测试方法

### 4.1 延迟测试

**测试指标：**
- P50/P90/P99/P999延迟
- 最大延迟
- 延迟抖动

**测试方法：**
```python
import time
latencies = []
for _ in range(10000):
    start = time.perf_counter_ns()
    process_order(order)
    end = time.perf_counter_ns()
    latencies.append(end - start)

p99 = np.percentile(latencies, 99)
```

### 4.2 吞吐量测试

**测试指标：**
- 每秒处理消息数（TPS）
- 峰值吞吐量
- 持续吞吐量

### 4.3 压力测试

**测试场景：**
- 正常负载：50%容量
- 高负载：80%容量
- 峰值负载：100%+容量

---

## 5. 常见性能问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| 锁竞争 | CPU高但吞吐低 | 无锁数据结构 |
| GC停顿 | 周期性延迟抖动 | 减少对象分配 |
| 缓存未命中 | 内存带宽高 | 优化数据布局 |
| 网络延迟 | 固定延迟开销 | 内核旁路/专线 |

---

## 6. 量化系统特定优化

### 6.1 行情处理优化

**优化策略：**
- 行情解析：使用定长消息格式
- 行情分发：使用广播而非点对点
- 行情缓存：环形缓冲区存储最近N条

### 6.2 订单处理优化

**关键路径优化：**
```
信号生成 → 风控检查 → 订单发送
   ↓           ↓           ↓
 <10μs      <50μs       <100μs
```

### 6.3 回测性能优化

**优化方向：**
- 数据预加载：避免IO等待
- 向量化计算：批量处理K线
- 并行回测：多策略并行执行
