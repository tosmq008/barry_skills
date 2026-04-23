# Delivery YAML Spec

## `slice-plan.yaml`

```yaml
delivery_scope:
release_mode:
cut_line:
freeze_points:
slices:
  - slice_id:
    name:
    objective:
    features: []
    use_cases: []
    stories: []
    architecture_units: []
    dependencies: []
    owner:
    validation:
    release_strategy:
    rollback_scope:
```

### 字段建议
- `delivery_scope`: MVP / iteration / release batch
- `release_mode`: phased / canary / big bang / internal
- `cut_line`: 明确 above/below cut line
- `freeze_points`: scope freeze / code freeze / release freeze
- `validation`: 本切片如何验收
- `release_strategy`: 本切片如何暴露给真实用户
- `rollback_scope`: 本切片失败时回滚边界

---

## `dependency-graph.yaml`

```yaml
critical_path:
hard_dependencies:
soft_dependencies:
external_dependencies:
environment_dependencies:
data_dependencies:
approval_gates:
risks:
```

### 字段建议
- `critical_path`: 按顺序列出关键依赖步骤
- `hard_dependencies`: 无法绕过的阻塞
- `soft_dependencies`: 可暂时绕开的依赖
- `approval_gates`: 需要的批准、合规、窗口、变更审查
- `risks`: 依赖风险及其缓解

---

## 最小示例

```yaml
delivery_scope: MVP
release_mode: canary
cut_line:
  above: [SLICE-001, SLICE-002]
  below: [SLICE-003]
freeze_points:
  - scope_freeze: 2025-10-10
slices:
  - slice_id: SLICE-001
    name: create-order happy path
    objective: user can create and view order
    features: [F-001, F-002]
    use_cases: [UC-001]
    stories: [US-001, US-002]
    architecture_units: [C-API, C-DB]
    dependencies: [DEP-identity]
    owner: squad-order
    validation: integration + canary metrics
    release_strategy: 10% tenant rollout
    rollback_scope: feature flag + API revert
```
