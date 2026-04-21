# 任务单模板

## 概述

所有任务单都必须同时绑定 **产品输入** 和 **架构输入**。`tech-manager` 发单时不能只给需求，不给架构约束。

通用必填字段：
- 任务 ID
- 项目路径
- 开发分支
- 来源 PRD
- 来源架构文档
- 当前迭代 / 优先级
- 不可变更架构约束
- 依赖关系
- 验收标准
- 输出要求

---

## 1. 客户端任务单模板

> 适用于 `client-expert`

```markdown
# 客户端开发任务单

## 基本信息
- 任务ID: TASK_CL_[xxx]
- 项目路径: [项目路径]
- 开发分支: feature/[name]
- 当前迭代: [ITER-xxx]
- 优先级: [P0/P1/P2]
- 目标平台: [iOS/Android/Flutter/小程序/混合]

## 来源文档
- PRD: docs/prd/L3-user-stories.yaml
- 页面清单: docs/prd/07-page-list.md
- 架构主文档: docs/architecture/[文档名].md
- API契约: docs/architecture/api-contract.md
- 数据字典: docs/architecture/data-dictionary.md

## 不可变更架构约束
- 技术栈: [例如 Flutter 3.x]
- 认证方案: [例如 JWT + Refresh Token]
- 网络层约束: [例如 Dio + 统一拦截器]
- 路由/容器约束: [例如 原生壳 + WebView]

## 开发范围
| 序号 | 页面/模块 | 功能描述 | 依赖API | 来源Story |
|------|-----------|----------|---------|-----------|
| 1 | [name] | [description] | [api] | US-001 |

## 依赖关系
- 前置依赖: [例如 JSBridge 协议先完成]
- 并行任务: [例如 静态页面可先做]
- 阻塞回流条件: [例如 需要新增原生认证方案时回流架构]

## 验收标准
| AC-ID | Given | When | Then |
|-------|-------|------|------|
| AC-001 | [given] | [when] | [then] |

## 输出要求
- 完成页面/组件与 API 对接
- 完成自测并说明 AC 覆盖情况
- 明确剩余风险与阻塞点
```

---

## 2. 前端任务单模板

> 适用于 `frontend-expert`

```markdown
# 前端开发任务单

## 基本信息
- 任务ID: TASK_FE_[xxx]
- 项目路径: [项目路径]
- 开发分支: feature/[name]
- 当前迭代: [ITER-xxx]
- 优先级: [P0/P1/P2]
- 端: [Client(Web)/Admin/Operation/H5]

## 来源文档
- PRD: docs/prd/L3-user-stories.yaml
- 页面清单: docs/prd/07-page-list.md
- 架构主文档: docs/architecture/[文档名].md
- API契约: docs/architecture/api-contract.md
- ADR: docs/architecture/adr/

## 不可变更架构约束
- 前端框架: [例如 React 18 / Vue 3]
- 状态管理: [例如 Pinia / Redux Toolkit]
- UI体系: [例如 Ant Design / Element Plus]
- 认证方案: [例如 Bearer Token + Refresh]
- 错误码规范: [例如 0 / 400xx / 401xx / 500xx]

## 开发范围
| 序号 | 页面/模块 | 路由 | 功能描述 | 来源Story |
|------|-----------|------|----------|-----------|
| 1 | [name] | /path | [description] | US-001 |

## API 对接
| 序号 | 接口 | 方法 | 用途 | 来源用例 |
|------|------|------|------|----------|
| 1 | /api/v1/[resource] | GET | [用途] | UC-001 |

## 依赖关系
- 前置依赖: [例如 登录接口需后端先可用]
- 并行任务: [例如 静态组件先实现]
- 阻塞回流条件: [例如 现有权限模型无法满足页面能力]

## 验收标准
| AC-ID | Given | When | Then |
|-------|-------|------|------|
| AC-001 | [given] | [when] | [then] |

## 输出要求
- 完成页面、组件、API 对接与本地验证
- 记录 AC 覆盖、自测结论、剩余风险
```

---

## 3. 后端任务单模板

> 适用于 `python-expert`

```markdown
# 后端开发任务单

## 基本信息
- 任务ID: TASK_BE_[xxx]
- 项目路径: [项目路径]
- 开发分支: feature/[name]
- 当前迭代: [ITER-xxx]
- 优先级: [P0/P1/P2]

## 来源文档
- PRD: docs/prd/L2-use-case-flows.yaml
- PRD: docs/prd/L3-user-stories.yaml
- 架构主文档: docs/architecture/[文档名].md
- API契约: docs/architecture/api-contract.md
- 数据字典: docs/architecture/data-dictionary.md
- ADR: docs/architecture/adr/

## 不可变更架构约束
- 后端框架: [例如 FastAPI]
- 数据库: [例如 PostgreSQL]
- 缓存/消息: [例如 Redis / MQ]
- 认证方案: [例如 JWT]
- API 响应规范: [例如 code/message/data/meta]

## 开发范围
| 序号 | 接口/服务 | 方法 | 功能描述 | 来源用例 |
|------|-----------|------|----------|----------|
| 1 | /api/v1/[resource] | POST | [description] | UC-001 |

## 数据模型
| 模型名 | 操作 | 字段 | 来源用例 |
|--------|------|------|----------|
| User | CREATE | id, phone, status | UC-001 |

## 依赖关系
- 前置依赖: [例如 架构方案中的权限模型已定]
- 并行任务: [例如 模型骨架与接口骨架可并行]
- 阻塞回流条件: [例如 必须改变数据库/服务边界]

## 验收标准
- API 与契约一致
- 数据模型与数据字典一致
- 业务规则符合 L2/L3
- 单元测试通过
- 输出剩余风险与阻塞点
```

---

## 4. 测试任务单模板

> 适用于 `test-expert`

```markdown
# 测试任务单

## 基本信息
- 任务ID: TASK_TEST_[xxx]
- 当前迭代: [ITER-xxx]
- 测试环境: [URL/环境说明]

## 来源文档
- PRD: docs/prd/L3-user-stories.yaml
- API契约: docs/architecture/api-contract.md
- 任务拆解: docs/dev/task-breakdown.md
- 联调报告: docs/dev/integration-report.md

## 测试范围
| Story ID | AC-ID | 功能点 | 测试类型 | 优先级 |
|----------|-------|--------|----------|--------|
| US-001 | AC-001 | [功能点] | 功能测试 | P0 |

## 特别关注
- 多端一致性
- 认证与权限
- 错误码与异常态
- 关键边界场景

## 输出要求
- AC 逐条验证结果
- Bug 列表与优先级
- 是否满足交付条件
```

---

## 5. 架构调整清单模板

> 当 `tech-manager` 判断当前需求不能直接进入实施时，使用此模板回流 `system-architect`

```markdown
# 架构调整清单

## 当前结论
- 结果: [ADJUST/REVIEW]
- 是否阻塞实施: [是/否]

## 触发来源
- Story / Use Case: [US-xxx / UC-xxx]
- 当前阶段: [架构关卡 / 任务拆分 / 联调]

## 缺口列表
| 编号 | 缺口 | 影响范围 | 风险 |
|------|------|----------|------|
| A-01 | [描述] | [前端/客户端/后端/测试] | [高/中/低] |

## 建议调整
| 编号 | 建议 | 责任方 | 参考文档 |
|------|------|--------|----------|
| R-01 | [描述] | system-architect | docs/architecture/... |

## 暂停说明
- 未完成以上调整前，不进入对应实现任务
```
