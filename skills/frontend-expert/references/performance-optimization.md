# 前端性能优化指南

## 性能指标

### Core Web Vitals

| 指标 | 全称 | 含义 | 良好标准 |
|------|------|------|----------|
| LCP | Largest Contentful Paint | 最大内容绘制 | < 2.5s |
| FID | First Input Delay | 首次输入延迟 | < 100ms |
| CLS | Cumulative Layout Shift | 累积布局偏移 | < 0.1 |
| INP | Interaction to Next Paint | 交互到下一次绘制 | < 200ms |

### 其他重要指标

| 指标 | 含义 | 良好标准 |
|------|------|----------|
| FCP | 首次内容绘制 | < 1.8s |
| TTI | 可交互时间 | < 3.8s |
| TBT | 总阻塞时间 | < 200ms |
| TTFB | 首字节时间 | < 800ms |

---

## 加载性能优化

### 1. 代码分割

**路由懒加载：**
```typescript
// Vue Router
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/pages/Dashboard.vue')
  },
  {
    path: '/user',
    component: () => import('@/pages/User.vue')
  }
]

// React Router
const Dashboard = lazy(() => import('@/pages/Dashboard'))
const User = lazy(() => import('@/pages/User'))

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/user" element={<User />} />
  </Routes>
</Suspense>
```

**组件懒加载：**
```vue
<!-- Vue 异步组件 -->
<script setup>
import { defineAsyncComponent } from 'vue'

const HeavyChart = defineAsyncComponent({
  loader: () => import('./HeavyChart.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
  timeout: 10000
})
</script>

<template>
  <HeavyChart v-if="showChart" />
</template>
```

**第三方库按需加载：**
```typescript
// 动态导入大型库
const loadEcharts = async () => {
  const echarts = await import('echarts/core')
  const { BarChart } = await import('echarts/charts')
  const { GridComponent } = await import('echarts/components')
  const { CanvasRenderer } = await import('echarts/renderers')

  echarts.use([BarChart, GridComponent, CanvasRenderer])
  return echarts
}

// 使用时
const initChart = async () => {
  const echarts = await loadEcharts()
  const chart = echarts.init(chartRef.value)
  chart.setOption(options)
}
```

### 2. 资源预加载

```html
<!-- 预加载关键资源 -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/critical.css" as="style">
<link rel="preload" href="/hero-image.webp" as="image">

<!-- 预连接第三方域名 -->
<link rel="preconnect" href="https://api.example.com">
<link rel="dns-prefetch" href="https://cdn.example.com">

<!-- 预获取下一页资源 -->
<link rel="prefetch" href="/next-page.js">
```

```typescript
// 编程式预加载
// 鼠标悬停时预加载
const handleMouseEnter = () => {
  import('./HeavyComponent.vue')
}

// 空闲时预加载
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    import('./NonCriticalComponent.vue')
  })
}
```

### 3. 图片优化

**响应式图片：**
```html
<picture>
  <source
    media="(min-width: 1200px)"
    srcset="/images/hero-large.webp"
    type="image/webp"
  >
  <source
    media="(min-width: 768px)"
    srcset="/images/hero-medium.webp"
    type="image/webp"
  >
  <img
    src="/images/hero-small.jpg"
    alt="Hero"
    loading="lazy"
    decoding="async"
  >
</picture>
```

**图片懒加载组件：**
```vue
<!-- components/LazyImage.vue -->
<template>
  <div ref="containerRef" class="lazy-image" :style="{ aspectRatio }">
    <img
      v-if="isVisible"
      :src="src"
      :alt="alt"
      :class="{ loaded: isLoaded }"
      @load="isLoaded = true"
    />
    <div v-else class="placeholder" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  src: string
  alt: string
  aspectRatio?: string
}>()

const containerRef = ref<HTMLElement>()
const isVisible = ref(false)
const isLoaded = ref(false)

let observer: IntersectionObserver

onMounted(() => {
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        isVisible.value = true
        observer.disconnect()
      }
    },
    { rootMargin: '100px' }
  )

  if (containerRef.value) {
    observer.observe(containerRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.lazy-image {
  position: relative;
  overflow: hidden;
  background: #f0f0f0;
}

.lazy-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s;
}

.lazy-image img.loaded {
  opacity: 1;
}

.placeholder {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

---

## 渲染性能优化

### 1. 虚拟列表

```vue
<!-- components/VirtualList.vue -->
<template>
  <div
    ref="containerRef"
    class="virtual-list"
    :style="{ height: `${containerHeight}px` }"
    @scroll="handleScroll"
  >
    <div :style="{ height: `${totalHeight}px`, position: 'relative' }">
      <div
        v-for="item in visibleItems"
        :key="item.index"
        :style="{
          position: 'absolute',
          top: `${item.offset}px`,
          width: '100%',
          height: `${itemHeight}px`
        }"
      >
        <slot :item="item.data" :index="item.index" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  items: T[]
  itemHeight: number
  containerHeight: number
  overscan?: number
}>()

const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)

const overscan = props.overscan ?? 3

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleItems = computed(() => {
  const startIndex = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - overscan)
  const endIndex = Math.min(
    props.items.length,
    Math.ceil((scrollTop.value + props.containerHeight) / props.itemHeight) + overscan
  )

  return props.items.slice(startIndex, endIndex).map((data, i) => ({
    data,
    index: startIndex + i,
    offset: (startIndex + i) * props.itemHeight
  }))
})

const handleScroll = (e: Event) => {
  scrollTop.value = (e.target as HTMLElement).scrollTop
}
</script>

<style scoped>
.virtual-list {
  overflow-y: auto;
}
</style>
```

### 2. 防抖与节流

```typescript
// utils/debounce.ts
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

// utils/throttle.ts
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// 使用示例
const handleSearch = debounce((query: string) => {
  fetchSearchResults(query)
}, 300)

const handleScroll = throttle(() => {
  updateScrollPosition()
}, 100)
```

### 3. Vue 渲染优化

**v-once 静态内容：**
```vue
<template>
  <!-- 只渲染一次的静态内容 -->
  <header v-once>
    <h1>{{ title }}</h1>
    <nav>...</nav>
  </header>

  <!-- 动态内容 -->
  <main>
    <article v-for="post in posts" :key="post.id">
      {{ post.content }}
    </article>
  </main>
</template>
```

**v-memo 条件缓存：**
```vue
<template>
  <div v-for="item in list" :key="item.id" v-memo="[item.id, item.selected]">
    <!-- 只有当 item.id 或 item.selected 变化时才重新渲染 -->
    <ExpensiveComponent :item="item" />
  </div>
</template>
```

**shallowRef 浅层响应：**
```typescript
import { shallowRef, triggerRef } from 'vue'

// 大型数据使用 shallowRef
const largeList = shallowRef<Item[]>([])

// 修改后手动触发更新
const updateItem = (index: number, newItem: Item) => {
  largeList.value[index] = newItem
  triggerRef(largeList)
}
```

### 4. React 渲染优化

**React.memo：**
```tsx
interface ItemProps {
  item: Item
  onSelect: (id: string) => void
}

const ListItem = React.memo<ItemProps>(
  ({ item, onSelect }) => {
    return (
      <div onClick={() => onSelect(item.id)}>
        {item.name}
      </div>
    )
  },
  // 自定义比较函数
  (prevProps, nextProps) => {
    return prevProps.item.id === nextProps.item.id &&
           prevProps.item.name === nextProps.item.name
  }
)
```

**useMemo 和 useCallback：**
```tsx
const ExpensiveList: React.FC<{ items: Item[]; filter: string }> = ({ items, filter }) => {
  // 缓存计算结果
  const filteredItems = useMemo(
    () => items.filter(item => item.name.includes(filter)),
    [items, filter]
  )

  // 缓存回调函数
  const handleSelect = useCallback((id: string) => {
    setSelectedId(id)
  }, [])

  return (
    <div>
      {filteredItems.map(item => (
        <ListItem key={item.id} item={item} onSelect={handleSelect} />
      ))}
    </div>
  )
}
```

---

## 网络性能优化

### 1. 请求优化

**请求合并：**
```typescript
// 批量请求合并
class RequestBatcher<T, R> {
  private queue: { key: T; resolve: (value: R) => void }[] = []
  private timeout: ReturnType<typeof setTimeout> | null = null

  constructor(
    private batchFn: (keys: T[]) => Promise<Map<T, R>>,
    private delay = 10
  ) {}

  async load(key: T): Promise<R> {
    return new Promise((resolve) => {
      this.queue.push({ key, resolve })

      if (!this.timeout) {
        this.timeout = setTimeout(() => this.flush(), this.delay)
      }
    })
  }

  private async flush() {
    const batch = this.queue
    this.queue = []
    this.timeout = null

    const keys = batch.map(item => item.key)
    const results = await this.batchFn(keys)

    batch.forEach(({ key, resolve }) => {
      resolve(results.get(key)!)
    })
  }
}

// 使用
const userBatcher = new RequestBatcher(async (ids: string[]) => {
  const users = await api.getUsersByIds(ids)
  return new Map(users.map(u => [u.id, u]))
})

// 多个请求会被合并
const user1 = await userBatcher.load('1')
const user2 = await userBatcher.load('2')
```

**请求缓存：**
```typescript
// composables/useRequest.ts
const cache = new Map<string, { data: any; timestamp: number }>()

export function useCachedRequest<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: { ttl?: number; staleWhileRevalidate?: boolean } = {}
) {
  const { ttl = 5 * 60 * 1000, staleWhileRevalidate = true } = options

  const data = ref<T>()
  const loading = ref(false)
  const error = ref<Error>()

  const fetchData = async () => {
    const cached = cache.get(key)
    const now = Date.now()

    // 返回缓存数据
    if (cached && now - cached.timestamp < ttl) {
      data.value = cached.data
      return
    }

    // stale-while-revalidate 策略
    if (cached && staleWhileRevalidate) {
      data.value = cached.data
    }

    loading.value = true
    try {
      const result = await fetcher()
      data.value = result
      cache.set(key, { data: result, timestamp: now })
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, refetch: fetchData }
}
```

### 2. 资源压缩

**Vite 配置：**
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  build: {
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 压缩选项
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    // 分包策略
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['element-plus'],
          'utils': ['lodash-es', 'dayjs']
        }
      }
    }
  },
  plugins: [
    // Gzip 压缩
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz'
    }),
    // Brotli 压缩
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br'
    })
  ]
})
```

---

## 性能监控

### 1. Performance API

```typescript
// utils/performance.ts
export const measurePerformance = () => {
  const timing = performance.timing
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

  return {
    // DNS 查询时间
    dns: timing.domainLookupEnd - timing.domainLookupStart,
    // TCP 连接时间
    tcp: timing.connectEnd - timing.connectStart,
    // 首字节时间
    ttfb: timing.responseStart - timing.requestStart,
    // DOM 解析时间
    domParse: timing.domInteractive - timing.responseEnd,
    // DOM 完成时间
    domComplete: timing.domComplete - timing.domLoading,
    // 页面加载时间
    loadTime: timing.loadEventEnd - timing.navigationStart
  }
}

// 监控 LCP
const observeLCP = (callback: (value: number) => void) => {
  const observer = new PerformanceObserver((list) => {
    const entries = list.getEntries()
    const lastEntry = entries[entries.length - 1]
    callback(lastEntry.startTime)
  })

  observer.observe({ type: 'largest-contentful-paint', buffered: true })
}

// 监控 FID
const observeFID = (callback: (value: number) => void) => {
  const observer = new PerformanceObserver((list) => {
    const entries = list.getEntries()
    entries.forEach((entry: any) => {
      callback(entry.processingStart - entry.startTime)
    })
  })

  observer.observe({ type: 'first-input', buffered: true })
}

// 监控 CLS
const observeCLS = (callback: (value: number) => void) => {
  let clsValue = 0

  const observer = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry: any) => {
      if (!entry.hadRecentInput) {
        clsValue += entry.value
        callback(clsValue)
      }
    })
  })

  observer.observe({ type: 'layout-shift', buffered: true })
}
```

### 2. 性能报告

```typescript
// utils/reportPerformance.ts
interface PerformanceReport {
  lcp: number
  fid: number
  cls: number
  ttfb: number
  fcp: number
}

export const reportPerformance = async (report: PerformanceReport) => {
  // 发送到分析服务
  await fetch('/api/analytics/performance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...report,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: Date.now()
    })
  })
}

// 初始化性能监控
export const initPerformanceMonitoring = () => {
  const report: Partial<PerformanceReport> = {}

  observeLCP((value) => { report.lcp = value })
  observeFID((value) => { report.fid = value })
  observeCLS((value) => { report.cls = value })

  // 页面加载完成后上报
  window.addEventListener('load', () => {
    setTimeout(() => {
      const timing = measurePerformance()
      reportPerformance({
        ...report as PerformanceReport,
        ttfb: timing.ttfb,
        fcp: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
      })
    }, 3000)
  })
}
```

---

## 性能优化清单

| 类别 | 优化项 | 优先级 |
|------|--------|--------|
| 加载 | 路由懒加载 | 高 |
| 加载 | 图片懒加载 | 高 |
| 加载 | 资源预加载 | 中 |
| 加载 | 代码分割 | 高 |
| 渲染 | 虚拟列表 | 高 |
| 渲染 | 防抖节流 | 中 |
| 渲染 | 组件缓存 | 中 |
| 网络 | 请求合并 | 中 |
| 网络 | 响应缓存 | 高 |
| 网络 | Gzip压缩 | 高 |
| 构建 | Tree-shaking | 高 |
| 构建 | 分包策略 | 中 |
