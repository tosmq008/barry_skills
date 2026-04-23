# Dependency and Critical Path Template

## 1. Dependency 分类

### Hard dependency
不完成就无法继续的阻塞项。

### Soft dependency
可通过 mock、feature flag、手工替代、顺序调整等方式暂时绕开的依赖。

### External dependency
外部团队 / 第三方 / 平台 / 审批依赖。

### Environment dependency
环境、流水线、网络、访问权限、证书、配额等依赖。

### Data dependency
迁移、回填、初始化、回滚、对账依赖。

---

## 2. Critical Path 表

| Step | Dependency | Type | Why critical | Owner | Earliest finish | Backup |
|---|---|---|---|---|---|---|

---

## 3. Dependency Register

| ID | Dependency | Type | Blocking slices | Probability | Impact | Mitigation | Escalation |
|---|---|---|---|---|---|---|---|

---

## 4. 并行策略

对每个关键依赖说明：
- 哪些工作可以并行
- 哪些只能串行
- 哪些可用 stub/mock/feature flag 提前验证
- 何时需要正式 cutover

---

## 5. 退出条件

- 所有 hard dependency 已闭合或有批准例外
- critical path 有 owner 和时间边界
- external dependency 有 escalation 方案
