# Release Readiness and Evidence Template

## 1. Release Decision

- Decision: go / conditional-go / no-go
- Scope:
- Version / batch:
- Main evidence:
- Main risks:

---

## 2. Gate Table

| Gate | Status | Evidence | Owner | Exception |
|---|---|---|---|---|

---

## 3. Blocking Conditions

以下任一成立，默认 no-go：
- P0/P1 风险无测试证据
- 回滚信号未定义
- 关键监控/告警缺失
- 数据迁移不可回滚且无批准例外
- 关键安全风险无缓解

---

## 4. Conditional Go Template

- Known issue:
- Risk:
- Mitigation:
- Observation window:
- Rollback threshold:
- Approver:
- Expiry:

---

## 5. Post-release Evidence

- Dashboard / SLI:
- Alert channel:
- On-call:
- Hypercare owner:
- First review checkpoint:
```
