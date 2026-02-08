# 前端架构设计指南

## 1. 前端技术选型

### 1.1 框架选型决策树

```
项目类型判断:
├── 企业级后台管理 → Vue 3 + Element Plus / React + Ant Design
├── C端营销页面 → Next.js(SSR) / Nuxt 3(SSR)
├── 移动端H5 → Vue 3 + Vant / React + Ant Design Mobile
├── 跨端小程序 → uni-app / Taro
├── 桌面应用 → Electron / Tauri
└── 高交互应用 → React + 自定义组件
```

### 1.2 构建工具选型

| 工具 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| Vite | 新项目首选 | 极快HMR，ESM原生 | 生态略新 |
| Webpack | 复杂定制需求 | 生态成熟，插件丰富 | 配置复杂，速度慢 |
| Turbopack | Next.js项目 | 极快，Rust实现 | 仅Next.js |
| Rspack | Webpack迁移 | 兼容Webpack，Rust加速 | 较新 |

## 2. 工程架构设计

### 2.1 项目结构规范

**Feature-Based 结构（推荐）：**
```
src/
├── app/                    # 应用层
│   ├── router/             # 路由配置
│   ├── store/              # 全局状态
│   ├── plugins/            # 插件
│   └── styles/             # 全局样式
├── features/               # 功能模块
│   ├── auth/               # 认证模块
│   │   ├── components/     # 模块组件
│   │   ├── composables/    # 模块逻辑 (Vue) 或 hooks/ (React)
│   │   ├── services/       # API调用
│   │   ├── stores/         # 模块状态
│   │   ├── types/          # 类型定义
│   │   └── views/          # 页面
│   └── dashboard/          # 仪表盘模块
├── shared/                 # 共享层
│   ├── components/         # 通用组件
│   ├── composables/        # 通用逻辑 (Vue) 或 hooks/ (React)
│   ├── utils/              # 工具函数
│   ├── constants/          # 常量
│   └── types/              # 全局类型
└── assets/                 # 静态资源
```

### 2.2 代码规范体系

| 工具 | 职责 | 配置 |
|------|------|------|
| ESLint | 代码质量检查 | @antfu/eslint-config |
| Prettier | 代码格式化 | 统一格式 |
| TypeScript | 类型检查 | strict模式 |
| Husky | Git Hooks | pre-commit检查 |
| lint-staged | 增量检查 | 只检查变更文件 |
| commitlint | 提交信息规范 | conventional commits |

## 3. 状态管理架构

### 3.1 状态分类策略

| 状态类型 | 存储方案 | 生命周期 | 示例 |
|----------|----------|----------|------|
| UI状态 | 组件内部 | 组件级 | 弹窗开关、表单输入 |
| 客户端状态 | 全局Store | 应用级 | 用户信息、主题、权限 |
| 服务端状态 | 请求缓存 | 请求级 | API响应数据 |
| URL状态 | 路由参数 | 导航级 | 分页、筛选条件 |
| 持久状态 | Storage | 跨会话 | 用户偏好、Token |

### 3.2 服务端状态管理

**推荐方案：**
- Vue: VueQuery (TanStack Query)
- React: TanStack Query / SWR

**核心能力：**
- 自动缓存与失效
- 后台数据刷新
- 乐观更新
- 分页/无限滚动
- 请求去重

## 4. 性能优化体系

### 4.1 加载性能

| 优化项 | 实现方式 | 效果 |
|--------|----------|------|
| 路由懒加载 | 动态import | 减少首包体积 |
| 组件懒加载 | defineAsyncComponent / lazy | 按需加载 |
| 图片优化 | WebP + 懒加载 + srcset | 减少图片体积 |
| 资源预加载 | prefetch / preload | 提前加载 |
| Tree Shaking | ESM + sideEffects | 移除无用代码 |
| 代码压缩 | Terser + Gzip/Brotli | 减少传输体积 |

### 4.2 运行时性能

| 优化项 | 实现方式 | 适用场景 |
|--------|----------|----------|
| 虚拟列表 | vue-virtual-scroller / react-window | 大数据量列表 |
| 防抖节流 | debounce / throttle | 高频事件 |
| 计算缓存 | computed / useMemo | 复杂计算 |
| Web Worker | 独立线程计算 | CPU密集型 |
| 骨架屏 | Skeleton组件 | 加载体验 |

## 5. 前端安全

| 安全项 | 防御措施 | 实现方式 |
|--------|----------|----------|
| XSS | 输出编码 + CSP | 框架自动转义 + CSP Header |
| CSRF | Token验证 | 请求携带CSRF Token |
| 敏感数据 | 不存储在前端 | Token存HttpOnly Cookie |
| 依赖安全 | 定期审计 | npm audit / Snyk |

## 6. 输出物清单

- 前端技术选型报告
- 项目结构设计文档
- 组件设计规范
- 状态管理方案
- 性能优化方案
- 前端安全方案
