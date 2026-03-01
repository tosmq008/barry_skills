# iOS 开发实战指南

> 本文档为 client-expert 技能参考手册，涵盖 iOS 开发核心技术栈、架构设计、常用 SDK 集成及发布流程。

---

## 1. iOS 开发技术栈总览

| 技术 | 版本/说明 | 适用场景 |
|------|-----------|----------|
| Swift | 5.9+ (支持宏、参数包) | 主力开发语言 |
| SwiftUI | iOS 16+ 生产可用 | 新项目首选 UI 框架 |
| UIKit | 成熟稳定 | 复杂自定义 UI、老项目维护 |
| Combine | 响应式框架 | 数据流绑定、网络请求 |
| async/await | Swift 5.5+ 原生并发 | 替代回调/Combine 的异步方案 |
| SwiftData | iOS 17+ | 轻量 ORM，替代 CoreData |
| Observation | iOS 17+ (@Observable) | 替代 ObservableObject 的新方案 |

### Swift 5.9+ 关键特性

```swift
// 宏 (Macros) — 编译期代码生成
@Observable
class UserStore {
    var name: String = ""
    var age: Int = 0
}

// if/switch 表达式
let label = if isVIP { "VIP 用户" } else { "普通用户" }

// 参数包 (Parameter Packs)
func allEqual<each T: Equatable>(_ values: repeat each T) -> Bool {
    // ...
}
```

---

## 2. 项目工程配置

### 2.1 推荐项目结构

```
MyApp/
├── App/
│   ├── MyApp.swift              # @main 入口
│   └── AppDelegate.swift        # 如需 UIKit 生命周期
├── Features/
│   ├── Auth/
│   │   ├── Views/
│   │   ├── ViewModels/
│   │   └── Models/
│   ├── Home/
│   └── Profile/
├── Core/
│   ├── Network/
│   ├── Storage/
│   └── Extensions/
├── Resources/
│   ├── Assets.xcassets
│   └── Localizable.xcstrings
└── Tests/
    ├── UnitTests/
    └── UITests/
```
### 2.2 关键 Build Settings

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| SWIFT_VERSION | 5.9 | Swift 语言版本 |
| IPHONEOS_DEPLOYMENT_TARGET | 16.0 | 最低支持系统版本 |
| SWIFT_STRICT_CONCURRENCY | complete | 严格并发检查 |
| ENABLE_USER_SCRIPT_SANDBOXING | YES | 脚本沙盒安全 |
| DEBUG_INFORMATION_FORMAT | dwarf-with-dsym | Release 需要 dSYM 用于崩溃符号化 |

### 2.3 代码签名 (Signing)

```
Signing & Capabilities:
├── Automatically manage signing: ✅ (开发阶段推荐)
├── Team: 选择开发者账号
├── Bundle Identifier: com.company.appname
└── Provisioning Profile: Xcode Managed Profile
```

手动签名场景：CI/CD 环境、企业分发、多 Target 项目。

### 2.4 依赖管理

**Swift Package Manager (SPM) — 首选**

```swift
// Package.swift 或 Xcode > File > Add Package Dependencies
dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.9.0"),
    .package(url: "https://github.com/onevcat/Kingfisher.git", from: "7.0.0"),
]
```

**CocoaPods — 老项目兼容**

```ruby
# Podfile
platform :ios, '16.0'
use_frameworks!

target 'MyApp' do
  pod 'SnapKit', '~> 5.7'
  pod 'Moya', '~> 15.0'
end
```

> 新项目优先使用 SPM，仅在依赖库不支持 SPM 时使用 CocoaPods。

---

## 3. SwiftUI vs UIKit 选型指南

| 维度 | SwiftUI | UIKit |
|------|---------|-------|
| 最低版本 | iOS 16+ 生产可用 | iOS 13+ |
| 学习曲线 | 声明式，上手快 | 命令式，概念多 |
| 自定义程度 | 中等，复杂布局受限 | 极高，完全可控 |
| 动画 | 简洁的声明式动画 | 灵活但代码量大 |
| 列表性能 | LazyVStack/List 已优化 | UITableView/UICollectionView 成熟 |
| 导航 | NavigationStack (iOS 16+) | UINavigationController |
| 生态成熟度 | 快速完善中 | 十余年积累 |

**选型建议：**

- 新项目且最低支持 iOS 16+ → SwiftUI 为主，UIKit 补充
- 需要高度自定义 UI (如复杂手势、自定义转场) → UIKit
- 老项目迭代 → UIKit 为主，新页面逐步引入 SwiftUI
- SwiftUI 中嵌入 UIKit → `UIViewRepresentable` / `UIViewControllerRepresentable`
---

## 4. MVVM 架构实现

### 4.1 架构分层

```
View (SwiftUI View)
  ↕ 数据绑定 (@Published / @Observable)
ViewModel (业务逻辑、状态管理)
  ↕ 调用
Service / Repository (网络请求、数据持久化)
  ↕
Model (数据模型、Codable)
```

### 4.2 ViewModel 实现 — @Observable (iOS 17+)

```swift
import Observation

@Observable
final class HomeViewModel {
    private(set) var articles: [Article] = []
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    private let articleService: ArticleServiceProtocol

    init(articleService: ArticleServiceProtocol = ArticleService()) {
        self.articleService = articleService
    }

    func loadArticles() async {
        isLoading = true
        errorMessage = nil
        do {
            articles = try await articleService.fetchArticles()
        } catch {
            errorMessage = "加载失败: \(error.localizedDescription)"
        }
        isLoading = false
    }
}
```

### 4.3 ViewModel 实现 — ObservableObject + Combine (iOS 15+)

```swift
import Combine

final class HomeViewModel: ObservableObject {
    @Published private(set) var articles: [Article] = []
    @Published private(set) var isLoading = false
    @Published private(set) var errorMessage: String?

    private let articleService: ArticleServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(articleService: ArticleServiceProtocol = ArticleService()) {
        self.articleService = articleService
    }

    func loadArticles() {
        isLoading = true
        errorMessage = nil
        articleService.fetchArticlesPublisher()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = "加载失败: \(error.localizedDescription)"
                    }
                },
                receiveValue: { [weak self] articles in
                    self?.articles = articles
                }
            )
            .store(in: &cancellables)
    }
}
```

### 4.4 View 层绑定

```swift
struct HomeView: View {
    @State private var viewModel = HomeViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("加载中...")
            } else if let error = viewModel.errorMessage {
                ContentUnavailableView("出错了", systemImage: "exclamationmark.triangle", description: Text(error))
            } else {
                List(viewModel.articles) { article in
                    ArticleRow(article: article)
                }
            }
        }
        .task {
            await viewModel.loadArticles()
        }
    }
}
```
---

## 5. 网络层封装

### 5.1 基于 URLSession + async/await 的网络客户端

```swift
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}

enum NetworkError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int, data: Data)
    case decodingFailed(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "无效的 URL"
        case .invalidResponse: return "无效的响应"
        case .httpError(let code, _): return "HTTP 错误: \(code)"
        case .decodingFailed(let error): return "解析失败: \(error.localizedDescription)"
        }
    }
}

actor NetworkClient {
    static let shared = NetworkClient()

    private let session: URLSession
    private let baseURL: String
    private let decoder: JSONDecoder

    init(
        baseURL: String = AppConfig.apiBaseURL,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.decoder.dateDecodingStrategy = .iso8601
    }

    func request<T: Decodable>(
        path: String,
        method: HTTPMethod = .get,
        body: Encodable? = nil,
        headers: [String: String] = [:]
    ) async throws -> T {
        guard let url = URL(string: baseURL + path) else {
            throw NetworkError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // 注入 Token
        if let token = try? KeychainHelper.read(key: "access_token") {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }

        if let body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.httpError(statusCode: httpResponse.statusCode, data: data)
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw NetworkError.decodingFailed(error)
        }
    }
}
```

### 5.2 API 响应模型

```swift
struct APIResponse<T: Decodable>: Decodable {
    let code: Int
    let message: String
    let data: T?
}

// 使用
let response: APIResponse<[Article]> = try await NetworkClient.shared.request(path: "/articles")
if let articles = response.data {
    // 处理数据
}
```

### 5.3 Service 层示例

```swift
protocol ArticleServiceProtocol: Sendable {
    func fetchArticles() async throws -> [Article]
    func fetchArticle(id: String) async throws -> Article
}

struct ArticleService: ArticleServiceProtocol {
    private let client = NetworkClient.shared

    func fetchArticles() async throws -> [Article] {
        let response: APIResponse<[Article]> = try await client.request(path: "/articles")
        return response.data ?? []
    }

    func fetchArticle(id: String) async throws -> Article {
        let response: APIResponse<Article> = try await client.request(path: "/articles/\(id)")
        guard let article = response.data else {
            throw NetworkError.invalidResponse
        }
        return article
    }
}
```
---

## 6. 数据持久化

### 6.1 方案对比

| 方案 | 适用场景 | 数据量 | 复杂度 |
|------|----------|--------|--------|
| UserDefaults | 用户偏好、开关设置 | 极小 (KB 级) | 低 |
| 文件存储 (JSON/Plist) | 缓存数据、配置文件 | 小 (MB 级) | 低 |
| SwiftData | 结构化业务数据 (iOS 17+) | 中大 | 中 |
| CoreData | 结构化业务数据 (兼容旧版本) | 中大 | 高 |
| Keychain | 密码、Token、敏感信息 | 极小 | 中 |
| SQLite (GRDB/FMDB) | 高性能查询、大数据量 | 大 | 中高 |

### 6.2 UserDefaults 封装

```swift
@propertyWrapper
struct AppStorage<T> {
    let key: String
    let defaultValue: T
    let container: UserDefaults

    init(_ key: String, defaultValue: T, container: UserDefaults = .standard) {
        self.key = key
        self.defaultValue = defaultValue
        self.container = container
    }

    var wrappedValue: T {
        get { container.object(forKey: key) as? T ?? defaultValue }
        set { container.set(newValue, forKey: key) }
    }
}

// 使用 SwiftUI 内置的 @AppStorage 更简洁
struct SettingsView: View {
    @AppStorage("isDarkMode") private var isDarkMode = false
    @AppStorage("fontSize") private var fontSize = 16.0

    var body: some View {
        Form {
            Toggle("深色模式", isOn: $isDarkMode)
            Slider(value: $fontSize, in: 12...24, step: 1) {
                Text("字体大小: \(Int(fontSize))")
            }
        }
    }
}
```

### 6.3 SwiftData (iOS 17+)

```swift
import SwiftData

@Model
final class Note {
    var title: String
    var content: String
    var createdAt: Date
    @Relationship(deleteRule: .cascade) var tags: [Tag]

    init(title: String, content: String, createdAt: Date = .now) {
        self.title = title
        self.content = content
        self.createdAt = createdAt
        self.tags = []
    }
}

@Model
final class Tag {
    var name: String
    var notes: [Note]

    init(name: String) {
        self.name = name
        self.notes = []
    }
}

// App 入口配置
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Note.self, Tag.self])
    }
}

// View 中使用
struct NoteListView: View {
    @Query(sort: \Note.createdAt, order: .reverse) private var notes: [Note]
    @Environment(\.modelContext) private var context

    var body: some View {
        List(notes) { note in
            Text(note.title)
        }
    }

    func addNote(title: String, content: String) {
        let note = Note(title: title, content: content)
        context.insert(note)
    }
}
```
### 6.4 Keychain 封装

```swift
import Security

enum KeychainHelper {
    static func save(key: String, data: Data) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock
        ]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.saveFailed(status)
        }
    }

    static func read(key: String) throws -> String {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data,
              let string = String(data: data, encoding: .utf8) else {
            throw KeychainError.readFailed(status)
        }
        return string
    }

    static func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}

enum KeychainError: LocalizedError {
    case saveFailed(OSStatus)
    case readFailed(OSStatus)

    var errorDescription: String? {
        switch self {
        case .saveFailed(let status): return "Keychain 保存失败: \(status)"
        case .readFailed(let status): return "Keychain 读取失败: \(status)"
        }
    }
}
```

---

## 7. 导航与路由

### 7.1 NavigationStack + 枚举路由 (iOS 16+)

```swift
enum AppRoute: Hashable {
    case home
    case articleDetail(id: String)
    case profile(userId: String)
    case settings
}

@Observable
final class Router {
    var path = NavigationPath()

    func push(_ route: AppRoute) {
        path.append(route)
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .home:
                        HomeView()
                    case .articleDetail(let id):
                        ArticleDetailView(articleId: id)
                    case .profile(let userId):
                        ProfileView(userId: userId)
                    case .settings:
                        SettingsView()
                    }
                }
        }
        .environment(router)
    }
}

// 子视图中使用
struct HomeView: View {
    @Environment(Router.self) private var router

    var body: some View {
        Button("查看文章") {
            router.push(.articleDetail(id: "123"))
        }
    }
}
```
### 7.2 TabView + 多 NavigationStack

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                HomeView()
            }
            .tabItem { Label("首页", systemImage: "house") }
            .tag(0)

            NavigationStack {
                DiscoverView()
            }
            .tabItem { Label("发现", systemImage: "magnifyingglass") }
            .tag(1)

            NavigationStack {
                ProfileView()
            }
            .tabItem { Label("我的", systemImage: "person") }
            .tag(2)
        }
    }
}
```

---

## 8. 常用 SDK 集成指南

### 8.1 推送通知 (APNs)

```swift
import UserNotifications

final class NotificationManager: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationManager()

    func requestAuthorization() async -> Bool {
        do {
            let granted = try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .badge, .sound])
            if granted {
                await MainActor.run {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
            return granted
        } catch {
            return false
        }
    }

    // AppDelegate 中注册
    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        // 上报 token 到服务端
        Task { try? await uploadDeviceToken(token) }
    }
}
```

**Xcode 配置：** Signing & Capabilities → + Capability → Push Notifications

### 8.2 地图 (MapKit)

```swift
import MapKit

struct MapView: View {
    @State private var position: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074),
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
    )

    var body: some View {
        Map(position: $position) {
            Marker("北京", coordinate: CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074))
            Annotation("自定义标注", coordinate: CLLocationCoordinate2D(latitude: 39.91, longitude: 116.41)) {
                Image(systemName: "star.fill")
                    .foregroundStyle(.yellow)
                    .padding(8)
                    .background(.blue)
                    .clipShape(Circle())
            }
        }
        .mapStyle(.standard(elevation: .realistic))
    }
}
```
### 8.3 应用内购买 (StoreKit 2)

```swift
import StoreKit

@Observable
final class StoreManager {
    private(set) var products: [Product] = []
    private(set) var purchasedProductIDs: Set<String> = []

    private let productIDs = ["com.app.premium.monthly", "com.app.premium.yearly"]

    func loadProducts() async {
        do {
            products = try await Product.products(for: productIDs)
        } catch {
            // 处理错误
        }
    }

    func purchase(_ product: Product) async throws -> Transaction? {
        let result = try await product.purchase()
        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            await transaction.finish()
            purchasedProductIDs.insert(product.id)
            return transaction
        case .userCancelled, .pending:
            return nil
        @unknown default:
            return nil
        }
    }

    func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified: throw StoreError.verificationFailed
        case .verified(let value): return value
        }
    }

    func listenForTransactions() async {
        for await result in Transaction.updates {
            if let transaction = try? checkVerified(result) {
                purchasedProductIDs.insert(transaction.productID)
                await transaction.finish()
            }
        }
    }
}
```

### 8.4 相机与相册 (PhotosUI)

```swift
import PhotosUI

struct PhotoPickerView: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: Image?

    var body: some View {
        VStack {
            PhotosPicker(selection: $selectedItem, matching: .images) {
                Label("选择照片", systemImage: "photo")
            }

            if let selectedImage {
                selectedImage
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 300)
            }
        }
        .onChange(of: selectedItem) { _, newItem in
            Task {
                if let data = try? await newItem?.loadTransferable(type: Data.self),
                   let uiImage = UIImage(data: data) {
                    selectedImage = Image(uiImage: uiImage)
                }
            }
        }
    }
}
```

### 8.5 系统分享

```swift
struct ShareButton: View {
    let text: String
    let url: URL?

    var body: some View {
        ShareLink(
            item: url ?? URL(string: "https://example.com")!,
            subject: Text("分享内容"),
            message: Text(text)
        ) {
            Label("分享", systemImage: "square.and.arrow.up")
        }
    }
}
```
---

## 9. 性能优化

### 9.1 Instruments 常用工具

| 工具 | 用途 | 关注指标 |
|------|------|----------|
| Time Profiler | CPU 耗时分析 | 主线程阻塞、热点函数 |
| Allocations | 内存分配追踪 | 内存增长趋势、大对象分配 |
| Leaks | 内存泄漏检测 | 循环引用、未释放对象 |
| Network | 网络请求分析 | 请求耗时、并发数 |
| Core Animation | 渲染性能 | FPS、离屏渲染 |
| App Launch | 启动耗时 | 冷启动 < 400ms 目标 |

### 9.2 内存管理 (ARC) 要点

```swift
// 避免循环引用 — 闭包中使用 [weak self]
class ViewController: UIViewController {
    var timer: Timer?

    func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateUI()
        }
    }

    deinit {
        timer?.invalidate()
    }
}

// delegate 使用 weak 修饰
protocol DataSourceDelegate: AnyObject {
    func didUpdateData()
}

class DataSource {
    weak var delegate: DataSourceDelegate?
}
```

### 9.3 启动优化

| 阶段 | 优化手段 |
|------|----------|
| pre-main | 减少动态库数量、合并 Framework、移除无用类 |
| didFinishLaunching | 延迟非必要 SDK 初始化、异步执行耗时操作 |
| 首屏渲染 | 减少首屏视图层级、预加载关键数据、骨架屏占位 |

```swift
// 延迟初始化示例
@main
struct MyApp: App {
    init() {
        // 仅初始化核心服务
        setupCoreServices()

        // 延迟初始化非关键 SDK
        Task.detached(priority: .background) {
            await setupAnalytics()
            await setupCrashReporting()
        }
    }
}
```

### 9.4 列表性能优化

```swift
// SwiftUI — 使用 LazyVStack 替代 VStack
ScrollView {
    LazyVStack(spacing: 12) {
        ForEach(items) { item in
            ItemRow(item: item)
                .id(item.id) // 确保唯一标识
        }
    }
}

// 图片加载优化 — 使用 AsyncImage 或 Kingfisher
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .empty:
        ProgressView()
    case .success(let image):
        image.resizable().scaledToFill()
    case .failure:
        Image(systemName: "photo")
    @unknown default:
        EmptyView()
    }
}
.frame(width: 80, height: 80)
.clipShape(RoundedRectangle(cornerRadius: 8))
```
---

## 10. 安全实践

### 10.1 安全检查清单

| 检查项 | 实现方式 |
|--------|----------|
| 敏感数据存储 | Keychain (非 UserDefaults) |
| 网络传输 | HTTPS 强制 (ATS) |
| Token 管理 | Keychain 存储 + 自动刷新 |
| 代码混淆 | Swift 编译优化 + 第三方混淆工具 |
| 越狱检测 | 检测 Cydia、可写系统路径 |
| 调试检测 | 检测 ptrace、sysctl |
| 数据加密 | CryptoKit (AES-GCM) |

### 10.2 App Transport Security (ATS)

```xml
<!-- Info.plist — 默认强制 HTTPS，仅在必要时添加例外 -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>legacy-api.example.com</key>
        <dict>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSTemporaryExceptionMinimumTLSVersion</key>
            <string>TLSv1.2</string>
        </dict>
    </dict>
</dict>
```

> 上架审核时，使用 `NSAllowsArbitraryLoads` 需要提供合理说明，否则可能被拒。

### 10.3 数据加密 (CryptoKit)

```swift
import CryptoKit

enum CryptoHelper {
    static func encrypt(data: Data, using key: SymmetricKey) throws -> Data {
        let sealedBox = try AES.GCM.seal(data, using: key)
        guard let combined = sealedBox.combined else {
            throw CryptoError.encryptionFailed
        }
        return combined
    }

    static func decrypt(data: Data, using key: SymmetricKey) throws -> Data {
        let sealedBox = try AES.GCM.SealedBox(combined: data)
        return try AES.GCM.open(sealedBox, using: key)
    }

    static func generateKey() -> SymmetricKey {
        SymmetricKey(size: .bits256)
    }

    static func hash(_ string: String) -> String {
        let data = Data(string.utf8)
        let digest = SHA256.hash(data: data)
        return digest.map { String(format: "%02x", $0) }.joined()
    }
}
```

### 10.4 越狱检测

```swift
enum JailbreakDetector {
    static var isJailbroken: Bool {
        #if targetEnvironment(simulator)
        return false
        #else
        let suspiciousPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/"
        ]
        for path in suspiciousPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }
        // 检测是否可以写入系统目录
        let testPath = "/private/jailbreak_test"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testPath)
            return true
        } catch {
            return false
        }
        #endif
    }
}
```
---

## 11. 发布流程

### 11.1 发布前检查清单

- [ ] 版本号 (CFBundleShortVersionString) 和 Build 号 (CFBundleVersion) 已更新
- [ ] 所有 TODO/FIXME 已处理
- [ ] Release 配置下编译通过，无 Warning
- [ ] 所有测试通过
- [ ] 隐私清单 (PrivacyInfo.xcprivacy) 已配置
- [ ] App Icons 和 Launch Screen 已设置
- [ ] 内存泄漏检测通过
- [ ] 敏感信息未硬编码

### 11.2 Archive 与上传

```
步骤：
1. Xcode → Product → Scheme → 选择 Release
2. 选择目标设备为 "Any iOS Device (arm64)"
3. Product → Archive
4. Archive 成功后 → Organizer 窗口自动打开
5. 选择 Archive → Distribute App
6. 选择 "App Store Connect" → Upload
7. 等待上传完成和 Apple 处理
```

**命令行方式 (CI/CD)：**

```bash
# 1. Archive
xcodebuild archive \
  -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -configuration Release \
  -archivePath ./build/MyApp.xcarchive \
  -destination "generic/platform=iOS"

# 2. 导出 IPA
xcodebuild -exportArchive \
  -archivePath ./build/MyApp.xcarchive \
  -exportPath ./build/ipa \
  -exportOptionsPlist ExportOptions.plist

# 3. 上传到 App Store Connect
xcrun altool --upload-app \
  -f ./build/ipa/MyApp.ipa \
  -t ios \
  -u "apple-id@example.com" \
  -p "@keychain:AC_PASSWORD"
```

### 11.3 TestFlight 测试

| 测试类型 | 人数上限 | 审核 | 适用场景 |
|----------|----------|------|----------|
| 内部测试 | 100 人 | 无需审核 | 团队内部快速验证 |
| 外部测试 | 10,000 人 | 需要 Beta 审核 | 公测、用户反馈收集 |

```
TestFlight 流程：
1. App Store Connect → 我的 App → TestFlight
2. 等待构建版本处理完成 (约 15-30 分钟)
3. 内部测试：直接添加内部测试员邮箱
4. 外部测试：创建测试组 → 添加构建版本 → 提交 Beta 审核
5. 审核通过后测试员收到邀请
```

### 11.4 App Store 提审

```
提审材料准备：
├── App 截图 (6.7" + 6.1" + 5.5" 各尺寸)
├── App 描述 (关键词优化)
├── 隐私政策 URL
├── 技术支持 URL
├── App 审核信息 (测试账号、特殊说明)
└── 年龄分级问卷
```

**常见拒审原因及应对：**

| 拒审原因 | 应对方案 |
|----------|----------|
| 2.1 性能 — 崩溃/Bug | 充分测试，提供稳定版本 |
| 2.3 元数据 — 截图不符 | 截图与实际功能一致 |
| 3.1.1 应用内购买 — 未使用 IAP | 虚拟商品必须使用 Apple IAP |
| 4.0 设计 — 功能过于简单 | 丰富功能，体现独特价值 |
| 5.1.1 隐私 — 未声明数据收集 | 完善隐私清单和隐私政策 |

---

## 附录：常用第三方库推荐

| 类别 | 库名 | 用途 |
|------|------|------|
| 网络 | Alamofire / Moya | HTTP 请求封装 |
| 图片 | Kingfisher / Nuke | 图片加载与缓存 |
| 布局 | SnapKit | UIKit Auto Layout DSL |
| JSON | SwiftyJSON | JSON 便捷解析 (Codable 优先) |
| 日志 | SwiftyBeaver / OSLog | 结构化日志 |
| 路由 | 自建 NavigationStack 方案 | 页面路由管理 |
| 数据库 | GRDB | SQLite 封装 |
| 键盘 | IQKeyboardManager | 键盘自动管理 |
| 加载 | SkeletonView | 骨架屏 |
| Lint | SwiftLint | 代码规范检查 |

> 优先使用系统框架 (URLSession、SwiftData、MapKit 等)，仅在系统能力不足时引入第三方库。
