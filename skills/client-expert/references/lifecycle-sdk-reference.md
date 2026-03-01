# 客户端全平台生命周期与SDK速查手册

> 覆盖 iOS / Android / Web / Flutter / 微信小程序五大平台，包含完整生命周期、常用SDK及跨平台能力对照。

---

## 目录

1. [iOS 完整生命周期与常用SDK](#1-ios-完整生命周期与常用sdk)
2. [Android 完整生命周期与常用SDK](#2-android-完整生命周期与常用sdk)
3. [Web 完整生命周期与常用API](#3-web-完整生命周期与常用api)
4. [Flutter 完整生命周期与常用插件](#4-flutter-完整生命周期与常用插件)
5. [微信小程序完整生命周期与常用API](#5-微信小程序完整生命周期与常用api)
6. [各平台SDK能力对照表](#6-各平台sdk能力对照表)

---

## 1. iOS 完整生命周期与常用SDK

### 1.1 App 生命周期

#### UIApplicationDelegate（UIKit）

```
未运行 ──▶ application(_:didFinishLaunchingWithOptions:)
                │
                ▼
           ┌─ 前台活跃 (Active) ◀──────────────────┐
           │    │                                    │
           │    ▼ applicationWillResignActive        │
           │  非活跃 (Inactive)                      │
           │    │                                    │
           │    ▼ applicationDidEnterBackground      │ applicationWillEnterForeground
           │  后台 (Background)  ────────────────────┘
           │    │
           │    ▼ (系统回收)
           └─ 挂起 (Suspended) ──▶ 终止 (Terminated)
```

| 回调方法 | 触发时机 |
|---------|---------|
| `didFinishLaunchingWithOptions` | App 启动完成 |
| `applicationDidBecomeActive` | 进入前台活跃状态 |
| `applicationWillResignActive` | 即将失去焦点（来电、下拉通知栏） |
| `applicationDidEnterBackground` | 已进入后台 |
| `applicationWillEnterForeground` | 即将回到前台 |
| `applicationWillTerminate` | 即将被终止（不保证调用） |

#### SwiftUI App Protocol

```swift
@main
struct MyApp: App {
    @Environment(\.scenePhase) var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            switch newPhase {
            case .active:      break // 前台活跃
            case .inactive:    break // 非活跃
            case .background:  break // 后台
            @unknown default:  break
            }
        }
    }
}
```

### 1.2 UIViewController 生命周期

```
        init / Storyboard 加载
               │
               ▼
         loadView()
               │
               ▼
        viewDidLoad()              ← 只调用一次，初始化UI
               │
               ▼
     viewWillAppear(_:)            ← 每次显示前调用
               │
               ▼
  viewWillLayoutSubviews()
               │
               ▼
  viewDidLayoutSubviews()
               │
               ▼
     viewDidAppear(_:)             ← 已显示，启动动画/定时器
               │
               ▼
   viewWillDisappear(_:)           ← 即将消失，暂停任务
               │
               ▼
   viewDidDisappear(_:)            ← 已消失，释放资源
               │
               ▼
          deinit                   ← 释放，检查循环引用
```

**关键注意事项：**

- `viewDidLoad` 中不要依赖 frame 尺寸，布局相关操作放在 `viewDidLayoutSubviews`
- `viewWillAppear` 每次页面显示都会调用，适合刷新数据
- `deinit` 未调用通常意味着存在循环引用（闭包未用 `[weak self]`）

### 1.3 SwiftUI View 生命周期

```swift
struct ProfileView: View {
    var body: some View {
        Text("Profile")
            .onAppear {
                // 视图出现时（类似 viewWillAppear）
            }
            .onDisappear {
                // 视图消失时
            }
            .task {
                // 异步任务，视图消失自动取消
                await loadProfile()
            }
            .task(id: userId) {
                // userId 变化时重新执行
                await loadProfile()
            }
    }
}
```

| 修饰符 | 用途 |
|-------|------|
| `.onAppear` | 视图出现时执行同步操作 |
| `.onDisappear` | 视图消失时清理 |
| `.task` | 异步任务，自动绑定视图生命周期 |
| `.task(id:)` | 依赖值变化时重新执行异步任务 |
| `.onChange(of:)` | 监听状态变化 |

### 1.4 后台任务

```swift
// BGTaskScheduler（iOS 13+）
import BackgroundTasks

// 注册后台任务（didFinishLaunchingWithOptions 中）
BGTaskScheduler.shared.register(
    forTaskWithIdentifier: "com.app.refresh",
    using: nil
) { task in
    guard let task = task as? BGAppRefreshTask else { return }
    task.expirationHandler = { task.setTaskCompleted(success: false) }
    // 执行后台工作
    task.setTaskCompleted(success: true)
}

// 调度后台任务
func scheduleRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
    try? BGTaskScheduler.shared.submit(request)
}
```

**Background Modes 配置（Info.plist）：**

| Mode | 用途 |
|------|------|
| `audio` | 后台音频播放 |
| `location` | 后台定位 |
| `fetch` | 后台数据拉取 |
| `remote-notification` | 静默推送 |
| `processing` | 后台处理任务 |
| `voip` | VoIP 通话 |

### 1.5 常用 SDK 速查

#### AVFoundation（相机/音视频）

```swift
import AVFoundation

// 相机捕获
let session = AVCaptureSession()
session.sessionPreset = .photo

guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
      let input = try? AVCaptureDeviceInput(device: device) else { return }
session.addInput(input)

let output = AVCapturePhotoOutput()
session.addOutput(output)
session.startRunning()
```

#### CoreLocation（定位）

```swift
import CoreLocation

class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    func start() {
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager,
                         didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        // location.coordinate.latitude / longitude
    }
}
```

#### StoreKit 2（内购）

```swift
import StoreKit

// 获取商品
let products = try await Product.products(for: ["premium_monthly"])

// 发起购买
guard let product = products.first else { return }
let result = try await product.purchase()

switch result {
case .success(let verification):
    let transaction = try checkVerified(verification)
    await transaction.finish()
case .userCancelled: break
case .pending: break
@unknown default: break
}

// 监听交易更新
Task {
    for await result in Transaction.updates {
        let transaction = try checkVerified(result)
        await transaction.finish()
    }
}
```

#### 其他常用 SDK

| SDK | 用途 | 关键类/方法 |
|-----|------|-----------|
| MapKit | 地图 | `MKMapView`, `MKAnnotation` |
| UserNotifications | 推送 | `UNUserNotificationCenter.requestAuthorization()` |
| CoreData | 数据持久化 | `NSManagedObjectContext`, `NSFetchRequest` |
| SwiftData | 数据持久化(新) | `@Model`, `@Query`, `ModelContainer` |
| HealthKit | 健康数据 | `HKHealthStore`, `HKQuantityType` |
| ARKit | 增强现实 | `ARSession`, `ARSCNView` |
| LocalAuthentication | 生物识别 | `LAContext.evaluatePolicy()` |
| CoreBluetooth | 蓝牙 | `CBCentralManager`, `CBPeripheral` |

---

## 2. Android 完整生命周期与常用SDK

### 2.1 Application 生命周期

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // 全局初始化：依赖注入、第三方SDK、全局配置
    }

    override fun onTerminate() {
        // 仅在模拟器中调用，不可依赖
    }

    override fun onLowMemory() {
        // 系统内存不足，释放非必要缓存
    }

    override fun onTrimMemory(level: Int) {
        when (level) {
            TRIM_MEMORY_UI_HIDDEN -> { /* UI 不可见，释放 UI 资源 */ }
            TRIM_MEMORY_RUNNING_LOW -> { /* 内存偏低 */ }
            TRIM_MEMORY_COMPLETE -> { /* 即将被杀 */ }
        }
    }
}
```

### 2.2 Activity 生命周期

```
                    onCreate()
                       │
                       ▼
                    onStart()  ◀──── onRestart()
                       │                 ▲
                       ▼                 │
                   onResume()            │
                       │                 │
                       ▼                 │
                ┌─ 运行中 (Running) ─┐   │
                │                    │   │
                ▼                    │   │
              onPause()              │   │
                │    ▲               │   │
                ▼    │               │   │
              onStop() ──────────────┘───┘
                │
                ▼
            onDestroy()
```

| 回调 | 触发时机 | 典型操作 |
|------|---------|---------|
| `onCreate` | Activity 创建 | 初始化 UI、绑定数据、恢复 savedInstanceState |
| `onStart` | 可见但不可交互 | 注册广播接收器 |
| `onResume` | 可见且可交互 | 启动动画、获取相机 |
| `onPause` | 部分遮挡 | 暂停动画、保存草稿 |
| `onStop` | 完全不可见 | 释放重量级资源 |
| `onDestroy` | 销毁 | 释放所有资源 |
| `onSaveInstanceState` | 系统可能回收前 | 保存临时 UI 状态 |

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyAppTheme { MainScreen() }
        }
    }
}
```

### 2.3 Fragment 生命周期

```
onAttach() → onCreate() → onCreateView() → onViewCreated()
    → onStart() → onResume()
    → onPause() → onStop()
    → onDestroyView() → onDestroy() → onDetach()
```

**关键区别：**

- `onCreateView` 创建视图层级，`onDestroyView` 销毁视图但 Fragment 实例可能保留
- ViewPager2 中 Fragment 视图会被销毁重建，数据应存于 ViewModel
- 使用 `viewLifecycleOwner` 而非 `this` 来观察 LiveData

### 2.4 Jetpack Compose 生命周期

```
进入 Composition ──▶ Recomposition（状态变化时） ──▶ 离开 Composition
```

```kotlin
@Composable
fun ProfileScreen(userId: String) {
    // 首次进入 Composition 时执行，userId 变化时重新执行
    LaunchedEffect(userId) {
        // 协程作用域，自动取消
        loadProfile(userId)
    }

    // 持续存在的协程作用域
    val scope = rememberCoroutineScope()

    // 进入/离开 Composition 的副作用
    DisposableEffect(Unit) {
        val listener = registerListener()
        onDispose {
            listener.unregister()
        }
    }

    // 每次 Recomposition 后执行
    SideEffect {
        analytics.trackScreen("profile")
    }
}
```

| 副作用 API | 用途 |
|-----------|------|
| `LaunchedEffect(key)` | 启动协程，key 变化时重启 |
| `DisposableEffect(key)` | 需要清理的副作用 |
| `SideEffect` | 每次成功 Recomposition 后执行 |
| `rememberCoroutineScope()` | 绑定 Composition 的协程作用域 |
| `rememberUpdatedState(value)` | 在长期副作用中引用最新值 |

### 2.5 四大组件补充

#### Service

```kotlin
// 前台服务（Android 14+ 需声明 foregroundServiceType）
class UploadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = buildNotification()
        startForeground(NOTIFICATION_ID, notification)
        // 执行上传任务
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

#### BroadcastReceiver

```kotlin
// 动态注册
val receiver = object : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // 处理广播
    }
}
ContextCompat.registerReceiver(
    context, receiver,
    IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION),
    ContextCompat.RECEIVER_NOT_EXPORTED
)
```

#### ContentProvider

```kotlin
// 通过 ContentResolver 访问
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    arrayOf(ContactsContract.Contacts.DISPLAY_NAME),
    null, null, null
)
```

### 2.6 后台任务

```kotlin
// WorkManager（推荐的后台任务方案）
class SyncWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        return try {
            syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// 调度任务
val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync", ExistingPeriodicWorkPolicy.KEEP, request
)
```

| 方案 | 适用场景 |
|------|---------|
| WorkManager | 可延迟的可靠后台任务 |
| Foreground Service | 用户可感知的持续任务（音乐播放、导航） |
| AlarmManager | 精确定时任务 |
| CoroutineScope | 与 UI 生命周期绑定的异步操作 |

### 2.7 常用 SDK 速查

#### CameraX（相机）

```kotlin
val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
cameraProviderFuture.addListener({
    val cameraProvider = cameraProviderFuture.get()
    val preview = Preview.Builder().build()
    val imageCapture = ImageCapture.Builder()
        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
        .build()

    cameraProvider.bindToLifecycle(
        lifecycleOwner,
        CameraSelector.DEFAULT_BACK_CAMERA,
        preview, imageCapture
    )
}, ContextCompat.getMainExecutor(context))
```

#### Room（数据库）

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAll(): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

#### 其他常用 SDK

| SDK | 用途 | 关键类/方法 |
|-----|------|-----------|
| Location Services | 定位 | `FusedLocationProviderClient` |
| Maps SDK | 地图 | `GoogleMap`, `MapView` |
| Billing Library | 支付 | `BillingClient`, `ProductDetails` |
| FCM | 推送 | `FirebaseMessagingService` |
| ML Kit | 机器学习 | `BarcodeScanning`, `TextRecognition` |
| Biometric | 生物识别 | `BiometricPrompt` |
| Bluetooth LE | 蓝牙 | `BluetoothLeScanner` |

---

## 3. Web 完整生命周期与常用API

### 3.1 页面加载生命周期

```
解析 HTML
    │
    ▼
DOMContentLoaded          ← DOM 树构建完成（图片/样式可能未加载）
    │
    ▼
load                      ← 所有资源加载完成
    │
    ▼
(用户交互阶段)
    │
    ▼
beforeunload              ← 离开前确认（可阻止关闭）
    │
    ▼
unload                    ← 页面卸载（不可靠，用 visibilitychange 替代）
```

```javascript
// 推荐：使用 visibilitychange 替代 unload
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    // 页面不可见，保存状态、发送 beacon
    navigator.sendBeacon('/analytics', JSON.stringify(data))
  }
})

// 性能监控
window.addEventListener('load', () => {
  const timing = performance.getEntriesByType('navigation')[0]
  // timing.domContentLoadedEventEnd - timing.startTime
})
```

### 3.2 Vue 3 组件生命周期

```
setup()                        ← Composition API 入口
    │
    ▼
onBeforeMount()                ← 挂载前
    │
    ▼
onMounted()                    ← 挂载完成，可访问 DOM
    │
    ▼
┌─ onBeforeUpdate()            ← 响应式数据变化，更新前
│       │
│       ▼
└─ onUpdated()                 ← DOM 更新完成
    │
    ▼
onBeforeUnmount()              ← 卸载前，清理定时器/事件
    │
    ▼
onUnmounted()                  ← 卸载完成
```

```typescript
import { ref, onMounted, onUnmounted, watch } from 'vue'

export function useWebSocket(url: string) {
  const data = ref<string | null>(null)
  let ws: WebSocket | null = null

  onMounted(() => {
    ws = new WebSocket(url)
    ws.onmessage = (event) => {
      data.value = event.data
    }
  })

  onUnmounted(() => {
    ws?.close()
    ws = null
  })

  return { data }
}
```

| 钩子 | Options API 等价 | 用途 |
|------|-----------------|------|
| `onBeforeMount` | `beforeMount` | 挂载前最后的修改机会 |
| `onMounted` | `mounted` | DOM 操作、第三方库初始化 |
| `onBeforeUpdate` | `beforeUpdate` | 更新前读取 DOM 状态 |
| `onUpdated` | `updated` | 更新后的 DOM 操作 |
| `onBeforeUnmount` | `beforeUnmount` | 清理副作用 |
| `onUnmounted` | `unmounted` | 最终清理 |
| `onActivated` | `activated` | `<KeepAlive>` 组件激活 |
| `onDeactivated` | `deactivated` | `<KeepAlive>` 组件停用 |

### 3.3 React 组件生命周期

```
挂载 (Mount)
    │  函数组件执行 → 返回 JSX → DOM 更新 → useEffect 执行
    │
更新 (Update)
    │  状态/props 变化 → 函数组件重新执行 → DOM 更新
    │  → useEffect cleanup → useEffect 执行
    │
卸载 (Unmount)
    │  useEffect cleanup 执行
```

```tsx
import { useState, useEffect, useRef, useCallback } from 'react'

function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    // 挂载 & userId 变化时执行
    abortRef.current = new AbortController()
    fetchUser(userId, abortRef.current.signal)
      .then(setUser)
      .catch(() => {})

    return () => {
      // 清理：取消请求
      abortRef.current?.abort()
    }
  }, [userId])

  useEffect(() => {
    // 仅挂载时执行一次
    const handler = () => { /* ... */ }
    window.addEventListener('resize', handler)
    return () => window.removeEventListener('resize', handler)
  }, [])

  return user ? <div>{user.name}</div> : <div>Loading...</div>
}
```

| Hook | 用途 |
|------|------|
| `useEffect(fn, [])` | 挂载时执行一次（componentDidMount） |
| `useEffect(fn, [dep])` | 依赖变化时执行 |
| `useEffect` return | 清理函数（componentWillUnmount） |
| `useLayoutEffect` | DOM 更新后同步执行（测量布局） |
| `useMemo` | 缓存计算结果 |
| `useCallback` | 缓存函数引用 |
| `useRef` | 跨渲染持久引用 |

### 3.4 Service Worker 生命周期

```
注册 (register)
    │
    ▼
安装 (install)          ← 缓存静态资源
    │
    ▼
等待 (waiting)          ← 旧 SW 仍在控制页面
    │
    ▼
激活 (activate)         ← 清理旧缓存
    │
    ▼
控制页面 (controlling)  ← 拦截 fetch 请求
    │
    ▼
冗余 (redundant)        ← 被新版本替换
```

```javascript
// 注册
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}

// sw.js
const CACHE_NAME = 'v1'

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      cache.addAll(['/index.html', '/styles.css', '/app.js'])
    )
  )
  self.skipWaiting() // 跳过等待，立即激活
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  )
  self.clients.claim() // 立即控制所有页面
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  )
})
```

### 3.5 常用 Web API 速查

| API | 用途 | 示例 |
|-----|------|------|
| Fetch API | 网络请求 | `fetch(url, { signal })` |
| WebSocket | 双向通信 | `new WebSocket('wss://...')` |
| localStorage | 同步键值存储(5MB) | `localStorage.setItem(k, v)` |
| sessionStorage | 会话级存储 | `sessionStorage.getItem(k)` |
| IndexedDB | 大容量结构化存储 | `indexedDB.open('db', 1)` |
| Geolocation | 定位 | `navigator.geolocation.getCurrentPosition()` |
| Notification | 通知 | `new Notification('title', { body })` |
| MediaDevices | 相机/麦克风 | `navigator.mediaDevices.getUserMedia()` |
| IntersectionObserver | 元素可见性检测 | 懒加载、无限滚动 |
| ResizeObserver | 元素尺寸变化 | 响应式组件 |
| Web Workers | 后台线程计算 | `new Worker('worker.js')` |
| Broadcast Channel | 跨标签页通信 | `new BroadcastChannel('ch')` |
| Web Crypto | 加密 | `crypto.subtle.digest()` |
| Clipboard API | 剪贴板 | `navigator.clipboard.writeText()` |

---

## 4. Flutter 完整生命周期与常用插件

### 4.1 App 生命周期

```
                  ┌──────────────┐
                  │   resumed    │ ← 前台可见可交互
                  └──────┬───────┘
                         │
              ┌──────────▼──────────┐
              │     inactive        │ ← 失去焦点（来电、系统对话框）
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │      hidden         │ ← 不可见（Flutter 3.13+）
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │      paused         │ ← 后台
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │     detached        │ ← 引擎仍运行但无视图
              └──────────────────────┘
```

```dart
class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:   // 回到前台
      case AppLifecycleState.inactive:  // 失去焦点
      case AppLifecycleState.hidden:    // 不可见
      case AppLifecycleState.paused:    // 后台
      case AppLifecycleState.detached:  // 分离
    }
  }

  @override
  Widget build(BuildContext context) => const MaterialApp(home: HomeScreen());
}
```
```
```
```
