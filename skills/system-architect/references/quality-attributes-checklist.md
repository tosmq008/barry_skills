# Quality Attributes and NFR Checklist

## 用法

本清单用于识别 ASR（Architecturally Significant Requirements）、定义质量预算、验证 tradeoff。

---

## 1. 安全 Security

- 认证方式是什么
- 授权模型是什么（RBAC / ABAC / policy）
- 最敏感的数据对象有哪些
- 是否有租户隔离
- 是否需要审计、不可抵赖、审批痕迹
- 是否有 secret/key rotation 要求
- 是否有滥用、防刷、速率限制、机器人流量风险

### 最少产出
- 敏感数据清单
- trust boundary
- 认证/授权策略
- 审计要求
- 风险与控制映射

---

## 2. 可靠性 Reliability

- 关键用户路径有哪些
- 什么级别的故障算不可接受
- RTO / RPO / MTTR 目标是什么
- 哪些依赖会拖垮系统
- 有哪些降级模式
- 是否支持重试、幂等、补偿

### 最少产出
- 错误预算/可接受失败范围
- 关键路径恢复策略
- 降级与 fallback
- 外部依赖故障策略

---

## 3. 性能 Performance

- 用户可接受的延迟阈值是什么
- 峰值吞吐预期是什么
- 哪些操作最重
- 缓存是否必要
- 后台任务是否应异步化
- 写路径/读路径是否需要不同优化

### 最少产出
- P50/P95/P99 目标
- 吞吐预算
- 高成本查询/操作清单
- 缓存与异步策略

---

## 4. 成本 Cost

- 哪些部分最容易放大基础设施成本
- 哪些资源按峰值收费
- 是否有闲时/高峰差异
- 是否存在第三方计费放大量

### 最少产出
- 成本热点清单
- 主要费用驱动因素
- 降成本杠杆

---

## 5. 运维 Operational Excellence

- 如何部署
- 如何观测
- 如何告警
- 如何回滚
- 如何排障
- 需要哪些 runbook

### 最少产出
- 关键 SLI/SLO
- 告警阈值
- 发布/回滚策略
- runbook ownership

---

## 6. 可持续性与演进 Sustainability / Evolvability

- 后续 2-3 个版本最可能扩展什么
- 当前 MVP 是否留下合理扩展点
- 哪些技术债必须记录
- 哪些地方故意延后

### 最少产出
- 演进路线
- 技术债清单
- ADR 中记录的 deferred choice
