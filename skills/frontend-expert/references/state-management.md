# 前端状态管理指南

## 状态分类

### 状态类型划分

| 状态类型 | 描述 | 存储位置 | 示例 |
|----------|------|----------|------|
| 服务端状态 | 来自API的数据 | React Query/SWR/Pinia | 用户列表、订单数据 |
| 客户端状态 | 纯前端状态 | Pinia/Zustand/Context | 主题、语言、侧边栏 |
| URL状态 | 路由相关状态 | 路由参数/查询字符串 | 分页、筛选、排序 |
| 表单状态 | 表单输入数据 | 组件内部/表单库 | 输入值、验证状态 |
| UI状态 | 界面交互状态 | 组件内部 | 弹窗开关、加载状态 |

### 状态选择决策树

```
需要管理的状态
    │
    ├── 是否来自服务端？
    │   ├── 是 → 使用 React Query / SWR / TanStack Query
    │   └── 否 ↓
    │
    ├── 是否需要跨组件共享？
    │   ├── 否 → 使用组件内部状态 (ref/useState)
    │   └── 是 ↓
    │
    ├── 是否需要持久化到URL？
    │   ├── 是 → 使用路由状态 (query params)
    │   └── 否 ↓
    │
    ├── 是否只在父子组件间共享？
    │   ├── 是 → 使用 Props/Emit 或 provide/inject
    │   └── 否 ↓
    │
    └── 使用全局状态管理 (Pinia/Zustand)
```

---

## Vue 3 状态管理

### 1. Pinia 基础使用

**Store 定义：**
```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { userApi } from '@/api/user'

// 组合式 API 风格（推荐）
export const useUserStore = defineStore('user', () => {
  // State
  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => currentUser.value?.name ?? '游客')

  // Actions
  const login = async (credentials: { email: string; password: string }) => {
    loading.value = true
    try {
      const response = await userApi.login(credentials)
      token.value = response.token
      currentUser.value = response.user
      localStorage.setItem('token', response.token)
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    currentUser.value = null
    localStorage.removeItem('token')
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return
    loading.value = true
    try {
      currentUser.value = await userApi.getCurrentUser()
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    currentUser,
    token,
    loading,
    // Getters
    isLoggedIn,
    userName,
    // Actions
    login,
    logout,
    fetchCurrentUser
  }
})

// 选项式 API 风格
export const useUserStoreOptions = defineStore('user-options', {
  state: () => ({
    currentUser: null as User | null,
    token: localStorage.getItem('token'),
    loading: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.currentUser?.name ?? '游客'
  },

  actions: {
    async login(credentials: { email: string; password: string }) {
      this.loading = true
      try {
        const response = await userApi.login(credentials)
        this.token = response.token
        this.currentUser = response.user
        localStorage.setItem('token', response.token)
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.currentUser = null
      localStorage.removeItem('token')
    }
  }
})
```

**组件中使用：**
```vue
<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()

// 解构响应式状态（使用 storeToRefs 保持响应性）
const { currentUser, isLoggedIn, loading } = storeToRefs(userStore)

// 直接解构 actions（不需要 storeToRefs）
const { login, logout } = userStore

const handleLogin = async () => {
  await login({ email: 'test@example.com', password: '123456' })
}
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="isLoggedIn">
    欢迎，{{ currentUser?.name }}
    <button @click="logout">退出</button>
  </div>
  <div v-else>
    <button @click="handleLogin">登录</button>
  </div>
</template>
```

### 2. Pinia 持久化

```typescript
// stores/plugins/persist.ts
import type { PiniaPluginContext } from 'pinia'

interface PersistOptions {
  key?: string
  storage?: Storage
  paths?: string[]
}

export function createPersistedState(options: PersistOptions = {}) {
  const {
    key = 'pinia',
    storage = localStorage,
    paths
  } = options

  return ({ store }: PiniaPluginContext) => {
    // 恢复状态
    const savedState = storage.getItem(`${key}-${store.$id}`)
    if (savedState) {
      store.$patch(JSON.parse(savedState))
    }

    // 监听变化并保存
    store.$subscribe((mutation, state) => {
      const toSave = paths
        ? paths.reduce((acc, path) => {
            acc[path] = state[path]
            return acc
          }, {} as Record<string, any>)
        : state

      storage.setItem(`${key}-${store.$id}`, JSON.stringify(toSave))
    })
  }
}

// main.ts
import { createPinia } from 'pinia'
import { createPersistedState } from './stores/plugins/persist'

const pinia = createPinia()
pinia.use(createPersistedState({
  key: 'my-app',
  paths: ['token', 'theme']
}))
```

### 3. 组合式函数状态

```typescript
// composables/useCounter.ts
import { ref, computed, readonly } from 'vue'

// 模块级别的状态（单例）
const count = ref(0)

export function useCounter() {
  const doubleCount = computed(() => count.value * 2)

  const increment = () => {
    count.value++
  }

  const decrement = () => {
    count.value--
  }

  const reset = () => {
    count.value = 0
  }

  return {
    count: readonly(count), // 只读，防止外部直接修改
    doubleCount,
    increment,
    decrement,
    reset
  }
}

// composables/useLocalStorage.ts
import { ref, watch } from 'vue'

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const storedValue = localStorage.getItem(key)
  const data = ref<T>(storedValue ? JSON.parse(storedValue) : defaultValue)

  watch(
    data,
    (newValue) => {
      localStorage.setItem(key, JSON.stringify(newValue))
    },
    { deep: true }
  )

  return data
}
```

---

## React 状态管理

### 1. Zustand 基础使用

```typescript
// stores/userStore.ts
import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'
import type { User } from '@/types'
import { userApi } from '@/api/user'

interface UserState {
  currentUser: User | null
  token: string | null
  loading: boolean
  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        currentUser: null,
        token: null,
        loading: false,

        login: async (credentials) => {
          set({ loading: true })
          try {
            const response = await userApi.login(credentials)
            set({
              token: response.token,
              currentUser: response.user,
              loading: false
            })
          } catch (error) {
            set({ loading: false })
            throw error
          }
        },

        logout: () => {
          set({ token: null, currentUser: null })
        },

        fetchCurrentUser: async () => {
          const { token } = get()
          if (!token) return

          set({ loading: true })
          try {
            const user = await userApi.getCurrentUser()
            set({ currentUser: user, loading: false })
          } catch (error) {
            set({ loading: false })
            throw error
          }
        }
      }),
      {
        name: 'user-storage',
        partialize: (state) => ({ token: state.token })
      }
    )
  )
)

// 选择器（优化重渲染）
export const useIsLoggedIn = () => useUserStore((state) => !!state.token)
export const useUserName = () => useUserStore((state) => state.currentUser?.name ?? '游客')
```

**组件中使用：**
```tsx
import { useUserStore, useIsLoggedIn } from '@/stores/userStore'

const UserProfile: React.FC = () => {
  // 选择性订阅，避免不必要的重渲染
  const currentUser = useUserStore((state) => state.currentUser)
  const loading = useUserStore((state) => state.loading)
  const logout = useUserStore((state) => state.logout)

  // 或使用选择器
  const isLoggedIn = useIsLoggedIn()

  if (loading) return <div>加载中...</div>

  if (!isLoggedIn) return <div>请登录</div>

  return (
    <div>
      <p>欢迎，{currentUser?.name}</p>
      <button onClick={logout}>退出</button>
    </div>
  )
}
```

### 2. React Query 服务端状态

```typescript
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { userApi } from '@/api/user'
import type { User, CreateUserDto } from '@/types'

// 查询键工厂
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...userKeys.lists(), filters] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const
}

// 获取用户列表
export function useUsers(filters?: { page?: number; size?: number }) {
  return useQuery({
    queryKey: userKeys.list(filters ?? {}),
    queryFn: () => userApi.getList(filters),
    staleTime: 5 * 60 * 1000, // 5分钟内数据视为新鲜
    gcTime: 10 * 60 * 1000    // 10分钟后垃圾回收
  })
}

// 获取单个用户
export function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => userApi.getById(id),
    enabled: !!id // 只有 id 存在时才执行查询
  })
}

// 创建用户
export function useCreateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateUserDto) => userApi.create(data),
    onSuccess: () => {
      // 使列表缓存失效
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
    }
  })
}

// 更新用户
export function useUpdateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      userApi.update(id, data),
    onSuccess: (updatedUser) => {
      // 更新详情缓存
      queryClient.setQueryData(userKeys.detail(updatedUser.id), updatedUser)
      // 使列表缓存失效
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
    }
  })
}

// 删除用户
export function useDeleteUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => userApi.delete(id),
    onSuccess: (_, id) => {
      // 移除详情缓存
      queryClient.removeQueries({ queryKey: userKeys.detail(id) })
      // 使列表缓存失效
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
    }
  })
}
```

**组件中使用：**
```tsx
import { useUsers, useCreateUser, useDeleteUser } from '@/hooks/useUsers'

const UserList: React.FC = () => {
  const { data, isLoading, error, refetch } = useUsers({ page: 1, size: 10 })
  const createUser = useCreateUser()
  const deleteUser = useDeleteUser()

  if (isLoading) return <div>加载中...</div>
  if (error) return <div>错误: {error.message}</div>

  const handleCreate = async () => {
    await createUser.mutateAsync({
      name: 'New User',
      email: 'new@example.com'
    })
  }

  const handleDelete = async (id: string) => {
    await deleteUser.mutateAsync(id)
  }

  return (
    <div>
      <button onClick={handleCreate} disabled={createUser.isPending}>
        {createUser.isPending ? '创建中...' : '创建用户'}
      </button>

      <ul>
        {data?.list.map((user) => (
          <li key={user.id}>
            {user.name}
            <button onClick={() => handleDelete(user.id)}>删除</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

---

## URL 状态管理

### Vue Router 状态

```typescript
// composables/useUrlState.ts
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useUrlState<T extends Record<string, string | number | boolean>>(
  defaultState: T
) {
  const route = useRoute()
  const router = useRouter()

  const state = computed(() => {
    const result = { ...defaultState }
    for (const key in defaultState) {
      const value = route.query[key]
      if (value !== undefined) {
        const defaultValue = defaultState[key]
        if (typeof defaultValue === 'number') {
          result[key] = Number(value) as T[typeof key]
        } else if (typeof defaultValue === 'boolean') {
          result[key] = (value === 'true') as T[typeof key]
        } else {
          result[key] = value as T[typeof key]
        }
      }
    }
    return result
  })

  const setState = (newState: Partial<T>) => {
    const query = { ...route.query }
    for (const key in newState) {
      const value = newState[key]
      if (value === defaultState[key]) {
        delete query[key]
      } else {
        query[key] = String(value)
      }
    }
    router.push({ query })
  }

  return [state, setState] as const
}

// 使用示例
const [tableState, setTableState] = useUrlState({
  page: 1,
  size: 10,
  sort: 'createdAt',
  order: 'desc'
})

// 修改状态
setTableState({ page: 2 })
```

### React Router 状态

```typescript
// hooks/useUrlState.ts
import { useSearchParams } from 'react-router-dom'
import { useCallback, useMemo } from 'react'

export function useUrlState<T extends Record<string, string | number | boolean>>(
  defaultState: T
) {
  const [searchParams, setSearchParams] = useSearchParams()

  const state = useMemo(() => {
    const result = { ...defaultState }
    for (const key in defaultState) {
      const value = searchParams.get(key)
      if (value !== null) {
        const defaultValue = defaultState[key]
        if (typeof defaultValue === 'number') {
          result[key] = Number(value) as T[typeof key]
        } else if (typeof defaultValue === 'boolean') {
          result[key] = (value === 'true') as T[typeof key]
        } else {
          result[key] = value as T[typeof key]
        }
      }
    }
    return result
  }, [searchParams, defaultState])

  const setState = useCallback(
    (newState: Partial<T>) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev)
        for (const key in newState) {
          const value = newState[key]
          if (value === defaultState[key]) {
            next.delete(key)
          } else {
            next.set(key, String(value))
          }
        }
        return next
      })
    },
    [setSearchParams, defaultState]
  )

  return [state, setState] as const
}
```

---

## 状态管理最佳实践

### 1. 状态规范化

```typescript
// 规范化数据结构
interface NormalizedState {
  users: {
    byId: Record<string, User>
    allIds: string[]
  }
  posts: {
    byId: Record<string, Post>
    allIds: string[]
  }
}

// 规范化函数
function normalizeUsers(users: User[]): NormalizedState['users'] {
  return {
    byId: users.reduce((acc, user) => {
      acc[user.id] = user
      return acc
    }, {} as Record<string, User>),
    allIds: users.map((user) => user.id)
  }
}

// 选择器
const selectUserById = (state: NormalizedState, id: string) =>
  state.users.byId[id]

const selectAllUsers = (state: NormalizedState) =>
  state.users.allIds.map((id) => state.users.byId[id])
```

### 2. 状态不可变性

```typescript
// 使用 Immer 简化不可变更新
import { produce } from 'immer'

// Pinia 中使用
const useStore = defineStore('store', () => {
  const items = ref<Item[]>([])

  const updateItem = (id: string, updates: Partial<Item>) => {
    items.value = produce(items.value, (draft) => {
      const item = draft.find((i) => i.id === id)
      if (item) {
        Object.assign(item, updates)
      }
    })
  }

  return { items, updateItem }
})

// Zustand 中使用 Immer 中间件
import { immer } from 'zustand/middleware/immer'

const useStore = create<State>()(
  immer((set) => ({
    items: [],
    updateItem: (id, updates) =>
      set((state) => {
        const item = state.items.find((i) => i.id === id)
        if (item) {
          Object.assign(item, updates)
        }
      })
  }))
)
```

### 3. 状态调试

```typescript
// Vue Devtools 集成（Pinia 自动支持）

// Zustand Devtools
import { devtools } from 'zustand/middleware'

const useStore = create<State>()(
  devtools(
    (set) => ({
      // ...
    }),
    { name: 'MyStore' }
  )
)

// 日志中间件
const logMiddleware = (config) => (set, get, api) =>
  config(
    (...args) => {
      console.log('  applying', args)
      set(...args)
      console.log('  new state', get())
    },
    get,
    api
  )
```

---

## 状态管理选型建议

| 场景 | Vue 推荐 | React 推荐 |
|------|----------|------------|
| 简单应用 | ref/reactive | useState/useReducer |
| 中型应用 | Pinia | Zustand |
| 大型应用 | Pinia + 模块化 | Zustand + React Query |
| 服务端状态 | VueQuery/SWR | TanStack Query |
| 表单状态 | VeeValidate | React Hook Form |
| URL状态 | Vue Router | React Router |
