# 多 Agent 调度指南

## 概述

技术经理作为协调者角色，根据 product-expert 输出的结构化 PRD（L1/L2/L3 YAML），通过平台路由决策调度客户端专家、前端专家、后端专家和测试专家四个 Agent 协同完成开发任务。

---

## Agent 角色详解

### 1. 技术经理 (Orchestrator)

**职责：**
- 解析 product-expert 输出的 L1/L2/L3 YAML
- 执行平台路由决策（client-expert vs frontend-expert）
- 分解任务并分配给对应 Agent
- 监控各 Agent 执行状态
- 执行多端联调保障
- 调度测试 Agent 执行验收
- 生成开发完成报告

**能力要求：**
- 理解结构化 PRD（L1 功能架构 / L2 用例流 / L3 User Story）
- 平台技术栈判断与路由决策
- 任务分解和优先级排序
- 并行调度和依赖管理
- 多端集成验证

### 2. 客户端专家 (client-expert)

**职责：**
- iOS/Android 原生开发
- Flutter 跨平台开发
- 微信小程序开发
- 混合方案中的原生壳与桥接
- 客户端架构设计与组件化
- 客户端自测与质量保障

**适用条件：**
- PRD 中 Client 端技术栈为 iOS/Android/Flutter/小程序
- 混合方案中的原生部分
- 需要原生能力（相机、推送、蓝牙等）的场景

**输入格式：**
```markdown
## 客户端 Agent 任务

### 任务信息
- 任务ID: TASK_CL_001
- 目标平台: [iOS/Android/Flutter/小程序/混合]
- 项目路径: /path/to/project
- 分支: feature/xxx

### 关联PRD
- L1 功能: [F-001, F-002]
- L2 用例: [UC-001]
- L3 Story: [US-001]
- UI设计稿: [.pen文件路径]

### 开发内容
| 序号 | 页面/组件 | 功能描述 | 依赖API | 来源Story |
|------|-----------|----------|---------|-----------|
| 1 | LoginPage | 用户登录 | POST /api/auth/login | US-002 |

### 验收标准（从L3 AC提取）
| AC-ID | Given | When | Then |
|-------|-------|------|------|
| AC-001 | ... | ... | ... |

### 输出要求
- 页面/组件代码
- API 对接代码
- 自测报告
```

**输出格式：**
```json
{
  "task_id": "TASK_CL_001",
  "agent_type": "client",
  "platform": "Flutter",
  "status": "completed",
  "summary": { "total": 5, "completed": 5, "failed": 0 },
  "results": [
    {
      "item": "LoginPage",
      "status": "completed",
      "files": ["lib/presentation/pages/login/login_page.dart"],
      "ac_verified": ["AC-001", "AC-002"]
    }
  ]
}
```

### 3. 前端专家 (frontend-expert)

**职责：**
- Web 前端开发（Vue/React）
- Admin 管理后台开发
- 运营后台开发
- 混合方案中的 H5 页面
- 前端测试编写

**适用条件：**
- PRD 中 Client 端技术栈为 Web（Vue/React）
- Admin 端和 Operation 端（始终由前端专家负责）
- 混合方案中的 WebView/H5 页面

**输入格式：**
```markdown
## 前端 Agent 任务

### 任务信息
- 任务ID: TASK_FE_001
- 项目路径: /path/to/project
- 分支: feature/xxx

### 关联PRD
- L1 功能: [F-001, F-002]
- L2 用例: [UC-001]
- L3 Story: [US-001]

### 开发内容
| 序号 | 页面/组件 | 功能描述 | 依赖API | 来源Story |
|------|-----------|----------|---------|-----------|
| 1 | LoginPage | 用户登录 | POST /api/auth/login | US-002 |

### 输出要求
- 页面/组件代码
- API 对接代码
- 本地测试通过
```

**输出格式：**
```json
{
  "task_id": "TASK_FE_001",
  "agent_type": "frontend",
  "status": "completed",
  "summary": { "total": 5, "completed": 5, "failed": 0 },
  "results": [
    {
      "item": "LoginPage",
      "status": "completed",
      "files": ["src/pages/Login.vue"],
      "ac_verified": ["AC-001", "AC-002"]
    }
  ]
}
```

### 4. 后端专家 (python-expert)

**职责：**
- API 接口设计与实现
- 数据模型设计
- 业务逻辑处理
- 数据库操作
- 单元测试编写

**输入格式：**
```markdown
## 后端 Agent 任务

### 任务信息
- 任务ID: TASK_BE_001
- 项目路径: /path/to/project
- 分支: feature/xxx

### 接口清单（从L2提取）
| 序号 | 接口路径 | 方法 | 功能描述 | 来源用例 |
|------|----------|------|----------|----------|
| 1 | /api/auth/login | POST | 用户登录 | UC-002 |

### 数据模型（从L2 data_changes提取）
| 模型名 | 操作 | 字段 |
|--------|------|------|
| User | CREATE | user_id, phone, ... |

### 输出要求
- API 接口实现
- 数据模型定义
- 单元测试通过
```

**输出格式：**
```json
{
  "task_id": "TASK_BE_001",
  "agent_type": "backend",
  "status": "completed",
  "summary": { "total": 3, "completed": 3, "failed": 0 },
  "results": [
    {
      "item": "/api/auth/login",
      "status": "completed",
      "files": ["src/api/auth.py"],
      "test_result": "passed"
    }
  ]
}
```

### 5. 测试专家 (test-expert)

**职责：**
- 按 L3 AC 逐条验证
- 功能测试、集成测试
- 多端一致性测试
- Bug 记录与测试报告

**输入格式：**
```markdown
## 测试 Agent 任务

### 任务信息
- 任务ID: TASK_TEST_001
- 测试环境: http://localhost:3000

### 测试依据
- PRD: docs/prd/L3-user-stories.yaml

### 测试范围
| Story ID | AC-ID | 功能点 | 测试类型 | 优先级 |
|----------|-------|--------|----------|--------|
| US-001 | AC-001 | 正常注册 | 功能测试 | P0 |

### 输出要求
- 按 AC-ID 逐条验证结果
- Bug 列表
- 测试报告
```

---

## 平台路由决策

### 决策规则

```
规则1: Admin端 / Operation端 → 始终调度 frontend-expert
规则2: Client端 + Web技术栈(Vue/React) → 调度 frontend-expert
规则3: Client端 + iOS/Android原生 → 调度 client-expert
规则4: Client端 + Flutter跨平台 → 调度 client-expert
规则5: Client端 + 微信小程序 → 调度 client-expert
规则6: Client端 + 混合方案 → client-expert(壳/桥接) + frontend-expert(H5)
规则7: 后端API → 始终调度 python-expert
```

### 决策示例

**示例1：纯Web全栈**
```
endpoints: Client(Web/Vue), Admin(Web/Vue)
→ frontend-expert: Client端 + Admin端
→ python-expert: 后端API
```

**示例2：Flutter + Web Admin**
```
endpoints: Client(Flutter), Admin(Web/React)
→ client-expert: Client端(Flutter)
→ frontend-expert: Admin端(React)
→ python-expert: 后端API
```

**示例3：多端覆盖**
```
endpoints: Client(iOS+Android+小程序), Admin(Web/Vue)
→ client-expert: Client端(iOS/Android/小程序)
→ frontend-expert: Admin端(Vue)
→ python-expert: 后端API
```

**示例4：混合方案**
```
endpoints: Client(原生壳+H5), Admin(Web/Vue)
→ client-expert: 原生壳、JSBridge、原生页面
→ frontend-expert: H5页面 + Admin端
→ python-expert: 后端API
```

---

## 调度策略

### 任务分解原则

1. **按平台路由分组**
   - 原生/跨平台客户端 → 客户端专家
   - Web前端/Admin/运营 → 前端专家
   - API/数据/业务逻辑 → 后端专家
   - 测试/验证 → 测试专家

2. **按优先级排序** — P0 先行，按 L3 迭代范围确定边界

3. **按依赖关系排序** — 无依赖并行，有依赖串行

### 并行执行策略

**策略A：Web全栈（2 Agent）**
```
后端   ████████████████████████
前端   ████████░░░░████████████
联调                    ████████
测试                            ████████
```

**策略B：原生App全栈（2 Agent）**
```
后端     ████████████████████████
客户端   ████████░░░░████████████
联调                      ████████
测试                              ████████
```

**策略C：多端项目（3 Agent）**
```
后端     ████████████████████████
客户端   ████████░░░░████████████
前端     ████████░░░░████████████
联调                      ████████████
测试                                    ████████
```

---

## 错误处理

| 失败类型 | 处理方式 |
|----------|----------|
| 超时 | 标记未完成，记录已完成部分 |
| 依赖阻塞 | 等待上游完成或标记阻塞 |
| 任务失败 | 记录失败原因，继续其他任务 |
| 平台路由错误 | 重新评估技术栈，调整Agent分配 |

重试机制：最大2次，间隔60秒。

---

## 最佳实践

1. **先解析PRD再分配** - 充分理解L1/L2/L3后再做平台路由决策
2. **合理判断技术栈** - 不确定时询问用户确认Client端技术栈
3. **混合方案注意协作** - client-expert 和 frontend-expert 需明确JSBridge协议
4. **结果对照AC** - 用L3 AC作为验收标准
5. **迭代优化** - 分析效率，改进调度
