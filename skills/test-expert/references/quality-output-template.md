# Quality Output Template

本模板用于 `test-expert` 生成 `docs/test/`。  
目标是把上游 PRD、架构和交付计划变成**风险驱动、可证据化、可放行**的测试主线。

---

## 1. `docs/test/01-quality-strategy.md`

```markdown
# Quality Strategy

## 文档信息
| 字段 | 内容 |
|---|---|
| 范围 | 版本 / 批次 / 切片 |
| 状态 | planned / active / approved |
| 更新时间 | |

## Quality Snapshot
- Top risks:
- Test focus:
- Release posture:
- Blocking criteria:
- Rollback signals:
- Main evidence sources:

## 1. 范围
- In scope:
- Out of scope:
- Main flows:
- Main quality attributes:

## 2. Strategy
- small / medium / large:
- exploratory:
- security:
- NFR:
- evidence and gates:
```

---

## 2. `docs/test/02-risk-matrix.md`

```markdown
# Risk Matrix

| Risk ID | Scenario | Type | Likelihood | Impact | Score | Detection | Prevention | Test layer |
|---|---|---|---|---|---|---|---|---|
```

---

## 3. `docs/test/03-traceability-matrix.md`

```markdown
# Traceability Matrix

| Product item | Risk | Test design | Evidence | Gate |
|---|---|---|---|---|
| Feature / UC / Story / QA | | | | |
```

---

## 4. `docs/test/04-test-design.md`

```markdown
# Test Design

## Test Catalog
| Test ID | Level | Objective | Preconditions | Data | Oracle | Owner |
|---|---|---|---|---|---|---|

## Critical Paths
### TEST-001 [名称]
- Trigger:
- Main path:
- Error path:
- Assertions:
- Evidence:
```

---

## 5. `docs/test/05-environment-and-data.md`

```markdown
# Environment and Data

## 1. Environments
| Env | Purpose | Risks | Gaps |
|---|---|---|---|

## 2. Test Data
| Data set | Source | Sensitivity | Reset strategy | Owner |
|---|---|---|---|---|
```

---

## 6. `docs/test/06-automation-strategy.md`

```markdown
# Automation Strategy

## 1. Layer split
| Layer | What to automate | Tooling | Stability expectations |
|---|---|---|---|

## 2. Ownership
- Who writes:
- Who reviews:
- Who maintains:

## 3. Flaky control
- Retry policy:
- Quarantine policy:
- Root cause loop:
```

---

## 7. `docs/test/07-nonfunctional-test-plan.md`

```markdown
# Nonfunctional Test Plan

| Attribute | Scenario | Target | Method | Evidence |
|---|---|---|---|---|
```

---

## 8. `docs/test/08-security-test-plan.md`

```markdown
# Security Test Plan

| Domain | Risk | Control | Test type | Evidence |
|---|---|---|---|---|
```

---

## 9. `docs/test/09-release-readiness.md`

```markdown
# Release Readiness

## 1. Gate Summary
| Gate | Result | Evidence | Decision |
|---|---|---|---|

## 2. Exceptions
| Exception | Risk | Mitigation | Approver | Expiry |
|---|---|---|---|---|

## 3. Rollback Signals
- Signal:
- Threshold:
- Source:
- Action:
```

---

## 10. `docs/test/validation-report.md`

```markdown
# Test Validation Report

| Check | Result | Notes |
|---|---|---|
| Risk model complete | PASS/WARN/FAIL | |
| Traceability complete | | |
| Test layers balanced | | |
| Gates explicit | | |
| Security/NFR covered | | |
| Rollback signals defined | | |

## Errors
- ...

## Warnings
- ...
```
