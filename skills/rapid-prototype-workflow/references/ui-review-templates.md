# UI 5轮审查模板

## 审查流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Round 1    │ →  │  Round 2    │ →  │  Round 3    │ →  │  Round 4    │ →  │  Round 5    │
│  商业分析师  │    │  领域产品   │    │  资深产品   │    │  UED专家    │    │  小白用户   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Round 1: 商业分析师 Review

```markdown
# UI Review - Round 1: 商业分析师视角

## Review Focus
- 界面是否清晰传达产品价值主张？
- 核心功能入口是否突出？
- 用户转化路径是否顺畅？
- 商业目标是否在UI中得到体现？

## 必须检查项
- [ ] 首屏是否传达核心价值？
- [ ] CTA按钮是否明确？
- [ ] 付费/转化入口是否合理？
- [ ] 数据展示是否支持商业决策？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

---

## Round 2: 项目专业领域产品经理 Review

```markdown
# UI Review - Round 2: 领域产品经理视角

## Review Focus (基于Round 1改进后)
- 功能是否符合行业最佳实践？
- 业务流程是否完整？
- 专业术语使用是否准确？
- 是否满足目标用户的专业需求？

## 必须检查项
- [ ] 业务流程是否完整闭环？
- [ ] 专业功能是否易于发现？
- [ ] 数据展示是否符合行业习惯？
- [ ] 异常场景是否有合理处理？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

---

## Round 3: 中国互联网资深产品经理 Review

```markdown
# UI Review - Round 3: 资深产品经理视角

## Review Focus (基于Round 2改进后)
- 是否符合中国用户使用习惯？
- 交互模式是否主流？
- 是否借鉴了成功产品的设计？
- 用户体验是否流畅？

## 必须检查项
- [ ] 导航结构是否清晰？
- [ ] 操作反馈是否及时？
- [ ] 加载状态是否友好？
- [ ] 是否有适当的引导？
- [ ] 是否考虑了移动端体验？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

---

## Round 4: 专业UED设计专家 Review

```markdown
# UI Review - Round 4: UED设计专家视角

## Review Focus (基于Round 3改进后)
- 视觉层次是否清晰？
- 色彩搭配是否和谐？
- 间距和对齐是否规范？
- 组件设计是否一致？

## 必须检查项
- [ ] 视觉层次：主次分明
- [ ] 色彩：配色和谐，对比度合适
- [ ] 排版：字体大小、行高、间距规范
- [ ] 组件：风格统一，状态完整
- [ ] 动效：自然流畅，不过度
- [ ] 响应式：各尺寸适配良好

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

---

## Round 5: 小白用户 Review

```markdown
# UI Review - Round 5: 小白用户视角

## Review Focus (基于Round 4改进后)
- 第一次使用能否快速上手？
- 功能是否一目了然？
- 是否有困惑的地方？
- 操作是否简单直观？

## 必须检查项
- [ ] 不看说明能否完成主要任务？
- [ ] 按钮文字是否易懂？
- [ ] 错误提示是否友好？
- [ ] 是否知道下一步该做什么？
- [ ] 整体感觉是否舒适？

## Feedback
[记录改进建议]

## Changes Made
[记录本轮修改]
```

---

## 自动执行5轮Review命令

```bash
/autoloop:autoloop "Execute 5-round UI review process:

Round 1 - 商业分析师视角:
Review current UI from business analyst perspective, focus on value proposition and conversion.
Make improvements based on feedback.

Round 2 - 领域产品经理视角:
Review improved UI from domain product manager perspective, focus on business flow completeness.
Make improvements based on feedback.

Round 3 - 资深产品经理视角:
Review improved UI from senior PM perspective, focus on Chinese user habits and UX.
Make improvements based on feedback.

Round 4 - UED设计专家视角:
Review improved UI from UED expert perspective, focus on visual hierarchy and design consistency.
Make improvements based on feedback.

Round 5 - 小白用户视角:
Review improved UI from novice user perspective, focus on ease of use and clarity.
Make final improvements.

Output: Create ui-review-report.md documenting all 5 rounds of feedback and changes."
```

---

## UI 全生命周期覆盖清单

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI 全生命周期覆盖清单                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 入口阶段                                                     │
│     ├── 启动页/闪屏 (Splash)                                     │
│     ├── 引导页 (Onboarding) - 首次使用                           │
│     ├── 登录页 (Login)                                          │
│     ├── 注册页 (Register)                                       │
│     ├── 忘记密码 (Forgot Password)                              │
│     └── 第三方登录 (业务需要时必须实现)                          │
│                                                                 │
│  2. 核心功能阶段                                                 │
│     ├── 首页/主界面                                              │
│     ├── 核心功能页面 (根据业务)                                   │
│     ├── 详情页                                                   │
│     ├── 列表页                                                   │
│     ├── 搜索页 + 搜索结果                                        │
│     └── 筛选/分类页                                              │
│                                                                 │
│  3. 交互操作阶段                                                 │
│     ├── 表单填写页                                               │
│     ├── 确认页/预览页                                            │
│     ├── 支付页 (业务需要时必须实现)                              │
│     └── 结果页 (成功/失败)                                       │
│                                                                 │
│  4. 个人中心阶段                                                 │
│     ├── 个人中心首页                                             │
│     ├── 个人信息编辑                                             │
│     ├── 修改密码                                                 │
│     ├── 消息中心                                                 │
│     └── 系统设置                                                 │
│                                                                 │
│  5. 异常状态 (必须覆盖)                                          │
│     ├── 空状态 (Empty State) - 无数据                            │
│     ├── 加载状态 (Loading)                                       │
│     ├── 错误状态 (Error) - 网络错误/服务器错误                    │
│     ├── 404 页面                                                 │
│     └── 无权限页面                                               │
│                                                                 │
│  6. 弹窗/浮层 (必须覆盖)                                         │
│     ├── 确认弹窗 (Confirm Dialog)                                │
│     ├── 提示弹窗 (Alert)                                         │
│     ├── 操作菜单 (Action Sheet)                                  │
│     ├── Toast 提示                                               │
│     └── 底部弹窗 (Bottom Sheet)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## UI 设计稿交付清单

| 类别 | 必须包含 | 检查项 |
|------|----------|--------|
| 入口流程 | 登录、注册、忘记密码 | ☐ 完整流程 |
| 核心页面 | 首页、列表、详情、搜索 | ☐ 所有主要页面 |
| 个人中心 | 个人中心、编辑、设置 | ☐ 完整模块 |
| 空状态 | 每个列表页的空状态 | ☐ 所有列表 |
| 加载状态 | 骨架屏/Loading | ☐ 统一风格 |
| 错误状态 | 网络错误、服务错误 | ☐ 友好提示 |
| 弹窗组件 | 确认、提示、操作菜单 | ☐ 统一风格 |
| Admin端 | 登录、列表、表单、详情 | ☐ 完整覆盖 |
| Website官网 | 首页、功能、定价、关于、联系 | ☐ 完整覆盖（必须先设计稿） |

---

## Client 侧设计交付清单

| 阶段 | 页面 | 状态 |
|------|------|------|
| 入口 | 启动页、引导页、登录、注册、忘记密码 | ☐ |
| 首页 | 首页(有数据)、首页(空状态)、首页(加载中) | ☐ |
| 核心 | 列表页、详情页、搜索页、筛选页 | ☐ |
| 操作 | 表单页、确认页、结果页(成功/失败) | ☐ |
| 个人 | 个人中心、编辑资料、修改密码 | ☐ |
| 消息 | 消息列表、消息详情、空消息 | ☐ |
| 设置 | 系统设置、关于我们、意见反馈 | ☐ |
| 异常 | 空状态、加载中、网络错误、404 | ☐ |
| 组件 | 弹窗、Toast、ActionSheet | ☐ |

---

## Admin 侧设计交付清单

| 阶段 | 页面 | 状态 |
|------|------|------|
| 入口 | 登录页 | ☐ |
| 首页 | Dashboard(数据概览) | ☐ |
| 列表 | 数据列表(有数据/空/加载中) | ☐ |
| 表单 | 新增表单、编辑表单 | ☐ |
| 详情 | 数据详情页 | ☐ |
| 配置 | 系统配置页 | ☐ |
| 组件 | 确认弹窗、操作反馈 | ☐ |

---

## Website 官网设计交付清单

> ⚠️ **Website 必须先完成 UI 设计稿，再实现静态 HTML。禁止跳过设计稿直接写代码。**

| 阶段 | 页面 | 状态 |
|------|------|------|
| 首页 | Landing Page (Hero + 功能亮点 + CTA) | ☐ |
| 功能 | 功能介绍页 (详细功能说明) | ☐ |
| 定价 | 定价页面 (价格方案对比表) | ☐ |
| 关于 | 关于我们 (团队/公司介绍) | ☐ |
| 联系 | 联系我们 (联系方式/表单) | ☐ |
| 下载 | 下载/开始使用 (引导页) | ☐ |
| 通用 | 页头导航 (响应式) | ☐ |
| 通用 | 页脚 (多列链接) | ☐ |
| 异常 | 404 页面 | ☐ |

### Website 官网组件清单

| 组件 | 用途 | 状态 |
|------|------|------|
| Hero Section | 首屏大图+标题+CTA | ☐ |
| Feature Card | 功能卡片展示 | ☐ |
| Pricing Table | 价格对比表 | ☐ |
| Testimonial | 用户评价/案例 | ☐ |
| CTA Section | 转化引导区块 | ☐ |
| FAQ Accordion | 常见问题折叠 | ☐ |
| Contact Form | 联系表单 | ☐ |
