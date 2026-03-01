# Flutter 开发完整指南

> 适用版本：Flutter 3.x / Dart 3.x | 最后更新：2025-05

---

## 1. Flutter 开发技术栈总览

| 组件 | 推荐版本 | 说明 |
|------|---------|------|
| Flutter SDK | 3.22+ | 稳定通道，支持 Impeller 渲染引擎 |
| Dart SDK | 3.4+ | 支持 patterns、records、sealed class |
| Material Design | Material 3 | 默认启用 `useMaterial3: true` |
| Cupertino | 最新 | iOS 风格组件，跟随 Flutter SDK |

Dart 3.x 关键特性：sealed class + pattern matching、records、switch expression。

```dart
sealed class Result<T> { const Result(); }
class Success<T> extends Result<T> { final T data; const Success(this.data); }
class Failure<T> extends Result<T> { final String message; const Failure(this.message); }

String handleResult(Result<String> r) => switch (r) {
  Success(:final data) => '成功: $data',
  Failure(:final message) => '失败: $message',
};
```

推荐技术栈组合：

| 层级 | 推荐方案 | 备选方案 |
|------|---------|---------|
| 状态管理 | BLoC/Cubit | Riverpod |
| 网络请求 | Dio | http |
| 序列化 | freezed + json_serializable | json_serializable |
| 路由 | GoRouter | auto_route |
| 本地存储 | drift (SQLite) | hive |
| DI | get_it + injectable | riverpod |

---

## 2. 项目工程配置

### pubspec.yaml 核心依赖

```yaml
environment:
  sdk: '>=3.4.0 <4.0.0'
dependencies:
  flutter: { sdk: flutter }
  flutter_bloc: ^8.1.0          # 状态管理
  dio: ^5.4.0                   # 网络请求
  go_router: ^14.0.0            # 路由
  freezed_annotation: ^2.4.0    # 不可变模型
  json_annotation: ^4.9.0       # JSON 序列化
  get_it: ^7.6.0                # 依赖注入
  drift: ^2.16.0                # SQLite ORM
  flutter_secure_storage: ^9.0.0
dev_dependencies:
  flutter_test: { sdk: flutter }
  build_runner: ^2.4.0
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  bloc_test: ^9.1.0
  mocktail: ^1.0.0
```

### Flavor 多环境配置

```dart
enum Flavor { dev, staging, prod }

class AppConfig {
  final String apiBaseUrl;
  final String appName;
  final Flavor flavor;
  const AppConfig({required this.apiBaseUrl, required this.appName, required this.flavor});

  static const dev = AppConfig(apiBaseUrl: 'https://dev-api.example.com', appName: 'MyApp Dev', flavor: Flavor.dev);
  static const prod = AppConfig(apiBaseUrl: 'https://api.example.com', appName: 'MyApp', flavor: Flavor.prod);
}

// lib/main_dev.dart
void main() => runApp(MyApp(config: AppConfig.dev));
// lib/main_prod.dart
void main() => runApp(MyApp(config: AppConfig.prod));
```

构建命令：

```bash
flutter build apk --flavor dev -t lib/main_dev.dart
flutter build apk --flavor prod -t lib/main_prod.dart
flutter build ios --flavor prod -t lib/main_prod.dart
```

| 平台 | 配置文件 | 常见配置项 |
|------|---------|-----------|
| Android | `android/app/build.gradle` | minSdk、targetSdk、签名、flavor |
| iOS | `ios/Runner.xcodeproj` | Bundle ID、签名、Capability |
| Web | `web/index.html` | PWA manifest、base href |

---

## 3. Widget 体系

三大核心类型：StatelessWidget（无状态展示）、StatefulWidget（局部状态）、InheritedWidget（跨层级共享）。

```dart
// StatelessWidget —— 纯展示
class UserAvatar extends StatelessWidget {
  final String imageUrl;
  final double size;
  const UserAvatar({super.key, required this.imageUrl, this.size = 40});

  @override
  Widget build(BuildContext context) {
    return ClipOval(child: Image.network(imageUrl, width: size, height: size, fit: BoxFit.cover));
  }
}

// StatefulWidget —— 有局部状态
class CounterButton extends StatefulWidget {
  const CounterButton({super.key});
  @override
  State<CounterButton> createState() => _CounterButtonState();
}
class _CounterButtonState extends State<CounterButton> {
  int _count = 0;
  @override
  Widget build(BuildContext context) {
    return ElevatedButton(onPressed: () => setState(() => _count++), child: Text('点击: $_count'));
  }
}
```

选型原则：

| 场景 | 推荐 Widget | 原因 |
|------|------------|------|
| 纯展示 UI | StatelessWidget | 无状态，性能最优 |
| 表单/动画等局部状态 | StatefulWidget | 需要 setState |
| 跨组件共享数据 | InheritedWidget / Provider | 避免 prop drilling |
| 列表项 | StatelessWidget + const | 配合 key 实现高效 diff |

---

## 4. 状态管理方案

### 方案对比

| 特性 | BLoC/Cubit | Riverpod | Provider |
|------|-----------|----------|----------|
| 学习曲线 | 中等 | 较陡 | 平缓 |
| 可测试性 | 优秀 | 优秀 | 良好 |
| 适用规模 | 中大型项目 | 中大型项目 | 小型项目 |
| 事件溯源 | 原生支持 | 需自行实现 | 不支持 |

### BLoC/Cubit 推荐实现

```dart
// 状态定义（使用 freezed）
@freezed
class AuthState with _$AuthState {
  const factory AuthState.initial() = _Initial;
  const factory AuthState.loading() = _Loading;
  const factory AuthState.authenticated(User user) = _Authenticated;
  const factory AuthState.unauthenticated(String? message) = _Unauthenticated;
}

// Cubit 实现
class AuthCubit extends Cubit<AuthState> {
  final AuthRepository _authRepo;
  AuthCubit(this._authRepo) : super(const AuthState.initial());

  Future<void> login(String email, String password) async {
    emit(const AuthState.loading());
    try {
      final user = await _authRepo.login(email, password);
      emit(AuthState.authenticated(user));
    } catch (e) {
      emit(AuthState.unauthenticated(e.toString()));
    }
  }
}

// UI 层使用
BlocConsumer<AuthCubit, AuthState>(
  listener: (context, state) {
    if (state case AuthState.authenticated()) context.go('/home');
  },
  builder: (context, state) => switch (state) {
    AuthState.loading() => const Center(child: CircularProgressIndicator()),
    _ => const LoginForm(),
  },
);
```

选型建议：团队有 BLoC 经验 → BLoC/Cubit；新项目追求类型安全 → Riverpod；小型项目 → Provider。

---

## 5. 网络层封装

### Dio 统一封装

```dart
class HttpClient {
  late final Dio _dio;

  HttpClient({required String baseUrl, String? token}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
    ));
    _dio.interceptors.addAll([_AuthInterceptor(token), _ErrorInterceptor()]);
  }

  Future<T> get<T>(String path, {Map<String, dynamic>? query, required T Function(dynamic) parser}) async {
    final response = await _dio.get(path, queryParameters: query);
    return parser(response.data);
  }

  Future<T> post<T>(String path, {dynamic data, required T Function(dynamic) parser}) async {
    final response = await _dio.post(path, data: data);
    return parser(response.data);
  }
}

// 认证拦截器
class _AuthInterceptor extends Interceptor {
  final String? _token;
  _AuthInterceptor(this._token);
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (_token != null) options.headers['Authorization'] = 'Bearer $_token';
    handler.next(options);
  }
}

// 错误拦截器
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final apiError = switch (err.response?.statusCode) {
      401 => const ApiError.unauthorized(),
      403 => const ApiError.forbidden(),
      404 => const ApiError.notFound(),
      500 => const ApiError.serverError(),
      _ => ApiError.unknown(err.message ?? '未知错误'),
    };
    handler.reject(DioException(requestOptions: err.requestOptions, error: apiError));
  }
}
```

### freezed 数据模型

```dart
@freezed
class User with _$User {
  const factory User({
    required int id,
    required String name,
    required String email,
    @JsonKey(name: 'avatar_url') String? avatarUrl,
    @Default(false) bool isVerified,
  }) = _User;
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
// 生成命令: dart run build_runner build --delete-conflicting-outputs
```

---

## 6. 数据持久化

| 方案 | 适用场景 | 数据量 | 查询能力 | 加密 |
|------|---------|--------|---------|------|
| shared_preferences | 简单键值对（设置项） | 小 | 无 | 否 |
| sqflite / drift | 结构化数据、复杂查询 | 大 | SQL | 可选 |
| hive | 轻量 NoSQL、缓存 | 中 | 有限 | 可选 |
| flutter_secure_storage | 敏感数据（token） | 极小 | 无 | 是 |

### drift (SQLite ORM)

```dart
class Users extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get name => text().withLength(min: 1, max: 50)();
  TextColumn get email => text().unique()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

@DriftDatabase(tables: [Users])
class AppDatabase extends _$AppDatabase {
  AppDatabase(super.e);
  @override int get schemaVersion => 1;

  Future<List<User>> getAllUsers() => select(users).get();
  Future<int> insertUser(UsersCompanion user) => into(users).insert(user);
}
```

### flutter_secure_storage

```dart
class SecureStorageService {
  final _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );
  Future<void> saveToken(String token) => _storage.write(key: 'auth_token', value: token);
  Future<String?> getToken() => _storage.read(key: 'auth_token');
  Future<void> clearAll() => _storage.deleteAll();
}
```

---

## 7. 路由方案

### GoRouter 配置

```dart
final router = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final isLoggedIn = context.read<AuthCubit>().state is Authenticated;
    final isLoginRoute = state.matchedLocation == '/login';
    if (!isLoggedIn && !isLoginRoute) return '/login';
    if (isLoggedIn && isLoginRoute) return '/home';
    return null;
  },
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginPage()),
    ShellRoute(
      builder: (_, __, child) => MainShell(child: child),
      routes: [
        GoRoute(path: '/home', builder: (_, __) => const HomePage()),
        GoRoute(
          path: '/profile/:userId',
          builder: (_, state) => ProfilePage(userId: state.pathParameters['userId']!),
        ),
      ],
    ),
  ],
);
```

### Deep Link 配置

Android `AndroidManifest.xml`：

```xml
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="https" android:host="example.com" android:pathPrefix="/app" />
</intent-filter>
```

iOS `Info.plist`：设置 `FlutterDeepLinkingEnabled` 为 `true`，配置 `CFBundleURLSchemes`。

---

## 8. 平台通道

| 通道类型 | 通信方向 | 适用场景 |
|---------|---------|---------|
| MethodChannel | 双向，请求-响应 | 调用原生 API、获取设备信息 |
| EventChannel | 原生→Dart 流 | 传感器、位置更新、蓝牙数据 |
| BasicMessageChannel | 双向，自定义编解码 | 自定义协议通信 |
| FFI | Dart→C/C++ | 高性能计算、复用 C 库 |

### MethodChannel 示例

```dart
// Dart 端
class BatteryService {
  static const _channel = MethodChannel('com.example.app/battery');
  Future<int> getBatteryLevel() async {
    try {
      return await _channel.invokeMethod<int>('getBatteryLevel') ?? -1;
    } on PlatformException catch (e) {
      throw Exception('获取电量失败: ${e.message}');
    }
  }
}
```

```kotlin
// Android (Kotlin)
MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "com.example.app/battery")
    .setMethodCallHandler { call, result ->
        when (call.method) {
            "getBatteryLevel" -> result.success(getBatteryLevel())
            else -> result.notImplemented()
        }
    }
```

```swift
// iOS (Swift)
let channel = FlutterMethodChannel(name: "com.example.app/battery", binaryMessenger: controller.binaryMessenger)
channel.setMethodCallHandler { (call, result) in
    if call.method == "getBatteryLevel" {
        UIDevice.current.isBatteryMonitoringEnabled = true
        result(Int(UIDevice.current.batteryLevel * 100))
    } else { result(FlutterMethodNotImplemented) }
}
```

---

## 9. 常用插件集成

| 功能 | 推荐插件 | 备注 |
|------|---------|------|
| 推送 | firebase_messaging + flutter_local_notifications | FCM 全平台 |
| 地图 | google_maps_flutter / amap_flutter | 海外 Google，国内高德 |
| 支付 | in_app_purchase / stripe_sdk | IAP 用官方插件 |
| 相机 | camera / image_picker | camera 更底层可控 |
| 权限 | permission_handler | 统一权限 API |
| 生物识别 | local_auth | 指纹/面容 |
| 分享 | share_plus | 系统分享面板 |
| 启动页 | flutter_native_splash | 原生启动屏 |
| 国际化 | flutter_localizations + intl | 官方方案 |
| 图片缓存 | cached_network_image | 自动磁盘缓存 |

### 推送初始化

```dart
class PushNotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  Future<void> initialize() async {
    final settings = await _messaging.requestPermission(alert: true, badge: true, sound: true);
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      final token = await _messaging.getToken();
      await _uploadToken(token);
      _messaging.onTokenRefresh.listen(_uploadToken);
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
      FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageTap);
    }
  }
}
```

### 权限请求

```dart
class PermissionService {
  static Future<bool> requestCamera(BuildContext context) async {
    var status = await Permission.camera.status;
    if (status.isDenied) status = await Permission.camera.request();
    if (status.isPermanentlyDenied) return await openAppSettings();
    return status.isGranted;
  }
}
```

---

## 10. 性能优化

```bash
flutter run --profile    # Profile 模式运行
dart devtools            # 打开 DevTools
```

### Widget 重建优化

```dart
// 1. const 构造减少重建
const Text('静态文本');  // 不会重建

// 2. 精确监听，缩小重建范围（BlocSelector 替代 BlocBuilder）
BlocSelector<CartCubit, CartState, int>(
  selector: (state) => state.itemCount,
  builder: (context, count) => Text('共 $count 件'),
);

// 3. 列表优化
ListView.builder(
  itemCount: items.length,
  itemExtent: 72.0,  // 固定高度提升滚动性能
  itemBuilder: (_, i) => ListTile(key: ValueKey(items[i].id), title: Text(items[i].name)),
);

// 4. RepaintBoundary 隔离重绘
RepaintBoundary(child: ComplexAnimationWidget())
```

### Isolate 并发

```dart
// 简单场景用 compute
Future<List<User>> parseUsers(String json) => compute(_parse, json);
List<User> _parse(String json) => (jsonDecode(json) as List).map((e) => User.fromJson(e)).toList();
```

| 优化项 | 方法 | 影响 |
|--------|------|------|
| 减少 Widget 重建 | const、BlocSelector、精确监听 | 高 |
| 列表性能 | ListView.builder + itemExtent + key | 高 |
| 图片优化 | cached_network_image、压缩、懒加载 | 中 |
| 耗时计算 | compute / Isolate | 高 |
| 隔离重绘 | RepaintBoundary | 中 |

---

## 11. 安全实践

```bash
# 代码混淆
flutter build apk --obfuscate --split-debug-info=build/debug-info
flutter build ios --obfuscate --split-debug-info=build/debug-info
```

### 证书固定

```dart
(dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
  final client = HttpClient();
  client.badCertificateCallback = (cert, host, port) {
    final expected = 'AA:BB:CC:DD:...';
    return sha256.convert(cert.der).toString() == expected;
  };
  return client;
};
```

| 检查项 | 实现方式 |
|--------|---------|
| 敏感数据加密存储 | flutter_secure_storage |
| 网络通信加密 | HTTPS + 证书固定 |
| 代码混淆 | --obfuscate 标志 |
| 防截屏（Android） | FLAG_SECURE |
| Root/越狱检测 | flutter_jailbreak_detection |
| API Key 保护 | --dart-define 或远程配置 |
| 调试模式检测 | kReleaseMode 判断 |

---

## 12. 多平台适配

### 平台自适应 Widget

```dart
class AdaptiveDialog {
  static Future<bool?> show(BuildContext context, String message) {
    if (Platform.isIOS) {
      return showCupertinoDialog<bool>(
        context: context,
        builder: (_) => CupertinoAlertDialog(
          title: const Text('提示'), content: Text(message),
          actions: [
            CupertinoDialogAction(isDestructiveAction: true, onPressed: () => Navigator.pop(context, false), child: const Text('取消')),
            CupertinoDialogAction(onPressed: () => Navigator.pop(context, true), child: const Text('确定')),
          ],
        ),
      );
    }
    return showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('提示'), content: Text(message),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('取消')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('确定')),
        ],
      ),
    );
  }
}
```

### 响应式布局

```dart
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;
  const ResponsiveLayout({super.key, required this.mobile, this.tablet, this.desktop});

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (_, constraints) {
      if (constraints.maxWidth >= 1200 && desktop != null) return desktop!;
      if (constraints.maxWidth >= 600 && tablet != null) return tablet!;
      return mobile;
    },
  );
}
```

| 平台 | 关键注意事项 |
|------|------------|
| Web | 路由用 PathUrlStrategy；避免 dart:io |
| Windows | 窗口管理用 window_manager；注意 DPI 缩放 |
| macOS | entitlements 声明网络权限；沙盒限制 |
| Linux | GTK 依赖；字体渲染差异 |

---

## 13. 发布流程

### Android 构建

```bash
keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
flutter build appbundle --release          # AAB（Google Play）
flutter build apk --release --split-per-abi # APK（按架构拆分）
```

### iOS 构建

```bash
flutter build ios --release
flutter build ipa --release --export-options-plist=ios/ExportOptions.plist
```

### CI/CD (GitHub Actions 核心步骤)

```yaml
name: Flutter CI/CD
on:
  push: { branches: [main] }
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.22.0', channel: 'stable', cache: true }
      - run: flutter pub get
      - run: flutter analyze --fatal-infos
      - run: flutter test --coverage
  build-android:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.22.0', channel: 'stable' }
      - run: flutter build appbundle --release
  build-ios:
    needs: test
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.22.0', channel: 'stable' }
      - run: flutter build ipa --release --export-options-plist=ios/ExportOptions.plist
```

### 发布前检查清单

| 检查项 | Android | iOS |
|--------|---------|-----|
| 版本号更新 | pubspec.yaml version | 同左 |
| 签名配置 | key.properties | Xcode Signing |
| 混淆启用 | --obfuscate | --obfuscate |
| 权限声明 | AndroidManifest.xml | Info.plist |
| 图标/启动图 | mipmap 各分辨率 | Assets.xcassets |
| 最低系统版本 | minSdk 23+ | iOS 13+ |
| 隐私政策 | Google Play 要求 | App Store 要求 |

---

## 附录：推荐项目结构

```
lib/
├── main.dart / main_dev.dart / main_prod.dart
├── app.dart                         # MaterialApp 配置
├── config/                          # 环境配置、主题、路由表
├── core/
│   ├── network/                     # Dio 封装 + 拦截器
│   ├── storage/                     # 安全存储 + drift 数据库
│   ├── error/                       # 统一错误类型
│   └── di/                          # get_it 注册
├── features/
│   ├── auth/
│   │   ├── data/                    # Repository + Models
│   │   ├── domain/                  # Entities
│   │   └── presentation/           # Cubit + Pages
│   └── home/
└── shared/
    ├── widgets/                     # 通用 Widget
    ├── utils/                       # 工具函数
    └── extensions/                  # Dart 扩展方法
```
