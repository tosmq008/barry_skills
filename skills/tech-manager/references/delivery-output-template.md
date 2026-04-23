# Delivery Output Template

本模板用于 `tech-manager` 生成 `docs/delivery/`。  
目标是把架构和 PRD 转成**可交付、可验证、可发布、可回滚**的计划。

---

## 1. `docs/delivery/01-delivery-overview.md`

```markdown
# Delivery Overview

## 文档信息
| 字段 | 内容 |
|---|---|
| 范围 | MVP / 本次迭代 / 发布批次 |
| 版本 | |
| 状态 | planned / approved / active |
| 更新时间 | |

## Delivery Snapshot
- Release mode:
- Cut line:
- Freeze points:
- Primary risks:
- Critical path:
- Canary / rollback strategy:
- Key dependencies:

## 1. 交付目标
- 本次交付要形成的最小价值闭环：
- 不包含内容：
- 成功标准：

## 2. 组织方式
- 团队数量：
- 负责人：
- 协作方式：
- 外部依赖：

## 3. 风险摘要
| 风险 | 触发条件 | 影响 | 缓解动作 | Owner |
|---|---|---|---|---|
```

---

## 2. `docs/delivery/02-slice-plan.md`

```markdown
# Slice Plan

## Slice Catalog
| Slice ID | 名称 | 目标 | Feature / Story | Owner | Depends on | Validation | Release Mode |
|---|---|---|---|---|---|---|---|

## Per Slice Detail
### Slice-01 [名称]
- Objective:
- Features:
- Use cases:
- Stories:
- Architecture units:
- Definition of ready:
- Validation:
- Release strategy:
- Rollback scope:
```

---

## 3. `docs/delivery/03-dependency-plan.md`

```markdown
# Dependency Plan

## 1. Critical Path
1. ...
2. ...
3. ...

## 2. Hard Dependencies
| Dependency | Why hard | Blocking impact | Owner | Exit criteria |
|---|---|---|---|---|

## 3. Soft Dependencies
| Dependency | Why soft | Workaround | Owner |
|---|---|---|---|

## 4. External Dependencies
| Dependency | Type | Risk | Fallback |
|---|---|---|---|
```

---

## 4. `docs/delivery/04-team-interfaces.md`

```markdown
# Team Interfaces

| Team / Function | Scope | Deliverables | Handoff in | Handoff out | Escalation |
|---|---|---|---|---|---|
```

---

## 5. `docs/delivery/05-iteration-and-release-plan.md`

```markdown
# Iteration and Release Plan

## 1. Iteration Plan
| Iteration | Goal | Included slices | Exit criteria |
|---|---|---|---|

## 2. Release Plan
| Release stage | Traffic / audience | Gate | Rollback trigger | Support readiness |
|---|---|---|---|---|

## 3. Cut line and freeze
- Cut line:
- Scope freeze:
- Release freeze:
```

---

## 6. `docs/delivery/06-quality-gates.md`

```markdown
# Quality Gates

## 1. Acceptance Criteria vs DoD vs Release Gate
| Layer | Purpose | Applies to | Owner |
|---|---|---|---|
| AC | 单项行为要求 | Story / slice | Product / Eng |
| DoD | 通用完成质量 | 全部交付项 | Team |
| Release Gate | 放行/阻断 | Release batch | Cross-functional |

## 2. Gate Checklist
| Gate | Must pass | Evidence | Exception path |
|---|---|---|---|
```

---

## 7. `docs/delivery/07-risk-and-rollback.md`

```markdown
# Risk and Rollback

## 1. Top Risks
| Risk | Trigger | Impact | Detect | Mitigate |
|---|---|---|---|---|

## 2. Rollback Plan
- Rollback scope:
- Data rollback:
- Feature flag rollback:
- Communication plan:

## 3. Hypercare
- Time window:
- Owners:
- Primary dashboards:
- Escalation policy:
```

---

## 8. `docs/delivery/validation-report.md`

```markdown
# Delivery Validation Report

| Check | Result | Notes |
|---|---|---|
| Slice plan complete | PASS/WARN/FAIL | |
| Critical path clear | | |
| Quality gates defined | | |
| Rollback ready | | |
| Team handoffs clear | | |
| Metrics and readiness defined | | |

## Errors
- ...

## Warnings
- ...
```
