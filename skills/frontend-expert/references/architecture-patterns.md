# 前端架构模式指南

## 项目架构模式

### 1. 功能模块化架构 (Feature-Based Architecture)

**适用场景：** 中大型项目，多人协作

```
src/
├── features/                    # 功能模块
│   ├── auth/                   # 认证模块
│   │   ├── components/         # 模块专属组件
│   │   │   ├── LoginForm.vue
│   │   │   └── RegisterForm.vue
│   │   ├── composables/        # 模块专属hooks
│   │   │   └── useAuth.ts
│   │   ├── services/           # 模块API服务
│   │   │   └── authService.ts
│   │   ├── stores/             # 模块状态
│   │   │   └── authStore.ts
│   │   ├── types/              # 模块类型
│   │   │   └── index.ts
│   │   └── index.ts            # 模块导出
│   │
│   ├── user/                   # 用户模块
│   │   ├── components/
│   │   ├── composables/
│   │   ├── services/
│   │   └── index.ts
│   │
│   └── order/                  # 订单模块
│       └── ...
│
├── shared/                     # 共享资源
│   ├── components/             # 通用组件
│   ├── composables/            # 通用hooks
│   ├── utils/                  # 工具函数
│   └── types/                  # 通用类型
│
├── layouts/                    # 布局组件
├── router/                     # 路由配置
├── stores/                     # 全局状态
└── App.vue
```

**模块导出规范：**
```typescript
// features/auth/index.ts
// 只导出对外公开的内容
export { LoginForm, RegisterForm } from './components'
export { useAuth } from './composables/useAuth'
export { authStore } from './stores/authStore'
export type { User, LoginParams } from './types'

// 内部实现不导出
// authService 只在模块内部使用
```

---

### 2. 分层架构 (Layered Architecture)

**适用场景：** 企业级应用，需要清晰的职责划分

```
src/
├── presentation/              # 表现层
│   ├── pages/                 # 页面组件
│   ├── components/            # UI组件
│   └── layouts/               # 布局组件
│
├── application/               # 应用层
│   ├── services/              # 应用服务
│   ├── useCases/              # 用例
│   └── dto/                   # 数据传输对象
│
├── domain/                    # 领域层
│   ├── entities/              # 实体
│   ├── valueObjects/          # 值对象
│   └── repositories/          # 仓储接口
│
├── infrastructure/            # 基础设施层
│   ├── api/                   # API客户端
│   ├── storage/               # 存储实现
│   └── repositories/          # 仓储实现
│
└── shared/                    # 共享内核
    ├── types/
    └── utils/
```

**层间依赖规则：**
```typescript
// ✅ 正确：上层依赖下层
// presentation -> application -> domain <- infrastructure

// presentation/pages/UserPage.vue
import { useUserService } from '@/application/services/userService'

// application/services/userService.ts
import { User } from '@/domain/entities/User'
import { UserRepository } from '@/domain/repositories/UserRepository'

// infrastructure/repositories/ApiUserRepository.ts
import { UserRepository } from '@/domain/repositories/UserRepository'

// ❌ 错误：下层依赖上层
// domain 不应该导入 presentation 的内容
```

---

### 3. 微前端架构 (Micro-Frontend)

**适用场景：** 超大型项目，多团队独立开发

```
root/
├── main-app/                  # 主应用（基座）
│   ├── src/
│   │   ├── micro/             # 微应用管理
│   │   │   ├── loader.ts      # 加载器
│   │   │   └── registry.ts    # 注册表
│   │   └── ...
│   └── package.json
│
├── micro-apps/                # 微应用
│   ├── user-app/              # 用户微应用
│   │   ├── src/
│   │   └── package.json
│   │
│   ├── order-app/             # 订单微应用
│   │   ├── src/
│   │   └── package.json
│   │
│   └── shared-lib/            # 共享库
│       ├── src/
│       └── package.json
│
└── package.json               # 工作空间配置
```

**微应用配置示例（qiankun）：**
```typescript
// main-app/src/micro/registry.ts
import { registerMicroApps, start } from 'qiankun'

const microApps = [
  {
    name: 'user-app',
    entry: '//localhost:8081',
    container: '#micro-container',
    activeRule: '/user',
    props: { token: getToken() }
  },
  {
    name: 'order-app',
    entry: '//localhost:8082',
    container: '#micro-container',
    activeRule: '/order'
  }
]

registerMicroApps(microApps, {
  beforeLoad: async (app) => {
    console.log('before load', app.name)
  },
  afterMount: async (app) => {
    console.log('after mount', app.name)
  }
})

start({ prefetch: 'all' })
```

---

## 组件架构模式

### 1. 容器/展示组件模式 (Container/Presentational)

**展示组件：** 只负责UI渲染，无业务逻辑

```vue
<!-- components/UserCard.vue - 展示组件 -->
<template>
  <div class="user-card">
    <img :src="user.avatar" :alt="user.name" />
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
    <button @click="$emit('edit')">编辑</button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  user: {
    avatar: string
    name: string
    email: string
  }
}

defineProps<Props>()
defineEmits<{ edit: [] }>()
</script>
```

**容器组件：** 负责数据获取和业务逻辑

```vue
<!-- containers/UserCardContainer.vue - 容器组件 -->
<template>
  <UserCard
    v-if="user"
    :user="user"
    @edit="handleEdit"
  />
  <LoadingSpinner v-else-if="loading" />
  <ErrorMessage v-else-if="error" :message="error" />
</template>

<script setup lang="ts">
import { useUserData } from '@/composables/useUserData'
import UserCard from '@/components/UserCard.vue'

const props = defineProps<{ userId: string }>()

const { user, loading, error, refetch } = useUserData(props.userId)

const handleEdit = () => {
  // 业务逻辑
  router.push(`/user/${props.userId}/edit`)
}
</script>
```

---

### 2. 复合组件模式 (Compound Components)

**适用场景：** 组件之间有隐式关系，需要共享状态

```vue
<!-- components/Tabs/index.vue -->
<template>
  <div class="tabs">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue'

const activeKey = ref<string>('')

const setActiveKey = (key: string) => {
  activeKey.value = key
}

provide('tabs', {
  activeKey,
  setActiveKey
})
</script>

<!-- components/Tabs/TabList.vue -->
<template>
  <div class="tab-list" role="tablist">
    <slot />
  </div>
</template>

<!-- components/Tabs/Tab.vue -->
<template>
  <button
    class="tab"
    :class="{ active: isActive }"
    role="tab"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { inject, computed } from 'vue'

const props = defineProps<{ tabKey: string }>()

const { activeKey, setActiveKey } = inject('tabs')!

const isActive = computed(() => activeKey.value === props.tabKey)

const handleClick = () => setActiveKey(props.tabKey)
</script>

<!-- components/Tabs/TabPanel.vue -->
<template>
  <div v-show="isActive" class="tab-panel" role="tabpanel">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { inject, computed } from 'vue'

const props = defineProps<{ tabKey: string }>()
const { activeKey } = inject('tabs')!

const isActive = computed(() => activeKey.value === props.tabKey)
</script>

<!-- 使用示例 -->
<Tabs>
  <TabList>
    <Tab tabKey="1">标签1</Tab>
    <Tab tabKey="2">标签2</Tab>
  </TabList>
  <TabPanel tabKey="1">内容1</TabPanel>
  <TabPanel tabKey="2">内容2</TabPanel>
</Tabs>
```

---

### 3. 渲染代理模式 (Render Delegation)

**适用场景：** 需要高度自定义渲染逻辑

```vue
<!-- components/DataList.vue -->
<template>
  <div class="data-list">
    <div v-if="loading" class="loading">
      <slot name="loading">
        <DefaultLoading />
      </slot>
    </div>

    <div v-else-if="error" class="error">
      <slot name="error" :error="error" :retry="refetch">
        <DefaultError :error="error" @retry="refetch" />
      </slot>
    </div>

    <div v-else-if="!data?.length" class="empty">
      <slot name="empty">
        <DefaultEmpty />
      </slot>
    </div>

    <div v-else class="list">
      <template v-for="(item, index) in data" :key="getKey(item, index)">
        <slot name="item" :item="item" :index="index">
          <DefaultItem :item="item" />
        </slot>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T">
interface Props {
  data: T[] | null
  loading: boolean
  error: Error | null
  getKey?: (item: T, index: number) => string | number
  refetch?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  getKey: (_, index) => index,
  refetch: () => {}
})
</script>

<!-- 使用示例 -->
<DataList
  :data="users"
  :loading="loading"
  :error="error"
  :get-key="user => user.id"
  :refetch="refetch"
>
  <template #item="{ item: user }">
    <UserCard :user="user" />
  </template>

  <template #empty>
    <div class="custom-empty">
      <img src="/empty.svg" />
      <p>暂无用户数据</p>
    </div>
  </template>
</DataList>
```

---

## 状态架构模式

### 1. 单向数据流 (Unidirectional Data Flow)

```
┌─────────────────────────────────────────────────────────────┐
│                      单向数据流                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    ┌─────────┐     ┌─────────┐     ┌─────────┐            │
│    │  State  │ ──▶ │  View   │ ──▶ │ Action  │            │
│    └─────────┘     └─────────┘     └─────────┘            │
│         ▲                               │                  │
│         │                               │                  │
│         └───────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Pinia 实现：**
```typescript
// stores/counter.ts
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  // State
  state: () => ({
    count: 0
  }),

  // Getters (派生状态)
  getters: {
    doubleCount: (state) => state.count * 2
  },

  // Actions (修改状态的唯一方式)
  actions: {
    increment() {
      this.count++
    },
    async fetchCount() {
      const response = await api.getCount()
      this.count = response.data
    }
  }
})

// 组件中使用
const store = useCounterStore()
// 读取状态
console.log(store.count)
// 触发action
store.increment()
```

---

### 2. 状态机模式 (State Machine)

**适用场景：** 复杂的状态转换逻辑

```typescript
// composables/useStateMachine.ts
import { ref, computed } from 'vue'

type State = 'idle' | 'loading' | 'success' | 'error'
type Event = 'FETCH' | 'RESOLVE' | 'REJECT' | 'RESET'

interface StateMachine {
  initial: State
  states: {
    [K in State]: {
      on: Partial<Record<Event, State>>
    }
  }
}

const machine: StateMachine = {
  initial: 'idle',
  states: {
    idle: {
      on: { FETCH: 'loading' }
    },
    loading: {
      on: { RESOLVE: 'success', REJECT: 'error' }
    },
    success: {
      on: { RESET: 'idle', FETCH: 'loading' }
    },
    error: {
      on: { RESET: 'idle', FETCH: 'loading' }
    }
  }
}

export function useStateMachine() {
  const state = ref<State>(machine.initial)

  const send = (event: Event) => {
    const nextState = machine.states[state.value].on[event]
    if (nextState) {
      state.value = nextState
    }
  }

  const isIdle = computed(() => state.value === 'idle')
  const isLoading = computed(() => state.value === 'loading')
  const isSuccess = computed(() => state.value === 'success')
  const isError = computed(() => state.value === 'error')

  return {
    state,
    send,
    isIdle,
    isLoading,
    isSuccess,
    isError
  }
}

// 使用示例
const { state, send, isLoading, isError } = useStateMachine()

const fetchData = async () => {
  send('FETCH')
  try {
    await api.getData()
    send('RESOLVE')
  } catch {
    send('REJECT')
  }
}
```

---

## 路由架构模式

### 1. 路由配置集中管理

```typescript
// router/routes.ts
import type { RouteRecordRaw } from 'vue-router'

// 路由元信息类型
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    roles?: string[]
    keepAlive?: boolean
  }
}

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/pages/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('@/pages/user/index.vue'),
        meta: { title: '用户管理', requiresAuth: true },
        children: [
          {
            path: ':id',
            name: 'UserDetail',
            component: () => import('@/pages/user/Detail.vue'),
            meta: { title: '用户详情' }
          }
        ]
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue')
  }
]
```

### 2. 路由守卫架构

```typescript
// router/guards/authGuard.ts
import type { NavigationGuard } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export const authGuard: NavigationGuard = (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    next({ name: 'Forbidden' })
    return
  }

  next()
}

// router/guards/titleGuard.ts
export const titleGuard: NavigationGuard = (to) => {
  const title = to.meta.title
  document.title = title ? `${title} - MyApp` : 'MyApp'
}

// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { authGuard } from './guards/authGuard'
import { titleGuard } from './guards/titleGuard'

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(authGuard)
router.afterEach(titleGuard)

export default router
```

---

## API 架构模式

### 1. API 服务层封装

```typescript
// api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

class ApiClient {
  private instance: AxiosInstance

  constructor(config: AxiosRequestConfig) {
    this.instance = axios.create(config)
    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截
    this.instance.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // 处理未授权
          router.push('/login')
        }
        return Promise.reject(error)
      }
    )
  }

  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }
}

export const apiClient = new ApiClient({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
})

// api/services/userService.ts
import { apiClient } from '../client'
import type { User, CreateUserDto, UpdateUserDto } from '../types'

export const userService = {
  getList: (params?: { page?: number; size?: number }) =>
    apiClient.get<{ list: User[]; total: number }>('/users', { params }),

  getById: (id: string) =>
    apiClient.get<User>(`/users/${id}`),

  create: (data: CreateUserDto) =>
    apiClient.post<User>('/users', data),

  update: (id: string, data: UpdateUserDto) =>
    apiClient.put<User>(`/users/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<void>(`/users/${id}`)
}
```

### 2. 请求状态管理 Hook

```typescript
// composables/useRequest.ts
import { ref, shallowRef } from 'vue'

interface UseRequestOptions<T> {
  immediate?: boolean
  initialData?: T
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
}

export function useRequest<T, P extends unknown[]>(
  service: (...args: P) => Promise<T>,
  options: UseRequestOptions<T> = {}
) {
  const { immediate = false, initialData, onSuccess, onError } = options

  const data = shallowRef<T | undefined>(initialData)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const run = async (...args: P) => {
    loading.value = true
    error.value = null

    try {
      const result = await service(...args)
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
      throw e
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = initialData
    loading.value = false
    error.value = null
  }

  if (immediate) {
    run(...([] as unknown as P))
  }

  return {
    data,
    loading,
    error,
    run,
    reset
  }
}

// 使用示例
const { data: users, loading, error, run: fetchUsers } = useRequest(
  userService.getList,
  {
    immediate: true,
    onError: (e) => message.error(e.message)
  }
)
```
