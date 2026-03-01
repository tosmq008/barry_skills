# 组件复用模式指南

> 本文档覆盖 iOS、Android、Web（Vue/React）、Flutter、微信小程序六大平台的组件复用最佳实践。

---

## 1. 组件化设计原则

### 1.1 SOLID 原则在组件中的应用

| 原则 | 组件化解读 | 反模式 |
|------|-----------|--------|
| 单一职责 (SRP) | 一个组件只做一件事，如 `Avatar` 只负责头像展示 | 一个组件同时处理展示、请求、缓存 |
| 开闭原则 (OCP) | 通过 Props/Slot 扩展行为，而非修改组件源码 | 在组件内部用 `if/else` 堆砌业务分支 |
| 里氏替换 (LSP) | 子组件可无缝替换父组件，接口保持兼容 | 子组件删除父组件已有的 Props |
| 接口隔离 (ISP) | 组件 Props 按职责拆分，避免巨型接口 | 一个组件接收 30+ 个 Props |
| 依赖倒置 (DIP) | 组件依赖抽象（协议/接口），不依赖具体实现 | 组件内部直接 `import` 具体服务类 |

### 1.2 组件粒度划分（Atomic Design）

```
页面 (Page)
  └── 模板 (Template)        — 页面骨架布局
        └── 有机体 (Organism)  — 独立功能区块，如 Header、ProductList
              └── 分子 (Molecule) — 组合原子，如 SearchBar = Input + Button
                    └── 原子 (Atom)   — 最小 UI 单元，如 Button、Icon、Text
```

| 层级 | 特征 | 示例 | 可复用范围 |
|------|------|------|-----------|
| 原子 | 无业务逻辑，纯 UI | `Button`, `Icon`, `Badge` | 全局 |
| 分子 | 组合原子，轻量交互 | `SearchBar`, `FormField` | 全局 |
| 有机体 | 包含业务逻辑的区块 | `UserCard`, `OrderItem` | 业务域内 |
| 模板 | 页面布局骨架 | `DashboardLayout` | 项目内 |
| 页面 | 绑定路由与数据源 | `HomePage`, `ProfilePage` | 不复用 |

### 1.3 组件接口设计规范

**命名规则：**

```
- Props 使用 camelCase（Web）或 snake_case（Flutter/小程序）
- 布尔值以 is/has/can/should 开头：isDisabled, hasError, canSubmit
- 事件回调以 on 开头：onPress, onChange, onSubmit
- 插槽/Slot 以名词命名：header, footer, leading, trailing
```

**类型约束示例（TypeScript）：**

```typescript
interface ButtonProps {
  /** 按钮变体 */
  variant: 'primary' | 'secondary' | 'ghost' | 'danger'
  /** 尺寸 */
  size?: 'sm' | 'md' | 'lg'
  /** 是否禁用 */
  isDisabled?: boolean
  /** 是否加载中 */
  isLoading?: boolean
  /** 点击回调 */
  onPress?: () => void
  /** 左侧图标 */
  leadingIcon?: ReactNode
}
```

**默认值策略：**

| 策略 | 说明 |
|------|------|
| 安全默认值 | `isDisabled = false`，组件默认可用 |
| 最小惊讶 | `size = 'md'`，中等尺寸最常用 |
| 可选优先 | 非核心 Props 全部可选，降低使用门槛 |

---

## 2. 各平台组件复用模式

### 2.1 iOS（SwiftUI / UIKit）

#### Protocol + Generic — 抽象组件行为

```swift
protocol ListItemRepresentable {
    associatedtype Content: View
    var id: String { get }
    func makeBody() -> Content
}

// 泛型列表组件，接受任何符合协议的数据
struct GenericListView<Item: ListItemRepresentable>: View {
    let items: [Item]
    let onSelect: (Item) -> Void

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 8) {
                ForEach(items, id: \.id) { item in
                    item.makeBody()
                        .onTapGesture { onSelect(item) }
                }
            }
        }
    }
}
```

#### ViewModifier — 可组合的样式/行为修饰

```swift
struct CardModifier: ViewModifier {
    var cornerRadius: CGFloat = 12
    var shadowRadius: CGFloat = 4

    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(Color.white)
            .cornerRadius(cornerRadius)
            .shadow(radius: shadowRadius)
    }
}

extension View {
    func cardStyle(corner: CGFloat = 12, shadow: CGFloat = 4) -> some View {
        modifier(CardModifier(cornerRadius: corner, shadowRadius: shadow))
    }
}

// 使用
Text("Hello").cardStyle()
```

#### PropertyWrapper — 封装可复用状态逻辑

```swift
@propertyWrapper
struct Debounced<Value> {
    private var value: Value
    private var delay: TimeInterval
    private var task: Task<Void, Never>?

    var wrappedValue: Value {
        get { value }
        set {
            task?.cancel()
            task = Task {
                try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                guard !Task.isCancelled else { return }
                value = newValue
            }
        }
    }

    init(wrappedValue: Value, delay: TimeInterval = 0.3) {
        self.value = wrappedValue
        self.delay = delay
    }
}
```

### 2.2 Android（Jetpack Compose）

#### Compose Modifier — 链式样式复用

```kotlin
// 自定义 Modifier 扩展
fun Modifier.cardStyle(
    cornerRadius: Dp = 12.dp,
    elevation: Dp = 4.dp
): Modifier = this
    .padding(16.dp)
    .shadow(elevation, RoundedCornerShape(cornerRadius))
    .background(Color.White, RoundedCornerShape(cornerRadius))

// 使用
Text("Hello", modifier = Modifier.cardStyle())
```

#### Slot API — 灵活的内容插槽

```kotlin
@Composable
fun AppBar(
    title: @Composable () -> Unit,
    leading: @Composable (() -> Unit)? = null,
    trailing: @Composable (() -> Unit)? = null,
) {
    Row(
        modifier = Modifier.fillMaxWidth().height(56.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        leading?.invoke()
        Box(modifier = Modifier.weight(1f)) { title() }
        trailing?.invoke()
    }
}

// 使用 — 插槽内容完全由调用方决定
AppBar(
    title = { Text("首页") },
    leading = { IconButton(onClick = {}) { Icon(Icons.Default.Menu, null) } },
    trailing = { IconButton(onClick = {}) { Icon(Icons.Default.Search, null) } }
)
```

#### CompositionLocal — 跨层级隐式传参

```kotlin
val LocalAppTheme = compositionLocalOf<AppTheme> { error("No theme provided") }

@Composable
fun AppThemeProvider(theme: AppTheme, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppTheme provides theme) {
        content()
    }
}

// 任意子组件中获取
@Composable
fun ThemedButton(text: String, onClick: () -> Unit) {
    val theme = LocalAppTheme.current
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(containerColor = theme.primaryColor)
    ) { Text(text) }
}
```

### 2.3 Web — Vue

#### Composables — 可组合的状态逻辑

```typescript
// useDebounce.ts
export function useDebounce<T>(value: Ref<T>, delay: number = 300): Ref<T> {
  const debounced = ref(value.value) as Ref<T>
  let timer: ReturnType<typeof setTimeout>

  watch(value, (newVal) => {
    clearTimeout(timer)
    timer = setTimeout(() => { debounced.value = newVal }, delay)
  })

  return debounced
}

// usePagination.ts
export function usePagination(fetchFn: (page: number) => Promise<PageResult>) {
  const page = ref(1)
  const list = ref<unknown[]>([])
  const isLoading = ref(false)
  const hasMore = ref(true)

  async function loadNext() {
    if (isLoading.value || !hasMore.value) return
    isLoading.value = true
    try {
      const result = await fetchFn(page.value)
      list.value = [...list.value, ...result.items]
      hasMore.value = result.hasMore
      page.value += 1
    } finally {
      isLoading.value = false
    }
  }

  return { list, isLoading, hasMore, loadNext }
}
```

#### Provide / Inject — 跨层级依赖注入

```typescript
// 提供方
const ThemeKey: InjectionKey<Ref<Theme>> = Symbol('theme')

export function provideTheme(theme: Ref<Theme>) {
  provide(ThemeKey, theme)
}

// 消费方
export function useTheme(): Ref<Theme> {
  const theme = inject(ThemeKey)
  if (!theme) throw new Error('Theme not provided')
  return theme
}
```

#### Render Functions — 动态组件生成

```typescript
// 动态表单渲染器
function FormRenderer(props: { schema: FormField[] }) {
  return () =>
    h('form', {},
      props.schema.map((field) => {
        switch (field.type) {
          case 'text':
            return h(BaseInput, { label: field.label, modelValue: field.value })
          case 'select':
            return h(BaseSelect, { label: field.label, options: field.options })
          default:
            return null
        }
      })
    )
}
```

### 2.4 Web — React

#### Custom Hooks — 封装可复用逻辑

```tsx
function useAsync<T>(asyncFn: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<{
    data: T | null
    error: Error | null
    isLoading: boolean
  }>({ data: null, error: null, isLoading: true })

  useEffect(() => {
    let cancelled = false
    setState((prev) => ({ ...prev, isLoading: true }))
    asyncFn()
      .then((data) => { if (!cancelled) setState({ data, error: null, isLoading: false }) })
      .catch((error) => { if (!cancelled) setState({ data: null, error, isLoading: false }) })
    return () => { cancelled = true }
  }, deps)

  return state
}
```

#### Compound Components — 组合式组件 API

```tsx
// 对外暴露语义化子组件，内部通过 Context 共享状态
const TabsContext = createContext<{ active: string; setActive: (v: string) => void } | null>(null)

function Tabs({ defaultValue, children }: { defaultValue: string; children: ReactNode }) {
  const [active, setActive] = useState(defaultValue)
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  )
}

function TabList({ children }: { children: ReactNode }) {
  return <div role="tablist">{children}</div>
}

function Tab({ value, children }: { value: string; children: ReactNode }) {
  const ctx = useContext(TabsContext)
  if (!ctx) throw new Error('Tab must be used within Tabs')
  return (
    <button role="tab" aria-selected={ctx.active === value} onClick={() => ctx.setActive(value)}>
      {children}
    </button>
  )
}

function TabPanel({ value, children }: { value: string; children: ReactNode }) {
  const ctx = useContext(TabsContext)
  if (!ctx) throw new Error('TabPanel must be used within Tabs')
  if (ctx.active !== value) return null
  return <div role="tabpanel">{children}</div>
}

Tabs.List = TabList
Tabs.Tab = Tab
Tabs.Panel = TabPanel

// 使用
<Tabs defaultValue="a">
  <Tabs.List>
    <Tabs.Tab value="a">标签A</Tabs.Tab>
    <Tabs.Tab value="b">标签B</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="a">内容A</Tabs.Panel>
  <Tabs.Panel value="b">内容B</Tabs.Panel>
</Tabs>
```

#### HOC — 高阶组件（横切关注点）

```tsx
function withAuth<P extends object>(WrappedComponent: ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading } = useAuth()
    if (isLoading) return <Spinner />
    if (!isAuthenticated) return <Navigate to="/login" />
    return <WrappedComponent {...props} />
  }
}

const ProtectedDashboard = withAuth(Dashboard)
```

### 2.5 Flutter

#### Mixin — 复用 State 逻辑

```dart
mixin AutoDisposeMixin<T extends StatefulWidget> on State<T> {
  final List<StreamSubscription> _subscriptions = [];

  void autoDispose(StreamSubscription sub) {
    _subscriptions.add(sub);
  }

  @override
  void dispose() {
    for (final sub in _subscriptions) {
      sub.cancel();
    }
    super.dispose();
  }
}

class MyPageState extends State<MyPage> with AutoDisposeMixin {
  @override
  void initState() {
    super.initState();
    autoDispose(stream.listen((data) { /* handle */ }));
  }
}
```

#### InheritedWidget — 跨层级数据共享

```dart
class AppConfig extends InheritedWidget {
  final String apiBaseUrl;
  final ThemeData theme;

  const AppConfig({
    required this.apiBaseUrl,
    required this.theme,
    required super.child,
  });

  static AppConfig of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<AppConfig>()!;
  }

  @override
  bool updateShouldNotify(AppConfig oldWidget) {
    return apiBaseUrl != oldWidget.apiBaseUrl || theme != oldWidget.theme;
  }
}

// 任意子 Widget 中获取
final config = AppConfig.of(context);
```

#### Extension — 为现有类型添加组件工具方法

```dart
extension WidgetPaddingX on Widget {
  Widget paddingAll(double value) => Padding(padding: EdgeInsets.all(value), child: this);
  Widget paddingH(double value) => Padding(
    padding: EdgeInsets.symmetric(horizontal: value), child: this,
  );
  Widget paddingV(double value) => Padding(
    padding: EdgeInsets.symmetric(vertical: value), child: this,
  );
}

// 使用
Text('Hello').paddingAll(16).paddingH(8)
```

### 2.6 微信小程序

#### Behavior — 组件逻辑复用

```javascript
// behaviors/pagination.js
module.exports = Behavior({
  data: {
    list: [],
    page: 1,
    isLoading: false,
    hasMore: true,
  },
  methods: {
    async loadNext() {
      if (this.data.isLoading || !this.data.hasMore) return
      this.setData({ isLoading: true })
      try {
        const res = await this.fetchPage(this.data.page)
        this.setData({
          list: [...this.data.list, ...res.items],
          page: this.data.page + 1,
          hasMore: res.hasMore,
        })
      } finally {
        this.setData({ isLoading: false })
      }
    },
  },
})

// 组件中使用
Component({
  behaviors: [require('../../behaviors/pagination')],
  methods: {
    fetchPage(page) {
      return api.getOrders({ page, limit: 20 })
    },
  },
})
```

#### 外部样式类 — 样式定制化

```javascript
// components/card/card.js
Component({
  externalClasses: ['custom-class', 'title-class', 'content-class'],
})
```

```html
<!-- components/card/card.wxml -->
<view class="card custom-class">
  <text class="card__title title-class">{{title}}</text>
  <view class="card__content content-class">
    <slot></slot>
  </view>
</view>

<!-- 使用方 -->
<card title="订单" custom-class="my-card" title-class="my-title" />
```

#### 抽象节点 — 运行时组件替换

```json
{
  "componentGenerics": {
    "list-item": {
      "default": "components/default-item/index"
    }
  }
}
```

```html
<!-- generic-list.wxml -->
<view wx:for="{{items}}" wx:key="id">
  <list-item item="{{item}}" />
</view>

<!-- 使用方可替换具体实现 -->
<generic-list items="{{orders}}" generic:list-item="order-item" />
<generic-list items="{{products}}" generic:list-item="product-item" />
```

---

## 3. 跨平台组件规范

### 3.1 统一组件命名规范

| 类别 | 规则 | 示例 |
|------|------|------|
| 基础组件 | `Base` 前缀 | `BaseButton`, `BaseInput`, `BaseModal` |
| 业务组件 | 业务域 + 功能 | `UserAvatar`, `OrderCard`, `PaymentForm` |
| 布局组件 | `Layout` 后缀 | `DashboardLayout`, `AuthLayout` |
| 页面组件 | `Page/Screen` 后缀 | `HomePage`, `ProfileScreen` |

**各平台命名映射：**

```
跨平台名称       iOS(Swift)        Android(Kotlin)    Web(Vue/React)     Flutter(Dart)      小程序
─────────────────────────────────────────────────────────────────────────────────────────────────
BaseButton      BaseButton        BaseButton         BaseButton.vue     BaseButton         base-button
UserCard        UserCardView      UserCard           UserCard.vue       UserCard           user-card
OrderList       OrderListView     OrderListScreen    OrderList.vue      OrderListPage      order-list
```

### 3.2 统一 Props / 参数设计规范

所有平台遵循相同的参数语义，仅语法不同：

```
参数名          类型              默认值     说明
──────────────────────────────────────────────────
variant        enum             'primary'  视觉变体
size           enum             'md'       尺寸
isDisabled     boolean          false      是否禁用
isLoading      boolean          false      是否加载中
label          string           ''         文本标签
onPress        callback         null       点击回调
```

### 3.3 统一事件 / 回调命名规范

| 事件语义 | 命名 | 各平台实现 |
|---------|------|-----------|
| 点击 | `onPress` | iOS: action closure / Android: onClick / Web: @click / Flutter: onPressed |
| 值变更 | `onChange` | iOS: Binding / Android: onValueChange / Web: @update:modelValue / Flutter: onChanged |
| 提交 | `onSubmit` | 各平台统一 |
| 关闭 | `onClose` | 各平台统一 |
| 滚动到底 | `onReachEnd` | 各平台统一 |

### 3.4 统一样式 Token 映射

```
Token 名称              值                  用途
────────────────────────────────────────────────────
color-primary          #1677FF             主色
color-success          #52C41A             成功
color-warning          #FAAD14             警告
color-danger           #FF4D4F             危险
color-text-primary     #1F1F1F             主文本
color-text-secondary   #8C8C8C             次要文本
color-bg-primary       #FFFFFF             主背景
color-bg-secondary     #F5F5F5             次要背景

spacing-xs             4px                 极小间距
spacing-sm             8px                 小间距
spacing-md             16px                中间距
spacing-lg             24px                大间距
spacing-xl             32px                极大间距

radius-sm              4px                 小圆角
radius-md              8px                 中圆角
radius-lg              16px                大圆角
radius-full            9999px              全圆角

font-size-xs           12px                极小字号
font-size-sm           14px                小字号
font-size-md           16px                中字号
font-size-lg           18px                大字号
font-size-xl           24px                标题字号
```

---

## 4. 组件库建设

### 4.1 基础组件库

基础组件是与业务无关的通用 UI 组件，所有项目共享。

| 组件 | 功能 | 关键 Props |
|------|------|-----------|
| `BaseButton` | 按钮 | variant, size, isDisabled, isLoading, onPress |
| `BaseInput` | 输入框 | type, placeholder, value, onChange, isError |
| `BaseModal` | 弹窗 | isVisible, title, onClose, onConfirm |
| `BaseToast` | 轻提示 | message, type, duration |
| `BaseList` | 列表 | items, renderItem, onReachEnd, isLoading |
| `BaseImage` | 图片 | src, fallback, aspectRatio, onLoad, onError |
| `BaseTabs` | 标签页 | items, activeKey, onChange |
| `BaseSwitch` | 开关 | isChecked, onChange, isDisabled |
| `BaseTag` | 标签 | text, variant, isClosable, onClose |
| `BaseSkeleton` | 骨架屏 | width, height, variant(text/circle/rect) |

**基础组件设计原则：**

```
1. 零业务依赖 — 不引入任何业务模块
2. 完全受控   — 状态由外部传入，组件本身无副作用
3. 样式隔离   — 使用 Token 变量，不硬编码颜色/尺寸
4. 无障碍支持 — 提供 aria-label / accessibilityLabel
5. 主题适配   — 支持 Light/Dark 模式切换
```

### 4.2 业务组件库

业务组件封装特定业务领域的 UI 与交互逻辑。

```
business-components/
├── user/
│   ├── UserAvatar          — 用户头像（含等级角标）
│   ├── UserCard            — 用户信息卡片
│   └── UserListItem        — 用户列表项
├── order/
│   ├── OrderCard           — 订单卡片
│   ├── OrderStatusBadge    — 订单状态标签
│   └── OrderTimeline       — 订单时间线
├── payment/
│   ├── PaymentMethodPicker — 支付方式选择器
│   ├── PriceDisplay        — 价格展示（含货币符号/折扣）
│   └── PaymentForm         — 支付表单
└── product/
    ├── ProductCard         — 商品卡片
    ├── ProductGallery      — 商品图片画廊
    └── SkuSelector         — SKU 选择器
```

### 4.3 组件文档与示例

每个组件必须包含以下文档内容：

```markdown
## ComponentName

### 概述
一句话描述组件用途。

### 基础用法
最简使用示例。

### Props
| 参数 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|

### Events
| 事件名 | 参数 | 说明 |
|--------|------|------|

### Slots（如适用）
| 插槽名 | 说明 |
|--------|------|

### 主题变量
| 变量名 | 默认值 | 说明 |
|--------|--------|------|

### 变体示例
展示所有 variant / size 组合的可视化示例。

### 最佳实践
推荐用法与常见误用。
```

### 4.4 版本管理与发布

```
版本号规则：MAJOR.MINOR.PATCH

MAJOR — 不兼容的 API 变更（删除 Props、修改默认行为）
MINOR — 向后兼容的新功能（新增 Props、新增组件）
PATCH — 向后兼容的缺陷修复

发布流程：
1. 功能开发 → feature 分支
2. 代码审查 → PR Review
3. 自动化测试 → CI 通过
4. 版本号更新 → CHANGELOG 记录
5. 发布 → npm publish / CocoaPods push / Maven publish
6. 文档同步 → Storybook / 组件文档站更新
```

---

## 5. 状态管理与组件通信

### 5.1 父子通信（Props / Callback）

最基础的通信方式，适用于直接父子关系。

**各平台实现对比：**

```swift
// iOS — 闭包回调
struct ChildView: View {
    let count: Int
    let onIncrement: () -> Void

    var body: some View {
        Button("Count: \(count)") { onIncrement() }
    }
}
```

```kotlin
// Android — Lambda 回调
@Composable
fun ChildView(count: Int, onIncrement: () -> Unit) {
    Button(onClick = onIncrement) { Text("Count: $count") }
}
```

```vue
<!-- Vue — Props + Emit -->
<script setup>
defineProps<{ count: number }>()
const emit = defineEmits<{ increment: [] }>()
</script>
<template>
  <button @click="emit('increment')">Count: {{ count }}</button>
</template>
```

```tsx
// React — Props + Callback
function ChildView({ count, onIncrement }: { count: number; onIncrement: () => void }) {
  return <button onClick={onIncrement}>Count: {count}</button>
}
```

```dart
// Flutter — Constructor 参数 + VoidCallback
class ChildView extends StatelessWidget {
  final int count;
  final VoidCallback onIncrement;

  const ChildView({required this.count, required this.onIncrement});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(onPressed: onIncrement, child: Text('Count: $count'));
  }
}
```

### 5.2 兄弟通信（状态提升 / EventBus）

**状态提升（推荐）：** 将共享状态提升到最近公共父组件。

```
      ParentView (持有 state)
       /          \
  ChildA          ChildB
  (读 state)      (写 state via callback)
```

**EventBus（谨慎使用）：** 适用于松耦合的跨模块通知。

```typescript
// 简易 EventBus 实现
type Handler = (...args: unknown[]) => void

class EventBus {
  private handlers = new Map<string, Set<Handler>>()

  on(event: string, handler: Handler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set())
    }
    this.handlers.get(event)!.add(handler)
    return () => this.handlers.get(event)?.delete(handler)
  }

  emit(event: string, ...args: unknown[]): void {
    this.handlers.get(event)?.forEach((handler) => handler(...args))
  }
}
```

> **注意：** EventBus 会导致数据流难以追踪，仅在以下场景使用：
> - 全局通知（网络状态变化、登录/登出）
> - 跨模块的松耦合事件（埋点、日志）

### 5.3 跨层通信（Context / Provider / InheritedWidget）

适用于需要跨越多层组件传递的数据（主题、国际化、用户信息）。

| 平台 | 机制 | 适用场景 |
|------|------|---------|
| iOS | `@Environment` / `@EnvironmentObject` | 主题、用户偏好 |
| Android | `CompositionLocal` | 主题、导航、配置 |
| Vue | `provide` / `inject` | 主题、服务注入 |
| React | `Context` + `useContext` | 主题、认证状态 |
| Flutter | `InheritedWidget` / `Provider` | 主题、全局配置 |
| 小程序 | `getApp().globalData` / 页面间通信 | 全局配置 |

### 5.4 全局状态（Store / BLoC / Pinia）

适用于复杂应用的全局状态管理。

| 平台 | 推荐方案 | 特点 |
|------|---------|------|
| iOS | TCA (The Composable Architecture) | 单向数据流、可测试 |
| Android | ViewModel + StateFlow | 生命周期感知、协程支持 |
| Vue | Pinia | 类型安全、DevTools 支持 |
| React | Zustand / Jotai | 轻量、无 Provider 嵌套 |
| Flutter | BLoC / Riverpod | 事件驱动、强类型 |
| 小程序 | MobX-miniprogram | 响应式、轻量 |

**全局状态使用原则：**

```
1. 最小化全局状态 — 能用局部状态解决的不要放全局
2. 单一数据源     — 同一份数据只在一个 Store 中管理
3. 不可变更新     — 通过新对象替换，不直接修改
4. 派生状态       — 用 computed/selector 派生，不冗余存储
5. 持久化分离     — 持久化逻辑与状态逻辑分离
```

---

## 6. 组件测试策略

### 6.1 组件单元测试

验证组件在给定 Props 下的渲染输出和行为。

```tsx
// React 示例 — @testing-library/react
describe('BaseButton', () => {
  it('should render label text', () => {
    render(<BaseButton label="Submit" onPress={() => {}} />)
    expect(screen.getByText('Submit')).toBeInTheDocument()
  })

  it('should call onPress when clicked', async () => {
    const onPress = vi.fn()
    render(<BaseButton label="Submit" onPress={onPress} />)
    await userEvent.click(screen.getByRole('button'))
    expect(onPress).toHaveBeenCalledOnce()
  })

  it('should not call onPress when disabled', async () => {
    const onPress = vi.fn()
    render(<BaseButton label="Submit" onPress={onPress} isDisabled />)
    await userEvent.click(screen.getByRole('button'))
    expect(onPress).not.toHaveBeenCalled()
  })

  it('should show loading spinner when isLoading', () => {
    render(<BaseButton label="Submit" onPress={() => {}} isLoading />)
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })
})
```

```dart
// Flutter 示例 — flutter_test
testWidgets('BaseButton renders label', (tester) async {
  await tester.pumpWidget(
    MaterialApp(home: BaseButton(label: 'Submit', onPressed: () {})),
  );
  expect(find.text('Submit'), findsOneWidget);
});

testWidgets('BaseButton calls onPressed', (tester) async {
  var pressed = false;
  await tester.pumpWidget(
    MaterialApp(home: BaseButton(label: 'Submit', onPressed: () { pressed = true; })),
  );
  await tester.tap(find.text('Submit'));
  expect(pressed, isTrue);
});
```

### 6.2 快照测试

捕获组件渲染输出的快照，检测意外的 UI 变更。

```tsx
// React 快照测试
it('should match snapshot for primary variant', () => {
  const { container } = render(
    <BaseButton label="Submit" variant="primary" onPress={() => {}} />
  )
  expect(container.firstChild).toMatchSnapshot()
})

it('should match snapshot for disabled state', () => {
  const { container } = render(
    <BaseButton label="Submit" isDisabled onPress={() => {}} />
  )
  expect(container.firstChild).toMatchSnapshot()
})
```

> **快照测试注意事项：**
> - 快照文件需纳入版本管理
> - 定期审查快照变更，避免盲目更新
> - 不要对频繁变化的内容（时间戳、随机 ID）做快照

### 6.3 交互测试

验证用户操作流程和组件间的交互行为。

```tsx
// React 交互测试 — 表单提交流程
describe('PaymentForm', () => {
  it('should submit valid form data', async () => {
    const onSubmit = vi.fn()
    render(<PaymentForm onSubmit={onSubmit} />)

    await userEvent.type(screen.getByLabelText('卡号'), '4242424242424242')
    await userEvent.type(screen.getByLabelText('有效期'), '12/25')
    await userEvent.type(screen.getByLabelText('CVV'), '123')
    await userEvent.click(screen.getByRole('button', { name: '确认支付' }))

    expect(onSubmit).toHaveBeenCalledWith({
      cardNumber: '4242424242424242',
      expiry: '12/25',
      cvv: '123',
    })
  })

  it('should show validation errors for empty fields', async () => {
    render(<PaymentForm onSubmit={() => {}} />)
    await userEvent.click(screen.getByRole('button', { name: '确认支付' }))

    expect(screen.getByText('请输入卡号')).toBeInTheDocument()
    expect(screen.getByText('请输入有效期')).toBeInTheDocument()
    expect(screen.getByText('请输入CVV')).toBeInTheDocument()
  })
})
```

**各平台测试工具对照：**

| 平台 | 单元测试 | 快照测试 | 交互/E2E 测试 |
|------|---------|---------|--------------|
| iOS | XCTest | SwiftUI Preview Tests | XCUITest |
| Android | JUnit + Compose Testing | Paparazzi | Espresso / UI Automator |
| Vue | Vitest + @vue/test-utils | Vitest Snapshot | Playwright / Cypress |
| React | Vitest + @testing-library/react | Vitest Snapshot | Playwright / Cypress |
| Flutter | flutter_test | Golden Tests | integration_test |
| 小程序 | miniprogram-simulate | — | Minium |

---

## 附录：组件复用决策树

```
需要复用逻辑？
├── 是 → 逻辑是否涉及 UI？
│   ├── 否 → 使用 Hook / Composable / Mixin / Behavior
│   └── 是 → 是否需要控制渲染结构？
│       ├── 否 → 使用 Modifier / ViewModifier / 外部样式类
│       └── 是 → 是否需要多个可替换区域？
│           ├── 否 → 使用 HOC / 高阶组件
│           └── 是 → 使用 Compound Components / Slot API / 抽象节点
└── 否 → 直接编写组件，不过度抽象
```