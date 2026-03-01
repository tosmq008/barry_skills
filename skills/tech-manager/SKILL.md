---
name: tech-manager
description: "技术经理，负责协调客户端、前端、后端开发任务的全流程管理。根据 product-expert 输出的结构化 PRD（L1/L2/L3 YAML）进行需求解析与任务分解，智能判断客户端类型并调度对应专家 Agent（client-expert、frontend-expert、python-expert）并行执行开发任务，确保多端接口对接正确、数据交互完整。开发完成后执行多端联调保障，验证需求完成度和正确性，最后调度测试专家 test-expert 进行系统测试。适用于需要多端协作的功能开发、接口联调、集成测试等场景。"
license: MIT
compatibility: "需要 client-expert、frontend-expert、python-expert、test-expert 四个 skill 支持。适用于多端架构的项目（Web/iOS/Android/Flutter/小程序）。"
metadata:
  category: coordination
  phase: orchestration
  version: "2.0.0"
  author: tech-manager
---

# Tech Manager Skill

作为技术经理，负责协调多端开发任务的全流程管理。根据 product-expert 输出的结构化 PRD（L1 功能架构 / L2 用例流 / L3 User Story）进行需求解析，智能判断客户端类型并调度对应专家 Agent 并行执行开发任务，确保多端串联正确完整，并在开发完成后进行联调保障和测试验收。

## When to Use

**适用场景：**
- 需要多端协作的功能开发（Web + 原生客户端 + 后端）
- 基于 product-expert 输出的 PRD 进行开发任务分解
- 前后端 / 客户端与后端接口联调
- 全栈功能实现与集成
- 需求开发的端到端交付
- 多端数据交互验证

**不适用：**
- 纯前端或纯后端的独立任务（直接使用对应专家 skill）
- 纯客户端独立任务（直接使用 client-expert）
- 简单的 Bug 修复（使用 bug-fix-task-split）
- 不涉及多端交互的任务

---

## 多 Agent 调度架构

> ⚠️ **执行前必须读取 `references/multi-agent-orchestration.md` 获取完整调度指南**

### 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│              技术经理 - 多 Agent 调度架构 v2.0                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────────┐                          │
│                    │   技术经理      │                          │
│                    │  (Orchestrator) │                          │
│                    │                 │                          │
│                    │ • PRD解析       │                          │
│                    │ • 平台路由决策  │                          │
│                    │ • 任务分解      │                          │
│                    │ • Agent 调度    │                          │
│                    │ • 多端联调      │                          │
│                    │ • 测试验收      │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│           ┌─────────────────┼─────────────────┐                 │
│           │                 │                 │                 │
│           ▼                 ▼                 ▼                 │
│     ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│     │ 客户端   │     │ 前端     │     │ 后端     │            │
│     │ Agent    │     │ Agent    │     │ Agent    │            │
│     │          │     │          │     │          │            │
│     │ client   │     │frontend  │     │ python   │            │
│     │ -expert  │     │-expert   │     │ -expert  │            │
│     │          │     │          │     │          │            │
│     │iOS/Andr  │     │Vue/React │     │FastAPI   │            │
│     │Flutter   │     │Web端     │     │Django    │            │
│     │小程序    │     │Admin端   │     │数据库    │            │
│     └──────────┘     └──────────┘     └──────────┘            │
│           │                 │                 │                 │
│           └─────────────────┼─────────────────┘                 │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   测试专家      │                          │
│                    │  test-expert    │                          │
│                    └─────────────────┘                          │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   交付验收      │                          │
│                    │   完成报告      │                          │
│                    └─────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Agent 角色定义

| Agent 角色 | Skill | 职责 | 适用场景 | 输入 | 输出 |
|------------|-------|------|----------|------|------|
| **技术经理** | tech-manager | PRD解析、任务分解、平台路由、调度、联调、验收 | 全流程协调 | PRD文档(L1/L2/L3 YAML) | 完成报告 |
| **客户端专家** | client-expert | iOS/Android/Flutter/小程序开发 | 原生/跨平台客户端 | 客户端任务单 | 客户端代码 |
| **前端专家** | frontend-expert | Web前端开发(Vue/React) | Web端/Admin后台 | 前端任务单 | 前端代码 |
| **后端专家** | python-expert | 后端API/数据库/业务逻辑 | 服务端开发 | 后端任务单 | 后端代码 |
| **测试专家** | test-expert | 功能测试、集成测试、回归测试 | 质量验收 | 测试任务单 | 测试报告 |

### 客户端专家 vs 前端专家：平台路由决策

> 这是 tech-manager 的核心决策点：根据 PRD 中的 `endpoints` 和客户端类型，决定调度哪个专家。

**路由决策矩阵：**

| 客户端类型 | 调度 Agent | 说明 |
|-----------|-----------|------|
| Web (Vue/React) - Client端 | `frontend-expert` | 纯Web技术栈，前端专家更深入 |
| Web (Vue/React) - Admin后台 | `frontend-expert` | 管理后台属于Web前端范畴 |
| Web (Vue/React) - 运营后台 | `frontend-expert` | 运营后台属于Web前端范畴 |
| iOS 原生 (Swift/SwiftUI) | `client-expert` | 原生平台，客户端专家负责 |
| Android 原生 (Kotlin/Compose) | `client-expert` | 原生平台，客户端专家负责 |
| Flutter 跨平台 | `client-expert` | 跨平台方案，客户端专家负责 |
| 微信小程序 | `client-expert` | 小程序平台，客户端专家负责 |
| 混合方案 (原生壳+WebView) | `client-expert` 主导 + `frontend-expert` 协助 | 客户端专家负责壳和桥接，前端专家负责H5页面 |
| 全端覆盖 | `client-expert` + `frontend-expert` 并行 | 各自负责对应平台 |

**决策流程：**

```
解析 PRD L1 YAML 中的 endpoints 字段
         │
         ▼
┌─────────────────────────────┐
│ 识别所有涉及的客户端平台      │
│ endpoints: ["Client","Admin"]│
│ + 项目技术栈信息              │
└──────────┬──────────────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  Client端    Admin/Operation端
     │              │
     ▼              ▼
 判断技术栈     → frontend-expert
     │
     ├── Web(Vue/React)    → frontend-expert
     ├── iOS/Android原生    → client-expert
     ├── Flutter跨平台      → client-expert
     ├── 微信小程序          → client-expert
     └── 混合方案           → client-expert + frontend-expert
```

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   技术经理工作流程 v2.0                            │
│           （适配 product-expert 结构化 PRD 输出）                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: PRD解析           Phase 2: 任务分解                    │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 解析L1功能架构   │  ──▶  │ 客户端任务拆分  │                  │
│  │ 解析L2用例流     │       │ 前端任务拆分    │                  │
│  │ 解析L3 UserStory │       │ 后端任务拆分    │                  │
│  │ 平台路由决策     │       │ 确定依赖关系    │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 3: 并行开发          Phase 4: 多端联调                    │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 调度客户端专家   │  ──▶  │ 接口联调验证    │                  │
│  │ 调度前端专家     │       │ 多端数据流验证  │                  │
│  │ 调度后端专家     │       │ 功能完整性检查  │                  │
│  │ 监控开发进度     │       │ 多端一致性检查  │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 5: 测试验收          Phase 6: 交付完成                    │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 调度测试专家     │  ──▶  │ 生成完成报告    │                  │
│  │ 多端功能测试     │       │ 确认需求完成    │                  │
│  │ 验证测试结果     │       │ 交付验收        │                  │
│  └─────────────────┘       └─────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: PRD 解析 (PRD Parsing & Analysis)

### 1.1 解析 product-expert 输出

**product-expert 输出的 PRD 文件结构：**

```
docs/prd/
├── 01-project-overview.md          # 项目概述
├── L1-feature-architecture.yaml    # L1: 功能架构图（AI可解析）
├── L1-feature-architecture.md      # L1: 功能架构图（人类可读）
├── L2-use-case-flows.yaml          # L2: 用例流（AI可解析）
├── L2-use-case-flows.md            # L2: 用例流（人类可读）
├── L3-user-stories.yaml            # L3: User Story+AC（AI可解析）
├── L3-user-stories.md              # L3: User Story+AC（人类可读）
├── 07-page-list.md                 # 页面清单
├── 12-data-spec.md                 # 数据规格
├── 14-release-plan.md              # 发布计划
└── validation-report.md            # PRD完整性验证报告
```

**技术经理必须解析的核心文件：**

| 文件 | 解析目标 | 关键字段 |
|------|----------|----------|
| L1 YAML | 功能边界、模块划分、平台分布 | `endpoints`, `priority`, `iteration`, `depends_on` |
| L2 YAML | 用例流程、数据变更、业务规则 | `main_flow`, `data_changes`, `business_rules` |
| L3 YAML | 迭代范围、验收标准、完成定义 | `stories`, `acceptance_criteria`, `definition_of_done` |
| 页面清单 | 各端页面列表 | Client端/Admin端/运营端页面 |
| UI设计稿 | .pen 文件 | 各页面设计稿 |

### 1.2 从 L1 提取平台路由信息

**从 L1 YAML 中提取 endpoints 分布：**

```yaml
# 解析 L1-feature-architecture.yaml
# 提取每个 feature 的 endpoints 字段
features:
  - feature_id: "F-001"
    endpoints: ["Client"]        # → 判断 Client 端技术栈
  - feature_id: "F-010"
    endpoints: ["Client", "Admin"]  # → Client + Admin 两端
  - feature_id: "F-020"
    endpoints: ["Admin"]         # → 纯 Admin 端 → frontend-expert
```

**平台路由决策执行：**

1. 汇总所有 feature 的 endpoints，得到涉及的端列表
2. 确认项目的客户端技术栈（Web/iOS/Android/Flutter/小程序）
3. 按路由决策矩阵分配 Agent
4. 如果 Client 端是 Web 技术栈 → `frontend-expert`
5. 如果 Client 端是原生/跨平台 → `client-expert`
6. Admin/Operation 端 → `frontend-expert`
7. 后端 API → `python-expert`

### 1.3 从 L2 提取接口契约

**从 L2 YAML 中提取数据变更和接口需求：**

> ⚠️ **执行前必须读取 `references/integration-checklist.md` 获取接口契约模板**

```yaml
# 解析 L2-use-case-flows.yaml
# 提取每个 use_case 的 data_changes 和 main_flow 中的 data_in/data_out
use_cases:
  - uc_id: "UC-001"
    data_changes:
      - entity: "User"
        operation: "CREATE"
        fields: ["user_id", "phone", "created_at"]
    main_flow:
      - step: 2
        data_in: { "phone": "string" }
        data_out: { "sms_code": "string" }
```

**输出：接口契约清单**

| 接口 | 方法 | 来源用例 | 请求参数 | 响应数据 | 涉及端 |
|------|------|----------|----------|----------|--------|
| /api/v1/auth/register | POST | UC-001 | phone, code | user_id, token | Client, Backend |

### 1.4 从 L3 提取迭代范围

**从 L3 YAML 中提取当前迭代的 Story 和 AC：**

```yaml
# 解析 L3-user-stories.yaml
iterations:
  - iteration_id: "ITER-MVP"
    scope_features: ["F-001", "F-002", "F-010"]
    stories:
      - story_id: "US-001"
        related_features: ["F-001"]
        acceptance_criteria:
          - ac_id: "AC-001"
            type: "happy_path"
            given: "..."
            when: "..."
            then: "..."
```

**输出：迭代开发范围表**

| Story ID | 功能 | 涉及端 | 客户端Agent | 后端Agent | 优先级 |
|----------|------|--------|-------------|-----------|--------|
| US-001 | 手机号注册 | Client | client-expert/frontend-expert | python-expert | P0 |

<!-- PLACEHOLDER_PHASE2 -->

---

## Phase 2: 任务分解 (Task Decomposition)

### 2.1 客户端任务拆分（client-expert / frontend-expert）

**根据平台路由决策，生成对应的任务单：**

**场景A：Client端为原生/跨平台 → 调度 client-expert**

```markdown
请使用 client-expert skill 执行客户端开发任务：

### 任务信息
- 任务ID: TASK_CL_[xxx]
- 来源PRD: docs/prd/L3-user-stories.yaml → ITER-MVP
- 目标平台: [iOS/Android/Flutter/小程序]
- 项目路径: [path]
- 分支: feature/[name]

### 关联PRD
- L1 功能: [F-001, F-002]
- L2 用例: [UC-001, UC-002]
- L3 Story: [US-001, US-002]
- UI设计稿: [.pen文件路径]

### 开发内容
| 序号 | 页面/组件 | 功能描述 | 依赖API | 来源Story |
|------|-----------|----------|---------|-----------|
| 1 | [name] | [description] | [api] | US-001 |

### 验收标准（从L3 AC提取）
| AC-ID | Given | When | Then |
|-------|-------|------|------|
| AC-001 | [given] | [when] | [then] |
```

**场景B：Client端为Web → 调度 frontend-expert**

```markdown
请使用 frontend-expert skill 执行前端开发任务：

### 任务信息
- 任务ID: TASK_FE_[xxx]
- 来源PRD: docs/prd/L3-user-stories.yaml → ITER-MVP
- 项目路径: [path]
- 分支: feature/[name]

### 关联PRD
- L1 功能: [F-001, F-002]
- L2 用例: [UC-001, UC-002]
- L3 Story: [US-001, US-002]
- UI设计稿: [.pen文件路径]

### 开发内容
[前端任务单内容 - 参见 references/task-template.md]

### 验收标准（从L3 AC提取）
| AC-ID | Given | When | Then |
|-------|-------|------|------|
| AC-001 | [given] | [when] | [then] |
```

**场景C：混合方案 → client-expert + frontend-expert 协作**

当项目采用混合方案（原生壳 + WebView/H5）时：

| 职责划分 | Agent | 具体内容 |
|----------|-------|----------|
| 原生壳 & 容器 | client-expert | App壳、导航框架、原生能力桥接 |
| JSBridge | client-expert | 桥接协议定义、原生侧实现 |
| H5页面 | frontend-expert | WebView内的页面开发 |
| 原生页面 | client-expert | 性能敏感的原生页面 |
| 共享逻辑 | 协商确定 | 根据技术栈决定归属 |

### 2.2 Admin/运营后台任务拆分 → frontend-expert

Admin 和运营后台始终由 frontend-expert 负责：

```markdown
请使用 frontend-expert skill 执行管理后台开发任务：

### 任务信息
- 任务ID: TASK_FE_ADMIN_[xxx]
- 来源PRD: docs/prd/L3-user-stories.yaml
- 端: Admin / Operation
- 项目路径: [path]

### 开发内容
[Admin端页面列表 - 从 07-page-list.md 提取]
```

### 2.3 后端任务拆分 → python-expert

```markdown
请使用 python-expert skill 执行后端开发任务：

### 任务信息
- 任务ID: TASK_BE_[xxx]
- 来源PRD: docs/prd/L2-use-case-flows.yaml
- 项目路径: [path]
- 分支: feature/[name]

### 接口清单（从L2 data_changes + main_flow提取）
| 序号 | 接口路径 | 方法 | 功能描述 | 来源用例 |
|------|----------|------|----------|----------|
| 1 | /api/v1/[resource] | [METHOD] | [description] | UC-001 |

### 数据模型（从L2 data_changes提取）
| 模型名 | 操作 | 字段 | 来源用例 |
|--------|------|------|----------|
| User | CREATE | user_id, phone, ... | UC-001 |

### 业务规则（从L2 business_rules提取）
| 规则ID | 规则描述 | 来源用例 |
|--------|----------|----------|
| BR-001 | 手机号格式校验 | UC-001 |
```

### 2.4 确定依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                      任务依赖关系 v2.0                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  无依赖任务 (可并行)                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 客户端: 页面布局、静态组件、本地Mock                      │   │
│  │ 前端:   页面布局、静态组件、样式开发                      │   │
│  │ 后端:   数据模型设计、基础 API 框架                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  有依赖任务 (需串行)                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 后端 API 实现 ──▶ 客户端/前端 API 对接                   │   │
│  │ 数据库设计 ──▶ 后端数据操作                              │   │
│  │ client-expert JSBridge ──▶ frontend-expert H5对接        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  最终依赖                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 各端开发完成 ──▶ 多端联调 ──▶ 测试                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

<!-- PLACEHOLDER_PHASE3 -->

---

## Phase 3: 并行开发 (Parallel Development)

### 3.1 调度策略

**根据平台路由结果，确定需要调度的 Agent 组合：**

| 项目类型 | 调度组合 | 并行策略 |
|----------|----------|----------|
| Web全栈 | frontend-expert + python-expert | 前后端并行 |
| 原生App全栈 | client-expert + python-expert | 客户端与后端并行 |
| 多端项目 | client-expert + frontend-expert + python-expert | 三端并行 |
| 混合方案 | client-expert + frontend-expert + python-expert | 壳先行，H5与后端并行 |

### 3.2 调度客户端专家（当需要时）

```markdown
请使用 client-expert skill 执行客户端开发任务：

### 任务信息
- 任务ID: TASK_CL_[xxx]
- 项目路径: [path]
- 分支: feature/[name]
- 目标平台: [iOS/Android/Flutter/小程序]

### 开发内容
[客户端任务单内容]

### 接口契约
[从Phase 1提取的接口契约]

### UI设计稿
[.pen文件路径]

### 输出要求
- 完成所有页面/组件开发
- API 对接代码（可先 Mock）
- 本地自测通过
- 提供自测报告
```

### 3.3 调度前端专家

```markdown
请使用 frontend-expert skill 执行前端开发任务：

### 任务信息
- 任务ID: TASK_FE_[xxx]
- 项目路径: [path]
- 分支: feature/[name]

### 开发内容
[前端任务单内容]

### 接口契约
[从Phase 1提取的接口契约]

### UI设计稿
[.pen文件路径]

### 输出要求
- 完成所有页面/组件开发
- API 对接代码（可先 Mock）
- 本地测试通过
```

### 3.4 调度后端专家

```markdown
请使用 python-expert skill 执行后端开发任务：

### 任务信息
- 任务ID: TASK_BE_[xxx]
- 项目路径: [path]
- 分支: feature/[name]

### 开发内容
[后端任务单内容]

### 输出要求
- 完成所有 API 接口实现
- 单元测试通过
- 接口文档更新
```

### 3.5 进度监控

| Agent | 任务数 | 已完成 | 进行中 | 状态 |
|-------|--------|--------|--------|------|
| 客户端专家 | [n] | [n] | [n] | [状态] |
| 前端专家 | [n] | [n] | [n] | [状态] |
| 后端专家 | [n] | [n] | [n] | [状态] |

---

## Phase 4: 多端联调 (Multi-Platform Integration)

> ⚠️ **执行前必须读取 `references/integration-checklist.md` 获取完整联调检查清单**

### 4.1 接口联调验证

**各端与后端的联调检查：**

| 检查项 | Client端(客户端/前端) | Admin端(前端) | 状态 |
|--------|----------------------|---------------|------|
| API 调用正确 | [ ] | [ ] | |
| 跨域/网络配置 | [ ] | [ ] | |
| 认证/授权机制 | [ ] | [ ] | |
| 请求参数格式 | [ ] | [ ] | |
| 响应数据结构 | [ ] | [ ] | |
| 错误响应处理 | [ ] | [ ] | |

### 4.2 多端数据流验证

| 检查项 | 客户端 | Web前端 | 后端 | 状态 |
|--------|--------|---------|------|------|
| 数据提交 | 表单序列化 | 表单序列化 | 接收解析 | [✓/✗] |
| 数据查询 | 发起请求 | 发起请求 | 返回数据 | [✓/✗] |
| 数据展示 | 渲染数据 | 渲染数据 | - | [✓/✗] |
| 错误处理 | 展示错误 | 展示错误 | 返回错误码 | [✓/✗] |

### 4.3 多端一致性检查（当多端并存时）

| 检查项 | 说明 | 状态 |
|--------|------|------|
| 功能一致性 | 各端实现的功能范围一致 | [ ] |
| 数据一致性 | 同一接口在各端展示数据一致 | [ ] |
| 交互一致性 | 核心交互流程各端一致 | [ ] |
| 错误处理一致性 | 错误提示和处理方式各端一致 | [ ] |
| 状态同步 | 多端登录状态、数据状态同步 | [ ] |

### 4.4 混合方案专项检查（当使用混合方案时）

| 检查项 | 说明 | 状态 |
|--------|------|------|
| JSBridge 通信 | 原生与H5双向通信正常 | [ ] |
| 页面跳转 | 原生页面与H5页面互跳正常 | [ ] |
| 登录态共享 | 原生与H5共享登录状态 | [ ] |
| 性能表现 | WebView加载速度达标 | [ ] |
| 降级方案 | H5加载失败时的降级处理 | [ ] |

### 4.5 功能完整性检查（对照L3 AC）

| Story ID | AC-ID | 功能点 | 客户端 | 前端 | 后端 | 联调状态 |
|----------|-------|--------|--------|------|------|----------|
| US-001 | AC-001 | 正常注册 | ✓ | - | ✓ | ✓ |
| US-001 | AC-002 | 手机号已注册 | ✓ | - | ✓ | ✓ |

---

## Phase 5: 测试验收 (Test Acceptance)

### 5.1 调度测试专家

```markdown
请使用 test-expert skill 执行测试任务：

### 测试范围
- 功能测试：验证所有 L3 AC（Given-When-Then）
- 集成测试：验证多端集成
- 回归测试：确保无引入新问题
- 多端测试：验证各端功能一致性

### 测试依据
- PRD: docs/prd/L3-user-stories.yaml
- 验收标准: docs/prd/13-acceptance-criteria.md
- 接口契约: docs/api/api-contract.md

### 测试环境
- 客户端: [平台/版本]
- 前端地址: [url]
- 后端地址: [url]
- 测试数据: [path]

### 输出要求
- 按 AC-ID 逐条验证结果
- Bug 列表（含复现步骤和截图）
- 测试报告
```

### 5.2 测试结果验证

| 测试类型 | 用例数 | 通过 | 失败 | 通过率 |
|----------|--------|------|------|--------|
| 功能测试 | [n] | [n] | [n] | [%] |
| 集成测试 | [n] | [n] | [n] | [%] |
| 多端一致性 | [n] | [n] | [n] | [%] |
| 回归测试 | [n] | [n] | [n] | [%] |

---

## Phase 6: 交付完成 (Delivery Completion)

### 6.1 完成标准

**必须满足：**
- [ ] 所有 L3 User Story 开发完成
- [ ] 所有 AC 验证通过
- [ ] 多端联调通过
- [ ] 测试通过率 ≥ 95%
- [ ] 无 Critical/Major Bug
- [ ] DoD（Definition of Done）全部满足

### 6.2 完成报告

```markdown
# 开发完成报告

## 基本信息
- 需求: [需求名称]
- 迭代: [ITER-MVP / ITER-V1.1]
- 来源PRD: docs/prd/
- 参与 Agent: [列出实际参与的Agent]

## 开发成果
| 类型 | Agent | 数量 | 说明 |
|------|-------|------|------|
| 客户端页面 | client-expert | [n] | [列表] |
| Web前端页面 | frontend-expert | [n] | [列表] |
| Admin页面 | frontend-expert | [n] | [列表] |
| 后端 API | python-expert | [n] | [列表] |
| 数据模型 | python-expert | [n] | [列表] |

## L3 验收标准完成情况
| Story ID | AC总数 | 通过 | 失败 | 状态 |
|----------|--------|------|------|------|
| US-001 | [n] | [n] | [n] | ✓/✗ |

## 测试结果
- 测试用例: [n] 个
- 通过率: [%]
- 遗留问题: [n] 个

## 交付确认
- [ ] 代码已合并
- [ ] 文档已更新
- [ ] 需求已验收
- [ ] DoD 全部满足
```

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 任务分解 | `docs/dev/task-breakdown.md` | 多端任务分解（含平台路由决策） |
| 接口契约 | `docs/api/api-contract.md` | API 接口契约（从L2提取） |
| 联调报告 | `docs/dev/integration-report.md` | 多端联调验证报告 |
| 完成报告 | `docs/dev/completion-report.md` | 开发完成报告（含L3 AC验证） |

---

## References

| 文档 | 用途 |
|------|------|
| `references/multi-agent-orchestration.md` | 多 Agent 调度指南（含客户端专家） |
| `references/integration-checklist.md` | 多端联调检查清单 |
| `references/task-template.md` | 任务单模板（含客户端任务单） |

---

## Related Skills

- `client-expert` - 客户端专家（iOS/Android/Flutter/小程序开发）
- `frontend-expert` - 前端专家（Web前端/Admin后台开发）
- `python-expert` - 后端专家（后端开发）
- `test-expert` - 测试专家（系统测试）
- `product-expert` - 产品专家（PRD输出，上游依赖）
- `system-architect` - 系统架构师（架构设计）
- `orchestrator` - 编排调度器
