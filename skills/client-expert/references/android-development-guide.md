# Android 开发实践指南

> 适用于 Kotlin 1.9+、Jetpack Compose、Android SDK 34+ 的现代 Android 开发参考手册。

---

## 1. Android 开发技术栈总览

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 语言 | Kotlin 1.9+ | 协程、Flow、密封类、值类 |
| UI 框架 | Jetpack Compose (BOM 2024+) | 声明式 UI，替代 XML 布局 |
| 架构 | MVVM + Clean Architecture | ViewModel + StateFlow + UseCases |
| DI | Hilt (Dagger 基础) | 编译期依赖注入 |
| 网络 | OkHttp + Retrofit + Moshi | 类型安全的 HTTP 客户端 |
| 数据库 | Room | SQLite 抽象层，支持 Flow |
| 导航 | Jetpack Navigation Compose | 类型安全导航 (Safe Args) |
| 异步 | Kotlin Coroutines + Flow | 结构化并发 |
| 图片 | Coil | Kotlin-first 图片加载库 |
| 测试 | JUnit5 + Turbine + Espresso | 单元测试 + UI 测试 |

### Kotlin 关键特性速查

```kotlin
// 密封接口 — 建模 UI 状态
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

// 值类 — 零开销类型包装
@JvmInline
value class UserId(val value: String)

// 协程 + Flow
fun fetchUsers(): Flow<List<User>> = flow {
    val users = apiService.getUsers()
    emit(users)
}.flowOn(Dispatchers.IO)
```

---

## 2. 项目工程配置

### 2.1 Gradle 版本目录 (libs.versions.toml)

```toml
[versions]
kotlin = "1.9.22"
agp = "8.3.0"
compose-bom = "2024.02.00"
hilt = "2.50"
room = "2.6.1"
retrofit = "2.9.0"
coroutines = "1.8.0"
coil = "2.6.0"
navigation = "2.7.7"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version = "1.9.22-1.0.17" }
```

### 2.2 Build Variants 与签名配置

```kotlin
// app/build.gradle.kts
android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
            buildConfigField("String", "BASE_URL", "\"https://api-dev.example.com\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            buildConfigField("String", "BASE_URL", "\"https://api.example.com\"")
        }
    }

    // 多渠道打包
    flavorDimensions += "channel"
    productFlavors {
        create("googleplay") { dimension = "channel" }
        create("huawei") { dimension = "channel" }
        create("xiaomi") { dimension = "channel" }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }
}
```

### 2.3 项目目录结构 (按功能模块)

```
app/src/main/kotlin/com/example/app/
├── di/                     # Hilt 模块
│   ├── NetworkModule.kt
│   ├── DatabaseModule.kt
│   └── RepositoryModule.kt
├── data/
│   ├── remote/             # API 接口与 DTO
│   │   ├── api/
│   │   ├── dto/
│   │   └── interceptor/
│   ├── local/              # Room 数据库
│   │   ├── dao/
│   │   ├── entity/
│   │   └── AppDatabase.kt
│   └── repository/         # Repository 实现
├── domain/
│   ├── model/              # 领域模型
│   ├── repository/         # Repository 接口
│   └── usecase/            # 用例
├── ui/
│   ├── theme/              # Compose 主题
│   ├── component/          # 通用组件
│   ├── navigation/         # 导航图
│   └── feature/            # 功能页面
│       ├── home/
│       ├── profile/
│       └── settings/
└── util/                   # 工具类
```

---

## 3. Jetpack Compose vs XML 布局选型

| 维度 | Jetpack Compose | XML 布局 |
|------|----------------|----------|
| 开发效率 | 高，声明式 + 实时预览 | 中等，需要 findViewById/ViewBinding |
| 学习曲线 | 需要理解 Composition | 传统 Android 开发者熟悉 |
| 性能 | 智能重组，跳过未变化节点 | 需手动优化 View 层级 |
| 互操作 | AndroidView 嵌入 XML 组件 | ComposeView 嵌入 Compose |
| 推荐场景 | 新项目首选 | 维护老项目、复杂自定义 View |

### 选型建议

- 新项目：100% Compose
- 老项目迁移：逐页面迁移，使用 `ComposeView` 桥接
- 复杂自定义绘制：Compose Canvas 或 `AndroidView` 包装

### Compose 基础模板

```kotlin
@Composable
fun UserCard(
    user: User,
    onTap: (UserId) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable { onTap(user.id) },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "用户头像",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(text = user.name, style = MaterialTheme.typography.titleMedium)
                Text(text = user.email, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
```

---

## 4. MVVM + Clean Architecture 实现

### 4.1 领域层 (Domain)

```kotlin
// domain/model/User.kt
data class User(
    val id: UserId,
    val name: String,
    val email: String,
    val avatarUrl: String
)

// domain/repository/UserRepository.kt
interface UserRepository {
    fun getUsers(): Flow<List<User>>
    suspend fun getUserById(id: UserId): User
    suspend fun updateUser(user: User): User
}

// domain/usecase/GetUsersUseCase.kt
class GetUsersUseCase @Inject constructor(
    private val repository: UserRepository
) {
    operator fun invoke(): Flow<UiState<List<User>>> = flow {
        emit(UiState.Loading)
        repository.getUsers()
            .catch { emit(UiState.Error(it.message ?: "未知错误")) }
            .collect { emit(UiState.Success(it)) }
    }
}
```

### 4.2 数据层 (Data)

```kotlin
// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override fun getUsers(): Flow<List<User>> =
        dao.observeAll()
            .map { entities -> entities.map { it.toDomain() } }
            .onStart {
                try {
                    val remote = api.getUsers()
                    dao.upsertAll(remote.map { it.toEntity() })
                } catch (e: Exception) {
                    // 网络失败时使用本地缓存
                }
            }

    override suspend fun getUserById(id: UserId): User =
        dao.getById(id.value)?.toDomain()
            ?: api.getUser(id.value).toDomain()

    override suspend fun updateUser(user: User): User {
        val response = api.updateUser(user.id.value, user.toRequest())
        dao.upsert(response.toEntity())
        return response.toDomain()
    }
}
```
### 4.3 表现层 (Presentation)

```kotlin
// ui/feature/home/HomeViewModel.kt
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getUsers: GetUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<User>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<User>>> = _uiState.asStateFlow()

    init { loadUsers() }

    fun loadUsers() {
        viewModelScope.launch {
            getUsers().collect { _uiState.value = it }
        }
    }
}

// ui/feature/home/HomeScreen.kt
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel(),
    onNavigateToDetail: (UserId) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Error -> ErrorMessage(state.message, onRetry = viewModel::loadUsers)
        is UiState.Success -> UserList(users = state.data, onTap = onNavigateToDetail)
    }
}
```

### 4.4 Hilt 依赖注入配置

```kotlin
// di/NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(authInterceptor: AuthInterceptor): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) Level.BODY else Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(client)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi =
        retrofit.create(UserApi::class.java)
}

// di/DatabaseModule.kt
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .addMigrations(MIGRATION_1_2)
            .build()

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}
```

---

## 5. 网络层封装

### 5.1 Retrofit API 定义

```kotlin
interface UserApi {
    @GET("v1/users")
    suspend fun getUsers(): List<UserDto>

    @GET("v1/users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @PUT("v1/users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body body: UpdateUserRequest): UserDto

    @Multipart
    @POST("v1/users/{id}/avatar")
    suspend fun uploadAvatar(
        @Path("id") id: String,
        @Part file: MultipartBody.Part
    ): UserDto
}
```

### 5.2 统一响应处理

```kotlin
// data/remote/ApiResult.kt
sealed interface ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>
    data class Failure(val code: Int, val message: String) : ApiResult<Nothing>
    data class NetworkError(val exception: Throwable) : ApiResult<Nothing>
}

suspend fun <T> safeApiCall(block: suspend () -> T): ApiResult<T> =
    try {
        ApiResult.Success(block())
    } catch (e: HttpException) {
        val errorBody = e.response()?.errorBody()?.string()
        ApiResult.Failure(e.code(), errorBody ?: "服务器错误")
    } catch (e: IOException) {
        ApiResult.NetworkError(e)
    }
```

### 5.3 常用拦截器

```kotlin
// Token 自动刷新拦截器
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenManager.getAccessToken()
        val request = chain.request().newBuilder()
            .apply { token?.let { header("Authorization", "Bearer $it") } }
            .build()

        val response = chain.proceed(request)

        if (response.code == 401) {
            synchronized(this) {
                val newToken = tokenManager.refreshTokenBlocking()
                if (newToken != null) {
                    val retryRequest = request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                    response.close()
                    return chain.proceed(retryRequest)
                }
            }
        }
        return response
    }
}

// 通用请求头拦截器
class CommonHeaderInterceptor @Inject constructor(
    @ApplicationContext private val context: Context
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .header("X-Platform", "Android")
            .header("X-App-Version", BuildConfig.VERSION_NAME)
            .header("X-Device-Id", getDeviceId(context))
            .build()
        return chain.proceed(request)
    }
}
```

---

## 6. 数据持久化

### 6.1 DataStore (替代 SharedPreferences)

```kotlin
// 创建 DataStore
val Context.settingsDataStore by preferencesDataStore(name = "settings")

// 封装读写
class SettingsRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.settingsDataStore

    private object Keys {
        val DARK_MODE = booleanPreferencesKey("dark_mode")
        val LANGUAGE = stringPreferencesKey("language")
        val FONT_SIZE = intPreferencesKey("font_size")
    }

    val darkMode: Flow<Boolean> = dataStore.data
        .map { it[Keys.DARK_MODE] ?: false }

    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { it[Keys.DARK_MODE] = enabled }
    }

    val language: Flow<String> = dataStore.data
        .map { it[Keys.LANGUAGE] ?: "zh-CN" }
}
```
### 6.2 Room 数据库

```kotlin
// data/local/entity/UserEntity.kt
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String,
    val updatedAt: Long = System.currentTimeMillis()
)

// data/local/dao/UserDao.kt
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY name ASC")
    fun observeAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: String): UserEntity?

    @Upsert
    suspend fun upsert(user: UserEntity)

    @Upsert
    suspend fun upsertAll(users: List<UserEntity>)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteById(id: String)
}

// data/local/AppDatabase.kt
@Database(entities = [UserEntity::class], version = 2, exportSchema = true)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// 数据库迁移
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE users ADD COLUMN avatarUrl TEXT NOT NULL DEFAULT ''")
    }
}
```

### 6.3 加密存储

```kotlin
// 使用 EncryptedSharedPreferences 存储敏感数据
class SecureStorage @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val prefs: SharedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "secure_prefs",
            MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun saveToken(token: String) { prefs.edit { putString("access_token", token) } }
    fun getToken(): String? = prefs.getString("access_token", null)
    fun clearAll() { prefs.edit { clear() } }
}
```

---

## 7. 导航方案

### 7.1 Jetpack Navigation Compose

```kotlin
// ui/navigation/AppNavigation.kt

// 类型安全路由定义
@Serializable sealed interface Route {
    @Serializable data object Home : Route
    @Serializable data object Profile : Route
    @Serializable data class UserDetail(val userId: String) : Route
    @Serializable data object Settings : Route
}

@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = Route.Home) {

        composable<Route.Home> {
            HomeScreen(
                onNavigateToDetail = { userId ->
                    navController.navigate(Route.UserDetail(userId.value))
                }
            )
        }

        composable<Route.UserDetail> { backStackEntry ->
            val route = backStackEntry.toRoute<Route.UserDetail>()
            UserDetailScreen(userId = UserId(route.userId))
        }

        composable<Route.Profile> { ProfileScreen() }
        composable<Route.Settings> { SettingsScreen() }
    }
}
```

### 7.2 底部导航栏

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val currentRoute by navController.currentBackStackEntryAsState()

    val tabs = listOf(
        BottomTab("首页", Icons.Default.Home, Route.Home),
        BottomTab("我的", Icons.Default.Person, Route.Profile),
        BottomTab("设置", Icons.Default.Settings, Route.Settings),
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                tabs.forEach { tab ->
                    NavigationBarItem(
                        selected = currentRoute?.destination?.route == tab.route::class.qualifiedName,
                        onClick = {
                            navController.navigate(tab.route) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(tab.icon, contentDescription = tab.label) },
                        label = { Text(tab.label) }
                    )
                }
            }
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding)) {
            AppNavHost(navController)
        }
    }
}
```

### 7.3 Deep Link 配置

```xml
<!-- AndroidManifest.xml -->
<activity android:name=".MainActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="example.com" android:pathPrefix="/user/" />
    </intent-filter>
</activity>
```

```kotlin
// 在 Navigation 中处理 Deep Link
composable<Route.UserDetail>(
    deepLinks = listOf(
        navDeepLink<Route.UserDetail>(basePath = "https://example.com/user")
    )
) { backStackEntry ->
    val route = backStackEntry.toRoute<Route.UserDetail>()
    UserDetailScreen(userId = UserId(route.userId))
}
```

---

## 8. 常用 SDK 集成指南

### 8.1 推送通知 (FCM + 厂商推送)

```kotlin
// FCM 基础集成
class AppFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        // 上报 token 到服务端
        CoroutineScope(Dispatchers.IO).launch {
            try {
                apiService.registerPushToken(PushTokenRequest(token = token, platform = "fcm"))
            } catch (e: Exception) {
                // 存储到本地，下次启动重试
            }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val notification = message.notification
        val data = message.data

        showNotification(
            title = notification?.title ?: data["title"] ?: "",
            body = notification?.body ?: data["body"] ?: "",
            data = data
        )
    }

    private fun showNotification(title: String, body: String, data: Map<String, String>) {
        val channelId = "default"
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            data.forEach { (k, v) -> putExtra(k, v) }
        }
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val builder = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)

        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(channelId, "默认通知", NotificationManager.IMPORTANCE_HIGH)
            )
        }
        manager.notify(System.currentTimeMillis().toInt(), builder.build())
    }
}
```
**国内厂商推送策略：**

| 厂商 | SDK | 适用场景 |
|------|-----|---------|
| 华为 HMS Push | `com.huawei.hms:push` | 华为/荣耀设备 |
| 小米 MiPush | 小米推送 SDK | 小米/Redmi 设备 |
| OPPO Push | OPPO 推送 SDK | OPPO/OnePlus/Realme |
| vivo Push | vivo 推送 SDK | vivo/iQOO 设备 |

> 建议使用统一推送聚合方案 (如个推、极光) 简化多厂商适配。

### 8.2 CameraX 相机集成

```kotlin
@Composable
fun CameraPreview(
    onImageCaptured: (Uri) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }

    AndroidView(
        factory = { ctx ->
            PreviewView(ctx).also { previewView ->
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    val imageCapture = ImageCapture.Builder()
                        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                        .build()

                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        CameraSelector.DEFAULT_BACK_CAMERA,
                        preview,
                        imageCapture
                    )
                }, ContextCompat.getMainExecutor(ctx))
            }
        },
        modifier = modifier
    )
}
```

### 8.3 支付集成要点

| 支付渠道 | 关键步骤 | 注意事项 |
|---------|---------|---------|
| Google Play Billing | BillingClient -> queryProductDetails -> launchBillingFlow -> 验证 | 服务端验证购买凭证 |
| 支付宝 | 服务端生成订单串 -> 客户端调起支付 -> 回调验证 | 不要在客户端生成签名 |
| 微信支付 | 服务端预下单 -> 客户端调起支付 -> 回调验证 | 需注册 WXPayEntryActivity |

> 核心原则：支付签名和订单验证必须在服务端完成，客户端仅负责调起和展示。

---

## 9. 性能优化

### 9.1 启动优化

```kotlin
// 使用 App Startup 库延迟初始化
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.init(context)
    }
    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// Baseline Profile 加速启动 (build.gradle.kts)
// 添加 androidx.benchmark:benchmark-macro-junit4 依赖
// 编写 BaselineProfileGenerator 生成 baseline-prof.txt
```

**启动优化检查清单：**

| 优化项 | 方法 | 预期收益 |
|-------|------|---------|
| 延迟初始化 | App Startup / lazy | 减少 Application.onCreate 耗时 |
| Baseline Profile | Macrobenchmark 生成 | 首次启动提速 30%+ |
| 减少主线程 IO | 移至协程 Dispatchers.IO | 避免 ANR |
| SplashScreen API | 使用 core-splashscreen | 统一启动体验 |
| 减少布局层级 | Compose 扁平化布局 | 减少测量/布局耗时 |

### 9.2 列表性能 (LazyColumn)

```kotlin
@Composable
fun UserList(users: List<User>, onTap: (UserId) -> Unit) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            items = users,
            key = { it.id.value }  // 必须提供 key，避免不必要的重组
        ) { user ->
            UserCard(user = user, onTap = onTap)
        }
    }
}

// 避免在 LazyColumn item 中创建新对象
// WRONG: modifier = Modifier.padding(16.dp) 每次重组都创建新 Modifier
// CORRECT: 提取为常量或使用 remember
```

**Compose 性能要点：**

- 使用 `key` 参数标识列表项，避免全量重组
- 使用 `derivedStateOf` 减少不必要的重组
- 使用 `remember` 缓存计算结果
- 避免在 Composable 中执行耗时操作
- 使用 `Modifier.drawBehind` 替代 `Box` + `Background` 减少节点

### 9.3 内存泄漏检测 (LeakCanary)

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.13")
}
// 无需额外代码，debug 构建自动启用

// 常见泄漏场景及修复
// 1. Activity/Fragment 引用泄漏 -> 使用 WeakReference 或 ViewModel
// 2. 协程未取消 -> 使用 viewModelScope / lifecycleScope
// 3. 匿名内部类持有外部引用 -> 使用静态内部类 + WeakReference
// 4. Handler 泄漏 -> 使用 lifecycleScope.launch 替代
```

### 9.4 Android Profiler 使用要点

| 工具 | 用途 | 关注指标 |
|------|------|---------|
| CPU Profiler | 方法耗时分析 | 主线程阻塞、热点方法 |
| Memory Profiler | 内存分配追踪 | 内存抖动、泄漏对象 |
| Network Profiler | 网络请求监控 | 请求耗时、数据量 |
| Energy Profiler | 电量消耗分析 | WakeLock、频繁定位 |
| Layout Inspector | Compose 布局检查 | 重组次数、布局层级 |

---

## 10. 安全实践

### 10.1 ProGuard / R8 混淆配置

```proguard
# proguard-rules.pro

# 保留 Retrofit 接口
-keep,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# 保留 Moshi 数据类
-keep class com.example.app.data.remote.dto.** { *; }

# 保留 Room 实体
-keep class com.example.app.data.local.entity.** { *; }

# 保留 Hilt 生成代码
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.android.internal.managers.ViewComponentManager$FragmentContextWrapper { *; }

# 移除日志
-assumenosideeffects class android.util.Log {
    public static int d(...);
    public static int v(...);
    public static int i(...);
}
```

### 10.2 数据加密

```kotlin
// AES 加密工具
object CryptoUtil {
    private const val TRANSFORMATION = "AES/GCM/NoPadding"
    private const val KEY_ALIAS = "app_master_key"

    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        keyStore.getEntry(KEY_ALIAS, null)?.let {
            return (it as KeyStore.SecretKeyEntry).secretKey
        }
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        keyGenerator.init(
            KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()
        )
        return keyGenerator.generateKey()
    }

    fun encrypt(plainText: String): Pair<ByteArray, ByteArray> {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        return cipher.iv to cipher.doFinal(plainText.toByteArray(Charsets.UTF_8))
    }

    fun decrypt(iv: ByteArray, cipherText: ByteArray): String {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), GCMParameterSpec(128, iv))
        return String(cipher.doFinal(cipherText), Charsets.UTF_8)
    }
}
```

### 10.3 运行时权限管理

```kotlin
// Compose 中的权限请求
@Composable
fun CameraFeature() {
    val cameraPermissionState = rememberPermissionState(Manifest.permission.CAMERA)

    when {
        cameraPermissionState.status.isGranted -> {
            CameraPreview(onImageCaptured = { /* 处理图片 */ })
        }
        cameraPermissionState.status.shouldShowRationale -> {
            PermissionRationale(
                message = "需要相机权限来拍照",
                onRequest = { cameraPermissionState.launchPermissionRequest() }
            )
        }
        else -> {
            Button(onClick = { cameraPermissionState.launchPermissionRequest() }) {
                Text("授权相机")
            }
        }
    }
}

// 多权限请求
@Composable
fun LocationFeature() {
    val permissionState = rememberMultiplePermissionsState(
        listOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )

    LaunchedEffect(Unit) {
        if (!permissionState.allPermissionsGranted) {
            permissionState.launchMultiplePermissionRequest()
        }
    }
}
```

### 10.4 安全检查清单

| 检查项 | 实现方式 | 优先级 |
|-------|---------|-------|
| 网络通信加密 | 强制 HTTPS + Certificate Pinning | P0 |
| 敏感数据存储 | EncryptedSharedPreferences / AndroidKeyStore | P0 |
| 代码混淆 | R8 + 自定义 ProGuard 规则 | P0 |
| 防止截屏 | `FLAG_SECURE` 标志 | P1 |
| Root 检测 | SafetyNet / Play Integrity API | P1 |
| 日志清理 | Release 构建移除所有日志 | P1 |
| WebView 安全 | 禁用 JS 接口、限制 URL 加载 | P1 |
| 证书固定 | OkHttp CertificatePinner | P2 |

---

## 11. 发布流程

### 11.1 签名与构建

```bash
# 生成签名密钥 (首次)
keytool -genkey -v -keystore release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias release

# 构建 Release APK
./gradlew assembleRelease

# 构建 AAB (Google Play 要求)
./gradlew bundleRelease

# 多渠道打包
./gradlew assembleGoogleplayRelease assembleHuaweiRelease assembleXiaomiRelease
```

### 11.2 CI/CD 配置 (GitHub Actions)

```yaml
# .github/workflows/android-release.yml
name: Android Release
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: gradle/actions/setup-gradle@v3

      - name: Build Release AAB
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > app/release.jks
          ./gradlew bundleRelease

      - name: Upload to Google Play
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/googleplayRelease/app-googleplay-release.aab
          track: internal
```

### 11.3 发布检查清单

| 阶段 | 检查项 | 说明 |
|------|-------|------|
| 构建前 | 版本号递增 | versionCode + versionName |
| 构建前 | 移除调试代码 | 日志、测试入口、Mock 数据 |
| 构建前 | ProGuard 规则验证 | 确保关键类未被混淆 |
| 构建中 | 签名正确性 | 使用正式签名密钥 |
| 构建后 | APK/AAB 大小检查 | 关注体积异常增长 |
| 构建后 | 多设备测试 | 覆盖主流分辨率和 API 级别 |
| 发布 | 灰度发布 | Google Play 分阶段发布 (5% -> 20% -> 100%) |
| 发布 | 崩溃监控 | Firebase Crashlytics 实时监控 |
| 发布 | 性能监控 | Firebase Performance 关注启动时间和 ANR 率 |

### 11.4 国内应用市场发布要点

| 市场 | 特殊要求 | 备注 |
|------|---------|------|
| 华为应用市场 | HMS Core 集成、隐私声明 | 需要软著证书 |
| 小米应用商店 | 应用加固、隐私合规 | 需要 ICP 备案 |
| OPPO 软件商店 | 64 位支持、目标 API 要求 | 审核周期 1-3 天 |
| vivo 应用商店 | 隐私政策弹窗、权限说明 | 需要企业开发者认证 |
| 应用宝 | 应用加固、广告合规 | 腾讯开放平台注册 |

> 国内市场通用要求：软件著作权证书、ICP 备案号、隐私政策 URL、个人信息收集清单。
```
