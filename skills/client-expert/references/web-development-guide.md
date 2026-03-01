# Web 前端开发指南

> 本文档为 client-expert 技能的 Web 平台参考指南，涵盖主流技术栈、工程化配置、架构模式、性能优化与安全实践。

---

## 1. Web 前端技术栈总览

| 层级 | 推荐方案 | 说明 |
|------|---------|------|
| 框架 | Vue 3.4+ / React 18+ | 根据团队和项目特点选型 |
| 语言 | TypeScript 5.3+ | 强类型，提升可维护性 |
| 构建工具 | Vite 5+ | 基于 ESBuild + Rollup，开发体验极佳 |
| 包管理 | pnpm 8+ | 磁盘效率高，支持 monorepo |
| 状态管理 | Pinia (Vue) / Zustand (React) | 轻量、类型友好 |
| 路由 | Vue Router 4 / React Router 6 | 官方/社区首选 |
| HTTP | Axios 1.x | 拦截器、取消请求、类型支持完善 |
| CSS 方案 | Tailwind CSS 3+ / UnoCSS | 原子化 CSS，按需生成 |
| 测试 | Vitest + Playwright | 单元测试 + E2E 测试 |
| 代码规范 | ESLint 9 + Prettier | Flat Config 模式 |

### 技术栈版本兼容矩阵

```
Vue 3.4+   → TypeScript 5.3+ → Vite 5+ → Pinia 2.1+
React 18+  → TypeScript 5.3+ → Vite 5+ → Zustand 4+
```

---

## 2. 项目工程配置

### 2.1 Vite 配置

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'  // 或 react() for React
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@utils': resolve(__dirname, 'src/utils'),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    build: {
      target: 'es2020',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'pinia'],
            // React: ['react', 'react-dom', 'react-router-dom']
          },
        },
      },
    },
  }
})
```

### 2.2 TypeScript 配置

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": false,
    "jsx": "preserve",
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]
}
```

### 2.3 ESLint Flat Config

```typescript
// eslint.config.js
import eslint from '@eslint/js'
import tseslint from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...pluginVue.configs['flat/recommended'],
  {
    rules: {
      'no-console': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  }
)
```

### 2.4 环境变量管理

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080
VITE_APP_TITLE=My App (Dev)

# .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=My App
```

```typescript
// src/env.d.ts — 类型声明
/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
}
```

> 规则：仅 `VITE_` 前缀的变量会暴露给客户端，敏感信息禁止使用此前缀。

---

## 3. Vue 3 vs React 18 选型指南

| 维度 | Vue 3 | React 18 |
|------|-------|----------|
| 学习曲线 | 较低，模板语法直观 | 中等，JSX + Hooks 需适应 |
| 响应式 | 内置 Proxy 响应式 | 手动 setState / useReducer |
| 模板 vs JSX | SFC 模板 + `<script setup>` | JSX / TSX |
| 生态规模 | 中大型，中文社区强 | 最大，英文资源丰富 |
| 状态管理 | Pinia（官方） | Zustand / Redux Toolkit |
| SSR | Nuxt 3 | Next.js 14+ |
| 适用场景 | 中后台、快速交付 | 大型应用、跨端（RN） |

### 选型建议

- 团队 Vue 经验丰富 + 中后台项目 → **Vue 3**
- 需要跨端（Web + React Native）→ **React 18**
- 新团队无历史包袱 → 根据招聘市场和项目复杂度决定

---

## 4. 架构模式

### 4.1 Vue 3: Composition API + Pinia

```
src/
├── api/              # 接口定义
├── assets/           # 静态资源
├── components/       # 通用组件
├── composables/      # 组合式函数 (useXxx)
├── layouts/          # 布局组件
├── pages/            # 页面视图
├── router/           # 路由配置
├── stores/           # Pinia Store
├── types/            # 类型定义
└── utils/            # 工具函数
```

```typescript
// stores/user.ts — Pinia Store 示例
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => user.value !== null)

  function setUser(newUser: User) {
    user.value = newUser
  }

  function logout() {
    user.value = null
  }

  return { user, isLoggedIn, setUser, logout }
})
```

```vue
<!-- composables/useCounter.ts -->
<script setup lang="ts">
import { ref } from 'vue'

export function useCounter(initial = 0) {
  const count = ref(initial)
  const increment = () => { count.value++ }
  const decrement = () => { count.value-- }
  return { count, increment, decrement }
}
</script>
```

### 4.2 React 18: Hooks + Zustand

```
src/
├── api/              # 接口定义
├── assets/           # 静态资源
├── components/       # 通用组件
├── hooks/            # 自定义 Hooks
├── layouts/          # 布局组件
├── pages/            # 页面视图
├── router/           # 路由配置
├── stores/           # Zustand Store
├── types/            # 类型定义
└── utils/            # 工具函数
```

```typescript
// stores/userStore.ts — Zustand Store 示例
import { create } from 'zustand'
import type { User } from '@/types/user'

interface UserState {
  readonly user: User | null
  readonly isLoggedIn: boolean
  setUser: (user: User) => void
  logout: () => void
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  isLoggedIn: false,
  setUser: (user) => set({ user, isLoggedIn: true }),
  logout: () => set({ user: null, isLoggedIn: false }),
}))
```

```typescript
// hooks/useCounter.ts
import { useState, useCallback } from 'react'

export function useCounter(initial = 0) {
  const [count, setCount] = useState(initial)
  const increment = useCallback(() => setCount((c) => c + 1), [])
  const decrement = useCallback(() => setCount((c) => c - 1), [])
  return { count, increment, decrement } as const
}
```

---

## 5. 网络层封装

### 5.1 Axios 实例与拦截器

```typescript
// api/request.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器 — 注入 Token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 — 统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const messages: Record<number, string> = {
      401: '登录已过期，请重新登录',
      403: '无权限访问',
      404: '请求资源不存在',
      500: '服务器内部错误',
    }
    const message = messages[status ?? 0] ?? '网络异常，请稍后重试'
    // 401 时跳转登录页
    if (status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(new Error(message))
  }
)

export default request
```

### 5.2 请求取消（AbortController）

```typescript
// api/cancelable.ts
export function createCancelableRequest<T>(
  requestFn: (signal: AbortSignal) => Promise<T>
) {
  const controller = new AbortController()
  const promise = requestFn(controller.signal)
  return {
    promise,
    cancel: () => controller.abort(),
  }
}

// 使用示例
const { promise, cancel } = createCancelableRequest((signal) =>
  request.get<User[]>('/users', { signal })
)
// 组件卸载时调用 cancel()
```

### 5.3 类型安全的 API 层

```typescript
// api/user.ts
import request from './request'
import type { User, CreateUserDto } from '@/types/user'

interface ApiResponse<T> {
  readonly success: boolean
  readonly data?: T
  readonly error?: string
  readonly meta?: { total: number; page: number; limit: number }
}

export const userApi = {
  getList: (params: { page: number; limit: number }) =>
    request.get<ApiResponse<User[]>>('/users', { params }),

  getById: (id: string) =>
    request.get<ApiResponse<User>>(`/users/${id}`),

  create: (data: CreateUserDto) =>
    request.post<ApiResponse<User>>('/users', data),

  remove: (id: string) =>
    request.delete<ApiResponse<void>>(`/users/${id}`),
} as const
```

---

## 6. 数据持久化

### 6.1 类型安全的 Storage 封装

```typescript
// utils/storage.ts
type StorageType = 'local' | 'session'

function getStorage(type: StorageType): Storage {
  return type === 'local' ? localStorage : sessionStorage
}

export const storage = {
  get<T>(key: string, type: StorageType = 'local'): T | null {
    try {
      const raw = getStorage(type).getItem(key)
      return raw ? (JSON.parse(raw) as T) : null
    } catch {
      return null
    }
  },

  set<T>(key: string, value: T, type: StorageType = 'local'): void {
    try {
      getStorage(type).setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error(`Storage set failed for key "${key}":`, error)
    }
  },

  remove(key: string, type: StorageType = 'local'): void {
    getStorage(type).removeItem(key)
  },
} as const
```

### 6.2 各方案对比

| 方案 | 容量 | 生命周期 | 适用场景 |
|------|------|---------|---------|
| LocalStorage | ~5MB | 永久 | 用户偏好、Token |
| SessionStorage | ~5MB | 标签页关闭 | 表单草稿、临时状态 |
| IndexedDB | 无硬限制 | 永久 | 大量结构化数据、离线缓存 |
| Cookie | ~4KB | 可设过期 | 服务端需读取的标识 |

### 6.3 Cookie 管理

```typescript
// utils/cookie.ts
export const cookie = {
  get(name: string): string | null {
    const match = document.cookie.match(
      new RegExp(`(?:^|; )${name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1')}=([^;]*)`)
    )
    return match ? decodeURIComponent(match[1]) : null
  },

  set(name: string, value: string, days = 7): void {
    const expires = new Date(Date.now() + days * 864e5).toUTCString()
    document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires};path=/;SameSite=Lax`
  },

  remove(name: string): void {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
  },
} as const
```

---

## 7. 路由方案

### 7.1 Vue Router 4

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/pages/Home.vue') },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  { path: '/login', name: 'Login', component: () => import('@/pages/Login.vue') },
  { path: '/:pathMatch(.*)*', component: () => import('@/pages/NotFound.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
```

### 7.2 React Router 6

```tsx
// router/index.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'

const Dashboard = lazy(() => import('@/pages/Dashboard'))
const Login = lazy(() => import('@/pages/Login'))

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <DefaultLayout />,
    children: [
      {
        path: 'dashboard',
        element: (
          <RequireAuth>
            <Suspense fallback={<Loading />}>
              <Dashboard />
            </Suspense>
          </RequireAuth>
        ),
      },
    ],
  },
  { path: '/login', element: <Login /> },
  { path: '*', element: <NotFound /> },
])
```

---

## 8. 常用能力集成

### 8.1 WebSocket 封装

```typescript
// utils/websocket.ts
interface WsOptions {
  readonly url: string
  readonly reconnectInterval?: number
  readonly maxRetries?: number
  onMessage: (data: unknown) => void
  onError?: (error: Event) => void
}

export function createWebSocket(options: WsOptions) {
  const { url, reconnectInterval = 3000, maxRetries = 5, onMessage, onError } = options
  let ws: WebSocket | null = null
  let retries = 0

  function connect() {
    ws = new WebSocket(url)

    ws.onopen = () => { retries = 0 }

    ws.onmessage = (event) => {
      try {
        const data: unknown = JSON.parse(event.data as string)
        onMessage(data)
      } catch {
        onMessage(event.data)
      }
    }

    ws.onerror = (error) => { onError?.(error) }

    ws.onclose = () => {
      if (retries < maxRetries) {
        retries++
        setTimeout(connect, reconnectInterval)
      }
    }
  }

  connect()

  return {
    send: (data: unknown) => ws?.send(JSON.stringify(data)),
    close: () => { ws?.close() },
  }
}
```

### 8.2 Web Worker 使用

```typescript
// workers/heavy-task.worker.ts
self.onmessage = (event: MessageEvent<{ data: number[] }>) => {
  const result = event.data.data.reduce((sum, n) => sum + n, 0)
  self.postMessage({ result })
}

// 主线程调用
const worker = new Worker(
  new URL('@/workers/heavy-task.worker.ts', import.meta.url),
  { type: 'module' }
)
worker.postMessage({ data: [1, 2, 3, 4, 5] })
worker.onmessage = (e) => { /* 处理结果 */ }
```

### 8.3 Service Worker / PWA

```typescript
// vite.config.ts — 使用 vite-plugin-pwa
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'My App',
        short_name: 'App',
        theme_color: '#4f46e5',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
})
```

### 8.4 Notification API

```typescript
// utils/notification.ts
export async function sendNotification(title: string, body: string): Promise<void> {
  if (!('Notification' in window)) return

  if (Notification.permission === 'default') {
    await Notification.requestPermission()
  }

  if (Notification.permission === 'granted') {
    new Notification(title, { body, icon: '/icon-192.png' })
  }
}
```

---

## 9. 组件库选型与封装

### 9.1 主流组件库对比

| 组件库 | 框架 | 特点 | 适用场景 |
|--------|------|------|---------|
| Element Plus | Vue 3 | 中文文档完善，中后台首选 | 企业中后台 |
| Ant Design Vue | Vue 3 | 设计规范统一，组件丰富 | 企业级应用 |
| Ant Design | React | 生态最完善，社区最大 | 企业级应用 |
| MUI (Material UI) | React | Material Design 风格 | 面向国际化产品 |
| Naive UI | Vue 3 | TypeScript 原生，主题定制强 | 需要高度定制的项目 |

### 9.2 二次封装策略

```typescript
// components/AppTable.vue — 表格二次封装示例 (Vue)
<script setup lang="ts" generic="T extends Record<string, unknown>">
import { ElTable, ElTableColumn, ElPagination } from 'element-plus'

interface Column {
  readonly prop: string
  readonly label: string
  readonly width?: number
  readonly formatter?: (row: T) => string
}

interface Props {
  readonly data: readonly T[]
  readonly columns: readonly Column[]
  readonly total?: number
  readonly page?: number
  readonly pageSize?: number
  readonly loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  total: 0,
  page: 1,
  pageSize: 20,
  loading: false,
})

const emit = defineEmits<{
  'page-change': [page: number]
  'size-change': [size: number]
}>()
</script>

<template>
  <div class="app-table">
    <ElTable :data="props.data" v-loading="props.loading" border stripe>
      <ElTableColumn
        v-for="col in props.columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
      />
    </ElTable>
    <ElPagination
      v-if="props.total > 0"
      :current-page="props.page"
      :page-size="props.pageSize"
      :total="props.total"
      layout="total, sizes, prev, pager, next"
      @current-change="emit('page-change', $event)"
      @size-change="emit('size-change', $event)"
    />
  </div>
</template>
```

封装原则：
- 只封装高频使用且需要统一行为的组件
- 保留原组件的 Props 透传能力（`v-bind="$attrs"`）
- 统一默认值、样式和交互规范
- 避免过度封装导致灵活性丧失

---

## 10. 性能优化

### 10.1 代码分割与懒加载

```typescript
// 路由级懒加载（见第 7 节）
const Dashboard = () => import('@/pages/Dashboard.vue')

// 组件级懒加载 (Vue)
import { defineAsyncComponent } from 'vue'
const HeavyChart = defineAsyncComponent(() => import('@/components/HeavyChart.vue'))

// 组件级懒加载 (React)
const HeavyChart = lazy(() => import('@/components/HeavyChart'))
```

### 10.2 图片优化

```typescript
// vite.config.ts — 使用 vite-plugin-imagemin
import imagemin from 'vite-plugin-imagemin'

export default defineConfig({
  plugins: [
    imagemin({
      gifsicle: { optimizationLevel: 3 },
      mozjpeg: { quality: 80 },
      pngquant: { quality: [0.65, 0.8] },
      svgo: { plugins: [{ name: 'removeViewBox', active: false }] },
    }),
  ],
})
```

```html
<!-- 响应式图片 + 懒加载 -->
<img
  srcset="/img/hero-480.webp 480w, /img/hero-800.webp 800w, /img/hero-1200.webp 1200w"
  sizes="(max-width: 600px) 480px, (max-width: 1024px) 800px, 1200px"
  src="/img/hero-800.webp"
  loading="lazy"
  decoding="async"
  alt="Hero banner"
/>
```

### 10.3 虚拟列表

```typescript
// 推荐库：@tanstack/react-virtual (React) / vue-virtual-scroller (Vue)
// React 示例
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualList({ items }: { items: readonly string[] }) {
  const parentRef = useRef<HTMLDivElement>(null)
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
  })

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 10.4 Web Vitals 监控

| 指标 | 含义 | 目标值 |
|------|------|--------|
| LCP | 最大内容绘制 | < 2.5s |
| INP | 交互到下一次绘制 | < 200ms |
| CLS | 累积布局偏移 | < 0.1 |
| FCP | 首次内容绘制 | < 1.8s |
| TTFB | 首字节时间 | < 800ms |

```typescript
// 使用 web-vitals 库上报
import { onLCP, onINP, onCLS } from 'web-vitals'

function reportMetric(metric: { name: string; value: number }) {
  // 上报到监控平台
  navigator.sendBeacon('/analytics', JSON.stringify(metric))
}

onLCP(reportMetric)
onINP(reportMetric)
onCLS(reportMetric)
```

---

## 11. 安全实践

### 11.1 XSS 防护

```typescript
// 规则 1：永远不要使用 v-html / dangerouslySetInnerHTML 渲染用户输入
// 规则 2：如果必须渲染富文本，使用 DOMPurify 清洗

import DOMPurify from 'dompurify'

function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target'],
  })
}
```

### 11.2 CSRF 防护

```typescript
// 方案 1：后端设置 SameSite Cookie
// Set-Cookie: token=xxx; SameSite=Strict; Secure; HttpOnly

// 方案 2：请求头携带 CSRF Token
request.interceptors.request.use((config) => {
  const csrfToken = document.querySelector<HTMLMetaElement>(
    'meta[name="csrf-token"]'
  )?.content
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})
```

### 11.3 Content Security Policy (CSP)

```html
<!-- 通过 meta 标签或 Nginx 响应头设置 -->
<meta http-equiv="Content-Security-Policy"
  content="
    default-src 'self';
    script-src 'self' 'unsafe-inline' https://cdn.example.com;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    connect-src 'self' https://api.example.com;
  "
/>
```

### 11.4 敏感数据处理清单

| 场景 | 做法 | 禁止 |
|------|------|------|
| Token 存储 | HttpOnly Cookie 或内存 | 明文存 LocalStorage |
| 密码传输 | HTTPS + 前端不存储 | HTTP 明文传输 |
| 敏感字段展示 | 脱敏显示（手机号：138****1234） | 完整展示 |
| 日志输出 | 过滤敏感字段 | 打印 Token/密码 |
| 第三方脚本 | CSP 白名单 + SRI 校验 | 随意引入外部 JS |

---

## 12. 响应式与多端适配

### 12.1 媒体查询断点

```css
/* 推荐断点（与 Tailwind 一致） */
/* sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px */

@media (max-width: 768px) {
  .sidebar { display: none; }
  .main-content { padding: 16px; }
}
```

### 12.2 移动端 H5 适配方案

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| rem + flexible | 根据屏幕宽度动态设置 root font-size | 兼容性好 | 需要 px→rem 转换 |
| vw/vh | 视口单位 | 原生支持，无需 JS | 极小屏幕可能文字过小 |
| postcss-px-to-viewport | 构建时自动转换 px→vw | 开发体验好 | 需配置插件 |

```typescript
// postcss.config.ts — vw 方案
export default {
  plugins: {
    'postcss-px-to-viewport-8-plugin': {
      viewportWidth: 375,    // 设计稿宽度
      unitPrecision: 5,
      viewportUnit: 'vw',
      minPixelValue: 1,
      exclude: [/node_modules/],
    },
  },
}
```

### 12.3 安全区域适配（刘海屏）

```css
/* iOS 安全区域 */
.bottom-bar {
  padding-bottom: env(safe-area-inset-bottom);
}

body {
  padding-top: env(safe-area-inset-top);
}
```

---

## 13. 构建与部署

### 13.1 Vite 构建优化

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    target: 'es2020',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,   // 生产环境移除 console
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('react')) return 'framework'
            if (id.includes('element-plus') || id.includes('antd')) return 'ui'
            return 'vendor'
          }
        },
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
      },
    },
    chunkSizeWarningLimit: 500,
  },
})
```

### 13.2 Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1024;

    # 静态资源长缓存（带 hash 的文件）
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由回退
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

### 13.3 CI/CD 流水线（GitHub Actions 示例）

```yaml
# .github/workflows/deploy.yml
name: Build & Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test -- --run
      - run: pnpm build

      - name: Deploy to server
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          source: dist/
          target: /usr/share/nginx/html
```

### 13.4 部署检查清单

| 检查项 | 说明 |
|--------|------|
| 环境变量 | 确认生产环境变量正确配置 |
| Source Map | 生产环境关闭或上传到错误监控平台 |
| HTTPS | 全站强制 HTTPS |
| CDN | 静态资源上 CDN，配置正确的 CORS |
| 错误监控 | 接入 Sentry 等平台 |
| 性能监控 | Web Vitals 上报已开启 |
| 回滚方案 | 保留上一版本产物，支持快速回滚 |
