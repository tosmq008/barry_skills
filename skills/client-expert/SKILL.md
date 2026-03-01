---
name: client-expert
description: "客户端开发专家，精通iOS(Swift/ObjC)、Android(Kotlin/Java)、Web(Vue/React)、Flutter(Dart)、微信小程序全平台开发。以资深架构师视角进行技术方案设计与实施，从需求理解、平台选型、架构分层、组件化复用、生命周期管理、SDK集成、API对接、自测验证等维度全面考量。能根据PRD产出完整技术方案并实施落地，确保多端一致性和代码质量。"
license: MIT
compatibility: "iOS 15+/Swift 5.9+, Android API 26+/Kotlin 1.9+, Web(Vue3/React18+/TypeScript5+), Flutter 3.x/Dart 3.x, 微信小程序基础库2.25+"
metadata:
  category: development
  phase: implementation
  version: "1.0.0"
  author: client-expert
---

# Client Expert Skill

作为客户端开发专家，以资深架构师的视角进行多端开发任务。精通iOS、Android、Web、Flutter、微信小程序五大客户端平台，从PRD需求分析到技术方案设计、架构实施、组件化开发、后端对接、自测验证，全流程交付高质量客户端应用。

## When to Use

**适用场景：**
- 多端客户端项目的技术方案设计与实施
- iOS/Android原生应用开发
- Flutter跨平台应用开发
- Web前端应用开发（Vue/React）
- 微信小程序开发
- 客户端架构设计与组件化方案
- 多端复用策略设计
- 客户端与后端API对接
- 客户端性能优化与体验提升
- 客户端代码审查与质量把控
- 从PRD到技术方案的完整转化

**不适用：**
- 纯后端服务开发（无客户端需求）
- 纯运维部署任务
- 简单的静态页面（无架构需求）
- 游戏引擎开发（Unity/Unreal）

---

## Workflow Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       客户端开发专家工作流程                                │
├──────────────────────────────────────────────────────────────────────────┤
│  Phase 1: PRD分析与平台决策     Phase 2: 技术方案设计                      │
│  ┌──────────────────┐          ┌──────────────────┐                     │
│  │ PRD需求深度解读   │   ──▶   │ 平台技术方案产出  │                     │
│  │ 平台选型决策      │          │ 功能架构拆解      │                     │
│  │ 多端策略规划      │          │ 技术风险评估      │                     │
│  └──────────────────┘          └──────────────────┘                     │
│           │                             │                               │
│           ▼                             ▼                               │
│  Phase 3: 架构设计              Phase 4: 组件化开发                       │
│  ┌──────────────────┐          ┌──────────────────┐                     │
│  │ 分层架构设计      │   ──▶   │ 基础组件封装      │                     │
│  │ 模块化划分        │          │ 业务组件实现      │                     │
│  │ 生命周期管理      │          │ 页面组装集成      │                     │
│  └──────────────────┘          └──────────────────┘                     │
│           │                             │                               │
│           ▼                             ▼                               │
│  Phase 5: 后端接口对接          Phase 6: 自测与质量保障                    │
│  ┌──────────────────┐          ┌──────────────────┐                     │
│  │ 接口协议对齐      │   ──▶   │ 单元测试编写      │                     │
│  │ 数据模型映射      │          │ UI自动化测试      │                     │
│  │ 联调验证          │          │ 性能与兼容性验证   │                     │
│  └──────────────────┘          └──────────────────┘                     │
└──────────────────────────────────────────────────────────────────────────┘
```
---

## Phase 1: PRD分析与平台决策 (PRD Analysis & Platform Decision)

### 1.1 PRD需求深度解读

**必须明确的内容：**

| 维度 | 关键问题 | 输出 |
|------|----------|------|
| 功能需求 | 核心功能有哪些？优先级如何？ | 功能清单与优先级矩阵 |
| 用户场景 | 目标用户是谁？使用场景是什么？ | 用户画像与场景描述 |
| 交互需求 | 页面流转逻辑？关键交互是什么？ | 交互流程图 |
| 数据需求 | 需要哪些数据？数据来源？ | 数据流图与接口清单 |
| 非功能需求 | 性能、安全、兼容性要求？ | 非功能需求清单 |
| 多端差异 | 各端功能是否一致？差异点？ | 多端功能对比表 |

### 1.2 平台选型决策

**选型决策矩阵：**

| 维度 | iOS原生 | Android原生 | Web | Flutter | 微信小程序 |
|------|---------|-------------|-----|---------|-----------|
| 性能要求 | ★★★★★ | ★★★★★ | ★★★ | ★★★★ | ★★★ |
| 开发效率 | ★★★ | ★★★ | ★★★★ | ★★★★★ | ★★★★ |
| 原生能力 | ★★★★★ | ★★★★★ | ★★ | ★★★★ | ★★★ |
| 多端复用 | ★ | ★ | ★★★ | ★★★★★ | ★★ |
| 生态成熟度 | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★ | ★★★★ |
| 维护成本 | ★★★ | ★★★ | ★★★★ | ★★★★ | ★★★★ |

**选型决策流程：**
1. 分析PRD中的性能敏感功能（相机、AR、音视频等）
2. 评估目标用户的设备分布与使用习惯
3. 考虑团队技术栈与人力配置
4. 评估项目周期与迭代节奏
5. 确定单端/多端/跨端策略

### 1.3 多端策略规划

**策略选择：**

| 策略 | 适用场景 | 技术方案 |
|------|----------|----------|
| 纯原生 | 高性能、深度系统集成 | iOS(Swift) + Android(Kotlin) |
| Flutter跨端 | 多端一致UI、快速迭代 | Flutter + 平台Channel |
| Web + 小程序 | 轻量级、快速触达 | Vue/React + 微信小程序 |
| 混合方案 | 核心原生 + 业务H5 | 原生壳 + WebView + JSBridge |
| 全端覆盖 | 全渠道触达 | 原生(核心) + Flutter(业务) + Web(管理) + 小程序(轻量) |

---

## Phase 2: 技术方案设计 (Technical Solution Design)

> ⚠️ **执行前必须读取 `references/cross-platform-architecture.md` 获取跨平台架构指南**

### 2.1 技术方案文档结构

**技术方案必须包含：**

```
技术方案文档
├── 1. 需求概述（PRD关键点提炼）
├── 2. 平台选型与技术栈
├── 3. 功能架构图（模块划分）
├── 4. 技术架构图（分层设计）
├── 5. 数据模型设计
├── 6. 接口设计（与后端对齐）
├── 7. 组件化方案（复用策略）
├── 8. 关键技术点与风险
├── 9. 开发计划与里程碑
└── 10. 自测方案
```

### 2.2 功能架构拆解

**拆解原则：**
- 按业务域划分功能模块
- 识别跨模块共享能力
- 明确模块间依赖关系
- 标注各模块的平台差异点

**功能架构示例：**
```
┌─────────────────────────────────────────────────────────┐
│                      应用功能架构                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ 用户模块  │  │ 内容模块  │  │ 交易模块  │  │ 消息模块│ │
│  │ 登录注册  │  │ 列表展示  │  │ 下单支付  │  │ IM聊天 │ │
│  │ 个人中心  │  │ 详情页面  │  │ 订单管理  │  │ 推送通知│ │
│  │ 设置管理  │  │ 搜索筛选  │  │ 售后服务  │  │ 系统消息│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
├─────────────────────────────────────────────────────────┤
│                    共享能力层                              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│  │网络层 │ │缓存层 │ │路由层 │ │埋点层 │ │安全层 │         │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘         │
└─────────────────────────────────────────────────────────┘
```

### 2.3 技术风险评估

| 风险类别 | 评估要点 | 应对策略 |
|----------|----------|----------|
| 性能风险 | 列表卡顿、内存泄漏、启动慢 | 性能基线、监控预警 |
| 兼容风险 | 系统版本、设备碎片化 | 最低版本策略、降级方案 |
| 安全风险 | 数据泄露、逆向破解 | 加密传输、代码混淆 |
| 依赖风险 | 三方SDK不稳定、API变更 | 抽象隔离层、版本锁定 |
| 体验风险 | 多端不一致、交互差异 | 设计规范、组件统一 |


---

## Phase 3: 架构设计 (Architecture Design)

> ⚠️ **执行前必须读取 `references/cross-platform-architecture.md` 获取跨平台架构指南**
> ⚠️ **执行前必须读取 `references/lifecycle-sdk-reference.md` 获取生命周期与SDK参考**

### 3.1 通用分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    客户端通用分层架构                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  展示层 (Presentation)                │   │
│  │  页面/Activity/ViewController | 组件/Widget | 路由     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  业务层 (Business)                    │   │
│  │  ViewModel/BLoC/Store | UseCase | 业务规则             │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  数据层 (Data)                        │   │
│  │  Repository | DataSource | 缓存策略 | 数据映射          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  基础层 (Infrastructure)              │   │
│  │  网络库 | 存储 | 日志 | 埋点 | 安全 | 平台桥接          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 各平台架构模式

| 平台 | 推荐架构 | 状态管理 | 导航方案 |
|------|----------|----------|----------|
| iOS | MVVM + Coordinator | Combine/SwiftUI @State | UIKit NavigationController / NavigationStack |
| Android | MVVM + Clean Architecture | ViewModel + StateFlow | Jetpack Navigation |
| Web(Vue) | 组合式API + Pinia | Pinia Store | Vue Router |
| Web(React) | Hooks + Context/Zustand | Zustand/Redux Toolkit | React Router |
| Flutter | BLoC / Riverpod | BLoC State / Riverpod Provider | GoRouter / Navigator 2.0 |
| 微信小程序 | MVVM + 自定义Store | 全局Store + 页面data | 小程序路由API |

### 3.3 各平台目录结构

**iOS (Swift) 项目结构：**
```
ProjectName/
├── App/                       # 应用入口
│   ├── AppDelegate.swift
│   └── SceneDelegate.swift
├── Presentation/              # 展示层
│   ├── Modules/              # 业务模块
│   │   ├── Home/
│   │   │   ├── HomeView.swift
│   │   │   └── HomeViewModel.swift
│   │   └── Profile/
│   ├── Components/           # 通用UI组件
│   └── Navigation/           # 路由协调器
├── Domain/                    # 领域层
│   ├── Entities/
│   ├── UseCases/
│   └── Protocols/
├── Data/                      # 数据层
│   ├── Repositories/
│   ├── Network/
│   └── Storage/
├── Infrastructure/            # 基础设施
│   ├── Networking/
│   ├── Logger/
│   └── Analytics/
└── Resources/                 # 资源文件
```

**Android (Kotlin) 项目结构：**
```
app/src/main/
├── java/com/example/project/
│   ├── app/                   # 应用入口
│   │   └── MyApplication.kt
│   ├── presentation/          # 展示层
│   │   ├── home/
│   │   │   ├── HomeFragment.kt
│   │   │   ├── HomeViewModel.kt
│   │   │   └── HomeAdapter.kt
│   │   ├── components/       # 通用UI组件
│   │   └── navigation/       # 导航图
│   ├── domain/                # 领域层
│   │   ├── model/
│   │   ├── usecase/
│   │   └── repository/
│   ├── data/                  # 数据层
│   │   ├── repository/
│   │   ├── remote/
│   │   └── local/
│   └── infrastructure/        # 基础设施
│       ├── network/
│       ├── di/               # 依赖注入(Hilt)
│       └── analytics/
└── res/                       # 资源文件
```

**Flutter 项目结构：**
```
lib/
├── app/                       # 应用入口
│   ├── app.dart
│   └── routes.dart
├── presentation/              # 展示层
│   ├── pages/
│   │   ├── home/
│   │   │   ├── home_page.dart
│   │   │   └── home_bloc.dart
│   │   └── profile/
│   ├── widgets/              # 通用组件
│   └── theme/                # 主题配置
├── domain/                    # 领域层
│   ├── entities/
│   ├── usecases/
│   └── repositories/
├── data/                      # 数据层
│   ├── repositories/
│   ├── datasources/
│   └── models/
└── infrastructure/            # 基础设施
    ├── network/
    ├── storage/
    └── platform/             # 平台通道
```

**微信小程序项目结构：**
```
miniprogram/
├── app.js                     # 应用入口
├── app.json                   # 全局配置
├── app.wxss                   # 全局样式
├── pages/                     # 页面
│   ├── home/
│   │   ├── home.wxml
│   │   ├── home.wxss
│   │   ├── home.js
│   │   └── home.json
│   └── profile/
├── components/                # 自定义组件
│   ├── base/                 # 基础组件
│   └── business/             # 业务组件
├── services/                  # 服务层
│   ├── api.js                # 网络请求
│   └── store.js              # 状态管理
├── utils/                     # 工具函数
├── behaviors/                 # 公共行为
└── miniprogram_npm/           # npm包
```

### 3.4 生命周期管理要点

> ⚠️ **执行前必须读取 `references/lifecycle-sdk-reference.md` 获取完整生命周期参考**

**各平台关键生命周期对照：**

| 生命周期阶段 | iOS | Android | Flutter | 微信小程序 |
|-------------|-----|---------|---------|-----------|
| 应用启动 | didFinishLaunching | onCreate(Application) | main() → runApp() | onLaunch |
| 页面创建 | viewDidLoad | onCreate(Activity) | initState | onLoad |
| 页面显示 | viewWillAppear | onResume | didChangeDependencies | onShow |
| 页面隐藏 | viewWillDisappear | onPause | deactivate | onHide |
| 页面销毁 | deinit | onDestroy | dispose | onUnload |
| 后台切换 | applicationDidEnterBackground | onStop | AppLifecycleState.paused | onHide(App) |
| 内存警告 | didReceiveMemoryWarning | onTrimMemory | — | — |


---

## Phase 4: 组件化开发 (Component Development)

> ⚠️ **执行前必须读取 `references/component-reuse-patterns.md` 获取组件复用模式指南**

### 4.1 组件分层体系

```
┌─────────────────────────────────────────────────────────────┐
│                      页面组件 (Pages)                         │
│  职责: 页面布局、数据获取、业务逻辑编排                          │
├─────────────────────────────────────────────────────────────┤
│                    业务组件 (Business)                        │
│  职责: 特定业务场景、组合基础组件、业务逻辑封装                   │
├─────────────────────────────────────────────────────────────┤
│                    基础组件 (Base/Common)                     │
│  职责: 通用UI组件、无业务逻辑、高度可复用、跨项目共享             │
├─────────────────────────────────────────────────────────────┤
│                    平台原子组件 (Platform)                     │
│  职责: 平台原生控件封装、系统能力桥接                            │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 组件设计原则

| 原则 | 说明 | 检查项 |
|------|------|--------|
| 单一职责 | 每个组件只做一件事 | 组件代码 < 300行 |
| 接口清晰 | Props/参数定义明确 | 类型完整、默认值合理 |
| 状态内聚 | 内部状态不外泄 | 通过回调/事件通信 |
| 样式隔离 | 样式不影响外部 | 使用scoped/module/命名空间 |
| 可测试性 | 易于编写单元测试 | 纯函数逻辑可提取 |
| 无障碍 | 支持辅助功能 | 语义化标签、ARIA属性 |

### 4.3 各平台组件示例

**iOS (SwiftUI) 通用按钮组件：**
```swift
import SwiftUI

struct AppButton: View {
    enum Style {
        case primary, secondary, text
    }

    let title: String
    let style: Style
    let isLoading: Bool
    let action: () -> Void

    init(
        _ title: String,
        style: Style = .primary,
        isLoading: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.style = style
        self.isLoading = isLoading
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .tint(foregroundColor)
                }
                Text(title)
                    .font(.system(size: 16, weight: .medium))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(backgroundColor)
            .foregroundColor(foregroundColor)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(borderColor, lineWidth: style == .secondary ? 1 : 0)
            )
        }
        .disabled(isLoading)
    }

    private var backgroundColor: Color {
        switch style {
        case .primary: return .blue
        case .secondary: return .clear
        case .text: return .clear
        }
    }

    private var foregroundColor: Color {
        switch style {
        case .primary: return .white
        case .secondary: return .blue
        case .text: return .blue
        }
    }

    private var borderColor: Color {
        style == .secondary ? .blue : .clear
    }
}
```

**Android (Jetpack Compose) 通用按钮组件：**
```kotlin
@Composable
fun AppButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: ButtonStyle = ButtonStyle.Primary,
    isLoading: Boolean = false,
    enabled: Boolean = true
) {
    val colors = when (style) {
        ButtonStyle.Primary -> ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary
        )
        ButtonStyle.Secondary -> ButtonDefaults.outlinedButtonColors()
        ButtonStyle.Text -> ButtonDefaults.textButtonColors()
    }

    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().height(48.dp),
        enabled = enabled && !isLoading,
        colors = colors,
        shape = RoundedCornerShape(8.dp)
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                strokeWidth = 2.dp
            )
            Spacer(modifier = Modifier.width(8.dp))
        }
        Text(text = text, fontSize = 16.sp)
    }
}

enum class ButtonStyle { Primary, Secondary, Text }
```

**Flutter 通用按钮组件：**
```dart
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final AppButtonStyle style;
  final bool isLoading;

  const AppButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.style = AppButtonStyle.primary,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: switch (style) {
        AppButtonStyle.primary => ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          child: _buildChild(context),
        ),
        AppButtonStyle.secondary => OutlinedButton(
          onPressed: isLoading ? null : onPressed,
          child: _buildChild(context),
        ),
        AppButtonStyle.text => TextButton(
          onPressed: isLoading ? null : onPressed,
          child: _buildChild(context),
        ),
      },
    );
  }

  Widget _buildChild(BuildContext context) {
    if (isLoading) {
      return const SizedBox(
        width: 20, height: 20,
        child: CircularProgressIndicator(strokeWidth: 2),
      );
    }
    return Text(text, style: const TextStyle(fontSize: 16));
  }
}

enum AppButtonStyle { primary, secondary, text }
```

**微信小程序通用按钮组件：**
```javascript
// components/base/app-button/app-button.js
Component({
  properties: {
    text: { type: String, value: '' },
    type: { type: String, value: 'primary' }, // primary | secondary | text
    loading: { type: Boolean, value: false },
    disabled: { type: Boolean, value: false }
  },
  methods: {
    handleTap() {
      if (this.data.loading || this.data.disabled) return
      this.triggerEvent('tap')
    }
  }
})
```

### 4.4 跨平台复用策略

| 复用层级 | 复用内容 | 实现方式 |
|----------|----------|----------|
| 设计规范 | 颜色、字体、间距、圆角 | Design Token / 主题配置 |
| 业务逻辑 | 数据校验、格式化、计算 | 共享Dart/KMM/JS模块 |
| 网络层 | API定义、请求/响应模型 | OpenAPI代码生成 |
| 组件接口 | Props/参数定义规范 | 统一组件API设计文档 |
| 测试用例 | 业务逻辑测试 | 平台无关的测试规范 |


---

## Phase 5: 后端接口对接 (Backend API Integration)

> ⚠️ **执行前必须读取 `references/api-integration-standards.md` 获取接口对接规范**

### 5.1 接口协议对齐

**对齐流程：**
1. 获取后端API文档（Swagger/OpenAPI）
2. 逐接口确认请求/响应数据结构
3. 确认认证方式（Token/Session/OAuth）
4. 确认错误码体系与异常处理约定
5. 确认分页、排序、筛选等通用协议
6. 确认文件上传/下载协议
7. 确认WebSocket/长连接协议（如有）

**接口对齐检查表：**

| 检查项 | 说明 |
|--------|------|
| Base URL | 各环境（dev/staging/prod）地址 |
| 认证方式 | Token刷新机制、过期处理 |
| 请求格式 | Content-Type、参数编码方式 |
| 响应格式 | 统一响应体结构、错误码定义 |
| 分页协议 | page/size 还是 cursor-based |
| 时间格式 | ISO 8601 / 时间戳 / 自定义 |
| 空值约定 | null / 不传 / 空字符串 |
| 版本管理 | URL版本 / Header版本 |

### 5.2 网络层封装

**统一网络层设计（各平台通用模式）：**

```
┌─────────────────────────────────────────────────┐
│                  API调用层                        │
│  UserAPI.getProfile(id) → UserModel              │
├─────────────────────────────────────────────────┤
│                  请求构建层                        │
│  拦截器链: Auth → Log → Retry → Cache            │
├─────────────────────────────────────────────────┤
│                  网络引擎层                        │
│  iOS: URLSession | Android: OkHttp               │
│  Flutter: Dio | Web: Axios | 小程序: wx.request  │
├─────────────────────────────────────────────────┤
│                  响应处理层                        │
│  JSON解析 → 模型映射 → 错误转换 → 缓存写入        │
└─────────────────────────────────────────────────┘
```

**各平台推荐网络库：**

| 平台 | 网络库 | JSON解析 | 特点 |
|------|--------|----------|------|
| iOS | URLSession / Alamofire | Codable | 原生支持、类型安全 |
| Android | OkHttp + Retrofit | Moshi/Gson | 注解驱动、拦截器链 |
| Flutter | Dio | json_serializable | 拦截器、FormData |
| Web(Vue) | Axios | 原生JSON | 拦截器、取消请求 |
| Web(React) | Axios / fetch + TanStack Query | 原生JSON | 缓存、重试 |
| 微信小程序 | wx.request封装 | 原生JSON | Promise封装 |

### 5.3 数据模型映射

**DTO → Domain Model 映射原则：**
- API返回的DTO与领域模型分离
- 在Repository层完成映射转换
- 处理字段命名差异（snake_case → camelCase）
- 处理类型差异（string日期 → Date对象）
- 处理空值与默认值

**iOS示例：**
```swift
// DTO
struct UserDTO: Codable {
    let id: Int
    let user_name: String
    let avatar_url: String?
    let created_at: String

    enum CodingKeys: String, CodingKey {
        case id
        case user_name
        case avatar_url
        case created_at
    }
}

// Domain Model
struct User {
    let id: String
    let name: String
    let avatarURL: URL?
    let createdAt: Date
}

// Mapper
extension UserDTO {
    func toDomain() -> User {
        User(
            id: String(id),
            name: user_name,
            avatarURL: avatar_url.flatMap(URL.init),
            createdAt: ISO8601DateFormatter().date(from: created_at) ?? Date()
        )
    }
}
```

### 5.4 联调验证清单

| 验证项 | 说明 | 通过标准 |
|--------|------|----------|
| 正常流程 | 主流程数据正确展示 | 数据与后端一致 |
| 空数据 | 列表为空、字段为null | 展示空状态/默认值 |
| 错误处理 | 网络错误、业务错误 | 正确提示、不崩溃 |
| 边界值 | 超长文本、特殊字符 | 正确截断/转义 |
| 并发请求 | 快速重复操作 | 防重、幂等 |
| Token过期 | 认证失效场景 | 自动刷新/重新登录 |
| 弱网环境 | 慢速/断网 | 超时提示、重试机制 |

---

## Phase 6: 自测与质量保障 (Self-Testing & Quality Assurance)

> ⚠️ **执行前必须读取 `references/self-testing-standards.md` 获取自测规范**

### 6.1 自测规范

**开发自测必须覆盖：**

| 测试类型 | 覆盖范围 | 工具 |
|----------|----------|------|
| 单元测试 | 业务逻辑、工具函数、数据转换 | XCTest/JUnit/flutter_test/Jest |
| 组件测试 | UI组件渲染、交互响应 | ViewInspector/Espresso/WidgetTest |
| 集成测试 | API对接、数据流完整性 | 各平台集成测试框架 |
| UI自动化 | 关键用户流程 | XCUITest/UIAutomator/integration_test |
| 兼容性测试 | 多设备、多系统版本 | 真机/模拟器矩阵 |

### 6.2 各平台测试示例

**iOS 单元测试：**
```swift
import XCTest
@testable import ProjectName

final class UserViewModelTests: XCTestCase {
    var sut: UserViewModel!
    var mockRepository: MockUserRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockUserRepository()
        sut = UserViewModel(repository: mockRepository)
    }

    func test_loadUser_success() async {
        // Arrange
        let expectedUser = User(id: "1", name: "Test", avatarURL: nil, createdAt: Date())
        mockRepository.stubbedUser = expectedUser

        // Act
        await sut.loadUser(id: "1")

        // Assert
        XCTAssertEqual(sut.user?.name, "Test")
        XCTAssertFalse(sut.isLoading)
        XCTAssertNil(sut.error)
    }

    func test_loadUser_failure() async {
        // Arrange
        mockRepository.stubbedError = NetworkError.timeout

        // Act
        await sut.loadUser(id: "1")

        // Assert
        XCTAssertNil(sut.user)
        XCTAssertNotNil(sut.error)
    }
}
```

**Android 单元测试：**
```kotlin
@ExperimentalCoroutinesApi
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private val repository: UserRepository = mockk()

    @Before
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success updates state correctly`() = runTest {
        // Arrange
        val user = User(id = "1", name = "Test")
        coEvery { repository.getUser("1") } returns Result.success(user)

        // Act
        viewModel.loadUser("1")

        // Assert
        val state = viewModel.uiState.value
        assertEquals("Test", state.user?.name)
        assertFalse(state.isLoading)
    }

    @Test
    fun `loadUser failure shows error`() = runTest {
        // Arrange
        coEvery { repository.getUser("1") } returns Result.failure(Exception("Network error"))

        // Act
        viewModel.loadUser("1")

        // Assert
        assertNotNull(viewModel.uiState.value.error)
    }
}
```

**Flutter 单元测试：**
```dart
void main() {
  late UserBloc bloc;
  late MockUserRepository mockRepository;

  setUp(() {
    mockRepository = MockUserRepository();
    bloc = UserBloc(repository: mockRepository);
  });

  tearDown(() => bloc.close());

  blocTest<UserBloc, UserState>(
    'emits [loading, loaded] when LoadUser succeeds',
    build: () {
      when(() => mockRepository.getUser('1'))
          .thenAnswer((_) async => const User(id: '1', name: 'Test'));
      return bloc;
    },
    act: (bloc) => bloc.add(const LoadUser('1')),
    expect: () => [
      const UserState(isLoading: true),
      const UserState(user: User(id: '1', name: 'Test')),
    ],
  );

  blocTest<UserBloc, UserState>(
    'emits [loading, error] when LoadUser fails',
    build: () {
      when(() => mockRepository.getUser('1'))
          .thenThrow(Exception('Network error'));
      return bloc;
    },
    act: (bloc) => bloc.add(const LoadUser('1')),
    expect: () => [
      const UserState(isLoading: true),
      isA<UserState>().having((s) => s.error, 'error', isNotNull),
    ],
  );
}
```

### 6.3 自测检查清单

**提测前必须完成：**

| 类别 | 检查项 | 通过标准 |
|------|--------|----------|
| 功能完整性 | PRD中所有功能点已实现 | 逐条对照PRD验证 |
| 交互正确性 | 页面流转、按钮响应、手势操作 | 符合交互设计稿 |
| 数据正确性 | 列表、详情、表单数据展示 | 与后端返回一致 |
| 异常处理 | 网络错误、空数据、权限不足 | 有明确提示、不崩溃 |
| 边界场景 | 快速点击、横竖屏、前后台切换 | 无ANR/Crash |
| 性能指标 | 启动时间、页面加载、内存占用 | 达到性能基线 |
| 兼容性 | 最低支持版本、主流设备 | 无布局错乱、功能异常 |
| 安全合规 | 敏感数据加密、权限申请合理 | 通过安全扫描 |

### 6.4 性能基线标准

| 指标 | iOS | Android | Flutter | Web | 小程序 |
|------|-----|---------|---------|-----|--------|
| 冷启动 | < 1s | < 1.5s | < 1.5s | FCP < 1.5s | < 2s |
| 页面切换 | < 300ms | < 300ms | < 300ms | < 300ms | < 300ms |
| 列表FPS | ≥ 60fps | ≥ 60fps | ≥ 60fps | ≥ 60fps | ≥ 30fps |
| 内存占用 | < 150MB | < 200MB | < 200MB | — | < 128MB |
| 包体积 | < 50MB | < 30MB | < 30MB | < 2MB(gzip) | < 2MB |
| API响应 | < 500ms | < 500ms | < 500ms | < 500ms | < 500ms |

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 技术方案文档 | `docs/technical-design.md` | 平台选型、架构设计、技术方案 |
| 接口对接文档 | `docs/api-mapping.md` | 接口清单、数据模型映射 |
| 组件文档 | `docs/components.md` | 组件API、使用示例、复用说明 |
| 自测报告 | `docs/self-test-report.md` | 自测用例、执行结果、遗留问题 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/ios-development-guide.md` | iOS开发指南（Swift/SwiftUI/UIKit） |
| `references/android-development-guide.md` | Android开发指南（Kotlin/Compose/Jetpack） |
| `references/web-development-guide.md` | Web前端开发指南（Vue/React/TypeScript） |
| `references/flutter-development-guide.md` | Flutter开发指南（Dart/Widget/BLoC） |
| `references/wechat-miniprogram-guide.md` | 微信小程序开发指南 |
| `references/cross-platform-architecture.md` | 跨平台架构设计指南 |
| `references/component-reuse-patterns.md` | 组件化复用模式指南 |
| `references/api-integration-standards.md` | 后端接口对接规范 |
| `references/self-testing-standards.md` | 自测规范与检查清单 |
| `references/lifecycle-sdk-reference.md` | 各平台生命周期与SDK参考 |

---

## Related Skills

- `frontend-expert` - 前端技术专家（Web深度开发）
- `python-expert` - Python技术专家（后端配合）
- `system-architect` - 系统架构师（整体架构设计）
- `tech-manager` - 技术经理（前后端协调）
- `test-expert` - 测试专家（系统测试）
- `tech-plan-template` - 技术方案模板
