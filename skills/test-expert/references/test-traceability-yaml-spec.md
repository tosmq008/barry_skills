# Test Traceability YAML Spec

`docs/test/test-traceability.yaml` 至少包含：

```yaml
test_scope:
release_scope:
risks:
features_to_risks:
use_cases_to_tests:
stories_to_acceptance_checks:
quality_attributes_to_tests:
security_domains_to_checks:
release_gates:
rollback_signals:
open_issues:
```

---

## 字段说明

### `test_scope`
测试范围，例如：
- MVP release-1
- slice batch-2
- regression window

### `release_scope`
本次放行对象、环境、受众。

### `risks`
风险列表，建议每项包含：
- risk_id
- scenario
- score
- owner
- mitigation

### `features_to_risks`
Feature 与风险映射。

### `use_cases_to_tests`
UseCase 与测试设计映射。

### `stories_to_acceptance_checks`
Story 到 AC/验证项映射。

### `quality_attributes_to_tests`
性能、可靠性、安全、可访问性等到测试设计映射。

### `security_domains_to_checks`
安全域到检查项映射，例如 authz / session / input validation / audit。

### `release_gates`
放行门禁及证据。

### `rollback_signals`
回滚信号、阈值、数据源、动作。

### `open_issues`
已知问题、例外、过期时间。

---

## 最小示例

```yaml
test_scope: MVP release-1
release_scope: 10% tenant canary
risks:
  - risk_id: RISK-001
    scenario: duplicate payout on retry
    score: 20
features_to_risks:
  - feature_id: F-021
    risks: [RISK-001]
use_cases_to_tests:
  - uc_id: UC-008
    tests: [TEST-101, TEST-205]
release_gates:
  - gate: canary error budget
    threshold: "< 1%"
rollback_signals:
  - signal: duplicate_payout_count
    threshold: "> 0"
```
