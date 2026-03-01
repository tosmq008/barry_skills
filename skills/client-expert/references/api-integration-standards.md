# API 集成规范指南

> 本文档为 client-expert 技能参考手册，定义跨平台（iOS / Android / Web / Flutter / 微信小程序）统一的 API 集成标准，涵盖协议规范、认证授权、网络层架构、数据映射、缓存策略、实时通信、文件传输及联调调试。

---

## 1. 接口协议规范

### 1.1 RESTful API 设计规范

| 规则 | 示例 | 说明 |
|------|------|------|
| 资源用名词复数 | `/api/v1/users` | 不使用动词 |
| 层级关系用嵌套 | `/api/v1/users/{id}/orders` | 最多两层嵌套 |
| 版本号放 URL | `/api/v1/...` | 或使用 Header: `Accept: application/vnd.app.v1+json` |
| 过滤用查询参数 | `?status=active&role=admin` | 避免在 path 中放过滤条件 |
| 批量操作用 POST | `POST /api/v1/users/batch` | body 携带 ID 列表 |

HTTP 方法语义：

| 方法 | 语义 | 幂等 | 安全 | 典型响应码 |
|------|------|------|------|-----------|
| GET | 查询资源 | 是 | 是 | 200 |
| POST | 创建资源 | 否 | 否 | 201 |
| PUT | 全量更新 | 是 | 否 | 200 |
| PATCH | 部分更新 | 否 | 否 | 200 |
| DELETE | 删除资源 | 是 | 否 | 204 |

### 1.2 统一响应体结构

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "meta": {
    "timestamp": 1700000000000,
    "requestId": "req_abc123"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | `number` | 是 | 0 表示成功，非 0 为业务错误码 |
| `message` | `string` | 是 | 人类可读的提示信息 |
| `data` | `object/array/null` | 是 | 业务数据，失败时为 `null` |
| `meta` | `object` | 否 | 元信息：时间戳、请求 ID、分页等 |
### 1.3 错误码体系

采用分段式错误码，便于快速定位问题来源：

| 范围 | 分类 | 示例 |
|------|------|------|
| `0` | 成功 | `0` — 操作成功 |
| `1000-1999` | 通用错误 | `1001` — 参数校验失败 |
| `2000-2999` | 认证授权 | `2001` — Token 过期，`2002` — 无权限 |
| `3000-3999` | 用户模块 | `3001` — 用户不存在 |
| `4000-4999` | 订单模块 | `4001` — 库存不足 |
| `5000-5999` | 支付模块 | `5001` — 支付超时 |
| `9000-9999` | 系统错误 | `9001` — 服务不可用 |

客户端统一错误处理模型：

```typescript
interface ApiError {
  code: number
  message: string
  details?: Record<string, string[]>  // 字段级错误
  requestId?: string                   // 用于排查
}

// 客户端错误分类处理
function handleApiError(error: ApiError): void {
  switch (true) {
    case error.code >= 2000 && error.code < 3000:
      // 认证错误 → 跳转登录
      redirectToLogin()
      break
    case error.code >= 1000 && error.code < 2000:
      // 参数错误 → 表单提示
      showFieldErrors(error.details)
      break
    default:
      // 通用错误 → Toast 提示
      showToast(error.message)
  }
}
```

### 1.4 分页协议

#### Page-Based 分页（适用于传统列表）

```
GET /api/v1/users?page=1&pageSize=20&sort=createdAt:desc
```

```json
{
  "code": 0,
  "data": {
    "list": [],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 150,
      "totalPages": 8
    }
  }
}
```

#### Cursor-Based 分页（适用于信息流、聊天记录）

```
GET /api/v1/messages?cursor=msg_abc123&limit=20&direction=before
```

```json
{
  "code": 0,
  "data": {
    "list": [],
    "cursor": {
      "next": "msg_xyz789",
      "prev": "msg_abc123",
      "hasMore": true
    }
  }
}
```

| 对比项 | Page-Based | Cursor-Based |
|--------|-----------|--------------|
| 跳页 | 支持 | 不支持 |
| 数据一致性 | 插入/删除会导致偏移 | 稳定 |
| 性能 | 大偏移量时慢 | 恒定 O(1) |
| 适用场景 | 后台管理列表 | 信息流、聊天、时间线 |

### 1.5 时间格式与空值约定

| 约定 | 规范 | 示例 |
|------|------|------|
| 时间传输 | ISO 8601 字符串或毫秒时间戳 | `"2024-01-15T08:30:00Z"` 或 `1705304400000` |
| 时区 | 服务端统一 UTC，客户端本地化显示 | — |
| 空值 | 字段缺失或 `null`，不使用空字符串表示无值 | `"name": null` |
| 空数组 | 返回 `[]`，不返回 `null` | `"tags": []` |
| 布尔值 | 严格 `true/false`，不使用 `0/1` | `"isActive": true` |
| 金额 | 整数（分），避免浮点精度问题 | `"amount": 9990` 表示 99.90 元 |

---

## 2. 认证与授权

### 2.1 Token 认证流程

```
┌─────────┐     POST /auth/login      ┌─────────┐
│  Client  │ ──────────────────────── → │  Server  │
│         │ ← ──────────────────────── │         │
│         │   { accessToken,           │         │
│         │     refreshToken,          │         │
│         │     expiresIn: 7200 }      │         │
│         │                            │         │
│         │   GET /api/xxx             │         │
│         │   Authorization: Bearer xx │         │
│         │ ──────────────────────── → │         │
│         │                            │         │
│         │   401 Token Expired        │         │
│         │ ← ──────────────────────── │         │
│         │                            │         │
│         │   POST /auth/refresh       │         │
│         │   { refreshToken }         │         │
│         │ ──────────────────────── → │         │
│         │ ← ──────────────────────── │         │
│         │   { newAccessToken,        │         │
│         │     newRefreshToken }      │         │
└─────────┘                            └─────────┘
```
### 2.2 Token 存储方案（各平台安全存储）

| 平台 | 存储方案 | 安全等级 | 说明 |
|------|---------|---------|------|
| iOS | Keychain Services | 高 | 硬件加密，支持 biometric 保护 |
| Android | EncryptedSharedPreferences / Keystore | 高 | AES-256 加密 |
| Web | httpOnly Cookie + CSRF Token | 中 | 禁止 localStorage 存 Token |
| Flutter | flutter_secure_storage | 高 | 底层调用各平台安全存储 |
| 微信小程序 | wx.setStorageSync (加密) | 中 | 配合自定义加密层 |

各平台存储示例：

```swift
// iOS — Keychain
import Security

func saveToken(_ token: String, forKey key: String) {
    let data = Data(token.utf8)
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    ]
    SecItemDelete(query as CFDictionary)
    SecItemAdd(query as CFDictionary, nil)
}
```

```kotlin
// Android — EncryptedSharedPreferences
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "auth_prefs", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

prefs.edit().putString("access_token", token).apply()
```

```dart
// Flutter — flutter_secure_storage
final storage = FlutterSecureStorage();
await storage.write(key: 'access_token', value: token);
final token = await storage.read(key: 'access_token');
```

### 2.3 Token 自动刷新机制

核心要求：
- 刷新过程对业务层透明，业务代码无需感知 Token 过期
- 并发请求遇到 401 时，只触发一次刷新，其余请求排队等待
- 刷新失败（Refresh Token 也过期）时统一跳转登录页

```typescript
// 通用 Token 刷新拦截器（伪代码）
class TokenRefreshInterceptor {
  private isRefreshing = false
  private pendingRequests: Array<() => void> = []

  async onResponseError(error: AxiosError): Promise<any> {
    if (error.response?.status !== 401) {
      throw error
    }

    if (this.isRefreshing) {
      // 排队等待刷新完成
      return new Promise((resolve) => {
        this.pendingRequests.push(() => {
          resolve(retryRequest(error.config))
        })
      })
    }

    this.isRefreshing = true
    try {
      const newToken = await this.refreshToken()
      this.updateStoredToken(newToken)
      // 重放排队请求
      this.pendingRequests.forEach((cb) => cb())
      this.pendingRequests = []
      return retryRequest(error.config)
    } catch (refreshError) {
      this.pendingRequests = []
      redirectToLogin()
      throw refreshError
    } finally {
      this.isRefreshing = false
    }
  }
}
```
### 2.4 OAuth 2.0 集成

常用授权模式：

| 模式 | 适用场景 | 客户端类型 |
|------|---------|-----------|
| Authorization Code + PKCE | 移动端、SPA | 公开客户端 |
| Authorization Code | Web 后端 | 机密客户端 |
| Client Credentials | 服务间调用 | 机密客户端 |

PKCE 流程（移动端推荐）：

```
1. 生成 code_verifier (43-128 字符随机串)
2. 计算 code_challenge = BASE64URL(SHA256(code_verifier))
3. 打开授权页: /authorize?response_type=code&code_challenge=xxx&code_challenge_method=S256
4. 用户授权后回调携带 code
5. 用 code + code_verifier 换取 Token
```

```swift
// iOS — ASWebAuthenticationSession
import AuthenticationServices

func startOAuth() {
    let codeVerifier = generateCodeVerifier()
    let codeChallenge = computeCodeChallenge(codeVerifier)

    let url = URL(string: "https://auth.example.com/authorize"
        + "?response_type=code"
        + "&client_id=\(clientId)"
        + "&redirect_uri=\(redirectUri)"
        + "&code_challenge=\(codeChallenge)"
        + "&code_challenge_method=S256")!

    let session = ASWebAuthenticationSession(
        url: url,
        callbackURLScheme: "myapp"
    ) { callbackURL, error in
        guard let code = callbackURL?.queryParam("code") else { return }
        exchangeCodeForToken(code: code, codeVerifier: codeVerifier)
    }
    session.presentationContextProvider = self
    session.start()
}
```

---

## 3. 网络层架构

### 3.1 各平台网络库选型

| 平台 | 推荐库 | 备选 | 说明 |
|------|--------|------|------|
| iOS | URLSession + async/await | Alamofire 5 | 原生优先，Alamofire 用于复杂场景 |
| Android | OkHttp + Retrofit | Ktor Client | Retrofit 注解式 API 定义 |
| Web | Axios | fetch + 封装 | Axios 拦截器生态成熟 |
| Flutter | Dio | http | Dio 拦截器、取消、上传进度完善 |
| 微信小程序 | wx.request 封装 | luch-request | 需封装 Promise 化 + 拦截器 |

### 3.2 统一拦截器设计

所有平台的网络层必须实现以下拦截器链：

```
Request → [Auth] → [Log] → [Retry] → [Cache] → Network
                                                    ↓
Response ← [Log] ← [Error] ← [Transform] ← ── Network
```

#### Auth 拦截器

```kotlin
// Android — OkHttp Interceptor
class AuthInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenProvider.getAccessToken()
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .addHeader("X-Platform", "android")
            .addHeader("X-App-Version", BuildConfig.VERSION_NAME)
            .build()
        return chain.proceed(request)
    }
}
```

#### Retry 拦截器

```dart
// Flutter — Dio Interceptor
class RetryInterceptor extends Interceptor {
  final Dio dio;
  final int maxRetries;
  final List<int> retryStatusCodes = [408, 500, 502, 503, 504];

  RetryInterceptor({required this.dio, this.maxRetries = 3});

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final statusCode = err.response?.statusCode;
    final retryCount = err.requestOptions.extra['retryCount'] ?? 0;

    if (retryStatusCodes.contains(statusCode) && retryCount < maxRetries) {
      final delay = Duration(milliseconds: 1000 * pow(2, retryCount).toInt());
      await Future.delayed(delay);

      final options = err.requestOptions;
      options.extra['retryCount'] = retryCount + 1;

      try {
        final response = await dio.fetch(options);
        handler.resolve(response);
      } catch (e) {
        handler.next(err);
      }
    } else {
      handler.next(err);
    }
  }
}
```
### 3.3 请求队列与并发控制

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| 最大并发数限制 | 同时最多 N 个请求 | 防止服务端过载 |
| 优先级队列 | 关键请求优先执行 | 登录 > 数据加载 > 预加载 |
| 请求合并 | 相同请求在窗口期内合并 | 搜索联想、频繁刷新 |
| 节流/防抖 | 限制请求频率 | 搜索输入、滚动加载 |

```typescript
// 并发控制器
class RequestQueue {
  private readonly maxConcurrent: number
  private running = 0
  private readonly queue: Array<() => Promise<void>> = []

  constructor(maxConcurrent = 6) {
    this.maxConcurrent = maxConcurrent
  }

  async add<T>(fn: () => Promise<T>): Promise<T> {
    if (this.running >= this.maxConcurrent) {
      await new Promise<void>((resolve) => {
        this.queue.push(resolve)
      })
    }
    this.running++
    try {
      return await fn()
    } finally {
      this.running--
      const next = this.queue.shift()
      if (next) next()
    }
  }
}
```

### 3.4 请求取消与去重

```swift
// iOS — Task 取消
class SearchViewModel {
    private var searchTask: Task<Void, Never>?

    func search(keyword: String) {
        // 取消上一次搜索
        searchTask?.cancel()

        searchTask = Task {
            try await Task.sleep(nanoseconds: 300_000_000) // 防抖 300ms
            guard !Task.isCancelled else { return }

            let results = try await apiClient.search(keyword: keyword)
            guard !Task.isCancelled else { return }

            await MainActor.run {
                self.results = results
            }
        }
    }
}
```

```kotlin
// Android — Coroutine 取消
class SearchViewModel : ViewModel() {
    private var searchJob: Job? = null

    fun search(keyword: String) {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300) // 防抖
            val results = repository.search(keyword)
            _results.value = results
        }
    }
}
```

请求去重策略：

```typescript
// 基于请求签名的去重
class RequestDeduplicator {
  private readonly pending = new Map<string, Promise<any>>()

  async dedupe<T>(key: string, fn: () => Promise<T>): Promise<T> {
    const existing = this.pending.get(key)
    if (existing) {
      return existing as Promise<T>
    }

    const promise = fn().finally(() => {
      this.pending.delete(key)
    })
    this.pending.set(key, promise)
    return promise
  }
}

// 使用
const dedup = new RequestDeduplicator()
const user = await dedup.dedupe(
  `GET:/api/v1/users/${id}`,
  () => api.getUser(id)
)
```

---

## 4. 数据模型映射

### 4.1 DTO 与 Domain Model 分离

```
Server JSON → DTO (数据传输对象) → Domain Model (业务模型) → ViewModel (视图模型)
```

| 层 | 职责 | 命名约定 |
|----|------|---------|
| DTO | 与接口 1:1 映射，snake_case 字段 | `UserDTO`, `OrderResponseDTO` |
| Domain Model | 业务逻辑，camelCase 字段 | `User`, `Order` |
| ViewModel | 视图展示，包含格式化逻辑 | `UserDisplayModel` |

```swift
// iOS 示例
// DTO — 与接口字段一致
struct UserDTO: Codable {
    let user_id: Int
    let nick_name: String
    let avatar_url: String?
    let created_at: String
}

// Domain Model — 业务模型
struct User {
    let id: Int
    let nickname: String
    let avatarURL: URL?
    let createdAt: Date
}

// 映射扩展
extension User {
    init(dto: UserDTO) {
        self.id = dto.user_id
        self.nickname = dto.nick_name
        self.avatarURL = dto.avatar_url.flatMap(URL.init)
        self.createdAt = ISO8601DateFormatter().date(from: dto.created_at) ?? Date()
    }
}
```
### 4.2 各平台 JSON 解析方案

| 平台 | 方案 | 特点 |
|------|------|------|
| iOS | `Codable` + `JSONDecoder` | 编译期类型安全，支持 keyDecodingStrategy |
| Android | Kotlin Serialization / Moshi / Gson | Kotlin Serialization 推荐，编译期生成 |
| Web | TypeScript 接口 + zod 校验 | 运行时类型校验 |
| Flutter | `json_serializable` + `freezed` | 代码生成，不可变模型 |
| 微信小程序 | 手动映射 / 工具函数 | 无原生方案，需封装 |

```kotlin
// Android — Kotlin Serialization
@Serializable
data class UserDTO(
    @SerialName("user_id") val userId: Int,
    @SerialName("nick_name") val nickName: String,
    @SerialName("avatar_url") val avatarUrl: String? = null,
    @SerialName("created_at") val createdAt: String
)

// Retrofit 配合
val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
    .build()
```

```dart
// Flutter — freezed + json_serializable
@freezed
class UserDTO with _$UserDTO {
  const factory UserDTO({
    @JsonKey(name: 'user_id') required int userId,
    @JsonKey(name: 'nick_name') required String nickName,
    @JsonKey(name: 'avatar_url') String? avatarUrl,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _UserDTO;

  factory UserDTO.fromJson(Map<String, dynamic> json) =>
      _$UserDTOFromJson(json);
}
```

### 4.3 字段命名映射（snake_case <-> camelCase）

各平台全局配置，避免逐字段手动映射：

```swift
// iOS — 全局 snake_case 转换
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
decoder.dateDecodingStrategy = .iso8601

let encoder = JSONEncoder()
encoder.keyEncodingStrategy = .convertToSnakeCase
```

```typescript
// Web — Axios 响应转换
import camelcaseKeys from 'camelcase-keys'
import snakecaseKeys from 'snakecase-keys'

axios.interceptors.response.use((response) => ({
  ...response,
  data: camelcaseKeys(response.data, { deep: true })
}))

axios.interceptors.request.use((config) => ({
  ...config,
  data: config.data ? snakecaseKeys(config.data, { deep: true }) : undefined
}))
```

### 4.4 类型安全与空值处理

| 平台 | 空安全机制 | 最佳实践 |
|------|-----------|---------|
| iOS | Swift Optional (`?`) | 使用 `guard let` / `if let` 解包 |
| Android | Kotlin Nullable (`?`) | 使用 `?.` 安全调用链 |
| Web | TypeScript strict null checks | 启用 `strictNullChecks`，使用 zod 校验 |
| Flutter | Dart sound null safety | 必填字段用 `required`，可选用 `?` |
| 微信小程序 | 无原生支持 | 封装安全取值工具函数 |

```typescript
// Web — zod 运行时校验
import { z } from 'zod'

const UserSchema = z.object({
  userId: z.number(),
  nickName: z.string(),
  avatarUrl: z.string().url().nullable(),
  createdAt: z.string().datetime(),
  tags: z.array(z.string()).default([]),
})

type User = z.infer<typeof UserSchema>

function parseUser(raw: unknown): User {
  return UserSchema.parse(raw)
}
```

---

## 5. 离线与缓存策略

### 5.1 请求缓存（内存 / 磁盘）

三级缓存架构：

```
请求 → [内存缓存] → [磁盘缓存] → [网络请求] → 回写缓存
```

| 缓存层 | 容量 | 过期策略 | 适用数据 |
|--------|------|---------|---------|
| L1 内存 | 50-100MB | LRU + TTL (5min) | 热点数据、列表 |
| L2 磁盘 | 200-500MB | LRU + TTL (24h) | 详情页、配置 |
| L3 数据库 | 按需 | 版本号 / 时间戳 | 离线核心数据 |

缓存策略枚举：

```typescript
enum CachePolicy {
  // 仅网络，不缓存
  NetworkOnly = 'network-only',
  // 优先缓存，过期则请求网络
  CacheFirst = 'cache-first',
  // 优先网络，失败则读缓存
  NetworkFirst = 'network-first',
  // 先返回缓存，同时请求网络更新（Stale-While-Revalidate）
  StaleWhileRevalidate = 'stale-while-revalidate',
  // 仅缓存
  CacheOnly = 'cache-only',
}
```
### 5.2 离线优先策略

```swift
// iOS — 离线优先数据加载
func loadArticles() async -> [Article] {
    // 1. 立即返回本地数据
    let cached = await localStore.getArticles()
    if !cached.isEmpty {
        self.articles = cached
    }

    // 2. 后台同步远程数据
    do {
        let remote = try await apiClient.fetchArticles()
        await localStore.saveArticles(remote)
        self.articles = remote
    } catch {
        // 网络失败时保持本地数据
        if cached.isEmpty {
            self.error = error
        }
    }
}
```

### 5.3 数据同步机制

| 策略 | 实现方式 | 适用场景 |
|------|---------|---------|
| Pull 同步 | 客户端定时拉取 | 低频更新数据 |
| Push 同步 | WebSocket / 推送通知触发 | 实时性要求高 |
| 增量同步 | `lastSyncTimestamp` + 变更列表 | 大数据量 |
| 冲突解决 | Last-Write-Wins / 服务端仲裁 | 多端编辑 |

增量同步协议：

```
GET /api/v1/sync?since=1700000000000&entities=users,orders
```

```json
{
  "code": 0,
  "data": {
    "changes": [
      { "entity": "users", "id": "u1", "action": "update", "data": {...}, "updatedAt": 1700001000000 },
      { "entity": "orders", "id": "o5", "action": "delete", "deletedAt": 1700002000000 }
    ],
    "syncTimestamp": 1700003000000,
    "hasMore": false
  }
}
```

### 5.4 乐观更新

```typescript
// Web — React Query 乐观更新
function useToggleLike(postId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.toggleLike(postId),

    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ['post', postId] })
      const previous = queryClient.getQueryData(['post', postId])

      // 乐观更新 UI
      queryClient.setQueryData(['post', postId], (old: Post) => ({
        ...old,
        isLiked: !old.isLiked,
        likeCount: old.isLiked ? old.likeCount - 1 : old.likeCount + 1,
      }))

      return { previous }
    },

    onError: (_err, _vars, context) => {
      // 失败回滚
      queryClient.setQueryData(['post', postId], context?.previous)
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['post', postId] })
    },
  })
}
```

---

## 6. 实时通信

### 6.1 WebSocket 集成

连接管理要点：

| 要点 | 规范 |
|------|------|
| 协议 | 生产环境必须使用 `wss://` |
| 认证 | 连接时通过 URL 参数或首条消息携带 Token |
| 消息格式 | JSON，包含 `type` / `payload` / `id` 字段 |
| 心跳 | 客户端每 30s 发送 ping，服务端 pong |
| 重连 | 指数退避，最大间隔 60s |

消息协议：

```json
// 客户端 → 服务端
{ "type": "subscribe", "payload": { "channel": "chat:room_123" }, "id": "msg_001" }

// 服务端 → 客户端
{ "type": "message", "payload": { "content": "Hello", "sender": "user_1" }, "id": "msg_002" }

// 心跳
{ "type": "ping", "id": "hb_001" }
{ "type": "pong", "id": "hb_001" }
```

```swift
// iOS — URLSessionWebSocketTask
class WebSocketManager {
    private var socket: URLSessionWebSocketTask?
    private var retryCount = 0
    private let maxRetryDelay: TimeInterval = 60

    func connect(url: URL, token: String) {
        var request = URLRequest(url: url)
        request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        socket = URLSession.shared.webSocketTask(with: request)
        socket?.resume()
        startListening()
        startHeartbeat()
    }

    private func startListening() {
        socket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                self?.handleMessage(message)
                self?.startListening() // 继续监听
            case .failure:
                self?.reconnect()
            }
        }
    }

    private func reconnect() {
        let delay = min(pow(2.0, Double(retryCount)), maxRetryDelay)
        retryCount += 1
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.connect(url: self?.currentURL, token: self?.currentToken)
        }
    }
}
```
### 6.2 SSE (Server-Sent Events)

适用于服务端单向推送场景（通知、实时数据流、AI 流式输出）：

```typescript
// Web — EventSource
function subscribeToNotifications(userId: string): EventSource {
  const source = new EventSource(`/api/v1/sse/notifications?userId=${userId}`)

  source.addEventListener('notification', (event) => {
    const data = JSON.parse(event.data)
    showNotification(data)
  })

  source.addEventListener('heartbeat', () => {
    // 保持连接活跃
  })

  source.onerror = () => {
    // 浏览器会自动重连，可在此记录日志
    console.error('SSE connection lost, auto-reconnecting...')
  }

  return source
}
```

```dart
// Flutter — SSE 流式接收（AI 对话场景）
Stream<String> streamChat(String prompt) async* {
  final request = http.Request('POST', Uri.parse('$baseUrl/api/v1/chat/stream'));
  request.headers['Authorization'] = 'Bearer $token';
  request.headers['Content-Type'] = 'application/json';
  request.body = jsonEncode({'prompt': prompt});

  final response = await http.Client().send(request);
  await for (final chunk in response.stream.transform(utf8.decoder)) {
    for (final line in chunk.split('\n')) {
      if (line.startsWith('data: ')) {
        final data = line.substring(6);
        if (data == '[DONE]') return;
        yield jsonDecode(data)['content'];
      }
    }
  }
}
```

### 6.3 长轮询降级方案

当 WebSocket / SSE 不可用时（如部分企业网络环境、微信小程序），降级为长轮询：

```javascript
// 微信小程序 — 长轮询
class LongPolling {
  constructor(url, onMessage) {
    this.url = url
    this.onMessage = onMessage
    this.active = true
  }

  async start() {
    while (this.active) {
      try {
        const res = await wxRequest({
          url: this.url,
          timeout: 30000, // 30s 超时
        })
        if (res.data?.messages?.length > 0) {
          res.data.messages.forEach(this.onMessage)
        }
      } catch (err) {
        // 网络错误时短暂等待后重试
        await sleep(3000)
      }
    }
  }

  stop() {
    this.active = false
  }
}
```

### 6.4 心跳与重连机制

```kotlin
// Android — 统一重连策略
class ReconnectPolicy(
    private val initialDelay: Long = 1000,
    private val maxDelay: Long = 60000,
    private val multiplier: Double = 2.0,
    private val jitterFactor: Double = 0.1
) {
    private var attempt = 0

    fun nextDelay(): Long {
        val base = min(initialDelay * multiplier.pow(attempt.toDouble()), maxDelay.toDouble())
        val jitter = base * jitterFactor * Random.nextDouble(-1.0, 1.0)
        attempt++
        return (base + jitter).toLong()
    }

    fun reset() { attempt = 0 }
}
```

实时通信方案选型：

| 方案 | 方向 | 延迟 | 兼容性 | 适用场景 |
|------|------|------|--------|---------|
| WebSocket | 双向 | 极低 | 好 | 聊天、协同编辑、游戏 |
| SSE | 服务端->客户端 | 低 | 好（IE 除外） | 通知、数据流、AI 流式 |
| 长轮询 | 模拟双向 | 中 | 极好 | 降级方案、小程序 |
| MQTT | 双向 | 低 | 需 SDK | IoT、消息推送 |

---

## 7. 文件上传下载

### 7.1 分片上传

大文件（>5MB）必须使用分片上传：

```
1. POST /api/v1/upload/init     -> 获取 uploadId
2. PUT  /api/v1/upload/part     -> 逐片上传 (并发 3 片)
3. POST /api/v1/upload/complete -> 合并完成
```

```swift
// iOS — 分片上传
func uploadLargeFile(fileURL: URL) async throws -> String {
    let fileData = try Data(contentsOf: fileURL)
    let chunkSize = 5 * 1024 * 1024 // 5MB per chunk
    let totalChunks = Int(ceil(Double(fileData.count) / Double(chunkSize)))

    // 1. 初始化上传
    let initResponse = try await api.initUpload(
        fileName: fileURL.lastPathComponent,
        fileSize: fileData.count,
        totalChunks: totalChunks
    )
    let uploadId = initResponse.uploadId

    // 2. 并发上传分片（最多 3 个并发）
    try await withThrowingTaskGroup(of: Void.self) { group in
        var runningTasks = 0
        for index in 0..<totalChunks {
            if runningTasks >= 3 {
                try await group.next()
                runningTasks -= 1
            }
            let start = index * chunkSize
            let end = min(start + chunkSize, fileData.count)
            let chunk = fileData[start..<end]

            group.addTask {
                try await self.api.uploadPart(
                    uploadId: uploadId,
                    partNumber: index + 1,
                    data: chunk
                )
            }
            runningTasks += 1
        }
        try await group.waitForAll()
    }

    // 3. 完成上传
    let result = try await api.completeUpload(uploadId: uploadId)
    return result.fileUrl
}
```
### 7.2 断点续传

```kotlin
// Android — 断点续传下载
class ResumableDownloader(private val okHttpClient: OkHttpClient) {

    suspend fun download(url: String, destFile: File, onProgress: (Float) -> Unit) {
        val downloadedBytes = if (destFile.exists()) destFile.length() else 0L

        val request = Request.Builder()
            .url(url)
            .apply {
                if (downloadedBytes > 0) {
                    addHeader("Range", "bytes=$downloadedBytes-")
                }
            }
            .build()

        val response = okHttpClient.newCall(request).await()
        val totalBytes = when (response.code) {
            206 -> downloadedBytes + (response.body?.contentLength() ?: 0)
            200 -> response.body?.contentLength() ?: 0
            else -> throw IOException("Unexpected code: ${response.code}")
        }

        val appendMode = response.code == 206
        FileOutputStream(destFile, appendMode).use { output ->
            response.body?.byteStream()?.use { input ->
                val buffer = ByteArray(8192)
                var bytesRead: Int
                var totalRead = downloadedBytes

                while (input.read(buffer).also { bytesRead = it } != -1) {
                    output.write(buffer, 0, bytesRead)
                    totalRead += bytesRead
                    onProgress(totalRead.toFloat() / totalBytes)
                }
            }
        }
    }
}
```

### 7.3 进度回调

各平台进度监听方案：

```dart
// Flutter — Dio 上传进度
Future<String> uploadFile(File file) async {
  final formData = FormData.fromMap({
    'file': await MultipartFile.fromFile(
      file.path,
      filename: file.path.split('/').last,
    ),
  });

  final response = await dio.post(
    '/api/v1/upload',
    data: formData,
    onSendProgress: (sent, total) {
      final progress = sent / total;
      uploadProgressController.add(progress);
    },
  );

  return response.data['data']['url'];
}
```

```javascript
// 微信小程序 — 上传进度
function uploadFile(filePath) {
  return new Promise((resolve, reject) => {
    const task = wx.uploadFile({
      url: `${BASE_URL}/api/v1/upload`,
      filePath,
      name: 'file',
      header: { Authorization: `Bearer ${getToken()}` },
      success: (res) => resolve(JSON.parse(res.data)),
      fail: reject,
    })

    task.onProgressUpdate((res) => {
      console.log('上传进度:', res.progress)
      console.log('已上传数据长度:', res.totalBytesSent)
      console.log('预期上传总长度:', res.totalBytesExpectedToSend)
    })
  })
}
```

### 7.4 大文件处理注意事项

| 注意事项 | 说明 |
|---------|------|
| 内存控制 | 使用流式读写，禁止将整个文件加载到内存 |
| 后台上传 | iOS 使用 `URLSessionConfiguration.background`，Android 使用 WorkManager |
| 文件校验 | 上传完成后比对 MD5 / SHA256 确保完整性 |
| 超时设置 | 大文件上传超时应设为 `文件大小 / 最低带宽 * 2` |
| 格式限制 | 客户端校验文件类型和大小，不依赖服务端 |
| 压缩策略 | 图片上传前压缩（质量 0.7-0.8），视频使用 H.264 转码 |

---

## 8. 联调与调试

### 8.1 接口 Mock 方案

| 工具 | 适用场景 | 特点 |
|------|---------|------|
| Apifox / Postman Mock | 团队协作 | 基于接口文档自动生成 Mock |
| MSW (Mock Service Worker) | Web 前端 | 拦截浏览器请求，不改业务代码 |
| JSON Server | 快速原型 | 零配置 REST API |
| WireMock | 后端联调 | 支持状态模拟、延迟、故障注入 |
| 本地拦截器 | 各平台通用 | 开发环境拦截器返回本地 JSON |

```typescript
// Web — MSW 配置
import { http, HttpResponse } from 'msw'
import { setupWorker } from 'msw/browser'

const handlers = [
  http.get('/api/v1/users/:id', ({ params }) => {
    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        userId: params.id,
        nickName: '测试用户',
        avatarUrl: 'https://placeholder.com/avatar.png',
      },
    })
  }),

  // 模拟网络延迟
  http.get('/api/v1/orders', async () => {
    await delay(2000)
    return HttpResponse.json({
      code: 0,
      data: { list: [], pagination: { total: 0 } },
    })
  }),

  // 模拟错误
  http.post('/api/v1/payments', () => {
    return HttpResponse.json(
      { code: 5001, message: '支付服务暂不可用', data: null },
      { status: 503 }
    )
  }),
]

const worker = setupWorker(...handlers)
worker.start()
```

### 8.2 抓包工具

| 工具 | 平台 | HTTPS 抓包 | 特点 |
|------|------|-----------|------|
| Charles | macOS / Windows | 需安装证书 | 功能全面，Map Local/Remote |
| Proxyman | macOS | 自动信任证书 | 原生 macOS 体验，性能好 |
| mitmproxy | 跨平台 | 需安装证书 | 命令行，可编程 |
| Flipper | 移动端 | 内置 | Facebook 出品，集成调试工具 |

各平台抓包配置要点：

| 平台 | 配置 |
|------|------|
| iOS 模拟器 | 自动使用系统代理，安装 CA 证书即可 |
| iOS 真机 | 设置 → Wi-Fi → 代理 → 手动配置 |
| Android 模拟器 | `emulator -avd <name> -http-proxy <host>:<port>` |
| Android 真机 (API 24+) | 需配置 `network_security_config.xml` 信任用户证书 |
| Flutter | 设置 `HttpClient` 代理或使用 `--proxy` 参数 |
| 微信小程序 | 开发者工具 → 设置 → 代理 → 手动设置 |

```xml
<!-- Android — network_security_config.xml (仅 debug) -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
            <certificates src="system" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

### 8.3 联调检查清单

#### 接口对接前

- [ ] 确认接口文档版本，与后端对齐字段定义
- [ ] 确认认证方式（Token / Cookie / API Key）
- [ ] 确认环境地址（开发 / 测试 / 预发 / 生产）
- [ ] 确认跨域配置（Web 端 CORS）
- [ ] 确认请求 Content-Type（`application/json` / `multipart/form-data`）

#### 联调过程中

- [ ] 检查请求 Header 是否完整（Authorization / Content-Type / Accept）
- [ ] 检查请求参数命名（snake_case vs camelCase）
- [ ] 检查空值处理（`null` / `undefined` / 空字符串）
- [ ] 检查分页参数（page 从 0 还是 1 开始）
- [ ] 检查时间格式（时间戳精度：秒 vs 毫秒）
- [ ] 检查文件上传字段名和格式
- [ ] 验证错误码处理逻辑

#### 联调完成后

- [ ] 弱网环境测试（3G / 高延迟 / 丢包）
- [ ] 无网络环境测试（离线降级是否正常）
- [ ] Token 过期场景测试（自动刷新是否正常）
- [ ] 并发请求测试（重复提交是否防护）
- [ ] 大数据量测试（分页加载、长列表性能）
- [ ] 异常数据测试（空列表、超长文本、特殊字符）

---

## 附录：各平台网络层最小实现模板

### iOS (URLSession + async/await)

```swift
actor APIClient {
    private let session: URLSession
    private let baseURL: URL
    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        d.dateDecodingStrategy = .iso8601
        return d
    }()

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        var request = endpoint.urlRequest(baseURL: baseURL)
        request.setValue("Bearer \(tokenStore.accessToken)", forHTTPHeaderField: "Authorization")

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if http.statusCode == 401 {
            try await refreshTokenAndRetry()
            return try await self.request(endpoint)
        }

        let apiResponse = try decoder.decode(APIResponse<T>.self, from: data)
        guard apiResponse.code == 0 else {
            throw APIError.business(code: apiResponse.code, message: apiResponse.message)
        }
        return apiResponse.data
    }
}
```

### Android (Retrofit + Kotlin Coroutines)

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): ApiResponse<UserDTO>

    @POST("users")
    suspend fun createUser(@Body body: CreateUserRequest): ApiResponse<UserDTO>
}

// 统一响应包装
data class ApiResponse<T>(
    val code: Int,
    val message: String,
    val data: T?
)
```

### Web (Axios)

```typescript
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code !== 0) {
      return Promise.reject(new ApiError(code, message))
    }
    return data
  },
  (error) => {
    if (error.response?.status === 401) {
      return handleTokenRefresh(error)
    }
    return Promise.reject(error)
  }
)
```
