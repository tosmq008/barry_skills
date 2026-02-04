# UI 设计工作流 (Pencil MCP)

## 概述

本文档定义使用 Pencil MCP 进行 UI 设计的完整工作流程。

---

## 一、设计准备

### 1.1 设计前置工作

| 步骤 | 内容 | 输出 |
|------|------|------|
| 1 | 明确设计目标 | 设计目标文档 |
| 2 | 确定设计风格 | 风格参考板 |
| 3 | 定义设计规范 | 设计规范文档 |
| 4 | 准备设计素材 | 素材库 |

### 1.2 设计规范定义

**颜色规范：**
```
主色 (Primary): #[色值] - 品牌主色，用于主要按钮、重点元素
辅助色 (Secondary): #[色值] - 辅助强调
成功色 (Success): #22C55E - 成功状态
警告色 (Warning): #F59E0B - 警告状态
错误色 (Error): #EF4444 - 错误状态
信息色 (Info): #3B82F6 - 信息提示

中性色:
- 标题文字: #1F2937
- 正文文字: #4B5563
- 次要文字: #9CA3AF
- 禁用文字: #D1D5DB
- 分割线: #E5E7EB
- 背景色: #F9FAFB
```

**字体规范：**
```
字体家族: Inter / SF Pro / 思源黑体

字号层级:
- H1: 32px / 40px line-height / Bold
- H2: 24px / 32px line-height / Semibold
- H3: 20px / 28px line-height / Semibold
- H4: 16px / 24px line-height / Medium
- Body: 14px / 22px line-height / Regular
- Caption: 12px / 18px line-height / Regular
```

**间距规范：**
```
基础单位: 4px

间距层级:
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
```

---

## 二、Pencil MCP 设计流程

### 2.1 完整设计流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pencil MCP 设计流程                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 获取灵感                                               │
│  ├── get_style_guide_tags() - 获取可用风格标签                  │
│  ├── get_style_guide(tags) - 获取风格指南                       │
│  └── 确定设计方向                                               │
│                                                                 │
│  Step 2: 创建文件                                               │
│  ├── open_document("new") - 创建新文件                          │
│  ├── get_guidelines("design-system") - 获取设计规范             │
│  └── batch_get(patterns) - 了解组件库                           │
│                                                                 │
│  Step 3: 设计页面                                               │
│  ├── batch_design(operations) - 创建页面结构                    │
│  ├── 使用组件库搭建界面                                         │
│  └── 逐步完善细节                                               │
│                                                                 │
│  Step 4: 验证设计                                               │
│  ├── get_screenshot(nodeId) - 截图检查                          │
│  ├── snapshot_layout() - 检查布局                               │
│  └── 迭代优化                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Step 1: 获取设计灵感

```javascript
// 1. 获取可用的风格标签
get_style_guide_tags()

// 2. 根据项目需求选择标签，获取风格指南
get_style_guide({
  tags: ["modern", "minimal", "webapp", "dashboard", "professional"]
})

// 或者使用特定风格名称
get_style_guide({
  name: "SaaS Dashboard"
})
```

### 2.3 Step 2: 创建设计文件

```javascript
// 1. 创建新文件或打开现有文件
open_document("new")  // 新建
open_document("docs/ui/project.pen")  // 打开现有

// 2. 获取设计规范
get_guidelines("design-system")

// 3. 了解可用组件
batch_get({
  patterns: [{ reusable: true }],
  readDepth: 2,
  searchDepth: 3
})
```

### 2.4 Step 3: 设计页面

```javascript
// 使用 batch_design 创建页面
batch_design({
  filePath: "docs/ui/project.pen",
  operations: `
    // 创建页面框架
    screen=I(document, {type: "frame", name: "Login Page", width: 375, height: 812})

    // 添加背景
    U(screen, {fill: "#FFFFFF"})

    // 添加内容容器
    content=I(screen, {type: "frame", layout: "vertical", padding: 24, gap: 24})

    // 添加标题
    title=I(content, {type: "text", content: "Welcome Back", fontSize: 24, fontWeight: "bold"})

    // 添加输入框组件
    emailInput=I(content, {type: "ref", ref: "InputField", width: "fill_container"})
    U(emailInput+"/label", {content: "Email"})
    U(emailInput+"/placeholder", {content: "Enter your email"})

    // 添加按钮组件
    loginBtn=I(content, {type: "ref", ref: "PrimaryButton", width: "fill_container"})
    U(loginBtn+"/label", {content: "Sign In"})
  `
})
```

### 2.5 Step 4: 验证设计

```javascript
// 1. 获取页面截图检查
get_screenshot({
  filePath: "docs/ui/project.pen",
  nodeId: "screen_id"
})

// 2. 检查布局结构
snapshot_layout({
  filePath: "docs/ui/project.pen",
  parentId: "screen_id",
  maxDepth: 3
})

// 3. 根据检查结果迭代优化
batch_design({
  operations: `
    // 修复发现的问题
    U("element_id", {padding: 16, gap: 12})
  `
})
```

---

## 三、页面设计模板

### 3.1 移动端页面模板

**登录页模板：**
```javascript
operations: `
  // 登录页框架
  loginPage=I(document, {type: "frame", name: "Login", width: 375, height: 812, fill: "#FFFFFF"})

  // 内容区域
  content=I(loginPage, {type: "frame", layout: "vertical", padding: 24, gap: 32, y: 120})

  // Logo区域
  logo=I(content, {type: "frame", layout: "vertical", gap: 8, alignItems: "center"})
  logoIcon=I(logo, {type: "frame", width: 64, height: 64, fill: "#3B82F6", cornerRadius: 16})
  appName=I(logo, {type: "text", content: "App Name", fontSize: 24, fontWeight: "bold"})

  // 表单区域
  form=I(content, {type: "frame", layout: "vertical", gap: 16, width: "fill_container"})
  emailField=I(form, {type: "ref", ref: "TextField", width: "fill_container"})
  passwordField=I(form, {type: "ref", ref: "TextField", width: "fill_container"})

  // 按钮区域
  buttons=I(content, {type: "frame", layout: "vertical", gap: 12, width: "fill_container"})
  loginBtn=I(buttons, {type: "ref", ref: "PrimaryButton", width: "fill_container"})
  registerLink=I(buttons, {type: "text", content: "Don't have an account? Sign up", fontSize: 14, textAlign: "center"})
`
```

**列表页模板：**
```javascript
operations: `
  // 列表页框架
  listPage=I(document, {type: "frame", name: "List", width: 375, height: 812, fill: "#F9FAFB"})

  // 导航栏
  navbar=I(listPage, {type: "ref", ref: "Navbar", width: "fill_container"})
  U(navbar+"/title", {content: "Items"})

  // 搜索栏
  searchBar=I(listPage, {type: "ref", ref: "SearchBar", width: "fill_container", y: 56})

  // 列表区域
  listContainer=I(listPage, {type: "frame", layout: "vertical", gap: 12, padding: 16, y: 112})

  // 列表项
  item1=I(listContainer, {type: "ref", ref: "ListItem", width: "fill_container"})
  item2=I(listContainer, {type: "ref", ref: "ListItem", width: "fill_container"})
  item3=I(listContainer, {type: "ref", ref: "ListItem", width: "fill_container"})
`
```

### 3.2 Web端页面模板

**Dashboard模板：**
```javascript
operations: `
  // Dashboard框架
  dashboard=I(document, {type: "frame", name: "Dashboard", width: 1440, height: 900, fill: "#F9FAFB"})

  // 侧边栏
  sidebar=I(dashboard, {type: "ref", ref: "Sidebar", width: 240, height: "fill_container"})

  // 主内容区
  main=I(dashboard, {type: "frame", layout: "vertical", x: 240, width: 1200, height: "fill_container", padding: 32, gap: 24})

  // 页面标题
  header=I(main, {type: "frame", layout: "horizontal", justifyContent: "space-between", width: "fill_container"})
  title=I(header, {type: "text", content: "Dashboard", fontSize: 24, fontWeight: "bold"})
  actions=I(header, {type: "ref", ref: "ButtonGroup"})

  // 统计卡片
  stats=I(main, {type: "frame", layout: "horizontal", gap: 24, width: "fill_container"})
  card1=I(stats, {type: "ref", ref: "StatCard", width: "fill_container"})
  card2=I(stats, {type: "ref", ref: "StatCard", width: "fill_container"})
  card3=I(stats, {type: "ref", ref: "StatCard", width: "fill_container"})
  card4=I(stats, {type: "ref", ref: "StatCard", width: "fill_container"})

  // 图表区域
  charts=I(main, {type: "frame", layout: "horizontal", gap: 24, width: "fill_container"})
  chart1=I(charts, {type: "ref", ref: "ChartCard", width: "fill_container"})
  chart2=I(charts, {type: "ref", ref: "ChartCard", width: "fill_container"})
`
```

---

## 四、设计审查流程

### 4.1 5轮审查机制

| 轮次 | 审查角色 | 审查重点 | 检查项 |
|------|----------|----------|--------|
| 1 | 商业分析师 | 商业价值 | 价值主张清晰、转化路径顺畅 |
| 2 | 领域产品经理 | 业务流程 | 流程完整、符合行业实践 |
| 3 | 资深产品经理 | 用户体验 | 交互合理、符合用户习惯 |
| 4 | UED设计专家 | 视觉设计 | 视觉层次、设计一致性 |
| 5 | 小白用户 | 易用性 | 直观易懂、无障碍使用 |

### 4.2 审查检查清单

**商业价值审查：**
- [ ] 核心价值主张在首屏清晰展示
- [ ] CTA按钮位置突出、文案有吸引力
- [ ] 转化路径清晰、步骤最少化
- [ ] 信任元素充分（评价、认证、数据）

**业务流程审查：**
- [ ] 核心流程完整覆盖
- [ ] 异常流程有处理
- [ ] 符合行业最佳实践
- [ ] 业务规则正确体现

**用户体验审查：**
- [ ] 导航清晰、层级合理
- [ ] 操作反馈及时
- [ ] 错误提示友好
- [ ] 加载状态明确

**视觉设计审查：**
- [ ] 视觉层次分明
- [ ] 颜色使用一致
- [ ] 字体规范统一
- [ ] 间距节奏和谐

**易用性审查：**
- [ ] 新用户可快速上手
- [ ] 功能入口易发现
- [ ] 操作步骤简单
- [ ] 帮助信息易获取

---

## 五、设计交付规范

### 5.1 交付物清单

| 交付物 | 格式 | 说明 |
|--------|------|------|
| 设计稿 | .pen | Pencil设计文件 |
| 设计规范 | .md | 设计规范文档 |
| 切图资源 | .png/.svg | 图标、图片资源 |
| 标注说明 | .md | 关键标注说明 |

### 5.2 设计稿命名规范

```
文件命名: [项目名]-[版本].pen
示例: myapp-v1.0.pen

页面命名: [端]-[模块]-[页面名]-[状态]
示例:
- Client-User-Login-Default
- Client-User-Login-Error
- Admin-Dashboard-Overview
- Web-Landing-Hero
```

### 5.3 组件命名规范

```
组件命名: [类型][变体][尺寸]
示例:
- ButtonPrimaryLarge
- ButtonSecondaryMedium
- InputTextDefault
- InputTextError
- CardProductDefault
```

---

## 六、常见问题处理

### 6.1 布局问题

| 问题 | 解决方案 |
|------|----------|
| 元素重叠 | 检查position和z-index |
| 间距不均 | 使用layout和gap属性 |
| 对齐问题 | 使用alignItems和justifyContent |
| 溢出问题 | 检查width和overflow设置 |

### 6.2 组件问题

| 问题 | 解决方案 |
|------|----------|
| 组件不显示 | 检查ref引用是否正确 |
| 样式不生效 | 检查属性路径是否正确 |
| 内容不更新 | 使用正确的子节点路径 |

### 6.3 性能问题

| 问题 | 解决方案 |
|------|----------|
| 操作过多 | 分批执行，每批≤25个操作 |
| 文件过大 | 拆分为多个设计文件 |
| 响应慢 | 减少readDepth和searchDepth |
