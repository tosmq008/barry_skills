# 前后端 API 交互指南

## API 客户端架构

### 1. Axios 封装

**基础配置：**
```typescript
// api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// 响应数据结构
interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
  timestamp: number
}

// 分页响应
interface PaginatedResponse<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// 请求配置扩展
interface RequestConfig extends AxiosRequestConfig {
  skipErrorHandler?: boolean  // 跳过全局错误处理
  skipAuth?: boolean          // 跳过认证
  retry?: number              // 重试次数
  retryDelay?: number         // 重试延迟
}

class ApiClient {
  private instance: AxiosInstance
  private refreshTokenPromise: Promise<string> | null = null

  constructor(baseURL: string) {
    this.instance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token && !(config as RequestConfig).skipAuth) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = this.generateRequestId()

        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response) => this.handleResponse(response),
      (error) => this.handleError(error)
    )
  }

  private handleResponse(response: AxiosResponse<ApiResponse>) {
    const { data } = response

    // 业务状态码检查
    if (data.code !== 0 && data.code !== 200) {
      return Promise.reject(new BusinessError(data.code, data.message))
    }

    return data.data
  }

  private async handleError(error: AxiosError<ApiResponse>) {
    const config = error.config as RequestConfig

    // 跳过错误处理
    if (config?.skipErrorHandler) {
      return Promise.reject(error)
    }

    // 网络错误
    if (!error.response) {
      return Promise.reject(new NetworkError('网络连接失败，请检查网络'))
    }

    const { status, data } = error.response

    switch (status) {
      case 401:
        return this.handle401Error(error)
      case 403:
        return Promise.reject(new AuthError('没有权限访问该资源'))
      case 404:
        return Promise.reject(new NotFoundError('请求的资源不存在'))
      case 422:
        return Promise.reject(new ValidationError(data?.message || '数据验证失败', data?.data))
      case 429:
        return Promise.reject(new RateLimitError('请求过于频繁，请稍后再试'))
      case 500:
      case 502:
      case 503:
        return this.handleServerError(error)
      default:
        return Promise.reject(new ApiError(status, data?.message || '请求失败'))
    }
  }

  private async handle401Error(error: AxiosError) {
    const config = error.config as RequestConfig

    // 尝试刷新Token
    try {
      const newToken = await this.refreshToken()
      if (newToken && config) {
        config.headers!.Authorization = `Bearer ${newToken}`
        return this.instance.request(config)
      }
    } catch {
      // 刷新失败，跳转登录
      this.handleLogout()
    }

    return Promise.reject(new AuthError('登录已过期，请重新登录'))
  }

  private async handleServerError(error: AxiosError) {
    const config = error.config as RequestConfig
    const retryCount = config?.retry ?? 0

    // 重试逻辑
    if (retryCount > 0) {
      const delay = config?.retryDelay ?? 1000
      await this.sleep(delay)

      return this.instance.request({
        ...config,
        retry: retryCount - 1
      })
    }

    return Promise.reject(new ServerError('服务器繁忙，请稍后再试'))
  }

  private async refreshToken(): Promise<string> {
    // 防止并发刷新
    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise
    }

    this.refreshTokenPromise = this.doRefreshToken()

    try {
      return await this.refreshTokenPromise
    } finally {
      this.refreshTokenPromise = null
    }
  }

  private async doRefreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refreshToken')
    if (!refreshToken) {
      throw new Error('No refresh token')
    }

    const response = await axios.post<ApiResponse<{ token: string }>>(
      `${this.instance.defaults.baseURL}/auth/refresh`,
      { refreshToken }
    )

    const newToken = response.data.data.token
    localStorage.setItem('token', newToken)
    return newToken
  }

  private getToken(): string | null {
    return localStorage.getItem('token')
  }

  private handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    window.location.href = '/login'
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // 公共请求方法
  async get<T>(url: string, config?: RequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  async post<T>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  async put<T>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  async patch<T>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.instance.patch(url, data, config)
  }

  async delete<T>(url: string, config?: RequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }
}

export const apiClient = new ApiClient(import.meta.env.VITE_API_BASE_URL)
```

---

## 错误处理体系

### 1. 错误类型定义

```typescript
// api/errors.ts

// 基础错误类
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// 业务错误（后端返回的业务逻辑错误）
export class BusinessError extends ApiError {
  constructor(
    public code: number,
    message: string,
    details?: any
  ) {
    super(400, message, details)
    this.name = 'BusinessError'
  }
}

// 认证错误
export class AuthError extends ApiError {
  constructor(message: string = '认证失败') {
    super(401, message)
    this.name = 'AuthError'
  }
}

// 权限错误
export class ForbiddenError extends ApiError {
  constructor(message: string = '没有权限') {
    super(403, message)
    this.name = 'ForbiddenError'
  }
}

// 资源不存在
export class NotFoundError extends ApiError {
  constructor(message: string = '资源不存在') {
    super(404, message)
    this.name = 'NotFoundError'
  }
}

// 数据验证错误
export class ValidationError extends ApiError {
  constructor(
    message: string = '数据验证失败',
    public errors?: Record<string, string[]>
  ) {
    super(422, message, errors)
    this.name = 'ValidationError'
  }
}

// 请求频率限制
export class RateLimitError extends ApiError {
  constructor(
    message: string = '请求过于频繁',
    public retryAfter?: number
  ) {
    super(429, message)
    this.name = 'RateLimitError'
  }
}

// 服务器错误
export class ServerError extends ApiError {
  constructor(message: string = '服务器错误') {
    super(500, message)
    this.name = 'ServerError'
  }
}

// 网络错误
export class NetworkError extends ApiError {
  constructor(message: string = '网络连接失败') {
    super(0, message)
    this.name = 'NetworkError'
  }
}

// 超时错误
export class TimeoutError extends ApiError {
  constructor(message: string = '请求超时') {
    super(408, message)
    this.name = 'TimeoutError'
  }
}
```

### 2. 全局错误处理

```typescript
// composables/useErrorHandler.ts (Vue)
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ApiError,
  AuthError,
  ValidationError,
  NetworkError,
  RateLimitError
} from '@/api/errors'

export function useErrorHandler() {
  const handleError = (error: unknown) => {
    // 已取消的请求不处理
    if (axios.isCancel(error)) {
      return
    }

    if (error instanceof AuthError) {
      ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
        confirmButtonText: '去登录',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        window.location.href = '/login'
      })
      return
    }

    if (error instanceof ValidationError) {
      // 显示第一个验证错误
      const firstError = Object.values(error.errors || {})[0]?.[0]
      ElMessage.error(firstError || error.message)
      return
    }

    if (error instanceof NetworkError) {
      ElMessage.error('网络连接失败，请检查网络设置')
      return
    }

    if (error instanceof RateLimitError) {
      ElMessage.warning(`请求过于频繁，请${error.retryAfter || 60}秒后再试`)
      return
    }

    if (error instanceof ApiError) {
      ElMessage.error(error.message)
      return
    }

    // 未知错误
    console.error('Unhandled error:', error)
    ElMessage.error('操作失败，请稍后再试')
  }

  return { handleError }
}

// React Hook 版本
export function useErrorHandler() {
  const { message, modal } = App.useApp()

  const handleError = useCallback((error: unknown) => {
    if (error instanceof AuthError) {
      modal.confirm({
        title: '提示',
        content: '登录已过期，请重新登录',
        onOk: () => {
          window.location.href = '/login'
        }
      })
      return
    }

    if (error instanceof ValidationError) {
      const firstError = Object.values(error.errors || {})[0]?.[0]
      message.error(firstError || error.message)
      return
    }

    if (error instanceof ApiError) {
      message.error(error.message)
      return
    }

    message.error('操作失败，请稍后再试')
  }, [message, modal])

  return { handleError }
}
```

---

## API 服务层设计

### 1. 服务模块化

```typescript
// api/services/userService.ts
import { apiClient } from '../client'

// 类型定义
export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  createdAt: string
  updatedAt: string
}

export interface CreateUserDto {
  name: string
  email: string
  password: string
  role?: 'admin' | 'user'
}

export interface UpdateUserDto {
  name?: string
  email?: string
  avatar?: string
  status?: 'active' | 'inactive'
}

export interface UserListParams {
  page?: number
  pageSize?: number
  keyword?: string
  role?: string
  status?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface UserListResponse {
  list: User[]
  total: number
  page: number
  pageSize: number
}

// 用户服务
export const userService = {
  // 获取用户列表
  getList(params?: UserListParams): Promise<UserListResponse> {
    return apiClient.get('/users', { params })
  },

  // 获取单个用户
  getById(id: string): Promise<User> {
    return apiClient.get(`/users/${id}`)
  },

  // 创建用户
  create(data: CreateUserDto): Promise<User> {
    return apiClient.post('/users', data)
  },

  // 更新用户
  update(id: string, data: UpdateUserDto): Promise<User> {
    return apiClient.put(`/users/${id}`, data)
  },

  // 删除用户
  delete(id: string): Promise<void> {
    return apiClient.delete(`/users/${id}`)
  },

  // 批量删除
  batchDelete(ids: string[]): Promise<void> {
    return apiClient.post('/users/batch-delete', { ids })
  }
}
```

---

## 请求 Hook 封装

### 1. Vue 请求 Hook

```typescript
// composables/useRequest.ts
import { ref, shallowRef, UnwrapRef } from 'vue'

interface UseRequestOptions<T, P extends any[]> {
  manual?: boolean           // 手动触发
  defaultParams?: P          // 默认参数
  initialData?: T            // 初始数据
  onSuccess?: (data: T, params: P) => void
  onError?: (error: Error, params: P) => void
  onFinally?: (params: P) => void
  debounceWait?: number      // 防抖等待时间
  throttleWait?: number      // 节流等待时间
  cacheKey?: string          // 缓存键
  cacheTime?: number         // 缓存时间
}

export function useRequest<T, P extends any[] = []>(
  service: (...args: P) => Promise<T>,
  options: UseRequestOptions<T, P> = {}
) {
  const {
    manual = false,
    defaultParams = [] as unknown as P,
    initialData,
    onSuccess,
    onError,
    onFinally
  } = options

  const data = shallowRef<T | undefined>(initialData)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const run = async (...params: P): Promise<T | undefined> => {
    loading.value = true
    error.value = null

    try {
      const result = await service(...params)
      data.value = result as UnwrapRef<T>
      onSuccess?.(result, params)
      return result
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error, params)
      throw e
    } finally {
      loading.value = false
      onFinally?.(params)
    }
  }

  const refresh = () => run(...defaultParams)

  const mutate = (newData: T | ((oldData?: T) => T)) => {
    if (typeof newData === 'function') {
      data.value = (newData as Function)(data.value) as UnwrapRef<T>
    } else {
      data.value = newData as UnwrapRef<T>
    }
  }

  // 自动执行
  if (!manual) {
    run(...defaultParams)
  }

  return {
    data,
    loading,
    error,
    run,
    refresh,
    mutate
  }
}

// 使用示例
const { data: users, loading, run: fetchUsers } = useRequest(
  (params: UserListParams) => userService.getList(params),
  {
    manual: false,
    defaultParams: [{ page: 1, pageSize: 10 }],
    onSuccess: (data) => {
      console.log('获取成功', data)
    }
  }
)
```

### 2. 分页请求 Hook

```typescript
// composables/usePagination.ts
import { ref, computed, watch } from 'vue'

interface UsePaginationOptions<T, P extends Record<string, any>> {
  defaultPageSize?: number
  defaultParams?: P
  onSuccess?: (data: { list: T[]; total: number }) => void
}

export function usePagination<T, P extends Record<string, any> = {}>(
  service: (params: P & { page: number; pageSize: number }) => Promise<{ list: T[]; total: number }>,
  options: UsePaginationOptions<T, P> = {}
) {
  const { defaultPageSize = 10, defaultParams = {} as P, onSuccess } = options

  const list = ref<T[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(defaultPageSize)
  const loading = ref(false)
  const params = ref<P>(defaultParams)

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const hasMore = computed(() => page.value < totalPages.value)

  const fetch = async () => {
    loading.value = true
    try {
      const result = await service({
        ...params.value,
        page: page.value,
        pageSize: pageSize.value
      })
      list.value = result.list as any
      total.value = result.total
      onSuccess?.(result)
    } finally {
      loading.value = false
    }
  }

  const changePage = (newPage: number) => {
    page.value = newPage
    fetch()
  }

  const changePageSize = (newSize: number) => {
    pageSize.value = newSize
    page.value = 1
    fetch()
  }

  const search = (newParams: Partial<P>) => {
    params.value = { ...params.value, ...newParams }
    page.value = 1
    fetch()
  }

  const reset = () => {
    params.value = defaultParams
    page.value = 1
    fetch()
  }

  // 初始加载
  fetch()

  return {
    list,
    total,
    page,
    pageSize,
    loading,
    params,
    totalPages,
    hasMore,
    fetch,
    changePage,
    changePageSize,
    search,
    reset
  }
}
```

---

## 文件上传处理

### 1. 文件上传服务

```typescript
// api/services/uploadService.ts
import { apiClient } from '../client'

export interface UploadResult {
  url: string
  filename: string
  size: number
  mimeType: string
}

export interface UploadProgress {
  loaded: number
  total: number
  percent: number
}

export const uploadService = {
  // 单文件上传
  async uploadFile(
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)

    return apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress({
            loaded: event.loaded,
            total: event.total,
            percent: Math.round((event.loaded / event.total) * 100)
          })
        }
      }
    })
  },

  // 多文件上传
  async uploadFiles(
    files: File[],
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResult[]> {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))

    return apiClient.post('/upload/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress({
            loaded: event.loaded,
            total: event.total,
            percent: Math.round((event.loaded / event.total) * 100)
          })
        }
      }
    })
  },

  // 分片上传
  async uploadChunked(
    file: File,
    options: {
      chunkSize?: number
      onProgress?: (progress: UploadProgress) => void
      onChunkComplete?: (chunkIndex: number, total: number) => void
    } = {}
  ): Promise<UploadResult> {
    const { chunkSize = 5 * 1024 * 1024, onProgress, onChunkComplete } = options
    const totalChunks = Math.ceil(file.size / chunkSize)
    const fileId = `${file.name}-${file.size}-${Date.now()}`

    let uploadedSize = 0

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)

      const formData = new FormData()
      formData.append('chunk', chunk)
      formData.append('fileId', fileId)
      formData.append('chunkIndex', String(i))
      formData.append('totalChunks', String(totalChunks))
      formData.append('filename', file.name)

      await apiClient.post('/upload/chunk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      uploadedSize += chunk.size
      onProgress?.({
        loaded: uploadedSize,
        total: file.size,
        percent: Math.round((uploadedSize / file.size) * 100)
      })
      onChunkComplete?.(i + 1, totalChunks)
    }

    // 合并分片
    return apiClient.post('/upload/merge', {
      fileId,
      filename: file.name,
      totalChunks
    })
  }
}
```

### 2. 上传组件 Hook

```typescript
// composables/useUpload.ts
import { ref } from 'vue'
import { uploadService, UploadResult, UploadProgress } from '@/api/services/uploadService'

interface UseUploadOptions {
  maxSize?: number           // 最大文件大小（字节）
  accept?: string[]          // 允许的文件类型
  multiple?: boolean         // 是否多选
  chunked?: boolean          // 是否分片上传
  onSuccess?: (result: UploadResult | UploadResult[]) => void
  onError?: (error: Error) => void
}

export function useUpload(options: UseUploadOptions = {}) {
  const {
    maxSize = 10 * 1024 * 1024,
    accept = [],
    multiple = false,
    chunked = false,
    onSuccess,
    onError
  } = options

  const uploading = ref(false)
  const progress = ref<UploadProgress>({ loaded: 0, total: 0, percent: 0 })
  const fileList = ref<File[]>([])

  const validateFile = (file: File): string | null => {
    if (maxSize && file.size > maxSize) {
      return `文件大小不能超过 ${formatSize(maxSize)}`
    }

    if (accept.length > 0) {
      const ext = file.name.split('.').pop()?.toLowerCase()
      const mimeType = file.type
      const isValid = accept.some(
        (type) => type === mimeType || type === `.${ext}` || type === `${mimeType.split('/')[0]}/*`
      )
      if (!isValid) {
        return `不支持的文件类型，请上传 ${accept.join(', ')} 格式的文件`
      }
    }

    return null
  }

  const upload = async (files: File | File[]): Promise<UploadResult | UploadResult[] | null> => {
    const fileArray = Array.isArray(files) ? files : [files]

    // 验证文件
    for (const file of fileArray) {
      const error = validateFile(file)
      if (error) {
        onError?.(new Error(error))
        return null
      }
    }

    uploading.value = true
    progress.value = { loaded: 0, total: 0, percent: 0 }

    try {
      let result: UploadResult | UploadResult[]

      if (chunked && fileArray.length === 1) {
        result = await uploadService.uploadChunked(fileArray[0], {
          onProgress: (p) => { progress.value = p }
        })
      } else if (multiple || fileArray.length > 1) {
        result = await uploadService.uploadFiles(fileArray, (p) => { progress.value = p })
      } else {
        result = await uploadService.uploadFile(fileArray[0], (p) => { progress.value = p })
      }

      onSuccess?.(result)
      return result
    } catch (e) {
      onError?.(e as Error)
      return null
    } finally {
      uploading.value = false
    }
  }

  return {
    uploading,
    progress,
    fileList,
    upload,
    validateFile
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
```

---

## 请求取消与竞态处理

### 1. 请求取消管理

```typescript
// api/cancelManager.ts
import axios, { CancelTokenSource } from 'axios'

class CancelManager {
  private pendingRequests = new Map<string, CancelTokenSource>()

  // 生成请求唯一标识
  generateKey(config: { url?: string; method?: string; params?: any }): string {
    const { url, method, params } = config
    return `${method}-${url}-${JSON.stringify(params || {})}`
  }

  // 添加请求
  add(key: string): CancelTokenSource {
    // 取消之前的相同请求
    this.cancel(key)

    const source = axios.CancelToken.source()
    this.pendingRequests.set(key, source)
    return source
  }

  // 取消请求
  cancel(key: string, message?: string): void {
    const source = this.pendingRequests.get(key)
    if (source) {
      source.cancel(message || '请求已取消')
      this.pendingRequests.delete(key)
    }
  }

  // 移除请求（请求完成后调用）
  remove(key: string): void {
    this.pendingRequests.delete(key)
  }

  // 取消所有请求
  cancelAll(message?: string): void {
    this.pendingRequests.forEach((source) => {
      source.cancel(message || '所有请求已取消')
    })
    this.pendingRequests.clear()
  }
}

export const cancelManager = new CancelManager()

// 在路由切换时取消所有请求
router.beforeEach(() => {
  cancelManager.cancelAll('路由切换，取消未完成请求')
})
```

### 2. 竞态条件处理

```typescript
// composables/useLatestRequest.ts
import { ref, onUnmounted } from 'vue'

export function useLatestRequest<T, P extends any[]>(
  service: (...args: P) => Promise<T>
) {
  const data = ref<T>()
  const loading = ref(false)
  const error = ref<Error | null>(null)
  let latestRequestId = 0

  const run = async (...params: P): Promise<T | undefined> => {
    const requestId = ++latestRequestId
    loading.value = true
    error.value = null

    try {
      const result = await service(...params)

      // 只处理最新请求的结果
      if (requestId === latestRequestId) {
        data.value = result as any
        return result
      }
    } catch (e) {
      if (requestId === latestRequestId) {
        error.value = e as Error
        throw e
      }
    } finally {
      if (requestId === latestRequestId) {
        loading.value = false
      }
    }
  }

  // 使用 AbortController 的版本
  let abortController: AbortController | null = null

  const runWithAbort = async (...params: P): Promise<T | undefined> => {
    // 取消之前的请求
    abortController?.abort()
    abortController = new AbortController()

    const currentController = abortController
    loading.value = true
    error.value = null

    try {
      const result = await service(...params)

      if (!currentController.signal.aborted) {
        data.value = result as any
        return result
      }
    } catch (e) {
      if (!currentController.signal.aborted) {
        error.value = e as Error
        throw e
      }
    } finally {
      if (!currentController.signal.aborted) {
        loading.value = false
      }
    }
  }

  onUnmounted(() => {
    abortController?.abort()
  })

  return {
    data,
    loading,
    error,
    run,
    runWithAbort
  }
}
```

---

## 请求缓存策略

### 1. 内存缓存

```typescript
// api/cache.ts
interface CacheItem<T> {
  data: T
  timestamp: number
  expiresAt: number
}

class RequestCache {
  private cache = new Map<string, CacheItem<any>>()
  private defaultTTL = 5 * 60 * 1000 // 5分钟

  set<T>(key: string, data: T, ttl: number = this.defaultTTL): void {
    const now = Date.now()
    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + ttl
    })
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) return null

    if (Date.now() > item.expiresAt) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  has(key: string): boolean {
    return this.get(key) !== null
  }

  delete(key: string): void {
    this.cache.delete(key)
  }

  // 删除匹配的缓存
  deleteMatching(pattern: string | RegExp): void {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern
    this.cache.forEach((_, key) => {
      if (regex.test(key)) {
        this.cache.delete(key)
      }
    })
  }

  clear(): void {
    this.cache.clear()
  }

  // 清理过期缓存
  cleanup(): void {
    const now = Date.now()
    this.cache.forEach((item, key) => {
      if (now > item.expiresAt) {
        this.cache.delete(key)
      }
    })
  }
}

export const requestCache = new RequestCache()

// 定期清理
setInterval(() => requestCache.cleanup(), 60 * 1000)
```

### 2. SWR 策略实现

```typescript
// composables/useSWR.ts
import { ref, watch, onMounted } from 'vue'
import { requestCache } from '@/api/cache'

interface UseSWROptions<T> {
  cacheKey: string
  ttl?: number
  revalidateOnFocus?: boolean
  revalidateOnReconnect?: boolean
  dedupingInterval?: number
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
}

export function useSWR<T>(
  fetcher: () => Promise<T>,
  options: UseSWROptions<T>
) {
  const {
    cacheKey,
    ttl = 5 * 60 * 1000,
    revalidateOnFocus = true,
    revalidateOnReconnect = true,
    dedupingInterval = 2000,
    onSuccess,
    onError
  } = options

  const data = ref<T>()
  const error = ref<Error | null>(null)
  const isValidating = ref(false)

  let lastFetchTime = 0

  const revalidate = async () => {
    const now = Date.now()

    // 防抖：避免短时间内重复请求
    if (now - lastFetchTime < dedupingInterval) {
      return
    }

    lastFetchTime = now
    isValidating.value = true

    try {
      const result = await fetcher()
      data.value = result as any
      requestCache.set(cacheKey, result, ttl)
      onSuccess?.(result)
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
    } finally {
      isValidating.value = false
    }
  }

  // 初始化：先返回缓存，再后台更新
  onMounted(() => {
    const cached = requestCache.get<T>(cacheKey)
    if (cached) {
      data.value = cached as any
    }
    revalidate()
  })

  // 窗口聚焦时重新验证
  if (revalidateOnFocus) {
    const handleFocus = () => revalidate()
    window.addEventListener('focus', handleFocus)
  }

  // 网络恢复时重新验证
  if (revalidateOnReconnect) {
    const handleOnline = () => revalidate()
    window.addEventListener('online', handleOnline)
  }

  return {
    data,
    error,
    isValidating,
    revalidate,
    mutate: (newData: T) => {
      data.value = newData as any
      requestCache.set(cacheKey, newData, ttl)
    }
  }
}
```

---

## WebSocket 实时通信

### 1. WebSocket 客户端封装

```typescript
// api/websocket.ts
type MessageHandler = (data: any) => void
type ConnectionHandler = () => void

interface WebSocketOptions {
  url: string
  protocols?: string[]
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

class WebSocketClient {
  private ws: WebSocket | null = null
  private options: Required<WebSocketOptions>
  private messageHandlers = new Map<string, Set<MessageHandler>>()
  private reconnectAttempts = 0
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  public onOpen: ConnectionHandler | null = null
  public onClose: ConnectionHandler | null = null
  public onError: ((error: Event) => void) | null = null

  constructor(options: WebSocketOptions) {
    this.options = {
      protocols: [],
      reconnect: true,
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      ...options
    }
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return

    this.ws = new WebSocket(this.options.url, this.options.protocols)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.startHeartbeat()
      this.onOpen?.()
    }

    this.ws.onclose = () => {
      this.stopHeartbeat()
      this.onClose?.()
      this.tryReconnect()
    }

    this.ws.onerror = (error) => {
      this.onError?.(error)
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        const { type, data } = message
        this.messageHandlers.get(type)?.forEach((handler) => handler(data))
      } catch (e) {
        console.error('WebSocket message parse error:', e)
      }
    }
  }

  disconnect(): void {
    this.stopHeartbeat()
    this.clearReconnectTimer()
    this.ws?.close()
    this.ws = null
  }

  send(type: string, data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }))
    }
  }

  on(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set())
    }
    this.messageHandlers.get(type)!.add(handler)

    // 返回取消订阅函数
    return () => {
      this.messageHandlers.get(type)?.delete(handler)
    }
  }

  off(type: string, handler?: MessageHandler): void {
    if (handler) {
      this.messageHandlers.get(type)?.delete(handler)
    } else {
      this.messageHandlers.delete(type)
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send('ping', { timestamp: Date.now() })
    }, this.options.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private tryReconnect(): void {
    if (!this.options.reconnect) return
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) return

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++
      this.connect()
    }, this.options.reconnectInterval)
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
}

export const wsClient = new WebSocketClient({
  url: import.meta.env.VITE_WS_URL
})
```

### 2. WebSocket Hook

```typescript
// composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { wsClient } from '@/api/websocket'

export function useWebSocket() {
  const connected = ref(false)

  onMounted(() => {
    wsClient.onOpen = () => { connected.value = true }
    wsClient.onClose = () => { connected.value = false }
    wsClient.connect()
  })

  onUnmounted(() => {
    wsClient.disconnect()
  })

  const subscribe = <T>(type: string, handler: (data: T) => void) => {
    return wsClient.on(type, handler)
  }

  const send = (type: string, data: any) => {
    wsClient.send(type, data)
  }

  return {
    connected,
    subscribe,
    send
  }
}

// 使用示例
const { connected, subscribe, send } = useWebSocket()

// 订阅消息
const unsubscribe = subscribe<{ content: string }>('chat:message', (data) => {
  messages.value.push(data)
})

// 发送消息
send('chat:send', { content: 'Hello!' })

// 组件卸载时自动取消订阅
onUnmounted(() => unsubscribe())
```

---

## API 设计规范

### 1. RESTful 规范

| 方法 | 路径 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /users | 获取用户列表 | - | 用户数组 |
| GET | /users/:id | 获取单个用户 | - | 用户对象 |
| POST | /users | 创建用户 | 用户数据 | 新用户对象 |
| PUT | /users/:id | 全量更新用户 | 完整用户数据 | 更新后用户 |
| PATCH | /users/:id | 部分更新用户 | 部分用户数据 | 更新后用户 |
| DELETE | /users/:id | 删除用户 | - | 空 |

### 2. 响应格式规范

```typescript
// 成功响应
interface SuccessResponse<T> {
  code: 0 | 200
  data: T
  message: 'success'
  timestamp: number
}

// 错误响应
interface ErrorResponse {
  code: number        // 业务错误码
  message: string     // 错误信息
  details?: any       // 详细错误（如验证错误）
  timestamp: number
}

// 分页响应
interface PaginatedData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
  hasMore: boolean
}

// 常用业务错误码
const ErrorCodes = {
  // 通用错误 1xxx
  UNKNOWN: 1000,
  VALIDATION_ERROR: 1001,
  NOT_FOUND: 1002,

  // 认证错误 2xxx
  UNAUTHORIZED: 2001,
  TOKEN_EXPIRED: 2002,
  INVALID_TOKEN: 2003,

  // 权限错误 3xxx
  FORBIDDEN: 3001,
  INSUFFICIENT_PERMISSIONS: 3002,

  // 业务错误 4xxx
  USER_EXISTS: 4001,
  USER_NOT_FOUND: 4002,
  INVALID_PASSWORD: 4003
}
```

### 3. 请求参数规范

```typescript
// 分页参数
interface PaginationParams {
  page: number        // 页码，从1开始
  pageSize: number    // 每页数量，默认10
}

// 排序参数
interface SortParams {
  sortBy: string      // 排序字段
  sortOrder: 'asc' | 'desc'  // 排序方向
}

// 筛选参数
interface FilterParams {
  keyword?: string    // 搜索关键词
  status?: string     // 状态筛选
  startDate?: string  // 开始日期
  endDate?: string    // 结束日期
}

// 组合查询参数
type QueryParams = PaginationParams & Partial<SortParams> & FilterParams
```

---

## 最佳实践清单

| 类别 | 实践 | 说明 |
|------|------|------|
| 错误处理 | 统一错误类型 | 定义清晰的错误层次结构 |
| 错误处理 | 全局错误拦截 | 在拦截器中统一处理 |
| 认证 | Token 自动刷新 | 无感知刷新过期Token |
| 认证 | 并发刷新防护 | 防止多个请求同时刷新 |
| 性能 | 请求缓存 | 缓存不常变化的数据 |
| 性能 | 请求去重 | 避免重复请求 |
| 性能 | 请求取消 | 路由切换时取消未完成请求 |
| 可靠性 | 请求重试 | 服务器错误自动重试 |
| 可靠性 | 竞态处理 | 只处理最新请求结果 |
| 类型安全 | 完整类型定义 | 请求和响应都有类型 |
| 可维护性 | 服务模块化 | 按业务领域拆分服务 |
