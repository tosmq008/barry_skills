# Architecture Output Template

本模板用于 `system-architect` 生成 `docs/architecture/` 主线文档。  
目标不是“把文档写满”，而是把已批准 PRD 转成**可实现、可运维、可测试、可审计**的架构主线。

---

## 1. `docs/architecture/01-architecture-overview.md`

```markdown
# Architecture Overview

## 文档信息
| 字段 | 内容 |
|---|---|
| 范围 | MVP / V1 / 本次迭代 |
| 版本 | |
| 更新时间 | |
| 状态 | proposed / approved / active |

## Architecture Snapshot
- Problem frame:
- Scope in:
- Scope out:
- Primary systems:
- Primary deployment units:
- Primary risks:
- Key quality drivers:
- Open questions:

## 1. 架构目标
- 要支撑的用户/业务闭环：
- 要满足的关键质量属性：
- 明确不做的事：

## 2. 系统边界
- 本系统负责：
- 外部系统负责：
- 信任边界：
- 数据边界：

## 3. 核心决策摘要
| 主题 | 决策 | 原因 | 影响面 | 对应 ADR |
|---|---|---|---|---|

## 4. 风险摘要
| 风险 | 触发条件 | 影响 | 缓解策略 |
|---|---|---|---|

## 5. 读取顺序建议
1. 02-system-context.md
2. 03-container-view.md
3. 04-component-and-flows.md
4. 06-quality-attributes.md
5. 09-architecture-decisions.md
```

---

## 2. `docs/architecture/02-system-context.md`

```markdown
# System Context

## 1. System of Interest
- 名称：
- 业务目标：
- 边界说明：

## 2. Actors
| Actor | 角色 | 目标 | 使用接口/入口 |
|---|---|---|---|

## 3. External Systems
| 系统 | 作用 | 交互方向 | 信任级别 | 关键约束 |
|---|---|---|---|---|

## 4. Trust Boundaries
| 边界 | 涉及对象 | 风险 | 控制策略 |
|---|---|---|---|

## 5. Context Diagram Notes
- 进入点：
- 敏感路径：
- 异步边界：
```

---

## 3. `docs/architecture/03-container-view.md`

```markdown
# Container View

## 1. Container List
| Container | 类型 | 责任 | Owner | Runtime | 数据/状态 | 扩缩容特征 |
|---|---|---|---|---|---|---|

## 2. Container Interaction
| Source | Target | Protocol | Sync/Async | Auth | SLA/SLO | Failure Handling |
|---|---|---|---|---|---|---|

## 3. Trust Boundaries by Container
| Boundary | In/Out | Control |
|---|---|---|

## 4. Deployment Notes
- 可独立发布单元：
- 需要同发布的单元：
- 数据迁移影响：
```

---

## 4. `docs/architecture/04-component-and-flows.md`

```markdown
# Components and Critical Flows

## 1. Component Catalog
| Component | 所属 Container | 职责 | 输入 | 输出 | 关键依赖 |
|---|---|---|---|---|---|

## 2. Critical Flows
### Flow-01 [名称]
- Trigger:
- Preconditions:
- Main path:
- Error path:
- Recovery:
- Observability:
- Security checks:

## 3. Interface Contracts
| Interface | Producer | Consumer | Contract Type | Versioning | Idempotency |
|---|---|---|---|---|---|
```

---

## 5. `docs/architecture/05-data-and-integration.md`

```markdown
# Data and Integration

## 1. Data Ownership
| Data Object | System of Record | Producers | Consumers | Sensitivity | Retention |
|---|---|---|---|---|---|

## 2. Consistency Strategy
| 场景 | 一致性要求 | 模式 | 失败补偿 |
|---|---|---|---|

## 3. Integration Patterns
| 集成 | 模式 | 触发方式 | Retry | DLQ/补偿 | 监控 |
|---|---|---|---|---|---|
```

---

## 6. `docs/architecture/06-quality-attributes.md`

```markdown
# Quality Attributes

## 1. Quality Attribute Summary
| 属性 | Why it matters | Budget / Target | Measurement | Tradeoff |
|---|---|---|---|---|

## 2. ASR / NFR Scenarios
### QA-01 [属性]
- Stimulus:
- Context:
- System response:
- Measure:

## 3. Operational Budgets
- Latency:
- Throughput:
- Error budget:
- Recovery target:
- Cost / capacity:
```

---

## 7. `docs/architecture/07-deployment-and-operations.md`

```markdown
# Deployment and Operations

## 1. Deployment Units
| Unit | Build artifact | Runtime | Environment | Scale unit |
|---|---|---|---|---|

## 2. Release Strategy
- Deployment mode:
- Canary / phased rollout:
- Feature flag usage:
- Rollback method:
- Rollforward method:

## 3. Observability
| Signal | What to watch | Threshold | Alert | Owner |
|---|---|---|---|---|

## 4. Resilience
- Degrade modes:
- Circuit breaker / retry:
- Backpressure:
- Rate limiting:
- Runbook links:
```

---

## 8. `docs/architecture/08-risk-register.md`

```markdown
# Architecture Risk Register

| Risk ID | Risk | Trigger | Impact | Likelihood | Owner | Mitigation | Residual Risk |
|---|---|---|---|---|---|---|---|
```

---

## 9. `docs/architecture/09-architecture-decisions.md`

```markdown
# Architecture Decisions

## ADR Index
| ADR | Topic | Status | Decision | Alternatives | Consequence |
|---|---|---|---|---|---|
```

---

## 10. `docs/architecture/validation-report.md`

```markdown
# Architecture Validation Report

## Checks
| Check | Result | Notes |
|---|---|---|
| Context and containers complete | PASS/WARN/FAIL | |
| Trust boundaries defined | | |
| Critical flows cover P0/P1 | | |
| Data ownership and consistency defined | | |
| Operational strategy present | | |
| ADRs cover major choices | | |
| Downstream handoff ready | | |

## Errors
- ...

## Warnings
- ...

## Handoff
- To tech-manager:
- To test-expert:
```

---

## 使用规则

1. 优先先写 `01/02/03/06/09`，再补 `04/05/07/08`。
2. `validation-report.md` 必须在最后生成。
3. 若只做增量更新，也必须保证 `03/06/09/validation-report` 至少同步。
