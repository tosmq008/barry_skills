# 跨平台客户端架构设计指南

> 适用平台：iOS / Android / Web / Flutter / 微信小程序

---

## 目录

1. [跨平台架构设计原则](#1-跨平台架构设计原则)
2. [多端代码复用策略](#2-多端代码复用策略)
3. [平台差异处理](#3-平台差异处理)
4. [混合开发架构](#4-混合开发架构)
5. [模块化与组件化架构](#5-模块化与组件化架构)
6. [持续集成与多端构建](#6-持续集成与多端构建)

---

## 1. 跨平台架构设计原则

### 1.1 分层架构通用模型

无论目标平台是什么，客户端架构都应遵循统一的四层模型。各层职责清晰、边界明确，上层依赖下层，禁止反向依赖。

```
┌─────────────────────────────────────────────┐
│              展示层 (Presentation)            │
│  UI组件 / 页面路由 / 动画 / 主题适配          │
├─────────────────────────────────────────────┤
│              业务层 (Domain)                  │
│  用例(UseCase) / 业务规则 / 状态管理          │
├─────────────────────────────────────────────┤
│              数据层 (Data)                    │
│  Repository / 网络请求 / 本地缓存 / 数据映射  │
├─────────────────────────────────────────────┤
│              基础层 (Infrastructure)          │
│  日志 / 监控 / 安全 / 平台桥接 / 工具库       │
└─────────────────────────────────────────────┘
```

各层核心职责：

| 层级 | 职责 | 关键约束 |
|------|------|----------|
| 展示层 | 渲染UI、响应用户交互、管理页面生命周期 | 不包含业务逻辑，仅做数据绑定与事件分发 |
| 业务层 | 封装业务规则、编排数据流、管理应用状态 | 不依赖任何平台API，纯逻辑实现 |
| 数据层 | 统一数据访问接口、处理缓存策略、数据格式转换 | 通过Repository模式隔离数据源 |
| 基础层 | 提供跨平台基础能力、封装平台差异 | 通过接口抽象屏蔽平台实现细节 |

### 1.2 各平台架构模式对照

不同平台有各自主流的架构模式，但核心思想一致：将UI与业务逻辑分离，实现单向数据流。

| 平台 | 主流模式 | 状态管理 | 数据流方向 |
|------|----------|----------|------------|
| iOS (SwiftUI) | MVVM | @Observable / Combine | View ← ViewModel ← Model |
| iOS (UIKit) | MVVM-C / VIPER | Combine / RxSwift | View → Coordinator → ViewModel |
| Android (Compose) | MVI | StateFlow / Compose State | Intent → Reducer → State → UI |
| Android (View) | MVVM | LiveData / StateFlow | View ← ViewModel ← Repository |
| Flutter | BLoC / Riverpod | Stream / StateNotifier | Event → BLoC → State → Widget |
| Web (Vue 3) | Composition API | ref / reactive / Pinia | Template ← Composable ← Store |
| Web (React) | Hooks + Context | useState / Zustand / Redux | JSX ← Hook ← Store |
| 微信小程序 | 类MVVM | setData / MobX | WXML ← Page/Component ← Store |

架构模式统一映射关系：

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   iOS MVVM   │ Android MVI  │  Flutter BLoC │  Vue Comp.   │
├──────────────┼──────────────┼──────────────┼──────────────┤
│    View      │   Screen     │   Widget     │  Template    │  ← 展示
│  ViewModel   │   ViewModel  │    BLoC      │  Composable  │  ← 状态管理
│   UseCase    │   UseCase    │   UseCase    │  UseCase     │  ← 业务逻辑
│  Repository  │  Repository  │  Repository  │  Repository  │  ← 数据访问
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### 1.3 依赖注入在各平台的实现

依赖注入(DI)是实现层间解耦的关键手段。各平台推荐方案如下：

| 平台 | DI方案 | 注入方式 | 示例 |
|------|--------|----------|------|
| iOS | Swinject / Factory | 构造器注入 + 属性包装器 | `@Injected var repo: UserRepo` |
| Android | Hilt (Dagger) | 注解注入 | `@Inject constructor(val repo: UserRepo)` |
| Flutter | get_it + injectable | 服务定位器 + 代码生成 | `getIt<UserRepo>()` |
| Web (Vue) | provide/inject | 组合式API注入 | `const repo = inject<UserRepo>('userRepo')` |
| Web (React) | Context + DI容器 | Provider模式 | `const repo = useInject(UserRepo)` |
| 小程序 | 手动注入 / 简易容器 | 构造器传参 | `new PageLogic({ repo })` |

依赖注入的核心原则：

- 面向接口编程，不依赖具体实现
- 生命周期管理：区分单例(Singleton)、作用域(Scoped)、瞬态(Transient)
- 测试时可替换为Mock实现
- 避免服务定位器反模式（优先构造器注入）

```
// 跨平台统一的依赖注册伪代码
Container.register<AuthRepository>(
  interface: AuthRepository,
  factory: () => AuthRepositoryImpl(
    api: Container.resolve<AuthApi>(),
    cache: Container.resolve<TokenCache>()
  ),
  lifecycle: Lifecycle.singleton
)
```

---

## 2. 多端代码复用策略

### 2.1 Design Token 统一

Design Token 是跨平台视觉一致性的基石。通过统一的 Token 定义，各平台自动生成对应的样式代码。

Token 分层体系：

```
┌─────────────────────────────────────────────┐
│          语义Token (Semantic)                │
│  color-primary / spacing-page / radius-card  │
├─────────────────────────────────────────────┤
│          基础Token (Primitive)               │
│  blue-500 / 16px / 8px                       │
├─────────────────────────────────────────────┤
│          原始值 (Raw Value)                   │
│  #3B82F6 / 16 / 8                            │
└─────────────────────────────────────────────┘
```

Token 定义源文件（JSON格式，作为单一数据源）：

```json
{
  "color": {
    "primary": { "value": "#3B82F6", "type": "color" },
    "secondary": { "value": "#6366F1", "type": "color" },
    "surface": { "value": "#FFFFFF", "type": "color" },
    "on-surface": { "value": "#1F2937", "type": "color" },
    "error": { "value": "#EF4444", "type": "color" }
  },
  "spacing": {
    "xs": { "value": 4, "type": "dimension" },
    "sm": { "value": 8, "type": "dimension" },
    "md": { "value": 16, "type": "dimension" },
    "lg": { "value": 24, "type": "dimension" },
    "xl": { "value": 32, "type": "dimension" }
  },
  "radius": {
    "sm": { "value": 4, "type": "dimension" },
    "md": { "value": 8, "type": "dimension" },
    "lg": { "value": 16, "type": "dimension" },
    "full": { "value": 9999, "type": "dimension" }
  },
  "typography": {
    "heading-lg": {
      "fontSize": 24,
      "fontWeight": "700",
      "lineHeight": 1.3
    },
    "body-md": {
      "fontSize": 16,
      "fontWeight": "400",
      "lineHeight": 1.5
    }
  }
}
```

各平台生成产物对照：

| Token源 | iOS产物 | Android产物 | Flutter产物 | Web产物 | 小程序产物 |
|---------|---------|-------------|-------------|---------|------------|
| color.primary | `Color.primary` | `R.color.primary` | `AppColors.primary` | `--color-primary` | `@primary` |
| spacing.md | `Spacing.md` | `R.dimen.spacing_md` | `AppSpacing.md` | `--spacing-md` | `@spacing-md` |
| radius.lg | `Radius.lg` | `R.dimen.radius_lg` | `AppRadius.lg` | `--radius-lg` | `@radius-lg` |

推荐工具链：Style Dictionary / Figma Tokens Plugin → 自动生成各平台代码。

### 2.2 业务逻辑复用方案

业务逻辑是最有价值的复用目标。根据团队技术栈选择合适的共享方案：

| 方案 | 共享语言 | 覆盖平台 | 适用场景 | 成熟度 |
|------|----------|----------|----------|--------|
| Kotlin Multiplatform (KMP) | Kotlin | iOS + Android | 原生双端共享业务逻辑 | 生产可用 |
| Flutter (Dart) | Dart | iOS + Android + Web | 全端统一UI + 逻辑 | 生产可用 |
| 共享JS模块 | TypeScript | Web + 小程序 + RN | 前端生态内复用 | 成熟 |
| Rust + FFI | Rust | 全平台 | 高性能计算、加密 | 进阶 |
| C++ 共享库 | C++ | iOS + Android | 音视频、图形处理 | 成熟 |

KMP 共享架构示意：

```
┌──────────────────────────────────────────────┐
│                 共享模块 (KMP)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ UseCase  │ │Repository│ │  数据模型     │  │
│  │ (纯逻辑) │ │ (接口)   │ │  (序列化)    │  │
│  └──────────┘ └──────────┘ └──────────────┘  │
│  ┌──────────────────────────────────────────┐ │
│  │         expect/actual 平台适配            │ │
│  └──────────────────────────────────────────┘ │
├──────────────┬───────────────────────────────┤
│  iOS Target  │       Android Target          │
│  (Swift调用) │       (直接调用)               │
└──────────────┴───────────────────────────────┘
```

共享JS模块策略（Web + 小程序）：

```
shared-logic/
├── src/
│   ├── models/          # 数据模型定义
│   ├── services/        # 业务服务
│   ├── validators/      # 校验规则
│   ├── formatters/      # 格式化工具
│   └── constants/       # 业务常量
├── package.json         # 发布为npm包
└── tsconfig.json        # 编译配置
```

复用决策矩阵：

```
                    复用价值
                      高
                       │
         ┌─────────────┼─────────────┐
         │  业务规则    │  数据模型    │  ← 优先复用
         │  校验逻辑    │  API定义    │
         ├─────────────┼─────────────┤
         │  工具函数    │  状态管理    │  ← 选择性复用
         │  格式化      │  缓存策略    │
         ├─────────────┼─────────────┤
         │  UI组件      │  动画效果    │  ← 平台各自实现
         │  手势交互    │  系统集成    │
         └─────────────┼─────────────┘
                       │
                      低
```

### 2.3 API层代码生成

通过 OpenAPI/Swagger 规范自动生成各平台的网络请求代码，消除手写API层的重复劳动。

代码生成流水线：

```
┌──────────┐    ┌──────────────┐    ┌─────────────────────┐
│ OpenAPI  │───→│  代码生成器   │───→│  各平台API客户端     │
│ 规范文件  │    │ (openapi-gen) │    │                     │
└──────────┘    └──────────────┘    │  ├── iOS (Swift)     │
                                    │  ├── Android (Kotlin)│
                                    │  ├── Flutter (Dart)  │
                                    │  ├── Web (TypeScript) │
                                    │  └── 小程序 (TS)      │
                                    └─────────────────────┘
```

各平台推荐生成工具：

| 平台 | 生成工具 | 网络库 | 产物 |
|------|----------|--------|------|
| iOS | swift-openapi-generator | URLSession / Alamofire | Swift协议+模型 |
| Android | openapi-generator (kotlin) | Retrofit + OkHttp | Kotlin接口+数据类 |
| Flutter | openapi-generator (dart) | dio | Dart类+序列化 |
| Web | openapi-typescript-codegen | axios / fetch | TypeScript类型+函数 |
| 小程序 | openapi-typescript-codegen | wx.request封装 | TS类型+请求函数 |

### 2.4 组件接口规范统一

跨平台组件应遵循统一的接口契约，确保行为一致性。

```
// 统一组件接口规范（以按钮为例）
ComponentSpec: Button
├── Props
│   ├── variant: "primary" | "secondary" | "outline" | "ghost"
│   ├── size: "sm" | "md" | "lg"
│   ├── disabled: boolean
│   ├── loading: boolean
│   └── onPress: () => void
├── Slots
│   ├── leading: Icon (可选)
│   └── trailing: Icon (可选)
├── States
│   ├── default / hover / pressed / disabled / loading
└── Accessibility
    ├── role: "button"
    ├── label: string (必填)
    └── hint: string (可选)
```

---

## 3. 平台差异处理

### 3.1 UI规范差异

各平台有独立的设计语言，跨平台开发需尊重平台惯例，而非强行统一。

| 维度 | iOS (HIG) | Android (Material 3) | Web | 微信小程序 |
|------|-----------|----------------------|-----|------------|
| 导航栏 | 大标题导航栏，左返回 | TopAppBar，左抽屉/返回 | 顶部导航+面包屑 | 自定义导航栏/原生导航栏 |
| Tab栏 | 底部TabBar(最多5个) | Bottom Navigation(3-5) | 顶部Tab/侧边栏 | 底部TabBar(最多5个) |
| 列表 | UITableView风格分组 | LazyColumn + Card | 虚拟滚动列表 | scroll-view + 分页 |
| 弹窗 | Alert / ActionSheet | Dialog / BottomSheet | Modal / Drawer | wx.showModal / 自定义 |
| 下拉刷新 | 原生UIRefreshControl | SwipeRefresh | 自定义实现 | enablePullDownRefresh |
| 加载态 | 系统ActivityIndicator | CircularProgressIndicator | Skeleton / Spinner | wx.showLoading |
| 空状态 | 居中图文提示 | 居中图文提示 | 居中图文+操作按钮 | 居中图文提示 |

平台适配策略：

```
// 适配器模式处理UI差异
interface PlatformAdapter {
  showAlert(title: string, message: string): void
  showLoading(): void
  hideLoading(): void
  hapticFeedback(type: FeedbackType): void
}

// 各平台提供具体实现
class IOSAdapter implements PlatformAdapter { ... }
class AndroidAdapter implements PlatformAdapter { ... }
class WebAdapter implements PlatformAdapter { ... }
class MiniProgramAdapter implements PlatformAdapter { ... }
```

### 3.2 系统能力差异

| 能力 | iOS | Android | Web | Flutter | 小程序 |
|------|-----|---------|-----|---------|--------|
| 推送通知 | APNs | FCM | Web Push API | firebase_messaging | 订阅消息 |
| 本地存储 | UserDefaults / Keychain | SharedPrefs / EncryptedSP | localStorage / IndexedDB | shared_preferences / hive | wx.setStorage |
| 文件系统 | FileManager (沙盒) | Context.filesDir | File API (受限) | path_provider | wx.getFileSystemManager |
| 相机/相册 | AVFoundation / PHPicker | CameraX / MediaStore | MediaDevices API | image_picker | wx.chooseMedia |
| 定位 | CoreLocation | FusedLocationProvider | Geolocation API | geolocator | wx.getLocation |
| 生物识别 | Face ID / Touch ID | BiometricPrompt | WebAuthn | local_auth | 不支持 |
| 后台任务 | BGTaskScheduler | WorkManager | Service Worker | workmanager | 受限(仅音频/定位) |
| 深度链接 | Universal Links | App Links | URL路由 | go_router | 场景值+页面参数 |
| 权限管理 | Info.plist声明+运行时请求 | Manifest声明+运行时请求 | Permissions API | permission_handler | 授权API |

权限处理统一抽象：

```
// 跨平台权限管理接口
interface PermissionManager {
  check(permission: Permission): PermissionStatus
  request(permission: Permission): PermissionStatus
  openSettings(): void
}

enum PermissionStatus {
  granted,        // 已授权
  denied,         // 已拒绝（可再次请求）
  permanentDenied,// 永久拒绝（需引导设置）
  restricted,     // 系统限制（iOS家长控制等）
  notDetermined   // 未决定（首次请求前）
}
```

### 3.3 交互差异

| 交互维度 | iOS | Android | Web | 小程序 |
|----------|-----|---------|-----|--------|
| 返回操作 | 左滑返回(边缘手势) | 系统返回键/手势 | 浏览器后退 | 左上角返回/navigateBack |
| 下拉刷新 | 弹性回弹+原生控件 | SwipeRefresh | 自定义实现 | onPullDownRefresh |
| 长按操作 | Context Menu (3D Touch) | Long Press → Menu | 右键菜单 | bindlongtap |
| 滑动删除 | 左滑显示操作按钮 | ItemTouchHelper | 自定义滑动 | movable-view |
| 键盘处理 | 自动避让+inputAccessoryView | windowSoftInputMode | CSS视口单位 | adjust-position |
| 触觉反馈 | UIImpactFeedbackGenerator | HapticFeedbackConstants | Vibration API | wx.vibrateShort |
| 页面转场 | push/present动画 | Fragment/Activity转场 | 路由过渡动画 | 页面切换动画 |
| 多指手势 | 原生支持(捏合/旋转) | ScaleGestureDetector | Touch Events / Pointer | 不支持多指 |

手势冲突处理策略：

```
┌─────────────────────────────────────────────┐
│              手势优先级仲裁                    │
├─────────────────────────────────────────────┤
│  1. 系统手势（返回、通知中心）  → 最高优先级   │
│  2. 页面级手势（下拉刷新）      → 高优先级     │
│  3. 容器级手势（滚动、翻页）    → 中优先级     │
│  4. 组件级手势（滑动删除、拖拽） → 低优先级    │
│  5. 元素级手势（点击、长按）    → 最低优先级   │
├─────────────────────────────────────────────┤
│  冲突时：高优先级手势消费事件，低优先级不响应   │
│  可通过 simultaneousGesture 允许并行识别      │
└─────────────────────────────────────────────┘
```

---

## 4. 混合开发架构

### 4.1 Native + WebView 方案（JSBridge设计）

JSBridge 是 Native 与 Web 通信的核心桥梁。设计良好的 Bridge 应具备类型安全、双向通信、版本兼容能力。

通信架构：

```
┌─────────────────┐          ┌─────────────────┐
│    WebView       │          │     Native       │
│                  │          │                  │
│  JS调用Native:   │ ──────→  │  注册Handler:    │
│  bridge.call(    │          │  bridge.register(│
│    'getUserInfo',│          │    'getUserInfo',│
│    {id: '123'}, │          │    (params) => { │
│    callback      │          │      return data │
│  )               │          │    }             │
│                  │          │  )               │
│  Native调用JS:   │ ←──────  │  主动调用JS:     │
│  bridge.on(      │          │  bridge.callJS(  │
│    'onPush',     │          │    'onPush',     │
│    handler       │          │    payload       │
│  )               │          │  )               │
└─────────────────┘          └─────────────────┘
```

JSBridge 协议设计：

```json
{
  "id": "msg_001",
  "type": "request | response | event",
  "module": "user",
  "method": "getUserInfo",
  "params": { "userId": "123" },
  "callback": "cb_001",
  "version": "1.0"
}
```

Bridge 能力注册表：

| 模块 | 方法 | 方向 | 说明 |
|------|------|------|------|
| device | getDeviceInfo | JS→Native | 获取设备信息 |
| device | getNetworkType | JS→Native | 获取网络状态 |
| auth | getToken | JS→Native | 获取登录态 |
| auth | login | JS→Native | 触发登录流程 |
| nav | pushPage | JS→Native | 打开原生页面 |
| nav | popPage | JS→Native | 关闭当前页面 |
| nav | setTitle | JS→Native | 设置导航栏标题 |
| media | chooseImage | JS→Native | 选择图片 |
| media | scanQRCode | JS→Native | 扫码 |
| event | onResume | Native→JS | 页面恢复前台 |
| event | onPush | Native→JS | 收到推送消息 |
| event | onThemeChange | Native→JS | 主题切换通知 |

安全策略：

- 白名单机制：仅允许指定域名的页面调用Bridge
- 鉴权校验：敏感API需验证调用方身份
- 参数校验：所有入参做类型和范围校验
- 版本协商：客户端与H5协商Bridge版本，向下兼容

### 4.2 Native + Flutter 混合（FlutterModule集成）

适用于已有Native应用逐步引入Flutter页面的场景。

集成架构：

```
┌─────────────────────────────────────────────┐
│              Native宿主应用                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │ Native  │  │ Native  │  │  Flutter     │  │
│  │ 页面A   │  │ 页面B   │  │  Module      │  │
│  │         │  │         │  │  ┌─────────┐ │  │
│  │         │  │         │  │  │Flutter  │ │  │
│  │         │  │         │  │  │页面C    │ │  │
│  │         │  │         │  │  │页面D    │ │  │
│  │         │  │         │  │  └─────────┘ │  │
│  └─────────┘  └─────────┘  └─────────────┘  │
├─────────────────────────────────────────────┤
│              MethodChannel 通信层             │
│  ┌──────────────────────────────────────┐    │
│  │  Native ←→ Flutter 双向方法调用       │    │
│  │  EventChannel: 持续数据流传输         │    │
│  │  BasicMessageChannel: 简单消息传递    │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

集成关键决策：

| 决策点 | 方案A | 方案B | 推荐 |
|--------|-------|-------|------|
| 引擎管理 | 单引擎复用 | 多引擎实例 | 单引擎（内存优化） |
| 页面容器 | FlutterActivity/VC | FlutterFragment/子View | 按场景选择 |
| 路由管理 | Native统一路由 | Flutter内部路由 | 混合路由表 |
| 数据共享 | MethodChannel传递 | 共享存储(MMKV) | 组合使用 |
| 构建集成 | 源码依赖 | AAR/Framework产物 | 产物依赖（CI友好） |

### 4.3 微前端在移动端的应用

微前端思想可迁移到移动端，实现业务模块的独立开发、独立部署。

```
┌─────────────────────────────────────────────┐
│                 宿主应用 (Shell)              │
│  ┌──────────────────────────────────────┐    │
│  │          模块加载器 / 路由分发          │    │
│  └──────────────────────────────────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ 模块A    │ │ 模块B    │ │ 模块C    │     │
│  │ (Native) │ │ (Flutter)│ │ (H5)    │     │
│  │ 独立仓库  │ │ 独立仓库  │ │ 独立仓库 │     │
│  │ 独立CI   │ │ 独立CI   │ │ 独立CI  │     │
│  └──────────┘ └──────────┘ └──────────┘     │
│  ┌──────────────────────────────────────┐    │
│  │          共享基础设施层                 │    │
│  │  网络 / 存储 / 监控 / 账号 / 路由      │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

移动端微前端的核心挑战与应对：

| 挑战 | 应对方案 |
|------|----------|
| 模块隔离 | 独立进程/独立ClassLoader/沙盒环境 |
| 资源冲突 | 资源前缀命名空间 + 动态加载 |
| 版本协调 | 基础库版本锁定 + 兼容性矩阵 |
| 包体积 | 按需下载模块 + 动态化框架 |
| 通信机制 | 统一事件总线 + 协议路由 |

---

## 5. 模块化与组件化架构

### 5.1 模块划分策略

模块划分有两种主流思路，实际项目中通常组合使用。

按业务域划分（推荐）：

```
app/
├── modules/
│   ├── auth/              # 认证模块
│   │   ├── data/          # 数据层
│   │   ├── domain/        # 业务层
│   │   └── presentation/  # 展示层
│   ├── product/           # 商品模块
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   ├── order/             # 订单模块
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   └── profile/           # 个人中心模块
│       ├── data/
│       ├── domain/
│       └── presentation/
├── shared/                # 共享模块
│   ├── ui-kit/            # 通用UI组件
│   ├── network/           # 网络基础设施
│   ├── storage/           # 存储抽象
│   └── analytics/         # 埋点SDK
└── app-shell/             # 宿主壳工程
    ├── di/                # 依赖注入配置
    ├── navigation/        # 全局路由
    └── config/            # 应用配置
```

模块依赖规则：

```
┌─────────────────────────────────────────────┐
│                  app-shell                   │
│            (组装所有模块，配置DI)              │
├──────────┬──────────┬──────────┬────────────┤
│   auth   │ product  │  order   │  profile   │
│          │          │    │     │            │
│          │          │    ▼     │            │
│          │          │ (依赖auth│            │
│          │          │  的接口) │            │
├──────────┴──────────┴──────────┴────────────┤
│                   shared                     │
│         (所有模块可依赖，不依赖业务模块)        │
├─────────────────────────────────────────────┤
│                基础设施 / 三方库               │
└─────────────────────────────────────────────┘

规则：
  ✓ 业务模块 → shared（允许）
  ✓ 业务模块 → 其他业务模块的接口（允许，通过DI）
  ✗ shared → 业务模块（禁止）
  ✗ 业务模块 → 其他业务模块的实现（禁止）
```

### 5.2 模块间通信

模块间通信的三种核心机制：

#### 路由通信

```
// 统一路由协议
scheme://module/path?params

// 示例
myapp://product/detail?id=123
myapp://order/confirm?productId=123&count=2
myapp://auth/login?redirect=order/confirm

// 路由表注册（各模块独立注册）
Router.register("product/detail", ProductDetailPage)
Router.register("order/confirm", OrderConfirmPage)
Router.register("auth/login", LoginPage)
```

各平台路由方案：

| 平台 | 路由库 | 特点 |
|------|--------|------|
| iOS | Coordinator模式 / URLNavigator | 协议路由 + 参数传递 |
| Android | Navigation Component / ARouter | 注解路由 + 拦截器 |
| Flutter | go_router / auto_route | 声明式路由 + 类型安全 |
| Web (Vue) | vue-router | 路由守卫 + 懒加载 |
| Web (React) | react-router / TanStack Router | 嵌套路由 + 数据加载 |
| 小程序 | wx.navigateTo | 页面栈管理 + 参数传递 |

#### 事件总线

```
// 发布-订阅模式
EventBus.emit('cart:updated', { itemCount: 5 })
EventBus.on('cart:updated', (data) => { updateBadge(data.itemCount) })

// 事件命名规范: module:action
// 示例:
//   auth:login-success
//   auth:logout
//   cart:item-added
//   order:payment-complete
```

#### 依赖注入通信

```
// 模块A暴露接口（不暴露实现）
interface AuthService {
  isLoggedIn(): boolean
  getCurrentUser(): User | null
  getToken(): string | null
}

// 模块A内部提供实现
class AuthServiceImpl implements AuthService { ... }

// 模块B通过DI获取接口
class OrderViewModel(
  private val authService: AuthService  // 注入接口，不知道实现
) {
  fun placeOrder() {
    if (!authService.isLoggedIn()) {
      // 跳转登录
    }
  }
}
```

### 5.3 独立编译与调试

各业务模块应支持独立运行，加速开发迭代。

```
┌─────────────────────────────────────────────┐
│              独立编译模式                      │
├─────────────────────────────────────────────┤
│                                             │
│  完整应用模式:                                │
│  app-shell + auth + product + order + ...   │
│  → 完整App，用于集成测试和发布                 │
│                                             │
│  独立模块模式:                                │
│  module-shell + product (单模块)             │
│  → 独立可运行的Mini App                      │
│  → Mock其他模块的依赖接口                     │
│  → 编译速度提升 3-5x                         │
│                                             │
├─────────────────────────────────────────────┤
│  实现方式:                                    │
│  iOS:   独立Target / SPM Package            │
│  Android: 动态application/library切换        │
│  Flutter: 独立main入口 + Mock注入            │
│  Web:    独立dev server + Module Federation  │
└─────────────────────────────────────────────┘
```

---

## 6. 持续集成与多端构建

### 6.1 多端CI/CD流水线设计

```
┌─────────────────────────────────────────────────────────┐
│                    代码提交 (Git Push)                    │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Stage 1: 质量门禁                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Lint检查  │ │ 类型检查  │ │ 单元测试  │ │ 安全扫描   │  │
│  │ (并行)   │ │ (并行)   │ │ (并行)   │ │ (并行)    │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       ▼ (全部通过)
┌─────────────────────────────────────────────────────────┐
│                  Stage 2: 多端构建                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ iOS构建   │ │ Android  │ │ Web构建   │ │ 小程序构建  │  │
│  │ (macOS)  │ │ 构建     │ │ (Linux)  │ │ (Linux)   │  │
│  │          │ │ (Linux)  │ │          │ │           │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       ▼ (全部成功)
┌─────────────────────────────────────────────────────────┐
│                  Stage 3: 集成测试                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │ iOS E2E  │ │ Android  │ │ Web E2E  │                │
│  │ (真机/   │ │ E2E      │ │(Playwright│                │
│  │ 模拟器)  │ │(Emulator)│ │          │                │
│  └──────────┘ └──────────┘ └──────────┘                │
└──────────────────────┬──────────────────────────────────┘
                       ▼ (全部通过)
┌─────────────────────────────────────────────────────────┐
│                  Stage 4: 发布                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │TestFlight│ │ Google   │ │ CDN部署   │ │ 体验版上传  │  │
│  │ / App    │ │ Play     │ │ (预发/   │ │ / 审核提交  │  │
│  │ Store    │ │ Console  │ │  生产)   │ │           │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

各平台构建环境要求：

| 平台 | 构建环境 | 签名/证书 | 产物 |
|------|----------|-----------|------|
| iOS | macOS + Xcode | Apple证书 + Provisioning Profile | .ipa / .xcarchive |
| Android | JDK + Android SDK | Keystore签名 | .aab / .apk |
| Flutter | Flutter SDK + 对应平台工具 | 同iOS/Android | 同iOS/Android |
| Web | Node.js | 无需签名 | 静态资源包 |
| 小程序 | Node.js + miniprogram-ci | 上传密钥 | 代码包 |

### 6.2 自动化测试策略

测试金字塔（各平台通用）：

```
          ╱  ╲
         ╱ E2E ╲           少量：关键用户流程
        ╱────────╲          (Appium / XCTest / Espresso / Playwright)
       ╱ 集成测试  ╲         适量：模块间交互、API集成
      ╱──────────────╲      (XCTest / JUnit / Widget Test)
     ╱    单元测试     ╲     大量：业务逻辑、工具函数
    ╱────────────────────╲  (XCTest / JUnit / flutter_test / Jest)
```

各平台测试工具矩阵：

| 测试类型 | iOS | Android | Flutter | Web | 小程序 |
|----------|-----|---------|---------|-----|--------|
| 单元测试 | XCTest | JUnit 5 / Kotest | flutter_test | Jest / Vitest | jest-miniprogram |
| UI测试 | XCUITest | Espresso / Compose Test | Widget Test | Testing Library | miniprogram-automator |
| 快照测试 | swift-snapshot-testing | Paparazzi / Roborazzi | golden_toolkit | Storybook + Chromatic | 不适用 |
| E2E测试 | XCUITest / Appium | UIAutomator / Appium | integration_test | Playwright / Cypress | miniprogram-automator |
| 性能测试 | Instruments / XCTest Metrics | Macrobenchmark | DevTools | Lighthouse | 性能面板 |

### 6.3 版本管理与发布协调

多端版本协调策略：

```
┌─────────────────────────────────────────────┐
│              版本号规范                       │
├─────────────────────────────────────────────┤
│                                             │
│  语义化版本: MAJOR.MINOR.PATCH              │
│                                             │
│  各端版本独立递增，但共享MAJOR版本号:          │
│                                             │
│  iOS:     2.5.3 (Build 203)                │
│  Android: 2.5.2 (VersionCode 205)          │
│  Web:     2.5.4 (CommitHash)               │
│  小程序:   2.5.1 (上传序号)                  │
│  Flutter:  2.5.3+203                        │
│                                             │
│  MAJOR一致 = API兼容                         │
│  MINOR独立 = 各端功能节奏不同                 │
│  PATCH独立 = 各端修复节奏不同                 │
│                                             │
└─────────────────────────────────────────────┘
```

发布协调流程：

| 阶段 | 动作 | 参与端 | 检查项 |
|------|------|--------|--------|
| 需求冻结 | 确认各端功能范围 | 全端 | 功能对齐、API就绪 |
| Alpha | 内部测试版本 | 全端并行 | 核心流程可用 |
| Beta | 外部测试版本 | 全端并行 | 回归测试通过、性能达标 |
| RC | 候选发布版本 | 全端并行 | 全量回归、灰度验证 |
| Release | 正式发布 | 按优先级排序 | 监控告警就绪、回滚方案确认 |
| Hotfix | 紧急修复 | 受影响端 | 最小改动、快速验证 |

灰度发布策略：

```
┌─────────────────────────────────────────────┐
│              灰度发布矩阵                     │
├──────────┬──────────────────────────────────┤
│ iOS      │ TestFlight → 1% → 10% → 50% → 全量 │
│ Android  │ 内测轨道 → 1% → 10% → 50% → 全量   │
│ Web      │ Feature Flag → 金丝雀 → 全量        │
│ 小程序    │ 体验版 → 灰度(按用户比例) → 全量     │
│ Flutter  │ 跟随宿主平台策略                     │
├──────────┴──────────────────────────────────┤
│ 灰度期间监控指标:                              │
│  - 崩溃率 < 0.1%                             │
│  - ANR率 < 0.5% (Android)                   │
│  - 接口错误率无上升                            │
│  - 核心转化率无下降                            │
│  - 用户反馈无新增严重问题                       │
└─────────────────────────────────────────────┘
```

---

## 附录：跨平台架构决策速查表

| 决策场景 | 推荐方案 | 备选方案 |
|----------|----------|----------|
| 全新项目，追求开发效率 | Flutter (全端统一) | React Native |
| 已有Native应用，新增页面 | Native + Flutter Module | Native + WebView |
| 运营活动页，频繁更新 | WebView (H5) | 小程序 |
| 高性能要求（音视频/游戏） | 纯Native | Native + C++共享库 |
| iOS + Android 共享业务逻辑 | Kotlin Multiplatform | Flutter |
| Web + 小程序 共享代码 | Taro / uni-app | 共享TS模块 |
| 设计系统统一 | Design Token + 各端原生组件 | 跨平台UI框架 |
| API层统一 | OpenAPI代码生成 | GraphQL + Codegen |

---

> 本文档作为 client-expert 技能的参考资料，覆盖跨平台架构设计的核心决策点。
> 具体平台的深入实践请参考各平台专项文档。
