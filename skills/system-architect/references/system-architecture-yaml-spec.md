# System Architecture YAML Spec

`docs/architecture/system-architecture.yaml` 至少包含以下字段。

```yaml
system_name:
architecture_scope:
quality_attributes:
constraints:
service_level_targets:
systems:
containers:
components:
critical_flows:
interfaces:
data_ownership:
consistency_strategy:
integration_patterns:
external_dependencies:
security_boundaries:
threat_model:
deployment_units:
observability:
risks:
decision_index:
open_questions:
```

---

## 字段说明

### `system_name`
系统名称。建议与 `01-architecture-overview.md` 保持一致。

### `architecture_scope`
范围说明，例如 `MVP`, `V1`, `2025Q4 release-1`。

### `quality_attributes`
列表，推荐每项包含：
- `attribute`
- `target`
- `measure`
- `tradeoff`

### `constraints`
硬约束列表，例如：
- 单租户/多租户
- 区域限制
- 合规约束
- 平台限制

### `service_level_targets`
建议包含：
- availability
- latency
- throughput
- recovery
- error_budget

### `systems`
System Context 层对象列表。

### `containers`
Container 列表，建议每项包含：
- `container_id`
- `name`
- `responsibility`
- `runtime`
- `owner`
- `state_type`
- `deployable`
- `dependencies`

### `components`
仅在需要下钻时填写。建议：
- `component_id`
- `container_id`
- `name`
- `responsibility`
- `depends_on`

### `critical_flows`
关键路径列表。建议每项包含：
- `flow_id`
- `name`
- `trigger`
- `containers`
- `failure_modes`
- `observability`

### `interfaces`
接口清单。建议包含：
- producer
- consumer
- protocol
- auth
- idempotency
- versioning

### `data_ownership`
数据对象归属。建议包含：
- data_object
- system_of_record
- sensitivity
- retention
- replication

### `consistency_strategy`
写明一致性策略与补偿方式。

### `integration_patterns`
例如 sync API / async event / batch / webhook。

### `external_dependencies`
第三方/平台依赖。

### `security_boundaries`
trust boundary 列表和控制策略。

### `threat_model`
可简化为威胁摘要引用，也可包含 threat IDs。

### `deployment_units`
部署单元、环境、发布模式、扩缩容。

### `observability`
信号、指标、日志、告警、trace hooks。

### `risks`
架构风险列表，建议映射到 `08-risk-register.md`。

### `decision_index`
ADR 索引，例如：
- `ADR-001: use event outbox`
- `ADR-002: single-writer ledger`

### `open_questions`
仍未关闭的问题。

---

## 最小示例

```yaml
system_name: payout-platform
architecture_scope: MVP
quality_attributes:
  - attribute: reliability
    target: "p95 success rate >= 99.9%"
    measure: payout_success_rate
constraints:
  - regulated data must stay in-region
containers:
  - container_id: C-API
    name: payout-api
    responsibility: expose payout APIs and policy checks
    runtime: k8s
    owner: payments
    state_type: stateless
    deployable: true
critical_flows:
  - flow_id: FLOW-001
    name: create payout
    trigger: partner submits payout
    containers: [C-API, C-WORKER, C-DB]
risks:
  - RISK-001 duplicate payout on retry
decision_index:
  - ADR-001: idempotency-key on payout create
```
